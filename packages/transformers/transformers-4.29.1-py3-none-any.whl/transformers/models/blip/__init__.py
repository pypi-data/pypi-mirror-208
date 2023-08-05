# Copyright 2022 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import TYPE_CHECKING

from ...utils import (
    OptionalDependencyNotAvailable,
    _LazyModule,
    is_tf_available,
    is_torch_available,
    is_vision_available,
)


_import_structure = {
    "configuration_blip": [
        "BLIP_PRETRAINED_CONFIG_ARCHIVE_MAP",
        "BlipConfig",
        "BlipTextConfig",
        "BlipVisionConfig",
    ],
    "processing_blip": ["BlipProcessor"],
}

try:
    if not is_vision_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["image_processing_blip"] = ["BlipImageProcessor"]


try:
    if not is_torch_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["modeling_blip"] = [
        "BLIP_PRETRAINED_MODEL_ARCHIVE_LIST",
        "BlipModel",
        "BlipPreTrainedModel",
        "BlipForConditionalGeneration",
        "BlipForQuestionAnswering",
        "BlipVisionModel",
        "BlipTextModel",
        "BlipForImageTextRetrieval",
    ]

try:
    if not is_tf_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["modeling_tf_blip"] = [
        "TF_BLIP_PRETRAINED_MODEL_ARCHIVE_LIST",
        "TFBlipModel",
        "TFBlipPreTrainedModel",
        "TFBlipForConditionalGeneration",
        "TFBlipForQuestionAnswering",
        "TFBlipVisionModel",
        "TFBlipTextModel",
        "TFBlipForImageTextRetrieval",
    ]

if TYPE_CHECKING:
    from .configuration_blip import BLIP_PRETRAINED_CONFIG_ARCHIVE_MAP, BlipConfig, BlipTextConfig, BlipVisionConfig
    from .processing_blip import BlipProcessor

    try:
        if not is_vision_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .image_processing_blip import BlipImageProcessor

    try:
        if not is_torch_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .modeling_blip import (
            BLIP_PRETRAINED_MODEL_ARCHIVE_LIST,
            BlipForConditionalGeneration,
            BlipForImageTextRetrieval,
            BlipForQuestionAnswering,
            BlipModel,
            BlipPreTrainedModel,
            BlipTextModel,
            BlipVisionModel,
        )

    try:
        if not is_tf_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .modeling_tf_blip import (
            TF_BLIP_PRETRAINED_MODEL_ARCHIVE_LIST,
            TFBlipForConditionalGeneration,
            TFBlipForImageTextRetrieval,
            TFBlipForQuestionAnswering,
            TFBlipModel,
            TFBlipPreTrainedModel,
            TFBlipTextModel,
            TFBlipVisionModel,
        )

else:
    import sys

    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
