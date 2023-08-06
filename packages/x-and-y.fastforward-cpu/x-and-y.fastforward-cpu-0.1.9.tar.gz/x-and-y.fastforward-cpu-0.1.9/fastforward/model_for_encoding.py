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

import numpy as np
import logging
from typing import Optional, Union, List, Tuple

from fastforward.engine.abstract_engine import EngineListeners
from fastforward.engine.onnx_engine import OnnxEngine
from fastforward.generation.generator import auto_tokenizer
from fastforward.model import FastForwardModel
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig, NetworkInfo
from fastforward.tokenizer.tokenizer_config import PaddingStrategy

Batch = Union[str, List[str], Tuple[str, str], List[Tuple[str, str]]]


class ModelForEncoding(FastForwardModel):
    """
    This class is used as a wrapper of text embedding ONNX models.
    """

    def __init__(self, config_path: str, listeners: EngineListeners = None):
        super().__init__(config_path)
        self.engine = OnnxEngine(config_path, "model", listeners or [])

        info = NetworkInfo(self.engine.get_model_input(), self.engine.get_model_output())
        self.tokenizer = auto_tokenizer(self.config, info)
        self.enc_config = EncodingConfig.from_config(self.config_path)

    def __call__(self, batch: Batch, config: Optional[EncodingConfig] = None):
        config = config if config else self.enc_config
        squeeze = not isinstance(batch, list)

        inputs = self.tokenizer.encode(batch, config)
        outputs = self.engine.execute(inputs)

        if len(outputs) == 1:
            return np.squeeze(outputs[0]) if squeeze else outputs[0]

        output_names = self.engine.get_model_output().names
        outputs = {k: v for k, v in zip(output_names, outputs)}

        return np.squeeze(outputs[config.output_name]) if squeeze else outputs[config.output_name]

    def get_output_dim(self) -> int:
        """
        Returns the output dimension of the onnx model. Some models cannot infer the output shape due to unsupported
        shape inferences. In this case the method tries to resolve the output dimension from the model config.
        :return: int
        """

        output_name = list(self.engine.get_model_output().shapes.keys())[0]
        shape = self.engine.get_model_output().shapes[output_name][1]

        if isinstance(shape, str):
            logging.warning("cannot determine output shape from onnx session. try to return dim from config")
            assert "dim" in self.config.config, "cannot determine output dim"
            return self.config.dim
        # noinspection PyTypeChecker
        return shape
