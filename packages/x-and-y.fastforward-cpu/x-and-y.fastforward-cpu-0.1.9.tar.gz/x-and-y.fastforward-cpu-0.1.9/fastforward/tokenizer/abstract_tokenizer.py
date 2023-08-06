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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Union, List, Optional, Tuple

import numpy as np

from fastforward.engine.abstract_engine import ModelIO
from fastforward.tokenizer.mixin.special_tokens_mixin import SpecialTokensMixin
from fastforward.tokenizer.tokenizer_config import PaddingStrategy, TruncationStrategy


class AbstractTokenizer(ABC, SpecialTokensMixin):
    """
    The Abstract tokenizer class for all tokenizer implementations is an abstraction class
    for tokenizers like implementations from huggingface's tokenizers library or custom implementations.
    """

    @abstractmethod
    def encode(self, sequence: 'Input', config: 'EncodingConfig'):
        pass

    @abstractmethod
    def decode(self, output: np.array, skip_special_token: bool = False):
        pass


@dataclass
class NetworkInfo:
    """
    A Network info data class contains all information about input/output nodes.
    This information can be used by a tokenizer to prepare the model input/output.
    """
    input: ModelIO
    output: ModelIO

    def get_input_names(self) -> List[str]:
        return self.input.names

    def get_input_type(self, name: str) -> str:
        return self.input.types[name] if name in self.input.types else None

    def get_input_shape(self, name: str) -> List[str]:
        return self.input.shapes[name] if name in self.input.shapes else None

    def get_output_names(self) -> List[str]:
        return self.output.names

    def get_output_type(self, name: str) -> str:
        return self.output.types[name] if name in self.output.types else None

    def get_output_shape(self, name: str) -> List[str]:
        return self.output.shapes[name] if name in self.output.shapes else None


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclass
class EncodingConfig:
    add_special_tokens: bool = True
    is_split_into_words: bool = False
    return_token_type_ids: Optional[bool] = None
    return_attention_mask: Optional[bool] = None
    return_overflowing_tokens: bool = False
    return_special_tokens_mask: bool = False
    return_offsets_mapping: bool = False
    return_length: bool = False
    padding_strategy: PaddingStrategy = PaddingStrategy.LONGEST
    truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE
    max_length: Optional[int] = None
    stride: int = 0
    pad_to_multiple_of: Optional[int] = None
    padding_direction: Direction = Direction.RIGHT
    truncation_direction: Direction = Direction.RIGHT
    do_lower_case: Optional[bool] = None
    output_name: str = "embedding"

    @staticmethod
    def from_config(config_path: str):
        encoding_config = EncodingConfig()

        import json
        from os.path import isfile
        max_length_variations = [
            "max_len",
            "model_max_length",
            "model_max_len",
            "max_length"
        ]
        if isfile(config_path + "/tokenizer_init.json"):
            with open(config_path + "/tokenizer_init.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                for max_len_var in max_length_variations:
                    if max_len_var in config:
                        encoding_config.max_length = config[max_len_var]
                        encoding_config.truncation_strategy = TruncationStrategy.LONGEST_FIRST
                        break
                if "do_lower_case" in config:
                    encoding_config.do_lower_case = config["do_lower_case"]


        return encoding_config


Text = str
BatchText = List[Text]
Pair = Tuple[str, str]
BatchPair = List[Pair]
Input = Union[Text, BatchText, Pair, BatchPair]
