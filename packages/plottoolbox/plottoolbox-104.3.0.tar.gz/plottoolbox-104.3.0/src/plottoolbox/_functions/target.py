"""Collection of functions for the manipulation of time series."""

import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from toolbox_utils import tsutils

from .. import _plotutils
from ..SkillMetrics import skill_metrics as sm

sys.path.append(str(Path(__file__).parent / ".." / "SciencePlots"))
import scienceplots

matplotlib.use("Agg")


warnings.filterwarnings("ignore")


@tsutils.doc(_plotutils.ldocstrings)
def target(
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
    colors="auto",
    linestyles="auto",
    markerstyles=" ",
    style="auto",
    por=False,
    round_index=None,
    source_units=None,
    target_units=None,
    plot_styles="bright",
    **kwds,
):
    r"""[obs column, sim N columns] Creates a "target" diagram to plot goodness of fit.

    "target" creates a target diagram that compares three goodness of fit
    statistics on one plot.  The three goodness of fit statistics calculated
    and displayed are bias, root mean square deviation, and centered root mean
    square deviation.  The data columns have to be organized as
    'observed,simulated1,simulated2,simulated3,...etc.'

    Parameters
    ----------
    obs_col
        If integer represents the column number of standard input. Can be
        If integer represents the column number of standard input. Can be
        a csv, wdm, hdf or xlsx file following format specified in
        'tstoolbox read ...'.
    sim_col
        If integer represents the column number of standard input. Can be
        a csv, wdm, hdf or xlsx file following format specified in
        'tstoolbox read ...'.
    ${input_ts}
    ${columns}
    ${start_date}
    ${end_date}
    ${clean}
    ${skiprows}
    ${index_type}
    ${names}
    ${ofilename}
    ${title}
    ${figsize}
    ${legend}
    ${legend_names}
    ${colors}
    ${linestyles}
    ${markerstyles}
    ${style}
    ${por}
    ${round_index}
    ${source_units}
    ${target_units}
    ${plot_styles}
    """

    # set up dataframe
    # Use dropna='no' to get the lengths of both time-series.
    # set up dataframe
    tsd = (
        tsutils.common_kwds(
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
        .astype(float)
        .dropna(how="any")
    )

    if len(tsd.columns) < 2:
        raise ValueError(
            tsutils.error_wrapper(
                """
                The "target" requires two or more two time-series, the first
                one is the observed values and the remaining are the simulated.
                """
            )
        )

    # Need to work around some old option defaults with the implementation of
    # cltoolbox
    legend = legend == "" or legend == "True" or legend is None or legend is True

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

    # Calculate statistics for target diagram
    bias = []
    crmsd = []
    rmsd = []
    for col in tsd.columns:
        data = tsd[col].values
        ref = tsd.iloc[:, 0].values
        target_stats = sm.target_statistics(data, ref, "data")

        # Store statistics in arrays
        bias.append(target_stats["bias"])
        crmsd.append(target_stats["crmsd"])
        rmsd.append(target_stats["rmsd"])

    sm.target_diagram(np.array(bias), np.array(crmsd), np.array(rmsd))

    plt.title(title)
    plt.tight_layout()
    if ofilename is not None:
        plt.savefig(ofilename)
    return plt
