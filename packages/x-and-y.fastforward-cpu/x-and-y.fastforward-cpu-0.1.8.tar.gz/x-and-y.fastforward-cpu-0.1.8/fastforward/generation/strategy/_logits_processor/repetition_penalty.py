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


class RepetitionPenaltyLogitsProcessor(LogitsProcessor):
    r"""
    :class:`transformers.LogitsProcessor` enforcing an exponential penalty on repeated sequences.

    Args:
        penalty (:obj:`float`):
            The parameter for repetition penalty. 1.0 means no penalty. See `this paper
            <https://arxiv.org/pdf/1909.05858.pdf>`__ for more details.
    """

    def __init__(self, penalty: float):
        if not isinstance(penalty, float) or not (penalty > 0):
            raise ValueError(f"`penalty` has to be a strictly positive float, but is {penalty}")

        self.penalty = penalty

    def __call__(self, input_ids: np.array, scores: np.array) -> np.array:
        # score = torch.gather(scores, 1, input_ids)
        score = np.take_along_axis(scores, input_ids, 1)

        # if score < 0 then repetition penalty has to be multiplied to reduce the previous token probability
        score = np.where(score < 0, score * self.penalty, score / self.penalty)

        self.scatter(scores, 1, input_ids, score)
        return scores

    # implementation of torch's tensor.scatter_ in numpy
    @staticmethod
    def scatter(a, dim, index, b):
        expanded_index = [index if dim==i else np.arange(a.shape[i]).reshape([-1 if i==j else 1 for j in range(a.ndim)]) for i in range(a.ndim)]
        a[tuple(expanded_index)] = b
