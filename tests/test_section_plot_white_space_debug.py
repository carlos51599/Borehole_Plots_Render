"""
Debug Section Plot White Space Issue

This script tests the section plot generation to identify why there's empty white space
on the right half of the plot. It will trace coordinate calculations and positioning.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from section import plot_section_from_ags_content


def test_section_plot_positioning():
    """Test section plot to identify white space positioning issues."""

    # Load test AGS data
    ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    print("=== Section Plot White Space Debug Test ===")
    print(f"Loading AGS data from: {ags_file}")

    if not os.path.exists(ags_file):
        print(f"❌ AGS file not found: {ags_file}")
        return False

    try:
        with open(ags_file, "r", encoding="utf-8") as f:
            ags_content = f.read()

        print(f"✅ Loaded AGS content: {len(ags_content)} characters")

        # Test with a few boreholes to see positioning
        test_boreholes = [
            "LFDS2401",
            "LFDS2402",
            "LFDS2404",
        ]  # Using actual borehole names from data

        print(f"\n🔍 Testing section plot with boreholes: {test_boreholes}")

        # Capture plot generation with debug output
        import io
        from contextlib import redirect_stdout

        output_buffer = io.StringIO()

        with redirect_stdout(output_buffer):
            result = plot_section_from_ags_content(
                ags_content,
                filter_loca_ids=test_boreholes,
                show_labels=True,
                return_base64=True,
            )

        debug_output = output_buffer.getvalue()

        print("\n📋 Debug Output from Section Plot Generation:")
        print("=" * 60)
        print(debug_output)
        print("=" * 60)

        if result:
            print("\n✅ Section plot generated successfully")

            # Analyze debug output for positioning issues
            lines = debug_output.split("\n")
            coordinate_lines = [
                line
                for line in lines
                if "coordinates" in line.lower()
                or "distance" in line.lower()
                or "rel_x" in line
            ]

            if coordinate_lines:
                print("\n🎯 Coordinate Analysis:")
                for line in coordinate_lines:
                    print(f"  {line}")

            # Look for borehole width and positioning info
            positioning_lines = [
                line
                for line in lines
                if "borehole" in line.lower()
                and ("width" in line.lower() or "position" in line.lower())
            ]

            if positioning_lines:
                print("\n📐 Positioning Analysis:")
                for line in positioning_lines:
                    print(f"  {line}")

            # Check for axis limits
            axis_lines = [
                line
                for line in lines
                if "xlim" in line.lower()
                or "ylim" in line.lower()
                or "total_length" in line.lower()
            ]

            if axis_lines:
                print("\n📊 Axis Configuration:")
                for line in axis_lines:
                    print(f"  {line}")

            return True
        else:
            print("❌ Section plot generation failed")
            return False

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


def analyze_coordinate_distribution():
    """Analyze the coordinate distribution to understand data spread."""

    print("\n=== Coordinate Distribution Analysis ===")

    # Load and parse AGS data manually to check coordinate spread
    try:
        from section.parsing import parse_ags_geol_section_from_string

        ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

        with open(ags_file, "r", encoding="utf-8") as f:
            ags_content = f.read()

        geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)

        print(f"📊 Data Summary:")
        print(f"  - Geology records: {len(geol_df)}")
        print(f"  - Location records: {len(loca_df)}")
        print(f"  - Unique boreholes: {len(loca_df['LOCA_ID'].unique())}")

        # Check coordinate spread
        if "LOCA_NATE" in loca_df.columns and "LOCA_NATN" in loca_df.columns:
            easting = pd.to_numeric(loca_df["LOCA_NATE"], errors="coerce")
            northing = pd.to_numeric(loca_df["LOCA_NATN"], errors="coerce")

            print(f"\n📍 Coordinate Analysis:")
            print(
                f"  - Easting range: {easting.min():.1f} to {easting.max():.1f} (span: {easting.max() - easting.min():.1f}m)"
            )
            print(
                f"  - Northing range: {northing.min():.1f} to {northing.max():.1f} (span: {northing.max() - northing.min():.1f}m)"
            )

            # Show first few boreholes and their coordinates
            print(f"\n🎯 First 5 Borehole Coordinates:")
            for i, (idx, row) in enumerate(loca_df.head().iterrows()):
                if i >= 5:
                    break
                try:
                    e = float(row["LOCA_NATE"])
                    n = float(row["LOCA_NATN"])
                    print(f"  {row['LOCA_ID']}: E={e:.1f}, N={n:.1f}")
                except:
                    print(f"  {row['LOCA_ID']}: Invalid coordinates")

        return True

    except Exception as e:
        print(f"❌ Error analyzing coordinates: {e}")
        return False


def main():
    """Run the debug tests."""

    logging.basicConfig(level=logging.INFO)

    # Test 1: Basic coordinate distribution
    success1 = analyze_coordinate_distribution()

    # Test 2: Section plot positioning
    success2 = test_section_plot_positioning()

    print(f"\n=== Debug Test Results ===")
    print(f"Coordinate Analysis: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Section Plot Test: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1 and success2:
        print("\n🎉 Debug tests completed successfully!")
        print("\nNext Steps:")
        print("1. Review the debug output above for coordinate positioning")
        print("2. Check if boreholes are clustered on one side")
        print("3. Verify axis limits are correctly calculated")
        print("4. Look for issues in relative positioning calculations")
    else:
        print("\n❌ Debug tests revealed issues that need investigation")

    return success1 and success2


if __name__ == "__main__":
    main()
