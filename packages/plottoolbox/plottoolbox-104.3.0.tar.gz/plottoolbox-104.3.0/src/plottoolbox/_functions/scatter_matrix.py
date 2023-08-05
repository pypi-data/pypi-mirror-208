"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix as scatter_matrix_plot
from toolbox_utils import tsutils

from .. import _plotutils

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")

warnings.filterwarnings("ignore")


@tsutils.doc(_plotutils.ldocstrings)
def scatter_matrix(
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
    scatter_matrix_diagonal="kde",
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
    r"""[N columns] Plots all columns against each other in matrix of plots.

    "scatter_matrix" will plots all columns against each other in a matrix,
    with the diagonal plots either histogram or KDE probability distribution
    depending on `scatter_matrix_diagonal` keyword.

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
    scatter_matrix_diagonal : bool
        [optional, defaults to "kde"]

        What to plot on the diagonal of the scatter matrix.
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
    plottype = "scatter_matrix"
    lnames = tsutils.make_list(legend_names)
    tsd, lnames = _plotutils.check_column_legend(plottype, tsd, lnames)

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

    if scatter_matrix_diagonal == "probablity_density":
        scatter_matrix_diagonal = "kde"
    scatter_matrix_plot(tsd, diagonal=scatter_matrix_diagonal, figsize=figsize)

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
