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
from fastforward.generation.strategy.beam.beam_search_scorer import BeamScorer
from fastforward.utils.numpy_utils import topk, softmax, expand_as


class BeamSearch:

    def __init__(self, step: AbstractGenerator, config):
        self.step = step
        self.config = config

    def beam_search(
            self,
            input_ids: np.array,
            beam_scorer: BeamScorer,
            logits_processor: Optional[LogitsProcessorList] = None,
            stopping_criteria: Optional[StoppingCriteriaList] = None,
            pad_token_id: Optional[int] = None,
            eos_token_id: Optional[int] = None,
            **model_kwargs,
    ) -> np.array:
        r"""
        Generates sequences for models with a language modeling head using beam search decoding.
    
        Parameters:
    
            input_ids (:obj:`torch.LongTensor` of shape :obj:`(batch_size, sequence_length)`):
                The sequence used as a prompt for the generation.
            beam_scorer (:obj:`BeamScorer`):
                An derived instance of :class:`~transformers.BeamScorer` that defines how beam hypotheses are
                constructed, stored and sorted during generation. For more information, the documentation of
                :class:`~transformers.BeamScorer` should be read.
            logits_processor (:obj:`LogitsProcessorList`, `optional`):
                An instance of :class:`~transformers.LogitsProcessorList`. List of instances of class derived from
                :class:`~transformers.LogitsProcessor` used to modify the prediction scores of the language modeling
                head applied at each generation step.
            stopping_criteria (:obj:`StoppingCriteriaList`, `optional`):
                An instance of :class:`~transformers.StoppingCriteriaList`. List of instances of class derived from
                :class:`~transformers.StoppingCriteria` used to tell if the generation loop should stop.
            max_length (:obj:`int`, `optional`, defaults to 20):
                **DEPRECATED**. Use :obj:`logits_processor` or :obj:`stopping_criteria` directly to cap the number of
                generated tokens. The maximum length of the sequence to be generated.
            pad_token_id (:obj:`int`, `optional`):
                The id of the `padding` token.
            eos_token_id (:obj:`int`, `optional`):
                The id of the `end-of-sequence` token.
            model_kwargs:
                Additional model specific kwargs will be forwarded to the :obj:`forward` function of the model. If
                model is an encoder-decoder model the kwargs should include :obj:`encoder_outputs`.
    
        Return:
            :obj:`numpy array` containing the generated tokens (default behaviour) or a
        """
        # init values
        logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()
        assert len(stopping_criteria) > 0, "You don't have defined any stopping_criteria, this will likely loop forever"

        pad_token_id = pad_token_id if pad_token_id is not None else self.config.pad_token_id
        eos_token_id = eos_token_id if eos_token_id is not None else self.config.eos_token_id

        batch_size = len(beam_scorer._beam_hyps)
        num_beams = beam_scorer.num_beams

        batch_beam_size, cur_len = input_ids.shape

        assert (
                num_beams * batch_size == batch_beam_size
        ), f"Batch dimension of `input_ids` should be {num_beams * batch_size}, but is {batch_beam_size}."

        beam_scores = np.zeros((batch_size, num_beams), dtype=float)
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.reshape((batch_size * num_beams,))

        while True:
            model_inputs = self.step.prepare_inputs_for_generation(input_ids, **model_kwargs)
            outputs = self.step(**model_inputs)

            next_token_logits = outputs.logits[:, -1, :]
            with np.errstate(divide='ignore'):
                next_token_logits = self.step.adjust_logits_during_generation(next_token_logits, cur_len=cur_len)
                next_token_scores = np.log(softmax(next_token_logits, axis=-1))  # (batch_size * num_beams, vocab_size)

            next_token_scores = logits_processor(input_ids, next_token_scores)
            next_token_scores = next_token_scores + expand_as(beam_scores[:, None], next_token_scores)

            # reshape for beam search
            vocab_size = next_token_scores.shape[-1]
            next_token_scores = next_token_scores.reshape(batch_size, num_beams * vocab_size)

            next_token_scores, next_tokens = topk(next_token_scores, 2 * num_beams)

            next_indices = (next_tokens / vocab_size).astype(np.compat.long)
            next_tokens = next_tokens % vocab_size

            # stateless
            beam_outputs = beam_scorer.process(
                input_ids,
                next_token_scores,
                next_tokens,
                next_indices,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
            )
            beam_scores = beam_outputs["next_beam_scores"]
            beam_next_tokens = beam_outputs["next_beam_tokens"]
            beam_idx = beam_outputs["next_beam_indices"]

            input_ids = np.concatenate([input_ids[beam_idx, :], np.expand_dims(beam_next_tokens, axis=-1)], axis=-1)

            model_kwargs = update_model_kwargs_for_generation(
                outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder
            )
            if model_kwargs["past"] is not None:
                model_kwargs["past"] = self.step.reorder_cache(model_kwargs["past"], beam_idx)

            # increase cur_len
            cur_len = cur_len + 1

            if beam_scorer.is_done or stopping_criteria(input_ids, None):
                break

        sequence_outputs = beam_scorer.finalize(
            input_ids,
            beam_scores,
            next_tokens,
            next_indices,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            max_length=stopping_criteria.max_length
        )

        return sequence_outputs["sequences"]
