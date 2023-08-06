import pandas as pd
from kolibri.distances.base_categorical import BaseDistance


class Eskin(BaseDistance):

    def __init__(self, data):
        super().__init__(data)
        self.num_cat = []
        for col_num in range(len(self.data.columns)):
            col_name = self.data.columns[col_num]
            categories = list(self.data[col_name].unique())
            self.num_cat.append(len(categories))




    def get_distance(self, x, y):
        """ Eskin Distance metric function which calculates the distance
        between two instances. Handles categorical values only.
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

        s = self.data.shape[1]

        x=pd.DataFrame([x], columns=self.columns)
        y=pd.DataFrame([y], columns=self.columns)

        x=self.encoder.transform(x).values[0]
        y=self.encoder.transform(y).values[0]
        agreement = []
        for i in range(s):
            agreement.append(0)

        for k in range(s):
            if x[k] == y[k]:
                agreement[k] = 1
            else:
                agreement[k] = self.num_cat[k] ** 2 / (self.num_cat[k] ** 2 + 2)
        eskin = (s / sum(agreement)) - 1
        return eskin


if __name__ == '__main__':
    # Example code of how the HEOM metric can be used together with Scikit-Learn
    import numpy as np
    from sklearn.neighbors import NearestNeighbors
    from sklearn.datasets import load_boston


    # Load the dataset from sklearn
    boston = load_boston()
    boston_data = boston["data"]
    # Categorical variables in the data
    categorical_ix = [3, 8]
    # The problem here is that NearestNeighbors can't handle np.nan
    # So we have to set up the NaN equivalent
    nan_eqv = 12345


    # Declare the HEOM with a correct NaN equivalent value
    heom_metric = Eskin(boston_data)

    # Declare NearestNeighbor and link the metric
    neighbor = NearestNeighbors(metric=heom_metric.get_distance)

    # Fit the model which uses the custom distance metric
    neighbor.fit(boston_data)

    # Return 5-Nearest Neighbors to the 1st instance (row 1)
    result = neighbor.kneighbors(boston_data[0].reshape(1, -1), n_neighbors=5)
    print(result)
