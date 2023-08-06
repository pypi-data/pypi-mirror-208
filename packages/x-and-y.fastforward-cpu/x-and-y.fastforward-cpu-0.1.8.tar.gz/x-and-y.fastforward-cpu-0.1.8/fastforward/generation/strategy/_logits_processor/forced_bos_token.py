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

from fastforward.generation.strategy._logits_processor.abstract_logits_processor import LogitsProcessor


class ForcedBOSTokenLogitsProcessor(LogitsProcessor):
    r"""
    :class:`~transformers.LogitsProcessor` that enforces the specified token as the first generated token.

    Args:
        bos_token_id (:obj:`int`):
            The id of the token to force as the first generated token.
    """

    def __init__(self, bos_token_id: int):
        self.bos_token_id = bos_token_id

    def __call__(self, input_ids: np.array, scores: np.array) -> np.array:
        cur_len = input_ids.shape[-1]
        if cur_len == 1:
            num_tokens = scores.shape[1]
            scores[:, [i for i in range(num_tokens) if i != self.bos_token_id]] = -float("inf")
            scores[:, self.bos_token_id] = 0
        return scores