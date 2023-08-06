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

import os
from pathlib import Path


def get_default_model_hub_url():
    default_url = "https://fastforward.x-and-y.ai/api/dispatch"
    return from_env("FAST_FORWARD_MODEL_HUB_URL", default_url)


def get_default_cache_dir():
    return from_env("FAST_FORWARD_CACHE_DIR", str(Path.home() / ".fastforward/cache").replace("\\", "/"))


def from_env(key: str, default_value: str):
    return os.environ[key] if key in os.environ else default_value


def bool_from_env(key: str, default_value: bool):
    return os.environ[key] in ["true", "True"] if key in os.environ else default_value


def int_from_env(key: str, default_value: int):
    return int(os.environ[key]) if key in os.environ else default_value
