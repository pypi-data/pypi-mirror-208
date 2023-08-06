# encoding: utf-8



from abc import ABC
from typing import Iterable, Iterator, TYPE_CHECKING
from typing import List, Any, Tuple

import numpy as np



class BaseGenerator(Iterable, ABC):
    def __init__(self, buffer_size: int = 2000) -> None:
        self.buffer_size = buffer_size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def sample(self) -> Iterator[Tuple[Any, Any]]:
        buffer, is_full = [], False
        for sample in self:
            buffer.append(sample)
            if is_full:
                i = np.random.randint(len(buffer))
                yield buffer.pop(i)
            elif len(buffer) == self.buffer_size:
                is_full = True
        while buffer:
            i = np.random.randint(len(buffer))
            yield buffer.pop(i)


class CorpusGenerator(BaseGenerator):

    def __init__(self,
                 x_data: List,
                 y_data: List,
                 *,
                 buffer_size: int = 2000) -> None:
        super(CorpusGenerator, self).__init__(buffer_size=buffer_size)
        self.x_data = x_data
        self.y_data = y_data
        self.buffer_size = buffer_size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:

        data_length=len(self.x_data) if self.x_data is not None else len(self.y_data)
        for i in range(data_length):
            y_value=None
            x_value=None
            if self.y_data is not None:
                y_value=self.y_data[i]
            if self.x_data is not None:
                x_value=self.x_data[i]
            yield x_value,y_value

    def __len__(self) -> int:
        return len(self.x_data)


class BatchDataSet(Iterable):
    def __init__(self,
                 corpus: CorpusGenerator,
                 *,
                 text_processor: 'BaseIndexer',
                 label_processor: 'BaseIndexer',
                 seq_length: int = None,
                 max_position: int = None,
                 segment: bool = False,
                 batch_size: int = 64) -> None:
        self.corpus = corpus
        self.text_processor = text_processor
        self.label_processor = label_processor

        self.seq_length = seq_length
        self.max_position = max_position
        self.segment = segment

        self.batch_size = batch_size

    def __len__(self) -> int:
        return max(len(self.corpus) // self.batch_size, 1)

    def __iter__(self) -> Iterator:
        batch_x, batch_y = [], []
        for x, y in self.corpus.sample():
            batch_x.append(x)
            batch_y.append(y)
            if len(batch_x) == self.batch_size:
                x_tensor = self.text_processor.transform(batch_x,
                                                         seq_length=self.seq_length,
                                                         max_position=self.max_position,
                                                         segment=self.segment)
                y_tensor = self.label_processor.transform(batch_y,
                                                          seq_length=self.seq_length,
                                                          max_position=self.max_position)
                yield x_tensor, y_tensor
                batch_x, batch_y = [], []
        if batch_x:
            x_tensor = self.text_processor.transform(batch_x,
                                                     seq_length=self.seq_length,
                                                     max_position=self.max_position,
                                                     segment=self.segment)
            y_tensor = self.label_processor.transform(batch_y,
                                                      seq_length=self.seq_length,
                                                      max_position=self.max_position)
            yield x_tensor, y_tensor

    def take(self, batch_count: int = None) -> Any:
        """
        take batches from the dataset

        Args:
            batch_count: number of batch count, iterate forever when batch_count is None.
        """
        i = 0
        should_continue = True
        while should_continue:
            for batch_x, batch_y in self.__iter__():
                if batch_count is None or i < batch_count:
                    i += 1
                    yield batch_x, batch_y
                if batch_count and i >= batch_count:
                    should_continue = False
                    break

        # x_shape = self.text_processor.get_tensor_shape(self.batch_size, self.seq_length)
        # y_shape = self.label_indexer.get_tensor_shape(self.batch_size, self.seq_length)
        # dataset = tf.data.Dataset.from_generator(self.__iter__,
        #                                          output_types=(tf.int64, tf.int64),
        #                                          output_shapes=(x_shape, y_shape))
        # dataset = dataset.repeat()
        # dataset = dataset.prefetch(50)
        # if batch_count is None:
        #     batch_count = len(self)
        # return dataset.take(batch_count)

