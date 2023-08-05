# coding:utf-8

from itertools import chain

import numpy as np
from joblib import Parallel, delayed

from kolibri.backend.bn.base_estimator import ParameterEstimator
from kolibri.backend.bn.CPD import TabularCPD
from kolibri.backend.bn import BayesianNetwork


class MaximumLikelihoodEstimator(ParameterEstimator):
    def __init__(self, model, data, **kwargs):
        """
        Class used to compute parameters for a model using Maximum Likelihood Estimation.

        Parameters
        ----------
        model: A pgmpy.models.BayesianNetwork instance

        data: pandas DataFrame object
            DataFrame object with column names identical to the variable names of the network.
            (If some values in the data are missing the data cells should be set to `numpy.NaN`.
            Note that pandas converts each column containing `numpy.NaN`s to dtype `float`.)

        state_names: dict (optional)
            A dict indicating, for each variable, the discrete set of states
            that the variable can take. If unspecified, the observed values
            in the data set are taken to be the only possible states.

        complete_samples_only: bool (optional, default `True`)
            Specifies how to deal with missing data, if present. If set to `True` all rows
            that contain `np.NaN` somewhere are ignored. If `False` then, for each variable,
            every row where neither the variable nor its parents are `np.NaN` is used.

        Examples
        --------
        """
        if not isinstance(model, BayesianNetwork):
            raise NotImplementedError(
                "Maximum Likelihood Estimate is only implemented for BayesianNetwork"
            )
        elif set(model.nodes()) > set(data.columns):
            raise ValueError(
                f"Maximum Likelihood Estimator works only for models with all observed variables. Found latent variables: {model.latents}."
            )

        super(MaximumLikelihoodEstimator, self).__init__(model, data, **kwargs)

    def get_parameters(self, n_jobs=-1, weighted=False):
        """
        Method to estimate the model parameters (CPDs) using Maximum Likelihood
        Estimation.

        Parameters
        ----------
        n_jobs: int (default: -1)
            Number of jobs to run in parallel. Default: -1 uses all the processors.

        weighted: bool
            If weighted=True, the data must contain a `_weight` column specifying the
            weight of each datapoint (row). If False, assigns an equal weight to each
            datapoint.

        Returns
        -------
        Estimated parameters: list
            List of pgmpy.factors.discrete.TabularCPDs, one for each variable of the model

        Examples
        --------
        """

        parameters = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(self.estimate_cpd)(node, weighted) for node in self.model.nodes()
        )

        return parameters

    def estimate_cpd(self, node, weighted=False):
        """
        Method to estimate the CPD for a given variable.

        Parameters
        ----------
        node: int, string (any hashable python object)
            The name of the variable for which the CPD is to be estimated.

        weighted: bool
            If weighted=True, the data must contain a `_weight` column specifying the
            weight of each datapoint (row). If False, assigns an equal weight to each
            datapoint.

        Returns
        -------
        Estimated CPD: pgmpy.factors.discrete.TabularCPD
            Estimated CPD for `node`.

        Examples
        --------

        """

        state_counts = self.state_counts(node, weighted=weighted)

        # if a column contains only `0`s (no states observed for some configuration
        # of parents' states) fill that column uniformly instead
        state_counts.values[:, (state_counts.values == 0).all(axis=0)] = 1

        parents = sorted(self.model.get_parents(node))
        parents_cardinalities = [len(self.state_names[parent]) for parent in parents]
        node_cardinality = len(self.state_names[node])

        # Get the state names for the CPD
        state_names = {node: list(state_counts.index)}
        if parents:
            state_names.update(
                {
                    state_counts.columns.names[i]: list(state_counts.columns.levels[i])
                    for i in range(len(parents))
                }
            )

        cpd = TabularCPD(
            node,
            node_cardinality,
            np.array(state_counts),
            evidence=parents,
            evidence_card=parents_cardinalities,
            state_names={var: self.state_names[var] for var in chain([node], parents)},
        )
        cpd.normalize()
        return cpd
