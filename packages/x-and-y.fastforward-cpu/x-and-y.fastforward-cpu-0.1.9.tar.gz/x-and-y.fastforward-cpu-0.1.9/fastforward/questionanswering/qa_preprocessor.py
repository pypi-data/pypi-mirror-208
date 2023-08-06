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

from typing import Union, List, Iterable

import numpy as np

from fastforward.config import ModelConfig
from fastforward.generation.generator import auto_tokenizer
from fastforward.model_for_generic import ModelForGeneric
from fastforward.questionanswering.squad_example import SquadExample
from fastforward.questionanswering.squad_features import SquadFeatures
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig, NetworkInfo
from fastforward.tokenizer.tokenizer_config import TruncationStrategy


class QuestionAnsweringPreprocessor:

    def __init__(self, config_path: str):
        self.config = ModelConfig.from_path(config_path)
        self.encoder = ModelForGeneric(config_path)
        self.tokenizer = auto_tokenizer(self.config, NetworkInfo(self.encoder.engine.get_model_input(),
                                                                 self.encoder.engine.get_model_output()))

    def __call__(self, contexts, questions, config: EncodingConfig):
        samples = self.generate_samples(contexts, questions)
        return list(map(lambda x: self.preprocess(x, config), samples))

    def preprocess(self, example, config: EncodingConfig):

        if config.max_length is None:
            config.max_length = min(self.config.max_position_embeddings, 384)
        if config.stride is None:
            config.stride = min(config.max_length // 4, 128)

        # Define the side we want to truncate / pad and the text/pair sorting
        question_first = config.padding_direction.value == "right"

        input = (
            example.question_text if question_first else example.context_text,
            example.context_text if question_first else example.question_text
        )

        config.truncation_strategy = TruncationStrategy.ONLY_SECOND if question_first else TruncationStrategy.ONLY_FIRST
        config.return_token_type_ids = True
        config.return_overflowing_tokens = True
        config.return_offsets_mapping = True
        config.return_special_tokens_mask = True

        encoded_inputs = self.tokenizer.encode(input, config)
        # When the input is too long, it's converted in a batch of inputs with overflowing tokens
        # and a stride of overlap between the inputs. If a batch of inputs is given, a special output
        # "overflow_to_sample_mapping" indicate which member of the encoded batch belong to which original batch sample.
        # Here we tokenize examples one-by-one so we don't need to use "overflow_to_sample_mapping".
        # "num_span" is the number of output samples generated from the overflowing tokens.
        num_spans = len(encoded_inputs["input_ids"])

        # p_mask: mask with 1 for token than cannot be in the answer (0 for token which can be in an answer)
        # We put 0 on the tokens from the context and 1 everywhere else (question and special tokens)
        p_mask = np.asarray(
            [
                [tok != 1 if question_first else 0 for tok in encoded_inputs.sequence_ids(span_id)]
                for span_id in range(num_spans)
            ]
        )

        # keep the cls_token unmasked (some models use it to indicate unanswerable questions)
        if self.tokenizer.cls_token_id is not None:
            cls_index = np.nonzero(encoded_inputs["input_ids"] == self.tokenizer.cls_token_id)
            p_mask[cls_index] = 0

        features = []
        for span_idx in range(num_spans):
            input_ids_span_idx = encoded_inputs["input_ids"][span_idx]
            attention_mask_span_idx = (
                encoded_inputs["attention_mask"][span_idx] if "attention_mask" in encoded_inputs else None
            )
            token_type_ids_span_idx = (
                encoded_inputs["token_type_ids"][span_idx] if "token_type_ids" in encoded_inputs else None
            )
            submask = p_mask[span_idx]
            if isinstance(submask, np.ndarray):
                submask = submask.tolist()
            features.append(
                SquadFeatures(
                    input_ids=input_ids_span_idx,
                    attention_mask=attention_mask_span_idx,
                    token_type_ids=token_type_ids_span_idx,
                    p_mask=submask,
                    encoding=encoded_inputs.encodings[span_idx],
                    # We don't use the rest of the values - and actually
                    # for Fast tokenizer we could totally avoid using SquadFeatures and SquadExample
                    cls_index=None,
                    token_to_orig_map={},
                    example_index=0,
                    unique_id=0,
                    paragraph_len=0,
                    token_is_max_context=0,
                    tokens=[],
                    start_position=0,
                    end_position=0,
                    is_impossible=False,
                    qas_id=None,
                )
            )

        split_features = []
        for feature in features:
            fw_args = {}
            others = {}
            model_input_names = self.encoder.incoming_vars

            for k, v in feature.__dict__.items():
                if k in model_input_names:
                    fw_args[k] = np.expand_dims(v, axis=0)
                else:
                    others[k] = v
            split_features.append({"fw_args": fw_args, "others": others})
        return {"features": split_features, "example": example}

    def normalize(self, item):
        if isinstance(item, SquadExample):
            return item
        elif isinstance(item, dict):
            for k in ["question", "context"]:
                if k not in item:
                    raise KeyError("You need to provide a dictionary with keys {question:..., context:...}")
                elif item[k] is None:
                    raise ValueError(f"`{k}` cannot be None")
                elif isinstance(item[k], str) and len(item[k]) == 0:
                    raise ValueError(f"`{k}` cannot be empty")

            return self.create_sample(**item)
        raise ValueError(f"{item} argument needs to be of type (SquadExample, dict)")

    def generate_samples(self, contexts, questions):
        if isinstance(questions, list) and isinstance(contexts, str):
            inputs = [{"question": Q, "context": contexts} for Q in questions]
        elif isinstance(questions, list) and isinstance(contexts, list):
            if len(questions) != len(contexts):
                raise ValueError("Questions and contexts don't have the same lengths")

            inputs = [{"question": Q, "context": C} for Q, C in zip(questions, contexts)]
        elif isinstance(questions, str) and isinstance(contexts, str):
            inputs = [{"question": questions, "context": contexts}]
        else:
            raise ValueError("Arguments can't be understood")

        # Normalize inputs
        if isinstance(inputs, dict):
            inputs = [inputs]
        elif isinstance(inputs, Iterable):
            # Copy to avoid overriding arguments
            inputs = [i for i in inputs]
        else:
            raise ValueError(f"Invalid arguments")

        for i, item in enumerate(inputs):
            inputs[i] = self.normalize(item)

        return inputs

    def create_sample(self, question: Union[str, List[str]], context: Union[str, List[str]]
                      ) -> Union[SquadExample, List[SquadExample]]:
        """
        QuestionAnsweringPipeline leverages the :class:`~transformers.SquadExample` internally. This helper method
        encapsulate all the logic for converting question(s) and context(s) to :class:`~transformers.SquadExample`.

        We currently support extractive question answering.

        Arguments:
            question (:obj:`str` or :obj:`List[str]`): The question(s) asked.
            context (:obj:`str` or :obj:`List[str]`): The context(s) in which we will look for the answer.

        Returns:
            One or a list of :class:`~transformers.SquadExample`: The corresponding :class:`~transformers.SquadExample`
            grouping question and context.
        """
        if isinstance(question, list):
            return [SquadExample(None, q, c, None, None, None) for q, c in zip(question, context)]
        else:
            return SquadExample(None, question, context, None, None, None)
