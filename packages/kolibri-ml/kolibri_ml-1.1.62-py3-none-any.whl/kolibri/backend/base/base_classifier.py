import gc

import numpy as np
import pandas as pd

from kolibri.backend.base.base_estimator import BaseEstimator
from kolibri.visualizations.classification_plots import ClassificationPlots

try:
    from kolibri.explainers.shap_explainer import PlotSHAP
    from kolibri.evaluation.classifier_evaluator import ClassifierEvaluator
except:
    pass
from sklearn.metrics import confusion_matrix, classification_report
from kolibri.config import TaskType
from kolibri.config import ParamType
from sklearn.calibration import CalibratedClassifierCV
from kolibri.logger import get_logger
from kolibri import default_configs as settings
import time
import datetime
from sklearn.model_selection import StratifiedKFold
from kdmt.df import color_df
from kolibri.evaluation.metrics import classification
from kolibri.indexers.label_indexer import LabelIndexer
logger = get_logger(__name__)
from kolibri.output import DefaultDisplay

KOLIBRI_MODEL_FILE_NAME = "classifier_kolibri.pkl"



class BaseClassifier(BaseEstimator):
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
                "sampler": None,
                "priors-thresolding": False,
                'calibrate-model':False,
                'calibration-method': "isotonic",
                "optimize-metric": "Accuracy"
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
        if indexer is not None:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=False)
        self.sampler=None

        self.X_sampled = None
        self.y_sampled = None

        if self.get_parameter('sampler'):
            from kolibri.samplers import get_sampler
            self.sampler = get_sampler(self.get_parameter('sampler'))
        if 'model' in params:
            self._setup_model(params['model'])
        elif 'model' in params["tunable"]:
            self._setup_model(params["tunable"]['model'])

        self.class_priors = None
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

    def fit(self, data_X = None, data_y = None, X_val=None, y_val=None):
        self._is_multi_class=len(set(data_y))>2

        runtime_start = time.time()
        full_name = type(self.model).__name__

#        self.display.move_progress()

        """
        MONITOR UPDATE STARTS
        """

        model_fit_time, performace_scores, avg_results, predictions = self._create_and_evaluate_model(data_X, data_y)

        if predictions != []:
            if len(predictions.shape)>1 and predictions.shape[1] > 1:
                predictions = np.column_stack((self.indexer.inverse_transform(np.argmax(predictions, axis=1)) ,predictions))
            elif len(predictions.shape)==1 or predictions.shape[1] == 1:
                if self.indexer is not None:
                    predictions = self.indexer.inverse_transform(predictions)
        # dashboard logging
        indices = "Mean"

#        self.display.move_progress()

        logger.info("Uploading results into container")


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

        self.y_true=data_y
        self.X=data_X
        predictions=np.array(predictions)
        if predictions.size>0 and len(predictions.shape)==1:
            self.y_pred=predictions
        else:
            self.y_pred= [] if predictions.size==0 else predictions[:,1:,].astype(np.float16)
        if self.get_parameter("evaluate-performance")==True:
            self.plotter = ClassificationPlots(y_true=self.y_true, y_pred=self.y_pred, labels_dict=self.indexer.idx2token, X=self.X, y=self.y_true, classifier=self.model)
            self.performace_scores=performace_scores.loc[['Mean', 'Std']].to_dict()
    #        self.performace_scores['Confusion_matrix']=confusion_matrix(self.y_true,np.argmax(self.y_pred, axis=1))
            self.performace_scores['Confusion_matrix']=ClassifierEvaluator.confusion_matrix(list(self.y_true), list(np.argmax(self.y_pred, axis=1)), list(self.indexer.idx2token.values())).to_dict()
            self.performace_scores['Class_report']=classification_report(self.y_true, np.argmax(self.y_pred, axis=1), target_names=list(self.indexer.idx2token.values()))

        return performace_scores, runtime, model_fit_time, predictions

    def _get_models(self):
        from kolibri.backend.models import sklearn_classification_models
        return sklearn_classification_models

    def _get_model(self, model):
        from kolibri.backend.models import get_model
        return get_model(model, task_type = TaskType.CLASSIFICATION)


    def _get_metrics(self):
        return classification.get_all_metrics()


    def compute_priors(self, y):
        unique, counts = np.unique(y, return_counts=True)
        self.class_priors = dict(zip(unique, counts))

        total = sum(self.class_priors.values(), 0.0)
        self.class_priors = {k: v / total for k, v in self.class_priors.items()}

    def _predict_proba(self, X):
        """Given a bow vector of an input text, predict the class label.

        Return probabilities for all y_values.

        :param X: bow of input text
        :return: vector of probabilities containing one entry for each label"""
        raw_predictions=None
        try:
            if self.get_parameter('task-type') == TaskType.BINARY_CLASSIFICATION:
                raw_predictions=self.model.predict_proba(X)[:, 1]
            elif self.get_parameter('task-type') == TaskType.CLASSIFICATION:
                raw_predictions=self.model.predict_proba(X)
        except:
            raise Exception('Predict_proba raised an error in Estimator')


        if self.get_parameter("priors-thresolding"):
            if not raw_predictions is None:
                try:
                    priors = np.array([v for v in self.class_priors.values()])
                    raw_predictions = (raw_predictions.T - priors[:, None]) / priors[:, None]
                    raw_predictions = np.argmax(raw_predictions.T, axis=1)
                except Exception as e:
                    print(e)

        # sort the probabilities retrieving the indices of
        # the elements in sorted order
        sorted_indices = np.fliplr(np.argsort(raw_predictions, axis=1))

        return raw_predictions, sorted_indices, [p[sorted_indices[i]] for i, p in enumerate(raw_predictions)]

    def predict_proba(self, X):
        return self.model.predict_proba(X)
    def predict(self, X):
        """Given a bow vector of an input text, predict most probable label.

        Return only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second,
                 its probability."""
        probabilities=[]
        try:
            raw_predictions, class_ids, probabilities=self._predict_proba(X)
        except:
            class_ids=self.model.predict(X)

        classes = [self.indexer.inverse_transform(np.ravel(class_id)) for class_id in class_ids]

        return self.process([list(zip(classe, probability)) for classe, probability in zip(classes, probabilities)])

    def process(self, results):

        if results is not None:
            ranking= [result[:settings.TARGET_RANKING_LENGTH] for result in results]

            target = [{"name": result[0][0], "confidence": result[0][1]} for result in results]

            target_ranking = [[{"name":r[0], "confidence":r[1]} for r in rank] for rank in ranking]
        else:
            target = {"name": None, "confidence": 0.0}
            target_ranking = []

        response=[{
            "label": target[i],
            "ranking": target_ranking[i]
        } for i in range(0, len(target))]
        return response
    def explain(self, **kwargs):


        # soft dependencies check

        dashboard_kwargs =  {"shap_interaction":False, "nsamples":500, "whatif":False}
        run_kwargs = {"port":3050}

        from explainerdashboard import ExplainerDashboard, RegressionExplainer

        # Replaceing chars which dash doesnt accept for column name `.` , `{`, `}`
        X = pd.DataFrame(self.X)

        X.columns = self.feature_names
        explainer = RegressionExplainer(
            self.model, X, pd.Series(self.y_true), **kwargs
        )
        db= ExplainerDashboard(
            explainer, **dashboard_kwargs
        )
        db.run(**run_kwargs)

if __name__=="__main__":
    import joblib
    cl=BaseClassifier({"model": 'LogisticRegression'})
    joblib.dump(cl, './test.pkl')