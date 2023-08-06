# General admin functions
import numpy as np
import pandas as pd

import om_code.omgenutils as gu


def initialiseprogress(self, experiment):
    """Initialise progress dictionary."""
    self.progress["ignoredwells"][experiment] = []
    self.progress["negativevalues"][experiment] = False


def makewellsdf(df_r):
    """Make a dataframe with the contents of the wells."""
    df = df_r[["experiment", "condition", "strain", "well"]].drop_duplicates()
    df = df.reset_index(drop=True)
    return df


def make_s(self, tmin=None, tmax=None):
    """
    Generate s dataframe.

    Calculates means and variances of all data types from raw data.
    """
    # restrict time
    if tmin and not tmax:
        rdf = self.r[self.r.time >= tmin]
    elif tmax and not tmin:
        rdf = self.r[self.r.time <= tmax]
    elif tmin and tmax:
        rdf = self.r[(self.r.time >= tmin) & (self.r.time <= tmax)]
    else:
        rdf = self.r
    # find means
    df1 = (
        rdf.groupby(["experiment", "condition", "strain", "time"])
        .mean(numeric_only=True)
        .reset_index()
    )
    for exp in self.allexperiments:
        for dtype in self.datatypes[exp]:
            df1 = df1.rename(columns={dtype: dtype + "_mean"})
    # find errors
    df2 = (
        rdf.groupby(["experiment", "condition", "strain", "time"])
        .std(numeric_only=True)
        .reset_index()
    )
    for exp in self.allexperiments:
        for dtype in self.datatypes[exp]:
            df2 = df2.rename(columns={dtype: dtype + "_err"})
    return pd.merge(df1, df2)


def update_s(self):
    """Update means and errors of all datatypes from raw data."""
    # find tmin and tmax in case restrict_time has been called
    tmin = self.s.time.min()
    tmax = self.s.time.max()
    # recalculate s dataframe
    self.s = make_s(self, tmin, tmax)


def add_to_s(self, derivname, outdf):
    """
    Add dataframe of time series to s dataframe.

    Parameters
    ----------
    derivname: str
        Root name for statistic described by dataframe, such as "gr".
    outdf: dataframe
        Data to add.
    """
    if derivname not in self.s.columns:
        # add new columns to dataframe
        self.s = pd.merge(self.s, outdf, how="outer")
    else:
        # update dataframe
        self.s = gu.absorbdf(
            self.s,
            outdf,
            ["experiment", "condition", "strain", "time"],
        )


def add_to_sc(self, statsdict):
    """Add one-line dict to sc dataframe."""
    statsdf = pd.DataFrame(statsdict, index=pd.RangeIndex(0, 1, 1))
    newstats = np.count_nonzero(
        [True if stat not in self.sc.columns else False for stat in statsdict]
    )
    if newstats:
        # add new columns to sc dataframe
        self.sc = pd.merge(self.sc, statsdf, how="outer")
    else:
        # update sc dataframe
        self.sc = gu.absorbdf(
            self.sc,
            statsdf,
            ["experiment", "condition", "strain"],
        )
