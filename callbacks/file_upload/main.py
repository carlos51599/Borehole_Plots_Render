"""
File Upload Main Callback Module

This module contains the main callback registration logic that coordinates
all file upload functionality using the extracted modules.
"""

import logging
from datetime import datetime
from typing import List, Tuple, Any
from dash import html, Output, Input, State
import dash

from ..base import FileUploadCallbackBase
from ..error_handling import CallbackError, create_error_message

# Import the extracted modules
from .validation import (
    validate_total_upload_size,
    validate_individual_file_size,
    validate_file_content_security,
)
from .processing import (
    process_uploaded_files,
    load_and_optimize_borehole_data,
    transform_coordinates_and_create_markers,
    calculate_optimal_map_view,
    prepare_borehole_data_for_storage,
)
from .ui_components import (
    create_upload_summary,
    create_file_success_status,
    create_file_error_status,
    create_file_breakdown_summary,
    create_map_status_info,
    create_processing_error_message,
)

logger = logging.getLogger(__name__)


class FileUploadCallback(FileUploadCallbackBase):
    """
    Main file upload processing callback using modular components.

    This class coordinates file validation, processing, and UI updates
    using the extracted validation, processing, and UI modules.
    """

    def __init__(self):
        super().__init__("file_upload")

    def register(self, app: dash.Dash) -> None:
        """Register the file upload callback with the Dash app."""

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
            """Handle file upload and create markers with modular processing."""
            logger.info("=== FILE UPLOAD CALLBACK ===")

            try:
                # Initialize default values
                map_center = map_center_state or [51.5, -0.1]
                map_zoom = map_zoom_state or 6

                # Check if data was uploaded
                if not stored_data or "contents" not in stored_data:
                    logger.info("No file uploaded yet")
                    return None, [], map_center, map_zoom, None, None

                # Extract upload data
                list_of_contents = stored_data["contents"]
                list_of_names = stored_data["filenames"]
                logger.info(f"Processing {len(list_of_contents)} uploaded files")

                # Step 1: Validate file sizes and content
                validation_result = self._validate_uploaded_files(
                    list_of_contents, list_of_names
                )
                if validation_result["has_errors"]:
                    return self._handle_validation_errors(
                        validation_result, map_center, map_zoom
                    )

                # Step 2: Process files and extract AGS data
                ags_files, total_size = process_uploaded_files(
                    list_of_contents, list_of_names
                )

                if not ags_files:
                    error_msg = create_processing_error_message(
                        "No valid AGS files could be processed from the upload."
                    )
                    return [error_msg], [], map_center, map_zoom, None, None

                # Step 3: Load and optimize borehole data
                loca_df, filename_map = load_and_optimize_borehole_data(ags_files)

                # Step 4: Transform coordinates and create markers
                markers, valid_coords = transform_coordinates_and_create_markers(
                    loca_df
                )

                # Step 5: Calculate optimal map view
                if valid_coords:
                    map_center, map_zoom = calculate_optimal_map_view(valid_coords)

                # Step 6: Prepare data for storage
                borehole_data = prepare_borehole_data_for_storage(loca_df, filename_map)

                # Step 7: Create UI status components
                status_components = self._create_status_components(
                    ags_files,
                    total_size,
                    list_of_contents,
                    filename_map,
                    loca_df,
                    markers,
                    map_center,
                    map_zoom,
                    valid_coords,
                )

                # Clear shapes on upload
                clear_shapes = datetime.now().timestamp()

                return (
                    status_components,
                    markers,
                    map_center,
                    map_zoom,
                    borehole_data,
                    clear_shapes,
                )

            except Exception as e:
                logger.error(f"Error in file upload callback: {e}", exc_info=True)
                error_msg = create_processing_error_message(
                    f"Unexpected error during file processing: {str(e)}"
                )
                clear_shapes = datetime.now().timestamp()
                return [error_msg], [], map_center, map_zoom, None, clear_shapes

    def _validate_uploaded_files(
        self, file_contents: List[str], file_names: List[str]
    ) -> dict:
        """
        Validate all uploaded files using the validation module.

        Returns:
            Dictionary with validation results and error details
        """
        validation_result = {
            "has_errors": False,
            "file_statuses": [],
            "valid_files": 0,
            "total_files": len(file_contents),
        }

        # Prepare files for validation
        files_for_validation = []
        for content, name in zip(file_contents, file_names or []):
            try:
                content_type, content_string = content.split(",")
                files_for_validation.append((content_type, content_string, name))
            except Exception:
                validation_result["file_statuses"].append(
                    create_file_error_status(f"Invalid file format: {name}")
                )
                continue

        # Validate total upload size
        is_valid_total, total_error, total_size = validate_total_upload_size(
            files_for_validation
        )
        if not is_valid_total:
            validation_result["has_errors"] = True
            validation_result["total_error"] = total_error
            return validation_result

        # Validate individual files
        for content_type, content_string, name in files_for_validation:
            # Size validation
            is_valid_size, size_error, file_size = validate_individual_file_size(
                content_string, name
            )
            if not is_valid_size:
                validation_result["file_statuses"].append(
                    create_file_error_status(size_error)
                )
                continue

            # Content security validation
            is_valid_content, content_error = validate_file_content_security(
                content_string, name
            )
            if not is_valid_content:
                validation_result["file_statuses"].append(
                    create_file_error_status(content_error)
                )
                continue

            # File passed all validations
            validation_result["file_statuses"].append(
                create_file_success_status(name, file_size)
            )
            validation_result["valid_files"] += 1

        return validation_result

    def _handle_validation_errors(
        self, validation_result: dict, map_center: List[float], map_zoom: int
    ) -> Tuple[Any, ...]:
        """Handle validation errors and return appropriate response."""
        if "total_error" in validation_result:
            error_msg = create_error_message(
                CallbackError(
                    "Upload rejected due to size limits",
                    validation_result["total_error"],
                    "warning",
                ),
                "File Upload",
            )
            return [error_msg], [], map_center, map_zoom, None, None
        else:
            # Some files failed validation but others might be valid
            return (
                validation_result["file_statuses"],
                [],
                map_center,
                map_zoom,
                None,
                None,
            )

    def _create_status_components(
        self,
        ags_files: List,
        total_size: float,
        all_files: List,
        filename_map: dict,
        loca_df,
        markers: List,
        map_center: List[float],
        map_zoom: int,
        valid_coords: List,
    ) -> List[html.Div]:
        """Create all status UI components."""
        components = []

        # Add upload summary
        summary = create_upload_summary(len(ags_files), len(all_files), total_size)
        components.append(summary)

        # Add file breakdown
        breakdown = create_file_breakdown_summary(filename_map, loca_df)
        if breakdown.children:  # Only add if there's content
            components.append(breakdown)

        # Add map status info
        if valid_coords:
            lats = [coord[0] for coord in valid_coords]
            lons = [coord[1] for coord in valid_coords]
            coord_range = max(max(lats) - min(lats), max(lons) - min(lons))

            map_status = create_map_status_info(
                len(markers), map_center, coord_range, map_zoom
            )
            components.append(map_status)

        return components


def register_file_upload_callbacks(callback_manager):
    """Register all file upload related callbacks."""
    callback_manager.add_callback(FileUploadCallback())
    logger.info("Registered modular file upload callbacks")
