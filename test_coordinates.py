#!/usr/bin/env python3
"""
Test script to verify coordinate transformations and filtering functions
"""

import pandas as pd
from pyproj import Transformer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# Test coordinate transformation
def test_coordinate_transformation():
    """Test BNG to WGS84 coordinate transformation"""
    print("=== Testing Coordinate Transformation ===")

    # Create transformer
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    # Test coordinates for various UK locations
    test_coords = [
        (529090, 181680, "Greenwich Observatory"),  # Greenwich
        (525745, 155939, "Big Ben"),  # Central London
        (430147, 564608, "Edinburgh Castle"),  # Edinburgh
        (394251, 806376, "John o' Groats"),  # Northern Scotland
        (409776, 142958, "Land's End"),  # Southwest England
    ]

    for easting, northing, name in test_coords:
        try:
            lon, lat = transformer.transform(easting, northing)
            print(
                f"{name:20} BNG({easting:6.0f}, {northing:6.0f}) -> WGS84({lat:.6f}, {lon:.6f})"
            )

            # Validate coordinates are in UK bounds
            if 49.0 <= lat <= 61.0 and -8.0 <= lon <= 2.0:
                status = "✓ Valid"
            else:
                status = "✗ Out of bounds"
            print(f"                     {status}")
        except Exception as e:
            print(f"{name:20} ERROR: {e}")


def test_dataframe_filtering():
    """Test DataFrame filtering with mock data"""
    print("\n=== Testing DataFrame Filtering ===")

    # Create mock DataFrame with UK coordinates
    data = {
        "LOCA_ID": ["BH001", "BH002", "BH003", "BH004", "BH005"],
        "easting": [529090, 525745, 430147, 394251, 409776],
        "northing": [181680, 155939, 564608, 806376, 142958],
        "lat": [51.477928, 51.499384, 55.948595, 58.644005, 50.066389],
        "lon": [-0.001545, -0.124593, -3.199913, -3.052222, -5.716667],
    }

    df = pd.DataFrame(data)
    print(f"Created test DataFrame with {len(df)} boreholes")
    print(df[["LOCA_ID", "lat", "lon"]])

    # Test rectangle filtering (London area)
    print("\n--- Testing Rectangle Filter (London area) ---")
    london_bounds = {"min_lat": 51.4, "max_lat": 51.6, "min_lon": -0.5, "max_lon": 0.1}

    london_filter = df[
        (df["lat"] >= london_bounds["min_lat"])
        & (df["lat"] <= london_bounds["max_lat"])
        & (df["lon"] >= london_bounds["min_lon"])
        & (df["lon"] <= london_bounds["max_lon"])
    ]

    print(f"London area filter: {len(london_filter)} boreholes found")
    if len(london_filter) > 0:
        print(london_filter[["LOCA_ID", "lat", "lon"]])

    # Test with mock GeoJSON
    print("\n--- Testing with Mock GeoJSON ---")
    mock_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Rectangle",
                    "coordinates": [
                        [
                            [-0.5, 51.4],
                            [0.1, 51.4],
                            [0.1, 51.6],
                            [-0.5, 51.6],
                            [-0.5, 51.4],
                        ]
                    ],
                },
                "properties": {},
            }
        ],
    }

    print(f"Mock GeoJSON: {mock_geojson}")

    try:
        from map_utils import filter_selection_by_shape

        result = filter_selection_by_shape(df, mock_geojson)
        print(
            f"Filter function result: {type(result)}, length: {len(result) if hasattr(result, '__len__') else 'N/A'}"
        )
        if hasattr(result, "__len__") and len(result) > 0:
            print("Selected borehole IDs:", result)
    except Exception as e:
        print(f"Error testing filter function: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_coordinate_transformation()
    test_dataframe_filtering()
    print("\n=== Test Complete ===")
