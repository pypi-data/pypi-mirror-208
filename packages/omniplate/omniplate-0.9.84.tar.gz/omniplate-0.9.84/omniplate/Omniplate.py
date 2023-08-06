# !/usr/bin/env python
import pprint
import re
import warnings
from pathlib import Path

import gaussianprocessderivatives as gp
import matplotlib.pyplot as plt
import numpy as np
import om_code.admin as admin
import om_code.clogger as clogger
import om_code.corrections as corrections
import om_code.loadplatedata as loadplatedata
import om_code.omerrors as errors
import om_code.omgenutils as gu
import om_code.omplot as omplot
import om_code.omstats as omstats
import om_code.sunder as sunder
import om_code.midlog as midlog
import pandas as pd
import seaborn as sns
from om_code.omfitderiv import fitderiv

version = "0.9.84"

plt.rcParams["figure.max_open_warning"] = 0
sns.set()


class platereader:
    """
    To analyse plate-reader data.

    Data are corrected for autofluorescence and growth rates found using
    a Gaussian process.

    All data is stored used Panda's dataframes and plotted using Seaborn.

    Three dataframes are created. If p is an instance of the platereader class,
    then p.r contains the raw data for each well in the plate; p.s contains the
    processed time-series using the data from all relevant wells; and p.sc
    contains any summary statistics, such as 'max gr'.

    For time series sampled from a Gaussian process, the mean is used as the
    statistics and errors are estimated by the standard deviation.
    For statistics calculated from time series, the median is used and errors
    are estimated by half the interquartile range, with the distribution of
    the statistic calculated by sampling time series.

    Examples
    -------
    A typical work flow is:

    >>> import omniplate as om

    then either

    >>> p= om.platereader('GALdata.xlsx', 'GALcontents.xlsx',
    ...                    wdir= 'data/')

    or

    >>> p= om.platereader()
    >>> p.load('GALdata.xls', 'GALcontents.xlsx')

    and to analyse OD data

    >>> p.plot('OD', plate= True)
    >>> p.correctOD()
    >>> p.correctmedia()
    >>> p.plot(y= 'OD')
    >>> p.plot(y= 'OD', hue= 'strain',
    ...        conditionincludes= ['Gal', 'Glu'],
    ...        strainexcludes= 'HXT7')
    >>> p.getstats('OD')

    and for fluorescence data

    >>> p.correctauto(['GFP', 'AutoFL'])
    >>> p.plot(y= 'c-GFPperOD', hue= 'condition')

    and to save the results

    >>> p.savefigs()
    >>> p.exportdf()

    General properties of the data and of previous processing are shown with:

    >>> p.info
    >>> p.attributes()
    >>> p.corrections()
    >>> p.log

    See also
        http://swainlab.bio.ed.ac.uk/software/omniplate/index.html
    for a tutorial, which can be opened directly using

    >>> p.webhelp()
    """

    # ratio of fluorescence emission at 585nm to emiisions at 525nm for eGFP
    _gamma = 0.114

    def __init__(
        self,
        dnames=False,
        anames=False,
        wdir=".",
        platereadertype="Tecan",
        dsheetnumbers=False,
        asheetnumbers=False,
        ODfname=None,
        info=True,
        ls=True,
    ):
        """
        Initiate and potentially immediately load data for processing.

        Parameters
        ----------
        dnames: string or list of strings, optional
            The name of the file containing the data from the plate reader or
            a list of file names.
        anames: string or list of strings, optional
            The name of file containing the corresponding annotation or a list
            of file names.
        wdir: string, optional
            The working directory where the data files are stored and where
            output will be saved.
        platereadertype: string
            The type of plate reader, currently either 'Tecan' or 'Sunrise' or
            'old Tecan'.
        dsheetnumbers: integer or list of integers, optional
            The relevant sheets of the Excel files storing the data.
        asheetnumbers: integer or list of integers, optional
            The relevant sheets of the corresponding Excel files for the
            annotation.
        info: boolean
            If True (default), display summary information on the data once
            loaded.
        ls: boolean
            If True (default), display contents of working directory.
        """
        self.__version__ = version
        # absolute path
        self.wdirpath = Path(wdir)

        # enable logging
        self.logger, self.logstream = clogger.initlog(version)

        if True:
            # warning generated occasionally when sampling from the Gaussian
            # process likely because of numerical errors
            warnings.simplefilter("ignore", RuntimeWarning)

        # dictionary recording extent of analysis
        self.progress = {
            "ignoredwells": {},
            "negativevalues": {},
        }
        self.allexperiments = []
        self.allconditions = {}
        self.allstrains = {}
        self.datatypes = {}
        self._find_available_data

        if dnames is False:
            # list all files in current directory
            if ls:
                self.ls
        else:
            # immediately load data
            self.load(
                dnames,
                anames,
                platereadertype,
                dsheetnumbers,
                asheetnumbers,
                info,
            )

    def __repr__(self):
        """Standard representation."""
        repstr = f"omniplate.{self.__class__.__name__}: "
        if self.allexperiments:
            for e in self.allexperiments:
                repstr += e + " ; "
            if repstr[-2:] == "; ":
                repstr = repstr[:-3]
        else:
            repstr += "no experiments"
        return repstr

    @property
    def _find_available_data(self):
        """Create files and data sets as attributes."""
        files = []
        datasets = []
        for f in self.wdirpath.glob("*.*"):
            if f.is_file() and (
                f.suffix == ".xlsx"
                or f.suffix == ".json"
                or f.suffix == ".tsv"
                or f.suffix == ".csv"
                or f.suffix == ".xls"
            ):
                files.append(f.stem + f.suffix)
                if (
                    f.suffix == ".tsv"
                    or f.suffix == ".json"
                    or f.suffix == ".csv"
                ):
                    froot = "_".join(f.stem.split("_")[:-1])
                    if froot not in datasets:
                        datasets.append(froot)
        self.files = {i: f for i, f in enumerate(sorted(files))}
        self.datasets = sorted(datasets)

    @property
    def ls(self):
        """
        List all files in the working directory.

        A dictionary of available files to load and a list of available
        data sets to import are created as a shortcuts.

        Parameter
        --------
        output: boolean
            If True, list available files.

        Examples
        --------
        >>> p.ls
        >>> p.files
        >>> p.load(p.files[0], p.files[1])
        >>> p.importdf(p.datasets)
        """
        print(f"Working directory is {str(self.wdirpath.resolve())}.")
        print("Files available are:", "\n---")
        pprint.pprint(self.files)
        print()

    def changewdir(self, wdir):
        """
        Change working directory.

        Parameters
        ----------
        wdir: string
            The new working directory specified from the current directory.

        Example
        -------
        >>> p.changewdir('newdata/')
        """
        self.wdirpath = Path(wdir)
        self.ls

    @clogger.log
    def load(
        self,
        dnames,
        anames=False,
        platereadertype="Tecan",
        dsheetnumbers=False,
        asheetnumbers=False,
        info=True,
    ):
        """
        Load raw data files.

        Two files are required: one generated by the plate reader and the other
        the corresponding annotation files - both assumed to be xlsx.

        Parameters
        ----------
        dnames: string or list of strings, optional
            The name of the file containing the data from the plate reader
            or a list of file names.
        anames: string or list of strings, optional
            The name of file containing the corresponding annotation or a list
            of file names.
        platereadertype: string
            The type of plate reader, currently either 'Tecan' or 'Sunrise' or
            'old Tecan'.
        dsheetnumbers: integer or list of integers, optional
            The relevant sheets of the Excel files storing the data.
        asheetnumbers: integer or list of integers, optional
            The relevant sheets of the corresponding Excel files for the
            annotation.
        info: boolean
            If True (default), display summary information on the data once
            loaded.

        Examples
        -------
        >>> p.load('Data.xlsx', 'DataContents.xlsx')
        >>> p.load('Data.xlsx', 'DataContents.xlsx', info= False)
        """
        dnames = gu.makelist(dnames)
        if not anames:
            anames = [
                dname.split(".")[0] + "Contents.xlsx" for dname in dnames
            ]
        else:
            anames = gu.makelist(anames)
        if not dsheetnumbers:
            dsheetnumbers = [0 for dname in dnames]
        if not asheetnumbers:
            asheetnumbers = [0 for dname in dnames]

        alldata = {}
        for i, dname in enumerate(dnames):
            # get dataframe for raw data
            (
                rdf,
                allconditionssingle,
                allstrainssingle,
                alldatasingle,
                experiment,
                datatypes,
            ) = loadplatedata.loadfromplate(
                platereadertype,
                self.wdirpath,
                dname,
                dsheetnumbers[i],
                anames[i],
                asheetnumbers[i],
            )
            self.allexperiments.append(experiment)
            self.allconditions[experiment] = allconditionssingle
            self.allstrains[experiment] = allstrainssingle
            self.datatypes[experiment] = datatypes
            alldata.update(alldatasingle)
            self.r = (
                pd.merge(self.r, rdf, how="outer")
                if hasattr(self, "r")
                else rdf
            )
            # update progress dictionary
            admin.initialiseprogress(self, experiment)

        # dataframe for summary stats and corrections
        alldfs = []
        # for exp in self.allexperiments:
        for exp in alldata:
            strs, cons = [], []
            for cs in alldata[exp]:
                strs.append(cs.split(" in ")[0])
                cons.append(cs.split(" in ")[1])
            corrdict = {
                "experiment": exp,
                "strain": strs,
                "condition": cons,
                "OD_corrected": False,
            }
            corrdict.update(
                {
                    dtype + "_corrected_for_media": False
                    for dtype in self.datatypes[exp]
                }
            )
            corrdict.update(
                {
                    dtype + "_corrected_for_autofluorescence": False
                    for dtype in self.datatypes[exp]
                    if dtype not in ["AutoFL", "OD"]
                }
            )
            alldfs.append(pd.DataFrame(corrdict))
        self.sc = pd.concat(alldfs)

        # dataframe of original data
        self.origr = self.r.copy()
        # dataframe for well content
        self.wellsdf = admin.makewellsdf(self.r)
        # dataframe for summary data
        self.s = admin.make_s(self)

        # display info on experiment, conditions and strains
        if info:
            self.info
        print(
            '\nWarning: wells with no strains have been changed to "Null"'
            "\nto avoid confusion with pandas.\n"
        )

    @property
    def info(self):
        """
        Display conditions, strains, and data types.

        Example
        -------
        >>> p.info
        """
        for exp in self.allexperiments:
            print("\nExperiment:", exp, "\n---")
            print("Conditions:")
            for c in sorted(self.allconditions[exp], key=gu.natural_keys):
                print("\t", c)
            print("Strains:")
            for s in sorted(self.allstrains[exp], key=gu.natural_keys):
                print("\t", s)
            print("Data types:")
            for d in self.datatypes[exp]:
                print("\t", d)
            if self.progress["ignoredwells"]:
                print("Ignored wells:")
                if self.progress["ignoredwells"][exp]:
                    for d in self.progress["ignoredwells"][exp]:
                        print("\t", d)
                else:
                    print("\t", "None")
        print()

    def webhelp(self, browser=None):
        """
        Open detailed examples of how to use in omniplate in a web browser.

        Parameters
        ----------
        browser: string, optional
            The browser to use - either the default if unspecified or 'firefox',
            'chrome', etc.

        Example
        -------
        >>> p.webhelp()
        """
        import webbrowser

        url = "https://swainlab.bio.ed.ac.uk/software/omniplate/index.html"
        webbrowser.get(browser).open_new(url)

    @property
    def attributes(self):
        """
        Print the attributes of the current instance.

        Example
        -------
        >>> p.attributes
        """
        ignore = [
            "d",
            "consist",
            "t",
            "nosamples",
            "_gamma",
            "ODfname",
            "overflow",
            "nooutchannels",
            "nodata",
            "__doc__",
        ]
        for a in self.__dict__:
            if (
                "corrected" not in a
                and "processed" not in a
                and a not in ignore
            ):
                print(a)

    @clogger.log
    def rename(self, translatedict, regex=True, **kwargs):
        """
        Rename strains or conditions.

        Uses a dictionary to replace all occurrences of a strain or a condition
        with an alternative.

        Note that instances of self.progress will not be updated.

        Parameters
        ----------
        translatedict: dictionary
            A dictionary of old name - new name pairs
        regex: boolean (optional)
            Value of regex to pass to panda's replace.
        kwargs: keyword arguments
            Passed to panda's replace.

        Example
        -------
        >>> p.rename({'77.WT' : 'WT', '409.Hxt4' : 'Hxt4'})
        """
        # check for duplicates
        if (
            len(translatedict.values())
            != np.unique(list(translatedict.values())).size
        ):
            print("Warning: new names are not unique.")
            print("Any processed data may be corrupted.\n")
            # replace in dataframes
            for df in [self.r, self.sc]:
                exps = df.experiment.copy()
                df.replace(translatedict, inplace=True, regex=regex, **kwargs)
                # do not change names of experiments
                df["experiment"] = exps
            # remake s so that strains with the same name are combined
            self.s = admin.make_s(self)
        else:
            # replace in dataframes
            for df in [self.r, self.s, self.sc]:
                exps = df.experiment.copy()
                df.replace(translatedict, inplace=True, regex=regex, **kwargs)
                df["experiment"] = exps
        self.wellsdf = admin.makewellsdf(self.r)
        # replace in attributes - allstrains and allconditions
        for e in self.allexperiments:
            for listattr in [self.allconditions[e], self.allstrains[e]]:
                for i, listitem in enumerate(listattr):
                    for key in translatedict:
                        if key in listitem:
                            listattr[i] = listitem.replace(
                                key, translatedict[key]
                            )
            # unique values in case two strains have been renamed to one
            self.allconditions[e] = sorted(
                list(np.unique(self.allconditions[e]))
            )
            self.allstrains[e] = sorted(list(np.unique(self.allstrains[e])))

    def corrections(
        self,
        experiments="all",
        conditions="all",
        strains="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditionincludes=False,
        conditionexcludes=False,
        strainincludes=False,
        strainexcludes=False,
    ):
        """
        Display the current corrections to the data.

        Parameters
        ----------
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.

        Returns
        -------
        df: dataframe
            Contains the status of the corrections for the specified strains,
            conditions, and experiments.

        Examples
        --------
        >>> p.corrections()
        >>> p.corrections(strainincludes= 'GAL')
        """
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
        )
        df = self.sc.query(
            "experiment == @exps and condition == @cons and strain == @strs"
        )
        # only show corrections and not stats
        df = df[
            ["experiment", "strain", "condition"]
            + [col for col in df.columns if "correct" in col]
        ]
        df = df.T
        return df

    @clogger.log
    def addcolumn(self, newcolumnname, oldcolumn, newcolumnvalues):
        """
        Add a new column to all dataframes by parsing an existing column.

        All possible entries for the new column are specified as strings and
        the entry in the new column will be whichever of these strings is
        present in the entry of the existing column.

        Parameters
        ----------
        newcolumnname: string
            The name of the new column.
        oldcolumn: string
            The name of the column to be parsed to create the new column.
        newcolumnvalues: list of strings
            All of the possible values for the entries in the new column.

        Example
        -------
        >>> p.addcolumn('medium', 'condition', ['Raffinose',
        ...                                     'Geneticin'])

        will parse each entry in 'condition' to create a new column called
        'medium' that has either a value 'Raffinose' if 'Raffinose' is in the
        entry from 'condition' or a value 'Geneticin' if 'Geneticin' is in the
        entry from 'condition'.
        """
        for df in [self.r, self.s, self.sc]:
            newcol = np.array(
                ("",) * len(df[oldcolumn].to_numpy()), dtype="object"
            )
            for i, oldcolvalue in enumerate(df[oldcolumn].to_numpy()):
                for newcolvalue in newcolumnvalues:
                    if newcolvalue in oldcolvalue:
                        newcol[i] = newcolvalue
            df[newcolumnname] = newcol

    @clogger.log
    def addnumericcolumn(
        self,
        newcolumnname,
        oldcolumn,
        picknumber=0,
        leftsplitstr=None,
        rightsplitstr=None,
        asstr=False,
    ):
        """
        Add a new numeric column.

        Parses the numbers from the entries of an existing column.

        It is recommended to run only after the basic analyses - ignorewells,
        correctOD, and correctmedia - have been performed because
        it changes the structure of the dataframes.

        Parameters
        ----------
        newcolumnname: string
            The name of the new column.
        oldcolumn: string
            The name of column to be parsed.
        picknumber: integer
            The number to pick from the list of numbers extracted from the
            existing column's entry.
        leftsplitstr: string, optional
            Split the entry of the column using whitespace and parse numbers
            from the substring to the immediate left of leftsplitstr rather
            than the whole entry.
        rightsplitstr: string, optional
            Split the entry of the column using whitespace and parse numbers
            from the substring to the immediate right of rightsplitstr rather
            than the whole entry.
        asstr: boolean
            If True, convert the numeric value to a string to improve plots
            with seaborn.

        Examples
        --------
        To extract concentrations from conditions use

        >>> p.addnumericcolumn('concentration', 'condition')

        For a condition like '0.5% Raf 0.05ug/mL Cycloheximide', use

        >>> p.addnumericcolumn('raffinose', 'condition',
        ...                     picknumber= 0)
        >>> p.addnumericcolumn('cycloheximide', 'condition',
        ...                     picknumber= 1)
        """
        # process splitstrs
        if leftsplitstr or rightsplitstr:
            splitstr = leftsplitstr if leftsplitstr else rightsplitstr
            locno = -1 if leftsplitstr else 1
        else:
            splitstr = False
        # change each dataframe
        for df in [self.r, self.s, self.sc]:
            if asstr:
                # new column of strings
                newcol = np.full_like(
                    df[oldcolumn].to_numpy(), "", dtype="object"
                )
            else:
                # new column of floats
                newcol = np.full_like(
                    df[oldcolumn].to_numpy(), np.nan, dtype="float"
                )
            # parse old column
            for i, oldcolvalue in enumerate(df[oldcolumn].to_numpy()):
                if oldcolvalue:
                    # split string first on spaces and then find substring
                    # adjacent to specified splitstring
                    if splitstr:
                        if splitstr in oldcolvalue:
                            # oldcolvalue contains leftsplitstring or
                            # rightsplitstring
                            bits = oldcolvalue.split()
                            for k, bit in enumerate(bits):
                                if splitstr in bit:
                                    loc = k + locno
                                    break
                            # adjacent string
                            oldcolvalue = bits[loc]
                        else:
                            # oldcolvalue does not contain leftsplitstring
                            # or rightsplitstring
                            oldcolvalue = ""
                    # loop through all floats in oldcolvalue
                    nocount = 0
                    for ci in re.split(
                        r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", oldcolvalue
                    ):
                        try:
                            no = float(ci)
                            if nocount == picknumber:
                                newcol[i] = ci if asstr else no
                                break
                            nocount += 1
                        except ValueError:
                            pass
            df[newcolumnname] = newcol

    @clogger.log
    def add_to_sc(
        self,
        newcolumn=None,
        s_column=None,
        func=None,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
        strains="all",
        strainincludes=False,
        strainexcludes=False,
    ):
        """
        Apply func to a column in the s dataframe.

        The results are stored in the sc dataframe.

        Parameters
        ----------
        newcolumn:  string
            The name of the new column in the sc dataframe
        s_column:   string
            The name of the column in s dataframe from which the
            data is to be processed
        func:   function
            The function to be applied to the data in the s dataframe.

        Examples
        --------
        >>> p.add_to_sc(newcolumn= "max_GFP", s_column= "GFP_mean",
        ...             func= np.nanmax)
        >>> p.add_to_sc(newcolumn= "GFP_lower_quartile", s_column= "GFP_mean",
        ...             func= lambda x: np.nanquantile(x, 0.25))
        """
        # extract data
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
        )
        self.sc[newcolumn] = np.nan
        for e in exps:
            for c in cons:
                for s in strs:
                    d = self.s.query(
                        "experiment == @e and condition == @c and strain == @s"
                    )[s_column].values
                    res = np.asarray(func(d))
                    if res.size == 1:
                        self.sc.loc[
                            (self.sc.experiment == e)
                            & (self.sc.condition == c)
                            & (self.sc.strain == s),
                            newcolumn,
                        ] = func(d)
                    else:
                        print("func must return a single value.")
                        return False

    @clogger.log
    def addcommonvar(
        self,
        var="time",
        dvar=None,
        varmin=None,
        varmax=None,
        figs=True,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
        strains="all",
        strainincludes=False,
        strainexcludes=False,
    ):
        """
        Add a common variable to all time-dependent dataframes.

        The common variable allows averaging across experiments
        and typically is time.

        A common variable is added to time-dependent dataframes. This
        variable's values only come from a fixed array so that they are
        from the same array for all experiments.

        For example, the plate reader often does not perfectly increment time
        between measurements and different experiments can have slightly
        different time points despite the plate reader having the same
        settings. These unique times prevent seaborn from taking averages.

        If experiments have measurements that start at the same time point and
        have the same interval between measurements, then setting a commontime
        for all experiments will allow seaborn to perform averaging.

        The array of the common variable runs from varmin to varmax with an
        interval dvar. These parameters are automatically calculated, but may
        be specified.

        Each instance of var is assigned a common value - the closest instance
        of the common variable to the instance of var. Measurements are assumed
        to the same for the true instance of var and for the assigned common
        value, which may generate errors if these two are sufficiently
        distinct.

        An alternative method is averageoverexpts.

        Parameters
        ----------
        var: string
            The variable from which the common variable is generated,
            typically 'time'.
        dvar: float, optional
            The interval between the values comprising the common array.
        varmin: float, optional
            The minimum of the common variable.
        varmax: float, optional
            The maximum of the common variable.
        figs: boolean
            If True, generate plot to check if the variable and the common
            variable generated from it are sufficiently close in value.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.

        Example
        -------
        To plot averages of time-dependent variables over experiments, use for
        example

        >>> p.addcommonvar('time')
        >>> p.plot(x= 'commontime', y= 'c-GFPperOD',
        ...        hue= 'condition', style= 'strain')
        """
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            nonull=True,
        )
        print(f"Finding common {var}.")
        for df in [self.r, self.s]:
            if var in df:
                loc = (
                    df.experiment.isin(exps)
                    & df.condition.isin(cons)
                    & df.strain.isin(strs)
                )
                print("r dataframe") if df.equals(self.r) else print(
                    "s dataframe"
                )
                if dvar is None:
                    # calculated for tidy printing
                    elen = np.max([len(e) for e in exps]) + 5
                    # find median increment in var
                    for e in exps:
                        evar = df[loc][var].to_numpy()
                        print(
                            " {:{}} {}_min= {:.2e} ; d{}= {:.2e}".format(
                                e,
                                elen,
                                var,
                                np.min(evar),
                                var,
                                np.median(np.diff(evar)),
                            )
                        )
                    ldvar = np.median(np.diff(df[loc][var].to_numpy()))
                else:
                    ldvar = dvar
                print(f" Using d{var}= {ldvar:.2e}")
                lvarmin = df[loc][var].min() if varmin is None else varmin
                print(f" Using {var}_min= {lvarmin:.2e}\n")
                lvarmax = df[loc][var].max() if varmax is None else varmax
                # define common var
                cvar = np.arange(lvarmin, lvarmax, ldvar)
                df.loc[loc, "common" + var] = df[loc][var].apply(
                    lambda x: cvar[np.argmin((x - cvar) ** 2)]
                )
                if figs:
                    plt.figure()
                    sl = np.linspace(
                        df[loc][var].min(), 1.05 * df[loc][var].max(), 100
                    )
                    plt.plot(sl, sl, alpha=0.4)
                    plt.plot(
                        df[loc][var].to_numpy(),
                        df[loc]["common" + var].to_numpy(),
                        ".",
                    )
                    plt.xlabel(var)
                    plt.ylabel("common" + var)
                    title = (
                        "r dataframe" if df.equals(self.r) else "s dataframe"
                    )
                    plt.title(title)
                    plt.suptitle(
                        f"comparing {var} with common {var} – "
                        "the line y= x is expected."
                    )
                    plt.tight_layout()
                    plt.show(block=False)

    def contentsofwells(self, wlist):
        """
        Display contents of wells.

        Parameters
        ----------
        wlist: string or list of string
            Specifies the well or wells of interest.

        Examples
        --------
        >>> p.contentsofwells(['A1', 'E4'])
        """
        wlist = gu.makelist(wlist)
        for w in wlist:
            print("\n" + w + "\n--")
            print(
                self.wellsdf.query("well == @w")
                .drop(["well"], axis=1)
                .to_string(index=False)
            )

    def showwells(
        self,
        concise=False,
        sortby=False,
        experiments="all",
        conditions="all",
        strains="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditionincludes=False,
        conditionexcludes=False,
        strainincludes=False,
        strainexcludes=False,
    ):
        """
        Display wells for specified experiments, conditions, and strains.

        Parameters
        ----------
        concise: boolean
            If True, display as experiment: condition: strain.
        sortby: list of strings, optional
            List of column names on which to sort the results.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.

        Examples
        --------
        >>> p.showwells()
        >>> p.showwells(strains= 'Mal12:GFP', conditions= '1% Mal')
        """
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            nonull=False,
        )
        if not hasattr(self, "wellsdf"):
            self.wellsdf = admin.makewellsdf(self.r)
        df = self.wellsdf.query(
            "experiment == @exps and condition == @cons and strain == @strs"
        )
        if sortby:
            df = df.sort_values(by=gu.makelist(sortby))
        print()
        for e in exps:
            if concise:
                print(
                    df[["experiment", "condition", "strain"]]
                    .drop_duplicates()
                    .query("experiment == @e")
                    .to_string(index=False)
                )
            else:
                print(df.query("experiment == @e").to_string(index=False))
            print()

    @clogger.log
    def ignorewells(
        self,
        exclude=[],
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        clearall=False,
    ):
        """
        Ignore the wells specified in any future processing.

        If called several times, the default behaviour is for any previously
        ignored wells not to be re-instated.

        Parameters
        ---------
        exclude: list of strings
            List of labels of wells on the plate to be excluded.
        experiments: string or list of strings
            The experiments to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        clearall: boolean
            If True, all previously ignored wells are re-instated.

        Example
        -------
        >>> p.ignorewells(['A1', 'C2'])
        """
        if clearall:
            # forget any previously ignoredwells
            self.r = self.origr.copy()
            self.progress["ignoredwells"] = {
                exp: [] for exp in self.allexperiments
            }
            admin.update_s(self)
            print(
                "Warning: all corrections and analysis to raw data have been"
                " lost. No wells have been ignored."
            )
        else:
            if gu.islistempty(exclude):
                return
            else:
                # exclude should be a list of lists
                if isinstance(exclude, str):
                    exclude = [gu.makelist(exclude)]
                elif isinstance(exclude[0], str):
                    exclude = [exclude]
                # check consistency
                if len(self.allexperiments) == 1:
                    exps = self.allexperiments
                else:
                    exps = sunder.getexps(
                        self,
                        experiments,
                        experimentincludes,
                        experimentexcludes,
                    )
                if len(exclude) != len(exps) and not clearall:
                    raise errors.IgnoreWells(
                        "Either a list of wells to exclude for a particular\n"
                        "experiment or a list of experiments must be given."
                    )
                else:
                    # drop wells
                    for ex, exp in zip(exclude, exps):
                        # wells cannot be ignored twice
                        wex = list(
                            set(ex) - set(self.progress["ignoredwells"][exp])
                        )
                        # drop data from ignored wells
                        df = self.r
                        filt = (df["experiment"] == exp) & df["well"].isin(wex)
                        df = df.loc[~filt]
                        df = df.reset_index(drop=True)
                        self.r = df
                        # store ignoredwells
                        self.progress["ignoredwells"][exp] += ex
                        # remove any duplicates
                        self.progress["ignoredwells"][exp] = list(
                            set(self.progress["ignoredwells"][exp])
                        )
                    anycorrections = np.count_nonzero(
                        self.sc[
                            [
                                col
                                for col in self.sc.columns
                                if "correct" in col
                            ]
                        ].values
                    )
                    if np.any(anycorrections):
                        print(
                            "Warning: you have ignored wells after correcting\n"
                            "the data. It is best to ignorewells first, before\n"
                            "running any analysis."
                        )
                # remake summary data
                admin.update_s(self)

    @clogger.log
    def restricttime(self, tmin=None, tmax=None):
        """
        Restrict the processed data to a range of time.

        Points outside this time range are ignored.

        Note that data in the .s dataframe outside the time range is lost.
        Exporting the dataframes before running restricttime is recommended.

        Parameters
        ----------
        tmin: float
            The minimum value of time, with data kept only for t >= tmin.
        tmax: float
            The maximum value of time, with data kept only for t <= tmax.

        Example
        -------
        >>> p.restricttime(tmin= 5)
        """
        if tmin is None:
            tmin = self.r.time.min()
        if tmax is None:
            tmax = self.r.time.max()
        if tmax > tmin:
            self.s = self.s[(self.s.time >= tmin) & (self.s.time <= tmax)]
        else:
            print("tmax or tmin is not properly defined.")

    @clogger.log
    def plot(
        self,
        x="time",
        y="OD",
        hue="strain",
        style="condition",
        size=None,
        kind="line",
        col=None,
        row=None,
        height=5,
        aspect=1,
        xlim=None,
        ylim=None,
        figsize=False,
        returnfacetgrid=False,
        title=None,
        plate=False,
        wells=False,
        nonull=False,
        messages=False,
        sortby=False,
        experiments="all",
        conditions="all",
        strains="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditionincludes=False,
        conditionexcludes=False,
        strainincludes=False,
        strainexcludes=False,
        **kwargs,
    ):
        """
        Plot from the underlying dataframes (chosen automatically).

        Seaborn's relplot is used, which is described at
        https://seaborn.pydata.org/generated/seaborn.relplot.html

        Parameters
        ----------
        x: string
            The variable - column of the dataframe - for the x-axis.
        y: string
            The variable - column of the dataframe - for y-axis.
        hue: string
            The variable whose variation will determine the colours of the
            lines plotted. From Seaborn.
        style: string
            The variable whose variation will determine the style of each line.
            From Seaborn.
        size: string
            The variable whose vairation will determine the size of each
            marker. From Seaborn.
        kind: string
            Either 'line' or 'scatter', which determines the type of plot.
            From Seaborn.
        col: string, optional
            The variable that varies over the columns in a multipanel plot.
            From Seaborn.
        row: string, optional
            The variable that varies over the rows in a multipanel plot.
            From Seaborn.
        height: float, optional
            The height of the individual panels in a multipanel plot.
            From Seaborn.
        aspect: float, optional
            The aspect ratio of the individual panels in a multipanel plot.
            From Seaborn.
        xlim: list of two floats, optional
            The minimal and maximal x-value, such as [0, None]
        ylim: list of two floats, optional
            The minimal and maximal y-value, such as [0, None]
        figsize: tuple, optional
            A tuple of (width, height) for the size of figure.
            Ignored if wells= True or plate= True.
        returnfacetgrid: boolean, optional
            If True, return Seaborn's facetgrid object created by relplot
        title: float, optional
            The title of the plot (overwrites any default titles).
        plate: boolean, optional
            If True, data for each well for a whole plate are plotted in one
            figure.
        wells: boolean, optional
            If True, data for the individual wells is shown.
        nonull: boolean, optional
            If True, 'Null' strains are not plotted.
        sortby: list of strings, optional
            A list of columns to sort the data in the dataframe and passed to
            pandas sort_values.
        messsages: boolean, optional
            If True, print warnings for any data requested but not found.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in
            their name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.
        kwargs: for Seaborn's relplot
            https://seaborn.pydata.org/generated/seaborn.relplot.html

        Returns
        -------
        sfig: Seaborn's facetgrid object generated by relplot if
        returnfacetgrid= True

        Examples
        --------
        >>> p.plot(y= 'OD', plate= True)
        >>> p.plot(y= 'OD', wells= True, strainincludes= 'Gal10:GFP')
        >>> p.plot(y= 'OD')
        >>> p.plot(x= 'OD', y= 'gr')
        >>> p.plot(y= 'c-GFPperOD', nonull= True, ymin= 0)
        >>> p.plot(y= 'c-GFPperOD', conditionincludes= '2% Mal',
        ...        hue= 'strain')
        >>> p.plot(y= 'c-mCherryperOD', conditions= ['0.5% Mal',
        ...        '1% Mal'], hue= 'strain', style= 'condition',
        ...         nonull= True, strainincludes= 'mCherry')
        >>> p.plot(y= 'c-GFPperOD', col= 'experiment')
        >>> p.plot(y= 'max gr')
        """
        # choose the correct dataframe
        basedf, dfname = omplot.plotfinddf(self, x, y)
        # get experiments, conditions and strains
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            nonull,
        )
        # choose the right type of plot
        if plate:
            dtype = y if x == "time" else x
            omplot.plotplate(basedf, exps, dtype)
        elif wells:
            omplot.plot_wells(
                x,
                y,
                basedf,
                exps,
                cons,
                strs,
                style,
                size,
                kind,
                col,
                row,
                xlim,
                ylim,
                title,
                messages,
                **kwargs,
            )
        elif dfname == "s" or dfname == "r":
            sfig = omplot.plot_rs(
                x,
                y,
                basedf,
                exps,
                cons,
                strs,
                hue,
                style,
                size,
                kind,
                col,
                row,
                height,
                aspect,
                xlim,
                ylim,
                title,
                figsize,
                sortby,
                returnfacetgrid,
                **kwargs,
            )
            if returnfacetgrid:
                return sfig
        elif dfname == "sc":
            omplot.plot_sc(
                x,
                y,
                basedf,
                exps,
                cons,
                strs,
                hue,
                style,
                size,
                kind,
                col,
                row,
                height,
                aspect,
                xlim,
                ylim,
                figsize,
                title,
                sortby,
                **kwargs,
            )
        else:
            raise errors.PlotError("No data found")

    def savefigs(self, fname=None, onefile=True):
        """
        Save all current figures to PDF.

        Either all figures save to one file or each to a separate one.

        Parameters
        ----------
        fname: string, optional
            Name of file. If unspecified, the name of the experiment is used.
        onefile: boolean, optional
            If False, each figures is save to its own PDF file.

        Example
        -------
        >>> p.savefigs()
        >>> p.savefigs('figures.pdf')
        """
        if fname:
            if ".pdf" not in fname:
                fname += ".pdf"
            fname = str(self.wdirpath / fname)
        else:
            fname = str(
                self.wdirpath / ("".join(self.allexperiments) + ".pdf")
            )
        if onefile:
            gu.figs2pdf(fname)
        else:
            for i in plt.get_fignums():
                plt.figure(i)
                savename = str(plt.getp(plt.gcf(), "axes")[0].title).split(
                    "'"
                )[1]
                savename = savename.replace(" ", "_")
                if savename == "":
                    savename = "Whole_plate_Figure_" + str(i)
                print("Saving", savename)
                plt.savefig(str(self.wdirpath / (savename + ".pdf")))

    @property
    def close(self):
        """
        Close all figures.

        Example
        -------
        >>> p.close
        """
        plt.close("all")

    @clogger.log
    def getdataframe(
        self,
        dfname="s",
        experiments="all",
        conditions="all",
        strains="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditionincludes=False,
        conditionexcludes=False,
        strainincludes=False,
        strainexcludes=False,
        nonull=True,
    ):
        """
        Obtain a subset of the data in a dataframe.

        This data can be used plotted directly.

        Parameters
        ---------
        dfname: string
            The dataframe of interest either 'r' (raw data),
            's' (default; processed data),
            or 'sc' (summary statistics).
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.
        nonull: boolean, optional
            If True, ignore 'Null' strains

        Returns
        -------
        ndf: dataframe

        Example
        -------
        >>> ndf= p.getdataframe('s', conditions= ['2% Glu'],
        ...                     nonull= True)
        """
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            nonull,
        )
        if hasattr(self, dfname):
            df = getattr(self, dfname)
            ndf = df.query(
                "experiment == @exps and condition == @cons "
                "and strain == @strs"
            )
            if ndf.empty:
                print("No data found.")
            else:
                return ndf.copy()
        else:
            raise errors.UnknownDataFrame(
                "Dataframe " + dfname + " is not recognised."
            )

    @clogger.log
    def correctOD(
        self,
        figs=True,
        bd=None,
        gp_results=False,
        ODfname=None,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
    ):
        """
        Correct for the non-linear relationship between OD and cell number.

        Requires a set of dilution data set, with the default being haploid
        yeast growing in glucose.

        An alternative can be loaded from a file - a txt file of two columns
        with OD specified in the first column and the dilution factor specified
        in descending order in the second.

        Parameters
        ---------
        figs: boolean, optional
            If True, a plot of the fit to the dilution data is produced.
        bd: dictionary, optional
            Specifies the limits on the hyperparameters for the Gaussian
            process.
            For example, bd= {0: [-1, 4], 2: [2, 6]})
            sets confines the first hyperparameter to be between 1e-1 and 1e^4
            and confines the third hyperparmater between 1e2 and 1e6.
        gp_results: boolean, optional
            If True, show the results of fitting the Gaussian process
        ODfname: string, optional
            The name of the file with the dilution data used to correct OD for
            its non-linear dependence on numbers of cells. If unspecified, data
            for haploid budding yeast growing in glucose is used.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.

        Examples
        -------
        >>> p.correctOD()
        >>> p.correctOD(figs= False)
        """
        exps = sunder.getexps(
            self, experiments, experimentincludes, experimentexcludes
        )
        cons = sunder.getcons(
            self,
            conditions,
            conditionincludes,
            conditionexcludes,
            nomedia=False,
        )
        # fit dilution data
        gc, odmatch = corrections.findODcorrection(
            self.wdirpath,
            ODfname,
            figs=figs,
            bd=bd,
            gp_results=gp_results,
        )
        # correct ODs
        for exp in exps:
            for c in cons:
                if self.sc[
                    (self.sc.experiment == exp) & (self.sc.condition == c)
                ]["OD_corrected"].any():
                    print(f"{exp}: OD is already corrected for {c}.")
                else:
                    # correct all wells
                    r_data = self.r.query(
                        "experiment == @exp and condition == @c"
                    )["OD"].to_numpy()
                    gc.batchpredict(r_data)
                    # leave small ODs unchanged
                    new_r = gc.f
                    new_r[r_data < odmatch] = r_data[r_data < odmatch]
                    # update r data frame
                    self.r.loc[
                        (self.r.experiment == exp) & (self.r.condition == c),
                        "OD",
                    ] = new_r
                    # flag corrections in summary stats dataframe
                    self.sc.loc[
                        (self.sc.experiment == exp) & (self.sc.condition == c),
                        "OD_corrected",
                    ] = True
        # update s dataframe
        admin.update_s(self)

    @clogger.log
    def correctmedia(
        self,
        datatypes="all",
        commonmedia=False,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
        figs=False,
        log=True,
        frac=0.33,
    ):
        """
        Correct OD or fluorescence for that of the media.

        Data from wells marked Null is used.

        Uses lowess to smooth measurements of from all Null wells and subtracts
        this smoothed time series from the raw data.

        Parameters
        ----------
        datatypes: string or list of strings
            Data types to be corrected.
        commonmedia: string
            A condition containing Null wells that should be used to correct
            media for other conditions.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        figs: boolean, optional
            If True, display fits to data for the Null wells.
        frac: float
            The fraction of the data used for smoothing via lowess.
            https://www.statsmodels.org/devel/generated/statsmodels.nonparametric.smoothers_lowess.lowess.html

        Examples
        --------
        >>> p.correctmedia()
        >>> p.correctmedia('OD')
        >>> p.correctmedia(commonmedia= '1% Glu')
        """
        exps = sunder.getexps(
            self, experiments, experimentincludes, experimentexcludes
        )
        cons = sunder.getcons(
            self,
            conditions,
            conditionincludes,
            conditionexcludes,
            nomedia=False,
        )
        for exp in exps:
            # data types
            expdatatypes = (
                self.datatypes[exp]
                if datatypes == "all"
                else gu.makelist(datatypes)
            )
            # correct for media
            for dtype in expdatatypes:
                for c in cons:
                    if self.sc[
                        (self.sc.experiment == exp) & (self.sc.condition == c)
                    ][dtype + "_corrected_for_media"].any():
                        print(
                            f"{exp}: {dtype} is already corrected for media"
                            " in {c}."
                        )
                    else:
                        print(f"{exp}: Correcting {dtype} for media in {c}.")
                        cm = commonmedia if commonmedia else c
                        # update r dataframe
                        (
                            success,
                            negvalues,
                        ) = corrections.performmediacorrection(
                            self.r, dtype, exp, c, figs, cm, frac
                        )
                        if success:
                            self.sc.loc[
                                (self.sc.experiment == exp)
                                & (self.sc.condition == c),
                                dtype + "_corrected_for_media",
                            ] = True
                            if negvalues:
                                if not self.progress["negativevalues"][exp]:
                                    self.progress["negativevalues"][
                                        exp
                                    ] = negvalues
                                else:
                                    self.progress["negativevalues"][
                                        exp
                                    ] += negvalues
            if self.progress["negativevalues"][exp]:
                print(
                    "\nWarning: correcting media has created negative "
                    f"values in {exp} for"
                )
                print(self.progress["negativevalues"][exp])
        # update s dataframe
        admin.update_s(self)

    @clogger.log
    def getstats(
        self,
        dtype="OD",
        bd=False,
        cvfn="matern",
        empirical_errors=False,
        noruns=10,
        exitearly=True,
        noinits=100,
        nosamples=100,
        logs=True,
        iskip=False,
        stats=True,
        printstats=False,
        figs=True,
        findareas=False,
        plotlocalmax=True,
        showpeakproperties=False,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
        strains="all",
        strainincludes=False,
        strainexcludes=False,
        **kwargs,
    ):
        """
        Estimate first and second time derivatives.

        The derivatives are found, typically of OD, using a Gaussian process
        (Swain et al., 2016), as well as corresponding summary statistics.

        The derivatives are stored in the .s dataframe; summary statistics are
        stored in the .sc dataframe.

        Parameters
        ----------
        dtype: string, optional
            The type of data - 'OD', 'GFP', 'c-GFPperOD', or 'c-GFP' - for
            which the derivatives are to be found. The data must exist in the
            .r or .s dataframes.
        bd: dictionary, optional
            The bounds on the hyperparameters for the Gaussian process.
            For example, bd= {1: [-2,0])} fixes the bounds on the
            hyperparameter controlling flexibility to be 1e-2 and 1e0.
            The default for a Matern covariance function
            is {0: (-5,5), 1: (-4,4), 2: (-5,2)},
            where the first element controls amplitude, the second controls
            flexibility, and the third determines the magnitude of the
            measurement error.
        cvfn: string, optional
            The covariance function used in the Gaussian process, either
            'matern' or 'sqexp' or 'nn'.
        empirical_errors: boolean, optional
            If True, measurement errors are empirically estimated from the
            variance across replicates at each time point and so vary with
            time.
            If False, the magnitude of the measurement error is fit from the
            data assuming that this magnitude is the same at all time points.
        noruns: integer, optional
            The number of attempts made for each fit. Each attempt is made
            with random initial estimates of the hyperparameters within their
            bounds.
        exitearly: boolean, optional
            If True, stop at the first successful fit.
            If False, use the best fit from all successful fits.
        noinits: integer, optional
            The number of random attempts to find a good initial condition
            before running the optimization.
        nosamples: integer, optional
            The number of samples used to calculate errors in statistics by
            bootstrapping.
        logs: boolean, optional
            If True, find the derivative of the log of the data and should be
            True to determine the specific growth rate when dtype= 'OD'.
        iskip: integer, optional
            Use only every iskip'th data point to increase speed.
        stats: boolean, optional
            If True, calculate summary statistics.
        printstats: boolean, optional
            If True, print summary statistics.
        figs: boolean, optional
            If True, plot both the fits and inferred derivative.
        findareas: boolean, optional
            If True, find the area under the plot of gr vs OD and the area
            under the plot of OD vs time. Setting to True can make getstats
            slow.
        plotlocalmax: boolean, optional
            If True, mark the highest local maxima found, which is used to
            calculate statistics, on any plots.
        showpeakproperties: boolean, optional
            If True, show properties of any local peaks that have found by
            scipy's find_peaks. Additional properties can be specified as
            kwargs and are passed to find_peaks.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in their
            name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.
        kwargs: for scipy's find_peaks
            To set the minimum property of a peak. e.g. prominence= 0.1 and
            width= 15 (specified in numbers of x-points or y-points and not
            real units).
            https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html

        Examples
        --------
        >>> p.getstats()
        >>> p.getstats(conditionincludes= 'Gal')
        >>> p.getstats(noruns= 10, exitearly= False)

        If the fits are poor, often changing the bounds on the hyperparameter
        for the measurement error helps:

        >>> p.getstats(bd= {2: (-3,0)})

        References
        ----------
        PS Swain, K Stevenson, A Leary, LF Montano-Gutierrez, IB Clark,
        J Vogel, T Pilizota. (2016). Inferring time derivatives including cell
        growth rates using Gaussian processes. Nat Commun, 7, 1-8.
        """
        linalgmax = 5
        warnings = ""
        if dtype == "OD" and logs:
            derivname = "gr"
        else:
            derivname = "d/dt_" + dtype
        snames = [
            "min_" + dtype,
            "max_" + dtype,
            "max_" + derivname,
            "time_of_max_" + derivname,
        ]
        if dtype == "OD" and logs:
            # special names with estimating specific growth rate
            snames += ["doubling_time", "lag_time"]
        else:
            snames += [
                "doubling_time_from-" + derivname,
                "lag_time_from_" + derivname,
            ]
        if logs:
            ylabels = ["log(" + dtype + ")", derivname]
        else:
            ylabels = [dtype, derivname]
        # extract data
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
        )
        # find growth rate and stats
        for e in exps:
            for c in cons:
                for s in strs:
                    figtitle = e + ": " + s + " in " + c
                    if dtype in self.r.columns:
                        # raw data
                        d = sunder.extractwells(self.r, self.s, e, c, s, dtype)
                        t = self.s.query(
                            "experiment == @e and condition == @c and "
                            "strain == @s"
                        )["time"].to_numpy()
                    elif dtype in self.s.columns:
                        # processed data
                        df = self.s.query(
                            "experiment == @e and condition == @c and "
                            "strain == @s"
                        )
                        # add columns plus and minus err
                        df = omplot.augmentdf(df, dtype)[
                            [dtype, "augtype", "time"]
                        ]
                        piv_df = df.pivot(
                            index="time", columns="augtype", values=dtype
                        )
                        # convert to array for fitderiv
                        d = piv_df.values
                        t = piv_df.index.to_numpy()
                        numberofnans = np.count_nonzero(np.isnan(d))
                        if np.any(numberofnans):
                            print(f"\nWarning: {numberofnans} NaNs in data")
                    else:
                        print(f"\n-> {dtype} not recognised for {figtitle}.\n")
                        return
                    # checks
                    if d.size == 0:
                        # no data
                        print(
                            f"\n-> No data found for {dtype} for {figtitle}.\m"
                        )
                        continue
                    if logs:
                        print(f"\nFitting log({dtype}) for {figtitle}.")
                    else:
                        print(f"\nFitting {dtype} for {figtitle}.")
                    # call fitderiv
                    f = fitderiv(
                        t,
                        d,
                        cvfn=cvfn,
                        logs=logs,
                        bd=bd,
                        empirical_errors=empirical_errors,
                        statnames=snames,
                        printstats=printstats,
                        noruns=noruns,
                        noinits=noinits,
                        exitearly=exitearly,
                        linalgmax=linalgmax,
                        nosamples=nosamples,
                        iskip=iskip,
                    )
                    if f.success:
                        if figs:
                            plt.figure()
                            plt.subplot(2, 1, 1)
                            f.plotfit(
                                "f", ylabel=ylabels[0], figtitle=figtitle
                            )
                            axgr = plt.subplot(2, 1, 2)
                            f.plotfit("df", ylabel=ylabels[1])
                            plt.tight_layout()
                        else:
                            axgr = None
                        # find summary statistics
                        outdf, statsdict, warning = omstats.findsummarystats(
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
                        )
                        if warning:
                            warnings += warning
                        # store results in the dataframes
                        statsdict[
                            "logmaxlikehood_for_" + derivname
                        ] = f.logmaxlike
                        statsdict["gp_for_" + derivname] = cvfn
                        for j, val in enumerate(f.lth):
                            statsdict[
                                "log_hyperparameter_"
                                + str(j)
                                + "_for_"
                                + derivname
                            ] = val
                        # add time series to s dataframe
                        admin.add_to_s(self, derivname, outdf)
                        if stats:
                            # add stats calculated by omfitderiv
                            for sname in f.ds.keys():
                                statsdict[sname] = f.ds[sname]
                        # create or add summary stats to sc dataframe
                        statsdf = pd.DataFrame(
                            statsdict, index=pd.RangeIndex(0, 1, 1)
                        )
                        admin.add_to_sc(self, statsdf)
                        if figs:
                            plt.show(block=False)
        omstats.cleansc(self)
        if warnings:
            print(warnings)

    @clogger.log
    def averageoverexpts(
        self,
        condition,
        strain,
        tvr="OD_mean",
        bd=False,
        addnoise=True,
        plot=False,
    ):
        """
        Average a time-dependent variable over all experiments.

        Uses a Matern Gaussian process.

        An alternative and best first choice is addcommonvar.

        Parameters
        ----------
        condition: string
            The condition of interest.
        strain: string
            The strain of interest.
        tvr: float
            The time-dependent variable to be averaged.
            For example, 'c-GFPperOD' or 'OD_mean'.
        bd: dictionary, optional
            The limits on the hyperparameters for the Matern Gaussian process.
            For example, {0: (-5,5), 1: (-4,4), 2: (-5,2)}
            where the first element controls amplitude, setting the bounds to
            1e-5 and 1e5, the second controls flexibility, and the third
            determines the magnitude of the measurement error.
        addnoise: boolean
            If True, add the fitted magnitude of the measurement noise to the
            predicted standard deviation for better comparison with the spread
            of the data.

        Returns
        -------
        res: dictionary
            {'t' : time, tvr : time-dependent data, 'mn' : mean,
            'sd' : standard deviation}
            where 'mn' is the average found and 'sd' is its standard deviation.
            'tvr' is the data used to find the average.

        Examples
        --------
        >>> p.averageoverexpts('1% Gal', 'GAL2', bd= {1: [-1,-1])})
        """
        # boundaries on hyperparameters
        if "OD" in tvr:
            bds = {0: (-4, 4), 1: (-1, 4), 2: (-6, 2)}
        else:
            bds = {0: (2, 12), 1: (-1, 4), 2: (4, 10)}
        if bd:
            bds = gu.mergedicts(original=bds, update=bd)
        # extract data
        df = self.s[["experiment", "condition", "strain", "time", tvr]]
        ndf = df.query("condition == @condition and strain == @strain")
        # use GP to average over experiments
        x = ndf["time"].to_numpy()
        y = ndf[tvr].to_numpy()
        ys = y[np.argsort(x)]
        xs = np.sort(x)
        g = gp.maternGP(bds, xs, ys)
        print(f"Averaging over {tvr} experiments for {strain} in {condition}.")
        g.findhyperparameters(noruns=2, noinits=1000)
        g.results()
        g.predict(xs, addnoise=addnoise)
        if plot:
            plt.figure()
            g.sketch(".")
            plt.title("averaging " + strain + " in " + condition)
            plt.xlabel("time")
            plt.ylabel(tvr)
            plt.show(block=False)
        # return results as a dictionary
        res = {"t": xs, tvr: ys, "mn": g.f, "sd": np.sqrt(g.fvar)}
        return res

    @clogger.log
    def correctauto(
        self,
        f=["GFP", "AutoFL"],
        refstrain="WT",
        figs=True,
        useGPs=True,
        flcvfn="matern",
        bd=None,
        nosamples=500,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
        strains="all",
        strainincludes=False,
        strainexcludes=False,
        **kwargs,
    ):
        """
        Correct fluorescence for autofluorescence.

        The correction is made using the fluorescence of an untagged
        reference strain.

        The reference strain is used to estimate the autofluorescence via
        either the method of Lichten et al., 2014, where measurements of
        fluorescence at two wavelengths is required, or by using the
        fluorescence of the reference strain interpolated to the OD of the
        strain of interest (Berthoumieux et al., 2013).

        Using two measurements of fluorescence is thought to be more accurate,
        particularly for low fluorescence measurements (Mihalcescu et al.,
        2015).

        Arguments
        --
        f: string or list of strings
            The fluorescence measurements, typically either ['mCherry'] or
            ['GFP', 'AutoFL'].
        refstrain: string
            The reference strain.
        figs: boolean
            If True, display plots showing the fits to the reference strain's
            fluorescence.
        useGPs: boolean
            If True, use Gaussian processes to generate extra samples from
            the replicates. Recommended, particularly if there are only a few
            replicates, but slower.
        flcvfn: str, optional
            The covariance function to use for the Gaussian process applied
            to the logarithm of the fluorescence.
        bd: dict, optional
            Specifies the bounds on the hyperparameters for the Gaussian
            process applied to the logarithm of the fluorescence,
            e.g. {2: (-2, 0)}.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in
            their name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.
        **kwargs: passed to fitderiv when fitting the fluorescence.

        Notes
        -----
        In principle

        >>> p.correctmedia()

        should be run before running correctauto when processing data with two
        fluorescence measurements.

        It is unnecessary with only one fluorescence measurement because the
        normalisation is then done directly with the reference strain's
        fluorescence and this fluorescence can include the fluorescence from
        the media.

        In practice, running correctmedia may generate negative values of the
        fluorescence at some time points. These negative values will create
        NaNs in the corrected fluorescence, which are normally harmless.

        With sufficiently many negative values of the fluorescence, however,
        correcting data with two fluorescence measurements can become
        corrupted.

        If correctmedia generates negative fluorescence values, we therefore
        recommend comparing the corrected fluorescence between

        >>> p.correctmedia()
        >>> p.correctauto(['GFP', 'AutoFL')

        and

        >>> p.correctauto('GFP')

        to determine if these negative values are deleterious.

        Examples
        --------
        To correct data with one type of fluorescence measurement, use:

        >>> p.correctauto('GFP')
        >>> p.correctauto('mCherry', refstrain= 'BY4741')

        To correct data with two types of fluorescence measurement, use:

        >>> p.correctauto(['GFP', 'AutoFL'])
        >>> p.correctauto(['GFP', 'AutoFL'], refstrain= 'wild-type')

        References
        ----------
        S Berthoumieux, H De Jong, G Baptist, C Pinel, C Ranquet, D Ropers,
        J Geiselmann (2013).
        Shared control of gene expression in bacteria by transcription factors
        and global physiology of the cell.
        Mol Syst Biol, 9, 634.

        CA Lichten, R White, IB Clark, PS Swain (2014).
        Unmixing of fluorescence spectra to resolve quantitative time-series
        measurements of gene expression in plate readers.
        BMC Biotech, 14, 1-11.

        I Mihalcescu, MVM Gateau, B Chelli, C Pinel, JL Ravanat (2015).
        Green autofluorescence, a double edged monitoring tool for bacterial
        growth and activity in micro-plates.
        Phys Biol, 12, 066016.

        """
        f = gu.makelist(f)
        exps, cons, _ = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
        )
        # check for negative fluorescence values
        for e in exps:
            for c in cons:
                if self.progress["negativevalues"][e]:
                    for datatype in f:
                        if (
                            datatype in self.progress["negativevalues"][e]
                            and c in self.progress["negativevalues"][e]
                        ):
                            print(
                                f"{e}: The negative values for {datatype}"
                                f" in {c} will generate NaNs."
                            )
        # going ahead
        print(f"Using {refstrain} as the reference.")
        # correct for autofluorescence
        if len(f) == 2:
            corrections.correctauto2(
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
            )
        elif len(f) == 1:
            corrections.correctauto1(
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
            )
        else:
            print(f"f = {f} must be a list of length 1 or 2.")

    @property
    def log(self):
        """
        Print a log of all methods called and their arguments.

        Example
        -------
        >>> p.log
        """
        print(self.logstream.getvalue())

    def savelog(self, fname=None):
        """
        Save log to file.

        Parameters
        --
        fname: string, optional
            The name of the file. If unspecified, the name of the experiment.

        Example
        -------
        >>> p.savelog()
        """
        # export log
        if fname:
            fnamepath = self.wdirpath / (fname + ".log")
        else:
            fnamepath = self.wdirpath / ("".join(self.allexperiments) + ".log")
        with fnamepath.open("w") as f:
            f.write(self.logstream.getvalue())
        print("Exported successfully.")

    @clogger.log
    def exportdf(self, commonname=False, type="tsv"):
        """
        Export the dataframes.

        The exported data may either be tab-delimited or csv or json files.
        Dataframes for the (processed) raw data, for summary data, and for
        summary statistics and corrections, as well as a log file, are
        exported.

        Parameters
        ----------
        commonname: string, optional
            The name used for the output files.
            If unspecified, the experiment or experiments is used.
        type: string
            The type of file for export, either 'json' or 'csv' or 'tsv'.

        Examples
        --------
        >>> p.exportdf()
        >>> p.exportdf('processed', type= 'json')
        """
        if commonname:
            fullcommonname = str(self.wdirpath / commonname)
        else:
            fullcommonname = str(self.wdirpath / "".join(self.allexperiments))
        # export data
        if type == "json":
            self.r.to_json(fullcommonname + "_r.json", orient="split")
            self.s.to_json(fullcommonname + "_s.json", orient="split")
            self.sc.to_json(fullcommonname + "_sc.json", orient="split")
        else:
            sep = "\t" if type == "tsv" else ","
            self.r.to_csv(fullcommonname + "_r." + type, sep=sep, index=False)
            self.s.to_csv(fullcommonname + "_s." + type, sep=sep, index=False)
            self.sc.to_csv(
                fullcommonname + "_sc." + type, sep=sep, index=False
            )
        # export log to file
        self.savelog(commonname)

    @clogger.log
    def importdf(self, commonnames, info=True, sep="\t"):
        """
        Import dataframes saved as either json or csv or tsv files.

        Parameters
        ----------
        commonnames: list of strings
            A list of names for the files to be imported with one string for
            each experiment.

        Examples
        --------
        >>> p.importdf('Gal')
        >>> p.importdf(['Gal', 'Glu', 'Raf'])
        """
        commonnames = gu.makelist(commonnames)
        # import data
        for commonname in commonnames:
            commonname = str(self.wdirpath / commonname)
            for df in ["r", "s", "sc"]:
                try:
                    # json files
                    exec(
                        "impdf= pd.read_json(commonname + '_' + df + "
                        "'.json', orient= 'split')"
                    )
                    print("Imported", commonname + "_" + df + ".json")
                except FileNotFoundError:
                    try:
                        # csv files
                        exec(
                            "impdf= pd.read_csv(commonname + '_' + df + "
                            "'.csv', sep= ',')"
                        )
                        print("Imported", commonname + "_" + df + ".csv")
                    except FileNotFoundError:
                        try:
                            # tsv files
                            exec(
                                "impdf= pd.read_csv(commonname + '_' + df "
                                "+ '.tsv', sep= '\t')"
                            )
                            print("Imported", commonname + "_" + df + ".tsv")
                        except FileNotFoundError:
                            print(
                                f"No file called {commonname}_{df}.json "
                                "or .csv or .tsv found"
                            )
                            return
                # ensure all are imported as strings
                for var in ["experiment", "condition", "strain"]:
                    exec("impdf[var]= impdf[var].astype(str)")
                # merge dataframes
                if hasattr(self, df):
                    exec(
                        "self."
                        + df
                        + "= pd.merge(self."
                        + df
                        + ", impdf, how= 'outer')"
                    )
                else:
                    exec("self." + df + "= impdf")
            print()

        # update attributes
        self.allexperiments = list(self.s.experiment.unique())
        self.allconditions.update(
            {
                e: list(self.s[self.s.experiment == e].condition.unique())
                for e in self.allexperiments
            }
        )
        self.allstrains.update(
            {
                e: list(self.s[self.s.experiment == e].strain.unique())
                for e in self.allexperiments
            }
        )

        # find datatypes with mean in self.s
        dtypdict = {}
        for e in self.allexperiments:
            # drop columns of NaNs - these are created by merge if a datatype
            # is in one experiment but not in another
            tdf = self.s[self.s.experiment == e].dropna(axis=1, how="all")
            dtypdict[e] = list(tdf.columns[tdf.columns.str.contains("mean")])
        self.datatypes.update(
            {e: [dt.split("_mean")[0] for dt in dtypdict[e]] for e in dtypdict}
        )
        # initialise progress
        for e in self.allexperiments:
            admin.initialiseprogress(self, e)
        # display info on import
        if info:
            self.info

        # display warning if duplicates created
        if len(self.allexperiments) != np.unique(self.allexperiments).size:
            print(
                "\nLikely ERROR: data with the same experiment, condition, "
                "strain, and time now appears twice!!"
            )

    @clogger.log
    def getmidlog(
        self,
        stat="mean",
        min_duration=1,
        figs=True,
        experiments="all",
        experimentincludes=False,
        experimentexcludes=False,
        conditions="all",
        conditionincludes=False,
        conditionexcludes=False,
        strains="all",
        strainincludes=False,
        strainexcludes=False,
        **kwargs,
    ):
        """
        Calculate mid-log statistics.

        Find the region of mid-log growth using nunchakue and calculate a
        statistic for each variable in the s dataframe in this region only.

        The results are added to the sc dataframe.

        Parameters
        ----------
        stat: str
            The name of the statistic to be calculated (using pandas).
        min_duration: float
            The expected minimal duration of the midlog phase in units of time.
        figs: boolean
            If True, show nunchaku's results with the mid-log region marked by black squares.
        experiments: string or list of strings
            The experiments to include.
        conditions: string or list of strings
            The conditions to include.
        strains: string or list of strings
            The strains to include.
        experimentincludes: string, optional
            Selects only experiments that include the specified string in
            their name.
        experimentexcludes: string, optional
            Ignores experiments that include the specified string in their
            name.
        conditionincludes: string, optional
            Selects only conditions that include the specified string in their
            name.
        conditionexcludes: string, optional
            Ignores conditions that include the specified string in their name.
        strainincludes: string, optional
            Selects only strains that include the specified string in their
            name.
        strainexcludes: string, optional
            Ignores strains that include the specified string in their name.
        kwargs: passed to Nunchaku
        """
        exps, cons, strs = sunder.getall(
            self,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            nonull=True,
            nomedia=True,
        )
        # run Nunchaku to find midlog and take the mean of summary stats
        midlog.find_midlog_stats(
            self, stat, min_duration, figs, exps, cons, strs
        )

    @property
    def cols_to_underscore(self):
        """Replace spaces in column names of all dataframes with underscores."""
        for df in [self.r, self.s, self.sc]:
            df.columns = df.columns.str.replace(" ", "_")


if __name__ == "__main__":
    print(platereader.__doc__)
