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

import json
from collections import OrderedDict
from dataclasses import dataclass
from os.path import exists
from typing import Tuple, Any, Optional

from fastforward.utils import load_json
from fastforward.utils.environment import get_default_cache_dir, get_default_model_hub_url


def from_json(path: str):
    """
    Converts the json file at the given path to a dict.

    :param path: the path to the json file
    :return: dict
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class ModelHubConfig:
    url: str = get_default_model_hub_url()
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    zip_secret: Optional[str] = None
    cache: str = get_default_cache_dir()


@dataclass
class ModelConfig:
    config: dict

    @staticmethod
    def from_path(config_path: str):
        assert exists(config_path + "/config.json"), f"no config file found at {config_path}"
        config = load_json(config_path + "/config.json")
        config["config_path"] = config_path
        return ModelConfig(config)

    def __getattr__(self, item):
        return self.config[item] if item in self.config else None

    def id2label(self, _id: int):
        dictionary = self.config["id2label"] if "id2label" in self.config else {}
        if _id in dictionary:
            return dictionary[_id]
        if str(_id) in dictionary:
            return dictionary[str(_id)]
        return _id


class CallableDict(OrderedDict):

    def __init__(self, _dict):
        super().__init__(_dict)

    def __getattr__(self, item):
        return self.get(item)

    def __getitem__(self, item):
        if isinstance(item, str):
            inner_dict = {k: v for (k, v) in self.items()}
            return inner_dict[item]
        else:
            return self.to_tuple()[item]

    def to_tuple(self) -> Tuple[Any]:
        return tuple(self[k] for k in self.keys())


class ModelInfo(CallableDict):

    def __init__(self, path: str):
        super().__init__(from_json(path + "/info.json"))
