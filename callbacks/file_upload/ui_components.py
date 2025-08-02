"""
UI Components Module

This module handles the creation of UI status messages, upload summaries,
and other display components for the file upload process.
"""

from typing import List, Dict, Tuple
from dash import html
import pandas as pd


def create_upload_summary(
    processed_files: int, total_files: int, total_size_mb: float
) -> html.Div:
    """
    Create upload summary component.

    Args:
        processed_files: Number of successfully processed files
        total_files: Total number of uploaded files
        total_size_mb: Total size in MB of processed files

    Returns:
        Dash HTML component for upload summary
    """
    return html.Div(
        [
            html.P(
                "📊 Upload Summary:",
                style={"fontWeight": "bold", "marginBottom": "5px"},
            ),
            html.P(
                f"Files processed: {processed_files}/{total_files}",
                style={"margin": "2px 0"},
            ),
            html.P(
                f"Total size: {total_size_mb:.1f}MB",
                style={"margin": "2px 0"},
            ),
        ],
        style={
            "backgroundColor": "#f0f0f0",
            "padding": "10px",
            "borderRadius": "5px",
            "marginBottom": "10px",
        },
    )


def create_file_success_status(name: str, size_mb: float) -> html.Div:
    """
    Create success status component for individual file.

    Args:
        name: File name
        size_mb: File size in MB

    Returns:
        Dash HTML component for success status
    """
    return html.Div(
        [
            html.Span("✅ ", style={"color": "green"}),
            html.Span(
                f"Uploaded: {name} ({size_mb:.1f}MB)",
                style={"color": "green"},
            ),
        ]
    )


def create_file_error_status(error_message: str) -> html.Div:
    """
    Create error status component for individual file.

    Args:
        error_message: Error message to display

    Returns:
        Dash HTML component for error status
    """
    return html.Div(
        [
            html.Span("❌ ", style={"color": "red"}),
            html.Span(error_message, style={"color": "red"}),
        ]
    )


def create_file_breakdown_summary(
    filename_map: Dict[str, str], loca_df: pd.DataFrame
) -> html.Div:
    """
    Create file breakdown summary showing boreholes per file.

    Args:
        filename_map: Mapping of filenames to content
        loca_df: DataFrame containing borehole location data

    Returns:
        Dash HTML component for file breakdown
    """
    file_breakdown = []
    for filename in filename_map.keys():
        file_rows = loca_df[loca_df["ags_file"] == filename]
        if len(file_rows) > 0:
            file_breakdown.append(
                html.Li([html.B(filename), f" : {len(file_rows)} boreholes"])
            )

    if not file_breakdown:
        return html.Div()

    # Import config for styling
    try:
        from config_modules import SUCCESS_MESSAGE_STYLE

        style = SUCCESS_MESSAGE_STYLE
    except (ImportError, AttributeError):
        style = {"color": "#28a745"}

    return html.Div(
        [
            html.H4("File Summary:", style=style),
            html.Ul(file_breakdown),
        ]
    )


def create_map_status_info(
    marker_count: int, map_center: List[float], coord_range: float, map_zoom: int
) -> html.Div:
    """
    Create map status information component.

    Args:
        marker_count: Number of map markers created
        map_center: Map center coordinates [lat, lon]
        coord_range: Coordinate range in degrees
        map_zoom: Map zoom level

    Returns:
        Dash HTML component for map status
    """
    return html.Div(
        [
            html.H4(
                "📍 Map Status:",
                style={"color": "#28a745", "marginTop": "10px"},
            ),
            html.P(f"• Loaded {marker_count} borehole markers"),
            html.P(f"• Map centered: ({map_center[0]:.6f}, {map_center[1]:.6f})"),
            html.P(f"• Coordinate range: {coord_range:.6f} degrees"),
            html.P(f"• Auto-zoom level: {map_zoom}"),
        ],
        style={
            "backgroundColor": "#f8f9fa",
            "padding": "10px",
            "borderRadius": "5px",
            "marginTop": "10px",
        },
    )


def create_processing_error_message(error_details: str) -> html.Div:
    """
    Create error message component for processing errors.

    Args:
        error_details: Detailed error message

    Returns:
        Dash HTML component for error message
    """
    return html.Div(
        [
            html.H4("❌ Processing Error", style={"color": "red"}),
            html.P(error_details, style={"color": "red", "fontSize": "14px"}),
            html.P(
                "Please check your files and try again.",
                style={"color": "gray", "fontSize": "12px"},
            ),
        ],
        style={
            "backgroundColor": "#ffe6e6",
            "padding": "15px",
            "borderRadius": "5px",
            "border": "1px solid red",
            "margin": "10px 0",
        },
    )
