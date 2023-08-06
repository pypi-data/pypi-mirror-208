import copy
import joblib
from tqdm import tqdm
from kdmt.jupyter import isnotebook
from kolibri.backend.base.base_classifier import BaseClassifier
from sklearn.utils.multiclass import type_of_target
from datetime import datetime
from kdmt.dict import update
from kolibri.optimizers.optuna.objective import EstimatorObjective
from copy import deepcopy
from kolibri.logger import get_logger
from kolibri.config import TaskType
from kdmt.objects import class_from_module_path
from kolibri.evaluation.classifier_evaluator import ClassifierEvaluator
import pandas as pd
from tabulate import tabulate

logger = get_logger(__name__)

class ZooClassifier(BaseClassifier):

    defaults =  {"fixed": {
            "default-params": None,
            "classifiers": "all",
            "fast-models-only": False,
            "task-type": TaskType.CLASSIFICATION
        },

        "tunable": {
        }
    }
    def __init__(self, hyperparameters=None, model=None, indexer=None):
        """Construct a new class classifier using the sklearn framework."""

        super(ZooClassifier, self).__init__(params=hyperparameters, model=model, indexer=indexer)
        import kolibri.backend.models


        selected_models=kolibri.backend.models.sklearn_classification_models_names

        if isinstance(self.get_parameter("classifiers", []), list):
            selected_models=self.get_parameter("classifiers", [])

        self.models=[]
        exceptions=['EcocEstimator']
        self.models=[]
        for model_name in selected_models:
            if model_name in exceptions:
                continue
            model=self.load_model_from_parameters(kolibri.backend.models.get_model(model_name, task_type=self.get_parameter("task-type")))
            print(model_name)
            if model is not None:
                if self.get_parameter("fast-models-only") and model[0]["performance"] !="fast":
                    continue
                print("adding: ", model_name)
                self.models.append((model[0],model[1]))


    def fit(
        self,
        X,
        y,
        X_validation=None,
        y_validation=None
    ):

        if self.indexer is not None:
            self.indexer.build_vocab(None, y)
            y = self.indexer.transform(y)


        if self.get_parameter('priors-thresolding'):
            self.compute_priors(y)

        if self.sampler and self.X_sampled is not None and self.y_sampled is not None:
            print('sampling data. Original data size: ', len(y))
            X_sampled, y_sampled = self.sampler.fit_resample(X, y)
            print('finished sampling. Sampled data size: ', len(y_sampled))
        names=[]
        self.performace_scores=[]
        pd_report_scores=[]
        for params, model in tqdm(self.models):

            print('fitting: '+params["name"])

            if params["matrix"]!="sparse":
                X = X.toarray()
            self.model=model

            model_results, runtime, model_fit_time, predictions=super().fit(X, y, X_validation, y_validation)

            performace_score=model_results.loc['Mean'].to_dict()
            performace_score["classif_name"] = params["name"]
            names.append(params["name"])
            self.performace_scores.append(performace_score)
            performace_score_pd=deepcopy(performace_score)

            pd_report_scores.append(performace_score_pd)
        scores = pd.DataFrame(pd_report_scores)
        self.scores = scores.sort_values(by="MAE", ascending=True).set_index(
            "classif_name"
        )
        if not isnotebook():
            print(tabulate(scores, headers='keys', tablefmt='psql'))

        return None,None,None, None

    def load_model_from_parameters(self, model_params):
        model_params=deepcopy(model_params)
        model=class_from_module_path(model_params["class"])
        if model is None:
            return None
        default_params={p:model_params["parameters"][p]["value"] for p in model_params["parameters"]}
        for param, param_val in default_params.items():
            if isinstance(param_val, list):
                for i, p in enumerate(param_val):
                    if isinstance(p, dict):
                        default_params[param][i]=self.load_model_from_parameters(p)
            elif isinstance(param, dict):
                default_params[param] = self.load_model_from_parameters(param_val)

        return (model_params, model(**default_params))

    def copy(self):
        return copy.deepcopy(self)

    def save(self, model_file_path):
        raise Exception("ZooClassifier cannot be saved.")

    def load_model(self, model_file_path):
        raise Exception('Cannot load ZooClassifier, because it cannot be saved')


