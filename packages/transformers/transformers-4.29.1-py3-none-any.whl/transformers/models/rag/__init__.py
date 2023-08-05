# Copyright 2020 The HuggingFace Team. All rights reserved.
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

from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available


_import_structure = {
    "configuration_rag": ["RagConfig"],
    "retrieval_rag": ["RagRetriever"],
    "tokenization_rag": ["RagTokenizer"],
}

try:
    if not is_torch_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["modeling_rag"] = [
        "RagModel",
        "RagPreTrainedModel",
        "RagSequenceForGeneration",
        "RagTokenForGeneration",
    ]

try:
    if not is_tf_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["modeling_tf_rag"] = [
        "TFRagModel",
        "TFRagPreTrainedModel",
        "TFRagSequenceForGeneration",
        "TFRagTokenForGeneration",
    ]


if TYPE_CHECKING:
    from .configuration_rag import RagConfig
    from .retrieval_rag import RagRetriever
    from .tokenization_rag import RagTokenizer

    try:
        if not is_torch_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .modeling_rag import RagModel, RagPreTrainedModel, RagSequenceForGeneration, RagTokenForGeneration

    try:
        if not is_tf_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .modeling_tf_rag import (
            TFRagModel,
            TFRagPreTrainedModel,
            TFRagSequenceForGeneration,
            TFRagTokenForGeneration,
        )

else:
    import sys

    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
