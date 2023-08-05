
from typing import Any, Dict, Optional, Union
import kolibri
from sklearn import metrics
from sklearn.metrics._scorer import _BaseScorer
import inspect
from kolibri.evaluation.metrics.base_metric import Metric
from kolibri.evaluation.metrics.metric_utils import make_scorer_with_error_score

class ClassificationMetric(Metric):
    """
    Base classification metric container class, for easier definition of containers. Ensures consistent format
    before being turned into a dataframe row.

    Parameters
    ----------
    id : str
        ID used as index.
    name : str
        Full name.
    score_func : type
        The callable used for the score function, eg. sklearn.metrics.accuracy_score.
    scorer : str or callable, default = None
        The scorer passed to models. Can be a string representing a built-in sklearn scorer,
        a sklearn Scorer object, or None, in which case a Scorer object will be created from
        score_func and args.
    target : str, default = 'pred'
        The target of the score function.
        - 'pred' for the prediction table
        - 'pred_proba' for pred_proba
        - 'threshold' for decision_function or predict_proba
    args : dict, default = {} (empty dict)
        The arguments to always pass to constructor when initializing score_func of class_def class.
    display_name : str, default = None
        Display name (shorter than name). Used in display dataframe header. If None or empty, will use name.
    greater_is_better: bool, default = True
        Whether score_func is a score function (default), meaning high is good,
        or a loss function, meaning low is good. In the latter case, the
        scorer object will sign-flip the outcome of the score_func.
    is_multiclass : bool,  default = True
        Can the metric be used for multiclass problems.
    is_custom : bool, default = False
        Is the metric custom. Should be False for all metrics defined in PyCaret.

    Attributes
    ----------
    id : str
        ID used as index.
    name : str
        Full name.
    score_func : type
        The callable used for the score function, eg. metrics.accuracy_score.
    scorer : str or callable
        The scorer passed to models. Can be a string representing a built-in sklearn scorer,
        a sklearn Scorer object, or None, in which case a Scorer object will be created from
        score_func and args.
    target : str
        The target of the score function.
        - 'pred' for the prediction table
        - 'pred_proba' for pred_proba
        - 'threshold' for decision_function or predict_proba
    args : dict
        The arguments to always pass to constructor when initializing score_func of class_def class.
    display_name : str
        Display name (shorter than name). Used in display dataframe header.
    greater_is_better: bool
        Whether score_func is a score function (default), meaning high is good,
        or a loss function, meaning low is good. In the latter case, the
        scorer object will sign-flip the outcome of the score_func.
    is_multiclass : bool
        Can the metric be used for multiclass problems.
    is_custom : bool
        Is the metric custom. Should be False for all metrics defined in PyCaret.

    """

    def __init__(
        self,
        id: str,
        name: str,
        score_func: type,
        scorer: Optional[Union[str, _BaseScorer]] = None,
        target: str = "pred",
        args: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
        greater_is_better: bool = True,
        is_multiclass: bool = True,
        is_custom: bool = False,
    ) -> None:

        allowed_targets = ["pred", "pred_proba", "threshold"]
        if target not in allowed_targets:
            raise ValueError(f"Target must be one of {', '.join(allowed_targets)}.")

        if not args:
            args = {}
        if not isinstance(args, dict):
            raise TypeError("args needs to be a dictionary.")

        scorer = (
            scorer
            if scorer
            else kolibri.evaluation.metrics.make_scorer_with_error_score(
                score_func,
                needs_proba=target == "pred_proba",
                needs_threshold=target == "threshold",
                greater_is_better=greater_is_better,
                error_score=0.0,
                **args,
            )
        )

        super().__init__(
            id=id,
            name=name,
            score_func=score_func,
            scorer=scorer,
            args=args,
            display_name=display_name,
            greater_is_better=greater_is_better,
            is_custom=is_custom,
        )

        self.target = target
        self.is_multiclass = is_multiclass

    def get_dict(self, internal: bool = True) -> Dict[str, Any]:
        """
        Returns a dictionary of the model properties, to
        be turned into a pandas DataFrame row.

        Parameters
        ----------
        internal : bool, default = True
            If True, will return all properties. If False, will only
            return properties intended for the user to see.

        Returns
        -------
        dict of str : Any

        """
        d = {
            "ID": self.id,
            "Name": self.name,
            "Display Name": self.display_name,
            "Score Function": self.score_func,
            "Scorer": self.scorer,
            "Target": self.target,
            "Args": self.args,
            "Greater is Better": self.greater_is_better,
            "Multiclass": self.is_multiclass,
            "Custom": self.is_custom,
        }

        return d


def _get_pos_label_arg(le):
    if le:
        return {"pos_label": list(le.token2idx.keys())[-1], "labels":  list(le.token2idx.keys())}
    return {}


class AccuracyMetric(ClassificationMetric):
    def __init__(self) -> None:
        super().__init__(
            id="acc",
            name="Accuracy",
            score_func=metrics.accuracy_score,
            scorer="accuracy",
        )


class ROCAUCMetric(ClassificationMetric):
    def __init__(self) -> None:
        args = {"average": "weighted", "multi_class": "ovr"}
        super().__init__(
            id="auc",
            name="AUC",
            score_func=metrics.roc_auc_score,
            scorer=make_scorer_with_error_score(
                metrics.roc_auc_score, needs_proba=True, error_score=0.0, **args
            ),
            target="pred_proba",
            args=args,
        )


class RecallMetric(ClassificationMetric):
    def __init__(self) -> None:
        args = {"average": "weighted"}
        super().__init__(
            id="recall",
            name="Recall",
            score_func=kolibri.evaluation.metrics.metric_utils.BinaryMulticlassScoreFunc(
                metrics.recall_score
            ),
            scorer=metrics.make_scorer(
                kolibri.evaluation.metrics.metric_utils.BinaryMulticlassScoreFunc(
                    metrics.recall_score
                ),
                **args,
            ),
            args=args,
        )


class PrecisionMetric(ClassificationMetric):
    def __init__(self) -> None:
        args = {"average": "weighted"}
        super().__init__(
            id="precision",
            name="Precision",
            display_name="Prec.",
            score_func=kolibri.evaluation.metrics.metric_utils.BinaryMulticlassScoreFunc(
                metrics.precision_score
            ),
            scorer=metrics.make_scorer(
                kolibri.evaluation.metrics.metric_utils.BinaryMulticlassScoreFunc(
                    metrics.precision_score
                ),
                **args,
            ),
            args=args,
        )


class F1Metric(ClassificationMetric):
    def __init__(self) -> None:
        args = {"average": "weighted"}
        super().__init__(
            id="f1",
            name="F1",
            score_func=kolibri.evaluation.metrics.metric_utils.BinaryMulticlassScoreFunc(
                metrics.f1_score
            ),
            scorer=metrics.make_scorer(
                kolibri.evaluation.metrics.metric_utils.BinaryMulticlassScoreFunc(metrics.f1_score),
                **args,
            ),
            args=args,
        )


class KappaMetric(ClassificationMetric):
    def __init__(self) -> None:
        super().__init__(
            id="kappa",
            name="Kappa",
            score_func=metrics.cohen_kappa_score,
            scorer=metrics.make_scorer(metrics.cohen_kappa_score),
        )


class MCCMetric(ClassificationMetric):
    def __init__(self) -> None:
        super().__init__(
            id="mcc",
            name="MCC",
            score_func=metrics.matthews_corrcoef,
            scorer=metrics.make_scorer(metrics.matthews_corrcoef),
        )


def get_all_metrics():
    metrics=  [
        obj
        for _, obj in globals().items() if inspect.isclass(obj)
        and  ClassificationMetric in tuple(x for x in inspect.getmro(obj) if x != obj)
    ]

    metrics_containers = []

    for obj in metrics:
        try:
            if hasattr(obj, "active") and not obj.active:
                continue
            instance = obj()
            if instance.active:
                metrics_containers.append(instance)
        except Exception as e:
            print(e)
            pass

    return {metric.id: metric for metric in metrics_containers}
