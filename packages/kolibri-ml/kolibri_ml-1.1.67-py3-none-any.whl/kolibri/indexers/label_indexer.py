# encoding: utf-8


import collections
import operator
from typing import List, Union, Dict, Any, Tuple

import numpy as np
import tqdm

from kolibri.data.text.generators import CorpusGenerator
from kolibri.indexers.base_indexer import BaseIndexer
from kolibri.types import TextSamplesVar


class LabelIndexer(BaseIndexer):

    def to_dict(self) -> Dict[str, Any]:
        data = super(LabelIndexer, self).to_dict()
        data['config']['multi_label'] = self.multi_label
        return data

    def __init__(self,
                 multi_label: bool = False,
                 **kwargs: Any) -> None:
        from kolibri.backend.tensorflow.utils import MultiLabelBinarizer
        super(LabelIndexer, self).__init__(**kwargs)
        self.multi_label = multi_label
        self.multi_label_binarizer = MultiLabelBinarizer(self.token2idx)

    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        from kolibri.backend.tensorflow.utils import MultiLabelBinarizer
        if self.token2idx:
            return

        token2idx: Dict[str, int] = {}
        token2count: Dict[str, int] = {}
        for generator in generators:
            if self.multi_label:
                for _, label in tqdm.tqdm(generator, desc="Preparing classification label vocab dict"):
                    for token in label:
                        count = token2count.get(token, 0)
                        token2count[token] = count + 1
            else:
                for _, label in tqdm.tqdm(generator, desc="Preparing classification label vocab dict"):
                    count = token2count.get(label, 0)
                    token2count[label] = count + 1

        sorted_token2count = sorted(token2count.items(),
                                    key=operator.itemgetter(1),
                                    reverse=True)
        token2count = collections.OrderedDict(sorted_token2count)

        for token, token_count in token2count.items():
            if token not in token2idx:
                token2idx[token] = len(token2idx)
        self.token2idx = token2idx
        self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])
        self.multi_label_binarizer = MultiLabelBinarizer(self.token2idx)

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        if self.multi_label:
            return batch_size, len(self.token2idx)
        else:
            return (batch_size,)

    def transform(self,
                  samples: TextSamplesVar,
                  *,
                  seq_length: int = None,
                  max_position: int = None,
                  segment: bool = False) -> np.ndarray:
        if self.multi_label:
            sample_tensor = self.multi_label_binarizer.transform(samples)
            return sample_tensor

        sample_tensor = [self.token2idx[i] for i in samples]
        return np.array(sample_tensor)

    def inverse_transform(self,  # type: ignore[override]
                          labels: Union[List[int], np.ndarray],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> Union[List[List[str]], List[str]]:
        if self.multi_label:
            return self.multi_label_binarizer.inverse_transform(labels,
                                                                threshold=threshold)
        else:
            return [self.idx2token[i] for i in labels]


if __name__ == "__main__":
    pass
