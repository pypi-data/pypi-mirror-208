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

from dataclasses import dataclass

from onnxruntime.capi.onnxruntime_pybind11_state import SessionOptions, ExecutionMode

from fastforward.engine.abstract_engine import EngineListener
from fastforward.utils.environment import int_from_env, bool_from_env


@dataclass
class OnnxListener(EngineListener):
    execution_mode: ExecutionMode = ExecutionMode.ORT_SEQUENTIAL
    intra_op_num_threads: int = int_from_env("FAST_FORWARD_INTRA_OP_NUM_THREADS", 0)
    inter_op_num_threads: int = int_from_env("FAST_FORWARD_INTER_OP_NUM_THREADS", 0)
    enable_cpu_mem_arena: bool = bool_from_env("FAST_FORWARD_CPU_MEM_ARENA", True)
    enable_mem_pattern: bool = bool_from_env("FAST_FORWARD_ENABLE_MEM_PATTERN", True)
    enable_mem_reuse: bool = bool_from_env("FAST_FORWARD_ENABLE_MEM_REUSE", True)
    enable_profiling: bool = bool_from_env("FAST_FORWARD_ENABLE_PROFILING", False)
    use_deterministic_compute: bool = bool_from_env("FAST_FORWARD_USE_DETERMINISTIC_COMPUTE", False)

    def initialize(self, session_options: SessionOptions):
        session_options.execution_mode = self.execution_mode
        session_options.intra_op_num_threads = self.intra_op_num_threads
        session_options.inter_op_num_threads = self.inter_op_num_threads
        session_options.enable_cpu_mem_arena = self.enable_cpu_mem_arena
        session_options.enable_mem_pattern = self.enable_mem_pattern
        session_options.enable_mem_reuse = self.enable_mem_reuse
        session_options.enable_profiling = self.enable_profiling
        session_options.use_deterministic_compute = self.use_deterministic_compute
