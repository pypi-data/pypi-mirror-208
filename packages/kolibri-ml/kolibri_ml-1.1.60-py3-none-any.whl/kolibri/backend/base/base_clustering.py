import gc

import numpy as np
import pandas as pd

from kolibri.backend.base.base_estimator import BaseEstimator
from kolibri.evaluation.metrics import clustering

from kolibri.config import TaskType
from kolibri.config import ParamType
from kolibri.logger import get_logger
from kolibri import default_configs as settings
import time
from kdmt.df import color_df

logger = get_logger(__name__)

KOLIBRI_MODEL_FILE_NAME = "clustring_kolibri.pkl"



class BaseClustering(BaseEstimator):
    """
    This is an abstract class.
    All estimators inherit from BaseEstimator.
    The notion of Estimator represents any mathematical model_type that estimate a response function. In machine learning it can represent either
    a supervised or unsupervised classification algorithm.

    Estimators have the following paramters that can be modified using the configuration object.

    Fixed Hyperparameters
    ---------------------
    base-estimator: a defined kolibri or sklearn.BaseEstimator (default=LogisticRegression)
        This is used by kolibri.bakend.meta estimators as a base estimator for each member of the ensemble is an instance of the base estimator

    explain : boolean (default=False)
        used to output an explanation file in the output folder.

    sampler: str (default=None), A sampler such as SMOTE can be used to balance the data in case the dataset is heavily unbalanced.
    see kolibri.samplers for various options that can be used.

    "priors-thresolding":boolean (default=False), a strategy to handle unbalanced dataset, by class prior probability.

    evaluate-performance: boolean (default=False), use this config to generate performance data before training the model_type.

    optimize-estimator: boolean (default=False), use this config to optimise the parameters of the estimtors. the optimisation stategy optimised the tunable parameters.

    Tunable Hyperparameters
    ---------------------

    These hyper parameters are used in optimization strategies to optimize the performances.
    one obvious parameter to optimise is the base model_type used to train the data.

    """

    short_name = "Unknown"

    component_type = "estimator"

    provides = ["clustering"]

    requires = ["text_features"]

    defaults = {
            "fixed": {
            },
            "tunable": {
                "model-param": {
                    "description": "This is just an example of a tuneable variable",
                    "value": "logreg",
                    "type": ParamType.CATEGORICAL,
                }

            }
        }

    def __init__(self, params, model=None, indexer=None):
        super().__init__(params=params, model=model)

        self._setup_model(params['model'])
        self.all_plots = {
            "pipeline": "Pipeline Plot",
            "roc": "ROC",
            "confusion_matrix": "Confusion Matrix",
            "threshold": "Threshold",
            "pr": "Precision Recall",
            "error": "Prediction Error",
            "class_report": "Class Report",
            "class_distribution": "Class Distribution",
            "score_distribution": "Score distribution",
            "errors": "Classification Errors",
            "tree": "Decision tree based visualization",
            "tsne": "TSNE Visualization",
            "umap": "UMAP based visualization",
            "calibration": "Probability Calibration Plot"
        }


    def _get_models(self):
        from kolibri.backend.models import sklearn_clustering_models
        return sklearn_clustering_models

    def _get_model(self, model):
        from kolibri.backend.models import get_model
        return get_model(model, task_type = TaskType.TOPICS)


    def _get_metrics(self):
        return clustering.get_all_metrics()


if __name__=="__main__":
    import joblib
    cl=BaseClassifier({"model": 'LogisticRegression'})
    joblib.dump(cl, './test.pkl')