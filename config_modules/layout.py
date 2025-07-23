"""
UI Layout and Text Content Configuration

This module contains all UI layout configuration including titles, labels,
messages, and alignment constants.
"""

# ===== MAIN APPLICATION LAYOUT =====
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
