"""
Section Plotting Module

This module provides professional geological cross-section plotting functionality
with BGS standards compliance and Openground-style formatting.

Key Functions:
- plot_professional_borehole_sections: Main plotting function for professional sections
- plot_section_from_ags_content: Convenience function for plotting from AGS content
- _prepare_coordinate_data: Coordinate transformation and preparation
- _create_professional_layout: Figure layout and formatting
- _plot_geological_intervals: Geological interval plotting with colors and patterns
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Patch, Rectangle
import pyproj
import re
import logging
from typing import Tuple, Optional, Dict, List, Union, Any

from .parsing import parse_ags_geol_section_from_string
from .utils import (
    convert_figure_to_base64,
    save_high_resolution_outputs,
    safe_close_figure,
    matplotlib_figure,
)

# Import constants from app_constants
try:
    from app_constants import (
        A4_LANDSCAPE_WIDTH,
        A4_LANDSCAPE_HEIGHT,
        DEFAULT_DPI,
        DEFAULT_COLOR_ALPHA,
        DEFAULT_HATCH_ALPHA,
        SECTION_PLOT_AXIS_FONTSIZE,
    )
except ImportError:
    # Fallback constants if app_constants not available
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27
    DEFAULT_DPI = 300
    DEFAULT_COLOR_ALPHA = 0.7
    DEFAULT_HATCH_ALPHA = 0.4
    SECTION_PLOT_AXIS_FONTSIZE = 10

# Import geology utilities
try:
    from geology_code_utils import get_geology_color, get_geology_pattern
except ImportError:
    # Fallback functions if geology_code_utils not available
    def get_geology_color(code):
        """Fallback color function"""
        return "#D3D3D3"

    def get_geology_pattern(code):
        """Fallback pattern function"""
        return ""


logger = logging.getLogger(__name__)


def plot_professional_borehole_sections(
    geol_df: pd.DataFrame,
    loca_df: pd.DataFrame,
    abbr_df: Optional[pd.DataFrame] = None,
    ags_title: Optional[str] = None,
    section_line: Optional[List[Tuple[float, float]]] = None,
    show_labels: bool = True,
    vertical_exaggeration: float = 3.0,
    save_high_res: bool = False,
    output_filename: Optional[str] = None,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
    return_base64: bool = True,
    figsize: Tuple[float, float] = (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
    dpi: int = DEFAULT_DPI,
) -> Union[str, plt.Figure, None]:
    """
    Plot professional-style borehole sections with Openground-style formatting.

    Args:
        geol_df: Geological data DataFrame
        loca_df: Location data DataFrame
        abbr_df: Abbreviations DataFrame (optional)
        ags_title: Title for the plot
        section_line: Section line coordinates for projection
        show_labels: Whether to show geological labels
        vertical_exaggeration: Vertical exaggeration factor (default 3.0)
        save_high_res: Whether to save high-resolution output
        output_filename: Output filename for saving (without extension)
        color_alpha: Transparency for geological colors (0.0-1.0)
        hatch_alpha: Transparency for hatch patterns (0.0-1.0)
        return_base64: If True, return base64-encoded PNG; if False, return Figure
        figsize: Figure size (width, height) in inches - default A4 landscape
        dpi: Resolution for the plot (default 300)

    Returns:
        Union[str, matplotlib.figure.Figure, None]: Base64-encoded PNG string,
        Figure object, or None if no data
    """
    logger.info(
        f"Creating professional section plot with {len(geol_df)} geological records"
    )

    # Prepare coordinate data and merge DataFrames
    merged_data = _prepare_coordinate_data(geol_df, loca_df, section_line)

    if merged_data is None or merged_data["merged"].empty:
        logger.warning("No valid coordinate data available for plotting")
        return None

    merged = merged_data["merged"]
    bh_x_map = merged_data["bh_x_map"]
    boreholes = merged_data["boreholes"]

    # Create professional color and hatch mappings
    color_map, hatch_map, leg_label_map = _create_geology_mappings(merged, abbr_df)

    # Create figure and layout
    fig, ax = _create_professional_layout(figsize, dpi, ags_title)

    # Calculate optimal borehole width
    width = _calculate_borehole_width(bh_x_map, len(boreholes))

    # Plot geological intervals
    _plot_geological_intervals(
        ax,
        merged,
        boreholes,
        bh_x_map,
        width,
        color_map,
        hatch_map,
        leg_label_map,
        color_alpha,
        hatch_alpha,
    )

    # Add ground surface line
    _plot_ground_surface(ax, merged, bh_x_map, boreholes)

    # Add professional formatting and labels
    _add_professional_formatting(ax, merged, bh_x_map, boreholes, width)

    # Add legend
    _add_professional_legend(ax, color_map, hatch_map, leg_label_map)

    # Add footer
    _add_professional_footer(fig, figsize)

    # Save high-resolution output if requested
    if save_high_res and output_filename:
        try:
            save_high_resolution_outputs(fig, output_filename, dpi)
        except Exception as e:
            logger.error(f"Failed to save high-resolution outputs: {e}")

    # Return based on requested format
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


def plot_section_from_ags_content(
    ags_content: str,
    filter_loca_ids: Optional[List[str]] = None,
    section_line: Optional[List[Tuple[float, float]]] = None,
    show_labels: bool = True,
    vertical_exaggeration: float = 3.0,
    save_high_res: bool = False,
    output_filename: Optional[str] = None,
    return_base64: bool = True,
    figsize: Tuple[float, float] = (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
    dpi: int = DEFAULT_DPI,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
) -> Union[str, plt.Figure, None]:
    """
    Create a professional geological section plot from AGS content.

    Args:
        ags_content: AGS file content as string
        filter_loca_ids: List of location IDs to include (optional)
        section_line: Section line coordinates for projection (optional)
        show_labels: Whether to show geological labels (default True)
        vertical_exaggeration: Vertical exaggeration factor (default 3.0)
        save_high_res: Whether to save high-resolution output (default False)
        output_filename: Output filename for saving (optional)
        return_base64: If True, return base64-encoded PNG; if False, return Figure
        figsize: Figure size (width, height) in inches - default A4 landscape
        dpi: Resolution for the plot (default 300)
        color_alpha: Transparency for geological colors (0.0-1.0)
        hatch_alpha: Transparency for hatch patterns (0.0-1.0)

    Returns:
        Union[str, matplotlib.figure.Figure, None]: Base64-encoded PNG string,
        Figure object, or None if no data
    """
    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)

    if filter_loca_ids is not None:
        geol_df = geol_df[geol_df["LOCA_ID"].isin(filter_loca_ids)]
        loca_df = loca_df[loca_df["LOCA_ID"].isin(filter_loca_ids)]

    if geol_df.empty or loca_df.empty:
        logger.warning("No data available after filtering")
        return None

    return plot_professional_borehole_sections(
        geol_df,
        loca_df,
        abbr_df,
        ags_title=None,
        section_line=section_line,
        show_labels=show_labels,
        vertical_exaggeration=vertical_exaggeration,
        save_high_res=save_high_res,
        output_filename=output_filename,
        return_base64=return_base64,
        figsize=figsize,
        dpi=dpi,
        color_alpha=color_alpha,
        hatch_alpha=hatch_alpha,
    )


def _prepare_coordinate_data(
    geol_df: pd.DataFrame,
    loca_df: pd.DataFrame,
    section_line: Optional[List[Tuple[float, float]]],
) -> Optional[Dict[str, Any]]:
    """
    Prepare coordinate data for plotting, handling coordinate transformations.

    Args:
        geol_df: Geological data DataFrame
        loca_df: Location data DataFrame
        section_line: Section line coordinates for projection

    Returns:
        Dict containing merged data, coordinate mappings, and borehole list
    """
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
        return _prepare_utm_coordinates(geol_df, loca_df, section_line)
    else:
        return _prepare_bng_coordinates(geol_df, loca_df)


def _prepare_utm_coordinates(
    geol_df: pd.DataFrame,
    loca_df: pd.DataFrame,
    section_line: List[Tuple[float, float]],
) -> Optional[Dict[str, Any]]:
    """Handle UTM coordinate transformation for polyline projection."""
    print("[DEBUG] Using polyline mode - need consistent coordinate system")

    try:
        from shapely.geometry import Point as ShapelyPoint, LineString
    except ImportError:
        logger.error("Shapely library required for polyline projection")
        return None

    # BNG to WGS84 transformer
    bng_to_wgs84 = pyproj.Transformer.from_crs(
        "EPSG:27700", "EPSG:4326", always_xy=True
    )

    # WGS84 to UTM Zone 30N transformer
    utm_crs = "EPSG:32630"
    wgs84_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)

    print(f"[DEBUG] Converting BNG -> WGS84 -> UTM ({utm_crs})")

    # Transform coordinates
    utm_coordinates = _transform_to_utm(loca_df, bng_to_wgs84, wgs84_to_utm)

    # Merge coordinates and LOCA_GL into geol_df
    loca_cols = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
    if "LOCA_GL" in loca_df.columns:
        loca_cols.append("LOCA_GL")

    merged = geol_df.merge(
        loca_df[loca_cols], left_on="LOCA_ID", right_on="LOCA_ID", how="left"
    )

    # Add UTM coordinates
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

    # Project boreholes onto section line
    bh_x_map = _project_onto_section_line(section_line, x_coords, y_coords, boreholes)

    return _finalize_coordinate_data(merged, bh_x_map, boreholes)


def _prepare_bng_coordinates(
    geol_df: pd.DataFrame, loca_df: pd.DataFrame
) -> Optional[Dict[str, Any]]:
    """Handle BNG coordinate preparation for standard plotting."""
    print("[DEBUG] Using standard mode with BNG coordinates")

    loca_cols = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
    if "LOCA_GL" in loca_df.columns:
        loca_cols.append("LOCA_GL")

    merged = geol_df.merge(
        loca_df[loca_cols], left_on="LOCA_ID", right_on="LOCA_ID", how="left"
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

    # Use easting as section orientation (default behavior)
    rel_x = x_coords - x_coords[0]
    bh_x_map = dict(zip(boreholes, rel_x))

    return _finalize_coordinate_data(merged, bh_x_map, boreholes)


def _transform_to_utm(
    loca_df: pd.DataFrame,
    bng_to_wgs84: pyproj.Transformer,
    wgs84_to_utm: pyproj.Transformer,
) -> Dict[str, Tuple[float, float]]:
    """Transform BNG coordinates to UTM."""
    # Hybrid vectorized + fallback loop for UTM conversion
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
                    f"[DEBUG] {loca_id}: BNG({bng_x[i]}, {bng_y[i]}) -> "
                    f"UTM({utm_x[i]:.1f}, {utm_y[i]:.1f})"
                )

    # Fallback loop for problematic rows
    for _, row in problem_df.iterrows():
        try:
            bng_x = float(row["LOCA_NATE"])
            bng_y = float(row["LOCA_NATN"])
            wgs84_lon, wgs84_lat = bng_to_wgs84.transform(bng_x, bng_y)
            utm_x, utm_y = wgs84_to_utm.transform(wgs84_lon, wgs84_lat)
            utm_coordinates[row["LOCA_ID"]] = (utm_x, utm_y)
        except (ValueError, TypeError) as e:
            print(f"[DEBUG] Skipping {row['LOCA_ID']} due to invalid coordinates: {e}")
            continue

    return utm_coordinates


def _project_onto_section_line(
    section_line: List[Tuple[float, float]],
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    boreholes: List[str],
) -> Dict[str, float]:
    """Project borehole coordinates onto section line."""
    try:
        from shapely.geometry import LineString, Point as ShapelyPoint
    except ImportError:
        logger.error("Shapely required for section line projection")
        return {}

    if len(section_line) > 2:
        # Polyline: project each borehole onto the closest point along the polyline
        print(f"[DEBUG] Processing polyline with {len(section_line)} points")
        line = LineString(section_line)
        rel_x = []
        for i, (x, y) in enumerate(zip(x_coords, y_coords)):
            point = ShapelyPoint(x, y)
            distance = line.project(point)
            rel_x.append(distance)
            print(f"[DEBUG] Borehole {boreholes[i]}: ({x}, {y}) -> distance {distance}")
        return dict(zip(boreholes, rel_x))
    else:
        # Two-point line: project each borehole onto the straight line
        (x0, y0), (x1, y1) = section_line
        dx = x1 - x0
        dy = y1 - y0
        line_length = np.hypot(dx, dy)
        if line_length == 0:
            rel_x = x_coords - x_coords[0]
        else:
            # Project using vector projection
            rel_x = ((x_coords - x0) * dx + (y_coords - y0) * dy) / line_length
        return dict(zip(boreholes, rel_x))


def _finalize_coordinate_data(
    merged: pd.DataFrame, bh_x_map: Dict[str, float], boreholes: List[str]
) -> Dict[str, Any]:
    """Finalize coordinate data preparation."""
    # Ensure LOCA_GL is available and numeric
    if "LOCA_GL" not in merged.columns:
        merged["LOCA_GL"] = 0.0
    merged["LOCA_GL"] = pd.to_numeric(merged["LOCA_GL"], errors="coerce").fillna(0.0)

    # Calculate elevation for each interval
    merged["ELEV_TOP"] = merged["LOCA_GL"] - merged["GEOL_TOP"].abs()
    merged["ELEV_BASE"] = merged["LOCA_GL"] - merged["GEOL_BASE"].abs()

    return {"merged": merged, "bh_x_map": bh_x_map, "boreholes": boreholes}


def _create_geology_mappings(
    merged: pd.DataFrame, abbr_df: Optional[pd.DataFrame]
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Create color, hatch, and label mappings for geological codes."""
    unique_leg = merged["GEOL_LEG"].unique()
    print(f"[DEBUG] Found {len(unique_leg)} unique GEOL_LEG codes: {unique_leg}")

    color_map = {}
    hatch_map = {}
    leg_label_map = {}

    for leg in unique_leg:
        color_map[leg] = get_geology_color(leg)
        hatch_map[leg] = get_geology_pattern(leg)

        # Build label using ABBR group if available
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
            # Fallback: first fully capitalized word(s) in GEOL_DESC
            if "GEOL_DESC" in merged.columns:
                descs = merged.loc[merged["GEOL_LEG"] == leg, "GEOL_DESC"]
                for desc in descs:
                    match = re.search(r"([A-Z]{2,}(?: [A-Z]{2,})*)", str(desc))
                    if match:
                        label = match.group(1)
                        break

        leg_label_map[leg] = f"{label} ({leg})"
        print(
            f"[DEBUG] GEOL_LEG '{leg}' -> Color: {color_map[leg]}, "
            f"Hatch: '{hatch_map[leg]}', Label: '{leg_label_map[leg]}'"
        )

    return color_map, hatch_map, leg_label_map


def _create_professional_layout(
    figsize: Tuple[float, float], dpi: int, ags_title: Optional[str]
) -> Tuple[plt.Figure, plt.Axes]:
    """Create professional figure layout with proper margins."""
    a4_width_in, a4_height_in = figsize

    # Professional margins
    left_margin_in = 0.5
    right_margin_in = 0.5
    top_margin_in = 0.3
    bottom_margin_in = 0.3
    header_height_in = 1.5

    # Calculate usable plot area
    plot_width_in = a4_width_in - left_margin_in - right_margin_in
    plot_height_in = a4_height_in - top_margin_in - bottom_margin_in - header_height_in

    # Create figure with A4 landscape dimensions
    fig = plt.figure(figsize=(a4_width_in, a4_height_in), dpi=dpi)
    fig.patch.set_facecolor("white")

    # Create subplot with professional margins
    ax = fig.add_subplot(111)

    # Position the plot area within the figure with proper margins
    plot_left = left_margin_in / a4_width_in
    plot_bottom = bottom_margin_in / a4_height_in
    plot_width_frac = plot_width_in / a4_width_in
    plot_height_frac = plot_height_in / a4_height_in

    ax.set_position([plot_left, plot_bottom, plot_width_frac, plot_height_frac])

    # Set up professional gridlines
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

    return fig, ax


def _calculate_borehole_width(bh_x_map: Dict[str, float], n_bhs: int) -> float:
    """Calculate optimal borehole width for plotting."""
    if n_bhs > 0:
        total_section_width = (
            max(bh_x_map.values()) - min(bh_x_map.values())
            if len(bh_x_map) > 1
            else 50.0
        )
        # Optimal width: use available plot width efficiently
        width = min(total_section_width / n_bhs * 0.8, 25.0)  # Max 25m width
        width = max(width, 2.0)  # Minimum 2m width for readability
    else:
        width = 5.0  # Default width

    print(f"[DEBUG] Calculated borehole width: {width:.1f}m for {n_bhs} boreholes")
    return width


def _plot_geological_intervals(
    ax: plt.Axes,
    merged: pd.DataFrame,
    boreholes: List[str],
    bh_x_map: Dict[str, float],
    width: float,
    color_map: Dict[str, str],
    hatch_map: Dict[str, str],
    leg_label_map: Dict[str, str],
    color_alpha: float,
    hatch_alpha: float,
) -> None:
    """Plot geological intervals with colors and patterns."""
    legend_labels_added = set()

    for bh in boreholes:
        bh_x = bh_x_map[bh]
        bh_df = (
            merged[merged["LOCA_ID"] == bh]
            .sort_values("GEOL_TOP")
            .reset_index(drop=True)
        )

        for _, row in bh_df.iterrows():
            leg = row["GEOL_LEG"]
            color = color_map.get(leg, "#D3D3D3")
            hatch = hatch_map.get(leg, "")
            legend_label = (
                leg_label_map[leg] if leg not in legend_labels_added else None
            )

            # Draw color (no hatch) with color_alpha
            ax.fill_betweenx(
                [row["ELEV_TOP"], row["ELEV_BASE"]],
                bh_x - width / 2,
                bh_x + width / 2,
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
                alpha=color_alpha,
                label=legend_label,
            )

            # Draw hatch overlay with hatch_alpha
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


def _plot_ground_surface(
    ax: plt.Axes, merged: pd.DataFrame, bh_x_map: Dict[str, float], boreholes: List[str]
) -> None:
    """Plot professional ground surface line."""
    # Get ground level for each borehole
    bh_gl_map = merged.groupby("LOCA_ID")["LOCA_GL"].first().to_dict()

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


def _add_professional_formatting(
    ax: plt.Axes,
    merged: pd.DataFrame,
    bh_x_map: Dict[str, float],
    boreholes: List[str],
    width: float,
) -> None:
    """Add professional formatting including labels and axes."""
    # Professional borehole labels
    label_y = 1.05
    rel_x = np.array(list(bh_x_map.values()))

    for bh in boreholes:
        bh_x = bh_x_map[bh]
        x_axes = (bh_x - (rel_x.min() - 2)) / ((rel_x.max() + 2) - (rel_x.min() - 2))
        ax.annotate(
            f"BH-{bh}",
            xy=(x_axes, label_y),
            xycoords=("axes fraction", "axes fraction"),
            ha="center",
            va="bottom",
            fontsize=SECTION_PLOT_AXIS_FONTSIZE,
            rotation=90,
            weight="bold",
            annotation_clip=False,
        )

    # Professional axis formatting
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

    ax.set_xlabel("Distance along section (m)", fontsize=11, weight="bold")
    ax.set_ylabel("Elevation (m AOD)", fontsize=11, weight="bold")

    # Set professional y-limits
    elev_max = merged[["ELEV_TOP", "ELEV_BASE"]].max().max()
    elev_min = merged[["ELEV_TOP", "ELEV_BASE"]].min().min()
    elev_range = elev_max - elev_min
    ax.set_ylim(elev_min - elev_range * 0.1, elev_max + elev_range * 0.15)
    ax.set_xlim(rel_x.min() - total_length * 0.05, rel_x.max() + total_length * 0.05)


def _add_professional_legend(
    ax: plt.Axes,
    color_map: Dict[str, str],
    hatch_map: Dict[str, str],
    leg_label_map: Dict[str, str],
) -> None:
    """Add professional legend with geological patterns."""
    legend_patches = []
    for leg in color_map.keys():
        label = leg_label_map[leg]
        patch = Patch(
            facecolor=color_map[leg],
            edgecolor="black",
            hatch=hatch_map[leg],
            label=label,
            linewidth=0.5,
        )
        legend_patches.append(patch)

    legend = ax.legend(
        handles=legend_patches,
        title="Geological Legend",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=True,
        fancybox=True,
        shadow=True,
        title_fontsize=11,
        fontsize=10,
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.9)


def _add_professional_footer(fig: plt.Figure, figsize: Tuple[float, float]) -> None:
    """Add professional footer to the figure."""
    a4_width_in, a4_height_in = figsize
    left_margin_in = 0.5
    bottom_margin_in = 0.3
    footer_height_in = 1.5
    a4_usable_width = a4_width_in - left_margin_in - 0.5  # right margin

    footer_ax = fig.add_axes(
        [
            left_margin_in / a4_width_in,
            bottom_margin_in / a4_height_in,
            a4_usable_width / a4_width_in,
            footer_height_in / a4_height_in,
        ]
    )
    footer_ax.axis("off")

    # Draw footer cells
    left_frac = 0.7
    right_frac = 0.3
    y_pos = 0.5

    # Left cell rectangle
    footer_ax.add_patch(
        Rectangle(
            (0, 0), left_frac, 1, edgecolor="black", facecolor="none", linewidth=1
        )
    )
    # Right cell rectangle
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

    # Add placeholder text
    footer_ax.text(
        0.02,
        y_pos,
        "Left Footer Placeholder",
        va="center",
        ha="left",
        fontsize=10,
        fontname="Arial",
    )
    footer_ax.text(
        left_frac + 0.02,
        y_pos,
        "Right Footer Placeholder",
        va="center",
        ha="left",
        fontsize=10,
        fontname="Arial",
    )
