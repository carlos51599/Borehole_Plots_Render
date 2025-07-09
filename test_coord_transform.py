#!/usr/bin/env python3
"""
Test the coordinate transformation logic
"""

import pandas as pd
import numpy as np

# Test the coordinate transformation logic
print("Testing coordinate transformation logic...")

# Create test data
test_data = {
    "LOCA_ID": ["BH001", "BH002", "BH003"],
    "lat": [51.5074, 51.5084, 51.5094],
    "lon": [-0.1278, -0.1268, -0.1258],
    "LOCA_GL": [100.0, 95.0, 90.0],
}

loca_df = pd.DataFrame(test_data)
print("Test DataFrame:")
print(loca_df)

# Test the polyline section line (UTM coordinates)
section_line = [(699316.23, 5710163.76), (699446.26, 5710391.57)]
print(f"\nSection line (UTM): {section_line}")

# Test the coordinate conversion
import pyproj
from shapely.geometry import LineString, Point

# Calculate UTM zone from section_line
# Note: section_line is already in UTM coordinates, so we use UK UTM Zone 30N.
utm_crs = "EPSG:32630"  # UTM Zone 30N for UK

print(f"UTM CRS: {utm_crs}")

# Transform borehole coordinates to UTM
project_to_utm = pyproj.Transformer.from_crs(
    "epsg:4326", utm_crs, always_xy=True
).transform
utm_coords = []
for _, row in loca_df.iterrows():
    if pd.notna(row["lat"]) and pd.notna(row["lon"]):
        utm_x, utm_y = project_to_utm(row["lon"], row["lat"])
        utm_coords.append({"LOCA_ID": row["LOCA_ID"], "UTM_X": utm_x, "UTM_Y": utm_y})

# Create a new DataFrame with UTM coordinates
utm_df = pd.DataFrame(utm_coords)
print(f"\nUTM coordinates for boreholes:")
print(utm_df)

# Test projection onto line
line = LineString(section_line)
for _, row in utm_df.iterrows():
    point = Point(row["UTM_X"], row["UTM_Y"])
    distance = line.project(point)
    print(f"Borehole {row['LOCA_ID']}: distance along line = {distance:.1f}m")

print("\n✅ Test completed successfully!")
