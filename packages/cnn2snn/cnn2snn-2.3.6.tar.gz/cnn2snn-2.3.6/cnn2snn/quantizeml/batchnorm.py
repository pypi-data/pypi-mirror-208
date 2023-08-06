#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
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
"""Functions to convert QuantizedBatchNormalization to Akida.
"""
from akida import LayerType, BatchNormalization
import quantizeml.layers as qlayers
import numpy as np

from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables
from .activations import parse_relu_v2, set_relu_variables
from .layer_utils import get_inbound_layers


def _set_batchnorm_variables(ak_layer, block):
    """Computes and sets the variables for an Akida BatchNormalization layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        block (list(:obj:`tf.keras.Layer`)): the block of keras layers.
    """
    layer_bn = block[0]
    assert isinstance(layer_bn, qlayers.QuantizedBatchNormalization)
    assert ak_layer.parameters.layer_type == LayerType.BatchNormalization
    assert isinstance(layer_bn.a_quantizer, qlayers.WeightQuantizer)
    assert isinstance(layer_bn.b_quantizer, qlayers.AlignedWeightQuantizer)

    # get the QuantizedBatchNormalization a, b and shift
    a_ak = layer_bn.a_quantizer.qweights.value.values.numpy()
    b_quantizer = layer_bn.b_quantizer
    b = b_quantizer.qweights.value.values.numpy().astype(np.int32)
    b_shift = b_quantizer.shift.value.numpy().astype(np.uint8)
    b_ak = (b >> b_shift).astype(np.int8)

    variables_ak = ak_layer.variables

    input_shift = layer_bn.input_shift.value
    if input_shift is not None:
        broadcast_and_set_variable(variables_ak, "input_shift",
                                   input_shift.numpy().astype(np.uint8))

    variables_ak["a"] = a_ak.astype(np.int8)
    variables_ak["b"] = b_ak
    broadcast_and_set_variable(variables_ak, "b_shift", b_shift)

    out_quantizer = getattr(layer_bn, "out_quantizer", False)
    if len(block) > 1:
        relu_layer = block[1]
        set_relu_variables(ak_layer, relu_layer)
        # the effective output_quantizer should be the relu one
        out_quantizer = getattr(relu_layer, "out_quantizer", False)

    if out_quantizer:
        set_output_v2_variables(ak_layer, out_quantizer)


def _create_batchnorm(layer_block):
    """Parses a quantizeml QuantizedBatchNormalization layer and returns the
    params to create the corresponding Akida BatchNormalization layer.

    Args:
        layer (:obj:`tf.keras.Layer`): the quantizeml
            QuantizedBatchNormalization layer to convert.

    Returns:
        :obj:`akida.BatchNormalization`: The created akida layer.
    """
    layer = layer_block[0]
    assert isinstance(layer, qlayers.QuantizedBatchNormalization)
    act_params = {}
    if len(layer_block) > 1:
        act_params = parse_relu_v2(layer_block[1])
    # In quantizeml one bit is reserved for the sign in the buffer bitwidth
    # variable, but in akida this value has to be added back to have the
    # correct clipping.
    buffer_bits = layer.buffer_bitwidth + 1
    # If there is no activation, find out output_bits
    if not act_params:
        out_quantizer = getattr(layer, "out_quantizer", False)
        if out_quantizer:
            act_params['output_bits'] = out_quantizer.bitwidth
        else:
            # Default to buffer bitwidth
            act_params['output_bits'] = buffer_bits

    return BatchNormalization(**act_params,
                              buffer_bits=buffer_bits,
                              name=layer.name)


def convert_batchnorm_block(model_ak, layers):
    """Converts QuantizedBatchNormalization layer and its variables and adds
    it to the Akida's model. If followed by QuantizedReLU, it will set its
    variables too.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be
            added.
        layers (list(:obj:`tf.keras.Layer`)): the remaining model layers to
            convert.

    Return:
        int: the number of converted layers.
    """
    if not layers or not isinstance(layers[0],
                                    qlayers.QuantizedBatchNormalization):
        return 0

    block = [layers[0]]
    if len(layers) > 1 and isinstance(layers[1], qlayers.QuantizedReLU):
        block.append(layers[1])
    layer_ak = _create_batchnorm(block)

    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, layers[0])
    model_ak.add(layer_ak, inbound_layers_ak)
    _set_batchnorm_variables(layer_ak, block)
    return len(block)
