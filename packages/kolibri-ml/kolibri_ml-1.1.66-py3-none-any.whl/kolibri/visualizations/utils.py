from os.path import abspath, dirname, join
import matplotlib.cm as cm
import numpy as np
import matplotlib as mpl
import warnings
from kolibri.config import TaskType

FILE_DIR = dirname(abspath(__file__))
DATA_DIR = join(FILE_DIR, "data")

MACOSKO_COLORS = {
    "Amacrine cells": "#A5C93D",
    "Astrocytes": "#8B006B",
    "Bipolar cells": "#2000D7",
    "Cones": "#538CBA",
    "Fibroblasts": "#8B006B",
    "Horizontal cells": "#B33B19",
    "Microglia": "#8B006B",
    "Muller glia": "#8B006B",
    "Pericytes": "#8B006B",
    "Retinal ganglion cells": "#C38A1F",
    "Rods": "#538CBA",
    "Vascular endothelium": "#8B006B",
}
ZEISEL_COLORS = {
    "Astroependymal cells": "#d7abd4",
    "Cerebellum neurons": "#2d74bf",
    "Cholinergic, monoaminergic and peptidergic neurons": "#9e3d1b",
    "Di- and mesencephalon neurons": "#3b1b59",
    "Enteric neurons": "#1b5d2f",
    "Hindbrain neurons": "#51bc4c",
    "Immature neural": "#ffcb9a",
    "Immune cells": "#768281",
    "Neural crest-like glia": "#a0daaa",
    "Oligodendrocytes": "#8c7d2b",
    "Peripheral sensory neurons": "#98cc41",
    "Spinal cord neurons": "#c52d94",
    "Sympathetic neurons": "#11337d",
    "Telencephalon interneurons": "#ff9f2b",
    "Telencephalon projecting neurons": "#fea7c1",
    "Vascular cells": "#3d672d",
}
MOUSE_10X_COLORS = {
    0: "#FFFF00",
    1: "#1CE6FF",
    2: "#FF34FF",
    3: "#FF4A46",
    4: "#008941",
    5: "#006FA6",
    6: "#A30059",
    7: "#FFDBE5",
    8: "#7A4900",
    9: "#0000A6",
    10: "#63FFAC",
    11: "#B79762",
    12: "#004D43",
    13: "#8FB0FF",
    14: "#997D87",
    15: "#5A0007",
    16: "#809693",
    17: "#FEFFE6",
    18: "#1B4400",
    19: "#4FC601",
    20: "#3B5DFF",
    21: "#4A3B53",
    22: "#FF2F80",
    23: "#61615A",
    24: "#BA0900",
    25: "#6B7900",
    26: "#00C2A0",
    27: "#FFAA92",
    28: "#FF90C9",
    29: "#B903AA",
    30: "#D16100",
    31: "#DDEFFF",
    32: "#000035",
    33: "#7B4F4B",
    34: "#A1C299",
    35: "#300018",
    36: "#0AA6D8",
    37: "#013349",
    38: "#00846F",
}

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
LINE_COLOR = "#111111"  # Colors for best fit lines, diagonals, etc.

# Default ticks for the learning curve train sizes
DEFAULT_TRAIN_SIZES = np.linspace(0.1, 1.0, 5)


from matplotlib import patches
from functools import wraps

import matplotlib.pyplot as plt
def memoized(fget):
    """
    Return a property attribute for new-style classes that only calls its
    getter on the first access. The result is stored and on subsequent
    accesses is returned, preventing the need to call the getter any more.

    Parameters
    ----------
    fget: function
        The getter method to memoize for subsequent access.

    See also
    --------
    python-memoized-property
        `python-memoized-property <https://github.com/estebistec/python-memoized-property>`_
    """
    attr_name = "_{0}".format(fget.__name__)

    @wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)


def get_color_cycle():
    """
    Returns the current color cycle from matplotlib.
    """
    cyl = mpl.rcParams["axes.prop_cycle"]
    # matplotlib 1.5 verifies that axes.prop_cycle *is* a cycler
    # but no garuantee that there's a `color` key.
    # so users could have a custom rcParams w/ no color...

    try:
        return [x["color"] for x in cyl]
    except KeyError:
        pass  # just return axes.color style below
    return mpl.rcParams["axes.color_cycle"]

def get_colors(n_colors=None, colormap=None, colors=None):
    """
    Generates a list of colors based on common color arguments, for example
    the name of a colormap or palette or another iterable of colors. The list
    is then truncated (or multiplied) to the specific number of requested
    colors.

    Parameters
    ----------
    n_colors : int, default: None
        Specify the length of the list of returned colors, which will either
        truncate or multiple the colors available. If None the length of the
        colors will not be modified.

    colormap : str, yellowbrick.style.palettes.ColorPalette, matplotlib.cm, default: None
        The name of the matplotlib color map with which to generate colors.

    colors : iterable, default: None
        A collection of colors to use specifically with the plot. Overrides
        colormap if both are specified.

    Returns
    -------
    colors : list
        A list of colors that can be used in matplotlib plots.

    Notes
    -----
    This function was originally based on a similar function in the pandas
    plotting library that has been removed in the new version of the library.
    """

    # Work with the colormap if specified and colors is not
    if colormap is not None and colors is None:
        # Must import here to avoid recursive import

        if isinstance(colormap, str):
            try:

                # try to get colormap from PALETTES first
                _colormap = PALETTES.get(colormap, None)

                if _colormap is None:

                    colormap = cm.get_cmap(colormap)
                    n_colors = n_colors or len(get_color_cycle())
                    _colors = list(map(colormap, np.linspace(0, 1, num=n_colors)))

                else:

                    _colors = colormap
                    n_colors = n_colors or len(_colors)

            except ValueError as e:

                raise Exception(e)


        # if matplotlib color palette is provided as colormap
        elif isinstance(colormap, mpl.colors.Colormap):
            n_colors = n_colors or len(get_color_cycle())
            _colors = list(map(colormap, np.linspace(0, 1, num=n_colors)))
        else:
            raise Exception(
                "Colormap type {} is not recognized. Possible types are: {}".format(
                    type(colormap),
                    ", ".join(
                        ["yellowbrick.style.ColorPalette,", "matplotlib.cm,", "str"]
                    ),
                )
            )

    # Work with the color list
    elif colors is not None:

        # Warn if both colormap and colors is specified.
        if colormap is not None:
            warnings.warn("both colormap and colors specified; using colors")

        _colors = list(colors)  # Ensure colors is a list

    # Get the default colors
    else:
        _colors = get_color_cycle()

    # Truncate or multiple the color list according to the number of colors
    if n_colors is not None and len(_colors) != n_colors:
        _colors = [_colors[idx % len(_colors)] for idx in np.arange(n_colors)]

    return _colors

def make_legend(labels, colors, **legend_kwargs):

    # Get access to the matplotlib Axes
    g = plt.gca()

    # Ensure that labels and colors are the same length to prevent odd behavior.
    if len(colors) != len(labels):
        raise Exception(
            "please specify the same number of colors as labels!"
        )

    # Create the legend handles with the associated colors and labels
    handles = [
        patches.Patch(color=color, label=label) for color, label in zip(colors, labels)
    ]

    # Return the Legend artist
    return g.legend(handles=handles, **legend_kwargs)

def draw_identity_line(ax=None, dynamic=True, **kwargs):
    """
    Draws a 45 degree identity line such that y=x for all points within the
    given axes x and y limits. This function also registeres a callback so
    that as the figure is modified, the axes are updated and the line remains
    drawn correctly.

    Parameters
    ----------

    ax : matplotlib Axes, default: None
        The axes to plot the figure on. If None is passed in the current axes
        will be used (or generated if required).

    dynamic : bool, default : True
        If the plot is dynamic, callbacks will be registered to update the
        identiy line as axes are changed.

    kwargs : dict
        Keyword arguments to pass to the matplotlib plot function to style the
        identity line.


    Returns
    -------

    ax : matplotlib Axes
        The axes with the line drawn on it.

    Notes
    -----

    .. seealso:: `StackOverflow discussion: Does matplotlib have a function for drawing diagonal lines in axis coordinates? <https://stackoverflow.com/questions/22104256/does-matplotlib-have-a-function-for-drawing-diagonal-lines-in-axis-coordinates>`_
    """

    # Get the current working axes
    ax = ax or plt.gca()

    # Define the standard line color
    if "c" not in kwargs and "color" not in kwargs:
        kwargs["color"] = LINE_COLOR

    # Define the standard opacity
    if "alpha" not in kwargs:
        kwargs["alpha"] = 0.5

    # Draw the identity line
    identity, = ax.plot([], [], **kwargs)

    # Define the callback
    def callback(ax):
        # Get the x and y limits on the axes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Set the bounding range of the line
        data = (max(xlim[0], ylim[0]), min(xlim[1], ylim[1]))
        identity.set_data(data, data)

    # Register the callback and return
    callback(ax)

    if dynamic:
        ax.callbacks.connect("xlim_changed", callback)
        ax.callbacks.connect("ylim_changed", callback)

    return ax


def get_param_name_and_range(model_params, task_type, nb_train_column):
    param_name = ""
    param_range = None

    if task_type == TaskType.CLASSIFICATION:

        # Catboost
        if "depth" in model_params:
            param_name = "depth"
            param_range = np.arange(1, 11)

        # SGD Classifier
        elif "l1_ratio" in model_params:
            param_name = "l1_ratio"
            param_range = np.arange(0, 1, 0.01)

        # tree based models
        elif "max_depth" in model_params:
            param_name = "max_depth"
            param_range = np.arange(1, 11)

        # knn
        elif "n_neighbors" in model_params:
            param_name = "n_neighbors"
            param_range = np.arange(1, 11)

        # MLP / Ridge
        elif "alpha" in model_params:
            param_name = "alpha"
            param_range = np.arange(0, 1, 0.1)

        # Logistic Regression
        elif "C" in model_params:
            param_name = "C"
            param_range = np.arange(1, 11)

        # Bagging / Boosting
        elif "n_estimators" in model_params:
            param_name = "n_estimators"
            param_range = np.arange(1, 1000, 10)

        # Naive Bayes
        elif "var_smoothing" in model_params:
            param_name = "var_smoothing"
            param_range = np.arange(0.1, 1, 0.01)

        # QDA
        elif "reg_param" in model_params:
            param_name = "reg_param"
            param_range = np.arange(0, 1, 0.1)

        # GPC
        elif "max_iter_predict" in model_params:
            param_name = "max_iter_predict"
            param_range = np.arange(100, 1000, 100)

        else:
            # display.clear_output()
            raise TypeError(
                "Plot not supported for this estimator. Try different estimator."
            )

    elif task_type == TaskType.REGRESSION:

        # Catboost
        if "depth" in model_params:
            param_name = "depth"
            param_range = np.arange(1, 11)

        # lasso/ridge/en/llar/huber/kr/mlp/br/ard
        elif "alpha" in model_params:
            param_name = "alpha"
            param_range = np.arange(0, 1, 0.1)

        elif "alpha_1" in model_params:
            param_name = "alpha_1"
            param_range = np.arange(0, 1, 0.1)

        # par/svm
        elif "C" in model_params:
            param_name = "C"
            param_range = np.arange(1, 11)

        # tree based models (dt/rf/et)
        elif "max_depth" in model_params:
            param_name = "max_depth"
            param_range = np.arange(1, 11)

        # knn
        elif "n_neighbors" in model_params:
            param_name = "n_neighbors"
            param_range = np.arange(1, 11)

        # Bagging / Boosting (ada/gbr)
        elif "n_estimators" in model_params:
            param_name = "n_estimators"
            param_range = np.arange(1, 1000, 10)

        # Bagging / Boosting (ada/gbr)
        elif "n_nonzero_coefs" in model_params:
            param_name = "n_nonzero_coefs"
            if len(nb_train_column) >= 10:
                param_max = 11
            else:
                param_max = len(nb_train_column) + 1
            param_range = np.arange(1, param_max, 1)

        elif "eps" in model_params:
            param_name = "eps"
            param_range = np.arange(0, 1, 0.1)

        elif "max_subpopulation" in model_params:
            param_name = "max_subpopulation"
            param_range = np.arange(1000, 100000, 2000)

        elif "min_samples" in model_params:
            param_name = "min_samples"
            param_range = np.arange(0.01, 1, 0.1)

        else:
            # display.clear_output()
            raise TypeError(
                "Plot not supported for this estimator. Try different estimator."
            )

        return param_name, param_range