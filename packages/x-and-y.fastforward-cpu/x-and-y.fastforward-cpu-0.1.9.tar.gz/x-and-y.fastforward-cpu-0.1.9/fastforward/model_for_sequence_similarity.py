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

from typing import Union, Tuple, List

from fastforward.engine.abstract_engine import EngineListeners
from fastforward.model import FastForwardModel
from fastforward.model_for_encoding import ModelForEncoding
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig
from fastforward.utils import cosine_similarity, as_list

Batch = Union[Tuple[str, str], List[Tuple[str, str]]]


class ModelForSequenceSimilarity(FastForwardModel):
    """
    This class is used as a wrapper of text similarity ONNX models.
    """

    def __init__(self, config_path: str, listeners: EngineListeners = None):
        super().__init__(config_path)
        self.encoder = ModelForEncoding(config_path, listeners)

    def __call__(self, batch: Batch, config: EncodingConfig = EncodingConfig()):
        batch = [[x[0], x[1]] for x in as_list(batch)]
        batch = [item for sublist in batch for item in sublist]

        outputs = self.encoder(batch, config)
        outputs = iter(outputs)
        return list(map(lambda x: cosine_similarity(x[0], x[1]), zip(outputs, outputs)))
