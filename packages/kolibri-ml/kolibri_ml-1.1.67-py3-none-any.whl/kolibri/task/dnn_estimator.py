import os

import joblib
from io import BytesIO

import numpy as np
from scipy.sparse import vstack
from sklearn.utils import class_weight
import h5py
from kolibri.config import override_defaults
from kolibri.core.component import Component
from kolibri.logger import get_logger
from sklearn.model_selection import train_test_split
from kdmt.cloud.azure import upload_file, get_file_object
from kolibri.evaluators.classifier_evaluator import ClassifierEvaluator


logger = get_logger(__name__)
from kolibri.default_configs import DEFAULT_NN_MODEL_FILENAME
KOLIBRI_MODEL_FILE_NAME = "classifier-kolibri.pkl"
DNN_MODEL_FOLDER_NAME = "classifier-dnn"


class DnnEstimator(Component):
    """classifier using the sklearn framework"""

    _estimator_type = 'estimator'

    name = ''

    provides = []

    requires = []

    defaults = {

        # the models used in the classifier if several models are given they will be combined
        'fixed':{
            "embeddings": None,
            "multi-label": False,
            "sequence_length": 'auto',
            "epochs": 1,
            "loss": 'categorical_crossentropy',
            "class-weight": False,
            "test_size": 0.3,
            "remote-storage": "azure-blob",
            "container-name": None,
            "model-name": DEFAULT_NN_MODEL_FILENAME
        },
        'tunable':{}

    }

    def __init__(self, component_config=None):

        """Construct a new class classifier using the sklearn framework."""

        self.defaults = override_defaults(
            super(DnnEstimator, self).defaults, self.defaults)
        self.clf=None
        super().__init__(parameters=component_config)


    @classmethod
    def required_packages(cls):
        return ["tensorflow"]

    def fit(self, X, y, X_val=None, y_val=None):
        fit_kwargs = {}
        if self.get_parameter('class-weight'):
            class_weights = class_weight.compute_class_weight('balanced',
                                                              np.unique(y),
                                                              y)
            fit_kwargs = {"class_weight": class_weights}

        if X_val ==None or y_val==None:
            X, X_val, y,y_val = train_test_split(X, y, test_size=self.get_parameter("test_size"))


        self.clf.fit(X, y, x_validate=X_val, y_validate=y_val, epochs=self.get_parameter("epochs"),
                     fit_kwargs=fit_kwargs)

        print(self.clf.evaluate(X_val, y_val))
        y_pred=self.clf.predict(X_val)
        self.performance_report=ClassifierEvaluator.get_performance_report(y_val, y_pred, None)

    def transform(self, document):

        return self.clf.transform(document, )

    def predict(self, X):
        """Given a bow vector of an input text, predict most probable label.

        Return only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second,
                 its probability."""

        return self.clf.predict(X)

    def train(self, training_data, **kwargs):

        y = [document.label for document in training_data]
        X = vstack([document.vector for document in training_data])
        self.fit(X, y)

    def process(self, document, **kwargs):
        raise NotImplementedError

    def __getstate__(self):
        """Return state values to be pickled."""
        return (self.hyperparameters, self.classifier_type)

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.hyperparameters, self.classifier_type = state


    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):


#        model_file=cls.__name__+'.model-weights.h5'
        classifier_file=cls.__name__+'.'+KOLIBRI_MODEL_FILE_NAME
        dnn_file_name=DNN_MODEL_FOLDER_NAME
        if model_metadata is not None:
            classifier_file_name = model_metadata.get("classifier_file", classifier_file)
            dnn_file_name = model_metadata.get("dnn_folder", dnn_file_name)

        classifier_file = os.path.join(model_dir, classifier_file)
        if os.path.exists(classifier_file):
            # Load saved model
            model = joblib.load(classifier_file)

            clf = model.classifier_type.load_model(os.path.join(model_dir, dnn_file_name))

            model.clf = clf
            return model
        else:
            return cls(model_metadata)


    @classmethod
    def load_from_buffer(cls, pickeld_kolibri,  buffer=None):


        if pickeld_kolibri is not None:
            # Load saved model
            model = joblib.load(pickeld_kolibri)
            with h5py.File(buffer, 'r') as h5_file:
                clf = model.classifier_type.load_model(h5_file)

                model.clf = clf
            return model
        else:
            return None


    @classmethod
    def load_from_azure(cls, container_name=None):
        from tensorflow import keras

        connect_str=os.environ.get("STORAGE_CONTAINER_STRING")


        blob_classifier_file=cls.__name__+'.'+KOLIBRI_MODEL_FILE_NAME

        classfier_file=get_file_object(connect_str, container_name, blob_classifier_file)

        model = joblib.load(classfier_file)
        blob_model_file = model.classifier_type.__name__ + '.model-weights.h5'
        stream = get_file_object(connect_str, container_name, blob_model_file)

        with h5py.File(stream, 'r') as h5_file:
            clf = keras.models.load_model(h5_file)

        model.clf = clf

        return model

    def persist(self, model_dir):
        """Persist this model into the passed directory.

        Returns the metadata necessary to load the model again."""

        classifier_file=self.__class__.__name__+'.'+KOLIBRI_MODEL_FILE_NAME


        classifier_file_name = os.path.join(model_dir, classifier_file)
        joblib.dump(self, classifier_file_name)
        dnn_file_name = os.path.join(model_dir, DNN_MODEL_FOLDER_NAME)
#        if self.get_parameter("remote-storage")=="azure-blob":
#            self.to_azure_blob2(model_dir)

        if self.clf:
            self.clf.save(dnn_file_name)

        return {"classifier_file": classifier_file, "dnn_folder": DNN_MODEL_FOLDER_NAME}

    def save_to_azure(self, container_name):
        """
        Save model
        Args:
            model_path:
        """
        import tempfile
        blob_config_file=type(self.clf).__name__+'.model-config.json'
        blob_model_file=type(self.clf).__name__+'.model-weights.h5'
        classifier_file=self.__class__.__name__+'.'+KOLIBRI_MODEL_FILE_NAME

        td=tempfile.TemporaryDirectory()
        model_path=td.name

        self.persist(model_path)
        connect_str=os.environ.get("STORAGE_CONTAINER_STRING")


        local_config_file = os.path.join(model_path, DNN_MODEL_FOLDER_NAME, blob_config_file)
        local_model_file = os.path.join(model_path, DNN_MODEL_FOLDER_NAME, blob_model_file)
        local_classifier_file = os.path.join(model_path, classifier_file)


        blob_classifier_file=self.__class__.__name__+'.'+KOLIBRI_MODEL_FILE_NAME

        upload_file(connect_str, container_name, local_config_file, blob_config_file, overwrite=True)
        upload_file(connect_str, container_name, local_model_file, blob_model_file, overwrite=True)
        upload_file(connect_str, container_name, local_classifier_file, blob_classifier_file, overwrite=True)

        return container_name
