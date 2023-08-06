# functions to plot from the data frames
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import om_code.omerrors as errors
import om_code.omgenutils as gu


def plotplate(basedf, exps, dtype):
    """
    Plot the data for each well following the layout of a 96-well plate.

    Parameters
    ----------
    basedf: DataFrame
        The r dataframe.
    exps: float
        The name of the experiments.
    dtype: float
        The data type to be plotted: 'OD', 'GFP', etc.
    """
    for e in exps:
        plt.figure()
        # first create an empty plate - in case of missing wells
        ax = []
        for rowl in range(8):
            for coll in np.arange(1, 13):
                sindex = coll + 12 * rowl
                axi = plt.subplot(8, 12, sindex)
                ax.append(axi)
                plt.tick_params(labelbottom=False, labelleft=False)
                # label well locations
                for j in range(12):
                    if sindex == j + 1:
                        plt.title(j + 1)
                for j, k in enumerate(np.arange(1, 96, 12)):
                    if sindex == k:
                        plt.ylabel("ABCDEFGH"[j] + " ", rotation=0)
        # fill in the wells that have been measured
        for pl in basedf.query("experiment == @e")["well"].unique():
            rowl = "ABCDEFGH".index(pl[0])
            coll = int(pl[1:])
            sindex = coll + 12 * rowl
            wd = basedf.query("experiment == @e and well == @pl")
            ax[sindex - 1].plot(
                wd["time"].to_numpy(), wd[dtype].to_numpy(), "-"
            )
        plt.suptitle(e + ": " + dtype)
        plt.show(block=False)


def plot_wells(
    x,
    y,
    basedf,
    exps,
    cons,
    strs,
    style="condition",
    size=None,
    kind="line",
    col=None,
    row=None,
    xlim=None,
    ylim=None,
    title=None,
    figsize=None,
    messages=False,
    **kwargs,
):
    """
    Plot data from the individual wells.

    Data for each experiment, condition, and strain are plotted in
    a separate figure unless row and col are specified.
    """
    for e in exps:
        if row and col:
            # use facetgrid to show multiple plots simultaneously
            df = basedf.query(
                "experiment == @e and condition == @cons and strain == @strs"
            )
            sfig = sns.FacetGrid(df, row=row, col=col)
            for (row_var, col_var), facet_df in df.groupby([row, col]):
                ax = sfig.axes[
                    sfig.row_names.index(row_var),
                    sfig.col_names.index(col_var),
                ]
                sns.lineplot(x=x, y=y, hue="well", data=facet_df, ax=ax)
                ax.set(xlabel="", ylabel="")
            sfig.set_axis_labels(x, y)
            sfig.set_titles()
            if title:
                sfig.fig.suptitle(title)
            else:
                sfig.fig.suptitle(e)
            if xlim is not None:
                plt.xlim(xlim)
            if ylim is not None:
                plt.ylim(ylim)
            if figsize and len(figsize) == 2:
                sfig.fig.set_figwidth(figsize[0])
                sfig.fig.set_figheight(figsize[1])
            plt.tight_layout()
            plt.show(block=False)
        else:
            # create one plot for each strain and condition
            for c in cons:
                for s in strs:
                    df = basedf.query(
                        "experiment == @e and condition == @c and strain == @s"
                    )
                    if df.empty:
                        if messages:
                            print(e + ":", "No data found for", s, "in", c)
                    else:
                        sfig = sns.relplot(
                            x=x,
                            y=y,
                            data=df,
                            hue="well",
                            kind=kind,
                            style=style,
                            size=size,
                            **kwargs,
                        )
                        if title:
                            sfig.fig.suptitle(title)
                        else:
                            sfig.fig.suptitle(e + ": " + s + " in " + c)
                        if xlim is not None:
                            plt.xlim(xlim)
                        if ylim is not None:
                            plt.ylim(ylim)
                        plt.tight_layout()
                        plt.show(block=False)


def plot_rs(
    x,
    y,
    basedf,
    exps,
    cons,
    strs,
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
    title=None,
    figsize=None,
    sortby=False,
    returnfacetgrid=False,
    **kwargs,
):
    """Plot time-series data from the .r or .s dataframes."""
    # plot time series
    df = basedf.query(
        "experiment == @exps and condition == @cons and strain == @strs"
    )
    if df.empty:
        print("No data found")
    else:
        if sortby:
            df = df.sort_values(by=gu.makelist(sortby))
        # add warnings for poor choice of seaborn's parameters - may cause
        # inadvertent averaging
        if hue == style:
            print(
                'Warning: "hue" and "style" have both been set to "'
                + hue
                + '" and there may be unintended averaging'
            )
        if (
            x != "commontime"
            and len(df["experiment"].unique()) > 1
            and hue != "experiment"
            and size != "experiment"
            and style != "experiment"
            and col != "experiment"
        ):
            print(
                "Warning: there are multiple experiments, but neither "
                '"hue", "style", nor "size" is set to "experiment" and there'
                " may be averaging over experiments"
            )

        if "units" not in kwargs:
            # try to augment df to allow seaborn to estimate errors
            df = augmentdf(df, y)
        # plot
        sfig = sns.relplot(
            x=x,
            y=y,
            data=df,
            hue=hue,
            kind=kind,
            style=style,
            errorbar="sd",
            size=size,
            col=col,
            row=row,
            aspect=aspect,
            height=height,
            **kwargs,
        )
        sfig.set_xlabels(gu.rm_under(x))
        sfig.set_ylabels(gu.rm_under(y))
        if title:
            sfig.fig.suptitle(title)
        if xlim is not None:
            sfig.set(xlim=xlim)
        if ylim is not None:
            sfig.set(ylim=ylim)
        if figsize and len(figsize) == 2:
            sfig.fig.set_figwidth(figsize[0])
            sfig.fig.set_figheight(figsize[1])
        plt.show(block=False)
        if returnfacetgrid:
            return sfig
        else:
            return None


def plot_sc(
    x,
    y,
    basedf,
    exps,
    cons,
    strs,
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
    figsize=None,
    title=None,
    sortby=False,
    **kwargs,
):
    """Plot summary statistics from the .sc dataframe."""
    # plot summary stats
    df = basedf.query(
        "experiment == @exps and condition == @cons and strain == @strs"
    )
    xcols = df.columns[df.columns.str.startswith(x)]
    ycols = df.columns[df.columns.str.startswith(y)]
    df = df[
        np.unique(
            ["experiment", "condition", "strain"] + list(xcols) + list(ycols)
        )
    ].dropna()
    if df.empty:
        print("No data found")
    else:
        if sortby:
            df = df.sort_values(by=gu.makelist(sortby))
        sfig = sns.relplot(
            x=x,
            y=y,
            data=df,
            hue=hue,
            kind="scatter",
            style=style,
            size=size,
            col=col,
            row=row,
            aspect=aspect,
            height=height,
            **kwargs,
        )
        sfig.set_xlabels(gu.rm_under(x))
        sfig.set_ylabels(gu.rm_under(y))
        if xlim is not None:
            sfig.set(xlim=xlim)
        if ylim is not None:
            sfig.set(ylim=ylim)
        if row is None and col is None:
            # add error bars
            # find coordinates of points in relplot
            xc, yc = [], []
            for point_pair in sfig.ax.collections:
                for xp, yp in point_pair.get_offsets():
                    xc.append(xp)
                    yc.append(yp)
            # add error bars
            xerr = df[x + "_err"] if x + "_err" in df.columns else None
            yerr = df[y + "_err"] if y + "_err" in df.columns else None
            sfig.ax.errorbar(
                xc,
                yc,
                xerr=xerr,
                yerr=yerr,
                fmt=" ",
                ecolor="dimgray",
                alpha=0.5,
            )
        plt.show(block=False)


def plotfinddf(self, x, y):
    """
    Find the correct dataframe for plotting y versus x.

    Parameters
    ----------
    self: a platereader instance
    x: string
        Name of x-variable.
    y: string
        Name of y-variable.

    Returns
    -------
    basedf: dataframe
        The dataframe that contains the x and y variables.
    dfname: string
        The name of the dataframe.
    """
    # choose the correct dataframe
    if hasattr(self, "r") and x in self.r.columns and y in self.r.columns:
        # raw data (with wells)
        basedf = self.r
        dfname = "r"
    elif x in self.s.columns and y in self.s.columns:
        # processed data (no wells)
        basedf = self.s
        dfname = "s"
    elif x in self.sc.columns and y in self.sc.columns:
        # summary stats
        basedf = self.sc
        dfname = "sc"
    else:
        raise errors.PlotError(
            f"The variables x= {x}"
            + f" and y= {y}"
            + " cannot be plotted against each other because they are not in "
            + " the same dataframe"
        )
    return basedf, dfname


def augmentdf(df, datatype):
    """
    Augment dataframe to allow Seaborn to errors.

    Use 'err' (if present in the dataframe) to allow Seaborn to generate
    errors in relplot, otherwise returns original dataframe.

    Note we call seaborn with errorbar = "sd" and so use sqrt(3/2) * error
    because seaborn calculates the standard deviation from the augmented data
    (the mean, the mean + std, and the mean - std) and so gets
    std/sqrt(3/2) otherwise because there are three data points.
    """
    if datatype + "_err" in df:
        derr = datatype + "_err"
    elif "mean" in datatype and datatype.split("_mean")[0] + "_err" in df:
        derr = datatype.split("_mean")[0] + "_err"
    else:
        derr = False
        # returned if df is df_r
        return df
    if derr:
        df.insert(0, "augtype", "mean")
        mn = df[datatype].to_numpy()
        err = df[derr].to_numpy()
        # add std
        dfp = df.copy()
        dfp[datatype] = mn + np.sqrt(3 / 2) * err
        dfp["augtype"] = "+err"
        # minus std
        dfm = df.copy()
        dfm[datatype] = mn - np.sqrt(3 / 2) * err
        dfm["augtype"] = "-err"
        # concat
        df = pd.concat([df, dfp, dfm], ignore_index=True)
    return df
