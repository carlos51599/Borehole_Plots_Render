"""
Professional Borehole Log Plotting Module with Industry-Standard Formatting.

This module creates publication-quality individual borehole logs that match
professional geotechnical reporting standards, specifically following Openground
style guidelines. It generates detailed logs with separate columns for lithology,
depth measurements, and geological descriptions using standardized BGS colors
and hatch patterns.

Key Features:
- **Professional Layout**: Multi-column format with standardized spacing and alignment
- **Industry Standards**: BGS-compliant geological colors and symbols
- **Multi-Page Support**: Automatic page breaks for long boreholes with proper headers
- **Openground Compatibility**: Styling and layout matching Openground software standards
- **High-Quality Output**: Publication-ready graphics suitable for technical reports

Log Components:
1. **Header Section**: Borehole identification, location, and project information
2. **Depth Column**: Precise depth measurements with appropriate scaling
3. **Lithology Column**: Visual representation with colors and hatch patterns
4. **Sample Information**: Sample numbers, types, and recovery data
5. **Description Column**: Detailed geological descriptions and observations
6. **Legend**: Comprehensive legend with geological units and symbols

Professional Standards:
- **A4 Format Optimization**: Designed for standard A4 portrait printing
- **Technical Typography**: Professional font hierarchy and text sizing
- **Geological Symbology**: Standard BGS geological patterns and colors
- **Measurement Precision**: Accurate depth scales and interval representations
- **Report Integration**: Compatible with standard geotechnical report formats

Multi-Page Features:
- Automatic page breaks for long boreholes
- Consistent headers across all pages
- Continuous depth scaling across pages
- Professional page numbering and referencing
- Seamless geological continuity between pages

Quality Assurance:
- Consistent geological color application
- Accurate depth interval representation
- Professional text formatting and alignment
- Error handling for incomplete data
- Performance optimization for complex logs

Dependencies:
- matplotlib: Professional plotting and page layout
- pandas: Geological data processing and validation
- geology_code_utils: BGS geological code management
- numpy: Numerical calculations and array operations

Author: [Project Team]
Last Modified: July 2025
"""

# Import shared geology code mapping utility (move to top for lint compliance)
from geology_code_utils import get_geology_color, get_geology_pattern

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
import pandas as pd
import logging
import numpy as np
import base64
import io
import textwrap
import csv
from typing import Optional, Tuple, List
from contextlib import contextmanager


# Define log_col_widths_in at module level for single source of truth
log_col_widths_in = [0.05, 0.08, 0.04, 0.14, 0.07, 0.07, 0.08, 0.42, 0.05]

# --- Transparency defaults (define once here) ---
DEFAULT_COLOR_ALPHA = 0.4
DEFAULT_HATCH_ALPHA = 0.2

# Configure matplotlib for professional rendering
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.linewidth"] = 0.5
plt.rcParams["lines.linewidth"] = 1.0

# OPTIMIZATION: Reduce matplotlib logging verbosity for better performance
# Prevents excessive font manager debug output during plot generation
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("matplotlib.pyplot").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@contextmanager
def matplotlib_figure(*args, **kwargs):
    """
    Context manager for matplotlib figures to ensure proper cleanup.

    Usage:
        with matplotlib_figure(figsize=(8, 6)) as fig:
            # work with figure
            pass
    # Figure is automatically closed here
    """
    fig = plt.figure(*args, **kwargs)
    try:
        yield fig
    finally:
        plt.close(fig)


def safe_close_figure(fig):
    """
    Safely close a matplotlib figure with error handling.

    Args:
        fig: matplotlib Figure object or None
    """
    if fig is not None:
        try:
            plt.close(fig)
        except Exception as e:
            logger.warning(f"Error closing matplotlib figure: {e}")


def classify_text_box_overflow(
    text_positions, page_top, page_bot, toe_y, log_area_in, intervals, borehole_data
):
    """
    Classify text boxes based on overflow behavior and page boundaries.

    Args:
        text_positions: List of text position dictionaries
        page_top: Top depth of current page
        page_bot: Bottom depth of current page
        toe_y: Y position of toe line (page boundary)
        log_area_in: Log area height in inches
        intervals: Current page intervals
        borehole_data: Original borehole data

    Returns:
        dict: Classification results with overflow strategies
    """

    def depth_to_y_abs(depth):
        """Convert depth to absolute Y position on page"""
        return log_area_in * (1 - (float(depth) - page_top) / (page_bot - page_top))

    results = {
        "on_page_boxes": [],  # Text boxes that fit on current page
        "layer_continues_overflow": [],  # Text boxes for layers continuing to next page
        "layer_complete_overflow": [],  # Text boxes for layers ending on page but text too long
        "overflow_page_needed": False,  # Whether an overflow page is needed
    }

    for i, text_pos in enumerate(text_positions):
        if i >= len(intervals):
            continue

        interval = intervals[i]
        layer_bottom_depth = interval["orig_Depth_Base"]

        # Check if text box extends below toe line (page boundary)
        if text_pos["y_bottom"] < toe_y:
            # Text box overflows page boundary

            # Strategy 1: Check if layer continues to next page
            if layer_bottom_depth > page_bot:
                # Layer continues beyond current page - defer to next page
                results["layer_continues_overflow"].append(
                    {
                        "text_pos": text_pos,
                        "interval": interval,
                        "overflow_type": "layer_continues",
                        "original_interval_idx": interval["orig_idx"],
                    }
                )
            else:
                # Strategy 2: Layer ends on current page but text doesn't fit
                # This needs an overflow page
                results["layer_complete_overflow"].append(
                    {
                        "text_pos": text_pos,
                        "interval": interval,
                        "overflow_type": "layer_complete",
                        "original_interval_idx": interval["orig_idx"],
                    }
                )
                results["overflow_page_needed"] = True
        else:
            # Text box fits on current page
            results["on_page_boxes"].append(
                {
                    "text_pos": text_pos,
                    "interval": interval,
                    "original_interval_idx": interval["orig_idx"],
                }
            )

    return results


def create_overflow_page(
    overflow_boxes,
    page_num,
    borehole_id,
    ground_level,
    hole_type,
    coords_str,
    figsize,
    dpi,
    color_alpha,
    hatch_alpha,
):
    """
    Create a dedicated overflow page for text boxes that don't fit on regular pages.

    Args:
        overflow_boxes: List of overflow text box dictionaries
        page_num: Base page number for overflow page
        borehole_id: Borehole identifier
        ground_level: Ground level for the borehole
        hole_type: Type of hole
        coords_str: Coordinates string
        figsize: Figure size tuple
        dpi: Resolution
        color_alpha: Color transparency
        hatch_alpha: Hatch transparency

    Returns:
        str: Base64-encoded PNG image
    """

    a4_width_in = figsize[0]
    a4_height_in = figsize[1]
    left_margin_in = 0.5
    right_margin_in = 0.5
    top_margin_in = 0.3
    header_height_in = 2.0
    bottom_margin_in = 0.3
    log_area_in = a4_height_in - (top_margin_in + header_height_in + bottom_margin_in)

    # Column setup
    total_col_width = sum(log_col_widths_in)
    a4_usable_width = a4_width_in - left_margin_in - right_margin_in
    scale = a4_usable_width / total_col_width
    log_col_widths = [w * scale for w in log_col_widths_in]
    log_col_x = [0]
    for w in log_col_widths:
        log_col_x.append(log_col_x[-1] + w)

    fig = plt.figure(figsize=(a4_width_in, a4_height_in))

    # Header axes - special header for overflow page
    header_ax = fig.add_axes(
        [
            left_margin_in / a4_width_in,
            (a4_height_in - top_margin_in - header_height_in) / a4_height_in,
            a4_usable_width / a4_width_in,
            header_height_in / a4_height_in,
        ]
    )

    # Draw overflow page header
    draw_header(
        header_ax,
        f"{page_num} Overflow",  # Special overflow page numbering
        f"{page_num} Overflow",  # Total pages will be updated later
        borehole_id,
        ground_level,
        hole_type=hole_type,
        coords_str=coords_str,
    )
    header_ax.set_xlim(0, 1)
    header_ax.set_ylim(0, 1)
    header_ax.axis("off")

    # Log area axes
    log_ax = fig.add_axes(
        [
            left_margin_in / a4_width_in,
            bottom_margin_in / a4_height_in,
            a4_usable_width / a4_width_in,
            log_area_in / a4_height_in,
        ]
    )
    log_ax.set_xlim(0, a4_usable_width)
    log_ax.set_ylim(0, log_area_in)
    log_ax.axis("off")

    # Draw log area bounding box
    log_box = [0, 0, a4_usable_width, log_area_in]
    rect = Rectangle(
        (log_box[0], log_box[1]),
        log_box[2],
        log_box[3],
        fill=False,
        edgecolor="black",
        linewidth=1.5,
    )
    log_ax.add_patch(rect)

    # Draw columns
    for idx, x_val in enumerate(log_col_x[1:-1], start=1):
        log_ax.plot([x_val, x_val], [0, log_area_in], color="black", linewidth=1)

    # Top line of log area
    log_ax.plot(
        [0, a4_usable_width], [log_area_in, log_area_in], color="black", linewidth=1
    )

    # Add overflow page title
    log_ax.text(
        a4_usable_width / 2,
        log_area_in * 0.95,
        f"Page {page_num} - Text Descriptions Overflow",
        ha="center",
        va="top",
        fontsize=12,
        fontweight="bold",
        fontname="Arial",
        zorder=10,
    )

    # Position overflow text boxes vertically with proper spacing
    desc_left = log_col_x[7]
    desc_width = log_col_widths[7]

    current_y = log_area_in * 0.85  # Start below title
    spacing = 0.1  # Space between boxes

    for box_info in overflow_boxes:
        text_pos = box_info["text_pos"].copy()
        interval = box_info["interval"]

        # Calculate required height for this text box
        required_height = text_pos["original_text_height"]

        # Position text box
        text_pos["y_top"] = current_y
        text_pos["y_bottom"] = current_y - required_height
        text_pos["x_left"] = desc_left
        text_pos["x_width"] = desc_width
        text_pos["text_height"] = required_height

        # Check if box fits on page
        if text_pos["y_bottom"] > 0:
            # Draw layer reference information
            ref_text = (
                f"Depth {interval['orig_Depth_Top']:.2f}-{interval['orig_Depth_Base']:.2f}m "
                f"(Code: {interval['Geology_Code']})"
            )
            log_ax.text(
                desc_left + desc_width * 0.02,
                current_y + 0.05,
                ref_text,
                va="bottom",
                ha="left",
                fontsize=7,
                color="blue",
                fontweight="bold",
                fontname="Arial",
                zorder=4,
            )

            # Draw text box (no connector lines on overflow page)
            draw_text_box(log_ax, text_pos, interval)

            # Move to next position
            current_y = text_pos["y_bottom"] - spacing
        else:
            # Box doesn't fit - would need another overflow page
            # For now, just note this in the log
            logger.warning(
                f"Overflow text box for interval {interval['orig_idx']} doesn't fit on overflow page"
            )

    # Convert to base64 image
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches=None)
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    return img_b64


def wrap_text_and_calculate_height(text, max_width_chars=45, font_size=8):
    """
    Wrap text and calculate required height in inches for rendering.

    Args:
        text: Text to wrap
        max_width_chars: Maximum characters per line
        font_size: Font size in points

    Returns:
        tuple: (wrapped_lines, height_in_inches)
    """
    if not text or pd.isna(text):
        return [""], 0.15  # Minimum height for empty text

    # Wrap text
    wrapped_lines = textwrap.wrap(str(text), width=max_width_chars)
    if not wrapped_lines:  # Empty after wrapping
        wrapped_lines = [""]

    # Calculate height: font_size in points, converted to inches
    # Add some line spacing (1.2x font size per line)
    line_height_inches = (font_size * 1.2) / 72.0  # 72 points per inch
    total_height = len(wrapped_lines) * line_height_inches

    # Minimum height for readability
    min_height = 0.15

    return wrapped_lines, max(total_height, min_height)


def calculate_text_box_positions_aligned(
    intervals, legend_positions, desc_left, desc_width
):
    """
    Calculate text box positions aligned with their geological layers,
    with adjustments for conflicts.

    Args:
        intervals: List of interval dictionaries with lithology data
        legend_positions: List of legend position dictionaries with y_top, y_bottom
        desc_left: Left edge of description column
        desc_width: Width of description column

    Returns:
        list: Text box positions with y_top, y_bottom, x_left, x_width for each interval
    """
    text_positions = []

    # Use full width of description column
    text_box_width = desc_width
    text_box_left = desc_left

    for i, (interval, legend_pos) in enumerate(zip(intervals, legend_positions)):
        # Calculate wrapped text height
        wrapped_lines, text_height = wrap_text_and_calculate_height(
            interval.get("Description", ""), max_width_chars=45
        )

        if legend_pos["y_center"] > 0:  # Valid legend position
            # Start with layer boundaries as default position
            layer_y_top = legend_pos["y_top"]
            layer_y_bottom = legend_pos["y_bottom"]
            layer_height = layer_y_top - layer_y_bottom

            # Default position: align with layer boundaries
            preferred_y_top = layer_y_top

            # Check if text fits within the layer
            if text_height <= layer_height:
                # Text fits within layer - extend text box to match layer's bottom boundary
                final_y_top = preferred_y_top
                final_y_bottom = layer_y_bottom  # Extend to layer's bottom boundary
                # Update text_height to reflect the extended box height
                extended_text_height = final_y_top - final_y_bottom
            else:
                # Text is too tall for layer - extend beyond layer boundary
                final_y_top = preferred_y_top
                final_y_bottom = preferred_y_top - text_height  # Extend to fit all text
                extended_text_height = text_height

        else:
            # No valid legend position - shouldn't happen, but handle gracefully
            final_y_top = 0
            final_y_bottom = -text_height
            extended_text_height = text_height

        text_positions.append(
            {
                "interval_idx": i,
                "y_top": final_y_top,
                "y_bottom": final_y_bottom,
                "x_left": text_box_left,
                "x_width": text_box_width,
                "wrapped_lines": wrapped_lines,
                "text_height": extended_text_height,  # Use extended height for drawing
                "original_text_height": text_height,  # Keep original for text positioning
                "layer_y_top": legend_pos.get("y_top", 0),
                "layer_y_bottom": legend_pos.get("y_bottom", 0),
            }
        )

    # Second pass: resolve conflicts with cascading push-down effect
    # Keep adjusting until no more conflicts exist
    conflicts_resolved = False
    max_iterations = len(text_positions) * 2  # Prevent infinite loops
    iteration = 0

    while not conflicts_resolved and iteration < max_iterations:
        conflicts_resolved = True
        iteration += 1

        for i in range(1, len(text_positions)):
            current = text_positions[i]
            previous = text_positions[i - 1]

            # Check if current text box overlaps with previous
            # Overlap occurs when current y_top is above previous y_bottom
            if current["y_top"] > previous["y_bottom"]:
                # Overlap detected - push current text box down
                current["y_top"] = (
                    previous["y_bottom"] - 0.001
                )  # Small gap to prevent infinite loops
                current["y_bottom"] = current["y_top"] - current["original_text_height"]

                # Check if the pushed-down text box is still within its layer's boundaries
                # If so, extend it to match the layer's bottom boundary
                if current["y_bottom"] > current["layer_y_bottom"]:
                    # Text box bottom is still above layer bottom - extend it
                    current["y_bottom"] = current["layer_y_bottom"]

                # Update the extended height after repositioning
                current["text_height"] = current["y_top"] - current["y_bottom"]
                conflicts_resolved = (
                    False  # Need another pass to check cascading effects
                )

    return text_positions


def draw_text_box(
    log_ax,
    text_pos,
    interval,
    legend_right=None,
    next_col_left=None,
    depth_to_y_abs=None,
    page_top=0,
    page_bot=1,
):
    """
    Draw a text box with shortened borders and diagonal connector lines.

    Args:
        log_ax: Matplotlib axes
        text_pos: Text position dictionary
        interval: Interval data dictionary
        legend_right: Right edge of legend/lithology column
        next_col_left: Left edge of column after description column
        depth_to_y_abs: Function to convert depth to Y position
        page_top: Top depth of current page
        page_bot: Bottom depth of current page
    """
    # Calculate margin for shortened boundaries (8% of box width)
    horizontal_margin = text_pos["x_width"] * 0.08

    # Text box coordinates
    x_left = text_pos["x_left"]
    x_right = x_left + text_pos["x_width"]
    y_top = text_pos["y_top"]
    y_bottom = text_pos["y_bottom"]

    # Shortened boundary coordinates
    x_left_margin = x_left + horizontal_margin
    x_right_margin = x_right - horizontal_margin

    # Draw left and right vertical lines (full height)
    log_ax.plot(
        [x_left, x_left], [y_bottom, y_top], color="black", linewidth=0.8, zorder=3
    )
    log_ax.plot(
        [x_right, x_right], [y_bottom, y_top], color="black", linewidth=0.8, zorder=3
    )

    # Draw shortened top and bottom lines
    log_ax.plot(
        [x_left_margin, x_right_margin],
        [y_top, y_top],
        color="black",
        linewidth=0.8,
        zorder=3,
    )
    log_ax.plot(
        [x_left_margin, x_right_margin],
        [y_bottom, y_bottom],
        color="black",
        linewidth=0.8,
        zorder=3,
    )

    # Draw diagonal connector lines if column positions are provided
    if (
        legend_right is not None
        and next_col_left is not None
        and depth_to_y_abs is not None
    ):
        # Get the true geological layer boundaries
        geol_top = interval.get("orig_Depth_Top", interval.get("Depth_Top", 0))
        geol_base = interval.get("orig_Depth_Base", interval.get("Depth_Base", 0))

        # Convert geological depths to Y positions
        y_geol_top = depth_to_y_abs(geol_top)
        y_geol_base = depth_to_y_abs(geol_base)

        # Ensure Y positions are within reasonable bounds
        y_geol_top = max(min(y_geol_top, y_top + 2), y_bottom - 2)
        y_geol_base = max(min(y_geol_base, y_top + 2), y_bottom - 2)

        # Draw diagonal connector lines
        # Top-Left: text box corner to legend column at GEOL_TOP
        log_ax.plot(
            [x_left_margin, legend_right],
            [y_top, y_geol_top],
            color="black",
            linewidth=0.5,
            zorder=2,
        )

        # Top-Right: text box corner to next column at GEOL_TOP
        log_ax.plot(
            [x_right_margin, next_col_left],
            [y_top, y_geol_top],
            color="black",
            linewidth=0.5,
            zorder=2,
        )

        # Bottom-Left: text box corner to legend column at GEOL_BASE
        log_ax.plot(
            [x_left_margin, legend_right],
            [y_bottom, y_geol_base],
            color="black",
            linewidth=0.5,
            zorder=2,
        )

        # Bottom-Right: text box corner to next column at GEOL_BASE
        log_ax.plot(
            [x_right_margin, next_col_left],
            [y_bottom, y_geol_base],
            color="black",
            linewidth=0.5,
            zorder=2,
        )

    # Draw wrapped text lines
    line_height_inches = (8 * 1.2) / 72.0  # 8pt font with 1.2x line spacing

    # Center the text block vertically in the box
    n_lines = len(text_pos["wrapped_lines"])
    total_text_height = n_lines * line_height_inches
    y_text_start = text_pos["y_top"] - (text_pos["text_height"] - total_text_height) / 2

    for i, line in enumerate(text_pos["wrapped_lines"]):
        y_text = y_text_start - (i + 0.5) * line_height_inches

        # Use simple centered text alignment to avoid matplotlib bugs
        log_ax.text(
            text_pos["x_left"] + text_pos["x_width"] / 2,
            y_text,
            line,
            va="center",
            ha="center",
            fontsize=8,
            color="black",
            fontname="Arial",
            zorder=4,
        )


def draw_header(
    ax,
    page_num=None,
    total_pages=None,
    borehole_id="BH01",
    ground_level=0.0,
    hole_type="",
    coords_str="",
):
    """
    Draw professional header matching Openground standards.

    Args:
        ax: Matplotlib axes to draw on
        page_num: Current page number
        total_pages: Total number of pages
        borehole_id: Borehole identifier
        ground_level: Ground level for the borehole
    """
    ax.axis("off")

    # For a 4-inch wide log, use a grid that fills the axes from 0 to 1 in x
    x_start = 0.0

    x = x_start

    # Header content
    top_labels = [
        ["Project Name:", "Client:", "Date:"],
        ["Location:", "Contractor:", "Co-ords:"],
        ["Project No.:", "Crew Name:", "Drilling Equipment:"],
    ]
    top_values = [
        ["SESRO", "Thames Water", ""],
        ["Abingdon, Oxfordshire", "", coords_str if coords_str else ""],
        ["303568-00", "", ""],
    ]
    bottom_labels = [
        "Borehole Number",
        "Hole Type",
        "Level",
        "Logged By",
        "Scale",
        "Page Number",
    ]
    # Set the page number cell dynamically if page_num and total_pages are provided
    if page_num is not None and total_pages is not None:
        page_number_str = f"Sheet {page_num} of {total_pages}"
    else:
        page_number_str = "Sheet 1 of 1"
    bottom_values = [
        borehole_id,
        hole_type if hole_type else "CP+RC",
        f"{ground_level:.2f}m AoD",
        "",
        "1:50",
        page_number_str,
    ]

    # Use a temporary figure to measure text widths with safe cleanup
    with matplotlib_figure(figsize=(8, 2)) as tmp_fig:
        tmp_ax = tmp_fig.add_subplot(111)
        fontprops = mpl.font_manager.FontProperties(family="Arial", size=8)
        cell_padd = 12  # pixels, padding left and right

        # Top 3 rows
        max_top_widths = []
        for row in range(3):
            for col in range(3):
                title = top_labels[row][col]
                value = top_values[row][col]
                t_width = (
                    tmp_ax.figure.canvas.get_renderer().get_text_width_height_descent(
                        title, fontprops, ismath=False
                    )[0]
                )
                v_width = (
                    tmp_ax.figure.canvas.get_renderer().get_text_width_height_descent(
                        value, fontprops, ismath=False
                    )[0]
                )
                max_top_widths.append(t_width + v_width + cell_padd)

        # Bottom row
        max_bottom_widths = []
        for i in range(6):
            title = bottom_labels[i]
            value = bottom_values[i]
            t_width = tmp_ax.figure.canvas.get_renderer().get_text_width_height_descent(
                title, fontprops, ismath=False
            )[0]
            v_width = tmp_ax.figure.canvas.get_renderer().get_text_width_height_descent(
                value, fontprops, ismath=False
            )[0]
            max_bottom_widths.append(max(t_width, v_width) + cell_padd)

        # For the top 3 rows (3 columns), find max width for each column
        top_col_widths_px = [
            max(
                max_top_widths[i],
                max_top_widths[i + 3],
                max_top_widths[i + 6],
            )
            for i in range(3)
        ]
        # For the bottom row (6 columns), use its own widths, but make each cell half the width of the cells above
        # Calculate the average width of the top row columns
        avg_top_col_width = sum(top_col_widths_px) / 3
        # Each bottom cell is half the width of a top cell
        bottom_col_widths_px = [avg_top_col_width / 2] * 6
        col_widths_px = bottom_col_widths_px
    # Temporary figure is automatically closed here by the context manager

    # Draw the complete header grid on the provided axes
    # Top 3 rows (3 columns each)
    top_row_height = 0.2  # Each of the 3 top rows takes 20% of axes height (reduced to make room for new row)

    # Draw top 3 rows
    for row in range(3):
        y_pos = 1.0 - (row * top_row_height)  # Start from top
        for col in range(3):
            col_width = 1.0 / 3.0  # Equal width for 3 columns
            x_pos = col * col_width

            # Draw cell rectangle
            ax.add_patch(
                Rectangle(
                    (x_pos, y_pos - top_row_height),
                    col_width,
                    top_row_height,
                    edgecolor="black",
                    facecolor="none",
                    linewidth=1,
                )
            )

            # Draw label and value
            label = top_labels[row][col]
            value = top_values[row][col]

            # Label (bold, upper part of cell)
            if label:
                ax.text(
                    x_pos + col_width * 0.05,
                    y_pos - top_row_height * 0.2,
                    label,
                    va="top",
                    ha="left",
                    fontsize=8,
                    fontweight="bold",
                    fontname="Arial",
                )

            # Value (normal, lower part of cell)
            if value:
                ax.text(
                    x_pos + col_width * 0.05,
                    y_pos - top_row_height * 0.6,
                    value,
                    va="top",
                    ha="left",
                    fontsize=8,
                    fontname="Arial",
                )

    # Draw bottom row rectangles and text
    # We'll use axes coordinates (0-1) for x/y, and scale col_widths_px to axes width
    total_col_width_px = sum(col_widths_px)
    axes_width = 1.0  # ax spans 0-1 in x
    px_to_axes = axes_width / total_col_width_px
    x = 0.0
    bottom_row_height = (
        0.2  # fraction of axes height for bottom row (reduced to make room for new row)
    )
    for i in range(6):
        col_width = col_widths_px[i] * px_to_axes
        ax.add_patch(
            Rectangle(
                (x, 0.2),  # Bottom row at y=0.2 to make room for new row below
                col_width,
                bottom_row_height,
                edgecolor="black",
                facecolor="none",
                linewidth=1,
            )
        )
        # Draw title (near top of cell)
        title_text = bottom_labels[i]
        ax.text(
            x + col_width / 2,
            0.2 + bottom_row_height * 0.85,
            title_text,
            va="top",
            ha="center",
            fontsize=8,
            fontweight="bold",
            fontname="Arial",
        )
        # Draw value (centered horizontally, lower in cell)
        ax.text(
            x + col_width / 2,
            0.2 + bottom_row_height * 0.35,
            bottom_values[i],
            va="top",
            ha="center",
            fontsize=8,
            fontname="Arial",
        )
        x += col_width

    # Draw new additional row at the bottom
    new_row_height = 0.2  # fraction of axes height for new row

    new_col_labels = [
        "Well",
        "Depth (m)",
        "Type",
        "Results",
        "Depth\n(m)",
        "Level\n(m)",
        "Legend",
        "Stratum Description",
        "",
    ]
    total_col_width = sum(log_col_widths_in)
    x = 0.0
    for i, (col_width, label) in enumerate(zip(log_col_widths_in, new_col_labels)):
        # Draw cell rectangle
        ax.add_patch(
            Rectangle(
                (x, 0),  # New row at very bottom (y=0)
                col_width / total_col_width,  # normalize to axes width
                new_row_height,
                edgecolor="black",
                facecolor="none",
                linewidth=1,
            )
        )

        # Special handling for "Sample and In Situ Testing" merged header
        if i == 1:  # First sub-column of the merged section
            merged_width = sum(log_col_widths_in[1:4]) / total_col_width
            ax.text(
                x + merged_width / 2,
                new_row_height * 0.9,
                "Sample and In Situ Testing",
                va="top",
                ha="center",
                fontsize=8,
                fontweight="bold",
                fontname="Arial",
            )
            # Draw horizontal line to separate merged header from sub-headers
            ax.plot(
                [x, x + merged_width],
                [new_row_height * 0.6, new_row_height * 0.6],
                "k-",
                linewidth=1,
            )

        # Draw sub-column labels
        if i in [1, 2, 3]:  # Sub-columns under "Sample and In Situ Testing"
            ax.text(
                x + (col_width / total_col_width) / 2,
                new_row_height * 0.4,
                label,
                va="top",
                ha="center",
                fontsize=7,
                fontweight="bold",
                fontname="Arial",
            )
        elif label:  # Other column labels
            ax.text(
                x + (col_width / total_col_width) / 2,
                new_row_height / 2,
                label,
                va="center",
                ha="center",
                fontsize=8,
                fontweight="bold",
                fontname="Arial",
            )

        x += col_width / total_col_width


def plot_borehole_log_from_ags_content(
    ags_content,
    loca_id,
    show_labels=True,
    fig_height=11.69,
    fig_width=4.0,
    geology_csv_path=None,
    title=None,
    dpi=300,
    color_alpha=DEFAULT_COLOR_ALPHA,
    hatch_alpha=DEFAULT_HATCH_ALPHA,
):
    """
    Parse AGS content and plot a professional borehole log for the given borehole ID.
    Returns a list of base64-encoded images for multi-page display.

    Args:
        ags_content: AGS file content as string
        loca_id: Borehole ID to plot
        show_labels: (compatibility, not used)
        fig_height: Figure height in inches (default A4 portrait)
        fig_width: Figure width in inches
        geology_csv_path: Path to geology code mapping CSV
        title: Optional plot title
        dpi: Figure DPI

    Returns:
        List of base64-encoded PNG images, or None if no data found
    """
    try:
        # Import parser from section_plot_professional (shared logic)
        from section import parse_ags_geol_section_from_string
    except ImportError as e:
        logger.error(f"Failed to import section_plot_professional: {e}")
        return None

    geol_df, loca_df, abbr_df, *extra_groups = parse_ags_geol_section_from_string(
        ags_content
    )
    geol_bh = geol_df[geol_df["LOCA_ID"] == loca_id]
    if geol_bh.empty:
        return None

    # Get ground level, hole type, and coordinates for this borehole from LOCA data
    ground_level = 0.0  # Default fallback
    hole_type = ""
    coords_str = ""
    if not loca_df.empty:
        loca_bh = loca_df[loca_df["LOCA_ID"] == loca_id]
        if not loca_bh.empty:
            try:
                ground_level = float(loca_bh["LOCA_GL"].iloc[0])
            except (ValueError, IndexError):
                logger.warning(
                    f"Could not extract ground level for {loca_id}, using 0.0"
                )
                ground_level = 0.0
            # Extract hole type
            if "LOCA_TYPE" in loca_bh.columns:
                hole_type = str(loca_bh["LOCA_TYPE"].iloc[0])
            # Extract and format coordinates
            nate = (
                str(loca_bh["LOCA_NATE"].iloc[0])
                if "LOCA_NATE" in loca_bh.columns
                else ""
            )
            natn = (
                str(loca_bh["LOCA_NATN"].iloc[0])
                if "LOCA_NATN" in loca_bh.columns
                else ""
            )
            if nate and natn:
                coords_str = f"E {nate}  N {natn}"
            elif nate or natn:
                coords_str = f"E {nate}{'  N ' + natn if natn else ''}"
    # Use GEOL_DESC if available, else fallback to empty string
    desc_col = "GEOL_DESC" if "GEOL_DESC" in geol_bh.columns else None

    # Build DataFrame for professional plotting
    borehole_data = pd.DataFrame(
        {
            "Depth_Top": geol_bh["GEOL_TOP"].astype(float),
            "Depth_Base": geol_bh["GEOL_BASE"].astype(float),
            "Geology_Code": geol_bh["GEOL_LEG"],
            "Description": (
                geol_bh[desc_col] if desc_col else ["" for _ in range(len(geol_bh))]
            ),
        }
    )

    # Check for unreasonable depth (e.g., >100m)
    max_depth = borehole_data["Depth_Base"].max()
    if max_depth > 100:
        return {
            "error": (
                f"Borehole base depth is {max_depth:.2f} m, which exceeds the 100 m limit. "
                "Check the AGS GEOL group for errors before plotting."
            )
        }

    # Sort by top depth
    borehole_data = borehole_data.sort_values("Depth_Top").reset_index(drop=True)

    # --- SPT/ISPT DATA PARSING LOGIC ---
    # Try to extract ISPT group from AGS content (if present)
    def parse_ags_ispt_group(ags_content, loca_id):
        """
        Parse ISPT group from AGS content for a given LOCA_ID.
        Returns a DataFrame with columns: Depth, Type, Results
        """

        # Use robust group-agnostic parsing (like section_plot_professional.py)
        lines = ags_content.splitlines()
        parsed = list(csv.reader(lines, delimiter=",", quotechar='"'))

        ispt_headings = []
        ispt_data = []
        in_ispt = False
        for row in parsed:
            if row and row[0] == "GROUP" and len(row) > 1 and row[1] == "ISPT":
                in_ispt = True
                continue
            if in_ispt and row and row[0] == "HEADING":
                ispt_headings = row[1:]
                continue
            if in_ispt and row and row[0] == "DATA":
                ispt_data.append(row[1 : len(ispt_headings) + 1])
                continue
            if (
                in_ispt
                and row
                and row[0] == "GROUP"
                and (len(row) < 2 or row[1] != "ISPT")
            ):
                break

        if not ispt_headings or not ispt_data:
            return None
        # Find required columns
        try:
            idx_loca = ispt_headings.index("LOCA_ID")
            idx_top = ispt_headings.index("ISPT_TOP")
            idx_type = ispt_headings.index("ISPT_TYPE")
            idx_rep = ispt_headings.index("ISPT_REP")
        except ValueError:
            return None
        spt_rows = []
        for fields in ispt_data:
            if len(fields) < max(idx_loca, idx_top, idx_type, idx_rep) + 1:
                continue
            if fields[idx_loca].strip() == str(loca_id):
                spt_rows.append(
                    {
                        "Depth": fields[idx_top].strip(),
                        "Type": fields[idx_type].strip(),
                        "Results": fields[idx_rep].strip(),
                    }
                )
        if not spt_rows:
            return None
        return pd.DataFrame(spt_rows)

    spt_df = parse_ags_ispt_group(ags_content, loca_id)
    # spt_df is a DataFrame with columns: Depth, Type, Results (or None)

    # Use the professional plotting function, now passing spt_df
    images = create_professional_borehole_log_multi_page(
        borehole_data=borehole_data,
        borehole_id=loca_id,
        ground_level=ground_level,
        geology_csv_path=geology_csv_path,
        title=title,
        figsize=(fig_width, fig_height),
        dpi=dpi,
        spt_df=spt_df,
        hole_type=hole_type,
        coords_str=coords_str,
        color_alpha=color_alpha,
        hatch_alpha=hatch_alpha,
    )
    return images


def create_professional_borehole_log_multi_page(
    borehole_data: pd.DataFrame,
    borehole_id: str,
    ground_level: float = 0.0,
    geology_csv_path: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8.27, 11.69),
    dpi: int = 300,
    spt_df: Optional[pd.DataFrame] = None,
    hole_type: str = "",
    coords_str: str = "",
    geology_mapping: Optional[dict] = None,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
) -> List[str]:
    """
    Create a professional multi-page borehole log plot.
    Returns a list of base64-encoded PNG images.

    Args:
        borehole_data: DataFrame with geological layer data
        borehole_id: Identifier for the borehole
        ground_level: Ground level for calculating elevations
        geology_csv_path: Path to geology code mapping CSV
        title: Optional title for the plot
        figsize: Figure size (width, height) in inches
        dpi: Resolution for the plot

    Returns:
        List of base64-encoded PNG images
    """
    logger.info(f"Creating professional multi-page borehole log for {borehole_id}")

    if borehole_data.empty:
        logger.warning(f"No data available for borehole {borehole_id}")
        return []

    # Note: We use get_geology_color and get_geology_pattern functions directly
    # which automatically load from the default CSV file, so no need for complex mapping

    # --- MULTI-PAGE LOG IMPLEMENTATION ---
    # A4 width is 8.27 inches, minus margins (0.5" each side) = 7.27" usable
    a4_width_in = figsize[0]
    a4_height_in = figsize[1]
    left_margin_in = 0.5
    right_margin_in = 0.5
    top_margin_in = 0.3
    header_height_in = 2.0
    bottom_margin_in = 0.3
    # Log area is the rest of the page
    log_area_in = a4_height_in - (top_margin_in + header_height_in + bottom_margin_in)
    log_depth = float(borehole_data["Depth_Base"].max())

    # --- SCALE HANDLING ---
    # Input scale: e.g., 1:50 (1 cm on paper = 50 cm in reality)
    # For this example, use 1:50 as in the header
    input_scale = 50  # 1:50 (1 mm on paper = 50 mm in reality)
    # 1 inch = 25.4 mm
    log_area_mm = log_area_in * 25.4
    # Depth per page in mm: log_area_mm * scale (in m/mm)
    # 1 mm on paper = 50 mm in reality = 0.05 m
    mm_to_m = input_scale / 1000  # 50/1000 = 0.05 m per mm
    depth_per_page = log_area_mm * mm_to_m

    last_borehole_page = int(np.ceil(log_depth / depth_per_page))

    images = []

    for page_num in range(1, last_borehole_page + 1):
        # Column setup in inches (proportional to a4_usable_width)
        total_col_width = sum(log_col_widths_in)
        a4_usable_width = a4_width_in - left_margin_in - right_margin_in
        scale = a4_usable_width / total_col_width
        log_col_widths = [w * scale for w in log_col_widths_in]
        log_col_x = [0]
        for w in log_col_widths:
            log_col_x.append(log_col_x[-1] + w)
        page_top = (page_num - 1) * depth_per_page
        page_bot = (
            page_num * depth_per_page
        )  # Always a full interval for scale, even on last page
        page_data_bot = min(page_bot, log_depth)  # Actual data ends here
        fig = plt.figure(figsize=(a4_width_in, a4_height_in))

        # Header axes (absolute units, top of page)
        header_ax = fig.add_axes(
            [
                left_margin_in / a4_width_in,
                (a4_height_in - top_margin_in - header_height_in) / a4_height_in,
                a4_usable_width / a4_width_in,
                header_height_in / a4_height_in,
            ]
        )

        # Draw header with page information
        draw_header(
            header_ax,
            page_num,
            last_borehole_page,
            borehole_id,
            ground_level,
            hole_type=hole_type,
            coords_str=coords_str,
        )
        header_ax.set_xlim(0, 1)
        header_ax.set_ylim(0, 1)
        header_ax.axis("off")

        # Log area axes (absolute units, below header)
        log_ax = fig.add_axes(
            [
                left_margin_in / a4_width_in,
                bottom_margin_in / a4_height_in,
                a4_usable_width / a4_width_in,
                log_area_in / a4_height_in,
            ]
        )
        log_ax.set_xlim(0, a4_usable_width)
        log_ax.set_ylim(0, log_area_in)
        log_ax.axis("off")

        # Draw log area bounding box
        log_box = [0, 0, a4_usable_width, log_area_in]
        rect = Rectangle(
            (log_box[0], log_box[1]),
            log_box[2],
            log_box[3],
            fill=False,
            edgecolor="black",
            linewidth=1.5,
        )
        log_ax.add_patch(rect)

        # Draw columns (absolute)
        for idx, x_val in enumerate(log_col_x[1:-1], start=1):
            log_ax.plot([x_val, x_val], [0, log_area_in], color="black", linewidth=1)
        # Top line of log area
        log_ax.plot(
            [0, a4_usable_width], [log_area_in, log_area_in], color="black", linewidth=1
        )

        # Draw toe line (solid black) always, only across legend and description columns
        # Draw fixed toe line (visual ruler reference) as before
        toe_y = 0.10  # 0.10 inches above bottom
        legend_left = log_col_x[6]
        legend_right = log_col_x[8]  # right edge of description column
        log_ax.plot(
            [legend_left, legend_right],
            [toe_y, toe_y],
            color="black",
            linewidth=1.5,
            zorder=10,
        )

        # Draw a new line at the end of the borehole (if it ends in the middle of the page), across legend and description columns
        borehole_end_on_page = page_data_bot < page_bot
        if borehole_end_on_page:
            borehole_end_y = log_area_in * (
                1 - (page_data_bot - page_top) / (page_bot - page_top)
            )
            log_ax.plot(
                [legend_left, legend_right],
                [borehole_end_y, borehole_end_y],
                color="black",
                linewidth=1.5,
                zorder=11,
            )

        # Draw fixed visual ruler: 0 at top, 10 at toe line, evenly spaced, not tied to data or page variables
        ruler_left = log_col_x[8]
        ruler_width = log_col_widths[8]
        ruler_x = ruler_left
        log_ax.plot([ruler_x, ruler_x], [0, log_area_in], color="black", linewidth=1.2)
        main_tick_length = ruler_width * 0.5
        sub_tick_length = ruler_width * 0.25

        # Ruler: page range is 0-10, 10-20, 20-30, etc. for each page, with decimal subticks
        page_ruler_start = (page_num - 1) * 10
        # Main ticks and labels at every integer, but skip the first marker number
        for i in range(0, 11):
            y_tick = toe_y + (log_area_in - toe_y) * (1 - i / 10)
            label_val = page_ruler_start + i
            log_ax.plot(
                [ruler_x, ruler_x + main_tick_length],
                [y_tick, y_tick],
                color="black",
                linewidth=1.1,
            )
            # Skip the first marker number (0, 10, 20, ...)
            if i != 0:
                log_ax.text(
                    ruler_x + main_tick_length + ruler_width * 0.1,
                    y_tick,
                    f"{label_val}",
                    va="center",
                    ha="left",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                )
            # Decimal subticks (every 0.1 unit, except at main ticks)
            if i < 10:
                for j in range(1, 10):
                    frac = j / 10
                    y_subtick = toe_y + (log_area_in - toe_y) * (1 - (i + frac) / 10)
                    log_ax.plot(
                        [ruler_x, ruler_x + sub_tick_length * 0.7],
                        [y_subtick, y_subtick],
                        color="black",
                        linewidth=0.5,
                    )

        # Draw lithology bars (scaled to log area)
        def depth_to_y_abs(depth):
            # Map depth to y in inches within the log area, scaled to page depth (always same for all pages)
            return log_area_in * (1 - (float(depth) - page_top) / (page_bot - page_top))

        legend_left = log_col_x[6]
        legend_width = log_col_widths[6]
        desc_left = log_col_x[7]
        desc_width = log_col_widths[7]

        # --- Draw lithology intervals (optimized) ---
        intervals = []

        # Vectorized filtering for performance - only process relevant rows
        depth_mask = (borehole_data["Depth_Base"] > page_top) & (
            borehole_data["Depth_Top"] < page_bot
        )
        relevant_data = borehole_data[depth_mask]

        if len(relevant_data) > 0:
            # Vectorized operations for depth calculations
            seg_tops = np.maximum(relevant_data["Depth_Top"].values, page_top)
            seg_bases = np.minimum(relevant_data["Depth_Base"].values, page_data_bot)

            # Only keep valid intervals
            valid_mask = seg_tops < seg_bases

            if valid_mask.any():
                valid_indices = relevant_data.index[valid_mask]
                valid_tops = seg_tops[valid_mask]
                valid_bases = seg_bases[valid_mask]

                # Build intervals list efficiently
                for idx, (orig_idx, seg_top, seg_base) in enumerate(
                    zip(valid_indices, valid_tops, valid_bases)
                ):
                    row = relevant_data.loc[orig_idx]
                    intervals.append(
                        {
                            "orig_idx": orig_idx,
                            "Depth_Top": seg_top,
                            "Depth_Base": seg_base,
                            "Geology_Code": row["Geology_Code"],
                            "Description": row["Description"],
                            "orig_Depth_Top": row["Depth_Top"],
                            "orig_Depth_Base": row["Depth_Base"],
                        }
                    )

        # First pass: Draw lithology rectangles and collect legend positions
        legend_positions = []
        for j, seg in enumerate(intervals):
            # Clip lithology at toe_y for all pages
            y_top = depth_to_y_abs(seg["Depth_Top"])
            y_base = depth_to_y_abs(seg["Depth_Base"])
            y_base_clipped = max(y_base, toe_y)

            if y_top > y_base_clipped:
                # Get color and hatch pattern using the same approach as section script
                geology_code = str(seg["Geology_Code"]).strip()
                color = get_geology_color(geology_code, "#b0c4de")
                hatch = get_geology_pattern(geology_code, None)

                # Convert hatch pattern to matplotlib format if needed
                if hatch == "\\":
                    hatch = "\\\\"  # Matplotlib needs double backslash
                elif hatch and len(hatch) > 1:
                    # Handle complex patterns like '-/.', '-/o', etc.
                    matplotlib_hatch = ""
                    for char in hatch:
                        if char == "\\":
                            matplotlib_hatch += "\\\\"
                        elif char == "/":
                            matplotlib_hatch += "///"
                        elif char == ".":
                            matplotlib_hatch += "..."
                        elif char == "o":
                            matplotlib_hatch += "ooo"
                        elif char == "O":
                            matplotlib_hatch += "OOO"
                        elif char == "x":
                            matplotlib_hatch += "xxx"
                        elif char == "-":
                            matplotlib_hatch += "---"
                        elif char == "+":
                            matplotlib_hatch += "+++"
                        elif char == "*":
                            matplotlib_hatch += "***"
                        else:
                            matplotlib_hatch += char
                    hatch = matplotlib_hatch

                # Draw lithology rectangle color (no hatch)
                log_ax.add_patch(
                    Rectangle(
                        (legend_left, y_base_clipped),
                        legend_width,
                        y_top - y_base_clipped,
                        facecolor=color,
                        edgecolor="black",
                        linewidth=1,
                        hatch=None,
                        alpha=color_alpha,
                        zorder=2,
                    )
                )
                # Draw hatch overlay (transparent face, only hatch)
                if hatch:
                    log_ax.add_patch(
                        Rectangle(
                            (legend_left, y_base_clipped),
                            legend_width,
                            y_top - y_base_clipped,
                            facecolor="none",
                            edgecolor="black",
                            linewidth=1,
                            hatch=hatch,
                            alpha=hatch_alpha,
                            zorder=3,
                        )
                    )

                y_center = (y_top + y_base_clipped) / 2
                # For depth/level values, align with base (bottom) of interval
                y_base_label = max(y_base, y_base_clipped)

                # Store legend position for this interval
                legend_positions.append(
                    {"y_center": y_center, "y_top": y_top, "y_bottom": y_base_clipped}
                )

                # Draw geology code in legend column
                log_ax.text(
                    legend_left + legend_width / 2,
                    y_center,
                    f"{seg['Geology_Code']}",
                    va="center",
                    ha="center",
                    fontsize=8,
                    color="black",
                    fontweight="bold",
                    fontname="Arial",
                    zorder=3,
                )

                # Draw depth (base) value in Depth column (col 4)
                depth_col_left = log_col_x[4]
                depth_col_width = log_col_widths[4]
                log_ax.text(
                    depth_col_left + depth_col_width / 2,
                    y_base_label,
                    f"{seg['Depth_Base']:.2f}",
                    va="bottom",
                    ha="center",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                    zorder=3,
                )
                # Draw level (base) value in Level column (col 5)
                level_col_left = log_col_x[5]
                level_col_width = log_col_widths[5]
                # Calculate level using the actual ground level from AGS data
                base_level = ground_level - seg["Depth_Base"]
                log_ax.text(
                    level_col_left + level_col_width / 2,
                    y_base_label,
                    f"{base_level:.2f}",
                    va="bottom",
                    ha="center",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                    zorder=3,
                )

                # Draw horizontal line at top of each stratum in legend column only
                # (not in description column - this is removed as per requirement)
                log_ax.plot(
                    [legend_left, legend_left + legend_width],
                    [y_top, y_top],
                    color="black",
                    linewidth=0.8,
                    zorder=4,
                )
            else:
                # Interval not visible, but we still need a placeholder for position tracking
                legend_positions.append({"y_center": 0, "y_top": 0, "y_bottom": 0})

        # Calculate text box positions aligned with legend positions
        text_positions = calculate_text_box_positions_aligned(
            intervals, legend_positions, desc_left, desc_width
        )

        # === NEW OVERFLOW MANAGEMENT SYSTEM ===
        # Classify text boxes based on overflow behavior
        overflow_classification = classify_text_box_overflow(
            text_positions,
            page_top,
            page_bot,
            toe_y,
            log_area_in,
            intervals,
            borehole_data,
        )

        # Store overflow information for this page
        if "page_overflow_data" not in locals():
            page_overflow_data = {}
        page_overflow_data[page_num] = overflow_classification

        # Draw only text boxes that fit on current page
        if legend_positions and text_positions:
            # Calculate column positions for connector lines
            legend_right = (
                log_col_x[6] + log_col_widths[6]
            )  # Right edge of legend column
            next_col_left = log_col_x[8]  # Left edge of column after description

            for box_info in overflow_classification["on_page_boxes"]:
                text_pos = box_info["text_pos"]
                interval = box_info["interval"]

                # Draw the text box with connector lines
                draw_text_box(
                    log_ax,
                    text_pos,
                    interval,
                    legend_right=legend_right,
                    next_col_left=next_col_left,
                    depth_to_y_abs=depth_to_y_abs,
                    page_top=page_top,
                    page_bot=page_bot,
                )

        # --- Draw SPT/ISPT data if available ---
        if spt_df is not None and not spt_df.empty:
            # Columns: Depth, Type, Results
            spt_depths = spt_df["Depth"].astype(float)
            spt_types = spt_df["Type"].astype(str)
            spt_results = spt_df["Results"].astype(str)
            for spt_depth, spt_type, spt_result in zip(
                spt_depths, spt_types, spt_results
            ):
                if spt_depth < page_top or spt_depth > page_data_bot:
                    continue  # Not on this page
                y_spt = depth_to_y_abs(spt_depth)
                spt_depth_col_left = log_col_x[1]
                spt_depth_col_width = log_col_widths[1]
                # Depth value (text, black, Arial)
                log_ax.text(
                    spt_depth_col_left + spt_depth_col_width / 2,
                    y_spt,
                    f"{spt_depth:.2f}",
                    va="center",
                    ha="center",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                    zorder=6,
                )
                # Type (text, black, Arial) in Type column (col 2)
                spt_type_col_left = log_col_x[2]
                spt_type_col_width = log_col_widths[2]
                log_ax.text(
                    spt_type_col_left + spt_type_col_width / 2,
                    y_spt,
                    spt_type,
                    va="center",
                    ha="center",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                    zorder=6,
                )
                # Results (formatted: N=9\n(1,1/2,1,3,3)) in Results column (col 3)
                spt_result_col_left = log_col_x[3]
                spt_result_col_width = log_col_widths[3]
                # Format: split at first parenthesis
                if "(" in spt_result and ")" in spt_result:
                    n_val, paren = spt_result.split("(", 1)
                    n_val = n_val.strip()
                    paren = "(" + paren.strip()
                    result_text = f"{n_val}\n{paren}"
                else:
                    result_text = spt_result
                log_ax.text(
                    spt_result_col_left + spt_result_col_width / 2,
                    y_spt,
                    result_text,
                    va="center",
                    ha="center",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                    zorder=6,
                )

        # Convert to base64 image
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches=None)
        plt.close(fig)
        buf.seek(0)
        img_bytes = buf.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append(img_b64)

    # === OVERFLOW PAGE GENERATION ===
    # After all regular pages are generated, create overflow pages for text boxes that didn't fit
    if "page_overflow_data" in locals():
        for page_num in range(1, last_borehole_page + 1):
            if page_num in page_overflow_data:
                classification = page_overflow_data[page_num]

                # Create overflow pages for layers that end on the page but text doesn't fit
                if (
                    classification["overflow_page_needed"]
                    and classification["layer_complete_overflow"]
                ):
                    logger.info(f"Creating overflow page for page {page_num}")

                    overflow_img = create_overflow_page(
                        classification["layer_complete_overflow"],
                        page_num,
                        borehole_id,
                        ground_level,
                        hole_type,
                        coords_str,
                        figsize,
                        dpi,
                        color_alpha,
                        hatch_alpha,
                    )
                    images.append(overflow_img)

                # Log information about deferred text boxes (layer continues strategy)
                if classification["layer_continues_overflow"]:
                    logger.info(
                        f"Page {page_num}: {len(classification['layer_continues_overflow'])} "
                        f"text boxes deferred to next page (layer continues)"
                    )

    logger.info(
        f"Generated {len(images)} pages for borehole {borehole_id} (including overflow pages)"
    )
    return images


class ProfessionalBoreholeLog:
    """Professional borehole log plotter with Openground-style formatting."""

    def __init__(self, geology_csv_path: Optional[str] = None):
        """
        Initialize the professional borehole log plotter.

        Args:
            geology_csv_path: Path to CSV file containing geology code mappings (optional, uses default if None)
        """
        # Note: We use get_geology_color and get_geology_pattern functions directly
        # which automatically load from the CSV file, so no need for complex mapping
        pass

    def create_borehole_log(
        self,
        borehole_data: pd.DataFrame,
        borehole_id: str,
        title: Optional[str] = None,
        figsize: Tuple[float, float] = (8.27, 11.69),
        dpi: int = 300,
        color_alpha: float = DEFAULT_COLOR_ALPHA,
        hatch_alpha: float = DEFAULT_HATCH_ALPHA,
    ) -> List[str]:
        """
        Create a professional borehole log plot.
        Returns a list of base64-encoded PNG images.

        Args:
            borehole_data: DataFrame with columns including 'Depth_Top', 'Depth_Base',
                          'Geology_Code', 'Description'
            borehole_id: Identifier for the borehole
            title: Optional title for the plot
            figsize: Figure size (width, height) in inches
            dpi: Resolution for the plot

        Returns:
            List of base64-encoded PNG images
        """
        logger.info(f"Creating professional borehole log for {borehole_id}")

        return create_professional_borehole_log_multi_page(
            borehole_data=borehole_data,
            borehole_id=borehole_id,
            geology_csv_path=None,  # Use the default CSV file
            title=title,
            figsize=figsize,
            dpi=dpi,
            color_alpha=color_alpha,
            hatch_alpha=hatch_alpha,
        )


def create_professional_borehole_log(
    borehole_data: pd.DataFrame,
    borehole_id: str,
    geology_csv_path: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8.27, 11.69),
    dpi: int = 300,
    color_alpha: float = DEFAULT_COLOR_ALPHA,
    hatch_alpha: float = DEFAULT_HATCH_ALPHA,
) -> List[str]:
    """
    Convenience function to create a professional borehole log plot.
    Returns a list of base64-encoded PNG images.

    Args:
        borehole_data: DataFrame with geological layer data
        borehole_id: Identifier for the borehole
        geology_csv_path: Path to geology code mapping CSV
        title: Optional title for the plot
        figsize: Figure size (width, height) in inches
        dpi: Resolution for the plot

    Returns:
        List of base64-encoded PNG images
    """
    # Ensure figsize is always a tuple (width, height)
    if not isinstance(figsize, tuple):
        figsize = (8.27, 11.69)
    return create_professional_borehole_log_multi_page(
        borehole_data,
        borehole_id,
        geology_csv_path=geology_csv_path,
        title=title,
        figsize=figsize,
        dpi=dpi,
        color_alpha=color_alpha,
        hatch_alpha=hatch_alpha,
    )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create sample data using real codes from the CSV for testing
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5, 8.0],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0, 12.0],
            "Geology_Code": ["101", "203", "501", "202", "801"],
            "Description": [
                "Soft brown clay with occasional organic matter",
                "Medium dense fine to coarse sand",
                "Dense angular gravel with cobbles",
                "Stiff grey clay with limestone fragments",
                "Weathered limestone bedrock",
            ],
        }
    )

    # Create professional borehole log
    images = create_professional_borehole_log(
        sample_data,
        "BH001",
        geology_csv_path="Geology Codes BGS.csv",
        title="Example Professional Borehole Log",
    )

    print(f"Generated {len(images)} page(s) for borehole log")
