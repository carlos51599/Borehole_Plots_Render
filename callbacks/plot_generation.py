"""
Plot Generation Callbacks Module

This module handles all plot generation and download functionality,
refactored from the original monolithic callbacks_split.py file.

Responsibilities:
- Section plot generation from AGS data
- Plot download functionality
- Coordinate transformation for polyline sections
- Memory management for matplotlib figures
"""

import logging
import io
import base64
from datetime import datetime
import dash
from dash import Output, Input, State, dcc, html
import matplotlib.pyplot as plt

from .base import PlotGenerationCallbackBase
from state_management import get_app_state_manager
from error_handling import get_error_handler
from coordinate_service import get_coordinate_service
from config_modules import (
    MAP_CENTER_STYLE,
)  # Use MAP_CENTER_STYLE instead of SECTION_PLOT_CENTER_STYLE
from app_constants import PLOT_CONFIG
from section import plot_section_from_ags_content


class PlotGenerationCallback(PlotGenerationCallbackBase):
    """Handles plot generation and download functionality."""

    def __init__(self):
        super().__init__("plot_generation")
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_error_handler()
        self.state_manager = get_app_state_manager()
        self.coordinate_service = get_coordinate_service()

    def register(self, app):
        """Register all plot generation callbacks with the Dash app."""
        self._register_plot_generation_callback(app)
        self._register_shape_clearing_callback(app)
        self._register_map_update_clientside_callback(app)
        self.logger.info("Registered plot generation callbacks")

    def _register_plot_generation_callback(self, app):
        """Register the main plot generation callback."""

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
            self.logger.info("=== PLOT GENERATION CALLBACK ===")
            self.logger.info(f"Triggered by: {dash.callback_context.triggered}")

            try:
                return self._handle_plot_generation_logic(
                    checked_ids,
                    show_labels_value,
                    download_clicks,
                    stored_borehole_data,
                )
            except Exception as e:
                error_msg = f"Error in plot generation callback: {str(e)}"
                self.logger.error(error_msg)
                self.error_handler.handle_callback_error(e, "handle_plot_generation")
                return None, None, None

    def _handle_plot_generation_logic(
        self, checked_ids, show_labels_value, download_clicks, stored_borehole_data
    ):
        """Core logic for plot generation."""
        import time

        start_time = time.time()

        ctx = dash.callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None

        self.logger.info(
            f"Plot generation started. Checked IDs: {len(checked_ids) if checked_ids else 0}"
        )

        if not stored_borehole_data or not checked_ids:
            self.logger.info("No data or checked IDs - returning None")
            return None, None, None

        show_labels = "show_labels" in (show_labels_value or [])

        try:
            # Get AGS content with timeout protection
            filename_map = stored_borehole_data["filename_map"]
            combined_content = ""
            for filename, content in filename_map.items():
                combined_content += content + "\n"

            content_prep_time = time.time()
            self.logger.info(
                f"Content preparation took: {content_prep_time - start_time:.2f}s"
            )

            # Generate section plot with polyline data if available
            section_line = self._process_polyline_data(stored_borehole_data)

            polyline_time = time.time()
            self.logger.info(
                f"Polyline processing took: {polyline_time - content_prep_time:.2f}s"
            )

            # Add timeout protection around the main plotting function
            self.logger.info("Starting section plot generation...")
            fig = plot_section_from_ags_content(
                combined_content,
                filter_loca_ids=checked_ids,
                section_line=section_line,
                show_labels=show_labels,
                return_base64=False,  # Return matplotlib Figure object for processing
            )

            plot_generation_time = time.time()
            self.logger.info(
                f"Plot generation took: {plot_generation_time - polyline_time:.2f}s"
            )

            if fig:
                result = self._process_plot_figure(fig, triggered, download_clicks)
                total_time = time.time()
                self.logger.info(
                    f"Total plot generation time: {total_time - start_time:.2f}s"
                )
                return result
            else:
                self.logger.warning("Plot generation returned None")
                return None, None, None

        except Exception as e:
            total_time = time.time()
            self.logger.error(
                f"Error generating plot after {total_time - start_time:.2f}s: {e}"
            )
            self.error_handler.handle_callback_error(e, "plot_generation_logic")
            return None, None, None

    def _process_polyline_data(self, stored_borehole_data):
        """Process polyline data for section generation."""
        section_line = None

        if "last_polyline" in stored_borehole_data:
            # Convert polyline coordinates to format expected by section_plot
            polyline_coords = stored_borehole_data["last_polyline"]

            # Convert polyline from geographic coordinates (lat/lon) to projected coordinates (easting/northing)
            # to match the coordinate system used by LOCA_NATE/LOCA_NATN in the borehole data
            try:
                # Extract lat/lon coordinates for transformation
                lats, lons = zip(*[(lat, lon) for lat, lon in polyline_coords])

                # Transform to UTM using coordinate service
                utm_x, utm_y, utm_crs = self.coordinate_service.transform_wgs84_to_utm(
                    lons, lats
                )

                # Create section line as (easting, northing) pairs
                section_line = list(zip(utm_x, utm_y))

                self.logger.info(
                    f"Using polyline section with {len(section_line)} points"
                )
                self.logger.info(f"Polyline coords (lat/lon): {polyline_coords[:2]}...")
                self.logger.info(
                    f"Section line coords (UTM {utm_crs}): {section_line[:2]}..."
                )

            except Exception as e:
                self.logger.error(f"Error converting polyline coordinates: {e}")
                # Fallback to original method if conversion fails
                section_line = [(lon, lat) for lat, lon in polyline_coords]
                self.logger.info(
                    f"Using fallback polyline section with {len(section_line)} points"
                )

        return section_line

    def _process_plot_figure(self, fig, triggered, download_clicks):
        """Process the matplotlib figure into display and download formats."""
        try:
            # Convert to image with higher DPI for sharper text
            # CRITICAL FIX: Use bbox_inches=None to preserve exact A4 landscape proportions
            # This matches the working borehole log implementation pattern
            buf = io.BytesIO()
            fig.savefig(
                buf,
                format="png",
                bbox_inches=None,  # FIXED: Was "tight" - now preserves exact figure dimensions
                dpi=PLOT_CONFIG.PREVIEW_DPI,
            )
            buf.seek(0)
            img_bytes = buf.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            # Create a custom style that preserves aspect ratio and allows full width
            section_plot = html.Img(
                src=f"data:image/png;base64,{img_b64}",
                style=MAP_CENTER_STYLE,  # Use updated config style
            )

            # Handle download
            download_data = None
            if "download-section-btn.n_clicks" in triggered and download_clicks:
                download_data = dcc.send_bytes(img_bytes, "section_plot.png")

            return section_plot, None, download_data

        finally:
            # MEMORY LEAK FIX: Always close the figure, even if an exception occurs
            plt.close(fig)

    def _register_shape_clearing_callback(self, app):
        """Register callback to explicitly clear shapes."""

        @app.callback(
            Output("draw-control", "clear_all", allow_duplicate=True),
            Input("draw-control", "geojson"),
            prevent_initial_call=True,
        )
        def clear_all_shapes(geojson):
            """Force clearing all shapes when a new shape is drawn"""
            if geojson and geojson.get("features") and len(geojson.get("features")) > 0:
                self.logger.info(
                    f"Server-side clearing all shapes. Features: {len(geojson.get('features'))}"
                )
                # Return the current timestamp to trigger the clear_all action
                return datetime.now().timestamp()
            return dash.no_update

    def _register_map_update_clientside_callback(self, app):
        """Register client-side callback for map updates on initial load."""
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
            Output(
                "dummy-div", "children"
            ),  # Dummy output that doesn't affect anything
            Input("borehole-data-store", "data"),
            prevent_initial_call=True,
        )
