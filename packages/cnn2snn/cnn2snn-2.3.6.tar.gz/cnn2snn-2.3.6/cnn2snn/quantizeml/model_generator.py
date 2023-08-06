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
"""Parsing functions to generate an Akida model from a Keras model quantized with quantizeml api.
"""

import quantizeml.layers as qlayers
from quantizeml.models import record_quantization_variables
from akida import Model

from .depthwise_conv2d import convert_depthwise_conv_block
from .depthwise_conv2d_transpose import convert_depthwise_conv2d_transpose_block
from .add import convert_quantized_add
from .input_data import convert_input
from .shiftmax import convert_quantized_shiftmax
from .attention import convert_quantized_attention
from .madnorm import convert_quantized_madnorm
from .stem import convert_quantized_stem_layers
from .concatenate import convert_quantized_concatenate
from .convolution import convert_conv_block
from .separable_convolution import convert_sepconv_block
from .batchnorm import convert_batchnorm_block
from .extract_token import convert_extract_token
from .conv2d_transpose import convert_conv_transpose_block
from .dequantizer import convert_dequantizer
from ..akida_versions import AkidaVersion, get_akida_version
from .compatibility_checks import check_model_compatibility
from .block_converter import BlockConverter


def _raise_block_error(block):
    """ Raise error due to non convertible layers block"""
    block_layers_name = ""
    block_layers_type = ""
    for layer in block:
        block_layers_name += f"{layer.name}, "
        block_layers_type += f"{layer.__class__.__name__}, "
    raise RuntimeError(f"Layers {block_layers_name[:-2]}: unsupported type "
                       f"[{block_layers_type[:-2]}].")


def generate_model(model, input_is_image):
    """Generates an Akida model.

    This function creates an Akida model by iterating through the layers of the
    quantized model. For each layer, the corresponding akida layer is created and
    added to the Akida model.

    Args:
        model (:obj:`tf.keras.Model`): a Keras model to convert.
        input_is_image (bool): True if input is an 8-bit unsigned tensors (like images).

    Returns:
        :obj:`akida.Model`: the generated Akida model.
    """
    # Check if input model is convertible and extract its layers blocks
    blocks = check_model_compatibility(model)
    # First store necessary variables for conversion
    record_quantization_variables(model)

    model_ak = Model()

    # Identify the input block
    ak_version = get_akida_version()
    # Flag to identify if the current block has been converted
    converted = False
    if not isinstance(blocks[0], BlockConverter) and input_is_image:
        if ak_version == AkidaVersion.v2:
            # Convert the akida 2.0 stem block layer if the keras model has one.
            converted = convert_quantized_stem_layers(model_ak, blocks[0])
        if not converted:
            # Look for an input convolution layer
            converted = convert_conv_block(model_ak, blocks[0])
    if not converted:
        # Convert the keras InputLayer into an InputData layer
        convert_input(model_ak, model.layers[0], input_is_image)
    else:
        blocks.pop(0)

    for block in blocks:
        # Create and add layer to the akida model
        # The next check converts the potential dense_block layers to a QuantizedDense
        if isinstance(block, BlockConverter):
            if block.convert(model_ak):
                continue
        # conv_block layers to a QuantizedConv2D
        if convert_conv_block(model_ak, block):
            continue
        # and sepconv_block to a QuantizedSeparableConv2D
        if convert_sepconv_block(model_ak, block):
            continue
        # Dequantizer conversion applies in both version
        if isinstance(block[0], qlayers.Dequantizer):
            convert_dequantizer(model_ak, block[0])
            continue
        # The other modules are for v2 only
        if get_akida_version() != AkidaVersion.v2:
            # If you got here, the layer is not supported: raise an error.
            _raise_block_error(block)
        if convert_batchnorm_block(model_ak, block):
            continue
        if convert_depthwise_conv_block(model_ak, block):
            continue
        # convert conv_transpose_block to a QuantizedConv2DTranspose
        if convert_conv_transpose_block(model_ak, block):
            continue
        if convert_depthwise_conv2d_transpose_block(model_ak, block):
            continue
        if len(block) == 1:
            layer = block[0]
            if isinstance(layer, qlayers.QuantizedAdd):
                convert_quantized_add(model_ak, layer)
            elif isinstance(layer, qlayers.QuantizedShiftmax):
                convert_quantized_shiftmax(model_ak, layer)
            elif isinstance(layer, qlayers.QuantizedAttention):
                convert_quantized_attention(model_ak, layer)
            elif isinstance(layer, qlayers.QuantizedLayerNormalization):
                convert_quantized_madnorm(model_ak, layer)
            elif isinstance(layer, qlayers.QuantizedConcatenate):
                convert_quantized_concatenate(model_ak, layer)
            elif isinstance(layer, qlayers.QuantizedExtractToken):
                convert_extract_token(model_ak, layer)
            else:
                # If you got here, the layer is not supported: raise an error.
                raise RuntimeError(f"Layer {layer.name}: unsupported type "
                                   f"{layer.__class__.__name__}.")
        else:
            # If you got here, the block is not supported: raise an error.
            _raise_block_error(block)
    return model_ak
