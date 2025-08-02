"""
Search Functionality Callbacks Module

This module handles all borehole search and navigation functionality,
refactored from the original monolithic callbacks_split.py file.

Responsibilities:
- Search dropdown population and updates
- Borehole search navigation
- Map centering on selected boreholes
- Search feedback and validation
"""

import logging
from dash import Output, Input, State, html, no_update
import pandas as pd

from .base import SearchCallbackBase
from state_management import get_app_state_manager
from error_handling import get_error_handler, ErrorCategory
from coordinate_service import get_coordinate_service
from borehole_log import plot_borehole_log_from_ags_content  # Use compatibility wrapper
from app_constants import MAP_CONFIG
from map_update_workaround import force_map_refresh_with_new_position


class SearchFunctionalityCallback(SearchCallbackBase):
    """Handles borehole search and navigation functionality."""

    def __init__(self):
        super().__init__("search_functionality")
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_error_handler()
        self.state_manager = get_app_state_manager()
        self.coordinate_service = get_coordinate_service()

    def register(self, app):
        """Register all search-related callbacks with the Dash app."""
        self._register_search_dropdown_callback(app)
        self._register_search_button_toggle_callback(app)
        self._register_search_go_callback(app)
        self.logger.info("Registered search functionality callbacks")

    def _register_search_dropdown_callback(self, app):
        """Register callback to update search dropdown options."""

        @app.callback(
            Output("borehole-search-dropdown", "options"),
            Output("borehole-search-dropdown", "value"),
            Input("borehole-data-store", "data"),
            prevent_initial_call=True,
        )
        def update_search_dropdown(stored_borehole_data):
            """Update search dropdown options when borehole data is loaded"""
            self.logger.info("=== UPDATING SEARCH DROPDOWN ===")

            try:
                return self._update_search_dropdown_logic(stored_borehole_data)
            except Exception as e:
                error_msg = f"Error updating search dropdown: {str(e)}"
                self.logger.error(error_msg)
                self.error_handler.handle_error(
                    e, ErrorCategory.SEARCH, "update_search_dropdown"
                )
                return [], None

    def _update_search_dropdown_logic(self, stored_borehole_data):
        """Core logic for updating search dropdown."""
        if not stored_borehole_data:
            self.logger.info("No borehole data available for search")
            return [], None

        loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

        if loca_df.empty:
            self.logger.info("Empty borehole dataframe")
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

        self.logger.info(f"Created {len(options)} search options")
        return options, None

    def _register_search_button_toggle_callback(self, app):
        """Register callback to toggle search button state."""

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

    def _register_search_go_callback(self, app):
        """Register the main search go functionality callback."""

        @app.callback(
            [
                Output("search-feedback", "children"),
                Output("log-plot-output", "children", allow_duplicate=True),
                Output("borehole-markers", "children", allow_duplicate=True),
                Output("borehole-map", "center", allow_duplicate=True),
                Output("borehole-map", "zoom", allow_duplicate=True),
                Output("borehole-map", "invalidateSize", allow_duplicate=True),
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
            self.logger.info("=== SEARCH GO BUTTON CLICKED ===")

            if not n_clicks or n_clicks == 0:
                return (
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            try:
                return self._handle_search_go_logic(
                    selected_borehole_index,
                    stored_borehole_data,
                    show_labels_value,
                    current_markers,
                )
            except Exception as e:
                error_msg = f"Error in search go callback: {str(e)}"
                self.logger.error(error_msg)
                self.error_handler.handle_error(
                    e, ErrorCategory.SEARCH, "handle_search_go"
                )
                feedback = html.Div(
                    "An error occurred during search. Please try again.",
                    style={"color": "red", "fontWeight": "bold"},
                )
                return (
                    feedback,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    None,
                    None,
                )

    def _handle_search_go_logic(
        self,
        selected_borehole_index,
        stored_borehole_data,
        show_labels_value,
        current_markers,
    ):
        """Core logic for handling search go functionality."""
        if selected_borehole_index is None:
            feedback = html.Div(
                "Please select a borehole from the dropdown.",
                style={"color": "orange", "fontWeight": "bold"},
            )
            return (
                feedback,
                no_update,
                no_update,
                no_update,
                no_update,
                None,
                no_update,
            )

        if not stored_borehole_data:
            feedback = html.Div(
                "No borehole data available. Please upload an AGS file first.",
                style={"color": "red", "fontWeight": "bold"},
            )
            return (feedback, no_update, no_update, no_update, no_update, None, None)

        # Get the borehole data
        loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

        if selected_borehole_index >= len(loca_df):
            feedback = html.Div(
                "Selected borehole not found in data.",
                style={"color": "red", "fontWeight": "bold"},
            )
            return (feedback, no_update, no_update, no_update, no_update, None, None)

        # Get the selected borehole
        selected_borehole = loca_df.iloc[selected_borehole_index]
        borehole_id = str(selected_borehole["LOCA_ID"]).strip()

        self.logger.info(f"Searching for borehole: {borehole_id}")

        # Get coordinates
        easting = selected_borehole.get("LOCA_NATE")
        northing = selected_borehole.get("LOCA_NATN")

        if pd.isna(easting) or pd.isna(northing):
            feedback = html.Div(
                f"No valid coordinates found for borehole {borehole_id}.",
                style={"color": "red", "fontWeight": "bold"},
            )
            return (feedback, no_update, no_update, no_update, no_update, None, None)

        try:
            # Convert coordinates
            lat, lon = self.coordinate_service.transform_bng_to_wgs84(easting, northing)
            self.logger.info(
                f"Converted coordinates: {easting}, {northing} -> {lat}, {lon}"
            )

            # Generate borehole log
            log_plot = self._generate_borehole_log(
                stored_borehole_data, borehole_id, show_labels_value
            )

            # Update map center and zoom
            new_center = [lat, lon]
            new_zoom = MAP_CONFIG.SEARCH_ZOOM_LEVEL

            # Success feedback
            feedback = html.Div(
                f"✅ Navigated to borehole: {borehole_id}",
                style={"color": "green", "fontWeight": "bold"},
            )

            self.logger.info(
                f"Successfully navigated to borehole {borehole_id} at {lat}, {lon}"
            )

            # Use workaround to force map update
            invalidate_value, final_center, final_zoom, _ = (
                force_map_refresh_with_new_position(new_center, new_zoom)
            )

            return (
                feedback,
                log_plot,
                current_markers,
                final_center,
                final_zoom,
                invalidate_value,
                None,
            )

        except Exception as e:
            self.logger.error(f"Error processing borehole {borehole_id}: {e}")
            feedback = html.Div(
                f"Error processing borehole {borehole_id}: {str(e)}",
                style={"color": "red", "fontWeight": "bold"},
            )
            return (feedback, no_update, no_update, no_update, no_update, None, None)

    def _generate_borehole_log(
        self, stored_borehole_data, borehole_id, show_labels_value
    ):
        """Generate borehole log for the selected borehole."""
        try:
            # Get AGS content
            filename_map = stored_borehole_data["filename_map"]
            combined_content = ""
            for filename, content in filename_map.items():
                combined_content += content + "\n"

            show_labels = "show_labels" in (show_labels_value or [])

            # Generate borehole log - this returns base64 images, not a figure
            images = plot_borehole_log_from_ags_content(
                combined_content, borehole_id, show_labels=show_labels
            )

            if images and len(images) > 0:
                # MULTI-PAGE FIX: Display all pages like marker_handling.py does
                return self._create_borehole_log_html_multi_page(borehole_id, images)
            else:
                return html.Div(
                    f"No borehole log data available for {borehole_id}",
                    style={
                        "textAlign": "center",
                        "color": "gray",
                        "fontStyle": "italic",
                    },
                )

        except Exception as e:
            self.logger.error(f"Error generating borehole log for {borehole_id}: {e}")
            return html.Div(
                f"Error generating borehole log: {str(e)}",
                style={"textAlign": "center", "color": "red", "fontStyle": "italic"},
            )

    def _create_borehole_log_html_multi_page(self, borehole_id, images):
        """
        Create HTML display for multi-page borehole log images.

        Replicates the exact working logic from marker_handling.py to ensure
        consistent multi-page display across both callback paths.
        """
        # Create a custom style that preserves aspect ratio and centers the images
        preserved_aspect_style = {
            "width": "66vw",  # 2/3 of viewport width for the image itself
            "height": "auto",  # Maintain aspect ratio
            "display": "block",
            "marginLeft": "auto",
            "marginRight": "auto",
            "margin-bottom": "20px",  # Space between images
            "objectFit": "contain",
        }

        # Create image elements for each page
        image_elements = []
        for i, img_b64 in enumerate(images):
            page_title = f"Page {i + 1} of {len(images)}" if len(images) > 1 else ""
            if page_title:
                image_elements.append(
                    html.H4(
                        page_title,
                        style={"text-align": "center", "margin": "10px 0"},
                    )
                )

            # CRITICAL FIX: Handle data URL prefix correctly
            # The borehole log function already returns data URL format
            if img_b64.startswith("data:image/png;base64,"):
                # Already has prefix, use as-is
                src_url = img_b64
            else:
                # Add prefix if missing
                src_url = f"data:image/png;base64,{img_b64}"

            image_elements.append(
                html.Img(
                    src=src_url,
                    style=preserved_aspect_style,
                )
            )

        return html.Div(
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
