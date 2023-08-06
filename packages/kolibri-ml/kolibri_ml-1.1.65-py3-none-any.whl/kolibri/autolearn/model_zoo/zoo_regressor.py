import copy
import joblib
from tqdm import tqdm
from kdmt.jupyter import isnotebook
from kolibri.backend.base.base_regressor import BaseRegressor
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

class ZooRegressor(BaseRegressor):

    defaults =  {"fixed": {
            "default-params": None,
            "classifiers": "all",
            "fast-models-only": False,
            "task-type": TaskType.REGRESSION,
            "Sort-values-by": "MAE",
            "sort-ascending": True
        },

        "tunable": {
        }
    }
    def __init__(self, hyperparameters=None, model=None, indexer=None):
        """Construct a new class classifier using the sklearn framework."""

        super(ZooRegressor, self).__init__(params=hyperparameters, model=model, indexer=indexer)
        import kolibri.backend.models


        selected_models=kolibri.backend.models.sklearn_regression_models_names
        if isinstance(self.get_parameter("classifiers", []), list):
            selected_models=self.get_parameter("classifiers", [])

        self.models=[]
        for model_name in selected_models:
            model=self.load_model_from_parameters(kolibri.backend.models.get_model(model_name, task_type=self.get_parameter("task-type")))
            print(model_name)
            if model is not None:
                if self.get_parameter("fast-models-only") and model[0]["performance"] !="fast":
                    continue
                print("adding: ", model_name)
                self.models.append((model[0],model[1]))


    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, ZooRegressor.defaults)
        super().update_default_hyper_parameters()

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

    def fit(
        self,
        X,
        y,
        X_validation=None,
        y_validation=None
    ):

        names=[]
        self.performace_scores=[]
        pd_report_scores=[]
        for params, model in tqdm(self.models):

            print('fitting: '+params["name"])
            self.model=model

            model_results, runtime, model_fit_time, predictions=super().fit(X, y, X_validation, y_validation)

            performace_score=model_results.loc['Mean'].to_dict()
            performace_score["classif_name"] = params["name"]
            names.append(params["name"])
            self.performace_scores.append(performace_score)
            performace_score_pd=deepcopy(performace_score)

            pd_report_scores.append(performace_score_pd)
        scores = pd.DataFrame(pd_report_scores)
        by=self.get_parameter("Sort-values-by")
        self.scores = scores.sort_values(by=by, ascending=self.get_parameter("sort-ascending")).set_index(
            "classif_name"
        )
        if not isnotebook():
            print(tabulate(self.scores, headers='keys', tablefmt='psql'))

        return None,None,None, None


    def copy(self):
        return copy.deepcopy(self)

    def save(self, model_file_path):
        raise Exception("ZooRegressor cannot be saved.")

    def load_model(self, model_file_path):
        raise Exception('Cannot load ZooRegressor, because it cannot be saved')

