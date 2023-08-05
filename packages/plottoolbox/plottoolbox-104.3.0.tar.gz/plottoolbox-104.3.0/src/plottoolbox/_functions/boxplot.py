"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from toolbox_utils import tsutils

from .. import _plotutils

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")

warnings.filterwarnings("ignore")


@tsutils.doc(_plotutils.ldocstrings)
def boxplot(
    input_ts="-",
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
    colors="auto",
    linestyles="auto",
    markerstyles=" ",
    style="auto",
    xaxis="arithmetic",
    yaxis="arithmetic",
    xlim=None,
    ylim=None,
    grid=False,
    por=False,
    invert_xaxis=False,
    invert_yaxis=False,
    round_index=None,
    dropna="all",
    source_units=None,
    target_units=None,
    plot_styles="bright",
    hlines_y=None,
    hlines_xmin=None,
    hlines_xmax=None,
    hlines_colors=None,
    hlines_linestyles="-",
    vlines_x=None,
    vlines_ymin=None,
    vlines_ymax=None,
    vlines_colors=None,
    vlines_linestyles="-",
    **kwds,
):
    r"""[N columns] Box and whiskers plot.

    Box extends from lower to upper quartile, with line at the median.
    Depending on the statistics, the wiskers represent the range of the data or
    1.5 times the inter-quartile range (Q3 - Q1).

    ${ydata}

    Parameters
    ----------
    ${input_ts}
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
    ${colors}
    ${linestyles}
    ${markerstyles}
    ${style}
    ${xaxis}
    ${yaxis}
    ${xlim}
    ${ylim}
    ${grid}
    ${por}
    ${invert_xaxis}
    ${invert_yaxis}
    ${round_index}
    ${dropna}
    ${source_units}
    ${target_units}
    ${plot_styles}
    ${hlines_y}
    ${hlines_xmin}
    ${hlines_xmax}
    ${hlines_colors}
    ${hlines_linestyles}
    ${vlines_x}
    ${vlines_ymin}
    ${vlines_ymax}
    ${vlines_colors}
    ${vlines_linestyles}
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
        round_index=round_index,
        dropna=dropna,
        source_units=source_units,
        target_units=target_units,
        clean=clean,
        por=por,
    )

    # Need to work around some old option defaults with the implementation of
    # cltoolbox
    legend = legend == "" or legend == "True" or legend is None or legend is True
    plottype = "boxplot"
    lnames = tsutils.make_list(legend_names)
    tsd, lnames = _plotutils.check_column_legend(plottype, tsd, lnames)

    # check axis scales
    xlim = _plotutils.know_your_limits(xlim, axis=xaxis)
    ylim = _plotutils.know_your_limits(ylim, axis=yaxis)

    # process styles: colors, linestyles, markerstyles
    (
        style,
        colors,
        linestyles,
        markerstyles,
        icolors,
        ilinestyles,
        imarkerstyles,
    ) = _plotutils.prepare_styles(
        len(tsd.columns), style, colors, linestyles, markerstyles
    )

    plot_styles = tsutils.make_list(plot_styles) + ["no-latex"]
    plt.style.use(plot_styles)

    figsize = tsutils.make_list(figsize, n=2)
    _, ax = plt.subplots(figsize=figsize)

    tsd.boxplot(figsize=figsize)

    if hlines_y is not None:
        hlines_y = tsutils.make_list(hlines_y)
        hlines_xmin = tsutils.make_list(hlines_xmin)
        hlines_xmax = tsutils.make_list(hlines_xmax)
        hlines_colors = tsutils.make_list(hlines_colors)
        hlines_linestyles = tsutils.make_list(hlines_linestyles)
        nxlim = ax.get_xlim()
        if hlines_xmin is None:
            hlines_xmin = nxlim[0]
        if hlines_xmax is None:
            hlines_xmax = nxlim[1]
    if vlines_x is not None:
        vlines_x = tsutils.make_list(vlines_x)
        vlines_ymin = tsutils.make_list(vlines_ymin)
        vlines_ymax = tsutils.make_list(vlines_ymax)
        vlines_colors = tsutils.make_list(vlines_colors)
        vlines_linestyles = tsutils.make_list(vlines_linestyles)
        nylim = ax.get_ylim()
        if vlines_ymin is None:
            vlines_ymin = nylim[0]
        if vlines_ymax is None:
            vlines_ymax = nylim[1]

    plt.xlabel(xtitle)
    plt.ylabel(ytitle)

    if invert_xaxis is True:
        plt.gca().invert_xaxis()
    if invert_yaxis is True:
        plt.gca().invert_yaxis()

    plt.grid(grid)

    plt.title(title)
    plt.tight_layout()
    if ofilename is not None:
        plt.savefig(ofilename)
    return plt
