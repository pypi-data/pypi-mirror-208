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
from typing import Any

import numpy as np
from numpy import matmul
from numpy.linalg import norm


def cosine_similarity(a, b):
    a = np.expand_dims(a, axis=0) if len(a.shape) == 1 else a
    b = np.expand_dims(b, axis=0) if len(b.shape) == 1 else b
    a_norm = a / norm(a, ord=2, axis=1, keepdims=True)
    b_norm = b / norm(b, ord=2, axis=1, keepdims=True)

    return np.ravel(matmul(a_norm, b_norm.transpose()))


def argmax(array: np.array, k: int = 5):
    return array.argsort()[-k:][::-1].tolist()


def sigmoid(z: np.array):
    return 1 / (1 + np.exp(-z))


def load_json(path: str):
    with open(path) as f:
        return json.load(f)


def softmax(array: np.array):
    return np.exp(array) / np.sum(np.exp(array))


def coalesce(a: Any, b: Any) -> Any:
    return a if a is not None else b


def as_list(item):
    if isinstance(item, np.ndarray):
        return item.tolist()
    return [item] if not isinstance(item, list) else item
