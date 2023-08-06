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
"""Functions to convert input layers to Akida layers.
"""
from keras.layers import InputLayer
from akida import Model, InputData

from ..akida_versions import AkidaVersion, get_akida_version


def _create_input_data(layer, input_is_image):
    """Parses a keras InputLayer layer and returns the corresponding Akida
    InputData layer.

    Args:
        layer (:obj:`tf.keras.Layer`): the InputLayer to convert.
        input_is_image (bool): True if input is an 8-bit unsigned tensors (like images).

    Returns:
        akida.InputData: The parsed layer.
    """
    if not isinstance(layer, InputLayer):
        raise TypeError(f"Layer {layer.name} was expected to be "
                        "InputLayer")
    # input_shape param is stored as a tuples in an array
    input_shape = layer.input_shape[0]

    if input_shape[0] is not None:
        raise ValueError("First dimension for input layer expected to be None")
    # Ignore first dimension, because it is None
    input_shape = input_shape[1:]
    # input shape must not exceeds 3 dim
    if len(input_shape) > 3:
        raise ValueError("input shape must not exceed 3 dimensions."
                         f"Receives {input_shape}")

    # Create a list with 1 for each dimension that we miss before having 3
    # dims, that is what akida expects
    missing_dimensions = [1] * (3 - len(input_shape))
    input_shape = [*missing_dimensions, *input_shape]
    # the akida version determines the input_bits
    input_bits = 4 if get_akida_version() == AkidaVersion.v1 else 8
    # if input_is_image is set to True the input is unsigned.
    input_signed = not input_is_image
    return InputData(input_shape=input_shape,
                     input_bits=input_bits,
                     input_signed=input_signed,
                     name=layer.name)


def convert_input(model_ak, layer_k, input_is_image):
    """Converts a keras Input layer into ``akida.InputData`` and add it to the
    Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        layer_k (:obj:`keras.Layer`): the InputLayer layer to convert.
        input_is_image (bool): True if input is an 8-bit unsigned tensors.
    """
    if not isinstance(layer_k, InputLayer):
        raise TypeError(f"Layer {layer_k.name} was expected to be "
                        "InputLayer")
    if not isinstance(model_ak, Model):
        raise TypeError(f"Expecting an akida model, received {type(model_ak)}")
    if len(model_ak.layers) != 0:
        raise TypeError("Akida model should be empty")

    input_data = _create_input_data(layer_k, input_is_image)
    model_ak.add(input_data)
