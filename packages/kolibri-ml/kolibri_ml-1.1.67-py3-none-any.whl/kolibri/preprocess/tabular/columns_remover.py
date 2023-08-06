from kolibri.core.component import Component
from sklearn.impute._base import _BaseImputer, SimpleImputer
import numpy as np
import pandas as pd
from copy import deepcopy
from kolibri.utils.common import prepare_names_for_json
from kolibri.preprocess.tabular.dummy_converter import DummyConverter
from kolibri.preprocess.tabular.time_features_extractor import TimeFeatures
from sklearn.preprocessing import LabelEncoder
import gc

class PandasColumnRemover(Component):

    defaults = {
        "fixed":{
            "columns-to-remove":[]
        },

    }


    def __init__(self, params={}):
        super().__init__(params)

        self.columns_to_remove = self.get_parameter("columns-to-remove")
    def fit(self, dataset, y=None):  #
        return self


    def transform(self, dataset, y=None):
        data=dataset
        # actual computation:

        return data.drop(columns=self.columns_to_remove, errors="ignore")

    def fit_transform(self, dataset, y=None):

        data = dataset
        self.fit(data)
        return self.transform(data)

