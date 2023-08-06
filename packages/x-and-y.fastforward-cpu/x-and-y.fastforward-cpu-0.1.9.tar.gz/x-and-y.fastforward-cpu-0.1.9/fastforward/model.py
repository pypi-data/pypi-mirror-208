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

from abc import ABC
from typing import Union

from fastforward.config import ModelConfig
from fastforward.mixin.registry_mixin import ModelHubMixin

Config_Path = str
Model = Union['OnnxModel', Config_Path]


class FastForwardModel(ModelHubMixin, ABC):

    def __init__(self, config_path: str):
        self.config = ModelConfig.from_path(config_path)
        self.config_path = config_path
