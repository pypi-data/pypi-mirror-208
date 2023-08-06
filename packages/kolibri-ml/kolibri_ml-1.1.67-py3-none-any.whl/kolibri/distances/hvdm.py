import numpy as np 
from kolibri.distances.base_categorical import BaseDistance
import pandas as pd
#import numba

class HVDM(BaseDistance):
    def __init__(self, X, y, cat_ix=None):
        """ input data to compute distance
        Parameters: X (pd.Series/pd.DataFrame/nd-array) - independent variables, can be mix-type
                    y (array-like) - dependent variable
                    continuous (list) - a list of column numbers denoting continuous columns
                                        defaul is None, if None, then will take all columns as categorical data
        """
        # check input variable types
        super().__init__(X)
        if not isinstance(X, (pd.core.series.Series, pd.DataFrame, np.ndarray)):
            raise TypeError('Wrong input data type: X')

        if not isinstance(y, (tuple, list, np.ndarray, pd.core.series.Series)):
            raise TypeError('Wrong input data type: y')

        if cat_ix is not None:
            if not isinstance(cat_ix, (tuple, list, np.ndarray, pd.core.series.Series)):
                raise TypeError('continuous must be a container type object')

        # check dimension
        if len(X) != len(y):
            raise Exception('Dimension of X != Dimension of y')

        self.X = np.array(X)
        self.y = np.array(y)
        self.categorical = cat_ix

        if cat_ix is not None:
            self.continuous = [i for i in range(self.X.shape[-1]) if i not in self.categorical]
            self.cont_X = self.X[:, self.continuous]

            self.cat_X = self.X[:, self.categorical]
        else:
            self.categorical = np.arange(self.X.shape[-1])
            self.cat_X = self.X
        self.cond_proba = self.get_conditional_proba_nd(self.cat_X, self.y)

#    @numba.jit
    def get_distance(self, ins_1, ins_2, norm=2):
        """ calculate distance between two instances
        Parameters: ins_1 (array-like) - instance 1
                    ins_2 (array-like) - instance 2
                    norm (int) - type of norm use, default is 2
        Returns: dist (float) - vdm distance between the two instances
        """

        if not isinstance(ins_1, (tuple, list, np.ndarray, pd.core.series.Series)):
            raise TypeError('Wrong input data type: ins_1')

        if not isinstance(ins_2, (tuple, list, np.ndarray, pd.core.series.Series)):
            raise TypeError('Wrong input data type: ins_2')

        if len(ins_1) != self.X.shape[-1]:
            raise Exception('Dimension mismatch with training data: ins_1')

        if len(ins_2) != self.X.shape[-1]:
            raise Exception('Dimension mismatch with training data: ins_2')

        if len(ins_1) != len(ins_2):
            raise Exception('Dimension of ins_1 != Dimension of ins_2')

        ins_1 = np.array(ins_1)
        ins_2 = np.array(ins_2)

        if self.continuous is not None:
            ins_1_cat = ins_1[self.categorical]
            ins_2_cat = ins_2[self.categorical]

            ins_1_cont = ins_1[self.continuous].astype(float)
            ins_2_cont = ins_2[self.continuous].astype(float)
        else:
            ins_1_cat = ins_1
            ins_2_cat = ins_2

        cat_dist = self.get_delta_nd(self.cond_proba, ins_1_cat, ins_2_cat, norm)

        if self.continuous is not None:
            cont_dist = self.get_cont_dist(ins_1_cont, ins_2_cont, norm)
            dist = (np.concatenate([cat_dist, cont_dist]).sum()) ** (1 / norm)
        else:
            dist = (cat_dist.sum()) ** (1 / norm)

        return dist

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


    vdm = HVDM(X_train, y_train, cat_ix= cat_idx)


    knn = KNeighborsClassifier(n_neighbors=3, metric=vdm.get_distance, algorithm='brute')
    knn.fit(X_train, y_train)

    print(knn.score(X_test, y_test))
