#!/usr/bin/env python3
"""
Test script to compare coordinate transformations between old and new methods
"""

import pandas as pd
from pyproj import Transformer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def test_coordinate_transformation_methods():
    """Compare old Streamlit method vs new Dash method"""
    print("=== Coordinate Transformation Comparison ===")

    # Create transformer (same as both methods)
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    # Test coordinates from your debug output
    test_coords = [
        (353084, 432123, "Sample 1"),  # Your example coordinates
        (529090, 181680, "Greenwich"),
        (525745, 155939, "Big Ben"),
    ]

    for easting, northing, name in test_coords:
        print(f"\n{name}: BNG({easting}, {northing})")

        # Old Streamlit method (with [::-1] reversal)
        old_result = transformer.transform(easting, northing)[
            ::-1
        ]  # Reverses (lon, lat) to (lat, lon)
        print(f"  Old method: lat={old_result[0]:.6f}, lon={old_result[1]:.6f}")

        # New Dash method (manual swap)
        new_transform = transformer.transform(easting, northing)  # Returns (lon, lat)
        lat, lon = new_transform[1], new_transform[0]  # Manual swap to (lat, lon)
        print(f"  New method: lat={lat:.6f}, lon={lon:.6f}")

        # Check if they match
        lat_diff = abs(old_result[0] - lat)
        lon_diff = abs(old_result[1] - lon)
        match = lat_diff < 0.000001 and lon_diff < 0.000001
        print(
            f"  Match: {'✓' if match else '✗'} (lat_diff: {lat_diff:.8f}, lon_diff: {lon_diff:.8f})"
        )


def test_dataframe_coordinate_storage():
    """Test how coordinates are stored in DataFrame"""
    print("\n=== DataFrame Coordinate Storage Test ===")

    # Create test DataFrame similar to what the app creates
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    data = {
        "LOCA_ID": ["BH001", "BH002", "BH003"],
        "LOCA_NATE": [353084, 529090, 525745],  # BNG Easting
        "LOCA_NATN": [432123, 181680, 155939],  # BNG Northing
    }

    loca_df = pd.DataFrame(data)
    print(f"Original DataFrame:\n{loca_df}")

    # Add easting/northing columns (like the app does)
    loca_df["easting"] = loca_df["LOCA_NATE"]
    loca_df["northing"] = loca_df["LOCA_NATN"]

    # Add lat/lon columns
    loca_df["lat"] = None
    loca_df["lon"] = None

    # Transform coordinates (new method)
    for i, row in loca_df.iterrows():
        easting = float(row["easting"])
        northing = float(row["northing"])
        lon, lat = transformer.transform(easting, northing)  # Returns (lon, lat)
        loca_df.at[i, "lat"] = lat
        loca_df.at[i, "lon"] = lon

    print(f"\nAfter transformation:\n{loca_df[['LOCA_ID', 'lat', 'lon']]}")

    # Test DataFrame to dict conversion and back (like the app does)
    df_dict = loca_df.to_dict()
    print(f"\nAs dict keys: {list(df_dict.keys())}")
    print(f"Sample lat values: {list(df_dict['lat'].values())[:3]}")
    print(f"Sample lon values: {list(df_dict['lon'].values())[:3]}")

    # Convert back to DataFrame
    restored_df = pd.DataFrame(df_dict)
    print(f"\nRestored DataFrame:\n{restored_df[['LOCA_ID', 'lat', 'lon']]}")

    # Check if lat/lon columns exist and have valid data
    has_lat = "lat" in restored_df.columns
    has_lon = "lon" in restored_df.columns
    print(f"\nRestored DataFrame has lat column: {has_lat}")
    print(f"Restored DataFrame has lon column: {has_lon}")

    if has_lat and has_lon:
        valid_coords = restored_df[["lat", "lon"]].dropna()
        print(
            f"Valid coordinates after restoration: {len(valid_coords)} out of {len(restored_df)}"
        )
        if len(valid_coords) > 0:
            print("Sample restored coordinates:")
            for i, row in valid_coords.head(3).iterrows():
                print(
                    f"  {restored_df.loc[i, 'LOCA_ID']}: lat={row['lat']:.6f}, lon={row['lon']:.6f}"
                )


def test_drawing_area_selection():
    """Test if coordinates fall within a drawn area"""
    print("\n=== Drawing Area Selection Test ===")

    # Create test DataFrame with your coordinates
    data = {
        "LOCA_ID": ["BH001", "BH002", "BH003"],
        "lat": [53.87266595289811, 51.477928, 51.499384],
        "lon": [-2.1836936523995725, -0.001545, -0.124593],
    }
    df = pd.DataFrame(data)
    print(f"Test DataFrame:\n{df}")

    # Test rectangle selection around your coordinates
    # Your coordinates: [53.87266595289811, -2.1836936523995725]
    min_lat, max_lat = 53.8, 53.9
    min_lon, max_lon = -2.2, -2.1

    print(f"\nRectangle bounds: lat [{min_lat}, {max_lat}], lon [{min_lon}, {max_lon}]")

    filtered = df[
        (df["lat"] >= min_lat)
        & (df["lat"] <= max_lat)
        & (df["lon"] >= min_lon)
        & (df["lon"] <= max_lon)
    ]

    print(f"Filtered results: {len(filtered)} boreholes")
    if len(filtered) > 0:
        print(filtered[["LOCA_ID", "lat", "lon"]])
    else:
        print("No boreholes found in selection area!")
        print("Coordinate ranges in DataFrame:")
        print(f"  Lat: {df['lat'].min():.6f} to {df['lat'].max():.6f}")
        print(f"  Lon: {df['lon'].min():.6f} to {df['lon'].max():.6f}")


if __name__ == "__main__":
    test_coordinate_transformation_methods()
    test_dataframe_coordinate_storage()
    test_drawing_area_selection()
    print("\n=== Test Complete ===")
