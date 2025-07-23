"""
Data Processing Module

This module handles the core data processing logic for uploaded files,
including coordinate transformation, marker creation, and data optimization.
"""

import logging
import base64
import statistics
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import dash_leaflet as dl

# Import required services and utilities
from data_loader import load_all_loca_data
from coordinate_service import get_coordinate_service
from dataframe_optimizer import optimize_borehole_dataframe
from memory_manager import monitor_memory_usage

logger = logging.getLogger(__name__)


def process_uploaded_files(
    file_contents: List[str], file_names: List[str]
) -> Tuple[List[Tuple[str, str]], float]:
    """
    Process uploaded file contents and extract AGS data.

    Args:
        file_contents: List of base64 encoded file contents
        file_names: List of file names

    Returns:
        Tuple of (ags_files_list, total_size_mb)
    """
    ags_files = []
    total_processed_size = 0.0

    for content, name in zip(file_contents, file_names or []):
        try:
            # Split content type and data
            content_type, content_string = content.split(",")

            # Calculate file size
            size_bytes = len(content_string) * 3 / 4  # Base64 overhead
            size_mb = size_bytes / (1024 * 1024)

            # Decode file content
            decoded = base64.b64decode(content_string)
            text_content = decoded.decode("utf-8")

            # Store AGS file data
            ags_files.append((name, text_content))
            total_processed_size += size_mb

            logger.info(f"Successfully processed file: {name} ({size_mb:.1f}MB)")

        except Exception as e:
            logger.error(f"Error reading {name}: {e}")
            # Skip failed files but continue processing
            continue

    return ags_files, total_processed_size


def load_and_optimize_borehole_data(
    ags_files: List[Tuple[str, str]],
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Load AGS data and optimize DataFrame for memory efficiency.

    Args:
        ags_files: List of (filename, content) tuples

    Returns:
        Tuple of (optimized_dataframe, filename_map)
    """
    # Load data using existing data loader
    loca_df, filename_map = load_all_loca_data(ags_files)
    logger.info(f"Loaded {len(loca_df)} boreholes")

    # Memory optimization
    monitor_memory_usage("DEBUG")
    loca_df = optimize_borehole_dataframe(loca_df)
    logger.info(f"✓ DataFrame optimized for memory efficiency: {len(loca_df)} rows")

    return loca_df, filename_map


def transform_coordinates_and_create_markers(
    loca_df: pd.DataFrame,
) -> Tuple[List[dl.Marker], List[Tuple[float, float]]]:
    """
    Transform coordinates and create map markers for boreholes.

    Args:
        loca_df: DataFrame containing borehole location data

    Returns:
        Tuple of (markers_list, valid_coordinates_list)
    """
    coordinate_service = get_coordinate_service()
    markers = []
    valid_coords = []

    # Define marker constants
    try:
        from .coordinate_utils import BLUE_MARKER
    except ImportError:
        BLUE_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"

    for i, row in loca_df.iterrows():
        try:
            # Extract coordinates
            easting = float(row["LOCA_NATE"]) if pd.notnull(row["LOCA_NATE"]) else None
            northing = float(row["LOCA_NATN"]) if pd.notnull(row["LOCA_NATN"]) else None

            if easting is not None and northing is not None:
                # Transform coordinates
                lat, lon = coordinate_service.transform_bng_to_wgs84(easting, northing)

                if lat is not None and lon is not None:
                    # Store coordinates in DataFrame
                    loca_df.at[i, "lat"] = lat
                    loca_df.at[i, "lon"] = lon
                    valid_coords.append((lat, lon))

                    # Create marker
                    marker = _create_borehole_marker(row, i, lat, lon)
                    markers.append(marker)

        except Exception as e:
            logger.warning(
                f"Skipping marker for row {i} ({row.get('LOCA_ID', 'unknown')}): {e}"
            )

    logger.info(
        f"Created {len(markers)} map markers from {len(valid_coords)} valid coordinates"
    )
    return markers, valid_coords


def _create_borehole_marker(
    row: pd.Series, index: int, lat: float, lon: float
) -> dl.Marker:
    """
    Create individual borehole marker.

    Args:
        row: DataFrame row containing borehole data
        index: Row index for marker ID
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        Dash Leaflet Marker component
    """
    # Create marker ID
    label = str(row["LOCA_ID"])
    marker_id = {"type": "borehole-marker", "index": index}

    # Format measurement values
    ground_level = _format_measurement_value(row.get("LOCA_GL", "N/A"))
    total_depth = _format_measurement_value(row.get("LOCA_FDEP", "N/A"))

    # Create tooltip text
    tooltip_text = f"""
    Borehole: {label}
    Ground Level: {ground_level}
    Total Depth: {total_depth}
    Click to view borehole log
    """

    # Define marker icon
    marker_icon = {
        "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
        "iconSize": [25, 41],
        "iconAnchor": [12, 41],
        "popupAnchor": [1, -34],
        "shadowSize": [41, 41],
    }

    return dl.Marker(
        id=marker_id,
        position=[lat, lon],
        children=dl.Tooltip(tooltip_text.strip()),
        icon=marker_icon,
        n_clicks=0,
    )


def _format_measurement_value(value) -> str:
    """
    Format measurement values with proper units.

    Args:
        value: Raw measurement value

    Returns:
        Formatted measurement string
    """
    if value == "N/A" or value is None or not str(value).strip():
        return "N/A"

    try:
        return f"{float(value):.2f}m"
    except (ValueError, TypeError):
        return "N/A"


def calculate_optimal_map_view(
    coordinates: List[Tuple[float, float]],
) -> Tuple[List[float], int]:
    """
    Calculate optimal map center and zoom from coordinate list.

    Args:
        coordinates: List of (lat, lon) coordinate tuples

    Returns:
        Tuple of (map_center, map_zoom)
    """
    if not coordinates:
        # Default to UK center
        return [51.5, -0.1], 6

    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]

    # Use median for robust centering
    median_lat = statistics.median(lats)
    median_lon = statistics.median(lons)
    map_center = [median_lat, median_lon]

    # Calculate zoom based on coordinate spread
    lat_range = max(lats) - min(lats)
    lon_range = max(lons) - min(lons)
    coord_range = max(lat_range, lon_range)

    if coord_range > 0.1:
        map_zoom = 10
    elif coord_range > 0.01:
        map_zoom = 12
    elif coord_range > 0.001:
        map_zoom = 14
    else:
        map_zoom = 16

    logger.info(
        f"🎯 Setting map center: [{median_lat:.6f}, {median_lon:.6f}] with zoom {map_zoom}"
    )

    return map_center, map_zoom


def prepare_borehole_data_for_storage(
    loca_df: pd.DataFrame, filename_map: Dict[str, str]
) -> Dict[str, Any]:
    """
    Prepare borehole data for Dash dcc.Store component.

    Args:
        loca_df: DataFrame containing borehole data
        filename_map: Mapping of filenames to content

    Returns:
        Dictionary ready for Dash store
    """
    return {
        "loca_df": loca_df.to_dict("records"),
        "filename_map": filename_map,
        "all_borehole_ids": loca_df["LOCA_ID"].tolist(),
    }
