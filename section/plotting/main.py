"""
Main Section Plotting Interface

This module provides the main plotting functions that coordinate
all the modular components for professional geological cross-section plotting.
"""

import logging
from typing import Tuple, Optional, Dict, List, Union, Any

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
        # Parse AGS data
        parse_result = parse_ags_geol_section_from_string(ags_data)
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
    **kwargs,
) -> Union[str, Tuple[str, Optional[str], Optional[str]]]:
    """
    Convenience function to plot section from AGS content string.

    Args:
        ags_content: AGS file content as string
        filename: Filename for the AGS data
        section_line: Optional polyline coordinates
        show_labels: Whether to show borehole labels
        figsize: Figure size in inches
        dpi: Figure resolution
        **kwargs: Additional arguments passed to plot_professional_borehole_sections

    Returns:
        Base64 image string or tuple of (base64_image, svg_content, pdf_path)
    """
    logger.info(f"Plotting section from AGS content: {filename}")

    # Prepare AGS data
    ags_data = [(filename, ags_content)]

    # Call main plotting function
    result = plot_professional_borehole_sections(
        ags_data=ags_data,
        section_line=section_line,
        show_labels=show_labels,
        figsize=figsize,
        dpi=dpi,
        **kwargs,
    )

    # Return based on output format
    base64_img, svg_content, pdf_path = result

    if svg_content is not None or pdf_path is not None:
        return base64_img, svg_content, pdf_path
    else:
        return base64_img
