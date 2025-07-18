"""
Dummy version of professional borehole log plotting for testing with dummy lithology data.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import pandas as pd

# Dummy lithology data based on AGS file codes
DUMMY_BOREHOLE_DATA = pd.DataFrame(
    {
        "Depth_Top": [0.0, 0.5, 2.0, 4.5, 7.0, 10.0],
        "Depth_Base": [0.5, 2.0, 4.5, 7.0, 10.0, 15.0],
        "Geology_Code": [
            "101",  # TOPSOIL
            "102",  # MADE GROUND
            "201",  # CLAY
            "401",  # SAND
            "504",  # Sandy GRAVEL
            "801",  # MUDSTONE
        ],
        "Description": [
            "Dark brown silty TOPSOIL with roots",
            "Brown MADE GROUND with brick fragments",
            "Firm brown CLAY, slightly silty",
            "Medium dense fine SAND, some gravel",
            "Dense sandy GRAVEL, occasional cobbles",
            "Weathered MUDSTONE, grey, fissured",
        ],
    }
)


# Header drawing function from Borehole Log header.py
def draw_header(ax):
    ax.axis("off")

    # For a 4-inch wide log, use a grid that fills the axes from 0 to 1 in x
    x_start = 0.0

    x = x_start
    import matplotlib as mpl

    # Accept page_num and total_pages as attributes of ax if present (set by caller)
    page_num = getattr(ax, "_page_num", None)
    total_pages = getattr(ax, "_total_pages", None)

    # Header content
    top_labels = [
        ["Project Name:", "Client:", "Date:"],
        ["Location:", "Contractor:", "Co-ords:"],
        ["Project No.:", "Crew Name:", "Drilling Equipment:"],
    ]
    top_values = [
        ["SESRO", "Thames Water", ""],
        ["Abingdon, Oxfordshire", "", "E443012.50 N195881.00"],
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
        page_number_str = "Sheet 4 of 5"
    bottom_values = ["BH01", "CP+RC", "62.50m AoD", "", "1:50", page_number_str]

    # Use a temporary figure to measure text widths
    tmp_fig = plt.figure(figsize=(8, 2))
    tmp_ax = tmp_fig.add_subplot(111)
    renderer = tmp_fig.canvas.get_renderer()
    fontprops = mpl.font_manager.FontProperties(family="Arial", size=8)
    cell_padd = 12  # pixels, padding left and right

    # Top 3 rows
    max_top_widths = []
    for row in range(3):
        for col in range(3):
            title = top_labels[row][col]
            value = top_values[row][col]
            t_width = tmp_ax.figure.canvas.get_renderer().get_text_width_height_descent(
                title, fontprops, ismath=False
            )[0]
            v_width = tmp_ax.figure.canvas.get_renderer().get_text_width_height_descent(
                value, fontprops, ismath=False
            )[0]
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
    total_width_px = sum(col_widths_px)
    dpi = tmp_fig.dpi
    fig_width_in = total_width_px / dpi
    plt.close(tmp_fig)

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

    # Define column widths for the new row (adjusted for better text fitting)
    # Increased proportions to accommodate longer text while maintaining relationships
    new_col_widths = [0.05, 0.10, 0.06, 0.12, 0.08, 0.08, 0.10, 0.37, 0.04]
    # Well, Depth, Type, Results, Depth, Level, Legend, Stratum, Empty
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

    x = 0.0
    for i, (col_width, label) in enumerate(zip(new_col_widths, new_col_labels)):
        # Draw cell rectangle
        ax.add_patch(
            Rectangle(
                (x, 0),  # New row at very bottom (y=0)
                col_width,
                new_row_height,
                edgecolor="black",
                facecolor="none",
                linewidth=1,
            )
        )

        # Special handling for "Sample and In Situ Testing" merged header
        if i == 1:  # First sub-column of the merged section
            # Draw the merged header text spanning columns 1, 2, 3
            merged_width = new_col_widths[1] + new_col_widths[2] + new_col_widths[3]
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
                x + col_width / 2,
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
                x + col_width / 2,
                new_row_height / 2,
                label,
                va="center",
                ha="center",
                fontsize=8,
                fontweight="bold",
                fontname="Arial",
            )

        x += col_width


def plot_dummy_borehole_log():
    # --- MULTI-PAGE LOG IMPLEMENTATION ---
    # A4 width is 8.27 inches, minus margins (0.5" each side) = 7.27" usable
    a4_width_in = 8.27
    a4_height_in = 11.69
    left_margin_in = 0.5
    right_margin_in = 0.5
    top_margin_in = 0.3
    header_height_in = 2.0
    bottom_margin_in = 0.3
    # Log area is the rest of the page
    log_area_in = a4_height_in - (top_margin_in + header_height_in + bottom_margin_in)
    log_area_top_in = a4_height_in - top_margin_in - header_height_in
    log_depth = float(DUMMY_BOREHOLE_DATA["Depth_Base"].max())

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
    for page_num in range(1, last_borehole_page + 1):
        # Column setup in inches (proportional to a4_usable_width)
        log_col_widths_in = [0.05, 0.10, 0.06, 0.12, 0.08, 0.08, 0.10, 0.37, 0.04]
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
        # Attach page_num and total_pages as attributes for header rendering
        header_ax._page_num = page_num
        header_ax._total_pages = last_borehole_page
        draw_header(header_ax)
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
            return log_area_in * (1 - (depth - page_top) / (page_bot - page_top))

        legend_left = log_col_x[6]
        legend_width = log_col_widths[6]
        desc_left = log_col_x[7]
        desc_width = log_col_widths[7]

        intervals = []
        for i, row in DUMMY_BOREHOLE_DATA.iterrows():
            d1 = row["Depth_Top"]
            d2 = row["Depth_Base"]
            if d2 <= page_top or d1 >= page_bot:
                continue
            seg_top = max(d1, page_top)
            seg_base = min(d2, page_data_bot)  # Only plot up to actual data
            if seg_top >= seg_base:
                continue
            intervals.append(
                {
                    "orig_idx": i,
                    "Depth_Top": seg_top,
                    "Depth_Base": seg_base,
                    "Geology_Code": row["Geology_Code"],
                    "Description": row["Description"],
                    "orig_Depth_Top": d1,
                    "orig_Depth_Base": d2,
                }
            )

        for j, seg in enumerate(intervals):
            # Clip lithology at toe_y for all pages
            y_top = depth_to_y_abs(seg["Depth_Top"])
            y_base = depth_to_y_abs(seg["Depth_Base"])
            y_base_clipped = max(y_base, toe_y)
            if y_top > y_base_clipped:
                # Draw lithology rectangle
                log_ax.add_patch(
                    Rectangle(
                        (legend_left, y_base_clipped),
                        legend_width,
                        y_top - y_base_clipped,
                        facecolor="#b0c4de",
                        edgecolor="black",
                        linewidth=1,
                        zorder=2,
                    )
                )
                y_center = (y_top + y_base_clipped) / 2
                # For depth/level values, align with base (bottom) of interval
                y_base_label = max(y_base, y_base_clipped)
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
                # Draw description in description column
                log_ax.text(
                    desc_left + desc_width * 0.02,
                    y_center,
                    seg["Description"],
                    va="center",
                    ha="left",
                    fontsize=8,
                    color="black",
                    fontname="Arial",
                    zorder=3,
                    wrap=True,
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
                # For demo, assume ground level is 62.50 and subtract depth
                base_level = 62.50 - seg["Depth_Base"]
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
                # Draw horizontal line at top of each stratum in description column
                log_ax.plot(
                    [desc_left, desc_left + desc_width],
                    [y_top, y_top],
                    color="black",
                    linewidth=0.8,
                    zorder=4,
                )

        # Save as A4-sized PNG image with 300 DPI (always full page)
        fig.savefig(
            f"borehole_log_output_page{page_num}.png", dpi=300, bbox_inches=None
        )
        plt.close(fig)


if __name__ == "__main__":
    plot_dummy_borehole_log()
