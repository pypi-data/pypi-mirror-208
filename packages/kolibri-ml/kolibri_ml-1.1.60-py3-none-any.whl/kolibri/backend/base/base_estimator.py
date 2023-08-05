import gc
import os
import uuid
from typing import Tuple

import numpy as np
from kdmt.jupyter import isnotebook
from kdmt.ml.common import sklearn_numpy_warning_fix

from kolibri.core.component import Component
from kolibri.utils.cross_validation import cross_val_predict_score

try:
    from kolibri.explainers.shap_explainer import PlotSHAP
except:
    pass
from kdmt.cloud import google
from kdmt.cloud import azure
from sklearn.model_selection import cross_validate
from kdmt.dict import update
from sklearn.calibration import CalibratedClassifierCV
from copy import deepcopy
from kdmt.objects import class_from_module_path
from kolibri.logger import get_logger
import pandas as pd
import time
import datetime


logger = get_logger(__name__)
from kolibri.output import DefaultDisplay
import joblib

KOLIBRI_MODEL_FILE_NAME = "classifier_kolibri.pkl"


class BaseEstimator(Component):
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

    provides = ["classification", "target_ranking"]

    requires = ["text_features"]

    defaults = {
        "fixed": {
            "auto-ml": False,
            "base-estimator": None,
            "explain": False,
            'evaluate-performance': False,
            'task-type': None,
            'optimize-estimator': False,
            'features-names': None,
            'max-nb-models': 5,
            'fold_strategy': 'stratifiedkfold',
            'resampling-strategy': 'holdout',  # 'cv'
            'imputer': 'none',
            'fold-shuffle': True,
            'cross-validate': True,
            'groups': None,
            "n-folds": 5,
            "round": 4,
            "display": "default",
            "return-predictions": True
        },

        "tunable": {
            'model':{
                "value":{

                }

            }
        }
    }

    def __init__(self, params, model=None):
        super().__init__(parameters=params)
        self.params = params
        self.library_version = None
        self.model = model
        self.all_plots = {}
        self.uid = params.get("uid", str(uuid.uuid4()))
        self.model_file_path = None
        self.data = None
        self.X=None
        self.y_true=None
        sklearn_numpy_warning_fix()

        self.performace_scores = "Not Computed"
        # CV params
        fold_param = self.get_parameter("n-folds")
        self.feature_names = None
        fold_shuffle_param = self.get_parameter("fold-shuffle")

        from sklearn.model_selection import (
            StratifiedKFold,
            KFold,
            GroupKFold,
            TimeSeriesSplit,
        )

        fold_seed = self.get_parameter("random-state") if fold_shuffle_param else None
        if fold_param is not None and fold_param > 0:
            if self.get_parameter("fold_strategy") == "kfold":
                self.fold_generator = KFold(
                    fold_param, random_state=fold_seed, shuffle=fold_shuffle_param
                )
            elif self.get_parameter("fold_strategy") == "stratifiedkfold":
                self.fold_generator = StratifiedKFold(
                    fold_param, random_state=fold_seed, shuffle=fold_shuffle_param
                )
            elif self.get_parameter("fold_strategy") == "groupkfold":
                self.fold_generator = GroupKFold(fold_param)
            elif self.get_parameter("fold_strategy") == "timeseries":
                self.fold_generator = TimeSeriesSplit(fold_param)
            else:
                self.fold_generator = self.get_parameter("fold_strategy")
        else:
            self.fold_generator = None

        self.plotter = None

    @property
    def task_type(self):
        return self.get_parameter("task-type")

    def update_default_hyper_parameters(self):
        self.defaults = update(BaseEstimator.defaults, self.defaults, )
        super().update_default_hyper_parameters()

    def load_model_from_parameters(self, model_params):
        model_params = deepcopy(model_params)
        model = class_from_module_path(model_params["class"])
        if model is None:
            raise ValueError('Could not fint ' + model_params[
                "class"] + ". Please make the name is correct and/or install any missing libraries")

        default_params = {p: model_params["parameters"][p]["value"] for p in model_params["parameters"]}
        for param, param_val in default_params.items():
            if isinstance(param_val, list):
                for i, p in enumerate(param_val):
                    if isinstance(p, dict):
                        default_params[param][i] = self.load_model_from_parameters(p)
            elif isinstance(param, dict):
                default_params[param] = self.load_model_from_parameters(param_val)

        return (model_params["name"], model(**default_params))

    def update_model_parameters(self):
        if "fixed" in self.hyperparameters:
            for c in self.hyperparameters["fixed"]:

                if c in self.hyperparameters["tunable"]["model"]["value"]["parameters"]:
                    self.hyperparameters["tunable"]["model"]["value"]["parameters"][c]["value"] = self.hyperparameters["fixed"][
                        c]

        model_params={k[6:]:p for k, p in self.params.items() if 'model.' in k[:6]}
        for k, p in model_params.items():
            if k in self.hyperparameters["tunable"]["model"]["value"]["parameters"]:
                self.hyperparameters["tunable"]["model"]["value"]["parameters"][k]["value"] = p

    def fit(self, data_X=None, data_y=None, X_val=None, y_val=None):

        """
        Internal version of ``create_model`` with private arguments.
        """
        raise NotImplementedError

    def _setup_model(self, model):

        logger.info("Checking exceptions")

        available_estimators = set(self._get_models().keys())

        # only raise exception of estimator is of type string.

        if isinstance(model, str):
            if model not in available_estimators:
                raise ValueError(
                    f"Estimator {model} not available. Please see docstring for list of available estimators."
                )
        elif model is not None and not isinstance(model, dict) and not hasattr(model, "fit"):
            raise ValueError(
                f"Estimator {str(model)} does not have the required fit() method."
            )
        if isinstance(model, str):
            self.hyperparameters["tunable"]["model"]["value"] = self._get_model(model)
            self.update_model_parameters()
        self.model = self.load_model_from_parameters(self.get_parameter("model"))[1]
        self.model_library=self.get_parameter("model")["library"]




        # checking round parameter
        if type(self.get_parameter("round")) is not int:
            raise TypeError("Round parameter only accepts integer value.")

        # checking verbose parameter
        if type(self.get_parameter("verbose")) is not bool:
            raise TypeError(
                "Verbose parameter can only take argument as True or False."
            )

        # checking cross_validation parameter
        if type(self.get_parameter('cross-validate')) is not bool:
            raise TypeError(
                "cross_validation parameter can only take argument as True or False."
            )

        """

        ERROR HANDLING ENDS HERE

        """

        groups = self.get_parameter("groups")
        self.display=False
        if not self.display:
            progress_args = {"max": 4}
            timestampStr = datetime.datetime.now().strftime("%H:%M:%S")
            monitor_rows = [
                ["Initiated", ". . . . . . . . . . . . . . . . . .", timestampStr],
                [
                    "Status",
                    ". . . . . . . . . . . . . . . . . .",
                    "Loading Dependencies",
                ],
                [
                    "Estimator",
                    ". . . . . . . . . . . . . . . . . .",
                    "Compiling Library",
                ],
            ]
            self.display = DefaultDisplay(
                verbose=self.get_parameter("verbose"),
                html_param=True,
                progress_args=progress_args,
                monitor_rows=monitor_rows,
            )


        np.random.seed(self.get_parameter("seed"))

        self.display.move_progress()

    def _create_and_evaluate_model(self, data_X, data_y):
        """
        MONITOR UPDATE STARTS
        """
        avgs_dict = {}
        predictions = []
        model_fit_start = time.time()
        model_results = None

        if self.get_parameter("evaluate-performance"):
            self.display.update_monitor(1, "Initializing CV")

            cv = self.fold_generator

            self.display.update_monitor(
                row_idx=1,
                message=f"Fitting {cv} Folds"
            )
            """
            MONITOR UPDATE ENDS
            """

            metrics = self._get_metrics()
            metrics_dict = dict([(k, v.scorer) for k, v in metrics.items()])

            logger.info("Starting cross validation")

            n_jobs = self.get_parameter("n_jobs")
            from sklearn.gaussian_process import (
                GaussianProcessClassifier,
                GaussianProcessRegressor,
            )

            # special case to prevent running out of memory
            if isinstance(self.model, (GaussianProcessClassifier, GaussianProcessRegressor)):
                n_jobs = 1

            logger.info(f"Cross validating with {cv}, n_jobs={n_jobs}")
            predictions=None
            if self.get_parameter("return-predictions"):
                predictions, scores = cross_val_predict_score(
                    self.model,
                    data_X,
                    data_y,
                    method='predict_proba',
                    cv=cv,
                    scoring=metrics_dict,
                    n_jobs=n_jobs,
                    error_score=0,
                )
            else:
                scores=cross_validate(
                self.model,
                    data_X,
                    data_y,
                    cv=cv,
                    scoring=metrics_dict,
                    n_jobs=n_jobs,
                    error_score=0)
            score_dict = {}
            for k, v in metrics.items():
                score_dict[v.display_name] = []
                test_score = scores[f"test_{k}"] * (1 if v.greater_is_better else -1)
                test_score = test_score.tolist()
                score_dict[v.display_name] += test_score

            logger.info("Calculating mean and std")

            avgs_dict = {}
            for k, v in metrics.items():
                avgs_dict[v.display_name] = []
                test_score = scores[f"test_{k}"] * (1 if v.greater_is_better else -1)
                test_score = test_score.tolist()
                avgs_dict[v.display_name] += [np.mean(test_score), np.std(test_score)]

            self.display.move_progress()

            logger.info("Creating metrics dataframe")

            if hasattr(cv, "n_splits"):
                fold = cv.n_splits
            elif hasattr(cv, "get_n_splits"):
                fold = cv.get_n_splits()
            else:
                raise ValueError(
                    "The cross validation class should implement a n_splits "
                    f"attribute or a get_n_splits method. {cv.__class__.__name__} "
                    "has neither."
                )

            model_results = pd.DataFrame(
                {
                    "Fold": np.arange(fold).tolist() + ["Mean", "Std"],
                }
            )

            model_scores = pd.concat(
                [pd.DataFrame(score_dict), pd.DataFrame(avgs_dict)]
            ).reset_index(drop=True)

            model_results = pd.concat([model_results, model_scores], axis=1)
            model_results.set_index(["Fold"], inplace=True)
            model_results = model_results.round(self.get_parameter("round"))
        else:
            self.display.update_monitor(1, f"Fitting {str(self.model)}")

        self.finalize_model(data_X, data_y)

        model_fit_end = time.time()

        # calculating metrics on predictions of complete train dataset

        model_fit_time = np.array(model_fit_end - model_fit_start).round(2)

        return model_fit_time, model_results, avgs_dict, predictions


    def finalize_model(self, X, y):
        self.model.fit(X, y)

        logger.info("Finalizing model")
        if self.get_parameter("calibrate-model"):
            self.model = CalibratedClassifierCV(self.model, cv=None, method=self.get_parameter("calibration-method"))


    def get_params(self):
        params = {
            "library_version": self.library_version,
            "algorithm_name": self.algorithm_name,
            "algorithm_short_name": self.algorithm_short_name,
            "uid": self.uid,
            "params": self.params,
            "name": self.name,
        }
        if hasattr(self, "best_ntree_limit") and self.best_ntree_limit is not None:
            params["best_ntree_limit"] = self.best_ntree_limit
        return params

    def set_params(self, json_desc, learner_path):
        self.library_version = json_desc.get("library_version", self.library_version)
        self.algorithm_name = json_desc.get("algorithm_name", self.algorithm_name)
        self.algorithm_short_name = json_desc.get(
            "algorithm_short_name", self.algorithm_short_name
        )
        self.uid = json_desc.get("uid", self.uid)
        self.params = json_desc.get("params", self.params)
        self.name = json_desc.get("name", self.name)
        self.model_file_path = learner_path

        if hasattr(self, "best_ntree_limit"):
            self.best_ntree_limit = json_desc.get(
                "best_ntree_limit", self.best_ntree_limit
            )

    @classmethod
    def required_packages(cls):
        return ["sklearn"]

    def _get_models(self)-> Tuple[dict, dict]:
        return ({}, {})


    def predict(self, X):
        return NotImplementedError

    def _get_metrics(self):
        raise  NotImplementedError

    def _get_model(self, model):
        raise NotImplementedError

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, platform=None, authentication=None,
             **kwargs):
        """
        This generic function loads a previously saved transformation pipeline and model
        from the current active directory into the current python environment.
        Load object must be a pickle file.

        Parameters
        ----------


        Returns
        -------
        Model Object

        """

        function_params_str = ", ".join([f"{k}={v}" for k, v in locals().items()])

        logger = get_logger()

        logger.info("Initializing load_model()")
        logger.info(f"load_model({function_params_str})")

        # exception checking
        file_name = model_metadata.get("classifier_file", KOLIBRI_MODEL_FILE_NAME)
        if platform:
            if not authentication:
                raise ValueError("Authentication is missing.")

        if not platform:

            classifier_file = os.path.join(model_dir, file_name)

            if os.path.exists(classifier_file):
                model = joblib.load(classifier_file)
            else:
                return cls(model_metadata)
            return model

        # cloud providers
        elif platform == "aws":

            import boto3

            bucketname = authentication.get("bucket")

            if bucketname is None:
                logger.error(
                    "S3 bucket name missing. Provide `bucket` as part of authentication parameter"
                )
                raise ValueError(
                    "S3 bucket name missing. Provide `bucket` name as part of authentication parameter"
                )

            filename = f"{file_name}.pkl"

            if "path" in authentication:
                key = os.path.join(authentication.get("path"), filename)
            else:
                key = filename

            index = filename.rfind("/")
            s3 = boto3.resource("s3")

            if index == -1:
                s3.Bucket(bucketname).download_file(key, filename)
            else:
                path, key = filename[: index + 1], filename[index + 1:]
                if not os.path.exists(path):
                    os.makedirs(path)
                s3.Bucket(bucketname).download_file(key, filename)

            model = cls.load_model(filename, verbose=False)

            logger.info("Transformation Pipeline and Model Successfully Loaded")

            return model

        elif platform == "gcp":

            bucket_name = authentication.get("bucket")
            project_name = authentication.get("project")

            if bucket_name is None or project_name is None:
                logger.error(
                    "Project and Bucket name missing. Provide `bucket` and `project` as part of "
                    "authentication parameter"
                )
                raise ValueError(
                    "Project and Bucket name missing. Provide `bucket` and `project` as part of "
                    "authentication parameter"
                )

            filename = f"{file_name}.pkl"

            _download_blob_gcp(project_name, bucket_name, filename, filename)

            model = cls.load_model(filename, verbose=False)

            logger.info("Transformation Pipeline and Model Successfully Loaded")
            return model

        elif platform == "azure":

            container_name = authentication.get("container")

            if container_name is None:
                logger.error(
                    "Storage Container name missing. Provide `container` as part of authentication parameter"
                )
                raise ValueError(
                    "Storage Container name missing. Provide `container` as part of authentication parameter"
                )

            filename = f"{file_name}.pkl"

            _download_blob_azure(container_name, filename, filename)

            model = cls.load_model(filename, verbose=False)

            logger.info("Transformation Pipeline and Model Successfully Loaded")
            return model
        else:
            print(f"Platform {platform} is not supported by Kolibri or illegal option")
        gc.collect()

    def persist(self, model_dir):
        """Persist this model_type into the passed directory."""

        classifier_file = os.path.join(model_dir, KOLIBRI_MODEL_FILE_NAME)
        joblib.dump(self, classifier_file)

        logger.info(f"{self.name} saved in current working directory")
        logger.info(str(self))
        logger.info(
            "save_model() successfully completed......................................"
        )

        gc.collect()
        return {
            "classifier_file": KOLIBRI_MODEL_FILE_NAME,
            "performace_scores": self.performace_scores,
        }

    def plot(
            self,
            plot,
            verbose=True,
    ):

        function_params_str = ", ".join([f"{k}={v}" for k, v in locals().items()])

        logger.info("Initializing plot_model()")
        logger.info(f"plot_model({function_params_str})")

        logger.info("Checking exceptions")
        print("plotting " + plot)
        fit_kwargs = {}

        if plot not in self.all_plots:
            raise ValueError(
                f"Plot {plot} is not Available. Please see docstring for list of available Plots."
            )

        # multiclass plot exceptions:
        multiclass_not_available = ["threshold", "manifold", "rfe"]
        if self._is_multi_class:
            if plot in multiclass_not_available:
                logger.warning(
                    "Plot Not Available for multiclass problems. Please see docstring for list of available Plots."
                )
                return None

        # exception for CatBoost
        # if "CatBoostClassifier" in str(type(estimator)):
        #    raise ValueError(
        #    "CatBoost estimator is not compatible with plot_model function, try using Catboost with interpret_model instead."
        # )

        # checking for auc plot
        if not hasattr(self.model, "predict_proba") and plot == "auc":
            raise TypeError(
                "AUC plot not available for estimators with no predict_proba attribute."
            )

        # checking for calibration plot
        if not hasattr(self.model, "predict_proba") and plot == "calibration":
            raise TypeError(
                "Calibration plot not available for estimators with no predict_proba attribute."
            )

        def is_tree(e):
            from sklearn.ensemble._forest import BaseForest
            from sklearn.tree import BaseDecisionTree

            if "final_estimator" in e.get_params():
                e = e.final_estimator
            if "base_estimator" in e.get_params():
                e = e.base_estimator
            if isinstance(e, BaseForest) or isinstance(e, BaseDecisionTree):
                return True

        # checking for calibration plot
        if plot == "tree" and not is_tree(self.model):
            raise TypeError(
                "Decision Tree plot is only available for scikit-learn Decision Trees and Forests, Ensemble models using those or Stacked models using those as meta (final) estimators."
            )

        # checking for feature plot
        if not (
                hasattr(self.model, "coef_") or hasattr(self.model, "feature_importances_")
        ) and (plot == "feature" or plot == "feature_all" or plot == "rfe"):
            raise TypeError(
                "Feature Importance and RFE plots not available for estimators that doesnt support coef_ or feature_importances_ attribute."
            )

        """

        ERROR HANDLING ENDS HERE

        """

        if isnotebook():
            display = DefaultDisplay(verbose=verbose, html_param=True)

        plot_kwargs = {}

        logger.info("Preloading libraries")
        # pre-load libraries

        np.random.seed(self.get_parameter("seed"))

        estimator = deepcopy(self.model)
        model = estimator

        # plots used for logging (controlled through plots_log_param)
        # AUC, #Confusion Matrix and #Feature Importance

        logger.info("Copying training dataset")

        logger.info(f"Plot type: {plot}")


        try:
            if self.plotter:
                function = getattr(self.plotter, plot)
        except:
                logger.warning(plot + " Does not exist. Please check the spelling")
                return None
        # execute the plot method
        plt = function()

        gc.collect()

        logger.info(
            "plot_model() successfully completed......................................"
        )

        return plt

    def deploy(self, model_dir: str, authentication: dict, platform: str = "azure", prep_pipe_=None
               ):

        function_params_str = ", ".join([f"{k}={v}" for k, v in locals().items()])

        logger = get_logger()

        logger.info("Initializing deploy_model()")
        logger.info(f"deploy_model({function_params_str})")

        allowed_platforms = ["aws", "gcp", "azure"]

        if platform not in allowed_platforms:
            logger.error(
                f"(Value Error): Platform {platform} is not supported by Kolibri or illegal option"
            )
            raise ValueError(
                f"Platform {platform} is not supported by Kolibri or illegal option"
            )

        if platform:
            if not authentication:
                raise ValueError("Authentication is missing.")

        # general dependencies
        import os

        logger.info("Saving model in active working directory")
        logger.info("SubProcess save_model() called ==================================")
        self.persist(model_dir)
        logger.info("SubProcess save_model() end ==================================")

        if platform == "aws":

            logger.info("Platform : AWS S3")
            import boto3

            # initialize s3
            logger.info("Initializing S3 client")
            s3 = boto3.client("s3")
            filename = f"{KOLIBRI_MODEL_FILE_NAME}.pkl"
            if "path" in authentication:
                key = os.path.join(authentication.get("path"), f"{KOLIBRI_MODEL_FILE_NAME}.pkl")
            else:
                key = f"{KOLIBRI_MODEL_FILE_NAME}.pkl"
            bucket_name = authentication.get("bucket")

            if bucket_name is None:
                logger.error(
                    "S3 bucket name missing. Provide `bucket` as part of authentication parameter."
                )
                raise ValueError(
                    "S3 bucket name missing. Provide `bucket` name as part of authentication parameter."
                )

            import botocore.exceptions

            try:
                s3.upload_file(filename, bucket_name, key)
            except botocore.exceptions.NoCredentialsError:
                logger.error(
                    "Boto3 credentials not configured. Refer boto3 documentation "
                    "(https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)"
                )
                logger.error("Model deployment to AWS S3 failed.")
                raise ValueError(
                    "Boto3 credentials not configured. Refer boto3 documentation "
                    "(https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)"
                )
            os.remove(filename)
            print("Model Successfully Deployed on AWS S3")
            logger.info("Model Successfully Deployed on AWS S3")
            logger.info(str(self.model))

        elif platform == "gcp":

            logger.info("Platform : GCP")

            # initialize deployment
            filename = f"{KOLIBRI_MODEL_FILE_NAME}.pkl"
            key = f"{KOLIBRI_MODEL_FILE_NAME}.pkl"
            bucket_name = authentication.get("bucket")
            project_name = authentication.get("project")

            if bucket_name is None or project_name is None:
                logger.error(
                    "Project and Bucket name missing. Provide `bucket` and `project` as part of "
                    "authentication parameter"
                )
                raise ValueError(
                    "Project and Bucket name missing. Provide `bucket` and `project` as part of "
                    "authentication parameter"
                )

            try:
                google.create_bucket(project_name, bucket_name)
                google.upload_blob(project_name, bucket_name, filename, key)
            except Exception:
                google.upload_blob(project_name, bucket_name, filename, key)
            os.remove(filename)
            print("Model Successfully Deployed on GCP")
            logger.info("Model Successfully Deployed on GCP")
            logger.info(str(self.model))

        elif platform == "azure":

            logger.info("Platform : Azure Blob Storage")

            # initialize deployment
            filename = f"{KOLIBRI_MODEL_FILE_NAME}.pkl"
            key = f"{KOLIBRI_MODEL_FILE_NAME}.pkl"
            container_name = authentication.get("container")

            if container_name is None:
                logger.error(
                    "Storage Container name missing. Provide `container` as part of authentication parameter"
                )
                raise ValueError(
                    "Storage Container name missing. Provide `container` as part of authentication parameter"
                )

            try:
                azure.get_container(authentication, container_name)
                azure.upload_file_object(authentication, container_name, filename, key)
            except Exception:
                azure.upload_file_object(authentication, container_name, filename, key)

            os.remove(filename)

            print("Model Successfully Deployed on Azure Storage Blob")
            logger.info("Model Successfully Deployed on Azure Storage Blob")
            logger.info(str(self.model))

        logger.info(
            "deploy_model() successfully completed......................................"
        )
        gc.collect()


    def explain(self, cats=None, **kwargs):


        # soft dependencies check

        dashboard_kwargs =  {"shap_interaction":False, "nsamples":500, "whatif":True}
        run_kwargs = {"port":3051}

        from explainerdashboard import ExplainerDashboard, RegressionExplainer

        # Replaceing chars which dash doesnt accept for column name `.` , `{`, `}`
        X = pd.DataFrame(self.X)

        X.columns = self.feature_names
        explainer = RegressionExplainer(
            self.model, X, pd.Series(self.y_true),  cats=cats, **kwargs
        )
        db= ExplainerDashboard(
            explainer, **dashboard_kwargs
        )
        db.run(**run_kwargs)