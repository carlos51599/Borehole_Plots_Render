"""
Figure and Plot Configuration Settings

This module contains all configuration constants related to figure sizes,
plot dimensions, and font sizes for different plot types.
"""

# ===== MAP DISPLAY CONFIGURATION =====
# Map display size
MAP_HEIGHT = 500  # in pixels
MAP_WIDTH = "100%"  # Use percentage for responsive width

# ===== INDIVIDUAL BOREHOLE LOG CONFIGURATION =====
# Individual borehole log figure size
LOG_FIG_HEIGHT = 4
LOG_FIG_WIDTH = 2.5

# Individual borehole log plot font sizes
LOG_PLOT_LABEL_FONTSIZE = 8
LOG_PLOT_AXIS_FONTSIZE = 9
LOG_PLOT_TITLE_FONTSIZE = 10

# ===== SECTION PLOT CONFIGURATION =====
# Section plot figure size (cross-section showing multiple boreholes)
SECTION_BASE_HEIGHT = 5
SECTION_MAX_HEIGHT = 6
SECTION_MIN_WIDTH = 8
SECTION_WIDTH_PER_BH = 1.5

# Section plot font sizes
SECTION_PLOT_LABEL_FONTSIZE = 10
SECTION_PLOT_AXIS_FONTSIZE = 11
SECTION_PLOT_TITLE_FONTSIZE = 12
SECTION_PLOT_LEGEND_FONTSIZE = 9
