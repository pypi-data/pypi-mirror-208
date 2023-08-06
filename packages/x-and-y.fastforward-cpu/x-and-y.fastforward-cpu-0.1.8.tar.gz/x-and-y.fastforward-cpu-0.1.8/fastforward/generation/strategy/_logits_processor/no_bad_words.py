#  Copyright 2022 The HuggingFace Inc. team (this file was largely adopted from the transformers library)
#  and the X-and-Y team
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

import logging
from typing import List, Iterable, Optional

import numpy as np

from fastforward.generation.strategy._logits_processor.abstract_logits_processor import LogitsProcessor
from fastforward.utils.numpy_utils import sparse, masked_fill

logger = logging.getLogger(__name__)


class NoBadWordsLogitsProcessor(LogitsProcessor):
    """
    :class:`transformers.LogitsProcessor` that enforces that specified sequences will never be sampled.

    Args:
        bad_words_ids (:obj:`List[List[int]]`):
            List of list of token ids that are not allowed to be generated. In order to get the tokens of the words
            that should not appear in the generated text, use :obj:`tokenizer(bad_word,
            add_prefix_space=True).input_ids`.
        eos_token_id (:obj:`int`):
            The id of the `end-of-sequence` token.
    """

    def __init__(self, bad_words_ids: List[List[int]], eos_token_id: int):

        if not isinstance(bad_words_ids, List) or len(bad_words_ids) == 0:
            raise ValueError(f"`bad_words_ids` has to be a non-emtpy list, but is {bad_words_ids}.")
        if any(not isinstance(bad_word_ids, list) for bad_word_ids in bad_words_ids):
            raise ValueError(f"`bad_words_ids` has to be a list of lists, but is {bad_words_ids}.")
        if any(
                any((not isinstance(token_id, (int, np.integer)) or token_id < 0) for token_id in bad_word_ids)
                for bad_word_ids in bad_words_ids
        ):
            raise ValueError(
                f"Each list in `bad_words_ids` has to be a list of positive integers, but is {bad_words_ids}."
            )

        bad_words_ids = list(filter(lambda bad_token_seq: bad_token_seq != [eos_token_id], bad_words_ids))
        self.bad_words_id_length_1 = []
        self.bad_words_id_length_greater_than_1 = []
        for word in bad_words_ids:
            if len(word) == 1:
                self.bad_words_id_length_1.append(word[0])
            else:
                self.bad_words_id_length_greater_than_1.append(word)

        self.static_bad_words_mask: Optional[np.array] = None

        for banned_token_seq in self.bad_words_id_length_greater_than_1:
            assert len(banned_token_seq) > 0, f"Banned words token sequences {bad_words_ids} cannot have an empty list"

    def __call__(self, input_ids: np.array, scores: np.array) -> np.array:
        if self.static_bad_words_mask is None and len(self.bad_words_id_length_1) > 0:
            self.static_bad_words_mask = self._calc_static_bad_word_mask(scores)

        dynamic_banned_tokens = self._calc_banned_bad_words_ids(input_ids.tolist())
        scores = self._set_scores_to_inf_for_banned_tokens(scores, dynamic_banned_tokens)

        return scores

    def _calc_static_bad_word_mask(self, scores: np.array) -> np.array:
        static_bad_words_mask = np.zeros(scores.shape[1])
        static_bad_words_mask[self.bad_words_id_length_1] = 1
        return np.expand_dims(static_bad_words_mask, axis=0).astype(bool)

    def _tokens_match(self, prev_tokens: List[int], tokens: List[int]) -> bool:
        if len(tokens) == 0:
            # if bad word tokens is just one token always ban it
            return True
        elif len(tokens) > len(prev_tokens):
            # if bad word tokens are longer then prev input_ids they can't be equal
            return False
        else:
            return prev_tokens[-len(tokens):] == tokens

    def _calc_banned_bad_words_ids(self, prev_input_ids: List[List[int]]) -> Iterable[int]:
        banned_tokens = []
        for prev_input_ids_slice in prev_input_ids:
            banned_tokens_slice = []
            for banned_token_seq in self.bad_words_id_length_greater_than_1:
                if self._tokens_match(prev_input_ids_slice, banned_token_seq[:-1]):
                    banned_tokens_slice.append(banned_token_seq[-1])

            banned_tokens.append(banned_tokens_slice)

        return banned_tokens

    def _set_scores_to_inf_for_banned_tokens(
            self, scores: np.array, banned_tokens: List[List[int]]
    ) -> np.array:
        """
        Modifies the scores in place by setting the banned token positions to `-inf`. Banned token is expected to be a
        list of list of banned tokens to ban in the format [[batch index, vocabulary position],...

        Args:
            scores: logits distribution of shape (batch size, vocabulary size)
            banned_tokens: list of list of tokens to ban of length (batch_size)
        """
        banned_mask_list = []
        for idx, batch_banned_tokens in enumerate(banned_tokens):
            for token in batch_banned_tokens:
                # Eliminates invalid bad word IDs that are over the vocabulary size.
                if token <= scores.shape[1]:
                    banned_mask_list.append([idx, token])
                else:
                    logger.error(
                        f"An invalid bad word ID is defined: {token}. This ID is not contained in the"
                        f"vocabulary, and is therefore ignored."
                    )
        if not banned_mask_list and self.static_bad_words_mask is None:
            return scores

        else:
            if banned_mask_list:
                banned_mask = np.array(banned_mask_list)
                indices = np.ones(len(banned_mask))
                # A sparse tensor is generated from a list of coordinates: [[0, 1], [0, 2], [2, 0]]. A conversion to dense tensor generates:
                # [ 0  1  1 ]
                # [ 0  0  0 ]
                # [ 1  0  0 ]

                banned_mask = (
                    sparse(banned_mask.t(), indices, scores.size())
                        .toarray()
                        .astype(np.bool)
                )

                if self.static_bad_words_mask is not None:
                    banned_mask = np.bitwise_or(banned_mask, self.static_bad_words_mask)
            else:
                banned_mask = self.static_bad_words_mask

            return masked_fill(scores, banned_mask)
