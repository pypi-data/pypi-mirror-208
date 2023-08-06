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


def topk(a, k):
    all_values = np.zeros((a.shape[0], k), dtype=a.dtype)
    all_indices = np.zeros((a.shape[0], k), dtype=np.int64)

    for i, flat in enumerate(a):
        indices = np.argpartition(flat, -k)[-k:]
        argsort = np.argsort(-flat[indices])

        indices = indices[argsort]
        values = flat[indices]

        values = np.expand_dims(values, axis=0)
        indices = np.expand_dims(indices, axis=0)

        all_values[i] = values
        all_indices[i] = indices

    return all_values, all_indices

def softmax(x, axis: int = 1):
    max = np.max(x, axis=axis, keepdims=True)  # returns max of each row and keeps same dims
    e_x = np.exp(x - max)  # subtracts each row with its max value
    sum = np.sum(e_x, axis=axis, keepdims=True)  # returns sum of each row and keeps same dims
    f_x = e_x / sum
    return f_x


def sparse(indices, values, size):
    from scipy.sparse import coo_matrix
    row = indices[0]
    col = indices[1]
    return coo_matrix((values, (row, col)), shape=size)


def masked_fill(array: np.array, mask: np.array):
    len1 = array.shape[0]
    len2 = mask.shape[0]

    if len1 > len2:
        mask = mask.repeat(len1, axis=0)

    np.place(array, mask, -float("inf"))
    return array
    # return  np.ma.array(array, mask=mask, fill_value=-float("inf")).filled()


def expand_as(array: np.array, other: np.array):
    return np.full_like(other, array)


def index_select(array: np.array, indices: np.array, axis: int = 0):
    return np.take(array, indices, axis=axis)


def new(size):
    return np.zeros(size)

def ones(size, dtype: np.dtype):
    return np.ones(size, dtype=dtype)


def pad_matrix(array: np.ndarray, target_length: int, pad_value: int = 0):
    b = []
    for i in range(len(array)):
        if len(array[i]) != target_length:
            x = np.pad(array[i], (0, target_length - len(array[i])), 'constant', constant_values=pad_value)
        else:
            x = array[i]
        b.append(x)
    return np.array(b)
