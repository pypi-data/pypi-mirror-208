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
"""Functions to convert QuantizedConcatenate to Akida.
"""
from akida import Concatenate
import quantizeml.layers as qlayers

from .layer_utils import get_inbound_layers


def convert_quantized_concatenate(model_ak, layer_k):
    """Converts QuantizedConcatenate layer and its variables and adds it to the
    Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        layer (:obj:`tf.keras.Layer`): the quantizeml QuantizedConcatenate layer to convert.
    """
    if not isinstance(layer_k, qlayers.QuantizedConcatenate):
        raise TypeError(f"Layer {layer_k.name} was expected to be "
                        "QuantizedConcatenate")
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, layer_k)
    # Create and add layer to the akida model
    # It is quite simple because there are no variables or params to be set.
    layer_ak = Concatenate()
    model_ak.add(layer_ak, inbound_layers_ak)
