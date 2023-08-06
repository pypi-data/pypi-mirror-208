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
"""Functions to convert QuantizedDepthwiseConv2D to Akida.
"""
import numpy as np

from quantizeml.layers import (QuantizedDepthwiseConv2D, QuantizedReLU,
                               WeightQuantizer, AlignedWeightQuantizer)
from akida import DepthwiseConv2D

from ..akida_versions import AkidaVersion, get_akida_version
from .activations import set_relu_variables
from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables
from .padding import get_padding_info
from .blocks import parse_block_additional_layers


def _set_depthwise_conv2d_variables(layer_ak, layer_k):
    """Computes and sets the variables for an Akida DepthwiseConv2D layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        layer_k (:obj:`tf.keras.Layer`): the source quantized layer.
    """
    assert isinstance(layer_k, QuantizedDepthwiseConv2D)
    assert isinstance(layer_k.weight_quantizer, WeightQuantizer)
    if layer_k.use_bias:
        assert isinstance(layer_k.bias_quantizer, AlignedWeightQuantizer)

    # Get the weights
    weights = layer_k.weight_quantizer.qweights.value.fp.values.numpy()
    # Flip W and H dimensions for depthwise
    weights = np.flip(weights, axis=[0, 1])

    layer_ak.variables["weights"] = weights.astype(np.int8)

    # Set the bias (if there is one)
    if layer_k.use_bias:
        bias_quantizer = layer_k.bias_quantizer
        bias = bias_quantizer.qweights.value.values.numpy().astype(np.int32)
        bias_shift = bias_quantizer.shift.value.numpy().astype(np.uint8)

        # Unshift the bias and store it
        layer_ak.variables["bias"] = (bias >> bias_shift).astype(np.int8)
        # Also store the bias shift
        broadcast_and_set_variable(layer_ak.variables, "bias_shift", bias_shift)

    # Set input shift
    input_shift = getattr(layer_k, 'input_shift', None)
    if input_shift is not None:
        broadcast_and_set_variable(layer_ak.variables, "input_shift",
                                   layer_k.input_shift.value.numpy().astype(np.uint8))


def _parse_depthwise_conv(layer):
    """Parses a quantizeml.QuantizedDepthwiseConv2D parameters.

    Args:
        layer (:obj:`tf.keras.Layer`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    assert isinstance(layer, QuantizedDepthwiseConv2D)

    # Make sure the DepthwiseConv2D kernel size and stride params are square
    assert layer.kernel_size[0] == layer.kernel_size[1], (
        "DepthwiseConv2D kernel_size should be square")
    assert layer.strides[0] == layer.strides[1], (
        "DepthwiseConv2D strides should be the same on both dimension")

    # Padding value must be built in constructor
    padding, _ = get_padding_info(layer)

    # The only weight bitwidth supported is [4, 8]
    weight_bits = layer.weight_quantizer.bitwidth
    assert weight_bits in [4, 8]

    # In quantizeml one bit is reserved for the sign in the buffer bitwidth
    # variable, but in akida this value has to be added back to have the
    # correct clipping.
    buffer_bits = layer.buffer_bitwidth + 1

    return dict(
        kernel_size=layer.kernel_size[0],
        kernel_stride=layer.strides[0],
        padding=padding,
        buffer_bits=buffer_bits,
        activation=False,
        name=layer.name
    )


def convert_depthwise_conv_block(model_ak, layers):
    """Converts a depthwise convolutional block into an akida DepthwiseConv2D layer.

    The expected sequence is:

    - QuantizedDepthwiseConv2D,
    - QuantizedMaxPool2D (optional),
    - QuantizedReLU (optional).

    Args:
        model_ak (:obj:`akida.Model`): the target Akida model.
        layers (list(:obj:`tf.keras.Layer`)): the block layers.

    Return:
        int: the number of layers in the block or O if the first layer is not a
        QuantizedDepthwiseConv2D.
    """
    if len(layers) == 0 or not isinstance(layers[0], QuantizedDepthwiseConv2D):
        return 0

    if get_akida_version() == AkidaVersion.v1:
        return 0

    dw_conv = layers[0]

    # Evaluate the depthwise convolutional layer parameters
    conv_params = _parse_depthwise_conv(dw_conv)

    # Identify the next layers
    next_layers = parse_block_additional_layers(layers, conv_params)
    # Check if we have ReLU or MaxPool
    relu_layer = next_layers.get(QuantizedReLU, None)

    if relu_layer:
        # Output quantizer should be in ReLU layer
        out_quantizer = getattr(relu_layer, "out_quantizer", False)
    else:
        # otherwise, output quantize is in the conv layer
        out_quantizer = getattr(dw_conv, "out_quantizer", False)

    # add output quantizer bitwidth parameter
    if out_quantizer:
        conv_params["output_bits"] = out_quantizer.bitwidth
    else:
        conv_params["output_bits"] = conv_params["buffer_bits"]

    # Create Akida layer
    dw_conv_ak = DepthwiseConv2D(**conv_params)
    # Add layer to the model to build its internal variables
    model_ak.add(dw_conv_ak)

    # Set base variables
    _set_depthwise_conv2d_variables(dw_conv_ak, dw_conv)

    # Set optional activation variables
    if relu_layer:
        set_relu_variables(dw_conv_ak, relu_layer)

    # Set optional output_quantizer variables
    if out_quantizer:
        set_output_v2_variables(dw_conv_ak, out_quantizer)

    return 1 + len(next_layers)
