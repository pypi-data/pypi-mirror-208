


"""
Visualize the residuals between predicted and actual data for regression problems
"""
import sklearn.tree
from scipy.stats import probplot
from sklearn.feature_selection import RFE
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import learning_curve as sk_learning_curve
from sklearn.model_selection import validation_curve as sk_validation_curve
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

from kolibri.config import TaskType
from logging import getLogger
import pandas as pd
from sklearn.manifold import TSNE
from dtreeviz.trees import *


logger=getLogger()
try:
    # Only available in Matplotlib >= 2.0.2
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    make_axes_locatable = None

import matplotlib.pyplot as plt
from kolibri.visualizations.utils import make_legend, memoized,draw_identity_line, LINE_COLOR, DEFAULT_TRAIN_SIZES, get_colors, get_param_name_and_range
import scipy as sp



PALETTES = {
    # "name": ['blue', 'green', 'red', 'maroon', 'yellow', 'cyan']
    # The yellowbrick default palette
    "yellowbrick": ["#0272a2", "#9fc377", "#ca0b03", "#a50258", "#d7c703", "#88cada"],
    # The following are from ColorBrewer
    "accent": ["#386cb0", "#7fc97f", "#f0027f", "#beaed4", "#ffff99", "#fdc086"],
    "dark": ["#7570b3", "#66a61e", "#d95f02", "#e7298a", "#e6ab02", "#1b9e77"],
    "pastel": ["#cbd5e8", "#b3e2cd", "#fdcdac", "#f4cae4", "#fff2ae", "#e6f5c9"],
    "bold": ["#377eb8", "#4daf4a", "#e41a1c", "#984ea3", "#ffff33", "#ff7f00"],
    "muted": ["#80b1d3", "#8dd3c7", "#fb8072", "#bebada", "#ffffb3", "#fdb462"],
    # The reset colors back to the original mpl color codes
    "reset": [
        "#0000ff",
        "#008000",
        "#ff0000",
        "#bf00bf",
        "#bfbf00",
        "#00bfbf",
        "#000000",
    ],
    # Colorblind colors
    "colorblind": ["#0072B2", "#009E73", "#D55E00", "#CC79A7", "#F0E442", "#56B4E9"],
    "sns_colorblind": [
        "#0072B2",
        "#009E73",
        "#D55E00",
        "#CC79A7",
        "#F0E442",
        "#56B4E9",
    ],
    # The following are Seaborn colors
    "sns_deep": ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"],
    "sns_muted": ["#4878CF", "#6ACC65", "#D65F5F", "#B47CC7", "#C4AD66", "#77BEDB"],
    "sns_pastel": ["#92C6FF", "#97F0AA", "#FF9F9A", "#D0BBFF", "#FFFEA3", "#B0E0E6"],
    "sns_bright": ["#003FFF", "#03ED3A", "#E8000B", "#8A2BE2", "#FFC400", "#00D7FF"],
    "sns_dark": ["#001C7F", "#017517", "#8C0900", "#7600A1", "#B8860B", "#006374"],
    # Other palettes
    "flatui": ["#34495e", "#2ecc71", "#e74c3c", "#9b59b6", "#f4d03f", "#3498db"],
    "paired": [
        "#a6cee3",
        "#1f78b4",
        "#b2df8a",
        "#33a02c",
        "#fb9a99",
        "#e31a1c",
        "#cab2d6",
        "#6a3d9a",
        "#ffff99",
        "#b15928",
        "#fdbf6f",
        "#ff7f00",
    ],
    "set1": [
        "#377eb8",
        "#4daf4a",
        "#e41a1c",
        "#984ea3",
        "#ffff33",
        "#ff7f00",
        "#a65628",
        "#f781bf",
        "#999999",
    ],
    # colors extracted from this blog post during pycon2017:
    # http://lewisandquark.tumblr.com/
    "neural_paint": [
        "#167192",
        "#6e7548",
        "#c5a2ab",
        "#00ccff",
        "#de78ae",
        "#ffcc99",
        "#3d3f42",
        "#ffffcc",
    ],
}

##########################################################################
## Residuals Plots
##########################################################################


class RegressionPlots():
    """
    A residual plot shows the residuals on the vertical axis and the
    independent variable on the horizontal axis.

    If the points are randomly dispersed around the horizontal axis, a linear
    regression model is appropriate for the data; otherwise, a non-linear
    model is more appropriate.

    Parameters
    ----------
    estimator : a Scikit-Learn regressor
        Should be an instance of a regressor, otherwise will raise a
        YellowbrickTypeError exception on instantiation.
        If the estimator is not fitted, it is fit when the visualizer is fitted,
        unless otherwise specified by ``is_fitted``.

    ax : matplotlib Axes, default: None
        The axes to plot the figure on. If None is passed in the current axes
        will be used (or generated if required).

    hist : {True, False, None, 'density', 'frequency'}, default: True
        Draw a histogram showing the distribution of the residuals on the
        right side of the figure. Requires Matplotlib >= 2.0.2.
        If set to 'density', the probability density function will be plotted.
        If set to True or 'frequency' then the frequency will be plotted.

    qqplot : {True, False}, default: False
        Draw a Q-Q plot on the right side of the figure, comparing the quantiles
        of the residuals against quantiles of a standard normal distribution.
        Q-Q plot and histogram of residuals can not be plotted simultaneously,
        either `hist` or `qqplot` has to be set to False.

    train_color : color, default: 'b'
        Residuals for training data are ploted with this color but also
        given an opacity of 0.5 to ensure that the test data residuals
        are more visible. Can be any matplotlib color.

    test_color : color, default: 'g'
        Residuals for test data are plotted with this color. In order to
        create generalizable models, reserved test data residuals are of
        the most analytical interest, so these points are highlighted by
        having full opacity. Can be any matplotlib color.

    line_color : color, default: dark grey
        Defines the color of the zero error line, can be any matplotlib color.

    train_alpha : float, default: 0.75
        Specify a transparency for traininig data, where 1 is completely opaque
        and 0 is completely transparent. This property makes densely clustered
        points more visible.

    test_alpha : float, default: 0.75
        Specify a transparency for test data, where 1 is completely opaque
        and 0 is completely transparent. This property makes densely clustered
        points more visible.

    is_fitted : bool or str, default='auto'
        Specify if the wrapped estimator is already fitted. If False, the estimator
        will be fit when the visualizer is fit, otherwise, the estimator will not be
        modified. If 'auto' (default), a helper method will check if the estimator
        is fitted before fitting it again.

    kwargs : dict
        Keyword arguments that are passed to the base class and may influence
        the visualization as defined in other Visualizers.

    Attributes
    ----------

    train_score_ : float
        The R^2 score that specifies the goodness of fit of the underlying
        regression model to the training data.

    test_score_ : float
        The R^2 score that specifies the goodness of fit of the underlying
        regression model to the test data.

    Examples
    --------

    Notes
    -----
    ResidualsPlot is a ScoreVisualizer, meaning that it wraps a model and
    its primary entry point is the ``score()`` method.

    The residuals histogram feature requires matplotlib 2.0.2 or greater.
    """

    def __init__(
        self,
        y_true,
        y_pred,
        model_name,
        X=None,
        y=None,
        estimator=None,
        features_names=None,
        hist=True,
        qqplot=False,
        train_color="b",
        test_color="g",
        scoring="neg_mean_absolute_error",
        shared_limits=True,
        identity=True,
        draw_threshold=True,
            logx=False
    ):

        # TODO: allow more scatter plot arguments for train and test points
        # See #475 (RE: ScatterPlotMixin)
        self.colors = {
            "train_point": train_color,
            "test_point": test_color,
            "point": None,
            "line": LINE_COLOR,
        }

        self.name=model_name
        self.hist = hist
        if self.hist not in {True, "density", "frequency", None, False}:
            raise Exception(
                "'{}' is an invalid argument for hist, use None, True, "
                "False, 'density', or 'frequency'".format(hist)
            )

        self.qqplot = qqplot
        if self.qqplot not in {True, False}:
            raise Exception(
                "'{}' is an invalid argument for qqplot, use True, "
                " or False".format(hist)
            )

        if self.hist in {True, "density", "frequency"} and self.qqplot in {True}:
            raise Exception(
                "Set either hist or qqplot to False, can not plot "
                "both of them simultaneously."
            )

        # Store labels and colors for the legend ordered by call
        self.alpha=0.75
        self._labels, self._colors = [], []
        self.alphas = {"train_point":self.alpha, "test_point": self.alpha}

        self.y_true=y_true
        self.y_pred=y_pred
        self.shared_limits = shared_limits
        self.identity=identity
        self.draw_threshold=draw_threshold
        self._model = LinearRegression()

        self.X=X
        self.y=y
        self.estimator=estimator

        # Validate the train sizes
        train_sizes = np.asarray(DEFAULT_TRAIN_SIZES)
        if train_sizes.ndim != 1:
            raise Exception(
                "must specify array of train sizes, '{}' is not valid".format(
                    repr(train_sizes)
                )
            )

        # Set the metric parameters to be used later

        self.train_sizes = train_sizes

        self.scoring = scoring
        self.logx = logx
        if features_names is not None:
            self.features_names=features_names
        elif self.X is not None:
            self.features_names=[f"column_{c}" for c in range(self.X.shape[1])]

    @memoized
    def hax(self):
        """
        Returns the histogram axes, creating it only on demand.
        """
        if make_axes_locatable is None:
            raise Exception(
                (
                    "residuals histogram requires matplotlib 2.0.2 or greater "
                    "please upgrade matplotlib or set hist=False on the visualizer"
                )
            )

        divider = make_axes_locatable(self.ax)

        hax = divider.append_axes("right", size=1, pad=0.1, sharey=self.ax)
        hax.yaxis.tick_right()
        hax.grid(False, axis="x")

        return hax
    @memoized
    def qqax(self):
        """
        Returns the Q-Q plot axes, creating it only on demand.
        """
        if make_axes_locatable is None:
            raise Exception(
                (
                    "residuals histogram requires matplotlib 2.0.2 or greater "
                    "please upgrade matplotlib or set qqplot=False on the visualizer"
                )
            )

        divider = make_axes_locatable(self.ax)

        qqax = divider.append_axes("right", size=2, pad=0.25, sharey=self.ax)
        qqax.yaxis.tick_right()

        return qqax

    @property
    def test_score_(self):
        from sklearn.metrics import r2_score
        return r2_score(self.y_true, self.y_pred)

    def residuals(self):
        """
        Draw the residuals against the predicted value for the specified split.
        It is best to draw the training split first, then the test split so
        that the test split (usually smaller) is above the training split;
        particularly if the histogram is turned on.


        Returns
        -------
        ax : matplotlib Axes
            The axis with the plotted figure
        """

        self.fig, self.ax=plt.subplots()

        if self.hist in {True, "density", "frequency"}:
            self.hax  # If hist is True, test the version availability

        if self.qqplot in {True}:
            self.qqax  # If qqplot is True, test the version availability


        color = self.colors["test_point"]

        label = "Test $R^2 = {:0.3f}$".format(self.test_score_)
        alpha = self.alphas["test_point"]

        # Update the legend information
        self._labels.append(label)
        self._colors.append(color)

        residuals=self.y_pred-self.y_true
        # Draw the residuals scatter plot
        self.ax.scatter(self.y_pred, residuals, c=color, alpha=alpha, label=label)

        # Add residuals histogram
        if self.hist in {True, "frequency"}:
            self.hax.hist(residuals, bins=50, orientation="horizontal", color=color)
        elif self.hist == "density":
            self.hax.hist(
                residuals, bins=50, orientation="horizontal", density=True, color=color
            )

        # Add residuals histogram
        if self.qqplot in {True}:
            osm, osr = probplot(residuals, dist="norm", fit=False)

            self.qqax.scatter(osm, osr, c=color, alpha=alpha, label=label)

        # Ensure the current axes is always the main residuals axes

        plt.title="Residuals for {} Model".format(self.name)
        make_legend(self._labels, self._colors, loc="best", frameon=True)
        # Create a full line across the figure at zero error.
        self.ax.axhline(y=0, c=self.colors["line"])

        # Set the axes labels
        self.ax.set_ylabel("Residuals")
        self.ax.set_xlabel("Predicted Value")

        # Finalize the histogram axes
        if self.hist:
            self.hax.axhline(y=0, c=self.colors["line"])
            self.hax.set_xlabel("Distribution")

        # Finalize the histogram axes
        if self.qqplot:
            self.qqax.set_title("Q-Q plot")
            self.qqax.set_xlabel("Theoretical quantiles")
            self.qqax.set_ylabel("Observed quantiles")


        return self.fig

    def errors(self):
        """
        Parameters
        ----------
        y : ndarray or Series of length n
            An array or series of target or class values

        y_pred : ndarray or Series of length n
            An array or series of predicted target values

        Returns
        -------
        ax : matplotlib Axes
            The axis with the plotted figure
        """
        self.fig, self.ax=plt.subplots()

        score_label = "$R^2$"

        label = "{} $ = {:0.3f}$".format(score_label, self.test_score_)

        self.ax.scatter(
            self.y_true, self.y_pred, c=self.colors["point"], alpha=self.alpha, label=label
        )

        # Set the axes limits based on the overall max/min values of
        # concatenated X and Y data
        # NOTE: shared_limits will be accounted for in finalize()
        if self.shared_limits is True:
            self.ax.set_xlim(min(min(self.y_true), min(self.y_pred)), max(max(self.y_true), max(self.y_pred)))
            self.ax.set_ylim(self.ax.get_xlim())
        plt.title="Prediction Error for {}".format(self.name)

        # Square the axes to ensure a 45 degree line
        if self.shared_limits:
            # Get the current limits
            ylim = self.ax.get_ylim()
            xlim = self.ax.get_xlim()

            # Find the range that captures all data
            bounds = (min(ylim[0], xlim[0]), max(ylim[1], xlim[1]))

            # Reset the limits
            self.ax.set_xlim(bounds)
            self.ax.set_ylim(bounds)

            # Ensure the aspect ratio is square
            self.ax.set_aspect("equal", adjustable="box")

        # Draw the 45 degree line
        if self.identity:
            draw_identity_line(
                ax=self.ax,
                ls="--",
                lw=2,
                c=self.colors["line"],
                alpha=0.5,
                label="identity",
            )

        # Set the axes labels
        self.ax.set_ylabel(r"$\hat{y}$")
        self.ax.set_xlabel(r"$y$")

        # Set the legend
        # Note: it would be nice to be able to use the manual_legend utility
        # here, since if the user sets a low alpha value, the R2 color in the
        # legend will also become more translucent. Unfortunately this is a
        # bit tricky because adding a manual legend here would override the
        # best fit and 45 degree line legend components. In particular, the
        # best fit is plotted in draw because it depends on y and y_pred.
        self.ax.legend(loc="best", frameon=True)
        return self.fig


    def _fit_linear_regression(self):
        """
        Computes the leverage of X and uses the residuals of a
        ``sklearn.linear_model.LinearRegression`` to compute the Cook's Distance of each
        observation in X, their p-values and the number of outliers defined by the
        number of observations supplied.

        Parameters
        ----------
        X : array-like, 2D
            The exogenous design matrix, e.g. training data.

        y : array-like, 1D
            The endogenous response variable, e.g. target data.

        Returns
        -------
        self : CooksDistance
            Fit returns the visualizer instance.
        """

        if self.X is None or self.y is None:
            raise Exception("X and y values connot be null")
        # Fit a linear model to X and y to compute MSE
        self._model.fit(self.X, self.y)

        # Leverage is computed as the diagonal of the projection matrix of X
        # TODO: whiten X before computing leverage
        leverage = (self.X * np.linalg.pinv(self.X).T).sum(1)

        # Compute the rank and the degrees of freedom of the OLS model
        rank = np.linalg.matrix_rank(self.X)
        df = self.X.shape[0] - rank

        # Compute the MSE from the residuals
        residuals = self.y_true - self._model.predict(self.X)
        mse = np.dot(residuals, residuals) / df

        # Compute Cook's distance
        residuals_studentized = residuals / np.sqrt(mse) / np.sqrt(1 - leverage)
        self.distance_ = residuals_studentized ** 2 / self.X.shape[1]
        self.distance_ *= leverage / (1 - leverage)

        # Compute the p-values of Cook's Distance
        # TODO: honestly this was done because it was only in the statsmodels
        # implementation... I have no idea what this is or why its important.
        self.p_values_ = sp.stats.f.sf(self.distance_, self.X.shape[1], df)

        # Compute the influence threshold rule of thumb
        self.influence_threshold_ = 4 / self.X.shape[0]
        self.outlier_percentage_ = (
            sum(self.distance_ > self.influence_threshold_) / self.X.shape[0]
        )

        self.outlier_percentage_ *= 100.0
        print(np.where(self.distance_>10*self.influence_threshold_))
        return

    def cooks(self):
        """
        Draws a stem plot where each stem is the Cook's Distance of the instance at the
        index specified by the x axis. Optionaly draws a threshold line.
        """

        self.fig, self.ax=plt.subplots()

        self._fit_linear_regression()
        # Draw a stem plot with the influence for each instance
        linefmt = "C0-"
        markerfmt = ","
        _, _, baseline = self.ax.stem(
            self.distance_, linefmt=linefmt, markerfmt=markerfmt,
            use_line_collection=True
        )

        # No padding on either side of the instance index
        self.ax.set_xlim(0, len(self.distance_))

        # Draw the threshold for most influential points
        if self.draw_threshold:
            label = r"{:0.2f}% > $I_t$ ($I_t=\frac {{4}} {{n}}$)".format(
                self.outlier_percentage_
            )
            self.ax.axhline(
                self.influence_threshold_,
                ls="--",
                label=label,
                c=baseline.get_color(),
                lw=baseline.get_linewidth(),
            )

        # Set the title and axis labels
        plt.title="Cook's Distance Outlier Detection"
        self.ax.set_xlabel("instance index")
        self.ax.set_ylabel("influence (I)")

        # Only add the legend if the influence threshold has been plotted
        if self.draw_threshold:
            self.ax.legend(loc="best", frameon=True)

        return self.fig

    def _fit_rfe(self):
        """
        Fits the RFECV with the wrapped model to the specified data and draws
        the rfecv curve with the optimal number of features found.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vector, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape (n_samples) or (n_samples, n_features), optional
            Target relative to X for classification or regression.

        Returns
        -------
        self : instance
            Returns the instance of the RFECV visualizer.
        """
        n_features = self.X.shape[1]


        # Create the RFE model
        rfe = RFE(self.estimator, step=1)
        self.n_feature_subsets_ = np.arange(1, n_features + 1, 1)
        print(len(self.n_feature_subsets_))

        # Create the cross validation params
        # TODO: handle random state
        cv_params = {"cv": None, "scoring":"neg_mean_absolute_error"}
        # Perform cross-validation for each feature subset
        scores = []
        for n_features_to_select in self.n_feature_subsets_:
            print("processing: "+str(n_features_to_select))
            rfe.set_params(n_features_to_select=n_features_to_select)
            scores.append(cross_val_score(rfe, self.X, self.y, **cv_params))

        # Convert scores to array
        self.cv_scores_ = np.array(scores)

        # Find the best RFE model
        bestidx = self.cv_scores_.mean(axis=1).argmax()
        self.n_features_ = self.n_feature_subsets_[bestidx]

        # Fit the final RFE model for the number of features
        self.rfe_estimator_ = rfe
        self.rfe_estimator_.set_params(n_features_to_select=self.n_features_)
        self.rfe_estimator_.fit(self.X, self.y)

        # Rewrap the visualizer to use the rfe estimator
        self._wrapped = self.rfe_estimator_

        # Hoist the RFE params to the visualizer
        self.support_ = self.rfe_estimator_.support_
        self.ranking_ = self.rfe_estimator_.ranking_

        return

    def rfe(self, **kwargs):
        """
        Renders the rfecv curve.
        """

        self.fig, self.ax=plt.subplots()

        self._fit_rfe()
        # Compute the curves
        x = self.n_feature_subsets_
        means = self.cv_scores_.mean(axis=1)
        sigmas = self.cv_scores_.std(axis=1)

        # Plot one standard deviation above and below the mean
        self.ax.fill_between(x, means - sigmas, means + sigmas, alpha=0.25)

        # Plot the curve
        self.ax.plot(x, means, "o-")

        # Plot the maximum number of features
        self.ax.axvline(
            self.n_features_,
            c="k",
            ls="--",
            label="n_features = {}\nscore = {:0.3f}".format(
                self.n_features_, self.cv_scores_.mean(axis=1).max()
            ),
        )
        plt.title="RFECV for {}".format(self.name)

        # Add the legend
        self.ax.legend(frameon=True, loc="best")

        # Set the axis labels
        self.ax.set_xlabel("Number of Features Selected")
        self.ax.set_ylabel("Score")
        return self.fig

    def _fit_learning(self):
        """
        Fits the learning curve with the wrapped model to the specified data.
        Draws training and test score curves and saves the scores to the
        estimator.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vector, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape (n_samples) or (n_samples, n_features), optional
            Target relative to X for classification or regression;
            None for unsupervised learning.

        Returns
        -------
        self : instance
            Returns the instance of the learning curve visualizer for use in
            pipelines and other sequential transformers.
        """
        # arguments to pass to sk_learning_curve
        sklc_kwargs = {
                "train_sizes": self.train_sizes,
                "cv":None,
                "scoring": self.scoring
        }

        # compute the learning curve and store the scores on the estimator
        curve = sk_learning_curve(self.estimator, self.X, self.y, **sklc_kwargs)
        self.train_sizes_, self.train_scores_, self.test_scores_ = curve

        # compute the mean and standard deviation of the training data
        self.train_scores_mean_ = np.mean(self.train_scores_, axis=1)
        self.train_scores_std_ = np.std(self.train_scores_, axis=1)

        # compute the mean and standard deviation of the test data
        self.test_scores_mean_ = np.mean(self.test_scores_, axis=1)
        self.test_scores_std_ = np.std(self.test_scores_, axis=1)

        return

    def learning(self, **kwargs):
        """
        Renders the training and test learning curves.
        """

        self.fig, self.ax=plt.subplots()

        self._fit_learning()
        # Specify the curves to draw and their labels
        labels = ("Training Score", "Cross Validation Score")
        curves = (
            (self.train_scores_mean_, self.train_scores_std_),
            (self.test_scores_mean_, self.test_scores_std_),
        )

        # Get the colors for the train and test curves
        colors = get_colors(n_colors=2)

        # Plot the fill betweens first so they are behind the curves.
        for idx, (mean, std) in enumerate(curves):
            # Plot one standard deviation above and below the mean
            self.ax.fill_between(
                self.train_sizes_, mean - std, mean + std, alpha=0.25, color=colors[idx]
            )

        # Plot the mean curves so they are in front of the variance fill
        for idx, (mean, _) in enumerate(curves):
            self.ax.plot(
                self.train_sizes_, mean, "o-", color=colors[idx], label=labels[idx]
            )
        plt.title="Learning Curve for {}".format(self.name)

        # Add the legend
        self.ax.legend(frameon=True, loc="best")

        # Set the axis labels
        self.ax.set_xlabel("Training Instances")
        self.ax.set_ylabel("Score")
        return self.fig

    def _fit_validation(self):
        """
        Fits the validation curve with the wrapped estimator and parameter
        array to the specified data. Draws training and test score curves and
        saves the scores to the visualizer.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vector, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape (n_samples) or (n_samples, n_features), optional
            Target relative to X for classification or regression;
            None for unsupervised learning.

        Returns
        -------
        self : instance
            Returns the instance of the validation curve visualizer for use in
            pipelines and other sequential transformers.
        """
        # arguments to pass to sk_validation_curve

        self.param_name, self.param_range=get_param_name_and_range(self.estimator.get_params(), task_type=TaskType.REGRESSION, nb_train_column=self.X.shape[1])
        skvc_kwargs = {
                "param_name":self.param_name,
                "param_range":self.param_range,
                "scoring": self.scoring,
                "n_jobs":-1
        }

        # compute the validation curve and store scores
        curve = sk_validation_curve(self.estimator, self.X, self.y, **skvc_kwargs)
        self.train_scores_, self.test_scores_ = curve

        # compute the mean and standard deviation of the training data
        self.train_scores_mean_ = np.mean(self.train_scores_, axis=1)
        self.train_scores_std_ = np.std(self.train_scores_, axis=1)

        # compute the mean and standard deviation of the test data
        self.test_scores_mean_ = np.mean(self.test_scores_, axis=1)
        self.test_scores_std_ = np.std(self.test_scores_, axis=1)

        return self

    def validation(self):
        """
        Renders the training and test curves.
        """

        self.fig, self.ax=plt.subplots()

        self._fit_validation()
        # Specify the curves to draw and their labels
        labels = ("Training Score", "Cross Validation Score")
        curves = (
            (self.train_scores_mean_, self.train_scores_std_),
            (self.test_scores_mean_, self.test_scores_std_),
        )

        # Get the colors for the train and test curves
        colors = get_colors(n_colors=2)

        # Plot the fill betweens first so they are behind the curves.
        for idx, (mean, std) in enumerate(curves):
            # Plot one standard deviation above and below the mean
            self.ax.fill_between(
                self.param_range, mean - std, mean + std, alpha=0.25, color=colors[idx]
            )

        # Plot the mean curves so they are in front of the variance fill
        for idx, (mean, _) in enumerate(curves):
            self.ax.plot(
                self.param_range, mean, '-d', color=colors[idx], label=labels[idx]
            )

        if self.logx:
            self.ax.set_xscale("log")

        plt.title="Validation Curve for {}".format(self.name)

        # Add the legend
        self.ax.legend(frameon=True, loc="best")

        # Set the axis labels
        self.ax.set_xlabel(self.param_name)
        self.ax.set_ylabel("score")
        return self.fig


    def feature(self):
        self.fig, self.ax=plt.subplots()

        return self._feature(10)

    def feature_all(self):
        self.fig, self.ax=plt.subplots()

        return self._feature(self.X.shape[1])

    def _feature(self, n: int):
        variables = None
        temp_model = self.estimator
        if hasattr(self.estimator, "steps"):
            temp_model = self.estimator.steps[-1][1]
        if hasattr(temp_model, "coef_"):
            try:
                coef = temp_model.coef_.flatten()
                if len(coef) > self.X.shape[1]:
                    coef = coef[: self.X.shape[1]]
                variables = abs(coef)
            except Exception:
                pass
        if variables is None:
            logger.warning(
                "No coef_ found. Trying feature_importances_"
            )
            variables = abs(temp_model.feature_importances_)
        coef_df = pd.DataFrame(
            {
                "Variable": self.features_names,
                "Value": variables,
            }
        )
        sorted_df = (
            coef_df.sort_values(by="Value", ascending=False)
            .head(n)
            .sort_values(by="Value")
        )
        my_range = range(1, len(sorted_df.index) + 1)
        plt.hlines(
            y=my_range,
            xmin=0,
            xmax=sorted_df["Value"],
            color="skyblue",
        )
        plt.plot(sorted_df["Value"], my_range, "o")
        plt.yticks(my_range, sorted_df["Variable"])
        plt.title="Feature Importance Plot"
        plt.xlabel="Variable Importance"
        plt.ylabel="Features"
        # display.clear_output()
        return plt

    def tree(self, X=None, y=None):
        self.fig, self.ax=plt.subplots()

        reg = DecisionTreeRegressor(max_depth=2, random_state=42)
        reg.fit(self.X, self.y)

        if X is None or y is None:
            X=self.X
            y=np.array(self.y)
        viz = dtreeviz(reg,
                       x_data=X,
                       y_data=y,
                       feature_names=self.features_names,
                       title=f"Decision Tree - {self.name}",
                       show_node_labels=True)

        return viz

    def tsne(self, X=None, y=None):
        self.fig, self.ax=plt.subplots()

        if X is None or y is None:
            X=self.X
            y=self.y



        logger.info("Fitting TSNE()")

        X_embedded = TSNE(n_components=2,
                              perplexity=30,
#                              initialization="pca",
                              metric="cosine"
                              ).fit_transform(X)

        X = pd.DataFrame(X_embedded)

        logger.info("Rendering Visual")
#        import plotly.express as px

        df = X
        df['target']=y
        df['target'] =df['target'].astype(str)

        self.ax.scatter(df[0].values, df[1].values)

        plt.title="TSNE Projection of {} Documents".format(len(y))


        logger.info("Visual Rendered Successfully")

        return self.fig

    def umap(self, X=None, y=None):
        self.fig, self.ax=plt.subplots()

        import umap
        if X is None or y is None:
            X=self.X
            y=self.y

        reducer = umap.UMAP(n_components=2, n_jobs=1)
        logger.info("Fitting UMAP()")
        embedding = reducer.fit_transform(X)
        X = pd.DataFrame(embedding)


        df = X
        df['target']=[str(i) for i in y]
        df.columns=['CP1', 'CP2', 'target']



        self.ax.scatter(df['CP1'].values, df['CP2'].values)

        plt.title="UMAP Projection of {} Documents".format(len(y))



        logger.info("Visual Rendered Successfully")
        return self.fig

if __name__=="__main__":
    import numpy as np
    from sklearn.metrics import r2_score

    np.random.seed(42)

    n_samples, n_features = 200, 50
    X = np.random.randn(n_samples, n_features)
    true_coef = 3 * np.random.randn(n_features)
    # Threshold coefficients to render them non-negative
    true_coef[true_coef < 0] = 0
    y = np.dot(X, true_coef)

    # Add some noise
    y += 5 * np.random.normal(size=(n_samples,))
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
    from sklearn.linear_model import Lasso

    reg_nnls = LinearRegression(positive=True)
    y_pred_nnls = reg_nnls.fit(X_train, y_train).predict(X_test)
    plot=RegressionPlots(y_test,y_pred_nnls, "linear_regression", X=X, y=y, estimator=reg_nnls)
    plot.umap()

    print("")