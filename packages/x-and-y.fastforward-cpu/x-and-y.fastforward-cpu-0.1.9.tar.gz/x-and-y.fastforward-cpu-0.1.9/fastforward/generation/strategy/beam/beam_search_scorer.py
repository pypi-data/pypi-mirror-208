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

from abc import abstractmethod, ABC
from collections import UserDict
from typing import Tuple, Optional

import numpy as np

from fastforward.generation.generation_config import GenerationConfig
from fastforward.utils import coalesce
from fastforward.utils.numpy_utils import new


class BeamScorer(ABC):
    """
    Abstract base class for all beam scorers that are used for :meth:`~transformers.PreTrainedModel.beam_search` and
    :meth:`~transformers.PreTrainedModel.beam_sample`.
    """

    @abstractmethod
    def process(
            self,
            input_ids: np.array,
            next_scores: np.array,
            next_tokens: np.array,
            next_indices: np.array,
            **kwargs
    ) -> Tuple[np.array]:
        raise NotImplementedError("This is an abstract method.")

    @abstractmethod
    def finalize(
            self,
            input_ids: np.array,
            next_scores: np.array,
            next_tokens: np.array,
            next_indices: np.array,
            max_length: int,
            **kwargs
    ) -> np.array:
        raise NotImplementedError("This is an abstract method.")


class BeamSearchScorer(BeamScorer):
    r"""
    :class:`transformers.BeamScorer` implementing standard beam search decoding.

    Adapted in part from `Facebook's XLM beam search code
    <https://github.com/facebookresearch/XLM/blob/9e6f6814d17be4fe5b15f2e6c43eb2b2d76daeb4/src/model/transformer.py#L529>`__.

    Reference for the diverse beam search algorithm and implementation `Ashwin Kalyan's DBS implementation
    <https://github.com/ashwinkalyan/dbs/blob/master/dbs/beam_utils.lua>`__

    Args:
        config (:obj:`GenerationConfig`):
            The config object for the generation task.
    """

    def __init__(self, config: GenerationConfig):
        batch_size = config.input_ids.shape[0]
        self.num_beams = config.num_beams
        self.num_beam_hyps_to_keep = coalesce(config.num_return_sequences, 1)
        self.num_beam_groups = coalesce(config.num_beam_groups, 1)
        self.group_size = self.num_beams // self.num_beam_groups

        self._is_init = False
        self._beam_hyps = [
            BeamHypotheses(
                num_beams=self.num_beams,
                length_penalty=coalesce(config.length_penalty, 1.0),
                early_stopping=coalesce(config.early_stopping, False),
            )
            for _ in range(batch_size)
        ]
        self._done = np.array([False for _ in range(batch_size)], dtype=bool)

        if not isinstance(config.num_beams, int) or config.num_beams <= 1:
            raise ValueError(
                f"`num_beams` has to be an integer strictly greater than 1, but is {config.num_beams}. For `num_beams` == 1, one should make use of `greedy_search` instead."
            )

        if not isinstance(config.num_beam_groups, int) or (config.num_beam_groups > config.num_beams) or (
                config.num_beams % config.num_beam_groups != 0):
            raise ValueError(
                f"`num_beam_groups` has to be an integer smaller or equal than `num_beams` and `num_beams` "
                f"has to be divisible by `num_beam_groups`, but is {config.num_beam_groups} with `num_beams` being {config.num_beams}."
            )

    @property
    def is_done(self) -> bool:
        return self._done.all()

    def process(
            self,
            input_ids: np.array,
            next_scores: np.array,
            next_tokens: np.array,
            next_indices: np.array,
            pad_token_id: Optional[int] = None,
            eos_token_id: Optional[int] = None,
    ) -> Tuple[np.array]:
        cur_len = input_ids.shape[-1]
        batch_size = len(self._beam_hyps)
        assert batch_size == (input_ids.shape[0] // self.group_size)

        next_beam_scores = np.zeros((batch_size, self.group_size), dtype=next_scores.dtype)
        next_beam_tokens = np.zeros((batch_size, self.group_size), dtype=next_tokens.dtype)
        next_beam_indices = np.zeros((batch_size, self.group_size), dtype=next_indices.dtype)

        for batch_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_idx]:
                expr1 = len(beam_hyp) >= self.num_beams
                expr2 = eos_token_id is not None and pad_token_id is not None
                assert expr1, f"Batch can only be done if at least {self.num_beams} beams have been generated"
                assert expr2, "generated beams >= num_beams -> eos_token_id and pad_token have to be defined"
                # pad the batch
                next_beam_scores[batch_idx, :] = 0
                next_beam_tokens[batch_idx, :] = pad_token_id
                next_beam_indices[batch_idx, :] = 0
                continue

            # next tokens for this sentence
            beam_idx = 0
            for beam_token_rank, (next_token, next_score, next_index) in enumerate(
                    zip(next_tokens[batch_idx], next_scores[batch_idx], next_indices[batch_idx])
            ):
                batch_beam_idx = batch_idx * self.group_size + next_index
                # add to generated hypotheses if end of sentence
                if (eos_token_id is not None) and (next_token.item() == eos_token_id):
                    # if beam_token does not belong to top num_beams tokens, it should not be added
                    is_beam_token_worse_than_top_num_beams = beam_token_rank >= self.group_size
                    if is_beam_token_worse_than_top_num_beams:
                        continue
                    beam_hyp.add(
                        input_ids[batch_beam_idx].copy(),
                        next_score.item(),
                    )
                else:
                    # add next predicted token since it is not eos_token
                    next_beam_scores[batch_idx, beam_idx] = next_score
                    next_beam_tokens[batch_idx, beam_idx] = next_token
                    next_beam_indices[batch_idx, beam_idx] = batch_beam_idx
                    beam_idx += 1

                # once the beam for next step is full, don't add more tokens to it.
                if beam_idx == self.group_size:
                    break

            if beam_idx < self.group_size:
                raise ValueError(
                    f"At most {self.group_size} tokens in {next_tokens[batch_idx]} can be equal to `eos_token_id: {eos_token_id}`. Make sure {next_tokens[batch_idx]} are corrected."
                )

            # Check if we are done so that we can save a pad step if all(done)
            self._done[batch_idx] = self._done[batch_idx] or beam_hyp.is_done(
                next_scores[batch_idx].max().item(), cur_len
            )

        # noinspection PyTypeChecker
        return UserDict({
            "next_beam_scores": next_beam_scores.reshape(-1),
            "next_beam_tokens": next_beam_tokens.reshape(-1),
            "next_beam_indices": next_beam_indices.reshape(-1),
        })

    def finalize(
            self,
            input_ids: np.array,
            final_beam_scores: np.array,
            final_beam_tokens: np.array,
            final_beam_indices: np.array,
            max_length: int,
            pad_token_id: Optional[int] = None,
            eos_token_id: Optional[int] = None,
    ) -> Tuple[np.array]:
        batch_size = len(self._beam_hyps)

        # finalize all open beam hypotheses and add to generated hypotheses
        for batch_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_idx]:
                continue

            # all open beam hypotheses are added to the beam hypothesis
            # beam hypothesis class automatically keeps the best beams
            for beam_id in range(self.num_beams):
                batch_beam_idx = batch_idx * self.num_beams + beam_id
                final_score = final_beam_scores[batch_beam_idx].item()
                final_tokens = input_ids[batch_beam_idx]
                beam_hyp.add(final_tokens, final_score)

        # select the best hypotheses
        sent_lengths = new(batch_size * self.num_beam_hyps_to_keep).astype(int)
        best = []
        best_scores = np.zeros(batch_size * self.num_beam_hyps_to_keep, dtype=np.float32)

        # retrieve best hypotheses
        for i, beam_hyp in enumerate(self._beam_hyps):
            sorted_hyps = sorted(beam_hyp.beams, key=lambda x: x[0])
            for j in range(self.num_beam_hyps_to_keep):
                best_hyp_tuple = sorted_hyps.pop()
                best_score = best_hyp_tuple[0]
                best_hyp = best_hyp_tuple[1]
                sent_lengths[self.num_beam_hyps_to_keep * i + j] = len(best_hyp)

                # append to lists
                best.append(best_hyp)
                best_scores[i * self.num_beam_hyps_to_keep + j] = best_score

        # prepare for adding eos
        sent_max_len = min(sent_lengths.max().item() + 1, max_length)
        decoded: np.array = new((batch_size * self.num_beam_hyps_to_keep, sent_max_len))
        # shorter batches are padded if needed
        if sent_lengths.min().item() != sent_lengths.max().item():
            assert pad_token_id is not None, "`pad_token_id` has to be defined"
            decoded.fill(pad_token_id)

        # fill with hypotheses and eos_token_id if the latter fits in
        for i, hypo in enumerate(best):
            decoded[i, : sent_lengths[i]] = hypo
            if sent_lengths[i] < max_length:
                decoded[i, sent_lengths[i]] = eos_token_id
        # noinspection PyTypeChecker
        return UserDict({
            "sequences": decoded,
            "sequence_scores": best_scores,
        })


class BeamHypotheses:
    def __init__(self, num_beams: int, length_penalty: float, early_stopping: bool):
        """
        Initialize n-best list of hypotheses.
        """
        self.length_penalty = length_penalty
        self.early_stopping = early_stopping
        self.num_beams = num_beams
        self.beams = []
        self.worst_score = 1e9

    def __len__(self):
        """
        Number of hypotheses in the list.
        """
        return len(self.beams)

    def add(self, hyp: np.array, sum_logprobs: float):
        """
        Add a new hypothesis to the list.
        """
        score = sum_logprobs / (hyp.shape[-1] ** self.length_penalty)
        if len(self) < self.num_beams or score > self.worst_score:
            self.beams.append((score, hyp))
            if len(self) > self.num_beams:
                sorted_next_scores = sorted([(s, idx) for idx, (s, _) in enumerate(self.beams)])
                del self.beams[sorted_next_scores[0][1]]
                self.worst_score = sorted_next_scores[1][0]
            else:
                self.worst_score = min(score, self.worst_score)

    def is_done(self, best_sum_logprobs: float, cur_len: int) -> bool:
        """
        If there are enough hypotheses and that none of the hypotheses being generated can become better than the worst
        one in the heap, then we are done with this sentence.
        """

        if len(self) < self.num_beams:
            return False
        elif self.early_stopping:
            return True
        else:
            cur_score = best_sum_logprobs / cur_len ** self.length_penalty
            ret = self.worst_score >= cur_score
            return ret
