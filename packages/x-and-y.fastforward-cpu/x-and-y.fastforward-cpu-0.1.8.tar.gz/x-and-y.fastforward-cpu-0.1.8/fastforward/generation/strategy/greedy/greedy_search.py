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

from fastforward.generation.generator.abstract_generator import AbstractGenerator
from fastforward.generation.strategy import update_model_kwargs_for_generation
from fastforward.generation.strategy._logits_processor.abstract_logits_processor import LogitsProcessorList
from fastforward.generation.strategy._stopping_criteria import StoppingCriteriaList
from fastforward.utils.numpy_utils import ones


class GreedySearch:

    def __init__(self, step: AbstractGenerator, config):
        self.step = step
        self.config = config

    def greedy_search(
            self,
            input_ids: np.array,
            logits_processor: Optional[LogitsProcessorList] = None,
            stopping_criteria: Optional[StoppingCriteriaList] = None,
            pad_token_id: Optional[int] = None,
            eos_token_id: Optional[int] = None,
            **model_kwargs,
    ) -> np.array:

        logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()

        pad_token_id = pad_token_id if pad_token_id is not None else self.config.pad_token_id
        eos_token_id = eos_token_id if eos_token_id is not None else self.config.eos_token_id

        # keep track of which sequences are already finished
        # unfinished_sequences = new(input_ids.shape[0]).fill(1)
        unfinished_sequences = ones(input_ids.shape[0], np.int64)
        cur_len = input_ids.shape[-1]

        while True:
            # prepare model inputs
            model_inputs = self.step.prepare_inputs_for_generation(input_ids, **model_kwargs)
            # forward pass to get next token
            outputs = self.step(**model_inputs)

            next_token_logits = outputs.logits[:, -1, :]

            # pre-process distribution
            next_tokens_scores = logits_processor(input_ids, next_token_logits)

            # argmax
            next_tokens = np.argmax(next_tokens_scores, axis=-1)

            # finished sentences should have their next token be a padding token
            if eos_token_id is not None:
                assert pad_token_id is not None, "If eos_token_id is defined, make sure that pad_token_id is defined."
                next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)

            # update generated ids, model inputs, and length for next step
            input_ids = np.concatenate([input_ids, next_tokens[:, None]], axis=-1)
            model_kwargs = update_model_kwargs_for_generation(
                outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder
            )
            cur_len = cur_len + 1

            # if eos_token was found in one sentence, set sentence to finished
            if eos_token_id is not None:
                unfinished_sequences = np.multiply(unfinished_sequences,
                                                   (next_tokens != eos_token_id).astype(np.compat.long))

            # stop when each sentence is finished, or if we exceed the maximum length
            if unfinished_sequences.max() == 0 or stopping_criteria(input_ids, None):
                break

        return input_ids
