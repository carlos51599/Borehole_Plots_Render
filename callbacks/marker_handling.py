"""
Marker Handling Callbacks Module

This module handles all borehole marker interactions and click functionality,
refactored from the original monolithic callbacks_split.py file.

Responsibilities:
- Marker click handling for borehole log generation
- Marker color state management (active/inactive)
- Borehole log generation and display
- Selection shape visualization
"""

import logging
import dash
from dash import Output, Input, State, html, no_update
import pandas as pd
import dash_leaflet as dl

from .base import MarkerHandlingCallbackBase
from state_management import get_app_state_manager
from error_handling import get_error_handler, ErrorCategory
from app_constants import MAP_CONFIG
from borehole_log_professional import plot_borehole_log_from_ags_content


class MarkerHandlingCallback(MarkerHandlingCallbackBase):
    """Handles borehole marker interactions and click functionality."""

    def __init__(self):
        super().__init__("marker_handling")
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_error_handler()
        self.state_manager = get_app_state_manager()

        # Define marker constants for easier access
        self.BLUE_MARKER = MAP_CONFIG.BLUE_MARKER_URL
        self.GREEN_MARKER = MAP_CONFIG.GREEN_MARKER_URL

    def register(self, app):
        """Register all marker handling callbacks with the Dash app."""
        self._register_marker_click_callback(app)
        self.logger.info("Registered marker handling callbacks")

    def _register_marker_click_callback(self, app):
        """Register callback to handle marker clicks."""

        @app.callback(
            [
                Output("section-plot-output", "children"),
                Output("borehole-markers", "children", allow_duplicate=True),
            ],
            [
                Input(
                    {"type": "borehole-marker", "index": dash.dependencies.ALL},
                    "n_clicks",
                )
            ],
            [
                State("borehole-data-store", "data"),
                State("borehole-markers", "children"),
                State("show-labels-checkbox", "value"),
            ],
            prevent_initial_call=True,
        )
        def marker_click_handler(
            marker_clicks, stored_borehole_data, current_markers, show_labels_value
        ):
            """Handle marker clicks to generate borehole logs"""
            try:
                return self._handle_marker_click_logic(
                    marker_clicks,
                    stored_borehole_data,
                    current_markers,
                    show_labels_value,
                )
            except Exception as e:
                error_msg = f"Error in marker click handler: {str(e)}"
                self.logger.error(error_msg)
                self.error_handler.handle_error(
                    e, ErrorCategory.MARKER_INTERACTION, "marker_click_handler"
                )
                return html.Div(f"Error generating borehole log: {e}"), no_update

    def _handle_marker_click_logic(
        self, marker_clicks, stored_borehole_data, current_markers, show_labels_value
    ):
        """Core logic for handling marker clicks."""
        self.logger.info("=== MARKER CLICK CALLBACK ===")
        self.logger.info(f"Triggered by: {dash.callback_context.triggered}")
        self.logger.info(f"Show labels checkbox value: {show_labels_value}")

        # Check if any marker was clicked
        if not marker_clicks or all(
            clicks is None or clicks == 0 for clicks in marker_clicks
        ):
            self.logger.info("No marker clicks detected")
            return no_update, no_update

        # Find which marker was clicked (latest click)
        clicked_index = self._find_clicked_marker_index(marker_clicks)

        if clicked_index is None:
            self.logger.info("No valid marker click found")
            return no_update, no_update

        self.logger.info(f"Marker {clicked_index} was clicked")

        # Get borehole data
        if not stored_borehole_data:
            self.logger.warning("No borehole data available")
            return html.Div("No borehole data available"), no_update

        loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
        if clicked_index >= len(loca_df):
            self.logger.warning(f"Invalid marker index: {clicked_index}")
            return html.Div("Invalid borehole selected"), no_update

        # Get the clicked borehole
        clicked_borehole = loca_df.iloc[clicked_index]
        borehole_id = clicked_borehole["LOCA_ID"]
        self.logger.info(f"Generating borehole log for: {borehole_id}")

        # Generate borehole log
        log_output = self._generate_borehole_log_display(
            stored_borehole_data, borehole_id, show_labels_value
        )

        # Update marker colors
        updated_markers = self._update_marker_colors(current_markers, clicked_index)

        return log_output, updated_markers

    def _find_clicked_marker_index(self, marker_clicks):
        """Find which marker was clicked based on click counts."""
        clicked_index = None
        max_clicks = 0

        for i, clicks in enumerate(marker_clicks):
            if clicks and clicks > max_clicks:
                max_clicks = clicks
                clicked_index = i

        return clicked_index

    def _generate_borehole_log_display(
        self, stored_borehole_data, borehole_id, show_labels_value
    ):
        """Generate the borehole log display for the selected borehole."""
        try:
            # Get AGS content
            filename_map = stored_borehole_data["filename_map"]
            combined_content = ""
            for filename, content in filename_map.items():
                combined_content += content + "\n"

            # Get if show_labels is enabled
            show_labels = "show_labels" in (show_labels_value or [])
            self.logger.info(f"Show labels for borehole log: {show_labels}")

            # Use larger figure size and proper aspect ratio for borehole logs
            # Borehole logs are typically taller than they are wide (portrait orientation)
            # The function returns a list of base64-encoded images
            images = plot_borehole_log_from_ags_content(
                combined_content,
                borehole_id,
                show_labels=show_labels,
                fig_height=11.69,  # A4 height
                fig_width=8.27,  # A4 width
            )

            if images and len(images) > 0:
                return self._create_borehole_log_html(borehole_id, images)
            else:
                return html.Div(
                    f"Could not generate borehole log for {borehole_id}",
                    style={"textAlign": "center", "color": "red"},
                )

        except Exception as e:
            self.logger.error(f"Error generating borehole log for {borehole_id}: {e}")
            return html.Div(
                f"Error generating borehole log: {str(e)}",
                style={"textAlign": "center", "color": "red"},
            )

    def _create_borehole_log_html(self, borehole_id, images):
        """Create HTML display for borehole log images."""
        # Create a custom style that preserves aspect ratio
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

            image_elements.append(
                html.Img(
                    src=f"data:image/png;base64,{img_b64}",
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

    def _update_marker_colors(self, current_markers, clicked_index):
        """Update marker colors - make clicked marker green, others blue."""
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
                            new_icon["iconUrl"] = self.GREEN_MARKER
                            new_props["icon"] = new_icon
                    else:
                        # Make other markers blue
                        if "icon" in new_props:
                            new_icon = new_props["icon"].copy()
                            new_icon["iconUrl"] = self.BLUE_MARKER
                            new_props["icon"] = new_icon

                    new_marker["props"] = new_props
                    updated_markers.append(new_marker)
                else:
                    updated_markers.append(marker)

        return updated_markers

    def create_selection_shape_visual(self, feature):
        """Create a visual representation of a drawn selection shape for display."""
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
            self.logger.error(f"Error creating selection shape visual: {e}")
            return []
