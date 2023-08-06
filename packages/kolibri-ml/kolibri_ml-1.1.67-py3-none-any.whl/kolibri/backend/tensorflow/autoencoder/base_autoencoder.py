import json
import os, io
import pathlib
from typing import Any, Dict

import numpy as np
import tensorflow as tf
import tqdm

import kolibri
from kdmt.cloud.azure import upload_file, get_file_object
from kolibri.backend.tensorflow.autoencoder.decoders.lstm_decoder import Decoder
from kolibri.backend.tensorflow.autoencoder.encoders.lstm_encoder import Encoder
from tensorflow import keras
from kolibri.logger import get_logger

logger = get_logger(__name__)

EVALUATION_INTERVAL=150

class BaseAutoEncoder:
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tf_version': tf.__version__,  # type: ignore
            'kolibri_version': kolibri.__version__,
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config': {
                "configs":self.configs,
                'input_shape': self.input_shape,
                'output_shape': self.output_shape
            },

            'encoders': self.encoder.to_dict(),  # type: ignore
            'decoders': self.decoder.to_dict(),

        }

    def __init__(self, configs, input_shape, output_shape):
        super(BaseAutoEncoder, self).__init__()
        self.ae_model = None
        self.configs=configs
        self.model_name= configs["model-name"]
        if configs["output-folder"] is not None:
            self.model_chekpoint_path = os.path.join(configs["output-folder"], 'Checkpoints', self.model_name)
        else:
            import tempfile
            td=tempfile.TemporaryDirectory()
            self.model_chekpoint_path = os.path.join(td.name, 'Checkpoints', self.model_name)
        self.input_shape=input_shape
        self.output_shape=output_shape
        self.title = "AutoEncoder training History"
        self.encoder = Encoder(self.input_shape, dropout=configs["dropout"])
        self.decoder = Decoder(self.output_shape, self.encoder.encoder_states, dropout=configs["dropout"])
        self.loss=configs["ae-loss"]
        # encoders decoders model
        self.ae_model = tf.keras.Model([self.encoder.encoder_input, self.decoder.decoder_input], self.decoder.decoder_output)
        self.ae_model.compile(loss=self.loss, optimizer='adam')
        self.history=None
        self.title=""

    def summary(self):
        if self.ae_model is not None:
            return self.ae_model.summary()

    def fit(self, encoder_train, decoder_train, label_train, encoder_val=None, decoder_val=None, label_val=None,
                epochs=500, patience=10):
            if self.ae_model is None:
                return

            self.history = self.ae_model.fit(
                [encoder_train, decoder_train],
                label_train, epochs=epochs, steps_per_epoch=EVALUATION_INTERVAL, validation_data=([encoder_val,
                                                                                                   decoder_val],
                                                                                                  label_val), verbose=1,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=patience, verbose=1,
                                                     mode='min'),
                    tf.keras.callbacks.ModelCheckpoint(self.model_chekpoint_path, monitor='val_loss', save_best_only=True,
                                                       mode='min',
                                                       verbose=0)])


    def save(self, model_path: str) -> str:
        """
        Save model
        Args:
            model_path:
        """

        config_file=self.__class__.__name__+'.model-config.json'
        model_file=self.__class__.__name__+'.model-weights.h5'

        pathlib.Path(model_path).mkdir(exist_ok=True, parents=True)
        model_path_full = os.path.abspath(model_path)

        with open(os.path.join(model_path_full, config_file), 'w') as f:
            f.write(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
            f.close()

        self.ae_model.save(os.path.join(model_path_full, model_file))

        logger.info('model saved to {}'.format(os.path.abspath(model_path_full)))

        return model_path

    @classmethod
    def load_from_azure(cls, container_name=None):
        from kolibri.backend.tensorflow.utils import load_data_object
        connect_str=os.environ.get("STORAGE_CONTAINER_STRING")

        blob_model_file=cls.__name__+'.model-weights.h5'
        blob_config_file=cls.__name__+'.model-config.json'

        model_config_file=get_file_object(connect_str, container_name, blob_config_file)
        model_config_file.seek(0)
        model_config_file = io.TextIOWrapper(model_config_file, encoding='utf-8')



        model_config = json.loads(model_config_file.read())
        model = load_data_object(model_config)

        stream = get_file_object(connect_str, container_name, blob_model_file)
        import h5py
        with h5py.File(stream, 'r') as h5_file:
            clf = keras.models.load_model(h5_file)

        model.ae_model = clf
        model.encoder.built = True

        return model


    def save_to_azure(self, container_name):
        """
        Save model
        Args:
            model_path:
        """

        connect_str=os.environ.get("STORAGE_CONTAINER_STRING")

        import tempfile

        blob_config_file=self.__class__.__name__+'.model-config.json'
        blob_model_file=self.__class__.__name__+'.model-weights.h5'

        td=tempfile.TemporaryDirectory()
        model_path=td.name

        self.save(model_path)

        local_config_file = os.path.join(model_path, blob_config_file)
        local_model_file=os.path.join(model_path, blob_model_file)



        upload_file(connect_str, container_name, local_config_file, blob_config_file, overwrite=True)
        upload_file(connect_str, container_name, local_model_file, blob_model_file, overwrite=True)

        return container_name

    @classmethod
    def load_model(cls, model_path):
        from kolibri.backend.tensorflow.utils import load_data_object

        config_file=cls.__name__+'.model-config.json'
        model_file=cls.__name__+'.model-weights.h5'

        model_config_path = os.path.join(model_path, config_file)
        model_config = json.loads(open(model_config_path, 'r').read())
        model = load_data_object(model_config)

        model.ae_model= keras.models.load_model(os.path.join(model_path, model_file))
        model.encoder.built = True

        return model


    def predict(self, encoder_data, decoder_data):
        return self.ae_model.predict([encoder_data, decoder_data])



