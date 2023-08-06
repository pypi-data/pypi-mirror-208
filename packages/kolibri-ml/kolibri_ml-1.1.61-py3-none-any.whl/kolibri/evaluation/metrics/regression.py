
from typing import Any, Dict, Optional, Union
import inspect
import numpy as np
from sklearn import metrics
from sklearn.metrics._regression import _check_reg_targets
from sklearn.metrics._scorer import _BaseScorer
from sklearn.utils.validation import check_consistent_length
from kdmt.ml.metrics.regression import relative_absolute_error
import kolibri
from kolibri.evaluation.metrics.base_metric import Metric


class RegressionMetric(Metric):
    """
    Base regression metric container class, for easier definition of containers. Ensures consistent format
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
        The target of the score function. Only 'pred' is supported for regression.
    args : dict, default = {} (empty dict)
        The arguments to always pass to constructor when initializing score_func of class_def class.
    display_name : str, default = None
        Display name (shorter than name). Used in display dataframe header. If None or empty, will use name.
    greater_is_better: bool, default = True
        Whether score_func is a score function (default), meaning high is good,
        or a loss function, meaning low is good. In the latter case, the
        scorer object will sign-flip the outcome of the score_func.
    is_custom : bool, default = False
        Is the metric custom. Should be False for all metrics defined in kolibri.

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
    args : dict
        The arguments to always pass to constructor when initializing score_func of class_def class.
    display_name : str
        Display name (shorter than name). Used in display dataframe header.
    greater_is_better: bool
        Whether score_func is a score function (default), meaning high is good,
        or a loss function, meaning low is good. In the latter case, the
        scorer object will sign-flip the outcome of the score_func.
    is_custom : bool
        Is the metric custom. Should be False for all metrics defined in kolibri.

    """

    def __init__(
        self,
        id: str,
        name: str,
        score_func: Union[float, Any],
        scorer: Optional[Union[str, _BaseScorer]] = None,
        target: str = "pred",
        args: Dict[str, Any] = None,
        display_name: Optional[str] = None,
        greater_is_better: bool = True,
        is_custom: bool = False,
    ) -> None:

        allowed_targets = ["pred"]
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
            "Custom": self.is_custom,
        }

        return d


class MAEMetric(RegressionMetric):
    def __init__(self) -> None:
        super().__init__(
            id="mae",
            name="MAE",
            score_func=metrics.mean_absolute_error,
            greater_is_better=False,
            scorer="neg_mean_absolute_error",
        )


class MSEMetric(RegressionMetric):
    def __init__(self) -> None:
        super().__init__(
            id="mse",
            name="MSE",
            score_func=metrics.mean_squared_error,
            greater_is_better=False,
            scorer="neg_mean_squared_error",
        )


class RMSEMetric(RegressionMetric):
    def __init__(self) -> None:

        super().__init__(
            id="rmse",
            name="RMSE",
            score_func=metrics.mean_squared_error,
            greater_is_better=False,
            args={"squared": False},
            scorer="neg_root_mean_squared_error",
        )

class RAEMetric(RegressionMetric):
    def __init__(self) -> None:

        super().__init__(
            id="rae",
            name="RAE",
            score_func=relative_absolute_error,
            greater_is_better=False,
            args={"squared": False},
            scorer=kolibri.evaluation.metrics.make_scorer_with_error_score(
                relative_absolute_error, error_score=0.0, greater_is_better=False
            ),
        )

class R2Metric(RegressionMetric):
    def __init__(self) -> None:

        super().__init__(
            id="r2",
            name="R2",
            score_func=metrics.r2_score,
            greater_is_better=True,
            scorer="r2",
        )


class RMSLEMetric(RegressionMetric):
    def __init__(self) -> None:
        def root_mean_squared_log_error(
            y_true, y_pred, *, sample_weight=None, multioutput="uniform_average"
        ):
            return np.sqrt(
                metrics.mean_squared_log_error(
                    np.abs(y_true),
                    np.abs(y_pred),
                    sample_weight=sample_weight,
                    multioutput=multioutput,
                )
            )

        super().__init__(
            id="rmsle",
            name="RMSLE",
            score_func=root_mean_squared_log_error,
            scorer=kolibri.evaluation.metrics.make_scorer_with_error_score(
                root_mean_squared_log_error, error_score=0.0, greater_is_better=False
            ),
            greater_is_better=False,
        )


class MAPEMetric(RegressionMetric):
    def __init__(self) -> None:
        def mean_absolute_percentage_error(
            y_true, y_pred, sample_weight=None, multioutput="uniform_average"
        ):
            y_type, y_true, y_pred, multioutput = _check_reg_targets(
                y_true, y_pred, multioutput
            )
            check_consistent_length(y_true, y_pred, sample_weight)
            mask = y_true != 0
            y_true = y_true[mask]
            y_pred = y_pred[mask]
            mape = np.abs(y_pred - y_true) / np.abs(y_true)
            output_errors = np.average(mape, weights=sample_weight, axis=0)
            if isinstance(multioutput, str):
                if multioutput == "raw_values":
                    return output_errors
                elif multioutput == "uniform_average":
                    # pass None as weights to np.average: uniform mean
                    multioutput = None

            return np.average(output_errors, weights=multioutput)

        super().__init__(
            id="mape",
            name="MAPE",
            score_func=mean_absolute_percentage_error,
            greater_is_better=False,
        )


def get_all_metrics():
    metrics=   [
        obj
        for _, obj in globals().items() if inspect.isclass(obj)
        and  RegressionMetric in tuple(x for x in inspect.getmro(obj) if x != obj)
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



if __name__ == "__main__":
    mae=MAEMetric()
    true_y=[1.2, 1.3, 1.4]
    pred_y=[0.9, 1.1, 1.0]
    print(mae.score_func(true_y, pred_y))