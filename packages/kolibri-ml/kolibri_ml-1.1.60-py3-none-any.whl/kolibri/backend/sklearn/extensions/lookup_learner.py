import logging

import numpy
import numpy
import pandas as pd
try:
    from catboost import CatBoostRegressor, Pool
except:
    pass

from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from tqdm import tqdm
from sklearn.linear_model import RANSACRegressor
from kolibri.automl.data_inspection import get_data_info
from kolibri.config import TaskType
from kolibri.distances.heom import HEOM
from kolibri.preprocess.tabular import AutoInferDatatype, NearZeroVariance, Multicollinearity, DummyConverter, \
    CategoryEncoder, FeaturesInteractions

from kolibri.logger import get_logger

logger=get_logger(__name__)
class LazyLookupRegression(BaseEstimator, RegressorMixin):
    """
    Fits a linear regression, on sub sample of size n. The sample formed by the top n similar items to the
    sample to be predicted
    """


    def __init__(self, lookup_keys=[], n_neighbors:int=2, algorithm='auto',  distance='heom', leaf_size:int=10, num_runs=20,
                 num_features_dist_importance=1,posterior_sampling=True, handle_outliers=True, return_db_value_if_input_maches=False,
                 objective='RMSE', rsm=0.5, depth=6, boosting_type='Ordered',bootstrap_type='Bayesian', bagging_temperature=1,
                 learning_rate=0.03, l2_leaf_reg=3.0, iterations=100, verbose=False, linear_model=False):
        "constructor"
        RegressorMixin.__init__(self)
        BaseEstimator.__init__(self)
        self.lookup_keys=lookup_keys
        self.objective=objective
        self.handle_outliers=handle_outliers
        self.return_db_value_if_input_maches=return_db_value_if_input_maches
        self.rsm=rsm
        self.verbose=verbose
        self.depth=depth
        self.boosting_type=boosting_type
        self.bootstrap_type=bootstrap_type
        self.bagging_temperature=bagging_temperature
        self.iterations=iterations
        self.learning_rate=learning_rate
        self.l2_leaf_reg=l2_leaf_reg
        self.posterior_sampling=posterior_sampling
        self.linear_model=linear_model
        self.num_runs = num_runs

        if self.linear_model:
            if self.handle_outliers:
                self.estimator = RANSACRegressor(max_trials=2000)
            else:
                self.estimator=LinearRegression(fit_intercept=False)
        else:
            self.estimator=CatBoostRegressor(learning_rate=self.learning_rate, l2_leaf_reg=self.l2_leaf_reg, iterations=self.iterations, posterior_sampling=self.posterior_sampling, objective=self.objective, rsm=self.rsm, depth=self.depth, bootstrap_type=self.bootstrap_type, bagging_temperature=self.bagging_temperature, verbose=False)
        logger.log(logging.INFO, "Estimator: "+str(self.estimator))
        self.algorithm=algorithm
        self.leaf_size=leaf_size
        self.n_neighbors=n_neighbors
        self.neigberhood=NearestNeighbors(n_neighbors=n_neighbors, algorithm=algorithm, leaf_size=leaf_size, n_jobs=-1)

        self.encoder=None
        self.distance=distance

        self.num_features_dist_importance=num_features_dist_importance

    def get_distance_metric(self, X):
        #create a mixed datatype distance measure
        if self.distance=='heom':
            distance_metric = HEOM(X, cat_ix=self.categorical_ix, encode_categories=False, nan_equivalents = [12345], num_features_dist_importance=self.num_features_dist_importance).get_distance_fast

        elif self.distance=='vdm':
            distance_metric = HEOM(X, cat_ix=self.categorical_ix, encode_categories=False).get_distance
        else:
            raise Exception("Unknow distance measure. Expected 'heom', 'hvdm' or 'vdm' got :"+ self.distance)
        if not isinstance(X, numpy.ndarray):
            if hasattr(X, 'values'):
                X = X.values
        if not isinstance(X, numpy.ndarray):
            raise TypeError("'X' must be an array.")


        return distance_metric
    def fit(self, X, y):
        """
        Builds the tree model.
        :param X: numpy array or sparse matrix of shape [n_samples,n_features]
            Training data
        :param y: numpy array of shape [n_samples, n_targets]
            Target values. Will be cast to X's dtype if necessary
        :param sample_weight: numpy array of shape [n_samples]
            Individual weights for each sample
        :return: self : returns an instance of self.
        Fitted attributes:
        * `classes_`: classes
        * `tree_`: tree structure, see @see cl _DecisionTreeLogisticRegressionNode
        * `n_nodes_`: number of nodes
        """

        self.features=X.columns.values
        logger.log(logging.INFO, "Features: "+str(self.features))

        self.categorical_features = list(X.select_dtypes(include=['category', 'object', 'string']))
        logger.log(logging.INFO, "Categorical Features: "+str(self.categorical_features))

        self.numerical_features = [feat for feat in self.features if feat not in self.categorical_features]
        logger.log(logging.INFO, "Numerical Features: "+str(self.numerical_features))

        #create and fit category encoders
        self.encoder = CategoryEncoder(params={})
        self.X=self.encoder.fit_transform(X)
        self.X['__target__']=y
        self.groups = self.X.groupby(self.lookup_keys)
        logger.log(logging.INFO, "Lookup keys: "+str(self.lookup_keys))

        self.models={}
        for name, group in self.groups:
            self.models[tuple(name)]=group.drop(columns=self.lookup_keys)

        logger.log(logging.INFO, "Nb models: "+str(len(self.models)))

        X_groups=self.X[self.lookup_keys].drop_duplicates().reset_index(drop=True)
        #get column info to detect categorical columns
        data_info=get_data_info(X_groups)
        self.categorical_ix = [c["id"] for c in data_info["categorical_columns"]]
        self.numerical_ix=[c["id"] for c in data_info["numerical_columns"]]

        logger.log(logging.INFO, "data_info: "+str(data_info))

        self.neigberhood.metric=self.get_distance_metric(X_groups)

        self.neigberhood.fit(X_groups , None)
        index_columns=list(self.X.columns.values)
        index_columns.remove('__target__')
        self.X.set_index(index_columns, inplace=True)
        return self

    def predict(self, X):
        """
        Runs the predictions.
        """

        X2=self.encoder.transform(X)
        for x in X2:
            for i in numpy.argwhere(pd.isnull(x)):
                x[i]=12345

        return [self._predict_one([x]) for i, x in tqdm(X2.iterrows())]



    def search_dataset(self, row_serie):

        if tuple(row_serie[0]) in self.X.index:
            res=self.X.loc[self.X.index==tuple(row_serie[0])]
            return res['__target__'].values.mean()
        return None


    def _predict_one(self, X):
        """Predict the target for the provided data.
        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_queries, n_features), \
                or (n_queries, n_indexed) if metric == 'precomputed'
            Test samples.
        Returns
        -------
        y : ndarray of shape (n_queries,) or (n_queries, n_outputs), dtype=int
            Target values.
        """

        #lazy: search first if an exact instance is in the dataset
        y_pred=None

        if self.return_db_value_if_input_maches:
            y_pred= self.search_dataset(X)

        if y_pred is not None:
            return y_pred

        #no instance is found continue with the algorithm
        estimator = clone(self.estimator)

        model_key=tuple(X[0][self.lookup_keys].values)
        y_pred=None
        to_pred = X[0][[x for x in X[0].index if x not in self.lookup_keys]]
        logger.debug("model_key: "+str(self.lookup_keys))
        if model_key not in self.models:
            logger.debug("model_key not in models: " + str(model_key))
            neigh_ind = self.neigberhood.kneighbors(numpy.array(model_key).reshape(1, -1), return_distance=False)
            model_key=tuple(self.neigberhood._fit_X[neigh_ind.ravel()][0])

        if isinstance(self.models[model_key], pd.DataFrame):
            logger.debug("Building model with key: " + str(to_pred))

            self.models[model_key]=self._fit_linear_model(self.models[model_key].drop(columns=['__target__']), self.models[model_key]['__target__'], estimator)
        if self.models[model_key] is not None:
            logger.debug("model with key already built: " + str(to_pred))
            y_pred= self.models[model_key].predict(to_pred.to_frame().transpose())


        y_pred = y_pred.ravel()
        logger.debug("prediction: "+str(y_pred[0]))
        return y_pred[0]
    def _fit_linear_model(self, X_train, y_train, estimator):

        logger.debug("X_train: " + str(X_train))
        logger.debug("y_train: " + str(y_train))

        infer_type=AutoInferDatatype(config={"categorical-features":self.categorical_features, "numerical-features": self.numerical_features})
        zero=NearZeroVariance(configs={})
        colinear=Multicollinearity(configs={"colinearity-threshold": 0.7, "correlation-with-target-threshold": 0.2})
        interact=FeaturesInteractions({"task-type": TaskType.REGRESSION})
        regressor = Pipeline(
            steps=[("infer_type", infer_type), ("dummy",DummyConverter(config={})),("interact", interact), ("zero_var", zero),("colinear", colinear), ("regressor", estimator)]
        )

        coefs = []
        intercepts=[]
        for _ in range(self.num_runs):
            estimator = clone(self.estimator)
            regressor = Pipeline(
                steps=[("infer_type", infer_type), ("dummy", DummyConverter(config={})), ("zero_var", zero),
                       ("colinear", colinear), ("regressor", estimator)]
            )

            regressor.fit(X_train, y_train)
            coefs.append(regressor['regressor'].estimator_.coef_)
            intercepts.append(regressor['regressor'].estimator_.intercept_)

        avg_coefs = numpy.mean(coefs, axis=0)
        avg_intercepts = numpy.mean(intercepts, axis=0)

        regressor['regressor'].estimator_.intercept_=avg_intercepts
        regressor['regressor'].estimator_.coef_=avg_coefs

        logger.debug("estimator_intercept: "+ str(regressor['regressor'].estimator_.intercept_))
        logger.debug("estimator_coef: "+ str(regressor['regressor'].estimator_.coef_))
        return regressor

    def _predict_local_model(self, X_test, estimator, important_features=None):

        X_test_df = pd.DataFrame(X_test)

        if important_features is None:
            X_test_df.columns = self.features
        else:
            X_test_df.columns=self.features[important_features]

        for col in self.categorical_features:
            if col in X_test_df.columns:
                X_test_df[col]=X_test_df[col].astype('string')

        if not self.linear_model:
            pool_test = Pool(data=X_test_df,
                              cat_features=self.categorical_features)

            return estimator.predict(pool_test)

        return estimator.predict(X_test_df)

    def _get_weights(self, dist, weights):
        """Get the weights from an array of distances and a parameter ``weights``.
        Assume weights have already been validated.
        Parameters
        ----------
        dist : ndarray
            The input distances.
        weights : {'uniform', 'distance'}, callable or None
            The kind of weighting used.
        Returns
        -------
        weights_arr : array of the same shape as ``dist``
            If ``weights == 'uniform'``, then returns None.
        """
        if weights in (None, "uniform"):
            return None

        if weights == "distance":
            # if user attempts to classify a point that was zero distance from one
            # or more training points, those training points are weighted as 1.0
            # and the other points as 0.0
            if dist.dtype is numpy.dtype(object):
                for point_dist_i, point_dist in enumerate(dist):
                    # check if point_dist is iterable
                    # (ex: RadiusNeighborClassifier.predict may set an element of
                    # dist to 1e-6 to represent an 'outlier')
                    if hasattr(point_dist, "__contains__") and 0.0 in point_dist:
                        dist[point_dist_i] = point_dist == 0.0
                    else:
                        dist[point_dist_i] = 1.0 / point_dist
            else:
                with numpy.errstate(divide="ignore"):
                    dist = 1.0 / dist
                inf_mask = numpy.isinf(dist)
                inf_row = numpy.any(inf_mask, axis=1)
                dist[inf_row] = inf_mask[inf_row]
            return dist

        if callable(weights):
            return weights(dist)

    def decision_function(self, X):
        """
        Calls *decision_function*.
        """
        raise NotImplementedError(  # pragma: no cover
            "Decision function is not available for this model.")


if __name__ == '__main__':
    # Example code of how the HEOM metric can be used together with Scikit-Learn
    columns_to_remove = ["NUM","NUMDO","NUMDO_NOPAP", 'Unnamed: 0', 'format1', 'format2']
    # Load the dataset from sklearn
    data_origin = pd.read_csv("/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-ml/examples/Poidspapier- 3 ao_t 2022_V3.csv")#.sample(20000)

    data_origin['Surface']=data_origin['format1']*data_origin['format2']
    data=data_origin.drop(columns=columns_to_remove, errors='ignore')

    lr=LazyLookupRegression(lookup_keys=['CID','TYPAR2', 'GRAMMAGE','AppelationPapetiere', 'Surface'], linear_model=True)
    target=data["PoidsKG"]

    lr.fit(data.drop(columns=["PoidsKG"]), target)
    test_data= pd.read_csv("/Users/mohamedmentis/Downloads/TEST POIDS PAPIER - Variation NombrePage.csv")

    test_data['Surface']=test_data['format1']*test_data['format2']
    print(lr.predict(test_data.drop(columns=["PoidsKG", 'format1', 'format2'])))
    print(test_data['PoidsKG'])