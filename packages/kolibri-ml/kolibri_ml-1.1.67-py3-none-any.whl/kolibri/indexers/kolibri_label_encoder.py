import pandas as pd
import numpy as np
from kolibri.core.component import Component

class KolibriLabelEncoder(Component):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.label_map = {}


    def fit(self, y):
        if not isinstance(y, pd.Series):
            list_of_labels = pd.Series(y)
        unique_labels = y.unique()
        try:
            unique_labels = sorted(unique_labels)
        except TypeError:
            unique_labels = unique_labels

        for idx, val in enumerate(unique_labels):
            self.label_map[val] = idx
        return self


    def transform(self, in_vals):
        return_vals = []
        for val in in_vals:
            if not isinstance(val, str):
                if isinstance(val, float) or isinstance(val, int) or val is None or isinstance(val, np.generic):
                    val = str(val)
                else:
                    val = val.encode('utf-8').decode('utf-8')

            if val not in self.label_map:
                self.label_map[val] = len(self.label_map.keys())
            return_vals.append(self.label_map[val])

        if len(in_vals) == 1:
            return return_vals[0]
        else:
            return return_vals
