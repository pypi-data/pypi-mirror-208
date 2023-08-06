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

import numpy as np

from fastforward.generation.strategy._logits_processor.abstract_logits_processor import LogitsProcessor, _get_ngrams, \
    _get_generated_ngrams


class EncoderNoRepeatNGramLogitsProcessor(LogitsProcessor):
    r"""
    :class:`transformers.LogitsProcessor` that enforces no repetition of encoder input ids n-grams for the decoder ids.
    See `ParlAI <https://github.com/facebookresearch/ParlAI/blob/master/parlai/core/torch_generator_agent.py#L1350>`__.

    Args:
        encoder_ngram_size (:obj:`int`):
            All ngrams of size :obj:`ngram_size` can only occur within the encoder input ids.
        encoder_input_ids (:obj:`int`):
            The encoder_input_ids that should not be repeated within the decoder ids.
    """

    def __init__(self, encoder_ngram_size: int, encoder_input_ids: np.array):
        if not isinstance(encoder_ngram_size, int) or encoder_ngram_size <= 0:
            raise ValueError(
                f"`encoder_ngram_size` has to be a strictly positive integer, but is {encoder_ngram_size}"
            )
        self.ngram_size = encoder_ngram_size
        if len(encoder_input_ids.shape) == 1:
            encoder_input_ids = encoder_input_ids.unsqueeze(0)
        self.batch_size = encoder_input_ids.shape[0]
        self.generated_ngrams = _get_ngrams(encoder_ngram_size, encoder_input_ids, self.batch_size)

    def __call__(self, input_ids: np.array, scores: np.array) -> np.array:
        # B x num_beams
        num_hypos = scores.shape[0]
        num_beams = num_hypos // self.batch_size
        cur_len = input_ids.shape[-1]
        banned_batch_tokens = [
            _get_generated_ngrams(
                self.generated_ngrams[hypo_idx // num_beams], input_ids[hypo_idx], self.ngram_size, cur_len
            )
            for hypo_idx in range(num_hypos)
        ]

        for i, banned_tokens in enumerate(banned_batch_tokens):
            scores[i, banned_tokens] = -float("inf")

        return scores
