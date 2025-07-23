"""
Section Utilities Module

This module provides utility functions for geological section plotting,
including figure management, coordinate transformations, and file operations.

Key Functions:
- convert_figure_to_base64: Convert matplotlib figure to base64 string
- save_high_resolution_outputs: Save figure in multiple high-resolution formats
- safe_close_figure: Safely close matplotlib figures
- matplotlib_figure: Context manager for matplotlib figures
"""

import io
import base64
import logging
import os
from contextlib import contextmanager
from typing import Optional, Generator
import matplotlib.pyplot as plt
import matplotlib.figure

logger = logging.getLogger(__name__)


def convert_figure_to_base64(
    fig: matplotlib.figure.Figure, dpi: int = 300, format: str = "png"
) -> str:
    """
    Convert a matplotlib figure to base64-encoded string.

    Args:
        fig: Matplotlib figure object
        dpi: Resolution for the output image (default 300)
        format: Image format ('png', 'jpg', 'svg', etc.)

    Returns:
        str: Base64-encoded image string

    Raises:
        Exception: If conversion fails
    """
    try:
        # Create a bytes buffer
        buffer = io.BytesIO()

        # Save figure to buffer
        fig.savefig(
            buffer,
            format=format,
            dpi=dpi,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
            transparent=False,
        )

        # Get buffer contents and encode
        buffer.seek(0)
        image_data = buffer.getvalue()
        buffer.close()

        # Encode to base64
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Add data URL prefix for web display
        data_url = f"data:image/{format};base64,{encoded_image}"

        logger.debug(f"Successfully converted figure to base64 ({format}, {dpi} DPI)")
        return data_url

    except Exception as e:
        logger.error(f"Failed to convert figure to base64: {e}")
        raise


def save_high_resolution_outputs(
    fig: matplotlib.figure.Figure,
    output_filename: str,
    dpi: int = 300,
    formats: Optional[list] = None,
) -> None:
    """
    Save matplotlib figure in multiple high-resolution formats.

    Args:
        fig: Matplotlib figure object
        output_filename: Base filename (without extension)
        dpi: Resolution for output files (default 300)
        formats: List of formats to save ['png', 'pdf', 'svg']

    Raises:
        Exception: If saving fails
    """
    if formats is None:
        formats = ["png", "pdf", "svg"]

    try:
        for fmt in formats:
            filename = f"{output_filename}.{fmt}"

            # Configure format-specific settings
            save_kwargs = {
                "dpi": dpi,
                "bbox_inches": "tight",
                "facecolor": "white",
                "edgecolor": "none",
            }

            # Format-specific optimizations
            if fmt.lower() == "png":
                save_kwargs["transparent"] = False
                save_kwargs["optimize"] = True
            elif fmt.lower() == "pdf":
                save_kwargs["backend"] = "pdf"
                save_kwargs["metadata"] = {
                    "Title": "Geological Cross-Section",
                    "Author": "AGS Section Plotter",
                    "Subject": "Professional geological cross-section plot",
                    "Creator": "matplotlib",
                }
            elif fmt.lower() == "svg":
                save_kwargs["transparent"] = True
                save_kwargs["bbox_inches"] = "tight"

            # Save the file
            fig.savefig(filename, format=fmt, **save_kwargs)

            # Verify file was created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                logger.info(f"Saved {fmt.upper()}: {filename} ({file_size:,} bytes)")
            else:
                logger.warning(f"Failed to create {fmt.upper()} file: {filename}")

    except Exception as e:
        logger.error(f"Failed to save high-resolution outputs: {e}")
        raise


def safe_close_figure(fig: matplotlib.figure.Figure) -> None:
    """
    Safely close a matplotlib figure and free memory.

    Args:
        fig: Matplotlib figure object to close
    """
    try:
        if fig is not None:
            plt.close(fig)
            logger.debug("Successfully closed matplotlib figure")
    except Exception as e:
        logger.warning(f"Error closing matplotlib figure: {e}")


@contextmanager
def matplotlib_figure(
    figsize: tuple = (11.69, 8.27), dpi: int = 300, facecolor: str = "white"
) -> Generator[matplotlib.figure.Figure, None, None]:
    """
    Context manager for matplotlib figures with automatic cleanup.

    Args:
        figsize: Figure size (width, height) in inches
        dpi: Resolution for the figure
        facecolor: Background color for the figure

    Yields:
        matplotlib.figure.Figure: Figure object

    Example:
        with matplotlib_figure(figsize=(12, 8)) as fig:
            ax = fig.add_subplot(111)
            ax.plot([1, 2, 3], [1, 4, 2])
            # Figure automatically closed when exiting context
    """
    fig = None
    try:
        # Create figure
        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
        logger.debug(f"Created matplotlib figure: {figsize} @ {dpi} DPI")

        # Yield figure for use
        yield fig

    except Exception as e:
        logger.error(f"Error in matplotlib figure context: {e}")
        raise
    finally:
        # Always clean up
        if fig is not None:
            safe_close_figure(fig)


def validate_figure_parameters(
    figsize: tuple, dpi: int, color_alpha: float, hatch_alpha: float
) -> tuple:
    """
    Validate and normalize figure parameters.

    Args:
        figsize: Figure size (width, height) in inches
        dpi: Resolution for the figure
        color_alpha: Color transparency (0.0-1.0)
        hatch_alpha: Hatch transparency (0.0-1.0)

    Returns:
        tuple: Validated (figsize, dpi, color_alpha, hatch_alpha)

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate figsize
    if not isinstance(figsize, (tuple, list)) or len(figsize) != 2:
        raise ValueError("figsize must be a tuple of (width, height)")

    width, height = figsize
    if not (isinstance(width, (int, float)) and isinstance(height, (int, float))):
        raise ValueError("figsize dimensions must be numeric")

    if width <= 0 or height <= 0:
        raise ValueError("figsize dimensions must be positive")

    # Validate DPI
    if not isinstance(dpi, int) or dpi <= 0:
        raise ValueError("dpi must be a positive integer")

    if dpi < 72:
        logger.warning(f"Low DPI ({dpi}) may result in poor quality output")
    elif dpi > 600:
        logger.warning(f"High DPI ({dpi}) may result in very large files")

    # Validate alpha values
    for alpha, name in [(color_alpha, "color_alpha"), (hatch_alpha, "hatch_alpha")]:
        if not isinstance(alpha, (int, float)):
            raise ValueError(f"{name} must be numeric")
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"{name} must be between 0.0 and 1.0")

    return figsize, dpi, color_alpha, hatch_alpha


def calculate_optimal_figsize(
    n_boreholes: int,
    max_width: float = 16.0,
    min_width: float = 8.0,
    aspect_ratio: float = 1.414,  # A4 landscape ratio
) -> tuple:
    """
    Calculate optimal figure size based on number of boreholes.

    Args:
        n_boreholes: Number of boreholes to plot
        max_width: Maximum figure width in inches
        min_width: Minimum figure width in inches
        aspect_ratio: Width to height ratio

    Returns:
        tuple: Optimal (width, height) in inches
    """
    # Base width calculation
    base_width = min_width + (n_boreholes - 1) * 0.5

    # Clamp to reasonable bounds
    width = max(min_width, min(base_width, max_width))
    height = width / aspect_ratio

    logger.debug(
        f"Calculated optimal figsize: ({width:.2f}, {height:.2f}) "
        f"for {n_boreholes} boreholes"
    )

    return (width, height)


def format_coordinate_label(value: float, precision: int = 1) -> str:
    """
    Format coordinate values for display labels.

    Args:
        value: Coordinate value to format
        precision: Number of decimal places

    Returns:
        str: Formatted coordinate string
    """
    if abs(value) >= 1000:
        return f"{value:,.{precision}f}"
    else:
        return f"{value:.{precision}f}"


def create_color_legend_patch(
    color: str, hatch: str = "", alpha: float = 0.7, linewidth: float = 0.5
):
    """
    Create a colored patch for legend entries.

    Args:
        color: Face color for the patch
        hatch: Hatch pattern (optional)
        alpha: Transparency level
        linewidth: Edge line width

    Returns:
        matplotlib.patches.Patch: Patch object for legend
    """
    from matplotlib.patches import Patch

    return Patch(
        facecolor=color,
        edgecolor="black",
        hatch=hatch,
        alpha=alpha,
        linewidth=linewidth,
    )


def setup_professional_axes(
    ax: plt.Axes,
    x_label: str = "Distance along section (m)",
    y_label: str = "Elevation (m AOD)",
    grid_major_spacing: float = 10.0,
    grid_minor_spacing: float = 2.0,
) -> None:
    """
    Set up professional-style axes formatting.

    Args:
        ax: Matplotlib axes object
        x_label: Label for x-axis
        y_label: Label for y-axis
        grid_major_spacing: Spacing for major grid lines
        grid_minor_spacing: Spacing for minor grid lines
    """
    # Set labels
    ax.set_xlabel(x_label, fontsize=11, weight="bold")
    ax.set_ylabel(y_label, fontsize=11, weight="bold")

    # Configure grid
    ax.grid(
        which="major",
        axis="both",
        linestyle="--",
        color="gray",
        linewidth=0.8,
        alpha=0.7,
    )
    ax.grid(
        which="minor",
        axis="both",
        linestyle=":",
        color="gray",
        linewidth=0.5,
        alpha=0.5,
    )

    # Set tick parameters
    ax.tick_params(which="major", labelsize=10, direction="in", length=6, width=1)
    ax.tick_params(which="minor", direction="in", length=3, width=0.5)

    logger.debug("Applied professional axes formatting")


def estimate_memory_usage(figsize: tuple, dpi: int, n_elements: int) -> float:
    """
    Estimate memory usage for a matplotlib figure.

    Args:
        figsize: Figure size (width, height) in inches
        dpi: Resolution
        n_elements: Number of plot elements (rough estimate)

    Returns:
        float: Estimated memory usage in MB
    """
    width, height = figsize

    # Base raster memory: width * height * dpi^2 * 4 bytes (RGBA)
    pixel_width = int(width * dpi)
    pixel_height = int(height * dpi)
    base_memory_bytes = pixel_width * pixel_height * 4

    # Additional memory for plot elements (rough estimate)
    element_memory_bytes = n_elements * 1000  # ~1KB per element

    # Total memory in MB
    total_memory_mb = (base_memory_bytes + element_memory_bytes) / (1024 * 1024)

    logger.debug(
        f"Estimated memory usage: {total_memory_mb:.1f} MB "
        f"({pixel_width}x{pixel_height} pixels, {n_elements} elements)"
    )

    return total_memory_mb
