# Copyright 2020 The HuggingFace Datasets Authors and the TensorFlow Datasets Authors.
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

# Lint as: python3
"""Utilities for file names."""

import re

_uppercase_uppercase_re = re.compile(r"([A-Z]+)([A-Z][a-z])")
_lowercase_uppercase_re = re.compile(r"([a-z\d])([A-Z])")

_single_underscore_re = re.compile(r"(?<!_)_(?!_)")
_multiple_underscores_re = re.compile(r"(_{2,})")

_split_re = r"^\w+(\.\w+)*$"


def camelcase_to_snakecase(name):
    """Convert camel-case string to snake-case."""
    name = _uppercase_uppercase_re.sub(r"\1_\2", name)
    name = _lowercase_uppercase_re.sub(r"\1_\2", name)
    return name.lower()
