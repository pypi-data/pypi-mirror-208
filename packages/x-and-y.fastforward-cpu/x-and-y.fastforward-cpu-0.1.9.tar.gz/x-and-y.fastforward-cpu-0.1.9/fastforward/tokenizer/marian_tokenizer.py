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

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from fastforward.tokenizer.abstract_tokenizer import AbstractTokenizer, EncodingConfig
from fastforward.tokenizer.tokenizer_config import TokenizerConfig
from fastforward.utils.numpy_utils import pad_matrix


class MarianTokenizer(AbstractTokenizer):
    """
    Construct a Marian tokenizer. Based on `SentencePiece <https://github.com/google/sentencepiece>`.
    """
    language_code_re = re.compile(">>.+<<")  # type: re.Pattern

    @staticmethod
    def from_config(config_path: str):
        tknzr_config = load_json(config_path + "/tokenizer.json")
        return MarianTokenizer(config_path + "/vocab.json",
                               config_path + "/source.spm",
                               config_path + "/target.spm",
                               source_lang=tknzr_config["source_lang"],
                               target_lang=tknzr_config["target_lang"])

    def __init__(
            self,
            vocab,
            source_spm,
            target_spm,
            source_lang=None,
            target_lang=None,
            unk_token="<unk>",
            eos_token="</s>",
            pad_token="<pad>",
            sp_model_kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        try: # noinspection PyPackageRequirements
            from sacremoses import MosesPunctNormalizer
        except (ImportError, FileNotFoundError):
            raise ValueError("no module sacremoses found, use pip install sacremoses")

        try: # noinspection PyPackageRequirements
            import sentencepiece
        except (ImportError, FileNotFoundError):
            raise ValueError("no module sentencepiece found, use pip install sentencepiece")

        assert Path(source_spm).exists(), f"cannot find spm source {source_spm}"
        self.encoder = load_json(vocab)
        self.decoder = {v: k for k, v in self.encoder.items()}

        assert unk_token in self.encoder
        assert pad_token in self.encoder
        assert eos_token in self.encoder

        self.source_lang = source_lang
        self.target_lang = target_lang
        self.supported_language_codes: list = [k for k in self.encoder if k.startswith(">>") and k.endswith("<<")]

        def load_spm(path: str, sp_model_kwargs: Dict[str, Any]) -> sentencepiece.SentencePieceProcessor:
            sp_model_kwargs = sp_model_kwargs if sp_model_kwargs is not None else {}
            spm = sentencepiece.SentencePieceProcessor(**sp_model_kwargs)
            spm.Load(path)
            return spm

        # load SentencePiece model for pre-processing
        self.spm_source = load_spm(source_spm, sp_model_kwargs)
        self.spm_target = load_spm(target_spm, sp_model_kwargs)

        self.config = TokenizerConfig({
            "unk_token": {"content": unk_token},
            "eos_token": {"content": eos_token},
            "pad_token": {"content": pad_token}
        })

        self.normalizer = MosesPunctNormalizer(self.source_lang).normalize

        self.special_tokens = [
            self.encoder.get(self.unk_token),
            self.encoder.get(self.eos_token),
            self.encoder.get(self.pad_token)
        ]

    def encode(self, text: Union[str, List[str]], config: EncodingConfig):
        def to_tokens(sentence: str):
            sentence = self.normalizer(sentence) if sentence else ""
            tokens = self._tokenize(sentence)
            encoded = list(map(lambda x: self._convert_token_to_id(x), tokens))
            return np.array(encoded + [self.special_tokens[1]])

        text = [text] if isinstance(text, str) else text
        encoded = np.array(list(map(to_tokens, text)), dtype=object)

        if config.padding_strategy:
            max_tokens = len(max(encoded, key=len))
            encoded = pad_matrix(encoded, max_tokens, self.special_tokens[2])

        attention_mask = np.where(encoded != self.special_tokens[2], 1, 0)

        return {
            "input_ids": encoded.astype(np.int64),
            "attention_mask": attention_mask.astype(np.int64)
        }

    def decode(self, tokens, skip_special_token: bool = False):
        tokens = tokens.tolist()

        def _decode(array):
            if skip_special_token:
                array = list(filter(lambda x: x not in self.special_tokens, array))

            array = list(map(lambda x: self._convert_id_to_token(x), array))
            return self.spm_target.DecodePieces(array)

        return list(map(_decode, tokens))

    def _convert_token_to_id(self, token):
        return self.encoder.get(token, self.encoder[self.unk_token])

    def remove_language_code(self, text: str):
        """Remove language codes like >>fr<< before sentencepiece"""
        match = self.language_code_re.match(text)
        code: list = [match.group(0)] if match else []
        return code, self.language_code_re.sub("", text)

    def _tokenize(self, text: str) -> List[str]:
        code, text = self.remove_language_code(text)
        pieces = self.spm_source.encode(text, out_type=str)
        return code + pieces

    def _convert_id_to_token(self, index: int) -> str:
        """Converts an index (integer) in a token (str) using the decoder."""
        token = self.decoder.get(index, self.unk_token)
        return token

    @property
    def vocab_size(self) -> int:
        return len(self.encoder)


def load_json(path: str) -> Union[Dict, List]:
    with open(path, "r") as f:
        return json.load(f)
