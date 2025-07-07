import matplotlib.pyplot as plt
import pandas as pd
import io


def plot_borehole_log_from_ags_content(
    ags_content, loca_id, show_labels=True, fig_height=4, fig_width=2.5
):
    from section_plot import parse_ags_geol_section_from_string

    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)
    geol_bh = geol_df[geol_df["LOCA_ID"] == loca_id]
    loca_bh = loca_df[loca_df["LOCA_ID"] == loca_id]
    if geol_bh.empty or loca_bh.empty:
        return None
    gl = float(loca_bh.iloc[0]["LOCA_GL"]) if "LOCA_GL" in loca_bh.columns else 0.0
    width = 1.0
    geol_bh = geol_bh.copy()
    geol_bh["ELEV_TOP"] = gl - geol_bh["GEOL_TOP"].abs()
    geol_bh["ELEV_BASE"] = gl - geol_bh["GEOL_BASE"].abs()
    fig, ax = plt.subplots(
        figsize=(fig_width, fig_height), dpi=100, constrained_layout=False
    )
    plt.subplots_adjust(left=0.25, right=0.75, top=0.98, bottom=0.08)
    unique_leg = geol_bh["GEOL_LEG"].unique()
    color_map = {leg: plt.cm.tab20(i % 20) for i, leg in enumerate(unique_leg)}
    leg_label_map = {leg: leg for leg in unique_leg}
    bh_df = geol_bh.sort_values("GEOL_TOP").reset_index(drop=True)
    prev_leg = None
    group_start_idx = None
    legend_labels_added = set()
    for idx, row in bh_df.iterrows():
        leg = row["GEOL_LEG"]
        color = color_map.get(leg, (0.7, 0.7, 0.7, 1))
        elev_top = gl - abs(row["GEOL_TOP"])
        elev_base = gl - abs(row["GEOL_BASE"])
        if prev_leg != leg:
            if prev_leg is not None and group_start_idx is not None:
                group_rows = bh_df.iloc[group_start_idx:idx]
                if not group_rows.empty:
                    group_top = gl - abs(group_rows.iloc[0]["GEOL_TOP"])
                    group_base = gl - abs(group_rows.iloc[-1]["GEOL_BASE"])
                    label_elev = (group_top + group_base) / 2
                    if show_labels:
                        ax.text(
                            0,
                            label_elev,
                            str(prev_leg),
                            ha="center",
                            va="center",
                            fontsize=8,
                            color="k",
                            rotation=90,
                        )
                ax.fill_betweenx(
                    [group_top, group_base],
                    0 - width / 2,
                    0 + width / 2,
                    color=color_map.get(prev_leg, (0.7, 0.7, 0.7, 1)),
                    alpha=0.7,
                    label=(
                        leg_label_map[prev_leg]
                        if prev_leg not in legend_labels_added
                        else None
                    ),
                )
                legend_labels_added.add(prev_leg)
            prev_leg = leg
            group_start_idx = idx
    if prev_leg is not None and group_start_idx is not None:
        group_rows = bh_df.iloc[group_start_idx:]
        if not group_rows.empty:
            group_top = gl - abs(group_rows.iloc[0]["GEOL_TOP"])
            group_base = gl - abs(group_rows.iloc[-1]["GEOL_BASE"])
            label_elev = (group_top + group_base) / 2
            if show_labels:
                ax.text(
                    0,
                    label_elev,
                    str(prev_leg),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="k",
                    rotation=90,
                )
            ax.fill_betweenx(
                [group_top, group_base],
                0 - width / 2,
                0 + width / 2,
                color=color_map.get(prev_leg, (0.7, 0.7, 0.7, 1)),
                alpha=0.7,
                label=(
                    leg_label_map[prev_leg]
                    if prev_leg not in legend_labels_added
                    else None
                ),
            )
            legend_labels_added.add(prev_leg)
    ax.plot([-width / 2, width / 2], [gl, gl], color="k", lw=2)
    ax.set_xlim(-width, width)
    elev_max = max(gl, geol_bh["GEOL_TOP"].apply(lambda d: gl - abs(d)).max())
    elev_min = min(gl, geol_bh["GEOL_BASE"].apply(lambda d: gl - abs(d)).min())
    ax.set_ylim(elev_min - 0.5, elev_max + 1.5)
    ax.set_xlabel("")
    ax.set_ylabel("Elevation (m)")
    ax.set_xticks([])
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="Geology")
    plt.tight_layout(rect=[0, 0, 0.8, 1])
    return fig
