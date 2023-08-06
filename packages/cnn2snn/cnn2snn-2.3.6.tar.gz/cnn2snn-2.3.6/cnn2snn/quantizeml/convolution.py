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
"""Functions to convert QuantizedConv2D to Akida.
"""
import numpy as np

from quantizeml.layers import (QuantizedConv2D, QuantizedReLU, QuantizedGlobalAveragePooling2D,
                               WeightQuantizer, AlignedWeightQuantizer)
from akida import InputConvolutional, Convolutional, LayerType, Conv2D, InputConv2D

from ..akida_versions import AkidaVersion, get_akida_version
from .activations import set_relu_variables
from .pooling import set_pooling_variables
from .outputs import set_output_v1_variables, set_output_v2_variables
from .padding import get_padding_info
from .blocks import parse_block_additional_layers, get_block_out_quantizer
from .weights import broadcast_and_set_variable


def _set_conv2d_variables(layer_ak, layer_k):
    """Computes and sets the variables for an Akida convolutional layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        layer_k (:obj:`tf.keras.Layer`): the source quantized layer.
    """
    assert isinstance(layer_k, QuantizedConv2D)
    assert isinstance(layer_k.weight_quantizer, WeightQuantizer)
    if layer_k.use_bias:
        assert isinstance(layer_k.bias_quantizer, AlignedWeightQuantizer)

    # Get the weights
    weights = layer_k.weight_quantizer.qweights.value.fp.values.numpy()
    if layer_ak.parameters.layer_type in (LayerType.Convolutional, LayerType.Conv2D):
        # Flip W and H dimensions for conv. kernels (not input conv.)
        weights = np.flip(weights, axis=[0, 1])
    layer_ak.variables["weights"] = weights.astype(np.int8)

    # Set the bias (if there is one)
    if layer_k.use_bias:
        bias_quantizer = layer_k.bias_quantizer
        bias = bias_quantizer.qweights.value.values.numpy().astype(np.int32)
        bias_shift = bias_quantizer.shift.value.numpy().astype(np.uint8)
        target_version = get_akida_version()
        if target_version == AkidaVersion.v1:
            # Store bias into the threshold variable
            layer_ak.variables["threshold"] = -bias
        else:
            # Unshift the bias and store it
            layer_ak.variables["bias"] = (bias >> bias_shift).astype(np.int8)
            # Also store the bias shift
            broadcast_and_set_variable(layer_ak.variables, "bias_shift", bias_shift)

            input_shift = getattr(layer_k, 'input_shift', None)
            if input_shift is not None:
                broadcast_and_set_variable(layer_ak.variables, "input_shift",
                                           input_shift.value.numpy().astype(np.uint8))


def _parse_convolutional(layer):
    """Parses a quantizeml.QuantizedConv2D parameters.

    Args:
        layer (:obj:`tf.keras.Layer`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    assert isinstance(layer, QuantizedConv2D)

    # Padding value must be built in constructor
    padding, padding_value = get_padding_info(layer)

    # The only weight bitwidth supported is [4, 8]
    weight_bits = layer.weight_quantizer.bitwidth
    assert weight_bits in [4, 8]

    conv_params = dict(
        input_shape=tuple(int(x) for x in layer.input_shape[1:4]),
        padding=padding,
        padding_value=padding_value,
        kernel_size=(layer.kernel_size[0], layer.kernel_size[1]),
        filters=int(layer.kernel.shape[3]),
        weights_bits=layer.weight_quantizer.bitwidth,
        kernel_stride=(layer.strides[0], layer.strides[1]),
        activation=False,
        name=layer.name
    )

    if get_akida_version() == AkidaVersion.v2:
        # Conv2D layer has no weight bits, nor padding_value params
        conv_params.pop("weights_bits", None)

        # Make sure the Conv2D layers spatial params are square
        assert layer.kernel_size[0] == layer.kernel_size[1], ("Conv2D and InputConv2D handle only"
                                                              "square kernels")
        conv_params.update({"kernel_size": layer.kernel_size[0]})
        assert layer.strides[0] == layer.strides[1], ("For Conv2D and InputConv2D stride should be"
                                                      "the same for both dimensions")
        conv_params.update({"kernel_stride": layer.strides[0]})

        # In quantizeml one bit is reserved for the sign in the buffer bitwidth
        # variable, but in akida this value has to be added back to have the
        # correct clipping.
        buffer_bits = layer.buffer_bitwidth + 1
        conv_params["buffer_bits"] = buffer_bits
        # Find out if there is a quantizer
        out_quantizer = getattr(layer, "out_quantizer", False)

        if out_quantizer:
            conv_params["output_bits"] = out_quantizer.bitwidth
        else:
            conv_params["output_bits"] = buffer_bits
    return conv_params


def convert_conv_block(model_ak, layers):
    """Converts an convolutional block into an akida convolutional layer.

    The expected sequence is:

    - QuantizedConv2D,
    - QuantizedMaxPooling2D (optional),
    - QuantizedRelU (optional).

    Args:
        model_ak (:obj:`akida.Model`): the target Akida model.
        layers (list(:obj:`tf.keras.Layer`)): the block layers.

    Return:
        int: the number of layers in the block or O if the first layer is not a QuantizedConv2D.
    """
    if len(layers) == 0 or not isinstance(layers[0], QuantizedConv2D):
        return 0

    conv = layers[0]

    # Evaluate the convolutional layer parameters
    conv_params = _parse_convolutional(conv)
    next_layers = parse_block_additional_layers(layers, conv_params)

    if len(model_ak.layers) == 0 and conv_params["input_shape"][-1] in [1, 3]:
        if get_akida_version() == AkidaVersion.v1:
            conv_ak = InputConvolutional(**conv_params)
        else:
            conv_ak = InputConv2D(**conv_params)
    elif len(model_ak.layers) != 0:
        # A Convolutional should be added if there is a previous layer (like InputData).
        # Unlike InputConvolutional or InputConv2D, Convolutional and Conv2D do not receive
        #  the following parameters:
        for no_param in ["input_shape", "padding_value"]:
            conv_params.pop(no_param, None)
        if get_akida_version() == AkidaVersion.v1:
            conv_ak = Convolutional(**conv_params)
        else:
            conv_ak = Conv2D(**conv_params)
    else:
        # Convert loop will manage the other cases
        return 0

    # Add layer to the model to build its internal variables
    model_ak.add(conv_ak)
    # Set base variables
    _set_conv2d_variables(conv_ak, conv)

    # Check if we have ReLU or GAP
    pool_layer = next_layers.get(QuantizedGlobalAveragePooling2D, None)
    if pool_layer:
        set_pooling_variables(conv_ak, pool_layer)
    relu_layer = next_layers.get(QuantizedReLU, None)
    if relu_layer:
        if get_akida_version() == AkidaVersion.v2:
            # Set the optional activation variables
            set_relu_variables(conv_ak, relu_layer)

    # Get out_quantizer of the block.
    out_quantizer = get_block_out_quantizer([conv] + list(next_layers.values()))

    if out_quantizer:
        if isinstance(conv_ak, (InputConvolutional, Convolutional)):
            set_output_v1_variables(conv_ak, out_quantizer)
        else:
            set_output_v2_variables(conv_ak, out_quantizer)

    return 1 + len(next_layers)
