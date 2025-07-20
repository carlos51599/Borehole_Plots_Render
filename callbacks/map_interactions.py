"""
Map Interaction Callbacks

This module handles all map interaction related callbacks, including drawing,
PCA line calculation, marker color updates, and selection management.
"""

import logging
from datetime import datetime
from typing import List, Tuple, Any, Optional, Dict
import pandas as pd
from dash import html, Output, Input, State, callback_context
import dash
from sklearn.decomposition import PCA
import dash_leaflet as dl

from .base import MapInteractionCallbackBase
from map_utils import filter_selection_by_shape
from polyline_utils import (
    create_buffer_visualization,
    create_polyline_section,
    project_boreholes_to_polyline,
)
from coordinate_service import get_coordinate_service
from app_constants import MAP_CONFIG

# Marker URLs (extracted from original callbacks_split.py)
BLUE_MARKER = MAP_CONFIG.BLUE_MARKER_URL
GREEN_MARKER = MAP_CONFIG.GREEN_MARKER_URL
from error_handling import get_error_handler, ErrorCategory, ErrorSeverity
from state_management import get_app_state_manager

logger = logging.getLogger(__name__)


class MapInteractionCallback(MapInteractionCallbackBase):
    """Main map interaction callback handling drawing, selection, and updates."""

    def __init__(self):
        super().__init__("map_interactions")

    def register(self, app: dash.Dash) -> None:
        """Register the map interaction callback."""

        @app.callback(
            [
                Output("pca-line-group", "children"),
                Output("selected-borehole-info", "children"),
                Output("subselection-checkbox-grid-container", "children"),
                Output("ui-feedback", "children"),
                Output("borehole-markers", "children", allow_duplicate=True),
                Output("borehole-data-store", "data", allow_duplicate=True),
                Output("buffer-controls", "style", allow_duplicate=True),
                Output("selection-shapes", "children"),
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
            prevent_initial_call=True,
        )
        def handle_map_interactions(
            drawn_geojson,
            checked_ids,
            update_buffer_clicks,
            stored_borehole_data,
            marker_children,
            buffer_value,
        ):
            """Handle map drawing and selection."""

            try:
                self.log_callback_start(
                    {
                        "trigger": self._get_trigger(),
                        "has_geojson": bool(drawn_geojson),
                        "checked_count": len(checked_ids) if checked_ids else 0,
                    }
                )

                if not stored_borehole_data:
                    self.logger.warning("No stored borehole data available")
                    return self._empty_response(stored_borehole_data)

                ctx = callback_context
                triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None

                # Route to appropriate handler based on trigger
                if self._is_drawing_trigger(triggered, drawn_geojson):
                    result = self._handle_shape_drawing(
                        drawn_geojson,
                        stored_borehole_data,
                        marker_children,
                        buffer_value,
                    )
                elif self._is_checkbox_trigger(triggered, checked_ids):
                    result = self._handle_checkbox_selection(
                        checked_ids, stored_borehole_data
                    )
                elif self._is_buffer_trigger(
                    triggered, update_buffer_clicks, stored_borehole_data
                ):
                    result = self._handle_buffer_update(
                        stored_borehole_data, buffer_value
                    )
                else:
                    result = self._empty_response(stored_borehole_data)

                self.log_callback_end({"success": True})
                return result

            except Exception as e:
                self.logger.error(
                    f"Error in map interactions callback: {e}", exc_info=True
                )
                return self.handle_error(e, output_count=8)

    def _get_trigger(self) -> str:
        """Get the name of the triggered input."""
        ctx = callback_context
        if ctx.triggered:
            return ctx.triggered[0]["prop_id"]
        return "none"

    def _is_drawing_trigger(self, triggered: str, drawn_geojson: dict) -> bool:
        """Check if this is a drawing trigger."""
        return (
            "draw-control.geojson" in (triggered or "")
            and drawn_geojson
            and drawn_geojson.get("features")
        )

    def _is_checkbox_trigger(self, triggered: str, checked_ids: List[str]) -> bool:
        """Check if this is a checkbox trigger."""
        return "subselection-checkbox-grid.value" in (triggered or "") and checked_ids

    def _is_buffer_trigger(
        self, triggered: str, clicks: int, stored_data: dict
    ) -> bool:
        """Check if this is a buffer update trigger."""
        return (
            "update-buffer-btn.n_clicks" in (triggered or "")
            and clicks
            and stored_data.get("last_polyline")
        )

    def _empty_response(self, stored_data: dict) -> Tuple[Any, ...]:
        """Return empty response when no action is needed."""
        return (
            [],
            None,
            None,
            None,
            [],
            stored_data,
            {"display": "none"},
            [],
        )

    def _handle_shape_drawing(
        self,
        drawn_geojson: dict,
        stored_borehole_data: dict,
        marker_children: List,
        buffer_value: float,
    ) -> Tuple[Any, ...]:
        """Handle shape drawing and borehole selection."""

        self.logger.info("🎨 Processing shape drawing event")

        # Get DataFrame
        loca_df = pd.DataFrame(stored_borehole_data["loca_df"])

        # Extract features
        features = drawn_geojson.get("features", [])
        if not features:
            error_msg = html.Div("No valid shapes found", style={"color": "orange"})
            return self._error_response(stored_borehole_data, error_msg)

        # Use most recent feature
        selected_feature = features[-1]
        geom_type = selected_feature.get("geometry", {}).get("type", "unknown")
        self.logger.info(f"Processing shape type: {geom_type}")

        # Handle different geometry types
        if geom_type == "LineString":
            return self._handle_polyline_selection(
                selected_feature, loca_df, stored_borehole_data, buffer_value
            )
        else:
            return self._handle_polygon_selection(
                selected_feature, loca_df, stored_borehole_data
            )

    def _handle_polyline_selection(
        self,
        feature: dict,
        loca_df: pd.DataFrame,
        stored_data: dict,
        buffer_value: float,
    ) -> Tuple[Any, ...]:
        """Handle polyline selection with buffer."""

        # Extract coordinates
        coordinates = feature["geometry"]["coordinates"]
        polyline_coords = [[lat, lon] for lon, lat in coordinates]

        buffer_meters = buffer_value or stored_data.get(
            "buffer_meters", MAP_CONFIG.DEFAULT_BUFFER_METERS
        )

        self.logger.info(
            f"Polyline with {len(polyline_coords)} points, buffer: {buffer_meters}m"
        )

        # Filter boreholes
        filtered_df = project_boreholes_to_polyline(
            loca_df, polyline_coords, buffer_meters
        )
        borehole_ids = filtered_df["LOCA_ID"].tolist() if not filtered_df.empty else []

        # Create visualizations
        section_line = create_polyline_section(polyline_coords)
        buffer_zone = create_buffer_visualization(polyline_coords, buffer_meters)

        # Combine line elements
        line_elements = []
        if isinstance(section_line, list):
            line_elements.extend(section_line)
        elif section_line:
            line_elements.append(section_line)

        if buffer_zone:
            line_elements.append(buffer_zone)

        # Update stored data
        updated_data = dict(stored_data)
        updated_data.update(
            {
                "selection_boreholes": borehole_ids,
                "polyline_feature": feature,
                "last_polyline": polyline_coords,
                "is_polyline": True,
                "buffer_meters": buffer_meters,
            }
        )

        # Update state manager
        state_manager = get_app_state_manager()
        state_manager.update_selection_state(
            selected_borehole_ids=borehole_ids,
            selection_method="polyline",
            last_polyline=polyline_coords,
            buffer_meters=buffer_meters,
            is_polyline_selection=True,
        )

        return self._success_response(
            line_elements=line_elements,
            borehole_ids=borehole_ids,
            updated_data=updated_data,
            feedback=f"Selected {len(borehole_ids)} boreholes along polyline",
            buffer_controls_visible=True,
        )

    def _handle_polygon_selection(
        self,
        feature: dict,
        loca_df: pd.DataFrame,
        stored_data: dict,
    ) -> Tuple[Any, ...]:
        """Handle polygon/rectangle selection."""

        # Create single-feature GeoJSON
        single_feature_geojson = {
            "type": "FeatureCollection",
            "features": [feature],
        }

        # Filter boreholes
        filtered_result = filter_selection_by_shape(loca_df, single_feature_geojson)

        # Handle different return types from filter function
        borehole_ids = []
        if isinstance(filtered_result, pd.DataFrame) and not filtered_result.empty:
            borehole_ids = filtered_result["LOCA_ID"].tolist()
        elif isinstance(filtered_result, list):
            borehole_ids = filtered_result

        # Create PCA line if we have enough points
        pca_line = []
        if len(borehole_ids) >= 2:
            filtered_df = loca_df[loca_df["LOCA_ID"].isin(borehole_ids)]
            pca_line = self._calculate_pca_line(filtered_df)

        # Update stored data
        updated_data = dict(stored_data)
        updated_data.update(
            {
                "selection_boreholes": borehole_ids,
                "is_polyline": False,
            }
        )

        # Update state manager
        state_manager = get_app_state_manager()
        state_manager.update_selection_state(
            selected_borehole_ids=borehole_ids,
            selection_method="shape",
        )

        return self._success_response(
            line_elements=pca_line,
            borehole_ids=borehole_ids,
            updated_data=updated_data,
            feedback=f"Selected {len(borehole_ids)} boreholes in shape",
            buffer_controls_visible=False,
        )

    def _handle_checkbox_selection(
        self, checked_ids: List[str], stored_data: dict
    ) -> Tuple[Any, ...]:
        """Handle checkbox selection changes."""

        self.logger.info("☑️ Processing checkbox selection")

        loca_df = pd.DataFrame(stored_data["loca_df"])

        # Use existing shape selection if available
        shape_selected_ids = stored_data.get("selection_boreholes", checked_ids)

        # Filter to checked boreholes
        filtered_df = loca_df[loca_df["LOCA_ID"].isin(checked_ids)]

        # Create appropriate line visualization
        if stored_data.get("last_polyline"):
            # Keep existing polyline visualization
            polyline_coords = stored_data["last_polyline"]
            buffer_meters = stored_data.get(
                "buffer_meters", MAP_CONFIG.DEFAULT_BUFFER_METERS
            )

            section_line = create_polyline_section(polyline_coords)
            buffer_zone = create_buffer_visualization(polyline_coords, buffer_meters)

            line_elements = []
            if isinstance(section_line, list):
                line_elements.extend(section_line)
            elif section_line:
                line_elements.append(section_line)

            if buffer_zone:
                line_elements.append(buffer_zone)

            buffer_controls_visible = True
        else:
            # Use PCA line
            line_elements = self._calculate_pca_line(filtered_df)
            buffer_controls_visible = False

        # Update state manager
        state_manager = get_app_state_manager()
        state_manager.update_selection_state(
            selected_borehole_ids=checked_ids,
            selection_method="checkbox",
        )

        return self._success_response(
            line_elements=line_elements,
            borehole_ids=checked_ids,
            updated_data=stored_data,
            feedback=f"Using {len(checked_ids)} selected boreholes",
            buffer_controls_visible=buffer_controls_visible,
            shape_selected_ids=shape_selected_ids,
        )

    def _handle_buffer_update(
        self, stored_data: dict, buffer_value: float
    ) -> Tuple[Any, ...]:
        """Handle buffer distance update."""

        self.logger.info(f"📏 Updating buffer to {buffer_value}m")

        polyline_coords = stored_data["last_polyline"]
        loca_df = pd.DataFrame(stored_data["loca_df"])

        # Re-filter with new buffer
        filtered_df = project_boreholes_to_polyline(
            loca_df, polyline_coords, buffer_value
        )
        new_borehole_ids = (
            filtered_df["LOCA_ID"].tolist() if not filtered_df.empty else []
        )

        # Create new visualizations
        section_line = create_polyline_section(polyline_coords)
        buffer_zone = create_buffer_visualization(polyline_coords, buffer_value)

        line_elements = []
        if isinstance(section_line, list):
            line_elements.extend(section_line)
        elif section_line:
            line_elements.append(section_line)

        if buffer_zone:
            line_elements.append(buffer_zone)

        # Update stored data
        updated_data = dict(stored_data)
        updated_data.update(
            {
                "buffer_meters": buffer_value,
                "selection_boreholes": new_borehole_ids,
            }
        )

        return self._success_response(
            line_elements=line_elements,
            borehole_ids=new_borehole_ids,
            updated_data=updated_data,
            feedback=f"Updated buffer to {buffer_value}m - {len(new_borehole_ids)} boreholes selected",
            buffer_controls_visible=True,
        )

    def _calculate_pca_line(self, filtered_df: pd.DataFrame) -> List:
        """Calculate and create PCA line for display."""

        if len(filtered_df) < 2:
            self.logger.info("Less than 2 points for PCA line calculation")
            return []

        try:
            # Use BNG coordinates for PCA
            bng_coords = filtered_df[["LOCA_NATE", "LOCA_NATN"]].values
            self.logger.info(f"Calculating PCA line for {len(bng_coords)} points")

            pca = PCA(n_components=2)
            pca_coords = pca.fit_transform(bng_coords)
            mean_coords = bng_coords.mean(axis=0)
            direction = pca.components_[0]

            # Calculate line extent
            length = max(pca_coords[:, 0]) - min(pca_coords[:, 0])
            extension = length * 0.2  # Extend 20% beyond points

            # Calculate endpoints in BNG
            start_bng = mean_coords - direction * (length / 2 + extension)
            end_bng = mean_coords + direction * (length / 2 + extension)

            # Transform to WGS84
            coordinate_service = get_coordinate_service()
            start_lat, start_lon = coordinate_service.transform_bng_to_wgs84(
                [start_bng[0]], [start_bng[1]]
            )
            end_lat, end_lon = coordinate_service.transform_bng_to_wgs84(
                [end_bng[0]], [end_bng[1]]
            )

            return [
                dl.Polyline(
                    positions=[[start_lat[0], start_lon[0]], [end_lat[0], end_lon[0]]],
                    color="red",
                    weight=3,
                    opacity=0.8,
                    dashArray="5, 5",
                    children=dl.Tooltip("Extended PCA section line"),
                )
            ]

        except Exception as e:
            self.logger.error(f"Error calculating PCA line: {e}")
            return []

    def _create_checkbox_grid(
        self, borehole_ids: List[str], current_checked: List[str]
    ) -> html.Div:
        """Create checkbox grid for borehole selection."""

        import config
        from dash import dcc

        # Ensure checked IDs are valid
        valid_checked = [bid for bid in current_checked if bid in borehole_ids]

        return html.Div(
            [
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

    def _update_marker_colors(self, stored_data: dict, selected_ids: List[str]) -> List:
        """Update marker colors based on selection using lazy loading."""

        if not stored_data:
            return []

        try:
            # Import lazy marker manager
            from lazy_marker_manager import get_lazy_marker_manager, ViewportBounds

            loca_df = pd.DataFrame(stored_data["loca_df"])

            # Get viewport info if available (for future viewport-based optimization)
            # For now, we'll use the smart loading based on dataset size
            lazy_manager = get_lazy_marker_manager()

            # Determine if we should render all markers or use lazy loading
            force_all = len(loca_df) <= 100  # Render all for small datasets

            markers = lazy_manager.get_visible_markers(
                loca_df=loca_df,
                viewport=None,  # TODO: Get from map state in future optimization
                selected_ids=selected_ids,
                force_all=force_all,
            )

            self.logger.info(
                f"Lazy marker update: {len(markers)} markers rendered for {len(loca_df)} total boreholes"
            )
            return markers

        except Exception as e:
            self.logger.error(f"Error in lazy marker update: {e}")
            # Fallback to original implementation
            return self._update_marker_colors_fallback(stored_data, selected_ids)

    def _update_marker_colors_fallback(
        self, stored_data: dict, selected_ids: List[str]
    ) -> List:
        """Fallback marker update method (original implementation)."""

        try:
            loca_df = pd.DataFrame(stored_data["loca_df"])
            markers = []

            for i, row in loca_df.iterrows():
                lat = row.get("lat")
                lon = row.get("lon")

                if pd.isna(lat) or pd.isna(lon):
                    continue

                borehole_id = str(row["LOCA_ID"]).strip()
                is_selected = borehole_id in selected_ids

                # Choose marker color
                icon_url = GREEN_MARKER if is_selected else BLUE_MARKER

                marker_id = {"type": "borehole-marker", "index": i}

                # Format tooltip
                ground_level = self._format_depth_value(row.get("LOCA_GL", "N/A"))
                total_depth = self._format_depth_value(row.get("LOCA_FDEP", "N/A"))

                tooltip_text = f"""
                Borehole: {borehole_id}
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

            return markers

        except Exception as e:
            self.logger.error(f"Error in fallback marker update: {e}")
            return []

    def _format_depth_value(self, value) -> str:
        """Format depth values for display."""

        if value == "N/A" or value is None or str(value).strip() == "":
            return "N/A"

        try:
            return f"{float(value):.2f}m"
        except (ValueError, TypeError):
            return "N/A"

    def _success_response(
        self,
        line_elements: List,
        borehole_ids: List[str],
        updated_data: dict,
        feedback: str,
        buffer_controls_visible: bool,
        shape_selected_ids: Optional[List[str]] = None,
    ) -> Tuple[Any, ...]:
        """Create a successful response tuple."""

        # Use shape_selected_ids for checkbox grid, borehole_ids for feedback
        checkbox_ids = (
            shape_selected_ids if shape_selected_ids is not None else borehole_ids
        )

        checkbox_grid = self._create_checkbox_grid(checkbox_ids, borehole_ids)
        updated_markers = self._update_marker_colors(updated_data, borehole_ids)
        feedback_div = html.Div(feedback)
        buffer_style = (
            {"display": "block"} if buffer_controls_visible else {"display": "none"}
        )

        return (
            line_elements,
            None,
            checkbox_grid,
            feedback_div,
            updated_markers,
            updated_data,
            buffer_style,
            [],  # Selection shapes cleared
        )

    def _error_response(
        self, stored_data: dict, error_msg: html.Div
    ) -> Tuple[Any, ...]:
        """Create an error response tuple."""

        updated_markers = self._update_marker_colors(stored_data, [])

        return (
            [],
            None,
            None,
            error_msg,
            updated_markers,
            stored_data,
            {"display": "none"},
            [],
        )


def register_map_interaction_callbacks(callback_manager):
    """Register all map interaction related callbacks."""

    callback_manager.add_callback(MapInteractionCallback())
    logger.info("Registered map interaction callbacks")
