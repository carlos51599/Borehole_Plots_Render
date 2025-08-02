"""
Main Section Plotting Interface

This module provides the main plotting functions that coordinate
all the modular components for professional geological cross-section plotting.
"""

# Configure matplotlib backend BEFORE any pyplot imports
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for server environments

import logging
from typing import Tuple, Optional, Dict, List, Union, Any
import matplotlib.pyplot as plt

# Import modular components
from .coordinates import prepare_coordinate_data
from .geology import (
    create_geology_mappings,
    plot_geological_intervals,
    plot_ground_surface,
    create_professional_legend,
    calculate_borehole_width,
)
from .layout import (
    create_professional_layout,
    add_professional_formatting,
    add_professional_footer,
    add_title_and_header,
    set_axis_limits_and_aspect,
    optimize_layout_for_legend,
)

# Import utilities
from ..parsing import parse_ags_geol_section_from_string
from ..utils import (
    convert_figure_to_base64,
    save_high_resolution_outputs,
    safe_close_figure,
    matplotlib_figure,
)

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
    # Fallback constants
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27
    DEFAULT_DPI = 300
    DEFAULT_COLOR_ALPHA = 0.7
    DEFAULT_HATCH_ALPHA = 0.4

logger = logging.getLogger(__name__)


def plot_professional_borehole_sections(
    ags_data: List[Tuple[str, str]],
    section_line: Optional[List[Tuple[float, float]]] = None,
    show_labels: bool = True,
    figsize: Tuple[float, float] = (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
    dpi: int = DEFAULT_DPI,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
    output_high_res: bool = False,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Create a professional geological cross-section plot with BGS standards compliance.

    Args:
        ags_data: List of (filename, content) tuples containing AGS data
        section_line: Optional polyline coordinates for projection [(lat1, lon1), ...]
        show_labels: Whether to show borehole labels
        figsize: Figure size in inches (width, height)
        dpi: Figure resolution
        color_alpha: Alpha value for geological fill colors
        hatch_alpha: Alpha value for geological patterns
        output_high_res: Whether to save high-resolution outputs

    Returns:
        Tuple of (base64_image, svg_content, pdf_path) or error message
    """
    logger.info("Starting professional borehole sections plot generation")

    try:
        # Parse AGS data - handle the list of tuples format
        if len(ags_data) != 1:
            error_msg = "Multiple AGS files not supported in current implementation"
            logger.error(error_msg)
            return error_msg, None, None

        filename, ags_content = ags_data[0]

        # Parse using the tuple-returning function and convert to expected format
        try:
            geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)

            # Create success wrapper that the rest of the function expects
            parse_result = {
                "success": True,
                "geol_df": geol_df,
                "loca_df": loca_df,
                "abbr_df": abbr_df,
                "title": f"Cross-Section from {filename}",
                "error": None,
            }

        except Exception as parse_error:
            logger.error(f"AGS parsing failed: {parse_error}")
            return f"AGS parsing failed: {str(parse_error)}", None, None

        if not parse_result["success"]:
            error_msg = (
                f"AGS parsing failed: {parse_result.get('error', 'Unknown error')}"
            )
            logger.error(error_msg)
            return error_msg, None, None

        geol_df = parse_result["geol_df"]
        loca_df = parse_result["loca_df"]
        abbr_df = parse_result.get("abbr_df")
        ags_title = parse_result.get("title", "Cross-Section")

        logger.info(
            f"Parsed AGS data: {len(geol_df)} geological records, {len(loca_df)} locations"
        )

        # Prepare coordinate data
        coord_data = prepare_coordinate_data(geol_df, loca_df, section_line)
        if coord_data is None:
            error_msg = "Failed to prepare coordinate data for plotting"
            logger.error(error_msg)
            return error_msg, None, None

        merged_df = coord_data["merged_df"]
        borehole_x_map = coord_data["borehole_x_map"]
        ordered_boreholes = coord_data["ordered_boreholes"]

        logger.info(f"Coordinate data prepared for {len(ordered_boreholes)} boreholes")

        # Calculate elevations
        merged_df["ELEV_TOP"] = merged_df["LOCA_GL"] - merged_df["GEOL_TOP"].abs()
        merged_df["ELEV_BASE"] = merged_df["LOCA_GL"] - merged_df["GEOL_BASE"].abs()

        # Create geology mappings
        color_map, hatch_map, leg_label_map = create_geology_mappings(
            merged_df, abbr_df
        )

        # Calculate borehole width
        borehole_width = calculate_borehole_width(
            borehole_x_map, len(ordered_boreholes)
        )

        # Create professional layout
        with matplotlib_figure():
            fig, ax = create_professional_layout(figsize, dpi, ags_title)

            # Plot geological intervals
            plot_geological_intervals(
                ax,
                merged_df,
                borehole_x_map,
                ordered_boreholes,
                color_map,
                hatch_map,
                borehole_width,
                color_alpha,
                hatch_alpha,
            )

            # Plot ground surface
            plot_ground_surface(
                ax, merged_df, borehole_x_map, ordered_boreholes, borehole_width
            )

            # Set axis limits and aspect
            set_axis_limits_and_aspect(ax, merged_df, borehole_x_map)

            # Add professional formatting
            add_professional_formatting(
                ax, merged_df, borehole_x_map, ordered_boreholes, show_labels
            )

            # Add title and header
            add_title_and_header(fig, ax, ags_title, figsize)

            # Optimize layout for legend
            has_legend = bool(color_map)
            optimize_layout_for_legend(fig, ax, has_legend, figsize)

            # Create legend
            if has_legend:
                create_professional_legend(
                    ax, color_map, hatch_map, leg_label_map, figsize
                )

            # Add footer
            add_professional_footer(fig, figsize)

            # Convert to outputs
            logger.info("Converting plot to output formats")
            base64_img = convert_figure_to_base64(fig)

            svg_content = None
            pdf_path = None
            if output_high_res:
                svg_content, pdf_path = save_high_resolution_outputs(
                    fig, "professional_section"
                )

            safe_close_figure(fig)

            logger.info("Professional section plot generation completed successfully")
            return base64_img, svg_content, pdf_path

    except Exception as e:
        logger.error(f"Error in professional section plotting: {e}", exc_info=True)
        error_msg = f"Section plotting failed: {str(e)}"
        return error_msg, None, None


def plot_section_from_ags_content(
    ags_content: str,
    filename: str = "section.ags",
    section_line: Optional[List[Tuple[float, float]]] = None,
    show_labels: bool = True,
    figsize: Tuple[float, float] = (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
    dpi: int = DEFAULT_DPI,
    filter_loca_ids: Optional[List[str]] = None,
    return_base64: bool = True,
    save_high_res: bool = False,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
) -> Union[str, Tuple[str, Optional[str], Optional[str]], plt.Figure]:
    """
    Convenience function to plot section from AGS content string using modular structure.

    Args:
        ags_content: AGS file content as string
        filename: Filename for the AGS data (for logging only)
        section_line: Optional polyline coordinates for projection
        show_labels: Whether to show borehole labels
        figsize: Figure size in inches (width, height)
        dpi: Figure resolution
        filter_loca_ids: Optional list of location IDs to filter
        return_base64: If True return base64, if False return matplotlib Figure
        save_high_res: Whether to save high-resolution outputs
        color_alpha: Transparency for geological colors
        hatch_alpha: Transparency for hatch patterns

    Returns:
        - If return_base64=True and not save_high_res: Base64 image string
        - If return_base64=True and save_high_res: Tuple of (base64, svg, pdf)
        - If return_base64=False: matplotlib Figure object
    """
    logger.info(
        f"Plotting section from AGS content: {filename} (return_base64={return_base64})"
    )

    try:
        # Use the modular plotting function
        ags_data = [(filename, ags_content)]

        if return_base64:
            # Use modular plotting for base64 output
            result = plot_professional_borehole_sections(
                ags_data=ags_data,
                section_line=section_line,
                show_labels=show_labels,
                figsize=figsize,
                dpi=dpi,
                color_alpha=color_alpha,
                hatch_alpha=hatch_alpha,
                output_high_res=save_high_res,
            )

            if save_high_res:
                # Return tuple format for high-res mode
                return result
            else:
                # Return just base64 string for simple mode
                base64_result, _, _ = result
                return base64_result
        else:
            # For Figure object output, use archive implementation directly
            return _plot_professional_archive_exact(
                ags_content=ags_content,
                filter_loca_ids=filter_loca_ids,
                section_line=section_line,
                show_labels=show_labels,
                save_high_res=save_high_res,
                return_base64=False,
                figsize=figsize,
                dpi=dpi,
                color_alpha=color_alpha,
                hatch_alpha=hatch_alpha,
            )

    except Exception as e:
        logger.error(f"Error in professional section plotting: {e}")
        return None


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
    import numpy as np
    import pandas as pd
    import pyproj
    import re
    from matplotlib.patches import Patch, Rectangle

    # Parse AGS data using modular parsing
    from ..parsing import parse_ags_geol_section_from_string
    from ..utils import get_geology_color, get_geology_pattern, convert_figure_to_base64, safe_close_figure
    
    logger.info("Starting professional borehole sections plot generation")
    
    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)

    if filter_loca_ids is not None:
        geol_df = geol_df[geol_df["LOCA_ID"].isin(filter_loca_ids)]
        loca_df = loca_df[loca_df["LOCA_ID"].isin(filter_loca_ids)]

    if geol_df.empty or loca_df.empty:
        logger.warning("No data available after filtering")
        return None

    logger.info(f"Parsed AGS data: {len(geol_df)} geological records, {len(loca_df)} locations")

    # REST OF ARCHIVE IMPLEMENTATION GOES HERE - EXACT COPY
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

    # Professional margins - EXACT ARCHIVE VALUES
    left_margin_in = 0.5
    right_margin_in = 0.5
    top_margin_in = 0.3
    bottom_margin_in = 0.3
    header_height_in = 1.5  # Reduced for landscape format

    # Calculate usable plot area
    plot_width_in = a4_width_in - left_margin_in - right_margin_in
    plot_height_in = a4_height_in - top_margin_in - bottom_margin_in - header_height_in

    # Create figure with A4 landscape dimensions
    fig = plt.figure(figsize=(a4_width_in, a4_height_in), dpi=dpi)
    fig.patch.set_facecolor("white")

    # Create subplot with professional margins
    ax = fig.add_subplot(111)

    # Position the plot area within the figure with proper margins - EXACT ARCHIVE CALCULATION
    plot_left = left_margin_in / a4_width_in
    plot_bottom = bottom_margin_in / a4_height_in
    plot_width_frac = plot_width_in / a4_width_in
    plot_height_frac = plot_height_in / a4_height_in

    ax.set_position([plot_left, plot_bottom, plot_width_frac, plot_height_frac])

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

    # Professional borehole labels - EXACT ARCHIVE POSITIONING
    from app_constants import SECTION_PLOT_AXIS_FONTSIZE
    label_y = 1.05
    rel_x = np.array(list(bh_x_map.values()))

    for i, bh in enumerate(boreholes):
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

    ax.set_xlabel("Distance along section (m)", fontsize=11, weight="bold")
    ax.set_ylabel("Elevation (m AOD)", fontsize=11, weight="bold")

    # Set professional y-limits - EXACT ARCHIVE CALCULATION
    elev_max = merged[["ELEV_TOP", "ELEV_BASE"]].max().max()
    elev_min = merged[["ELEV_TOP", "ELEV_BASE"]].min().min()
    elev_range = elev_max - elev_min
    ax.set_ylim(elev_min - elev_range * 0.1, elev_max + elev_range * 0.15)
    ax.set_xlim(rel_x.min() - total_length * 0.05, rel_x.max() + total_length * 0.05)

    # Professional title with proper positioning for A4 landscape - EXACT ARCHIVE POSITIONING
    ags_title = "Geological Cross-Section"

    # Position title in the header area
    title_y = (a4_height_in - top_margin_in - header_height_in / 2) / a4_height_in
    fig.suptitle(ags_title, fontsize=14, weight="bold", y=title_y, ha="center")

    # Professional legend with color and hatch patterns - EXACT ARCHIVE LEGEND
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

    # Add professional footer at the bottom of the figure - EXACT ARCHIVE FOOTER
    footer_height_in = 1.5  # Match header height from borehole log
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
    # Draw footer row: two cells, left 70%, right 30%
    left_frac = 0.7
    right_frac = 0.3
    y_pos = 0.5  # Vertically center text in footer
    # Draw left cell rectangle
    footer_ax.add_patch(
        Rectangle(
            (0, 0), left_frac, 1, edgecolor="black", facecolor="none", linewidth=1
        )
    )
    # Draw right cell rectangle
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

    except Exception as e:
        logger.error(f"Error in professional section plotting: {e}")
        return None

            except Exception as parse_error:
                error_msg = f"AGS parsing failed: {str(parse_error)}"
                logger.error(error_msg)
                # Return empty figure with error message
                fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                ax.text(
                    0.5,
                    0.5,
                    error_msg,
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"Parsing Error: {filename}")
                return fig

            # Apply filtering if specified
            if filter_loca_ids is not None:
                logger.info(f"Filtering to locations: {filter_loca_ids}")
                geol_df = geol_df[geol_df["LOCA_ID"].isin(filter_loca_ids)]
                loca_df = loca_df[loca_df["LOCA_ID"].isin(filter_loca_ids)]

                if geol_df.empty or loca_df.empty:
                    logger.warning("No data available after filtering")
                    # Return empty figure with warning
                    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                    ax.text(
                        0.5,
                        0.5,
                        "No data available after filtering",
                        ha="center",
                        va="center",
                        transform=ax.transAxes,
                    )
                    ax.set_title(f"No Data: {filename}")
                    return fig

            logger.info(
                f"Parsed AGS data: {len(geol_df)} geological records, {len(loca_df)} locations"
            )

            # Use modular components to build the figure
            coord_data = prepare_coordinate_data(geol_df, loca_df, section_line)
            if coord_data is None:
                error_msg = "Failed to prepare coordinate data for plotting"
                logger.error(error_msg)
                fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                ax.text(
                    0.5,
                    0.5,
                    error_msg,
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"Coordinate Error: {filename}")
                return fig

            merged_df = coord_data["merged_df"]
            borehole_x_map = coord_data["borehole_x_map"]
            ordered_boreholes = coord_data["ordered_boreholes"]

            # Calculate elevations
            merged_df["ELEV_TOP"] = merged_df["LOCA_GL"] - merged_df["GEOL_TOP"].abs()
            merged_df["ELEV_BASE"] = merged_df["LOCA_GL"] - merged_df["GEOL_BASE"].abs()

            # Create geology mappings (this will load from CSV)
            color_map, hatch_map, leg_label_map = create_geology_mappings(
                merged_df, abbr_df
            )

            # Calculate borehole width
            borehole_width = calculate_borehole_width(
                borehole_x_map, len(ordered_boreholes)
            )

            # Create figure and axis
            fig, ax = create_professional_layout(figsize, dpi, ags_title)

            # Plot geological intervals
            plot_geological_intervals(
                ax,
                merged_df,
                borehole_x_map,
                ordered_boreholes,
                color_map,
                hatch_map,
                borehole_width,
                color_alpha,
                hatch_alpha,
            )

            # Plot ground surface
            plot_ground_surface(
                ax, merged_df, borehole_x_map, ordered_boreholes, borehole_width
            )

            # Set axis limits and aspect
            set_axis_limits_and_aspect(ax, merged_df, borehole_x_map)

            # Add professional formatting
            add_professional_formatting(
                ax, merged_df, borehole_x_map, ordered_boreholes, show_labels
            )

            # Add title and header
            add_title_and_header(fig, ax, ags_title, figsize)

            # Optimize layout for legend
            has_legend = bool(color_map)
            optimize_layout_for_legend(fig, ax, has_legend, figsize)

            # Create legend
            if has_legend:
                create_professional_legend(
                    ax, color_map, hatch_map, leg_label_map, figsize
                )

            # Add footer
            add_professional_footer(fig, figsize)

            logger.info(
                "Successfully created matplotlib Figure using modular structure"
            )
            return fig

    except Exception as e:
        logger.error(f"Error in plot_section_from_ags_content: {e}", exc_info=True)
        if return_base64:
            return f"Error generating plot: {str(e)}"
        else:
            # Return error figure
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            ax.text(
                0.5,
                0.5,
                f"Error: {str(e)}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title(f"Error: {filename}")
            return fig
