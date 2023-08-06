import numpy as np
from kolibri.data import find
import os, json
from logging import getLogger
import random
log = getLogger(__name__)
from kolibri.datasets.reader.base_reader import DatasetReader
from kolibri.logger import get_logger

logger = get_logger(__name__)
class ConllCorpusNER:
    """
    Chinese Daily New New Corpus
    https://github.com/zjy-ucas/ChineseNER/

    Example:
        >>> from kolibri.datasets.reader.conll import ConllCorpusNER
        >>> train_x, train_y = ConllCorpusNER.load_data('train')
        >>> test_x, test_y = ConllCorpusNER.load_data('test')
        >>> valid_x, valid_y = ConllCorpusNER.load_data('valid')

    """

    @classmethod
    def load_data(cls,
                  subset_name: str = 'train',
                  shuffle: bool = True):
        """
        Load dataset as sequence labeling format, char level tokenized

        Args:
            subset_name: {train, test, valid}
            shuffle: should shuffle or not, default True.

        Returns:
            dataset_features and dataset labels
        """
        corpus_path = find('datasets/conll_2003')

        if subset_name == 'train':
            file_path = os.path.join(corpus_path, 'train.txt')
        elif subset_name == 'test':
            file_path = os.path.join(corpus_path, 'test.txt')
        else:
            file_path = os.path.join(corpus_path, 'valid.txt')

        x_data, y_data = DatasetReader.read_conll_format_file(file_path, label_index=3)
        if shuffle:
            x_data, y_data = unison_shuffled_copies(x_data, y_data)
        logger.debug(f"loaded {len(x_data)} samples from {file_path}. Sample:\n"
                     f"x[0]: {x_data[0]}\n"
                     f"y[0]: {y_data[0]}")
        return x_data, y_data




def unison_shuffled_copies(a, b):
    """
    Union shuffle two arrays
    Args:
        a:
        b:

    Returns:

    """
    data_type = type(a)
    assert len(a) == len(b)
    c = list(zip(a, b))
    random.shuffle(c)
    a, b = zip(*c)
    if data_type == np.ndarray:
        return np.array(a), np.array(b)
    return list(a), list(b)


if __name__=='__main__':
    train_x, train_y = ConllCorpusNER.load_data('train')
    print(train_x)