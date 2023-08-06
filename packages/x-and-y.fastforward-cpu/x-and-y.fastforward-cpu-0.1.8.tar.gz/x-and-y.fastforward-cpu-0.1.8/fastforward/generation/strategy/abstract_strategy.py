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

from abc import ABC
from typing import Tuple, Dict, Any

import numpy as np

from fastforward.config import CallableDict


class SearchStrategy(ABC):

    def expand_inputs_for_generation(
            self,
            input_ids: np.array,
            expand_size: int = 1,
            is_encoder_decoder: bool = False,
            attention_mask: np.array = None,
            encoder_outputs: CallableDict = None,
            **model_kwargs,
    ) -> Tuple[np.array, Dict[str, Any]]:
        expanded_return_idx = (
            np.arange(input_ids.shape[0]).reshape(-1, 1).repeat(expand_size)
        )
        input_ids = input_ids.take(expanded_return_idx, axis=0)

        if "token_type_ids" in model_kwargs:
            token_type_ids = model_kwargs["token_type_ids"]
            model_kwargs["token_type_ids"] = token_type_ids.take(expanded_return_idx, axis=0)

        if attention_mask is not None:
            model_kwargs["attention_mask"] = attention_mask.take(expanded_return_idx, axis=0)

        if is_encoder_decoder:
            assert encoder_outputs is not None
            encoder_outputs["last_hidden_state"] = encoder_outputs.last_hidden_state.take(expanded_return_idx, axis=0)
            model_kwargs["encoder_outputs"] = encoder_outputs
        return input_ids, model_kwargs



