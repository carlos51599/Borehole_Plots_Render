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

import config
from data_loader import load_all_loca_data
from map_utils import filter_selection_by_shape
from section_plot import plot_section_from_ags_content

matplotlib.use("Agg")


# Define marker icon URLs
BLUE_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
GREEN_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"


def transform_coordinates(easting, northing):
    """Transform BNG to WGS84 coordinates (imported from main app)"""
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    try:
        lon, lat = transformer.transform(easting, northing)
        return lat, lon
    except Exception as e:
        logging.error(f"Error transforming coordinates: {e}")
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

                        # Create marker
                        label = str(row["LOCA_ID"])
                        marker_id = {"type": "borehole-marker", "index": i}
                        markers.append(
                            dl.Marker(
                                id=marker_id,
                                position=[lat, lon],
                                children=dl.Tooltip(label),
                                icon={"iconUrl": BLUE_MARKER},
                                n_clicks=0,
                            )
                        )
                        valid_coords.append((lat, lon))

                except Exception as e:
                    logging.warning(f"Skipping marker for row {i}: {e}")

            # Auto-zoom to show all markers
            if valid_coords:
                lats = [coord[0] for coord in valid_coords]
                lons = [coord[1] for coord in valid_coords]
                map_center = [statistics.mean(lats), statistics.mean(lons)]
                map_zoom = 12

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
            Output("draw-control", "geojson"),  # Add this back to clear previous shapes
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
            return [], None, None, None, dash.no_update

        # Drawing triggered
        if (
            "draw-control.geojson" in triggered
            and drawn_geojson
            and drawn_geojson.get("features")
        ):
            logging.info("Processing drawing event")
            result = handle_shape_drawing(
                drawn_geojson, stored_borehole_data, marker_children
            )
            # Add the cleared geojson to the result
            return result + (get_latest_shape_geojson(drawn_geojson),)

        # Checkbox selection triggered
        elif "subselection-checkbox-grid.value" in triggered and checked_ids:
            result = handle_checkbox_selection(checked_ids, stored_borehole_data)
            return result + (dash.no_update,)

        return [], None, None, None, dash.no_update

    def handle_shape_drawing(drawn_geojson, stored_borehole_data, marker_children):
        """Handle shape drawing and borehole selection"""
        try:
            # Reconstruct DataFrame
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            logging.info(f"Processing shape with {len(loca_df)} boreholes")

            # Get the single feature (we've already validated there's exactly one)
            features = drawn_geojson.get("features", [])
            if not features:
                logging.warning("No features found in drawn GeoJSON")
                return [], None, None, html.Div("No valid shapes found")

            selected_feature = features[0]  # Use the single feature
            geom_type = selected_feature.get("geometry", {}).get("type", "unknown")
            logging.info(f"Processing {geom_type} for borehole selection")

            # Filter by the selected shape
            filtered_result = filter_selection_by_shape(loca_df, drawn_geojson)
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

                feedback = html.Div(
                    f"Selected {len(borehole_ids)} boreholes from {geom_type}"
                )

                return (
                    pca_line,
                    None,
                    checkbox_grid,
                    feedback,
                )
            else:
                feedback = html.Div(
                    "No boreholes found in selection",
                    style=config.WARNING_MESSAGE_STYLE,
                )
                return (
                    [],
                    None,
                    None,
                    feedback,
                )

        except Exception as e:
            logging.error(f"Error in shape drawing: {e}")
            error_msg = html.Div(
                f"Selection error: {e}", style=config.ERROR_MESSAGE_STYLE
            )
            return (
                [],
                None,
                None,
                error_msg,
            )

    def handle_checkbox_selection(checked_ids, stored_borehole_data):
        """Handle checkbox selection changes"""
        try:
            loca_df = pd.DataFrame(stored_borehole_data["loca_df"])
            filtered_df = loca_df[loca_df["LOCA_ID"].isin(checked_ids)]

            # Calculate PCA line for checked boreholes
            pca_line = calculate_pca_line(filtered_df)

            feedback = html.Div(f"Using {len(checked_ids)} selected boreholes")

            return pca_line, None, None, feedback

        except Exception as e:
            logging.error(f"Error in checkbox selection: {e}")
            return [], None, None, None

    def calculate_pca_line(filtered_df):
        """Calculate and create PCA line for display"""
        if len(filtered_df) < 2:
            return []

        try:
            # Use BNG coordinates for PCA (as in original Streamlit)
            bng_coords = filtered_df[["LOCA_NATE", "LOCA_NATN"]].values

            pca = PCA(n_components=2)
            pca_coords = pca.fit_transform(bng_coords)
            mean_coords = bng_coords.mean(axis=0)
            direction = pca.components_[0]

            # Calculate line extent
            length = max(pca_coords[:, 0]) - min(pca_coords[:, 0])
            buffer = 0.2 * length

            # Calculate start and end points in BNG
            start_bng = mean_coords + direction * (-length / 2 - buffer)
            end_bng = mean_coords + direction * (length / 2 + buffer)

            # Transform to lat/lon
            start_lat, start_lon = transform_coordinates(start_bng[0], start_bng[1])
            end_lat, end_lon = transform_coordinates(end_bng[0], end_bng[1])

            if start_lat and start_lon and end_lat and end_lon:
                return [
                    dl.Polyline(
                        positions=[[start_lat, start_lon], [end_lat, end_lon]],
                        color="red",
                        weight=3,
                        opacity=0.8,
                        dashArray="5, 5",
                        children=[dl.Tooltip("PCA section line")],
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

    def update_marker_colors(marker_children, selected_ids, loca_df):
        """Update marker colors (green for selected, blue for unselected)"""
        # This would be handled by a separate callback that listens to selection changes
        # For now, we'll implement this in the plot callback
        pass

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

    logging.info("✅ All split callbacks registered successfully!")


def get_latest_shape_geojson(drawn_geojson):
    """Return GeoJSON with only the latest drawn shape to clear previous shapes"""
    if not drawn_geojson or not drawn_geojson.get("features"):
        return {"type": "FeatureCollection", "features": []}

    features = drawn_geojson.get("features", [])
    if not features:
        return {"type": "FeatureCollection", "features": []}

    # Find the most recently created feature (highest ID or most recent timestamp)
    latest_feature = features[-1]  # Assume the last feature is the most recent

    # Return GeoJSON with only the latest feature
    return {"type": "FeatureCollection", "features": [latest_feature]}
