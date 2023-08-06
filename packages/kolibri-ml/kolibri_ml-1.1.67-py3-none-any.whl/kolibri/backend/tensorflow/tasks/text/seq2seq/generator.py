from kolibri.data.text.generators import CorpusGenerator
from typing import Iterable, Iterator, Any
import tensorflow as tf

class Seq2SeqDataSet(Iterable):
    def __init__(self,
                 corpus: CorpusGenerator,
                 *,
                 batch_size: int = 64,
                 encoder_processor: 'BaseIndexer',
                 decoder_processor: 'BaseIndexer',
                 encoder_seq_length: int = None,
                 decoder_seq_length: int = None,
                 encoder_segment: bool = False,
                 decoder_segment: bool = False):
        self.corpus = corpus

        self.encoder_processor = encoder_processor
        self.decoder_processor = decoder_processor

        self.encoder_seq_length = encoder_seq_length
        self.decoder_seq_length = decoder_seq_length

        self.encoder_segment = encoder_segment
        self.decoder_segment = decoder_segment

        self.batch_size = batch_size

    def __len__(self) -> int:
        return max(len(self.corpus) // self.batch_size, 1)

    def __iter__(self) -> Iterator:
        batch_x, batch_y = [], []
        for x, y in self.corpus.sample():
            batch_x.append(x)
            batch_y.append(y)
            if len(batch_x) == self.batch_size:
                x_tensor = self.encoder_processor.transform(batch_x,
                                                            seq_length=self.encoder_seq_length,
                                                            segment=self.encoder_segment)
                y_tensor = self.decoder_processor.transform(batch_y,
                                                            seq_length=self.decoder_seq_length,
                                                            segment=self.encoder_segment)
                yield x_tensor, y_tensor
                batch_x, batch_y = [], []

    def take(self, batch_count: int = None) -> Any:
        x_shape = [self.batch_size, self.encoder_seq_length]
        y_shape = [self.batch_size, self.decoder_seq_length]
        dataset = tf.data.Dataset.from_generator(self.__iter__,
                                                 output_types=(tf.int64, tf.int64),
                                                 output_shapes=(x_shape, y_shape))
        dataset = dataset.repeat()
        dataset = dataset.prefetch(50)
        if batch_count is None:
            batch_count = len(self)
        return dataset.take(batch_count)
