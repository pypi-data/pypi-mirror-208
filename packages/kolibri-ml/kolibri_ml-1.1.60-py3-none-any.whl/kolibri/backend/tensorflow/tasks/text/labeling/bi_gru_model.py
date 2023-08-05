# encoding: utf-8


from typing import Dict, Any

from tensorflow import keras

from kolibri.backend.tensorflow.layers import L
from kolibri.backend.tensorflow.tasks.text.labeling.base_model import BaseLabelingModel


class BiGRU_Model(BaseLabelingModel):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'layer_bgru': {
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
            L.Bidirectional(L.GRU(**config['layer_bgru']), name='layer_bgru'),
            L.Dropout(**config['layer_dropout'], name='layer_dropout'),
            L.TimeDistributed(L.Dense(output_dim, **config['layer_time_distributed']), name='layer_time_distributed'),
            L.Activation(**config['layer_activation'])
        ]

        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(embed_model.inputs, tensor)


if __name__ == "__main__":
    from kolibri.data.text.corpus import ChineseDailyNerCorpus
    from kolibri.backend.tensorflow.callbacks import EvalCallBack

    train_x, train_y = ChineseDailyNerCorpus.load_data('train')
    valid_x, valid_y = ChineseDailyNerCorpus.load_data('valid')
    test_x, test_y = ChineseDailyNerCorpus.load_data('test')

    model = BiGRU_Model(sequence_length=10)

    eval_callback = EvalCallBack(kash_model=model,
                                 x_data=valid_x,
                                 y_data=valid_y,
                                 truncating=True,
                                 step=1)

    model.fit(train_x[:300], train_y[:300], valid_x, valid_y, epochs=1,
              callbacks=[eval_callback])
    y = model.predict(train_x[:200])
    model.tf_model.summary()
    model.evaluate(test_x, test_y)
