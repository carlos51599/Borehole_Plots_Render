"""
Main Section Plotting Interface with Exact Archive Implementation

This module provides the main plotting functions that use the exact archive
implementation to ensure consistent proportions and layout.
"""

# Configure matplotlib backend BEFORE any pyplot imports
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for server environments

import logging
from typing import Tuple, Optional, Dict, List, Union, Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import re
from matplotlib.patches import Patch, Rectangle

# Import constants
try:
    from app_constants import (
        A4_LANDSCAPE_WIDTH,
        A4_LANDSCAPE_HEIGHT,
        DEFAULT_DPI,
        DEFAULT_COLOR_ALPHA,
        DEFAULT_HATCH_ALPHA,
    )
except ImportError:
    # Fallback values if app_constants is not available
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27
    DEFAULT_DPI = 300
    # Alpha settings: INDEPENDENT SECTION PLOT ALPHA (different from borehole log alpha)
    DEFAULT_COLOR_ALPHA = (
        1.0  # SECTION PLOT: Full opacity for all boreholes in cross-section
    )
    DEFAULT_HATCH_ALPHA = 0.6


def get_logger():
    """Get logger for this module."""
    return logging.getLogger(__name__)


def plot_section_from_ags_content(
    ags_content: str,
    filter_loca_ids: Optional[List[str]] = None,
    section_line: Optional[List[Tuple[float, float]]] = None,
    show_labels: bool = True,
    save_high_res: bool = False,
    return_base64: bool = True,
    figsize: Tuple[float, float] = (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
    dpi: int = DEFAULT_DPI,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
) -> Union[str, plt.Figure, Tuple[str, Dict, plt.Figure], None]:
    """
    Create a professional geological cross-section plot from AGS data.
    Uses exact archive implementation for consistent proportions.
    """
    logger = get_logger()

    try:
        # Use exact archive implementation
        return _plot_professional_archive_exact(
            ags_content=ags_content,
            filter_loca_ids=filter_loca_ids,
            section_line=section_line,
            show_labels=show_labels,
            save_high_res=save_high_res,
            return_base64=return_base64,
            figsize=figsize,
            dpi=dpi,
            color_alpha=color_alpha,
            hatch_alpha=hatch_alpha,
        )

    except Exception as e:
        logger.error(f"Error in professional section plotting: {e}")
        return None


# Alias for backward compatibility
plot_professional_borehole_sections = plot_section_from_ags_content


def _plot_professional_archive_exact(
    ags_content: str,
    filter_loca_ids: Optional[List[str]] = None,
    section_line: Optional[List[Tuple[float, float]]] = None,
    show_labels: bool = True,
    save_high_res: bool = False,
    return_base64: bool = True,
    figsize: Tuple[float, float] = (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
    dpi: int = DEFAULT_DPI,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
) -> Union[str, plt.Figure, None]:
    """
    EXACT copy of archive plotting implementation to ensure consistent proportions.

    This is a direct port from archive/section_plot_professional_original.py
    to guarantee identical layout and proportions.
    """

    # Parse AGS data using modular parsing
    from ..parsing import parse_ags_geol_section_from_string
    from ..utils import convert_figure_to_base64, safe_close_figure
    from .geology import get_geology_color, get_geology_pattern

    logger = get_logger()
    logger.info("Starting professional borehole sections plot generation")

    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)

    if filter_loca_ids is not None:
        geol_df = geol_df[geol_df["LOCA_ID"].isin(filter_loca_ids)]
        loca_df = loca_df[loca_df["LOCA_ID"].isin(filter_loca_ids)]

    if geol_df.empty or loca_df.empty:
        logger.warning("No data available after filtering")
        return None

    logger.info(
        f"Parsed AGS data: {len(geol_df)} geological records, {len(loca_df)} locations"
    )

    # REST OF ARCHIVE IMPLEMENTATION - EXACT COPY
    merged = geol_df
    print(f"[DEBUG] Professional section plot called with section_line: {section_line}")
    print(f"[DEBUG] LOCA DataFrame shape: {loca_df.shape}")
    print(f"[DEBUG] LOCA DataFrame columns: {loca_df.columns.tolist()}")

    # Check what coordinate columns are available
    coord_cols = [
        col
        for col in loca_df.columns
        if any(x in col.upper() for x in ["NATE", "NATN", "LAT", "LON"])
    ]
    print(f"[DEBUG] Available coordinate columns: {coord_cols}")

    # Handle coordinate system for polyline mode
    if section_line is not None:
        print("[DEBUG] Using polyline mode - need consistent coordinate system")
        from shapely.geometry import Point as ShapelyPoint

        # BNG to WGS84 transformer
        bng_to_wgs84 = pyproj.Transformer.from_crs(
            "EPSG:27700", "EPSG:4326", always_xy=True
        )

        # WGS84 to UTM Zone 30N transformer
        utm_crs = "EPSG:32630"
        wgs84_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)

        print(f"[DEBUG] Converting BNG -> WGS84 -> UTM ({utm_crs})")

        # Hybrid vectorized + fallback loop for UTM conversion
        # 1. Identify rows with valid numeric LOCA_NATE and LOCA_NATN
        valid_mask = loca_df["LOCA_NATE"].apply(
            lambda x: pd.notnull(x)
            and str(x).replace(".", "", 1).replace("-", "", 1).isdigit()
        ) & loca_df["LOCA_NATN"].apply(
            lambda x: pd.notnull(x)
            and str(x).replace(".", "", 1).replace("-", "", 1).isdigit()
        )
        clean_df = loca_df[valid_mask].copy()
        problem_df = loca_df[~valid_mask].copy()

        utm_coordinates = {}
        # Vectorized transform for clean batch
        if not clean_df.empty:
            bng_x = clean_df["LOCA_NATE"].astype(float).values
            bng_y = clean_df["LOCA_NATN"].astype(float).values
            # BNG to WGS84
            wgs84_lon, wgs84_lat = bng_to_wgs84.transform(bng_x, bng_y)
            # WGS84 to UTM
            utm_x, utm_y = wgs84_to_utm.transform(wgs84_lon, wgs84_lat)
            for i, loca_id in enumerate(clean_df["LOCA_ID"].values):
                utm_coordinates[loca_id] = (utm_x[i], utm_y[i])
                if i < 3:
                    print(
                        f"[DEBUG] {loca_id}: BNG({bng_x[i]}, {bng_y[i]}) -> UTM({utm_x[i]:.1f}, {utm_y[i]:.1f})"
                    )

        # Fallback loop for problematic rows
        for _, row in problem_df.iterrows():
            try:
                bng_x = float(row["LOCA_NATE"])
                bng_y = float(row["LOCA_NATN"])
                wgs84_lon, wgs84_lat = bng_to_wgs84.transform(bng_x, bng_y)
                utm_x, utm_y = wgs84_to_utm.transform(wgs84_lon, wgs84_lat)
                utm_coordinates[row["LOCA_ID"]] = (utm_x, utm_y)
                if len(utm_coordinates) <= 3:
                    print(
                        f"[DEBUG] {row['LOCA_ID']}: BNG({bng_x}, {bng_y}) -> UTM({utm_x:.1f}, {utm_y:.1f})"
                    )
            except (ValueError, TypeError) as e:
                print(
                    f"[DEBUG] Skipping {row['LOCA_ID']} due to invalid coordinates: {e}"
                )
                continue

        # Merge coordinates and LOCA_GL into geol_df
        loca_cols = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
        if "LOCA_GL" in loca_df.columns:
            loca_cols.append("LOCA_GL")

        merged = geol_df.merge(
            loca_df[loca_cols],
            left_on="LOCA_ID",
            right_on="LOCA_ID",
            how="left",
        )

        # Add UTM coordinates based on the transformed coordinates
        merged["UTM_X"] = merged["LOCA_ID"].map(
            lambda x: utm_coordinates.get(x, (None, None))[0]
        )
        merged["UTM_Y"] = merged["LOCA_ID"].map(
            lambda x: utm_coordinates.get(x, (None, None))[1]
        )

        # Remove rows with missing UTM coordinates
        merged = merged.dropna(subset=["UTM_X", "UTM_Y"])

        if merged.empty:
            print("[DEBUG] No boreholes with valid UTM coordinates")
            return None

        # Get unique boreholes and their UTM coordinates
        borehole_utm = merged.groupby("LOCA_ID")[["UTM_X", "UTM_Y"]].first()
        boreholes = borehole_utm.index.tolist()
        x_coords = borehole_utm["UTM_X"].values
        y_coords = borehole_utm["UTM_Y"].values

        print(f"[DEBUG] Using UTM coordinates for {len(boreholes)} boreholes")
        print(f"[DEBUG] X coords (UTM): {x_coords[:3]}...")
        print(f"[DEBUG] Y coords (UTM): {y_coords[:3]}...")

    else:
        print("[DEBUG] Using standard mode with BNG coordinates")
        loca_cols = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
        if "LOCA_GL" in loca_df.columns:
            loca_cols.append("LOCA_GL")

        merged = geol_df.merge(
            loca_df[loca_cols],
            left_on="LOCA_ID",
            right_on="LOCA_ID",
            how="left",
        )

        # Remove rows with missing coordinates
        merged = merged.dropna(subset=["LOCA_NATE", "LOCA_NATN"])

        if merged.empty:
            print("No boreholes with valid coordinates to plot.")
            return None

        # Get unique boreholes and their coordinates
        borehole_x = merged.groupby("LOCA_ID")["LOCA_NATE"].first().sort_values()
        borehole_y = (
            merged.groupby("LOCA_ID")["LOCA_NATN"].first().reindex(borehole_x.index)
        )
        boreholes = borehole_x.index.tolist()
        x_coords = borehole_x.values
        y_coords = borehole_y.values

    # Ensure LOCA_GL is available in merged DataFrame
    if "LOCA_GL" not in merged.columns:
        if "LOCA_GL" in loca_df.columns:
            merged = merged.merge(
                loca_df[["LOCA_ID", "LOCA_GL"]], on="LOCA_ID", how="left"
            )
        else:
            merged["LOCA_GL"] = 0.0

    # Ensure LOCA_GL is numeric
    merged["LOCA_GL"] = pd.to_numeric(merged["LOCA_GL"], errors="coerce").fillna(0.0)

    # Calculate elevation for each interval
    merged["ELEV_TOP"] = merged["LOCA_GL"] - merged["GEOL_TOP"].abs()
    merged["ELEV_BASE"] = merged["LOCA_GL"] - merged["GEOL_BASE"].abs()

    # Project boreholes onto section line if provided
    if section_line is not None:
        try:
            from shapely.geometry import LineString
        except ImportError:
            print("You need to install the 'shapely' library. Run: pip install shapely")
            return None

        if isinstance(section_line, (list, tuple)) and len(section_line) > 2:
            # Polyline: project each borehole onto the closest point along the polyline
            print(f"[DEBUG] Processing polyline with {len(section_line)} points")
            line = LineString(section_line)
            rel_x = []
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                point = ShapelyPoint(x, y)
                distance = line.project(point)
                rel_x.append(distance)
                print(
                    f"[DEBUG] Borehole {boreholes[i]}: ({x}, {y}) -> distance {distance}"
                )
            bh_x_map = dict(zip(boreholes, rel_x))
        else:
            # Two-point line: project each borehole onto the straight line (PCA axis)
            (x0, y0), (x1, y1) = section_line
            dx = x1 - x0
            dy = y1 - y0
            line_length = np.hypot(dx, dy)
            if line_length == 0:
                rel_x = x_coords - x_coords[0]
            else:
                # Project each borehole onto the section line using vector projection
                rel_x = ((x_coords - x0) * dx + (y_coords - y0) * dy) / line_length
            bh_x_map = dict(zip(boreholes, rel_x))
    else:
        # Default: use easting as section orientation
        rel_x = x_coords - x_coords[0]
        bh_x_map = dict(zip(boreholes, rel_x))

    # Get ground level for each borehole
    bh_gl_map = merged.groupby("LOCA_ID")["LOCA_GL"].first().to_dict()

    # Create professional color and hatch mappings
    unique_leg = merged["GEOL_LEG"].unique()
    print(f"[DEBUG] Found {len(unique_leg)} unique GEOL_LEG codes: {unique_leg}")
    color_map = {}
    hatch_map = {}
    for leg in unique_leg:
        color_map[leg] = get_geology_color(leg)
        hatch_map[leg] = get_geology_pattern(leg)
        print(
            f"[DEBUG] GEOL_LEG '{leg}' -> Color: {color_map[leg]}, Hatch: '{hatch_map[leg]}'"
        )
    print(f"[DEBUG] Final color_map: {color_map}")
    print(f"[DEBUG] Final hatch_map: {hatch_map}")

    # Build labels for each GEOL_LEG using ABBR group if available
    leg_label_map = {}
    for leg in unique_leg:
        label = leg  # fallback
        if (
            abbr_df is not None
            and "ABBR_CODE" in abbr_df.columns
            and "ABBR_DESC" in abbr_df.columns
        ):
            abbr_match = abbr_df[abbr_df["ABBR_CODE"] == str(leg)]
            if not abbr_match.empty:
                label = abbr_match["ABBR_DESC"].iloc[0]
        else:
            # fallback to previous logic: first fully capitalized word(s) in GEOL_DESC
            if "GEOL_DESC" in merged.columns:
                descs = merged.loc[merged["GEOL_LEG"] == leg, "GEOL_DESC"]
                for desc in descs:
                    match = re.search(r"([A-Z]{2,}(?: [A-Z]{2,})*)", str(desc))
                    if match:
                        label = match.group(1)
                        break
        leg_label_map[leg] = f"{label} ({leg})"

    # Professional A4 landscape figure sizing and layout - EXACT ARCHIVE MARGINS
    a4_width_in = figsize[0]  # 11.69" for A4 landscape
    a4_height_in = figsize[1]  # 8.27" for A4 landscape

    # Professional margins - MATCHED: All margins equal for symmetrical layout
    left_margin_in = 0.3  # Changed to match top/bottom margins
    right_margin_in = 0.3  # Changed to match top/bottom margins
    top_margin_in = 0.3
    bottom_margin_in = 0.3
    # header_height_in removed - no title needed
    footer_height_in = 1.5  # FIXED: Reserve space for footer
    divider_space_in = 0.2  # NEW: Space for dividing line between plot and footer

    # Calculate usable plot area - OPTIMIZED: No header space, more room for plot
    plot_width_in = a4_width_in - left_margin_in - right_margin_in
    plot_height_in = (
        a4_height_in
        - top_margin_in
        - bottom_margin_in
        # No header_height_in subtraction - gives more space to plot
        - footer_height_in
        - divider_space_in  # NEW: Subtract space for dividing line
    )

    # Create figure with A4 landscape dimensions
    fig = plt.figure(figsize=(a4_width_in, a4_height_in), dpi=dpi)
    fig.patch.set_facecolor("white")

    # Create subplot with professional margins
    ax = fig.add_subplot(111)

    # SCALABLE TOTAL VISUAL BOX: Define complete visual area including plot + labels
    # This makes it easy to resize the total visual package and all elements scale proportionally
    #
    # TO RESIZE THE TOTAL VISUAL AREA: Simply modify the margin values above
    # The actual plot area will be calculated inside this box with proper label spacing
    #

    # STANDARDIZED FONTS: All text elements use Arial 8pt throughout figure
    # This includes borehole labels, plot axis labels/titles, footer text
    standard_fontsize = 8  # Arial 8pt for ALL text elements
    standard_fontfamily = "Arial"  # Consistent font family

    # TOTAL VISUAL BOX: Calculate buffer spaces for labels that extend beyond plot area
    # Convert font sizes to approximate inches (72 points per inch)
    axis_label_height_in = standard_fontsize / 72.0
    tick_label_height_in = standard_fontsize / 72.0

    # Calculate buffer spaces for labels extending beyond actual plot area
    top_buffer_in = 0.05  # MINIMAL TOP BUFFER: Extend plot area to top of bounding box
    bottom_buffer_in = (
        axis_label_height_in + tick_label_height_in + 0.2
    )  # X-axis label + ticks + padding
    left_buffer_in = (
        axis_label_height_in + tick_label_height_in + 0.3
    )  # Y-axis label + ticks + padding
    right_buffer_in = 0.05  # Small buffer for visual balance

    # Define total visual box that aligns with footer boundaries - ADJUSTED: Lower boundary = footer top
    footer_top_position = (bottom_margin_in + footer_height_in) / a4_height_in
    total_visual_box = {
        "left": left_margin_in / a4_width_in,  # Matches footer left boundary
        "bottom": footer_top_position,  # Lower boundary matches footer top exactly
        "width": plot_width_in / a4_width_in,  # Matches footer width
        "height": (plot_height_in + divider_space_in)
        / a4_height_in,  # Extended height to include divider space
    }

    # Calculate actual plot area INSIDE the total visual box, accounting for label buffers
    actual_plot_left = total_visual_box["left"] + (left_buffer_in / a4_width_in)
    actual_plot_bottom = total_visual_box["bottom"] + (bottom_buffer_in / a4_height_in)
    actual_plot_width = (
        total_visual_box["width"] - (left_buffer_in + right_buffer_in) / a4_width_in
    )
    actual_plot_height = (
        total_visual_box["height"] - (top_buffer_in + bottom_buffer_in) / a4_height_in
    )

    # Position the actual plot area within the total visual box
    ax.set_position(
        [actual_plot_left, actual_plot_bottom, actual_plot_width, actual_plot_height]
    )

    # SHOW INVISIBLE BOX: Draw the total visual box boundaries for visualization (solid black line)
    # This shows the area that aligns with the footer boundaries
    total_box_rect = plt.Rectangle(
        (total_visual_box["left"], total_visual_box["bottom"]),
        total_visual_box["width"],
        total_visual_box["height"],
        linewidth=1,  # STANDARDIZED: Use consistent line width for all boundaries
        edgecolor="black",  # Changed from red to black
        facecolor="none",
        transform=fig.transFigure,
        linestyle="-",  # Changed from dashed to solid
        alpha=1.0,  # Full opacity for black line
    )
    fig.patches.append(total_box_rect)

    # Calculate optimal borehole width based on available space and number of boreholes - EXACT ARCHIVE LOGIC
    n_bhs = len(boreholes)
    if n_bhs > 0:
        total_section_width = (
            max(bh_x_map.values()) - min(bh_x_map.values())
            if len(bh_x_map) > 1
            else 50.0
        )
        # Optimal width: use available plot width efficiently
        width = min(
            total_section_width / n_bhs * 0.8, 25.0
        )  # Max 25m width per borehole
        width = max(width, 2.0)  # Minimum 2m width for readability
    else:
        width = 5.0  # Default width

    print(f"[DEBUG] Calculated borehole width: {width:.1f}m for {n_bhs} boreholes")

    # Set up professional gridlines - EXACT ARCHIVE SETUP
    import matplotlib.ticker as ticker

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

    ax.grid(
        which="major",
        axis="both",
        linestyle="--",
        color="gray",
        linewidth=0.8,
        alpha=0.7,
    )
    ax.grid(
        which="minor",
        axis="both",
        linestyle=":",
        color="gray",
        linewidth=0.5,
        alpha=0.5,
    )

    # Plot geological intervals with professional styling - EXACT ARCHIVE PLOTTING
    legend_labels_added = set()

    for i, bh in enumerate(boreholes):
        bh_x = bh_x_map[bh]
        bh_df = (
            merged[merged["LOCA_ID"] == bh]
            .sort_values("GEOL_TOP")
            .reset_index(drop=True)
        )

        # Group consecutive intervals with the same GEOL_LEG for labeling
        prev_leg = None

        for idx, row in bh_df.iterrows():
            leg = row["GEOL_LEG"]
            color = color_map.get(leg, "#D3D3D3")
            hatch = hatch_map.get(leg, "")
            legend_label = (
                leg_label_map[leg] if leg not in legend_labels_added else None
            )
            # Draw color (no hatch) with color_alpha
            # SECTION PLOT COLOR ALPHA SETTING: This alpha controls transparency
            # for ALL boreholes in the section plot (different from borehole log alpha)
            ax.fill_betweenx(
                [row["ELEV_TOP"], row["ELEV_BASE"]],
                bh_x - width / 2,
                bh_x + width / 2,
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
                alpha=color_alpha,  # <-- SECTION PLOT ALPHA: Controls transparency for all boreholes in cross-section
                label=legend_label,
            )
            # Draw hatch overlay (transparent face, only hatch) with hatch_alpha
            if hatch:
                ax.fill_betweenx(
                    [row["ELEV_TOP"], row["ELEV_BASE"]],
                    bh_x - width / 2,
                    bh_x + width / 2,
                    facecolor="none",
                    hatch=hatch,
                    edgecolor="black",
                    linewidth=0.5,
                    alpha=hatch_alpha,
                    label=None,
                )
            if legend_label is not None:
                legend_labels_added.add(leg)
            if prev_leg != leg:
                prev_leg = leg

    # Draw professional ground surface line - EXACT ARCHIVE STYLE
    rel_x = np.array(list(bh_x_map.values()))
    sorted_indices = np.argsort(rel_x)
    sorted_boreholes = [boreholes[i] for i in sorted_indices]
    sorted_x = [bh_x_map[bh] for bh in sorted_boreholes]
    ground_levels = [bh_gl_map[bh] for bh in sorted_boreholes]

    ax.plot(
        sorted_x,
        ground_levels,
        color="black",
        linewidth=2.5,
        linestyle="-",
        zorder=100,
        label="Ground Level",
        marker="o",
        markersize=4,
        markerfacecolor="white",
        markeredgecolor="black",
        markeredgewidth=1,
    )

    # Professional axis formatting - EXACT ARCHIVE LOGIC
    total_length = rel_x.max() - rel_x.min()
    if total_length > 100:
        step = 20
    elif total_length > 50:
        step = 10
    elif total_length > 15:
        step = 5
    else:
        step = 2

    x_start = int(np.floor(rel_x.min() / step) * step)
    x_end = int(np.ceil(rel_x.max() / step) * step)
    x_tick_vals = np.arange(x_start, x_end + step, step)
    ax.set_xticks(x_tick_vals)
    ax.set_xticklabels([f"{int(x)}" for x in x_tick_vals])

    # Set axis labels with scalable fonts that adjust to plot box size
    ax.set_xlabel(
        "Distance along section (m)",
        fontsize=standard_fontsize,
        fontfamily=standard_fontfamily,
        weight="bold",
    )
    ax.set_ylabel(
        "Elevation (m AOD)",
        fontsize=standard_fontsize,
        fontfamily=standard_fontfamily,
        weight="bold",
    )

    # Set tick label font sizes to scale with plot box
    ax.tick_params(axis="both", which="major", labelsize=standard_fontsize)

    # Set professional y-limits - EXACT ARCHIVE CALCULATION
    elev_max = merged[["ELEV_TOP", "ELEV_BASE"]].max().max()
    elev_min = merged[["ELEV_TOP", "ELEV_BASE"]].min().min()
    elev_range = elev_max - elev_min
    # Set y limits with EXTENDED RANGE for borehole labels space
    # INCREASED: Extra space at top for full borehole label visibility
    ax.set_ylim(
        elev_min - elev_range * 0.1, elev_max + elev_range * 0.25
    )  # Changed from 0.15 to 0.25

    # Professional borehole labels - IMPROVED: Position directly above each borehole
    # Place labels just above the highest geology point for each borehole
    rel_x = np.array(list(bh_x_map.values()))
    for i, bh in enumerate(boreholes):
        bh_x = bh_x_map[bh]

        # Find the highest elevation for this borehole
        bh_data = merged[merged["LOCA_ID"] == bh]
        if not bh_data.empty:
            max_elev = bh_data["ELEV_TOP"].max()
            # Position label slightly above the highest point
            label_elev = (
                max_elev + elev_range * 0.02
            )  # 2% of elevation range above highest point
        else:
            # Fallback if no data
            label_elev = elev_max + elev_range * 0.02

        ax.annotate(
            f"BH-{bh}",
            xy=(bh_x, label_elev),
            xycoords="data",  # Use data coordinates instead of axes fraction
            ha="center",
            va="bottom",
            fontsize=standard_fontsize,  # Arial 8pt for borehole labels
            fontfamily=standard_fontfamily,
            rotation=90,
            weight="bold",
            annotation_clip=False,
        )

    # IMPROVED X-axis limits handling for clustered data
    # Fix for issue where clustered boreholes only used "left half" of plot
    data_span = rel_x.max() - rel_x.min()
    min_axis_span = 20.0  # Minimum 20m axis span for proper visualization

    if data_span < min_axis_span:
        # For clustered data: center the data and use minimum span
        data_center = (rel_x.min() + rel_x.max()) / 2
        x_margin = min_axis_span / 2
        x_min = data_center - x_margin
        x_max = data_center + x_margin
        print(
            f"[DEBUG] Clustered data detected (span: {data_span:.1f}m) - using centered axis: {x_min:.1f} to {x_max:.1f}"
        )
    else:
        # For spread data: use proportional margins
        margin = data_span * 0.1  # 10% margin on each side
        x_min = rel_x.min() - margin
        x_max = rel_x.max() + margin
        print(
            f"[DEBUG] Spread data detected (span: {data_span:.1f}m) - using proportional margins: {x_min:.1f} to {x_max:.1f}"
        )

    ax.set_xlim(x_min, x_max)

    # No title needed - gives more space for plot area

    # Add professional footer at the bottom of the figure - FIXED: Footer below plot area
    a4_usable_width = a4_width_in - left_margin_in - right_margin_in
    footer_ax = fig.add_axes(
        [
            left_margin_in / a4_width_in,
            bottom_margin_in / a4_height_in,
            a4_usable_width / a4_width_in,
            footer_height_in / a4_height_in,
        ]
    )
    footer_ax.axis("off")
    footer_ax.set_xlim(0, 1)
    footer_ax.set_ylim(0, 1)

    # Draw footer row: two cells, left 70%, right 30%
    left_frac = 0.7
    right_frac = 0.3
    y_pos = 0.5  # Vertically center text in footer

    # Draw left cell rectangle for legend
    footer_ax.add_patch(
        Rectangle(
            (0, 0), left_frac, 1, edgecolor="black", facecolor="none", linewidth=1
        )
    )
    # Draw right cell rectangle for project info
    footer_ax.add_patch(
        Rectangle(
            (left_frac, 0),
            right_frac,
            1,
            edgecolor="black",
            facecolor="none",
            linewidth=1,
        )
    )

    # Create legend in the left cell of footer - IMPROVED: Legend in footer
    legend_patches = []
    for leg in unique_leg:
        label = leg_label_map[leg]
        patch = Patch(
            facecolor=color_map[leg],
            edgecolor="black",
            hatch=hatch_map[leg],
            label=label,
            linewidth=0.5,
        )
        legend_patches.append(patch)

    # Position legend in left cell of footer - FIXED: Align at bottom of footer cell
    legend_margin = 0.010  # Reduced margin for more space in 4x4 layout
    legend_x = legend_margin  # Start closer to left edge
    legend_y = (
        0.20  # CHANGED: Start from bottom of footer cell instead of top (was 0.95)
    )
    legend_max_width = left_frac - (
        2 * legend_margin
    )  # Maximum usable width in left cell

    # Add geological legend as text in footer left cell
    footer_ax.text(
        legend_x,
        0.95,  # Keep title at top
        "Geological Legend:",
        va="top",
        ha="left",
        fontsize=standard_fontsize,  # Arial 8pt for footer legend title
        fontweight="bold",
        fontfamily=standard_fontfamily,
    )

    # Calculate optimal column layout to fit within bounds - UPDATED: 4x5 layout (4 columns, 5 rows)
    items_per_column = 5  # 5 rows per column
    max_columns = 4  # 4 columns maximum for 4x5 layout
    symbol_size = 0.015  # Reduced further for 4x5 layout
    text_offset = 0.004  # Reduced for tighter spacing

    # Estimate text width (conservative estimate based on average label length)
    avg_label_length = sum(len(leg_label_map[leg]) for leg in unique_leg) / len(
        unique_leg
    )
    estimated_text_width = (
        avg_label_length * 0.006
    )  # Rough estimate: 6 units per character

    # Calculate column width needed for symbol + text + margin
    min_column_width = (
        symbol_size + text_offset + estimated_text_width + 0.01
    )  # Small margin

    # Adjust number of columns if content won't fit
    if max_columns * min_column_width > legend_max_width:
        max_columns = 1  # Fall back to single column
        items_per_column = len(unique_leg)  # All items in one column

    column_width = legend_max_width / max_columns
    current_y = legend_y  # Start from bottom instead of subtracting

    for i, leg in enumerate(unique_leg):
        col = i // items_per_column
        row = i % items_per_column

        # Ensure we don't exceed column bounds
        if col >= max_columns:
            col = max_columns - 1
            row = i - (col * items_per_column)

        item_x = legend_x + (col * column_width)
        item_y = current_y + (
            row * 0.10
        )  # UPDATED: Reduced row spacing for 4x5 layout (5 rows need tighter spacing)

        # Ensure item stays within left cell bounds
        max_item_x = (
            left_frac - symbol_size - text_offset - estimated_text_width - legend_margin
        )
        if item_x > max_item_x:
            item_x = max_item_x

        # Add colored symbol
        footer_ax.add_patch(
            Rectangle(
                (item_x, item_y - symbol_size / 2),
                symbol_size,
                symbol_size,
                facecolor=color_map[leg],
                edgecolor="black",
                hatch=hatch_map[leg],
                linewidth=0.5,
            )
        )

        # Add label text with bounds checking
        text_x = item_x + symbol_size + text_offset
        max_text_x = left_frac - legend_margin

        # Truncate text if necessary to fit within bounds
        label_text = leg_label_map[leg]
        if text_x + estimated_text_width > max_text_x:
            # Use clip to prevent overflow
            footer_ax.text(
                text_x,
                item_y,
                label_text,
                va="center",
                ha="left",
                fontsize=standard_fontsize,  # Arial 8pt for legend items
                fontfamily=standard_fontfamily,
                clip_on=True,  # Enable clipping
            )
        else:
            footer_ax.text(
                text_x,
                item_y,
                label_text,
                va="center",
                ha="left",
                fontsize=standard_fontsize,  # Arial 8pt for legend items
                fontfamily=standard_fontfamily,
            )

    # Add project info in right cell
    footer_ax.text(
        left_frac + 0.02,
        y_pos,
        "Professional Geological Cross-Section\nGenerated by AGS Borehole Renderer",
        va="center",
        ha="left",
        fontsize=standard_fontsize,  # Arial 8pt for project info
        fontfamily=standard_fontfamily,
    )

    # Return based on requested format - EXACT ARCHIVE RETURN LOGIC
    if return_base64:
        try:
            img_b64 = convert_figure_to_base64(fig, dpi)
            safe_close_figure(fig)
            logger.info("Successfully created base64-encoded section plot")
            return img_b64
        except Exception as e:
            logger.error(f"Failed to convert figure to base64: {e}")
            safe_close_figure(fig)
            raise
    else:
        logger.info("Returning matplotlib Figure object")
        return fig
