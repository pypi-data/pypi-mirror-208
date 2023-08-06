#  Copyright 2022 The X-and-Y team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import numpy as np

from fastforward.config import ModelConfig
from fastforward.tokenizer.abstract_tokenizer import AbstractTokenizer, EncodingConfig, Input
from fastforward.utils import coalesce


class PrefixTokenizerAdapter(AbstractTokenizer):
    def __init__(self, tokenizer: AbstractTokenizer, model_config: ModelConfig):
        self.tokenizer = tokenizer
        self.model_config = model_config
        self.config = tokenizer.config

    def encode(self, sequence: Input, config: EncodingConfig = EncodingConfig()):
        def handle_prefix(item):
            prefix = coalesce(self.model_config.prefix, "")
            if isinstance(item, tuple):
                return prefix + item[0], prefix + item[1]
            else:
                return prefix + item

        if isinstance(sequence, str):
            sequence = list(map(handle_prefix, sequence))
        if isinstance(sequence, list) and isinstance(sequence[0], str):
            sequence = list(map(handle_prefix, sequence))
        return self.tokenizer.encode(sequence, config)

    def decode(self, output: np.array, skip_special_token: bool = False):
        return self.tokenizer.decode(output, skip_special_token)
