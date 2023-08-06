from kolibri.backend.bn.bnlearn import make_DAG
from kolibri.backend.bn.structure.no_tears import from_pandas
from kolibri.backend.bn.structure import *
from kolibri.backend.bn.BayesianNetwork import BayesianNetwork
from kolibri.backend.bn.structure.structure_model import StructureModel
import networkx as nx
import numpy as np


def learn_structure_from_data(data, method_type='nt', threshold=0.1, rank=3):

    columns=list(data.columns.values)
    nt=None

    if method_type=='nt':
        # Learn the structure using the NOTEARS algorithm
        structure = from_pandas(data, w_threshold=threshold)
        # Create a StructureModel from the learned structure
        nt = StructureModel()
        nt.add_edges_from(structure.edges())

        # Convert the learned structure into a DAG by breaking cycles
        while not nx.is_directed_acyclic_graph(nt):
            cycles = nx.simple_cycles(nt)
            min_weight_edge = None
            min_weight = float('inf')
            for cycle in cycles:
                for i in range(len(cycle)):
                    source, target = cycle[i], cycle[(i + 1) % len(cycle)]
                    weight = np.abs(structure[source][target]['weight'])
                    if weight < min_weight:
                        min_weight = weight
                        min_weight_edge = (source, target)
            if min_weight_edge:
                nt.remove_edge(*min_weight_edge)

        return make_DAG(list(nt.edges))
    elif method_type=='lr':
        nt=NotearsLowRank(w_threshold=threshold)
    elif method_type=='nl':
        nt=NotearsNonlinear(w_threshold=threshold)
    elif method_type=='gl':
        nt=GolemModel()

    if method_type=='lr':
        nt.learn(data.values, columns=columns, rank=rank)



    edges=[]
    for s, source  in enumerate(nt.causal_matrix):
        for t, target in enumerate(source):
            if target>0:
                edges.append((columns[s], columns[t]))


    return make_DAG(edges)


