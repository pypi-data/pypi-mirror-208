

from abc import ABCMeta, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import List, Union, Iterator

import numpy as np
from overrides import overrides
from kolibri.core.component import Component
from kdmt.sequences import pad

log = getLogger(__name__)


class Embedder(Component):
    """
    Class implements fastText embedding model

    Args:
        load_path: path where to load pre-trained embedding model from
        pad_zero: whether to pad samples or not

    Attributes:
        model: model instance
        tok2emb: dictionary with already embedded tokens
        dim: dimension of embeddings
        pad_zero: whether to pad sequence of tokens with zeros or not
        mean: whether to return one mean embedding vector per sample
        load_path: path with pre-trained fastText binary model
    """

    defaults = {
        "fixed":{
            "embedding-path":None,
            "pad-zero":False,
            "mean": False
        },
        "tunable":{

        }
    }
    def __init__(self, parameters={}, **kwargs):
        """
        Initialize embedder with given parameters
        :param parameters:
        """

        super().__init__(parameters)
        self.tok2emb = {}
        self.pad_zero = self.get_parameter("pad-zero")
        self.mean = self.get_parameter("mean")
        self.dim = None
        self.model = None
        if self.get_parameter("embedding-path", None)!=None:
            self.load_path=Path(self.get_parameter("embedding-path"))
        self.load()

    @overrides
    def persist(self, model_dir=None) -> None:
        """
        Class does not save loaded model again as it is not trained during usage
        """
        raise NotImplementedError

    @overrides
    def __call__(self, batch: List[List[str]], mean: bool = None) -> List[Union[list, np.ndarray]]:
        """
        Embed sentences from batch

        Args:
            batch: list of tokenized text samples
            mean: whether to return mean embedding of tokens per sample

        Returns:
            embedded batch
        """
        batch = [self._encode(sample, mean) for sample in batch]
        if self.pad_zero:
            batch = pad(batch)
        return batch

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all words from the model vocabulary

        Returns:
            iterator
        """

    @abstractmethod
    def _get_word_vector(self, w: str) -> np.ndarray:
        """
        Embed a word using ``self.model``

        Args:
            w: a word

        Returns:
            embedding vector
        """

    def _encode(self, tokens: List[str], mean: bool) -> Union[List[np.ndarray], np.ndarray]:
        """
        Embed one text sample

        Args:
            tokens: tokenized text sample
            mean: whether to return mean embedding of tokens per sample

        Returns:
            list of embedded tokens or array of mean values
        """
        embedded_tokens = []
        for t in tokens:
            try:
                emb = self.tok2emb[t]
            except KeyError:
                try:
                    emb = self._get_word_vector(t)
                except KeyError:
                    emb = np.zeros(self.dim, dtype=np.float32)
                self.tok2emb[t] = emb
            embedded_tokens.append(emb)

        if mean is None:
            mean = self.mean

        if mean:
            filtered = [et for et in embedded_tokens if np.any(et)]
            if filtered:
                return np.mean(filtered, axis=0)
            return np.zeros(self.dim, dtype=np.float32)

        return embedded_tokens
