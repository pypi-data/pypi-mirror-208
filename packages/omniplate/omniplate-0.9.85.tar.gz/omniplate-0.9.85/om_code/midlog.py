# Find and analyse mid-log growth
import matplotlib.pylab as plt
import numpy as np
from nunchaku import Nunchaku

import om_code.admin as admin
import om_code.sunder as sunder


def find_midlog_stats(
    self, stat, min_duration, figs, exps, cons, strs, **kwargs
):
    """Find the stat of all variables in the s dataframe for mid-log growth."""
    for e in exps:
        for c in cons:
            for s in strs:
                # get OD data
                res = sunder.extractwells(
                    self.r, self.s, e, c, s, ["time", "OD"]
                )
                t, od = res[0], res[1]
                if len(od):
                    res_dict = {col: [] for col in self.s.columns}
                    print(f"\nFinding mid-log growth for {e} : {s} in {c}")
                    # run nunchaku on log(OD)
                    od[od < 0] = np.finfo(float).eps
                    X = np.median(t, axis=1)
                    Y = np.log(od.T)
                    nc = Nunchaku(
                        X,
                        Y,
                        prior=[-5, 5],
                        **kwargs,
                    )
                    num_segs, evidence = nc.get_number(max_num=6)
                    bds, bds_std = nc.get_iboundaries(num_segs)
                    res_df = nc.get_info(bds)
                    # pick midlog segment
                    t_st, t_en = pick_midlog(res_df, min_duration)
                    # plot nunchaku's results
                    if figs:
                        nc.plot(res_df, hlmax=None)
                        for tv in [t_st, t_en]:
                            iv = np.argmin((X - tv) ** 2)
                            plt.plot(
                                tv,
                                np.median(Y, axis=0)[iv],
                                "ks",
                                markersize=10,
                            )
                        plt.xlabel("time")
                        plt.ylabel("log(OD)")
                        plt.title(f"mid-log growth for {e} : {s} in {c}")
                        plt.show(block=False)
                    # find means over mid-log growth
                    sdf = self.s[
                        (self.s.experiment == e)
                        & (self.s.condition == c)
                        & self.s.strain.str.contains(s)
                    ]
                    midlog_sdf = sdf[(sdf.time >= t_st) & (sdf.time <= t_en)]
                    stat_fn = getattr(midlog_sdf, stat)
                    stats = stat_fn(numeric_only=True)
                    # store results in dict
                    res_dict["experiment"].append(e)
                    res_dict["condition"].append(c)
                    res_dict["strain"].append(s)
                    for key, value in zip(stats.index, stats.values):
                        res_dict[key].append(value)
                    # add "mid-log" to data names
                    res_dict = {
                        (
                            stat + "_midlog_" + k
                            if k not in ["experiment", "condition", "strain"]
                            else k
                        ): v
                        for k, v in res_dict.items()
                    }
                    # add to sc dataframe
                    admin.add_to_sc(self, res_dict)


def pick_midlog(res_df, min_duration):
    """Find midlog from nunchaku's results dataframe."""
    # find duration of each segment
    xs = np.array([np.array(i) for i in res_df["x range"].values])
    res_df["duration"] = np.diff(xs, axis=1)
    # midlog had a minimal duration and positive growth rate
    sdf = res_df[(res_df.duration > min_duration) & (res_df.gradient > 0)]
    # find mid-log growth - maximal specific growth rate
    ibest = sdf.index[sdf.gradient.argmax()]
    t_st, t_en = sdf["x range"][ibest]
    return t_st, t_en
