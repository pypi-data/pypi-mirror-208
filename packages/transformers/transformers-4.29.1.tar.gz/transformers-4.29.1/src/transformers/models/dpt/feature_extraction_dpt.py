# coding=utf-8
# Copyright 2021 The HuggingFace Inc. team. All rights reserved.
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
"""Feature extractor class for DPT."""

import warnings

from ...utils import logging
from .image_processing_dpt import DPTImageProcessor


logger = logging.get_logger(__name__)


class DPTFeatureExtractor(DPTImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class DPTFeatureExtractor is deprecated and will be removed in version 5 of Transformers. Please"
            " use DPTImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
