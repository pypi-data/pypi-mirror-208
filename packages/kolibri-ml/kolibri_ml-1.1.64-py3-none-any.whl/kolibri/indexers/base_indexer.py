# encoding: utf-8

from abc import ABC
from typing import Dict, List, Optional, Any, Tuple
from kolibri.types import TextSamplesVar

import numpy as np
try:
    from kolibri.data.text.generators import CorpusGenerator
except:
    pass

class BaseIndexer(ABC):
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': {
                'token_pad': self.token_pad,
                'token_unk': self.token_unk,
                'token_bos': self.token_bos,
                'token_eos': self.token_eos,
                'token2idx': self.token2idx,
                'segment': self.segment
            },
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
        }

    def __init__(self, **kwargs: Any) -> None:
        self.token2idx = kwargs.get('token2idx', {})
        self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])

        self.segment = False

        self.token_pad: str = kwargs.get('token_pad', '[PAD]')  # type: ignore
        self.token_unk: str = kwargs.get('token_unk', '[UNK]')  # type: ignore
        self.token_bos: str = kwargs.get('token_bos', '[CLS]')  # type: ignore
        self.token_eos: str = kwargs.get('token_eos', '[SEP]')  # type: ignore

        self._sequence_length_from_saved_model: Optional[int] = None

    @property
    def vocab_size(self) -> int:
        return len(self.token2idx)

    @property
    def is_vocab_build(self) -> bool:
        return self.vocab_size != 0

    def build_vocab(self,
                    x_data: TextSamplesVar,
                    y_data: TextSamplesVar) -> None:
        corpus_gen = CorpusGenerator(x_data, y_data)
        self.build_vocab_generator([corpus_gen])

    def build_vocab_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        raise NotImplementedError

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        if self.segment:
            return 2, batch_size, seq_length
        else:
            return batch_size, seq_length

    def transform(self,
                  samples: TextSamplesVar,
                  *,
                  seq_length: int = None,
                  max_position: int = None,
                  segment: bool = False) -> np.ndarray:
        raise NotImplementedError

    def inverse_transform(self,
                          labels: List[int],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> List[str]:
        raise NotImplementedError


if __name__ == "__main__":
    pass
