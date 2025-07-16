import csv
import os

# Utility to load geology code mappings from a CSV file with header: Code,Description,Color,Hatch


def load_geology_code_mappings(csv_filename=None):
    """
    Load geology code mappings from a CSV file.
    Returns two dicts: code -> color, code -> pattern
    """
    color_map = {}
    pattern_map = {}
    if csv_filename is None:
        csv_filename = os.path.join(os.path.dirname(__file__), "Geology Codes BGS.csv")

    print(f"[DEBUG] Loading geology codes from: {csv_filename}")
    try:
        with open(csv_filename, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                code = str(row["Code"]).strip()
                color = row["Color"].strip() if row["Color"] else None
                pattern = row["Hatch"].strip() if row["Hatch"] else None
                if color:
                    color_map[code] = color
                if pattern:
                    pattern_map[code] = pattern
                print(f"[DEBUG] Loaded: {code} -> Color: {color}, Pattern: '{pattern}'")
        print(
            f"[DEBUG] Total loaded: {len(color_map)} colors, {len(pattern_map)} patterns"
        )
    except Exception as e:
        print(f"Warning: Could not load geology code mappings: {e}")
    return color_map, pattern_map


# Optionally, load at import for convenience
GEOLOGICAL_COLOR_MAP, GEOLOGICAL_HATCH_PATTERNS = load_geology_code_mappings()


def get_geology_color(code, fallback="#D3D3D3"):
    return GEOLOGICAL_COLOR_MAP.get(str(code), fallback)


def get_geology_pattern(code, fallback=""):
    return GEOLOGICAL_HATCH_PATTERNS.get(str(code), fallback)
