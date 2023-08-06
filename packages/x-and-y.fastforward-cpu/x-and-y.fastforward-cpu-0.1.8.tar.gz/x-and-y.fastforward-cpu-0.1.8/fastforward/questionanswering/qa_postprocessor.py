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

from typing import Tuple

import numpy as np

from fastforward.config import ModelConfig
from fastforward.generation.generator import auto_tokenizer
from fastforward.model_for_generic import ModelForGeneric
from fastforward.tokenizer.abstract_tokenizer import NetworkInfo, EncodingConfig


class QuestionAnsweringPostprocessor:

    def __init__(self, config_path: str):
        self.config = ModelConfig.from_path(config_path)
        self.encoder = ModelForGeneric(config_path)
        self.tokenizer = auto_tokenizer(self.config, NetworkInfo(self.encoder.engine.get_model_input(), self.encoder.engine.get_model_output()))

    def __call__(
            self,
            model_outputs,
            top_k=1,
            handle_impossible_answer=False,
            max_answer_len=15,
            config: EncodingConfig = EncodingConfig()
    ):
        min_null_score = 1000000  # large and positive
        answers = []
        example = model_outputs["example"]
        for i, (feature_, start_, end_) in enumerate(
                zip(model_outputs["features"], model_outputs["starts"], model_outputs["ends"])
        ):
            feature = feature_["others"]
            # Ensure padded tokens & question tokens cannot belong to the set of candidate answers.
            undesired_tokens = np.abs(np.array(feature["p_mask"]) - 1)

            if feature_["fw_args"].get("attention_mask", None) is not None:
                undesired_tokens = undesired_tokens & feature_["fw_args"]["attention_mask"]

            # Generate mask
            undesired_tokens_mask = undesired_tokens == 0.0

            # Make sure non-context indexes in the tensor cannot contribute to the softmax
            start_ = np.where(undesired_tokens_mask, -10000.0, start_)
            end_ = np.where(undesired_tokens_mask, -10000.0, end_)

            # Normalize logits and spans to retrieve the answer
            start_ = np.exp(start_ - np.log(np.sum(np.exp(start_), axis=-1, keepdims=True)))
            end_ = np.exp(end_ - np.log(np.sum(np.exp(end_), axis=-1, keepdims=True)))

            if handle_impossible_answer:
                min_null_score = min(min_null_score, (start_[0] * end_[0]).item())

            # Mask CLS
            start_[0, 0] = end_[0, 0] = 0.0

            starts, ends, scores = self.decode(start_, end_, top_k, max_answer_len, undesired_tokens)

            # Convert the answer (tokens) back to the original text
            # Score: score from the model
            # Start: Index of the first character of the answer in the context string
            # End: Index of the character following the last character of the answer in the context string
            # Answer: Plain text of the answer
            question_first = config.padding_direction.value == "right"
            enc = feature["encoding"]

            # Sometimes the max probability token is in the middle of a word so:
            # - we start by finding the right word containing the token with `token_to_word`
            # - then we convert this word in a character span with `word_to_chars`
            sequence_index = 1 if question_first else 0
            for s, e, score in zip(starts, ends, scores):
                try:
                    start_word = enc.token_to_word(s)
                    end_word = enc.token_to_word(e)
                    start_index = enc.word_to_chars(start_word, sequence_index=sequence_index)[0]
                    end_index = enc.word_to_chars(end_word, sequence_index=sequence_index)[1]
                except Exception:
                    # Some tokenizers don't really handle words. Keep to offsets then.
                    start_index = enc.offsets[s][0]
                    end_index = enc.offsets[e][1]

                answers.append(
                    {
                        "score": score.item(),
                        "start": start_index,
                        "end": end_index,
                        "answer": example.context_text[start_index:end_index],
                    }
                )

        if handle_impossible_answer:
            answers.append({"score": min_null_score, "start": 0, "end": 0, "answer": ""})
        answers = sorted(answers, key=lambda x: x["score"], reverse=True)[:top_k]
        if len(answers) == 1:
            return answers[0]
        return answers

    def decode(
            self, start: np.ndarray, end: np.ndarray, topk: int, max_answer_len: int, undesired_tokens: np.ndarray
    ) -> Tuple:
        """
        Take the output of any :obj:`ModelForQuestionAnswering` and will generate probabilities for each span to be the
        actual answer.

        In addition, it filters out some unwanted/impossible cases like answer len being greater than max_answer_len or
        answer end position being before the starting position. The method supports output the k-best answer through
        the topk argument.

        Args:
            start (:obj:`np.ndarray`): Individual start probabilities for each token.
            end (:obj:`np.ndarray`): Individual end probabilities for each token.
            topk (:obj:`int`): Indicates how many possible answer span(s) to extract from the model output.
            max_answer_len (:obj:`int`): Maximum size of the answer to extract from the model's output.
            undesired_tokens (:obj:`np.ndarray`): Mask determining tokens that can be part of the answer
        """
        # Ensure we have batch axis
        if start.ndim == 1:
            start = start[None]

        if end.ndim == 1:
            end = end[None]

        # Compute the score of each tuple(start, end) to be the real answer
        outer = np.matmul(np.expand_dims(start, -1), np.expand_dims(end, 1))

        # Remove candidate with end < start and end - start > max_answer_len
        candidates = np.tril(np.triu(outer), max_answer_len - 1)

        #  Inspired by Chen & al. (https://github.com/facebookresearch/DrQA)
        scores_flat = candidates.flatten()
        if topk == 1:
            idx_sort = [np.argmax(scores_flat)]
        elif len(scores_flat) < topk:
            idx_sort = np.argsort(-scores_flat)
        else:
            idx = np.argpartition(-scores_flat, topk)[0:topk]
            idx_sort = idx[np.argsort(-scores_flat[idx])]

        starts, ends = np.unravel_index(idx_sort, candidates.shape)[1:]
        desired_spans = np.isin(starts, undesired_tokens.nonzero()) & np.isin(ends, undesired_tokens.nonzero())
        starts = starts[desired_spans]
        ends = ends[desired_spans]
        scores = candidates[0, starts, ends]

        return starts, ends, scores
