
from logging import getLogger
from typing import List, Union, Optional, Tuple

import numpy as np
from overrides import overrides
from pathlib import Path
from kdmt.dict import update
from kolibri.features.text.tf_idf_featurizer import TFIDFFeaturizer
from kolibri.logger import get_logger


from kolibri.features.text.embedders import get_embedder

def expand_path(path: Union[str, Path]) -> Path:
    """Convert relative paths to absolute with resolving user directory."""
    return Path(path).expanduser().resolve()

from kdmt.sequences import pad


logger = getLogger(__name__)


class TfidfWeightedEmbedder(TFIDFFeaturizer):
    """
    The class implements the functionality of embedding the sentence \
        as a weighted average by special coefficients of tokens embeddings. \
        Coefficients can be taken from the given TFIDF-vectorizer in ``vectorizer`` or \
        calculated as TFIDF from counter vocabulary given in ``counter_vocab_path``.
        Also one can give ``tags_vocab_path`` to the vocabulary with weights of tags. \
        In this case, batch with tags should be given as a second input in ``__call__`` method.

    Args:
        embedder: embedder instance
        tokenizer: tokenizer instance, should be able to detokenize sentence
        pad_zero: whether to pad samples or not
        mean: whether to return mean token embedding
        tags_vocab_path: optional path to vocabulary with tags weights
        vectorizer: vectorizer instance should be trained with ``analyzer="word"``
        counter_vocab_path: path to counter vocabulary
        idf_base_count: minimal idf value (less time occured are not counted)
        log_base: logarithm base for TFIDF-coefficient calculation froom counter vocabulary
        min_idf_weight: minimal idf weight

    Attributes:
        embedder: embedder instance
        tokenizer: tokenizer instance, should be able to detokenize sentence
        dim: dimension of embeddings
        pad_zero: whether to pad samples or not
        mean: whether to return mean token embedding
        tags_vocab: vocabulary with weigths for tags
        vectorizer: vectorizer instance
        counter_vocab_path: path to counter vocabulary
        counter_vocab: counter vocabulary
        idf_base_count: minimal idf value (less time occured are not counted)
        log_base: logarithm base for TFIDF-coefficient calculation froom counter vocabulary
        min_idf_weight: minimal idf weight

    Examples:
        >>> from kolibri.features.text.embedders.tfidf_weighted_embedder import TfidfWeightedEmbedder
        >>> from kolibri.features.text.embedders.fasttext_embedder import FasttextEmbedder
        >>> fasttext_embedder = FasttextEmbedder('/data/embeddings/wiki.ru.bin')
        >>> fastTextTfidf = TfidfWeightedEmbedder(embedder=fasttext_embedder,
                counter_vocab_path='/data/vocabs/counts_wiki_lenta.txt')
        >>> fastTextTfidf([['большой', 'и', 'розовый', 'бегемот']])
        [array([ 1.99135890e-01, -7.14746421e-02,  8.01428872e-02, -5.32840924e-02,
                 5.05212297e-02,  2.76053832e-01, -2.53270134e-01, -9.34443950e-02,
                 ...
                 1.18385439e-02,  1.05643446e-01, -1.21904516e-03,  7.70555378e-02])]
    """


    provides = ["text_features"]

    requires = ["tokens"]

    defaults = {
            "fixed": {

                # regular expression for tokens
                "embedder": 'glove',

                # remove accents during the preprocessing step
                "pad-zero": False,  # {'ascii', 'unicode', None}
                "embedder-dim": 100,
                "mean": False
            },

            "tunable": {

            }
        }


    def __init__(self, hyperparameters={}, **kwargs) -> None:

        super().__init__(hyperparameters)

        self.embedder = get_embedder(self.get_parameter("embedder", "glove"), hyperparameters)
        self.dim = self.get_parameter("embedder-dim")
        self.mean = self.get_parameter("mean")
        self.pad_zero =self.get_parameter("pad-zero")


    @staticmethod
    def space_detokenizer(batch: List[List[str]]) -> List[str]:
        """
        Detokenizer by default. Linking tokens by space symbol

        Args:
            batch: batch of tokenized texts

        Returns:
            batch of detokenized texts
        """
        return [" ".join(tokens) for tokens in batch]

    @overrides
    def fit(self, X, y) -> List[Union[list, np.ndarray]]:
        """
        Infer on the given data

        Args:
            batch: tokenized text samples
            tags_batch: optional batch of corresponding tags
            mean: whether to return mean token embedding (does not depend on self.mean)
            *args: additional arguments
            **kwargs: additional arguments

        Returns:

        """
        return super().fit(X, y)

    @property
    def vocabulary(self):
        if not hasattr(self, "vocab"):
            self.vocab = np.array(self.vectorizer.get_feature_names())

        return self.vocab

    def transform(self, X):
        batch = [self._encode(sample, mean=self.get_parameter("mean")) for sample in X]

        if self.pad_zero:
            batch = pad(batch)

        return batch

    def _encode2(self, tokens: List[str], mean: bool) -> Union[List[np.ndarray], np.ndarray]:
        """
        Embed one text sample

        Args:
            tokens: tokenized text sample
            mean: whether to return mean token embedding (does not depend on self.mean)

        Returns:
            list of embedded tokens or array of mean values
        """
        if self.vectorizer:
            detokenized_sample = self.tokenizer([tokens])[0]  # str
            vectorized_sample = self.vectorizer([detokenized_sample])  # (voc_size,)

            weights = np.array([vectorized_sample[0, np.where(self.vocabulary == token)[0][0]]
                                if len(np.where(self.vocabulary == token)[0]) else 0.
                                for token in tokens])
        else:
            weights = np.array([self.get_weight(max(self.counter_vocab.get(token, 0), self.idf_base_count))
                                for token in tokens])

        if sum(weights) == 0:
            weights = np.ones(len(tokens))

        embedded_tokens = np.array(self.embedder([tokens]))[0, :, :]

        if mean is None:
            mean = self.mean

        if mean:
            embedded_tokens = np.average(embedded_tokens, weights=weights, axis=0)
        else:
            embedded_tokens = np.array([weights[i] * embedded_tokens[i] for i in range(len(tokens))])

        return embedded_tokens
    def _encode(self, tokens: List[str], mean: bool) -> Union[List[np.ndarray], np.ndarray]:
        """
        Embed one text sample

        Args:
            tokens: tokenized text sample
            mean: whether to return mean token embedding (does not depend on self.mean)

        Returns:
            list of embedded tokens or array of mean values
        """
        vectorized_sample = self.vectorizer.transform([tokens]).toarray()  # (voc_size,)

        weights = np.array([vectorized_sample[0, np.where(self.vocabulary == token)[0][0]]
                                if len(np.where(self.vocabulary == token)[0]) else 0.
                                for token in tokens])


        if sum(weights) == 0:
            weights = np.ones(len(tokens))

        embedded_tokens = np.array(self.embedder([tokens], mean=False))[0, :, :]

        if mean is None:
            mean = self.mean

        if mean:
            embedded_tokens = np.average(embedded_tokens, weights=weights, axis=0)
        else:
            embedded_tokens = np.array([weights[i] * embedded_tokens[i] for i in range(len(tokens))])

        return embedded_tokens

    def get_weight(self, count: int) -> float:
        """
        Calculate the weight corresponding to the given count

        Args:
            count: the number of occurences of particular token

        Returns:
            weight
        """
        log_count = np.log(count) / np.log(self.log_base)
        log_base_count = np.log(self.idf_base_count) / np.log(self.log_base)
        weight = max(1.0 / (1.0 + log_count - log_base_count), self.min_idf_weight)
        return weight

