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
"""Functions to update akida layer output variables from a keras OutputQuantizer.
"""
import numpy as np
from quantizeml.layers import OutputQuantizer
from quantizeml.tensors import pow2
from .weights import broadcast_and_set_variable


def set_output_v1_variables(layer_ak, out_quantizer):
    """Computes and sets the output variables in an akida v1 layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida v1 layer.
        out_quantizer (:obj:`quantizeml.OutputQuantizer`): the source output quantizer.
    """
    assert isinstance(out_quantizer, OutputQuantizer)

    # Extract the OutputQuantizer variables
    scales = out_quantizer.qscales.value.values
    shift = out_quantizer.shift.value

    # Quantizeml evaluates the outputs as: y = x * scales * 2^shift
    # Calculate the float activation step, as the reciprocal of (scales * 2^shift)
    scales_rec = (pow2(-shift) / scales).numpy().astype(np.float32)
    # In akida 1.0, the outputs are evaluated as: y = x / act_step
    layer_ak.variables["act_step"] = scales_rec
    if layer_ak.parameters.activation:
        # For activations, x is decreased by half the activations step before division
        # to increase the precision. This is obtained by increasing the threshold.
        layer_ak.variables["threshold"] += np.round(0.5 * scales_rec).astype(np.int32)
        # Adjust activation step to match activation formula
        act_bits = layer_ak.parameters.act_bits
        layer_ak.variables["act_step"] *= 2 ** (act_bits - 4)


def set_output_v2_variables(layer_ak, out_quantizer):
    """Computes and sets the output variables in an akida v2 layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida v2 layer.
        out_quantizer (:obj:`quantizeml.OutputQuantizer`): the source output quantizer.
    """
    assert isinstance(out_quantizer, OutputQuantizer)

    # Extract the OutputQuantizer variables
    scales = out_quantizer.qscales.value.values
    shift = out_quantizer.shift.value

    output_scales = scales.numpy().astype(np.uint8)
    broadcast_and_set_variable(layer_ak.variables, "output_scales",
                               output_scales)
    broadcast_and_set_variable(layer_ak.variables, "output_shift",
                               shift.numpy().astype(np.int8))
