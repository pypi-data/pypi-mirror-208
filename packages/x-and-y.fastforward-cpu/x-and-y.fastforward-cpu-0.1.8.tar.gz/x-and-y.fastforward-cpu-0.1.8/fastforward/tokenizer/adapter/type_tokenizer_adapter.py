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

from fastforward.tokenizer.abstract_tokenizer import AbstractTokenizer, NetworkInfo, EncodingConfig, Input
from fastforward.utils import as_list


class TypeTokenizerAdapter(AbstractTokenizer):
    def __init__(self, tokenizer: AbstractTokenizer, network_info: NetworkInfo):
        self.tokenizer = tokenizer
        self.network_info = network_info
        self.config = tokenizer.config

    def encode(self, sequence: Input, config: EncodingConfig = EncodingConfig()):
        outputs = self.tokenizer.encode(as_list(sequence), config)

        for k in outputs:
            _type = self.network_info.get_input_type(k)
            if _type == "tensor(int64)":
                outputs[k] = np.array(outputs[k]).astype(np.int64)
        return outputs

    def decode(self, output: np.array, skip_special_token: bool = False):
        return self.tokenizer.decode(output, skip_special_token)
