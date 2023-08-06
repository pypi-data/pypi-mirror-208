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
"""Functions to convert QuantizedSeparableConv2D to Akida.
"""
import numpy as np

from akida import LayerType, SeparableConvolutional
from quantizeml.layers import (QuantizedSeparableConv2D, QuantizedGlobalAveragePooling2D,
                               WeightQuantizer, AlignedWeightQuantizer)

from ..akida_versions import AkidaVersion, get_akida_version
from .pooling import set_pooling_variables
from .outputs import set_output_v1_variables
from .padding import get_padding_info
from .blocks import parse_block_additional_layers, get_block_out_quantizer


def _set_sepconv_variables(ak_layer, k_layer):
    """Computes and sets the variables for an Akida SeparableConvolutional layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        k_layer (:obj:`tf.keras.Layer`): the source quantized layer.
    """
    assert isinstance(k_layer, QuantizedSeparableConv2D)
    assert ak_layer.parameters.layer_type == LayerType.SeparableConvolutional
    assert isinstance(k_layer.dw_weight_quantizer, WeightQuantizer)
    assert isinstance(k_layer.pw_weight_quantizer, WeightQuantizer)

    variables_ak = ak_layer.variables

    # Get the QuantizedSeparableConv2D weights
    weights_ak = k_layer.dw_weight_quantizer.qweights.value.fp.values.numpy()
    weights_pw_ak = k_layer.pw_weight_quantizer.qweights.value.fp.values.numpy()
    # We require flip depthwise weights
    weights_ak = np.flip(weights_ak, axis=[0, 1])

    # Get the QuantizedSeparableConv2D bias
    if k_layer.use_bias:
        bias_quantizer = k_layer.bias_quantizer
        assert isinstance(bias_quantizer, AlignedWeightQuantizer)
        bias = bias_quantizer.qweights.value.values.numpy().astype(np.int32)
        # Store bias into the threshold variable
        variables_ak["threshold"] = -bias

    variables_ak["weights"] = weights_ak.astype(np.int8)
    variables_ak["weights_pw"] = weights_pw_ak.astype(np.int8)


def _parse_sepconv(layer):
    """Parses a quantizeml.SeparableConvolutional parameters.

    Args:
        layer (:obj:`tf.keras.Layer`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """

    assert isinstance(layer, QuantizedSeparableConv2D)

    # The only weight bitwidth supported is 4
    weight_bits = layer.dw_weight_quantizer.bitwidth
    assert weight_bits == 4 and weight_bits == layer.pw_weight_quantizer.bitwidth

    # Padding value must be built in constructor
    padding, _ = get_padding_info(layer)

    sepconv_params = dict(kernel_size=(layer.kernel_size[0], layer.kernel_size[1]),
                          filters=int(layer.pointwise_kernel.shape[3]),
                          padding=padding,
                          kernel_stride=(layer.strides[0], layer.strides[1]),
                          weights_bits=weight_bits,
                          activation=False,
                          name=layer.name)
    return sepconv_params


def convert_sepconv_block(model_ak, layers):
    """Converts a separable convolutional block into an akida SeparableConvolutional layer.

    The expected sequence is:

        - QuantizedSeparableConv2D,
        - QuantizedMaxPooling2D (optional),
        - QuantizedReLU (optional).

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        layers (list(:obj:`tf.keras.Layer`)): the remaining model layers to convert.

    Return:
        int: the number of layers in the block or O if the first layer is not a
            QuantizedSeparableConv2D.
    """
    if len(layers) == 0 or not isinstance(layers[0], QuantizedSeparableConv2D):
        return 0

    if get_akida_version() == AkidaVersion.v2:
        return 0

    if len(model_ak.layers) == 0:
        raise RuntimeError("An InputData layer is required previous to add a new SeparableConv2D.")

    sepconv = layers[0]

    # Evaluate the separable convolutional layer parameters
    sepconv_params = _parse_sepconv(sepconv)
    next_layers = parse_block_additional_layers(layers, sepconv_params)

    # Create the Akida SeparableConv2D layer
    sepconv_ak = SeparableConvolutional(**sepconv_params)

    # Add layer to the model to build its internal variables
    model_ak.add(sepconv_ak)

    # Set variables
    _set_sepconv_variables(sepconv_ak, sepconv)
    pool_layer = next_layers.get(QuantizedGlobalAveragePooling2D, None)
    if pool_layer:
        set_pooling_variables(sepconv_ak, pool_layer)
    out_quantizer = get_block_out_quantizer([sepconv] + list(next_layers.values()))
    if out_quantizer:
        set_output_v1_variables(sepconv_ak, out_quantizer)

    return 1 + len(next_layers)
