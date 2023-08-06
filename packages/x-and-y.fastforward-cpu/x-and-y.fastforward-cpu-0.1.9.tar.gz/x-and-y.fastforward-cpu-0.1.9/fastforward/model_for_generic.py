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
from fastforward.config import CallableDict
from fastforward.engine.abstract_engine import EngineListeners
from fastforward.engine.onnx_engine import OnnxEngine
from fastforward.model import FastForwardModel


class ModelForGeneric(FastForwardModel):

    def __init__(self, config_path: str, model_name: str = "model", listeners: EngineListeners = None):
        super().__init__(config_path)
        self.engine = OnnxEngine(config_path, model_name, listeners or [])

        self.incoming_vars = self.engine.get_model_input().names
        self.outgoing_vars = self.engine.get_model_output().names

    def __call__(self, **kwargs):
        def get_attr(name):
            assert kwargs[name] is not None, f"value {name} must not be null"
            # import numpy as np
            # if hasattr(kwargs[name], "dtype") and kwargs[name].dtype == np.float32:
            #     return kwargs[name].astype(np.float16)
            return kwargs[name]

        model_input = {x: get_attr(x) for x in self.incoming_vars}
        outputs = self.engine.execute(model_input)

        return CallableDict({k: v for k, v in zip(self.outgoing_vars, outputs)})
