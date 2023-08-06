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

from fastforward.config import ModelConfig
from fastforward.engine.abstract_engine import EngineListeners
from fastforward.generation.generator.bart_generator import BartGenerator
from fastforward.generation.generator.marian_generator import MarianGenerator
from fastforward.generation.generator.pegasus_generator import PegasusGenerator
from fastforward.generation.generator.t5_generator import T5Generator
from fastforward.tokenizer.abstract_tokenizer import AbstractTokenizer, NetworkInfo
from fastforward.tokenizer.adapter.fast_tokenizer_adapter import FastTokenizerAdapter
from fastforward.tokenizer.adapter.prefix_tokenizer_adapter import PrefixTokenizerAdapter
from fastforward.tokenizer.adapter.type_tokenizer_adapter import TypeTokenizerAdapter
from fastforward.tokenizer.marian_tokenizer import MarianTokenizer


def auto_generator(config: ModelConfig, listeners: EngineListeners):
    model_ref = config._name_or_path
    assert model_ref is not None

    architecture: str = config.architectures[0]
    if architecture == "BartForConditionalGeneration":
        return BartGenerator(config, listeners)
    if "opus-mt" in model_ref:
        return MarianGenerator(config, listeners)
    if architecture.startswith("T5"):
        return T5Generator(config, listeners)
    if architecture.startswith("MT5"):
        return T5Generator(config, listeners)
    if architecture.startswith("Pegasus"):
        return PegasusGenerator(config, listeners)

    raise ValueError("cannot create generator for " + model_ref)


def auto_tokenizer(config: ModelConfig, network_info: NetworkInfo):
    def wrap(tokenizer: AbstractTokenizer):
        tokenizer = PrefixTokenizerAdapter(tokenizer, config)
        tokenizer = TypeTokenizerAdapter(tokenizer, network_info)
        return tokenizer

    model_ref = config._name_or_path
    assert model_ref is not None

    if "opus-mt" in model_ref:  # MarianTokenizer is not implemented in tokenizers library
        return wrap(MarianTokenizer.from_config(config.config_path))

    return wrap(FastTokenizerAdapter(config, network_info))
