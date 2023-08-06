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


class InfNanRemoveLogitsProcessor(LogitsProcessor):
    r"""
    :class:`~transformers.LogitsProcessor` that removes all :obj:`nan` and :obj:`inf` values to avoid the generation
    method to fail. Note that using the logits processor should only be used if necessary since it can slow down the
    generation method. :obj:`max_length` is reached.
    """

    def __call__(self, input_ids: np.array, scores: np.array) -> np.array:
        # set all nan values to 0.0
        scores[scores != scores] = 0.0

        # set all inf values to max possible value
        scores[scores == float("inf")] = np.finfo(scores.dtype).max

        return scores