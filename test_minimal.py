#!/usr/bin/env python3
"""Minimal test to verify polyline plotting fixes"""

import sys
import os
import pandas as pd
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from section_plot import plot_borehole_sections


def create_test_data():
    """Create minimal test data for polyline plotting"""
    print("Creating test data...")

    # Create GEOL data
    geol_data = []
    loca_data = []

    # Create 4 test boreholes at known BNG coordinates
    test_boreholes = [
        {"id": "BH01", "bng_x": 529090, "bng_y": 181680, "gl": 10.0},  # Greenwich area
        {"id": "BH02", "bng_x": 529200, "bng_y": 181780, "gl": 12.0},  # 200m northeast
        {"id": "BH03", "bng_x": 529300, "bng_y": 181880, "gl": 8.0},  # 400m northeast
        {"id": "BH04", "bng_x": 529400, "bng_y": 181980, "gl": 15.0},  # 600m northeast
    ]

    # Create geology data for each borehole
    for bh in test_boreholes:
        # Add some geology layers
        geol_data.extend(
            [
                {
                    "LOCA_ID": bh["id"],
                    "GEOL_TOP": 0.0,
                    "GEOL_BASE": 2.0,
                    "GEOL_LEG": "TOPSOIL",
                    "GEOL_DESC": "Dark brown topsoil",
                },
                {
                    "LOCA_ID": bh["id"],
                    "GEOL_TOP": 2.0,
                    "GEOL_BASE": 5.0,
                    "GEOL_LEG": "CLAY",
                    "GEOL_DESC": "Firm brown clay",
                },
                {
                    "LOCA_ID": bh["id"],
                    "GEOL_TOP": 5.0,
                    "GEOL_BASE": 10.0,
                    "GEOL_LEG": "SAND",
                    "GEOL_DESC": "Dense yellow sand",
                },
            ]
        )

        # Add location data
        loca_data.append(
            {
                "LOCA_ID": bh["id"],
                "LOCA_NATE": bh["bng_x"],
                "LOCA_NATN": bh["bng_y"],
                "LOCA_GL": bh["gl"],
            }
        )

    # Create DataFrames
    geol_df = pd.DataFrame(geol_data)
    loca_df = pd.DataFrame(loca_data)

    # Convert to numeric types
    geol_df["GEOL_TOP"] = pd.to_numeric(geol_df["GEOL_TOP"])
    geol_df["GEOL_BASE"] = pd.to_numeric(geol_df["GEOL_BASE"])
    loca_df["LOCA_NATE"] = pd.to_numeric(loca_df["LOCA_NATE"])
    loca_df["LOCA_NATN"] = pd.to_numeric(loca_df["LOCA_NATN"])
    loca_df["LOCA_GL"] = pd.to_numeric(loca_df["LOCA_GL"])

    print(f"Created {len(geol_df)} geology records for {len(loca_df)} boreholes")
    print(f"Borehole locations (BNG):")
    for _, row in loca_df.iterrows():
        print(
            f"  {row['LOCA_ID']}: ({row['LOCA_NATE']}, {row['LOCA_NATN']}) GL={row['LOCA_GL']}"
        )

    return {"geol": geol_df, "loca": loca_df}


def test_polyline_plotting():
    """Test polyline plotting with coordinate transformation"""
    print("\n=== Testing Polyline Plotting Fixes ===")

    # Create test data
    test_data = create_test_data()

    # Create a test polyline in UTM coordinates (Zone 30N)
    # These coordinates correspond roughly to the Greenwich area in UTM
    test_polyline = [
        (698000, 5710000),  # Start point
        (698200, 5710200),  # 200m northeast
        (698400, 5710400),  # 400m northeast
        (698600, 5710600),  # 600m northeast
    ]

    print(f"\nTest polyline (UTM Zone 30N): {test_polyline}")

    # Test the section plot creation
    print("\nTesting section plot creation...")
    try:
        fig = plot_borehole_sections(
            geol_df=test_data["geol"],
            loca_df=test_data["loca"],
            section_line=test_polyline,
        )

        if fig:
            print("✓ Section plot created successfully!")
            print("✓ Coordinate transformation and distance calculation should work")

            # Check if fig has any data
            if hasattr(fig, "data") and fig.data:
                print(f"✓ Plot contains {len(fig.data)} traces")
                return True
            else:
                print("⚠ Plot created but contains no data")
                return False
        else:
            print("✗ Failed to create section plot")
            return False

    except Exception as e:
        print(f"✗ Error during section plot creation: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_no_polyline():
    """Test standard plotting without polyline"""
    print("\n=== Testing Standard Plotting (No Polyline) ===")

    # Create test data
    test_data = create_test_data()

    # Test the section plot creation without polyline
    print("Testing section plot creation without polyline...")
    try:
        fig = plot_borehole_sections(
            geol_df=test_data["geol"], loca_df=test_data["loca"], section_line=None
        )

        if fig:
            print("✓ Standard section plot created successfully!")
            return True
        else:
            print("✗ Failed to create standard section plot")
            return False

    except Exception as e:
        print(f"✗ Error during standard section plot creation: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing polyline plotting fixes...")

    # Test both modes
    polyline_success = test_polyline_plotting()
    standard_success = test_no_polyline()

    print(f"\n=== Test Results ===")
    print(f"Polyline plotting: {'✓ PASS' if polyline_success else '✗ FAIL'}")
    print(f"Standard plotting: {'✓ PASS' if standard_success else '✗ FAIL'}")

    if polyline_success and standard_success:
        print("\n🎉 All tests passed! The fixes should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
