"""
Shared functions related to benchmarks.
"""

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

import time
from contextlib import contextmanager
from typing import List

import numpy as np


def print_timings(name: str, timings: List[float]) -> None:
    """
    Format and print latencies
    :param name: engine name
    :param timings: latencies measured during the inference
    """
    print(
        f"[{name}] "
        f"mean={1e3 * np.mean(timings):.2f}ms, "
        f"sd={1e3 * np.std(timings):.2f}ms, "
        f"min={1e3 * np.min(timings):.2f}ms, "
        f"max={1e3 * np.max(timings):.2f}ms, "
        f"median={1e3 * np.percentile(timings, 50):.2f}ms, "
        f"95p={1e3 * np.percentile(timings, 95):.2f}ms, "
        f"99p={1e3 * np.percentile(timings, 99):.2f}ms"
    )


@contextmanager
def track_infer_time(buffer: List[float]) -> None:
    """
    A context manager to perform latency measures
    :param buffer: a List where to save latencies for each input
    """
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    buffer.append(end - start)


@contextmanager
def stopwatch(name: str, in_seconds: bool = True) -> None:
    """
    A context manager to perform latency measures
    :param name: the name of the stopwatch
    :param in_seconds: indicates if the time measure unit is second else milliseconds
    """
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(name + ": " + str((end - start) * (1000 if in_seconds else 1)))


def benchmark(name: str, inference_function):
    buffer = []
    for _ in range(10):  # warmup
        inference_function()
    for _ in range(10):
        with track_infer_time(buffer):
            print(inference_function())

    print_timings(name, buffer)
