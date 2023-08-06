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
"""Functions to convert QuantizedLayerNormalization to Akida.
"""
from akida import LayerType, MadNorm
import quantizeml.layers as qlayers
import numpy as np

from .layer_utils import get_inbound_layers
from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables


def _set_madnorm_variables(ak_layer, k_layer):
    """Computes and sets the variables for an Akida MadNorm layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        k_layer (:obj:`tf.keras.Layer`): the source quantized layer.
    """
    assert isinstance(k_layer, qlayers.QuantizedLayerNormalization)
    assert ak_layer.parameters.layer_type == LayerType.MadNorm
    assert isinstance(k_layer.gamma_quantizer, qlayers.WeightQuantizer)
    assert isinstance(k_layer.beta_quantizer, qlayers.AlignedWeightQuantizer)

    # get the QuantizedLayerNormalization gamma and shift
    gamma_ak = k_layer.gamma_quantizer.qweights.value.values.numpy()
    gamma_shift = k_layer.gamma_shift.value.numpy().astype(np.uint8)
    # get the QuantizedLayerNormalization beta and shift
    beta_quantizer = k_layer.beta_quantizer
    beta = beta_quantizer.qweights.value.values.numpy().astype(np.int32)
    beta_shift = beta_quantizer.shift.value.numpy().astype(np.uint8)
    beta_ak = (beta >> beta_shift).astype(np.int8)

    variables_ak = ak_layer.variables

    input_shift = getattr(k_layer, 'input_shift', None)
    if input_shift is not None:
        if np.any(input_shift.value < 0):
            raise RuntimeError(
                f"Layer {k_layer.name} contains negative values for " +
                "input_shift, that is not supported")
        broadcast_and_set_variable(variables_ak, "input_shift",
                                   input_shift.value.numpy().astype(np.uint8))
    variables_ak["gamma"] = gamma_ak.astype(np.int8)
    broadcast_and_set_variable(variables_ak, "gamma_shift", gamma_shift)
    variables_ak["beta"] = beta_ak.astype(np.int8)
    broadcast_and_set_variable(variables_ak, "beta_shift", beta_shift)
    out_quantizer = getattr(k_layer, "out_quantizer", False)
    if out_quantizer:
        set_output_v2_variables(ak_layer, out_quantizer)


def _create_madnorm(layer):
    """Parses a quantizeml QuantizedLayerNormalization layer and returns the
    params to create the corresponding Akida MadNorm layer.

    Args:
        layer (:obj:`tf.keras.Layer`): the quantizeml QuantizedLayerNormalization layer to convert.

    Returns:
        :obj:`akida.MadNorm`: The created akida layer.
    """
    assert isinstance(layer, qlayers.QuantizedLayerNormalization)

    # Find out if there is a quantizer
    out_quantizer = getattr(layer, "out_quantizer", False)
    # In quantizeml one bit is reserved automatically for the sign, but in
    # akida this is rather checked during the clipping operations.
    buffer_bits = layer.buffer_bitwidth + 1
    if out_quantizer:
        output_bits = out_quantizer.bitwidth
    else:
        # Default to buffer bitwidth
        output_bits = buffer_bits

    return MadNorm(output_bits=output_bits,
                   buffer_bits=buffer_bits,
                   name=layer.name)


def convert_quantized_madnorm(model_ak, layer_k):
    """Converts QuantizedLayerNormalization layer and its variables and adds
    it to the Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        layer_k (:obj:`tf.keras.Layer`): the quantizeml QuantizedLayerNormalization
            layer to convert.
    """
    if not isinstance(layer_k, qlayers.QuantizedLayerNormalization):
        raise TypeError(f"Layer {layer_k.name} was expected to be "
                        "QuantizedLayerNormalization")
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, layer_k)
    # Create and add layer to the akida model
    layer_ak = _create_madnorm(layer_k)
    model_ak.add(layer_ak, inbound_layers_ak)
    # Set the akida layer converted variables
    _set_madnorm_variables(layer_ak, layer_k)
