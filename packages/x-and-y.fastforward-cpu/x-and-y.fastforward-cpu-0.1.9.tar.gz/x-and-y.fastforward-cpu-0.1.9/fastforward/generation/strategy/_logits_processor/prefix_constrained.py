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

import math
from typing import List, Callable

import numpy as np

from fastforward.generation.strategy._logits_processor.abstract_logits_processor import LogitsProcessor


class PrefixConstrainedLogitsProcessor(LogitsProcessor):
    r"""
    :class:`transformers.LogitsProcessor` that enforces constrained generation and is useful for prefix-conditioned
    constrained generation. See `Autoregressive Entity Retrieval <https://arxiv.org/abs/2010.00904>`__ for more
    information.

    Args:
        prefix_allowed_tokens_fn: (:obj:`Callable[[int, np.array], List[int]]`):
            This function constraints the beam search to allowed tokens only at each step. This function takes 2
            arguments :obj:`inputs_ids` and the batch ID :obj:`batch_id`. It has to return a list with the allowed
            tokens for the next generation step conditioned on the previously generated tokens :obj:`inputs_ids` and
            the batch ID :obj:`batch_id`.
    """

    def __init__(self, prefix_allowed_tokens_fn: Callable[[int, np.array], List[int]], num_beams: int):
        self._prefix_allowed_tokens_fn = prefix_allowed_tokens_fn
        self._num_beams = num_beams

    def __call__(self, input_ids: np.array, scores: np.array) -> np.array:
        mask = np.full_like(scores, -math.inf)
        for batch_id, beam_sent in enumerate(input_ids.view(-1, self._num_beams, input_ids.shape[-1])):
            for beam_id, sent in enumerate(beam_sent):
                mask[batch_id * self._num_beams + beam_id, self._prefix_allowed_tokens_fn(batch_id, sent)] = 0

        return scores + mask