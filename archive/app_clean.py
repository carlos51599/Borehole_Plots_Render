import dash
from dash import html, dcc
import dash_leaflet as dl
from dash_leaflet import EditControl

import logging
import sys
import webbrowser
from datetime import datetime

import config  # Import UI configuration

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
                                # Markers will be added dynamically
                            ],
                            id="borehole-markers",
                        ),
                        dl.FeatureGroup(
                            [
                                # PCA line will be added dynamically
                            ],
                            id="pca-line-group",
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
        # Store components for data sharing between callbacks
        dcc.Store(id="upload-data-store"),
        dcc.Store(id="borehole-data-store"),
    ]
)

# Log layout components after creation
logging.info("App layout created successfully")


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

# Import and register the split callbacks
logging.info("Registering split callbacks...")
from callbacks_split import register_callbacks

register_callbacks(app)
logging.info("✅ All callbacks registered successfully!")


# Upload data store callback (simple helper)
@app.callback(
    dash.Output("upload-data-store", "data"),
    dash.Input("upload-ags", "contents"),
    dash.State("upload-ags", "filename"),
)
def store_upload_data(contents, filenames):
    """Store uploaded file data in a dcc.Store component"""
    if contents is None:
        logging.info("No upload data to store")
        return None

    try:
        logging.info("=== STORING UPLOAD DATA ===")
        if isinstance(contents, list):
            logging.info(f"Storing {len(contents)} files")
            return {"contents": contents, "filenames": filenames}
        else:
            logging.info("Storing single file")
            return {"contents": [contents], "filenames": [filenames]}
    except Exception as e:
        logging.error(f"Error storing upload data: {str(e)}")
        return None


if __name__ == "__main__":
    try:
        logging.info("Opening browser and starting Dash server")
        webbrowser.open("http://127.0.0.1:8050/")
        app.run(debug=True, host="0.0.0.0", port=8050)
    except Exception as e:
        logging.error(f"Error starting app: {str(e)}")
        print(f"Error: {str(e)}")
