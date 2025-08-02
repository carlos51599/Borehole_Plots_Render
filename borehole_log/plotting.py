"""
Professional Borehole Log Plotting Module

This module provides plotting and geological rendering functions extracted from the
monolithic borehole_log_professional.py implementation. These functions handle
geological layer visualization, text box rendering, and lithology patterns while
maintaining 100% compatibility with the original implementation.

Key Functions:
- draw_text_box: Text box rendering with diagonal connectors
- draw_geological_layer: Single geological layer rendering
- render_lithology_column: Complete lithology column rendering

Dependencies:
- borehole_log.utils: Core utilities and constants
- geology_code_utils: BGS geological code mapping
"""

from matplotlib.patches import Rectangle
from geology_code_utils import get_geology_color, get_geology_pattern


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

    Exact copy from monolithic borehole_log_professional.py implementation.

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


def draw_geological_layer(
    log_ax,
    seg,
    legend_left,
    legend_width,
    depth_to_y_abs,
    toe_y,
    color_alpha=0.8,
    hatch_alpha=0.6,
):
    """
    Draw a single geological layer with color and hatch pattern.

    Extracted from monolithic borehole_log_professional.py implementation.

    Args:
        log_ax: Matplotlib axes
        seg: Segment/interval data dictionary
        legend_left: Left edge of legend column
        legend_width: Width of legend column
        depth_to_y_abs: Function to convert depth to Y position
        toe_y: Bottom Y position limit
        color_alpha: Alpha transparency for colors
        hatch_alpha: Alpha transparency for hatch patterns

    Returns:
        dict: Legend position information for the layer
    """
    # Clip lithology at toe_y for all pages
    y_top = depth_to_y_abs(seg["Depth_Top"])
    y_base = depth_to_y_abs(seg["Depth_Base"])
    y_base_clipped = max(y_base, toe_y)

    if y_top <= y_base_clipped:
        return None  # Layer not visible

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

    # Return legend position for this interval
    return {
        "y_center": y_center,
        "y_top": y_top,
        "y_bottom": y_base_clipped,
        "geology_code": seg["Geology_Code"],
    }
