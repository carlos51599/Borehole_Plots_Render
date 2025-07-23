"""
Borehole Log Main Plotting Module

This module provides the main plotting functionality for professional borehole logs,
coordinating between layout, overflow, and header/footer modules.

Key Functions:
- create_borehole_log: Main function to create complete borehole log
- plot_single_page: Plot a single page of borehole log
- setup_plot_axes: Configure matplotlib axes for professional plotting
- coordinate_multi_page_layout: Handle multi-page borehole logs
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import logging
from typing import Dict, List, Optional, Tuple, Any
import os

from .utils import matplotlib_figure, safe_close_figure, wrap_text_smart
from .layout import calculate_plot_layout, create_column_layout, calculate_depths
from .header_footer import (
    draw_header,
    draw_footer,
    create_header_content,
    create_footer_content,
)
from .overflow import (
    check_depth_overflow,
    filter_data_for_page,
    get_page_depth_range,
    calculate_continuation_indicators,
)

logger = logging.getLogger(__name__)


def create_borehole_log(
    borehole_id: str,
    loca_data: Dict,
    geology_data: List[Dict],
    sample_data: Optional[List[Dict]] = None,
    project_info: Optional[Dict] = None,
    output_path: Optional[str] = None,
    page_settings: Optional[Dict] = None,
) -> str:
    """
    Create a complete professional borehole log with multi-page support.

    Args:
        borehole_id: Borehole identifier
        loca_data: Location data (LOCA group)
        geology_data: Geological data (GEOL group)
        sample_data: Sample data (SAMP group, optional)
        project_info: Project information (PROJ group, optional)
        output_path: Output file path (if None, auto-generate)
        page_settings: Page layout settings

    Returns:
        str: Path to created PDF file
    """
    if page_settings is None:
        page_settings = get_default_page_settings()

    try:
        # Generate output path if not provided
        if output_path is None:
            output_path = f"borehole_log_{borehole_id}.pdf"

        # Calculate total depth and check for overflow
        total_depth = _calculate_total_depth(geology_data, sample_data)
        layout_info = calculate_plot_layout(page_settings)

        needs_overflow, total_pages, page_ranges = check_depth_overflow(
            total_depth,
            layout_info["plot_height"],
            page_settings.get("depth_scale", 50.0),
        )

        # Create header and footer content
        header_content = create_header_content(loca_data, project_info)
        footer_content = create_footer_content(project_info)

        # Create PDF with multiple pages
        with PdfPages(output_path) as pdf_pages:
            for page_num in range(1, total_pages + 1):
                fig = _create_single_page(
                    page_num,
                    total_pages,
                    page_ranges,
                    geology_data,
                    sample_data,
                    header_content,
                    footer_content,
                    page_settings,
                    layout_info,
                )

                if fig:
                    pdf_pages.savefig(fig, bbox_inches="tight", dpi=300)
                    safe_close_figure(fig)

        logger.info(f"Borehole log created: {output_path} ({total_pages} pages)")
        return output_path

    except Exception as e:
        logger.error(f"Error creating borehole log for {borehole_id}: {e}")
        raise


def _create_single_page(
    page_num: int,
    total_pages: int,
    page_ranges: List[Tuple[float, float]],
    geology_data: List[Dict],
    sample_data: Optional[List[Dict]],
    header_content: Dict,
    footer_content: Dict,
    page_settings: Dict,
    layout_info: Dict,
) -> Optional[plt.Figure]:
    """Create a single page of the borehole log."""

    try:
        # Get page depth range
        page_start, page_end = get_page_depth_range(page_num, page_ranges)

        # Filter data for this page
        page_geology = filter_data_for_page(geology_data, page_start, page_end)
        page_samples = []
        if sample_data:
            page_samples = filter_data_for_page(
                sample_data, page_start, page_end, "SAMP_TOP", "SAMP_BASE"
            )

        # Create figure and plot
        fig = plot_single_page(
            page_geology,
            page_samples,
            page_start,
            page_end,
            header_content,
            footer_content,
            page_num,
            total_pages,
            page_settings,
            layout_info,
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating page {page_num}: {e}")
        return None


def plot_single_page(
    geology_data: List[Dict],
    sample_data: List[Dict],
    start_depth: float,
    end_depth: float,
    header_content: Dict,
    footer_content: Dict,
    page_number: int,
    total_pages: int,
    page_settings: Dict,
    layout_info: Dict,
) -> plt.Figure:
    """
    Plot a single page of borehole log with professional formatting.

    Args:
        geology_data: Filtered geology data for this page
        sample_data: Filtered sample data for this page
        start_depth: Page start depth
        end_depth: Page end depth
        header_content: Header information
        footer_content: Footer information
        page_number: Current page number
        total_pages: Total number of pages
        page_settings: Page layout settings
        layout_info: Layout calculation results

    Returns:
        matplotlib.figure.Figure: Configured figure
    """
    try:
        # Create figure with proper size
        fig = matplotlib_figure(
            figsize=(page_settings["page_width"], page_settings["page_height"])
        )

        # Draw header and footer
        draw_header(fig, None, header_content, page_settings["page_width"])
        draw_footer(
            fig, page_number, total_pages, footer_content, page_settings["page_width"]
        )

        # Create main plot area
        main_ax = fig.add_axes(
            [
                layout_info["plot_left"],
                layout_info["plot_bottom"],
                layout_info["plot_width_norm"],
                layout_info["plot_height_norm"],
            ]
        )

        # Setup axes for borehole plotting
        setup_plot_axes(main_ax, start_depth, end_depth, page_settings)

        # Create column layout
        column_layout = create_column_layout(layout_info["plot_width"])

        # Plot geological data
        _plot_geology_column(
            main_ax, geology_data, column_layout, start_depth, end_depth
        )

        # Plot sample data if available
        if sample_data:
            _plot_sample_column(
                main_ax, sample_data, column_layout, start_depth, end_depth
            )

        # Add depth scale
        _add_depth_scale(main_ax, start_depth, end_depth, column_layout)

        # Add continuation indicators if needed
        continuation = calculate_continuation_indicators(
            [(start_depth, end_depth)], 1  # Single page for this function
        )
        if total_pages > 1:
            _add_continuation_indicators(
                main_ax, continuation, page_number, total_pages
            )

        return fig

    except Exception as e:
        logger.error(f"Error plotting single page: {e}")
        raise


def setup_plot_axes(
    ax: plt.Axes, start_depth: float, end_depth: float, page_settings: Dict
) -> None:
    """Configure matplotlib axes for professional borehole plotting."""

    try:
        # Set depth range (inverted Y-axis for depth)
        ax.set_ylim(end_depth, start_depth)
        ax.set_xlim(0, 100)  # Percentage-based width

        # Configure axis appearance
        ax.set_ylabel("Depth (m)", fontsize=10, fontweight="bold")
        ax.tick_params(axis="y", labelsize=9)
        ax.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        # Add grid
        ax.grid(True, axis="y", alpha=0.3, linestyle="-", linewidth=0.5)

        # Remove top and right spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # Configure left spine (depth axis)
        ax.spines["left"].set_linewidth(1.5)

    except Exception as e:
        logger.error(f"Error setting up plot axes: {e}")


def _plot_geology_column(
    ax: plt.Axes,
    geology_data: List[Dict],
    column_layout: Dict,
    start_depth: float,
    end_depth: float,
) -> None:
    """Plot geological information in the geology column."""

    geology_col = column_layout["geology"]

    for stratum in geology_data:
        try:
            # Get stratum depths
            top_depth = float(stratum.get("GEOL_TOP", 0))
            base_depth = float(stratum.get("GEOL_BASE", top_depth))

            # Clip to page range
            top_depth = max(top_depth, start_depth)
            base_depth = min(base_depth, end_depth)

            if top_depth >= base_depth:
                continue

            # Get geological description
            description = stratum.get("GEOL_DESC", "Unknown")
            description = wrap_text_smart(description, geology_col["width"] * 0.8)

            # Draw stratum rectangle
            rect = patches.Rectangle(
                (geology_col["left"], top_depth),
                geology_col["width"],
                base_depth - top_depth,
                linewidth=1,
                edgecolor="black",
                facecolor=_get_geology_color(stratum),
                alpha=0.7,
            )
            ax.add_patch(rect)

            # Add description text
            text_y = (top_depth + base_depth) / 2
            ax.text(
                geology_col["left"] + geology_col["width"] / 2,
                text_y,
                description,
                ha="center",
                va="center",
                fontsize=8,
                wrap=True,
            )

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping invalid geology record: {e}")
            continue


def _plot_sample_column(
    ax: plt.Axes,
    sample_data: List[Dict],
    column_layout: Dict,
    start_depth: float,
    end_depth: float,
) -> None:
    """Plot sample information in the sample column."""

    sample_col = column_layout["samples"]

    for sample in sample_data:
        try:
            # Get sample depth
            sample_top = float(sample.get("SAMP_TOP", 0))
            sample_base = float(sample.get("SAMP_BASE", sample_top))

            # Check if sample is in page range
            if sample_top > end_depth or sample_base < start_depth:
                continue

            # Clip to page range
            sample_top = max(sample_top, start_depth)
            sample_base = min(sample_base, end_depth)

            # Get sample information
            sample_id = sample.get("SAMP_ID", "Unknown")
            sample_type = sample.get("SAMP_TYPE", "")

            # Draw sample indicator
            marker_y = (sample_top + sample_base) / 2
            ax.plot(
                sample_col["left"] + sample_col["width"] / 2,
                marker_y,
                marker="s",
                markersize=6,
                color="red",
                markeredgecolor="black",
            )

            # Add sample label
            ax.text(
                sample_col["left"] + sample_col["width"] + 2,
                marker_y,
                f"{sample_id}\n{sample_type}",
                ha="left",
                va="center",
                fontsize=7,
            )

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping invalid sample record: {e}")
            continue


def _add_depth_scale(
    ax: plt.Axes, start_depth: float, end_depth: float, column_layout: Dict
) -> None:
    """Add depth scale markings to the plot."""

    depth_col = column_layout["depth"]

    # Calculate appropriate tick interval
    depth_range = end_depth - start_depth
    if depth_range <= 5:
        tick_interval = 0.5
    elif depth_range <= 20:
        tick_interval = 1.0
    elif depth_range <= 50:
        tick_interval = 2.0
    else:
        tick_interval = 5.0

    # Add depth ticks
    tick_depth = start_depth
    while tick_depth <= end_depth:
        ax.text(
            depth_col["left"] + depth_col["width"] / 2,
            tick_depth,
            f"{tick_depth:.1f}",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
        )
        tick_depth += tick_interval


def _add_continuation_indicators(
    ax: plt.Axes, continuation: Dict, page_number: int, total_pages: int
) -> None:
    """Add indicators showing page continuation."""

    if continuation["continues_above"] and page_number > 1:
        ax.text(
            50,
            ax.get_ylim()[1] + 0.1,
            "↑ Continued from above",
            ha="center",
            va="bottom",
            fontsize=9,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
        )

    if continuation["continues_below"] and page_number < total_pages:
        ax.text(
            50,
            ax.get_ylim()[0] - 0.1,
            "↓ Continued below",
            ha="center",
            va="top",
            fontsize=9,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
        )


def _get_geology_color(stratum: Dict) -> str:
    """Get color for geological stratum based on description or code."""

    description = stratum.get("GEOL_DESC", "").lower()

    # Simple color mapping based on common geological terms
    if any(term in description for term in ["clay", "clayey"]):
        return "#8B4513"  # Brown
    elif any(term in description for term in ["sand", "sandy"]):
        return "#F4E4BC"  # Tan
    elif any(term in description for term in ["gravel", "gravelly"]):
        return "#A0A0A0"  # Gray
    elif any(term in description for term in ["silt", "silty"]):
        return "#D2B48C"  # Light brown
    elif any(term in description for term in ["rock", "limestone", "chalk"]):
        return "#DCDCDC"  # Light gray
    elif any(term in description for term in ["peat", "organic"]):
        return "#2F4F2F"  # Dark green
    else:
        return "#E6E6FA"  # Lavender (default)


def _calculate_total_depth(
    geology_data: List[Dict], sample_data: Optional[List[Dict]] = None
) -> float:
    """Calculate total borehole depth from available data."""

    max_depth = 0.0

    # Check geology data
    for stratum in geology_data:
        try:
            base_depth = stratum.get("GEOL_BASE")
            if base_depth is not None:
                max_depth = max(max_depth, float(base_depth))
        except (ValueError, TypeError):
            continue

    # Check sample data
    if sample_data:
        for sample in sample_data:
            try:
                sample_base = sample.get("SAMP_BASE") or sample.get("SAMP_TOP")
                if sample_base is not None:
                    max_depth = max(max_depth, float(sample_base))
            except (ValueError, TypeError):
                continue

    return max_depth


def get_default_page_settings() -> Dict:
    """Get default page settings for borehole log creation."""

    return {
        "page_width": 8.27,  # A4 width in inches
        "page_height": 11.69,  # A4 height in inches
        "margin": 0.5,  # Margin in inches
        "header_height": 1.5,  # Header height in inches
        "footer_height": 0.8,  # Footer height in inches
        "depth_scale": 50.0,  # Pixels per meter
        "column_widths": {"depth": 10, "geology": 60, "samples": 20, "spacing": 5},
    }


def validate_plot_data(
    geology_data: List[Dict], sample_data: Optional[List[Dict]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate plot data before creating borehole log.

    Args:
        geology_data: Geological data to validate
        sample_data: Sample data to validate (optional)

    Returns:
        tuple: (is_valid, list_of_warnings)
    """
    warnings = []

    # Check geology data
    if not geology_data:
        warnings.append("No geological data provided")
    else:
        for i, stratum in enumerate(geology_data):
            if "GEOL_TOP" not in stratum:
                warnings.append(f"Geology record {i+1} missing GEOL_TOP")
            if "GEOL_DESC" not in stratum:
                warnings.append(f"Geology record {i+1} missing GEOL_DESC")

    # Check sample data if provided
    if sample_data:
        for i, sample in enumerate(sample_data):
            if "SAMP_TOP" not in sample:
                warnings.append(f"Sample record {i+1} missing SAMP_TOP")
            if "SAMP_ID" not in sample:
                warnings.append(f"Sample record {i+1} missing SAMP_ID")

    is_valid = len(warnings) == 0
    return is_valid, warnings
