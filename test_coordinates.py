#!/usr/bin/env python3
"""
Test script to verify coordinate transformation
"""

import pyproj
from shapely.geometry import LineString
from shapely.ops import transform as shapely_transform

# Test polyline coordinates (lat/lon format)
polyline_coords = [[51.5074, -0.1278], [51.5094, -0.1258]]
print(f"Original polyline coords (lat/lon): {polyline_coords}")

# Convert to lon/lat for Shapely
line_points = [(lon, lat) for lat, lon in polyline_coords]
print(f"Line points (lon/lat): {line_points}")

# Create LineString
line = LineString(line_points)
print(f"LineString created: {line}")

# Get centroid
centroid = line.centroid
median_lon, median_lat = centroid.x, centroid.y
print(f"Centroid: {median_lon}, {median_lat}")

# Calculate UTM zone
utm_zone = int((median_lon + 180) / 6) + 1
utm_crs = f"EPSG:{32600 + utm_zone if median_lat >= 0 else 32700 + utm_zone}"
print(f"UTM CRS: {utm_crs}")

# Create transformer
project_to_utm = pyproj.Transformer.from_crs(
    "epsg:4326", utm_crs, always_xy=True
).transform

# Transform line
line_utm = shapely_transform(project_to_utm, line)
print(f"UTM line coords: {list(line_utm.coords)}")

print("Test completed successfully!")
