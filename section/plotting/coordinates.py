"""
Coordinate Transformation Module

This module handles all coordinate transformations and data preparation
for section plotting, including BNG to WGS84, UTM projections, and
projection onto section lines.
"""

import pandas as pd
import pyproj
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


def prepare_coordinate_data(
    geol_df: pd.DataFrame,
    loca_df: pd.DataFrame,
    section_line: Optional[List[Tuple[float, float]]],
) -> Optional[Dict[str, Any]]:
    """
    Prepare coordinate data for plotting, handling coordinate transformations.

    Args:
        geol_df: Geological data DataFrame
        loca_df: Location data DataFrame
        section_line: Section line coordinates for projection

    Returns:
        Dict containing merged data, coordinate mappings, and borehole list
    """
    logger.debug(f"Professional section plot called with section_line: {section_line}")
    logger.debug(f"LOCA DataFrame shape: {loca_df.shape}")
    logger.debug(f"LOCA DataFrame columns: {loca_df.columns.tolist()}")

    # Check what coordinate columns are available
    coord_cols = [
        col
        for col in loca_df.columns
        if any(x in col.upper() for x in ["NATE", "NATN", "LAT", "LON"])
    ]
    logger.debug(f"Available coordinate columns: {coord_cols}")

    # Handle coordinate system for polyline mode
    if section_line is not None:
        return prepare_utm_coordinates(geol_df, loca_df, section_line)
    else:
        return prepare_bng_coordinates(geol_df, loca_df)


def prepare_utm_coordinates(
    geol_df: pd.DataFrame,
    loca_df: pd.DataFrame,
    section_line: List[Tuple[float, float]],
) -> Optional[Dict[str, Any]]:
    """Handle UTM coordinate transformation for polyline projection."""
    logger.debug("Using polyline mode - need consistent coordinate system")

    try:
        from shapely.geometry import Point as ShapelyPoint, LineString
    except ImportError:
        logger.error("Shapely library required for polyline projection")
        return None

    # BNG to WGS84 transformer
    bng_to_wgs84 = pyproj.Transformer.from_crs(
        "EPSG:27700", "EPSG:4326", always_xy=True
    )

    # WGS84 to UTM Zone 30N transformer
    utm_crs = "EPSG:32630"
    wgs84_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)

    # Transform section line from WGS84 to UTM
    utm_section_line = []
    for lat, lon in section_line:
        utm_x, utm_y = wgs84_to_utm.transform(lon, lat)
        utm_section_line.append((utm_x, utm_y))

    logger.debug(f"UTM Section line: {utm_section_line}")

    # Transform borehole coordinates from BNG to UTM (via WGS84)
    utm_coords = transform_to_utm(loca_df, bng_to_wgs84, wgs84_to_utm)

    if utm_coords is None:
        return None

    # Project onto section line and finalize data
    return project_onto_section_line(geol_df, loca_df, utm_coords, utm_section_line)


def prepare_bng_coordinates(
    geol_df: pd.DataFrame, loca_df: pd.DataFrame
) -> Optional[Dict[str, Any]]:
    """Handle BNG coordinate system (direct plotting without projection)."""
    logger.debug("Using direct BNG coordinates")

    # Merge geological and location data
    merged_df = pd.merge(geol_df, loca_df, on="LOCA_ID", how="inner")

    if merged_df.empty:
        logger.warning("No matching boreholes found between GEOL and LOCA data")
        return None

    logger.debug(f"Merged DataFrame shape: {merged_df.shape}")

    # Extract valid coordinates
    valid_coords = []
    borehole_x_map = {}

    for _, row in merged_df.iterrows():
        try:
            easting = float(row["LOCA_NATE"])
            borehole_id = row["LOCA_ID"]

            if borehole_id not in borehole_x_map:
                borehole_x_map[borehole_id] = easting
                valid_coords.append(easting)

        except (ValueError, TypeError, KeyError):
            continue

    if not valid_coords:
        logger.warning("No valid coordinates found")
        return None

    # Sort boreholes by easting for logical ordering
    sorted_boreholes = sorted(borehole_x_map.items(), key=lambda x: x[1])
    ordered_boreholes = [bh_id for bh_id, _ in sorted_boreholes]

    return finalize_coordinate_data(merged_df, borehole_x_map, ordered_boreholes)


def transform_to_utm(
    loca_df: pd.DataFrame,
    bng_to_wgs84: pyproj.Transformer,
    wgs84_to_utm: pyproj.Transformer,
) -> Optional[Dict[str, Tuple[float, float]]]:
    """Transform coordinates from BNG to UTM via WGS84."""
    utm_coords = {}

    for _, row in loca_df.iterrows():
        try:
            borehole_id = row["LOCA_ID"]
            bng_easting = float(row["LOCA_NATE"])
            bng_northing = float(row["LOCA_NATN"])

            # BNG to WGS84
            wgs84_lon, wgs84_lat = bng_to_wgs84.transform(bng_easting, bng_northing)

            # WGS84 to UTM
            utm_x, utm_y = wgs84_to_utm.transform(wgs84_lon, wgs84_lat)

            utm_coords[borehole_id] = (utm_x, utm_y)

            logger.debug(
                f"BH {borehole_id}: BNG({bng_easting}, {bng_northing}) -> "
                f"WGS84({wgs84_lat:.6f}, {wgs84_lon:.6f}) -> "
                f"UTM({utm_x:.2f}, {utm_y:.2f})"
            )

        except Exception as e:
            logger.warning(f"Failed to transform coordinates for {borehole_id}: {e}")
            continue

    if not utm_coords:
        logger.error("No valid coordinates could be transformed")
        return None

    return utm_coords


def project_onto_section_line(
    geol_df: pd.DataFrame,
    loca_df: pd.DataFrame,
    utm_coords: Dict[str, Tuple[float, float]],
    utm_section_line: List[Tuple[float, float]],
) -> Optional[Dict[str, Any]]:
    """Project borehole coordinates onto the section line."""
    try:
        from shapely.geometry import Point as ShapelyPoint, LineString
    except ImportError:
        logger.error("Shapely library required for projection")
        return None

    # Create section line geometry
    section_line_geom = LineString(utm_section_line)
    section_length = section_line_geom.length

    logger.debug(f"Section line length: {section_length:.2f} meters")

    # Project each borehole onto the section line
    projected_positions = {}

    for borehole_id, (utm_x, utm_y) in utm_coords.items():
        try:
            point = ShapelyPoint(utm_x, utm_y)

            # Find the closest point on the section line
            projected_point = section_line_geom.interpolate(
                section_line_geom.project(point)
            )

            # Calculate distance along section line
            distance_along_line = section_line_geom.project(projected_point)

            projected_positions[borehole_id] = distance_along_line

            logger.debug(
                f"BH {borehole_id}: UTM({utm_x:.2f}, {utm_y:.2f}) -> "
                f"Distance: {distance_along_line:.2f}m"
            )

        except Exception as e:
            logger.warning(f"Failed to project {borehole_id}: {e}")
            continue

    if not projected_positions:
        logger.error("No boreholes could be projected onto section line")
        return None

    # Sort boreholes by position along section line
    sorted_boreholes = sorted(projected_positions.items(), key=lambda x: x[1])
    ordered_boreholes = [bh_id for bh_id, _ in sorted_boreholes]

    # Create merged data
    merged_df = pd.merge(geol_df, loca_df, on="LOCA_ID", how="inner")

    return finalize_coordinate_data(merged_df, projected_positions, ordered_boreholes)


def finalize_coordinate_data(
    merged_df: pd.DataFrame,
    borehole_x_map: Dict[str, float],
    ordered_boreholes: List[str],
) -> Dict[str, Any]:
    """Finalize coordinate data structure for plotting."""
    logger.info(f"Final coordinate data: {len(ordered_boreholes)} boreholes ordered")

    return {
        "merged_df": merged_df,
        "borehole_x_map": borehole_x_map,
        "ordered_boreholes": ordered_boreholes,
    }
