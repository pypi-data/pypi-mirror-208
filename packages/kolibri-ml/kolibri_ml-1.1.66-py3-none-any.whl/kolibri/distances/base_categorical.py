import category_encoders as ce
import numpy as np
import pandas as pd

class BaseDistance():

    def __init__(self, data, encode_categories=False):


        if encode_categories is True:
            self.data=self.ordinal_encode(data)
        else:
            self.data=data
        if not isinstance(self.data, pd.DataFrame):
            self.data=pd.DataFrame(self.data)
        self.columns=list(self.data.columns)

    def ordinal_encode(self, db):
        encoding_data = db.copy()
        self.encoder = ce.OrdinalEncoder(encoding_data)
        data_encoded = self.encoder.fit_transform(encoding_data)
        return data_encoded

    def frequency_table(self):
        num_cat = []
        for col_num in range(len(self.data.columns)):
            col_name = self.data.columns[col_num]
            categories = list(self.data[col_name].unique())
            num_cat.append(len(categories))
        r = self.data.shape[0]
        s = self.data.shape[1]
        freq_table = np.zeros(shape=(max(num_cat), s))

        for i in range(s):
            for j in range(num_cat[i]):
                count = []
                for num in range(0, r):
                    count.append(0)
                for k in range(0, r):
                    if (self.data.iat[k, i] - 1 == j):
                        count[k] = 1
                    else:
                        count[k] = 0
                freq_table[j][i] = sum(count)
        return (freq_table)

    def get_conditional_proba(self, x, y):
        """ get conditional probability of x given that y
        Parameters: x (nd-array) - an array of categorical data
                    y (nd-array) - an array of categorical data, the dependent variable
        Returns: class_proba (dict) - a dictionary collects all the conditional probability
                                      {unique_y: pd.Sereis of conditional probability}
        """
        unique_y = np.unique(y)
        class_proba = dict()

        # creaet conditional probability
        for unique_x in np.unique(x):
            cond_data = y[x == unique_x]
            cond_proba = pd.Series(cond_data).value_counts() / len(cond_data)

            append_val = [i for i in unique_y if i not in cond_proba]
            if len(append_val) > 0:
                append_series = pd.Series(np.zeros(len(append_val)), index=append_val)
                cond_proba = cond_proba.append(append_series)

            # create new key
            class_proba[unique_x] = cond_proba

        return class_proba

    def get_delta(self, cond_proba, val_1, val_2, norm=2):
        """ get delta for vdm
        Parameters: cond_proba (dict) - a dictionary of conditional probability, extract from get_conditional_proba()
                    val_1 (str/int/float) - value 1
                    val_2 (str/int/float) - value 2
                    norm (int) - type of norm use, default is 2
        Returns: delta (float) - the delta value for this instance
        """
        try:
            proba = np.array(
                [abs(cond_proba[val_1][uni_x] - cond_proba[val_2][uni_x]) for uni_x in cond_proba[val_1].index])
        except Exception as e:
            return 0.001
        delta = (proba ** norm).sum()
        return delta

    def get_conditional_proba_nd(self, X, y):
        """ given a nd array, return the dimensional conditional probability given that y
        Parameters: X (nd-array) - an nd-array of categorical data
                    y (nd-array) - an array of categorical data, the dependent variable
        Returns: dim_proba (dict) - a dictionary collects all the conditional probability
                                    {col_num:{unique_y: pd.Sereis of conditional probability}}
        """
        dim_proba = {col: self.get_conditional_proba(X[:, col], y) for col in range(X.shape[1])}
        return dim_proba

    def get_delta_nd(self, cond_proba, ins_1, ins_2, norm=2):
        """ get deltas for vdm for multidimensional data
        Parameters: cond_proba (dict) - a dictionary of conditional probability, extract from get_conditional_proba_nd()
                    ins_1 (nd-array) - array 1
                    ins_2 (nd-array) - array 2
                    norm (int) - type of norm use, default is 2
        Returns: deltas (array) - the delta values between ins_1 and ins_2
        """
        deltas = np.array([self.get_delta(cond_proba[col], ins_1[col], ins_2[col], norm) for col in cond_proba])
        return deltas

    def get_cont_dist(self, ins_1, ins_2, norm=2):
        """ get dimensional distance for continuous data
        Parameters: ins_1 (nd-array) - array 1
                    ins_2 (nd-array) - array 2
                    norm (int) - type of norm use, default is 2
        Returns: dist (array) - the dimenional distance between ins_1 and ins_2
        """
        dist = abs(ins_1 - ins_2) ** norm
        return dist