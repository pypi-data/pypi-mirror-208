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
from collections import defaultdict
from os.path import isfile
from typing import List, Optional, Tuple, Dict, Any, OrderedDict

import numpy as np
from tokenizers import Tokenizer

from fastforward.config import ModelConfig
from fastforward.tokenizer.abstract_tokenizer import AbstractTokenizer, NetworkInfo, EncodingConfig, Input
from fastforward.tokenizer.tokenizer_config import TokenizerConfig, TruncationStrategy, PaddingStrategy, EncodingFast

from threading import RLock


class FastTokenizerAdapter(AbstractTokenizer):

    def __init__(self, config: ModelConfig, network_info: NetworkInfo):
        self.tokenizer = Tokenizer.from_file(
            config.config_path + "/tokenizer.json")
        self.network_info = network_info
        self.lock = RLock()

        with open(config.config_path + "/tokenizer.json", encoding="utf-8") as config_file:
            self.config = TokenizerConfig(json.load(config_file))

        if isfile(config.config_path + "/tokenizer_init.json"):
            with open(config.config_path + "/tokenizer_init.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                if "do_lower_case" in config and config["do_lower_case"]:
                    from tokenizers.normalizers import Lowercase, Sequence
                    # noinspection PyArgumentList
                    normalizer = Sequence(
                        [Lowercase(), self.tokenizer.normalizer])
                    # noinspection PyPropertyAccess
                    self.tokenizer.normalizer = normalizer

    def encode(self, sequence: Input, config: EncodingConfig = EncodingConfig()):
        encodings = self._do_encode(sequence, config)
        tokens_and_encodings = [
            self._convert_encoding(
                encoding=encoding,
                return_token_type_ids=config.return_token_type_ids,
                return_attention_mask=config.return_attention_mask,
                return_overflowing_tokens=config.return_overflowing_tokens,
                return_special_tokens_mask=config.return_special_tokens_mask,
                return_offsets_mapping=config.return_offsets_mapping,
                return_length=config.return_length
            )
            for encoding in encodings
        ]

        # Convert the output to have dict[list] from list[dict] and remove the additional overflows dimension
        # From (variable) shape (batch, overflows, sequence length) to ~ (batch * overflows, sequence length)
        # (we say ~ because the number of overflow varies with the example in the batch)
        #
        # To match each overflowing sample with the original sample in the batch
        # we add an overflow_to_sample_mapping array (see below)
        sanitized_tokens = {}
        for key in tokens_and_encodings[0][0].keys():
            if key in self.network_info.get_input_names():
                stack = [np.array(e) for item,
                         _ in tokens_and_encodings for e in item[key]]
                sanitized_tokens[key] = stack
        sanitized_encodings = [
            e for _, item in tokens_and_encodings for e in item]

        # If returning overflowing tokens, we need to return a mapping
        # from the batch idx to the original sample
        if config.return_overflowing_tokens:
            overflow_to_sample_mapping = []
            for i, (toks, _) in enumerate(tokens_and_encodings):
                overflow_to_sample_mapping += [i] * len(toks["input_ids"])

            # FIXME: ValueError: no node with name 'overflow_to_sample_mapping' found
            # sanitized_tokens["overflow_to_sample_mapping"] = overflow_to_sample_mapping
        return BatchEncoding(sanitized_tokens, sanitized_encodings)

    def _do_encode(self, sequence: Input, config: EncodingConfig) -> Any:
        """
        Non ideal quickfix for:
            https://github.com/huggingface/tokenizers/issues/537
        """
        with self.lock:
            self.set_truncation_and_padding(config)
            return self.tokenizer.encode_batch(
                sequence if isinstance(sequence, list) else [
                    sequence],
                add_special_tokens=config.add_special_tokens,
                is_pretokenized=config.is_split_into_words
            )

    def decode(self, output: np.array, skip_special_token: bool = False):
        # FIXME: summarization
        output = output.astype(np.int32)
        # quickfix: https://github.com/huggingface/tokenizers/issues/537
        with self.lock:
            return self.tokenizer.decode_batch(output, skip_special_tokens=skip_special_token)


    def set_truncation_and_padding(self, config: EncodingConfig):
        """
        Define the truncation and the padding strategies for fast tokenizers (provided by HuggingFace tokenizers
        library) and restore the tokenizer settings afterwards.

        The provided tokenizer has no padding / truncation strategy before the managed section. If your tokenizer set a
        padding / truncation strategy before, then it will be reset to no padding / truncation when exiting the managed
        section.
        """
        _truncation = self.tokenizer.truncation
        _padding = self.tokenizer.padding
        # Set truncation and padding on the backend tokenizer
        if config.truncation_strategy == TruncationStrategy.DO_NOT_TRUNCATE:
            if _truncation is not None:
                self.tokenizer.no_truncation()
        else:
            target = {"max_length": config.max_length, "stride": config.stride,
                      "strategy": config.truncation_strategy.value}
            if _truncation != target:
                self.tokenizer.enable_truncation(**target)

        if config.padding_strategy == PaddingStrategy.DO_NOT_PAD:
            if _padding is not None:
                self.tokenizer.no_padding()
        else:
            length = config.max_length if config.padding_strategy == PaddingStrategy.MAX_LENGTH else None
            target = {
                "length": length,
                "direction": config.padding_direction.value,
                "pad_id": self.pad_token_id,
                "pad_token": self.pad_token,
                "pad_type_id": self.pad_token_type_id,
                "pad_to_multiple_of": config.pad_to_multiple_of,
            }
            if _padding != target:
                self.tokenizer.enable_padding(**target)

    def _convert_encoding(
            self,
            encoding: EncodingFast,
            return_token_type_ids: Optional[bool] = None,
            return_attention_mask: Optional[bool] = None,
            return_overflowing_tokens: bool = False,
            return_special_tokens_mask: bool = False,
            return_offsets_mapping: bool = False,
            return_length: bool = False,
    ) -> Tuple[Dict[str, Any], List[EncodingFast]]:
        """
        Convert the encoding representation (from low-level HuggingFace tokenizer output) to a python Dict and a list
        of encodings, take care of building a batch from overflowing tokens.

        Overflowing tokens are converted to additional examples (like batches) so the output values of the dict are
        lists (overflows) of lists (tokens).

        Output shape: (overflows, sequence length)
        """
        if return_token_type_ids is None:
            return_token_type_ids = "token_type_ids" in self.network_info.get_input_names()
        if return_attention_mask is None:
            return_attention_mask = "attention_mask" in self.network_info.get_input_names()

        if return_overflowing_tokens and encoding.overflowing is not None:
            encodings = [encoding] + encoding.overflowing
        else:
            encodings = [encoding]

        encoding_dict = defaultdict(list)
        for e in encodings:
            encoding_dict["input_ids"].append(e.ids)

            if return_token_type_ids:
                encoding_dict["token_type_ids"].append(e.type_ids)
            if return_attention_mask:
                encoding_dict["attention_mask"].append(e.attention_mask)
            if return_special_tokens_mask:
                encoding_dict["special_tokens_mask"].append(
                    e.special_tokens_mask)
            if return_offsets_mapping:
                encoding_dict["offset_mapping"].append(e.offsets)
            if return_length:
                encoding_dict["length"].append(len(e.ids))

        return encoding_dict, encodings


class BatchEncoding(OrderedDict):

    def __init__(self, d: dict, encoding):
        super().__init__(d)
        self.encodings = encoding if isinstance(encoding, list) else [encoding]

    def sequence_ids(self, batch_index: int = 0) -> List[Optional[int]]:
        """
        Return a list mapping the tokens to the id of their original sentences:
        """
        if not self.encodings:
            raise ValueError(
                "sequence_ids() is not available when using Python-based tokenizers")
        return self.encodings[batch_index].sequence_ids
