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
"""Functions to convert Conv2DTranspose to Akida.
"""
import numpy as np

from quantizeml.layers import (QuantizedConv2DTranspose, QuantizedReLU,
                               QuantizedMaxPool2D, WeightQuantizer, AlignedWeightQuantizer)
from akida import Conv2DTranspose

from ..akida_versions import AkidaVersion, get_akida_version
from .activations import set_relu_variables
from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables
from .blocks import parse_block_additional_layers, get_block_out_quantizer


def _set_conv2d_transpose_variables(layer_ak, layer_k):
    """Computes and sets the variables for an Akida Conv2DTranspose layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        layer_k (:obj:`tf.keras.Layer`): the source quantized layer.
    """
    assert isinstance(layer_k, QuantizedConv2DTranspose)
    assert isinstance(layer_k.weight_quantizer, WeightQuantizer)
    if layer_k.use_bias:
        assert isinstance(layer_k.bias_quantizer, AlignedWeightQuantizer)

    # Get the weights (Note that in qweights the filter and channel dimensions are already
    # transposed)
    weights = layer_k.weight_quantizer.qweights.value.fp.values.numpy()

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

    # Set input shift if available
    if getattr(layer_k, 'input_shift', None):
        broadcast_and_set_variable(layer_ak.variables, "input_shift",
                                   layer_k.input_shift.value.numpy().astype(np.uint8))


def _parse_conv2d_transpose(layer):
    """Parses a quantizeml.QuantizedConv2DTranspose parameters.

    Args:
        layer (:obj:`tf.keras.Layer`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    assert isinstance(layer, QuantizedConv2DTranspose)

    # Make sure the QuantizedConv2DTranspose kernel size and stride params are square
    assert layer.kernel_size[0] == layer.kernel_size[1], (
        "QuantizedConv2DTranspose kernel_size should be square")
    assert layer.kernel_size[0] in (3, 4)
    assert layer.strides[0] == layer.strides[1], (
        "QuantizedConv2DTranspose strides should be the same on both dimensions.")

    assert layer.strides[0] == 2, ("QuantizedConv2DTranspose handles only stride 2")
    # Padding value must be built in constructor
    assert layer.padding == "same", ("QuantizedConv2DTranspose handles only 'same' padding")
    # The only weight bitwidth supported is [4, 8]
    weight_bits = layer.weight_quantizer.bitwidth
    assert weight_bits in [4, 8]

    # In quantizeml one bit is reserved for the sign in the buffer bitwidth
    # variable, but in akida this value has to be added back to have the
    # correct clipping.
    buffer_bits = layer.buffer_bitwidth + 1

    return dict(
        filters=layer.filters,
        kernel_size=layer.kernel_size[0],
        buffer_bits=buffer_bits,
        activation=False,
        name=layer.name
    )


def convert_conv_transpose_block(model_ak, layers):
    """Converts a convolutional transpose block into an akida Conv2DTranspose layer.

    The expected sequence is:

    - QuantizedConv2DTranspose,
    - QuantizedReLU (optional).

    Args:
        model_ak (:obj:`akida.Model`): the target Akida model.
        layers (list(:obj:`tf.keras.Layer`)): the remaining unconverted keras model layers.

    Returns:
        int: the number of layers in the block or 0 if the first layer is not a
        QuantizedConv2DTranspose.
    """
    if len(layers) == 0 or not isinstance(layers[0], QuantizedConv2DTranspose):
        return 0

    if get_akida_version() == AkidaVersion.v1:
        return 0

    conv_transpose = layers[0]

    # Evaluate the convolutional transpose layer parameters
    conv_transpose_params = _parse_conv2d_transpose(conv_transpose)

    # Identify the next layers
    next_layers = parse_block_additional_layers(layers, conv_transpose_params)

    if len(next_layers) > 1 or next_layers.get(QuantizedMaxPool2D):
        raise RuntimeError("QuantizedConv2DTranspose may only be followed by an optional"
                           " QuantizedReLU")

    # Check if we have ReLU
    relu_layer = next_layers.get(QuantizedReLU, None)

    # Get the layer block output_quantizer
    out_quantizer = get_block_out_quantizer([conv_transpose] + [*next_layers.values()])

    # add output quantizer bitwidth parameter
    if out_quantizer:
        conv_transpose_params["output_bits"] = out_quantizer.bitwidth
    else:
        conv_transpose_params["output_bits"] = conv_transpose_params["buffer_bits"]

    # Create Akida layer
    conv_transpose_ak = Conv2DTranspose(**conv_transpose_params)
    # Add layer to the model to build its internal variables
    model_ak.add(conv_transpose_ak)

    # Set base variables
    _set_conv2d_transpose_variables(conv_transpose_ak, conv_transpose)

    # Set optional activation variables
    if relu_layer:
        set_relu_variables(conv_transpose_ak, relu_layer)

    # Set optional output_quantizer variables
    if out_quantizer:
        set_output_v2_variables(conv_transpose_ak, out_quantizer)

    return 1 + len(next_layers)
