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

from fastforward.generation.generation_mixin import GenerationConfig
from fastforward.generation.generator.abstract_generator import AbstractGenerator
from fastforward.generation.strategy._logits_processor import get_logits_processor
from fastforward.generation.strategy._stopping_criteria import get_stopping_criteria
from fastforward.generation.strategy.abstract_strategy import SearchStrategy
from fastforward.generation.strategy.greedy.greedy_search import GreedySearch


class GreedyGenModeStrategy(SearchStrategy):

    def __init__(self, generation_step: AbstractGenerator):
        self.generation_step = generation_step

    def handle(self, config: GenerationConfig, **model_kwargs):
        # get distribution pre_processing samplers
        logits_processor = get_logits_processor(config)

        assert config.num_return_sequences is not None
        assert config.num_beams is not None
        if config.num_return_sequences > config.num_beams:
            raise ValueError("`num_return_sequences` has to be smaller or equal to `num_beams`.")

        if config.max_length is None:
            raise ValueError("`max_length` needs to be a stopping_criteria for now.")

        # interleave with `num_beams`
        input_ids, model_kwargs = self.expand_inputs_for_generation(
            config.input_ids, expand_size=config.num_beams, is_encoder_decoder=config.is_encoder_decoder, **model_kwargs
        )
        return GreedySearch(self.generation_step, config).greedy_search(
            input_ids,
            logits_processor=logits_processor,
            stopping_criteria=get_stopping_criteria(config),
            pad_token_id=config.pad_token_id,
            eos_token_id=config.eos_token_id,
            output_scores=config.output_scores,
            return_dict_in_generate=config.return_dict_in_generate,
            synced_gpus=config.synced_gpus,
            **model_kwargs
        )