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
"""Functions to convert QuantizedAdd to Akida.
"""
from akida import LayerType, Add
import quantizeml.layers as qlayers
import numpy as np

from .layer_utils import get_inbound_layers
from .weights import broadcast_and_set_variable


def _set_add_variables(ak_layer, k_layer):
    """Computes and sets the variables for an Akida Add layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        k_layer (:obj:`tf.keras.Layer`): the source quantized layer.
    """
    assert isinstance(k_layer, qlayers.QuantizedAdd)
    assert ak_layer.parameters.layer_type == LayerType.Add

    variables_ak = ak_layer.variables

    a_shift = k_layer.a_shift.value.numpy().astype(np.uint8)
    broadcast_and_set_variable(variables_ak, "a_shift", a_shift)
    b_shift = k_layer.b_shift.value.numpy().astype(np.uint8)
    broadcast_and_set_variable(variables_ak, "b_shift", b_shift)

    out_quantizer = getattr(k_layer, "out_quantizer", False)
    if out_quantizer:
        assert isinstance(out_quantizer, qlayers.OutputQuantizer)
        out_shift = out_quantizer.shift.value.numpy().astype(np.int8)
        variables_ak["output_shift"] = out_shift


def _create_add(layer):
    """Parses a quantizeml QuantizedAdd layer and returns the corresponding
    Akida Add layer.

    Args:
        layer (:obj:`tf.keras.Layer`): the quantizeml QuantizedAdd layer to convert.

    Returns:
        :obj:`akida.Add`: The created akida layer.
    """
    assert isinstance(layer, qlayers.QuantizedAdd)
    # In quantizeml one reserves automaticaly one bit for the sign, but in akida
    # this is rather checked during the clipping operations.
    buffer_bits = layer.buffer_bitwidth + 1
    if getattr(layer, 'out_quantizer', False):
        output_bits = layer.out_quantizer.bitwidth
    else:
        output_bits = buffer_bits
    return Add(output_bits=output_bits,
               buffer_bits=buffer_bits,
               name=layer.name)


def convert_quantized_add(model_ak, layer_k):
    """Converts QuantizedAdd layer and its variables and adds it to the
    Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        layer_k (:obj:`tf.keras.Layer`): the quantizeml QuantizedAdd layer to convert.
    """
    if not isinstance(layer_k, qlayers.QuantizedAdd):
        raise TypeError(f"Layer {layer_k.name} was expected to be "
                        "QuantizedAdd")
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, layer_k)
    # Create and add layer to the akida model
    layer_ak = _create_add(layer_k)
    model_ak.add(layer_ak, inbound_layers_ak)
    # Set the akida layer converted variables
    _set_add_variables(layer_ak, layer_k)
