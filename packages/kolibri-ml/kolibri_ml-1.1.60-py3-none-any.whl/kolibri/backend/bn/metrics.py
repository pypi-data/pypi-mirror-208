from kolibri.backend.bn.DAG import DAG
from kolibri.backend.bn.BayesianNetwork import BayesianNetwork
import pandas as pd




def structure_score(model, data, scoring_method="bic", **kwargs):

    """
    Uses the standard model scoring methods to give a score for each structure.
    The score doesn't have very straight forward interpretebility but can be
    used to compare different models. A higher score represents a better fit.
    This method only needs the model structure to compute the score and parameters
    aren't required.

    Parameters
    ----------
    model: pgmpy.base.DAG or pgmpy.models.BayesianNetwork instance
        The model whose score needs to be computed.

    data: pd.DataFrame instance
        The dataset against which to score the model.

    scoring_method: str ( k2 | bdeu | bds | bic )
        The following four scoring methods are supported currently: 1) K2Score
        2) BDeuScore 3) BDsScore 4) BicScore

    kwargs: kwargs
        Any additional parameters that needs to be passed to the
        scoring method. Check pgmpy.estimators.StructureScore for details.

    Returns
    -------
    Model score: float
        A score value for the model.

    Examples
    --------
    """
    from kolibri.backend.bn.StructureScore import K2Score, BDeuScore, BDsScore, BicScore

    supported_methods = {
        "k2": K2Score,
        "bdeu": BDeuScore,
        "bds": BDsScore,
        "bic": BicScore,
    }

    # Step 1: Test the inputs
    if not isinstance(model, (DAG, BayesianNetwork)):
        raise ValueError(
            f"model must be an instance of pgmpy.base.DAG or pgmpy.models.BayesianNetwork. Got {type(model)}"
        )
    elif not isinstance(data, pd.DataFrame):
        raise ValueError(f"data must be a pandas.DataFrame instance. Got {type(data)}")
    elif set(model.nodes()) != set(data.columns):
        raise ValueError(
            f"Missing columns in data. Can't find values for the following variables: { set(model.nodes()) - set(data.columns) }"
        )
    elif (scoring_method not in supported_methods.keys()) and (
        not callable(scoring_method)
    ):
        raise ValueError(f"scoring method not supported and not a callable")

    # Step 2: Compute the score and return
    return supported_methods[scoring_method](data).score(model, **kwargs)
