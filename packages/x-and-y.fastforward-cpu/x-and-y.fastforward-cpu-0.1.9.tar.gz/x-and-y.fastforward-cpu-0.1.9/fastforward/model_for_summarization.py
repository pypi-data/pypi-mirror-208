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

from typing import Union, List, Optional

from onnxruntime import InferenceSession

from fastforward.engine.abstract_engine import EngineListeners
from fastforward.generation.generation_config import GenerationConfig
from fastforward.generation.generation_mixin import GenerationMixin
from fastforward.model import FastForwardModel


class ModelForSummarization(GenerationMixin, FastForwardModel):
    """
    This class is used as a wrapper of text embedding ONNX models.
    """

    def __init__(self, config_path: str, listeners: Optional[EngineListeners] = None):
        super().__init__(config_path, listeners)

    def __call__(self, text: Union[str, List[str]], **kwargs):
        input = self.sequence_to_ids(text)
        output = self.generate(GenerationConfig(self.config, **input, **kwargs))

        return self.ids_to_sequence(output)

    def get_onnx_session(self) -> InferenceSession:
        return self.generator.decoder.onnx_session
