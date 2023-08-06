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
from typing import Optional

import numpy as np

from fastforward.engine.abstract_engine import EngineListeners
from fastforward.model import FastForwardModel
from fastforward.model_for_encoding import ModelForEncoding
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig
from fastforward.utils import softmax, as_list


class ModelForSequenceClassification(FastForwardModel):
    """
    This class is used as a wrapper of text classification ONNX models.
    """

    def __init__(self, config_path: str, listeners: EngineListeners = None):
        super().__init__(config_path)
        self.encoder = ModelForEncoding(config_path, listeners)

    def __call__(self, batch, return_scores: bool = False, config: Optional[EncodingConfig] = None):
        outputs = self.encoder(batch, config)
        if return_scores:
            return list(map(softmax, outputs[0]))
        label_ids = as_list(np.argmax(outputs, axis=len(outputs.shape) - 1))
        return [self.encoder.config.id2label(label_id) for label_id in label_ids]
