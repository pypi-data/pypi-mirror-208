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
"""Functions to convert keras activation layers parameters and variables to akida.
"""
import numpy as np
from quantizeml.layers import QuantizedReLU, AlignedWeightQuantizer, OutputQuantizer
from .weights import broadcast_and_set_variable
from ..akida_versions import AkidaVersion, get_akida_version


def v1_relu_checks(layer):
    """Additionnal checks on QuantizedReLU layers of akida v1 models.

    Args:
        layer (:obj:`tf.keras.Layer`): the QuantizedReLU layer to check.
    """
    assert isinstance(layer.max_value_quantizer, AlignedWeightQuantizer)
    lname = layer.name
    # Check if there is an output_quantizer
    out_quantizer = getattr(layer, "out_quantizer", None)
    if not out_quantizer:
        raise ValueError(f"{lname}: in AkidaVersion.v1, output_quantizer is mandatory.")
    assert isinstance(out_quantizer, OutputQuantizer)
    if out_quantizer._axis == "per-axis":
        raise ValueError(f"{lname}: in AkidaVersion.v1, output_quantizer must be per-tensor.")


def parse_relu_v1(layer_k):
    """Parses the quantizeml.QuantizedReLU parameters for Akida v1 layers.

    Args:
        layer_k (:obj:`tf.keras.Layer`): the QuantizedReLU layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    # Check if there is an output_quantizer
    out_quantizer = getattr(layer_k, "out_quantizer", None)

    return {'activation': True, 'act_bits': out_quantizer.bitwidth}


def parse_relu_v2(layer_k):
    """Parses the quantizeml.QuantizedReLU parameters for Akida v2 layers.

    Args:
        layer_k (:obj:`tf.keras.Layer`): the QuantizedReLU layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    assert isinstance(layer_k.max_value_quantizer, AlignedWeightQuantizer)

    # Check if there is an output_quantizer
    out_quantizer = getattr(layer_k, "out_quantizer", None)

    if not out_quantizer:
        return {'activation': True}

    assert isinstance(out_quantizer, OutputQuantizer)
    return {'activation': True, 'output_bits': out_quantizer.bitwidth}


def set_relu_variables(layer_ak, layer_k):
    """Computes and sets the activation variables in an akida layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        layer_k (:obj:`quantizeml.QuantizedRelu`): the source QuantizedReLU layer.
    """
    # Nothing to do in AkidaVersion.v1 : the values will be modified by
    # :func:`set_output_v1_variables`.
    # TODO: remove this checks once the conversion pipeline uses only BlockConverter
    if get_akida_version() == AkidaVersion.v1:
        return

    assert isinstance(layer_k, QuantizedReLU)

    variables_ak = layer_ak.variables

    max_value_quantizer = layer_k.max_value_quantizer
    assert isinstance(max_value_quantizer, AlignedWeightQuantizer)
    max_value = max_value_quantizer.qweights.value.values.numpy().astype(np.int32)
    max_value_shift = max_value_quantizer.shift.value.numpy().astype(np.uint8)
    max_value_ak = (max_value >> max_value_shift).astype(np.uint8)
    broadcast_and_set_variable(variables_ak, "max_value", max_value_ak)
    broadcast_and_set_variable(variables_ak, "max_value_shift", max_value_shift)
