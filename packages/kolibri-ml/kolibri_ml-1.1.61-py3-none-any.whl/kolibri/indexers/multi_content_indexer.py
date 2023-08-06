from typing import Dict, Any

import numpy as np
from kolibri.indexers.base_indexer import BaseIndexer



class MultiContentIndexer(BaseIndexer):

    def to_dict(self) -> Dict[str, Any]:
        data = super(MultiContentIndexer, self).to_dict()
        data['config'].update({
            'min_count': self.min_count,
            'content_indexers': [indexer.to_dict() for indexer in self.content_indexers]
        })
        return data

    def __init__(self, min_count=0, **kwargs):
        super(MultiContentIndexer, self).__init__(**kwargs)
        self.content_indexers = []
        self.min_count = min_count

    def build_vocab(self, x_data, y_data):

        for indexer in self.content_indexers:
            indexer.build_vocab(x_data, y_data)

    def transform(self, samples, **kwargs):
        samples_tensors = []
        for indexer in self.content_indexers:
            sample_tensor = []
            for sample in samples:
                trandformed = indexer.transform([sample])
                sample_tensor.append(trandformed[0])
            samples_tensors.append(np.array(sample_tensor))
        return samples_tensors

    def inverse_transform(self, labels, *, lengths=None, **kwargs):
        raise NotImplementedError

