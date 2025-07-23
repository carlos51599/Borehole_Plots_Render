"""
UI Style Dictionaries

This module contains all the main style dictionaries used throughout the
application for consistent styling.
"""

# Import sizing and layout constants
from .sizing import (
    HEADER_H1_SIZE,
    HEADER_H2_SIZE,
    HEADER_H3_SIZE,
    HEADER_H4_SIZE,
    HEADER_H1_LINE_HEIGHT,
    HEADER_H2_LINE_HEIGHT,
    HEADER_H3_LINE_HEIGHT,
    HEADER_H4_LINE_HEIGHT,
    BUTTON_HEIGHT,
    BUTTON_MIN_WIDTH,
    BUTTON_PADDING,
    BUTTON_BORDER_RADIUS,
    BUTTON_FONT_SIZE,
    MAP_HEIGHT,
    MAP_WIDTH,
    UPLOAD_AREA_HEIGHT,
    UPLOAD_AREA_LINE_HEIGHT,
    UPLOAD_AREA_BORDER_RADIUS,
    CONTAINER_MAX_WIDTH,
    CONTAINER_MARGIN,
    CONTAINER_PADDING,
)
from .layout import (
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_RIGHT,
    JUSTIFY_CONTENT_CENTER,
    ALIGN_ITEMS_CENTER,
)

# ===== COLOR CONFIGURATION =====
PRIMARY_COLOR = "#006600"  # Green for headers and success messages
ERROR_COLOR = "red"
WARNING_COLOR = "orange"
CHECKBOX_BG_COLOR = "#e8f5e8"  # Light green background for checkboxes
CHECKBOX_BORDER_COLOR = "#28a745"  # Green border for checkboxes
FILE_BREAKDOWN_BG_COLOR = "#f9f9f9"  # Light gray for file breakdown

# ===== FONT AND SPACING =====
PRIMARY_FONT_SIZE = "14px"
SECONDARY_FONT_SIZE = "12px"
SMALL_FONT_SIZE = "8px"

STANDARD_MARGIN_TOP = "1em"
STANDARD_MARGIN_BOTTOM = "0.5em"
SMALL_MARGIN = "0.3em"
LARGE_MARGIN = "2em"
BUTTON_MARGIN_LEFT = "1em"

BORDER_RADIUS = "5px"
BORDER_WIDTH = "1px"
BORDER_STYLE_DASHED = "dashed"
BORDER_STYLE_SOLID = "solid"

# ===== HEADER STYLES =====
HEADER_H1_LEFT_STYLE = {
    "fontSize": HEADER_H1_SIZE,
    "lineHeight": HEADER_H1_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_LEFT,
    "marginBottom": "32px",
}

HEADER_H1_CENTER_STYLE = {
    "fontSize": HEADER_H1_SIZE,
    "lineHeight": HEADER_H1_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_CENTER,
    "marginBottom": "32px",
}

HEADER_H1_RIGHT_STYLE = {
    "fontSize": HEADER_H1_SIZE,
    "lineHeight": HEADER_H1_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_RIGHT,
    "marginBottom": "32px",
}

HEADER_H2_LEFT_STYLE = {
    "fontSize": HEADER_H2_SIZE,
    "lineHeight": HEADER_H2_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_LEFT,
    "marginBottom": "24px",
}

HEADER_H2_CENTER_STYLE = {
    "fontSize": HEADER_H2_SIZE,
    "lineHeight": HEADER_H2_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_CENTER,
    "marginBottom": "24px",
}

HEADER_H2_RIGHT_STYLE = {
    "fontSize": HEADER_H2_SIZE,
    "lineHeight": HEADER_H2_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_RIGHT,
    "marginBottom": "24px",
}

HEADER_H3_LEFT_STYLE = {
    "fontSize": HEADER_H3_SIZE,
    "lineHeight": HEADER_H3_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_LEFT,
    "marginBottom": "20px",
}

HEADER_H3_CENTER_STYLE = {
    "fontSize": HEADER_H3_SIZE,
    "lineHeight": HEADER_H3_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_CENTER,
    "marginBottom": "20px",
}

HEADER_H4_LEFT_STYLE = {
    "fontSize": HEADER_H4_SIZE,
    "lineHeight": HEADER_H4_LINE_HEIGHT,
    "textAlign": TEXT_ALIGN_LEFT,
    "marginBottom": "16px",
}

# ===== LAYOUT STYLES =====
MAIN_CONTAINER_STYLE = {
    "maxWidth": CONTAINER_MAX_WIDTH,
    "margin": CONTAINER_MARGIN,
    "padding": CONTAINER_PADDING,
}

# ===== UPLOAD AREA STYLES =====
UPLOAD_AREA_CENTER_STYLE = {
    "width": "100%",
    "height": UPLOAD_AREA_HEIGHT,
    "lineHeight": UPLOAD_AREA_LINE_HEIGHT,
    "borderWidth": BORDER_WIDTH,
    "borderStyle": BORDER_STYLE_DASHED,
    "borderRadius": BORDER_RADIUS,
    "textAlign": TEXT_ALIGN_CENTER,
    "margin": STANDARD_MARGIN_TOP + " auto " + STANDARD_MARGIN_BOTTOM,
}

# ===== MAP STYLES =====
MAP_CENTER_STYLE = {
    "width": MAP_WIDTH,
    "height": MAP_HEIGHT,
    "margin": "0 auto",
    "display": "block",
}

# ===== BUTTON STYLES =====
BUTTON_LEFT_STYLE = {
    "marginTop": STANDARD_MARGIN_TOP,
    "marginBottom": STANDARD_MARGIN_BOTTOM,
    "height": BUTTON_HEIGHT,
    "minWidth": BUTTON_MIN_WIDTH,
    "padding": BUTTON_PADDING,
    "borderRadius": BUTTON_BORDER_RADIUS,
    "fontSize": BUTTON_FONT_SIZE,
    "textAlign": TEXT_ALIGN_LEFT,
}

BUTTON_CENTER_STYLE = {
    "marginTop": STANDARD_MARGIN_TOP,
    "marginBottom": STANDARD_MARGIN_BOTTOM,
    "height": BUTTON_HEIGHT,
    "minWidth": BUTTON_MIN_WIDTH,
    "padding": BUTTON_PADDING,
    "borderRadius": BUTTON_BORDER_RADIUS,
    "fontSize": BUTTON_FONT_SIZE,
    "textAlign": TEXT_ALIGN_CENTER,
    "display": "block",
    "margin": "0 auto",
}

BUTTON_RIGHT_STYLE = {
    "marginTop": STANDARD_MARGIN_TOP,
    "marginBottom": STANDARD_MARGIN_BOTTOM,
    "height": BUTTON_HEIGHT,
    "minWidth": BUTTON_MIN_WIDTH,
    "padding": BUTTON_PADDING,
    "borderRadius": BUTTON_BORDER_RADIUS,
    "fontSize": BUTTON_FONT_SIZE,
    "textAlign": TEXT_ALIGN_RIGHT,
    "float": "right",
}

# ===== CHECKBOX STYLES =====
CHECKBOX_CONTROL_STYLE = {
    "display": "block",
    "marginTop": STANDARD_MARGIN_TOP,
    "marginBottom": STANDARD_MARGIN_BOTTOM,
    "textAlign": TEXT_ALIGN_LEFT,
}
