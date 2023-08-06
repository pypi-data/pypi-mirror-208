from kolibri.evaluation.metrics.anomaly import get_all_metric_containers as get_all_anomaly_metric_containers
from kolibri.evaluation.metrics.base_metric import Metric
from kolibri.evaluation.metrics.metric_utils import make_scorer_with_error_score
from kolibri.evaluation.metrics.classification import get_all_metrics as get_all_classification_metrics
from kolibri.evaluation.metrics.regression import get_all_metrics as get_all_regression_metrics
from kolibri.config import TaskType


def get_metric(task_type, metric):
    if task_type in [TaskType.CLASSIFICATION, TaskType.MULTI_TARGET_CLASSIFICATION, TaskType.BINARY_CLASSIFICATION]:
        return get_all_classification_metrics()[metric]
    elif task_type in [TaskType.REGRESSION, TaskType.SCORING]:
        return get_all_regression_metrics()[metric]