# functions for taking subsets of the data
import numpy as np

import om_code.omerrors as errors
import om_code.omgenutils as gu


def getsubset(
    self,
    type,
    set="all",
    includes=False,
    excludes=False,
    nonull=False,
    nomedia=False,
):
    """
    Return a subset of either the conditions or strains.

    Parameters
    --
    self: instance of platereader
    type: string
        Either 'c' (conditions) or 's' (strains).
    set: list of strings
        List of items to include (default is 'all').
    includes: string
        Select only items with this string in their name.
    excludes: string
        Ignore any items with this string in their name.
    nonull: boolean
        If True, ignore Null strain.
    nomedia: boolean
        If True, ignores 'media' condition.

    Returns
    -------
    sset: list of strings
    """
    if set == "all" or includes or excludes:
        if type == "c":
            sset = list(
                np.unique(
                    [
                        con
                        for e in self.allconditions
                        for con in self.allconditions[e]
                    ]
                )
            )
            if nomedia and "media" in sset:
                sset.pop(sset.index("media"))
        elif type == "s":
            sset = list(
                np.unique(
                    [
                        str
                        for e in self.allstrains
                        for str in self.allstrains[e]
                    ]
                )
            )
            if nonull and "Null" in sset:
                sset.pop(sset.index("Null"))
        else:
            sset = self.allexperiments
        # find those items containing keywords given in 'includes'
        if includes:
            includes = gu.makelist(includes)
            newset = []
            for s in sset:
                gotone = 0
                for item in includes:
                    if item in s:
                        gotone += 1
                if gotone == len(includes):
                    newset.append(s)
            sset = newset
        # remove any items containing keywords given in 'excludes'
        if excludes:
            excludes = gu.makelist(excludes)
            exs = []
            for s in sset:
                for item in excludes:
                    if item in s:
                        exs.append(s)
                        break
            for ex in exs:
                sset.pop(sset.index(ex))
    else:
        sset = gu.makelist(set)
    if sset:
        # sort by numeric values in list entries
        return sorted(sset, key=gu.natural_keys)
    else:
        if includes:
            raise errors.getsubset(
                "Nothing found for " + " and ".join(includes)
            )
        else:
            raise errors.getsubset("Nothing found")


def getexps(self, experiments, experimentincludes, experimentexcludes):
    """Return list of experiments."""
    if experimentincludes or experimentexcludes:
        exps = getsubset(
            self,
            "e",
            includes=experimentincludes,
            excludes=experimentexcludes,
        )
    elif experiments == "all":
        exps = self.allexperiments
    else:
        exps = gu.makelist(experiments)
    return exps


def getcons(self, conditions, conditionincludes, conditionexcludes, nomedia):
    """Return list of conditions."""
    if conditionincludes or conditionexcludes:
        cons = getsubset(
            self,
            "c",
            includes=conditionincludes,
            excludes=conditionexcludes,
            nomedia=nomedia,
        )
    elif conditions == "all":
        cons = list(
            np.unique(
                [
                    con
                    for e in self.allconditions
                    for con in self.allconditions[e]
                ]
            )
        )
        if nomedia and "media" in cons:
            cons.pop(cons.index("media"))
    else:
        cons = gu.makelist(conditions)
    return sorted(cons, key=gu.natural_keys)


def getstrs(self, strains, strainincludes, strainexcludes, nonull):
    """Return list of strains."""
    if strainincludes or strainexcludes:
        strs = getsubset(
            self,
            "s",
            includes=strainincludes,
            excludes=strainexcludes,
            nonull=nonull,
        )
    elif strains == "all":
        strs = list(
            np.unique(
                [str for e in self.allstrains for str in self.allstrains[e]]
            )
        )
        if nonull and "Null" in strs:
            strs.pop(strs.index("Null"))
    else:
        strs = gu.makelist(strains)
    if nonull and "Null" in strs:
        strs.pop(strs.index("Null"))
    return sorted(strs, key=gu.natural_keys)


def getall(
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
):
    """Return experiments, conditions, and strains."""
    exps = getexps(self, experiments, experimentincludes, experimentexcludes)
    cons = getcons(
        self, conditions, conditionincludes, conditionexcludes, nomedia
    )
    strs = getstrs(self, strains, strainincludes, strainexcludes, nonull)
    return exps, cons, strs


def extractwells(r_df, s_df, experiment, condition, strain, datatypes):
    """
    Extract a list of data matrices from the r dataframe.

    Each column in each matrix contains the data
    from one well.

    Data is returned for each dtype in datatypes, which may include "time", for
    the given experiment, condition, and strain.
    """
    datatypes = gu.makelist(datatypes)
    # restrict time if necessary
    lrdf = r_df[
        (r_df.time >= s_df.time.min()) & (r_df.time <= s_df.time.max())
    ]
    # extract data
    df = lrdf.query(
        "experiment == @experiment and condition == @condition "
        "and strain == @strain"
    )
    matrices = []
    for dtype in datatypes:
        df2 = df[[dtype, "well"]]
        df2well = df2.groupby("well", group_keys=True)[dtype].apply(list)
        data = np.transpose([df2well[w] for w in df2well.index])
        matrices.append(data)
    if len(datatypes) == 1:
        # return array
        return matrices[0]
    else:
        # return list of arrays
        return matrices
