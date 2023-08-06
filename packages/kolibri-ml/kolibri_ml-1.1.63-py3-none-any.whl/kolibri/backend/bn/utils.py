from typing import List

import pandas as pd
from kolibri.backend.bn.factors_base import factor_product
from kolibri.backend.bn.CPD import TabularCPD


def pd_to_tabular_cpd(cpd: pd.DataFrame) -> TabularCPD:
    """
    Converts a dataframe to a pgmpy TabularCPD
    Args:
        cpd: Pandas dataframe containing conditional probability distribution (CPD)
    Returns:
        Corresponding tabular CPD
    """
    parents = cpd.columns.names

    if (parents is None) or all(el is None for el in parents):
        parents = None
        parents_cardinalities = None
        state_names = {}
    else:
        parents_cardinalities = [len(level) for level in cpd.columns.levels]
        state_names = {
            name: list(levels)
            for name, levels in zip(cpd.columns.names, cpd.columns.levels)
        }

    node_cardinality = cpd.shape[0]
    node_name = cpd.index.name
    state_names[node_name] = list(cpd.index)

    return TabularCPD(
        node_name,
        node_cardinality,
        cpd.values,
        evidence=parents,
        evidence_card=parents_cardinalities,
        state_names=state_names,
    )


def tabular_cpd_to_pd(tab_cpd: TabularCPD) -> pd.DataFrame:
    """
    Converts a pgmpy TabularCPD to a Pandas dataframe
    Args:
        tab_cpd: Tabular conditional probability distribution (CPD)
    Returns:
        Corresponding Pandas dataframe
    """
    node_states = tab_cpd.state_names
    iterables = [sorted(node_states[var]) for var in tab_cpd.variables[1:]]
    cols = [""]

    if iterables:
        cols = pd.MultiIndex.from_product(iterables, names=tab_cpd.variables[1:])

    tab_df = pd.DataFrame(
        tab_cpd.values.reshape(
            len(node_states[tab_cpd.variable]),
            max(1, len(cols)),
        )
    )
    tab_df[tab_cpd.variable] = sorted(node_states[tab_cpd.variable])
    tab_df.set_index([tab_cpd.variable], inplace=True)
    tab_df.columns = cols
    return tab_df


def cpd_multiplication(
    cpds: List[pd.DataFrame], normalize: bool = True
) -> pd.DataFrame:
    """
    Multiplies CPDs represented as pandas.DataFrame
    It does so by converting to PGMPY's TabularCPDs and calling a product function designed for these.
    It then convert the table back to pandas.DataFrame
    Important note: the result will be a CPD and the index will be the index of the first element on the list `cpds`
    Args:
        cpds: _cpds to multiply
        normalize: wether to normalise the columns, so that each column sums to 1
    Returns:
        Pandas dataframe containing the resulting product, looking like a cpd
    """
    cpds_pgmpy = [pd_to_tabular_cpd(df) for df in cpds]
    product_pgmpy = factor_product(*cpds_pgmpy)  # type: TabularCPD

    if normalize:
        product_pgmpy.normalize()

    return tabular_cpd_to_pd(product_pgmpy)