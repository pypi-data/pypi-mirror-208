#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Dict, Any

from tensorflow import keras
from kolibri.backend.tensorflow.layers import L, KConditionalRandomField
from kolibri.backend.tensorflow.tasks.text.labeling.base_model import BaseLabelingModel


class BiLSTM_CRF_Model(BaseLabelingModel):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'layer_blstm': {
                'units': 128,
                'return_sequences': True
            },
            'layer_dropout': {
                'rate': 0.4
            },
            'layer_time_distributed': {},
            'layer_activation': {
                'activation': 'softmax'
            }
        }

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model

        crf = KConditionalRandomField()

        layer_stack = [
            L.Bidirectional(L.LSTM(**config['layer_blstm']), name='layer_blstm'),
            L.Dropout(**config['layer_dropout'], name='layer_dropout'),
            L.Dense(output_dim, **config['layer_time_distributed']),
            crf
        ]

        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(embed_model.inputs, tensor)
        self.crf_layer = crf

    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:
        if loss is None:
            loss = self.crf_layer.loss
        if metrics is None:
            metrics = [self.crf_layer.accuracy]
        super(BiLSTM_CRF_Model, self).compile_model(loss=loss,
                                                    optimizer=optimizer,
                                                    metrics=metrics,
                                                    **kwargs)


if __name__ == "__main__":
    from kolibri.data.text.corpus import DataReader
    from kolibri.backend.tensorflow.embeddings import BertEmbedding

    x, y = DataReader.read_conll_format_file("/Users/mohamedmentis/.kolibri/datasets/conll_2003/train.txt", label_index=3)
    x_valid, y_valid = DataReader.read_conll_format_file('/Users/mohamedmentis/.kolibri/datasets/conll_2003/test.txt', label_index=3)
    bert_embed =  BertEmbedding('/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-ml/bert_ner-main/language_model/bert/uncased_L-12_H-768_A-12')

    model = BiLSTM_CRF_Model(bert_embed)
    model.fit(x, y, x_valid, y_valid, epochs=3)
    model.evaluate(*DataReader.read_conll_format_file('/Users/mohamedmentis/.kolibri/datasets/conll_2003/valid.txt', label_index=3))
    model.evaluate(*DataReader.read_conll_format_file('/Users/mohamedmentis/.kolibri/datasets/conll_2003/test.txt', label_index=3))
