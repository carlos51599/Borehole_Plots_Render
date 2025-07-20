"""
Functions for creating buffer zones around polylines
"""

import logging
import pyproj
from shapely.geometry import Point, LineString
from shapely.ops import transform as shapely_transform
import dash_leaflet as dl
import numpy as np
from coordinate_service import get_coordinate_service


def create_buffer_polygon(polyline_coords, buffer_meters=50):
    """
    Create a buffer polygon around a polyline for visualization

    Args:
        polyline_coords: List of [lat, lon] coordinates
        buffer_meters: Buffer size in meters

    Returns:
        List of [lat, lon] coordinates representing the buffer polygon
    """
    try:
        logging.info(
            f"Creating buffer polygon with {len(polyline_coords)} points and {buffer_meters}m buffer"
        )

        # Convert to lon, lat for Shapely
        line_points = [(lon, lat) for lat, lon in polyline_coords]
        line = LineString(line_points)

        # Get the centroid for UTM zone calculation
        centroid = line.centroid
        median_lon, median_lat = centroid.x, centroid.y

        # Calculate UTM zone
        utm_zone = int((median_lon + 180) / 6) + 1
        utm_crs = f"EPSG:{32600 + utm_zone if median_lat >= 0 else 32700 + utm_zone}"
        logging.info(f"Using UTM CRS: {utm_crs}")

        # Create transformer to UTM
        project_to_utm = pyproj.Transformer.from_crs(
            "epsg:4326", utm_crs, always_xy=True
        ).transform

        # Create transformer from UTM back to WGS84
        project_to_wgs84 = pyproj.Transformer.from_crs(
            utm_crs, "epsg:4326", always_xy=True
        ).transform

        # Transform line to UTM and create buffer with flat caps
        line_utm = shapely_transform(project_to_utm, line)
        # Use cap_style=2 for flat caps (perpendicular to line ends)
        # cap_style options: 1=round (default), 2=flat, 3=square
        buffer_utm = line_utm.buffer(buffer_meters, cap_style=2)

        # Transform buffer back to WGS84
        buffer_wgs84 = shapely_transform(project_to_wgs84, buffer_utm)

        # Extract coordinates (convert from lon,lat to lat,lon)
        buffer_coords = []
        if hasattr(buffer_wgs84, "exterior"):
            # Convert to lat, lon format for Leaflet
            buffer_coords = [[lat, lon] for lon, lat in buffer_wgs84.exterior.coords]

        return buffer_coords

    except Exception as e:
        logging.error(f"Error creating buffer polygon: {e}")
        return []


def create_buffer_visualization(polyline_coords, buffer_meters=50):
    """
    Create a Leaflet Polygon component to visualize the buffer

    Args:
        polyline_coords: List of [lat, lon] coordinates
        buffer_meters: Buffer size in meters

    Returns:
        dash_leaflet.Polygon component
    """
    buffer_coords = create_buffer_polygon(polyline_coords, buffer_meters)

    if buffer_coords:
        return dl.Polygon(
            positions=buffer_coords,
            color="blue",
            fillColor="blue",
            fillOpacity=0.2,
            weight=1,
            opacity=0.7,
            dashArray="5,5",
            children=dl.Tooltip(f"{buffer_meters}m Buffer Zone"),
        )
    else:
        return None


def calculate_distance_along_polyline(polyline_coords, point_lat, point_lon):
    """
    Calculate the distance along a polyline from start to the closest point to the given coordinates

    Args:
        polyline_coords: List of [lat, lon] coordinates
        point_lat: Latitude of the point
        point_lon: Longitude of the point

    Returns:
        Distance in meters from the start of the polyline
    """
    try:
        # Validate input coordinates
        if not point_lat or not point_lon:
            logging.warning("Invalid point coordinates: lat or lon is None/empty")
            return 0

        # Try to convert to float
        try:
            point_lat = float(point_lat)
            point_lon = float(point_lon)
        except (ValueError, TypeError) as e:
            logging.warning(
                f"Cannot convert coordinates to float: lat={point_lat}, lon={point_lon}, error={e}"
            )
            return 0

        # Convert to lon, lat for Shapely
        line_points = [(lon, lat) for lat, lon in polyline_coords]
        line = LineString(line_points)
        point = Point(point_lon, point_lat)

        # Get centroid for UTM zone calculation
        centroid = line.centroid
        median_lon, median_lat = centroid.x, centroid.y

        # Calculate UTM zone
        utm_zone = int((median_lon + 180) / 6) + 1
        utm_crs = f"EPSG:{32600 + utm_zone if median_lat >= 0 else 32700 + utm_zone}"

        # Create transformer to UTM
        project_to_utm = pyproj.Transformer.from_crs(
            "epsg:4326", utm_crs, always_xy=True
        ).transform

        # Transform line and point to UTM
        line_utm = shapely_transform(project_to_utm, line)
        point_utm = shapely_transform(project_to_utm, point)

        # Calculate closest point on line
        closest_point_dist = line_utm.project(point_utm)

        return closest_point_dist

    except Exception as e:
        logging.error(f"Error calculating distance along polyline: {e}")
        return 0


def create_polyline_section(polyline_feature, stored_data=None):
    """
    Create a section line from a polyline feature drawn on the map

    Args:
        polyline_feature: GeoJSON feature representing a polyline
        stored_data: Dictionary containing stored app data (optional)

    Returns:
        List of Dash Leaflet components for visualization
    """
    try:
        logging.info("Creating polyline section")

        # Extract coordinates from the feature
        if isinstance(polyline_feature, dict) and "geometry" in polyline_feature:
            coordinates = polyline_feature["geometry"]["coordinates"]
            # Convert from [lon, lat] to [lat, lon] for Leaflet
            polyline_coords = [[lat, lon] for lon, lat in coordinates]
        elif isinstance(polyline_feature, list):
            # Assume already in [lat, lon] format
            polyline_coords = polyline_feature
        else:
            logging.error(
                f"Unexpected polyline feature format: {type(polyline_feature)}"
            )
            return []

        # Store the polyline coordinates for later use
        if stored_data is not None:
            stored_data["last_polyline"] = polyline_coords
            buffer_value = stored_data.get("buffer_value", 50)
            stored_data["buffer_value"] = buffer_value

        # Create a Leaflet Polyline component to visualize the section line
        polyline = dl.Polyline(
            positions=polyline_coords,
            color="red",
            weight=3,
            opacity=0.8,
            children=dl.Tooltip("Section Line"),
        )

        # Return only the polyline component (removed start/end markers)
        return [polyline]

    except Exception as e:
        logging.error(f"Error creating polyline section: {e}")
        return []


def create_buffer_zone(polyline_feature, buffer_meters=50):
    """
    Create a buffer zone visualization around a polyline feature

    Args:
        polyline_feature: GeoJSON feature representing a polyline
        buffer_meters: Buffer size in meters

    Returns:
        List containing the buffer zone visualization component
    """
    try:
        # Extract coordinates from the feature
        if isinstance(polyline_feature, dict) and "geometry" in polyline_feature:
            coordinates = polyline_feature["geometry"]["coordinates"]
            # Convert from [lon, lat] to [lat, lon] for Leaflet
            polyline_coords = [[lat, lon] for lon, lat in coordinates]
        elif isinstance(polyline_feature, list):
            # Assume already in [lat, lon] format
            polyline_coords = polyline_feature
        else:
            logging.error(
                f"Unexpected polyline feature format: {type(polyline_feature)}"
            )
            return []

        # Create buffer visualization
        buffer_viz = create_buffer_visualization(polyline_coords, buffer_meters)

        if buffer_viz:
            return [buffer_viz]
        else:
            return []

    except Exception as e:
        logging.error(f"Error creating buffer zone: {e}")
        return []


def project_boreholes_to_polyline(borehole_df, polyline_coords, buffer_distance=50):
    """
    Project boreholes onto the polyline axis and filter those within buffer distance.
    Args:
        borehole_df: DataFrame with borehole data including LOCA_LAT and LOCA_LON
        polyline_coords: List of [lat, lon] coordinates defining the polyline
        buffer_distance: Buffer distance in meters
    Returns:
        DataFrame with filtered boreholes and their distances along the polyline
    """
    import pandas as pd

    try:
        if len(polyline_coords) < 2:
            logging.warning(
                "Polyline has fewer than 2 coordinates, returning all boreholes"
            )
            return borehole_df

        logging.info(
            f"Project boreholes to polyline: {len(polyline_coords)} coords, buffer {buffer_distance}m"
        )
        logging.info(f"Polyline coords: {polyline_coords}")

        # Convert polyline coordinates to UTM for accurate distance calculations
        line_points = [(lon, lat) for lat, lon in polyline_coords]
        line = LineString(line_points)
        centroid = line.centroid
        median_lon, median_lat = centroid.x, centroid.y
        utm_zone = int((median_lon + 180) / 6) + 1
        utm_crs = f"EPSG:{32600 + utm_zone if median_lat >= 0 else 32700 + utm_zone}"

        logging.info(f"Using UTM CRS: {utm_crs}")

        project_to_utm = pyproj.Transformer.from_crs(
            "epsg:4326", utm_crs, always_xy=True
        ).transform
        line_utm = shapely_transform(project_to_utm, line)

        logging.info(f"Processing {len(borehole_df)} boreholes")

        filtered_boreholes = []
        for i, (_, borehole) in enumerate(borehole_df.iterrows()):
            # Try both coordinate column names, but check for valid values
            bh_lon = bh_lat = None
            coord_source = None

            # Check LOCA_LAT/LOCA_LON first
            if (
                "LOCA_LAT" in borehole
                and "LOCA_LON" in borehole
                and borehole["LOCA_LAT"]
                and borehole["LOCA_LON"]
                and str(borehole["LOCA_LAT"]).strip() != ""
                and str(borehole["LOCA_LON"]).strip() != ""
            ):
                try:
                    bh_lat = float(borehole["LOCA_LAT"])
                    bh_lon = float(borehole["LOCA_LON"])
                    coord_source = "LOCA_LAT/LON"
                except (ValueError, TypeError):
                    pass  # Fall through to try lat/lon

            # If LOCA_LAT/LON failed, try lat/lon
            if bh_lat is None or bh_lon is None:
                if (
                    "lat" in borehole
                    and "lon" in borehole
                    and borehole["lat"]
                    and borehole["lon"]
                ):
                    try:
                        bh_lat = float(borehole["lat"])
                        bh_lon = float(borehole["lon"])
                        coord_source = "lat/lon"
                    except (ValueError, TypeError):
                        pass  # Skip this borehole

            # Skip if we couldn't get valid coordinates
            if bh_lat is None or bh_lon is None or coord_source is None:
                logging.warning(
                    f"Borehole {borehole.get('LOCA_ID', 'unknown')} has no valid coordinates"
                )
                continue

            try:
                point_utm = shapely_transform(project_to_utm, Point(bh_lon, bh_lat))
                distance_to_line = line_utm.distance(point_utm)

                if i < 3:  # Log first few for debugging
                    logging.debug(
                        f"Borehole {borehole.get('LOCA_ID', 'unknown')} ({coord_source}): "
                        f"coords=({bh_lat:.6f}, {bh_lon:.6f}), distance={distance_to_line:.1f}m"
                    )

                if distance_to_line <= buffer_distance:
                    distance_along = line_utm.project(point_utm)
                    borehole_dict = borehole.to_dict()
                    borehole_dict["distance_along_polyline"] = distance_along
                    borehole_dict["distance_to_polyline"] = distance_to_line
                    filtered_boreholes.append(borehole_dict)
            except Exception as e:
                logging.warning(
                    f"Error processing borehole {borehole.get('LOCA_ID', 'unknown')}: {e}"
                )
                continue

        logging.info(
            f"Filtered result: {len(filtered_boreholes)} boreholes within {buffer_distance}m"
        )

        if filtered_boreholes:
            result_df = pd.DataFrame(filtered_boreholes)
            result_df = result_df.sort_values("distance_along_polyline")
            return result_df
        else:
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error projecting boreholes to polyline: {e}")
        # Return empty DataFrame instead of all boreholes to avoid selecting everything
        return pd.DataFrame()


def point_to_line_distance(point, line_start, line_end):
    """
    Calculate perpendicular distance from a point to a line segment.
    Args:
        point: (x, y) coordinates of the point
        line_start: (x, y) coordinates of line start
        line_end: (x, y) coordinates of line end
    Returns:
        Distance in same units as input coordinates
    """
    try:
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_length == 0:
            return np.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        distance = (
            abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / line_length
        )
        return distance
    except Exception as e:
        logging.error(f"Error calculating point to line distance: {e}")
        return float("inf")


def project_point_to_line_segment(point, line_start, line_end):
    """
    Project a point onto a line segment.
    Args:
        point: (x, y) coordinates of the point
        line_start: (x, y) coordinates of line start
        line_end: (x, y) coordinates of line end
    Returns:
        (x, y) coordinates of the projected point on the line segment
    """
    try:
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx**2 + dy**2
        if length_sq == 0:
            return (x1, y1)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / length_sq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return (proj_x, proj_y)
    except Exception as e:
        logging.error(f"Error projecting point to line segment: {e}")
        return point
