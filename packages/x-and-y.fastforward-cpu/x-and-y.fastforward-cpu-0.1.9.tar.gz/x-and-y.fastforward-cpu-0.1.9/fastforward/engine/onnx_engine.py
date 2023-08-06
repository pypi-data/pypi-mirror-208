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

# noinspection PyUnresolvedReferences
from onnxruntime import SessionOptions, InferenceSession

from fastforward.config import ModelInfo
from fastforward.engine.abstract_engine import Engine, ModelIO, EngineListeners


# ort.set_default_logger_severity(0)


def get_provider(info: dict) -> str:
    if "optimization" in info and info["optimization"] == "cuda":
        return "CUDAExecutionProvider"
    return "CPUExecutionProvider"


class OnnxEngine(Engine):
    """
    ONNX Engine implementation.
    """

    def __init__(self, config_path: str, model_path: str, listeners: EngineListeners):
        info = ModelInfo(config_path)
        model_path = config_path + "/" + model_path + ".onnx"

        opt = SessionOptions()
        [listener.initialize(opt) for listener in (listeners or [])]
        # opt.enable_profiling = True

        self.session = InferenceSession(model_path, opt, providers=[get_provider(info)])
        self.use_io_binding = "CUDAExecutionProvider" in self.session.get_providers()

    def execute(self, inputs: dict):
        """
        Runs the ONNX model with the given inputs.
        :param inputs: the inputs to run the model with
        :return: dict
        """

        if self.use_io_binding:
            io_binding = self.session.io_binding()
            for k in inputs:
                io_binding.bind_cpu_input(k, inputs[k])
            for k in self.get_model_output().names:
                io_binding.bind_output(k)
            self.session.run_with_iobinding(io_binding)
            return io_binding.copy_outputs_to_cpu()

        return self.session.run(None, inputs)

    def get_model_input(self) -> ModelIO:
        """
        Returns the model input information.
        :return: ModelIO
        """

        names = [x.name for x in self.session.get_inputs()]
        types = {x.name: x.type for x in self.session.get_inputs()}
        shapes = {x.name: x.shape for x in self.session.get_inputs()}

        return ModelIO(names, types, shapes)

    def get_model_output(self) -> ModelIO:
        """
        Returns the model output information.
        :return: ModelIO
        """

        names = [x.name for x in self.session.get_outputs()]
        types = {x.name: x.type for x in self.session.get_outputs()}
        shapes = {x.name: x.shape for x in self.session.get_outputs()}

        return ModelIO(names, types, shapes)
