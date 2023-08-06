import numpy as np
import warnings
import matplotlib.pylab as plt
from scipy.interpolate import interp1d
import copy
import gaussianprocessderivatives as gp
import om_code.omgenutils as gu
import om_code.omstats as omstats


class fitderiv:
    """
    Smooth and estimate the time derivative of the data via Gaussian processes.

    Summary statistics - the maximal time derivative, the time at which the
    maximal time derivative occurs, the timescale found from inverting the
    maximal time derivative, the maximal value of the smoothed data, and the
    lag time (the time when the tangent from the point with the maximal time
    derivative crosses a line parallel to the time-axis that passes through the
    first data point) - are found and their errors estimated using
    bootstrapping. All statistics can be postfixed by ' err' to find this
    error.

    A summary statistic is given as the median of a distribution of the
    statistic calculated from time series sampled from the optimal Gaussian
    process. Its error is estimated as the interquartile range of this
    distribution.

    After a successful optimisation, the following attributes are generated:

    t: array
        The times specified as input.
    d: array
        The data specified as input.
    f: array
        The mean of the Gaussian process with the optimal hyperparmeters
        at each time point.
    fvar: array
        The variance of the optimal Gaussian process at each time point.
    df: array
        The inferred first time-derivative.
    dfvar: array
        The inferred variance of the first time-derivative.
    ddf: array
        The inferred second time-derivative.
    ddfvar: array
        The inferred variance of the second time-derivative.
    ds: dictionary
        The summary statistics and their estimated errors.

    Examples
    --------
    A typical work flow is:

    >>> from fitderiv import fitderiv
    >>> q= fitderiv(t, od, figs= True)
    >>> q.plotfit('df')

    or potentially

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(q.t, q.d, 'r.', q.t, q.y, 'b')

    Reference
    ---------
    PS Swain, K Stevenson, A Leary, LF Montano-Gutierrez, IBN Clark, J Vogel,
    and T Pilizota.
    Inferring time derivatives including growth rates using Gaussian processes
    Nat Commun 7 (2016) 13766
    """

    def __init__(
        self,
        t,
        d,
        cvfn="matern",
        logs=True,
        noruns=5,
        noinits=100,
        exitearly=False,
        bd=False,
        empirical_errors=False,
        optmethod="L-BFGS-B",
        nosamples=100,
        stats=True,
        statnames=False,
        printstats=True,
        showstaterrors=True,
        warn=False,
        linalgmax=3,
        iskip=False,
    ):
        """
        Smooth data and estimate time derivatives with a Gaussian process.

        Parameters
        ----------
        t: 1D array
            The time points.
        d: array
            The data corresponding to the time points with any replicates given
             as columns.
        cvfn: string
            The type of kernel function for the Gaussian process either 'sqexp'
            (squared exponential) or 'matern' (Matern with nu= 5/2) or 'nn'
            (neural network).
        logs: boolean
            If True, the Gaussian process is used to smooth the natural
            logarithm of the data and the time-derivative is therefore of the
            logarithm of the data.
        noruns: integer, optional
            The number of attempts to be made at optimising the kernel's
            hyperparmeters.
        noinits: integer, optional
            The number of random attempts made to find good initial choices for
            the hyperparameters before running their optimisation.
        exitearly: boolean, optional
            If True, stop at the first successful attempt at optimising the
            hyperparameters otherwise take the best choice from all successful
            optimisations.
        bd: dictionary, optional
            Specifies the limits on the hyperparameters for the Gaussian process.
            For example, bd= {0: [-1, 4], 2: [2, 6]})
            sets confines the first hyperparameter to be between 1e-1 and 1e^4
            and confines the third hyperparmater between 1e2 and 1e6.
        empirical_errors: boolean, optional
            If True, measurement errors are empirically estimated by the
            variance across replicates at each time point.
            If False, the variance of the measurement error is assumed to be
            the same for all time points and its magnitude is a hyperparameter
            that is optimised.
        optmethod: string, optional
            The algorithm used to optimise the hyperparameters, either
            'l_bfgs_b' or 'tnc'.
        nosamples: integer, optional
            The number of bootstrap samples taken to estimate errors in
            statistics.
        stats: boolean, optional
            If True, calculate summary statistics for both the smoothed data and
            the inferred time- derivative.
        statnames: list of strings
            To customise the names of the statistics.
            The default names are:
            'max df' for the maximal time derivative;
            'time of max df' for the time at which the maximal time
            derivative occurs;
            'inverse max df' for the timescale found from inverting the
            maximal time
            derivative;
            'max f' for the maximal value of the smoothed data;
            'lag time' for the lag time defined as the time when the
            tangent from the point with the maximal time derivative
            crosses a line parallel to the time-axis that passes
            through the first data point.
        printstats: boolean, optional
            If True, print the summary statistics calculated.
        showstaterrors: boolean, optional
            If True, display estimated errors for the statistics when printing.
        warn: boolean, optional
            If False, warnings created by covariance matrices that are not
            positive semi-definite are suppressed.
        linalgmax: integer, optional
            The number of times errors generated by underlying linear algebra
            modules during the optimisation by poor choices of the
            hyperparameters should be ignored.
        iskip: integer, optional
            If non-zero, only every iskip'th data point is used to increase
            speed.
        """
        self.linalgmax = linalgmax
        self.success = True
        if not warn:
            # warning generated occasionally when sampling from the Gaussian
            # process likely because of numerical errors
            warnings.simplefilter("ignore", RuntimeWarning)
        try:
            noreps = d.shape[1]
        except IndexError:
            noreps = 1
        self.noreps = noreps
        self.d = np.copy(d)
        self.t = np.copy(t)
        if iskip:
            t = self.t[::iskip]
            d = self.d[::iskip]
        else:
            t = self.t
            d = self.d
        # default bounds for hyperparameters
        bddict = {
            "nn": {0: (-1, 5), 1: (-7, -2), 2: (-6, 2)},
            "sqexp": {0: (-5, 5), 1: (-6, 2), 2: (-5, 2)},
            "matern": {0: (-5, 5), 1: (-4, 4), 2: (-5, 2)},
        }
        # find bounds
        if bd:
            self.bds = gu.mergedicts(original=bddict[cvfn], update=bd)
        else:
            self.bds = bddict[cvfn]
        # log data
        self.logs = logs
        if logs:
            print("Taking natural logarithm of the data.")
            if np.any(np.nonzero(d < 0)):
                print("Warning: Negative data is being set to NaN.")
            # replace zeros and negs so that logs can be applied
            d[np.nonzero(d <= 0)] = np.nan
            # take log of data
            d = np.log(np.asarray(d))
        # run checks and define measurement errors
        if empirical_errors:
            # errors must be empirically estimated
            if noreps > 1:
                lod = [
                    np.count_nonzero(np.isnan(d[:, i])) for i in range(noreps)
                ]
                if np.sum(np.diff(lod)) != 0:
                    print(
                        "The replicates have different number of data "
                        "points, but equal numbers of data points are "
                        "needed for empirically estimating errors."
                    )
                    merrors = None
                else:
                    # estimate errors empirically
                    print("Estimating measurement errors empirically.")
                    merrors = gu.findsmoothvariance(d)
            else:
                print("Not enough replicates to estimate errors empirically.")
                merrors = None
        else:
            merrors = None
        self.merrors = merrors
        # combine data into one array
        tb = np.tile(t, noreps)
        db = np.reshape(d, np.size(d), order="F")
        # check for NaNs
        if np.any(merrors):
            mb = np.tile(merrors, noreps)
            keep = np.intersect1d(
                np.nonzero(~np.isnan(db))[0], np.nonzero(~np.isnan(mb))[0]
            )
        else:
            keep = np.nonzero(~np.isnan(db))[0]
        # remove any NaNs
        da = db[keep]
        ta = tb[keep]
        # check data remains after removing NaNs
        if not np.any(da):
            print("Warning: omfitderiv failed - too many NaNs.")
            self.success = False
        elif np.any(merrors):
            ma = mb[keep]
            if not np.any(ma):
                print("Warning: omfitderiv failed - too many NaNs.")
                self.success = False
        else:
            ma = None
        if self.success:
            self.run(
                cvfn,
                ta,
                da,
                ma,
                noruns,
                noinits,
                exitearly,
                optmethod,
                stats,
                nosamples,
                statnames,
                showstaterrors,
                printstats,
            )

    def run(
        self,
        cvfn,
        ta,
        da,
        ma,
        noruns,
        noinits,
        exitearly,
        optmethod,
        stats,
        nosamples,
        statnames,
        showstaterrors,
        printstats,
    ):
        """Instantiate and run a Gaussian process."""
        try:
            # instantiate GP
            g = getattr(gp, cvfn + "GP")(self.bds, ta, da, merrors=ma)
            print("Using a " + g.description + ".")
            g.info
        except NameError:
            raise Exception("Gaussian process not recognised.")
        # optimise parameters
        g.findhyperparameters(
            noruns,
            noinits=noinits,
            exitearly=exitearly,
            optmethod=optmethod,
            linalgmax=self.linalgmax,
        )
        # display results
        g.results()
        if np.any(ma):
            if len(ma) != len(self.t):
                # NaNs have been removed
                mainterp = interp1d(
                    ta, ma, bounds_error=False, fill_value=(ma[0], ma[-1])
                )
                ma = mainterp(self.t)
        g.predict(self.t, derivs=2, addnoise=True, merrorsnew=ma)
        # results
        self.g = g
        self.logmaxlike = -g.nlml_opt
        self.hparamerr = g.hparamerr
        self.lth = g.lth_opt
        self.f = g.f
        self.df = g.df
        self.ddf = g.ddf
        self.fvar = g.fvar
        self.dfvar = g.dfvar
        self.ddfvar = g.ddfvar
        if stats:
            self.calculatestats(
                nosamples, statnames, showstaterrors, printstats
            )

    def fitderivsample(self, nosamples, newt=None):
        """
        Generate samples from the latent function.

        Both values for the latent function and its first two
        derivatives are returned, as a tuple.

        All derivatives must be sampled because by default all are asked
        to be predicted by the underlying Gaussian process.

        Parameters
        ----------
        nosamples: integer
            The number of samples.
        newt: array, optional
            Time points for which the samples should be made.
            If None, the orginal time points are used.

        Returns
        -------
        samples: a tuple of arrays
            The first element of the tuple gives samples of the latent
            function;
            the second element gives samples of the first time derivative; and
            the third element gives samples of the second time derivative.
        """
        if np.any(newt):
            newt = np.asarray(newt)
            # make prediction for new time points
            gps = copy.deepcopy(self.g)
            gps.predict(newt, derivs=2, addnoise=True)
        else:
            gps = self.g
        samples = gps.sample(nosamples, derivs=2)
        return samples

    def calculatestats(self, nosamples, statnames, showerrors, printstats):
        """
        Calculate statistics from the smoothed data.

        The default names are 'max df', 'time of max df', 'inverse max grad',
        'max f', and 'lag time'.

        Parameters
        ----------
        nosamples: integer
            The number of bootstrap samples used to estimate errors.
        statnames: list of strings, optional
            A list of alternative names for the statistics.
        showerrors: boolean, optional
            If True, display the estimated errors.
        printstats: boolean, optional
            If True, print the summary stats calculated.
        """
        print(f"\nCalculating statistics with {nosamples} samples.")
        if statnames:
            self.stats = statnames
        else:
            self.stats = [
                "min_f",
                "max_f",
                "max_df",
                "time_of_max_df",
                "doubling_time_from_max_df",
                "lag_time",
            ]
        t = self.t
        fs, gs, hs = self.fitderivsample(nosamples)
        # min f
        min_od = fs[np.argmin(fs, 0), np.arange(nosamples)]
        if self.logs:
            min_od = np.exp(min_od)
        # max f
        max_od = fs[np.argmax(fs, 0), np.arange(nosamples)]
        if self.logs:
            max_od = np.exp(max_od)
        # calculate df stats
        im = np.argmax(gs, 0)
        # max df
        mgr = gs[im, np.arange(nosamples)]
        # time of max df
        tmgr = np.array([t[i] for i in im])
        # inverse max df
        dt = np.log(2) / mgr
        # lag time
        lagtime = (
            tmgr
            + (fs[0, np.arange(nosamples)] - fs[im, np.arange(nosamples)])
            / mgr
        )
        # store stats
        ds = {}
        for stname, st in zip(
            self.stats, [min_od, max_od, mgr, tmgr, dt, lagtime]
        ):
            ds[stname] = np.median(st)
            ds[stname + "_err"] = omstats.statserr(st) / 2
        self.ds = ds
        self.nosamples = nosamples
        self.stats2dict(showerrors, printstats)

    def stats2dict(self, showerrors, printstats):
        """
        Create and print a dictionary of statistics.

        The statistics are calculated from the smoothed data and its
        inferred time-derivatives.

        Parameters
        ----------
        showerrors: boolean, optional
            If True, display the errors.
        printstats: boolean optional
            If True, display the statistics.

        Returns
        -------
        statd: dictionary
            The statistics and their errors.
        """
        if showerrors and printstats:
            print("\t(displaying median +/- half interquartile range)\n")
        ds = self.ds
        statd = {}
        lenstr = np.max([len(s) for s in self.stats])
        for s in self.stats:
            statd[s] = ds[s]
            statd[s + "_err"] = ds[s + "_err"]
            if printstats:
                stname = s.rjust(lenstr + 1)
                if showerrors:
                    print(
                        "{:s}= {:6e} +/- {:6e}".format(
                            stname, statd[s], ds[s + "_err"]
                        )
                    )
                else:
                    print("{:s}= {:6e}".format(stname, statd[s]))
        print()
        return statd

    def plotfit(
        self, char="f", errorfac=1, xlabel="time", ylabel=False, figtitle=False
    ):
        """
        Plot the results of the fitting.

        Either the data and the mean of the optimal Gaussian process or
        the inferred time derivatives are plotted.

        Parameters
        ----------
        char: string
            The variable to plot either 'f' or 'df' or 'ddf'.
        errorfac: float, optional
            The size of the errorbars are errorfac times the standard deviation
            of the optimal Gaussian process.
        ylabel: string, optional
            A label for the y-axis.
        figtitle: string, optional
            A title for the figure.
        """
        x = getattr(self, char)
        xv = getattr(self, char + "var")
        if char == "f":
            d = np.log(self.d) if self.logs else self.d
            plt.plot(self.t, d, "r.")
        plt.plot(self.t, x, "b")
        plt.fill_between(
            self.t,
            x - errorfac * np.sqrt(xv),
            x + errorfac * np.sqrt(xv),
            facecolor="blue",
            alpha=0.2,
        )
        if ylabel:
            plt.ylabel(ylabel)
        else:
            plt.ylabel(char)
        plt.xlabel(xlabel)
        if figtitle:
            plt.title(figtitle)
