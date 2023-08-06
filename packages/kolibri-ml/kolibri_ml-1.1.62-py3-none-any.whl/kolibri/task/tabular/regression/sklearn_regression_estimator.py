import copy

import joblib
import pandas as pd

from kolibri.backend.base.base_regressor import BaseRegressor
from kdmt.dict import update

try:
    from kolibri.optimizers.optuna.objective import EstimatorObjective
except:
    pass

from kolibri.logger import get_logger

logger = get_logger(__name__)
from kolibri.config import TaskType

class RegSklearnEstimator(BaseRegressor):
    defaults = {"fixed": {
        "default-params": None,
        "task-type": TaskType.REGRESSION
    },

        "tunable": {
        }
    }

    def __init__(self, hyperparameters=None, model=None, indexer=None):
        """Construct a new class classifier using the sklearn framework."""
        from kolibri.backend.models import get_model
        super(RegSklearnEstimator, self).__init__(params=hyperparameters, model=model, indexer=indexer)
        self.update_model_parameters()
        self.logger = logger


    def update_default_hyper_parameters(self):
        self.defaults = update(self.defaults, RegSklearnEstimator.defaults)
        super().update_default_hyper_parameters()

    def fit(self, X, y, X_val=None, y_val=None):

        if isinstance(X,pd.DataFrame):
            if self.get_parameter("target") in X.columns:
                X=X.drop(self.get_parameter("target"), axis=1)

            self.feature_names=X.columns

#            X=X.to_numpy()

        model_results = super(RegSklearnEstimator, self).fit(X, y)

        return model_results

    def copy(self):
        return copy.deepcopy(self)


    def is_fitted(self):
        return (
                hasattr(self.model, "n_features_")
                and self.model.n_features_ is not None
                and self.model.n_features_ > 0
        )

    def objective(self, X, y):
        objective = EstimatorObjective(X, y, self, None, eval_metric=self.get_parameter('opt-metric-name'), n_jobs=-1,
                                       random_state=42, direction='minimize')
        return objective


from kolibri.registry import ModulesRegistry

ModulesRegistry.add_module(RegSklearnEstimator.name, RegSklearnEstimator)
