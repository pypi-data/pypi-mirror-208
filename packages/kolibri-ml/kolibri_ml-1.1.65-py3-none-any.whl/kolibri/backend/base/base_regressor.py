import gc

import numpy as np

import pandas as pd
from kolibri.backend.base.base_estimator import BaseEstimator
from kolibri.visualizations.regression_plots import RegressionPlots
try:
    from kolibri.explainers.shap_explainer import PlotSHAP
except:
    pass

from kolibri.config import TaskType
from kolibri.config import ParamType
from sklearn.utils.multiclass import type_of_target
from kolibri.logger import get_logger
import time
from kdmt.df import color_df

from kolibri.evaluation.metrics import regression

logger = get_logger(__name__)

KOLIBRI_MODEL_FILE_NAME = "classifier_kolibri.pkl"



class BaseRegressor(BaseEstimator):
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
                "target": None,
                "opt-metric-name": "mean_squared_error",
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
        self._is_multi_class=False
        if 'model' in params:
            self._setup_model(params['model'])
        elif 'model' in params["tunable"]:
            self._setup_model(params["tunable"]['model'])
        self.all_plots = {
            "pipeline": "Pipeline Plot",
            "parameter": "Hyperparameters",
            "residuals": "Residuals",
            "errors": "Prediction Error",
            "cooks": "Cooks Distance",
            "rfe": "Feature Selection",
            "learning": "Learning Curve",
            "tsne": "Manifold Learning",
            "validation": "Validation Curve",
            "feature": "Feature Importance",
            "feature_all": "Feature Importance (All)",
            "tree": "Decision Tree"
        }
        from sklearn.model_selection import KFold

        fold_shuffle_param = self.get_parameter("fold-shuffle")
        fold_param = self.get_parameter("n-folds")
        fold_seed = self.get_parameter("random-state") if fold_shuffle_param else None
        self.fold_generator = KFold(
                    fold_param, random_state=fold_seed, shuffle=fold_shuffle_param
                )


    def _get_models(self):
        from kolibri.backend.models import sklearn_regression_models
        return sklearn_regression_models



    def _get_model(self, model):
        from kolibri.backend.models import get_model
        return get_model(model, task_type = TaskType.REGRESSION)


    def _get_metrics(self):
        return regression.get_all_metrics()


    def fit(self, data_X = None, data_y = None, X_val=None, y_val=None):

        """
        Internal version of ``create_model`` with private arguments.
        """

        logger.info("Checking exceptions")

        target_type = type_of_target(data_y)
        supported_types = ['binary', 'multiclass', 'multilabel-indicator', 'continuous']
        if target_type not in supported_types:
            raise ValueError("Classification with data of type {} is "
                             "not supported. Supported types are {}. "
                             "".format(
                                    target_type,
                                    supported_types
                                )
                             )
        # run_time
        runtime_start = time.time()


#        self.display.move_progress()

        logger.info("Defining folds")


        logger.info("Declaring metric variables")

        """
        MONITOR UPDATE STARTS
        """
        self.display.update_monitor(1, "Selecting Estimator")
        """
        MONITOR UPDATE ENDS
        """

        logger.info("Importing untrained model")


        full_name = type(self.model).__name__

#        self.display.update_monitor(2, full_name)

#        self.display.move_progress()

        """
        MONITOR UPDATE STARTS
        """


        model_fit_time, performace_scores, avg_results, predictions = self._create_and_evaluate_model(data_X, data_y)

        # dashboard logging
        indices = "Mean"

#        self.display.move_progress()


        if performace_scores is not None:
            # yellow the mean
            model_results_ = color_df(performace_scores, "yellow", indices, axis=1)
            model_results_ = model_results_.format(precision=self.get_parameter("round"))
            self.display.display(model_results_)

        # end runtime
        runtime_end = time.time()
        runtime = np.array(runtime_end - runtime_start).round(self.get_parameter("round"))




        logger.info(str(self.model))
        logger.info(
            "create_model() successfully completed......................................"
        )
        gc.collect()
#        self.display.close()
#        self.display=None

        if predictions is not None:
            self.y_true=data_y
            self.X=data_X
            if predictions!=[]  and len(predictions.shape)==1:
                self.y_pred=predictions
            else:
                self.y_pred= [] if predictions==[]  else predictions[:,1:,].astype(np.float16)

            self.plotter =  RegressionPlots(y_true=self.y_true, y_pred=self.y_pred, model_name=str(self.model), X=self.X,
                                        y=self.y_true, estimator=self.model,
                                        features_names=self.feature_names)

        if performace_scores is not None:
            self.performace_scores=performace_scores.loc[['Mean', 'Std']].to_dict()
        else:
            self.performace_scores="Performance not evaluated"
        return performace_scores, runtime, model_fit_time, predictions

    def predict(self, X_test):

        preds=self.model.predict(X_test)

        return preds

