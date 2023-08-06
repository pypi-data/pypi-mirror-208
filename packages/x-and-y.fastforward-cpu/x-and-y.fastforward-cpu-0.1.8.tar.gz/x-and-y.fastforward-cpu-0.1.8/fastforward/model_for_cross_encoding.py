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

from typing import Optional, Union, Tuple, List

import numpy as np

from fastforward.engine.abstract_engine import EngineListeners
from fastforward.engine.onnx_engine import OnnxEngine
from fastforward.model import FastForwardModel
from fastforward.model_for_encoding import ModelForEncoding
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig
from fastforward.tokenizer.tokenizer_config import PaddingStrategy
from fastforward.utils import sigmoid

Batch = Union[Tuple[str, str], List[Tuple[str, str]]]


class ModelForCrossEncoding(FastForwardModel):
    """
    This class is used as a wrapper of cross-encoding ONNX models.
    The output of the encode method is either the logits value or a probability calculated by sigmoid.
    """

    def __init__(self, config_path: str, listeners: EngineListeners = None, use_sigmoid: bool = True):
        super().__init__(config_path)
        self.engine = OnnxEngine(config_path, "model", listeners or [])
        self.encoder = ModelForEncoding(config_path)
        self.use_sigmoid = use_sigmoid

    def __call__(self, batch: Batch, config: Optional[EncodingConfig] = None):
        logits = np.squeeze(self.encoder(batch, config))
        return sigmoid(logits) if self.use_sigmoid else logits
