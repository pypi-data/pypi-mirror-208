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

import base64
import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Optional, Union

import requests

from fastforward.config import ModelHubConfig, ModelConfig
from fastforward.engine.abstract_engine import EngineListeners
from fastforward.engine.listener.onnx_listener import OnnxListener


def hmac(key: str, message: str) -> str:
    """
    Creates a hmac from the given message with the given key.

    :param key: the hmac key
    :param message:  the hmac message
    :return: str
    """
    import hmac
    _hmac = hmac.new(key=key.encode(), digestmod="sha256")
    _hmac.update(bytes(message, encoding="utf-8"))
    return base64.b64encode(_hmac.digest()).decode()


def to_json(obj: dict) -> str:
    """
    Creates a json string of the given object.

    :param obj: the object to convert to json
    :return: str
    """
    return json.dumps(obj, separators=(",", ":"))


def from_json(path: str):
    """
    Converts the json file at the given path to a dict.

    :param path: the path to the json file
    :return: dict
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def http_get(url: str) -> bytes:
    """
    Invokes a http get request to the given url
    :param url: the url
    :return: bytes
    """
    return requests.get(url).content


def http_post(data: {}, config: ModelHubConfig) -> str:
    """
    Invokes a http post request.

    :param data: the request body
    :param config: the registry config
    :return: dict
    """
    message = to_json(data)

    headers = {"Content-Type": "application/json"}
    if config.api_key is not None and config.api_secret is not None:
        headers["Authorization"] = "HMAC " + config.api_key + ":" + hmac(config.api_secret, message)

    # return json.loads(requests.post(config.url, data=message, headers=headers).text)
    response = requests.post(config.url, data=message, headers=headers)
    if "errorType" in response.text:
        raise ValueError(response.text)
    return response.text[1:-1]


def http_put(url: str, path: str):
    """
    Invokes a http put request.

    :param url: the url
    :param path: the path to the file to upload
    """
    headers = {"Content-Type": "application/octet-stream"}
    print("uploading " + path)
    with open(path, "rb") as data:
        response = requests.put(url, data=data.read(), headers=headers)
        if response.status_code != 200:
            raise ValueError(response.text)


def zip_dir(path: Union[str, Path], pwd: Optional[str]) -> Path:
    paths = []
    path = Path(path) if isinstance(path, str) else path

    for root, directories, files in os.walk(path):
        paths.extend([os.path.join(root, file) for file in files])

    with zipfile.ZipFile(path.as_posix() + ".zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
        for file in paths:
            logging.info(f"add {file} to zip")
            z.write(Path(file), Path(file).name)
        if pwd is not None:
            z.setpassword(bytes(pwd, "utf-8"))

    return Path(path.as_posix() + ".zip")


def unzip(path: Path, pwd: Optional[str]):
    with zipfile.ZipFile(path.as_posix(), "r", compression=zipfile.ZIP_DEFLATED) as z:
        z.extractall(path=path.parent / path.name[:-4], pwd=pwd)


class ModelHubMixin:
    config: ModelConfig

    @classmethod
    def restore(cls, group: str, name: str, version: str, variant: str,
                config: ModelHubConfig = ModelHubConfig(), listeners: EngineListeners = None):
        listeners = listeners if listeners is not None else [OnnxListener()]

        if os.path.exists(config.cache + "/" + group + "/" + name + "/" + version + "/" + variant):
            logging.info("use cached model")
            # noinspection PyArgumentList
            return cls(config.cache + "/" + group + "/" + name + "/" + version + "/" + variant, listeners)

        url = http_post({
            "__type__": "model/get",
            "group": group,
            "name": name,
            "version": version,
            "variant": variant
        }, config)

        # FIXME
        index1 = str(url).find("amazonaws.com/") + len("amazonaws.com/")
        index2 = str(url).find("?")

        key = url[index1:index2]
        print("downloading " + key)

        path = Path(config.cache + "/" + key)
        os.makedirs(path.parent, exist_ok=True)

        with open(path, "wb") as file:
            file.write(http_get(url))

        unzip(path, config.zip_secret)

        # noinspection PyArgumentList
        return cls(config.cache + "/" + group + "/" + name + "/" + version + "/" + variant, listeners)

    def store(self, config: ModelHubConfig()):
        """
        Stores the given model in the FastForward registry.
        """
        info = from_json(self.config.config_path + "/info.json")

        url = http_post({
            "__type__": "model/create",
            "group": info["group"],
            "name": info["name"],
            "version": info["version"],
            "variant": f"{info['optimization']}-{info['quantization']}"
        }, config)

        zip_path = zip_dir(self.config.config_path, config.zip_secret)
        http_put(url, zip_path.as_posix())
