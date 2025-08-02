"""
Geology Plotting Module

This module handles the geological aspects of section plotting,
including geology color/pattern mappings, interval plotting,
and legend creation.
"""

# Configure matplotlib backend BEFORE any pyplot imports
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for server environments

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


def get_geology_color(code):
    """Get geology color from the geology codes utility."""
    try:
        from geology_code_utils import get_geology_color

        return get_geology_color(code)
    except ImportError:
        return "#CCCCCC"  # Default gray


def get_geology_pattern(code):
    """Get geology pattern from the geology codes utility."""
    try:
        from geology_code_utils import get_geology_pattern

        return get_geology_pattern(code)
    except ImportError:
        return ""  # Default no pattern


def create_geology_mappings(
    merged: pd.DataFrame, abbr_df: Optional[pd.DataFrame]
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Create color, hatch, and label mappings for geological codes."""

    # Check if GEOL_LEG column exists, if not use GEOL_DESC
    if "GEOL_LEG" in merged.columns:
        unique_leg = merged["GEOL_LEG"].unique()
        logger.debug(f"Found {len(unique_leg)} unique GEOL_LEG codes: {unique_leg}")
        leg_column = "GEOL_LEG"
    elif "GEOL_DESC" in merged.columns:
        # Extract geological codes from descriptions or use descriptions as fallback
        unique_leg = merged["GEOL_DESC"].unique()
        logger.debug(
            f"Using GEOL_DESC as geology identifier: {len(unique_leg)} unique descriptions"
        )
        leg_column = "GEOL_DESC"
    else:
        logger.warning("No geology legend or description column found")
        return {}, {}, {}

    color_map = {}
    hatch_map = {}
    leg_label_map = {}

    for leg in unique_leg:
        # Try to extract geology code from description if using GEOL_DESC
        if leg_column == "GEOL_DESC":
            # Try to extract geology code from description (e.g., "CLAY:" -> "CLAY")
            match = re.search(r"([A-Z]{2,})", str(leg))
            geology_code = match.group(1) if match else str(leg)[:4].upper()
        else:
            geology_code = leg

        color_map[leg] = get_geology_color(geology_code)
        hatch_map[leg] = get_geology_pattern(geology_code)

        # Build label using ABBR group if available
        label = leg  # fallback
        if (
            abbr_df is not None
            and "ABBR_CODE" in abbr_df.columns
            and "ABBR_DESC" in abbr_df.columns
        ):
            abbr_match = abbr_df[abbr_df["ABBR_CODE"] == str(geology_code)]
            if not abbr_match.empty:
                label = abbr_match["ABBR_DESC"].iloc[0]
        else:
            # Fallback: first fully capitalized word(s) in GEOL_DESC
            if "GEOL_DESC" in merged.columns:
                descs = merged.loc[merged[leg_column] == leg, "GEOL_DESC"]
                for desc in descs:
                    match = re.search(r"([A-Z]{2,}(?: [A-Z]{2,})*)", str(desc))
                    if match:
                        label = match.group(1)
                        break

        leg_label_map[leg] = label

    logger.debug(f"Geology mappings created for {len(color_map)} codes")
    return color_map, hatch_map, leg_label_map


def plot_geological_intervals(
    ax: plt.Axes,
    merged_df: pd.DataFrame,
    borehole_x_map: Dict[str, float],
    ordered_boreholes: List[str],
    color_map: Dict[str, str],
    hatch_map: Dict[str, str],
    borehole_width: float,
    color_alpha: float = 0.7,
    hatch_alpha: float = 0.4,
) -> None:
    """
    Plot geological intervals for all boreholes on the cross-section.

    Args:
        ax: Matplotlib axes object
        merged_df: Merged geological and location data
        borehole_x_map: Mapping of borehole IDs to x-positions
        ordered_boreholes: List of boreholes in plotting order
        color_map: Geology code to color mapping
        hatch_map: Geology code to hatch pattern mapping
        borehole_width: Width of each borehole column
        color_alpha: Alpha value for fill colors
        hatch_alpha: Alpha value for hatch patterns
    """
    logger.debug("Plotting geological intervals...")

    interval_count = 0
    plotted_boreholes = set()

    for _, row in merged_df.iterrows():
        borehole_id = row["LOCA_ID"]
        if borehole_id not in ordered_boreholes:
            continue

        bh_x = borehole_x_map[borehole_id]
        plotted_boreholes.add(borehole_id)

        # Get geological properties
        leg = row["GEOL_LEG"]
        color = color_map.get(leg, "#CCCCCC")
        hatch = hatch_map.get(leg, "")

        # Calculate elevations
        elev_top = row["ELEV_TOP"]
        elev_base = row["ELEV_BASE"]
        thickness = elev_top - elev_base

        if thickness <= 0:
            continue  # Skip invalid intervals

        # Plot filled rectangle for geology color
        rect_fill = patches.Rectangle(
            (bh_x - borehole_width / 2, elev_base),
            borehole_width,
            thickness,
            facecolor=color,
            alpha=color_alpha,
            edgecolor="black",
            linewidth=0.5,
        )
        ax.add_patch(rect_fill)

        # Plot hatched rectangle for geology pattern (if any)
        if hatch:
            rect_hatch = patches.Rectangle(
                (bh_x - borehole_width / 2, elev_base),
                borehole_width,
                thickness,
                facecolor="none",
                hatch=hatch,
                alpha=hatch_alpha,
                edgecolor="black",
                linewidth=0.5,
            )
            ax.add_patch(rect_hatch)

        interval_count += 1

    logger.info(
        f"Plotted {interval_count} geological intervals "
        f"across {len(plotted_boreholes)} boreholes"
    )


def plot_ground_surface(
    ax: plt.Axes,
    merged_df: pd.DataFrame,
    borehole_x_map: Dict[str, float],
    ordered_boreholes: List[str],
    borehole_width: float,
) -> None:
    """
    Plot ground surface line connecting borehole tops.

    Args:
        ax: Matplotlib axes object
        merged_df: Merged geological and location data
        borehole_x_map: Mapping of borehole IDs to x-positions
        ordered_boreholes: List of boreholes in plotting order
        borehole_width: Width of each borehole column
    """
    logger.debug("Plotting ground surface...")

    # Get ground levels for each borehole
    ground_levels = {}
    for borehole_id in ordered_boreholes:
        bh_data = merged_df[merged_df["LOCA_ID"] == borehole_id]
        if not bh_data.empty:
            ground_level = bh_data["LOCA_GL"].iloc[0]
            ground_levels[borehole_id] = ground_level

    if len(ground_levels) < 2:
        logger.warning("Not enough boreholes for ground surface line")
        return

    # Create ground surface line
    x_coords = []
    y_coords = []

    for borehole_id in ordered_boreholes:
        if borehole_id in ground_levels:
            x_coords.append(borehole_x_map[borehole_id])
            y_coords.append(ground_levels[borehole_id])

    # Plot ground surface line
    ax.plot(
        x_coords,
        y_coords,
        color="brown",
        linewidth=2,
        linestyle="-",
        label="Ground Surface",
        zorder=10,
    )

    # Add ground level markers at each borehole
    for x, y in zip(x_coords, y_coords):
        ax.plot(x, y, "o", color="brown", markersize=4, zorder=11)

    logger.debug(f"Ground surface plotted with {len(x_coords)} points")


def create_professional_legend(
    ax: plt.Axes,
    color_map: Dict[str, str],
    hatch_map: Dict[str, str],
    leg_label_map: Dict[str, str],
    figsize: Tuple[float, float],
) -> None:
    """
    Create professional geological legend.

    Args:
        ax: Matplotlib axes object
        color_map: Geology code to color mapping
        hatch_map: Geology code to hatch pattern mapping
        leg_label_map: Geology code to label mapping
        figsize: Figure size tuple
    """
    logger.debug("Creating professional legend...")

    # Filter out codes that aren't actually plotted
    plotted_codes = [code for code in color_map.keys() if code in leg_label_map]

    if not plotted_codes:
        logger.warning("No geological codes to include in legend")
        return

    # Create legend elements
    legend_elements = []
    for code in sorted(plotted_codes):
        color = color_map[code]
        hatch = hatch_map.get(code, "")
        label = leg_label_map[code]

        # Create patch with color and hatch
        patch = patches.Patch(
            facecolor=color,
            hatch=hatch,
            edgecolor="black",
            linewidth=0.5,
            label=f"{code}: {label}",
        )
        legend_elements.append(patch)

    # Position legend based on figure size
    if figsize[0] > 10:  # Wide figure
        legend_bbox = (1.02, 1.0)
        legend_loc = "upper left"
    else:  # Narrow figure
        legend_bbox = (0.5, -0.15)
        legend_loc = "upper center"

    # Add legend to plot
    legend = ax.legend(
        handles=legend_elements,
        bbox_to_anchor=legend_bbox,
        loc=legend_loc,
        ncol=1 if figsize[0] > 10 else 2,
        fontsize=8,
        frameon=True,
        fancybox=True,
        shadow=True,
    )

    logger.debug(f"Legend created with {len(legend_elements)} geological codes")


def calculate_borehole_width(
    borehole_x_map: Dict[str, float], n_boreholes: int
) -> float:
    """
    Calculate appropriate borehole width for plotting using archived logic.

    Args:
        borehole_x_map: Mapping of borehole IDs to x-positions
        n_boreholes: Number of boreholes

    Returns:
        Calculated borehole width
    """
    if n_boreholes <= 0:
        return 5.0  # Default width

    if n_boreholes == 1:
        return 50.0  # Default width for single borehole

    # Calculate total section width
    x_positions = list(borehole_x_map.values())
    total_section_width = (
        max(x_positions) - min(x_positions) if len(x_positions) > 1 else 50.0
    )

    # Optimal width: use available space efficiently
    # Based on archived version logic
    width = min(
        total_section_width / n_boreholes * 0.8, 25.0
    )  # Max 25m width per borehole
    width = max(width, 2.0)  # Minimum 2m width for readability

    logger.debug(
        f"Calculated borehole width: {width:.1f}m for {n_boreholes} boreholes "
        f"(total width: {total_section_width:.1f}m)"
    )
    return width
