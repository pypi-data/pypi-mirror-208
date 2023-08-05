"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from toolbox_utils import tsutils

from .. import _plotutils

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")
warnings.filterwarnings("ignore")


@tsutils.doc(_plotutils.ldocstrings)
def hexbin(
    input_ts="-",
    reduce_C_function=np.mean,
    gridsize=100,
    columns=None,
    start_date=None,
    end_date=None,
    clean=False,
    skiprows=None,
    index_type="datetime",
    names=None,
    ofilename="plot.png",
    xtitle="",
    ytitle="",
    title="",
    figsize="10,6.0",
    legend=None,
    legend_names=None,
    xaxis="arithmetic",
    yaxis="arithmetic",
    xlim=None,
    ylim=None,
    xlabel_rotation=0,
    ylabel_rotation=0,
    por=False,
    invert_xaxis=False,
    invert_yaxis=False,
    dropna="all",
    source_units=None,
    target_units=None,
    plot_styles="bright",
):
    r"""[x, y, optional third data column] Hexbin plot.

    Only available for a single x,y pair with an additional, optional data
    column.

    If the data column is not provided, the number of points in each bin is
    shown.

    If the data column is provided, the `reduce_C_function` is applied to all
    values within each hexagon cell.

    Parameters
    ----------
    ${input_ts}

    reduce_C_function : callable, default np.mean
        Function of one argument that reduces all the values in a bin to
        a single number.  The available options at the command line are
        "np.mean", "np.max", "np.sum", "np.std".  Using the Python API can use
        any callable.

    gridsize: int or tuple of (int, int), default 100
        The number of hexagons in the x-direction. The corresponding number of
        hexagons in the y-direction is chosen in a way that the hexagons are
        approximately regular. Alternatively, gridsize can be a tuple with two
        elements specifying the number of hexagons in the x-direction and the
        y-direction.

    ${columns}
    ${start_date}
    ${end_date}
    ${clean}
    ${skiprows}
    ${index_type}
    ${names}
    ${ofilename}
    ${xtitle}
    ${ytitle}
    ${title}
    ${figsize}
    ${legend}
    ${legend_names}
    ${xlim}
    ${ylim}
    ${grid}
    ${xlabel_rotation}
    ${ylabel_rotation}
    ${por}
    ${invert_xaxis}
    ${invert_yaxis}
    ${dropna}
    ${source_units}
    ${target_units}
    ${plot_styles}
    """
    # set up dataframe
    tsd = tsutils.common_kwds(
        input_ts,
        skiprows=skiprows,
        names=names,
        index_type=index_type,
        start_date=start_date,
        end_date=end_date,
        pick=columns,
        dropna=dropna,
        source_units=source_units,
        target_units=target_units,
        clean=clean,
        por=por,
    )

    # Need to work around some old option defaults with the implementation of
    # cltoolbox
    legend = legend == "" or legend == "True" or legend is None or legend is True
    plottype = "hexbin"
    lnames = tsutils.make_list(legend_names)
    tsd, lnames = _plotutils.check_column_legend(plottype, tsd, lnames)

    # check axis scales
    logx = bool(xaxis == "log")
    logy = bool(yaxis == "log")
    loglog = logx and logy
    xlim = _plotutils.know_your_limits(xlim, axis=xaxis)
    ylim = _plotutils.know_your_limits(ylim, axis=yaxis)

    plot_styles = tsutils.make_list(plot_styles) + ["no-latex"]
    plt.style.use(plot_styles)

    figsize = tsutils.make_list(figsize, n=2)
    _, ax = plt.subplots(figsize=figsize)

    data_col = 2 if len(tsd.columns) == 3 else None
    ax = tsd.plot.hexbin(
        0,
        1,
        C=data_col,
        reduce_C_function=reduce_C_function,
        gridsize=gridsize,
        ax=ax,
        loglog=loglog,
        logx=logx,
        logy=logy,
        xlim=xlim,
        ylim=ylim,
        title=title,
        xlabel=xtitle,
        ylabel=ytitle,
    )

    plt.xlabel(xtitle)
    plt.ylabel(ytitle)

    plt.xticks(rotation=xlabel_rotation)
    plt.yticks(rotation=ylabel_rotation)

    plt.xlim(xlim)
    plt.ylim(ylim)

    if invert_xaxis is True:
        plt.gca().invert_xaxis()
    if invert_yaxis is True:
        plt.gca().invert_yaxis()

    plt.title(title)
    plt.tight_layout()
    if ofilename is not None:
        plt.savefig(ofilename)
    return plt
