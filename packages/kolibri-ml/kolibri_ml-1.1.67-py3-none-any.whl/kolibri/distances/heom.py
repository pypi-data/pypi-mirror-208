import numpy as np
#import numba

from kolibri.distances.base_categorical import BaseDistance

class HEOM(BaseDistance):
    def __init__(self, X, cat_ix, nan_equivalents=[np.nan, 0], normalised="normal", encode_categories=True, num_features_dist_importance=10):
        """ Heterogeneous Euclidean-Overlap Metric
        Distance metric class which initializes the parameters
        used in heom function

        Parameters
        ----------
        X : array-like of shape = [n_rows, n_features]
            Dataset that will be used with HEOM. Needs to be provided
            here because minimum and maximimum values from numerical
            columns have to be extracted

        cat_ix : array-like of shape = [cat_columns_number]
            List containing categorical feature indices

        cat_ix : array-like of shape = [x]
            List containing missing values indicators

        normalised: string
            normalises euclidan distance function for numerical variables
            Can be set as "std". Default is a column range

        Returns
        -------
        None
        """

        super().__init__(X, encode_categories=encode_categories)
        self.nan_eqvs = nan_equivalents
        self.cat_ix = cat_ix
        self.col_ix = [i for i in range(self.data.shape[1])]
        # Get the normalization scheme for numerical variables
        if normalised == "std":
            self.range = 4* np.nanstd(self.data, axis = 0)
        else:
            self.range = np.nanmax(self.data, axis = 0) - np.nanmin(self.data, axis = 0)
        self.num_features_dist_importance=num_features_dist_importance
    #@numba.jit(fastmath=True)
    def get_distance(self, x, y):
        """ Distance metric function which calculates the distance
        between two instances. Handles heterogeneous data and missing values.
        It can be used as a custom defined function for distance metrics
        in Scikit-Learn

        Parameters
        ----------
        x : array-like of shape = [n_features]
            First instance

        y : array-like of shape = [n_features]
            Second instance
        Returns
        -------
        result: float
            Returns the result of the distance metrics function
        """
        # Initialise results' array
        results_array = np.zeros(x.shape)

        # Get indices for missing values, if any
        nan_x_ix = np.flatnonzero( np.logical_or(np.isin(x, self.nan_eqvs), np.isnan(x)))
        nan_y_ix = np.flatnonzero( np.logical_or(np.isin(y, self.nan_eqvs), np.isnan(y)))
        nan_ix = np.unique(np.concatenate((nan_x_ix, nan_y_ix)))
        # Calculate the distance for missing values elements
        results_array[nan_ix] = 1

        # Get categorical indices without missing values elements
        cat_ix = np.setdiff1d(self.cat_ix, nan_ix)
        # Calculate the distance for categorical elements
        results_array[cat_ix]= np.not_equal(x[cat_ix], y[cat_ix]) * 1 # use "* 1" to convert it into int

        # Get numerical indices without missing values elements
        num_ix = np.setdiff1d(self.col_ix, self.cat_ix)
        num_ix = np.setdiff1d(num_ix, nan_ix)
        # Calculate the distance for numerical elements
        results_array[num_ix] = self.num_features_dist_importance*(np.abs(x[num_ix] - y[num_ix]) / self.range[num_ix])

        # Return the final result
        # Square root is not computed in practice
        # As it doesn't change similarity between instances
        return np.sum(np.square(results_array))


    #@numba.jit(fastmath=True)
    def get_distance_fast(self, x, y):
        """ Distance metric function which calculates the distance
        between two instances. Handles heterogeneous data and missing values.
        It can be used as a custom defined function for distance metrics
        in Scikit-Learn

        Parameters
        ----------
        x : array-like of shape = [n_features]
            First instance

        y : array-like of shape = [n_features]
            Second instance
        Returns
        -------
        result: float
            Returns the result of the distance metrics function
        """
        # Initialise results' array
        results_array = np.zeros(x.shape)

        # Calculate the distance for categorical elements
        results_array[self.cat_ix]= np.not_equal(x[self.cat_ix], y[self.cat_ix]) * 1 # use "* 1" to convert it into int

        # Get numerical indices without missing values elements
        num_ix = np.setdiff1d(self.col_ix, self.cat_ix)

        results_array[num_ix] = self.num_features_dist_importance*(np.abs(x[num_ix] - y[num_ix]) / self.range[num_ix])

        # Return the final result
        # Square root is not computed in practice
        # As it doesn't change similarity between instances
        return np.sum(np.square(results_array))


if __name__ == '__main__':
    # load data

    from sklearn.datasets import load_boston
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier

    boston = load_boston(return_X_y=False)

    # separate the data into X and y
    X = boston['data']
    y = boston['target']

    # transform the y from continuous to categorical
    quantile = np.quantile(y, [0.25, 0.5, 0.75])



    def num_to_cat(quantile, input_):
        """ use quantil to categorize continuous data
        """
        if input_ <= quantile[0]:
            return 0
        elif input_ <= quantile[1]:
            return 1
        elif input_ <= quantile[2]:
            return 2
        else:
            return 3

    # the categorized y
    y_cat = [num_to_cat(quantile, i) for i in y]
    X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.1)

    cat_idx = [3, 8]
    cont_idx = [i for i in range(X.shape[-1]) if i not in cat_idx]

    # scale the continuous columns
    scaler = StandardScaler().fit(X_train[:, cont_idx])

    X_train[:, cont_idx] = scaler.transform(X_train[:, cont_idx])
    X_test[:, cont_idx] = scaler.transform(X_test[:, cont_idx])


    vdm = HEOM(X_train, cat_ix= cat_idx, encode_categories=False)


    knn = KNeighborsClassifier(n_neighbors=3, metric=vdm.get_distance, algorithm='brute')
    knn.fit(X_train, y_train)

    print(knn.score(X_test, y_test))
