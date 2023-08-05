import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import gridspec
from toolbox_utils import tsutils

from .. import _plotutils

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots


@tsutils.doc(_plotutils.ldocstrings)
def handh(
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
    round_index=None,
    dropna="all",
    source_units=None,
    target_units=None,
    plot_styles="bright",
):
    r"""[time index, Q, P] Hydrograph and hyetograph time-series plot.

    "handh" creates a time series plot of a hydrograph (flow) and hyetograph
    (precipitation).

    Data must be organized as 'index,Q,P'.  The 'index' must be
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
    # check dataframe
    if not isinstance(tsd.index, pd.DatetimeIndex):
        raise ValueError(
            tsutils.error_wrapper(
                """
                The index is not a datetime index and cannot be plotted as
                a time-series. Instead of "time" you might want "xy" or change
                the index to a datetime index.
                """
            )
        )

    # Need to work around some old option defaults with the implementation of
    # cltoolbox
    legend = legend == "" or legend == "True" or legend is None or legend is True
    plottype = "time"
    lnames = tsutils.make_list(legend_names)
    tsd, lnames = _plotutils.check_column_legend(plottype, tsd, lnames)

    # check axis scales
    logy = yaxis == "log"
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

    plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 2])

    # HYDROGRAM CHART
    ax = plt.subplot(gs[1])
    tsd[0].plot(ax=ax, kind="time", logy=logy)
    ax.set_ylabel("Q", color="b")
    ax.set_xlabel("Time")
    ax.tick_params(axis="y", colors="b")
    ax.xaxis.grid(b=True, which="major", color=".7", linestyle="-")
    ax.yaxis.grid(b=True, which="major", color=".7", linestyle="-")
    ax.set_ylim(0, max(sQ) * 1.2)

    # PRECIPITATION/HYETOGRAPH CHART
    ax2 = plt.subplot(gs[0])
    tsd[1].plot(ax=ax2, kind="bar", color="#b0c4de")
    ax2.xaxis.grid(b=True, which="major", color=".7", linestyle="-")
    ax2.yaxis.grid(b=True, which="major", color="0.7", linestyle="-")
    ax2.set_ylabel("P")
    plt.setp(ax2.get_xticklabels(), visible=False)

    plt.tight_layout()
    ax2.invert_yaxis()
    plt.gcf().subplots_adjust(bottom=0.15)
    if ofilename is not None:
        plt.savefig(ofilename)
    return plt
