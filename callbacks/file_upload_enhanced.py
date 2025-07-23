"""
Enhanced File Upload Callbacks

This module handles all file upload related callbacks with security validation,
error handling, and coordinate transformation.
"""

import logging
import base64
import statistics
from datetime import datetime
from typing import List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from dash import html, dcc, Output, Input, State
import dash
import dash_leaflet as dl

from .base import FileUploadCallbackBase
from .error_handling import CallbackError, create_error_message
from .file_validation import validate_file_size, validate_total_upload_size
from .coordinate_utils import BLUE_MARKER, calculate_map_center_and_zoom

from data_loader import load_all_loca_data
from coordinate_service import get_coordinate_service
from dataframe_optimizer import optimize_borehole_dataframe
from memory_manager import monitor_memory_usage
import config

logger = logging.getLogger(__name__)


class EnhancedFileUploadCallback(FileUploadCallbackBase):
    """Enhanced file upload processing callback with comprehensive validation."""

    def __init__(self):
        super().__init__("enhanced_file_upload")

    def register(self, app: dash.Dash) -> None:
        """Register the enhanced file upload callback."""

        @app.callback(
            [
                Output("output-upload", "children"),
                Output("borehole-markers", "children"),
                Output("borehole-map", "center", allow_duplicate=True),
                Output("borehole-map", "zoom", allow_duplicate=True),
                Output("borehole-data-store", "data"),
                Output("draw-control", "clear_all", allow_duplicate=True),
            ],
            [Input("upload-data-store", "data")],
            [State("borehole-map", "center"), State("borehole-map", "zoom")],
            prevent_initial_call=True,
        )
        def handle_file_upload(stored_data, map_center_state, map_zoom_state):
            """Handle file upload and create markers with comprehensive validation."""
            logging.info("=== ENHANCED FILE UPLOAD CALLBACK ===")

            # Default values
            map_center = map_center_state or [51.5, -0.1]
            map_zoom = map_zoom_state or 6

            if not stored_data or "contents" not in stored_data:
                logging.info("No file uploaded yet")
                return None, [], map_center, map_zoom, None, None

            try:
                # Process uploaded files
                list_of_contents = stored_data["contents"]
                list_of_names = stored_data["filenames"]
                logging.info(f"Processing {len(list_of_contents)} uploaded files")

                # SECURITY: Validate file sizes before processing
                files_for_validation = []
                for content, name in zip(list_of_contents, list_of_names or []):
                    content_type, content_string = content.split(",")
                    files_for_validation.append((content_type, content_string, name))

                # Validate total upload size and count
                is_valid_total, total_error, total_size_mb = validate_total_upload_size(
                    files_for_validation
                )
                if not is_valid_total:
                    logging.warning(f"Upload rejected: {total_error}")
                    error_msg = create_error_message(
                        CallbackError(
                            "Upload rejected due to size limits", total_error, "warning"
                        ),
                        "File Upload",
                    )
                    return [error_msg], [], map_center, map_zoom, None, None

                ags_files = []
                file_status = []
                total_processed_size = 0

                # Process each file individually
                for content, name in zip(list_of_contents, list_of_names or []):
                    try:
                        content_type, content_string = content.split(",")

                        # Validate individual file size
                        is_valid_file, file_error, file_size_mb = validate_file_size(
                            content_string, name
                        )
                        if not is_valid_file:
                            logging.warning(f"File rejected: {file_error}")
                            file_status.append(
                                html.Div(
                                    [
                                        html.Span("❌ ", style={"color": "red"}),
                                        html.Span(file_error, style={"color": "red"}),
                                    ]
                                )
                            )
                            continue

                        # Decode file content
                        decoded = base64.b64decode(content_string)
                        s = decoded.decode("utf-8")
                        ags_files.append((name, s))
                        total_processed_size += file_size_mb

                        file_status.append(
                            html.Div(
                                [
                                    html.Span("✅ ", style={"color": "green"}),
                                    html.Span(
                                        f"Uploaded: {name} ({file_size_mb:.1f}MB)",
                                        style={"color": "green"},
                                    ),
                                ]
                            )
                        )
                        logging.info(
                            f"Successfully processed file: {name} ({file_size_mb:.1f}MB)"
                        )

                    except Exception as e:
                        logging.error(f"Error reading {name}: {e}")
                        file_status.append(
                            html.Div(
                                [
                                    html.Span("❌ ", style={"color": "red"}),
                                    html.Span(
                                        f"Error reading {name}: {e}",
                                        style={"color": "red"},
                                    ),
                                ]
                            )
                        )

                # Check if any files were successfully processed
                if not ags_files:
                    error_msg = create_error_message(
                        CallbackError(
                            "No valid files could be processed",
                            "All uploaded files were rejected due to size limits or processing errors",
                            "error",
                        ),
                        "File Processing",
                    )
                    return [error_msg], [], map_center, map_zoom, None, None

                # Add upload summary
                file_status.insert(
                    0,
                    html.Div(
                        [
                            html.P(
                                "📊 Upload Summary:",
                                style={"fontWeight": "bold", "marginBottom": "5px"},
                            ),
                            html.P(
                                f"Files processed: {len(ags_files)}/{len(list_of_contents)}",
                                style={"margin": "2px 0"},
                            ),
                            html.P(
                                f"Total size: {total_processed_size:.1f}MB",
                                style={"margin": "2px 0"},
                            ),
                        ],
                        style={
                            "backgroundColor": "#f0f0f0",
                            "padding": "10px",
                            "borderRadius": "5px",
                            "marginBottom": "10px",
                        },
                    ),
                )

                # Load and process data
                loca_df, filename_map = load_all_loca_data(ags_files)
                logging.info(f"Loaded {len(loca_df)} boreholes")

                # === MEMORY OPTIMIZATION ===
                monitor_memory_usage("DEBUG")
                loca_df = optimize_borehole_dataframe(loca_df)
                logging.info(
                    f"✓ DataFrame optimized for memory efficiency: {len(loca_df)} rows"
                )

                # === COORDINATE TRANSFORMATION ===
                coordinate_service = get_coordinate_service()
                valid_coords = []
                markers = []

                for i, row in loca_df.iterrows():
                    try:
                        easting = (
                            float(row["LOCA_NATE"])
                            if pd.notnull(row["LOCA_NATE"])
                            else None
                        )
                        northing = (
                            float(row["LOCA_NATN"])
                            if pd.notnull(row["LOCA_NATN"])
                            else None
                        )

                        if easting is not None and northing is not None:
                            lat, lon = coordinate_service.transform_bng_to_wgs84(
                                easting, northing
                            )

                            if lat is not None and lon is not None:
                                # Store coordinates
                                loca_df.at[i, "lat"] = lat
                                loca_df.at[i, "lon"] = lon
                                valid_coords.append((lat, lon))

                                # Create marker
                                markers.append(
                                    self._create_borehole_marker(row, i, lat, lon)
                                )

                    except Exception as e:
                        logging.warning(
                            f"Skipping marker for row {i} ({row.get('LOCA_ID', 'unknown')}): {e}"
                        )

                # Calculate optimal map center and zoom
                if valid_coords:
                    map_center, map_zoom = calculate_map_center_and_zoom(valid_coords)
                    logging.info(f"🎯 Map center: {map_center}, zoom: {map_zoom}")
                else:
                    logging.warning("No valid coordinates found for map centering")

                # Store data for other callbacks
                borehole_data = {
                    "loca_df": loca_df.to_dict("records"),
                    "filename_map": filename_map,
                    "all_borehole_ids": loca_df["LOCA_ID"].tolist(),
                }

                # Add file breakdown and status info
                file_status.extend(
                    self._create_status_displays(
                        filename_map,
                        loca_df,
                        len(markers),
                        map_center,
                        map_zoom,
                        valid_coords,
                    )
                )

                # Clear any existing shapes on file upload
                clear_shapes = datetime.now().timestamp()

                return (
                    file_status,
                    markers,
                    map_center,
                    map_zoom,
                    borehole_data,
                    clear_shapes,
                )

            except Exception as e:
                logging.error(f"Error in file upload: {e}", exc_info=True)
                error_msg = create_error_message(
                    CallbackError(
                        "Failed to process uploaded files",
                        f"Unexpected error during file processing: {str(e)}",
                        "error",
                    ),
                    "File Upload",
                )
                clear_shapes = datetime.now().timestamp()
                return [error_msg], [], map_center, map_zoom, None, clear_shapes

    def _create_borehole_marker(
        self, row, index: int, lat: float, lon: float
    ) -> dl.Marker:
        """Create a borehole marker with proper formatting."""
        label = str(row["LOCA_ID"])
        marker_id = {"type": "borehole-marker", "index": index}

        # Format measurements
        ground_level = self._format_measurement(row.get("LOCA_GL", "N/A"))
        total_depth = self._format_measurement(row.get("LOCA_FDEP", "N/A"))

        tooltip_text = f"""
        Borehole: {label}
        Ground Level: {ground_level}
        Total Depth: {total_depth}
        Click to view borehole log
        """

        marker_icon = {
            "iconUrl": BLUE_MARKER,
            "iconSize": [25, 41],
            "iconAnchor": [12, 41],
            "popupAnchor": [1, -34],
            "shadowSize": [41, 41],
        }

        return dl.Marker(
            id=marker_id,
            position=[lat, lon],
            children=dl.Tooltip(tooltip_text.strip()),
            icon=marker_icon,
            n_clicks=0,
        )

    def _format_measurement(self, value) -> str:
        """Format measurement values with proper units."""
        if value == "N/A" or value is None or not str(value).strip():
            return "N/A"

        try:
            return f"{float(value):.2f}m"
        except (ValueError, TypeError):
            return "N/A"

    def _create_status_displays(
        self, filename_map, loca_df, marker_count, map_center, map_zoom, valid_coords
    ):
        """Create status display components for the UI."""
        displays = []

        # File breakdown
        file_breakdown = []
        for filename, content in filename_map.items():
            file_rows = loca_df[loca_df["ags_file"] == filename]
            if len(file_rows) > 0:
                file_breakdown.append(
                    html.Li([html.B(filename), f" : {len(file_rows)} boreholes"])
                )

        if file_breakdown:
            displays.append(
                html.Div(
                    [
                        html.H4("File Summary:", style=config.SUCCESS_MESSAGE_STYLE),
                        html.Ul(file_breakdown),
                    ]
                )
            )

        # Map status
        if valid_coords:
            lats = [coord[0] for coord in valid_coords]
            lons = [coord[1] for coord in valid_coords]
            coord_range = max(max(lats) - min(lats), max(lons) - min(lons))

            status_info = html.Div(
                [
                    html.H4(
                        "📍 Map Status:",
                        style={"color": "#28a745", "margin-top": "10px"},
                    ),
                    html.P(f"• Loaded {marker_count} borehole markers"),
                    html.P(
                        f"• Map centered: ({map_center[0]:.6f}, {map_center[1]:.6f})"
                    ),
                    html.P(f"• Coordinate range: {coord_range:.6f} degrees"),
                    html.P(f"• Auto-zoom level: {map_zoom}"),
                ],
                style={
                    "background-color": "#f8f9fa",
                    "padding": "10px",
                    "border-radius": "5px",
                    "margin-top": "10px",
                },
            )
            displays.append(status_info)

        return displays


# For backward compatibility
FileUploadCallback = EnhancedFileUploadCallback
