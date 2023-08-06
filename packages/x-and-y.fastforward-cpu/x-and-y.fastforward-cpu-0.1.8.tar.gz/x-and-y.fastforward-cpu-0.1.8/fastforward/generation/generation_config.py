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
from typing import Optional, List, Callable, Iterable, Any

import numpy as np

from fastforward.config import CallableDict


@dataclass
class GenerationConfig:
    """
            Parameters:

            input_ids (:obj:`torch.LongTensor` of shape :obj:`(batch_size, sequence_length)`, `optional`):
                The sequence used as a prompt for the generation. If :obj:`None` the method initializes it with
                :obj:`bos_token_id` and a batch size of 1.
            max_length (:obj:`int`, `optional`, defaults to :obj:`model.config.max_length`):
                The maximum length of the sequence to be generated.
            max_new_tokens (:obj:`int`, `optional`, defaults to None):
                The maximum numbers of tokens to generate, ignore the current number of tokens. Use either
                :obj:`max_new_tokens` or :obj:`max_length` but not both, they serve the same purpose.
            min_length (:obj:`int`, `optional`, defaults to 10):
                The minimum length of the sequence to be generated.
            do_sample (:obj:`bool`, `optional`, defaults to :obj:`False`):
                Whether or not to use sampling ; use greedy decoding otherwise.
            early_stopping (:obj:`bool`, `optional`, defaults to :obj:`False`):
                Whether to stop the beam search when at least ``num_beams`` sentences are finished per batch or not.
            num_beams (:obj:`int`, `optional`, defaults to 1):
                Number of beams for beam search. 1 means no beam search.
            temperature (:obj:`float`, `optional`, defaults to 1.0):
                The value used to module the next token probabilities.
            top_k (:obj:`int`, `optional`, defaults to 50):
                The number of highest probability vocabulary tokens to keep for top-k-filtering.
            top_p (:obj:`float`, `optional`, defaults to 1.0):
                If set to float < 1, only the most probable tokens with probabilities that add up to :obj:`top_p` or
                higher are kept for generation.
            repetition_penalty (:obj:`float`, `optional`, defaults to 1.0):
                The parameter for repetition penalty. 1.0 means no penalty. See `this paper
                <https://arxiv.org/pdf/1909.05858.pdf>`__ for more details.
            pad_token_id (:obj:`int`, `optional`):
                The id of the `padding` token.
            bos_token_id (:obj:`int`, `optional`):
                The id of the `beginning-of-sequence` token.
            eos_token_id (:obj:`int`, `optional`):
                The id of the `end-of-sequence` token.
            length_penalty (:obj:`float`, `optional`, defaults to 1.0):
                Exponential penalty to the length. 1.0 means no penalty. Set to values < 1.0 in order to encourage the
                model to generate shorter sequences, to a value > 1.0 in order to encourage the model to produce longer
                sequences.
            no_repeat_ngram_size (:obj:`int`, `optional`, defaults to 0):
                If set to int > 0, all ngrams of that size can only occur once.
            encoder_no_repeat_ngram_size (:obj:`int`, `optional`, defaults to 0):
                If set to int > 0, all ngrams of that size that occur in the ``encoder_input_ids`` cannot occur in the
                ``decoder_input_ids``.
            bad_words_ids(:obj:`List[List[int]]`, `optional`):
                List of token ids that are not allowed to be generated. In order to get the tokens of the words that
                should not appear in the generated text, use :obj:`tokenizer(bad_word,
                add_prefix_space=True).input_ids`.
            num_return_sequences(:obj:`int`, `optional`, defaults to 1):
                The number of independently computed returned sequences for each element in the batch.
            max_time(:obj:`float`, `optional`, defaults to None):
                The maximum amount of time you allow the computation to run for in seconds. generation will still
                finish the current pass after allocated time has been passed.
            attention_mask (:obj:`torch.LongTensor` of shape :obj:`(batch_size, sequence_length)`, `optional`):
                Mask to avoid performing attention on padding token indices. Mask values are in ``[0, 1]``, 1 for
                tokens that are not masked, and 0 for masked tokens. If not provided, will default to a tensor the same
                shape as :obj:`input_ids` that masks the pad token. `What are attention masks?
                <../glossary.html#attention-mask>`__
            decoder_start_token_id (:obj:`int`, `optional`):
                If an encoder-decoder model starts decoding with a different token than `bos`, the id of that token.
            use_cache: (:obj:`bool`, `optional`, defaults to :obj:`True`):
                Whether or not the model should use the past last key/values attentions (if applicable to the model) to
                speed up decoding.
            num_beam_groups (:obj:`int`, `optional`, defaults to 1):
                Number of groups to divide :obj:`num_beams` into in order to ensure diversity among different groups of
                beams. `this paper <https://arxiv.org/pdf/1610.02424.pdf>`__ for more details.
            diversity_penalty (:obj:`float`, `optional`, defaults to 0.0):
                This value is subtracted from a beam's score if it generates a token same as any beam from other group
                at a particular time. Note that :obj:`diversity_penalty` is only effective if ``group beam search`` is
                enabled.
            prefix_allowed_tokens_fn: (:obj:`Callable[[int, torch.Tensor], List[int]]`, `optional`):
                If provided, this function constraints the beam search to allowed tokens only at each step. If not
                provided no constraint is applied. This function takes 2 arguments: the batch ID :obj:`batch_id` and
                :obj:`input_ids`. It has to return a list with the allowed tokens for the next generation step
                conditioned on the batch ID :obj:`batch_id` and the previously generated tokens :obj:`inputs_ids`. This
                argument is useful for constrained generation conditioned on the prefix, as described in
                `Autoregressive Entity Retrieval <https://arxiv.org/abs/2010.00904>`__.
            forced_bos_token_id (:obj:`int`, `optional`):
                The id of the token to force as the first generated token after the :obj:`decoder_start_token_id`.
                Useful for multilingual models like :doc:`mBART <../model_doc/mbart>` where the first generated token
                needs to be the target language token.
            forced_eos_token_id (:obj:`int`, `optional`):
                The id of the token to force as the last generated token when :obj:`max_length` is reached.
            remove_invalid_values (:obj:`bool`, `optional`):
                Whether to remove possible `nan` and `inf` outputs of the model to prevent the generation method to
                crash. Note that using ``remove_invalid_values`` can slow down generation.
    """

    model_config: Any
    input_ids: Optional[np.array] = None
    attention_mask: Optional[np.array] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    do_sample: Optional[bool] = None
    early_stopping: Optional[bool] = None
    num_beams: Optional[int] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    repetition_penalty: Optional[float] = None
    bad_words_ids: Optional[Iterable[int]] = None
    bos_token_id: Optional[int] = None
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    length_penalty: Optional[float] = None
    no_repeat_ngram_size: Optional[int] = None
    encoder_no_repeat_ngram_size: Optional[int] = None
    num_return_sequences: Optional[int] = None
    max_time: Optional[float] = None
    max_new_tokens: Optional[int] = None
    decoder_start_token_id: Optional[int] = None
    use_cache: Optional[bool] = None
    num_beam_groups: Optional[int] = None
    diversity_penalty: Optional[float] = None
    prefix_allowed_tokens_fn: Optional[Callable[[int, np.array], List[int]]] = None
    forced_bos_token_id: Optional[int] = None
    forced_eos_token_id: Optional[int] = None
    remove_invalid_values: Optional[bool] = None
    encoder_outputs: Optional[CallableDict] = None
    past_key_values: Optional[Any] = None
    decoder_input_ids: Optional[Any] = None
    head_mask: Optional[Any] = None
    decoder_head_mask: Optional[Any] = None
    cross_attn_head_mask: Optional[Any] = None
    return_dict: Optional[bool] = False

    def __post_init__(self):
        self.pad_token_id = self.pad_token_id if self.pad_token_id is not None else self.model_config.pad_token_id
        self.bos_token_id = self.bos_token_id if self.bos_token_id is not None else self.model_config.bos_token_id
        self.eos_token_id = self.eos_token_id if self.eos_token_id is not None else self.model_config.eos_token_id
        self.max_length = self.max_length if self.max_length is not None else self.model_config.max_length
        self.num_beams = self.num_beams if self.num_beams is not None else self.model_config.num_beams
        self.num_beam_groups = self.num_beam_groups if self.num_beam_groups is not None else self.model_config.num_beam_groups
        self.do_sample = self.do_sample if self.do_sample is not None else self.model_config.do_sample
        self.repetition_penalty = self.repetition_penalty if self.repetition_penalty is not None else self.model_config.repetition_penalty
        self.no_repeat_ngram_size = self.no_repeat_ngram_size if self.no_repeat_ngram_size is not None else self.model_config.no_repeat_ngram_size
        self.encoder_no_repeat_ngram_size = self.encoder_no_repeat_ngram_size if self.encoder_no_repeat_ngram_size is not None else self.model_config.encoder_no_repeat_ngram_size
        self.bad_words_ids = self.bad_words_ids if self.bad_words_ids is not None else self.model_config.bad_words_ids
        self.min_length = self.min_length if self.min_length is not None else self.model_config.min_length
        self.eos_token_id = self.eos_token_id if self.eos_token_id is not None else self.model_config.eos_token_id
        self.diversity_penalty = self.diversity_penalty if self.diversity_penalty is not None else self.model_config.diversity_penalty
        self.forced_bos_token_id = self.forced_bos_token_id if self.forced_bos_token_id is not None else self.model_config.forced_bos_token_id
        self.forced_eos_token_id = self.forced_eos_token_id if self.forced_eos_token_id is not None else self.model_config.forced_eos_token_id
        self.remove_invalid_values = self.remove_invalid_values if self.remove_invalid_values is not None else self.model_config.remove_invalid_values
        self.is_encoder_decoder = self.model_config.is_encoder_decoder
        self.length_penalty = self.length_penalty if self.length_penalty is not None else self.model_config.length_penalty
        self.early_stopping = self.early_stopping if self.early_stopping is not None else self.model_config.early_stopping
        self.num_return_sequences = self.num_return_sequences if self.num_return_sequences is not None else self.model_config.num_return_sequences
