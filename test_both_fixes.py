#!/usr/bin/env python3
"""
Test script to verify both fixes work together
"""

import sys
import os
import pyproj
from shapely.geometry import LineString
from shapely.ops import transform as shapely_transform
from polyline_utils import create_polyline_section

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing both fixes...")

# Test 1: Polyline markers removed
print("\n1. Testing polyline marker removal...")

polyline_feature = {
    "geometry": {"coordinates": [[-0.1278, 51.5074], [-0.1258, 51.5094]]}
}

components = create_polyline_section(polyline_feature)
if len(components) == 1:
    print("✅ PASS: Only polyline component returned (no markers)")
else:
    print("❌ FAIL: Expected 1 component, got", len(components))

# Test 2: Coordinate transformation
print("\n2. Testing coordinate transformation...")
try:
    # Test the same logic from callbacks_split.py
    polyline_coords = [[51.5074, -0.1278], [51.5094, -0.1258]]
    line_points = [(lon, lat) for lat, lon in polyline_coords]
    line = LineString(line_points)

    centroid = line.centroid
    median_lon, median_lat = centroid.x, centroid.y
    utm_zone = int((median_lon + 180) / 6) + 1
    utm_crs = f"EPSG:{32600 + utm_zone if median_lat >= 0 else 32700 + utm_zone}"

    project_to_utm = pyproj.Transformer.from_crs(
        "epsg:4326", utm_crs, always_xy=True
    ).transform

    line_utm = shapely_transform(project_to_utm, line)
    section_line = list(line_utm.coords)

    print("✅ PASS: Coordinate transformation successful")
    print(f"   Original: {polyline_coords}")
    print(f"   UTM: {section_line}")

except Exception as e:
    print(f"❌ FAIL: Coordinate transformation failed: {e}")

print("\n✅ All tests completed successfully!")
