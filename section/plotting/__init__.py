"""
Section Plotting Package

Professional geological cross-section plotting with BGS standards compliance.
This package provides modular plotting capabilities for AGS borehole data.

Main Functions:
    plot_professional_borehole_sections: Main plotting function
    plot_section_from_ags_content: Convenience function for single AGS content

Modules:
    coordinates: Coordinate transformation and projection utilities
    geology: Geological plotting, colors, patterns, and legends
    layout: Professional figure layout and formatting
    main: Main plotting interface and coordination
"""

# Import main plotting functions for backward compatibility
from .main import (
    plot_professional_borehole_sections,
    plot_section_from_ags_content,
)

# Re-export for backward compatibility with existing code
plot_professional_section = plot_professional_borehole_sections
plot_section = plot_section_from_ags_content

__all__ = [
    "plot_professional_borehole_sections",
    "plot_section_from_ags_content",
    "plot_professional_section",  # Legacy alias
    "plot_section",  # Legacy alias
]

__version__ = "1.0.0"
__author__ = "Geological Cross-Section Renderer"
