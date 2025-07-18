"""
Professional borehole log plotting module matching Openground style standards.

This module creates professional borehole logs with separate columns for
lithology, depth, and layer description using color and hatch patterns
from CSV geology code mapping with Openground-style formatting and layout.

Updated to include multi-page support, professional headers, and proper A4 formatting
based on the dummy3 implementation.
"""

# Import shared geology code mapping utility (move to top for lint compliance)
from geology_code_utils import load_geology_code_mappings

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
import logging
import numpy as np
import base64
import io
from typing import Optional, Tuple, List

# Define log_col_widths_in at module level for single source of truth
log_col_widths_in = [0.05, 0.08, 0.04, 0.14, 0.07, 0.07, 0.08, 0.42, 0.05]

# Configure matplotlib for professional rendering
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.linewidth"] = 0.5
plt.rcParams["lines.linewidth"] = 1.0

logger = logging.getLogger(__name__)


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
    import matplotlib as mpl

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

    # Use a temporary figure to measure text widths
    tmp_fig = plt.figure(figsize=(8, 2))
    tmp_ax = tmp_fig.add_subplot(111)
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
        from section_plot_professional import parse_ags_geol_section_from_string
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
        import csv

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

    # Load geology mapping if not provided
    if geology_mapping is None:
        geology_mapping = {}
        if geology_csv_path:
            try:
                color_map, pattern_map = load_geology_code_mappings(geology_csv_path)
                all_codes = set(color_map.keys()) | set(pattern_map.keys())
                for code in all_codes:
                    geology_mapping[code] = {
                        "color": color_map.get(code, "#b0c4de"),
                        "hatch": pattern_map.get(code, None),
                    }
                logger.info(
                    f"Loaded {len(geology_mapping)} geology codes from {geology_csv_path}"
                )
            except Exception as e:
                logger.error(f"Failed to load geology mapping: {e}")

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

        # --- Draw lithology intervals ---
        intervals = []
        for i, row in borehole_data.iterrows():
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
                # Get color and hatch pattern from mapping (normalize code to string and strip)
                geology_code = str(seg["Geology_Code"]).strip()
                color = "#b0c4de"
                hatch = None
                if geology_mapping:
                    entry = geology_mapping.get(geology_code)
                    if entry:
                        color = entry.get("color", "#b0c4de")
                        hatch = entry.get("hatch", None)
                    else:
                        print(
                            f"[DEBUG] Geology code '{geology_code}' not found in mapping."
                        )

                # Draw lithology rectangle
                log_ax.add_patch(
                    Rectangle(
                        (legend_left, y_base_clipped),
                        legend_width,
                        y_top - y_base_clipped,
                        facecolor=color,
                        edgecolor="black",
                        linewidth=1,
                        hatch=hatch,
                        alpha=0.8,
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
                # Draw horizontal line at top of each stratum in description column
                log_ax.plot(
                    [desc_left, desc_left + desc_width],
                    [y_top, y_top],
                    color="black",
                    linewidth=0.8,
                    zorder=4,
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

    logger.info(f"Generated {len(images)} pages for borehole {borehole_id}")
    return images


class ProfessionalBoreholeLog:
    """Professional borehole log plotter with Openground-style formatting."""

    def __init__(self, geology_csv_path: Optional[str] = None):
        """
        Initialize the professional borehole log plotter.

        Args:
            geology_csv_path: Path to CSV file containing geology code mappings
        """
        self.geology_mapping = {}
        if geology_csv_path:
            try:
                color_map, pattern_map = load_geology_code_mappings(geology_csv_path)
                # Combine the two maps into a single mapping structure
                all_codes = set(color_map.keys()) | set(pattern_map.keys())
                for code in all_codes:
                    self.geology_mapping[code] = {
                        "color": color_map.get(code, "#b0c4de"),  # Light blue default
                        "hatch": pattern_map.get(code, None),
                    }
                logger.info(
                    f"Loaded {len(self.geology_mapping)} geology codes from {geology_csv_path}"
                )
            except Exception as e:
                logger.error(f"Failed to load geology mapping: {e}")

    def create_borehole_log(
        self,
        borehole_data: pd.DataFrame,
        borehole_id: str,
        title: Optional[str] = None,
        figsize: Tuple[float, float] = (8.27, 11.69),
        dpi: int = 300,
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
            geology_csv_path=None,  # Use the already loaded mapping
            title=title,
            figsize=figsize,
            dpi=dpi,
        )


def create_professional_borehole_log(
    borehole_data: pd.DataFrame,
    borehole_id: str,
    geology_csv_path: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8.27, 11.69),
    dpi: int = 300,
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
    return create_professional_borehole_log_multi_page(
        borehole_data, borehole_id, geology_csv_path, title, figsize, dpi
    )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create sample data
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5, 8.0],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0, 12.0],
            "Geology_Code": ["CLAY", "SAND", "GRAV", "CLAY", "ROCK"],
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
        sample_data, "BH001", title="Example Professional Borehole Log"
    )

    print(f"Generated {len(images)} page(s) for borehole log")
