"""
Borehole Log Layout Module

This module handles page layout, positioning, and spacing calculations for
professional borehole log generation.

Key Functions:
- calculate_text_box_positions_aligned: Position calculations for text boxes
- get_log_column_specifications: Column width and position definitions
- calculate_page_dimensions: Page size and margin calculations
- determine_optimal_layout: Layout optimization for content fitting
"""

import logging
from typing import Tuple, List, Dict, Optional

logger = logging.getLogger(__name__)

# Define column widths as fractions of page width (single source of truth)
LOG_COLUMN_WIDTHS = [0.05, 0.08, 0.04, 0.14, 0.07, 0.07, 0.08, 0.42, 0.05]

# Page layout constants (A4 portrait)
A4_WIDTH_INCHES = 8.27
A4_HEIGHT_INCHES = 11.69
DEFAULT_MARGIN_INCHES = 0.5
HEADER_HEIGHT_INCHES = 1.5
FOOTER_HEIGHT_INCHES = 0.8


def get_log_column_specifications() -> Dict[str, Dict]:
    """
    Get standardized column specifications for borehole logs.

    Returns:
        dict: Column specifications with widths, positions, and purposes
    """
    column_names = [
        "margin_left",
        "depth_from",
        "depth_to",
        "lithology",
        "sample_num",
        "sample_type",
        "recovery",
        "description",
        "margin_right",
    ]

    # Calculate cumulative positions
    cumulative_positions = []
    cumulative = 0.0
    for width in LOG_COLUMN_WIDTHS:
        cumulative_positions.append(cumulative)
        cumulative += width

    specifications = {}
    for i, (name, width, position) in enumerate(
        zip(column_names, LOG_COLUMN_WIDTHS, cumulative_positions)
    ):
        specifications[name] = {
            "index": i,
            "width_fraction": width,
            "position_fraction": position,
            "purpose": _get_column_purpose(name),
        }

    return specifications


def _get_column_purpose(column_name: str) -> str:
    """Get descriptive purpose for each column."""
    purposes = {
        "margin_left": "Left page margin",
        "depth_from": "Depth start values",
        "depth_to": "Depth end values",
        "lithology": "Geological visual representation",
        "sample_num": "Sample identification numbers",
        "sample_type": "Sample type codes",
        "recovery": "Sample recovery percentages",
        "description": "Detailed geological descriptions",
        "margin_right": "Right page margin",
    }
    return purposes.get(column_name, "Unknown purpose")


def calculate_page_dimensions(
    margin_inches: float = DEFAULT_MARGIN_INCHES,
    header_height: float = HEADER_HEIGHT_INCHES,
    footer_height: float = FOOTER_HEIGHT_INCHES,
) -> Dict[str, float]:
    """
    Calculate page dimensions and usable area.

    Args:
        margin_inches: Page margins in inches
        header_height: Header height in inches
        footer_height: Footer height in inches

    Returns:
        dict: Page dimension specifications
    """
    usable_width = A4_WIDTH_INCHES - (2 * margin_inches)
    usable_height = (
        A4_HEIGHT_INCHES - header_height - footer_height - (2 * margin_inches)
    )

    return {
        "page_width": A4_WIDTH_INCHES,
        "page_height": A4_HEIGHT_INCHES,
        "margin": margin_inches,
        "usable_width": usable_width,
        "usable_height": usable_height,
        "content_left": margin_inches,
        "content_bottom": margin_inches + footer_height,
        "content_right": A4_WIDTH_INCHES - margin_inches,
        "content_top": A4_HEIGHT_INCHES - margin_inches - header_height,
        "header_bottom": A4_HEIGHT_INCHES - margin_inches - header_height,
        "footer_top": margin_inches + footer_height,
    }


def calculate_text_box_positions_aligned(
    fig,
    ax,
    text_boxes: List[Dict],
    page_width_in: float,
    usable_width_in: float,
    col_widths_in: List[float],
    start_x_in: float,
    usable_bottom_in: float,
    gap_height: float = 0.02,
) -> List[Dict]:
    """
    Calculate aligned positions for text boxes in borehole log layout.

    Args:
        fig: matplotlib figure
        ax: matplotlib axes
        text_boxes: List of text box specifications
        page_width_in: Total page width in inches
        usable_width_in: Usable content width in inches
        col_widths_in: Column widths in inches
        start_x_in: Starting X position in inches
        usable_bottom_in: Bottom boundary for content in inches
        gap_height: Vertical gap between rows in inches

    Returns:
        list: Updated text boxes with calculated positions
    """
    if not text_boxes:
        return []

    # Group text boxes by row (same depth interval)
    rows = {}
    for box in text_boxes:
        depth_key = (box.get("depth_top", 0), box.get("depth_base", 0))
        if depth_key not in rows:
            rows[depth_key] = []
        rows[depth_key].append(box)

    # Sort rows by depth
    sorted_depths = sorted(rows.keys(), key=lambda x: x[0])

    positioned_boxes = []
    current_y = usable_bottom_in

    for depth_key in sorted_depths:
        row_boxes = rows[depth_key]

        # Calculate maximum height needed for this row
        max_height = max(box.get("height", 0.3) for box in row_boxes)

        # Position each box in the row
        for box in row_boxes:
            col_index = box.get("column_index", 0)

            # Calculate X position based on column
            if col_index < len(col_widths_in):
                x_position = start_x_in + sum(col_widths_in[:col_index])
                box_width = col_widths_in[col_index]
            else:
                # Default to last column if index out of range
                x_position = start_x_in + sum(col_widths_in[:-1])
                box_width = col_widths_in[-1]

            # Update box position
            updated_box = box.copy()
            updated_box.update(
                {
                    "x": x_position,
                    "y": current_y,
                    "width": box_width,
                    "height": max_height,
                    "row_height": max_height,
                }
            )

            positioned_boxes.append(updated_box)

        # Move to next row
        current_y += max_height + gap_height

    return positioned_boxes


def determine_optimal_layout(
    content_height: float,
    available_height: float,
    min_row_height: float = 0.2,
    max_rows_per_page: int = 50,
) -> Dict[str, float]:
    """
    Determine optimal layout parameters for content fitting.

    Args:
        content_height: Required content height in inches
        available_height: Available space height in inches
        min_row_height: Minimum row height in inches
        max_rows_per_page: Maximum rows per page

    Returns:
        dict: Layout optimization parameters
    """
    # Calculate if content fits on one page
    fits_single_page = content_height <= available_height

    if fits_single_page:
        return {
            "pages_needed": 1,
            "content_per_page": content_height,
            "rows_per_page": min(
                int(available_height / min_row_height), max_rows_per_page
            ),
            "optimal_row_height": max(
                min_row_height,
                content_height
                / min(content_height / min_row_height, max_rows_per_page),
            ),
            "scaling_factor": 1.0,
            "requires_compression": False,
        }

    # Calculate multi-page layout
    pages_needed = int(content_height / available_height) + 1
    content_per_page = content_height / pages_needed
    rows_per_page = min(int(available_height / min_row_height), max_rows_per_page)

    # Determine if compression is needed
    requires_compression = content_per_page > available_height
    scaling_factor = (
        available_height / content_per_page if requires_compression else 1.0
    )

    return {
        "pages_needed": pages_needed,
        "content_per_page": content_per_page,
        "rows_per_page": rows_per_page,
        "optimal_row_height": min_row_height * scaling_factor,
        "scaling_factor": scaling_factor,
        "requires_compression": requires_compression,
    }


def calculate_column_positions(
    usable_width: float, start_x: float, column_widths: Optional[List[float]] = None
) -> List[Tuple[float, float]]:
    """
    Calculate absolute column positions and widths.

    Args:
        usable_width: Total usable width in inches
        start_x: Starting X coordinate in inches
        column_widths: Optional custom column width fractions

    Returns:
        list: List of (position, width) tuples for each column
    """
    if column_widths is None:
        column_widths = LOG_COLUMN_WIDTHS

    positions = []
    current_x = start_x

    for width_fraction in column_widths:
        width_inches = usable_width * width_fraction
        positions.append((current_x, width_inches))
        current_x += width_inches

    return positions


def validate_layout_parameters(
    page_width: float,
    page_height: float,
    margins: float,
    header_height: float,
    footer_height: float,
) -> Tuple[bool, str]:
    """
    Validate layout parameters for reasonableness.

    Args:
        page_width: Page width in inches
        page_height: Page height in inches
        margins: Margin size in inches
        header_height: Header height in inches
        footer_height: Footer height in inches

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check basic parameter validity
    if any(
        param <= 0
        for param in [page_width, page_height, margins, header_height, footer_height]
    ):
        return False, "All layout parameters must be positive"

    # Check that margins don't exceed page dimensions
    if margins * 2 >= page_width:
        return False, "Horizontal margins too large for page width"

    if margins * 2 >= page_height:
        return False, "Vertical margins too large for page height"

    # Check that header and footer don't consume entire page
    total_fixed_height = header_height + footer_height + (margins * 2)
    if total_fixed_height >= page_height:
        return False, "Header, footer, and margins consume entire page height"

    # Check for reasonable usable area
    usable_width = page_width - (margins * 2)
    usable_height = page_height - total_fixed_height

    if usable_width < 2.0:  # Less than 2 inches wide
        return False, "Usable width too narrow for content"

    if usable_height < 3.0:  # Less than 3 inches tall
        return False, "Usable height too short for content"

    return True, "Layout parameters valid"


def optimize_column_widths(
    content_analysis: Dict[str, float],
    total_width: float,
    min_column_width: float = 0.5,
) -> List[float]:
    """
    Optimize column widths based on content analysis.

    Args:
        content_analysis: Analysis of content requirements per column
        total_width: Total available width
        min_column_width: Minimum column width in inches

    Returns:
        list: Optimized column width fractions
    """
    # Start with default widths
    base_widths = LOG_COLUMN_WIDTHS.copy()

    # Adjust based on content analysis
    if "description_avg_length" in content_analysis:
        desc_length = content_analysis["description_avg_length"]

        # Increase description column if content is long
        if desc_length > 100:  # Long descriptions
            # Reduce other columns slightly and increase description
            adjustment = 0.05
            base_widths[7] += adjustment  # Description column

            # Redistribute reduction across other columns
            reduction_per_col = adjustment / 6
            for i in [1, 2, 4, 5, 6, 8]:  # Skip lithology and description
                base_widths[i] = max(base_widths[i] - reduction_per_col, 0.02)

    # Ensure minimum widths
    total_fraction = sum(base_widths)
    if total_fraction > 1.0:
        # Normalize to sum to 1.0
        base_widths = [w / total_fraction for w in base_widths]

    # Validate minimum absolute widths
    for i, width_fraction in enumerate(base_widths):
        min_fraction = min_column_width / total_width
        if width_fraction < min_fraction:
            base_widths[i] = min_fraction

    # Re-normalize if needed
    total_fraction = sum(base_widths)
    if total_fraction > 1.0:
        base_widths = [w / total_fraction for w in base_widths]

    return base_widths


def get_standard_row_heights() -> Dict[str, float]:
    """
    Get standard row height specifications.

    Returns:
        dict: Standard row heights for different content types
    """
    return {
        "minimal": 0.15,  # Very short descriptions
        "standard": 0.25,  # Normal descriptions
        "expanded": 0.4,  # Longer descriptions
        "maximum": 0.6,  # Very long descriptions
        "header": 0.3,  # Header rows
        "footer": 0.2,  # Footer rows
    }


def calculate_plot_layout(page_settings: Dict) -> Dict:
    """
    Calculate the main plot layout from page settings.

    Args:
        page_settings: Page configuration settings

    Returns:
        dict: Layout information including plot dimensions and positions
    """
    try:
        page_width = page_settings.get("page_width", 8.27)
        page_height = page_settings.get("page_height", 11.69)
        margin = page_settings.get("margin", 0.5)
        header_height = page_settings.get("header_height", 1.5)
        footer_height = page_settings.get("footer_height", 0.8)

        # Calculate plot area
        plot_width = page_width - (2 * margin)
        plot_height = page_height - (2 * margin) - header_height - footer_height

        # Calculate positions (normalized to page)
        plot_left = margin / page_width
        plot_bottom = (margin + footer_height) / page_height
        plot_width_norm = plot_width / page_width
        plot_height_norm = plot_height / page_height

        return {
            "plot_width": plot_width * 72,  # Convert to points
            "plot_height": plot_height * 72,
            "plot_left": plot_left,
            "plot_bottom": plot_bottom,
            "plot_width_norm": plot_width_norm,
            "plot_height_norm": plot_height_norm,
            "margin": margin,
            "header_height": header_height,
            "footer_height": footer_height,
        }

    except Exception as e:
        logger.error(f"Error calculating plot layout: {e}")
        # Return safe defaults
        return {
            "plot_width": 500,
            "plot_height": 700,
            "plot_left": 0.06,
            "plot_bottom": 0.08,
            "plot_width_norm": 0.88,
            "plot_height_norm": 0.84,
            "margin": 0.5,
            "header_height": 1.5,
            "footer_height": 0.8,
        }


def create_column_layout(plot_width: float) -> Dict:
    """
    Create column layout for borehole log sections.

    Args:
        plot_width: Available plot width in points

    Returns:
        dict: Column specifications with positions and widths
    """
    try:
        # Define column proportions
        depth_width = 10  # Percentage
        geology_width = 60
        sample_width = 20
        spacing = 5

        # Calculate actual widths
        total_content = depth_width + geology_width + sample_width
        spacing_total = spacing * 2  # Between columns

        # Scale to available width
        scale_factor = (100 - spacing_total) / total_content

        depth_actual = (depth_width * scale_factor * plot_width) / 100
        geology_actual = (geology_width * scale_factor * plot_width) / 100
        sample_actual = (sample_width * scale_factor * plot_width) / 100
        spacing_actual = (spacing * plot_width) / 100

        # Calculate positions
        depth_left = 0
        geology_left = depth_actual + spacing_actual
        sample_left = geology_left + geology_actual + spacing_actual

        return {
            "depth": {
                "left": depth_left,
                "width": depth_actual,
                "center": depth_left + depth_actual / 2,
            },
            "geology": {
                "left": geology_left,
                "width": geology_actual,
                "center": geology_left + geology_actual / 2,
            },
            "samples": {
                "left": sample_left,
                "width": sample_actual,
                "center": sample_left + sample_actual / 2,
            },
            "spacing": spacing_actual,
        }

    except Exception as e:
        logger.error(f"Error creating column layout: {e}")
        # Return safe defaults
        return {
            "depth": {"left": 0, "width": 50, "center": 25},
            "geology": {"left": 60, "width": 300, "center": 210},
            "samples": {"left": 370, "width": 100, "center": 420},
            "spacing": 10,
        }


def calculate_depths(start_depth: float, end_depth: float, scale: float = 50.0) -> Dict:
    """
    Calculate depth-related layout parameters.

    Args:
        start_depth: Starting depth in meters
        end_depth: Ending depth in meters
        scale: Scale factor (points per meter)

    Returns:
        dict: Depth calculation results
    """
    try:
        depth_range = end_depth - start_depth
        plot_height = depth_range * scale

        return {
            "start_depth": start_depth,
            "end_depth": end_depth,
            "depth_range": depth_range,
            "plot_height": plot_height,
            "scale": scale,
            "meters_per_point": 1.0 / scale,
        }

    except Exception as e:
        logger.error(f"Error calculating depths: {e}")
        return {
            "start_depth": 0.0,
            "end_depth": 10.0,
            "depth_range": 10.0,
            "plot_height": 500,
            "scale": 50.0,
            "meters_per_point": 0.02,
        }


def get_standard_margins() -> Dict[str, float]:
    """
    Get standard margin specifications.

    Returns:
        dict: Standard margin values in inches
    """
    return {
        "page_margin": 0.5,
        "header_margin": 0.2,
        "footer_margin": 0.2,
        "column_spacing": 0.1,
        "text_padding": 0.05,
    }


def validate_layout_settings(settings: Dict) -> Tuple[bool, List[str]]:
    """
    Validate layout settings for consistency and reasonableness.

    Args:
        settings: Layout settings to validate

    Returns:
        tuple: (is_valid, list_of_warnings)
    """
    warnings = []

    try:
        # Check required fields
        required_fields = ["page_width", "page_height", "margin"]
        for field in required_fields:
            if field not in settings:
                warnings.append(f"Missing required field: {field}")

        # Check page dimensions
        if "page_width" in settings and "page_height" in settings:
            width = settings["page_width"]
            height = settings["page_height"]

            if width <= 0 or height <= 0:
                warnings.append("Page dimensions must be positive")

            if width > 20 or height > 30:  # Reasonable limits
                warnings.append("Page dimensions appear unusually large")

        # Check margins
        if "margin" in settings:
            margin = settings["margin"]
            if margin < 0:
                warnings.append("Margin cannot be negative")
            elif margin > 2:
                warnings.append("Margin appears unusually large")

        # Check header/footer heights
        for field in ["header_height", "footer_height"]:
            if field in settings:
                height = settings[field]
                if height < 0:
                    warnings.append(f"{field} cannot be negative")
                elif height > 5:
                    warnings.append(f"{field} appears unusually large")

    except Exception as e:
        warnings.append(f"Error during validation: {e}")

    is_valid = len(warnings) == 0
    return is_valid, warnings
