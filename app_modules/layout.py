"""
Main application layout components.

This module defines the complete Dash application layout with all UI components
including the header, map, file upload, and output sections.
"""

import dash
from dash import html, dcc
import dash_leaflet as dl
from dash_leaflet import EditControl

# Import configuration from new modular structure
from config_modules import (
    APP_TITLE,
    APP_SUBTITLE,
    MAP_SECTION_TITLE,
    UPLOAD_PROMPT,
    LABELS_CHECKBOX_LABEL,
    DOWNLOAD_BUTTON_LABEL,
    HEADER_H1_CENTER_STYLE,
    HEADER_H2_CENTER_STYLE,
    HEADER_H2_LEFT_STYLE,
    HEADER_H4_LEFT_STYLE,
    UPLOAD_AREA_CENTER_STYLE,
    MAP_CONTAINER_STYLE,
    CHECKBOX_CONTROL_STYLE,
    BUTTON_RIGHT_STYLE,
)


def create_header_section():
    """
    Create the header section with logo and theme toggle buttons.

    Returns:
        list: List of Dash components for the header
    """
    return [
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
        html.H1(APP_TITLE, style=HEADER_H1_CENTER_STYLE),
        html.P(APP_SUBTITLE, style=HEADER_H2_CENTER_STYLE),
    ]


def create_file_upload_section():
    """
    Create the file upload section for AGS files.

    Returns:
        list: List of Dash components for file upload
    """
    return [
        # ===== FILE UPLOAD SECTION =====
        # AGS file upload component with drag-and-drop functionality
        dcc.Upload(
            id="upload-ags",
            children=html.Div(["Drag and Drop or ", html.A(UPLOAD_PROMPT)]),
            style=UPLOAD_AREA_CENTER_STYLE,
            multiple=True,
            accept=".ags",
        ),
        html.Div(id="output-upload"),
        html.Hr(),
    ]


def create_search_section():
    """
    Create the borehole search functionality section.

    Returns:
        html.Div: Search section component
    """
    return html.Div(
        [
            html.H3(
                "Search for Borehole",
                style={
                    **HEADER_H4_LEFT_STYLE,
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
    )


def create_map_layers():
    """
    Create map layers for the interactive map.

    Returns:
        list: List of map layer components
    """
    return [
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
    ]


def create_map_feature_groups():
    """
    Create feature groups for the interactive map.

    Returns:
        list: List of feature group components
    """
    return [
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
    ]


def create_interactive_map():
    """
    Create the main interactive map component.

    Returns:
        dl.Map: Interactive map component
    """
    map_children = create_map_layers() + create_map_feature_groups()

    return dl.Map(
        map_children,
        id="borehole-map",
        center=[51.5, -0.1],  # Default center on UK
        zoom=6,
        style=MAP_CONTAINER_STYLE,
    )


def create_buffer_controls():
    """
    Create buffer control section for polyline adjustments.

    Returns:
        html.Div: Buffer controls component
    """
    return html.Div(
        [
            html.H3(
                "Buffer Settings",
                style={"marginTop": "20px", "marginBottom": "10px"},
            ),
            html.Div(
                [
                    html.Label(
                        "Polyline Buffer (meters):", style={"marginRight": "10px"}
                    ),
                    dcc.Input(
                        id="buffer-input",
                        type="number",
                        value=50,
                        min=1,
                        max=500,
                        step=1,
                        style={"width": "100px", "marginRight": "10px"},
                    ),
                    html.Button(
                        "Update Buffer",
                        id="update-buffer-btn",
                        n_clicks=0,
                        style={"marginLeft": "10px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "10px",
                },
            ),
        ],
        id="buffer-controls",
        style={"display": "none"},  # Initially hidden, shown when polyline is drawn
    )


def create_output_sections():
    """
    Create output sections for plots and controls.

    Returns:
        list: List of output section components
    """
    return [
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
                    options=[{"label": LABELS_CHECKBOX_LABEL, "value": "show_labels"}],
                    value=["show_labels"],
                    inline=True,
                    style=CHECKBOX_CONTROL_STYLE,
                ),
                html.Button(
                    DOWNLOAD_BUTTON_LABEL,
                    id="download-section-btn",
                    n_clicks=0,
                    style=BUTTON_RIGHT_STYLE,
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
    ]


def create_data_stores():
    """
    Create data store components for sharing data between callbacks.

    Returns:
        list: List of dcc.Store components
    """
    return [
        # ===== DATA STORES =====
        # Store components for data sharing between callbacks
        dcc.Store(id="upload-data-store"),  # Uploaded file data
        dcc.Store(id="borehole-data-store"),  # Processed borehole data
        dcc.Store(id="search-selected-borehole", data=None),  # Search selection state
        dcc.Store(id="draw-state-store", data={"lastUpdate": 0}),  # Draw state tracking
    ]


def create_main_content_section():
    """
    Create the main content section with map and search.

    Returns:
        html.Div: Main content section
    """
    return html.Div(
        [
            html.H2(MAP_SECTION_TITLE, style=HEADER_H2_LEFT_STYLE),
            create_search_section(),
            create_interactive_map(),
        ]
    )


def create_complete_layout():
    """
    Create the complete application layout by combining all sections.

    Returns:
        html.Div: Complete application layout
    """
    layout_components = (
        create_header_section()
        + create_file_upload_section()
        + [create_main_content_section()]
        + [create_buffer_controls()]
        + create_output_sections()
        + create_data_stores()
    )

    return html.Div(
        layout_components,
        className="dash-container",  # Add a class for styling the main container
    )
