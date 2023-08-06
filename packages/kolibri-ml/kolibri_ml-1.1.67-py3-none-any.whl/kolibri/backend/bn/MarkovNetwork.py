#!/usr/bin/env python3
import itertools
from collections import defaultdict

import networkx as nx
import numpy as np
from networkx.algorithms.components import connected_components

from kolibri.backend.bn.UndirectedGraph import UndirectedGraph
from kolibri.backend.bn.factors_base import factor_product
from kolibri.backend.bn.Independencies import Independencies


class MarkovNetwork(UndirectedGraph):
    """
    Base class for markov model.

    A MarkovNetwork stores nodes and edges with potentials

    MarkovNetwork holds undirected edges.

    Parameters
    ----------
    data : input graph
        Data to initialize graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, or any
        NetworkX graph object.

    Examples
    --------

    """

    def __init__(self, ebunch=None, latents=[]):
        super(MarkovNetwork, self).__init__()
        if ebunch:
            self.add_edges_from(ebunch)
        self.factors = []
        self.latents = latents

    def add_edge(self, u, v, **kwargs):
        """
        Add an edge between u and v.

        The nodes u and v will be automatically added if they are
        not already in the graph

        Parameters
        ----------
        u,v : nodes
            Nodes can be any hashable Python object.

        Examples
        --------
        """
        # check that there is no self loop.
        if u != v:
            super(MarkovNetwork, self).add_edge(u, v, **kwargs)
        else:
            raise ValueError("Self loops are not allowed")

    def add_factors(self, *factors):
        """
        Associate a factor to the graph.
        See factors class for the order of potential values

        Parameters
        ----------
        *factor: pgmpy.factors.factors object
            A factor object on any subset of the variables of the model which
            is to be associated with the model.

        Returns
        -------
        None

        Examples
        --------
        """
        for factor in factors:
            if set(factor.variables) - set(factor.variables).intersection(
                set(self.nodes())
            ):
                raise ValueError("Factors defined on variable not in the model", factor)

            self.factors.append(factor)

    def get_factors(self, node=None):
        """
        Returns all the factors containing the node. If node is not specified
        returns all the factors that have been added till now to the graph.

        Parameters
        ----------
        node: any hashable python object (optional)
           The node whose factor we want. If node is not specified

        Examples
        --------
        """
        if node:
            if node not in self.nodes():
                raise ValueError("Node not present in the Undirected Graph")
            node_factors = []
            for factor in self.factors:
                if node in factor.scope():
                    node_factors.append(factor)
            return node_factors
        else:
            return self.factors

    def remove_factors(self, *factors):
        """
        Removes the given factors from the added factors.

        Examples
        --------
        """
        for factor in factors:
            self.factors.remove(factor)

    def get_cardinality(self, node=None):
        """
        Returns the cardinality of the node. If node is not specified returns
        a dictionary with the given variable as keys and their respective cardinality
        as values.

        Parameters
        ----------
        node: any hashable python object (optional)
            The node whose cardinality we want. If node is not specified returns a
            dictionary with the given variable as keys and their respective cardinality
            as values.

        Examples
        --------
        """
        if node:
            for factor in self.factors:
                for variable, cardinality in zip(factor.scope(), factor.cardinality):
                    if node == variable:
                        return cardinality
        else:
            cardinalities = defaultdict(int)
            for factor in self.factors:
                for variable, cardinality in zip(factor.scope(), factor.cardinality):
                    cardinalities[variable] = cardinality
            return cardinalities

    @property
    def states(self):
        """
        Returns a dictionary mapping each node to its list of possible states.

        Returns
        -------
        state_dict: dict
            Dictionary of nodes to possible states
        """
        state_names_list = [phi.state_names for phi in self.factors]
        state_dict = {
            node: states for d in state_names_list for node, states in d.items()
        }
        return state_dict

    def check_model(self):
        """
        Check the model for various errors. This method checks for the following
        errors -

        * Checks if the cardinalities of all the variables are consistent across all the factors.
        * Factors are defined for all the random variables.

        Returns
        -------
        check: boolean
            True if all the checks are passed
        """
        cardinalities = self.get_cardinality()
        for factor in self.factors:
            for variable, cardinality in zip(factor.scope(), factor.cardinality):
                if cardinalities[variable] != cardinality:
                    raise ValueError(
                        f"Cardinality of variable {variable} not matching among factors"
                    )
                if len(self.nodes()) != len(cardinalities):
                    raise ValueError("Factors for all the variables not defined")
            for var1, var2 in itertools.combinations(factor.variables, 2):
                if var2 not in self.neighbors(var1):
                    raise ValueError("DiscreteFactor inconsistent with the model.")
        return True

    def triangulate(self, heuristic="H6", order=None, inplace=False):
        """
        Triangulate the graph.

        If order of deletion is given heuristic algorithm will not be used.

        Parameters
        ----------
        heuristic: H1 | H2 | H3 | H4 | H5 | H6
            The heuristic algorithm to use to decide the deletion order of
            the variables to compute the triangulated graph.
            Let X be the set of variables and X(i) denotes the i-th variable.

            * S(i) - The size of the clique created by deleting the variable.
            * E(i) - Cardinality of variable X(i).
            * M(i) - Maximum size of cliques given by X(i) and its adjacent nodes.
            * C(i) - Sum of size of cliques given by X(i) and its adjacent nodes.

            The heuristic algorithm decide the deletion order if this way:

            * H1 - Delete the variable with minimal S(i).
            * H2 - Delete the variable with minimal S(i)/E(i).
            * H3 - Delete the variable with minimal S(i) - M(i).
            * H4 - Delete the variable with minimal S(i) - C(i).
            * H5 - Delete the variable with minimal S(i)/M(i).
            * H6 - Delete the variable with minimal S(i)/C(i).

        order: list, tuple (array-like)
            The order of deletion of the variables to compute the triagulated
            graph. If order is given heuristic algorithm will not be used.

        inplace: True | False
            if inplace is true then adds the edges to the object from
            which it is called else returns a new object.

        References
        ----------
        http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.56.3607

        Examples
        --------
        """
        self.check_model()

        if self.is_triangulated():
            if inplace:
                return
            else:
                return self

        graph_copy = nx.Graph(self.edges())
        edge_set = set()

        def _find_common_cliques(cliques_list):
            """
            Finds the common cliques among the given set of cliques for
            corresponding node.
            """
            common = set([tuple(x) for x in cliques_list[0]])
            for i in range(1, len(cliques_list)):
                common = common & set([tuple(x) for x in cliques_list[i]])
            return list(common)

        def _find_size_of_clique(clique, cardinalities):
            """
            Computes the size of a clique.

            Size of a clique is defined as product of cardinalities of all the
            nodes present in the clique.
            """
            return list(
                map(lambda x: np.prod([cardinalities[node] for node in x]), clique)
            )

        def _get_cliques_dict(node):
            """
            Returns a dictionary in the form of {node: cliques_formed} of the
            node along with its neighboring nodes.

            clique_dict_removed would be containing the cliques created
            after deletion of the node
            clique_dict_node would be containing the cliques created before
            deletion of the node
            """
            graph_working_copy = nx.Graph(graph_copy.edges())
            neighbors = list(graph_working_copy.neighbors(node))
            graph_working_copy.add_edges_from(itertools.combinations(neighbors, 2))
            clique_dict = nx.cliques_containing_node(
                graph_working_copy, nodes=([node] + neighbors)
            )
            graph_working_copy.remove_node(node)
            clique_dict_removed = nx.cliques_containing_node(
                graph_working_copy, nodes=neighbors
            )
            return clique_dict, clique_dict_removed

        if not order:
            order = []

            cardinalities = self.get_cardinality()
            for index in range(self.number_of_nodes()):
                # S represents the size of clique created by deleting the
                # node from the graph
                S = {}
                # M represents the size of maximum size of cliques given by
                # the node and its adjacent node
                M = {}
                # C represents the sum of size of the cliques created by the
                # node and its adjacent node
                C = {}
                for node in set(graph_copy.nodes()) - set(order):
                    clique_dict, clique_dict_removed = _get_cliques_dict(node)
                    S[node] = _find_size_of_clique(
                        _find_common_cliques(list(clique_dict_removed.values())),
                        cardinalities,
                    )[0]
                    common_clique_size = _find_size_of_clique(
                        _find_common_cliques(list(clique_dict.values())), cardinalities
                    )
                    M[node] = np.max(common_clique_size)
                    C[node] = np.sum(common_clique_size)

                if heuristic == "H1":
                    node_to_delete = min(S, key=S.get)

                elif heuristic == "H2":
                    S_by_E = {key: S[key] / cardinalities[key] for key in S}
                    node_to_delete = min(S_by_E, key=S_by_E.get)

                elif heuristic == "H3":
                    S_minus_M = {key: S[key] - M[key] for key in S}
                    node_to_delete = min(S_minus_M, key=S_minus_M.get)

                elif heuristic == "H4":
                    S_minus_C = {key: S[key] - C[key] for key in S}
                    node_to_delete = min(S_minus_C, key=S_minus_C.get)

                elif heuristic == "H5":
                    S_by_M = {key: S[key] / M[key] for key in S}
                    node_to_delete = min(S_by_M, key=S_by_M.get)

                else:
                    S_by_C = {key: S[key] / C[key] for key in S}
                    node_to_delete = min(S_by_C, key=S_by_C.get)

                order.append(node_to_delete)

        graph_copy = nx.Graph(self.edges())
        for node in order:
            for edge in itertools.combinations(graph_copy.neighbors(node), 2):
                graph_copy.add_edge(edge[0], edge[1])
                edge_set.add(edge)
            graph_copy.remove_node(node)

        if inplace:
            for edge in edge_set:
                self.add_edge(edge[0], edge[1])
            return self

        else:
            graph_copy = MarkovNetwork(self.edges())
            for edge in edge_set:
                graph_copy.add_edge(edge[0], edge[1])
            return graph_copy


    def markov_blanket(self, node):
        """
        Returns a markov blanket for a random variable.

        Markov blanket is the neighboring nodes of the given node.

        Examples
        --------
        """
        return self.neighbors(node)

    def get_local_independencies(self, latex=False):
        """
        Returns all the local independencies present in the markov model.

        Local independencies are the independence assertion in the form of
        .. math:: {X \perp W - {X} - MB(X) | MB(X)}
        where MB is the markov blanket of all the random variables in X

        Parameters
        ----------
        latex: boolean
            If latex=True then latex string of the indepedence assertion would
            be created

        Examples
        --------

        """
        local_independencies = Independencies()

        all_vars = set(self.nodes())
        for node in self.nodes():
            markov_blanket = set(self.markov_blanket(node))
            rest = all_vars - set([node]) - markov_blanket
            try:
                local_independencies.add_assertions(
                    [node, list(rest), list(markov_blanket)]
                )
            except ValueError:
                pass

        local_independencies.reduce()

        if latex:
            return local_independencies.latex_string()
        else:
            return local_independencies

    def to_bayesian_model(self):
        """
        Creates a Bayesian Model which is a minimum I-Map for this markov model.

        The ordering of parents may not remain constant. It would depend on the
        ordering of variable in the junction tree (which is not constant) all the
        time. Also, if the model is not connected, the connected components are
        treated as separate models, converted, and then joined together.

        Examples
        --------

        """
        from kolibri.backend.bn.BayesianNetwork import BayesianNetwork

        # If the graph is not connected, treat them as separate models and join them together in the end.
        bms = []
        for node_set in connected_components(self):
            bm = BayesianNetwork()
            var_clique_dict = defaultdict(tuple)
            var_order = []

            subgraph = self.subgraph(node_set)

            # Create a junction tree from the markov model.
            # Creation of clique tree involves triangulation, finding maximal cliques
            # and creating a tree from these cliques
            junction_tree = MarkovNetwork(subgraph.edges()).to_junction_tree()

            # create an ordering of the nodes based on the ordering of the clique
            # in which it appeared first
            root_node = next(iter(junction_tree.nodes()))
            bfs_edges = nx.bfs_edges(junction_tree, root_node)
            for node in root_node:
                var_clique_dict[node] = root_node
                var_order.append(node)
            for edge in bfs_edges:
                clique_node = edge[1]
                for node in clique_node:
                    if not var_clique_dict[node]:
                        var_clique_dict[node] = clique_node
                        var_order.append(node)

            # create a bayesian model by adding edges from parent of node to node as
            # par(x_i) = (var(c_k) - x_i) \cap {x_1, ..., x_{i-1}}
            for node_index in range(len(var_order)):
                node = var_order[node_index]
                node_parents = (set(var_clique_dict[node]) - set([node])).intersection(
                    set(var_order[:node_index])
                )
                bm.add_edges_from([(parent, node) for parent in node_parents])
                # TODO : Convert factor into CPDs
            bms.append(bm)

        # Join the bms in a single model.
        final_bm = BayesianNetwork()
        for bm in bms:
            final_bm.add_edges_from(bm.edges())
            final_bm.add_nodes_from(bm.nodes())
        return final_bm

    def get_partition_function(self):
        """
        Returns the partition function for a given undirected graph.

        A partition function is defined as

        .. math:: \sum_{X}(\prod_{i=1}^{m} \phi_i)

        where m is the number of factors present in the graph
        and X are all the random variables present.

        Examples
        --------
        """
        self.check_model()

        factor = self.factors[0]
        factor = factor_product(
            factor, *[self.factors[i] for i in range(1, len(self.factors))]
        )
        if set(factor.scope()) != set(self.nodes()):
            raise ValueError("DiscreteFactor for all the random variables not defined.")

        return np.sum(factor.values)

    def copy(self):
        """
        Returns a copy of this Markov Model.

        Returns
        -------
        MarkovNetwork: Copy of this Markov model.

        Examples
        --------

        """
        clone_graph = MarkovNetwork(self.edges())
        clone_graph.add_nodes_from(self.nodes())

        if self.factors:
            factors_copy = [factor.copy() for factor in self.factors]
            clone_graph.add_factors(*factors_copy)

        return clone_graph
