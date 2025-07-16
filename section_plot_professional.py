"""
Professional-style borehole section plotting module.
Implements Openground-style formatting with hatch patterns, consistent fonts,
professional gridlines, and high-quality output.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
import pandas as pd
import csv
import re
import numpy as np
import pyproj
from config import (
    SECTION_BASE_HEIGHT,
    SECTION_MAX_HEIGHT,
    SECTION_MIN_WIDTH,
    SECTION_WIDTH_PER_BH,
    SECTION_PLOT_LABEL_FONTSIZE,
    SECTION_PLOT_AXIS_FONTSIZE,
)


# Set global matplotlib parameters for professional appearance
def setup_professional_style():
    """Configure matplotlib for professional geological section plots."""
    # Font configuration
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica"]
    mpl.rcParams["axes.labelsize"] = 11
    mpl.rcParams["xtick.labelsize"] = 10
    mpl.rcParams["ytick.labelsize"] = 10
    mpl.rcParams["legend.fontsize"] = 10
    mpl.rcParams["axes.titlesize"] = 12

    # Hatch configuration
    mpl.rcParams["hatch.linewidth"] = 0.8
    mpl.rcParams["hatch.color"] = "black"

    # Grid configuration
    mpl.rcParams["axes.grid"] = True
    mpl.rcParams["grid.linewidth"] = 0.5
    mpl.rcParams["grid.alpha"] = 0.7

    # General appearance
    mpl.rcParams["axes.edgecolor"] = "black"
    mpl.rcParams["axes.linewidth"] = 0.8
    mpl.rcParams["figure.facecolor"] = "white"
    mpl.rcParams["axes.facecolor"] = "white"


# Initialize professional style
setup_professional_style()


# Load geology codes from CSV file
def load_geology_codes():
    """Load geology codes from Geology Codes.csv file."""
    import os
    import pandas as pd

    geology_codes = {}
    csv_path = os.path.join(os.path.dirname(__file__), "Geology Codes.csv")

    try:
        df = pd.read_csv(csv_path, header=None, names=["code", "description"])
        for _, row in df.iterrows():
            geology_codes[str(row["code"])] = row["description"]
    except (FileNotFoundError, Exception) as e:
        print(f"Warning: Could not load geology codes from CSV: {e}")
        # Fallback to basic codes
        geology_codes = {
            "101": "TOPSOIL",
            "102": "MADE GROUND",
            "104": "CONCRETE",
            "999": "Void",
        }

    return geology_codes


# Load geology codes
GEOLOGY_CODES = load_geology_codes()


# Geological hatch pattern mapping based on your specific geology codes
GEOLOGICAL_HATCH_PATTERNS = {
    # Surface materials
    "101": "ooo",  # TOPSOIL - circles
    "102": "***",  # MADE GROUND - stars
    "104": "####",  # CONCRETE - hash marks
    # Clay types
    "202": "...",  # Silty CLAY - dots
    "203": ".//.",  # Sandy CLAY - dots with diagonal lines
    "204": "...\\\\\\",  # Gravelly CLAY - dots with backslash
    "205": "...ooo",  # Cobbly CLAY - dots with circles
    "207": ".//.",  # Silty sandy CLAY - dots with diagonal
    "220": ".//\\\\\\",  # Sandy gravelly CLAY - mixed pattern
    "227": "...~~~",  # Sandy organic CLAY - dots with waves
    # Silt types
    "301": "---",  # SILT - horizontal lines
    "308": "---//\\\\\\",  # Sandy gravelly SILT - mixed pattern
    # Sand types
    "403": "///",  # Silty SAND - diagonal lines
    "410": "///...\\\\\\",  # Clayey gravelly SAND - complex pattern
    # Gravel types
    "501": "\\\\\\",  # GRAVEL - backslash lines
    "509": "\\\\\\...///",  # Clayey sandy GRAVEL - complex pattern
    # Cobbles
    "708": "ooo\\\\\\...",  # Clayey sandy COBBLES - complex pattern
    # Rock types
    "801": "===",  # MUDSTONE - thick horizontal lines
    "802": "---",  # SILTSTONE - horizontal lines
    "803": "|||",  # SANDSTONE - vertical lines
    # Special
    "999": "",  # Void - no pattern
    # Fallback patterns for common terms (for backward compatibility)
    "CLAY": "...",
    "CLAYEY": "...",
    "SILTY_CLAY": "...",
    "SANDY_CLAY": ".//.",
    "SILT": "---",
    "SILTY": "---",
    "CLAYEY_SILT": ".---.",
    "SAND": "///",
    "SANDY": "///",
    "FINE_SAND": "//",
    "MEDIUM_SAND": "///",
    "COARSE_SAND": "/////",
    "SILTY_SAND": "///---",
    "GRAVEL": "\\\\\\",
    "GRAVELLY": "\\\\\\",
    "SANDY_GRAVEL": "///\\\\\\",
    "CLAYEY_GRAVEL": "...\\\\\\",
    "LIMESTONE": "xxx",
    "CHALK": "xx",
    "SANDSTONE": "|||",
    "MUDSTONE": "===",
    "SHALE": "====",
    "GRANITE": "++++",
    "BEDROCK": "+++",
    "TOPSOIL": "ooo",
    "MADE_GROUND": "***",
    "FILL": "***",
    "CONCRETE": "####",
    "ASPHALT": "^^^^",
    "UNKNOWN": "",
    "DEFAULT": "",
}

# Color mapping for geological units based on your specific codes
GEOLOGICAL_COLOR_MAP = {
    # Surface materials
    "101": "#654321",  # TOPSOIL - dark brown
    "102": "#8B0000",  # MADE GROUND - dark red
    "104": "#D3D3D3",  # CONCRETE - light gray
    # Clay types - browns and earth tones
    "202": "#8B4513",  # Silty CLAY - saddle brown
    "203": "#CD853F",  # Sandy CLAY - peru
    "204": "#A0522D",  # Gravelly CLAY - sienna
    "205": "#8B4513",  # Cobbly CLAY - saddle brown
    "207": "#DEB887",  # Silty sandy CLAY - burlywood
    "220": "#D2691E",  # Sandy gravelly CLAY - chocolate
    "227": "#8B4513",  # Sandy organic CLAY - saddle brown
    # Silt types - tan colors
    "301": "#D2B48C",  # SILT - tan
    "308": "#DEB887",  # Sandy gravelly SILT - burlywood
    # Sand types - yellow/sandy colors
    "403": "#F4A460",  # Silty SAND - sandy brown
    "410": "#DAA520",  # Clayey gravelly SAND - goldenrod
    # Gravel types - gray colors
    "501": "#696969",  # GRAVEL - dim gray
    "509": "#778899",  # Clayey sandy GRAVEL - light slate gray
    # Cobbles - darker gray
    "708": "#708090",  # Clayey sandy COBBLES - slate gray
    # Rock types - stone colors
    "801": "#2F4F4F",  # MUDSTONE - dark slate gray
    "802": "#8FBC8F",  # SILTSTONE - dark sea green
    "803": "#F0E68C",  # SANDSTONE - khaki
    # Special
    "999": "#FFFFFF",  # Void - white
    # Fallback colors for common terms (for backward compatibility)
    "CLAY": "#8B4513",
    "CLAYEY": "#8B4513",
    "SILTY_CLAY": "#A0522D",
    "SANDY_CLAY": "#CD853F",
    "SILT": "#D2B48C",
    "SILTY": "#D2B48C",
    "CLAYEY_SILT": "#DEB887",
    "SAND": "#F4A460",
    "SANDY": "#F4A460",
    "FINE_SAND": "#F5DEB3",
    "MEDIUM_SAND": "#F4A460",
    "COARSE_SAND": "#DAA520",
    "SILTY_SAND": "#E6D3A3",
    "GRAVEL": "#696969",
    "GRAVELLY": "#696969",
    "SANDY_GRAVEL": "#778899",
    "CLAYEY_GRAVEL": "#708090",
    "LIMESTONE": "#F5F5DC",
    "CHALK": "#FFFAF0",
    "SANDSTONE": "#F0E68C",
    "MUDSTONE": "#8FBC8F",
    "SHALE": "#2F4F4F",
    "GRANITE": "#C0C0C0",
    "BEDROCK": "#808080",
    "TOPSOIL": "#654321",
    "MADE_GROUND": "#8B0000",
    "FILL": "#8B0000",
    "CONCRETE": "#D3D3D3",
    "ASPHALT": "#2F2F2F",
}


def get_geological_pattern(geol_leg, geol_desc=""):
    """
    Determine the appropriate hatch pattern for a geological unit.

    Args:
        geol_leg (str): Geological legend code
        geol_desc (str): Geological description

    Returns:
        str: Hatch pattern string
    """
    # First try exact match with GEOL_LEG (your specific codes)
    if str(geol_leg) in GEOLOGICAL_HATCH_PATTERNS:
        return GEOLOGICAL_HATCH_PATTERNS[str(geol_leg)]

    # Try matching with the description from your geology codes
    if str(geol_leg) in GEOLOGY_CODES:
        desc = GEOLOGY_CODES[str(geol_leg)].upper()

        # Check for keywords in the official description
        if "CLAY" in desc:
            if "SANDY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("203", ".//.")
            elif "SILTY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("202", "...")
            elif "GRAVELLY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("204", "...\\\\\\")
            else:
                return GEOLOGICAL_HATCH_PATTERNS.get("CLAY", "...")
        elif "SILT" in desc:
            if "SANDY" in desc and "GRAVELLY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("308", "---//\\\\\\")
            else:
                return GEOLOGICAL_HATCH_PATTERNS.get("301", "---")
        elif "SAND" in desc:
            if "SILTY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("403", "///")
            elif "CLAYEY" in desc and "GRAVELLY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("410", "///...\\\\\\")
            else:
                return GEOLOGICAL_HATCH_PATTERNS.get("SAND", "///")
        elif "GRAVEL" in desc:
            if "CLAYEY" in desc and "SANDY" in desc:
                return GEOLOGICAL_HATCH_PATTERNS.get("509", "\\\\\\...///")
            else:
                return GEOLOGICAL_HATCH_PATTERNS.get("501", "\\\\\\")
        elif "COBBLES" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("708", "ooo\\\\\\...")
        elif "TOPSOIL" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("101", "ooo")
        elif "MADE GROUND" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("102", "***")
        elif "CONCRETE" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("104", "####")
        elif "MUDSTONE" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("801", "===")
        elif "SILTSTONE" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("802", "---")
        elif "SANDSTONE" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("803", "|||")
        elif "VOID" in desc:
            return GEOLOGICAL_HATCH_PATTERNS.get("999", "")

    # Fallback: try pattern matching in the provided description
    desc_upper = str(geol_desc).upper()

    # Check for keywords in description
    for pattern_key in GEOLOGICAL_HATCH_PATTERNS:
        if str(pattern_key).upper() in desc_upper:
            return GEOLOGICAL_HATCH_PATTERNS[pattern_key]

    # Final fallbacks for common variations
    if any(word in desc_upper for word in ["CLAY", "CLAYEY"]):
        return GEOLOGICAL_HATCH_PATTERNS.get("CLAY", "...")
    elif any(word in desc_upper for word in ["SAND", "SANDY"]):
        return GEOLOGICAL_HATCH_PATTERNS.get("SAND", "///")
    elif any(word in desc_upper for word in ["SILT", "SILTY"]):
        return GEOLOGICAL_HATCH_PATTERNS.get("SILT", "---")
    elif any(word in desc_upper for word in ["GRAVEL", "GRAVELLY"]):
        return GEOLOGICAL_HATCH_PATTERNS.get("GRAVEL", "\\\\\\")
    elif any(word in desc_upper for word in ["TOPSOIL", "SOIL"]):
        return GEOLOGICAL_HATCH_PATTERNS.get("TOPSOIL", "ooo")
    elif any(word in desc_upper for word in ["MADE", "FILL"]):
        return GEOLOGICAL_HATCH_PATTERNS.get("MADE_GROUND", "***")

    return GEOLOGICAL_HATCH_PATTERNS.get("DEFAULT", "")


def get_geological_color(geol_leg, geol_desc=""):
    """
    Determine the appropriate color for a geological unit.

    Args:
        geol_leg (str): Geological legend code
        geol_desc (str): Geological description

    Returns:
        str: Color hex code
    """
    # First try exact match with GEOL_LEG (your specific codes)
    if str(geol_leg) in GEOLOGICAL_COLOR_MAP:
        return GEOLOGICAL_COLOR_MAP[str(geol_leg)]

    # Try matching with the description from your geology codes
    if str(geol_leg) in GEOLOGY_CODES:
        desc = GEOLOGY_CODES[str(geol_leg)].upper()

        # Check for keywords in the official description
        if "CLAY" in desc:
            if "SANDY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("203", "#CD853F")
            elif "SILTY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("202", "#8B4513")
            elif "GRAVELLY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("204", "#A0522D")
            else:
                return GEOLOGICAL_COLOR_MAP.get("CLAY", "#8B4513")
        elif "SILT" in desc:
            if "SANDY" in desc and "GRAVELLY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("308", "#DEB887")
            else:
                return GEOLOGICAL_COLOR_MAP.get("301", "#D2B48C")
        elif "SAND" in desc:
            if "SILTY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("403", "#F4A460")
            elif "CLAYEY" in desc and "GRAVELLY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("410", "#DAA520")
            else:
                return GEOLOGICAL_COLOR_MAP.get("SAND", "#F4A460")
        elif "GRAVEL" in desc:
            if "CLAYEY" in desc and "SANDY" in desc:
                return GEOLOGICAL_COLOR_MAP.get("509", "#778899")
            else:
                return GEOLOGICAL_COLOR_MAP.get("501", "#696969")
        elif "COBBLES" in desc:
            return GEOLOGICAL_COLOR_MAP.get("708", "#708090")
        elif "TOPSOIL" in desc:
            return GEOLOGICAL_COLOR_MAP.get("101", "#654321")
        elif "MADE GROUND" in desc:
            return GEOLOGICAL_COLOR_MAP.get("102", "#8B0000")
        elif "CONCRETE" in desc:
            return GEOLOGICAL_COLOR_MAP.get("104", "#D3D3D3")
        elif "MUDSTONE" in desc:
            return GEOLOGICAL_COLOR_MAP.get("801", "#2F4F4F")
        elif "SILTSTONE" in desc:
            return GEOLOGICAL_COLOR_MAP.get("802", "#8FBC8F")
        elif "SANDSTONE" in desc:
            return GEOLOGICAL_COLOR_MAP.get("803", "#F0E68C")
        elif "VOID" in desc:
            return GEOLOGICAL_COLOR_MAP.get("999", "#FFFFFF")

    # Fallback: try pattern matching in the provided description
    desc_upper = str(geol_desc).upper()

    # Check for keywords in description
    for color_key in GEOLOGICAL_COLOR_MAP:
        if str(color_key).upper() in desc_upper:
            return GEOLOGICAL_COLOR_MAP[color_key]

    # Final fallbacks for common variations
    if any(word in desc_upper for word in ["CLAY", "CLAYEY"]):
        return GEOLOGICAL_COLOR_MAP.get("CLAY", "#8B4513")
    elif any(word in desc_upper for word in ["SAND", "SANDY"]):
        return GEOLOGICAL_COLOR_MAP.get("SAND", "#F4A460")
    elif any(word in desc_upper for word in ["SILT", "SILTY"]):
        return GEOLOGICAL_COLOR_MAP.get("SILT", "#D2B48C")
    elif any(word in desc_upper for word in ["GRAVEL", "GRAVELLY"]):
        return GEOLOGICAL_COLOR_MAP.get("GRAVEL", "#696969")
    elif any(word in desc_upper for word in ["TOPSOIL", "SOIL"]):
        return GEOLOGICAL_COLOR_MAP.get("TOPSOIL", "#654321")
    elif any(word in desc_upper for word in ["MADE", "FILL"]):
        return GEOLOGICAL_COLOR_MAP.get("MADE_GROUND", "#8B0000")

    # Default to a neutral color if no match found
    return "#D3D3D3"  # Light gray
    return "#D3D3D3"  # Light gray


def parse_ags_geol_section_from_string(content):
    """Parse AGS content string and extract GEOL, LOCA, and ABBR group data as DataFrames."""
    lines = content.splitlines()

    def parse_lines(lines):
        return list(csv.reader(lines, delimiter=",", quotechar='"'))

    parsed = parse_lines(lines)

    # Parse GEOL
    geol_headings = []
    geol_data = []
    in_geol = False
    for row in parsed:
        if row and row[0] == "GROUP" and len(row) > 1 and row[1] == "GEOL":
            in_geol = True
            continue
        if in_geol and row and row[0] == "HEADING":
            geol_headings = row[1:]
            continue
        if in_geol and row and row[0] == "DATA":
            geol_data.append(row[1 : len(geol_headings) + 1])
            continue
        if in_geol and row and row[0] == "GROUP" and (len(row) < 2 or row[1] != "GEOL"):
            break

    geol_df = pd.DataFrame(geol_data, columns=geol_headings)
    if "LOCA_ID" in geol_df.columns:
        geol_df["LOCA_ID"] = geol_df["LOCA_ID"].str.strip()
    for col in ["GEOL_TOP", "GEOL_BASE"]:
        if col in geol_df.columns:
            geol_df[col] = pd.to_numeric(geol_df[col], errors="coerce")

    # Parse LOCA
    loca_headings = []
    loca_data = []
    in_loca = False
    for row in parsed:
        if row and row[0] == "GROUP" and len(row) > 1 and row[1] == "LOCA":
            in_loca = True
            continue
        if in_loca and row and row[0] == "HEADING":
            loca_headings = row[1:]
            continue
        if in_loca and row and row[0] == "DATA":
            loca_data.append(row[1 : len(loca_headings) + 1])
            continue
        if in_loca and row and row[0] == "GROUP" and (len(row) < 2 or row[1] != "LOCA"):
            break

    loca_df = pd.DataFrame(loca_data, columns=loca_headings)
    if "LOCA_ID" in loca_df.columns:
        loca_df["LOCA_ID"] = loca_df["LOCA_ID"].str.strip()
    for col in ["LOCA_NATE", "LOCA_NATN", "LOCA_GL"]:
        if col in loca_df.columns:
            loca_df[col] = pd.to_numeric(loca_df[col], errors="coerce")

    # Parse ABBR
    abbr_headings = []
    abbr_data = []
    in_abbr = False
    for row in parsed:
        if row and row[0] == "GROUP" and len(row) > 1 and row[1] == "ABBR":
            in_abbr = True
            continue
        if in_abbr and row and row[0] == "HEADING":
            abbr_headings = row[1:]
            continue
        if in_abbr and row and row[0] == "DATA":
            abbr_data.append(row[1 : len(abbr_headings) + 1])
            continue
        if in_abbr and row and row[0] == "GROUP" and (len(row) < 2 or row[1] != "ABBR"):
            break

    abbr_df = pd.DataFrame(abbr_data, columns=abbr_headings) if abbr_headings else None
    return geol_df, loca_df, abbr_df


def plot_professional_borehole_sections(
    geol_df,
    loca_df,
    abbr_df=None,
    ags_title=None,
    section_line=None,
    show_labels=True,
    vertical_exaggeration=3.0,
    save_high_res=False,
    output_filename=None,
):
    """
    Plot professional-style borehole sections with Openground-style formatting.

    Args:
        geol_df: Geological data DataFrame
        loca_df: Location data DataFrame
        abbr_df: Abbreviations DataFrame (optional)
        ags_title: Title for the plot
        section_line: Section line coordinates for projection
        show_labels: Whether to show geological labels
        vertical_exaggeration: Vertical exaggeration factor (default 3.0)
        save_high_res: Whether to save high-resolution output
        output_filename: Output filename for saving (without extension)

    Returns:
        matplotlib.figure.Figure: The generated figure
    """
    print(f"[DEBUG] Professional section plot called with section_line: {section_line}")
    print(f"[DEBUG] LOCA DataFrame shape: {loca_df.shape}")
    print(f"[DEBUG] LOCA DataFrame columns: {loca_df.columns.tolist()}")

    # Check what coordinate columns are available
    coord_cols = [
        col
        for col in loca_df.columns
        if any(x in col.upper() for x in ["NATE", "NATN", "LAT", "LON"])
    ]
    print(f"[DEBUG] Available coordinate columns: {coord_cols}")

    # Handle coordinate system for polyline mode
    if section_line is not None:
        print("[DEBUG] Using polyline mode - need consistent coordinate system")
        from shapely.geometry import Point as ShapelyPoint

        # BNG to WGS84 transformer
        bng_to_wgs84 = pyproj.Transformer.from_crs(
            "EPSG:27700", "EPSG:4326", always_xy=True
        )

        # WGS84 to UTM Zone 30N transformer
        utm_crs = "EPSG:32630"
        wgs84_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)

        print(f"[DEBUG] Converting BNG -> WGS84 -> UTM ({utm_crs})")


        # Hybrid vectorized + fallback loop for UTM conversion
        # 1. Identify rows with valid numeric LOCA_NATE and LOCA_NATN
        valid_mask = (
            loca_df["LOCA_NATE"].apply(lambda x: pd.notnull(x) and str(x).replace('.', '', 1).replace('-', '', 1).isdigit()) &
            loca_df["LOCA_NATN"].apply(lambda x: pd.notnull(x) and str(x).replace('.', '', 1).replace('-', '', 1).isdigit())
        )
        clean_df = loca_df[valid_mask].copy()
        problem_df = loca_df[~valid_mask].copy()

        utm_coordinates = {}
        # Vectorized transform for clean batch
        if not clean_df.empty:
            bng_x = clean_df["LOCA_NATE"].astype(float).values
            bng_y = clean_df["LOCA_NATN"].astype(float).values
            # BNG to WGS84
            wgs84_lon, wgs84_lat = bng_to_wgs84.transform(bng_x, bng_y)
            # WGS84 to UTM
            utm_x, utm_y = wgs84_to_utm.transform(wgs84_lon, wgs84_lat)
            for i, loca_id in enumerate(clean_df["LOCA_ID"].values):
                utm_coordinates[loca_id] = (utm_x[i], utm_y[i])
                if i < 3:
                    print(f"[DEBUG] {loca_id}: BNG({bng_x[i]}, {bng_y[i]}) -> UTM({utm_x[i]:.1f}, {utm_y[i]:.1f})")

        # Fallback loop for problematic rows
        for _, row in problem_df.iterrows():
            try:
                bng_x = float(row["LOCA_NATE"])
                bng_y = float(row["LOCA_NATN"])
                wgs84_lon, wgs84_lat = bng_to_wgs84.transform(bng_x, bng_y)
                utm_x, utm_y = wgs84_to_utm.transform(wgs84_lon, wgs84_lat)
                utm_coordinates[row["LOCA_ID"]] = (utm_x, utm_y)
                if len(utm_coordinates) <= 3:
                    print(f"[DEBUG] {row['LOCA_ID']}: BNG({bng_x}, {bng_y}) -> UTM({utm_x:.1f}, {utm_y:.1f})")
            except (ValueError, TypeError) as e:
                print(f"[DEBUG] Skipping {row['LOCA_ID']} due to invalid coordinates: {e}")
                continue

        # Merge coordinates and LOCA_GL into geol_df
        loca_cols = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
        if "LOCA_GL" in loca_df.columns:
            loca_cols.append("LOCA_GL")

        merged = geol_df.merge(
            loca_df[loca_cols],
            left_on="LOCA_ID",
            right_on="LOCA_ID",
            how="left",
        )

        # Add UTM coordinates based on the transformed coordinates
        merged["UTM_X"] = merged["LOCA_ID"].map(
            lambda x: utm_coordinates.get(x, (None, None))[0]
        )
        merged["UTM_Y"] = merged["LOCA_ID"].map(
            lambda x: utm_coordinates.get(x, (None, None))[1]
        )

        # Remove rows with missing UTM coordinates
        merged = merged.dropna(subset=["UTM_X", "UTM_Y"])

        if merged.empty:
            print("[DEBUG] No boreholes with valid UTM coordinates")
            return None

        # Get unique boreholes and their UTM coordinates
        borehole_utm = merged.groupby("LOCA_ID")[["UTM_X", "UTM_Y"]].first()
        boreholes = borehole_utm.index.tolist()
        x_coords = borehole_utm["UTM_X"].values
        y_coords = borehole_utm["UTM_Y"].values

        print(f"[DEBUG] Using UTM coordinates for {len(boreholes)} boreholes")
        print(f"[DEBUG] X coords (UTM): {x_coords[:3]}...")
        print(f"[DEBUG] Y coords (UTM): {y_coords[:3]}...")

    else:
        print("[DEBUG] Using standard mode with BNG coordinates")
        loca_cols = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
        if "LOCA_GL" in loca_df.columns:
            loca_cols.append("LOCA_GL")

        merged = geol_df.merge(
            loca_df[loca_cols],
            left_on="LOCA_ID",
            right_on="LOCA_ID",
            how="left",
        )

        # Remove rows with missing coordinates
        merged = merged.dropna(subset=["LOCA_NATE", "LOCA_NATN"])

        if merged.empty:
            print("No boreholes with valid coordinates to plot.")
            return None

        # Get unique boreholes and their coordinates
        borehole_x = merged.groupby("LOCA_ID")["LOCA_NATE"].first().sort_values()
        borehole_y = (
            merged.groupby("LOCA_ID")["LOCA_NATN"].first().reindex(borehole_x.index)
        )
        boreholes = borehole_x.index.tolist()
        x_coords = borehole_x.values
        y_coords = borehole_y.values

    # Ensure LOCA_GL is available in merged DataFrame
    if "LOCA_GL" not in merged.columns:
        if "LOCA_GL" in loca_df.columns:
            merged = merged.merge(
                loca_df[["LOCA_ID", "LOCA_GL"]], on="LOCA_ID", how="left"
            )
        else:
            merged["LOCA_GL"] = 0.0

    # Ensure LOCA_GL is numeric
    merged["LOCA_GL"] = pd.to_numeric(merged["LOCA_GL"], errors="coerce").fillna(0.0)

    # Calculate elevation for each interval
    merged["ELEV_TOP"] = merged["LOCA_GL"] - merged["GEOL_TOP"].abs()
    merged["ELEV_BASE"] = merged["LOCA_GL"] - merged["GEOL_BASE"].abs()

    # Project boreholes onto section line if provided
    if section_line is not None:
        try:
            from shapely.geometry import LineString
        except ImportError:
            print("You need to install the 'shapely' library. Run: pip install shapely")
            return None

        if isinstance(section_line, (list, tuple)) and len(section_line) > 2:
            # Polyline: project each borehole onto the closest point along the polyline
            print(f"[DEBUG] Processing polyline with {len(section_line)} points")
            line = LineString(section_line)
            rel_x = []
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                point = ShapelyPoint(x, y)
                distance = line.project(point)
                rel_x.append(distance)
                print(
                    f"[DEBUG] Borehole {boreholes[i]}: ({x}, {y}) -> distance {distance}"
                )
            bh_x_map = dict(zip(boreholes, rel_x))
        else:
            # Two-point line: project each borehole onto the straight line (PCA axis)
            (x0, y0), (x1, y1) = section_line
            dx = x1 - x0
            dy = y1 - y0
            line_length = np.hypot(dx, dy)
            if line_length == 0:
                rel_x = x_coords - x_coords[0]
            else:
                # Project each borehole onto the section line using vector projection
                rel_x = ((x_coords - x0) * dx + (y_coords - y0) * dy) / line_length
            bh_x_map = dict(zip(boreholes, rel_x))
    else:
        # Default: use easting as section orientation
        rel_x = x_coords - x_coords[0]
        bh_x_map = dict(zip(boreholes, rel_x))

    # Get ground level for each borehole
    bh_gl_map = merged.groupby("LOCA_ID")["LOCA_GL"].first().to_dict()

    # Create professional color and hatch mappings
    unique_leg = merged["GEOL_LEG"].unique()
    color_map = {}
    hatch_map = {}

    for leg in unique_leg:
        # Get a sample description for this leg
        sample_desc = (
            merged.loc[merged["GEOL_LEG"] == leg, "GEOL_DESC"].iloc[0]
            if "GEOL_DESC" in merged.columns
            else ""
        )
        color_map[leg] = get_geological_color(leg, sample_desc)
        hatch_map[leg] = get_geological_pattern(leg, sample_desc)

    # Build labels for each GEOL_LEG using ABBR group if available
    leg_label_map = {}
    for leg in unique_leg:
        label = leg  # fallback
        if (
            abbr_df is not None
            and "ABBR_CODE" in abbr_df.columns
            and "ABBR_DESC" in abbr_df.columns
        ):
            abbr_match = abbr_df[abbr_df["ABBR_CODE"] == str(leg)]
            if not abbr_match.empty:
                label = abbr_match["ABBR_DESC"].iloc[0]
        else:
            # fallback to previous logic: first fully capitalized word(s) in GEOL_DESC
            if "GEOL_DESC" in merged.columns:
                descs = merged.loc[merged["GEOL_LEG"] == leg, "GEOL_DESC"]
                for desc in descs:
                    match = re.search(r"([A-Z]{2,}(?: [A-Z]{2,})*)", str(desc))
                    if match:
                        label = match.group(1)
                        break
        leg_label_map[leg] = f"{label} ({leg})"

    # Professional figure sizing with vertical exaggeration
    width = 1.2  # width of each borehole (slightly wider for professional look)
    n_bhs = len(boreholes)
    width_inches = max(SECTION_MIN_WIDTH, n_bhs * SECTION_WIDTH_PER_BH * 1.2)
    height_inches = min(
        SECTION_BASE_HEIGHT * vertical_exaggeration, SECTION_MAX_HEIGHT * 1.5
    )

    # Create figure with professional styling
    fig, ax = plt.subplots(figsize=(width_inches, height_inches))
    fig.patch.set_facecolor("white")

    # Set up professional gridlines
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

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

    # Plot geological intervals with professional styling
    legend_labels_added = set()

    for i, bh in enumerate(boreholes):
        bh_x = bh_x_map[bh]
        bh_df = (
            merged[merged["LOCA_ID"] == bh]
            .sort_values("GEOL_TOP")
            .reset_index(drop=True)
        )

        # Group consecutive intervals with the same GEOL_LEG for labeling
        prev_leg = None
        group_start_idx = None

        for idx, row in bh_df.iterrows():
            leg = row["GEOL_LEG"]
            color = color_map.get(leg, "#D3D3D3")
            hatch = hatch_map.get(leg, "")

            # Only suppress repeated legend entries, not text labels
            legend_label = (
                leg_label_map[leg] if leg not in legend_labels_added else None
            )

            # Professional geological interval plotting with hatch patterns
            ax.fill_betweenx(
                [row["ELEV_TOP"], row["ELEV_BASE"]],
                bh_x - width / 2,
                bh_x + width / 2,
                facecolor=color,
                hatch=hatch,
                edgecolor="black",
                linewidth=0.5,
                alpha=0.8,
                label=legend_label,
            )

            if legend_label is not None:
                legend_labels_added.add(leg)

            # Grouping logic for labeling
            if prev_leg != leg:
                # Start new group (no label)
                prev_leg = leg
                group_start_idx = idx

        # Label the last group (no label)

    # Draw professional ground surface line
    rel_x = np.array(list(bh_x_map.values()))
    sorted_indices = np.argsort(rel_x)
    sorted_boreholes = [boreholes[i] for i in sorted_indices]
    sorted_x = [bh_x_map[bh] for bh in sorted_boreholes]
    ground_levels = [bh_gl_map[bh] for bh in sorted_boreholes]

    ax.plot(
        sorted_x,
        ground_levels,
        color="black",
        linewidth=2.5,
        linestyle="-",
        zorder=100,
        label="Ground Level",
        marker="o",
        markersize=4,
        markerfacecolor="white",
        markeredgecolor="black",
        markeredgewidth=1,
    )

    # Professional borehole labels
    label_y = 1.05
    rel_x = np.array(list(bh_x_map.values()))

    for i, bh in enumerate(boreholes):
        bh_x = bh_x_map[bh]
        x_axes = (bh_x - (rel_x.min() - 2)) / ((rel_x.max() + 2) - (rel_x.min() - 2))
        ax.annotate(
            f"BH-{bh}",
            xy=(x_axes, label_y),
            xycoords=("axes fraction", "axes fraction"),
            ha="center",
            va="bottom",
            fontsize=SECTION_PLOT_AXIS_FONTSIZE,
            rotation=90,
            weight="bold",
            annotation_clip=False,
        )

    # Professional title with adequate spacing
    if ags_title is None:
        ags_title = "Geological Cross-Section"
    ax.set_title(f"{ags_title}", pad=80, fontsize=14, weight="bold")

    # Professional axis formatting
    total_length = rel_x.max() - rel_x.min()
    if total_length > 100:
        step = 20
    elif total_length > 50:
        step = 10
    elif total_length > 15:
        step = 5
    else:
        step = 2

    x_start = int(np.floor(rel_x.min() / step) * step)
    x_end = int(np.ceil(rel_x.max() / step) * step)
    x_tick_vals = np.arange(x_start, x_end + step, step)
    ax.set_xticks(x_tick_vals)
    ax.set_xticklabels([f"{int(x)}" for x in x_tick_vals])

    ax.set_xlabel("Distance along section (m)", fontsize=11, weight="bold")
    ax.set_ylabel("Elevation (m AOD)", fontsize=11, weight="bold")

    # Set professional y-limits
    elev_max = merged[["ELEV_TOP", "ELEV_BASE"]].max().max()
    elev_min = merged[["ELEV_TOP", "ELEV_BASE"]].min().min()
    elev_range = elev_max - elev_min
    ax.set_ylim(elev_min - elev_range * 0.1, elev_max + elev_range * 0.15)
    ax.set_xlim(rel_x.min() - total_length * 0.05, rel_x.max() + total_length * 0.05)

    # Professional legend with color and hatch patterns
    legend_patches = []
    for leg in unique_leg:
        label = leg_label_map[leg]
        patch = Patch(
            facecolor=color_map[leg],
            edgecolor="black",
            hatch=hatch_map[leg],
            label=label,
            linewidth=0.5,
        )
        legend_patches.append(patch)

    legend = ax.legend(
        handles=legend_patches,
        title="Geological Legend",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=True,
        fancybox=True,
        shadow=True,
        title_fontsize=11,
        fontsize=10,
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.9)

    # Apply tight layout
    plt.tight_layout()

    # Save high-resolution output if requested
    if save_high_res and output_filename:
        # Save as PDF (vector format)
        pdf_filename = f"{output_filename}.pdf"
        plt.savefig(pdf_filename, format="pdf", dpi=300, bbox_inches="tight")
        print(f"[INFO] Saved high-resolution PDF: {pdf_filename}")

        # Save as high-DPI PNG
        png_filename = f"{output_filename}.png"
        plt.savefig(png_filename, format="png", dpi=300, bbox_inches="tight")
        print(f"[INFO] Saved high-resolution PNG: {png_filename}")

    return fig


def plot_section_from_ags_content(
    ags_content,
    filter_loca_ids=None,
    section_line=None,
    show_labels=True,
    vertical_exaggeration=3.0,
    save_high_res=False,
    output_filename=None,
):
    """
    Create a professional geological section plot from AGS content.

    Args:
        ags_content: AGS file content as string
        filter_loca_ids: List of location IDs to include (optional)
        section_line: Section line coordinates for projection (optional)
        show_labels: Whether to show geological labels (default True)
        vertical_exaggeration: Vertical exaggeration factor (default 3.0)
        save_high_res: Whether to save high-resolution output (default False)
        output_filename: Output filename for saving (optional)

    Returns:
        matplotlib.figure.Figure: The generated figure
    """
    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)

    if filter_loca_ids is not None:
        geol_df = geol_df[geol_df["LOCA_ID"].isin(filter_loca_ids)]
        loca_df = loca_df[loca_df["LOCA_ID"].isin(filter_loca_ids)]

    if geol_df.empty or loca_df.empty:
        return None

    return plot_professional_borehole_sections(
        geol_df,
        loca_df,
        abbr_df,
        ags_title=None,
        section_line=section_line,
        show_labels=show_labels,
        vertical_exaggeration=vertical_exaggeration,
        save_high_res=save_high_res,
        output_filename=output_filename,
    )
