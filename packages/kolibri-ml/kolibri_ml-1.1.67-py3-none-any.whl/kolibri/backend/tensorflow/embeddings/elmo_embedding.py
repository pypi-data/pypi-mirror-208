# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from logging import getLogger
from typing import Iterator, List, Union, Optional

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from overrides import overrides

from kdmt.sequences import pad, chunk_generator
from kdmt.path import expand_path
from kolibri.core.component import Component


log = getLogger(__name__)



class ELMoEmbedder(Component):


    def __init__(self, spec: str, elmo_output_names: Optional[List] = None, dim: Optional[int] = None,
                 pad_zero: bool = False, concat_last_axis: bool = True, max_token: Optional[int] = None,
                 mini_batch_size: int = 32, **kwargs) -> None:

        super().__init__()
        self.spec = spec if '://' in spec else str(expand_path(spec))

        self.elmo_output_dims = {'word_emb': 512,
                                 'lstm_outputs1': 1024,
                                 'lstm_outputs2': 1024,
                                 'elmo': 1024,
                                 'default': 1024}
        elmo_output_names = elmo_output_names or ['default']
        self.elmo_output_names = elmo_output_names
        elmo_output_names_set = set(self.elmo_output_names)
        if elmo_output_names_set - set(self.elmo_output_dims.keys()):
            log.error(f'Incorrect elmo_output_names = {elmo_output_names} . You can use either  ["default"] or some of'
                      '["word_emb", "lstm_outputs1", "lstm_outputs2","elmo"]')
            sys.exit(1)

        if elmo_output_names_set - {'default'} and elmo_output_names_set - {"word_emb", "lstm_outputs1",
                                                                            "lstm_outputs2", "elmo"}:
            log.error('Incompatible conditions: you can use either  ["default"] or list of '
                      '["word_emb", "lstm_outputs1", "lstm_outputs2","elmo"] ')
            sys.exit(1)

        self.pad_zero = pad_zero
        self.concat_last_axis = concat_last_axis
        self.max_token = max_token
        self.mini_batch_size = mini_batch_size
        self.elmo_outputs, self.sess, self.tokens_ph, self.tokens_length_ph = self._load()
        self.dim = self._get_dims(self.elmo_output_names, dim, concat_last_axis)

    def _get_dims(self, elmo_output_names, in_dim, concat_last_axis):
        dims = [self.elmo_output_dims[elmo_output_name] for elmo_output_name in elmo_output_names]
        if concat_last_axis:
            dims = in_dim if in_dim else sum(dims)
        else:
            if in_dim:
                log.warning(f"[ dim = {in_dim} is not used, because the elmo_output_names has more than one element.]")
        return dims

    def _load(self):
        """
        Load a ELMo TensorFlow Hub Module from a self.spec.

        Returns:
            ELMo pre-trained model wrapped in TenserFlow Hub Module.
        """
        elmo_module = hub.Module(self.spec, trainable=False)

        sess_config = tf.ConfigProto()
        sess_config.gpu_options.allow_growth = True
        sess = tf.Session(config=sess_config)

        tokens_ph = tf.placeholder(shape=(None, None), dtype=tf.string, name='tokens')
        tokens_length_ph = tf.placeholder(shape=(None,), dtype=tf.int32, name='tokens_length')

        elmo_outputs = elmo_module(inputs={"tokens": tokens_ph,
                                           "sequence_len": tokens_length_ph},
                                   signature="tokens",
                                   as_dict=True)

        sess.run(tf.global_variables_initializer())

        return elmo_outputs, sess, tokens_ph, tokens_length_ph

    def _fill_batch(self, batch):
        """
        Fill batch correct values.

        Args:
            batch: A list of tokenized text samples.

        Returns:
            batch: A list of tokenized text samples.
        """

        if not batch:
            empty_vec = np.zeros(self.dim, dtype=np.float32)
            return [empty_vec] if 'default' in self.elmo_output_names else [[empty_vec]]

        filled_batch = []
        for batch_line in batch:
            batch_line = batch_line if batch_line else ['']
            filled_batch.append(batch_line)

        batch = filled_batch

        if self.max_token:
            batch = [batch_line[:self.max_token] for batch_line in batch]
        tokens_length = [len(batch_line) for batch_line in batch]
        tokens_length_max = max(tokens_length)
        batch = [batch_line + [''] * (tokens_length_max - len(batch_line)) for batch_line in batch]

        return batch, tokens_length

    def _mini_batch_fit(self, batch: List[List[str]], *args, **kwargs) -> Union[List[np.ndarray], np.ndarray]:
        """
        Embed sentences from a batch.

        Args:
            batch: A list of tokenized text samples.

        Returns:
            A batch of ELMo embeddings.
        """
        batch, tokens_length = self._fill_batch(batch)

        elmo_outputs = self.sess.run(self.elmo_outputs,
                                     feed_dict={self.tokens_ph: batch,
                                                self.tokens_length_ph: tokens_length})

        if 'default' in self.elmo_output_names:
            elmo_output_values = elmo_outputs['default']
            dim0, dim1 = elmo_output_values.shape
            if self.dim != dim1:
                shape = (dim0, self.dim if isinstance(self.dim, int) else self.dim[0])
                elmo_output_values = np.resize(elmo_output_values, shape)
        else:
            elmo_output_values = [elmo_outputs[elmo_output_name] for elmo_output_name in self.elmo_output_names]
            elmo_output_values = np.concatenate(elmo_output_values, axis=-1)

            dim0, dim1, dim2 = elmo_output_values.shape
            if self.concat_last_axis and self.dim != dim2:
                shape = (dim0, dim1, self.dim)
                elmo_output_values = np.resize(elmo_output_values, shape)

            elmo_output_values = [elmo_output_values_line[:length_line]
                                  for length_line, elmo_output_values_line in zip(tokens_length, elmo_output_values)]

            if not self.concat_last_axis:
                slice_indexes = np.cumsum(self.dim).tolist()[:-1]
                elmo_output_values = [[np.array_split(vec, slice_indexes) for vec in tokens]
                                      for tokens in elmo_output_values]

        return elmo_output_values

    @overrides
    def __call__(self, batch: List[List[str]],
                 *args, **kwargs) -> Union[List[np.ndarray], np.ndarray]:
        """
        Embed sentences from a batch.

        Args:
            batch: A list of tokenized text samples.

        Returns:
            A batch of ELMo embeddings.
        """
        if len(batch) > self.mini_batch_size:
            batch_gen = chunk_generator(batch, self.mini_batch_size)
            elmo_output_values = []
            for mini_batch in batch_gen:
                mini_batch_out = self._mini_batch_fit(mini_batch, *args, **kwargs)
                elmo_output_values.extend(mini_batch_out)
        else:
            elmo_output_values = self._mini_batch_fit(batch, *args, **kwargs)

        if self.pad_zero:
            elmo_output_values = pad(elmo_output_values)

        return elmo_output_values

    def __iter__(self) -> Iterator:
        """
        Iterate over all words from a ELMo model vocabulary.
        The ELMo model vocabulary consists of ``['<S>', '</S>', '<UNK>']``.

        Returns:
            An iterator of three elements ``['<S>', '</S>', '<UNK>']``.
        """

        yield from ['<S>', '</S>', '<UNK>']

    def destroy(self):
        if hasattr(self, 'sess'):
            for k in list(self.sess.graph.get_all_collection_keys()):
                self.sess.graph.clear_collection(k)
        super().destroy()
