"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from toolbox_utils import tsutils

from .. import _plotutils
from ..SkillMetrics.skill_metrics import centered_rms_dev, taylor_diagram

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")


warnings.filterwarnings("ignore")


@tsutils.doc(_plotutils.ldocstrings)
def taylor(
    input_ts="-",
    columns=None,
    start_date=None,
    end_date=None,
    clean=False,
    skiprows=None,
    index_type="datetime",
    names=None,
    ofilename="plot.png",
    title="",
    figsize="10,6.0",
    legend=None,
    legend_names=None,
    colors="auto",
    linestyles="auto",
    markerstyles=" ",
    style="auto",
    por=False,
    round_index=None,
    dropna="all",
    source_units=None,
    target_units=None,
    plot_styles="bright",
    **kwds,
):
    r"""[obs columns, sim N columns] Taylor diagram to plot goodness of fit.

    "taylor" will create a taylor diagram that compares three goodness of fit
    statistics on one plot.  The three goodness of fit statistics calculated
    and displayed are standard deviation, correlation coefficient, and centered
    root mean square deviation.  The data columns have to be organized as
    'observed,simulated1,simulated2,simulated3,...etc.'

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
    ).astype(float)

    # Need to work around some old option defaults with the implementation of
    # cltoolbox
    legend = legend == "" or legend == "True" or legend is None or legend is True
    plottype = "taylor"
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

    ref = tsd.iloc[:, 0]
    std = [np.std(ref)]
    ccoef = [1.0]
    crmsd = [0.0]
    for col in range(1, len(tsd.columns)):
        std.append(np.std(tsd.iloc[:, col]))
        ccoef.append(np.corrcoef(tsd.iloc[:, col], ref)[0][1])
        crmsd.append(centered_rms_dev(tsd.iloc[:, col].values, ref.values))

    taylor_diagram(np.array(std), np.array(crmsd), np.array(ccoef))

    plt.title(title)
    plt.tight_layout()
    if ofilename is not None:
        plt.savefig(ofilename)
    return plt
