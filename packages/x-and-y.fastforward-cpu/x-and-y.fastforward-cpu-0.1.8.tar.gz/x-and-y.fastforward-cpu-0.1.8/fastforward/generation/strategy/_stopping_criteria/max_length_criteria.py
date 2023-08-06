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

from fastforward.generation.strategy._stopping_criteria.abstract_stopping_criteria import StoppingCriteria


class MaxLengthCriteria(StoppingCriteria):
    """
    This class can be used to stop generation whenever the full generated number of tokens exceeds :obj:`max_length`.
    Keep in mind for decoder-only type of transformers, this will include the initial prompted tokens.

    Args:
        max_length (:obj:`int`):
            The maximum length that the output sequence can have in number of tokens.
    """

    def __init__(self, max_length: int):
        self.max_length = max_length

    def __call__(self, input_ids: np.array, scores: np.array, **kwargs) -> bool:
        return input_ids.shape[-1] >= self.max_length
