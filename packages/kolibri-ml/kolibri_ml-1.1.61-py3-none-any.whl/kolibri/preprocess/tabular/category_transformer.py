from kolibri.core.component import Component
import pandas as pd
import category_encoders as ce
import numpy as np
import importlib


class CategoryEncoder(Component):
    """
    - converts categorical features into ordinal values
    - takes a dataframe , and information about column names and ordered categories as dict
    - returns float panda data frame
  """

    defaults = {
        "fixed":{
            "encoder_name": "OrdinalEncoder"
        }
    }
    def __init__(self, params):
        """

        Args:
            params: define the following parameter as a json dictionary
            "encoder_name": the name of the encoder. can be one of the following:
                    "BackwardDifferenceEncoder",
        "BinaryEncoder",
        "GrayEncoder",
        "CountEncoder",
        "HashingEncoder",
        "HelmertEncoder",
        "OneHotEncoder",
        "OrdinalEncoder",
        "SumEncoder",
        "PolynomialEncoder",
        "BaseNEncoder",
        "LeaveOneOutEncoder",
        "TargetEncoder",
        "WOEEncoder",
        "MEstimateEncoder",
        "JamesSteinEncoder",
        "CatBoostEncoder",
        "GLMMEncoder",
        "QuantileEncoder",
        "SummaryEncoder",
        'RankHotEncoder',

        """
        super().__init__(params)


    def fit(self, data, y=None):
        self.fit_transform(data, y=y)
        return self

    def transform(self, dataset, y=None):

        return self.enc.transform(dataset)


    def get_encoder(self, encoder_name):


        Encoder = getattr(importlib.import_module("category_encoders"), encoder_name)

        # Instantiate the class (pass arguments to the constructor, if needed)
        return Encoder


    def fit_transform(self, dataset, y=None):
        self.enc = self.get_encoder(self.get_parameter("encoder_name"))(dataset, handle_missing="return_nan")

        return self.enc.fit_transform(dataset)


