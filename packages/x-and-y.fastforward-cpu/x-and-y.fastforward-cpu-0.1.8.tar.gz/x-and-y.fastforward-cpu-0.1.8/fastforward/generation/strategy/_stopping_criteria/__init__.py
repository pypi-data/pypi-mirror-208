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

from typing import Optional

import numpy as np

from fastforward.generation.generation_config import GenerationConfig
from fastforward.generation.strategy._stopping_criteria.max_length_criteria import MaxLengthCriteria
from fastforward.generation.strategy._stopping_criteria.max_new_tokens_criteria import MaxNewTokensCriteria
from fastforward.generation.strategy._stopping_criteria.max_time_criteria import MaxTimeCriteria


class StoppingCriteriaList(list):
    def __call__(self, input_ids: np.array, scores: np.array, **kwargs) -> bool:
        return any(criteria(input_ids, scores) for criteria in self)

    @property
    def max_length(self) -> Optional[int]:
        for stopping_criterium in self:
            if isinstance(stopping_criterium, MaxLengthCriteria):
                return stopping_criterium.max_length
            elif isinstance(stopping_criterium, MaxNewTokensCriteria):
                return stopping_criterium.max_length
        return None


def get_stopping_criteria(config: GenerationConfig) -> StoppingCriteriaList:
    stopping_criteria = StoppingCriteriaList()
    if config.max_length is not None:
        stopping_criteria.append(MaxLengthCriteria(max_length=config.max_length))
    if config.max_time is not None:
        stopping_criteria.append(MaxTimeCriteria(max_time=config.max_time))
    if config.max_new_tokens is not None:
        stopping_criteria.append(
            MaxNewTokensCriteria(start_length=config.input_ids.shape[-1], max_new_tokens=config.max_new_tokens))
    return stopping_criteria
