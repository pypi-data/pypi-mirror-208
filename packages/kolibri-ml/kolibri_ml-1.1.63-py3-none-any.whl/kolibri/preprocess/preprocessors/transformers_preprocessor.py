
from logging import getLogger
from typing import List, Union, Tuple

import numpy as np
from kolibri.tokenizers.bert_tokenizer import BertTokenizer

from kdmt.path import expand_path

from kolibri.core.component import Component

log = getLogger(__name__)


def _pad(data: List[List[Union[int, float]]], value: Union[int, float] = 0):
    max_len = max(map(len, data))
    res = np.ones([len(data), max_len], dtype=type(value)) * value
    for i, item in enumerate(data):
        res[i][:len(item)] = item
    return res


class TransformersBertPreprocessor(Component):
    def __init__(self, vocab_file: str, do_lower_case: bool = False, max_seq_length: int = 512,
                 tokenize_chinese_chars: bool = True, **kwargs):
        super().__init__()
        vocab_file = expand_path(vocab_file)
        self.tokenizer = BertTokenizer(vocab_file=vocab_file, do_lower_case=do_lower_case,
                                       tokenize_chinese_chars=tokenize_chinese_chars)
        self.max_seq_length = max_seq_length

    def __call__(self, tokens_batch: Union[List[str], List[List[str]]]) ->\
            Tuple[List[List[str]], List[List[str]], np.ndarray, np.ndarray, np.ndarray]:

        if isinstance(tokens_batch[0], str):  # skip for already tokenized text
            tokens_batch = [self.tokenizer.basic_tokenizer.tokenize(sentence, self.tokenizer.all_special_tokens)
                            for sentence in tokens_batch]
        startofword_markers_batch = []
        subtokens_batch = []
        for tokens in tokens_batch:
            startofword_markers = [0]
            subtokens = ['[CLS]']
            for token in tokens:
                for i, subtoken in enumerate(self.tokenizer.wordpiece_tokenizer.tokenize(token)):
                    startofword_markers.append(int(i == 0))
                    subtokens.append(subtoken)
            startofword_markers.append(0)
            subtokens.append('[SEP]')
            if len(subtokens) > self.max_seq_length:
                raise RuntimeError(f"input sequence after bert tokenization"
                                   f" cannot exceed {self.max_seq_length} tokens.")

            startofword_markers_batch.append(startofword_markers)
            subtokens_batch.append(subtokens)

        encoded = self.tokenizer.batch_encode_plus([[subtokens, None] for subtokens in subtokens_batch],
                                                   add_special_tokens=False)

        return (tokens_batch, subtokens_batch,
                _pad(encoded['input_ids'], value=self.tokenizer.pad_token_id),
                _pad(startofword_markers_batch), _pad(encoded['attention_mask']))
