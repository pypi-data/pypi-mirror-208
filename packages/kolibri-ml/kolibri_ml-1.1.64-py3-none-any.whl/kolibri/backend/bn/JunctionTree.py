#!/usr/bin/env python3

import networkx as nx

from kolibri.backend.bn.UndirectedGraph import UndirectedGraph


class JunctionTree(UndirectedGraph):
    """
    Class for representing Junction Tree.

    Junction tree is undirected graph where each node represents a clique
    (list, tuple or set of nodes) and edges represent sepset between two cliques.
    Each sepset in G separates the variables strictly on one side of edge to
    other.

    Parameters
    ----------
    data: input graph
        Data to initialize graph. If data=None (default) an empty graph is
        created. The data is an edge list.

    Examples
    --------
    Create an empty JunctionTree with no nodes and no edges

    """

    def __init__(self, ebunch=None):
        super(JunctionTree, self).__init__()
        if ebunch:
            self.add_edges_from(ebunch)

    def add_edge(self, u, v, **kwargs):
        """
        Add an edge between two clique nodes.

        Parameters
        ----------
        u, v: nodes
            Nodes can be any list or set or tuple of nodes forming a clique.

        Examples
        --------
        """
        if u in self.nodes() and v in self.nodes() and nx.has_path(self, u, v):
            raise ValueError(
                f"Addition of edge between {str(u)} and {str(v)} forms a cycle breaking the properties of Junction Tree"
            )

        super(JunctionTree, self).add_edge(u, v, **kwargs)

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
        errors. In the same time also updates the cardinalities of all the random
        variables.

        * Checks if clique potentials are defined for all the cliques or not.
        * Check for running intersection property is not done explicitly over
          here as it done in the add_edges method.

        Returns
        -------
        check: boolean
            True if all the checks are passed
        """
        if not nx.is_connected(self):
            raise ValueError("The Junction Tree defined is not fully connected.")

        return super(JunctionTree, self).check_model()

    def copy(self):
        """
        Returns a copy of JunctionTree.

        Returns
        -------
        JunctionTree : copy of JunctionTree

        Examples
        --------
        """
        copy = JunctionTree(self.edges())
        copy.add_nodes_from(self.nodes())
        if self.factors:
            factors_copy = [factor.copy() for factor in self.factors]
            copy.add_factors(*factors_copy)
        return copy
