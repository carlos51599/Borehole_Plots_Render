"""
Split callbacks module for the Geo Borehole Sections Render application.

This module contains all Dash callbacks organized in a clean, modular structure
to handle the interactive functionality of the geotechnical borehole visualization
application. It coordinates data upload, processing, map interactions, and plot generation.

Main Callback Functions:
1. File Upload Callbacks:
   - handle_file_upload(): Process AGS file uploads and validation
   - display_upload_feedback(): Show upload status and file information

2. Map Interaction Callbacks:
   - update_borehole_markers(): Place borehole markers on map
   - handle_map_interactions(): Process map clicks and selections
   - update_map_center(): Auto-center map on uploaded boreholes

3. Drawing Tool Callbacks:
   - handle_shape_drawing(): Process polygon/rectangle/polyline selections
   - update_buffer_controls(): Show/hide buffer controls for polylines
   - apply_buffer_filtering(): Filter boreholes by buffered polylines

4. Search Functionality:
   - update_borehole_search(): Populate search dropdown with borehole names
   - handle_search_selection(): Navigate to selected borehole on map

5. Plot Generation Callbacks:
   - generate_section_plots(): Create cross-sectional geological plots
   - generate_borehole_logs(): Create individual borehole log plots
   - handle_plot_downloads(): Enable plot downloads as images

6. Data Management:
   - optimize_data_handling(): Memory-efficient data processing
   - error_handling(): Comprehensive error management with user feedback

Key Features:
- Memory optimization for large datasets
- Comprehensive error handling and user feedback
- Progress indicators for long-running operations
- Professional plot styling and customization
- Multi-file AGS support with conflict resolution

Dependencies:
- dash: Core web application framework
- pandas: Data manipulation and analysis
- matplotlib: Professional geological plot generation
- sklearn: PCA analysis for optimal section orientation
- pyproj: Coordinate system transformations (via coordinate_service)

Author: [Project Team]
Last Modified: July 2025
"""

# ====================================================================
# SPLIT CALLBACKS - Clean, Focused, Easy to Edit
# ====================================================================

import dash
from dash import html, dcc, Output, Input, State
import dash_leaflet as dl
import pandas as pd
import logging
import statistics
import base64
import io
from sklearn.decomposition import PCA
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

import config
from data_loader import load_all_loca_data
from map_utils import filter_selection_by_shape
from coordinate_service import get_coordinate_service
from dataframe_optimizer import optimize_borehole_dataframe
from app_constants import FILE_LIMITS, MAP_CONFIG, PLOT_CONFIG
from loading_indicators import (
    LoadingIndicator,
    get_loading_manager,
    create_upload_loading,
    create_plot_loading,
    create_data_loading,
)

# Import memory management
from memory_manager import monitor_memory_usage

# from section_plot import plot_section_from_ags_content
from section import plot_section_from_ags_content

# from borehole_log import plot_borehole_log_from_ags_content
from borehole_log_professional import plot_borehole_log_from_ags_content
from polyline_utils import (
    create_buffer_visualization,
    create_polyline_section,
    create_buffer_zone,
    project_boreholes_to_polyline,
    calculate_distance_along_polyline,
    point_to_line_distance,
    project_point_to_line_segment,
)

matplotlib.use("Agg")

# File upload security configuration
# File size limits - imported from constants
MAX_FILE_SIZE_MB = FILE_LIMITS.MAX_FILE_SIZE_MB
MAX_TOTAL_FILES_SIZE_MB = FILE_LIMITS.MAX_TOTAL_FILES_MB
MAX_FILES_COUNT = 10  # Maximum number of files that can be uploaded at once


class CallbackError(Exception):
    """
    Custom exception for callback errors with user-friendly messages.

    This exception class enables better error handling by separating technical
    error details (for logging) from user-friendly messages (for display).
    It also supports different error types for appropriate styling.

    Attributes:
        user_message (str): User-friendly error message for display
        technical_message (str): Technical error details for logging
        error_type (str): Type of error - 'error', 'warning', or 'info'

    Example:
        >>> raise CallbackError(
        ...     user_message="Unable to process AGS file. Please check file format.",
        ...     technical_message="AGS parser failed: missing LOCA group header",
        ...     error_type="error"
        ... )
    """

    def __init__(self, user_message, technical_message=None, error_type="error"):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        self.error_type = error_type  # 'error', 'warning', 'info'
        super().__init__(self.technical_message)


def create_error_message(error, context="Operation"):
    """
    Create a standardized error message component for display to users.

    This function takes any error (Exception or CallbackError) and creates
    a styled HTML component for consistent error presentation throughout
    the application.

    Args:
        error (Exception or CallbackError): The error to display
        context (str): Context description where the error occurred
                      (default: "Operation")

    Returns:
        html.Div: Styled Dash HTML component containing the error message

    Error Types and Styling:
        - error: Red border, light red background (for critical errors)
        - warning: Orange border, light orange background (for warnings)
        - info: Blue border, light blue background (for informational messages)

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     return create_error_message(e, "File upload")
    """
    if isinstance(error, CallbackError):
        user_msg = error.user_message
        tech_msg = error.technical_message
        error_type = error.error_type
    else:
        user_msg = f"{context} failed. Please try again."
        tech_msg = str(error)
        error_type = "error"

    # Choose colors based on error type
    colors = {
        "error": {"border": "red", "bg": "#ffebee", "text": "darkred"},
        "warning": {"border": "orange", "bg": "#fff3e0", "text": "darkorange"},
        "info": {"border": "blue", "bg": "#e3f2fd", "text": "darkblue"},
    }

    color_scheme = colors.get(error_type, colors["error"])

    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        f"❌ {user_msg}" if error_type == "error" else f"⚠️ {user_msg}",
                        style={
                            "margin": "0",
                            "fontWeight": "bold",
                            "color": color_scheme["text"],
                        },
                    ),
                    (
                        html.Details(
                            [
                                html.Summary(
                                    "Technical Details",
                                    style={"cursor": "pointer", "marginTop": "10px"},
                                ),
                                html.P(
                                    tech_msg,
                                    style={
                                        "margin": "5px 0",
                                        "fontFamily": "monospace",
                                        "fontSize": "12px",
                                    },
                                ),
                            ],
                            style={"marginTop": "10px"},
                        )
                        if tech_msg != user_msg
                        else None
                    ),
                ]
            )
        ],
        style={
            "border": f"2px solid {color_scheme['border']}",
            "backgroundColor": color_scheme["bg"],
            "padding": "15px",
            "borderRadius": "8px",
            "margin": "10px 0",
        },
    )


def create_success_message(message, details=None):
    """
    Create a standardized success message for display to users.

    Args:
        message: Success message text
        details: Optional additional details

    Returns:
        html.Div: Styled success message component
    """
    return html.Div(
        [
            html.P(
                f"✅ {message}",
                style={"margin": "0", "fontWeight": "bold", "color": "darkgreen"},
            ),
            (
                html.P(details, style={"margin": "5px 0 0 0", "color": "green"})
                if details
                else None
            ),
        ],
        style={
            "border": "2px solid green",
            "backgroundColor": "#e8f5e8",
            "padding": "15px",
            "borderRadius": "8px",
            "margin": "10px 0",
        },
    )


def handle_callback_error(func):
    """
    Decorator for consistent error handling in callbacks.

    Usage:
        @handle_callback_error
        def my_callback(...):
            # callback logic
            return results
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CallbackError as e:
            logging.error(f"Callback error in {func.__name__}: {e.technical_message}")
            # Return appropriate no_update or error UI based on callback signature
            return create_callback_error_response(e, func.__name__)
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            error = CallbackError(
                f"An unexpected error occurred in {func.__name__.replace('_', ' ')}",
                str(e),
            )
            return create_callback_error_response(error, func.__name__)

    return wrapper


def create_callback_error_response(error, callback_name):
    """
    Create appropriate error response based on callback type.
    This is a simplified version - in practice, you'd need to know the expected return structure.
    """
    # For now, return a generic error message
    # In a full implementation, you'd inspect the callback signature or use a registry
    return create_error_message(error, callback_name.replace("_", " ").title())


def validate_file_size(content_string, filename):
    """
    Validate file size to prevent DoS attacks.

    Args:
        content_string: Base64 encoded file content
        filename: Name of the file being uploaded

    Returns:
        tuple: (is_valid, error_message, size_mb)
    """
    try:
        # Calculate file size from base64 content
        # Base64 encoding increases size by ~33%, so we decode to get actual size
        decoded_size = len(base64.b64decode(content_string))
        size_mb = decoded_size / (1024 * 1024)  # Convert to MB

        if size_mb > MAX_FILE_SIZE_MB:
            return (
                False,
                f"File '{filename}' ({size_mb:.1f}MB) exceeds maximum size of {MAX_FILE_SIZE_MB}MB",
                size_mb,
            )

        return True, None, size_mb
    except Exception as e:
        return False, f"Error validating file '{filename}': {str(e)}", 0


def validate_total_upload_size(files_data):
    """
    Validate total upload size and file count.

    Args:
        files_data: List of tuples containing (content_type, content_string, filename)

    Returns:
        tuple: (is_valid, error_message, total_size_mb)
    """
    if len(files_data) > MAX_FILES_COUNT:
        return (
            False,
            f"Too many files ({len(files_data)}). Maximum allowed: {MAX_FILES_COUNT}",
            0,
        )

    total_size = 0
    for _, content_string, filename in files_data:
        try:
            decoded_size = len(base64.b64decode(content_string))
            total_size += decoded_size
        except Exception as e:
            return False, f"Error processing file '{filename}': {str(e)}", 0

    total_size_mb = total_size / (1024 * 1024)

    if total_size_mb > MAX_TOTAL_FILES_SIZE_MB:
        return (
            False,
            f"Total upload size ({total_size_mb:.1f}MB) exceeds maximum of {MAX_TOTAL_FILES_SIZE_MB}MB",
            total_size_mb,
        )

    return True, None, total_size_mb


# Define marker icon URLs - imported from constants
BLUE_MARKER = MAP_CONFIG.BLUE_MARKER_URL
GREEN_MARKER = MAP_CONFIG.GREEN_MARKER_URL


def transform_coordinates(easting, northing):
    """Transform BNG to WGS84 coordinates using centralized coordinate service"""
    try:
        # Use the centralized coordinate service
        coordinate_service = get_coordinate_service()
        lat, lon = coordinate_service.transform_bng_to_wgs84(easting, northing)

        # Add detailed logging for debugging
        logging.debug(
            f"Coordinate transform: BNG({easting}, {northing}) -> WGS84({lat:.6f}, {lon:.6f})"
        )

        # Validate the transformed coordinates (service already validates, but double-check)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logging.error(f"Invalid transformed coordinates: lat={lat}, lon={lon}")
            return None, None

        return lat, lon
    except Exception as e:
        logging.error(f"Error transforming coordinates BNG({easting}, {northing}): {e}")
        return None, None


def create_selection_shape_visual(feature):
    """Create a visual representation of a drawn selection shape for display"""
    try:
        if not feature or "geometry" not in feature:
            return []

        geometry = feature["geometry"]
        geom_type = geometry.get("type", "")
        coordinates = geometry.get("coordinates", [])

        if not coordinates:
            return []

        if geom_type == "Polygon":
            # Convert coordinates from GeoJSON format [lon, lat] to Leaflet format [lat, lon]
            if coordinates and len(coordinates[0]) > 0:
                polygon_coords = [[lat, lon] for lon, lat in coordinates[0]]
                return [
                    dl.Polygon(
                        positions=polygon_coords,
                        color="#ff7800",
                        fillColor="#ffb347",
                        fillOpacity=0.2,
                        weight=2,
                        opacity=0.8,
                        children=dl.Tooltip("Selected Area"),
                    )
                ]
        elif geom_type == "Rectangle":
            # Rectangle is typically stored as a polygon
            if coordinates and len(coordinates[0]) > 0:
                rect_coords = [[lat, lon] for lon, lat in coordinates[0]]
                return [
                    dl.Polygon(
                        positions=rect_coords,
                        color="#ff7800",
                        fillColor="#ffb347",
                        fillOpacity=0.2,
                        weight=2,
                        opacity=0.8,
                        children=dl.Tooltip("Selected Rectangle"),
                    )
                ]
        # Note: LineString shapes are handled in pca-line-group, not here

        return []
    except Exception as e:
        logging.error(f"Error creating selection shape visual: {e}")
        return []


def register_callbacks(app):
    # Font cache warming callback: triggers on first map pan/zoom after upload
    # Font cache warming callback removed as per user request

    """Register all split callbacks with the app"""

    # ====================================================================
    # CALLBACK 1: FILE UPLOAD HANDLING (Clean & Focused)
    # ====================================================================
    @app.callback(
        [
            Output("output-upload", "children"),
            Output("borehole-markers", "children"),
            Output("borehole-map", "center", allow_duplicate=True),
            Output("borehole-map", "zoom", allow_duplicate=True),
            Output("borehole-data-store", "data"),
            Output(
                "draw-control", "clear_all", allow_duplicate=True
            ),  # Clear shapes on new upload
        ],
        [Input("upload-data-store", "data")],
        [State("borehole-map", "center"), State("borehole-map", "zoom")],
        prevent_initial_call=True,  # Added to fix duplicate callback error
    )
    def handle_file_upload(stored_data, map_center_state, map_zoom_state):
        """Handle file upload and create markers"""
        logging.info("=== FILE UPLOAD CALLBACK ===")

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
                                    f"Error reading {name}: {e}", style={"color": "red"}
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
                            f"📊 Upload Summary:",
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

            # === MEMORY OPTIMIZATION: Monitor and optimize DataFrames ===
            monitor_memory_usage("DEBUG")

            # OPTIMIZATION: Apply borehole-specific DataFrame optimizations
            # Reduces memory usage through categorical conversion and numeric downcasting
            loca_df = optimize_borehole_dataframe(loca_df)
            logging.info(
                f"✓ DataFrame optimized for memory efficiency: {len(loca_df)} rows"
            )

            # --- Hybrid vectorized + fallback approach for coordinate transformation ---
            import numpy as np

            # Use centralized coordinate service for transformation
            coordinate_service = get_coordinate_service()

            # Identify valid numeric rows (avoid defensive copying)
            valid_mask = loca_df["LOCA_NATE"].apply(
                lambda x: pd.notnull(x)
                and str(x).replace(".", "", 1).replace("-", "", 1).isdigit()
            ) & loca_df["LOCA_NATN"].apply(
                lambda x: pd.notnull(x)
                and str(x).replace(".", "", 1).replace("-", "", 1).isdigit()
            )

            # Only copy when necessary for modification
            clean_df = loca_df[valid_mask]
            problem_df = loca_df[~valid_mask]

            # Vectorized transform for clean batch
            lat_arr = np.full(len(loca_df), np.nan)
            lon_arr = np.full(len(loca_df), np.nan)
            if not clean_df.empty:
                bng_x = clean_df["LOCA_NATE"].astype(float).values
                bng_y = clean_df["LOCA_NATN"].astype(float).values
                wgs84_lat, wgs84_lon = coordinate_service.transform_bng_to_wgs84(
                    bng_x, bng_y
                )
                lat_arr[clean_df.index] = wgs84_lat
                lon_arr[clean_df.index] = wgs84_lon

            # Fallback loop for problematic rows
            for i, row in problem_df.iterrows():
                try:
                    easting = float(row["LOCA_NATE"])
                    northing = float(row["LOCA_NATN"])
                    lat, lon = coordinate_service.transform_bng_to_wgs84(
                        easting, northing
                    )
                    lat_arr[i] = lat
                    lon_arr[i] = lon
                except Exception as e:
                    logging.warning(f"Skipping marker for row {i}: {e}")

            # Store transformed coordinates in DataFrame
            loca_df["lat"] = lat_arr
            loca_df["lon"] = lon_arr

            # Create markers
            markers = []
            valid_coords = []
            for i, row in loca_df.iterrows():
                lat = row["lat"]
                lon = row["lon"]
                if pd.notnull(lat) and pd.notnull(lon):
                    label = str(row["LOCA_ID"])
                    marker_id = {"type": "borehole-marker", "index": i}
                    ground_level = row.get("LOCA_GL", "N/A")
                    total_depth = row.get("LOCA_FDEP", "N/A")
                    if (
                        ground_level != "N/A"
                        and ground_level is not None
                        and str(ground_level).strip()
                    ):
                        try:
                            ground_level = f"{float(ground_level):.2f}m"
                        except (ValueError, TypeError):
                            ground_level = "N/A"
                    else:
                        ground_level = "N/A"
                    if (
                        total_depth != "N/A"
                        and total_depth is not None
                        and str(total_depth).strip()
                    ):
                        try:
                            total_depth = f"{float(total_depth):.2f}m"
                        except (ValueError, TypeError):
                            total_depth = "N/A"
                    else:
                        total_depth = "N/A"
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
                    markers.append(
                        dl.Marker(
                            id=marker_id,
                            position=[lat, lon],
                            children=dl.Tooltip(tooltip_text.strip()),
                            icon=marker_icon,
                            n_clicks=0,
                        )
                    )
                    valid_coords.append((lat, lon))
                    if i < 3:
                        logging.info(
                            f"Marker {i} ({label}): BNG({row['LOCA_NATE']}, {row['LOCA_NATN']}) "
                            f"-> Position([{lat:.6f}, {lon:.6f}])"
                        )

            # Auto-zoom to median coordinates for better centering
            if valid_coords:
                lats = [coord[0] for coord in valid_coords]
                lons = [coord[1] for coord in valid_coords]

                # Use median instead of mean for more robust centering
                median_lat = statistics.median(lats)
                median_lon = statistics.median(lons)
                map_center = [median_lat, median_lon]

                # Calculate appropriate zoom level based on coordinate spread
                lat_range = max(lats) - min(lats)
                lon_range = max(lons) - min(lons)
                coord_range = max(lat_range, lon_range)

                # Dynamic zoom based on coordinate spread
                if coord_range > 0.1:
                    map_zoom = 10
                elif coord_range > 0.01:
                    map_zoom = 12
                elif coord_range > 0.001:
                    map_zoom = 14
                else:
                    map_zoom = 16

                logging.info(
                    f"🎯 SETTING MAP CENTER: [{median_lat:.6f}, {median_lon:.6f}] with zoom {map_zoom}"
                )
                logging.info(
                    f"📊 Coordinate analysis: Range={coord_range:.6f}, "
                    f"Bounds: Lat[{min(lats):.6f}, {max(lats):.6f}], Lon[{min(lons):.6f}, {max(lons):.6f}]"
                )
            else:
                logging.warning("No valid coordinates found for map centering")

            # Store data for other callbacks
            borehole_data = {
                "loca_df": loca_df.to_dict("records"),
                "filename_map": filename_map,
                "all_borehole_ids": loca_df["LOCA_ID"].tolist(),
            }

            # Add file breakdown info
            file_breakdown = []
            for filename, content in filename_map.items():
                file_rows = loca_df[loca_df["ags_file"] == filename]
                if len(file_rows) > 0:
                    file_breakdown.append(
                        html.Li([html.B(filename), f" : {len(file_rows)} boreholes"])
                    )

            if file_breakdown:
                file_status.append(
                    html.Div(
                        [
                            html.H4(
                                "File Summary:", style=config.SUCCESS_MESSAGE_STYLE
                            ),
                            html.Ul(file_breakdown),
                        ]
                    )
                )

            # Add detailed status logging for the app UI
            status_info = html.Div(
                [
                    html.H4(
                        "📍 Map Status:",
                        style={"color": "#28a745", "margin-top": "10px"},
                    ),
                    html.P(f"• Loaded {len(markers)} borehole markers"),
                    html.P(
                        f"• Map centered on median coordinates: ({median_lat:.6f}, {median_lon:.6f})"
                    ),
                    html.P(f"• Coordinate range: {coord_range:.6f} degrees"),
                    html.P(f"• Auto-zoom level: {map_zoom}"),
                    html.P(
                        f"• Coordinate bounds: Lat [{min(lats):.6f}, {max(lats):.6f}], Lon [{min(lons):.6f}, {max(lons):.6f}]"
                    ),
                ],
                style={
                    "background-color": "#f8f9fa",
                    "padding": "10px",
                    "border-radius": "5px",
                    "margin-top": "10px",
                },
            )

            file_status.append(status_info)

            # Ensure map center is correct before returning
            logging.info(f"📍 Final map_center: {map_center}, zoom: {map_zoom}")

            # Add additional server-side logging about the map center
            logging.warning(
                f"⚠️ MAP CENTER VERIFICATION: Returning center={map_center}, zoom={map_zoom}. "
                f"If this doesn't match what you see in the UI, check browser console logs."
            )

            # Clear any existing shapes on file upload (timestamp for clear_all)
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
            # Also clear shapes on error
            clear_shapes = datetime.now().timestamp()
            return [error_msg], [], map_center, map_zoom, None, clear_shapes

    # ====================================================================
    # CALLBACK 2: MAP INTERACTIONS (Drawing, PCA, Marker Colors)
    # ====================================================================
    @app.callback(
        [
            Output("pca-line-group", "children"),
            Output("selected-borehole-info", "children"),
            Output("subselection-checkbox-grid-container", "children"),
            Output("ui-feedback", "children"),
            Output("borehole-markers", "children", allow_duplicate=True),
            Output("borehole-data-store", "data", allow_duplicate=True),
            Output("buffer-controls", "style", allow_duplicate=True),
            Output("selection-shapes", "children"),  # Add selection shapes control
        ],
        [
            Input("draw-control", "geojson"),
            Input("subselection-checkbox-grid", "value"),
            Input("update-buffer-btn", "n_clicks"),
        ],
        [
            State("borehole-data-store", "data"),
            State("borehole-markers", "children"),
            State("buffer-input", "value"),
        ],
        prevent_initial_call=True,  # Prevent triggering on initial load
    )
    def handle_map_interactions(
        drawn_geojson,
        checked_ids,
        update_buffer_clicks,
        stored_borehole_data,
        marker_children,
        buffer_value,
    ):
        """Handle map drawing and selection"""
        logging.info("=== MAP INTERACTION CALLBACK ===")

        ctx = dash.callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None
        logging.info(f"Triggered by: {triggered}")

        if not stored_borehole_data:
            logging.warning("No stored borehole data available")
            return (
                [],
                None,
                None,
                None,
                [],
                stored_borehole_data,
                {"display": "none"},
                [],
            )

        # Drawing triggered
        if (
            "draw-control.geojson" in triggered
            and drawn_geojson
            and drawn_geojson.get("features")
        ):
            logging.info(
                "🎨 Processing drawing event - this will clear old polylines and selection shapes"
            )
            return handle_shape_drawing(
                drawn_geojson, stored_borehole_data, marker_children, buffer_value
            )

        # Checkbox selection triggered
        elif "subselection-checkbox-grid.value" in triggered and checked_ids:
            logging.info(
                "☑️ Checkbox selection changed - will clear selection shapes, keep current polyline/PCA"
            )
            return handle_checkbox_selection(checked_ids, stored_borehole_data)

        # Buffer update triggered
        elif (
            "update-buffer-btn.n_clicks" in triggered
            and update_buffer_clicks
            and stored_borehole_data.get("last_polyline")
        ):
            logging.info(
                f"📏 Updating buffer to {buffer_value}m - will update polyline and clear selection shapes"
            )

            # Get the polyline coordinates and original DataFrame
            polyline_coords = stored_borehole_data.get("last_polyline")
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

            # Re-filter boreholes with new buffer distance
            filtered_boreholes_df = project_boreholes_to_polyline(
                loca_df, polyline_coords, buffer_value
            )
            new_borehole_ids = (
                filtered_boreholes_df["LOCA_ID"].tolist()
                if not filtered_boreholes_df.empty
                else []
            )

            # Update the buffer in the data store
            new_data = dict(stored_borehole_data)
            new_data["buffer_meters"] = buffer_value
            new_data["selection_boreholes"] = new_borehole_ids

            # Create new section line with buffer
            section_line = create_polyline_section(polyline_coords)
            buffer_zone = create_buffer_visualization(polyline_coords, buffer_value)

            # Flatten the components into a proper list
            line_group = []
            if isinstance(section_line, list):
                line_group.extend(section_line)
            elif section_line:
                line_group.append(section_line)

            if buffer_zone:
                line_group.append(buffer_zone)

            # Update marker colors for new selection
            updated_markers = update_marker_colors(
                stored_borehole_data, new_borehole_ids
            )

            # Create new checkbox grid
            checkbox_grid = create_checkbox_grid(new_borehole_ids, new_borehole_ids)

            # Re-filter the boreholes based on the new buffer
            return (
                line_group,
                None,
                checkbox_grid,
                html.Div(
                    f"Updated buffer to {buffer_value}m - {len(new_borehole_ids)} boreholes selected"
                ),
                updated_markers,
                new_data,
                {"display": "block"},
                [],  # Clear selection shapes when updating buffer
            )

        return [], None, None, None, [], stored_borehole_data, {"display": "none"}, []

    def handle_shape_drawing(
        drawn_geojson,
        stored_borehole_data,
        marker_children,
        buffer_value=MAP_CONFIG.DEFAULT_BUFFER_METERS,
    ):
        """Handle shape drawing and borehole selection"""
        try:
            # Log detailed GeoJSON information
            logging.info("=== DETAILED SHAPE DRAWING DIAGNOSTICS ===")
            logging.info(f"GeoJSON type: {type(drawn_geojson)}")
            if isinstance(drawn_geojson, dict):
                logging.info(f"GeoJSON keys: {list(drawn_geojson.keys())}")
                logging.info(
                    f"Features count: {len(drawn_geojson.get('features', []))}"
                )
                for i, feature in enumerate(drawn_geojson.get("features", [])):
                    logging.info(
                        f"Feature {i} type: {feature.get('geometry', {}).get('type')}"
                    )
                    if "properties" in feature:
                        logging.info(
                            f"Feature {i} properties: {feature.get('properties')}"
                        )

            # Reconstruct DataFrame
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            logging.info(f"Processing shape with {len(loca_df)} boreholes")

            # Get the features
            features = drawn_geojson.get("features", [])
            if not features:
                logging.warning("No features found in drawn GeoJSON")
                return [], None, None, html.Div("No valid shapes found")

            # Get only the most recent feature and log its details
            selected_feature = features[-1]  # Always use last drawn shape
            geom_type = selected_feature.get("geometry", {}).get("type", "unknown")
            logging.info(f"Processing most recent shape: {geom_type}")
            logging.info(f"Selected feature details: {selected_feature}")

            # Create a GeoJSON with only the selected feature
            single_feature_geojson = {
                "type": "FeatureCollection",
                "features": [selected_feature],
            }
            logging.info("Created clean GeoJSON with single feature")

            # Filter by the selected shape
            if geom_type == "LineString":
                # For polylines, skip the general filter and use the polyline-specific function
                logging.info("=== POLYLINE FILTERING DEBUG ===")
                logging.info("Using polyline-specific filtering for LineString")

                # Extract polyline coordinates
                if (
                    isinstance(selected_feature, dict)
                    and "geometry" in selected_feature
                ):
                    coordinates = selected_feature["geometry"]["coordinates"]
                    polyline_coords = [[lat, lon] for lon, lat in coordinates]
                    logging.info(f"Extracted polyline coordinates: {polyline_coords}")
                else:
                    polyline_coords = []
                    logging.warning("Failed to extract polyline coordinates")

                # Use the buffer value
                buffer_meters = buffer_value or stored_borehole_data.get(
                    "buffer_meters", MAP_CONFIG.DEFAULT_BUFFER_METERS
                )
                logging.info(f"Using buffer distance: {buffer_meters}m")

                # Debug the input DataFrame
                logging.info(f"Input DataFrame shape: {loca_df.shape}")
                logging.info(f"DataFrame columns: {list(loca_df.columns)}")

                # Log first few rows for debugging
                if len(loca_df) > 0:
                    logging.info("First few boreholes in DataFrame:")
                    for i in range(min(3, len(loca_df))):
                        row = loca_df.iloc[i]
                        logging.info(
                            f"  {row.get('LOCA_ID', 'unknown')}: "
                            f"lat={row.get('lat', 'missing')}, lon={row.get('lon', 'missing')}, "
                            f"LOCA_LAT={row.get('LOCA_LAT', 'missing')}, LOCA_LON={row.get('LOCA_LON', 'missing')}"
                        )

                # Project and filter boreholes using the polyline and buffer
                filtered_boreholes_df = project_boreholes_to_polyline(
                    loca_df, polyline_coords, buffer_meters
                )

                # Get borehole IDs from the filtered result
                borehole_ids = (
                    filtered_boreholes_df["LOCA_ID"].tolist()
                    if not filtered_boreholes_df.empty
                    else []
                )

                logging.info(
                    f"Polyline filter result: {len(borehole_ids)} boreholes selected"
                )
                logging.info(f"Selected borehole IDs: {borehole_ids}")
                logging.info("=== END POLYLINE FILTERING DEBUG ===")
            else:
                # For other shapes, use the general filter
                filtered_result = filter_selection_by_shape(
                    loca_df, single_feature_geojson
                )
                logging.info(
                    f"filter_selection_by_shape returned: {type(filtered_result)}"
                )

                # Handle both DataFrame and list return types
                borehole_ids = []
                if isinstance(filtered_result, pd.DataFrame):
                    if not filtered_result.empty:
                        borehole_ids = filtered_result["LOCA_ID"].tolist()
                        logging.info(
                            f"Extracted {len(borehole_ids)} LOCA_IDs from DataFrame"
                        )
                elif isinstance(filtered_result, list):
                    borehole_ids = filtered_result
                    logging.info(
                        f"Got {len(borehole_ids)} LOCA_IDs directly from filter"
                    )
                else:
                    logging.warning(f"Unexpected return type: {type(filtered_result)}")

            if borehole_ids:
                logging.info(f"Selected {len(borehole_ids)} boreholes: {borehole_ids}")

                # Different handling for polylines vs other shapes
                if geom_type == "LineString":
                    # For polylines, create the section line and buffer zone
                    section_line = create_polyline_section(
                        selected_feature, stored_borehole_data
                    )
                    buffer_zone = create_buffer_zone(selected_feature, buffer_meters)
                    # Store polyline data for buffer updates
                    data_with_selection = dict(stored_borehole_data)
                    data_with_selection["selection_boreholes"] = borehole_ids
                    data_with_selection["polyline_feature"] = selected_feature
                    data_with_selection["last_polyline"] = polyline_coords
                    data_with_selection["is_polyline"] = True
                    data_with_selection["buffer_meters"] = buffer_meters
                    # Combine section line and buffer zone safely
                    line_elements = []
                    if isinstance(section_line, list):
                        line_elements.extend(section_line)
                    elif section_line:
                        line_elements.append(section_line)

                    if isinstance(buffer_zone, list):
                        line_elements.extend(buffer_zone)
                    elif buffer_zone:
                        line_elements.append(buffer_zone)
                else:
                    # For other shapes, use PCA line (original behavior)
                    if isinstance(filtered_result, pd.DataFrame):
                        line_elements = calculate_pca_line(filtered_result)
                    else:
                        # If we got a list, filter the original DataFrame
                        filtered_df = loca_df[loca_df["LOCA_ID"].isin(borehole_ids)]
                        line_elements = calculate_pca_line(filtered_df)

                    # Store data without polyline info
                    data_with_selection = dict(stored_borehole_data)
                    data_with_selection["selection_boreholes"] = borehole_ids
                    data_with_selection["is_polyline"] = False

                logging.info(f"Created {len(line_elements)} line elements")

                # Create checkbox grid
                checkbox_grid = create_checkbox_grid(borehole_ids, borehole_ids)

                # Update the global data store (this will be picked up by other callbacks)
                stored_borehole_data = data_with_selection

                logging.info(
                    f"About to update marker colors with {len(borehole_ids)} selected IDs"
                )

                # Update marker colors based on selection
                updated_markers = update_marker_colors(
                    stored_borehole_data, borehole_ids
                )

                logging.info(
                    f"Marker update complete, returning {len(updated_markers)} markers"
                )

                # Create detailed feedback message with status info
                total_boreholes = len(stored_borehole_data.get("all_borehole_ids", []))
                blue_markers = total_boreholes - len(borehole_ids)

                line_type = (
                    "Polyline section" if geom_type == "LineString" else "PCA line"
                )

                feedback_content = [
                    html.H4(
                        "🎯 Selection Status:",
                        style={"color": "#28a745", "margin-bottom": "5px"},
                    ),
                    html.P(
                        f"• Selected {len(borehole_ids)} boreholes from {geom_type}"
                    ),
                    html.P(f"• Borehole IDs: {', '.join(borehole_ids)}"),
                    html.P(f"• {line_type} created: {len(line_elements) > 0}"),
                    html.P(
                        f"• Markers updated: {len(borehole_ids)} green, {blue_markers} blue"
                    ),
                ]

                # Add polyline distance info if available
                if geom_type == "LineString":
                    distance_info = add_polyline_distance_info(
                        borehole_ids, stored_borehole_data
                    )
                    if distance_info:
                        feedback_content.append(html.Hr())
                        feedback_content.append(html.H5("Distance along polyline:"))
                        for dist_info in distance_info:
                            feedback_content.append(html.P(f"• {dist_info}"))

                feedback = html.Div(
                    feedback_content,
                    style={
                        "background-color": "#d4edda",
                        "padding": "10px",
                        "border-radius": "5px",
                        "border": "1px solid #c3e6cb",
                    },
                )

                logging.info("Shape drawing complete - returning results")
                logging.info(
                    f"Line elements: {len(line_elements)}, Markers: {len(updated_markers)}"
                )
                logging.info(
                    "🧹 CLEARING OLD SHAPES: Replacing pca-line-group and selection-shapes with new content"
                )

                # Create visual representation of the selection shape
                selection_shapes = []
                if geom_type != "LineString":  # For polygons, rectangles, etc.
                    selection_shapes = create_selection_shape_visual(selected_feature)
                    logging.info(f"📋 Created selection shape visual for {geom_type}")
                else:
                    logging.info(
                        "📏 Polyline detected - selection shapes will be cleared, line goes to pca-line-group"
                    )

                return (
                    line_elements,
                    None,
                    checkbox_grid,
                    feedback,
                    updated_markers,
                    data_with_selection,
                    (
                        {"display": "block"}
                        if geom_type == "LineString"
                        else {"display": "none"}
                    ),
                    selection_shapes,  # Add selection shapes visualization
                )
            else:
                feedback = html.Div(
                    "No boreholes found in selection",
                    style=config.WARNING_MESSAGE_STYLE,
                )
                # Return markers with all blue (no selection)
                updated_markers = update_marker_colors(stored_borehole_data, [])
                return (
                    [],
                    None,
                    None,
                    feedback,
                    updated_markers,
                    stored_borehole_data,  # Unchanged data store
                    {"display": "none"},
                    [],  # No selection shapes when no boreholes found
                )

        except Exception as e:
            logging.error(f"Error in shape drawing: {e}")
            error_msg = html.Div(
                f"Selection error: {e}", style=config.ERROR_MESSAGE_STYLE
            )
            # Return markers with all blue (no selection) on error
            updated_markers = update_marker_colors(stored_borehole_data, [])
            return (
                [],
                None,
                None,
                error_msg,
                updated_markers,
                stored_borehole_data,  # Unchanged data store
                {"display": "none"},
                [],  # No selection shapes on error
            )

    def handle_checkbox_selection(checked_ids, stored_borehole_data):
        """Handle checkbox selection changes"""
        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

            # We need to use the current checkbox options rather than all boreholes
            # Get the shape-selected boreholes from stored data
            if "selection_boreholes" in stored_borehole_data:
                # Use the stored selection from shape drawing
                shape_selected_ids = stored_borehole_data["selection_boreholes"]
            else:
                # Fallback - use the checked IDs as a guide (not ideal but safer than all boreholes)
                shape_selected_ids = checked_ids

            # Filter to only the checked boreholes
            filtered_df = loca_df[loca_df["LOCA_ID"].isin(checked_ids)]

            # Create the section line based on the method used
            if "last_polyline" in stored_borehole_data:
                # If we have a polyline, use it
                polyline_coords = stored_borehole_data["last_polyline"]
                buffer_meters = stored_borehole_data.get(
                    "buffer_meters", MAP_CONFIG.DEFAULT_BUFFER_METERS
                )

                # Create section line and buffer visualization
                section_line = create_polyline_section(polyline_coords)
                buffer_zone = create_buffer_visualization(
                    polyline_coords, buffer_meters
                )

                # Safely combine section line and buffer zone
                section_lines = []
                if isinstance(section_line, list):
                    section_lines.extend(section_line)
                elif section_line:
                    section_lines.append(section_line)

                if isinstance(buffer_zone, list):
                    section_lines.extend(buffer_zone)
                elif buffer_zone:
                    section_lines.append(buffer_zone)

                # Show buffer controls
                buffer_controls_style = {"display": "block"}
            else:
                # Use PCA if no polyline
                section_lines = calculate_pca_line(filtered_df)
                buffer_controls_style = {"display": "none"}

            # Create checkbox grid with only the shape-selected boreholes
            checkbox_grid = create_checkbox_grid(shape_selected_ids, checked_ids)

            feedback = html.Div(f"Using {len(checked_ids)} selected boreholes")

            # Update marker colors based on checkbox selection
            updated_markers = update_marker_colors(stored_borehole_data, checked_ids)

            return (
                section_lines,
                None,
                checkbox_grid,
                feedback,
                updated_markers,
                stored_borehole_data,
                buffer_controls_style,
                [],  # Keep selection shapes empty for checkbox selections
            )

        except Exception as e:
            logging.error(f"Error in checkbox selection: {e}")
            # Return markers with all blue (no selection) on error
            updated_markers = update_marker_colors(stored_borehole_data, [])
            return (
                [],
                None,
                None,
                None,
                updated_markers,
                stored_borehole_data,
                {"display": "none"},
                [],  # No selection shapes on error
            )

    def calculate_pca_line(filtered_df):
        """Calculate and create PCA line for display - extended past markers"""
        if len(filtered_df) < 2:
            logging.info("Less than 2 points for PCA line calculation")
            return []

        try:
            # Use BNG coordinates for PCA (as in original Streamlit)
            bng_coords = filtered_df[["LOCA_NATE", "LOCA_NATN"]].values
            logging.info(f"Calculating PCA line for {len(bng_coords)} points")

            pca = PCA(n_components=2)
            pca_coords = pca.fit_transform(bng_coords)
            mean_coords = bng_coords.mean(axis=0)
            direction = pca.components_[0]

            # Calculate line extent - EXTENDED further past markers
            length = max(pca_coords[:, 0]) - min(pca_coords[:, 0])
            # Increased buffer from 0.2 to 1.0 to extend line much further
            buffer = 1.0 * length

            logging.info(f"PCA line length: {length:.2f}, buffer: {buffer:.2f}")

            # Calculate start and end points in BNG - extended much further
            start_bng = mean_coords + direction * (-length / 2 - buffer)
            end_bng = mean_coords + direction * (length / 2 + buffer)

            logging.info(
                f"PCA line BNG: start({start_bng[0]:.2f}, {start_bng[1]:.2f}) "
                f"to end({end_bng[0]:.2f}, {end_bng[1]:.2f})"
            )

            # OPTIMIZATION: Batch transform coordinates for PCA line endpoints
            # Transform both start and end coordinates at once instead of individually
            eastings = [start_bng[0], end_bng[0]]
            northings = [start_bng[1], end_bng[1]]
            coord_service = get_coordinate_service()
            lats, lons = coord_service.transform_bng_to_wgs84(eastings, northings)
            start_lat, start_lon = lats[0], lons[0]
            end_lat, end_lon = lats[1], lons[1]

            if start_lat and start_lon and end_lat and end_lon:
                logging.info(
                    f"PCA line WGS84: start({start_lat:.6f}, {start_lon:.6f}) to end({end_lat:.6f}, {end_lon:.6f})"
                )
                return [
                    dl.Polyline(
                        positions=[[start_lat, start_lon], [end_lat, end_lon]],
                        color="red",
                        weight=3,
                        opacity=0.8,
                        dashArray="5, 5",
                        children=dl.Tooltip("Extended PCA section line"),
                    )
                ]

        except Exception as e:
            logging.error(f"Error calculating PCA line: {e}")

        return []

    def create_checkbox_grid(borehole_ids, current_checked):
        """Create checkbox grid for borehole selection"""
        if not borehole_ids:
            # Return empty grid if no boreholes selected
            logging.warning("No borehole IDs provided for checkbox grid")
            return html.Div(
                [
                    html.H4("No boreholes selected", style=config.HEADER_H4_LEFT_STYLE),
                    html.P(
                        "Please select boreholes on the map",
                        style=config.DESCRIPTION_TEXT_STYLE,
                    ),
                ]
            )

        # Ensure current_checked contains only valid IDs
        valid_checked = [bh_id for bh_id in current_checked if bh_id in borehole_ids]

        return html.Div(
            [
                html.H4(
                    config.CHECKBOX_SECTION_TITLE, style=config.HEADER_H4_LEFT_STYLE
                ),
                html.P(
                    config.CHECKBOX_INSTRUCTIONS, style=config.DESCRIPTION_TEXT_STYLE
                ),
                dcc.Checklist(
                    id="subselection-checkbox-grid",
                    options=[
                        {"label": f" {bh_id}", "value": bh_id} for bh_id in borehole_ids
                    ],
                    value=valid_checked,
                    labelStyle=config.CHECKBOX_LABEL_STYLE,
                    style=config.CHECKBOX_LEFT_STYLE,
                ),
            ]
        )

    def update_marker_colors(stored_borehole_data, selected_ids):
        """Update marker colors based on selection - green for selected, blue for unselected"""
        logging.info("=== UPDATE MARKER COLORS DEBUG ===")
        logging.info(f"Selected IDs input: {selected_ids}")
        logging.info(
            f"Number of selected IDs: {len(selected_ids) if selected_ids else 0}"
        )

        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            markers = []

            logging.info(f"Total boreholes in DataFrame: {len(loca_df)}")

            for i, row in loca_df.iterrows():
                try:
                    lat = row.get("lat")
                    lon = row.get("lon")
                    loca_id = str(row["LOCA_ID"])

                    if lat and lon:
                        # Determine marker color based on selection
                        is_selected = loca_id in (selected_ids or [])
                        icon_url = GREEN_MARKER if is_selected else BLUE_MARKER

                        # Log first few markers for debugging
                        if i < 5:
                            color = "green" if is_selected else "blue"
                            logging.info(
                                f"Marker {i} ({loca_id}): selected={is_selected}, color={color}"
                            )

                        # Create marker with appropriate color
                        marker_id = {"type": "borehole-marker", "index": i}

                        # Get additional information for tooltip
                        ground_level = row.get("LOCA_GL", "N/A")
                        total_depth = row.get("LOCA_FDEP", "N/A")

                        # Format ground level and total depth
                        if (
                            ground_level != "N/A"
                            and ground_level is not None
                            and str(ground_level).strip()
                        ):
                            try:
                                ground_level = f"{float(ground_level):.2f}m"
                            except (ValueError, TypeError):
                                ground_level = "N/A"
                        else:
                            ground_level = "N/A"

                        if (
                            total_depth != "N/A"
                            and total_depth is not None
                            and str(total_depth).strip()
                        ):
                            try:
                                total_depth = f"{float(total_depth):.2f}m"
                            except (ValueError, TypeError):
                                total_depth = "N/A"
                        else:
                            total_depth = "N/A"

                        # Create detailed tooltip
                        tooltip_text = f"""
                        Borehole: {loca_id}
                        Ground Level: {ground_level}
                        Total Depth: {total_depth}
                        Click to view borehole log
                        """

                        marker_icon = {
                            "iconUrl": icon_url,
                            "iconSize": [25, 41],
                            "iconAnchor": [12, 41],
                            "popupAnchor": [1, -34],
                            "shadowSize": [41, 41],
                        }

                        markers.append(
                            dl.Marker(
                                id=marker_id,
                                position=[lat, lon],
                                children=dl.Tooltip(tooltip_text.strip()),
                                icon=marker_icon,
                                n_clicks=0,
                            )
                        )

                except Exception as e:
                    logging.warning(f"Error creating marker for row {i}: {e}")

            green_count = len([m for m in markers if "green" in str(m.icon["iconUrl"])])
            blue_count = len(markers) - green_count

            logging.info(
                f"Updated {len(markers)} markers: {green_count} green, {blue_count} blue"
            )
            logging.info("=== END UPDATE MARKER COLORS DEBUG ===")
            return markers

        except Exception as e:
            logging.error(f"Error updating marker colors: {e}")
            return []

    # ====================================================================
    # CALLBACK 3: PLOT GENERATION (Section Plots & Downloads)
    # ====================================================================
    @app.callback(
        [
            Output("section-plot-output", "children", allow_duplicate=True),
            Output("log-plot-output", "children"),
            Output("download-section-plot", "data"),
        ],
        [
            Input("subselection-checkbox-grid", "value"),
            Input("show-labels-checkbox", "value"),
            Input("download-section-btn", "n_clicks"),
        ],
        [
            State("borehole-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_plot_generation(
        checked_ids, show_labels_value, download_clicks, stored_borehole_data
    ):
        """Handle plot generation and downloads"""
        logging.info("=== PLOT GENERATION CALLBACK ===")
        logging.info(f"Triggered by: {dash.callback_context.triggered}")

        ctx = dash.callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None

        if not stored_borehole_data or not checked_ids:
            return None, None, None

        show_labels = "show_labels" in (show_labels_value or [])

        try:
            # Get AGS content
            filename_map = stored_borehole_data["filename_map"]
            combined_content = ""
            for filename, content in filename_map.items():
                combined_content += content + "\n"

            # Generate section plot with polyline data if available
            section_line = None
            if "last_polyline" in stored_borehole_data:
                # Convert polyline coordinates to format expected by section_plot
                polyline_coords = stored_borehole_data["last_polyline"]

                # Convert polyline from geographic coordinates (lat/lon) to projected coordinates (easting/northing)
                # to match the coordinate system used by LOCA_NATE/LOCA_NATN in the borehole data
                try:
                    # Use coordinate service for UTM transformation
                    coordinate_service = get_coordinate_service()

                    # Extract lat/lon coordinates for transformation
                    lats, lons = zip(*[(lat, lon) for lat, lon in polyline_coords])

                    # Transform to UTM using coordinate service
                    utm_x, utm_y, utm_crs = coordinate_service.transform_wgs84_to_utm(
                        lons, lats
                    )

                    # Create section line as (easting, northing) pairs
                    section_line = list(zip(utm_x, utm_y))

                    logging.info(
                        f"Using polyline section with {len(section_line)} points"
                    )
                    logging.info(f"Polyline coords (lat/lon): {polyline_coords[:2]}...")
                    logging.info(
                        f"Section line coords (UTM {utm_crs}): {section_line[:2]}..."
                    )

                except Exception as e:
                    logging.error(f"Error converting polyline coordinates: {e}")
                    # Fallback to original method if conversion fails
                    section_line = [(lon, lat) for lat, lon in polyline_coords]
                    logging.info(
                        f"Using fallback polyline section with {len(section_line)} points"
                    )

            fig_or_b64 = plot_section_from_ags_content(
                combined_content,
                checked_ids,
                section_line=section_line,
                show_labels=show_labels,
            )

            # Minimal, careful handling: support both base64 string and Figure
            if isinstance(fig_or_b64, str):
                # Accept both raw base64 and full data URI
                if fig_or_b64.startswith("iVBORw0KGgo"):
                    img_src = f"data:image/png;base64,{fig_or_b64}"
                elif fig_or_b64.startswith("data:image/png;base64,"):
                    img_src = fig_or_b64
                else:
                    return None, None, None
                centered_img_style = {
                    "display": "block",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                    "maxWidth": "100%",
                    "height": "auto",
                    "maxHeight": "80vh",
                    "objectFit": "contain",
                }
                section_plot = html.Img(src=img_src, style=centered_img_style)
                # For download, decode if needed
                if img_src.startswith("data:image/png;base64,"):
                    img_bytes = base64.b64decode(img_src.split(",", 1)[1])
                else:
                    img_bytes = base64.b64decode(img_src)
                download_data = None
                if "download-section-btn.n_clicks" in triggered and download_clicks:
                    download_data = dcc.send_bytes(img_bytes, "section_plot.png")
                return section_plot, None, download_data
            elif hasattr(fig_or_b64, "savefig"):
                try:
                    buf = io.BytesIO()
                    fig_or_b64.savefig(
                        buf,
                        format="png",
                        bbox_inches="tight",
                        dpi=PLOT_CONFIG.PREVIEW_DPI,
                    )
                    buf.seek(0)
                    img_bytes = buf.read()
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    centered_img_style = {
                        "display": "block",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                        "maxWidth": "100%",
                        "height": "auto",
                        "maxHeight": "80vh",
                        "objectFit": "contain",
                    }
                    section_plot = html.Img(
                        src=f"data:image/png;base64,{img_b64}",
                        style=centered_img_style,
                    )
                    download_data = None
                    if "download-section-btn.n_clicks" in triggered and download_clicks:
                        download_data = dcc.send_bytes(img_bytes, "section_plot.png")
                    return section_plot, None, download_data
                finally:
                    plt.close(fig_or_b64)
            else:
                return None, None, None

        except Exception as e:
            logging.error(f"Error generating plot: {e}")
            return None, None, None

    # Add a callback to explicitly clear shapes
    @app.callback(
        Output("draw-control", "clear_all", allow_duplicate=True),
        Input("draw-control", "geojson"),
        prevent_initial_call=True,
    )
    def clear_all_shapes(geojson):
        """Force clearing all shapes when a new shape is drawn"""
        if geojson and geojson.get("features") and len(geojson.get("features")) > 0:
            logging.info(
                f"Server-side clearing all shapes. Features: {len(geojson.get('features'))}"
            )
            # Return the current timestamp to trigger the clear_all action
            return datetime.now().timestamp()
        return dash.no_update

    # Add a client-side callback to force map to update view on initial load only
    # This callback has been modified to not disrupt user zoom/pan interactions
    app.clientside_callback(
        """
        function(data_store) {
            // Only execute if we have data and it's a fresh load (from file upload)
            if (data_store && data_store.hasOwnProperty('loca_df')) {
                console.log('File upload detected - checking if map needs updating');
                
                // Force Leaflet map to update by accessing the internal map instance
                const mapDiv = document.getElementById('borehole-map');
                
                if (mapDiv && mapDiv._leaflet_map) {
                    console.log('Found map div:', mapDiv.id);
                    
                    // Log current map state
                    const currentCenter = mapDiv._leaflet_map.getCenter();
                    const currentZoom = mapDiv._leaflet_map.getZoom();
                    console.log('Current map center:', [currentCenter.lat, currentCenter.lng], 'Current zoom:', currentZoom);
                    
                    // Let the map's internal mechanisms handle centering based on the data
                    // We're no longer forcing any setView() here to avoid disrupting user interactions
                    mapDiv._leaflet_map.invalidateSize();
                    console.log('Map updated for file upload');
                }
            }
            // This is a dummy output that doesn't change anything
            return window.dash_clientside.no_update;
        }
        """,
        # Use a placeholder output for the clientside callback
        Output("ui-feedback", "children", allow_duplicate=True),
        [Input("borehole-data-store", "data")],
        prevent_initial_call=True,
    )

    # ====================================================================
    # BOREHOLE SEARCH CALLBACKS
    # ====================================================================

    @app.callback(
        Output("borehole-search-dropdown", "options"),
        Output("borehole-search-dropdown", "value"),
        Input("borehole-data-store", "data"),
        prevent_initial_call=True,
    )
    def update_search_dropdown(stored_borehole_data):
        """Update search dropdown options when borehole data is loaded"""
        logging.info("=== UPDATING SEARCH DROPDOWN ===")

        if not stored_borehole_data:
            logging.info("No borehole data available for search")
            return [], None

        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

            if loca_df.empty:
                logging.info("Empty borehole dataframe")
                return [], None

            # Create options for dropdown
            options = []
            for i, row in loca_df.iterrows():
                borehole_id = str(row["LOCA_ID"]).strip()
                ground_level = row.get("LOCA_GL", "N/A")
                total_depth = row.get("LOCA_FDEP", "N/A")

                # Format additional info for display
                info_parts = []
                if (
                    ground_level != "N/A"
                    and ground_level is not None
                    and str(ground_level).strip()
                ):
                    try:
                        gl_val = float(ground_level)
                        info_parts.append(f"GL: {gl_val:.2f}m")
                    except (ValueError, TypeError):
                        pass

                if (
                    total_depth != "N/A"
                    and total_depth is not None
                    and str(total_depth).strip()
                ):
                    try:
                        td_val = float(total_depth)
                        info_parts.append(f"Depth: {td_val:.2f}m")
                    except (ValueError, TypeError):
                        pass

                info_str = f" ({', '.join(info_parts)})" if info_parts else ""

                options.append(
                    {
                        "label": f"{borehole_id}{info_str}",
                        "value": i,  # Use the DataFrame index as the value
                        "search": borehole_id.lower(),  # For case-insensitive search
                    }
                )

            # Sort options alphabetically by borehole ID
            options.sort(key=lambda x: x["label"])

            logging.info(f"Created {len(options)} search options")
            return options, None

        except Exception as e:
            logging.error(f"Error updating search dropdown: {e}")
            return [], None

    @app.callback(
        Output("search-go-btn", "disabled"),
        Output("search-go-btn", "children"),
        Input("borehole-search-dropdown", "value"),
    )
    def toggle_search_button(selected_value):
        """Enable/disable the search button based on dropdown selection"""
        if selected_value is None:
            return True, "Go to Borehole"
        else:
            return False, "🔍 Go to Borehole"

    @app.callback(
        [
            Output("search-feedback", "children"),
            Output("log-plot-output", "children", allow_duplicate=True),
            Output("borehole-markers", "children", allow_duplicate=True),
            Output("borehole-map", "center", allow_duplicate=True),
            Output("borehole-map", "zoom", allow_duplicate=True),
            Output("borehole-search-dropdown", "value", allow_duplicate=True),
        ],
        Input("search-go-btn", "n_clicks"),
        [
            State("borehole-search-dropdown", "value"),
            State("borehole-data-store", "data"),
            State("show-labels-checkbox", "value"),
            State("borehole-markers", "children"),
        ],
        prevent_initial_call=True,
    )
    def handle_search_go(
        n_clicks,
        selected_borehole_index,
        stored_borehole_data,
        show_labels_value,
        current_markers,
    ):
        """Handle the 'Go to Borehole' button click"""
        logging.info("=== SEARCH GO BUTTON CLICKED ===")

        if not n_clicks or n_clicks == 0:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        if selected_borehole_index is None:
            feedback = html.Div(
                "Please select a borehole from the dropdown.",
                style={"color": "orange", "fontWeight": "bold"},
            )
            return (
                feedback,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        if not stored_borehole_data:
            feedback = html.Div(
                "No borehole data available. Please upload AGS files first.",
                style={"color": "red", "fontWeight": "bold"},
            )
            return (
                feedback,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

            if selected_borehole_index >= len(loca_df):
                feedback = html.Div(
                    "Invalid borehole selection.",
                    style={"color": "red", "fontWeight": "bold"},
                )
                return (
                    feedback,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                )

            # Get the selected borehole
            selected_borehole = loca_df.iloc[selected_borehole_index]
            borehole_id = selected_borehole["LOCA_ID"]
            lat = selected_borehole.get("lat")
            lon = selected_borehole.get("lon")

            logging.info(f"Processing search for borehole: {borehole_id}")

            # Generate borehole log
            filename_map = stored_borehole_data["filename_map"]
            combined_content = ""
            for filename, content in filename_map.items():
                combined_content += content + "\n"

            show_labels = "show_labels" in (show_labels_value or [])

            images = plot_borehole_log_from_ags_content(
                combined_content,
                borehole_id,
                show_labels=show_labels,
                fig_height=11.69,  # A4 height
                fig_width=8.27,  # A4 width,
            )

            # Handle error from log plotting (e.g., excessive depth)
            log_output = None
            if isinstance(images, dict) and "error" in images:
                log_output = html.Div(
                    [
                        html.H3(
                            f"Borehole Log: {borehole_id}",
                            style=config.HEADER_H4_CENTER_STYLE,
                        ),
                        html.P(
                            images["error"],
                            style={
                                "color": "red",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                        ),
                    ]
                )
            elif images and len(images) > 0:
                preserved_aspect_style = {
                    "width": "66vw",
                    "height": "auto",
                    "display": "block",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                    "margin-bottom": "20px",
                    "objectFit": "contain",
                }

                if len(images) == 1:
                    log_output = html.Div(
                        [
                            html.H3(
                                f"Borehole Log: {borehole_id}",
                                style=config.HEADER_H4_CENTER_STYLE,
                            ),
                            html.Img(
                                src=f"data:image/png;base64,{images[0]}",
                                style=preserved_aspect_style,
                            ),
                        ]
                    )
                else:
                    image_elements = [
                        html.H3(
                            f"Borehole Log: {borehole_id}",
                            style=config.HEADER_H4_CENTER_STYLE,
                        )
                    ]
                    for i, img in enumerate(images):
                        if i > 0:
                            image_elements.append(
                                html.H4(
                                    f"Page {i+1} of {len(images)}",
                                    style=config.HEADER_H4_CENTER_STYLE,
                                )
                            )
                        image_elements.append(
                            html.Img(
                                src=f"data:image/png;base64,{img}",
                                style=preserved_aspect_style,
                            )
                        )
                    log_output = html.Div(image_elements)
            else:
                log_output = html.Div(
                    [
                        html.H3(
                            f"Borehole Log: {borehole_id}",
                            style=config.HEADER_H4_CENTER_STYLE,
                        ),
                        html.P(
                            "No geological data found for this borehole.",
                            style={"textAlign": "center", "color": "orange"},
                        ),
                    ]
                )

            # Update markers to highlight the selected one
            updated_markers = []
            if current_markers:
                for i, marker in enumerate(current_markers):
                    # Create new marker with updated icon
                    if i == selected_borehole_index:
                        # Highlight selected marker with green color
                        new_icon = {
                            "iconUrl": GREEN_MARKER,
                            "iconSize": [25, 41],
                            "iconAnchor": [12, 41],
                            "popupAnchor": [1, -34],
                            "shadowSize": [41, 41],
                        }
                    else:
                        # Reset other markers to blue
                        new_icon = {
                            "iconUrl": BLUE_MARKER,
                            "iconSize": [25, 41],
                            "iconAnchor": [12, 41],
                            "popupAnchor": [1, -34],
                            "shadowSize": [41, 41],
                        }

                    # Create new marker with updated icon
                    if (
                        hasattr(marker, "id")
                        and hasattr(marker, "position")
                        and hasattr(marker, "children")
                    ):
                        updated_marker = dl.Marker(
                            id=marker.id,
                            position=marker.position,
                            children=marker.children,
                            icon=new_icon,
                            n_clicks=getattr(marker, "n_clicks", 0),
                        )
                        updated_markers.append(updated_marker)
                    else:
                        # Fallback for any unexpected marker format
                        updated_markers.append(marker)
            else:
                updated_markers = current_markers

            # Update map center and zoom
            new_center = (
                [lat, lon] if lat is not None and lon is not None else dash.no_update
            )
            new_zoom = 16 if lat is not None and lon is not None else dash.no_update

            # Success feedback with auto-clear instruction
            feedback = html.Div(
                [
                    html.Span("✓ ", style={"fontSize": "16px", "marginRight": "5px"}),
                    html.Span(
                        f"Successfully found and centered on borehole: {borehole_id}"
                    ),
                ],
                style={"color": "green", "fontWeight": "bold"},
            )

            # Reset dropdown selection for next search
            return feedback, log_output, updated_markers, new_center, new_zoom, None

        except Exception as e:
            logging.error(f"Error handling search: {e}")
            feedback = html.Div(
                f"Error processing borehole search: {str(e)}",
                style={"color": "red", "fontWeight": "bold"},
            )
            return (
                feedback,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

    # Add keyboard shortcut support (Enter key to trigger search)
    app.clientside_callback(
        """
        function(dropdown_value, n_clicks) {
            // Listen for Enter key on the search dropdown
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    const searchDropdown = document.querySelector('#borehole-search-dropdown input');
                    const searchButton = document.querySelector('#search-go-btn');
                    
                    if (document.activeElement === searchDropdown &&
                        searchButton && !searchButton.disabled) {
                        event.preventDefault();
                        searchButton.click();
                    }
                }
            });
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("search-feedback", "id"),  # Dummy output
        [
            Input("borehole-search-dropdown", "value"),
            Input("search-go-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )

    # ====================================================================
    # MARKER CLICK HANDLING
    # ====================================================================

    # Register marker click callback
    handle_marker_click(app)

    logging.info("✅ All split callbacks registered successfully!")

    # ====================================================================
    # HELPER FUNCTIONS - Reusable Logic for Callbacks
    # ====================================================================

    def add_polyline_distance_info(borehole_ids, stored_borehole_data):
        """Add distance along polyline information to borehole display"""
        try:
            if "last_polyline" not in stored_borehole_data:
                return []

            polyline_coords = stored_borehole_data["last_polyline"]
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

            distance_info = []
            for borehole_id in borehole_ids:
                borehole_row = loca_df[loca_df["LOCA_ID"] == borehole_id]
                if not borehole_row.empty:
                    # Try both coordinate column names
                    if (
                        "LOCA_LAT" in borehole_row.columns
                        and "LOCA_LON" in borehole_row.columns
                    ):
                        lat = borehole_row["LOCA_LAT"].iloc[0]
                        lon = borehole_row["LOCA_LON"].iloc[0]
                    elif (
                        "lat" in borehole_row.columns and "lon" in borehole_row.columns
                    ):
                        lat = borehole_row["lat"].iloc[0]
                        lon = borehole_row["lon"].iloc[0]
                    else:
                        continue

                    # Calculate distance along polyline
                    distance = calculate_distance_along_polyline(
                        polyline_coords, lat, lon
                    )
                    distance_info.append(
                        f"{borehole_id}: {distance:.1f}m along polyline"
                    )

            return distance_info
        except Exception as e:
            logging.error(f"Error calculating polyline distances: {e}")
            return []


def validate_borehole_near_polyline(
    borehole_lat, borehole_lon, polyline_coords, max_distance=100
):
    """
    Validate if a borehole is within a reasonable distance of the polyline using helper functions
    """
    try:
        # Convert polyline to segments and check distance to each segment
        for i in range(len(polyline_coords) - 1):
            start_point = (polyline_coords[i][1], polyline_coords[i][0])  # (lon, lat)
            end_point = (
                polyline_coords[i + 1][1],
                polyline_coords[i + 1][0],
            )  # (lon, lat)
            borehole_point = (borehole_lon, borehole_lat)

            # Calculate distance from borehole to this line segment
            distance = point_to_line_distance(borehole_point, start_point, end_point)

            # If within max distance, also get the projected point
            if distance <= max_distance:
                projected_point = project_point_to_line_segment(
                    borehole_point, start_point, end_point
                )
                logging.debug(
                    f"Borehole validated: {distance:.1f}m from polyline, projected to {projected_point}"
                )
                return True

        return False
    except Exception as e:
        logging.error(f"Error validating borehole near polyline: {e}")
        return True  # Default to include if validation fails


def handle_marker_click(app):
    """Handle marker clicks to generate borehole logs and update marker colors"""

    @app.callback(
        [
            Output(
                "section-plot-output", "children"
            ),  # Changed from log-plot-output to section-plot-output
            Output("borehole-markers", "children", allow_duplicate=True),
        ],
        [
            Input(
                {"type": "borehole-marker", "index": dash.dependencies.ALL}, "n_clicks"
            )
        ],
        [
            State("borehole-data-store", "data"),
            State("borehole-markers", "children"),
            State(
                "show-labels-checkbox", "value"
            ),  # Add state for show-labels checkbox
        ],
        prevent_initial_call=True,
    )
    def marker_click_handler(
        marker_clicks, stored_borehole_data, current_markers, show_labels_value
    ):
        """Handle marker clicks to generate borehole logs"""
        try:
            logging.info("=== MARKER CLICK CALLBACK ===")
            logging.info(f"Triggered by: {dash.callback_context.triggered}")
            logging.info(f"Show labels checkbox value: {show_labels_value}")

            # Check if any marker was clicked
            if not marker_clicks or all(
                clicks is None or clicks == 0 for clicks in marker_clicks
            ):
                logging.info("No marker clicks detected")
                return dash.no_update, dash.no_update

            # OPTIMIZATION: Find clicked marker efficiently without logging all marker states
            # Only log the clicked marker instead of all 94 marker states (616 character reduction)
            clicked_index = None
            max_clicks = 0
            for i, clicks in enumerate(marker_clicks):
                if clicks and clicks > max_clicks:
                    max_clicks = clicks
                    clicked_index = i

            if clicked_index is None:
                logging.info("No valid marker click found")
                return dash.no_update, dash.no_update

            # Log only the clicked marker information, not all marker states
            logging.info(
                f"Marker {clicked_index} was clicked ({max_clicks} times) out of {len(marker_clicks)} total markers"
            )

            # Get borehole data
            if not stored_borehole_data:
                logging.warning("No borehole data available")
                return html.Div("No borehole data available"), dash.no_update

            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            if clicked_index >= len(loca_df):
                logging.warning(f"Invalid marker index: {clicked_index}")
                return html.Div("Invalid borehole selected"), dash.no_update

            # Get the clicked borehole
            clicked_borehole = loca_df.iloc[clicked_index]
            borehole_id = clicked_borehole["LOCA_ID"]
            logging.info(f"Generating borehole log for: {borehole_id}")

            # Generate borehole log with larger figure size to match section plot proportions
            filename_map = stored_borehole_data["filename_map"]
            combined_content = ""
            for filename, content in filename_map.items():
                combined_content += content + "\n"

            # Get if show_labels is enabled
            show_labels = "show_labels" in (show_labels_value or [])
            logging.info(f"Show labels for borehole log: {show_labels}")

            # Use larger figure size and proper aspect ratio for borehole logs
            # Borehole logs are typically taller than they are wide (portrait orientation)
            # The new function returns a list of base64-encoded images
            images = plot_borehole_log_from_ags_content(
                combined_content,
                borehole_id,
                show_labels=show_labels,
                fig_height=11.69,  # A4 height
                fig_width=8.27,  # A4 width
            )

            if images and len(images) > 0:
                # Create a custom style that preserves aspect ratio
                preserved_aspect_style = {
                    "width": "66vw",  # 2/3 of viewport width for the image itself
                    "height": "auto",  # Maintain aspect ratio
                    "display": "block",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                    "margin-bottom": "20px",  # Space between images
                    "objectFit": "contain",
                    # Remove maxWidth/minWidth from image, let container control max width if needed
                }

                # Create image elements for each page
                image_elements = []
                for i, img_b64 in enumerate(images):
                    page_title = (
                        f"Page {i + 1} of {len(images)}" if len(images) > 1 else ""
                    )
                    if page_title:
                        image_elements.append(
                            html.H4(
                                page_title,
                                style={"text-align": "center", "margin": "10px 0"},
                            )
                        )

                    image_elements.append(
                        html.Img(
                            src=f"data:image/png;base64,{img_b64}",
                            style=preserved_aspect_style,
                        )
                    )

                log_output = html.Div(
                    [
                        html.H3(
                            f"Borehole Log: {borehole_id}",
                            style={"text-align": "center", "margin-bottom": "20px"},
                        ),
                        html.P(
                            f"Generated {len(images)} page(s)",
                            style={
                                "text-align": "center",
                                "margin-bottom": "20px",
                                "color": "#666",
                            },
                        ),
                        # All image pages displayed one after another
                        html.Div(image_elements),
                    ],
                    style={
                        "width": "100%",  # Container is full width, image inside is 66vw
                        "maxWidth": "100vw",  # No artificial max width
                        "margin": "0 auto",
                        "display": "block",
                    },
                )
            else:
                log_output = html.Div(
                    f"Could not generate borehole log for {borehole_id}"
                )

            # Update marker colors - make clicked marker green, others blue
            updated_markers = []
            if current_markers:
                for i, marker in enumerate(current_markers):
                    if marker and marker.get("props"):
                        # Copy the marker
                        new_marker = marker.copy()
                        new_props = marker["props"].copy()

                        # Update icon color based on whether this marker was clicked
                        if i == clicked_index:
                            # Make clicked marker green
                            if "icon" in new_props:
                                new_icon = new_props["icon"].copy()
                                new_icon["iconUrl"] = GREEN_MARKER
                                new_props["icon"] = new_icon
                        else:
                            # Make other markers blue
                            if "icon" in new_props:
                                new_icon = new_props["icon"].copy()
                                new_icon["iconUrl"] = BLUE_MARKER
                                new_props["icon"] = new_icon

                        new_marker["props"] = new_props
                        updated_markers.append(new_marker)
                    else:
                        updated_markers.append(marker)

            # log_output is now returned to section-plot-output
            return log_output, updated_markers

        except Exception as e:
            logging.error(f"Error in marker click handler: {e}")
            import traceback

            traceback.print_exc()
            # Error message is returned to section-plot-output
            return html.Div(f"Error generating borehole log: {e}"), dash.no_update

    def create_selection_shape_visual(feature):
        """Create a visual representation of a drawn selection shape for display"""
        try:
            if not feature or "geometry" not in feature:
                return []

            geometry = feature["geometry"]
            geom_type = geometry.get("type", "")
            coordinates = geometry.get("coordinates", [])

            if not coordinates:
                return []

            if geom_type == "Polygon":
                # Convert coordinates from GeoJSON format [lon, lat] to Leaflet format [lat, lon]
                if coordinates and len(coordinates[0]) > 0:
                    polygon_coords = [[lat, lon] for lon, lat in coordinates[0]]
                    return [
                        dl.Polygon(
                            positions=polygon_coords,
                            color="#ff7800",
                            fillColor="#ffb347",
                            fillOpacity=0.2,
                            weight=2,
                            opacity=0.8,
                            children=dl.Tooltip("Selected Area"),
                        )
                    ]
            elif geom_type == "Rectangle":
                # Rectangle is typically stored as a polygon
                if coordinates and len(coordinates[0]) > 0:
                    rect_coords = [[lat, lon] for lon, lat in coordinates[0]]
                    return [
                        dl.Polygon(
                            positions=rect_coords,
                            color="#ff7800",
                            fillColor="#ffb347",
                            fillOpacity=0.2,
                            weight=2,
                            opacity=0.8,
                            children=dl.Tooltip("Selected Rectangle"),
                        )
                    ]
            # Note: LineString shapes are handled in pca-line-group, not here

            return []
        except Exception as e:
            logging.error(f"Error creating selection shape visual: {e}")
            return []
