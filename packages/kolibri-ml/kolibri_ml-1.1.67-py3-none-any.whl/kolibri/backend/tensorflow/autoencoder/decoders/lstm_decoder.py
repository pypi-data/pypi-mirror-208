import tensorflow as tf

class Decoder(tf.keras.Model):

    def to_dict(self):
        return {
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'decoder_input_shape': self.decoder_input_shape,  # type: ignore
            'dropout': self.dropout,

        }

    def __init__(self, input_shape, encoder_states,layer1_size=64, layer2_size=200, dropout=0.3):
        super(Decoder, self).__init__()

        self.decoder_input_shape=input_shape
        self.dropout=dropout
        self.decoder_input = tf.keras.Input(shape=self.decoder_input_shape)
        # gaussian_decoder_input = GaussianNoise(0.01)(decoder_input)

        decoder_lstm1 = tf.keras.layers.LSTM(layer1_size, return_sequences=True, return_state=True, dropout=self.dropout)
        decoder_output1, _, _ = decoder_lstm1(self.decoder_input, initial_state=encoder_states, training=True)

        decoder_lstm2 = tf.keras.layers.LSTM(layer2_size, return_state=True, dropout=self.dropout)
        decoder_output2, _, _ = decoder_lstm2(decoder_output1, training=True)

        decoder_dense = tf.keras.layers.Dense(4)
        self.decoder_output = decoder_dense(decoder_output2)
