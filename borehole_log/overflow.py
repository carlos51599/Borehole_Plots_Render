"""
Professional Borehole Log Overflow Management Module

This module provides overflow detection and handling functions extracted from the
monolithic borehole_log_professional.py implementation. These functions handle
text box overflow detection, classification, and dedicated overflow page creation
while maintaining 100% compatibility with the original implementation.

Key Functions:
- classify_text_box_overflow: Detect and classify text box overflow
- create_overflow_page: Generate dedicated overflow pages
- handle_page_boundaries: Manage text positioning across page breaks

Dependencies:
- borehole_log.utils: Core utilities and matplotlib_figure
- borehole_log.header_footer: Header generation for overflow pages
- borehole_log.plotting: Text box drawing functions
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import io
import base64
import logging

# Import from other modules
from .utils import matplotlib_figure, log_col_widths_in
from .header_footer import draw_header
from .plotting import draw_text_box

logger = logging.getLogger(__name__)


def classify_text_box_overflow(
    text_positions,
    page_top,
    page_bot,
    toe_y,
    log_area_in,
    intervals,
    borehole_data,
):
    """
    Classify text boxes based on overflow behavior and page boundaries.

    Exact copy from monolithic borehole_log_professional.py implementation.

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

    Exact copy from monolithic borehole_log_professional.py implementation.

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
