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

import matplotlib
from data_loader import load_all_loca_data
from map_utils import filter_selection_by_shape
import config  # Import UI configuration

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
        html.H1(config.APP_TITLE, style=config.HEADER_H1_CENTER_STYLE),
        html.P(config.APP_SUBTITLE, style=config.HEADER_H2_CENTER_STYLE),
        dcc.Upload(
            id="upload-ags",
            children=html.Div(["Drag and Drop or ", html.A(config.UPLOAD_PROMPT)]),
            style=config.UPLOAD_AREA_CENTER_STYLE,
            multiple=True,
            accept=".ags",
        ),
        html.Div(id="output-upload"),
        html.Hr(),
        html.Div(
            [
                html.H2(config.MAP_SECTION_TITLE, style=config.HEADER_H2_LEFT_STYLE),
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
                    style=config.MAP_CENTER_STYLE,
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
                    options=[
                        {"label": config.LABELS_CHECKBOX_LABEL, "value": "show_labels"}
                    ],
                    value=["show_labels"],
                    inline=True,
                    style=config.CHECKBOX_CONTROL_STYLE,
                ),
                html.Button(
                    config.DOWNLOAD_BUTTON_LABEL,
                    id="download-section-btn",
                    n_clicks=0,
                    style=config.BUTTON_RIGHT_STYLE,
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

# Log layout components after creation
logging.info("App layout created successfully")
logging.info("Registering callbacks...")


# Add a function to inspect layout IDs
def log_layout_ids(component, prefix=""):
    """Recursively log all component IDs in the layout"""
    try:
        if hasattr(component, "id") and component.id:
            logging.info(f"Found component ID: {component.id}")
        if hasattr(component, "children"):
            if isinstance(component.children, list):
                for child in component.children:
                    log_layout_ids(child, prefix + "  ")
            elif component.children is not None:
                log_layout_ids(component.children, prefix + "  ")
    except Exception as e:
        logging.warning(f"Error inspecting component: {e}")


# Log all IDs in the layout
logging.info("=== LAYOUT COMPONENT IDs ===")
log_layout_ids(app.layout)
logging.info("=== END LAYOUT IDs ===")

# Log callback registration
logging.info("Registering main callback with draw-control input...")


# Modified main callback to use the stored upload data
@app.callback(
    [
        Output("output-upload", "children"),
        Output("borehole-markers", "children"),
        Output("selected-borehole-info", "children"),
        Output("borehole-map", "center", allow_duplicate=True),
        Output("borehole-map", "zoom", allow_duplicate=True),  # Add zoom control
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
        # Remove map center/zoom inputs to prevent constant re-centering
    ],
    [
        State("borehole-map", "center"),
        State("borehole-map", "zoom"),
        State("borehole-data-store", "data"),  # Add stored borehole data
    ],
    prevent_initial_call=True,
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

    # Determine what triggered this callback
    ctx = dash.callback_context
    triggered_input = ctx.triggered[0]["prop_id"] if ctx.triggered else None
    logging.info(f"Callback triggered by: {triggered_input}")

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
    # Log removed due to old logging format
    # Enhanced debug logging: break long parameter list into multiple log lines
    logging.info("===== MAIN CALLBACK TRIGGERED =====")
    logging.info(f"Current time: {datetime.now()}")
    logging.debug(f"- stored_data: {type(stored_data)}")
    if stored_data:
        logging.debug(
            f"  - stored_data keys: {stored_data.keys() if isinstance(stored_data, dict) else 'not a dict'}"
        )
    logging.debug(f"- drawn_geojson: {type(drawn_geojson)}")  # Re-enabled
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
    logging.debug(f"- map_center_state: {map_center_state}")
    logging.debug(f"- map_zoom_state: {map_zoom_state}")
    logging.debug(
        f"- marker_children length: {len(marker_children) if marker_children else 0}"
    )
    logging.debug(f"- checked_ids: {checked_ids}")
    logging.debug(f"- section_plot_img: {'present' if section_plot_img else 'None'}")
    logging.debug(f"- map_center_state: {map_center_state}")
    logging.debug(f"- map_zoom_state: {map_zoom_state}")
    logging.debug(
        f"- stored_borehole_data: {'present' if stored_borehole_data else 'None'}"
    )

    # Handle drawing operations with existing borehole data (independent of file upload)
    if drawn_geojson and drawn_geojson.get("features") and stored_borehole_data:
        print("🎯 DRAWING OPERATION DETECTED!")  # Console debug
        logging.info("====== PROCESSING DRAWN SHAPE WITH STORED BOREHOLE DATA ======")
        logging.info(f"drawn_geojson type: {type(drawn_geojson)}")
        logging.info(
            f"drawn_geojson keys: {drawn_geojson.keys() if isinstance(drawn_geojson, dict) else 'not a dict'}"
        )

        # Log the complete GeoJSON structure for detailed analysis
        try:
            geojson_str = json.dumps(drawn_geojson, indent=2)
            logging.info(f"Complete drawn_geojson structure:\n{geojson_str}")
        except Exception as json_err:
            logging.warning(f"Could not serialize drawn_geojson to JSON: {json_err}")
            logging.info(f"drawn_geojson repr: {repr(drawn_geojson)}")

        # Analyze features in detail
        features = drawn_geojson.get("features", [])
        logging.info(f"Number of features in drawn_geojson: {len(features)}")

        for i, feature in enumerate(features):
            logging.info(f"Feature {i}: type={type(feature)}")
            if isinstance(feature, dict):
                logging.info(f"  Feature {i} keys: {feature.keys()}")
            else:
                logging.info(f"  Feature {i} is not a dict")
            if isinstance(feature, dict):
                geometry = feature.get("geometry", {})
                properties = feature.get("properties", {})
                logging.info(f"  Geometry type: {geometry.get('type', 'missing')}")
                logging.info(
                    f"  Geometry coordinates length: {len(geometry.get('coordinates', []))}"
                )
                logging.info(f"  Properties: {properties}")

                # Log first few coordinates for debugging
                coords = geometry.get("coordinates", [])
                if coords:
                    logging.info(
                        f"  First coordinate: {coords[0] if len(coords) > 0 else 'empty'}"
                    )
                    if len(coords) > 1:
                        logging.info(f"  Second coordinate: {coords[1]}")
                    if len(coords) > 2:
                        logging.info(f"  ... and {len(coords) - 2} more coordinates")

        try:
            # Reconstruct loca_df and filename_map from stored data
            logging.info("Reconstructing loca_df and filename_map from stored data...")
            loca_df = stored_borehole_data.get("loca_df")
            filename_map = stored_borehole_data.get("filename_map")

            logging.info(f"loca_df type: {type(loca_df)}")
            logging.info(f"filename_map type: {type(filename_map)}")
            logging.info(
                f"filename_map keys: {list(filename_map.keys()) if filename_map else 'None'}"
            )

            if loca_df is not None and filename_map is not None:
                # Convert stored data back to DataFrame if needed
                if isinstance(loca_df, (dict, list)):
                    import pandas as pd

                    logging.info("Converting stored data back to DataFrame...")
                    loca_df = pd.DataFrame(loca_df)
                    logging.info(f"Converted DataFrame shape: {loca_df.shape}")
                    logging.info(f"DataFrame columns: {list(loca_df.columns)}")

                # Check if DataFrame has required coordinate columns
                required_cols = [
                    "LOCA_ID",
                    "LOCA_NATE",
                    "LOCA_NATN",
                ]  # Fixed column names
                missing_cols = [
                    col for col in required_cols if col not in loca_df.columns
                ]
                if missing_cols:
                    logging.error(
                        f"Missing required columns in loca_df: {missing_cols}"
                    )
                    logging.info(f"Available columns: {list(loca_df.columns)}")

                # Add lat/lon columns if they don't exist (for drawing operations)
                if "lat" not in loca_df.columns or "lon" not in loca_df.columns:
                    logging.warning(
                        "lat/lon columns missing from stored DataFrame - this should not happen with new uploads!"
                    )
                    logging.info(
                        "Adding lat/lon columns to loca_df for drawing operations..."
                    )
                    loca_df["lat"] = None
                    loca_df["lon"] = None

                    for i, row in loca_df.iterrows():
                        try:
                            easting = float(row["easting"])
                            northing = float(row["northing"])
                            lat, lon = transform_coordinates(easting, northing)
                            loca_df.at[i, "lat"] = lat
                            loca_df.at[i, "lon"] = lon
                            logging.debug(
                                f"Transformed {row['LOCA_ID']}: "
                                f"BNG({easting}, {northing}) -> WGS84({lat:.6f}, {lon:.6f})"
                            )
                        except Exception as coord_err:
                            logging.warning(
                                f"Failed to transform coordinates for row {i}: {coord_err}"
                            )
                            loca_df.at[i, "lat"] = None
                            loca_df.at[i, "lon"] = None

                    # Log coordinate ranges for debugging
                    valid_lats = loca_df["lat"].dropna()
                    valid_lons = loca_df["lon"].dropna()
                    if len(valid_lats) > 0:
                        logging.info(
                            f"Coordinate ranges - Lat: {valid_lats.min():.6f} to {valid_lats.max():.6f}"
                        )
                        logging.info(
                            f"Coordinate ranges - Lon: {valid_lons.min():.6f} to {valid_lons.max():.6f}"
                        )
                        logging.info(
                            f"Valid coordinates: {len(valid_lats)} out of {len(loca_df)}"
                        )
                    else:
                        logging.warning("No valid lat/lon coordinates found!")
                else:
                    logging.info("✓ lat/lon columns already exist in DataFrame")
                    # Check for any None values
                    null_coords = loca_df[["lat", "lon"]].isnull().any(axis=1).sum()
                    if null_coords > 0:
                        logging.warning(
                            f"Found {null_coords} rows with null coordinates in existing DataFrame"
                        )

                    # Log existing coordinate info
                    valid_lats = loca_df["lat"].dropna()
                    valid_lons = loca_df["lon"].dropna()
                    if len(valid_lats) > 0:
                        logging.info(
                            f"Using stored coordinates: {len(valid_lats)} valid points"
                        )
                        logging.info(
                            f"Sample coordinates: lat={valid_lats.iloc[0]:.6f}, lon={valid_lons.iloc[0]:.6f}"
                        )
                        logging.info(
                            f"Coordinate ranges: lat [{valid_lats.min():.6f}, {valid_lats.max():.6f}]"
                        )
                        logging.info(
                            f"Coordinate ranges: lon [{valid_lons.min():.6f}, {valid_lons.max():.6f}]"
                        )

                logging.info(
                    f"Using stored data: {len(loca_df)} boreholes, {len(filename_map)} files"
                )
                logging.info(f"Sample borehole IDs: {list(loca_df['LOCA_ID'].head(5))}")

                # Filter boreholes by the drawn shape - enhanced logging
                print(
                    f"🔍 FILTERING {len(loca_df)} boreholes with drawn shape..."
                )  # Console debug
                logging.info("Calling filter_selection_by_shape...")
                logging.info(f"loca_df shape before filtering: {loca_df.shape}")

                try:
                    filtered_loca_ids = filter_selection_by_shape(
                        loca_df, drawn_geojson
                    )
                    filter_length = (
                        len(filtered_loca_ids)
                        if hasattr(filtered_loca_ids, "__len__")
                        else "N/A"
                    )
                    print(
                        f"📊 FILTER RESULT: {type(filtered_loca_ids)}, length: {filter_length}"
                    )  # Console debug
                    logging.info(
                        f"filter_selection_by_shape returned: {type(filtered_loca_ids)}"
                    )

                    if hasattr(filtered_loca_ids, "shape"):
                        logging.info(
                            f"Filtered result shape: {filtered_loca_ids.shape}"
                        )
                    if hasattr(filtered_loca_ids, "__len__"):
                        logging.info(
                            f"Filtered result length: {len(filtered_loca_ids)}"
                        )

                    # Convert DataFrame result to list of LOCA_IDs if needed
                    import pandas as pd

                    if isinstance(filtered_loca_ids, pd.DataFrame):  # It's a DataFrame
                        borehole_ids = filtered_loca_ids["LOCA_ID"].tolist()
                        logging.info(
                            f"Extracted {len(borehole_ids)} LOCA_IDs from filtered DataFrame"
                        )
                    elif isinstance(filtered_loca_ids, list):
                        borehole_ids = filtered_loca_ids
                        logging.info(
                            f"Got {len(borehole_ids)} LOCA_IDs directly from filter"
                        )
                    else:
                        logging.error(
                            f"Unexpected return type from filter_selection_by_shape: {type(filtered_loca_ids)}"
                        )
                        borehole_ids = []

                    logging.info(f"Final borehole IDs for section plot: {borehole_ids}")

                except Exception as filter_err:
                    logging.error(
                        f"Error in filter_selection_by_shape: {filter_err}",
                        exc_info=True,
                    )
                    borehole_ids = []

                if borehole_ids:
                    print(
                        f"✅ FOUND {len(borehole_ids)} BOREHOLES: {borehole_ids}"
                    )  # Console debug
                    logging.info(
                        f"✓ Selected {len(borehole_ids)} boreholes: {borehole_ids}"
                    )

                    # Create checkbox grid for selected boreholes (subselection)
                    current_checked = checked_ids if checked_ids else borehole_ids
                    checkbox_grid = html.Div(
                        [
                            html.H4(
                                config.CHECKBOX_SECTION_TITLE,
                                style=config.HEADER_H4_LEFT_STYLE,
                            ),
                            html.P(
                                config.CHECKBOX_INSTRUCTIONS,
                                style=config.DESCRIPTION_TEXT_STYLE,
                            ),
                            dcc.Checklist(
                                id="subselection-checkbox-grid",
                                options=[
                                    {"label": f" {bh_id}", "value": bh_id}
                                    for bh_id in borehole_ids  # Only selected boreholes!
                                ],
                                value=current_checked,
                                labelStyle=config.CHECKBOX_LABEL_STYLE,
                                style=config.CHECKBOX_LEFT_STYLE,
                            ),
                        ]
                    )

                    # Create section plot using checked boreholes (subset of selected)
                    boreholes_to_plot = (
                        current_checked if current_checked else borehole_ids
                    )
                    logging.info(
                        f"Creating section plot for {len(boreholes_to_plot)} checked boreholes: {boreholes_to_plot}"
                    )

                    # Find which AGS file contains the most boreholes for section plotting
                    # For now, combine all AGS content into a single string
                    # TODO: Improve this to handle multiple files more intelligently
                    combined_content = ""
                    for filename, content in filename_map.items():
                        logging.info(f"Including content from {filename}")
                        combined_content += content + "\n"

                    logging.info(
                        f"Combined content length: {len(combined_content)} characters"
                    )

                    try:
                        fig = plot_section_from_ags_content(
                            combined_content, boreholes_to_plot, show_labels=show_labels
                        )
                        logging.info(
                            f"plot_section_from_ags_content returned: {type(fig)}"
                        )

                        if fig:
                            logging.info("✓ Section plot figure created successfully")
                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", bbox_inches="tight")
                            plt.close(fig)
                            buf.seek(0)
                            img_bytes = buf.read()
                            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                            section_plot_img_out = html.Img(
                                src=f"data:image/png;base64,{img_b64}",
                                style=config.SECTION_PLOT_CENTER_STYLE,
                            )
                            ui_feedback = html.Div(
                                f"{config.FILE_UPLOAD_SUCCESS_PREFIX} {len(borehole_ids)} {config.FILE_UPLOAD_SUCCESS_SUFFIX}"
                            )
                            logging.info(
                                "✓ Successfully created section plot from drawing"
                            )
                        else:
                            ui_feedback = html.Div(
                                config.ERROR_PLOT_MESSAGE,
                                style=config.ERROR_MESSAGE_STYLE,
                            )
                            logging.warning(
                                "✗ plot_section_from_ags_content returned None"
                            )
                    except Exception as plot_err:
                        logging.error(
                            f"Error creating section plot: {plot_err}", exc_info=True
                        )
                        ui_feedback = html.Div(
                            f"{config.ERROR_SELECTION_MESSAGE}: {plot_err}",
                            style=config.ERROR_MESSAGE_STYLE,
                        )
                else:
                    print(
                        "❌ NO BOREHOLES FOUND - Check console/logs for details"
                    )  # Console debug
                    ui_feedback = html.Div(
                        config.NO_BOREHOLES_MESSAGE,
                        style=config.WARNING_MESSAGE_STYLE,
                    )
                    logging.info("No boreholes found in drawn area")
            else:
                logging.error("Stored borehole data is incomplete")
                logging.error(f"loca_df is None: {loca_df is None}")
                logging.error(f"filename_map is None: {filename_map is None}")
                ui_feedback = html.Div(
                    "Error: Borehole data not available for drawing operations.",
                    style=config.ERROR_MESSAGE_STYLE,
                )

        except Exception as e:
            logging.error(
                f"Error processing drawn shape with stored data: {str(e)}",
                exc_info=True,
            )
            logging.error(f"Exception type: {type(e)}")
            logging.error(f"Exception args: {e.args}")
            ui_feedback = html.Div(
                f"{config.ERROR_SELECTION_MESSAGE}: {str(e)}",
                style=config.ERROR_MESSAGE_STYLE,
            )

        # Return early for drawing operations (keep existing markers and data)
        logging.info("====== DRAWING OPERATION RETURN ======")
        logging.info(f"Returning map_center: {map_center}, map_zoom: {map_zoom}")
        logging.info(
            f"section_plot_img_out: {'present' if section_plot_img_out else 'None'}"
        )
        logging.info(f"ui_feedback: {ui_feedback}")
        logging.info("===== END DRAWING OPERATION RETURN =====")

        # Update stored borehole data to include the last selection for checkbox updates
        updated_borehole_data = (
            stored_borehole_data.copy() if stored_borehole_data else {}
        )
        if borehole_ids:  # Only update if we have a valid selection
            updated_borehole_data["last_selection"] = borehole_ids
            logging.info(f"Stored last selection: {borehole_ids}")

        return (
            None,  # output-upload (no change)
            marker_children,  # Keep existing markers
            selected_info,
            map_center,
            map_zoom,
            section_plot_img_out,
            log_plot_img,
            download_data,
            ui_feedback,
            checkbox_grid,
            updated_borehole_data,  # Updated with last selection
        )
    if stored_data and "contents" in stored_data:
        list_of_contents = stored_data["contents"]
        list_of_names = stored_data["filenames"]
        logging.info(
            f"Received AGS upload: {len(list_of_contents)} file(s), names={list_of_names}"
        )
        ags_files = []
        file_status = []
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

            # Add per-file information to UI
            file_breakdown = []
            for filename, content in filename_map.items():
                file_rows = loca_df[loca_df["ags_file"] == filename]
                if len(file_rows) > 0:
                    easting_range = (
                        file_rows["LOCA_NATE"].max() - file_rows["LOCA_NATE"].min()
                    )
                    northing_range = (
                        file_rows["LOCA_NATN"].max() - file_rows["LOCA_NATN"].min()
                    )
                    file_breakdown.append(
                        html.Li(
                            [
                                html.B(filename),
                                f": {len(file_rows)} boreholes",
                                html.Br(),
                                f"   BNG Easting range: {easting_range:.1f}m, Northing range: {northing_range:.1f}m",
                            ]
                        )
                    )

            if file_breakdown:
                file_status.append(
                    html.Div(
                        [
                            html.H4(
                                config.FILE_BREAKDOWN_TITLE,
                                style=config.SUCCESS_MESSAGE_STYLE,
                            ),
                            html.Ul(file_breakdown),
                        ],
                        style={
                            "background": "#f0fff0",
                            "padding": "10px",
                            "margin": "10px",
                            "border": f"{config.BORDER_WIDTH} {config.BORDER_STYLE_SOLID} {config.PRIMARY_COLOR}",
                            "borderRadius": config.BORDER_RADIUS,
                        },
                    )
                )

            # Note: LOCA_NATN and LOCA_NATE are typically BNG coordinates, not lat/lon
            loca_df["easting"] = loca_df["LOCA_NATE"]  # BNG Easting
            loca_df["northing"] = loca_df["LOCA_NATN"]  # BNG Northing

            # Add lat/lon columns to store transformed coordinates
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
                        logging.warning(f"  Original BNG: ({easting}, {northing})")
                        continue

                    # Double-check coordinates are valid numbers
                    if (
                        lat is None
                        or lon is None
                        or not (
                            isinstance(lat, (int, float))
                            and isinstance(lon, (int, float))
                        )
                    ):
                        logging.warning(
                            f"Invalid coordinate types for {row['LOCA_ID']}: lat={lat}, lon={lon}"
                        )
                        continue

                    # Store the transformed coordinates back into the DataFrame
                    loca_df.at[i, "lat"] = lat
                    loca_df.at[i, "lon"] = lon

                    label = str(row["LOCA_ID"])
                    marker_id = {"type": "borehole-marker", "index": i}
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
                    continue

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

            # No checkboxes during initial upload - only after drawing selection

            return (
                file_status,
                markers,
                None,
                map_center,
                map_zoom,
                None,  # section_plot_output
                None,  # log_plot_output
                None,  # download_data
                None,  # ui_feedback
                None,  # checkbox_grid (empty on upload)
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
