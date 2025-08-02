#!/usr/bin/env python3
"""
Test Aspect Ratio Fix
=====================

This test verifies that the aspect ratio fix preserves A4 landscape proportions.
"""

import sys
import os
import base64
from PIL import Image
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section import plot_section_from_ags_content


def test_aspect_ratio_fix():
    """Test that the aspect ratio fix preserves A4 landscape proportions."""

    print("=== Testing Aspect Ratio Fix ===")
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

    print("\n🔧 Testing fixed aspect ratio...")
    print("Boreholes: LFDS2401, LFDS2401A, LFDS2402")

    try:
        result = plot_section_from_ags_content(
            ags_content,
            filter_loca_ids=["LFDS2401", "LFDS2401A", "LFDS2402"],
            return_base64=True,
        )

        if result and len(result) > 100:
            # Decode and analyze the fixed image
            image_data = base64.b64decode(result[22:])
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            actual_aspect_ratio = width / height

            # Expected A4 landscape values
            a4_landscape_width_in = 11.69
            a4_landscape_height_in = 8.27
            expected_aspect_ratio = a4_landscape_width_in / a4_landscape_height_in

            expected_width_px = int(a4_landscape_width_in * 300)
            expected_height_px = int(a4_landscape_height_in * 300)

            print(f"\n📊 Fixed Image Analysis:")
            print(f"- Actual dimensions: {width} x {height} pixels")
            print(
                f"- Expected A4 @ 300 DPI: {expected_width_px} x {expected_height_px} pixels"
            )
            print(f"- Actual aspect ratio: {actual_aspect_ratio:.3f}")
            print(f"- Expected A4 aspect ratio: {expected_aspect_ratio:.3f}")
            print(
                f"- Aspect ratio difference: {abs(actual_aspect_ratio - expected_aspect_ratio):.3f}"
            )

            # Check if fix worked
            aspect_tolerance = 0.01  # Tighter tolerance for fixed version
            aspect_ratio_ok = (
                abs(actual_aspect_ratio - expected_aspect_ratio) <= aspect_tolerance
            )

            if aspect_ratio_ok:
                print(f"\n✅ ASPECT RATIO FIX SUCCESSFUL!")
                print(f"✅ Figure maintains proper A4 landscape proportions")
                print(f"✅ Should display without stretching in web interface")

                # Check dimensions are close to expected
                width_diff = abs(width - expected_width_px)
                height_diff = abs(height - expected_height_px)

                if width_diff <= 10 and height_diff <= 10:  # Within 10 pixels tolerance
                    print(f"✅ Dimensions match expected A4 @ 300 DPI")
                else:
                    print(f"⚠️  Dimensions slightly different but aspect ratio correct")

            else:
                print(f"\n❌ Aspect ratio still incorrect after fix")
                return False

            # Save fixed version for comparison
            with open("test_results/aspect_ratio_FIXED.png", "wb") as f:
                f.write(image_data)
            print(f"\n📏 Saved fixed version: test_results/aspect_ratio_FIXED.png")

            print(f"\n🔧 Applied Fix:")
            print(f"- Removed bbox_inches='tight' from savefig")
            print(f"- Set bbox_inches=None to preserve figure proportions")
            print(f"- Added pad_inches=0.0 for clean edges")
            print(f"- Figure now maintains exact A4 landscape aspect ratio")

            return aspect_ratio_ok

        else:
            print("❌ Plot generation failed")
            return False

    except Exception as e:
        print(f"❌ Plot generation error: {e}")
        return False


if __name__ == "__main__":
    success = test_aspect_ratio_fix()
    exit(0 if success else 1)
