# functions to calculate the statistics
import numpy as np
import pandas as pd
from scipy import integrate
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
from scipy.stats import iqr


def statserr(d, **kwargs):
    """
    Use the half the interquartile range as an error.

    For errors in statistics calculated from samples from a
    Gaussian process to be consistent with fitderiv.
    """
    return iqr(d)


def cleansc(self):
    """Ensure that NaNs do not change numeric variables from being floats."""
    floatvars = [
        "log2_OD_ratio",
        "log2_OD_ratio_err",
        "local_max_gr",
        "local_max_gr_err",
        "time_of_local_max_gr",
        "time_of_local_max_gr_err",
        "area_under_gr_vs_OD",
        "area_under_gr_vs_OD_err",
        "normalised_area_under_gr_vs_OD",
        "normalised_area_under_gr_vs_OD_err",
        "area_under_OD",
        "area_under_OD_err",
        "normalised_area_under_OD",
        "normalised_area_under_OD_err",
        "OD_logmaxlike",
        "max_gr",
        "max_gr_err",
        "time_of_max_gr",
        "time_of_max_gr_err",
        "doubling_time",
        "doubling_time_err",
        "max_OD",
        "max_OD_err",
        "lag_time",
        "lag_time_err",
    ]
    for var in floatvars:
        if var in self.sc.columns:
            self.sc[var] = self.sc[var].astype(float)


def findsummarystats(
    dtype,
    derivname,
    logs,
    nosamples,
    f,
    t,
    e,
    c,
    s,
    findareas,
    figs,
    plotlocalmax,
    axgr,
    showpeakproperties,
    **kwargs,
):
    """Find summary statistics from GP fit to time series of dtype."""
    warning = None
    odtype = "log(" + dtype + ")" if logs else dtype
    outdf = pd.DataFrame(
        {
            "experiment": e,
            "condition": c,
            "strain": s,
            "time": t,
            "f" + odtype: f.f,
            "f" + odtype + "_err": np.sqrt(f.fvar),
            derivname: f.df,
            derivname + "_err": np.sqrt(f.dfvar),
            "d/dt_" + derivname: f.ddf,
            "d/dt_" + derivname + "_err": np.sqrt(f.ddfvar),
        }
    )
    # check derivative has been sensibly defined
    if (
        np.max(np.abs(f.df)) < 1.0e-20
        and np.max(np.abs(np.diff(f.dfvar))) < 1.0e-20
    ):
        warning = (
            "\nWarning: getstats may have failed for "
            + e
            + ": "
            + s
            + " in "
            + c
        )
    # find summary statistics
    fs, gs, hs = f.fitderivsample(nosamples)
    # find local maximal derivative
    da, dt = findlocalmaxderiv(
        f, gs, axgr, figs, plotlocalmax, showpeakproperties, **kwargs
    )
    # find area under df vs f and area under f vs t
    if findareas:
        adff, andff, aft, anft = findareasunder(t, fs, gs, logs)
    else:
        adff, andff, aft, anft = np.nan, np.nan, np.nan, np.nan
    # store results
    statsdict = {
        "experiment": e,
        "condition": c,
        "strain": s,
        "local_max_" + derivname: np.median(da),
        "local_max_" + derivname + "_err": statserr(da),
        "time_of_local_max_" + derivname: np.median(dt),
        "time_of_local_max_" + derivname + "_err": statserr(dt),
        "area_under_" + derivname + "_vs_" + dtype: np.median(adff),
        "area_under_" + derivname + "_vs_" + dtype + "_err": statserr(adff),
        "normalised_area_under_"
        + derivname
        + "_vs_"
        + dtype: np.median(andff),
        "normalised_area_under_"
        + derivname
        + "_vs_"
        + dtype
        + "_err": statserr(andff),
        "area_under_" + dtype: np.median(aft),
        "area_under_" + dtype + "_err": statserr(aft),
        "normalised_area_under_" + dtype: np.median(anft),
        "normalised_area_under_" + dtype + "_err": statserr(anft),
    }
    return outdf, statsdict, warning


def findlocalmaxderiv(
    f, gs, axgr, figs, plotlocalmax, showpeakproperties, **kwargs
):
    """
    Find the greatest local maxima in the derivative.

    Check the derivative for local maxima and so find the local maximum
    with the highest derivative using samples, gs, of df.

    The keyword variables kwargs are passed to scipy's find_peaks.
    """
    # find peaks in mean df
    lpksmn, lpksmndict = find_peaks(f.df, **kwargs)
    if np.any(lpksmn):
        if showpeakproperties:
            # display properties of peaks
            print("Peak properties\n---")
            for prop in lpksmndict:
                print("{:15s}".format(prop), lpksmndict[prop])
        # da: samples of local max df
        # dt: samples of time of local max df
        da, dt = [], []
        # find peaks of sampled df
        for gsample in np.transpose(gs):
            tpks = find_peaks(gsample, **kwargs)[0]
            if np.any(tpks):
                da.append(np.max(gsample[tpks]))
                dt.append(f.t[tpks[np.argmax(gsample[tpks])]])
        if figs and plotlocalmax:
            # plot local max df as a point
            axgr.plot(
                np.median(dt),
                np.median(da),
                "o",
                color="yellow",
                markeredgecolor="k",
            )
        return da, dt
    else:
        # mean df has no peaks
        return np.nan, np.nan


def findareasunder(t, fs, gs, logs):
    """
    Find areas.

    Given samples of f, as arguments fs, and of df, as arguments gs,
    either find the area under df/dt vs f and the area under f vs t
    or if logs find the area under d/dt log(f) vs f and the area
    under f vs t.
    """
    adff, andff, aft, anft = [], [], [], []
    for fsample, gsample in zip(np.transpose(fs), np.transpose(gs)):
        sf = np.exp(fsample) if logs else fsample
        # area under df vs f: integrand has f as x and df as y
        def integrand(x):
            return interp1d(sf, gsample)(x)

        iresult = integrate.quad(
            integrand, np.min(sf), np.max(sf), limit=100, full_output=1
        )[0]
        adff.append(iresult)
        andff.append(iresult / (np.max(sf) - np.min(sf)))
        # area under f vs t: integrand has t as x and f as y
        def integrand(x):
            return interp1d(t, sf)(x)

        iresult = integrate.quad(
            integrand, np.min(t), np.max(t), limit=100, full_output=1
        )[0]
        aft.append(iresult)
        anft.append(iresult / (np.max(t) - np.min(t)))
    return adff, andff, aft, anft
