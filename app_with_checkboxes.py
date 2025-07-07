import dash
from dash import html, dcc, Output, Input, State, ALL
import dash_leaflet as dl
from dash_leaflet import EditControl

import base64
import io
import logging
import sys
import traceback
import json
import statistics
import webbrowser
from datetime import datetime
from pyproj import Transformer
import pandas as pd

import matplotlib
from data_loader import load_all_loca_data
from map_utils import filter_selection_by_shape

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from section_plot import plot_section_from_ags_content
from borehole_log import plot_borehole_log_from_ags_content

# Set up enhanced logging format with detailed context
logfile = "app_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d %(funcName)s] %(message)s",
    handlers=[
        logging.FileHandler(logfile, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),  # Also log to console
    ],
)

# Create root logger and make it extremely verbose
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Log app startup
logging.info(f"App starting at {datetime.now()}")
logging.info(f"Dash version: {dash.__version__}")
logging.info(f"Dash-leaflet version: {dl.__version__}")

# Create coordinate transformer from British National Grid (EPSG:27700) to WGS84 (EPSG:4326)
# This converts the projected coordinates typically found in UK AGS files to lat/lon for Leaflet
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def transform_coordinates(easting, northing):
    """
    Transform British National Grid coordinates to WGS84 lat/lon

    Args:
        easting (float): BNG easting coordinate
        northing (float): BNG northing coordinate

    Returns:
        tuple: (latitude, longitude) in WGS84
    """
    try:
        logging.debug(
            f"Transforming coordinates: easting={easting}, northing={northing}"
        )

        # Validate input coordinates are reasonable for BNG
        if not (0 <= easting <= 800000):
            logging.warning(f"Easting {easting} outside typical BNG range [0, 800000]")
        if not (0 <= northing <= 1400000):
            logging.warning(
                f"Northing {northing} outside typical BNG range [0, 1400000]"
            )

        # Transform from BNG (easting, northing) to WGS84 (lon, lat)
        # Note: pyproj returns (longitude, latitude) when always_xy=True
        lon, lat = transformer.transform(easting, northing)

        logging.debug(f"Transformed result: lat={lat:.6f}, lon={lon:.6f}")

        # Validate output coordinates are reasonable for UK
        if not (49.0 <= lat <= 61.0):
            logging.warning(
                f"Transformed latitude {lat:.6f} outside UK range [49.0, 61.0]"
            )
        if not (-8.0 <= lon <= 2.0):
            logging.warning(
                f"Transformed longitude {lon:.6f} outside UK range [-8.0, 2.0]"
            )

        return lat, lon
    except Exception as e:
        logging.error(f"Error transforming coordinates ({easting}, {northing}): {e}")
        return None, None


app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Log layout creation
logging.info("Creating app layout...")

app.layout = html.Div(
    [
        html.H1("Geo Borehole Sections Render - Dash Version"),
        html.P("Upload one or more AGS files to begin."),
        dcc.Upload(
            id="upload-ags",
            children=html.Div(["Drag and Drop or ", html.A("Select AGS Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
            accept=".ags",
        ),
        html.Div(id="output-upload"),
        html.Hr(),
        html.Div(
            [
                html.H2("Borehole Map"),
                dl.Map(
                    [
                        dl.TileLayer(),
                        dl.FeatureGroup(
                            [
                                # Markers will be added dynamically, but always keep an empty list if none
                            ],
                            id="borehole-markers",
                        ),
                        dl.FeatureGroup(
                            [
                                EditControl(
                                    id="draw-control",
                                    draw={
                                        "polyline": True,
                                        "polygon": True,
                                        "circle": False,
                                        "rectangle": True,
                                        "marker": False,
                                    },
                                    edit={"edit": True, "remove": True},
                                ),
                            ],
                            id="draw-feature-group",
                        ),
                    ],
                    id="borehole-map",
                    center=[51.5, -0.1],
                    zoom=6,
                    style={"width": "100%", "height": "500px"},
                ),
            ]
        ),
        html.Div(id="selected-borehole-info"),
        html.Div(id="section-plot-output"),
        html.Div(id="log-plot-output"),
        html.Div(
            [
                dcc.Checklist(
                    id="show-labels-checkbox",
                    options=[{"label": "Labels", "value": "show_labels"}],
                    value=["show_labels"],
                    inline=True,
                    style={"marginTop": "1em"},
                ),
                html.Button(
                    "Download Section Plot",
                    id="download-section-btn",
                    n_clicks=0,
                    style={"marginLeft": "1em"},
                ),
                dcc.Download(id="download-section-plot"),
            ]
        ),
        html.Div(id="ui-feedback"),
        html.Div(id="subselection-checkbox-grid-container", children=[]),
        dcc.Checklist(
            id="subselection-checkbox-grid",
            options=[],
            value=[],
            style={"display": "none"},
        ),
        html.Div(
            id="test-upload-output",
            style={
                "margin": "15px",
                "padding": "10px",
                "border": "1px solid #ddd",
                "background-color": "#f9f9f9",
            },
        ),  # Output for test callback
        # Add a dcc.Store component to reliably store the uploaded file data
        dcc.Store(id="upload-data-store"),
        # Add a dcc.Store component to store processed borehole data for drawing operations
        dcc.Store(id="borehole-data-store"),
    ]
)

# Log layout creation
logging.info("App layout created successfully")
logging.info("Registering callbacks...")


# Modified main callback to use the stored upload data and handle checkbox changes
@app.callback(
    [
        Output("output-upload", "children"),
        Output("borehole-markers", "children"),
        Output("selected-borehole-info", "children"),
        Output("borehole-map", "center"),
        Output("borehole-map", "zoom"),  # Add zoom control
        Output("section-plot-output", "children"),
        Output("log-plot-output", "children"),
        Output("download-section-plot", "data"),
        Output("ui-feedback", "children"),
        Output("subselection-checkbox-grid-container", "children"),
        Output("borehole-data-store", "data"),  # Add borehole data storage
    ],
    [
        Input("upload-data-store", "data"),  # File upload trigger
        Input(
            "draw-control", "geojson"
        ),  # Drawing tool trigger (use geojson, not n_clicks)
        Input("show-labels-checkbox", "value"),
        Input("download-section-btn", "n_clicks"),
        Input({"type": "borehole-marker", "index": ALL}, "n_clicks"),
        Input("subselection-checkbox-grid", "value"),  # Checkbox changes trigger
    ],
    [
        State("borehole-markers", "children"),
        State("section-plot-output", "children"),
        State("borehole-map", "center"),
        State("borehole-map", "zoom"),
        State("borehole-data-store", "data"),  # Add stored borehole data
    ],
)
def handle_upload_and_draw(
    stored_data,  # Input("upload-data-store", "data")
    drawn_geojson,  # Input("draw-control", "geojson") - Fixed to use geojson
    show_labels_value,  # Input("show-labels-checkbox", "value")
    download_n_clicks,  # Input("download-section-btn", "n_clicks")
    marker_clicks,  # Input({"type": "borehole-marker", "index": ALL}, "n_clicks")
    checked_ids,  # Input("subselection-checkbox-grid", "value") - Checkbox changes trigger
    marker_children,  # State("borehole-markers", "children")
    section_plot_img,  # State("section-plot-output", "children")
    map_center_state,  # State("borehole-map", "center")
    map_zoom_state,  # State("borehole-map", "zoom")
    stored_borehole_data,  # State("borehole-data-store", "data")
):
    # Log successful callback registration
    logging.info("Main callback successfully registered and called!")
    logging.info(f"Callback parameters - upload data type: {type(stored_data)}")

    selected_info = None
    section_plot_img_out = None
    log_plot_img = None
    download_data = None
    ui_feedback = None
    checkbox_grid = None
    show_labels = "show_labels" in (show_labels_value or [])

    # Default map settings - only change these when uploading files or first load
    map_center = map_center_state or [51.5, -0.1]  # Use current center, or default
    map_zoom = map_zoom_state or 6  # Use current zoom, or default

    # Initialize borehole data storage
    borehole_data_out = stored_borehole_data  # Keep existing data by default

    # Enhanced debug logging
    logging.info("===== MAIN CALLBACK TRIGGERED =====")
    logging.info(f"Current time: {datetime.now()}")
    logging.debug(f"- stored_data: {type(stored_data)}")
    if stored_data:
        logging.debug(
            f"  - stored_data keys: {stored_data.keys() if isinstance(stored_data, dict) else 'not a dict'}"
        )
    logging.debug(f"- drawn_geojson: {type(drawn_geojson)}")
    if drawn_geojson:
        has_features = (
            "features" in drawn_geojson
            if isinstance(drawn_geojson, dict)
            else "not a dict"
        )
        logging.debug(f"  - has features: {has_features}")
    logging.debug(f"- show_labels_value: {show_labels_value}")
    logging.debug(f"- download_n_clicks: {download_n_clicks}")
    logging.debug(f"- marker_clicks: {marker_clicks}")
    logging.debug(f"- checked_ids: {checked_ids}")
    logging.debug(
        f"- stored_borehole_data: {'present' if stored_borehole_data else 'None'}"
    )

    # Handle checkbox visibility changes when we already have stored borehole data
    if stored_borehole_data and not stored_data:
        logging.info("====== HANDLING CHECKBOX VISIBILITY CHANGES ======")

        # Reconstruct the loca_df and other data from stored data
        loca_df_records = stored_borehole_data.get("loca_df", [])
        all_borehole_ids = stored_borehole_data.get("all_borehole_ids", [])

        if loca_df_records and all_borehole_ids:
            loca_df = pd.DataFrame(loca_df_records)

            # Get currently checked IDs (default to all if none specified)
            current_checked = checked_ids if checked_ids else all_borehole_ids
            logging.info(f"Current checked boreholes: {current_checked}")

            # Create checkbox grid for borehole visibility control
            checkbox_grid = html.Div(
                [
                    html.H4(
                        "Borehole Visibility Control:",
                        style={"marginTop": "1em", "marginBottom": "0.5em"},
                    ),
                    html.P(
                        "Uncheck boreholes to hide them from the map and plots:",
                        style={
                            "fontSize": "14px",
                            "color": "#666",
                            "marginBottom": "0.5em",
                        },
                    ),
                    dcc.Checklist(
                        id="subselection-checkbox-grid",
                        options=[
                            {"label": f" {bh_id}", "value": bh_id}
                            for bh_id in all_borehole_ids
                        ],
                        value=current_checked,
                        labelStyle={
                            "display": "inline-block",
                            "marginRight": "1em",
                            "marginBottom": "0.3em",
                            "fontSize": "14px",
                        },
                        style={
                            "marginTop": "0.5em",
                            "marginBottom": "1em",
                            "padding": "10px",
                            "backgroundColor": "#f8f9fa",
                            "borderRadius": "5px",
                            "border": "1px solid #dee2e6",
                        },
                    ),
                ]
            )

            # Filter markers based on checked boreholes
            if current_checked:
                # Filter the displayed markers to only show checked boreholes
                visible_loca_df = loca_df[
                    loca_df["LOCA_ID"].isin(current_checked)
                ].copy()
                logging.info(
                    f"Filtering markers to show only checked boreholes: {current_checked}"
                )

                # Recreate markers with only visible boreholes
                markers = []
                for _, row in visible_loca_df.iterrows():
                    if pd.notna(row["lat"]) and pd.notna(row["lon"]):
                        marker = dl.Marker(
                            position=[row["lat"], row["lon"]],
                            children=[
                                dl.Tooltip(
                                    f"LOCA_ID: {row['LOCA_ID']}\nEasting: {row['LOCA_NATE']}\nNorthing: {row['LOCA_NATN']}"
                                )
                            ],
                            id={"type": "borehole-marker", "index": row["LOCA_ID"]},
                        )
                        markers.append(marker)
                logging.info(
                    f"Updated markers list with {len(markers)} visible boreholes"
                )
            else:
                # If no boreholes are checked, show empty marker list
                markers = []
                logging.info("No boreholes checked - hiding all markers")

            return (
                None,  # No file status update needed
                markers,
                None,  # No selected info change
                map_center,
                map_zoom,
                None,  # No section plot change
                None,  # No log plot change
                None,  # No download data
                None,  # No UI feedback change
                checkbox_grid,
                stored_borehole_data,  # Keep existing stored data
            )

    # Handle file upload operations
    if stored_data:
        logging.info("====== PROCESSING UPLOADED AGS FILES ======")
        list_of_contents = stored_data["contents"]
        list_of_names = stored_data["filenames"]

        file_status = [html.H3("📊 File Upload Status", style={"color": "#006600"})]

        ags_files = []
        for content, name in zip(list_of_contents, list_of_names or []):
            logging.debug(f"Processing uploaded file: {name}")
            try:
                content_type, content_string = content.split(",")
                decoded = base64.b64decode(content_string)
                s = decoded.decode("utf-8")
                ags_files.append((name, s))
                file_status.append(html.Div([f"Uploaded: {name}"]))
                logging.info(f"Successfully decoded and added file: {name}")
            except Exception as e:
                logging.error(f"Error reading {name}: {str(e)}")
                file_status.append(html.Div([f"Error reading {name}: {str(e)}"]))

        try:
            logging.debug(
                f"Calling load_all_loca_data with {len(ags_files)} files: {[n for n, _ in ags_files]}"
            )
            loca_df, filename_map = load_all_loca_data(ags_files)
            logging.info(f"Loaded loca_df with {len(loca_df)} rows")

            # Transform coordinates and create markers
            loca_df["easting"] = loca_df["LOCA_NATE"]  # BNG Easting
            loca_df["northing"] = loca_df["LOCA_NATN"]  # BNG Northing
            loca_df["lat"] = None
            loca_df["lon"] = None

            markers = []
            valid_coords = []  # Track valid coordinates for auto-zoom

            for i, row in loca_df.iterrows():
                try:
                    # Get BNG coordinates
                    easting = float(row["easting"])
                    northing = float(row["northing"])

                    # Transform to WGS84 lat/lon for Leaflet
                    lat, lon = transform_coordinates(easting, northing)

                    if lat is None or lon is None:
                        logging.warning(
                            f"Failed to transform coordinates for {row['LOCA_ID']}: ({easting}, {northing})"
                        )
                        continue

                    # Validate transformed coordinates are reasonable for UK
                    if not (49.0 <= lat <= 61.0 and -8.0 <= lon <= 2.0):
                        logging.warning(
                            f"Transformed coordinates outside UK bounds for {row['LOCA_ID']}: ({lat:.6f}, {lon:.6f})"
                        )
                        continue

                    # Store the transformed coordinates back into the DataFrame
                    loca_df.at[i, "lat"] = lat
                    loca_df.at[i, "lon"] = lon

                    label = str(row["LOCA_ID"])
                    marker_id = {"type": "borehole-marker", "index": row["LOCA_ID"]}
                    markers.append(
                        dl.Marker(
                            id=marker_id,
                            position=[lat, lon],
                            children=dl.Tooltip(label),
                            n_clicks=0,
                        )
                    )
                    valid_coords.append((lat, lon))
                    logging.debug(
                        f"Added marker for {label}: BNG({easting}, {northing}) -> WGS84({lat:.6f}, {lon:.6f})"
                    )
                except Exception as marker_exc:
                    logging.warning(
                        f"Skipping marker for row {i} due to coordinate error: {marker_exc}"
                    )

            if valid_coords:
                # Calculate bounds for auto-zoom to show all markers
                lats = [coord[0] for coord in valid_coords]
                lons = [coord[1] for coord in valid_coords]
                center_lat = statistics.mean(lats)
                center_lon = statistics.mean(lons)
                map_center = [center_lat, center_lon]
                map_zoom = 12  # Set appropriate zoom level
                logging.info(f"Auto-zooming to center: {map_center}")
            else:
                logging.warning("No valid coordinates found for markers")

            # Store all borehole data for later use
            all_borehole_ids = loca_df["LOCA_ID"].tolist()
            borehole_data_out = {
                "loca_df": loca_df.to_dict(
                    "records"
                ),  # Convert DataFrame to dict for storage
                "filename_map": {
                    filename: content for filename, content in filename_map.items()
                },
                "all_borehole_ids": all_borehole_ids,
            }

            # Get currently checked IDs (default to all selected if first time)
            current_checked = checked_ids if checked_ids else all_borehole_ids

            # Create checkbox grid for borehole visibility control
            checkbox_grid = html.Div(
                [
                    html.H4(
                        "Borehole Visibility Control:",
                        style={"marginTop": "1em", "marginBottom": "0.5em"},
                    ),
                    html.P(
                        "Uncheck boreholes to hide them from the map and plots:",
                        style={
                            "fontSize": "14px",
                            "color": "#666",
                            "marginBottom": "0.5em",
                        },
                    ),
                    dcc.Checklist(
                        id="subselection-checkbox-grid",
                        options=[
                            {"label": f" {bh_id}", "value": bh_id}
                            for bh_id in all_borehole_ids
                        ],
                        value=current_checked,
                        labelStyle={
                            "display": "inline-block",
                            "marginRight": "1em",
                            "marginBottom": "0.3em",
                            "fontSize": "14px",
                        },
                        style={
                            "marginTop": "0.5em",
                            "marginBottom": "1em",
                            "padding": "10px",
                            "backgroundColor": "#f8f9fa",
                            "borderRadius": "5px",
                            "border": "1px solid #dee2e6",
                        },
                    ),
                ]
            )

            # Filter markers and data based on checked boreholes
            if current_checked:
                # Filter the displayed markers to only show checked boreholes
                visible_loca_df = loca_df[
                    loca_df["LOCA_ID"].isin(current_checked)
                ].copy()
                logging.info(
                    f"Filtering markers to show only checked boreholes: {current_checked}"
                )

                # Recreate markers with only visible boreholes
                markers = []
                for _, row in visible_loca_df.iterrows():
                    if pd.notna(row["lat"]) and pd.notna(row["lon"]):
                        marker = dl.Marker(
                            position=[row["lat"], row["lon"]],
                            children=[
                                dl.Tooltip(
                                    f"LOCA_ID: {row['LOCA_ID']}\nEasting: {row['LOCA_NATE']}\nNorthing: {row['LOCA_NATN']}"
                                )
                            ],
                            id={"type": "borehole-marker", "index": row["LOCA_ID"]},
                        )
                        markers.append(marker)
                logging.info(
                    f"Updated markers list with {len(markers)} visible boreholes"
                )
            else:
                # If no boreholes are checked, show empty marker list
                markers = []
                logging.info("No boreholes checked - hiding all markers")

            return (
                file_status,
                markers,
                None,
                map_center,
                map_zoom,
                None,
                None,
                None,
                None,
                checkbox_grid,
                borehole_data_out,
            )
        except Exception as e:
            logging.error(f"Error parsing AGS files: {str(e)}", exc_info=True)
            file_status.append(html.Div([f"Error parsing AGS files: {str(e)}"]))
            return (
                file_status,
                [],
                None,
                map_center,
                map_zoom,
                None,
                None,
                None,
                None,
                None,
                stored_borehole_data,
            )

    logging.info("No AGS file uploaded yet.")
    return (
        None,
        [],
        None,
        map_center,
        map_zoom,
        None,
        None,
        None,
        None,
        None,
        borehole_data_out,
    )


@app.callback(
    Output("upload-data-store", "data"),
    Input("upload-ags", "contents"),
    State("upload-ags", "filename"),
)
def store_upload_data(contents, filenames):
    """Store uploaded file data in a dcc.Store component to ensure it's available to other callbacks"""
    if contents is None:
        logging.info("No upload data to store")
        return None

    try:
        # Log detailed information for debugging
        logging.info("===== STORING UPLOAD DATA =====")
        logging.info(f"Current time: {datetime.now()}")

        if isinstance(contents, list):
            logging.info(f"Storing {len(contents)} files with names: {filenames}")
            for i, (content, name) in enumerate(zip(contents, filenames or [])):
                content_type = content.split(",")[0] if "," in content else "unknown"
                content_length = len(content) if content else 0
                logging.info(
                    f"File {i+1}: {name} - Type: {content_type} - Length: {content_length}"
                )
            result = {"contents": contents, "filenames": filenames}
            logging.info(f"Store data created with {len(contents)} files")
            return result
        else:
            content_type = contents.split(",")[0] if "," in contents else "unknown"
            content_length = len(contents) if contents else 0
            logging.info(
                f"Storing single file: {filenames} - Type: {content_type} - Length: {content_length}"
            )
            result = {"contents": [contents], "filenames": [filenames]}
            logging.info("Store data created with 1 file")
            return result
    except Exception as e:
        logging.error(f"Error storing upload data: {str(e)}")
        logging.error(traceback.format_exc())
        return None


if __name__ == "__main__":
    try:
        logging.info("Opening browser and starting Dash server")
        webbrowser.open("http://127.0.0.1:8050/")
        app.run(debug=True, host="0.0.0.0", port=8050)
    except Exception as e:
        logging.error(f"Error starting app: {str(e)}")
        logging.error(traceback.format_exc())
        print(f"Error: {str(e)}")
