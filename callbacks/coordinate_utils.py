"""
Coordinate transformation and mapping utilities for callbacks.

This module provides coordinate system transformations, map utilities,
and geographic calculations used by various callback functions.
"""

import logging
from typing import Tuple, Optional, List, Dict, Any
from coordinate_service import get_coordinate_service

logger = logging.getLogger(__name__)

# Define marker icon URLs
BLUE_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
GREEN_MARKER = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"


def transform_coordinates(
    easting: float, northing: float
) -> Tuple[Optional[float], Optional[float]]:
    """
    Transform BNG to WGS84 coordinates using centralized coordinate service.

    Args:
        easting: British National Grid easting coordinate
        northing: British National Grid northing coordinate

    Returns:
        tuple: (latitude, longitude) in WGS84, or (None, None) if transformation fails
    """
    try:
        coord_service = get_coordinate_service()
        lat, lon = coord_service.bng_to_wgs84(easting, northing)
        return lat, lon
    except Exception as e:
        logger.error(
            f"Coordinate transformation failed for ({easting}, {northing}): {e}"
        )
        return None, None


def calculate_map_bounds(coordinates: List[Tuple[float, float]]) -> Dict[str, float]:
    """
    Calculate map bounds for a list of coordinates.

    Args:
        coordinates: List of (lat, lon) tuples

    Returns:
        dict: Map bounds with keys 'north', 'south', 'east', 'west'
    """
    if not coordinates:
        return {
            "north": 52.0,
            "south": 50.0,
            "east": 1.0,
            "west": -2.0,
        }  # Default UK bounds

    lats = [coord[0] for coord in coordinates if coord[0] is not None]
    lons = [coord[1] for coord in coordinates if coord[1] is not None]

    if not lats or not lons:
        return {"north": 52.0, "south": 50.0, "east": 1.0, "west": -2.0}

    # Add small padding
    padding = 0.01

    return {
        "north": max(lats) + padding,
        "south": min(lats) - padding,
        "east": max(lons) + padding,
        "west": min(lons) - padding,
    }


def calculate_map_center_and_zoom(
    coordinates: List[Tuple[float, float]],
) -> Tuple[List[float], int]:
    """
    Calculate optimal map center and zoom level for given coordinates.

    Args:
        coordinates: List of (lat, lon) tuples

    Returns:
        tuple: ([center_lat, center_lon], zoom_level)
    """
    if not coordinates:
        return [51.5, -0.1], 6  # Default to London, UK

    valid_coords = [
        (lat, lon) for lat, lon in coordinates if lat is not None and lon is not None
    ]

    if not valid_coords:
        return [51.5, -0.1], 6

    if len(valid_coords) == 1:
        return list(valid_coords[0]), 15  # Single point, high zoom

    # Calculate center
    lats = [coord[0] for coord in valid_coords]
    lons = [coord[1] for coord in valid_coords]

    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Calculate zoom based on coordinate spread
    lat_range = max(lats) - min(lats)
    lon_range = max(lons) - min(lons)
    max_range = max(lat_range, lon_range)

    # Estimate zoom level based on range
    if max_range > 2.0:
        zoom = 6
    elif max_range > 1.0:
        zoom = 7
    elif max_range > 0.5:
        zoom = 8
    elif max_range > 0.1:
        zoom = 10
    elif max_range > 0.05:
        zoom = 12
    else:
        zoom = 14

    return [center_lat, center_lon], zoom


def create_selection_shape_visual(feature: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a visual representation of a drawn selection shape for display.

    Args:
        feature: GeoJSON feature from drawing controls

    Returns:
        dict: Visual representation data for the shape
    """
    try:
        geometry_type = feature.get("geometry", {}).get("type", "")
        coordinates = feature.get("geometry", {}).get("coordinates", [])

        shape_info = {
            "type": geometry_type,
            "coordinates": coordinates,
            "bounds": None,
            "area": None,
        }

        if geometry_type == "Polygon" and coordinates:
            # Calculate polygon bounds and approximate area
            if len(coordinates) > 0 and len(coordinates[0]) > 2:
                lats = [coord[1] for coord in coordinates[0]]
                lons = [coord[0] for coord in coordinates[0]]

                shape_info["bounds"] = {
                    "north": max(lats),
                    "south": min(lats),
                    "east": max(lons),
                    "west": min(lons),
                }

                # Simple area approximation (not accurate for large areas)
                lat_range = max(lats) - min(lats)
                lon_range = max(lons) - min(lons)
                shape_info["area"] = lat_range * lon_range

        elif geometry_type == "LineString" and coordinates:
            # Calculate line length and bounds
            if len(coordinates) > 1:
                lats = [coord[1] for coord in coordinates]
                lons = [coord[0] for coord in coordinates]

                shape_info["bounds"] = {
                    "north": max(lats),
                    "south": min(lats),
                    "east": max(lons),
                    "west": min(lons),
                }

                # Calculate approximate line length
                total_length = 0
                for i in range(1, len(coordinates)):
                    lat1, lon1 = coordinates[i - 1][1], coordinates[i - 1][0]
                    lat2, lon2 = coordinates[i][1], coordinates[i][0]
                    # Simple Euclidean distance (not accurate for large distances)
                    length = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5
                    total_length += length

                shape_info["length"] = total_length

        logger.debug(f"Created shape visual for {geometry_type}: {shape_info}")
        return shape_info

    except Exception as e:
        logger.error(f"Error creating selection shape visual: {e}")
        return {"type": "unknown", "coordinates": [], "bounds": None, "area": None}


def validate_borehole_near_polyline(
    borehole_lat: float,
    borehole_lon: float,
    polyline_coords: List[List[float]],
    max_distance: float = 100,
) -> bool:
    """
    Validate if a borehole is within a specified distance of a polyline.

    Args:
        borehole_lat: Borehole latitude
        borehole_lon: Borehole longitude
        polyline_coords: List of [lon, lat] coordinate pairs for the polyline
        max_distance: Maximum distance in meters (default 100m)

    Returns:
        bool: True if borehole is within max_distance of the polyline
    """
    if not polyline_coords or len(polyline_coords) < 2:
        return False

    try:
        # Simple distance check - in a real implementation, you'd use proper geodesic calculations
        # Convert max_distance from meters to approximate degrees (very rough)
        max_distance_deg = max_distance / 111000  # ~111km per degree

        for i in range(len(polyline_coords) - 1):
            lon1, lat1 = polyline_coords[i]
            lon2, lat2 = polyline_coords[i + 1]

            # Check distance to line segment (simplified)
            # This is a very rough approximation
            dist = point_to_line_distance_simple(
                borehole_lat, borehole_lon, lat1, lon1, lat2, lon2
            )

            if dist <= max_distance_deg:
                return True

        return False

    except Exception as e:
        logger.error(f"Error validating borehole distance to polyline: {e}")
        return False


def point_to_line_distance_simple(
    px: float, py: float, x1: float, y1: float, x2: float, y2: float
) -> float:
    """
    Calculate approximate distance from point to line segment.

    This is a simplified 2D distance calculation, not suitable for accurate geodesic calculations.
    """
    # Line segment vector
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        # Point to point distance
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5

    # Parameter t for closest point on line
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

    # Closest point on line segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    # Distance from point to closest point
    return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
