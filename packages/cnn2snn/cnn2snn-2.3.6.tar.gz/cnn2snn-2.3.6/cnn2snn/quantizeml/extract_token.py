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
"""Functions to convert QuantizedExtractToken to Akida.
"""
from akida import ExtractToken
import quantizeml.layers as qlayers

from .layer_utils import get_inbound_layers


def _create_extract_token(layer):
    """Parses a quantizeml QuantizedExtractToken layer and returns the
    params to create the corresponding Akida ExtractToken layer.

    Args:
        layer (:obj:`tf.keras.Layer`): the quantizeml QuantizedExtractToken
            layer to convert.

    Returns:
        :obj:`akida.MadNorm`: The created akida layer.
    """
    assert isinstance(layer, qlayers.QuantizedExtractToken)

    # Akida is capable of supporting only a given combination of token
    if isinstance(layer.token, int):
        token_range = [layer.token]
    else:
        token_range = [*layer.token]
    # Check range is continuous
    begin = min(token_range)
    end = max(token_range) + 1
    continuous = sorted(token_range) == list(range(begin, end))
    if not continuous:
        raise ValueError(f"Argument token in {layer.name} should contain a "
                         "continuous range")
    extract_token = ExtractToken(begin=begin,
                                 end=end,
                                 name=layer.name)
    return extract_token


def convert_extract_token(model_ak, layer_k):
    """Converts QuantizedExtractToken layer and adds it to the Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be
            added.
        layer_k (:obj:`tf.keras.Layer`): the quantizeml QuantizedExtractToken
            layer to convert.
    """
    if not isinstance(layer_k, qlayers.QuantizedExtractToken):
        raise TypeError(f"Layer {layer_k.name} was expected to be "
                        "QuantizedExtractToken")
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, layer_k)
    # Create and add layer to the akida model
    # It is quite simple because there are no variables or params to be set.
    layer_ak = _create_extract_token(layer_k)
    model_ak.add(layer_ak, inbound_layers_ak)
