"""
Map utilities for geometric operations and coordinate transformations.

This module provides utility functions for map-based operations in the Geo Borehole
Sections Render application, including:

1. Geometric Filtering:
   - Filter boreholes by drawn shapes (polygons, rectangles, lines)
   - Point-in-polygon calculations
   - Distance-based filtering for polylines

2. Coordinate Transformations:
   - British National Grid (EPSG:27700) to WGS84 (EPSG:4326)
   - Proper handling of coordinate system conversions
   - Integration with pyproj for accurate transformations

3. Shape Processing:
   - GeoJSON to Shapely geometry conversion
   - Buffer calculations for polyline selections
   - Geometric validation and error handling

Key Functions:
- filter_selection_by_shape(): Main filtering function for borehole selection
- transform_coordinates(): Convert between coordinate systems
- create_buffer_zone(): Generate buffer areas around polylines
- validate_geometry(): Check geometric validity

Dependencies:
- shapely: Geometric operations and spatial calculations
- pyproj: Coordinate system transformations
- pandas: Data manipulation for borehole datasets

Coordinate Systems:
- Input: British National Grid (EPSG:27700) from AGS files
- Output: WGS84 (EPSG:4326) for web mapping compatibility

Author: [Project Team]
Last Modified: July 2025
"""

import pandas as pd
import logging
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import transform as shapely_transform
import pyproj


def filter_selection_by_shape(loca_df, drawn_geojson):
    """
    Filter borehole data by drawn shape with comprehensive validation and logging.

    This function takes a DataFrame of borehole locations and a GeoJSON shape
    (polygon, rectangle, or polyline) and returns the IDs of boreholes that
    fall within or near the drawn shape.

    Args:
        loca_df (pandas.DataFrame): DataFrame containing borehole location data
                                   Must have columns: 'lat', 'lon', 'LOCA_ID'
        drawn_geojson (dict): GeoJSON object representing the drawn shape
                             Supports Polygon, Rectangle, and LineString geometries

    Returns:
        list: List of LOCA_ID strings for boreholes within the selection

    Processing Steps:
        1. Validate input data and required columns
        2. Convert GeoJSON to Shapely geometry objects
        3. Create Point objects from borehole coordinates
        4. Apply geometric filtering based on shape type:
           - Polygon/Rectangle: Point-in-polygon test
           - LineString: Distance-based filtering with buffer
        5. Return matching borehole IDs

    Coordinate System:
        - Input coordinates expected in WGS84 (lat/lon)
        - All geometric operations performed in WGS84
        - Automatic coordinate validation and range checking

    Error Handling:
        - Comprehensive input validation
        - Detailed logging for debugging
        - Graceful fallback for invalid geometries

    Example:
        >>> loca_df = pd.DataFrame({
        ...     'LOCA_ID': ['BH001', 'BH002'],
        ...     'lat': [51.5, 51.6],
        ...     'lon': [-0.1, -0.2]
        ... })
        >>> geojson = {
        ...     'type': 'FeatureCollection',
        ...     'features': [{
        ...         'geometry': {
        ...             'type': 'Polygon',
        ...             'coordinates': [[[-0.15, 51.45], [-0.05, 51.45],
        ...                            [-0.05, 51.55], [-0.15, 51.55], [-0.15, 51.45]]]
        ...         }
        ...     }]
        ... }
        >>> selected_ids = filter_selection_by_shape(loca_df, geojson)
        >>> print(selected_ids)
        ['BH001']
    """
    logging.info("====== FILTER_SELECTION_BY_SHAPE CALLED ======")
    logging.info(f"loca_df type: {type(loca_df)}")
    logging.info(f"drawn_geojson type: {type(drawn_geojson)}")

    # Validate inputs
    if loca_df is None:
        logging.error("loca_df is None")
        return []

    if drawn_geojson is None:
        logging.error("drawn_geojson is None")
        return []

    # Log DataFrame info
    if hasattr(loca_df, "shape"):
        logging.info(f"loca_df shape: {loca_df.shape}")
        logging.info(f"loca_df columns: {list(loca_df.columns)}")

        # Check for required columns
        required_cols = ["lat", "lon", "LOCA_ID"]
        missing_cols = [col for col in required_cols if col not in loca_df.columns]
        if missing_cols:
            logging.error(f"Missing required columns: {missing_cols}")
            return []

        # Log sample data and validate coordinate ranges
        if len(loca_df) > 0:
            logging.info(
                f"Sample coordinates: lat={loca_df['lat'].iloc[0]}, lon={loca_df['lon'].iloc[0]}"
            )
            logging.info(
                f"Coordinate ranges: lat [{loca_df['lat'].min():.6f}, {loca_df['lat'].max():.6f}]"
            )
            logging.info(
                f"Coordinate ranges: lon [{loca_df['lon'].min():.6f}, {loca_df['lon'].max():.6f}]"
            )

    # Log GeoJSON structure for debugging
    logging.info(
        f"drawn_geojson keys: {drawn_geojson.keys() if isinstance(drawn_geojson, dict) else 'not a dict'}"
    )

    # Extract features
    features = drawn_geojson.get("features", [])
    logging.info(f"Number of features: {len(features)}")

    if not features:
        logging.warning("No features found in drawn_geojson")
        return []

    # Process only the first feature (should be the only one)
    feature = features[0]
    logging.info("Processing feature...")
    logging.info(f"Feature type: {type(feature)}")

    if not isinstance(feature, dict):
        logging.warning("Feature is not a dict, skipping")
        return []

    geometry = feature.get("geometry", {})
    logging.info(f"Geometry: {geometry}")

    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    logging.info(f"Geometry type: {geom_type}")
    logging.info(f"Coordinates length: {len(coordinates)}")

    if coordinates:
        logging.info(
            f"First coordinate: {coordinates[0] if len(coordinates) > 0 else 'empty'}"
        )

    try:
        filtered_df = filter_by_geometry(loca_df, geometry)
        logging.info(f"Filtered result: {len(filtered_df)} boreholes")

        if len(filtered_df) > 0:
            # Return the selected borehole IDs
            unique_ids = filtered_df["LOCA_ID"].tolist()
            logging.info(f"Final borehole IDs: {unique_ids}")
            return unique_ids
        else:
            logging.info("No boreholes found in the feature")
            return []
    except Exception as filter_err:
        logging.error(f"Error filtering by feature: {filter_err}", exc_info=True)
        return []


def filter_by_geometry(loca_df, geometry):
    """Filter DataFrame by a single geometry with detailed logging"""
    logging.info(
        f"filter_by_geometry called with geometry type: {geometry.get('type')}"
    )

    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    if geom_type == "Rectangle":
        logging.info("Processing Rectangle geometry")
        # Rectangle coordinates are typically [[x1,y1], [x2,y1], [x2,y2], [x1,y2], [x1,y1]]
        if len(coordinates) > 0 and len(coordinates[0]) >= 4:
            coords = coordinates[0]
            lons = [pt[0] for pt in coords]
            lats = [pt[1] for pt in coords]
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)

            logging.info(
                f"Rectangle bounds: lat [{min_lat:.6f}, {max_lat:.6f}], lon [{min_lon:.6f}, {max_lon:.6f}]"
            )

            # Use boolean indexing without unnecessary copy
            mask = (
                (loca_df["lat"] >= min_lat)
                & (loca_df["lat"] <= max_lat)
                & (loca_df["lon"] >= min_lon)
                & (loca_df["lon"] <= max_lon)
            )
            result = loca_df[mask]
            logging.info(f"Rectangle filter result: {len(result)} boreholes")
            if len(result) > 0:
                logging.info(f"Selected borehole IDs: {result['LOCA_ID'].tolist()}")
            # Only copy when necessary for return (caller expects ownership)
            return result.copy() if len(result) > 0 else pd.DataFrame()
        else:
            logging.error(f"Invalid Rectangle coordinates: {coordinates}")
            return pd.DataFrame()

    elif geom_type == "Polygon":
        logging.info("Processing Polygon geometry")
        if len(coordinates) > 0 and len(coordinates[0]) >= 3:
            coords = coordinates[0]  # First ring of polygon
            logging.info(f"Polygon has {len(coords)} vertices")
            logging.info(f"First vertex: {coords[0]}, Last vertex: {coords[-1]}")

            try:
                poly = Polygon(
                    [(pt[0], pt[1]) for pt in coords]
                )  # lon, lat order for Shapely
                logging.info(f"Created Shapely polygon: bounds={poly.bounds}")

                # Test polygon validity
                if not poly.is_valid:
                    logging.warning(f"Polygon is not valid: {poly}")
                    poly = poly.buffer(0)  # Attempt to fix invalid polygon
                    logging.info(f"Fixed polygon validity: {poly.is_valid}")

                # Bounding box pre-filter (vectorized operation)
                minx, miny, maxx, maxy = poly.bounds
                bbox_mask = (
                    (loca_df["lon"] >= minx)
                    & (loca_df["lon"] <= maxx)
                    & (loca_df["lat"] >= miny)
                    & (loca_df["lat"] <= maxy)
                )
                candidates = loca_df[bbox_mask]

                # Vectorized point-in-polygon using shapely - optimized for performance
                if len(candidates) > 0:
                    # Create Points efficiently using numpy arrays
                    lon_values = candidates["lon"].values
                    lat_values = candidates["lat"].values
                    points = [
                        Point(lon, lat) for lon, lat in zip(lon_values, lat_values)
                    ]

                    # Vectorized contains operation
                    mask = [poly.contains(pt) for pt in points]
                    result = candidates[mask]
                else:
                    result = pd.DataFrame()

                logging.info(f"Polygon filter result: {len(result)} boreholes")

                # Log which points were selected
                if len(result) > 0:
                    selected_ids = result["LOCA_ID"].tolist()
                    logging.info(f"Selected borehole IDs: {selected_ids}")
                    # Only copy when returning (caller expects ownership)
                    return result.copy()
                else:
                    logging.warning("No boreholes found inside polygon!")
                    # Vectorized debug logging (avoid iterrows for performance)
                    if len(loca_df) <= 20:  # Only log details for small datasets
                        for idx in loca_df.index[
                            :10
                        ]:  # Limit to first 10 for performance
                            row = loca_df.loc[idx]
                            logging.info(
                                f"  {row['LOCA_ID']}: ({row['lon']:.6f}, {row['lat']:.6f})"
                            )
                            # Check distance to polygon for debugging
                            point = Point(row["lon"], row["lat"])
                            distance = poly.distance(point)
                            logging.info(f"    Distance to polygon: {distance:.6f}")
                    else:
                        logging.info(
                            f"Dataset too large ({len(loca_df)} rows) for detailed logging"
                        )
                    return pd.DataFrame()
            except Exception as poly_err:
                logging.error(
                    f"Error creating/using polygon: {poly_err}", exc_info=True
                )
                return pd.DataFrame()
        else:
            logging.error(f"Invalid Polygon coordinates: {coordinates}")
            return pd.DataFrame()

    elif geom_type == "LineString":
        logging.info("Processing LineString geometry")
        if len(coordinates) >= 2:
            coords = coordinates
            logging.info(f"LineString has {len(coords)} points")

            try:
                line = LineString([(pt[0], pt[1]) for pt in coords])  # lon, lat order
                buffer_m = 50  # Buffer in meters

                # Get median coordinates for UTM zone calculation
                median_lat = loca_df["lat"].median()
                median_lon = loca_df["lon"].median()
                logging.info(
                    f"Median coordinates for UTM: lat={median_lat:.6f}, lon={median_lon:.6f}"
                )

                utm_zone = int((median_lon + 180) / 6) + 1
                utm_crs = (
                    f"EPSG:{32600 + utm_zone if median_lat >= 0 else 32700 + utm_zone}"
                )
                logging.info(f"Using UTM CRS: {utm_crs}")

                # Create transformer
                project = pyproj.Transformer.from_crs(
                    "epsg:4326", utm_crs, always_xy=True
                ).transform

                # Transform line to UTM and create buffer
                line_utm = shapely_transform(project, line)
                buffer_utm = line_utm.buffer(buffer_m)
                logging.info(f"Created UTM buffer with {buffer_m}m radius")

                # Optimize LineString buffer operation using vectorized approach
                # Bounding box pre-filter in UTM coordinates
                minx, miny, maxx, maxy = buffer_utm.bounds

                # Vectorized coordinate transformation and filtering
                lon_values = loca_df["lon"].values
                lat_values = loca_df["lat"].values

                # Transform all points to UTM efficiently
                utm_x, utm_y = project(lon_values, lat_values)

                # Vectorized bounding box check
                bbox_mask = (
                    (utm_x >= minx)
                    & (utm_x <= maxx)
                    & (utm_y >= miny)
                    & (utm_y <= maxy)
                )

                if bbox_mask.any():
                    # Only process points within bounding box
                    candidate_indices = bbox_mask.nonzero()[0]
                    candidate_utm_points = [
                        Point(utm_x[i], utm_y[i]) for i in candidate_indices
                    ]

                    # Check which points are within buffer
                    buffer_mask = [
                        buffer_utm.contains(pt) for pt in candidate_utm_points
                    ]
                    result_indices = candidate_indices[buffer_mask]

                    result = loca_df.iloc[result_indices]
                    logging.info(f"LineString filter result: {len(result)} boreholes")
                    # Only copy when returning (caller expects ownership)
                    return result.copy() if len(result) > 0 else pd.DataFrame()
                else:
                    logging.info("No boreholes within LineString bounding box")
                    return pd.DataFrame()
            except Exception as line_err:
                logging.error(f"Error processing LineString: {line_err}", exc_info=True)
                return pd.DataFrame()
        else:
            logging.error(f"Invalid LineString coordinates: {coordinates}")
            return pd.DataFrame()
    else:
        logging.error(f"Unsupported geometry type: {geom_type}")
        return pd.DataFrame()
