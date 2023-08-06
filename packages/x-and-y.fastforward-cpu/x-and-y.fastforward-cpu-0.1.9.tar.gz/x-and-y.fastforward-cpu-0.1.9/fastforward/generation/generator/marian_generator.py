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

from fastforward.config import ModelConfig
from fastforward.engine.abstract_engine import EngineListeners
from fastforward.generation.generator.abstract_generator import AbstractGenerator


class MarianGenerator(AbstractGenerator):
    def __init__(self, config: ModelConfig, listeners: EngineListeners):
        super().__init__(config, listeners)

    def adjust_logits_during_generation(self, logits: np.array, **kwargs) -> np.array:
        """
        Adjust tokens for Marian. For Marian we have to make sure that the `pad_token_id`
        cannot be generated both before and after the `log_softmax` operation.
        :param logits: the logits to adjust
        :param kwargs: custom arguments
        :return: np.array
        """
        logits[:, self.config.pad_token_id] = float("-inf")  # never predict pad token.
        return logits
