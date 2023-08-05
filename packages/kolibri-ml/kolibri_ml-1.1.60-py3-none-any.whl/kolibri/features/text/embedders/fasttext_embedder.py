

from logging import getLogger
from typing import Iterator


try:
    import fasttext
    fast_text_loaded = True
except:
    fast_text_not_loaded=True

import numpy as np
from overrides import overrides

from kolibri.features.text.embedders.abstract_embedder import Embedder

log = getLogger(__name__)

class FasttextEmbedder(Embedder):
    """
    Class implements fastText embedding model

    Args:
        load_path: path where to load pre-trained embedding model from
        pad_zero: whether to pad samples or not

    Attributes:
        model: fastText model instance
        tok2emb: dictionary with already embedded tokens
        dim: dimension of embeddings
        pad_zero: whether to pad sequence of tokens with zeros or not
        load_path: path with pre-trained fastText binary model
    """

    def _get_word_vector(self, w: str) -> np.ndarray:
        return self.model.get_word_vector(w)

    def load(self) -> None:
        """
        Load fastText binary model from self.load_path
        """
        log.info(f"[loading fastText embeddings from `{self.load_path}`]")
        if fast_text_loaded:
            self.model = fasttext.load_model(str(self.load_path))
        else:
            raise Exception("fasttext library nont installed. Please install it 'pip install fasttext'")
        self.dim = self.model.get_dimension()

    @overrides
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all words from fastText model vocabulary

        Returns:
            iterator
        """
        yield from self.model.get_words()
