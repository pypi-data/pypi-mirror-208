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
"""Functions to convert Dequantizer to Akida.
"""
import numpy as np

import akida
from quantizeml.layers import Dequantizer

from .weights import broadcast_and_set_variable
from ..akida_versions import AkidaVersion, get_akida_version


def _set_dequantizer_variables(layer_ak, dequantizer):
    """Computes and sets the dequantizer recorded variables into the akida layer

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        dequantizer (:obj:`quantizeml.Dequantizer`): the source quantizeml layer.
    """
    assert isinstance(dequantizer, Dequantizer)

    # Extract the Dequantizer variables
    frac_bits = dequantizer.frac_bits
    scales = dequantizer.scales
    if isinstance(frac_bits, (list, tuple)):
        if len(frac_bits) > 1:
            raise RuntimeError(f"Multi-inbounds in {dequantizer.name} is not supported.")
        frac_bits = frac_bits[0]
        scales = scales[0] if scales else None

    # We project the frac_bits into the scales as:
    #   new_scales = scales / 2 ** frac_bits
    scales = scales.value if scales else 1.0
    scales /= 2**frac_bits.value
    scales = scales.numpy().astype(np.float32)

    # Depending on ak_version:
    layer_variables = layer_ak.variables
    if get_akida_version() == AkidaVersion.v1:
        # We should not modify the activation step if the model ends with an activation
        if layer_ak.parameters.activation == 1:
            return
        # Project scales in the final layer activation step
        params = ("act_step", layer_variables["act_step"] / scales)
    else:
        # Set scales in the independant layer
        assert layer_ak.parameters.layer_type == akida.LayerType.Dequantizer
        params = ("scales", scales)
    broadcast_and_set_variable(layer_variables, *params)


def convert_dequantizer(model_ak, layer_k):
    """Converts Dequantizer layer and set its variables into the Akida model.

    Args:
        model_ak (:obj:`akida.Model`): the model where the layer will be added.
        layer_k (:obj:`tf.keras.Layer`): the quantizeml layer to convert.
    """
    if not isinstance(layer_k, Dequantizer):
        raise TypeError(f"Layer {layer_k.name} was expected to be Dequantizer")

    # Depending on ak_version:
    if get_akida_version() == AkidaVersion.v1:
        # Take the last layer to set variables
        layer_ak = model_ak.layers[-1]
    else:
        # Create and add one akida.Dequantizer to the model
        layer_ak = akida.Dequantizer(name=layer_k.name)
        model_ak.add(layer_ak)

    # Set variables into the akida layer
    _set_dequantizer_variables(layer_ak, layer_k)
