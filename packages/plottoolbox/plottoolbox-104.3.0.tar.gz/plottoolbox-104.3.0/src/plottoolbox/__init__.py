"""Define plottoolbox package."""

from toolbox_utils.tsutils import about as _about

from ._functions.autocorrelation import autocorrelation
from ._functions.bar import bar
from ._functions.bar_stacked import bar_stacked
from ._functions.barh import barh
from ._functions.barh_stacked import barh_stacked
from ._functions.bootstrap import bootstrap
from ._functions.boxplot import boxplot
from ._functions.double_mass import double_mass
from ._functions.handh import handh
from ._functions.heatmap import heatmap
from ._functions.hexbin import hexbin
from ._functions.histogram import histogram
from ._functions.kde import kde
from ._functions.kde_time import kde_time
from ._functions.lag_plot import lag_plot
from ._functions.lognorm_xaxis import lognorm_xaxis
from ._functions.lognorm_yaxis import lognorm_yaxis
from ._functions.norm_xaxis import norm_xaxis
from ._functions.norm_yaxis import norm_yaxis
from ._functions.probability_density import probability_density
from ._functions.scatter_matrix import scatter_matrix
from ._functions.target import target
from ._functions.taylor import taylor
from ._functions.time import time
from ._functions.waterfall import waterfall
from ._functions.weibull_xaxis import weibull_xaxis
from ._functions.weibull_yaxis import weibull_yaxis
from ._functions.xy import xy


def about():
    """Display version number and system information."""
    _about(__name__)


__all__ = [
    "about",
    "autocorrelation",
    "bar",
    "bar_stacked",
    "barh",
    "barh_stacked",
    "bootstrap",
    "boxplot",
    "double_mass",
    "handh",
    "heatmap",
    "hexbin",
    "histogram",
    "kde",
    "kde_time",
    "lag_plot",
    "lognorm_xaxis",
    "lognorm_yaxis",
    "norm_xaxis",
    "norm_yaxis",
    "probability_density",
    "scatter_matrix",
    "target",
    "taylor",
    "time",
    "waterfall",
    "weibull_xaxis",
    "weibull_yaxis",
    "xy",
]
