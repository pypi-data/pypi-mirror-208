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
"""Functions to check model compatibility for CNN2SNN conversion.
"""
from keras import layers
from quantizeml import layers as qlayers

from .blocks import split_model_into_blocks
from .padding import check_same_valid_compatibility
from ..transforms.sequential import _check_layers_data_format, _check_layer_inbounds
from ..akida_versions import get_akida_version, AkidaVersion
from .block_converter import _V1_PATTERN_CONVERTERS, _V2_PATTERN_CONVERTERS

neural_layers = (qlayers.QuantizedConv2D, qlayers.QuantizedSeparableConv2D,
                 qlayers.QuantizedDense, qlayers.QuantizedDepthwiseConv2D,
                 qlayers.QuantizedConv2DTranspose, qlayers.QuantizedDepthwiseConv2DTranspose)
skippable_layers = (layers.InputLayer, layers.Rescaling, layers.Activation, layers.Softmax,
                    layers.Dropout)
pooling_layers = (qlayers.QuantizedGlobalAveragePooling2D, qlayers.QuantizedMaxPool2D)
norm_layers = (qlayers.LayerMadNormalization, qlayers.QuantizedBatchNormalization)
activation_layers = (qlayers.QuantizedReLU,)
stem_layers = (qlayers.ClassToken, qlayers.AddPositionEmbs)
reshape_layers = (qlayers.QuantizedReshape, qlayers.QuantizedFlatten)


class CompatibilityMessage:
    """Helper to represent an error message

    Args:
        message (str): main error message.
        layers (list or tf.keras.Layers): layer(s) that will raise(s) the exception.
            Defaults to None.
    """

    def __init__(self, message, layers=None):
        if not message.endswith("."):
            message += "."
        self.message = message
        # Replace empty list by None
        self.layers = layers or None

    def __str__(self):
        if self.layers is None:
            return self.message

        message = f"{self.message} Layer(s): "
        if isinstance(self.layers, list):
            message += str([x.name for x in self.layers])
        else:
            message += self.layers.name
        return message


class CompatibilityBlockError:
    """Helper to raise a list of ``CompatibilityMessage`` errors"""

    def __init__(self):
        self._errors_msg = []

    @property
    def status(self):
        return len(self._errors_msg) > 0

    def push(self, message, layers=None):
        self._errors_msg.append(CompatibilityMessage(message, layers))

    def __str__(self):
        err_msg = "The following errors were found when the block was checked:"
        for err in self._errors_msg:
            err_msg += "\n\t- " + str(err)
        return err_msg

    def __call__(self):
        if self.status:
            raise RuntimeError(str(self))


def _block_pattern(block):
    """Method that returns the pattern of a block of layers.

    Args:
        block (list): list of quantized quantizeml layers.

    Returns:
        tuple: list of layer types representing the block pattern.
    """
    return tuple([layer.__class__ for layer in block])


def _get_block_converter(block):
    """Helper to get the BlockConverter of a block of layers.

    Args:
        block (list): list of quantized quantizeml layers.

    Returns:
        (:obj:`BlockConverter`): the BlockConverter corresponding to the block of layers or None.
    """
    pattern = _block_pattern(block)

    if get_akida_version() == AkidaVersion.v1:
        block_converter = _V1_PATTERN_CONVERTERS.get(pattern, None)
    else:
        block_converter = _V2_PATTERN_CONVERTERS.get(pattern, None)

    return block_converter


def check_model_compatibility(model):
    r"""Checks if a QuantizeML model is compatible for Akida conversion.

    This function does NOT:

    - convert the QuantizeML model to an Akida model,
    - check if the model is compatible with Akida hardware

    It ONLY checks if the model design is compatible with Akida.

    Args:
        model (:obj:`tf.keras.Model`): the model to check.

    Returns:
        list: a list of sequences of the non_skippable layers ('blocks').
    """
    # Check general rules about model in three steps:
    # 1. Check if model has only one input and one output,
    # 2. Check right data format and
    # 3. Over Akida 1.0, check if model is sequential.
    _check_model_input_output(model)
    _check_layers_data_format(model)
    if get_akida_version() == AkidaVersion.v1:
        _check_layer_inbounds(model)

    # Split model into theirs blocks:
    blocks = split_model_into_blocks(model)

    # This list will contains either a block converter instance,
    # or a list of non-skippable layers.
    straight_blocks = []
    # Evaluate block-by-block integrity
    for block in blocks:
        # Split blocks into skippable and none skippable blocks
        _, non_skippable = _extract_skippable_layers(block)
        # Get the corresponding BlockConverter of the layers block if available.
        block_converter = _get_block_converter(non_skippable)
        if block_converter:
            straight_blocks.append(block_converter(non_skippable))
            continue
        # TODO: remove this part once all conversion uses BlockConverter classes
        # Check pooling layers
        _check_pooling_compatibility(non_skippable)
        # Check other rules
        _check_block_integrity(non_skippable)
        if len(non_skippable) > 0:
            straight_blocks.append(non_skippable)
    return straight_blocks


def _split_block_into_layer_types(block):
    """Split input block into the following categories:

    - neural (processing) layers,
    - activation layers,
    - normalization layers and
    - stem block layers.

    Args:
        block (list): block layers to split.

    Returns:
        list: block divided into categories.
    """
    neurals, acts, norms, stems = [], [], [], []
    for layer in block:
        if isinstance(layer, neural_layers):
            neurals.append(layer)
        elif isinstance(layer, activation_layers):
            acts.append(layer)
        elif isinstance(layer, norm_layers):
            norms.append(layer)
        elif isinstance(layer, stem_layers):
            stems.append(layer)
        elif isinstance(layer, reshape_layers):
            continue
        elif not isinstance(layer, pooling_layers):
            raise RuntimeError(f"Unrecognizable layer in block: {layer.name}")
    return neurals, acts, norms, stems


def _check_block_integrity(block):
    """Check integrity of one block.

    Args:
        block (list(tf.keras.Layer)): block to analysis.
    """
    if len(block) == 0 or isinstance(block[0], qlayers.Dequantizer):
        return

    def _islast(layer):
        outbound = layer.outbound_nodes
        if len(outbound) == 1:
            outbound_layer = outbound[0].outbound_layer
            if isinstance(outbound_layer, skippable_layers):
                return _islast(outbound_layer)
            # If outbound layer is a Dequantizer, target is the final quantized layer
            if isinstance(outbound_layer, qlayers.Dequantizer):
                return True
        return len(outbound) == 0

    def _isfirst(layer):
        ly_inbounds = layer.inbound_nodes[0].inbound_layers
        if not isinstance(ly_inbounds, (tuple, list)):
            ly_inbounds = [ly_inbounds]
        if len(ly_inbounds) == 1 and isinstance(ly_inbounds[0], skippable_layers):
            return _isfirst(ly_inbounds[0])
        return len(ly_inbounds) == 0

    # Start with Akida 1.0 restrictions
    errors = CompatibilityBlockError()
    ak_version = get_akida_version()
    if ak_version == AkidaVersion.v1:
        islast = _islast(block[-1])
        if len(block) == 1 and not islast:
            errors.push("In Akida 1.0, every block must have at least "
                        "one neural and activation layer")
        if islast and not isinstance(block[0], neural_layers):
            errors.push("The last block must start by a neural layer", block[0])
        if not (islast or isinstance(block[-1], activation_layers)):
            errors.push("A block must end by an activation layer", block[-1])

    # General limitations
    if len(block) > 1:
        neurals, acts, norms, stems = _split_block_into_layer_types(block)
        if len(neurals) != 1:
            errors.push("A block must have one neural layer", neurals)
        if len(neurals) > 0:
            if block[0] != neurals[0]:
                errors.push("A block must start by a neural layer", block[0])
        if len(acts) > 1:
            errors.push("A block could have up to only one activation layer", acts)
        if len(norms) != 0:
            errors.push("A block should not have normalization layers: "
                        "these must be folded into previous neural layers", norms)
        if len(stems) > 0:
            if ak_version == AkidaVersion.v1:
                errors.push("Stem-block is not supported on Akida 1.0.")
            if not _isfirst(block[0]):
                errors.push("Stem-block must be the first one in the model.")
            if not all(isinstance(x, qlayers.ClassToken) for x in stems[1:-1]):
                errors.push("'ClassToken' is the only intermediate layer allowed "
                            "in a stem block.", stems[1:-1])
            if not isinstance(block[0], qlayers.QuantizedConv2D):
                errors.push("Stem-block must begin by one 'Conv2D'", block[0])
            if not isinstance(stems[-1], qlayers.AddPositionEmbs):
                errors.push("Stem-block must end by one 'AddPositionEmbs'.", stems[-1])

    # Raise exception if there is at least one error message
    errors()


def _check_model_input_output(model):
    """Asserts that model inputs/outputs are supported for conversion.

    The Keras model must have only one input layer and one output layer.
    On Akida 1.0, the input shape must 4-D (N, H, W, C).

    Args:
        model (tf.keras.model): the Keras model to check.
    """

    # Error if multiple inputs
    if len(model.input_names) > 1:
        raise RuntimeError("Model must have only one input layer. Receives "
                           f"inputs {model.input_names}.")

    # Error if multiple outputs
    if len(model.output_names) != 1:
        raise RuntimeError("Model must have only one output layer. Receives"
                           f"outputs {model.output_names}.")

    # Error if input shape is not 2D or 4D
    if len(model.input_shape) not in (2, 4) and get_akida_version() == AkidaVersion.v1:
        raise RuntimeError(
            "Input shape of model must be 2-D or 4-D (batch size + 1-D or 3-D "
            f"tensors). Receives input shape {model.input_shape}.")


def _extract_skippable_layers(block):
    """Split block into skippable and non skippable layers

    Args:
        block (tf.keras.Layer): block to split.

    Returns:
        tuple: list of skippable and non skippable layers
    """
    skippable, non_skippable = [], []
    for layer in block:
        if isinstance(layer, skippable_layers):
            skippable.append(layer)
        else:
            non_skippable.append(layer)
    return skippable, non_skippable


def _check_pooling_compatibility(block):
    """Asserts pooling layer is compatible for conversion.

    Args:
        block (list): the layers block.
    """
    errors = CompatibilityBlockError()
    conv_neural_layers = (qlayers.QuantizedConv2D,
                          qlayers.QuantizedSeparableConv2D, qlayers.QuantizedDepthwiseConv2D)
    pool_layer = [ly for ly in block if isinstance(ly, pooling_layers)]
    if len(pool_layer) == 0:
        return
    elif len(pool_layer) != 1:
        errors.push("A block could have up to only one pooling layer", pool_layer)

    # Raise error if pooling does not have a convolutional layer in the block
    pool_layer = pool_layer[0]
    conv_layer = [ly for ly in block if isinstance(ly, conv_neural_layers)]
    if len(conv_layer) != 1:
        errors.push("Pooling layer must be placed after a convolutional layer", conv_layer)

    if isinstance(pool_layer, qlayers.QuantizedGlobalAveragePooling2D) and pool_layer != block[-1] \
            and get_akida_version() == AkidaVersion.v2:
        errors.push("In v2, GAP should occur after ReLU and placed at the end of the block",
                    pool_layer)
    # Raise the exceptions(if exist)
    errors()

    # Raises error if the padding of MaxPool2D is different from the padding
    # of the neural processing layer.
    conv_layer = conv_layer[0]
    neur_pad = conv_layer.padding if not check_same_valid_compatibility(conv_layer) else "same"
    pool_pad = getattr(pool_layer, "padding", "")
    if isinstance(pool_layer, qlayers.QuantizedMaxPool2D) and neur_pad != pool_pad:
        raise RuntimeError(f"Pooling layer {pool_layer.name} (padding: {pool_pad}) must have "
                           f"the same padding as {conv_layer.name} (padding: {neur_pad}).")
