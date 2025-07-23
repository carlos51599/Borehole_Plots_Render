"""
Geology code utilities for BGS (British Geological Survey) standard geological classifications.

This module handles the loading and mapping of geological codes to their corresponding
colors and hatch patterns for professional geological plotting. It supports the
standard BGS geological classification system used in UK geotechnical practice.

Key Features:
- Loads geology codes from CSV file (Geology Codes BGS.csv)
- Maps geological codes to colors and hatch patterns
- Provides fallback values for unknown codes
- Supports matplotlib-compatible color and pattern definitions
- Follows BGS standards for geological visualization

CSV File Format:
The geology codes CSV file should have columns:
- Code: Geological classification code (e.g., "CLAY", "SAND", "GRAVEL")
- Description: Human-readable description of the geological unit
- Color: Hex color code or matplotlib color name for visualization
- Hatch: Matplotlib hatch pattern for texture representation

Usage:
    >>> color = get_geology_color("CLAY")  # Returns color for clay
    >>> pattern = get_geology_pattern("SAND")  # Returns hatch pattern for sand

Author: [Project Team]
Last Modified: July 2025
"""

import csv
import os

# Global mappings loaded at import time for performance
GEOLOGICAL_COLOR_MAP = {}
GEOLOGICAL_HATCH_PATTERNS = {}


def load_geology_code_mappings(csv_filename=None):
    """
    Load geology code mappings from a CSV file containing BGS standard codes.

    This function reads a CSV file containing geological codes and their associated
    colors and hatch patterns, creating lookup dictionaries for use in plotting
    geological sections and borehole logs.

    Args:
        csv_filename (str, optional): Path to the geology codes CSV file.
                                     If None, uses default "Geology Codes BGS.csv"
                                     in the same directory as this module.

    Returns:
        tuple: (color_map, pattern_map)
            - color_map (dict): Maps geological codes to color values
            - pattern_map (dict): Maps geological codes to matplotlib hatch patterns

    CSV File Structure:
        Code,Description,Color,Hatch
        CLAY,Clay,#8B4513,|||
        SAND,Sand,#F4A460,...
        GRAVEL,Gravel,#A0522D,ooo

    Error Handling:
        - Prints warning if file cannot be loaded
        - Returns empty dictionaries on failure
        - Gracefully handles missing or malformed data

    Example:
        >>> color_map, pattern_map = load_geology_code_mappings()
        >>> print(f"Loaded {len(color_map)} geological color mappings")
        >>> clay_color = color_map.get("CLAY", "#D3D3D3")
    """
    color_map = {}
    pattern_map = {}

    # Use default file if none specified
    if csv_filename is None:
        csv_filename = os.path.join(os.path.dirname(__file__), "Geology Codes BGS.csv")

    print(f"[DEBUG] Loading geology codes from: {csv_filename}")

    try:
        with open(csv_filename, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Normalize code to string and strip whitespace
                code = str(row["Code"]).strip()
                color = row["Color"].strip() if row["Color"] else None
                pattern = row["Hatch"].strip() if row["Hatch"] else None

                # Add to mappings if values exist
                if color:
                    color_map[code] = color
                if pattern:
                    pattern_map[code] = pattern

                print(
                    f"[DEBUG] Loaded: '{code}' -> Color: {color}, Pattern: '{pattern}'"
                )

        print(
            f"[DEBUG] Total loaded: {len(color_map)} colors, {len(pattern_map)} patterns"
        )

    except Exception as e:
        print(f"Warning: Could not load geology code mappings: {e}")

    return color_map, pattern_map


def get_geology_color(code, fallback="#D3D3D3"):
    """
    Get the color associated with a geological code.

    Args:
        code (str): Geological code (e.g., "CLAY", "SAND")
        fallback (str): Default color to return if code not found
                       (default: "#D3D3D3" - light gray)

    Returns:
        str: Color value (hex code or matplotlib color name)

    Example:
        >>> color = get_geology_color("CLAY")  # Returns BGS standard clay color
        >>> unknown_color = get_geology_color("UNKNOWN")  # Returns "#D3D3D3"
    """
    return GEOLOGICAL_COLOR_MAP.get(str(code), fallback)


def get_geology_pattern(code, fallback=""):
    """
    Get the hatch pattern associated with a geological code.

    Args:
        code (str): Geological code (e.g., "CLAY", "SAND")
        fallback (str): Default pattern to return if code not found
                       (default: "" - no pattern)

    Returns:
        str: Matplotlib hatch pattern string

    Example:
        >>> pattern = get_geology_pattern("SAND")  # Returns BGS standard sand pattern
        >>> no_pattern = get_geology_pattern("UNKNOWN")  # Returns ""
    """
    return GEOLOGICAL_HATCH_PATTERNS.get(str(code), fallback)


# Load geological mappings at module import for immediate availability
GEOLOGICAL_COLOR_MAP, GEOLOGICAL_HATCH_PATTERNS = load_geology_code_mappings()
