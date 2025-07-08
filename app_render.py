import os
import dash
from dash import html, dcc, Output, Input, State
from dash.dependencies import ALL
import dash_leaflet as dl
from dash_leaflet import EditControl

import base64
import io
import logging
import sys
import traceback
import webbrowser
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_loader import load_all_loca_data
from section_plot import plot_section_from_ags_content
from borehole_log import plot_borehole_log_from_ags_content
from map_utils import filter_selection_by_shape

# Set up enhanced logging format with detailed context
logfile = "app_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d %(funcName)s] %(message)s",
    handlers=[
        logging.FileHandler(logfile, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),  # Also log to stdout for Render.com logs
    ],
)

# Create root logger and make it extremely verbose
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Log app startup
logging.info(f"App starting at {datetime.now()}")

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose Flask server for Render.com

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
                                EditControl(
                                    id="draw-control",
                                    draw={
                                        "polyline": False,
                                        "circle": False,
                                        "marker": False,
                                    },
                                    edit={"edit": True, "remove": True},
                                ),
                                # Markers will be added dynamically, but always keep an empty list if none
                            ],
                            id="borehole-markers",
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
    ]
)


# Modified main callback to use the stored upload data
@app.callback(
    [
        Output("output-upload", "children"),
        Output("borehole-markers", "children"),
        Output("selected-borehole-info", "children"),
        Output("borehole-map", "center", allow_duplicate=True),
        Output("section-plot-output", "children"),
        Output("log-plot-output", "children"),
        Output("download-section-plot", "data"),
        Output("ui-feedback", "children"),
        Output("subselection-checkbox-grid-container", "children"),
    ],
    [
        Input(
            "upload-data-store", "data"
        ),  # Changed to use stored data instead of direct upload
        Input("draw-control", "geojson"),
        Input("show-labels-checkbox", "value"),
        Input("download-section-btn", "n_clicks"),
        Input({"type": "borehole-marker", "index": ALL}, "n_clicks"),
        Input("borehole-map", "center"),
        Input("borehole-map", "zoom"),
    ],
    [
        State("borehole-map", "center"),
        State("borehole-map", "zoom"),
        State("subselection-checkbox-grid", "value"),
    ],
    prevent_initial_call=True,
)
def handle_upload_and_draw(
    stored_data,  # Input("upload-data-store", "data")
    drawn_geojson,  # Input("draw-control", "geojson")
    show_labels_value,  # Input("show-labels-checkbox", "value")
    download_n_clicks,  # Input("download-section-btn", "n_clicks")
    marker_clicks,  # Input({"type": "borehole-marker", "index": ALL}, "n_clicks")
    map_center_in,  # Input("borehole-map", "center")
    map_zoom_in,  # Input("borehole-map", "zoom")
    marker_children,  # State("borehole-markers", "children")
    section_plot_img,  # State("section-plot-output", "children")
    map_center_state,  # State("borehole-map", "center")
    map_zoom_state,  # State("borehole-map", "zoom")
    checked_ids,  # State("subselection-checkbox-grid", "value")
):
    selected_info = None
    section_plot_img_out = None
    log_plot_img = None
    download_data = None
    ui_feedback = None
    checkbox_grid = None
    selected_loca_ids = []
    show_labels = "show_labels" in (show_labels_value or [])
    # marker_selected = None  # Unused, removed for linting
    map_center = map_center_in or [51.5, -0.1]
    # map_zoom = map_zoom_in or 6  # Unused, removed for linting
    # Log removed due to old logging format
    # Enhanced debug logging: break long parameter list into multiple log lines
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
    logging.debug(f"- map_center_in: {map_center_in}")
    logging.debug(f"- map_zoom_in: {map_zoom_in}")
    logging.debug(
        f"- marker_children length: {len(marker_children) if marker_children else 0}"
    )
    logging.debug(f"- checked_ids: {checked_ids}")
    logging.debug(f"- section_plot_img: {'present' if section_plot_img else 'None'}")
    logging.debug(f"- map_center_state: {map_center_state}")
    logging.debug(f"- map_zoom_state: {map_zoom_state}")
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
            loca_df["lat"] = loca_df["LOCA_NATN"]
            loca_df["lon"] = loca_df["LOCA_NATE"]
            markers = []
            for i, row in loca_df.iterrows():
                try:
                    lat = float(row["lat"])
                    lon = float(row["lon"])
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
                    logging.debug(f"Added marker for {label} at ({lat}, {lon})")
                except Exception as marker_exc:
                    logging.warning(
                        f"Skipping marker for row {i} due to invalid lat/lon: {marker_exc}"
                    )
                    continue
            # Marker click for log plot
            if marker_clicks and any(marker_clicks):
                idx = marker_clicks.index(max(marker_clicks))
                row = loca_df.iloc[idx]
                ags_content = filename_map[row["ags_file"]]
                logging.info(f"Plotting borehole log for {row['LOCA_ID']}")
                fig = plot_borehole_log_from_ags_content(
                    ags_content, row["LOCA_ID"], show_labels=show_labels
                )
                if fig:
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight")
                    plt.close(fig)
                    buf.seek(0)
                    img_bytes = buf.read()
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    log_plot_img = html.Img(
                        src=f"data:image/png;base64,{img_b64}",
                        style={"maxWidth": "100%", "marginTop": "2em"},
                    )
                    ui_feedback = html.Div("Log plot for selected borehole.")
            # Drawn shape for section plot
            elif drawn_geojson and drawn_geojson.get("features"):
                logging.info(f"Processing drawn shape: {drawn_geojson}")
                try:
                    geom = drawn_geojson["features"][-1]["geometry"]
                    logging.info(f"Geometry type: {geom.get('type')}")
                    selected_df = filter_selection_by_shape(geom, loca_df)
                    selected_loca_ids = selected_df["LOCA_ID"].tolist()
                    logging.info(
                        f"Selected borehole IDs from shape: {selected_loca_ids}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error processing drawn shape: {str(e)}", exc_info=True
                    )
                    ui_feedback = html.Div(
                        f"Error processing drawn shape: {str(e)}",
                        style={"color": "red"},
                    )
                    return (
                        file_status,
                        markers,
                        None,
                        map_center,
                        None,
                        None,
                        None,
                        ui_feedback,
                        None,
                    )
                if selected_loca_ids:
                    # Sub-selection checkbox
                    checkbox_grid = dcc.Checklist(
                        id="subselection-checkbox-grid",
                        options=[
                            {"label": bh, "value": bh} for bh in selected_loca_ids
                        ],
                        value=checked_ids if checked_ids else selected_loca_ids,
                        labelStyle={"display": "inline-block", "marginRight": "1em"},
                        style={"marginTop": "1em", "marginBottom": "1em"},
                    )
                    filtered_ids = checked_ids if checked_ids else selected_loca_ids
                    selected_info = html.Div(
                        [
                            html.H3(
                                f"Selected Boreholes: {', '.join(filtered_ids)}",
                                style={"marginTop": "1em"},
                            ),
                            html.P(f"Count: {len(filtered_ids)}"),
                        ]
                    )
                    ags_content = filename_map[selected_df.iloc[0]["ags_file"]]
                    # Section axis orientation: use drawn line if type is LineString, else PCA
                    section_line = None
                    if geom["type"] == "LineString":
                        section_line = geom["coordinates"]
                    if len(filtered_ids) == 1:
                        logging.info(
                            f"Plotting log for single borehole {filtered_ids[0]}"
                        )
                        fig = plot_borehole_log_from_ags_content(
                            ags_content, filtered_ids[0], show_labels=show_labels
                        )
                        if fig:
                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", bbox_inches="tight")
                            plt.close(fig)
                            buf.seek(0)
                            img_bytes = buf.read()
                            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                            log_plot_img = html.Img(
                                src=f"data:image/png;base64,{img_b64}",
                                style={"maxWidth": "100%", "marginTop": "2em"},
                            )
                    else:
                        logging.info(f"Plotting section for boreholes {filtered_ids}")
                        fig = plot_section_from_ags_content(
                            ags_content,
                            filter_loca_ids=filtered_ids,
                            show_labels=show_labels,
                            section_line=section_line,
                        )
                        if fig:
                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", bbox_inches="tight")
                            plt.close(fig)
                            buf.seek(0)
                            img_bytes = buf.read()
                            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                            section_plot_img_out = html.Img(
                                src=f"data:image/png;base64,{img_b64}",
                                style={"maxWidth": "100%", "marginTop": "2em"},
                            )
                            if download_n_clicks:
                                logging.info("Preparing section plot for download")
                                download_data = dict(
                                    content=img_bytes, filename="section_plot.png"
                                )
                        if section_line:
                            logging.info("Section axis set by drawn line.")
                            ui_feedback = html.Div("Section axis set by drawn line.")
                        else:
                            logging.info("Section axis set by PCA.")
                            ui_feedback = html.Div("Section axis set by PCA.")
            return (
                file_status,
                markers,
                selected_info,
                map_center,
                section_plot_img_out,
                log_plot_img,
                download_data,
                ui_feedback,
                checkbox_grid,
            )
        except Exception as e:
            logging.error(f"Error parsing AGS files: {str(e)}", exc_info=True)
            file_status.append(html.Div([f"Error parsing AGS files: {str(e)}"]))
            return file_status, [], None, map_center, None, None, None, None, None
    logging.info("No AGS file uploaded yet.")
    return None, [], None, map_center, None, None, None, None, None


@app.callback(
    Output("test-upload-output", "children"),
    Input("upload-ags", "contents"),
    State("upload-ags", "filename"),
)
def test_upload(contents, filenames):
    """Test callback specifically for debugging file upload issues"""
    # Log detailed information about the upload
    try:
        logging.info("===== TEST UPLOAD CALLBACK TRIGGERED =====")
        logging.info(f"Current time: {datetime.now()}")
        logging.info(f"Filenames received: {filenames}")

        # Log content details
        if contents:
            if isinstance(contents, list):
                logging.info(f"Number of files received: {len(contents)}")
                for i, content in enumerate(contents):
                    content_type = (
                        content.split(",")[0] if "," in content else "unknown"
                    )
                    content_length = len(content) if content else 0
                    logging.info(
                        f"File {i+1}: {filenames[i]} - Type: {content_type} - Length: {content_length}"
                    )
            else:
                content_type = contents.split(",")[0] if "," in contents else "unknown"
                logging.info(
                    f"Single file received - Type: {content_type} - Length: {len(contents)}"
                )
        else:
            logging.info("No contents received in the test callback")

        # Also write to a separate log file for easier debugging
        with open("upload_test.log", "w") as f:
            f.write(f"Callback triggered at: {datetime.now()}\n")
            f.write(f"Filenames received: {filenames}\n")
            if contents:
                if isinstance(contents, list):
                    f.write(f"Number of files: {len(contents)}\n")
                    for i, content in enumerate(contents):
                        content_type = (
                            content.split(",")[0] if "," in content else "unknown"
                        )
                        f.write(
                            f"File {i+1}: {filenames[i]} - Type: {content_type} - Length: {len(content) if content else 0}\n"
                        )
                else:
                    content_type = (
                        contents.split(",")[0] if "," in contents else "unknown"
                    )
                    f.write(f"Content type: {content_type}\n")
                    f.write(f"Content length: {len(contents)}\n")
            else:
                f.write("No contents received\n")
    except Exception as e:
        error_msg = f"Error in test_upload: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        with open("upload_test.log", "w") as f:
            f.write(error_msg)
        return html.Div(f"Error processing upload: {str(e)}", style={"color": "red"})

    # Return visible feedback
    if contents is None:
        return "No file uploaded yet. Select a file to test upload."

    if isinstance(filenames, list):
        return html.Div(
            [
                html.H5(f"Successfully received {len(filenames)} files:"),
                html.Ul([html.Li(name) for name in filenames]),
                html.P(
                    "See upload_test.log for details", style={"fontStyle": "italic"}
                ),
            ]
        )
    else:
        return html.Div(
            [
                html.H5(f"Uploaded: {filenames}"),
                html.P(
                    "See upload_test.log for details", style={"fontStyle": "italic"}
                ),
            ]
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


def clear_log_files():
    """Clear log files at startup to make debugging easier"""
    log_files = ["app_debug.log", "upload_test.log"]
    for log_file in log_files:
        try:
            with open(log_file, "w") as f:
                f.write(f"Log file cleared at {datetime.now()}\n")
            logging.info(f"Cleared log file: {log_file}")
        except Exception as e:
            print(f"Error clearing log file {log_file}: {str(e)}")


if __name__ == "__main__":
    try:
        clear_log_files()  # Clear log files at startup
        logging.info("Opening browser and starting Dash server")
        # When running locally, open the browser
        if not os.environ.get("RENDER"):
            webbrowser.open("http://127.0.0.1:8050/")
            app.run(debug=True, host="0.0.0.0", port=8050)
        else:
            # For Render.com, use a different port (set by environment variable)
            port = int(os.environ.get("PORT", 8080))
            app.run(debug=False, host="0.0.0.0", port=port)
    except Exception as e:
        logging.error(f"Error starting app: {str(e)}")
        logging.error(traceback.format_exc())
        print(f"Error: {str(e)}")
