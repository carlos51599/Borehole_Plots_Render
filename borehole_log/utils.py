"""
Borehole Log Utilities Module

This module provides utility functions for borehole log generation including
figure management, text processing, and coordinate calculations.

Key Functions:
- matplotlib_figure: Context manager for safe figure handling
- safe_close_figure: Memory-safe figure cleanup
- wrap_text_and_calculate_height: Text wrapping with height calculation
- format_measurement: Consistent measurement formatting
- calculate_text_metrics: Text sizing and positioning calculations
"""

import matplotlib.pyplot as plt
import logging
import textwrap
from contextlib import contextmanager
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Configure matplotlib for professional rendering
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.linewidth"] = 0.5
plt.rcParams["lines.linewidth"] = 1.0

# OPTIMIZATION: Reduce matplotlib logging verbosity for better performance
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("matplotlib.pyplot").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)


@contextmanager
def matplotlib_figure(*args, **kwargs):
    """
    Context manager for matplotlib figures to ensure proper cleanup.

    Args:
        *args: Arguments passed to plt.figure()
        **kwargs: Keyword arguments passed to plt.figure()

    Yields:
        matplotlib.figure.Figure: The created figure

    Example:
        with matplotlib_figure(figsize=(8, 11)) as fig:
            ax = fig.add_subplot(111)
            # Figure automatically cleaned up on exit
    """
    fig = None
    try:
        fig = plt.figure(*args, **kwargs)
        yield fig
    finally:
        if fig is not None:
            safe_close_figure(fig)


def safe_close_figure(fig):
    """
    Safely close a matplotlib figure and clean up memory.

    Args:
        fig: matplotlib.figure.Figure to close
    """
    try:
        if fig is not None:
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Error closing figure: {e}")


def wrap_text_and_calculate_height(
    text: str, max_width_chars: int = 45, font_size: int = 8
) -> Tuple[str, float]:
    """
    Wrap text to fit within specified character width and calculate required height.

    Args:
        text: Text to wrap
        max_width_chars: Maximum characters per line (default 45)
        font_size: Font size for height calculation (default 8)

    Returns:
        tuple: (wrapped_text, required_height_inches)
    """
    if not text or pd.isna(text):
        return "", 0.0

    # Clean and wrap text
    text = str(text).strip()
    wrapped_lines = textwrap.wrap(text, width=max_width_chars, break_long_words=True)
    wrapped_text = "\n".join(wrapped_lines)

    # Calculate height based on number of lines and font size
    line_count = len(wrapped_lines) if wrapped_lines else 1
    # Approximate height: font_size in points * 1.2 line spacing / 72 points per inch
    height_inches = (font_size * 1.2 * line_count) / 72.0

    return wrapped_text, height_inches


def format_measurement(value, precision: int = 2, unit: str = "m") -> str:
    """
    Format measurement values consistently.

    Args:
        value: Numeric value to format
        precision: Decimal places (default 2)
        unit: Unit string to append (default "m")

    Returns:
        str: Formatted measurement string
    """
    try:
        if pd.isna(value) or value is None:
            return ""

        # Convert to float and format
        numeric_value = float(value)
        if precision == 0:
            return f"{int(numeric_value)}{unit}"
        else:
            return f"{numeric_value:.{precision}f}{unit}"

    except (ValueError, TypeError):
        return str(value) if value is not None else ""


def calculate_text_metrics(text: str, font_size: int = 8) -> dict:
    """
    Calculate text metrics for layout purposes.

    Args:
        text: Text to analyze
        font_size: Font size in points

    Returns:
        dict: Text metrics including width, height, line count
    """
    if not text or pd.isna(text):
        return {
            "width_chars": 0,
            "height_lines": 0,
            "estimated_width_inches": 0.0,
            "estimated_height_inches": 0.0,
        }

    text_str = str(text).strip()
    lines = text_str.split("\n")

    # Calculate metrics
    max_line_length = max(len(line) for line in lines) if lines else 0
    line_count = len(lines)

    # Estimate dimensions (rough approximation)
    # Average character width is approximately 0.6 of font size
    char_width_inches = (font_size * 0.6) / 72.0
    line_height_inches = (font_size * 1.2) / 72.0

    return {
        "width_chars": max_line_length,
        "height_lines": line_count,
        "estimated_width_inches": max_line_length * char_width_inches,
        "estimated_height_inches": line_count * line_height_inches,
    }


def normalize_depth_value(value) -> Optional[float]:
    """
    Normalize depth values to consistent float format.

    Args:
        value: Depth value to normalize

    Returns:
        float or None: Normalized depth value
    """
    try:
        if pd.isna(value) or value is None:
            return None

        # Handle string representations
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

        return float(value)

    except (ValueError, TypeError):
        logger.warning(f"Could not normalize depth value: {value}")
        return None


def calculate_depth_range(depth_top: float, depth_base: float) -> float:
    """
    Calculate depth range with validation.

    Args:
        depth_top: Top depth
        depth_base: Base depth

    Returns:
        float: Depth range (always positive)
    """
    try:
        top = normalize_depth_value(depth_top)
        base = normalize_depth_value(depth_base)

        if top is None or base is None:
            return 0.0

        return abs(base - top)

    except Exception as e:
        logger.warning(f"Error calculating depth range: {e}")
        return 0.0


def validate_coordinate_bounds(x: float, y: float, width: float, height: float) -> bool:
    """
    Validate that coordinates and dimensions are within reasonable bounds.

    Args:
        x: X coordinate
        y: Y coordinate
        width: Width dimension
        height: Height dimension

    Returns:
        bool: True if coordinates are valid
    """
    try:
        # Check for valid numeric values
        if any(not isinstance(val, (int, float)) for val in [x, y, width, height]):
            return False

        # Check for reasonable bounds (assuming A4 page)
        if x < 0 or x > 12:  # inches
            return False
        if y < 0 or y > 17:  # inches
            return False
        if width <= 0 or width > 12:
            return False
        if height <= 0 or height > 17:
            return False

        return True

    except Exception:
        return False


def get_optimal_font_size(text_length: int, available_width: float) -> int:
    """
    Calculate optimal font size based on text length and available width.

    Args:
        text_length: Length of text in characters
        available_width: Available width in inches

    Returns:
        int: Optimal font size in points
    """
    if text_length == 0 or available_width <= 0:
        return 8  # Default font size

    # Estimate character width at different font sizes
    # Average character width is approximately 0.6 of font size in points
    min_font_size = 6
    max_font_size = 12

    for font_size in range(max_font_size, min_font_size - 1, -1):
        char_width_inches = (font_size * 0.6) / 72.0
        required_width = text_length * char_width_inches

        if required_width <= available_width:
            return font_size

    return min_font_size


def create_color_with_alpha(color: str, alpha: float = 1.0) -> tuple:
    """
    Create color tuple with alpha transparency.

    Args:
        color: Color specification (hex, name, etc.)
        alpha: Alpha transparency (0.0-1.0)

    Returns:
        tuple: RGBA color tuple
    """
    try:
        import matplotlib.colors as mcolors

        # Convert color to RGB
        rgb = mcolors.to_rgb(color)

        # Add alpha channel
        return (*rgb, alpha)

    except Exception:
        # Fallback to default gray with alpha
        return (0.5, 0.5, 0.5, alpha)


def estimate_figure_memory_usage(
    width_inches: float, height_inches: float, dpi: int = 300
) -> float:
    """
    Estimate memory usage for a matplotlib figure.

    Args:
        width_inches: Figure width in inches
        height_inches: Figure height in inches
        dpi: Resolution in dots per inch

    Returns:
        float: Estimated memory usage in MB
    """
    # Calculate pixel dimensions
    width_pixels = int(width_inches * dpi)
    height_pixels = int(height_inches * dpi)

    # Estimate memory for RGBA image (4 bytes per pixel)
    memory_bytes = width_pixels * height_pixels * 4

    # Convert to MB
    memory_mb = memory_bytes / (1024 * 1024)

    return memory_mb


# Import pandas here to avoid circular imports
import pandas as pd


def wrap_text_smart(text: str, max_width: int = 50, max_lines: int = 5) -> str:
    """
    Smart text wrapping with line length optimization.

    Args:
        text: Text to wrap
        max_width: Maximum character width per line
        max_lines: Maximum number of lines

    Returns:
        str: Wrapped text
    """
    if not text:
        return ""

    try:
        # Clean up text
        text = text.strip().replace("\n", " ").replace("\r", "")

        # Use textwrap for basic wrapping
        wrapped_lines = textwrap.wrap(text, width=max_width)

        # Limit to max lines
        if len(wrapped_lines) > max_lines:
            wrapped_lines = wrapped_lines[: max_lines - 1]
            wrapped_lines.append("...")

        return "\n".join(wrapped_lines)

    except Exception as e:
        logger.warning(f"Error wrapping text: {e}")
        return text[:max_width] + "..." if len(text) > max_width else text


def calculate_text_dimensions(text: str, fontsize: int = 10) -> Tuple[float, float]:
    """
    Calculate approximate text dimensions for layout planning.

    Args:
        text: Text to measure
        fontsize: Font size in points

    Returns:
        tuple: (width, height) in points
    """
    if not text:
        return (0.0, 0.0)

    try:
        # Approximate character width (varies by font)
        char_width = fontsize * 0.6  # Rough approximation for Arial
        line_height = fontsize * 1.2  # Standard line height

        lines = text.split("\n")
        max_line_length = max(len(line) for line in lines) if lines else 0

        width = max_line_length * char_width
        height = len(lines) * line_height

        return (width, height)

    except Exception as e:
        logger.warning(f"Error calculating text dimensions: {e}")
        return (100.0, 20.0)  # Safe default


def format_depth_value(depth_val: float, precision: int = 2) -> str:
    """
    Format depth value for consistent display.

    Args:
        depth_val: Depth value to format
        precision: Number of decimal places

    Returns:
        str: Formatted depth string
    """
    if depth_val is None:
        return "N/A"

    try:
        return f"{float(depth_val):.{precision}f}"
    except (ValueError, TypeError):
        return str(depth_val)
