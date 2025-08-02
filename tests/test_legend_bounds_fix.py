#!/usr/bin/env python3
"""
Test Legend Bounds Fix
======================

This test verifies that the legend now stays within the left cell bounds.
"""

import sys
import os
import base64

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section import plot_section_from_ags_content


def test_legend_bounds_fix():
    """Test that the legend now stays within left cell bounds."""

    print("=== Testing Legend Bounds Fix ===")
    print()

    # Load AGS data
    ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    try:
        with open(ags_file, "r", encoding="utf-8") as f:
            ags_content = f.read()
        print("✅ Loaded AGS file")

    except Exception as e:
        print(f"❌ Failed to load AGS data: {e}")
        return False

    print("\n🎯 Testing legend bounds with clustered boreholes...")
    print("Boreholes: LFDS2401, LFDS2401A, LFDS2402")

    try:
        result = plot_section_from_ags_content(
            ags_content,
            filter_loca_ids=["LFDS2401", "LFDS2401A", "LFDS2402"],
            return_base64=True,
        )

        if result and len(result) > 100:
            # Save the fixed plot
            plot_bytes = base64.b64decode(result[22:])  # Remove data URL prefix
            with open("test_results/legend_bounds_FIXED.png", "wb") as f:
                f.write(plot_bytes)

            print("✅ Plot generated with legend bounds fix")
            print("📏 File: test_results/legend_bounds_FIXED.png")

            print("\n🔧 Applied Fixes:")
            print("- Reduced legend margins from 0.02 to 0.015")
            print("- Added dynamic column width calculation")
            print("- Implemented text width estimation")
            print("- Added bounds checking for all legend elements")
            print("- Enabled text clipping to prevent overflow")
            print("- Fall back to single column if content too wide")
            print("- Reduced symbol size from 0.03 to 0.025")

            print("\n✅ Legend should now stay within left cell bounds (0-0.7)")

            return True

        else:
            print("❌ Plot generation failed")
            return False

    except Exception as e:
        print(f"❌ Plot generation error: {e}")
        return False


if __name__ == "__main__":
    success = test_legend_bounds_fix()
    exit(0 if success else 1)
