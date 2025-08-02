"""
Configuration Modules Package

Modular configuration system for the Geo Borehole Sections Render application.
This package splits the large config.py file into focused modules while
maintaining backward compatibility.

Modules:
    figures: Figure and plot configuration (sizes, fonts)
    layout: UI layout and text content configuration
    sizing: Element sizing constants and measurements
    styles: Complete style dictionaries for UI components

Usage:
    # Import specific modules
    from config_modules import figures, layout, sizing, styles

    # Or import all into a single namespace (backward compatibility)
    from config_modules import *
"""

# Import all constants from submodules for backward compatibility
from .figures import *
from .layout import *
from .sizing import *
from .styles import *

__all__ = [
    # Re-export everything for backward compatibility
    # Figure configuration
    "MAP_HEIGHT",
    "MAP_WIDTH",
    "LOG_FIG_HEIGHT",
    "LOG_FIG_WIDTH",
    "SECTION_BASE_HEIGHT",
    "SECTION_MAX_HEIGHT",
    "SECTION_MIN_WIDTH",
    "SECTION_WIDTH_PER_BH",
    "LOG_PLOT_LABEL_FONTSIZE",
    "LOG_PLOT_AXIS_FONTSIZE",
    "LOG_PLOT_TITLE_FONTSIZE",
    "SECTION_PLOT_LABEL_FONTSIZE",
    "SECTION_PLOT_AXIS_FONTSIZE",
    "SECTION_PLOT_TITLE_FONTSIZE",
    "SECTION_PLOT_LEGEND_FONTSIZE",
    # Layout and text
    "APP_TITLE",
    "APP_SUBTITLE",
    "MAP_SECTION_TITLE",
    "CHECKBOX_SECTION_TITLE",
    "FILE_BREAKDOWN_TITLE",
    "FILE_UPLOAD_STATUS_TITLE",
    "UPLOAD_PROMPT",
    "CHECKBOX_INSTRUCTIONS",
    "SUCCESS_UPLOAD_MESSAGE",
    "ERROR_UPLOAD_MESSAGE",
    "ERROR_PLOT_MESSAGE",
    "ERROR_SELECTION_MESSAGE",
    "NO_BOREHOLES_MESSAGE",
    "NO_SELECTION_MESSAGE",
    "DOWNLOAD_BUTTON_LABEL",
    "LABELS_CHECKBOX_LABEL",
    "FILE_UPLOAD_SUCCESS_PREFIX",
    "FILE_UPLOAD_SUCCESS_SUFFIX",
    # Alignment constants
    "ALIGN_LEFT",
    "ALIGN_CENTER",
    "ALIGN_RIGHT",
    "ALIGN_JUSTIFY",
    "TEXT_ALIGN_LEFT",
    "TEXT_ALIGN_CENTER",
    "TEXT_ALIGN_RIGHT",
    "TEXT_ALIGN_JUSTIFY",
    "POSITION_STATIC",
    "POSITION_RELATIVE",
    "POSITION_ABSOLUTE",
    "POSITION_FIXED",
    "JUSTIFY_CONTENT_START",
    "JUSTIFY_CONTENT_CENTER",
    "JUSTIFY_CONTENT_END",
    "JUSTIFY_CONTENT_BETWEEN",
    "JUSTIFY_CONTENT_AROUND",
    "ALIGN_ITEMS_START",
    "ALIGN_ITEMS_CENTER",
    "ALIGN_ITEMS_END",
    "ALIGN_ITEMS_STRETCH",
    # Sizing constants
    "HEADER_H1_SIZE",
    "HEADER_H2_SIZE",
    "HEADER_H3_SIZE",
    "HEADER_H4_SIZE",
    "HEADER_H5_SIZE",
    "HEADER_H1_LINE_HEIGHT",
    "HEADER_H2_LINE_HEIGHT",
    "HEADER_H3_LINE_HEIGHT",
    "HEADER_H4_LINE_HEIGHT",
    "CONTAINER_MAX_WIDTH",
    "CONTAINER_MARGIN",
    "CONTAINER_PADDING",
    "BUTTON_HEIGHT",
    "BUTTON_MIN_WIDTH",
    "BUTTON_PADDING",
    "BUTTON_BORDER_RADIUS",
    "BUTTON_FONT_SIZE",
    # Style dictionaries
    "HEADER_H1_LEFT_STYLE",
    "HEADER_H1_CENTER_STYLE",
    "HEADER_H1_RIGHT_STYLE",
    "HEADER_H2_LEFT_STYLE",
    "HEADER_H2_CENTER_STYLE",
    "HEADER_H2_RIGHT_STYLE",
    "HEADER_H3_LEFT_STYLE",
    "HEADER_H3_CENTER_STYLE",
    "HEADER_H4_LEFT_STYLE",
    "MAIN_CONTAINER_STYLE",
    "UPLOAD_AREA_CENTER_STYLE",
    "MAP_CENTER_STYLE",
    "MAP_CONTAINER_STYLE",
    "BUTTON_LEFT_STYLE",
    "BUTTON_CENTER_STYLE",
    "BUTTON_RIGHT_STYLE",
    "CHECKBOX_CONTROL_STYLE",
    "DESCRIPTION_TEXT_STYLE",
    "CHECKBOX_LABEL_STYLE",
    "CHECKBOX_LEFT_STYLE",
    # Colors and styling
    "PRIMARY_COLOR",
    "ERROR_COLOR",
    "WARNING_COLOR",
    "CHECKBOX_BG_COLOR",
    "CHECKBOX_BORDER_COLOR",
    "FILE_BREAKDOWN_BG_COLOR",
]

__version__ = "1.0.0"
__author__ = "Geological Cross-Section Renderer"
