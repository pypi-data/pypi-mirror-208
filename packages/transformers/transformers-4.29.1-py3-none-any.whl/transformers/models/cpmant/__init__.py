# flake8: noqa
# There's no way to ignore "F401 '...' imported but unused" warnings in this
# module, but to preserve other warnings. So, don't check this module at all.

# Copyright 2022 The HuggingFace Team and The OpenBMB Team. All rights reserved.
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

# rely on isort to merge the imports
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tokenizers_available, is_torch_available


_import_structure = {
    "configuration_cpmant": ["CPMANT_PRETRAINED_CONFIG_ARCHIVE_MAP", "CpmAntConfig"],
    "tokenization_cpmant": ["CpmAntTokenizer"],
}

try:
    if not is_torch_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["modeling_cpmant"] = [
        "CPMANT_PRETRAINED_MODEL_ARCHIVE_LIST",
        "CpmAntForCausalLM",
        "CpmAntModel",
        "CpmAntPreTrainedModel",
    ]


if TYPE_CHECKING:
    from .configuration_cpmant import CPMANT_PRETRAINED_CONFIG_ARCHIVE_MAP, CpmAntConfig
    from .tokenization_cpmant import CpmAntTokenizer

    try:
        if not is_torch_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .modeling_cpmant import (
            CPMANT_PRETRAINED_MODEL_ARCHIVE_LIST,
            CpmAntForCausalLM,
            CpmAntModel,
            CpmAntPreTrainedModel,
        )


else:
    import sys

    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
