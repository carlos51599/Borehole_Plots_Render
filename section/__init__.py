"""
Section Package

This package contains all section plotting functionality, organized into
focused modules for better maintainability and testing.

The package provides:
- AGS data parsing and validation
- Professional geological plotting
- Figure management utilities
- Color and pattern mapping
"""

from .plotting import plot_professional_borehole_sections, plot_section_from_ags_content
from .parsing import (
    parse_ags_geol_section_from_string,
    validate_ags_format,
    extract_ags_metadata,
)
from .utils import (
    convert_figure_to_base64,
    save_high_resolution_outputs,
    safe_close_figure,
    matplotlib_figure,
)

__all__ = [
    "plot_professional_borehole_sections",
    "plot_section_from_ags_content",
    "parse_ags_geol_section_from_string",
    "validate_ags_format",
    "extract_ags_metadata",
    "convert_figure_to_base64",
    "save_high_resolution_outputs",
    "safe_close_figure",
    "matplotlib_figure",
]
