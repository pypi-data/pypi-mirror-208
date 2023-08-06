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
"""Utility function to convert block layers to akida.
"""
from quantizeml.layers import (QuantizedMaxPool2D,
                               QuantizedGlobalAveragePooling2D,
                               QuantizedReLU,
                               QuantizedExtractToken,
                               Dequantizer)

from .pooling import parse_max_pooling, parse_global_average_pooling
from .activations import parse_relu_v1, parse_relu_v2
from ..akida_versions import AkidaVersion, get_akida_version


def parse_block_additional_layers(layers, block_params):
    """Parse block additional layers into the parameters of one.

    In Akida v1, we are able to manage this sequence of layers:

    - QuantizedMaxPooling2D or QuantizedGlobalAveragePooling2D
    - QuantizedReLU.

    In v2, the possible sequences are:

    - QuantizedMaxPooling2D
    - QuantizedReLU

    or:

    - QuantizedReLU
    - QuantizedGlobalAveragePooling2D

    Args:
        layers (list(:obj:`tf.keras.Layer`)): the layers block.
        block_params (dict): the current block parameters.

    Returns:
        dict: additional layers found in the process, with layer type as key
    """
    # Identify the next layers
    next_layers = {}
    akida_version = get_akida_version()
    if akida_version == AkidaVersion.v1:
        layer_types = [QuantizedMaxPool2D, QuantizedGlobalAveragePooling2D, QuantizedReLU]
    else:
        layer_types = [QuantizedMaxPool2D, QuantizedReLU, QuantizedGlobalAveragePooling2D]
    index = 1
    while index < len(layers) and layer_types:
        layer_type = layer_types.pop(0)
        layer = layers[index]
        if isinstance(layer, layer_type):
            next_layers[layer_type] = layer
            index += 1

    relu_layer = next_layers.get(QuantizedReLU, None)
    max_pool_layer = next_layers.get(QuantizedMaxPool2D, None)
    global_average_pool_layer = next_layers.get(QuantizedGlobalAveragePooling2D, None)

    if len(next_layers) == 1 and max_pool_layer:
        raise RuntimeError("Unsupported configuration: a maxpool requires an activation.")

    # Evaluate the neural layer parameters
    neural_name = layers[0].name
    if getattr(layers[0], "out_quantizer", False) and len(next_layers) > 0:
        raise RuntimeError(f"{neural_name} layer is followed by a pool/activation layer."
                           "It should not have an output_quantizer.")

    if max_pool_layer:
        pool_params = parse_max_pooling(max_pool_layer)
        # Padding checked on check_compatibility_model()
        block_params.update(pool_params)
    if global_average_pool_layer:
        pool_params = parse_global_average_pooling(global_average_pool_layer)
        block_params.update(pool_params)
    if relu_layer:
        # TODO: Remove the dependence to the akida_version when the conv block conversion
        # will be done with it proper ConvBlockConverter
        if akida_version == AkidaVersion.v1:
            act_params = parse_relu_v1(relu_layer)
        else:
            act_params = parse_relu_v2(relu_layer)
        block_params.update(act_params)

    return next_layers


def split_model_into_blocks(model):
    """Search into the model the sets of possible blocks and return them.

    A set of layers are considered as block if:
        1. There is only one output quantizer (in the last layer of the block)
        2. There are no multi-inbound layers
        3. There are no QuantizedExtractToken layers

    Layers with more than one inbound layer will be handled separately.

    Args:
        model (:obj:`tf.models.Model`): The model to split

    Returns:
        list: a list of sequences of layers ('blocks').
    """
    def _get_inbound_layers(target_layer):
        inbound = target_layer.inbound_nodes[0].inbound_layers
        return inbound if isinstance(inbound, (list, tuple)) else [inbound]

    def _check_single_layer_block(target_layer):
        # Single blocks will be multi-inputs and QuantizedExtractToken
        prev_layers = _get_inbound_layers(target_layer)
        if len(prev_layers) > 1:
            return True
        if isinstance(target_layer, QuantizedExtractToken):
            return True
        return False

    def _search_block_v1(target_layer):
        # We consider the target is part of one block if there are previous
        # layers. (Akida v1 doesn't support multi inbound layers)
        prev_layers = _get_inbound_layers(target_layer)
        # If it's the first layer return it
        if len(prev_layers) == 0:
            return [target_layer]

        # If previous layer has an output quantizer, the blocks end here.
        next_target = prev_layers[0]
        out_quantizer = getattr(next_target, "out_quantizer", None)
        if out_quantizer:
            if not isinstance(next_target, QuantizedReLU):
                raise RuntimeError("Model incompatible with akida v1 version. The layer"
                                   f" {next_target.name} followed by {target_layer.name}"
                                   " is not valid.")
            return [target_layer]

        # Otherwise, we continue searching...
        return _search_block_v1(next_target) + [target_layer]

    def _search_block_v2(target_layer):
        # We consider the target is part of one block if there are previous
        # layers (target is not the model's input), or it's multi-inbound.
        prev_layers = _get_inbound_layers(target_layer)
        if len(prev_layers) != 1:
            return [target_layer]
        # If previous layer has an output quantizer, the blocks end here.
        next_target = prev_layers[0]
        out_quantizer = getattr(next_target, "out_quantizer", None)
        if out_quantizer or _check_single_layer_block(next_target):
            return [target_layer]

        # Otherwise, we continue searching...
        return _search_block_v2(next_target) + [target_layer]

    def _search_block(layer):
        return _search_block_v1(layer) if get_akida_version() == AkidaVersion.v1 \
            else _search_block_v2(layer)

    def _get_layers_before_dequantizer(model):
        # Return layers before the first dequantizer
        layers = []
        last_deq_layer = None
        for layer in model.layers:
            if isinstance(layer, Dequantizer):
                last_deq_layer = layer
                break
            layers.append(layer)
        return last_deq_layer, layers

    def _is_end_of_block(layer, blocks):
        # Return true if the layer is the end of a new block.
        # The very last layer is the end of another block
        if not blocks:
            return True
        outbounds = layer.outbound_nodes
        # If there are many outbounds, this is an end of block
        if len(outbounds) > 1:
            return True
        # Prepare a list of all first layers of all blocks
        first_layers = [block[0] for block in blocks]
        outbound = outbounds[0].outbound_layer
        return outbound in first_layers

    blocks = []
    # If there is a Dequantizer, save the first one as single block layer and then
    # remove all layers after it (not supported at conversion time)
    deq_layer, model_layers = _get_layers_before_dequantizer(model)
    if deq_layer:
        blocks.append([deq_layer])

    # We forward from head to bottom
    for layer in model_layers[::-1]:
        if _is_end_of_block(layer, blocks):
            new_block = _search_block(layer)
            blocks.append(new_block)
        # The skip layers must be inside of one block
        elif layer not in sum(blocks, []):
            raise RuntimeError(f"Impossible to append {layer.name} into a block.")

    # At the end, we sort blocks from bottom to head
    return blocks[::-1]


def get_block_out_quantizer(block):
    """Extract the output_quantizer of the layers block.

    Note that a block of layers is considered as block if:
        1. There is only one output quantizer (in the last layer of the block)
        2. There are no multi-inbound layers
        3. There are no QuantizedExtractToken layers

    This method should ideally be called after "split_model_into_blocks" to make sure
    that the layers block can be handled correctly.

    Args:
        block (list(:obj:`tf.keras.Layer`)): the layers block.

    Returns:
        :obj:`quantizeml.layers.OutputQuantizer`: the layers block output quantizer (None if the
            block has no output quantizer)
    """
    # Output quantizer is on the last layer of the block
    return getattr(block[-1], "out_quantizer", None)
