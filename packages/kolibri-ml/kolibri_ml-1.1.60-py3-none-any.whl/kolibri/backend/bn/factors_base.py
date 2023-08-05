from abc import abstractmethod
from functools import reduce
from itertools import chain

from opt_einsum import contract


class BaseFactor(object):
    """
    Base class for Factors. Any Factor implementation should inherit this class.
    """

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def is_valid_cpd(self):
        pass


def factor_product(*args):
    """
    Returns factor product over `args`.

    Parameters
    ----------
    args: `BaseFactor` instances.
        factors to be multiplied

    Returns
    -------
    BaseFactor: `BaseFactor` representing factor product over all the `BaseFactor` instances in args.

    Examples
    --------
    """
    if not all(isinstance(phi, BaseFactor) for phi in args):
        raise TypeError("Arguments must be factors")
    # Check if all of the arguments are of the same type
    elif len(set(map(type, args))) != 1:
        raise NotImplementedError(
            "All the args are expected to be instances of the same factor class."
        )

    if len(args) == 1:
        return args[0].copy()
    else:
        return reduce(lambda phi1, phi2: phi1 * phi2, args)


def factor_sum_product(output_vars, factors):
    """
    For a given set of factors: `args` returns the result of $ \sum_{var \not \in output_vars} \prod \textit{args} $.

    Parameters
    ----------
    output_vars: list, iterable
        List of variable names on which the output factor is to be defined. Variable which are present in any of the factors
        but not in output_vars will be marginalized out.

    factors: list, iterable
        List of DiscreteFactor objects on which to perform the sum product operation.

    Returns
    -------
    pgmpy.factor.discrete.DiscreteFactor: A DiscreteFactor object on `output_vars`.

    Examples
    --------
    <DiscreteFactor representing phi(HISTORY:2) at 0x7f240556b970>
    """
    state_names = {}
    for phi in factors:
        state_names.update(phi.state_names)

    einsum_expr = []
    for phi in factors:
        einsum_expr.append(phi.values)
        einsum_expr.append(phi.variables)
    values = contract(*einsum_expr, output_vars, optimize="greedy")

    from kolibri.backend.bn.DiscreteFactor import DiscreteFactor

    return DiscreteFactor(
        variables=output_vars,
        cardinality=values.shape,
        values=values,
        state_names={var: state_names[var] for var in output_vars},
    )


def factor_divide(phi1, phi2):
    """
    Returns `DiscreteFactor` representing `phi1 / phi2`.

    Parameters
    ----------
    phi1: Factor
        The Dividend.

    phi2: Factor
        The Divisor.

    Returns
    -------
    DiscreteFactor: `DiscreteFactor` representing factor division `phi1 / phi2`.

    Examples
    --------
    """
    if not isinstance(phi1, BaseFactor) or not isinstance(phi2, BaseFactor):
        raise TypeError("phi1 and phi2 should be factors instances")

    # Check if all of the arguments are of the same type
    elif type(phi1) != type(phi2):
        raise NotImplementedError(
            "All the args are expected to be instances of the same factor class."
        )

    return phi1.divide(phi2, inplace=False)
