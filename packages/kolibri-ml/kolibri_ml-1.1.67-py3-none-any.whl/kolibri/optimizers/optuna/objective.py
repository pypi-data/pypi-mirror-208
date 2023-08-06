try:
    import optuna
    has_optuna=True
except:
    has_optuna=False
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_predict
EPS = 1e-8
from kolibri.evaluation.metrics import Metric
from kolibri.core.pipeline import Pipeline
import warnings
from copy import deepcopy
from sklearn.model_selection import train_test_split
from kdmt.objects import class_from_module_path, class_name
from kolibri.config import ParamType, TaskType
warnings.filterwarnings("ignore")

from kdmt.dict import nested_dict_set_key_value, nested_dict_get_key_path

class Objective:
    def __init__(
        self,
        X,
        y,
        estimator,
        sample_weight,
        eval_metric="f1-score",
        random_state=41,
        n_jobs=-1,
        sampling_ratio=None
        ):

        self.X = X
        self.y = y
        self.sample_weight = sample_weight
        self.parameters=deepcopy(estimator.parameters)
        self.eval_metric = eval_metric
        self.eval_metric_name=eval_metric.display_name
        self.n_jobs = n_jobs
        self.seed = random_state
        self.estimator=estimator
        self.sampling_ratio=sampling_ratio

    def get_parameters(self, trial):
        params = deepcopy(self.parameters)
        for component, component_val in params.items():
            path=str(component)
            tunable=component_val["tunable"]
            path=path+".tunable"
            if tunable:
                for tuneable_key, tuneable_val in tunable.items():
                    if "type" in tuneable_val:
                        try:
                            path2=tuneable_key
                            if tuneable_val["type"] == "categorical" and "values" in tuneable_val:
                                tuneable_val["value"] = trial.suggest_categorical(path2, tuneable_val["values"])
                            elif tuneable_val["type"] == "integer" and "values" in tuneable_val:
                                tuneable_val["value"] = trial.suggest_int(path2, low=tuneable_val["values"][0],
                                                                          high=tuneable_val["values"][-1])
                            elif tuneable_val["type"] == "integer" and "range" in tuneable_val:
                                tuneable_val["value"] = trial.suggest_int(path2, low=tuneable_val["range"][0],
                                                                          high=tuneable_val["range"][-1])
                            elif tuneable_val["type"] == "float" and "values" in tuneable_val:
                                tuneable_val["value"] = trial.suggest_float(path2, low=tuneable_val["values"][0],
                                                                           high=tuneable_val["values"][-1])
                            elif tuneable_val["type"] == "float" and "range" in tuneable_val:
                                tuneable_val["value"] = trial.suggest_float(path2, low=tuneable_val["range"][0],
                                                                           high=tuneable_val["range"][-1])
                        except Exception as e:
                            raise e
                    elif tuneable_key=='model':
                        for parameter_name, parameter in tuneable_val["value"]["parameters"].items():
                            if "type" in parameter:
                                path2 = "model."+parameter_name
                                if parameter["type"] == "categorical" and "values" in parameter:
                                    parameter["value"] = trial.suggest_categorical(path2, parameter["values"])
                                elif parameter["type"] == "integer" and "values" in parameter:
                                    parameter["value"] = trial.suggest_int(path2, low=parameter["values"][0],
                                                                              high=parameter["values"][-1])
                                elif parameter["type"] == "integer" and "range" in parameter:
                                    parameter["value"] = trial.suggest_int(path2, low=parameter["range"][0],
                                                                              high=parameter["range"][-1])
                                elif parameter["type"] == "float" and "values" in parameter:
                                    parameter["value"] = trial.suggest_float(path2, low=parameter["values"][0],
                                                                               high=parameter["values"][-1])
                                elif parameter["type"] == "float" and "range" in parameter:
                                    parameter["value"] = trial.suggest_float(path2, low=parameter["range"][0],
                                                                               high=parameter["range"][-1])
        return params

    def get_optuna_parameters(self, params):
        opt_params = {}
        for component, component_val in params.items():
            path=str(component)
            tunable=component_val["tunable"]
            if tunable:
                for tuneable_key, tuneable_val in tunable.items():
                    if "type" in tuneable_val:
                        try:
                            path2=tuneable_key
                            opt_params[path2]=tuneable_val["value"]
                        except Exception as e:
                            raise e
                    elif tuneable_key=='model':
                        for parameter_name, parameter in tuneable_val["value"]["parameters"].items():
                            if "type" in parameter:
                                path2 = "model."+parameter_name
                                opt_params[path2] = parameter["value"]
        return opt_params

    def update_parameters(self, best):
        raise NotImplementedError

    def __call__(self, trial):
        raise NotImplementedError


class EstimatorObjective(Objective):

    def get_estimator_parameters(self, original_params, trial, path=[]):

        for tuneable_key, tuneable_val in original_params.items():
            if len(path)==0 or path[-1]!=tuneable_key:
                path.append(tuneable_key)
            if isinstance(tuneable_val, dict):
                if "type" in tuneable_val and "values" in tuneable_val:
                    if tuneable_val["type"] in [ParamType.CATEGORICAL, "categorical"]:
                        print(path)
                        tuneable_val["value"] = trial.suggest_categorical('.'.join(path), tuneable_val["values"])
                    elif tuneable_val["type"] in [ParamType.INTEGER, "integer"]:
                        print(path)
                        tuneable_val["value"] = trial.suggest_int('.'.join(path), low=tuneable_val["values"][0],
                                                                  high=tuneable_val["values"][-1])
                    elif tuneable_val["type"] in [ParamType.RANGE, "float"]:
                        print(path)
                        tuneable_val["value"] = trial.suggest_float('.'.join(path), low=tuneable_val["values"][0],
                                                                    high=tuneable_val["values"][-1])
                elif isinstance(tuneable_val, dict):
                    self.get_estimator_parameters(tuneable_val, trial, path)
                else:
                    tuneable_val[tuneable_key] = tuneable_val["value"]
            elif isinstance(tuneable_val, list):
                for i, val in enumerate(tuneable_val):
                    if isinstance(val, dict):
                        path.append(str(i))
                        self.get_estimator_parameters(val, trial, path)
                    path.pop()
            if len(path)>0:
                path.pop()
        return original_params

    def __call__(self, trial):
        try:
            params=self.get_estimator_parameters(deepcopy(self.parameters), trial, path=[])


            model = class_from_module_path(class_name(self.estimator))(params)

            preds=cross_val_predict(model.model_type, self.X, self.y, cv=3, n_jobs=self.n_jobs)


            score = self.eval_metric(self.y, preds)
            if self.direction=='maximize':
                score *= -1.0

        except optuna.exceptions.TrialPruned as e:
            raise e
        except Exception as e:
            print("Exception in EstimatorObjective", str(e))
            if self.direction=="maximize":
                return -100000
            else:
                return 100000


        return score


class PipelineObjective(Objective):

    def __call__(self, trial):
        try:
            params=self.get_parameters(trial)


            pipeline = Pipeline.from_configs(params)

            if self.sampling_ratio is not None:
                X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size = 0.3)

            else:
                X_train, y_train=self.X, self.y

            results= pipeline.fit(X_train, y_train)
            if self.eval_metric.display_name in results[0].to_dict():
                score = results[0].to_dict()[self.eval_metric.display_name]['Mean']
            else:
                pred=pipeline.predict(X_test)
                if self.estimator.estimator.task_type==TaskType.CLASSIFICATION:
                    pred=[p['name'] for p in pred['label']]



                score = self.eval_metric(y_test, pred)

            if not self.eval_metric.greater_is_better:
                score *= -1.0

        except optuna.exceptions.TrialPruned as e:
            raise e
        except Exception as e:
            print("Exception in EstimatorObjective", str(e))
            if not self.eval_metric.greater_is_better:
                return -100000
            else:
                return 100000


        return score

    def update_parameters(self, best):
        if best:
            for key in best:
                keys=key.split(".")
                if len(keys)>1 and keys[0]=='model':
                    for name, component in self.parameters.items():
                        if 'model' in component["tunable"]:
                            for param_name, param in component["tunable"]["model"]["value"]["parameters"].items():
                                if param_name==keys[1]:
                                    component["tunable"]["model"]["value"]["parameters"][param_name]["value"]=best[key]
                else:
                    for name, component in self.parameters.items():
                        for param_name, param in component["tunable"].items():
                            if param_name==keys[0]:
                                component["tunable"][param_name]["value"]=best[key]



        return self.parameters
