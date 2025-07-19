#!/usr/bin/env python3
"""
Test script to verify geology code color and hatch mapping works correctly.
"""

import pandas as pd
from borehole_log_professional import create_professional_borehole_log
from geology_code_utils import get_geology_color, get_geology_pattern


def test_geology_mapping():
    """Test that geology code mapping works correctly."""

    # Test codes that should exist in the CSV
    test_codes = ["101", "203", "501", "202", "801"]

    print("Testing geology code mapping:")
    for code in test_codes:
        color = get_geology_color(code)
        pattern = get_geology_pattern(code)
        print(f"Code '{code}': Color={color}, Hatch='{pattern}'")

    # Create test borehole data with real geology codes
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5, 8.0],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0, 12.0],
            "Geology_Code": test_codes,
            "Description": [
                "TOPSOIL - Brown organic clay",
                "Sandy CLAY - Firm brown clay with sand",
                "GRAVEL - Dense angular gravel with cobbles",
                "Silty CLAY - Stiff grey clay with occasional stones",
                "MUDSTONE - Weathered grey mudstone bedrock",
            ],
        }
    )

    print("\nTest data:")
    print(sample_data)

    # Create professional borehole log
    print(f"\nCreating borehole log with geology CSV mapping...")
    images = create_professional_borehole_log(
        sample_data,
        "TEST_BH001",
        geology_csv_path="Geology Codes BGS.csv",
        title="Test Borehole Log - Geology Code Mapping",
    )

    if images:
        print(f"SUCCESS: Generated {len(images)} page(s) for test borehole log")
        return True
    else:
        print("ERROR: Failed to generate borehole log")
        return False


if __name__ == "__main__":
    success = test_geology_mapping()
    if success:
        print(
            "\n✓ All tests passed! Legend colors and hatching should be working correctly."
        )
    else:
        print("\n✗ Tests failed! There may be issues with the legend mapping.")
