"""
Borehole Log Header and Footer Module

This module handles header and footer generation for professional borehole logs,
including project information, borehole details, and page numbering.

Key Functions:
- draw_header: Create professional header with project information
- draw_footer: Create footer with page numbers and references
- create_header_content: Generate header content from data
- format_borehole_info: Format borehole identification information
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import logging
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)


def draw_header(
    fig,
    ax,
    header_data: Dict,
    page_width_in: float,
    header_height_in: float = 1.5,
    margin_in: float = 0.5,
) -> None:
    """
    Draw professional header for borehole log.

    Args:
        fig: matplotlib figure
        ax: matplotlib axes (used for coordinate transformation)
        header_data: Dictionary containing header information
        page_width_in: Page width in inches
        header_height_in: Header height in inches
        margin_in: Page margin in inches
    """
    try:
        # Calculate header position (top of page)
        header_left = margin_in / page_width_in
        header_bottom = 1.0 - (margin_in + header_height_in) / 11.69  # A4 height
        header_width = (page_width_in - 2 * margin_in) / page_width_in
        header_height = header_height_in / 11.69

        # Create header area as separate axes
        header_ax = fig.add_axes(
            [header_left, header_bottom, header_width, header_height]
        )
        header_ax.set_xlim(0, 1)
        header_ax.set_ylim(0, 1)
        header_ax.axis("off")

        # Draw header border
        header_ax.add_patch(
            Rectangle((0, 0), 1, 1, linewidth=1.5, edgecolor="black", facecolor="none")
        )

        # Header content layout
        _draw_header_content(header_ax, header_data)

    except Exception as e:
        logger.error(f"Error drawing header: {e}")


def _draw_header_content(header_ax, header_data: Dict) -> None:
    """Draw the actual header content within the header area."""

    # Title section (top portion)
    title = header_data.get("title", "Borehole Log")
    header_ax.text(
        0.5,
        0.85,
        title,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        transform=header_ax.transAxes,
    )

    # Project information (left side)
    project_info = [
        f"Project: {header_data.get('project_name', 'N/A')}",
        f"Location: {header_data.get('location', 'N/A')}",
        f"Client: {header_data.get('client', 'N/A')}",
    ]

    for i, info in enumerate(project_info):
        header_ax.text(
            0.05,
            0.65 - i * 0.15,
            info,
            ha="left",
            va="center",
            fontsize=9,
            transform=header_ax.transAxes,
        )

    # Borehole information (right side)
    borehole_info = [
        f"Borehole: {header_data.get('borehole_id', 'N/A')}",
        f"Coordinates: {_format_coordinates(header_data)}",
        f"Ground Level: {header_data.get('ground_level', 'N/A')} m",
    ]

    for i, info in enumerate(borehole_info):
        header_ax.text(
            0.55,
            0.65 - i * 0.15,
            info,
            ha="left",
            va="center",
            fontsize=9,
            transform=header_ax.transAxes,
        )

    # Date and revision information (bottom)
    date_info = f"Date: {header_data.get('date', 'N/A')}"
    revision_info = f"Rev: {header_data.get('revision', '01')}"

    header_ax.text(
        0.05,
        0.1,
        date_info,
        ha="left",
        va="center",
        fontsize=8,
        transform=header_ax.transAxes,
    )

    header_ax.text(
        0.95,
        0.1,
        revision_info,
        ha="right",
        va="center",
        fontsize=8,
        transform=header_ax.transAxes,
    )


def _format_coordinates(header_data: Dict) -> str:
    """Format coordinate information for display."""
    easting = header_data.get("easting")
    northing = header_data.get("northing")

    if easting and northing:
        try:
            return f"{float(easting):.0f}, {float(northing):.0f}"
        except (ValueError, TypeError):
            return f"{easting}, {northing}"

    return "N/A"


def draw_footer(
    fig,
    page_number: int,
    total_pages: int,
    footer_data: Optional[Dict] = None,
    page_width_in: float = 8.27,
    footer_height_in: float = 0.8,
    margin_in: float = 0.5,
) -> None:
    """
    Draw professional footer for borehole log.

    Args:
        fig: matplotlib figure
        page_number: Current page number
        total_pages: Total number of pages
        footer_data: Optional footer information
        page_width_in: Page width in inches
        footer_height_in: Footer height in inches
        margin_in: Page margin in inches
    """
    try:
        if footer_data is None:
            footer_data = {}

        # Calculate footer position (bottom of page)
        footer_left = margin_in / page_width_in
        footer_bottom = margin_in / 11.69  # A4 height
        footer_width = (page_width_in - 2 * margin_in) / page_width_in
        footer_height = footer_height_in / 11.69

        # Create footer area as separate axes
        footer_ax = fig.add_axes(
            [footer_left, footer_bottom, footer_width, footer_height]
        )
        footer_ax.set_xlim(0, 1)
        footer_ax.set_ylim(0, 1)
        footer_ax.axis("off")

        # Draw footer border
        footer_ax.add_patch(
            Rectangle((0, 0), 1, 1, linewidth=1, edgecolor="black", facecolor="none")
        )

        # Footer content
        _draw_footer_content(footer_ax, page_number, total_pages, footer_data)

    except Exception as e:
        logger.error(f"Error drawing footer: {e}")


def _draw_footer_content(
    footer_ax, page_number: int, total_pages: int, footer_data: Dict
) -> None:
    """Draw the actual footer content within the footer area."""

    # Company/organization name (left)
    company = footer_data.get("company", "Professional Geotechnical Services")
    footer_ax.text(
        0.05,
        0.7,
        company,
        ha="left",
        va="center",
        fontsize=9,
        fontweight="bold",
        transform=footer_ax.transAxes,
    )

    # Drawing/document reference (center-left)
    drawing_ref = footer_data.get("drawing_ref", "BH-LOG-001")
    footer_ax.text(
        0.05,
        0.3,
        f"Drawing No: {drawing_ref}",
        ha="left",
        va="center",
        fontsize=8,
        transform=footer_ax.transAxes,
    )

    # Page number (center-right)
    page_text = f"Page {page_number} of {total_pages}"
    footer_ax.text(
        0.7,
        0.5,
        page_text,
        ha="center",
        va="center",
        fontsize=9,
        transform=footer_ax.transAxes,
    )

    # Scale and date (right)
    scale = footer_data.get("scale", "1:500")
    date = footer_data.get("date", "July 2025")

    footer_ax.text(
        0.95,
        0.7,
        f"Scale: {scale}",
        ha="right",
        va="center",
        fontsize=8,
        transform=footer_ax.transAxes,
    )

    footer_ax.text(
        0.95,
        0.3,
        date,
        ha="right",
        va="center",
        fontsize=8,
        transform=footer_ax.transAxes,
    )


def create_header_content(
    loca_row: Dict,
    project_info: Optional[Dict] = None,
    additional_info: Optional[Dict] = None,
) -> Dict:
    """
    Create header content dictionary from borehole and project data.

    Args:
        loca_row: Borehole location data (from LOCA group)
        project_info: Project information (from PROJ group)
        additional_info: Additional header information

    Returns:
        dict: Formatted header content
    """
    header_content = {}

    # Borehole identification
    header_content["borehole_id"] = loca_row.get("LOCA_ID", "Unknown")
    header_content["ground_level"] = _format_elevation(loca_row.get("LOCA_GL"))

    # Coordinates
    header_content["easting"] = loca_row.get("LOCA_NATE")
    header_content["northing"] = loca_row.get("LOCA_NATN")

    # Project information
    if project_info:
        header_content["project_name"] = project_info.get(
            "PROJ_NAME", "Unnamed Project"
        )
        header_content["location"] = project_info.get("PROJ_LOC", "Unknown Location")
        header_content["client"] = project_info.get("PROJ_CLNT", "Unknown Client")
    else:
        header_content["project_name"] = "Unnamed Project"
        header_content["location"] = "Unknown Location"
        header_content["client"] = "Unknown Client"

    # Additional information
    if additional_info:
        header_content.update(additional_info)

    # Default values
    header_content.setdefault("title", "Professional Borehole Log")
    header_content.setdefault("date", "July 2025")
    header_content.setdefault("revision", "01")

    return header_content


def _format_elevation(elevation) -> str:
    """Format elevation value for display."""
    if elevation is None:
        return "N/A"

    try:
        return f"{float(elevation):.2f}"
    except (ValueError, TypeError):
        return str(elevation)


def create_footer_content(
    project_info: Optional[Dict] = None, document_info: Optional[Dict] = None
) -> Dict:
    """
    Create footer content dictionary.

    Args:
        project_info: Project information
        document_info: Document-specific information

    Returns:
        dict: Formatted footer content
    """
    footer_content = {}

    # Company/organization
    if document_info and "company" in document_info:
        footer_content["company"] = document_info["company"]
    else:
        footer_content["company"] = "Professional Geotechnical Services"

    # Drawing reference
    if document_info and "drawing_ref" in document_info:
        footer_content["drawing_ref"] = document_info["drawing_ref"]
    else:
        # Generate drawing reference from project
        project_id = ""
        if project_info and "PROJ_ID" in project_info:
            project_id = project_info["PROJ_ID"]
        footer_content["drawing_ref"] = (
            f"{project_id}-BH-LOG" if project_id else "BH-LOG-001"
        )

    # Scale and date
    footer_content.setdefault("scale", "1:500")
    footer_content.setdefault("date", "July 2025")

    return footer_content


def validate_header_data(header_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate header data completeness and format.

    Args:
        header_data: Header data dictionary

    Returns:
        tuple: (is_valid, list_of_warnings)
    """
    warnings = []

    # Required fields
    required_fields = ["borehole_id", "title"]
    for field in required_fields:
        if not header_data.get(field):
            warnings.append(f"Missing required field: {field}")

    # Coordinate validation
    easting = header_data.get("easting")
    northing = header_data.get("northing")

    if easting and northing:
        try:
            east_val = float(easting)
            north_val = float(northing)

            # Basic UK coordinate range check (very rough)
            if not (0 <= east_val <= 800000):
                warnings.append("Easting value appears out of range for UK coordinates")
            if not (0 <= north_val <= 1400000):
                warnings.append(
                    "Northing value appears out of range for UK coordinates"
                )

        except (ValueError, TypeError):
            warnings.append("Coordinate values should be numeric")

    # Ground level validation
    ground_level = header_data.get("ground_level")
    if ground_level and ground_level != "N/A":
        try:
            gl_val = float(ground_level)
            if gl_val < -100 or gl_val > 2000:  # Reasonable elevation range
                warnings.append("Ground level appears out of reasonable range")
        except (ValueError, TypeError):
            warnings.append("Ground level should be numeric")

    is_valid = len(warnings) == 0
    return is_valid, warnings


def get_header_layout_specs() -> Dict[str, Dict]:
    """
    Get standard header layout specifications.

    Returns:
        dict: Header layout specifications
    """
    return {
        "title": {
            "position": (0.5, 0.85),
            "alignment": ("center", "center"),
            "fontsize": 14,
            "fontweight": "bold",
        },
        "project_info": {
            "start_position": (0.05, 0.65),
            "line_spacing": 0.15,
            "fontsize": 9,
            "alignment": ("left", "center"),
        },
        "borehole_info": {
            "start_position": (0.55, 0.65),
            "line_spacing": 0.15,
            "fontsize": 9,
            "alignment": ("left", "center"),
        },
        "footer_info": {
            "left_position": (0.05, 0.1),
            "right_position": (0.95, 0.1),
            "fontsize": 8,
            "alignment": ("left", "center"),
        },
    }
