# encoding: utf-8


from typing import Dict, Any

from tensorflow import keras

from kolibri.backend.tensorflow.layers import L
from kolibri.backend.tensorflow.tasks.text.labeling.base_model import BaseLabelingModel


class BiLSTM_Model(BaseLabelingModel):
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

        layer_stack = [
            L.Bidirectional(L.LSTM(**config['layer_blstm']), name='layer_blstm'),
            L.Dropout(**config['layer_dropout'], name='layer_dropout'),
            L.Dense(output_dim, **config['layer_time_distributed']),
            L.Activation(**config['layer_activation'])
        ]
        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(embed_model.inputs, tensor)


if __name__ == "__main__":
    from kolibri.data.text.corpus import DataReader

    x, y = DataReader.read_conll_format_file("/Users/mohamedmentis/Downloads/BERT-NER-TF2-master/data/train.txt", label_index=3)
    x_valid, y_valid = DataReader.read_conll_format_file('/Users/mohamedmentis/Downloads/BERT-NER-TF2-master/data/valid.txt', label_index=3)

    from kolibri.backend.tensorflow.tasks.text.labeling import BiLSTM_Model
    from kolibri.backend.tensorflow.embeddings import BertEmbedding

    bert_embed =  BertEmbedding('/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-ml/bert_ner-main/language_model/bert/uncased_L-12_H-768_A-12')

    model = BiLSTM_Model(bert_embed, sequence_length=100)


    model.fit(x, y, x_valid, y_valid, epochs=3)
    model.evaluate(*DataReader.read_conll_format_file('/Users/mohamedmentis/Downloads/BERT-NER-TF2-master/data/valid.txt', label_index=3), truncating=True)


