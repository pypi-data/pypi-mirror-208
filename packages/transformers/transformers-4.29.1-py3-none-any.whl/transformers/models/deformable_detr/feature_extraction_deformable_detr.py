# coding=utf-8
# Copyright 2022 The HuggingFace Inc. team. All rights reserved.
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
"""Feature extractor class for Deformable DETR."""

import warnings

from ...utils import logging
from .image_processing_deformable_detr import DeformableDetrImageProcessor


logger = logging.get_logger(__name__)


class DeformableDetrFeatureExtractor(DeformableDetrImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class DeformableDetrFeatureExtractor is deprecated and will be removed in version 5 of Transformers."
            " Please use DeformableDetrImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
