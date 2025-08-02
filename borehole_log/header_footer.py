"""
Professional Borehole Log Header and Footer Module

This module provides header and footer rendering functions extracted from the monolithic
borehole_log_professional.py implementation. These functions handle professional header
layout with company information, borehole details, and column headers while maintaining
100% compatibility with the original implementation.

Key Functions:
- draw_header: Professional header rendering with Openground standards

Dependencies:
- borehole_log.utils: matplotlib_figure context manager, log_col_widths_in
"""

import matplotlib as mpl
from matplotlib.patches import Rectangle

# Import from utils module
from .utils import matplotlib_figure, log_col_widths_in


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

    Exact copy from monolithic borehole_log_professional.py implementation.

    Args:
        ax: Matplotlib axes to draw on
        page_num: Current page number
        total_pages: Total number of pages
        borehole_id: Borehole identifier
        ground_level: Ground level for the borehole
        hole_type: Type of hole (e.g., "CP+RC")
        coords_str: Coordinate string for location
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
