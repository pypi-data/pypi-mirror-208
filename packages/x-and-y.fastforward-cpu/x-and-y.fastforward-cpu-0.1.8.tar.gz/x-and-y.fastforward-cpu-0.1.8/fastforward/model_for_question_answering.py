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

from typing import Union, List

from fastforward.engine.abstract_engine import EngineListeners
from fastforward.model import FastForwardModel
from fastforward.model_for_generic import ModelForGeneric
from fastforward.questionanswering.qa_postprocessor import QuestionAnsweringPostprocessor
from fastforward.questionanswering.qa_preprocessor import QuestionAnsweringPreprocessor
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig

QAInput = Union[str, List[str]]


class ModelForQuestionAnswering(FastForwardModel):

    def __init__(self, config_path: str, listeners: EngineListeners = None):
        super().__init__(config_path)
        self.encoder = ModelForGeneric(config_path, listeners=listeners)
        self.preprocessor = QuestionAnsweringPreprocessor(config_path)
        self.postprocessor = QuestionAnsweringPostprocessor(config_path)

    def __call__(self, contexts: QAInput, questions: QAInput, config: EncodingConfig = EncodingConfig()):
        samples = self.preprocessor(contexts, questions, config)

        outputs = []
        for sample in samples:
            features = sample["features"]
            example = sample["example"]
            starts = []
            ends = []
            for feature in features:
                fw_args = feature["fw_args"]

                start, end = self.encoder(**fw_args)[:2]
                starts.append(start)
                ends.append(end)

                outputs.append({"starts": starts, "ends": ends, "features": features, "example": example})

        return list(map(lambda x: self.postprocessor(x, config=config), outputs))
