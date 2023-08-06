import numpy as np
from scipy import integrate

from kolibri.backend.bn.distributions import BaseDistribution


class CustomDistribution(BaseDistribution):
    def __init__(self, variables, distribution, *args, **kwargs):
        """
        Class for representing custom continuous distributions.

        Parameters
        ----------
        variables: list or array-like
            The variables for which the distribution is defined.

        distribution: function
            The probability density function of the distribution.

        Examples
        --------

        """
        if not isinstance(variables, (list, tuple, np.ndarray)):
            raise TypeError(
                f"variables: Expected type: iterable, got: {type(variables)}"
            )

        if len(set(variables)) != len(variables):
            raise ValueError("Multiple variables can't have the same name")

        self._variables = list(variables)
        self._pdf = distribution

    @property
    def pdf(self):
        """
        Returns the Probability Density Function of the distribution.

        Returns
        -------
        function: The probability density function of the distribution

        Examples
        --------

        """
        return self._pdf

    @pdf.setter
    def pdf(self, f):
        self._pdf = f

    @property
    def variables(self):
        """
        Returns the scope of the distribution.

        Returns
        -------
        list: List of variables on which the distribution is defined.

        Examples
        --------

        """
        return self._variables

    @variables.setter
    def variables(self, value):
        self._variables = value

    def assignment(self, *x):
        """
        Returns the probability value of the PDF at the given parameter values.

        Parameters
        ----------
        *x: values of all variables of this distribution,
            collective defining a point at which the probability value is to be computed.

        Returns
        -------
        float: The probability value at the point.

        Examples
        --------

        """
        return self.pdf(*x)

    def copy(self):
        """
        Returns a copy of the CustomDistribution instance.

        Returns
        -------
        CustomDistribution object: copy of the instance

        Examples
        --------

        """
        return CustomDistribution(self.variables, self.pdf)

    # TODO: Discretize methods need to be fixed for this to work
    def discretize(self, method, *args, **kwargs):
        """
        Discretizes the continuous distribution into discrete
        probability masses using specified method.

        Parameters
        ----------
        method: string, BaseDiscretizer instance
            A Discretizer Class from pgmpy.factors.discretize

        *args, **kwargs: values
            The parameters to be given to the Discretizer Class.

        Returns
        -------
        An n-D array or a DiscreteFactor object according to the discretiztion
        method used.

        Examples
        --------
        """
        super(CustomDistribution, self).discretize(method, *args, **kwargs)

    def reduce(self, values, inplace=True):
        """
        Reduces the factor to the context of the given variable values.

        Parameters
        ----------
        values: list, array-like
            A list of tuples of the form (variable_name, variable_value).

        inplace: boolean
            If inplace=True it will modify the factor itself, else would return
            a new CustomDistribution object.

        Returns
        -------
        CustomDistribution or None:
                    if inplace=True (default) returns None
                    if inplace=False returns a new CustomDistribution instance.

        Examples
        --------

        """
        if not isinstance(values, (list, tuple, np.ndarray)):
            raise TypeError(f"variables: Expected type: iterable, got: {type(values)}")

        for var, value in values:
            if var not in self.variables:
                raise ValueError(f"{var} not in scope.")

        phi = self if inplace else self.copy()

        var_to_remove = [var for var, value in values]
        var_to_keep = [var for var in self.variables if var not in var_to_remove]

        reduced_var_index = [
            (self.variables.index(var), value) for var, value in values
        ]
        pdf = self.pdf

        def reduced_pdf(*args, **kwargs):
            reduced_args = list(args)
            reduced_kwargs = kwargs.copy()

            if reduced_args:
                for index, val in reduced_var_index:
                    reduced_args.insert(index, val)
            if reduced_kwargs:
                for variable, val in values:
                    reduced_kwargs[variable] = val
            if reduced_args and reduced_kwargs:
                reduced_args = [
                    arg for arg in reduced_args if arg not in reduced_kwargs.values()
                ]

            return pdf(*reduced_args, **reduced_kwargs)

        phi.variables = var_to_keep
        phi._pdf = reduced_pdf

        if not inplace:
            return phi

    def marginalize(self, variables, inplace=True):
        """
        Marginalize the distribution with respect to the given variables.

        Parameters
        ----------
        variables: list, array-like
            List of variables to be removed from the marginalized distribution.

        inplace: boolean
            If inplace=True it will modify the factor itself, else would return
            a new CustomDistribution instance.

        Returns
        -------
        Marginalized distribution or None:
                if inplace=True (default) returns None
                if inplace=False returns a new CustomDistribution instance.

        Examples
        --------

        """
        if len(variables) == 0:
            raise ValueError("Shouldn't be calling marginalize over no variable.")

        if not isinstance(variables, (list, tuple, np.ndarray)):
            raise TypeError(
                f"variables: Expected type iterable, got: {type(variables)}"
            )

        for var in variables:
            if var not in self.variables:
                raise ValueError(f"{var} not in scope.")

        phi = self if inplace else self.copy()

        all_var = [var for var in self.variables]
        var_to_keep = [var for var in self.variables if var not in variables]
        reordered_var_index = [all_var.index(var) for var in variables + var_to_keep]
        pdf = phi._pdf

        # The arguments need to be reordered because integrate.nquad
        # integrates the first n-arguments of the function passed.

        def reordered_pdf(*args):
            # ordered_args restores the original order as it was in self.variables
            ordered_args = [
                args[reordered_var_index.index(index_id)]
                for index_id in range(len(all_var))
            ]
            return pdf(*ordered_args)

        def marginalized_pdf(*args):
            return integrate.nquad(
                reordered_pdf,
                [[-np.inf, np.inf] for i in range(len(variables))],
                args=args,
            )[0]

        phi._pdf = marginalized_pdf
        phi.variables = var_to_keep

        if not inplace:
            return phi

    def normalize(self, inplace=True):
        """
        Normalizes the pdf of the distribution so that it
        integrates to 1 over all the variables.

        Parameters
        ----------
        inplace: boolean
            If inplace=True it will modify the distribution itself, else would return
            a new distribution.

        Returns
        -------
        CustomDistribution or None:
             if inplace=True (default) returns None
             if inplace=False returns a new CustomDistribution instance.

        Examples
        --------

        """
        phi = self if inplace else self.copy()
        pdf = self.pdf

        pdf_mod = integrate.nquad(pdf, [[-np.inf, np.inf] for var in self.variables])[0]

        phi._pdf = lambda *args: pdf(*args) / pdf_mod

        if not inplace:
            return phi

    def is_valid_cpd(self):
        return np.isclose(
            integrate.nquad(self.pdf, [[-np.inf, np.inf] for var in self.variables])[0],
            1,
        )

    def _operate(self, other, operation, inplace=True):
        """
        Gives the CustomDistribution operation (product or divide) with
        the other distribution.

        Parameters
        ----------
        other: CustomDistribution
            The CustomDistribution to be multiplied.

        operation: str
            'product' for multiplication operation and 'divide' for
            division operation.

        inplace: boolean
            If inplace=True it will modify the factor itself, else would return
            a new distribution.

        Returns
        -------
        CustomDistribution or None:
                        if inplace=True (default) returns None
                        if inplace=False returns a new `CustomDistribution` instance.

        """
        if not isinstance(other, CustomDistribution):
            raise TypeError(
                f"CustomDistribution objects can only be multiplied or divided with another CustomDistribution object. Got {type(other)}, expected: CustomDistribution."
            )

        phi = self if inplace else self.copy()
        pdf = self.pdf
        self_var = [var for var in self.variables]

        modified_pdf_var = self_var + [
            var for var in other.variables if var not in self_var
        ]

        def modified_pdf(*args):
            self_pdf_args = list(args[: len(self_var)])
            other_pdf_args = [
                args[modified_pdf_var.index(var)] for var in other.variables
            ]

            if operation == "product":
                return pdf(*self_pdf_args) * other._pdf(*other_pdf_args)
            if operation == "divide":
                return pdf(*self_pdf_args) / other._pdf(*other_pdf_args)

        phi.variables = modified_pdf_var
        phi._pdf = modified_pdf

        if not inplace:
            return phi

    def product(self, other, inplace=True):
        """
        Gives the CustomDistribution product with the other distribution.

        Parameters
        ----------
        other: CustomDistribution
            The CustomDistribution to be multiplied.

        Returns
        -------
        CustomDistribution or None:
                        if inplace=True (default) returns None
                        if inplace=False returns a new `CustomDistribution` instance.

        Example
        -------

        """
        return self._operate(other, "product", inplace)

    def divide(self, other, inplace=True):
        """
        Gives the CustomDistribution divide with the other factor.

        Parameters
        ----------
        other: CustomDistribution
            The CustomDistribution to be multiplied.

        Returns
        -------
        CustomDistribution or None:
                        if inplace=True (default) returns None
                        if inplace=False returns a new `CustomDistribution` instance.

        Example
        -------

        """
        if set(other.variables) - set(self.variables):
            raise ValueError("Scope of divisor should be a subset of dividend")

        return self._operate(other, "divide", inplace)

    def __mul__(self, other):
        return self.product(other, inplace=False)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.divide(other, inplace=False)

    __div__ = __truediv__
