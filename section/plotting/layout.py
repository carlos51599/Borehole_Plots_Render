"""
Layout and Formatting Module

This module handles the figure layout, professional formatting,
axis setup, and visual styling for section plots.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Import constants
try:
    from app_constants import (
        A4_LANDSCAPE_WIDTH,
        A4_LANDSCAPE_HEIGHT,
        DEFAULT_DPI,
        SECTION_PLOT_AXIS_FONTSIZE,
    )
except ImportError:
    # Fallback constants
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27
    DEFAULT_DPI = 300
    SECTION_PLOT_AXIS_FONTSIZE = 10


def create_professional_layout(
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

    logger.debug(f"Professional layout created with figure size: {figsize}")
    return fig, ax


def add_professional_formatting(
    ax: plt.Axes,
    merged_df,
    borehole_x_map: Dict[str, float],
    ordered_boreholes: List[str],
    show_labels: bool = True,
) -> None:
    """Add professional formatting including labels and axis styling."""

    # Set axis labels with professional styling
    ax.set_xlabel(
        "Distance (m)", fontsize=SECTION_PLOT_AXIS_FONTSIZE, fontweight="bold"
    )
    ax.set_ylabel(
        "Elevation (mOD)", fontsize=SECTION_PLOT_AXIS_FONTSIZE, fontweight="bold"
    )

    # Format axis ticks
    ax.tick_params(
        axis="both",
        which="major",
        labelsize=SECTION_PLOT_AXIS_FONTSIZE - 1,
        width=1.2,
        length=6,
    )
    ax.tick_params(
        axis="both",
        which="minor",
        width=0.8,
        length=3,
    )

    # Add borehole labels if requested
    if show_labels:
        add_borehole_labels(ax, merged_df, borehole_x_map, ordered_boreholes)

    # Set spine properties for professional appearance
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
        spine.set_color("black")

    logger.debug("Professional formatting applied to axes")


def add_borehole_labels(
    ax: plt.Axes,
    merged_df,
    borehole_x_map: Dict[str, float],
    ordered_boreholes: List[str],
) -> None:
    """Add borehole ID labels at the top of each borehole column."""

    # Get the axis limits to position labels properly
    y_min, y_max = ax.get_ylim()
    label_y = y_max + (y_max - y_min) * 0.02  # 2% above the top

    for borehole_id in ordered_boreholes:
        if borehole_id in borehole_x_map:
            x_pos = borehole_x_map[borehole_id]

            # Add borehole ID label
            ax.text(
                x_pos,
                label_y,
                borehole_id,
                ha="center",
                va="bottom",
                fontsize=SECTION_PLOT_AXIS_FONTSIZE - 1,
                fontweight="bold",
                rotation=0,
                color="black",
            )

            # Add vertical line to mark borehole position
            ax.axvline(
                x=x_pos,
                color="black",
                linestyle="-",
                linewidth=1.0,
                alpha=0.6,
                zorder=1,
            )

    logger.debug(f"Borehole labels added for {len(ordered_boreholes)} boreholes")


def add_professional_footer(fig: plt.Figure, figsize: Tuple[float, float]) -> None:
    """Add professional footer with project information."""

    # Footer text
    footer_text = (
        "Generated by Geo Borehole Sections Render | "
        "Professional geological cross-section visualization"
    )

    # Position footer at bottom of figure
    fig.text(
        0.5,  # Center horizontally
        0.02,  # Near bottom
        footer_text,
        ha="center",
        va="bottom",
        fontsize=8,
        color="gray",
        style="italic",
    )

    logger.debug("Professional footer added to figure")


def add_title_and_header(
    fig: plt.Figure,
    ax: plt.Axes,
    ags_title: Optional[str],
    figsize: Tuple[float, float],
) -> None:
    """Add title and header information to the plot."""

    # Main title
    if ags_title:
        title = f"Geological Cross-Section: {ags_title}"
    else:
        title = "Geological Cross-Section"

    # Add title to figure (above the plot)
    fig.suptitle(
        title,
        fontsize=SECTION_PLOT_AXIS_FONTSIZE + 2,
        fontweight="bold",
        y=0.95,  # Near top of figure
        ha="center",
    )

    logger.debug(f"Title added: {title}")


def set_axis_limits_and_aspect(
    ax: plt.Axes,
    merged_df,
    borehole_x_map: Dict[str, float],
    padding_factor: float = 0.05,
) -> None:
    """Set appropriate axis limits and aspect ratio for the plot."""

    if not borehole_x_map:
        logger.warning("No borehole positions available for axis limits")
        return

    # Calculate X-axis limits
    x_positions = list(borehole_x_map.values())
    x_min, x_max = min(x_positions), max(x_positions)
    x_range = x_max - x_min if x_max > x_min else 50.0
    x_padding = x_range * padding_factor

    ax.set_xlim(x_min - x_padding, x_max + x_padding)

    # Calculate Y-axis limits from elevation data
    if (
        not merged_df.empty
        and "ELEV_TOP" in merged_df.columns
        and "ELEV_BASE" in merged_df.columns
    ):
        y_values = []
        y_values.extend(merged_df["ELEV_TOP"].dropna().tolist())
        y_values.extend(merged_df["ELEV_BASE"].dropna().tolist())

        if y_values:
            y_min, y_max = min(y_values), max(y_values)
            y_range = y_max - y_min if y_max > y_min else 10.0
            y_padding = y_range * padding_factor

            ax.set_ylim(y_min - y_padding, y_max + y_padding)
        else:
            logger.warning("No elevation data available for Y-axis limits")
            ax.set_ylim(0, 100)  # Default range
    else:
        logger.warning("No elevation columns found in merged data")
        ax.set_ylim(0, 100)  # Default range

    # Set equal aspect ratio for accurate representation
    ax.set_aspect("equal", adjustable="box")

    logger.debug(f"Axis limits set: X({ax.get_xlim()}), Y({ax.get_ylim()})")


def optimize_layout_for_legend(
    fig: plt.Figure,
    ax: plt.Axes,
    has_legend: bool,
    figsize: Tuple[float, float],
) -> None:
    """Optimize layout to accommodate legend placement."""

    if not has_legend:
        return

    # Adjust subplot position if legend will be placed outside
    if figsize[0] > 10:  # Wide figure - legend on right
        # Reduce plot width to make room for legend
        current_pos = ax.get_position()
        new_width = current_pos.width * 0.85  # 85% of original width
        ax.set_position([current_pos.x0, current_pos.y0, new_width, current_pos.height])
    else:  # Narrow figure - legend at bottom
        # Reduce plot height to make room for legend
        current_pos = ax.get_position()
        new_height = current_pos.height * 0.85  # 85% of original height
        new_y = current_pos.y0 + (current_pos.height - new_height)  # Shift up
        ax.set_position([current_pos.x0, new_y, current_pos.width, new_height])

    logger.debug("Layout optimized for legend placement")
