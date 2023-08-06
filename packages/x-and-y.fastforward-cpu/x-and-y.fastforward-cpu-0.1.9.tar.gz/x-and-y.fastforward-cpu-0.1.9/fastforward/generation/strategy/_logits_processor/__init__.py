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

from fastforward.generation.generation_config import GenerationConfig
from fastforward.generation.strategy._logits_processor.abstract_logits_processor import LogitsProcessorList
from fastforward.generation.strategy._logits_processor.encoder_no_repeat_ngram import \
    EncoderNoRepeatNGramLogitsProcessor
from fastforward.generation.strategy._logits_processor.forced_bos_token import ForcedBOSTokenLogitsProcessor
from fastforward.generation.strategy._logits_processor.forced_eos_token import ForcedEOSTokenLogitsProcessor
from fastforward.generation.strategy._logits_processor.hamming_diversity import HammingDiversityLogitsProcessor
from fastforward.generation.strategy._logits_processor.inf_nan_remove import InfNanRemoveLogitsProcessor
from fastforward.generation.strategy._logits_processor.min_length import MinLengthLogitsProcessor
from fastforward.generation.strategy._logits_processor.no_bad_words import NoBadWordsLogitsProcessor
from fastforward.generation.strategy._logits_processor.no_repeat_ngram import NoRepeatNGramLogitsProcessor
from fastforward.generation.strategy._logits_processor.prefix_constrained import PrefixConstrainedLogitsProcessor
from fastforward.generation.strategy._logits_processor.repetition_penalty import RepetitionPenaltyLogitsProcessor


def get_logits_processor(config: GenerationConfig) -> 'LogitsProcessorList':
    """
    This class returns a :obj:`~transformers.LogitsProcessorList` list object that contains all relevant
    :obj:`~transformers.LogitsProcessor` instances used to modify the scores of the language model head.
    """
    processors = LogitsProcessorList()
    encoder_input_ids = config.input_ids if config.is_encoder_decoder else None

    # the following idea is largely copied from this PR: https://github.com/huggingface/transformers/pull/5420/files
    # all samplers can be found in `generation_utils_samplers.py`
    if config.diversity_penalty is not None and config.diversity_penalty > 0.0:
        processors.append(
            HammingDiversityLogitsProcessor(
                diversity_penalty=config.diversity_penalty, num_beams=config.num_beams,
                num_beam_groups=config.num_beam_groups
            )
        )
    if config.repetition_penalty is not None and config.repetition_penalty != 1.0:
        processors.append(RepetitionPenaltyLogitsProcessor(penalty=config.repetition_penalty))
    if config.no_repeat_ngram_size is not None and config.no_repeat_ngram_size > 0:
        processors.append(NoRepeatNGramLogitsProcessor(config.no_repeat_ngram_size))
    if config.encoder_no_repeat_ngram_size is not None and config.encoder_no_repeat_ngram_size > 0:
        if config.is_encoder_decoder:
            processors.append(
                EncoderNoRepeatNGramLogitsProcessor(config.encoder_no_repeat_ngram_size, encoder_input_ids))
        else:
            raise ValueError(
                "It's impossible to use `encoder_no_repeat_ngram_size` with decoder-only architecture"
            )
    if config.bad_words_ids is not None:
        processors.append(NoBadWordsLogitsProcessor(config.bad_words_ids, config.eos_token_id))
    if config.min_length is not None and config.eos_token_id is not None and config.min_length > -1:
        processors.append(MinLengthLogitsProcessor(config.min_length, config.eos_token_id))
    if config.prefix_allowed_tokens_fn is not None:
        processors.append(PrefixConstrainedLogitsProcessor(config.prefix_allowed_tokens_fn,
                                                           config.num_beams // config.num_beam_groups))
    if config.forced_bos_token_id is not None:
        processors.append(ForcedBOSTokenLogitsProcessor(config.forced_bos_token_id))
    if config.forced_eos_token_id is not None:
        processors.append(ForcedEOSTokenLogitsProcessor(config.max_length, config.forced_eos_token_id))
    if config.remove_invalid_values is True:
        processors.append(InfNanRemoveLogitsProcessor())
    return processors