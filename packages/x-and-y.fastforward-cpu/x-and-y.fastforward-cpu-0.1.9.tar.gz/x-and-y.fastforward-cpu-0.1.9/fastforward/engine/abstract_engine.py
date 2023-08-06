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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional

from onnxruntime.capi.onnxruntime_pybind11_state import SessionOptions


@dataclass
class ModelIO(ABC):
    """
    This data class contains all information about model input nodes.
    This information can be used by a tokenizer to prepare the model input.
    """
    names: List[str]
    types: Dict[str, str]
    shapes: Dict[str, List[str]]


class Engine(ABC):

    @abstractmethod
    def execute(self, inputs: dict):
        pass

    @abstractmethod
    def get_model_input(self) -> ModelIO:
        pass

    @abstractmethod
    def get_model_output(self) -> ModelIO:
        pass


class EngineListener(ABC):

    @abstractmethod
    def initialize(self, session_options: SessionOptions):
        pass


EngineListeners = Optional[List[EngineListener]]