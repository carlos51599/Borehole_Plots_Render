"""
Configuration settings for the Geo Borehole Sections Render Dash application.

This module contains all configuration constants used throughout the application,
including:

1. FIGURE/PLOT CONFIGURATION:
   - Map display dimensions and settings
   - Individual borehole log figure sizes
   - Section plot dimensions and scaling
   - Font sizes for different plot types

2. UI LAYOUT CONFIGURATION:
   - Application titles and headers
   - Section headers and labels
   - Button text and prompts

3. ALIGNMENT CONFIGURATION:
   - Layout alignment constants
   - Text alignment options
   - Element positioning values
   - Flexbox alignment settings

4. STYLING CONFIGURATION:
   - Header styles with different alignments
   - Button styles for various positions
   - Map and upload area styling
   - Color schemes and themes

5. COLOR SCHEMES:
   - Geology color mappings (BGS standards)
   - UI element colors
   - Theme-specific color palettes

6. MAP CONFIGURATION:
   - Default map settings
   - Coordinate system parameters
   - Layer configuration options

Usage:
    Import this module in other parts of the application to access
    configuration constants:

    from config import APP_TITLE, MAP_HEIGHT, HEADER_H1_CENTER_STYLE

Author: [Project Team]
Last Modified: July 2025
"""

# ===== FIGURE/PLOT CONFIGURATION =====
# Map display size
MAP_HEIGHT = 500  # in pixels
MAP_WIDTH = "100%"  # Use percentage for responsive width

# Individual borehole log figure size
LOG_FIG_HEIGHT = 4
LOG_FIG_WIDTH = 2.5

# Section plot figure size (cross-section showing multiple boreholes)
SECTION_BASE_HEIGHT = 5
SECTION_MAX_HEIGHT = 6
SECTION_MIN_WIDTH = 8
SECTION_WIDTH_PER_BH = 1.5

# Individual borehole log plot font sizes
LOG_PLOT_LABEL_FONTSIZE = 8
LOG_PLOT_AXIS_FONTSIZE = 9
LOG_PLOT_TITLE_FONTSIZE = 10

# Section plot font sizes
SECTION_PLOT_LABEL_FONTSIZE = 10
SECTION_PLOT_AXIS_FONTSIZE = 11
SECTION_PLOT_TITLE_FONTSIZE = 12
SECTION_PLOT_LEGEND_FONTSIZE = 9

# ===== UI LAYOUT CONFIGURATION =====
# Main application layout
APP_TITLE = "Geo Borehole Sections Render - Dash Version"
APP_SUBTITLE = "Upload one or more AGS files to begin."

# Section headers
MAP_SECTION_TITLE = "Borehole Map"
CHECKBOX_SECTION_TITLE = "Selected Boreholes:"
FILE_BREAKDOWN_TITLE = "📁 File Breakdown"
FILE_UPLOAD_STATUS_TITLE = "📊 File Upload Status"

# ===== ALIGNMENT CONFIGURATION =====
# Layout alignment options
ALIGN_LEFT = "left"
ALIGN_CENTER = "center"
ALIGN_RIGHT = "right"
ALIGN_JUSTIFY = "justify"

# Text alignment
TEXT_ALIGN_LEFT = "left"
TEXT_ALIGN_CENTER = "center"
TEXT_ALIGN_RIGHT = "right"
TEXT_ALIGN_JUSTIFY = "justify"

# Element positioning
POSITION_STATIC = "static"
POSITION_RELATIVE = "relative"
POSITION_ABSOLUTE = "absolute"
POSITION_FIXED = "fixed"

# Flex alignment
JUSTIFY_CONTENT_START = "flex-start"
JUSTIFY_CONTENT_CENTER = "center"
JUSTIFY_CONTENT_END = "flex-end"
JUSTIFY_CONTENT_BETWEEN = "space-between"
JUSTIFY_CONTENT_AROUND = "space-around"

ALIGN_ITEMS_START = "flex-start"
ALIGN_ITEMS_CENTER = "center"
ALIGN_ITEMS_END = "flex-end"
ALIGN_ITEMS_STRETCH = "stretch"

# ===== ELEMENT SIZING CONFIGURATION =====

# --- HEADER ELEMENTS ---
HEADER_H1_SIZE = "2.5rem"
HEADER_H2_SIZE = "2rem"
HEADER_H3_SIZE = "1.75rem"
HEADER_H4_SIZE = "1.5rem"
HEADER_H5_SIZE = "1.25rem"

HEADER_H1_LINE_HEIGHT = "1.2"
HEADER_H2_LINE_HEIGHT = "1.3"
HEADER_H3_LINE_HEIGHT = "1.4"
HEADER_H4_LINE_HEIGHT = "1.4"

# Header alignment options
HEADER_ALIGN_LEFT = TEXT_ALIGN_LEFT
HEADER_ALIGN_CENTER = TEXT_ALIGN_CENTER
HEADER_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# Header style dictionaries
HEADER_H1_LEFT_STYLE = {
    "fontSize": HEADER_H1_SIZE,
    "lineHeight": HEADER_H1_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_LEFT,
    "marginBottom": "32px",
}

HEADER_H1_CENTER_STYLE = {
    "fontSize": HEADER_H1_SIZE,
    "lineHeight": HEADER_H1_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_CENTER,
    "marginBottom": "32px",
}

HEADER_H1_RIGHT_STYLE = {
    "fontSize": HEADER_H1_SIZE,
    "lineHeight": HEADER_H1_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_RIGHT,
    "marginBottom": "32px",
}

HEADER_H2_LEFT_STYLE = {
    "fontSize": HEADER_H2_SIZE,
    "lineHeight": HEADER_H2_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_LEFT,
    "marginBottom": "32px",
}

HEADER_H2_CENTER_STYLE = {
    "fontSize": HEADER_H2_SIZE,
    "lineHeight": HEADER_H2_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_CENTER,
    "marginBottom": "32px",
}

HEADER_H2_RIGHT_STYLE = {
    "fontSize": HEADER_H2_SIZE,
    "lineHeight": HEADER_H2_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_RIGHT,
    "marginBottom": "32px",
}

HEADER_H4_LEFT_STYLE = {
    "fontSize": HEADER_H4_SIZE,
    "lineHeight": HEADER_H4_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_LEFT,
    "marginBottom": "32px",
}

HEADER_H4_CENTER_STYLE = {
    "fontSize": HEADER_H4_SIZE,
    "lineHeight": HEADER_H4_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_CENTER,
    "marginBottom": "32px",
}

HEADER_H4_RIGHT_STYLE = {
    "fontSize": HEADER_H4_SIZE,
    "lineHeight": HEADER_H4_LINE_HEIGHT,
    "textAlign": HEADER_ALIGN_RIGHT,
    "marginBottom": "32px",
}

# --- BUTTON ELEMENTS ---
BUTTON_MIN_WIDTH = "120px"
BUTTON_HEIGHT = "40px"
BUTTON_PADDING_HORIZONTAL = "16px"
BUTTON_PADDING_VERTICAL = "8px"
BUTTON_BORDER_RADIUS = "5px"
BUTTON_FONT_SIZE = "14px"

# Large buttons
BUTTON_LARGE_HEIGHT = "48px"
BUTTON_LARGE_PADDING_H = "24px"
BUTTON_LARGE_PADDING_V = "12px"
BUTTON_LARGE_FONT_SIZE = "16px"

# Small buttons
BUTTON_SMALL_HEIGHT = "32px"
BUTTON_SMALL_PADDING_H = "12px"
BUTTON_SMALL_PADDING_V = "6px"
BUTTON_SMALL_FONT_SIZE = "12px"

# Button alignment options
BUTTON_ALIGN_LEFT = ALIGN_LEFT
BUTTON_ALIGN_CENTER = ALIGN_CENTER
BUTTON_ALIGN_RIGHT = ALIGN_RIGHT

# --- INPUT ELEMENTS ---
INPUT_HEIGHT = "40px"
INPUT_MIN_WIDTH = "200px"
INPUT_PADDING = "8px 12px"
INPUT_BORDER_RADIUS = "4px"
INPUT_FONT_SIZE = "14px"

# Text areas
TEXTAREA_MIN_HEIGHT = "80px"
TEXTAREA_MIN_WIDTH = "300px"

# Input alignment options
INPUT_ALIGN_LEFT = TEXT_ALIGN_LEFT
INPUT_ALIGN_CENTER = TEXT_ALIGN_CENTER
INPUT_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# --- UPLOAD AREA ---
UPLOAD_AREA_WIDTH = "100%"
UPLOAD_AREA_HEIGHT = "60px"
UPLOAD_AREA_LINE_HEIGHT = "60px"
UPLOAD_AREA_MIN_HEIGHT = "100px"
UPLOAD_AREA_BORDER_RADIUS = "8px"

# Upload area alignment options
UPLOAD_ALIGN_LEFT = TEXT_ALIGN_LEFT
UPLOAD_ALIGN_CENTER = TEXT_ALIGN_CENTER
UPLOAD_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# --- MAP ELEMENTS ---
MAP_WIDTH = "100%"
MAP_HEIGHT = 500  # in pixels
MAP_MIN_HEIGHT = "400px"
MAP_MAX_HEIGHT = "800px"
MAP_BORDER_RADIUS = "8px"

# Map alignment options
MAP_ALIGN_LEFT = ALIGN_LEFT
MAP_ALIGN_CENTER = ALIGN_CENTER
MAP_ALIGN_RIGHT = ALIGN_RIGHT

# --- CHECKBOX ELEMENTS ---
CHECKBOX_SIZE = "16px"
CHECKBOX_MARGIN_RIGHT = "8px"
CHECKBOX_LABEL_FONT_SIZE = "14px"
CHECKBOX_GROUP_PADDING = "12px"
CHECKBOX_GROUP_BORDER_RADIUS = "6px"

# Checkbox alignment options
CHECKBOX_ALIGN_LEFT = TEXT_ALIGN_LEFT
CHECKBOX_ALIGN_CENTER = TEXT_ALIGN_CENTER
CHECKBOX_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# --- IMAGE/PLOT ELEMENTS ---
# Individual borehole log plot sizing
LOG_PLOT_MAX_WIDTH = "100%"
LOG_PLOT_MIN_WIDTH = "200px"
LOG_PLOT_DEFAULT_HEIGHT = "400px"
LOG_PLOT_BORDER_RADIUS = "4px"

# Section plot sizing (cross-section showing multiple boreholes)
SECTION_PLOT_MAX_WIDTH = "100%"
SECTION_PLOT_MIN_WIDTH = "600px"
SECTION_PLOT_DEFAULT_HEIGHT = "500px"
SECTION_PLOT_BORDER_RADIUS = "4px"

# General plot alignment options
PLOT_ALIGN_LEFT = TEXT_ALIGN_LEFT
PLOT_ALIGN_CENTER = TEXT_ALIGN_CENTER
PLOT_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# Individual log plot alignment options
LOG_PLOT_ALIGN_LEFT = TEXT_ALIGN_LEFT
LOG_PLOT_ALIGN_CENTER = TEXT_ALIGN_CENTER
LOG_PLOT_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# Section plot alignment options
SECTION_PLOT_ALIGN_LEFT = TEXT_ALIGN_LEFT
SECTION_PLOT_ALIGN_CENTER = TEXT_ALIGN_CENTER
SECTION_PLOT_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# --- CONTAINER ELEMENTS ---
CONTAINER_MAX_WIDTH = "1200px"
CONTAINER_PADDING = "20px"
CONTAINER_MARGIN = "0 auto"

SECTION_PADDING = "24px"
SECTION_MARGIN_BOTTOM = "32px"
SECTION_BORDER_RADIUS = "8px"

# Container alignment options
CONTAINER_ALIGN_LEFT = ALIGN_LEFT
CONTAINER_ALIGN_CENTER = ALIGN_CENTER
CONTAINER_ALIGN_RIGHT = ALIGN_RIGHT

# --- CARD ELEMENTS ---
CARD_PADDING = "16px"
CARD_BORDER_RADIUS = "8px"
CARD_MIN_HEIGHT = "120px"
CARD_SHADOW = "0 2px 4px rgba(0,0,0,0.1)"

# Card alignment options
CARD_ALIGN_LEFT = TEXT_ALIGN_LEFT
CARD_ALIGN_CENTER = TEXT_ALIGN_CENTER
CARD_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# --- LIST ELEMENTS ---
LIST_ITEM_PADDING = "8px 0"
LIST_ITEM_MIN_HEIGHT = "32px"

# List alignment options
LIST_ALIGN_LEFT = TEXT_ALIGN_LEFT
LIST_ALIGN_CENTER = TEXT_ALIGN_CENTER
LIST_ALIGN_RIGHT = TEXT_ALIGN_RIGHT

# ===== LAYOUT STYLING WITH ALIGNMENT =====
# --- MAIN LAYOUT CONTAINERS ---
MAIN_CONTAINER_STYLE = {
    "maxWidth": CONTAINER_MAX_WIDTH,
    "margin": CONTAINER_MARGIN,
    "padding": CONTAINER_PADDING,
    "textAlign": ALIGN_LEFT,
}

APP_HEADER_STYLE = {
    "textAlign": TEXT_ALIGN_CENTER,
    "marginBottom": SECTION_MARGIN_BOTTOM,
    "padding": SECTION_PADDING,
}

# --- SECTION LAYOUTS ---
SECTION_LEFT_ALIGNED = {
    "textAlign": TEXT_ALIGN_LEFT,
    "padding": SECTION_PADDING,
    "marginBottom": SECTION_MARGIN_BOTTOM,
}

SECTION_CENTER_ALIGNED = {
    "textAlign": TEXT_ALIGN_CENTER,
    "padding": SECTION_PADDING,
    "marginBottom": SECTION_MARGIN_BOTTOM,
}

SECTION_RIGHT_ALIGNED = {
    "textAlign": TEXT_ALIGN_RIGHT,
    "padding": SECTION_PADDING,
    "marginBottom": SECTION_MARGIN_BOTTOM,
}

# --- FLEX LAYOUTS ---
FLEX_ROW_LEFT = {
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": JUSTIFY_CONTENT_START,
    "alignItems": ALIGN_ITEMS_CENTER,
}

FLEX_ROW_CENTER = {
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": JUSTIFY_CONTENT_CENTER,
    "alignItems": ALIGN_ITEMS_CENTER,
}

FLEX_ROW_RIGHT = {
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": JUSTIFY_CONTENT_END,
    "alignItems": ALIGN_ITEMS_CENTER,
}

FLEX_ROW_BETWEEN = {
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": JUSTIFY_CONTENT_BETWEEN,
    "alignItems": ALIGN_ITEMS_CENTER,
}

FLEX_COLUMN_CENTER = {
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": JUSTIFY_CONTENT_CENTER,
    "alignItems": ALIGN_ITEMS_CENTER,
}

# ===== UI STYLING CONFIGURATION =====
# Colors
PRIMARY_COLOR = "#006600"  # Green for headers and success messages
ERROR_COLOR = "red"
WARNING_COLOR = "orange"
CHECKBOX_BG_COLOR = "#e8f5e8"  # Light green background for checkboxes
CHECKBOX_BORDER_COLOR = "#28a745"  # Green border for checkboxes
FILE_BREAKDOWN_BG_COLOR = "#f9f9f9"  # Light gray for file breakdown

# Font sizes
PRIMARY_FONT_SIZE = "14px"
SECONDARY_FONT_SIZE = "12px"
SMALL_FONT_SIZE = "8px"

# Spacing and margins
STANDARD_MARGIN_TOP = "1em"
STANDARD_MARGIN_BOTTOM = "0.5em"
SMALL_MARGIN = "0.3em"
LARGE_MARGIN = "2em"
BUTTON_MARGIN_LEFT = "1em"

# Element sizing
UPLOAD_AREA_HEIGHT = "60px"
UPLOAD_AREA_LINE_HEIGHT = "60px"
MAP_HEIGHT_PX = "500px"
IMAGE_MAX_WIDTH = "600px"

# Border and corner styling
BORDER_RADIUS = "5px"
BORDER_WIDTH = "1px"
BORDER_STYLE_DASHED = "dashed"
BORDER_STYLE_SOLID = "solid"

# Upload area styling
UPLOAD_AREA_STYLE = {
    "width": "100%",
    "height": UPLOAD_AREA_HEIGHT,
    "lineHeight": UPLOAD_AREA_LINE_HEIGHT,
    "borderWidth": BORDER_WIDTH,
    "borderStyle": BORDER_STYLE_DASHED,
    "borderRadius": BORDER_RADIUS,
    "textAlign": "center",
    "margin": "10px",
}

# Upload area alignment styles
UPLOAD_AREA_LEFT_STYLE = {
    "width": UPLOAD_AREA_WIDTH,
    "height": UPLOAD_AREA_HEIGHT,
    "lineHeight": UPLOAD_AREA_LINE_HEIGHT,
    "borderRadius": UPLOAD_AREA_BORDER_RADIUS,
    "borderWidth": BORDER_WIDTH,
    "borderStyle": BORDER_STYLE_DASHED,
    "textAlign": UPLOAD_ALIGN_LEFT,
    "minHeight": UPLOAD_AREA_MIN_HEIGHT,
    "margin": "10px",
}

UPLOAD_AREA_CENTER_STYLE = {
    "width": UPLOAD_AREA_WIDTH,
    "height": UPLOAD_AREA_HEIGHT,
    "lineHeight": UPLOAD_AREA_LINE_HEIGHT,
    "borderRadius": UPLOAD_AREA_BORDER_RADIUS,
    "borderWidth": BORDER_WIDTH,
    "borderStyle": BORDER_STYLE_DASHED,
    "textAlign": UPLOAD_ALIGN_CENTER,
    "minHeight": UPLOAD_AREA_MIN_HEIGHT,
    "margin": "10px",
}

UPLOAD_AREA_RIGHT_STYLE = {
    "width": UPLOAD_AREA_WIDTH,
    "height": UPLOAD_AREA_HEIGHT,
    "lineHeight": UPLOAD_AREA_LINE_HEIGHT,
    "borderRadius": UPLOAD_AREA_BORDER_RADIUS,
    "borderWidth": BORDER_WIDTH,
    "borderStyle": BORDER_STYLE_DASHED,
    "textAlign": UPLOAD_ALIGN_RIGHT,
    "minHeight": UPLOAD_AREA_MIN_HEIGHT,
    "margin": "10px",
}

# Map container styling
MAP_STYLE = {
    "width": MAP_WIDTH,
    "height": MAP_HEIGHT_PX,
}

# Map alignment styles
MAP_LEFT_STYLE = {
    "width": MAP_WIDTH,
    "height": MAP_HEIGHT,
    "borderRadius": MAP_BORDER_RADIUS,
    "textAlign": MAP_ALIGN_LEFT,
}

MAP_CENTER_STYLE = {
    "width": MAP_WIDTH,
    "height": MAP_HEIGHT,
    "borderRadius": MAP_BORDER_RADIUS,
    "textAlign": MAP_ALIGN_CENTER,
    "margin": "0 auto",
}

MAP_RIGHT_STYLE = {
    "width": MAP_WIDTH,
    "height": MAP_HEIGHT,
    "borderRadius": MAP_BORDER_RADIUS,
    "textAlign": MAP_ALIGN_RIGHT,
    "marginLeft": "auto",
}

# Checkbox grid styling
CHECKBOX_CONTAINER_STYLE = {
    "marginTop": STANDARD_MARGIN_BOTTOM,
    "marginBottom": STANDARD_MARGIN_TOP,
    "padding": "10px",
    "backgroundColor": CHECKBOX_BG_COLOR,
    "borderRadius": BORDER_RADIUS,
    "border": f"{BORDER_WIDTH} {BORDER_STYLE_SOLID} {CHECKBOX_BORDER_COLOR}",
}

CHECKBOX_LABEL_STYLE = {
    "display": "inline-block",
    "marginRight": STANDARD_MARGIN_TOP,
    "marginBottom": SMALL_MARGIN,
    "fontSize": PRIMARY_FONT_SIZE,
}

# Checkbox alignment styles
CHECKBOX_LEFT_STYLE = {
    "padding": CHECKBOX_GROUP_PADDING,
    "borderRadius": CHECKBOX_GROUP_BORDER_RADIUS,
    "backgroundColor": CHECKBOX_BG_COLOR,
    "border": f"{BORDER_WIDTH} {BORDER_STYLE_SOLID} {CHECKBOX_BORDER_COLOR}",
    "textAlign": CHECKBOX_ALIGN_LEFT,
    "marginTop": STANDARD_MARGIN_BOTTOM,
    "marginBottom": STANDARD_MARGIN_TOP,
}

CHECKBOX_CENTER_STYLE = {
    "padding": CHECKBOX_GROUP_PADDING,
    "borderRadius": CHECKBOX_GROUP_BORDER_RADIUS,
    "backgroundColor": CHECKBOX_BG_COLOR,
    "border": f"{BORDER_WIDTH} {BORDER_STYLE_SOLID} {CHECKBOX_BORDER_COLOR}",
    "textAlign": CHECKBOX_ALIGN_CENTER,
    "marginTop": STANDARD_MARGIN_BOTTOM,
    "marginBottom": STANDARD_MARGIN_TOP,
}

CHECKBOX_RIGHT_STYLE = {
    "padding": CHECKBOX_GROUP_PADDING,
    "borderRadius": CHECKBOX_GROUP_BORDER_RADIUS,
    "backgroundColor": CHECKBOX_BG_COLOR,
    "border": f"{BORDER_WIDTH} {BORDER_STYLE_SOLID} {CHECKBOX_BORDER_COLOR}",
    "textAlign": CHECKBOX_ALIGN_RIGHT,
    "marginTop": STANDARD_MARGIN_BOTTOM,
    "marginBottom": STANDARD_MARGIN_TOP,
}

# Header styling
SECTION_HEADER_STYLE = {
    "marginTop": STANDARD_MARGIN_TOP,
    "marginBottom": STANDARD_MARGIN_BOTTOM,
}

DESCRIPTION_TEXT_STYLE = {
    "fontSize": PRIMARY_FONT_SIZE,
    "color": "#666",
    "marginBottom": STANDARD_MARGIN_BOTTOM,
}

# Button styling
BUTTON_STYLE = {
    "marginLeft": BUTTON_MARGIN_LEFT,
}

# Button alignment styles
BUTTON_LEFT_STYLE = {
    "minWidth": BUTTON_MIN_WIDTH,
    "height": BUTTON_HEIGHT,
    "padding": f"{BUTTON_PADDING_VERTICAL} {BUTTON_PADDING_HORIZONTAL}",
    "borderRadius": BUTTON_BORDER_RADIUS,
    "fontSize": BUTTON_FONT_SIZE,
    "textAlign": BUTTON_ALIGN_LEFT,
    "marginLeft": BUTTON_MARGIN_LEFT,
}

BUTTON_CENTER_STYLE = {
    "minWidth": BUTTON_MIN_WIDTH,
    "height": BUTTON_HEIGHT,
    "padding": f"{BUTTON_PADDING_VERTICAL} {BUTTON_PADDING_HORIZONTAL}",
    "borderRadius": BUTTON_BORDER_RADIUS,
    "fontSize": BUTTON_FONT_SIZE,
    "textAlign": BUTTON_ALIGN_CENTER,
    "margin": "0 auto",
}

BUTTON_RIGHT_STYLE = {
    "minWidth": BUTTON_MIN_WIDTH,
    "height": BUTTON_HEIGHT,
    "padding": f"{BUTTON_PADDING_VERTICAL} {BUTTON_PADDING_HORIZONTAL}",
    "borderRadius": BUTTON_BORDER_RADIUS,
    "fontSize": BUTTON_FONT_SIZE,
    "textAlign": BUTTON_ALIGN_RIGHT,
    "float": "right",
}

CHECKBOX_CONTROL_STYLE = {
    "marginTop": STANDARD_MARGIN_TOP,
}

# Image/plot styling
# Individual borehole log plot styling
LOG_PLOT_IMAGE_STYLE = {
    "maxWidth": LOG_PLOT_MAX_WIDTH,
    "minWidth": LOG_PLOT_MIN_WIDTH,
    "height": LOG_PLOT_DEFAULT_HEIGHT,
    "marginTop": LARGE_MARGIN,
}

# Section plot styling (cross-section showing multiple boreholes)
SECTION_PLOT_IMAGE_STYLE = {
    "maxWidth": SECTION_PLOT_MAX_WIDTH,
    "minWidth": SECTION_PLOT_MIN_WIDTH,
    "height": SECTION_PLOT_DEFAULT_HEIGHT,
    "marginTop": LARGE_MARGIN,
}

# Legacy plot styling (for backward compatibility)
PLOT_IMAGE_STYLE = {
    "maxWidth": IMAGE_MAX_WIDTH,
    "marginTop": LARGE_MARGIN,
}

# Error message styling
ERROR_MESSAGE_STYLE = {
    "color": ERROR_COLOR,
}

WARNING_MESSAGE_STYLE = {
    "color": WARNING_COLOR,
}

SUCCESS_MESSAGE_STYLE = {
    "color": PRIMARY_COLOR,
}

# File breakdown styling
FILE_BREAKDOWN_STYLE = {
    "margin": "15px",
    "padding": "10px",
    "border": f"{BORDER_WIDTH} {BORDER_STYLE_SOLID} #ddd",
    "backgroundColor": FILE_BREAKDOWN_BG_COLOR,
}

# Hidden element styling
HIDDEN_ELEMENT_STYLE = {
    "display": "none",
}

# ===== TEXT CONTENT CONFIGURATION =====
# User interface messages
UPLOAD_PROMPT = "Select AGS Files"
CHECKBOX_INSTRUCTIONS = (
    "Found boreholes in the selected area. Uncheck any you want to exclude from plots:"
)
SUCCESS_UPLOAD_MESSAGE = "✓ Successfully uploaded and processed files"
ERROR_UPLOAD_MESSAGE = "✗ Error processing upload"
ERROR_PLOT_MESSAGE = "✗ Could not generate plot"
ERROR_SELECTION_MESSAGE = "✗ Error processing selection"
NO_BOREHOLES_MESSAGE = "No boreholes found in selected area."
NO_SELECTION_MESSAGE = "No boreholes selected for plotting."

# Button labels
DOWNLOAD_BUTTON_LABEL = "Download Section Plot"
LABELS_CHECKBOX_LABEL = "Labels"

# File upload messages
FILE_UPLOAD_SUCCESS_PREFIX = "✓ Section plot for"
FILE_UPLOAD_SUCCESS_SUFFIX = "selected boreholes."
PLOT_UPDATE_SUCCESS_PREFIX = "✓ Updated plot for"
PLOT_UPDATE_SUCCESS_SUFFIX = "selected boreholes."

# ===== PLOT-SPECIFIC STYLE DICTIONARIES WITH ALIGNMENT =====

# --- INDIVIDUAL BOREHOLE LOG PLOT STYLES ---
LOG_PLOT_LEFT_STYLE = {
    "maxWidth": LOG_PLOT_MAX_WIDTH,
    "minWidth": LOG_PLOT_MIN_WIDTH,
    "height": LOG_PLOT_DEFAULT_HEIGHT,
    "borderRadius": LOG_PLOT_BORDER_RADIUS,
    "textAlign": LOG_PLOT_ALIGN_LEFT,
    "marginTop": LARGE_MARGIN,
}

LOG_PLOT_CENTER_STYLE = {
    "maxWidth": LOG_PLOT_MAX_WIDTH,
    "minWidth": LOG_PLOT_MIN_WIDTH,
    "height": LOG_PLOT_DEFAULT_HEIGHT,
    "borderRadius": LOG_PLOT_BORDER_RADIUS,
    "textAlign": LOG_PLOT_ALIGN_CENTER,
    "marginTop": LARGE_MARGIN,
    "margin": "0 auto",
}

LOG_PLOT_RIGHT_STYLE = {
    "maxWidth": LOG_PLOT_MAX_WIDTH,
    "minWidth": LOG_PLOT_MIN_WIDTH,
    "height": LOG_PLOT_DEFAULT_HEIGHT,
    "borderRadius": LOG_PLOT_BORDER_RADIUS,
    "textAlign": LOG_PLOT_ALIGN_RIGHT,
    "marginTop": LARGE_MARGIN,
    "marginLeft": "auto",
}

# --- SECTION PLOT STYLES ---
SECTION_PLOT_LEFT_STYLE = {
    "maxWidth": SECTION_PLOT_MAX_WIDTH,
    "minWidth": SECTION_PLOT_MIN_WIDTH,
    "height": SECTION_PLOT_DEFAULT_HEIGHT,
    "borderRadius": SECTION_PLOT_BORDER_RADIUS,
    "textAlign": SECTION_PLOT_ALIGN_LEFT,
    "marginTop": LARGE_MARGIN,
}

SECTION_PLOT_CENTER_STYLE = {
    "maxWidth": SECTION_PLOT_MAX_WIDTH,
    "minWidth": SECTION_PLOT_MIN_WIDTH,
    "height": SECTION_PLOT_DEFAULT_HEIGHT,
    "borderRadius": SECTION_PLOT_BORDER_RADIUS,
    "textAlign": SECTION_PLOT_ALIGN_CENTER,
    "marginTop": LARGE_MARGIN,
    "margin": "0 auto",
}

SECTION_PLOT_RIGHT_STYLE = {
    "maxWidth": SECTION_PLOT_MAX_WIDTH,
    "minWidth": SECTION_PLOT_MIN_WIDTH,
    "height": SECTION_PLOT_DEFAULT_HEIGHT,
    "borderRadius": SECTION_PLOT_BORDER_RADIUS,
    "textAlign": SECTION_PLOT_ALIGN_RIGHT,
    "marginTop": LARGE_MARGIN,
    "marginLeft": "auto",
}

# --- LAYOUT COMBINATIONS FOR PLOTS ---
# Individual log plot section with left-aligned title and centered plot
LOG_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER = {
    "titleStyle": HEADER_H2_LEFT_STYLE,
    "plotStyle": LOG_PLOT_CENTER_STYLE,
    "containerStyle": SECTION_LEFT_ALIGNED,
}

# Section plot section with left-aligned title and centered plot
SECTION_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER = {
    "titleStyle": HEADER_H2_LEFT_STYLE,
    "plotStyle": SECTION_PLOT_CENTER_STYLE,
    "containerStyle": SECTION_LEFT_ALIGNED,
}

# Side-by-side log plots
LOG_PLOTS_SIDE_BY_SIDE = {
    "containerStyle": FLEX_ROW_CENTER,
    "plotStyle": LOG_PLOT_CENTER_STYLE,
}

# ===== CONFIGURATION USAGE GUIDE =====
"""
USAGE GUIDE FOR CONFIG.PY

This configuration file provides comprehensive styling and layout options for the Dash application.
The config is organized into the following sections:

1. FIGURE/PLOT CONFIGURATION
   - Contains separate sizing and styling for different plot types:
     * Individual borehole log plots (LOG_*)
     * Section plots showing multiple boreholes (SECTION_PLOT_*)
     * Map display settings
   - Use these constants for consistent plot dimensions and fonts across the app

2. UI LAYOUT CONFIGURATION
   - App titles, section headers, and user-facing text
   - Modify these to change application content

3. ALIGNMENT CONFIGURATION
   - Basic alignment constants (left, center, right, justify)
   - Flex alignment options for advanced layouts
   - Use these for consistent alignment across elements

4. ELEMENT SIZING CONFIGURATION
   - Organized by element type (headers, buttons, inputs, etc.)
   - Each section includes alignment options specific to that element
   - Provides consistent sizing across the application

5. LAYOUT STYLING WITH ALIGNMENT
   - Pre-built layout dictionaries for common patterns
   - Includes main containers, sections, and flex layouts
   - Use these for consistent layout structure

6. ELEMENT-SPECIFIC STYLE DICTIONARIES
   - Complete style dictionaries for each element type
   - Available in left, center, and right alignment variants
   - Ready to use in Dash components

7. LAYOUT COMBINATIONS AND RESPONSIVE UTILITIES
   - Common layout combinations for typical UI patterns
   - Responsive design utilities and breakpoints
   - Grid system for flexible layouts
   - Animation and transition utilities

EXAMPLE USAGE:

# Using alignment-specific styles
html.H1("My Title", style=config.HEADER_H1_CENTER_STYLE)
html.Button("Click Me", style=config.BUTTON_RIGHT_STYLE)

# Using layout combinations
app.layout = html.Div([
    html.Div([
        html.H1("App Title", style=config.HEADER_TITLE_CENTER_SUBTITLE_LEFT["titleStyle"]),
        html.P("Subtitle", style=config.HEADER_TITLE_CENTER_SUBTITLE_LEFT["subtitleStyle"])
    ], style=config.HEADER_TITLE_CENTER_SUBTITLE_LEFT["containerStyle"]),
    
    html.Div([
        dcc.Upload(style=config.UPLOAD_AREA_CENTER_STYLE)
    ], style=config.UPLOAD_SECTION_CENTERED["containerStyle"])
], style=config.MAIN_CONTAINER_STYLE)

# Using responsive utilities
responsive_container = {
    **config.CONTAINER_CENTER_STYLE,
    "maxWidth": config.CONTAINER_LARGE,  # Responsive width
    "fontSize": config.FONT_SIZE_BASE,   # Responsive font size
    "padding": config.SPACING_LG,        # Responsive spacing
}

# Using grid system
grid_layout = {
    "display": "grid",
    "gridTemplateColumns": f"{config.GRID_COL_6} {config.GRID_COL_6}",  # Two equal columns
    "gridGap": config.GRID_GAP_BASE,
}

PLOT TYPE SPECIFIC EXAMPLES:

# Individual borehole log plots
html.Img(src="log_plot.png", style=config.LOG_PLOT_CENTER_STYLE)
html.H3("Borehole Log", style=config.HEADER_H3_LEFT_STYLE)

# Section plots (showing multiple boreholes)
html.Img(src="section_plot.png", style=config.SECTION_PLOT_CENTER_STYLE)
html.H2("Cross Section", style=config.HEADER_H2_LEFT_STYLE)

# Using layout combinations
section_layout = html.Div([
    html.H2("Section Plot", style=config.SECTION_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER["titleStyle"]),
    html.Img(src="section.png", style=config.SECTION_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER["plotStyle"])
], style=config.SECTION_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER["containerStyle"])

log_layout = html.Div([
    html.H2("Individual Log", style=config.LOG_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER["titleStyle"]),
    html.Img(src="log.png", style=config.LOG_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER["plotStyle"])
], style=config.LOG_PLOT_SECTION_TITLE_LEFT_PLOT_CENTER["containerStyle"])

FONT SIZE CONFIGURATION:
- Individual log plots use LOG_PLOT_LABEL_FONTSIZE, LOG_PLOT_AXIS_FONTSIZE, LOG_PLOT_TITLE_FONTSIZE
- Section plots use SECTION_PLOT_LABEL_FONTSIZE, SECTION_PLOT_AXIS_FONTSIZE, SECTION_PLOT_TITLE_FONTSIZE

PLOT SIZING:
- Individual log plots: smaller, optimized for single borehole display
- Section plots: larger, optimized for multiple boreholes and cross-sections
"""
