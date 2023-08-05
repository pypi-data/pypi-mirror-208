"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from toolbox_utils import tsutils

from .. import _plotutils

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")

warnings.filterwarnings("ignore")


@tsutils.transform_args(figsize=tsutils.make_list)
@tsutils.doc(_plotutils.ldocstrings)
def heatmap(
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
    r"""[time index(day), 1 column] 2D heatmap of daily data.

    "heatmap" creates a 2D heatmap of daily data, day of year x-axis, and year
    for y-axis.  Only available for a single, daily time-series.

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
    plottype = "heatmap"
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

    # Find beginning and end years
    byear = tsd.index[0].year
    eyear = tsd.index[-1].year
    tsd = tsutils.asbestfreq(tsd)
    if tsd.index.freqstr != "D":
        raise ValueError(
            tsutils.error_wrapper(
                """
                The "heatmap" plot type can only work with daily time series.
                """
            )
        )
    dr = pd.date_range(f"{byear}-01-01", f"{eyear}-12-31", freq="D")
    ntsd = tsd.reindex(index=dr)
    groups = ntsd.iloc[:, 0].groupby(pd.Grouper(freq="A"))
    years = pd.DataFrame()
    for name, group in groups:
        ngroup = group.values
        if len(group.values) == 365:
            ngroup = np.append(group.values, [np.nan])
        years[name.year] = ngroup
    years = years.T
    plt.imshow(years, interpolation=None, aspect="auto")
    plt.colorbar()
    yticks = list(range(byear, eyear + 1))
    skip = len(yticks) // 20 + 1
    plt.yticks(range(0, len(yticks), skip), yticks[::skip])
    mnths = [0, 30, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    mnths_labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    plt.xticks(mnths, mnths_labels)
    grid = False

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
