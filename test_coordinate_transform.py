#!/usr/bin/env python3
"""
Test coordinate transformation from BNG to WGS84
"""

from pyproj import Transformer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create transformer
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def test_transform_coordinates(easting, northing):
    """Test coordinate transformation"""
    try:
        lon, lat = transformer.transform(easting, northing)
        print(f"BNG({easting}, {northing}) -> WGS84({lat:.6f}, {lon:.6f})")

        # Check if coordinates are reasonable for UK
        if 49.0 <= lat <= 61.0 and -8.0 <= lon <= 2.0:
            print("✅ Coordinates are within UK bounds")
        else:
            print("❌ Coordinates are outside UK bounds")

        return lat, lon
    except Exception as e:
        print(f"❌ Error transforming: {e}")
        return None, None


# Test with the coordinates from your debug output
print("Testing coordinate transformation:")
print("=" * 50)

# Your original coordinates that appeared at top of map
test_transform_coordinates(441882.095, 388034.2)
test_transform_coordinates(441844.67, 388019.49)

print("\nTesting known UK locations:")
print("=" * 50)

# Test with known BNG coordinates
# London area (roughly)
test_transform_coordinates(530000, 180000)

# Manchester area (roughly)
test_transform_coordinates(380000, 400000)

# Edinburgh area (roughly)
test_transform_coordinates(325000, 665000)

print(
    "\nIf your coordinates are from UK AGS files, they should now show reasonable lat/lon values!"
)
