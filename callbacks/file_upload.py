"""
File Upload Callbacks

This module handles all file upload related callbacks, extracted from
the monolithic callbacks_split.py file for better organization and maintainability.
"""

import logging
import base64
import statistics
from datetime import datetime
from typing import List, Tuple, Any, Optional
import pandas as pd
from dash import html, dcc, Output, Input, State, callback_context
import dash

from .base import FileUploadCallbackBase
from data_loader import load_all_loca_data
from coordinate_service import get_coordinate_service
from app_constants import FILE_LIMITS, MAP_CONFIG
from error_handling import get_error_handler, ErrorCategory, ErrorSeverity
from state_management import get_app_state_manager

logger = logging.getLogger(__name__)


class FileUploadCallback(FileUploadCallbackBase):
    """Main file upload processing callback."""

    def __init__(self):
        super().__init__("file_upload")

    def register(self, app: dash.Dash) -> None:
        """Register the file upload callback."""

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
            """Handle file upload and create markers."""

            try:
                self.log_callback_start(
                    {
                        "files_count": (
                            len(stored_data.get("contents", [])) if stored_data else 0
                        )
                    }
                )

                # Default values
                map_center = map_center_state or [51.5, -0.1]
                map_zoom = map_zoom_state or 6

                if not stored_data or "contents" not in stored_data:
                    self.logger.info("No file uploaded yet")
                    return None, [], map_center, map_zoom, None, None

                # Process uploaded files
                result = self._process_upload(stored_data, map_center, map_zoom)

                self.log_callback_end({"success": True})
                return result

            except Exception as e:
                self.logger.error(f"Error in file upload callback: {e}", exc_info=True)
                return self.handle_error(e, output_count=6)

    def _process_upload(
        self, stored_data: dict, map_center: List[float], map_zoom: int
    ) -> Tuple[Any, ...]:
        """Process the uploaded files and return results."""

        list_of_contents = stored_data["contents"]
        list_of_names = stored_data["filenames"]
        self.logger.info(f"Processing {len(list_of_contents)} uploaded files")

        # Validate file sizes
        files_for_validation = []
        for content, name in zip(list_of_contents, list_of_names or []):
            content_type, content_string = content.split(",")
            files_for_validation.append((content_type, content_string, name))

        # Validate total upload size
        is_valid_total, total_error, total_size_mb = self._validate_total_upload_size(
            files_for_validation
        )
        if not is_valid_total:
            self.logger.warning(f"Upload rejected: {total_error}")
            error_msg = self._create_error_message(total_error, "warning")
            return [error_msg], [], map_center, map_zoom, None, None

        # Process individual files
        ags_files, file_status, total_processed_size = self._process_files(
            list_of_contents, list_of_names
        )

        if not ags_files:
            error_msg = self._create_error_message(
                "No valid files could be processed", "error"
            )
            return [error_msg], [], map_center, map_zoom, None, None

        # Add upload summary
        file_status = self._add_upload_summary(
            file_status, ags_files, list_of_contents, total_processed_size
        )

        # Load and process borehole data
        loca_df, filename_map = load_all_loca_data(ags_files)
        self.logger.info(f"Loaded {len(loca_df)} boreholes")

        # Transform coordinates and create markers
        markers, valid_coords = self._create_markers(loca_df)

        # Calculate map center and zoom
        if valid_coords:
            map_center, map_zoom = self._calculate_optimal_view(valid_coords)

        # Update application state
        self._update_app_state(loca_df, filename_map)

        # Create borehole data for Dash store
        borehole_data = {
            "loca_df": loca_df.to_dict("records"),
            "filename_map": filename_map,
            "all_borehole_ids": loca_df["LOCA_ID"].tolist(),
        }

        # Add file breakdown
        file_status = self._add_file_breakdown(file_status, filename_map, loca_df)

        # Clear shapes on upload
        clear_shapes = datetime.now().timestamp()

        return (
            file_status,
            markers,
            map_center,
            map_zoom,
            borehole_data,
            clear_shapes,
        )

    def _validate_total_upload_size(
        self, files: List[Tuple[str, str, str]]
    ) -> Tuple[bool, str, float]:
        """Validate total upload size."""

        total_size = 0.0

        for content_type, content_string, name in files:
            # Calculate size in MB
            size_bytes = len(content_string) * 3 / 4  # Base64 overhead
            size_mb = size_bytes / (1024 * 1024)
            total_size += size_mb

        if len(files) > FILE_LIMITS.MAX_FILES:
            return False, f"Too many files (max {FILE_LIMITS.MAX_FILES})", total_size

        if total_size > FILE_LIMITS.MAX_TOTAL_SIZE_MB:
            return (
                False,
                f"Total size too large (max {FILE_LIMITS.MAX_TOTAL_SIZE_MB}MB)",
                total_size,
            )

        return True, "", total_size

    def _validate_file_size(
        self, content_string: str, name: str
    ) -> Tuple[bool, str, float]:
        """Validate individual file size."""

        size_bytes = len(content_string) * 3 / 4  # Base64 overhead
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > FILE_LIMITS.MAX_FILE_SIZE_MB:
            return (
                False,
                f"File {name} too large (max {FILE_LIMITS.MAX_FILE_SIZE_MB}MB)",
                size_mb,
            )

        return True, "", size_mb

    def _process_files(
        self, list_of_contents: List[str], list_of_names: List[str]
    ) -> Tuple[List[Tuple[str, str]], List, float]:
        """Process individual uploaded files."""

        ags_files = []
        file_status = []
        total_processed_size = 0.0

        for content, name in zip(list_of_contents, list_of_names or []):
            try:
                content_type, content_string = content.split(",")

                # Validate individual file size
                is_valid_file, file_error, file_size_mb = self._validate_file_size(
                    content_string, name
                )

                if not is_valid_file:
                    self.logger.warning(f"File rejected: {file_error}")
                    file_status.append(
                        html.Div(
                            [
                                html.Span("❌ ", style={"color": "red"}),
                                html.Span(file_error, style={"color": "red"}),
                            ]
                        )
                    )
                    continue

                # Decode and process file
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

                self.logger.info(
                    f"Successfully processed file: {name} ({file_size_mb:.1f}MB)"
                )

            except Exception as e:
                self.logger.error(f"Error reading {name}: {e}")
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

        return ags_files, file_status, total_processed_size

    def _create_markers(
        self, loca_df: pd.DataFrame
    ) -> Tuple[List, List[Tuple[float, float]]]:
        """Create map markers from borehole data."""

        import dash_leaflet as dl

        # Define marker URL constant
        BLUE_MARKER = MAP_CONFIG.BLUE_MARKER_URL

        coordinate_service = get_coordinate_service()
        markers = []
        valid_coords = []

        # Vectorized coordinate transformation
        valid_mask = loca_df["LOCA_NATE"].apply(
            lambda x: pd.notnull(x)
            and str(x).replace(".", "", 1).replace("-", "", 1).isdigit()
        ) & loca_df["LOCA_NATN"].apply(
            lambda x: pd.notnull(x)
            and str(x).replace(".", "", 1).replace("-", "", 1).isdigit()
        )

        clean_df = loca_df[valid_mask].copy()
        problem_df = loca_df[~valid_mask].copy()

        # Batch transform for clean data
        if not clean_df.empty:
            bng_x = clean_df["LOCA_NATE"].astype(float).values
            bng_y = clean_df["LOCA_NATN"].astype(float).values
            wgs84_lat, wgs84_lon = coordinate_service.transform_bng_to_wgs84(
                bng_x, bng_y
            )

            clean_df = clean_df.copy()
            clean_df["lat"] = wgs84_lat
            clean_df["lon"] = wgs84_lon

        # Fallback for problematic rows
        for i, row in problem_df.iterrows():
            try:
                easting = float(row["LOCA_NATE"])
                northing = float(row["LOCA_NATN"])
                lat, lon = coordinate_service.transform_bng_to_wgs84(
                    [easting], [northing]
                )
                problem_df.at[i, "lat"] = lat[0]
                problem_df.at[i, "lon"] = lon[0]
            except Exception as e:
                self.logger.warning(
                    f"Could not transform coordinates for {row['LOCA_ID']}: {e}"
                )
                continue

        # Combine dataframes
        combined_df = pd.concat([clean_df, problem_df], ignore_index=True)

        # Create markers
        for i, row in combined_df.iterrows():
            lat = row.get("lat")
            lon = row.get("lon")

            if pd.isna(lat) or pd.isna(lon):
                continue

            label = str(row["LOCA_ID"]).strip()
            marker_id = {"type": "borehole-marker", "index": i}

            # Format tooltip info
            ground_level = self._format_depth_value(row.get("LOCA_GL", "N/A"))
            total_depth = self._format_depth_value(row.get("LOCA_FDEP", "N/A"))

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

        self.logger.info(f"Created {len(markers)} map markers")
        return markers, valid_coords

    def _calculate_optimal_view(
        self, coordinates: List[Tuple[float, float]]
    ) -> Tuple[List[float], int]:
        """Calculate optimal map center and zoom from coordinates."""

        lats = [coord[0] for coord in coordinates]
        lons = [coord[1] for coord in coordinates]

        # Use median for robust centering
        median_lat = statistics.median(lats)
        median_lon = statistics.median(lons)
        map_center = [median_lat, median_lon]

        # Calculate zoom based on coordinate spread
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        coord_range = max(lat_range, lon_range)

        if coord_range > 0.1:
            map_zoom = 10
        elif coord_range > 0.01:
            map_zoom = 12
        elif coord_range > 0.001:
            map_zoom = 14
        else:
            map_zoom = 16

        self.logger.info(
            f"🎯 Setting map center: [{median_lat:.6f}, {median_lon:.6f}] with zoom {map_zoom}"
        )

        return map_center, map_zoom

    def _update_app_state(self, loca_df: pd.DataFrame, filename_map: dict):
        """Update the centralized application state."""

        state_manager = get_app_state_manager()

        # Update borehole data
        state_manager.update_borehole_data(
            loca_df=loca_df,
            filename_map=filename_map,
            all_borehole_ids=loca_df["LOCA_ID"].tolist(),
        )

        # Update upload state
        state_manager.update_upload_state(
            files_uploaded=list(filename_map.keys()),
            total_size_mb=sum([len(content) for content in filename_map.values()])
            / (1024 * 1024),
            upload_errors=[],
        )

        self.logger.debug("Updated centralized application state")

    def _format_depth_value(self, value) -> str:
        """Format depth values for display."""

        if value == "N/A" or value is None or str(value).strip() == "":
            return "N/A"

        try:
            return f"{float(value):.2f}m"
        except (ValueError, TypeError):
            return "N/A"

    def _add_upload_summary(
        self, file_status: List, ags_files: List, all_files: List, total_size: float
    ) -> List:
        """Add upload summary to file status."""

        summary = html.Div(
            [
                html.P(
                    "📊 Upload Summary:",
                    style={"fontWeight": "bold", "marginBottom": "5px"},
                ),
                html.P(
                    f"Files processed: {len(ags_files)}/{len(all_files)}",
                    style={"margin": "2px 0"},
                ),
                html.P(f"Total size: {total_size:.1f}MB", style={"margin": "2px 0"}),
            ],
            style={
                "backgroundColor": "#f0f0f0",
                "padding": "10px",
                "borderRadius": "5px",
                "marginBottom": "10px",
            },
        )

        file_status.insert(0, summary)
        return file_status

    def _add_file_breakdown(
        self, file_status: List, filename_map: dict, loca_df: pd.DataFrame
    ) -> List:
        """Add file breakdown information."""

        file_breakdown = []
        for filename in filename_map.keys():
            file_rows = loca_df[loca_df["ags_file"] == filename]
            if len(file_rows) > 0:
                file_breakdown.append(
                    html.Li([html.B(filename), f" : {len(file_rows)} boreholes"])
                )

        if file_breakdown:
            import config

            file_status.append(
                html.Div(
                    [
                        html.H4("File Summary:", style=config.SUCCESS_MESSAGE_STYLE),
                        html.Ul(file_breakdown),
                    ]
                )
            )

        return file_status

    def _create_error_message(self, message: str, severity: str = "error") -> html.Div:
        """Create standardized error message."""

        error_handler = get_error_handler()

        if severity == "warning":
            error_severity = ErrorSeverity.WARNING
        else:
            error_severity = ErrorSeverity.ERROR

        error = error_handler.create_error(
            message=message,
            category=ErrorCategory.FILE_UPLOAD,
            severity=error_severity,
            user_message=message,
        )

        return error_handler._create_error_component(error)


def register_file_upload_callbacks(callback_manager):
    """Register all file upload related callbacks."""

    callback_manager.add_callback(FileUploadCallback())
    logger.info("Registered file upload callbacks")
