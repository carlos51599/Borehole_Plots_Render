import pandas as pd
import logging
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import transform as shapely_transform
import pyproj


def filter_selection_by_shape(loca_df, drawn_geojson):
    """Filter borehole data by drawn shape with extensive logging"""
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

        # Log sample data
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

    # Log GeoJSON structure
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

            result = loca_df[
                (loca_df["lat"] >= min_lat)
                & (loca_df["lat"] <= max_lat)
                & (loca_df["lon"] >= min_lon)
                & (loca_df["lon"] <= max_lon)
            ].copy()  # Add .copy() to avoid view issues
            logging.info(f"Rectangle filter result: {len(result)} boreholes")
            if len(result) > 0:
                logging.info(f"Selected borehole IDs: {result['LOCA_ID'].tolist()}")
            return result
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

                def point_in_polygon(row):
                    try:
                        point = Point(row["lon"], row["lat"])  # lon, lat order
                        result = poly.contains(point)
                        logging.debug(
                            f"Point {row['LOCA_ID']} ({row['lon']:.6f}, {row['lat']:.6f}): {result}"
                        )
                        return result
                    except Exception as e:
                        logging.warning(f"Error checking point {row['LOCA_ID']}: {e}")
                        return False

                mask = loca_df.apply(point_in_polygon, axis=1)
                result = loca_df[mask].copy()  # Add .copy() to avoid view issues
                logging.info(f"Polygon filter result: {len(result)} boreholes")

                # Log which points were selected
                if len(result) > 0:
                    selected_ids = result["LOCA_ID"].tolist()
                    logging.info(f"Selected borehole IDs: {selected_ids}")
                else:
                    logging.warning("No boreholes found inside polygon!")
                    # Log all available points for debugging
                    logging.info("Available borehole coordinates:")
                    for i, row in loca_df.iterrows():
                        if pd.notna(row["lat"]) and pd.notna(row["lon"]):
                            logging.info(
                                f"  {row['LOCA_ID']}: ({row['lon']:.6f}, {row['lat']:.6f})"
                            )
                            # Also check if point is close to polygon
                            point = Point(row["lon"], row["lat"])
                            distance = poly.distance(point)
                            logging.info(f"    Distance to polygon: {distance:.6f}")

                return result
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

                def point_near_line(row):
                    try:
                        point = Point(row["lon"], row["lat"])  # lon, lat order
                        point_utm = shapely_transform(project, point)
                        result = buffer_utm.contains(point_utm)
                        return result
                    except Exception as e:
                        logging.warning(
                            f"Error checking point {row['LOCA_ID']} near line: {e}"
                        )
                        return False

                mask = loca_df.apply(point_near_line, axis=1)
                result = loca_df[mask].copy()  # Add .copy() to avoid view issues
                logging.info(f"LineString filter result: {len(result)} boreholes")
                return result
            except Exception as line_err:
                logging.error(f"Error processing LineString: {line_err}", exc_info=True)
                return pd.DataFrame()
        else:
            logging.error(f"Invalid LineString coordinates: {coordinates}")
            return pd.DataFrame()
    else:
        logging.error(f"Unsupported geometry type: {geom_type}")
        return pd.DataFrame()
