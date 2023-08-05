import pandas as pd
import numpy as np
import category_encoders as ce
import math
from kolibri.distances.base_categorical import BaseDistance

class Lin(BaseDistance):

    def __init__(self, data):
        super().__init__(data)
        r = self.data.shape[0]

        self.freq_rel = self.frequency_table(data) / r
    def get_distance(self, x, y):
        s = self.data.shape[0]
        agreement = []
        for i in range(s):
            agreement.append(0)

        x=pd.DataFrame([x], columns=self.columns)
        y=pd.DataFrame([y], columns=self.columns)

        x=self.encoder.transform(x).values[0]
        y=self.encoder.transform(y).values[0]

        weights = []
        for i in range(s):
            weights.append(0)

        for k in range(s):
            c = x[k] - 1
            d = y[k] - 1
            if (x[k] == y[k]):
                agreement[k] = 2 * np.log(self.freq_rel[c][k])
            else:
                agreement[k] = 2 * np.log(self.freq_rel[c][k] + self.freq_rel[d][k])
            weights[k] = np.log(self.freq_rel[c][k]) + np.log(self.freq_rel[d][k])
        lin = 1 / (1 / sum(weights) * (sum(agreement))) - 1

        lin[lin == -math.inf] = lin.max() + 1
        return (lin)



