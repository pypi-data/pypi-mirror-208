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

from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class TokenizerConfig(OrderedDict):
    special_tokens: Dict[str, int] = {}

    def __init__(self, data: {}):
        super().__init__(data)

    def _get_token(self, name: str, abbreviations: List[str]):
        if name in self:
            return self[name]

        for entry in self["added_tokens"]:
            for abbreviation in abbreviations:
                if entry["content"] == abbreviation:
                    return entry

        return None

    @property
    def cls_token(self):
        return self._get_token("cls_token", ["[CLS]"])

    @property
    def pad_token(self):
        return self._get_token("pad_token", ["[PAD]", "<pad>"])

    @property
    def sep_token(self):
        return self._get_token("sep_token", ["[SEP]"])

    @property
    def eos_token(self):
        return self._get_token("eos_token", ["[EOS]", "</s>"])

    @property
    def unk_token(self):
        return self._get_token("unk_token", ["[UNK]", "<unk>"])

    @property
    def bos_token(self):
        return self._get_token("bos_token", ["[BOS]"])

    @property
    def mask_token(self):
        return self._get_token("mask_token", ["[MASK]", "<mask>"])


@dataclass
class EncodingFast:
    """This is dummy class because without the `tokenizers` library we don't have these objects anyway"""
    pass


class ExplicitEnum(Enum):
    """
    Enum with more explicit error message for missing values.
    """

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}"
        )


class TruncationStrategy(ExplicitEnum):
    """
    Possible values for the ``truncation`` argument in :meth:`PreTrainedTokenizerBase.__call__`. Useful for
    tab-completion in an IDE.
    """

    ONLY_FIRST = "only_first"
    ONLY_SECOND = "only_second"
    LONGEST_FIRST = "longest_first"
    DO_NOT_TRUNCATE = "do_not_truncate"


class PaddingStrategy(ExplicitEnum):
    """
    Possible values for the ``padding`` argument in :meth:`PreTrainedTokenizerBase.__call__`. Useful for tab-completion
    in an IDE.
    """

    LONGEST = "longest"
    MAX_LENGTH = "max_length"
    DO_NOT_PAD = "do_not_pad"
