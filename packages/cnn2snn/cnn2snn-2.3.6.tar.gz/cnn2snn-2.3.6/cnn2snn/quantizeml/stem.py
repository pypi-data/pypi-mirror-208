#!/usr/bin/env python
# ******************************************************************************
# Copyright 2022 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
"""Functions to convert Stem block quantized layers to Akida.
Those layers are:
    - The Embedding layer
    - The Reshape layer
    - The ClassToken (+ the DistToken for distilled models) layer(s)
    - The AddPosEmbedding layer
"""
from akida import LayerType, Stem
import quantizeml.layers as qlayers
import numpy as np
from .blocks import get_block_out_quantizer
from .outputs import set_output_v2_variables
from .weights import broadcast_and_set_variables


def _set_stem_variables(ak_layer, layers):
    """Computes and sets the variables for an Akida Stem layer.

    This function converts the variables of a Keras layers and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        layers (list): list of the source quantized layers.
    """
    assert ak_layer.parameters.layer_type == LayerType.Stem

    embedding_layer = layers[0]

    cls_layers = []
    add_pos_emb_layer = None
    # Get the QuantizedClassToken layer(s) and the optional
    # QuantizedAddPositionEmbs layer
    for layer in layers:
        if isinstance(layer, qlayers.QuantizedClassToken):
            cls_layers.append(layer)
        elif isinstance(layer, qlayers.QuantizedAddPositionEmbs):
            add_pos_emb_layer = layer

    # Prepare a dict for akida variables
    variables_ak = {}

    # get the Embedding weights
    weights_ak = embedding_layer.weight_quantizer.qweights.value.fp.values.numpy()

    # get the Embedding bias
    bias_quantizer = embedding_layer.bias_quantizer
    bias = bias_quantizer.qweights.value.values.numpy().astype(np.int32)
    bias_shift = bias_quantizer.shift.value.numpy().astype(np.uint8)
    bias_ak = (bias >> bias_shift).astype(np.int8)

    if len(cls_layers) > 0:
        tokens_ak = []
        shifts_tokens_ak = []
        for cls_layer in cls_layers:
            # get the ClassToken layer token variable (aka cls member)
            cls_quantizer = cls_layer.cls_quantizer
            token = cls_quantizer.qweights.value.values.numpy().astype(np.int32)
            token_shift = cls_quantizer.shift.value.numpy().astype(np.uint8)
            token_ak = token >> token_shift
            # Insert the token value at the first position. This allows us to match
            # the model concatenation order.
            tokens_ak.insert(0, np.squeeze(token_ak))
            shifts_tokens_ak.insert(0, token_shift)
        variables_ak["tokens"] = np.stack(tokens_ak)
        variables_ak["tokens_shift"] = np.concatenate(shifts_tokens_ak)

    if add_pos_emb_layer:
        # get the positional embedding matrix
        pos_emb_quantizer = add_pos_emb_layer.pe_quantizer
        pos_emb = pos_emb_quantizer.qweights.value.values.numpy().astype(np.int32)
        pos_emb_shift = pos_emb_quantizer.shift.value.numpy().astype(np.uint8)
        pos_emb_ak = pos_emb >> pos_emb_shift
        variables_ak["pos_embedding"] = pos_emb_ak
        # Get the QuantizedAddPositionEmbs layer shifts
        variables_ak["pos_embs_shift"] = pos_emb_shift

    variables_ak["weights"] = weights_ak.astype(np.int8)
    variables_ak["bias"] = bias_ak
    # Get the Embedding layer shifts
    variables_ak["bias_shift"] = bias_shift.astype(np.uint8)

    broadcast_and_set_variables(ak_layer, variables_ak)


def _parse_embedding(layer):
    """Parses the quantizeml.QuantizedConv2D embedding layer parameters.

    Args:
        layer (:obj:`tf.keras.Layer`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    # Remove batch dimension to get input shape
    input_shape = layer.input_shape[1:]
    filters = layer.filters
    kernel_size = layer.kernel_size[0]
    # In quantizeml one reserves automatically one bit for the sign, but in akida
    # this is rather checked during the clipping operations.
    buffer_bits = layer.buffer_bitwidth + 1
    name = layer.name

    embedding_params = dict(input_shape=input_shape,
                            filters=filters,
                            kernel_size=kernel_size,
                            buffer_bits=buffer_bits,
                            name=name)
    return embedding_params


def _parse_additional_layers(layers):
    """Parses the quantizeml quantized additional layers of the Stem block and returns the
    params to create the corresponding Akida Stem layer.

    Args:
        layers (list): the quantizeml quantized layers of the Stem to convert.

    Returns:
        dict: the corresponding akida parameters.
    """

    cls_layers = []
    add_pos_emb_layer = None
    # Get the QuantizedClassToken layer(s) and the optional
    # QuantizedAddPositionEmbs layer
    for layer in layers:
        if isinstance(layer, qlayers.QuantizedClassToken):
            cls_layers.append(layer)
        elif isinstance(layer, qlayers.QuantizedAddPositionEmbs):
            add_pos_emb_layer = layer

    # A block of layers always end with an output Quantizer. Extract it.
    out_quantizer = getattr(layers[-1], "out_quantizer", False)
    assert isinstance(out_quantizer, qlayers.OutputQuantizer)
    output_bits = out_quantizer.bitwidth

    num_non_patch_tokens = len(cls_layers)

    return dict(output_bits=output_bits,
                collapse_spatial_dims=True,
                num_non_patch_tokens=num_non_patch_tokens,
                add_pos_embs_available=add_pos_emb_layer is not None)


def convert_quantized_stem_layers(model_ak, block):
    """Converts QuantizedDense layer and its variables and adds it to the
    Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        block (list): the quantizeml quantized layers of the Stem to convert.

    Returns:
        bool: return False if conversion fails, True otherwise.
    """
    # Extract neural layer of the block
    embedding_layer = block[0]
    # Stem block has at least one embedding layer and an additional layer (QuantizedClassToken
    # and/or QuantizedAddPosEmbedding). Stem can only be the first layer of the Akida model.
    if len(block) == 1 or not isinstance(embedding_layer, qlayers.QuantizedConv2D) \
            or len(model_ak.layers) != 0:
        return False

    # The embedding layer should be followed by a QuantizedReshape in the Stem
    next_layer = embedding_layer.outbound_nodes[0].outbound_layer
    if not isinstance(next_layer, qlayers.QuantizedReshape):
        return False

    # Parse the Stem embedding layer parameters
    stem_params = _parse_embedding(embedding_layer)
    # Stem can handle only 3D or 1D inputs
    if stem_params["input_shape"][-1] not in [1, 3]:
        return False

    # Parse additional layers of the Stem
    additional_params = _parse_additional_layers(block[1:])
    stem_params.update(additional_params)

    layer_ak = Stem(**stem_params)
    model_ak.add(layer_ak)
    _set_stem_variables(layer_ak, block)
    # Get out_quantizer of the block.
    out_quantizer = get_block_out_quantizer(block)
    # OutputQuantizer is mandatory at the end of the block
    assert isinstance(out_quantizer, qlayers.OutputQuantizer)

    set_output_v2_variables(layer_ak, out_quantizer)

    return True
