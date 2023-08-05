import os
from typing import List
from typing import Text

import joblib
from gensim.models import Phrases

from kolibri.core.component import Component
from kolibri.logger import get_logger
from kdmt.file import save_to_disk, load_from_disk

logger = get_logger(__name__)

BIGRAM_FILENAME = "kolibri-bigram.model"


class CollocationAnalyzer(Component):

    _estimator_type = 'estimator'

    provides = ["ngram"]

    requires = ["text_features"]

    defaults = {
        "fixed":{
            "retrain-bigram": False
                 },
        # We try to find a good number of cross folds to use during
        # class training, this specifies the max number of folds
        "tunable":{
            "min-count": 5,
            "threshold": 10,
        }
    }

    def __init__(self, component_config=None):
        """Construct a new class classifier using the sklearn framework."""
        super().__init__(parameters=component_config)
        self.bigram_model = None

    @classmethod
    def required_packages(cls):
        return ["gensim"]

    def train(self, training_data, **kwargs):
        retrain = self.get_parameter('retrain-bigram')
        if retrain:
            self.train_bigram(training_data)
            self.save_bigram_model()
        elif self.bigram_model:
            [self.process(d) for d in training_data]
        else:
            self.bigram_model = self.load_bigram_model()
            [self.process(d) for d in training_data]

    def fit(self, X, y):
        retrain = self.get_parameter('retrain-bigram')
        if retrain:
            self.train_bigram(X)
            self.save_bigram_model()
        else:
            try:
                self.bigram_model = self.load_bigram_model()

            except:
                self.train_bigram(X)
                self.save_bigram_model()
                self.bigram_model = self.load_bigram_model()
        return self

    def transform(self, data, **kwargs):
        return [self.bigram_model[d] for d in data]

    def process(self, document, **kwargs):
        return self.bigram_model[document.sentences]

    def train_bigram(self, trainingdata):
        """
        Train the word2vec model on a directory with text files.
        :param train_dir: directory with '.txt' files
        :param vec_dim: dimensionality of the word vectors

        :return: trained gensim model
        """

        class SentenceIterator(object):
            def __init__(self, data):
                self.training_data = data

            def __iter__(self):
                for document in self.training_data:
#                    for sentence in document.sentences:
                    yield document

        self.bigram_model = Phrases(SentenceIterator(trainingdata), min_count=self.get_parameter('min-count'),
                                    threshold=self.get_parameter('threshold'))

        return self.bigram_model

    def save_bigram_model(self, overwrite=True):
        """ Save the word2vec model to a file """
        if not self.bigram_model:
            raise ValueError("Can't save the word2vec model, " + \
                             "it has not been trained yet")
        save_to_disk(os.path.join(self.get_parameter("output-folder"), BIGRAM_FILENAME), self.bigram_model,
                     overwrite=overwrite)

    def load_bigram_model(self):
        """ Load the word2vec model from a file """
        self.bigram_model = load_from_disk(os.path.join(self.get_parameter("output-folder"), BIGRAM_FILENAME))
        return self.bigram_model

    @classmethod
    def load(cls, model_dir=None, metadata=None, cached_component=None, **kwargs):


        file_name = metadata.get("bigram_file", BIGRAM_FILENAME)
        classifier_file = os.path.join(model_dir, file_name)

        if os.path.exists(classifier_file):
            model = joblib.load(classifier_file)

            return model
        else:
            return cls(metadata)

    def persist(self, model_dir):
        """Persist this model into the passed directory."""

        bigram_file = os.path.join(model_dir, BIGRAM_FILENAME)
        joblib.dump(self, bigram_file)

        return {
            "bigram_file": BIGRAM_FILENAME
        }

    def get_info(self):
        return "brigram analyzer"



from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(CollocationAnalyzer.name, CollocationAnalyzer)
