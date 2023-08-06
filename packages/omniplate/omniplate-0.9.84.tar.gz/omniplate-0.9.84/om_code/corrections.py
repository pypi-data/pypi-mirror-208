# functions for correcting for non-linearity in the OD, for
# the fluorescence of the media, and for autofluorescence
import importlib.resources as import_files
import re

import gaussianprocessderivatives as gp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nunchaku import Nunchaku
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from statsmodels.nonparametric.smoothers_lowess import lowess

import om_code.omerrors as errors
import om_code.omgenutils as gu
import om_code.sunder as sunder
from om_code.omfitderiv import fitderiv


def _read_dilution_data(fname):
    d = import_files.read_text("om_code", fname)
    res = np.array(re.split(r"\n|\t", d)[:-1]).astype(float)
    if fname == "dilution_data_xiao.tsv":
        od, dilfac = res[::2], res[1::2]
        # missing replicate - use mean of existing ones
        dilfac = np.insert(dilfac, 0, dilfac[0])
        dilfac = dilfac.reshape(int(dilfac.size / 3), 3)
        od = np.insert(od, 0, np.mean(od[:2]))
        od = od.reshape(int(od.size / 3), 3)
    else:
        raise SystemExit("Dilution data unrecognised.")
    return od, dilfac


def findODcorrection(wdirpath, ODfname, figs, bd, gp_results):
    """
    Determine a function to correct OD.

    Use a Gaussian process to fit serial dilution data to correct for
    non-linearities in the relationship between OD and cell density.

    The data are either loaded from file ODfname or the default
    data for haploid yeast growing in glucose are used.
    """
    print("Fitting dilution data for OD correction for non-linearities.")
    if ODfname is not None:
        try:
            od_df = pd.read_csv(
                str(wdirpath / ODfname), sep=None, engine="python", header=None
            )
            print(f"Using {ODfname}.")
            od_data = od_df.to_numpy()
            od, dilfac = od_data[:, 0], od_data[:, 1]
        except (FileNotFoundError, OSError):
            raise errors.FileNotFound(str(wdirpath / ODfname))
    else:
        print("Using default data.")
        fname = "dilution_data_xiao.tsv"
        od, dilfac = _read_dilution_data(fname)
    # run nunchaku
    X = np.mean(dilfac, 1)
    nc = Nunchaku(X, od.T, estimate_err=True, prior=[-5, 5])
    num_regions, _ = nc.get_number(4)
    bds, _ = nc.get_iboundaries(num_regions)
    # linear region starts from origin
    odmatch = np.mean(od, 1)[bds[0]]
    dilfacmatch = X[bds[0]]
    # process data
    dilfac = dilfac.flatten()[np.argsort(od.flatten())]
    od = np.sort(od.flatten())
    # rescale so that OD and dilfac match
    y = dilfac / dilfacmatch * odmatch
    # set up Gaussian process
    bds = {0: (-4, 4), 1: (-4, 4), 2: (-3, 1)}
    # find bounds
    if bd is not None:
        bds = gu.mergedicts(original=bds, update=bd)
    gc = gp.maternGP(bds, od, y)
    # run Gaussian process
    gc.findhyperparameters(noruns=5, exitearly=True, quiet=True)
    if gp_results:
        gc.results()
    gc.predict(od)
    if figs:
        plt.figure()
        gc.sketch(".")
        plt.plot(odmatch, odmatch, "bs")
        plt.grid(True)
        plt.xlabel("OD")
        plt.ylabel("corrected OD (relative cell numbers)")
        if ODfname:
            plt.title("Fitting " + ODfname)
        else:
            plt.title("for haploid budding yeast in glucose")
        plt.show(block=False)
    return gc, odmatch


def performmediacorrection(
    r_df, dtype, exp, condition, figs, commonmedia, frac
):
    """
    Correct data of type dtype for any signal from the media.

    Use lowess to smooth over time the media data from the Null
    wells and subtract the smoothed values from the data.
    """
    # find data for correction with condition equal to commonmedia
    df = r_df.query(
        "experiment == @exp and condition == @commonmedia"
        " and strain == 'Null'"
    )
    if df.empty:
        # no data
        print(
            f' No well annotated "Null" was found for {commonmedia}'
            f"in experiment {exp}."
        )
        print(
            f"-> Correcting for media for {dtype} in {commonmedia} abandoned!"
        )
        return False, None
    else:
        # there is data - change r dataframe
        rtest = (r_df.experiment == exp) & (r_df.condition == condition)
        t, data = df["time"].to_numpy(), df[dtype].to_numpy()
        # find correction
        res = lowess(data, t, frac=frac)
        correctionfn = interp1d(
            res[:, 0],
            res[:, 1],
            fill_value=(res[0, 1], res[-1, 1]),
            bounds_error=False,
        )
        if figs:
            plt.figure()
            plt.plot(t, data, "ro", res[:, 0], res[:, 1], "b-")
            plt.xlabel("time (hours)")
            plt.title(
                exp + ": media correction for " + dtype + " in " + condition
            )
            plt.show(block=False)
        # perform correction
        r_df.loc[rtest, dtype] = r_df[rtest][dtype] - correctionfn(
            r_df[rtest]["time"]
        )
        # check for any negative values
        negvalues = ""
        for s in np.unique(r_df[rtest]["strain"][r_df[rtest][dtype] < 0]):
            if s != "Null":
                wstr = (
                    "\t"
                    + dtype
                    + ": "
                    + s
                    + " in "
                    + condition
                    + " for wells "
                )
                for well in np.unique(
                    r_df[rtest][r_df[rtest].strain == s]["well"][
                        r_df[rtest][dtype] < 0
                    ]
                ):
                    wstr += well + " "
                wstr += "\n"
                negvalues += wstr
        return True, negvalues


def correctauto1(
    self,
    f,
    refstrain,
    figs,
    useGPs,
    flcvfn,
    bd,
    nosamples,
    experiments,
    experimentincludes,
    experimentexcludes,
    conditions,
    conditionincludes,
    conditionexcludes,
    strains,
    strainincludes,
    strainexcludes,
    **kwargs,
):
    """
    Correct autofluorescence for measurements with emissions at one wavelength.

    Corrects for autofluorescence for data with emissions measured at one
    wavelength using the fluorescence of the reference strain
    interpolated to the OD of the tagged strain.

    This method in principle corrects too for the fluorescence of the medium,
    although running correctmedia is still recommended.
    """
    print("Using one fluorescence wavelength.")
    print(f"Correcting autofluorescence using {f[0]}.")
    for e in sunder.getexps(
        self, experiments, experimentincludes, experimentexcludes
    ):
        for c in sunder.getcons(
            self,
            conditions,
            conditionincludes,
            conditionexcludes,
            nomedia=True,
        ):
            # process reference strain
            refstrfn = processref1(self, f, refstrain, figs, e, c)
            # correct strains
            for s in sunder.getstrs(
                self, strains, strainincludes, strainexcludes, nonull=True
            ):
                if not self.sc[
                    (self.sc.experiment == e)
                    & (self.sc.condition == c)
                    & (self.sc.strain == s)
                ][f[0] + "_corrected_for_autofluorescence"].any():
                    od, rawfl = sunder.extractwells(
                        self.r, self.s, e, c, s, ["OD", f[0]]
                    )
                    # no data
                    if od.size == 0 or rawfl.size == 0:
                        print(f"\n-> No data found for {e}: {s} in {c}.\n")
                        continue
                    # correct autofluorescence for each replicate
                    fl = np.transpose(
                        [
                            rawfl[:, i] - refstrfn(od[:, i])
                            for i in range(od.shape[1])
                        ]
                    )
                    fl[fl < 0] = np.nan
                    if useGPs:
                        # get time
                        t = self.s.query(
                            "experiment == @e and condition == @c and strain == @s"
                        )["time"].to_numpy()
                        flperod = samplewithGPs(
                            self,
                            t,
                            fl,
                            od,
                            flcvfn,
                            bd,
                            nosamples,
                            e,
                            c,
                            s,
                            figs,
                            **kwargs,
                        )
                    else:
                        # use only the replicates
                        flperod = np.transpose(
                            [fl[:, i] / od[:, i] for i in range(od.shape[1])]
                        )
                        flperod[flperod < 0] = np.nan
                    # check number of NaN
                    nonans = np.count_nonzero(np.isnan(fl))
                    if np.any(nonans):
                        if nonans == fl.size:
                            print(
                                f"\n-> Corrected fluorescence is all NaN for {e}: {s} in {c}.\n"
                            )
                        else:
                            print(
                                f"Warning - {e}: {s} in {c}\n"
                                f"{nonans} corrected data points are"
                                " NaN because the corrected fluorescence"
                                " was negative.",
                            )
                    # store results
                    bname = "c-" + f[0]
                    autofdict = {
                        "experiment": e,
                        "condition": c,
                        "strain": s,
                        "time": self.s.query(
                            "experiment == @e and condition == @c "
                            "and strain == @s"
                        )["time"].to_numpy(),
                        bname: np.nanmean(fl, 1),
                        bname + "_err": nanstdzeros2nan(fl, 1),
                        bname + "perOD": np.nanmean(flperod, 1),
                        bname + "perOD_err": nanstdzeros2nan(flperod, 1),
                    }
                    addtodataframes(self, autofdict, bname)
                    addrecord(self, f[0], e, c, s)


def processref1(self, f, refstrain, figs, experiment, condition):
    """
    Process reference strain for data with one fluorescence measurement.

    Use lowess to smooth the fluorescence of the reference
    strain as a function of OD.

    Parameters
    ----------
    f: string
        The fluorescence to be corrected. For example, ['mCherry'].
    refstrain: string
        The reference strain. For example, 'WT'.
    figs: boolean
        If True, display fits of the reference strain's fluorescence.
    experiment: string
        The experiment to be corrected.
    condition: string
        The condition to be corrected.

    Returns
    -------
    refstrfn: function
        The reference strain's fluorescence as a function of OD.
    """
    e, c = experiment, condition
    print(f"{e}: Processing reference strain {refstrain} for {f[0]} in {c}.")
    od, fl = sunder.extractwells(self.r, self.s, e, c, refstrain, ["OD", f[0]])
    if od.size == 0 or fl.size == 0:
        raise errors.CorrectAuto(f"{e}: {refstrain} not found in {c}.")
    else:
        odf = od.flatten("F")
        flf = fl.flatten("F")
        # smooth fluorescence as a function of OD using lowess to minimize
        # refstrain's autofluorescence

        def choosefrac(frac):
            res = lowess(flf, odf, frac=frac)
            refstrfn = interp1d(
                res[:, 0],
                res[:, 1],
                fill_value=(res[0, 1], res[-1, 1]),
                bounds_error=False,
            )
            # max gives smoother fits than mean
            return np.max(np.abs(flf - refstrfn(odf)))

        res = minimize_scalar(choosefrac, bounds=(0.1, 0.99), method="bounded")
        # choose the optimum frac
        frac = res.x if res.success else 0.33
        res = lowess(flf, odf, frac=frac)
        refstrfn = interp1d(
            res[:, 0],
            res[:, 1],
            fill_value=(res[0, 1], res[-1, 1]),
            bounds_error=False,
        )
        if figs:
            # plot fit
            plt.figure()
            plt.plot(odf, flf, ".", alpha=0.5)
            plt.plot(res[:, 0], res[:, 1])
            plt.xlabel("OD")
            plt.ylabel(f[0])
            plt.title(e + ": " + refstrain + " for " + c)
            plt.show(block=False)
        return refstrfn


def correctauto2(
    self,
    f,
    refstrain,
    figs,
    useGPs,
    flcvfn,
    bd,
    nosamples,
    experiments,
    experimentincludes,
    experimentexcludes,
    conditions,
    conditionincludes,
    conditionexcludes,
    strains,
    strainincludes,
    strainexcludes,
    **kwargs,
):
    """
    Correct autofluorescence for measurements with two emission wavelengths.

    Corrects for autofluorescence using spectral unmixing for data with
    measured emissions at two wavelengths.

    References
    ----------
    CA Lichten, R White, IB Clark, PS Swain (2014). Unmixing of fluorescence
    spectra to resolve quantitative time-series measurements of gene
    expression in plate readers.
    BMC Biotech, 14, 1-11.
    """
    # correct for autofluorescence
    print("Using two fluorescence wavelengths.")
    print(f"Correcting autofluorescence using {f[0]} and {f[1]}.")
    for e in sunder.getexps(
        self, experiments, experimentincludes, experimentexcludes
    ):
        for c in sunder.getcons(
            self,
            conditions,
            conditionincludes,
            conditionexcludes,
            nomedia=True,
        ):
            # process reference strain
            refqrfn = processref2(self, f, refstrain, figs, e, c)
            # process other strains
            for s in sunder.getstrs(
                self, strains, strainincludes, strainexcludes, nonull=True
            ):
                if s != refstrain and not (
                    self.sc[
                        (self.sc.experiment == e)
                        & (self.sc.condition == c)
                        & (self.sc.strain == s)
                    ][f[0] + "_corrected_for_autofluorescence"].any()
                ):
                    f0, f1, od = sunder.extractwells(
                        self.r, self.s, e, c, s, f.copy() + ["OD"]
                    )
                    if f0.size == 0 or f1.size == 0:
                        print(f"Warning: No data found for {e}: {s} in {c} !!")
                        continue
                    nodata, nr = f0.shape
                    # set negative values to NaNs
                    f0[f0 < 0] = np.nan
                    f1[f1 < 0] = np.nan
                    # use mean OD for correction
                    odmean = self.s.query(
                        "experiment == @e and condition == @c and strain == @s"
                    )["OD_mean"].to_numpy()
                    # correct autofluorescence
                    ra = refqrfn(odmean)
                    fl = applyautoflcorrection(self, ra, f0, f1)
                    fl[fl < 0] = np.nan
                    # get time
                    t = self.s.query(
                        "experiment == @e and condition == @c and strain == @s"
                    )["time"].to_numpy()
                    # store corrected fluorescence
                    bname = "c-" + f[0]
                    autofdict = {
                        "experiment": e,
                        "condition": c,
                        "strain": s,
                        "time": t,
                        bname: np.nanmean(fl, 1),
                        bname + " err": nanstdzeros2nan(fl, 1),
                    }
                    if useGPs:
                        flperod = samplewithGPs(
                            self,
                            t,
                            fl,
                            od,
                            flcvfn,
                            bd,
                            nosamples,
                            e,
                            c,
                            s,
                            figs,
                            **kwargs,
                        )
                    else:
                        # use only the replicates
                        flperod = fl / od
                        flperod[flperod < 0] = np.nan
                    # update dict
                    autofdict[bname + "perOD_err"] = naniqrzeros2nan(
                        flperod, 1
                    )
                    autofdict[bname + "perOD"] = np.nanmean(flperod, 1)
                    # add to data frames
                    addtodataframes(self, autofdict, bname)
                    addrecord(self, f[0], e, c, s)


def processref2(self, f, refstrain, figs, experiment, condition):
    """
    Process reference strain for spectral unmixing.

    Requires data with two fluorescence measurements.

    Use lowess to smooth the ratio of emitted fluorescence measurements
    so that the reference strain's data is corrected to zero as best
    as possible.

    Parameters
    ----------
    f: list of strings
        The fluorescence measurements. For example, ['GFP', 'AutoFL'].
    refstrain: string
        The reference strain. For example, 'WT'.
    figs: boolean
        If True, display fits of the fluorescence ratios.
    experiment: string
        The experiment to be corrected.
    condition: string
        The condition to be corrected.

    Returns
    -------
    qrfn: function
        The ratio of the two fluorescence values for the reference strain
        as a function of OD.
    """
    e, c = experiment, condition
    print(f"{e}: Processing reference strain {refstrain} for {f[0]} in {c}.")
    # refstrain data
    f0, f1, od = sunder.extractwells(
        self.r, self.s, e, c, refstrain, f + ["OD"]
    )
    if f0.size == 0 or f1.size == 0 or od.size == 0:
        raise errors.CorrectAuto(f"{e}: {refstrain} not found in {c}.")
    else:
        f0[f0 < 0] = np.nan
        f1[f1 < 0] = np.nan
        odf = od.flatten("F")
        odrefmean = np.mean(od, 1)
        qrf = (f1 / f0).flatten("F")
        if np.all(np.isnan(qrf)):
            raise errors.CorrectAuto(
                f"{e}: {refstrain} in {c} has too many NaNs."
            )
        # smooth to minimise autofluorescence in refstrain

        def choosefrac(frac):
            res = lowess(qrf, odf, frac)
            qrfn = interp1d(
                res[:, 0],
                res[:, 1],
                fill_value=(res[0, 1], res[-1, 1]),
                bounds_error=False,
            )
            flref = applyautoflcorrection(self, qrfn(odrefmean), f0, f1)
            return np.max(np.abs(flref))

        res = minimize_scalar(choosefrac, bounds=(0.1, 0.99), method="bounded")
        # calculate the relationship between qr and OD
        frac = res.x if res.success else 0.95
        res = lowess(qrf, odf, frac)
        qrfn = interp1d(
            res[:, 0],
            res[:, 1],
            fill_value=(res[0, 1], res[-1, 1]),
            bounds_error=False,
        )
        if figs:
            plt.figure()
            plt.plot(odf, qrf, ".", alpha=0.5)
            plt.plot(res[:, 0], res[:, 1])
            plt.xlabel("OD")
            plt.ylabel(f[1] + "/" + f[0])
            plt.title(e + ": " + refstrain + " in " + c)
            plt.show(block=False)
        # check autofluorescence correction for reference strain
        flref = applyautoflcorrection(self, qrfn(odrefmean), f0, f1)
        flrefperod = flref / od
        # set negative values to NaNs
        flref[flref < 0] = np.nan
        flrefperod[flrefperod < 0] = np.nan
        # store results
        bname = "c-" + f[0]
        autofdict = {
            "experiment": e,
            "condition": c,
            "strain": refstrain,
            "time": self.s.query(
                "experiment == @e and condition == @c and strain == @refstrain"
            )["time"].to_numpy(),
            bname: np.nanmean(flref, 1),
            bname + "perOD": np.nanmean(flrefperod, 1),
            bname + "_err": nanstdzeros2nan(flref, 1),
            bname + "perOD_err": nanstdzeros2nan(flrefperod, 1),
        }
        addtodataframes(self, autofdict, bname)
        return qrfn


def applyautoflcorrection(self, ra, f0data, f1data):
    """Correct for autofluorescence returning an array of replicates."""
    nr = f0data.shape[1]
    raa = np.reshape(np.tile(ra, nr), (np.size(ra), nr), order="F")
    return (raa * f0data - f1data) / (
        raa - self._gamma * np.ones(np.shape(raa))
    )


def addtodataframes(self, autofdict, bname):
    """Added dict of autofluorescence corrections to data frames."""
    autofdf = pd.DataFrame(autofdict)
    if bname not in self.s.columns:
        # extend dataframe
        self.s = pd.merge(self.s, autofdf, how="outer")
    else:
        # update dataframe
        self.s = gu.absorbdf(
            self.s,
            autofdf,
            ["experiment", "condition", "strain", "time"],
        )


def addrecord(self, fname, e, c, s):
    """Record correction."""
    self.sc.loc[
        (self.sc.experiment == e)
        & (self.sc.condition == c)
        & (self.sc.strain == s),
        fname + "_corrected_for_autofluorescence",
    ] = True


def nanstdzeros2nan(a, axis=None):
    """Like nanstd but setting zeros to nan."""
    err = np.nanstd(a, axis)
    err[err == 0] = np.nan
    return err


def naniqrzeros2nan(a, axis=None):
    """Interquartile range but setting zeros to nan."""
    iqr = np.nanquantile(a, 0.75, axis) - np.nanquantile(a, 0.25, axis)
    iqr[iqr == 0] = np.nan
    return iqr


def gethypers(self, exp, con, s, dtype="gr"):
    """Find parameters for GP from sc data frame."""
    sdf = self.sc[
        (self.sc.experiment == exp)
        & (self.sc.condition == con)
        & (self.sc.strain == s)
    ]
    try:
        cvfn = sdf["gp_for_gr"].values[0]
        hypers = [
            sdf[col].values[0] for col in sorted(sdf.columns) if "hyper" in col
        ]
        if np.any(np.isnan(hypers)):
            return None, None
        else:
            return hypers, cvfn
    except KeyError:
        return None, None


def samplewithGPs(
    self, t, fl, od, flcvfn, bd, nosamples, e, c, s, figs, **kwargs
):
    """Generate extra samples of flperod using Gaussian processes."""
    hypers, cvfn = gethypers(self, e, c, s)
    if hypers is None or cvfn is None:
        raise SystemExit(
            f"\nYou first must run getstats for {s} in {c} for {e}."
        )
    # initialise GP for log ODs
    t1 = np.tile(t, od.shape[1])
    od1 = np.reshape(od, od.size, order="F")
    od1 = od1[np.argsort(t1)]
    t1 = np.sort(t1)
    # bounds are irrelevant because parameters are optimal
    go = getattr(gp, cvfn + "GP")(
        {0: (-5, 5), 1: (-4, 4), 2: (-5, 2)},
        t1,
        np.log(od1),
    )
    go.lth_opt = hypers
    go.predict(t)
    # run GP for log fluorescence
    print(f"Fitting fluorescence for {e}: {s} in {c}")
    ff = fitderiv(
        t,
        fl,
        cvfn=flcvfn,
        bd=bd,
        logs=True,
        stats=False,
        **kwargs,
    )
    if ff.success:
        print()
        if figs:
            plt.figure()
            ff.plotfit(
                ylabel="log fluorescence",
                figtitle=f"{e}: {s} in {c}",
            )
            plt.show(block=False)
    else:
        print(f"\n-> Fitting fluorescence failed for {e}: {s} in {c}.\n")
        return np.nan * np.ones(fl.shape)
    # sample
    lod_samples = go.sample(nosamples)
    lfl_samples = ff.fitderivsample(nosamples)[0]
    flperod = np.exp(lfl_samples - lod_samples)
    return flperod
