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
        Either "experiment", "condition", or "strain".
    set: list of strings
        List of items to include (default is "all").
    includes: string
        Select only items with this string in their name.
    excludes: string
        Ignore any items with this string in their name.
    nonull: boolean
        If True, ignore Null strain.
    nomedia: boolean
        If True, ignores "media" condition.

    Returns
    -------
    sset: list of strings
    """
    if set == "all" or includes or excludes:
        if type == "condition":
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
        elif type == "strain":
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
        elif type == "experiment":
            sset = self.allexperiments
        else:
            raise errors.getsubset("Nothing found.")
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
            raise errors.getsubset("Nothing found.")


def getset(
    self,
    label,
    labelincludes,
    labelexcludes,
    labeltype,
    nomedia=False,
    nonull=False,
):
    """Find user-specified list of experiments, conditions, or strains."""
    if label != "all":
        # prioritise user-specified labels
        return gu.makelist(label)
    if labelincludes or labelexcludes:
        # selected labels
        labels = getsubset(
            self, labeltype, includes=labelincludes, excludes=labelexcludes
        )
    else:
        # all labels
        if labeltype == "experiment":
            labels = self.allexperiments
        elif labeltype == "condition":
            labels = list(
                np.unique(
                    [
                        con
                        for e in self.allconditions
                        for con in self.allconditions[e]
                    ]
                )
            )
            if nomedia and "media" in labels:
                labels.pop(labels.index("media"))
        elif labeltype == "strain":
            labels = list(
                np.unique(
                    [
                        str
                        for e in self.allstrains
                        for str in self.allstrains[e]
                    ]
                )
            )
            if nonull and "Null" in labels:
                labels.pop(labels.index("Null"))
        else:
            raise errors.getsubset("Nothing found.")
    return labels


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
    exps = getset(
        self, experiments, experimentincludes, experimentexcludes, "experiment"
    )
    cons = getset(
        self,
        conditions,
        conditionincludes,
        conditionexcludes,
        "condition",
        nomedia=nomedia,
    )
    strs = getset(
        self, strains, strainincludes, strainexcludes, "strain", nonull=nonull
    )
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
