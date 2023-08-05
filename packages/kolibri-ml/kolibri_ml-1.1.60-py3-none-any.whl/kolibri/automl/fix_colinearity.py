import numpy
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor

def calculate_vif(df, method="linear_regression"):
    """

    Args:
        df: Feature dataframe containing only features and not target column
        method: method used to compute the vif. options are:
        1- 'linear_regression': using linear gresion R2 and the formula: 1/(1-R2)
        2- 'inflation_factor': using statsmodel variance_inflation_factor function to compute vif

    Returns:

    """

    if method=='linear_regression':
        vif, tolerance = {}, {}
        # all the features that you want to examine
        for feature in df.columns:
            # extract all the other features you will regress against
            X = [f for f in df.columns if f != feature]
            X, y = df[X], df[feature]
            # extract r-squared from the fit
            r2 = LinearRegression().fit(X, y).score(X, y)

            # calculate tolerance
            tolerance[feature] = 1 - r2
            # calculate VIF
            vif[feature] = 1/ (tolerance[feature])
    elif method=='inflation_factor':
        vif=[variance_inflation_factor(df.values, i)
                          for i in range(len(df.columns))]

        tolerance=[0 for i in range(len(df.columns))]


    # return VIF DataFrame

    return pd.DataFrame({'VIF': vif, 'Tolerance': tolerance})



def calculate_correlation_with_output(df, target):

    if len(df) != len(target):
        raise Exception("Inconsistant dataframe and target lengths")

    if isinstance(target, numpy.ndarray):
        target=target.reshape(-1)
    return abs(df.apply(lambda x: x.corr(pd.Series(target))))

def remove_features(df, target):
    vif=calculate_vif(df)#, method="inflation_factor")
    vif['corr']=calculate_correlation_with_output(df, target)

    inf_values=[i for i, v in enumerate(np.isfinite(vif['VIF'])) if v == False]

    if inf_values !=[]:
        pass
    df.iloc[inf_values].idxmax()
    id=vif[['VIF']].idxmax()[0]

    df2=df.drop(df.columns[id], axis=1)
    print(calculate_correlation_with_output(df, target))
    print(calculate_vif(df2))#, method="inflation_factor"))

    vif=calculate_vif(df)