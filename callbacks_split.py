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
from section_plot import plot_section_from_ags_content

matplotlib.use("Agg")


# Define marker icon URLs
BLUE_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
GREEN_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"


def transform_coordinates(easting, northing):
    """Transform BNG to WGS84 coordinates with detailed logging"""
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    try:
        # Transform coordinates
        lon, lat = transformer.transform(easting, northing)

        # Add detailed logging for debugging
        logging.debug(
            f"Coordinate transform: BNG({easting}, {northing}) -> WGS84({lat:.6f}, {lon:.6f})"
        )

        # Validate the transformed coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logging.error(f"Invalid transformed coordinates: lat={lat}, lon={lon}")
            return None, None

        return lat, lon
    except Exception as e:
        logging.error(f"Error transforming coordinates BNG({easting}, {northing}): {e}")
        return None, None


def register_callbacks(app):
    """Register all split callbacks with the app"""

    # ====================================================================
    # CALLBACK 1: FILE UPLOAD HANDLING (Clean & Focused)
    # ====================================================================
    @app.callback(
        [
            Output("output-upload", "children"),
            Output("borehole-markers", "children"),
            Output("borehole-map", "center"),
            Output("borehole-map", "zoom"),
            Output("borehole-data-store", "data"),
        ],
        [Input("upload-data-store", "data")],
        [State("borehole-map", "center"), State("borehole-map", "zoom")],
    )
    def handle_file_upload(stored_data, map_center_state, map_zoom_state):
        """Handle file upload and create markers"""
        logging.info("=== FILE UPLOAD CALLBACK ===")

        # Default values
        map_center = map_center_state or [51.5, -0.1]
        map_zoom = map_zoom_state or 6

        if not stored_data or "contents" not in stored_data:
            logging.info("No file uploaded yet")
            return None, [], map_center, map_zoom, None

        try:
            # Process uploaded files
            list_of_contents = stored_data["contents"]
            list_of_names = stored_data["filenames"]
            logging.info(f"Processing {len(list_of_contents)} uploaded files")

            ags_files = []
            file_status = []

            for content, name in zip(list_of_contents, list_of_names or []):
                try:
                    content_type, content_string = content.split(",")
                    decoded = base64.b64decode(content_string)
                    s = decoded.decode("utf-8")
                    ags_files.append((name, s))
                    file_status.append(html.Div([f"Uploaded: {name}"]))
                    logging.info(f"Successfully processed file: {name}")
                except Exception as e:
                    logging.error(f"Error reading {name}: {e}")
                    file_status.append(html.Div([f"Error reading {name}: {e}"]))

            # Load and process data
            loca_df, filename_map = load_all_loca_data(ags_files)
            logging.info(f"Loaded {len(loca_df)} boreholes")

            # Create markers
            markers = []
            valid_coords = []

            for i, row in loca_df.iterrows():
                try:
                    easting = float(row["LOCA_NATE"])
                    northing = float(row["LOCA_NATN"])
                    lat, lon = transform_coordinates(easting, northing)

                    if lat and lon:
                        # Store transformed coordinates
                        loca_df.at[i, "lat"] = lat
                        loca_df.at[i, "lon"] = lon

                        # Create marker with proper icon configuration
                        label = str(row["LOCA_ID"])
                        marker_id = {"type": "borehole-marker", "index": i}

                        # Use more detailed icon configuration for better positioning
                        marker_icon = {
                            "iconUrl": BLUE_MARKER,
                            "iconSize": [25, 41],  # Standard Leaflet marker size
                            "iconAnchor": [
                                12,
                                41,
                            ],  # Point of the icon which will correspond to marker's location
                            "popupAnchor": [
                                1,
                                -34,
                            ],  # Point from which the popup should open relative to the iconAnchor
                            "shadowSize": [41, 41],  # Size of the shadow
                        }

                        markers.append(
                            dl.Marker(
                                id=marker_id,
                                position=[lat, lon],  # Ensure this is [lat, lon] order
                                children=dl.Tooltip(label),
                                icon=marker_icon,
                                n_clicks=0,
                            )
                        )
                        valid_coords.append((lat, lon))

                        # Log first few markers for debugging
                        if i < 3:
                            logging.info(
                                f"Marker {i} ({label}): BNG({easting}, {northing}) -> Position([{lat:.6f}, {lon:.6f}])"
                            )

                except Exception as e:
                    logging.warning(f"Skipping marker for row {i}: {e}")

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
                    f"Map centering: Median coords ({median_lat:.6f}, {median_lon:.6f}), "
                    f"Range: {coord_range:.6f}, Zoom: {map_zoom}"
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
                        html.Li([html.B(filename), f": {len(file_rows)} boreholes"])
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

            return file_status, markers, map_center, map_zoom, borehole_data

        except Exception as e:
            logging.error(f"Error in file upload: {e}")
            error_msg = html.Div([f"Error processing files: {e}"])
            return [error_msg], [], map_center, map_zoom, None

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
        ],
        [
            Input("draw-control", "geojson"),
            Input("subselection-checkbox-grid", "value"),
        ],
        [
            State("borehole-data-store", "data"),
            State("borehole-markers", "children"),
        ],
        prevent_initial_call=True,  # Prevent triggering on initial load
    )
    def handle_map_interactions(
        drawn_geojson, checked_ids, stored_borehole_data, marker_children
    ):
        """Handle map drawing and selection"""
        logging.info("=== MAP INTERACTION CALLBACK ===")

        ctx = dash.callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None
        logging.info(f"Triggered by: {triggered}")

        if not stored_borehole_data:
            logging.warning("No stored borehole data available")
            return [], None, None, None, []

        # Drawing triggered
        if (
            "draw-control.geojson" in triggered
            and drawn_geojson
            and drawn_geojson.get("features")
        ):
            logging.info("Processing drawing event")
            return handle_shape_drawing(
                drawn_geojson, stored_borehole_data, marker_children
            )

        # Checkbox selection triggered
        elif "subselection-checkbox-grid.value" in triggered and checked_ids:
            return handle_checkbox_selection(checked_ids, stored_borehole_data)

        return [], None, None, None, []

    def handle_shape_drawing(drawn_geojson, stored_borehole_data, marker_children):
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
            filtered_result = filter_selection_by_shape(loca_df, single_feature_geojson)
            logging.info(f"filter_selection_by_shape returned: {type(filtered_result)}")

            # Handle both DataFrame and list return types (like in original megacallback)
            borehole_ids = []
            if isinstance(filtered_result, pd.DataFrame):
                if not filtered_result.empty:
                    borehole_ids = filtered_result["LOCA_ID"].tolist()
                    logging.info(
                        f"Extracted {len(borehole_ids)} LOCA_IDs from DataFrame"
                    )
            elif isinstance(filtered_result, list):
                borehole_ids = filtered_result
                logging.info(f"Got {len(borehole_ids)} LOCA_IDs directly from filter")
            else:
                logging.warning(f"Unexpected return type: {type(filtered_result)}")

            if borehole_ids:
                logging.info(f"Selected {len(borehole_ids)} boreholes: {borehole_ids}")

                # Calculate PCA line (need to get the filtered DataFrame for PCA)
                if isinstance(filtered_result, pd.DataFrame):
                    pca_line = calculate_pca_line(filtered_result)
                else:
                    # If we got a list, filter the original DataFrame
                    filtered_df = loca_df[loca_df["LOCA_ID"].isin(borehole_ids)]
                    pca_line = calculate_pca_line(filtered_df)

                # Create checkbox grid
                checkbox_grid = create_checkbox_grid(borehole_ids, borehole_ids)

                # Create detailed feedback message with status info
                total_boreholes = len(stored_borehole_data.get("all_borehole_ids", []))
                blue_markers = total_boreholes - len(borehole_ids)
                feedback = html.Div(
                    [
                        html.H4(
                            "🎯 Selection Status:",
                            style={"color": "#28a745", "margin-bottom": "5px"},
                        ),
                        html.P(
                            f"• Selected {len(borehole_ids)} boreholes from {geom_type}"
                        ),
                        html.P(f"• Borehole IDs: {', '.join(borehole_ids)}"),
                        html.P(f"• PCA line extended with buffer: {len(pca_line) > 0}"),
                        html.P(
                            f"• Markers updated: {len(borehole_ids)} green, {blue_markers} blue"
                        ),
                    ],
                    style={
                        "background-color": "#d4edda",
                        "padding": "10px",
                        "border-radius": "5px",
                        "border": "1px solid #c3e6cb",
                    },
                )

                # Update marker colors - green for selected, blue for others
                updated_markers = update_marker_colors(
                    stored_borehole_data, borehole_ids
                )

                return (
                    pca_line,
                    None,
                    checkbox_grid,
                    feedback,
                    updated_markers,
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
            )

    def handle_checkbox_selection(checked_ids, stored_borehole_data):
        """Handle checkbox selection changes"""
        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            filtered_df = loca_df[loca_df["LOCA_ID"].isin(checked_ids)]

            # Calculate PCA line for checked boreholes
            pca_line = calculate_pca_line(filtered_df)

            feedback = html.Div(f"Using {len(checked_ids)} selected boreholes")

            # Update marker colors based on checkbox selection
            updated_markers = update_marker_colors(stored_borehole_data, checked_ids)

            return pca_line, None, None, feedback, updated_markers

        except Exception as e:
            logging.error(f"Error in checkbox selection: {e}")
            # Return markers with all blue (no selection) on error
            updated_markers = update_marker_colors(stored_borehole_data, [])
            return [], None, None, None, updated_markers

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

            # Transform to lat/lon
            start_lat, start_lon = transform_coordinates(start_bng[0], start_bng[1])
            end_lat, end_lon = transform_coordinates(end_bng[0], end_bng[1])

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
                        children=[dl.Tooltip("Extended PCA section line")],
                    )
                ]

        except Exception as e:
            logging.error(f"Error calculating PCA line: {e}")

        return []

    def create_checkbox_grid(borehole_ids, current_checked):
        """Create checkbox grid for borehole selection"""
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
                    value=current_checked,
                    labelStyle=config.CHECKBOX_LABEL_STYLE,
                    style=config.CHECKBOX_LEFT_STYLE,
                ),
            ]
        )

    def update_marker_colors(stored_borehole_data, selected_ids):
        """Update marker colors based on selection - green for selected, blue for unselected"""
        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            markers = []

            for i, row in loca_df.iterrows():
                try:
                    lat = row.get("lat")
                    lon = row.get("lon")
                    loca_id = str(row["LOCA_ID"])

                    if lat and lon:
                        # Determine marker color based on selection
                        is_selected = loca_id in (selected_ids or [])
                        icon_url = GREEN_MARKER if is_selected else BLUE_MARKER

                        # Create marker with appropriate color
                        marker_id = {"type": "borehole-marker", "index": i}
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
                                children=dl.Tooltip(loca_id),
                                icon=marker_icon,
                                n_clicks=0,
                            )
                        )

                except Exception as e:
                    logging.warning(f"Error creating marker for row {i}: {e}")

            logging.info(
                f"Updated {len(markers)} markers, {len(selected_ids or [])} selected (green)"
            )
            return markers

        except Exception as e:
            logging.error(f"Error updating marker colors: {e}")
            return []

    # ====================================================================
    # CALLBACK 3: PLOT GENERATION (Section Plots & Downloads)
    # ====================================================================
    @app.callback(
        [
            Output("section-plot-output", "children"),
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
    )
    def handle_plot_generation(
        checked_ids, show_labels_value, download_clicks, stored_borehole_data
    ):
        """Handle plot generation and downloads"""
        logging.info("=== PLOT GENERATION CALLBACK ===")

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

            # Generate section plot
            fig = plot_section_from_ags_content(
                combined_content, checked_ids, show_labels=show_labels
            )

            if fig:
                # Convert to image
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                plt.close(fig)
                buf.seek(0)
                img_bytes = buf.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")

                section_plot = html.Img(
                    src=f"data:image/png;base64,{img_b64}",
                    style=config.SECTION_PLOT_CENTER_STYLE,
                )

                # Handle download
                download_data = None
                if "download-section-btn.n_clicks" in triggered and download_clicks:
                    download_data = dcc.send_bytes(img_bytes, "section_plot.png")

                return section_plot, None, download_data
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

    logging.info("✅ All split callbacks registered successfully!")
