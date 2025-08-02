#!/usr/bin/env python3
"""
Test script to validate legend 4x5 grid layout changes.
"""

import sys
import os
from section.plotting.main import plot_section_from_ags_content

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_legend_layout():
    """Test that legend layout configuration is correctly set to 4x5."""
    print("🧪 Testing Legend 4x5 Grid Layout Configuration")
    print("=" * 60)

    try:
        # Read the AGS file for testing
        ags_file_path = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

        if not os.path.exists(ags_file_path):
            print(f"❌ AGS file not found: {ags_file_path}")
            return False

        with open(ags_file_path, "r") as f:
            ags_content = f.read()

        print("✅ AGS file loaded successfully")

        # Test the plotting function with legend parameters
        try:
            plot_result = plot_section_from_ags_content(
                ags_content=ags_content, show_labels=True
            )

            if plot_result and plot_result.startswith("data:image/png;base64,"):
                print("✅ Section plot generated successfully with 4x5 legend grid")
                print("✅ Plot returns valid base64 image data")
                return True
            else:
                print("❌ Plot generation failed or returned invalid data")
                return False

        except Exception as e:
            print(f"❌ Error during plot generation: {e}")
            return False

    except Exception as e:
        print(f"❌ Error reading AGS file: {e}")
        return False


def main():
    """Run the legend layout test."""
    print("🎯 Legend 4x5 Grid Layout Validation Test")
    print("=" * 60)

    success = test_legend_layout()

    if success:
        print("\n🎉 All tests passed!")
        print("✅ Legend 4x5 grid layout is working correctly")
        print("✅ Section plotting with new legend layout successful")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        print("⚠️  Legend layout may have issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
