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
"""Functions to convert keras pooling layers parameters to akida.
"""

from quantizeml.layers import QuantizedMaxPool2D, QuantizedGlobalAveragePooling2D, OutputQuantizer
from akida import Padding, PoolType
from ..akida_versions import AkidaVersion, get_akida_version


def parse_max_pooling(layer):
    """Parses a quantizeml.QuantizedMaxPool2D parameters.

    Args:
        layer (:obj:`quantizeml.QuantizedMaxPool2D`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    assert isinstance(layer, QuantizedMaxPool2D)

    padding = Padding.Same if layer.padding == "same" else Padding.Valid
    pool_size = layer.pool_size
    pool_stride = layer.strides if layer.strides else pool_size

    pool_params = dict(
        pool_type=PoolType.Max,
        padding=padding,
        pool_size=pool_size,
        pool_stride=pool_stride
    )

    if get_akida_version() == AkidaVersion.v2:

        # Make sure the Conv2D layers spatial params are square
        assert pool_size[0] == pool_size[1], "Akida v2 layers only handle square pooling"
        pool_params.update({"pool_size": pool_size[0]})
        assert pool_stride[0] == pool_stride[1], (
            "Akida v2 layers pooling stride should be the same for both dimensions")
        pool_params.update({"pool_stride": pool_stride[0]})

    return pool_params


def parse_global_average_pooling(layer):
    """Parses a quantizeml.QuantizedGlobalAveragePooling2D parameters.

    Args:
        layer (:obj:`quantizeml.QuantizedGlobalAveragePooling2D`): the layer to parse.

    Returns:
        dict: the corresponding akida parameters.
    """
    assert isinstance(layer, QuantizedGlobalAveragePooling2D)

    if get_akida_version() == AkidaVersion.v1:
        return dict(pool_type=PoolType.Average)

    # Check if there is an output_quantizer
    out_quantizer = getattr(layer, "out_quantizer", None)

    assert isinstance(out_quantizer, OutputQuantizer)

    return dict(pool_type=PoolType.Average, output_bits=out_quantizer.bitwidth)


def set_pooling_variables(layer_ak, layer_k):
    """Computes and sets the pooling variables in an akida layer.

    Args:
        layer_ak (:obj:`akida.Layer`): the targeted akida layer.
        layer_k (:obj:`quantizeml.Layer`): the source layer.
    """
    assert isinstance(layer_k, (QuantizedGlobalAveragePooling2D, QuantizedMaxPool2D))
    # Nothing to do in AkidaVersion.v2 or for QuantizedMaxPool2D
    if get_akida_version() == AkidaVersion.v2 or isinstance(layer_k, QuantizedMaxPool2D):
        return

    # In AkidaVersion.v1, biases are only applied when evaluating activations, by
    # subtracting the threshold. Since this happens after pooling, the scaling factor
    # introduced by the GAP operation must be applied to the threshold.
    spatial_size = layer_k.input_shape[1] * layer_k.input_shape[2]
    if spatial_size > 2**8:
        raise RuntimeError(f"Unsupported spatial size product ({spatial_size}). "
                           "We only accepts values smaller than 256. "
                           "Consider to replace GlobalAveragePooling2D by MaxPooling2D.")
    layer_ak.variables["threshold"] *= spatial_size
