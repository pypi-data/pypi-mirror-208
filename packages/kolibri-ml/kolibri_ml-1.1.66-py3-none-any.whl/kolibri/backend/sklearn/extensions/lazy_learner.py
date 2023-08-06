import category_encoders as ce
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

from kolibri.automl.data_inspection import get_data_info
from kolibri.distances.heom import HEOM
from kolibri.distances.hvdm import HVDM
from kolibri.preprocess.tabular import AutoInferDatatype, NearZeroVariance, Multicollinearity, DummyConverter
from kolibri.backend.sklearn.extensions.distributed_nn import DistributedNearestNeighbors

class LazyRegression(BaseEstimator, RegressorMixin):
    """
    Fits a linear regression, on sub sample of size n. The sample formed by the top n similar items to the
    sample to be predicted
    """


    def __init__(self, n_neighbors:int=10, algorithm='auto',  distance='heom', leaf_size:int=10,weight_by_distance=True,
                 weights = 'uniform', nb_features_to_keep=8, nb_buckets=100, num_features_dist_importance=1,posterior_sampling=True,
                 objective='RMSE', rsm=0.5, depth=6, boosting_type='Ordered',bootstrap_type='Bayesian', bagging_temperature=1,
                 learning_rate=0.03, l2_leaf_reg=3.0, iterations=100, verbose=False, linear_model=False, augment_samples_ratio=[], inddependent_var_name=None):
        "constructor"
        RegressorMixin.__init__(self)
        BaseEstimator.__init__(self)
        self.objective=objective
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
        self.inddependent_var_name=inddependent_var_name
        self.estimator_fe = CatBoostRegressor(learning_rate=self.learning_rate, l2_leaf_reg=self.l2_leaf_reg, iterations=self.iterations, posterior_sampling=self.posterior_sampling, objective=self.objective, rsm=self.rsm, depth=self.depth, bootstrap_type=self.bootstrap_type, bagging_temperature=self.bagging_temperature, verbose=False)
        if self.linear_model:
            self.estimator=LinearRegression(fit_intercept=False)
        else:
            self.estimator=clone(self.estimator_fe)

        self.algorithm=algorithm
        self.leaf_size=leaf_size
        self.n_neighbors=n_neighbors
        self.neigberhood=NearestNeighbors(n_neighbors=n_neighbors, algorithm=algorithm, leaf_size=leaf_size, n_jobs=-1)

        self.weights=weights
        self.weight_by_distance=weight_by_distance
        self.encoder=None
        self.distance=distance
        self.nb_features_to_keep=nb_features_to_keep
        self.nb_buckets=nb_buckets
        self.num_features_dist_importance=num_features_dist_importance
        self.augment_samples_ratio=augment_samples_ratio
        self.independent_var_indices=None
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
        if self.inddependent_var_name is not None:
            self.independent_var_indices=[X.columns.get_loc(v) for v in self.inddependent_var_name]
        self.features=X.columns.values
        #convert to Dataframe if X is not a Dataframe


        if not isinstance(X, pd.DataFrame):
            X=pd.DataFrame(X).convert_dtypes()
            for col in X.columns:
                if X[col].dtype=="string":
                    X[col]=X[col].astype('object')

        self.categorical_features = list(X.select_dtypes(include=['category', 'object', 'string']))
        self.numerical_features = [feat for feat in self.features if feat not in self.categorical_features]

        #get column info to detect categorical columns
        data_info=get_data_info(X)
        self.categorical_ix = [c["id"] for c in data_info["categorical_columns"]]
        self.numerical_ix=[c["id"] for c in data_info["numerical_columns"]]
        #create and fit category encoders
        self.encoder = ce.OrdinalEncoder(X, handle_missing="return_nan")
        X=self.encoder.fit_transform(X)


        #create a mixed datatype distance measure
        if self.distance=='heom':
            distance_metric = HEOM(X, cat_ix=self.categorical_ix, encode_categories=False, nan_equivalents = [12345], num_features_dist_importance=self.num_features_dist_importance).get_distance_fast
        elif self.distance=='hvdm':
            bins = numpy.linspace(min(y), max(y), self.nb_buckets)
            d_y = numpy.digitize(y, bins)
            distance_metric = HVDM(X, d_y, cat_ix=self.categorical_ix).get_distance

        elif self.distance=='vdm':
            distance_metric = HEOM(X, cat_ix=self.categorical_ix, encode_categories=False).get_distance
        else:
            distance_metric=None
        if not isinstance(X, numpy.ndarray):
            if hasattr(X, 'values'):
                X = X.values
        if not isinstance(X, numpy.ndarray):
            raise TypeError("'X' must be an array.")

        if distance_metric is not None:
            self.neigberhood.metric=distance_metric

        self.neigberhood.fit(X, y)
        self._y=numpy.array(y)
        self._feature_importance=self._get_feature_importance(X, y)
        return self

    def _get_feature_importance(self, X, y):
        self.estimator_fe=self._fit_local_model(X, y, self.estimator_fe, get_feature_importance=True)
        feature_importance=self.estimator_fe.feature_importances_
        return numpy.argsort(-feature_importance)

    def predict(self, X):
        """
        Runs the predictions.
        """
        X=self.encoder.transform(X)
        #Neigherest Neigbors do not like nan values
        for x in X:
            for i in numpy.argwhere(pd.isnull(x)):
                x[i]=12345

        return [self._predict_one([x]) for x in tqdm(X.values)]

    def interval(self, min_val, max_val, n):
        sub_division=(max_val-min_val)/n
        ret=[]
        for i in range(n):
            ret.append((i+1)*sub_division)
        return ret
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
        if self.weights == "uniform":
            # In that case, we do not need the distances to perform
            # the weighting so we do not compute them.
            neigh_ind = self.neigberhood.kneighbors(X, return_distance=False)
            neigh_dist = None
        else:
            neigh_dist, neigh_ind = self.neigberhood.kneighbors(X)

        weights = self._get_weights(neigh_dist, self.weights)
        X=X[0][self._feature_importance[:self.nb_features_to_keep]]

        _y = self._y
        if _y.ndim == 1:
            _y = _y.reshape((-1, 1))

        _X = self.neigberhood._fit_X[:,self._feature_importance[:self.nb_features_to_keep]]

        estimator = clone(self.estimator)
        _X_train, _y_train=_X[neigh_ind.ravel()], _y[neigh_ind.ravel()]

        if self.augment_samples_ratio!=[] and sum(self.augment_samples_ratio)>0:
            last_row_to_change=1
            for i in range(len(self.augment_samples_ratio)):
                nb_values_to_create = self.interval(0.1, 3, int(self.n_neighbors*self.augment_samples_ratio[i])+1)

                independent_var_for_linear_augmentation = \
                numpy.where(self._feature_importance == self.independent_var_indices[i])[0]
                X_values_to_augment=_X_train[0]
                y_values_to_augment=_y_train[0]

                if X_values_to_augment[self.independent_var_indices[i]]/X[0][self.independent_var_indices[i]] >0.01:
                    nb_values_to_create.append(X_values_to_augment[self.independent_var_indices[i]]/X[0][self.independent_var_indices[i]])

                for n, v in enumerate(nb_values_to_create):
                    _X_train[-(n+last_row_to_change)]=X_values_to_augment
                    _X_train[-(n+last_row_to_change)][independent_var_for_linear_augmentation]=X_values_to_augment[independent_var_for_linear_augmentation]*v
                    _y_train[-(n+last_row_to_change)]=y_values_to_augment*v
                last_row_to_change=n+1
        try:

            estimator=self._fit_local_model(_X_train, _y_train, estimator, important_features=self._feature_importance[:self.nb_features_to_keep], weights=weights)


#            y_pred=estimator.predict([X[0][self._feature_importance[:self.nb_features_to_keep]]])
            y_pred=self._predict_local_model(X_test=[X], estimator=estimator, important_features=self._feature_importance[:self.nb_features_to_keep])
        except Exception as e:
            if weights is None:
                y_pred = numpy.mean(_y_train, axis=1)
            else:
                y_pred = numpy.empty((neigh_dist.shape[0], _y.shape[1]), dtype=numpy.float64)
                denom = numpy.sum(weights, axis=1)

                for j in range(_y.shape[1]):
                    num = numpy.sum(_y[neigh_ind, j] * weights, axis=1)
                    y_pred[:, j] = num / denom

        if self._y.ndim == 1:
            y_pred = y_pred.ravel()

        return y_pred[0]

    def _fit_local_model(self, X_train, y_train, estimator, get_feature_importance=False, important_features=None, weights=None):

        X_train_df = pd.DataFrame(X_train)
        if important_features is None:
            X_train_df.columns = self.features
        else:
            X_train_df.columns=self.features[important_features]
        categorical_features=[]
        for col in self.categorical_features:
            if col in X_train_df.columns:
                categorical_features.append(col)
                X_train_df[col]=X_train_df[col].astype('string')

        if not self.linear_model or get_feature_importance:
            if weights is None:
                pool_train = Pool(X_train_df, y_train,
                                  cat_features=categorical_features)
            else:
                pool_train = Pool(
                    data=X_train_df,
                    weight=weights.ravel(),
                    label=y_train,
                    cat_features=categorical_features
                )

            return estimator.fit(pool_train)

        return self._fit_linear_model(X_train_df, y_train, estimator, important_features)

    def _fit_linear_model(self, X_train, y_train, estimator, important_features=None):
        infer_type=AutoInferDatatype(config={"categorical-features":self.categorical_features, "numerical-features": self.numerical_features})
        zero=NearZeroVariance(configs={})
        colinear=Multicollinearity(configs={"colinearity-threshold": 0.7, "correlation-with-target-threshold": 0.2})

        regressor = Pipeline(
            steps=[("infer_type", infer_type), ("zero_var", zero), ("colinearity", colinear), ("dummy",DummyConverter(config={})), ("regressor", estimator)]
        )

        regressor.fit(X_train, y_train)

        return regressor

    def _predict_local_model(self, X_test, estimator, important_features=None):

        X_test_df = pd.DataFrame(X_test)
        categorical_features=self.categorical_features
        if important_features is None:
            X_test_df.columns = self.features
        else:
            X_test_df.columns=self.features[important_features]


        categorical_features=[]
        for col in self.categorical_features:
            if col in X_test_df.columns:
                categorical_features.append(col)
                X_test_df[col]=X_test_df[col].astype('string')

        if not self.linear_model:
            pool_test = Pool(data=X_test_df,
                              cat_features=categorical_features)

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

    columns_to_remove = ["NUM","NUMDO","NUMDO_NOPAP", 'Unnamed: 0']
    # Load the dataset from sklearn
    data_origin = pd.read_csv("/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-ml/examples/Poidspapier- 3 ao_t 2022_V2.csv").sample(20000)

    data=data_origin.drop(columns=columns_to_remove, errors='ignore')

    lr=LazyRegression(n_neighbors=10, linear_model=False, augment_samples_ratio=0.0,inddependent_var_name="QteFact")
    target=data["PoidsKG"]

    lr.fit(data.drop(columns=["PoidsKG"]), target)
    test_data=pd.read_csv("/Users/mohamedmentis/Downloads/Poidspapier-test.csv")

    print(lr.predict(test_data.drop(columns=["PoidsKG", "Surface"])))
    print(test_data['PoidsKG'])