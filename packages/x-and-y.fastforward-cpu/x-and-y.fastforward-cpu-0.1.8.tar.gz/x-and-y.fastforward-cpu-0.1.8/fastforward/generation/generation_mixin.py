#  Copyright 2022 The HuggingFace Inc. team (this file was largely adopted from the transformers library)
#  and the X-and-Y team
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

import logging
from typing import Any, Dict

import numpy as np

from fastforward.config import ModelConfig, CallableDict
from fastforward.engine.abstract_engine import EngineListeners
from fastforward.generation.generation_config import GenerationConfig
from fastforward.generation.generator import auto_generator, auto_tokenizer
from fastforward.generation.strategy.beam_gen_mode_strategy import BeamGenModeStrategy
from fastforward.generation.strategy.greedy_gen_mode_strategy import GreedyGenModeStrategy
from fastforward.tokenizer.abstract_tokenizer import EncodingConfig
from fastforward.tokenizer.tokenizer_config import PaddingStrategy
from fastforward.utils import as_list

logger = logging.getLogger(__name__)


class GenerationMixin:
    """
    A class containing all of the functions supporting generation, to be used as a mixin in
    :class:`~transformers.PreTrainedModel`.
    """

    def __init__(self, config_path: str, listeners: EngineListeners):
        self.config_path = config_path
        self.config = ModelConfig.from_path(config_path)
        self.generator = auto_generator(self.config, listeners)
        self.tokenizer = auto_tokenizer(self.config, self.generator.get_network_info())

    def _prepare_attention_mask_for_generation(self, config: GenerationConfig) -> np.array:
        input_ids = config.input_ids
        pad_token_id = config.pad_token_id
        eos_token_id = config.eos_token_id

        is_pad_token_in_inputs_ids = (pad_token_id is not None) and (pad_token_id in input_ids)
        is_pad_token_not_equal_to_eos_token_id = (eos_token_id is None) or (
                (eos_token_id is not None) and (pad_token_id != eos_token_id)
        )
        if is_pad_token_in_inputs_ids and is_pad_token_not_equal_to_eos_token_id:
            return input_ids.__ne__(pad_token_id).astype(np.int64)

        return np.ones(input_ids.shape).astype(np.int64)

    def _prepare_encoder_decoder_kwargs_for_generation(self, input_ids: np.array, model_kwargs) -> Dict[str, Any]:
        if "encoder_outputs" not in model_kwargs:
            # retrieve encoder hidden states
            encoder = self.generator.encoder
            encoder_kwargs = {
                argument: value
                for argument, value in model_kwargs.items()
                if not (argument.startswith("decoder_") or argument.startswith("cross_attn"))
            }
            encoder_kwargs["input_ids"] = input_ids
            model_kwargs["encoder_outputs"] = encoder(**encoder_kwargs)
        return model_kwargs

    def _prepare_decoder_input_ids_for_generation(self, config: GenerationConfig) -> np.array:
        input_ids = config.input_ids
        decoder_start_token_id = config.decoder_start_token_id
        bos_token_id = config.bos_token_id
        decoder_start_token_id = self._get_decoder_start_token_id(decoder_start_token_id, bos_token_id)
        return np.ones((input_ids.shape[0], 1), dtype=np.int64) * decoder_start_token_id

    def _get_decoder_start_token_id(self, decoder_start_token_id: int = None, bos_token_id: int = None) -> int:
        decoder_start_token_id = (
            decoder_start_token_id if decoder_start_token_id is not None else self.config.decoder_start_token_id
        )
        bos_token_id = bos_token_id if bos_token_id is not None else self.config.bos_token_id

        if decoder_start_token_id is not None:
            return decoder_start_token_id
        elif (
                hasattr(self.config, "decoder")
                and hasattr(self.config.decoder, "decoder_start_token_id")
                and self.config.decoder.decoder_start_token_id is not None
        ):
            return self.config.decoder.decoder_start_token_id
        elif bos_token_id is not None:
            return bos_token_id
        elif (
                hasattr(self.config, "decoder")
                and hasattr(self.config.decoder, "bos_token_id")
                and self.config.decoder.bos_token_id is not None
        ):
            return self.config.decoder.bos_token_id
        raise ValueError(
            "`decoder_start_token_id` or `bos_token_id` has to be defined for encoder-decoder generation."
        )

    def sequence_to_ids(self, sequence):
        return self.tokenizer.encode(as_list(sequence), EncodingConfig(padding_strategy=PaddingStrategy.MAX_LENGTH))

    def ids_to_sequence(self, output):
        return self.tokenizer.decode(output, skip_special_token=True)

    def generate(self, config: GenerationConfig, **model_kwargs) -> np.array:
        r"""
        Generates sequences for models with a language modeling head. The method currently supports greedy decoding,
        multinomial sampling, beam-search decoding, and beam-search multinomial sampling.

        Apart from :obj:`input_ids` and :obj:`attention_mask`, all the arguments below will default to the value of the
        attribute of the same name inside the :class:`~transformers.PretrainedConfig` of the model. The default values
        indicated are the default values of those config.

        Most of these parameters are explained in more detail in `this blog post
        <https://huggingface.co/blog/how-to-generate>`__.

        Parameters:

            model_kwargs:
                Additional model specific kwargs will be forwarded to the :obj:`forward` function of the model. If the
                model is an encoder-decoder model, encoder specific kwargs should not be prefixed and decoder specific
                kwargs should be prefixed with `decoder_`.
        """

        input_ids = config.input_ids
        assert input_ids is not None, "no input_ids found"

        if model_kwargs.get("attention_mask", None) is None:
            model_kwargs["attention_mask"] = self._prepare_attention_mask_for_generation(config)

        if config.is_encoder_decoder:
            # add encoder_outputs to model_kwargs
            model_kwargs = self._prepare_encoder_decoder_kwargs_for_generation(input_ids, model_kwargs)

            # set input_ids as decoder_input_ids
            if "decoder_input_ids" in model_kwargs:
                config.input_ids = model_kwargs.pop("decoder_input_ids")
            else:
                config.input_ids = self._prepare_decoder_input_ids_for_generation(config)

            if "encoder_outputs" not in model_kwargs or not isinstance(model_kwargs["encoder_outputs"], CallableDict):
                raise ValueError("Make sure that `model_kwargs` include `encoder_outputs` of type `ModelOutput`.")

        assert config.max_length is not None
        if input_ids.shape[-1] >= config.max_length:
            input_ids_string = "decoder_input_ids" if self.config.is_encoder_decoder else "input_ids"
            logger.warning(
                f"Input length of {input_ids_string} is {input_ids.shape[-1]}, but ``max_length`` is set to {config.max_length}."
                "This can lead to unexpected behavior. You should consider increasing ``config.max_length`` or ``max_length``."
            )

        assert config.num_beam_groups is not None
        assert config.num_beams is not None
        assert config.num_beam_groups <= config.num_beams, "`num_beam_groups` has to be smaller or equal to `num_beams`"

        # set model_kwargs
        model_kwargs["use_cache"] = config.use_cache

        if (config.num_beams == 1) and (config.num_beam_groups == 1) and config.do_sample is False:
            return GreedyGenModeStrategy(self.generator).handle(config, **model_kwargs)

        elif (config.num_beams == 1) and (config.num_beam_groups == 1) and config.do_sample is True:
            raise ValueError("sample_gen_mode not implemented")

        elif (config.num_beams > 1) and (config.num_beam_groups == 1) and config.do_sample is False:
            return BeamGenModeStrategy(self.generator).handle(config, **model_kwargs)

        elif (config.num_beams > 1) and (config.num_beam_groups == 1) and config.do_sample is True:
            raise ValueError("beam_sample_gen_mode not implemented")

        elif (config.num_beams > 1) and (config.num_beam_groups > 1):
            raise ValueError("group_beam_gen_mode not implemented")

        raise ValueError("not implemented")