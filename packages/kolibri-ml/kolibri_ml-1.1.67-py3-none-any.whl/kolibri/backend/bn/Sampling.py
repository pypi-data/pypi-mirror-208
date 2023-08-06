import itertools
from collections import namedtuple

import networkx as nx
import numpy as np
import os, math
from joblib import Parallel, delayed
from tqdm.auto import tqdm

from kolibri.backend.bn.factors_base import factor_product
from kolibri.backend.bn.BayesianNetwork import BayesianNetwork
from kolibri.backend.bn.MarkovNetwork import MarkovNetwork
from kolibri.backend.bn.MarkovChain import MarkovChain
from kolibri.backend.bn.base_inference import Inference
import pandas as pd

from kolibri.utils.mathext import sample_discrete, sample_discrete_maps

State = namedtuple("State", ["var", "state"])




def _return_samples(samples, state_names_map=None):
    """
    A utility function to return samples according to type
    """
    df = pd.DataFrame.from_records(samples)
    if state_names_map is not None:
        for var in df.columns:
            if var != "_weight":
                df[var] = df[var].map(state_names_map[var])
    return df

class BayesianModelInference(Inference):
    """
    Inference class specific to Bayesian Models
    """

    def __init__(self, model):
        """
        Class to calculate probability (pmf) values specific to Bayesian Models

        Parameters
        ----------
        model: Bayesian Model
            model on which inference queries will be computed
        """


        if not isinstance(model, BayesianNetwork):
            raise TypeError(
                f"Model expected type: BayesianNetwork, got type: {type(model)}"
            )
        super(BayesianModelInference, self).__init__(model)
        self._initialize_structures()

        self.topological_order = list(nx.topological_sort(model))

    def pre_compute_reduce(self, variable):
        """
        Get probability arrays for a node as function of conditional dependencies

        Internal function used for Bayesian networks, eg. in BayesianModelSampling
        and BayesianModelProbability.

        Parameters
        ----------
        variable: Bayesian Model Node
            node of the Bayesian network

        Returns
        -------
        dict: dictionary with probability array for node
            as function of conditional dependency values
        """
        variable_cpd = self.model.get_cpds(variable)
        variable_evid = variable_cpd.variables[:0:-1]
        cached_values = {}

        for state_combination in itertools.product(
            *[range(self.cardinality[var]) for var in variable_evid]
        ):
            states = list(zip(variable_evid, state_combination))
            cached_values[state_combination] = variable_cpd.reduce(
                states, inplace=False, show_warnings=False
            ).values

        return cached_values

    @staticmethod
    def _reduce(variable_cpd, variable_evid, sc_values):
        """
        Method to compute values of the `variable_cpd` when it it reduced on
        `variable_evid` with states `sc_values`. This is a stripped down
        version DiscreteFactor.reduce to only compute the values for faster
        runtime.

        Parameters
        ----------
        variable_cpd: Instance of pgmpy.factors.discrete.TabularCPD
            The CPD that will be reduced.

        variable_evid: list
            List of variable name that need to be reduced.

        sc_values: list
            list of list of states (corresponding to variable_evid) to which to
            reduce the CPD.

        Returns
        -------
        list: List of np.array with each element representing the reduced
                values correponding to the states in sc_values.
        """
        return_values = []
        for sc in sc_values:
            sc = list(zip(variable_evid, sc))
            try:
                values = [
                    (var, variable_cpd.get_state_no(var, state_name))
                    for var, state_name in sc
                ]
            except KeyError:
                values = sc
            slice_ = [slice(None)] * len(variable_cpd.variables)
            for var, state in values:
                var_index = variable_cpd.variables.index(var)
                slice_[var_index] = state
            return_values.append(variable_cpd.values[tuple(slice_)])
        return return_values

    def pre_compute_reduce_maps(self, variable, state_combinations=None, n_jobs=-1):
        """
        Get probability array-maps for a node as function of conditional dependencies

        Internal function used for Bayesian networks, eg. in BayesianModelSampling
        and BayesianModelProbability.

        Parameters
        ----------
        variable: Bayesian Model Node
            node of the Bayesian network

        state_combinations: list (default=None)
            List of tuple of state combinations for which to compute the reductions maps.

        n_jobs: int (default: -1)
            The number of CPU cores to use. By default uses all.

        Returns
        -------
        dict: dictionary with probability array-index for node as function of conditional dependency values,
            dictionary with mapping of probability array-index to probability array.
        """
        variable_cpd = self.model.get_cpds(variable)
        variable_evid = variable_cpd.variables[:0:-1]

        if state_combinations is None:
            state_combinations = [
                tuple(sc)
                for sc in itertools.product(
                    *[range(self.cardinality[var]) for var in variable_evid]
                )
            ]

        # Comptue batch sizes and call _reduce in parallel.
        if n_jobs == -1:
            n_jobs = os.cpu_count()
        batch_size = math.ceil(len(state_combinations) / n_jobs)

        weights_list = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(BayesianModelInference._reduce)(
                variable_cpd,
                variable_evid,
                state_combinations[
                    (batch_size * i) : min(
                        batch_size * (i + 1), len(state_combinations)
                    )
                ],
            )
            for i in range((len(state_combinations) // batch_size) + 1)
        )

        weights_list = np.array(list(itertools.chain(*weights_list)))
        unique_weights, weights_indices = np.unique(
            weights_list, axis=0, return_inverse=True
        )

        # convert weights to index; make mapping of state to index
        state_to_index = dict(zip(state_combinations, weights_indices))

        # make mapping of index to weights
        index_to_weight = dict(enumerate(unique_weights))

        # return mappings of state to index, and index to weight
        return state_to_index, index_to_weight

class BayesianModelSampling(BayesianModelInference):
    """
    Class for sampling methods specific to Bayesian Models

    Parameters
    ----------
    model: instance of BayesianNetwork
        model on which inference queries will be computed
    """

    def __init__(self, model):
        super(BayesianModelSampling, self).__init__(model)

    def forward_sample(
        self,
        size=1,
        include_latents=False,
        seed=None,
        show_progress=True,
        partial_samples=None,
        n_jobs=-1,
    ):
        """
        Generates sample(s) from joint distribution of the bayesian network.

        Parameters
        ----------
        size: int
            size of sample to be generated

        include_latents: boolean
            Whether to include the latent variable values in the generated samples.

        seed: int (default: None)
            If a value is provided, sets the seed for numpy.random.

        show_progress: boolean
            Whether to show a progress bar of samples getting generated.

        partial_samples: pandas.DataFrame
            A pandas dataframe specifying samples on some of the variables in the model. If
            specified, the sampling procedure uses these sample values, instead of generating them.

        n_jobs: int (default: -1)
            The number of CPU cores to use. Default uses all cores.

        Returns
        -------
        sampled: pandas.DataFrame
            The generated samples

        Examples
        --------

        """
        sampled = pd.DataFrame(columns=list(self.model.nodes()))

        if show_progress:
            pbar = tqdm(self.topological_order)
        else:
            pbar = self.topological_order

        if seed is not None:
            np.random.seed(seed)

        for node in pbar:
            if show_progress:
                pbar.set_description(f"Generating for node: {node}")
            # If values specified in partial_samples, use them. Else generate the values.
            if (partial_samples is not None) and (node in partial_samples.columns):
                sampled[node] = partial_samples.loc[:, node].values
            else:
                cpd = self.model.get_cpds(node)
                states = range(self.cardinality[node])
                evidence = cpd.variables[:0:-1]
                if evidence:
                    evidence_values = np.vstack([sampled[i] for i in evidence])

                    unique, inverse = np.unique(
                        evidence_values.T, axis=0, return_inverse=True
                    )
                    unique = [tuple(u) for u in unique]
                    state_to_index, index_to_weight = self.pre_compute_reduce_maps(
                        variable=node, state_combinations=unique, n_jobs=n_jobs
                    )
                    weight_index = np.array([state_to_index[u] for u in unique])[
                        inverse
                    ]
                    sampled[node] = sample_discrete_maps(
                        states, weight_index, index_to_weight, size
                    )
                else:
                    weights = cpd.values
                    sampled[node] = sample_discrete(states, weights, size)

        samples_df = _return_samples(sampled, self.state_names_map)
        if not include_latents:
            samples_df.drop(self.model.latents, axis=1, inplace=True)
        return samples_df

    def rejection_sample(
        self,
        evidence=[],
        size=1,
        include_latents=False,
        seed=None,
        show_progress=True,
        partial_samples=None,
    ):
        """
        Generates sample(s) from joint distribution of the bayesian network,
        given the evidence.

        Parameters
        ----------
        evidence: list of `pgmpy.factor.State` namedtuples
            None if no evidence

        size: int
            size of sample to be generated

        include_latents: boolean
            Whether to include the latent variable values in the generated samples.

        seed: int (default: None)
            If a value is provided, sets the seed for numpy.random.

        show_progress: boolean
            Whether to show a progress bar of samples getting generated.

        partial_samples: pandas.DataFrame
            A pandas dataframe specifying samples on some of the variables in the model. If
            specified, the sampling procedure uses these sample values, instead of generating them.

        Returns
        -------
        sampled: pandas.DataFrame
            The generated samples

        Examples
        --------

        """

        if seed is not None:
            np.random.seed(seed)

        # If no evidence is given, it is equivalent to forward sampling.
        if len(evidence) == 0:
            return self.forward_sample(size=size, include_latents=include_latents)

        # Setup array to be returned
        sampled = pd.DataFrame()
        prob = 1
        i = 0

        # Do the sampling by generating samples from forward sampling and rejecting the
        # samples which do not match our evidence. Keep doing until we have enough
        # samples.
        if show_progress:
            pbar = tqdm(total=size)

        while i < size:
            _size = int(((size - i) / prob) * 1.5)

            # If partial_samples is specified, can only generate < partial_samples.shape[0] number of samples
            # at a time. For simplicity, just generate the same size as partial_samples.shape[0].
            if partial_samples is not None:
                _size = partial_samples.shape[0]

            _sampled = self.forward_sample(
                size=_size,
                include_latents=True,
                show_progress=False,
                partial_samples=partial_samples,
            )

            for var, state in evidence:
                _sampled = _sampled[_sampled[var] == state]

            prob = max(len(_sampled) / _size, 0.01)
            sampled = pd.concat([sampled, _sampled], axis=0, join="outer").iloc[
                :size, :
            ]
            i += _sampled.shape[0]

            if show_progress:
                # Update at maximum to `size`
                comp = _sampled.shape[0] if i < size else size - (i - _sampled.shape[0])
                pbar.update(comp)

        if show_progress:
            pbar.close()

        sampled = sampled.reset_index(drop=True)
        if not include_latents:
            sampled.drop(self.model.latents, axis=1, inplace=True)
        return sampled

    def likelihood_weighted_sample(
        self,
        evidence=[],
        size=1,
        include_latents=False,
        seed=None,
        show_progress=True,
        n_jobs=-1,
    ):
        """
        Generates weighted sample(s) from joint distribution of the bayesian
        network, that comply with the given evidence.
        'Probabilistic Graphical Model Principles and Techniques', Koller and
        Friedman, Algorithm 12.2 pp 493.

        Parameters
        ----------
        evidence: list of `pgmpy.factor.State` namedtuples
            None if no evidence

        size: int
            size of sample to be generated

        include_latents: boolean
            Whether to include the latent variable values in the generated samples.

        seed: int (default: None)
            If a value is provided, sets the seed for numpy.random.

        show_progress: boolean
            Whether to show a progress bar of samples getting generated.

        n_jobs: int (default: -1)
            The number of CPU cores to use. Default uses all cores.

        Returns
        -------
        sampled: A pandas.DataFrame
            The generated samples with corresponding weights

        Examples
        --------

        """
        if seed is not None:
            np.random.seed(seed)

        # Convert evidence state names to number
        evidence = [
            (var, self.model.get_cpds(var).get_state_no(var, state))
            for var, state in evidence
        ]

        # Prepare the return dataframe
        sampled = pd.DataFrame(columns=list(self.model.nodes()))
        sampled["_weight"] = np.ones(size)
        evidence_dict = dict(evidence)

        if show_progress:
            pbar = tqdm(self.topological_order)
        else:
            pbar = self.topological_order

        # Do the sampling
        for node in pbar:
            if show_progress:
                pbar.set_description(f"Generating for node: {node}")

            cpd = self.model.get_cpds(node)
            states = range(self.cardinality[node])
            evidence = cpd.get_evidence()

            if evidence:
                evidence_values = np.vstack([sampled[i] for i in evidence])

                unique, inverse = np.unique(
                    evidence_values.T, axis=0, return_inverse=True
                )
                unique = [tuple(u) for u in unique]
                state_to_index, index_to_weight = self.pre_compute_reduce_maps(
                    variable=node, state_combinations=unique, n_jobs=n_jobs
                )
                weight_index = np.array([state_to_index[tuple(u)] for u in unique])[
                    inverse
                ]

                if node in evidence_dict:
                    evidence_value = evidence_dict[node]
                    sampled[node] = evidence_value
                    sampled.loc[:, "_weight"] *= np.array(
                        list(
                            map(
                                lambda i: index_to_weight[weight_index[i]][
                                    evidence_value
                                ],
                                range(size),
                            )
                        )
                    )
                else:
                    sampled[node] = sample_discrete_maps(
                        states, weight_index, index_to_weight, size
                    )
            else:
                if node in evidence_dict:
                    sampled[node] = evidence_dict[node]
                    sampled.loc[:, "_weight"] *= np.array(
                        list(
                            map(lambda _: cpd.values[evidence_dict[node]], range(size))
                        )
                    )
                else:
                    sampled[node] = sample_discrete(states, cpd.values, size)

        # Postprocess the samples: Change state numbers to names, remove latents.
        samples_df = _return_samples(sampled, self.state_names_map)
        if not include_latents:
            samples_df.drop(self.model.latents, axis=1, inplace=True)
        return samples_df


class GibbsSampling(MarkovChain):
    """
    Class for performing Gibbs sampling.

    Parameters
    ----------
    model: BayesianNetwork or MarkovNetwork
        Model from which variables are inherited and transition probabilities computed.

    Examples
    --------
    """

    def __init__(self, model=None):
        super(GibbsSampling, self).__init__()
        if isinstance(model, BayesianNetwork):
            self._get_kernel_from_bayesian_model(model)
        elif isinstance(model, MarkovNetwork):
            self._get_kernel_from_markov_model(model)

    def _get_kernel_from_bayesian_model(self, model):
        """
        Computes the Gibbs transition models from a Bayesian Network.
        'Probabilistic Graphical Model Principles and Techniques', Koller and
        Friedman, Section 12.3.3 pp 512-513.

        Parameters
        ----------
        model: BayesianNetwork
            The model from which probabilities will be computed.
        """
        self.variables = np.array(model.nodes())
        self.latents = model.latents
        self.cardinalities = {
            var: model.get_cpds(var).variable_card for var in self.variables
        }

        for var in self.variables:
            other_vars = [v for v in self.variables if var != v]
            other_cards = [self.cardinalities[v] for v in other_vars]
            kernel = {}
            factors = [cpd.to_factor() for cpd in model.cpds if var in cpd.scope()]
            factor = factor_product(*factors)
            scope = set(factor.scope())
            for tup in itertools.product(*[range(card) for card in other_cards]):
                states = [State(v, s) for v, s in zip(other_vars, tup) if v in scope]
                reduced_factor = factor.reduce(states, inplace=False)
                kernel[tup] = reduced_factor.values / sum(reduced_factor.values)
            self.transition_models[var] = kernel

    def _get_kernel_from_markov_model(self, model):
        """
        Computes the Gibbs transition models from a Markov Network.
        'Probabilistic Graphical Model Principles and Techniques', Koller and
        Friedman, Section 12.3.3 pp 512-513.

        Parameters
        ----------
        model: MarkovNetwork
            The model from which probabilities will be computed.
        """
        self.variables = np.array(model.nodes())
        self.latents = model.latents
        factors_dict = {var: [] for var in self.variables}
        for factor in model.get_factors():
            for var in factor.scope():
                factors_dict[var].append(factor)

        # Take factor product
        factors_dict = {
            var: factor_product(*factors) if len(factors) > 1 else factors[0]
            for var, factors in factors_dict.items()
        }
        self.cardinalities = {
            var: factors_dict[var].get_cardinality([var])[var] for var in self.variables
        }

        for var in self.variables:
            other_vars = [v for v in self.variables if var != v]
            other_cards = [self.cardinalities[v] for v in other_vars]
            kernel = {}
            factor = factors_dict[var]
            scope = set(factor.scope())
            for tup in itertools.product(*[range(card) for card in other_cards]):
                states = [
                    State(first_var, s)
                    for first_var, s in zip(other_vars, tup)
                    if first_var in scope
                ]
                reduced_factor = factor.reduce(states, inplace=False)
                kernel[tup] = reduced_factor.values / sum(reduced_factor.values)
            self.transition_models[var] = kernel

    def sample(self, start_state=None, size=1, seed=None, include_latents=False):
        """
        Sample from the Markov Chain.

        Parameters
        ----------
        start_state: dict or array-like iterable
            Representing the starting states of the variables. If None is passed, a random start_state is chosen.

        size: int
            Number of samples to be generated.

        seed: int (default: None)
            If a value is provided, sets the seed for numpy.random.

        include_latents: boolean
            Whether to include the latent variable values in the generated samples.

        Returns
        -------
        sampled: pandas.DataFrame
            The generated samples

        Examples
        --------

        """
        if start_state is None and self.state is None:
            self.state = self.random_state()
        elif start_state is not None:
            self.set_start_state(start_state)

        if seed is not None:
            np.random.seed(seed)

        types = [(str(var_name), "int") for var_name in self.variables]
        sampled = np.zeros(size, dtype=types).view(np.recarray)
        sampled[0] = tuple(st for var, st in self.state)
        for i in tqdm(range(size - 1)):
            for j, (var, st) in enumerate(self.state):
                other_st = tuple(st for v, st in self.state if var != v)
                next_st = sample_discrete(
                    list(range(self.cardinalities[var])),
                    self.transition_models[var][other_st],
                )[0]
                self.state[j] = State(var, next_st)
            sampled[i + 1] = tuple(st for var, st in self.state)

        samples_df = _return_samples(sampled)
        if not include_latents:
            samples_df.drop(self.latents, axis=1, inplace=True)
        return samples_df

    def generate_sample(
        self, start_state=None, size=1, include_latents=False, seed=None
    ):
        """
        Generator version of self.sample

        Returns
        -------
        List of State namedtuples, representing the assignment to all variables of the model.

        Examples
        --------
        """
        if seed is not None:
            np.random.seed(seed)

        if start_state is None and self.state is None:
            self.state = self.random_state()
        elif start_state is not None:
            self.set_start_state(start_state)

        for i in range(size):
            for j, (var, st) in enumerate(self.state):
                other_st = tuple(st for v, st in self.state if var != v)
                next_st = sample_discrete(
                    list(range(self.cardinalities[var])),
                    self.transition_models[var][other_st],
                )[0]
                self.state[j] = State(var, next_st)
            if include_latents:
                yield self.state[:]
            else:
                yield [s for s in self.state if i not in self.latents]
