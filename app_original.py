"""
Main Dash application entry point for the Geo Borehole Sections Render application.

This module creates and configures a Dash web application for visualizing AGS (Association of
Geotechnical and Geoenvironmental Specialists) borehole data with interactive mapping and
section plotting capabilities.

Key Features:
- Interactive map with multiple layer types (OpenStreetMap, Satellite, Hybrid)
- AGS file upload and processing
- Borehole search functionality
- Drawing tools for borehole selection (polygon, rectangle, polyline)
- Cross-sectional plot generation
- Theme switching (light/dark)
- Responsive design with professional styling

Dependencies:
- dash: Web application framework
- dash-leaflet: Interactive mapping components
- Various custom modules for callbacks, configuration, and app factory

Author: [Project Team]
Last Modified: July 2025
"""

import dash
from dash import html, dcc
import dash_leaflet as dl
from dash_leaflet import EditControl

import logging
import sys
import webbrowser
from datetime import datetime

import config  # Import UI configuration
from callbacks import register_callbacks  # Import modular callback registration
from app_factory import create_app_with_duplicate_callbacks  # Import app factory

# ===== LOGGING CONFIGURATION =====
# Set up enhanced logging format with detailed context for debugging and monitoring
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

# OPTIMIZATION: Reduce matplotlib logging verbosity to improve performance
# This addresses the 538 font manager debug lines found in baseline testing
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("matplotlib.pyplot").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(
    logging.INFO
)  # Keep INFO level for other matplotlib logs

# Log app startup
logging.info(f"App starting at {datetime.now()}")
logging.info(f"Dash version: {dash.__version__}")
logging.info(f"Dash-leaflet version: {dl.__version__}")
logging.info("✓ Matplotlib logging optimized for performance")

# ===== APP INITIALIZATION =====
# Create the Dash app using the factory function for proper duplicate callback handling
app = create_app_with_duplicate_callbacks()

# Log layout creation
logging.info("Creating app layout...")

# ===== APPLICATION LAYOUT =====
# Define the main application layout with all UI components
app.layout = html.Div(
    [
        # ===== HIDDEN STORES AND STATE MANAGEMENT =====
        # Hidden store to track font cache warming
        dcc.Store(id="font-cache-warmed", data=False),
        # ===== HEADER SECTION =====
        # Logo container positioned absolutely in top-left corner
        html.Div(
            html.Img(
                src="assets/BinniesLogo.png", className="logo-image", id="logo-img"
            ),
            className="logo-container",
            id="logo-container",
        ),
        # Theme toggle buttons positioned absolutely in top-right corner
        html.Div(
            [
                html.Button(
                    "☀️",  # Sun emoji
                    id="light-theme-btn",
                    className="theme-toggle-btn sun-icon",
                    title="Switch to Light Theme",
                ),
                html.Button(
                    "🌙",  # Moon emoji
                    id="dark-theme-btn",
                    className="theme-toggle-btn moon-icon active",
                    title="Switch to Dark Theme",
                ),
            ],
            className="theme-toggle-container",
        ),
        # ===== TITLE AND SUBTITLE =====
        html.H1(config.APP_TITLE, style=config.HEADER_H1_CENTER_STYLE),
        html.P(config.APP_SUBTITLE, style=config.HEADER_H2_CENTER_STYLE),
        # ===== FILE UPLOAD SECTION =====
        # AGS file upload component with drag-and-drop functionality
        dcc.Upload(
            id="upload-ags",
            children=html.Div(["Drag and Drop or ", html.A(config.UPLOAD_PROMPT)]),
            style=config.UPLOAD_AREA_CENTER_STYLE,
            multiple=True,
            accept=".ags",
        ),
        html.Div(id="output-upload"),
        html.Hr(),
        # ===== MAIN CONTENT SECTION =====
        html.Div(
            [
                html.H2(config.MAP_SECTION_TITLE, style=config.HEADER_H2_LEFT_STYLE),
                # ===== BOREHOLE SEARCH SECTION =====
                # Search functionality for finding specific boreholes by name
                html.Div(
                    [
                        html.H3(
                            "Search for Borehole",
                            style={
                                **config.HEADER_H4_LEFT_STYLE,
                                "marginBottom": "10px",
                                "marginTop": "10px",
                            },
                        ),
                        html.P(
                            "Search by borehole name or use the map to click on markers",
                            style={
                                "fontSize": "12px",
                                "marginBottom": "15px",
                                "fontStyle": "italic",
                            },
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="borehole-search-dropdown",
                                    placeholder="Type to search for a borehole by name...",
                                    options=[],
                                    value=None,
                                    searchable=True,
                                    clearable=True,
                                    style={
                                        "width": "70%",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                    },
                                ),
                                html.Button(
                                    "Go to Borehole",
                                    id="search-go-btn",
                                    n_clicks=0,
                                    disabled=True,
                                    style={
                                        "width": "25%",
                                        "marginLeft": "5%",
                                        "height": "40px",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                        "minWidth": "120px",
                                        "borderRadius": "5px",
                                        "fontSize": "14px",
                                        "cursor": "pointer",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "marginBottom": "20px",
                                "width": "100%",
                            },
                        ),
                        html.Div(id="search-feedback", style={"marginBottom": "15px"}),
                    ],
                    id="borehole-search-section",
                    style={
                        "marginBottom": "20px",
                        "padding": "15px",
                        "border": "1px solid rgba(204, 204, 204, 0.3)",
                        "borderRadius": "5px",
                        "backgroundColor": "rgba(255, 255, 255, 0.05)",
                    },
                ),
                # ===== INTERACTIVE MAP SECTION =====
                # Main map component with multiple layers and drawing tools
                dl.Map(
                    [
                        # ===== MAP LAYER CONTROLS =====
                        # Layer control to switch between map types (OpenStreetMap, Satellite, Hybrid)
                        dl.LayersControl(
                            [
                                dl.BaseLayer(
                                    dl.TileLayer(
                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                        attribution="&copy; OpenStreetMap contributors",
                                    ),
                                    name="OpenStreetMap",
                                    checked=False,
                                ),
                                dl.BaseLayer(
                                    dl.TileLayer(
                                        url=(
                                            "https://server.arcgisonline.com/ArcGIS/rest/services/"
                                            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                        ),
                                        attribution="&copy; Esri",
                                    ),
                                    name="Satellite",
                                    checked=False,
                                ),
                                # Hybrid layer combining satellite imagery with labels (default)
                                dl.BaseLayer(
                                    dl.LayerGroup(
                                        [
                                            # Base satellite layer
                                            dl.TileLayer(
                                                url=(
                                                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                                                    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                                ),
                                                attribution="&copy; Esri",
                                            ),
                                            # Translucent labels layer on top
                                            dl.TileLayer(
                                                url=(
                                                    "https://{s}.basemaps.cartocdn.com/rastertiles/"
                                                    "voyager_only_labels/{z}/{x}/{y}{r}.png"
                                                ),
                                                attribution="&copy; CARTO",
                                                opacity=0.9,
                                            ),
                                        ]
                                    ),
                                    name="Hybrid (Satellite + Labels)",
                                    checked=True,  # Set as default
                                ),
                            ],
                            position="topright",
                        ),
                        # ===== MAP FEATURE GROUPS =====
                        # Feature group for borehole markers (populated dynamically)
                        dl.FeatureGroup(
                            [
                                # Markers will be added dynamically
                            ],
                            id="borehole-markers",
                        ),
                        # Feature group for selection shapes (polygons, rectangles, etc.)
                        dl.FeatureGroup(
                            [
                                # Selection shapes will be added here
                            ],
                            id="selection-shapes",
                        ),
                        # Feature group for PCA (Principal Component Analysis) line visualization
                        dl.FeatureGroup(
                            [
                                # PCA line will be added dynamically
                            ],
                            id="pca-line-group",
                        ),
                        # Feature group for drawing controls and user-drawn shapes
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
                                        "circlemarker": False,
                                    },
                                    edit={
                                        "edit": True,
                                        "remove": True,
                                        "removeAll": True,  # Enable remove all shapes
                                        "poly": True,
                                    },
                                    position="topleft",
                                ),
                            ],
                            id="draw-feature-group",
                        ),
                    ],
                    id="borehole-map",
                    center=[51.5, -0.1],  # Default center on UK
                    zoom=6,
                    style=config.MAP_CENTER_STYLE,
                ),
            ]
        ),
        # ===== BUFFER CONTROLS SECTION =====
        # Controls for adjusting polyline buffer distance (shown when polyline is drawn)
        html.Div(
            [
                html.H3(
                    "Buffer Settings",
                    style={"margin-top": "20px", "margin-bottom": "10px"},
                ),
                html.Div(
                    [
                        html.Label(
                            "Polyline Buffer (meters):", style={"margin-right": "10px"}
                        ),
                        dcc.Input(
                            id="buffer-input",
                            type="number",
                            value=50,
                            min=1,
                            max=500,
                            step=1,
                            style={"width": "100px", "margin-right": "10px"},
                        ),
                        html.Button(
                            "Update Buffer",
                            id="update-buffer-btn",
                            n_clicks=0,
                            style={"margin-left": "10px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "margin-bottom": "10px",
                    },
                ),
            ],
            id="buffer-controls",
            style={"display": "none"},  # Initially hidden, shown when polyline is drawn
        ),
        # ===== OUTPUT SECTIONS =====
        # Dynamic content areas populated by callbacks
        html.Div(id="selected-borehole-info"),  # Selected borehole information display
        html.Div(id="section-plot-output"),  # Cross-sectional plots
        html.Div(id="log-plot-output"),  # Individual borehole logs
        # ===== CONTROL BUTTONS AND DOWNLOADS =====
        # Checkbox and download controls for plots
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
        # ===== FEEDBACK AND SUBSELECTION =====
        # UI feedback and borehole subselection components
        html.Div(id="ui-feedback"),
        html.Div(id="subselection-checkbox-grid-container", children=[]),
        dcc.Checklist(
            id="subselection-checkbox-grid",
            options=[],
            value=[],
            style={"display": "none"},
        ),
        # ===== DATA STORES =====
        # Store components for data sharing between callbacks
        dcc.Store(id="upload-data-store"),  # Uploaded file data
        dcc.Store(id="borehole-data-store"),  # Processed borehole data
        dcc.Store(id="search-selected-borehole", data=None),  # Search selection state
    ],
    className="dash-container",  # Add a class for styling the main container
)

# Log layout components after creation
logging.info("App layout created successfully")


# Add a function to inspect layout IDs
def log_layout_ids(component, prefix=""):
    """
    Recursively log all component IDs in the layout for debugging purposes.

    This function traverses the entire Dash layout tree and logs each component's ID
    to help with debugging callback connections and component identification.

    Args:
        component: Dash component to inspect (html.Div, dcc.Graph, etc.)
        prefix (str): Indentation prefix for nested components (default: "")

    Returns:
        None: Function logs to the configured logger

    Note:
        Used during app startup to verify all components have proper IDs for callbacks
    """
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

# ===== CLIENTSIDE CALLBACKS =====
# These callbacks run in the browser for better performance

# Theme switching callback - handles light/dark theme toggle
app.clientside_callback(
    """
    function(light_clicks, dark_clicks) {
        console.log('=== THEME CALLBACK TRIGGERED ===');
        console.log('Light clicks:', light_clicks);
        console.log('Dark clicks:', dark_clicks);
        
        // Determine which button was clicked
        const ctx = window.dash_clientside.callback_context;
        console.log('Callback context:', ctx);
        
        if (!ctx.triggered.length) {
            console.log('No triggers found');
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        
        const button_id = ctx.triggered[0].prop_id.split('.')[0];
        console.log('Button clicked:', button_id);
        
        if (button_id === 'light-theme-btn') {
            // Switch to light theme
            console.log('Switching to LIGHT theme');
            document.body.className = 'light-theme';
            console.log('Body className after change:', document.body.className);
            console.log('Computed background image:', window.getComputedStyle(document.body).backgroundImage);
            return ['theme-toggle-btn sun-icon active', 'theme-toggle-btn moon-icon'];
        } else if (button_id === 'dark-theme-btn') {
            // Switch to dark theme
            console.log('Switching to DARK theme');
            document.body.className = '';
            console.log('Body className after change:', document.body.className);
            console.log('Computed background image:', window.getComputedStyle(document.body).backgroundImage);
            return ['theme-toggle-btn sun-icon', 'theme-toggle-btn moon-icon active'];
        }
        
        console.log('Unknown button clicked');
        return [window.dash_clientside.no_update, window.dash_clientside.no_update];
    }
    """,
    [
        dash.Output("light-theme-btn", "className"),
        dash.Output("dark-theme-btn", "className"),
    ],
    [
        dash.Input("light-theme-btn", "n_clicks"),
        dash.Input("dark-theme-btn", "n_clicks"),
    ],
    prevent_initial_call=True,
)

# Theme logo swapper callback - changes logo based on selected theme
app.clientside_callback(
    """
    function(light_clicks, dark_clicks) {
        // Existing theme logic
        const ctx = window.dash_clientside.callback_context;
        if (!ctx.triggered.length) {
            return window.dash_clientside.no_update;
        }
        const button_id = ctx.triggered[0].prop_id.split('.')[0];
        var logo = document.querySelector('.logo-image');
        if (button_id === 'light-theme-btn') {
            if (logo) logo.src = 'assets/BinniesLogoDark.png';
        } else if (button_id === 'dark-theme-btn') {
            if (logo) logo.src = 'assets/BinniesLogo.png';
        }
        return window.dash_clientside.no_update;
    }
    """,
    dash.Output("logo-container", "children"),
    [
        dash.Input("light-theme-btn", "n_clicks"),
        dash.Input("dark-theme-btn", "n_clicks"),
    ],
    prevent_initial_call=True,
)

# ===== CALLBACK REGISTRATION =====
# Import and register the split callbacks from the callbacks module
logging.info("Registering split callbacks...")
register_callbacks(app)
logging.info("✅ All callbacks registered successfully!")


# Upload data store callback (simple helper)
@app.callback(
    dash.Output("upload-data-store", "data"),
    dash.Input("upload-ags", "contents"),
    dash.State("upload-ags", "filename"),
)
def store_upload_data(contents, filenames):
    """
    Store uploaded file data in a dcc.Store component for use across callbacks.

    This callback processes uploaded AGS files and stores their contents and filenames
    in a Dash Store component, making the data available to other callbacks without
    requiring re-upload or re-processing.

    Args:
        contents (list/str): Base64 encoded file contents from dcc.Upload
        filenames (list/str): Original filenames of uploaded files

    Returns:
        dict/None: Dictionary containing contents and filenames, or None if no upload

    Structure of returned data:
        {
            "contents": [base64_string1, base64_string2, ...],
            "filenames": ["file1.ags", "file2.ags", ...]
        }
    """
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


# ===== SHAPE HANDLING CALLBACKS =====
# Clientside callbacks for managing drawn shapes on the map

# Create a dcc.Store to track the draw state
app.layout.children.append(dcc.Store(id="draw-state-store", data={"lastUpdate": 0}))

# Primary callback: When a new shape is drawn, keep only the latest and update the draw-state-store
app.clientside_callback(
    """
    function(geojson, oldState) {
        console.log("==== SHAPE CALLBACK TRIGGERED ====");
        if (!geojson || !geojson.features) {
            console.log("No geojson or features available");
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        const timestamp = new Date().getTime();
        console.log(`Time: ${timestamp}, Features count: ${geojson.features.length}`);
        if (geojson.features.length === 0) {
            console.log("No features to process");
            return [window.dash_clientside.no_update, oldState];
        }
        // Only process if it's actually a new shape (check timestamp)
        if (oldState && (timestamp - oldState.lastUpdate < 500)) {
            console.log("Ignoring rapid consecutive updates");
            return [window.dash_clientside.no_update, oldState];
        }
        console.log("Processing new shape, clearing old shapes");
        // Keep only the most recent feature
        const latestFeature = geojson.features[geojson.features.length - 1];
        console.log(`Latest feature type: ${latestFeature.geometry.type}`);
        // Create new state
        const newState = {
            lastUpdate: timestamp,
            featureCount: 1,
            featureType: latestFeature.geometry.type
        };
        // Return the new state with the timestamp to trigger clear_all in the next callback
        return [
            {
                type: 'FeatureCollection',
                features: [latestFeature]
            },
            newState
        ];
    }
    """,
    [dash.Output("draw-control", "geojson"), dash.Output("draw-state-store", "data")],
    [dash.Input("draw-control", "geojson")],
    [dash.State("draw-state-store", "data")],
    prevent_initial_call=True,
)

# Secondary callback: Use state changes to clear all layers
app.clientside_callback(
    """
    function(state) {
        console.log("==== CLEAR LAYERS CALLBACK ====");
        if (!state || !state.lastUpdate) {
            console.log("No state available");
            return window.dash_clientside.no_update;
        }
        console.log(`Clearing all layers at time: ${state.lastUpdate}`);
        
        // Return a timestamp to trigger clear_all
        return new Date().getTime();
    }
    """,
    dash.Output("draw-control", "clear_all", allow_duplicate=True),
    dash.Input("draw-state-store", "data"),
    prevent_initial_call=True,
)

# Direct map update callback - replace with a logging function only
# Removed this callback to avoid duplicate center outputs


# ===== APPLICATION EXECUTION =====
# Main execution block - runs when script is executed directly
if __name__ == "__main__":
    try:
        logging.info("Opening browser and starting Dash server")
        webbrowser.open("http://127.0.0.1:8050/")  # Open web browser to app URL
        app.run(debug=True, host="0.0.0.0", port=8050)  # Start Dash development server
    except Exception as e:
        logging.error(f"Error starting app: {str(e)}")
        print(f"Error: {str(e)}")
