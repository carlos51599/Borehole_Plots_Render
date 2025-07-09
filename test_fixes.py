#!/usr/bin/env python3
"""Test script to verify the polyline plotting fixes"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_ags_data
from section_plot import create_section_plot

# Test with a simple polyline
test_polyline = [
    (400000, 5600000),  # UTM coordinates
    (400100, 5600100),
    (400200, 5600200),
    (400300, 5600300),
]

print("Testing polyline plotting fixes...")
print(f"Test polyline: {test_polyline}")

# Try to load some test data
try:
    # Look for any AGS file in the workspace
    ags_files = [f for f in os.listdir(".") if f.endswith(".ags")]
    if ags_files:
        print(f"Found AGS files: {ags_files}")

        # Load first AGS file
        ags_file = ags_files[0]
        print(f"Loading {ags_file}...")

        data = load_ags_data(ags_file)
        if data:
            print("Data loaded successfully")

            # Test section plot with polyline
            fig = create_section_plot(data, section_line=test_polyline)

            if fig:
                print("Section plot created successfully!")
                print(
                    "The plot should show boreholes at their correct distances along the polyline"
                )
            else:
                print("Failed to create section plot")
        else:
            print("Failed to load data")
    else:
        print("No AGS files found in current directory")

except Exception as e:
    print(f"Error during test: {e}")
    import traceback

    traceback.print_exc()
