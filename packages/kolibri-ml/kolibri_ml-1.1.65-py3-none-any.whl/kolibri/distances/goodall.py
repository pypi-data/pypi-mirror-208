import pandas as pd
from kolibri.distances.base_categorical import BaseDistance





class Goodall(BaseDistance):
    def __init__(self, data):
        super().__init__(data)
        self.data=self.ordinal_encode(data)
        r = self.data.shape[0]
        self.columns=list(self.data.columns)
        self.freq_rel = self.frequency_table(self.data)/r
        self.freq_rel2 = self.freq_rel ** 2
    def goodall1(self, x, y):
        s=self.data.shape[1]

        agreement = []
        for i in range(s):
            agreement.append(0)

        x=pd.DataFrame([x], columns=self.columns)
        y=pd.DataFrame([y], columns=self.columns)

        x=self.encoder.transform(x).values[0]
        y=self.encoder.transform(y).values[0]

        for k in range(s):
            c = x[k]
            if (x[k] == y[k]):
                logic = self.freq_rel[:, k] <= self.freq_rel[c][k]
                agreement[k] = 1 - sum(self.freq_rel2[:, k] * logic)
            else:
                agreement[k] = 0
        good1= 1 - (sum(agreement) / s)

        return (good1)

    def goodall2(self, x, y):
        s=self.data.shape[1]

        agreement = []
        for i in range(s):
            agreement.append(0)

        x=pd.DataFrame([x], columns=self.columns)
        y=pd.DataFrame([y], columns=self.columns)

        x=self.encoder.transform(x).values[0]
        y=self.encoder.transform(y).values[0]

        for k in range(s):
            c = x[k]
            if (x[k] == y[k]):
                logic = self.freq_rel[:, k] >= self.freq_rel[c][k]
                agreement[k] = 1 - sum(self.freq_rel2[:, k] * logic)
            else:
                agreement[k] = 0
        good2= 1 - (sum(agreement) / s)

        return (good2)


    def goodall3(self, x, y):
        s=self.data.shape[1]

        agreement = []
        for i in range(s):
            agreement.append(0)

        x=pd.DataFrame([x], columns=self.columns)
        y=pd.DataFrame([y], columns=self.columns)

        x=self.encoder.transform(x).values[0]
        y=self.encoder.transform(y).values[0]

        for k in range(s):
            c = x[k] - 1
            if (x[k] == y[k]):
                agreement[k] = 1 - self.freq_rel[c][k] ** 2
            else:
                agreement[k] = 0
        good3= 1 - (sum(agreement) / s)

        return (good3)


    def goodall4(self, x, y):
        s=self.data.shape[1]

        agreement = []
        for i in range(s):
            agreement.append(0)

        x=pd.DataFrame([x], columns=self.columns)
        y=pd.DataFrame([y], columns=self.columns)

        x=self.encoder.transform(x).values[0]
        y=self.encoder.transform(y).values[0]

        for k in range(s):
            c = x[k]
            if (x[k] == y[k]):
                agreement[k] = self.freq_rel[c][k] ** 2
            else:
                agreement[k] = 0
        good3= 1 - (sum(agreement) / s)

        return (good3)


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
    heom_metric = Goodall(boston_data)

    # Declare NearestNeighbor and link the metric
    neighbor = NearestNeighbors(metric=heom_metric.goodall1)

    # Fit the model which uses the custom distance metric
    neighbor.fit(boston_data)

    # Return 5-Nearest Neighbors to the 1st instance (row 1)
    result = neighbor.kneighbors(boston_data[0].reshape(1, -1), n_neighbors=5)
    print(result)
