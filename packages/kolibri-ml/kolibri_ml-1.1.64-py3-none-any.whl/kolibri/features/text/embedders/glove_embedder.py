
import pickle
from logging import getLogger
from typing import Iterator

import numpy as np
gensim_imported=False
try:
    from gensim.models import KeyedVectors
    gensim_imported=True
except:
    pass
from overrides import overrides

from kolibri.features.text.embedders.abstract_embedder import Embedder

log = getLogger(__name__)


#Todo: soleve duplicate declaration of this class in tensorflow backend
class GloVeEmbedder(Embedder):
    """
    Class implements GloVe embedding model

    Args:
        load_path: path where to load pre-trained embedding model from
        pad_zero: whether to pad samples or not

    Attributes:
        model: GloVe model instance
        tok2emb: dictionary with already embedded tokens
        dim: dimension of embeddings
        pad_zero: whether to pad sequence of tokens with zeros or not
        load_path: path with pre-trained GloVe model
    """

    def _get_word_vector(self, w: str) -> np.ndarray:
        return self.model[w]

    def load(self):
        """
        Load dict of embeddings from given file
        """
        log.info(f"[loading GloVe embeddings from `{self.load_path}`]")
        if not self.load_path.exists():
            log.warning(f'{self.load_path} does not exist, cannot load embeddings from it!')
            return
        if not gensim_imported:
            raise Exception("Could not imoort gensim, did you install it?. Run the following command: 'pip install gensim' or 'conda install gensim'")
        self.model = KeyedVectors.load_word2vec_format(str(self.load_path))
        self.dim = self.model.vector_size

    @overrides
    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all words from GloVe model vocabulary

        Returns:
            iterator
        """
        yield from self.model.vocab

    def persist(self, model_dir=None):
        return pickle.dumps(self.model, protocol=4)

    def deserialize(self, data: bytes) -> None:
        self.model = pickle.loads(data)
        self.dim = self.model.vector_size
