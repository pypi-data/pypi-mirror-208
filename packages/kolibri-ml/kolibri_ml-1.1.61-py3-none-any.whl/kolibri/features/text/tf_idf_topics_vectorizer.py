import os
import time
from typing import Any, Dict, Text
from sklearn.pipeline import FeatureUnion

import joblib
import pickle
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline as SKPipeline
from kolibri.features.text.tf_idf_featurizer import TFIDFFeaturizer
from kolibri.logger import get_logger

logger = get_logger(__name__)

class TFIDFTopicFeaturizer(TFIDFFeaturizer):
    """Bag of words featurizer

    Creates bag-of-words representation of intent features
    using sklearn's `CountVectorizer`.
    All tokens which consist only of digits (e.g. 123 and 99
    but not ab12d) will be represented by a single feature."""

    provides = ["text_features"]

    requires = ["tokens"]

    defaults = {
            "fixed": {

                # regular expression for tokens
                "token-pattern": r'(?u)\b\w\w+\b',

                # remove accents during the preprocessing step
                "strip-accents": None,  # {'ascii', 'unicode', None}

                "min-ngram": 1,  # int
            },

            "tunable": {

                "nb-topics": {
                    "description": "numner of topics for the topic model",
                    "value": 50,
                    "type": "integer",
                    "range": [20, 50]
                }

            }
        }

    @classmethod
    def required_packages(cls):
        return ["sklearn"]

    def _load_count_vect_params(self):
        from kolibri.stopwords import get_stop_words

        # regular expression for tokens
        self.token_pattern = self.get_parameter('token-pattern')

        # remove accents during the preprocessing step
        self.strip_accents = self.get_parameter('strip-accents')

        self.stop_words = None
        # list of stop words
        if self.get_parameter('stop-words'):
            self.stop_words = self.get_parameter('stop-words')
        elif self.get_parameter("remove-stopwords") and self.get_parameter('language'):
            self.stop_words=get_stop_words(self.get_parameter('language'))
        elif self.get_parameter("remove-stopwords") and not self.get_parameter('language'):
            raise Exception('Please specify "language" if you want to remove stop words')

        # min number of word occurancies in the document to add to vocabulary
        self.min_df = self.get_parameter('min-df')

        # max number (fraction if float) of word occurancies
        # in the document to add to vocabulary
        self.max_df = self.get_parameter('max-df')

        # set ngram range
        self.min_ngram = self.get_parameter('min-ngram')
        self.max_ngram = self.get_parameter('max-ngram')

        # limit vocabulary size
        self.max_features = self.get_parameter('max-features')

        # if convert all characters to lowercase
        self.lowercase = self.get_parameter('do-lower-case')

    def __init__(self, hyperparameters=None):
        """Construct a new count vectorizer using the sklearn framework."""

        super(TFIDFTopicFeaturizer, self).__init__(hyperparameters)

        self.topic_model= TruncatedSVD(n_components=self.get_parameter("nb-topics"))

        self.__build_pipeline()

    def _identity_tokenizer(self, text):
        return text

    def get_feature_names(self):
        return self.vectorizer.get_feature_names()

    def fit(self, X, y):
        if not self.fitted:
            self.vectorizer_topic.fit(list(X), y)
            self.fitted=True
        return self

    def __build_pipeline(self):
        # define pipeline
        self.vectorizer_topic =  FeatureUnion(
                transformer_list=[
                    # TFIDF features
                    ('tfidf', self.vectorizer),
                    # standard bag-of-words model : TFIDF+SVD
                    ('body_bow', SKPipeline([
                        ('tfidf', self.vectorizer),
                        ('best', self.topic_model),
                    ]))
                ],
                # weight components in FeatureUnion
                transformer_weights={
                    'tfidf': 1,
                    'body_bow': 0.5
                },
                n_jobs=1
            )

    def transform(self, X):

        if self.vectorizer is None:
            logger.error("There is no trained CountVectorizer: "
                         "component is either not trained or "
                         "didn't receive enough training texts")
        else:
            return self.vectorizer.transform(raw_documents=X)

    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]
        """Persist this model_type into the passed directory.
        Returns the metadata necessary to load the model_type again."""

        featurizer_file = os.path.join(model_dir, self.name + ".pkl")
        joblib.dump(self, featurizer_file)

        if self.get_parameter("save-base-model")==True:
            pickle.dump(self.vectorizer.vocabulary_, open(os.path.join(model_dir, "_base_tfidf_.pkl"), "wb"))


        return {"featurizer_file": self.name + ".pkl", 'folder': model_dir}

    @classmethod
    def load(cls,
             model_dir=None, model_metadata=None, cached_component=None, **kwargs):


        if model_metadata.get("folder") is not None:
            model_dir=model_metadata.get("folder")
        if model_dir and model_metadata.get("featurizer_file"):
            file_name = model_metadata.get("featurizer_file")
            featurizer_file = os.path.join(model_dir, file_name)
            return joblib.load(featurizer_file)
        else:
            logger.warning("Failed to load featurizer. Maybe path {} "
                           "doesn't exist".format(os.path.abspath(model_dir)))
            return TFIDFFeaturizer(model_metadata)
