"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import pandas as pd
from toolbox_utils import tsutils

from .. import _plotutils
from ..waterfall_ax import waterfall_ax

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")
warnings.filterwarnings("ignore")


@tsutils.doc(_plotutils.ldocstrings)
def waterfall(
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
    subplots=False,
    sharex=True,
    sharey=False,
    colors="auto",
    linestyles="auto",
    markerstyles=" ",
    style="auto",
    xaxis="arithmetic",
    yaxis="arithmetic",
    xlim=None,
    ylim=None,
    secondary_y=False,
    mark_right=True,
    grid=False,
    drawstyle="default",
    por=False,
    invert_xaxis=False,
    invert_yaxis=False,
    round_index=None,
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
    r"""[time index, N columns] Watefall plot.

    Create a waterfall plot from a time series.

    Data must be organized as 'index,y1,y2,y3,...,yN'.  The 'index' must be
    a date/time and all data columns are plotted.  Legend names are taken from
    the column names in the first row unless over-ridden by the `legend_names`
    keyword.

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
    ${subplots}
    ${sharex}
    ${sharey}
    ${colors}
    ${linestyles}
    ${markerstyles}
    ${style}
    ${xaxis}
    ${yaxis}
    ${xlim}
    ${ylim}
    secondary_y
        ${secondary}
    ${mark_right}
    ${grid}
    ${drawstyle}
    ${por}
    ${invert_xaxis}
    ${invert_yaxis}
    ${round_index}
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

    import matplotlib.pyplot as plt

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
        dropna="all",
        source_units=source_units,
        target_units=target_units,
        clean=clean,
        por=por,
    )

    tsd.index = range(len(tsd.index))

    # Need to work around some old option defaults with the implementation of
    # cltoolbox
    legend = legend == "" or legend == "True" or legend is None or legend is True
    plottype = "waterfall"
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

    tsd = tsd.squeeze()

    # Labels
    step_names = list(range(len(tsd.index)))
    last_step_label = tsd.index.to_list()[-1]

    # Styles
    bar_labels = True
    bar_kwargs = {"edgecolor": "black"}
    line_kwargs = {"color": "red"}

    tsd = tsd.round(2)

    # Plot waterfall
    wf = waterfall_ax.WaterfallChart(
        tsd.to_list(),
        step_names=step_names,
        metric_name=ytitle,
        last_step_label=last_step_label,
    )

    ax = wf.plot_waterfall(
        title="Change Styles and Labels",
        bar_labels=bar_labels,
        bar_kwargs=bar_kwargs,
        line_kwargs=line_kwargs,
    )

    plt.xlabel(xtitle)
    plt.ylabel(ytitle)

    plt = _plotutils.hv_lines(
        plt,
        hlines_y=hlines_y,
        hlines_xmin=hlines_xmin,
        hlines_xmax=hlines_xmax,
        hlines_colors=hlines_colors,
        hlines_linestyles=hlines_linestyles,
        vlines_x=None,
        vlines_ymin=None,
        vlines_ymax=None,
        vlines_colors=None,
        vlines_linestyles=None,
    )

    plt.grid(grid)

    plt.title(title)
    plt.tight_layout()
    if ofilename is not None:
        plt.savefig(ofilename)
    return plt
