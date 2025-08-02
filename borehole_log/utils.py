"""
Professional Borehole Log Utilities Module

This module provides core utility functions extracted from the monolithic
borehole_log_professional.py implementation. These utilities handle figure
management, text processing, and coordinate calculations while maintaining
100% compatibility with the original implementation.

Key Functions:
- matplotlib_figure: Context manager for safe figure handling
- safe_close_figure: Memory-safe figure cleanup
- wrap_text_and_calculate_height: Text wrapping with height calculation

Constants:
- log_col_widths_in: Column width definitions for layout
- DEFAULT_COLOR_ALPHA: Standard transparency for geological colors
- DEFAULT_HATCH_ALPHA: Standard transparency for geological patterns
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import logging
import textwrap
import base64
import io
from contextlib import contextmanager
from typing import Tuple, Optional, List

# Define log column widths (single source of truth from monolithic implementation)
log_col_widths_in = [0.05, 0.08, 0.04, 0.14, 0.07, 0.07, 0.08, 0.42, 0.05]

# Transparency defaults (from monolithic implementation)
DEFAULT_COLOR_ALPHA = 0.4
DEFAULT_HATCH_ALPHA = 0.2

# Configure matplotlib for professional rendering (exact copy from monolithic)
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.linewidth"] = 0.5
plt.rcParams["lines.linewidth"] = 1.0

# OPTIMIZATION: Reduce matplotlib logging verbosity for better performance
# Prevents excessive font manager debug output during plot generation
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("matplotlib.pyplot").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@contextmanager
def matplotlib_figure(*args, **kwargs):
    """
    Context manager for matplotlib figures to ensure proper cleanup.

    Exact copy from monolithic borehole_log_professional.py implementation.

    Usage:
        with matplotlib_figure(figsize=(8, 6)) as fig:
            # work with figure
            pass
    # Figure is automatically closed here
    """
    fig = plt.figure(*args, **kwargs)
    try:
        yield fig
    finally:
        plt.close(fig)


def safe_close_figure(fig):
    """
    Safely close a matplotlib figure with error handling.

    Exact copy from monolithic borehole_log_professional.py implementation.

    Args:
        fig: matplotlib Figure object or None
    """
    if fig is not None:
        try:
            plt.close(fig)
        except Exception as e:
            logger.warning(f"Error closing matplotlib figure: {e}")


def wrap_text_and_calculate_height(text, max_width_chars=45, font_size=8):
    """
    Wrap text and calculate required height in inches for rendering.

    Exact copy from monolithic borehole_log_professional.py implementation.

    Args:
        text: Text to wrap
        max_width_chars: Maximum characters per line
        font_size: Font size in points

    Returns:
        tuple: (wrapped_lines, height_in_inches)
    """
    if not text or pd.isna(text):
        return [""], 0.15  # Minimum height for empty text

    # Wrap text
    wrapped_lines = textwrap.wrap(str(text), width=max_width_chars)
    if not wrapped_lines:  # Empty after wrapping
        wrapped_lines = [""]

    # Calculate height: font_size in points, converted to inches
    # Add some line spacing (1.2x font size per line)
    line_height_inches = (font_size * 1.2) / 72.0  # 72 points per inch
    total_height = len(wrapped_lines) * line_height_inches

    # Minimum height for readability
    min_height = 0.15

    return wrapped_lines, max(total_height, min_height)
