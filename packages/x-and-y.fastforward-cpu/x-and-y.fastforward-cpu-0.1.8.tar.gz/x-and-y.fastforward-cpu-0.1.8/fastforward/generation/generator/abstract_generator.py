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

import functools
import operator

import numpy as np

from fastforward.config import ModelConfig, CallableDict
from fastforward.engine.abstract_engine import EngineListeners
from fastforward.model_for_generic import ModelForGeneric
from fastforward.tokenizer.abstract_tokenizer import NetworkInfo
from fastforward.utils.numpy_utils import index_select


class GeneratorMixin:

    def fold_past_keys(self, outputs):
        output = list(outputs.values())
        list_pkv = tuple(output[1:])
        past_key_values = tuple(list_pkv[i: i + 4] for i in range(0, len(list_pkv), 4))

        return {
            "logits": output[0],
            "past_key_values": past_key_values
        }

    def unfold_past_keys(self, past_key_values):
        flat_past_key_values = functools.reduce(operator.iconcat, past_key_values, [])
        return {f"pkv_{i}": pkv for i, pkv in enumerate(flat_past_key_values)}

class AbstractGenerator(GeneratorMixin):

    def __init__(self, config: ModelConfig, listeners: EngineListeners):
        self.encoder = ModelForGeneric(config.config_path, "encoder", listeners)
        self.decoder = ModelForGeneric(config.config_path, "decoder", listeners)
        self.config = config

    def prepare_inputs_for_generation(self, input_ids, **model_kwargs):
        decoder_input_ids = input_ids
        # cut decoder_input_ids if past is used
        if model_kwargs.get("past") is not None:
            decoder_input_ids = input_ids[:, -1:]

        return {
            "input_ids": None,  # encoder_outputs is defined. input_ids not needed
            "encoder_outputs": model_kwargs["encoder_outputs"],
            "past_key_values": model_kwargs.get("past"),
            "decoder_input_ids": decoder_input_ids,
            "attention_mask": model_kwargs["attention_mask"]
        }

    def adjust_logits_during_generation(self, logits: np.array, **kwargs) -> np.array:
        return logits

    def reorder_cache(self, past, beam_idx):
        reordered_past = ()
        for layer_past in past:
            # cached cross_attention states don't have to be reordered -> they are always the same
            reordered_past += (
                tuple(index_select(past_state, beam_idx, 0) for past_state in layer_past[:2]) + layer_past[2:],
            )
        return reordered_past

    def __call__(
            self,
            attention_mask=None,
            decoder_input_ids=None,
            encoder_outputs=None,
            past_key_values=None,
            **kwargs
    ):
        assert encoder_outputs is not None, "encoder output must not be null"

        decoder_inputs = {
            "input_ids": decoder_input_ids,
            "encoder_attention_mask": attention_mask,
            "encoder_hidden_states": encoder_outputs[0],
            "is_first_run": np.array([True]) if past_key_values is None else np.array([False])
        }

        if past_key_values is not None:
            decoder_inputs = {**decoder_inputs, **self.unfold_past_keys(past_key_values)}
        else:
            num_heads = self.config.decoder_attention_heads or self.config.num_heads
            hidden_size = self.config.d_model
            embed_size_per_head = self.config.d_kv or int(hidden_size / num_heads)
            decoder_layers = self.config.decoder_layers or self.config.num_decoder_layers

            dummy_pkv1 = np.zeros((1, num_heads, 1, embed_size_per_head), dtype=np.float32)
            dummy_pkv2 = np.zeros((1, num_heads, 9, embed_size_per_head), dtype=np.float32)

            for i in range(decoder_layers):
                decoder_inputs[f"pkv_{i * 4 + 0}"] = dummy_pkv1
                decoder_inputs[f"pkv_{i * 4 + 1}"] = dummy_pkv1
                decoder_inputs[f"pkv_{i * 4 + 2}"] = dummy_pkv2
                decoder_inputs[f"pkv_{i * 4 + 3}"] = dummy_pkv2

        return CallableDict(self.fold_past_keys(self.decoder(**decoder_inputs)))

    def get_network_info(self) -> NetworkInfo:
        return NetworkInfo(self.encoder.engine.get_model_input(), self.decoder.engine.get_model_output())
