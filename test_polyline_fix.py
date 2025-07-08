#!/usr/bin/env python3
"""
Test script to verify polyline filtering fix
"""

import pandas as pd
import sys
import os
from polyline_utils import project_boreholes_to_polyline

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_polyline_filtering():
    """Test that polyline filtering works correctly"""

    # Create sample borehole data
    test_data = {
        "LOCA_ID": ["BH001", "BH002", "BH003", "BH004", "BH005"],
        "lat": [51.5074, 51.5084, 51.5094, 51.5104, 51.5114],  # Along a line
        "lon": [-0.1278, -0.1268, -0.1258, -0.1248, -0.1238],  # Along a line
        "LOCA_NATE": [529000, 529100, 529200, 529300, 529400],
        "LOCA_NATN": [181000, 181100, 181200, 181300, 181400],
    }

    df = pd.DataFrame(test_data)

    # Create a polyline that should select only some boreholes
    polyline_coords = [
        [51.5074, -0.1278],  # Start near BH001
        [51.5094, -0.1258],  # Pass through BH003
    ]

    # Test with different buffer distances
    buffer_distances = [10, 100, 1000]  # meters

    print("Testing polyline filtering with different buffer distances:")
    print(f"Total boreholes: {len(df)}")
    print(f"Polyline coordinates: {polyline_coords}")

    for buffer_dist in buffer_distances:
        result = project_boreholes_to_polyline(df, polyline_coords, buffer_dist)
        selected_ids = result["LOCA_ID"].tolist() if not result.empty else []
        print(
            f"Buffer {buffer_dist}m: Selected {len(selected_ids)} boreholes: {selected_ids}"
        )

    # Test with a very small buffer - should select few or no boreholes
    small_buffer_result = project_boreholes_to_polyline(df, polyline_coords, 10)

    # Test with a large buffer - should select more boreholes
    large_buffer_result = project_boreholes_to_polyline(df, polyline_coords, 1000)

    print("\nTest Results:")
    print(f"Small buffer (10m): {len(small_buffer_result)} boreholes")
    print(f"Large buffer (1000m): {len(large_buffer_result)} boreholes")

    # The large buffer should select more boreholes than the small buffer
    if len(large_buffer_result) >= len(small_buffer_result):
        print("✅ Test PASSED: Buffer distance affects selection correctly")
        return True
    else:
        print("❌ Test FAILED: Buffer distance not working correctly")
        return False


if __name__ == "__main__":
    success = test_polyline_filtering()
    sys.exit(0 if success else 1)
