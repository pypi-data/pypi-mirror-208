## v104.3.0 (2023-05-11)

### Feat

- added dropna option to all plots
- **waterfall**: added new waterfall plot but not particularly impressed - WIP

## v104.2.0 (2023-03-17)

### Feat

- finished target and taylor plots including tests

### Refactor

- moved SkillMetrics and SciencePlots to use from git submodules
- removed unused os imports

## v104.1.0 (2023-03-01)

### Feat

- added hexbin plot

## v104.0.1 (2023-02-24)

### Fix

- fixed cltoolbox so not part of imports

## v104.0.0 (2023-02-05)

## v103.0.0 (2023-02-05)

## v102.1.1 (2023-02-04)

### Fix

- bumped toolbox_utils version to make sure xlsxwriter is installed

### Refactor

- refactored everything to prevent individual functions showing up in tstoolbox help

## v102.1.0 (2023-01-16)

### Feat

- added new plot styles

### Fix

- replaced deprecated pandas feature

## v102.0.1 (2023-01-08)

## v102.0.0 (2022-10-29)

### Feat

- change all toolboxes to use pydantic instead of typical

## v101.6.5 (2022-10-03)

### Fix

- fixed vlines_ymin and vlines_ymax

## v101.6.4 (2022-09-29)

### Refactor

- move to toolbox_utils.tsutils and complete pyproject.toml

## v101.6.3 (2022-07-29)

### Fix

- **plotutils.py**: Fixed legend_names to actually renamed columns in the dataframe

## v101.6.2 (2022-07-17)

### Fix

- correctly intepret "colors = ['auto']"

### Refactor

- removed __future__
- moved format and % string interpolation to f strings

## v101.6.1 (2022-05-27)

### Fix

- the *_cli shouldn't return a plot value

## v101.6.0 (2022-05-11)

### Feat

- fixed return plot object and cleaned up function signatures to match plot type

### Refactor

- begin to finish converting tstoolbox plot to plottoolbox

## v101.5.0 (2022-02-14)

### Feat

- **docstrings**: moved to new dostring template format in latest tstoolbox

## v101.4.13 (2022-02-07)

### Fix

- more changes to separate the plot type keywords
- **time**: fixed aspects of hlines and vlines
- **plot_styles**: updated and added new plot styles from SciencePlots styles

## v101.4.12 (2021-08-08)

### Fix

- **setup.py**: needed to include package data

## v101.4.11 (2021-08-08)

### Fix

- included the necessary files in MANIFEST.in

### Refactor

- plottoolbox -> src/plottoolbox, docsrc -> docs

## v101.4.10 (2021-08-02)

## v101.4.9 (2021-07-22)
