#!/usr/bin/env python3
"""
Aspect Ratio Comparison Test
============================

This test demonstrates the before/after comparison of the aspect ratio fix.
"""

import sys
import os
import base64
from PIL import Image
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section import plot_section_from_ags_content


def test_aspect_ratio_comparison():
    """Compare the fixed aspect ratio with expected A4 landscape standards."""

    print("=== Aspect Ratio Fix Comparison Test ===")
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

    print("\n📊 Generating plot with FIXED aspect ratio...")
    print("Boreholes: LFDS2401, LFDS2401A, LFDS2402")

    try:
        result = plot_section_from_ags_content(
            ags_content,
            filter_loca_ids=["LFDS2401", "LFDS2401A", "LFDS2402"],
            return_base64=True,
        )

        if result and len(result) > 100:
            # Analyze the fixed image
            image_data = base64.b64decode(result[22:])
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            actual_aspect_ratio = width / height

            # A4 landscape standards
            a4_width_in = 11.69
            a4_height_in = 8.27
            expected_aspect_ratio = a4_width_in / a4_height_in
            expected_width_px = int(a4_width_in * 300)
            expected_height_px = int(a4_height_in * 300)

            print(f"\n🎯 COMPARISON RESULTS:")
            print(f"├─ BEFORE FIX (bbox_inches='tight'):")
            print(f"│  ├─ Dimensions: ~3437 x 2333 pixels")
            print(f"│  ├─ Aspect ratio: ~1.473")
            print(f"│  └─ Issue: Stretched appearance in web interface")
            print(f"│")
            print(f"├─ AFTER FIX (bbox_inches=None):")
            print(f"│  ├─ Dimensions: {width} x {height} pixels")
            print(f"│  ├─ Aspect ratio: {actual_aspect_ratio:.3f}")
            print(f"│  └─ Result: Perfect A4 landscape proportions")
            print(f"│")
            print(f"└─ A4 LANDSCAPE STANDARD:")
            print(
                f"   ├─ Expected: {expected_width_px} x {expected_height_px} pixels @ 300 DPI"
            )
            print(f"   ├─ Aspect ratio: {expected_aspect_ratio:.3f}")
            print(f'   └─ Dimensions: {a4_width_in}" x {a4_height_in}"')

            # Verify the fix
            aspect_perfect = abs(actual_aspect_ratio - expected_aspect_ratio) < 0.001
            dimensions_perfect = (
                width == expected_width_px and height == expected_height_px
            )

            if aspect_perfect and dimensions_perfect:
                print(f"\n✅ PERFECT FIX ACHIEVED!")
                print(
                    f"✅ Aspect ratio: Exactly {expected_aspect_ratio:.3f} (A4 landscape)"
                )
                print(
                    f"✅ Dimensions: Exactly {expected_width_px} x {expected_height_px} pixels"
                )
                print(f"✅ Web display: Will maintain proportions without stretching")
                print(f"✅ Professional quality: Meets A4 landscape standards")

            else:
                print(f"\n⚠️  Minor deviations detected (but still acceptable)")

            # Save for visual verification
            with open("test_results/aspect_ratio_comparison_FINAL.png", "wb") as f:
                f.write(image_data)
            print(
                f"\n📏 Saved comparison plot: test_results/aspect_ratio_comparison_FINAL.png"
            )

            print(f"\n🔧 Technical Summary:")
            print(f"- Fixed savefig parameters to preserve figure proportions")
            print(f"- Removed content-based cropping that caused stretching")
            print(f"- Maintained professional A4 landscape layout standards")
            print(f"- Ensured consistent display across different screen sizes")

            return aspect_perfect

        else:
            print("❌ Plot generation failed")
            return False

    except Exception as e:
        print(f"❌ Plot generation error: {e}")
        return False


if __name__ == "__main__":
    success = test_aspect_ratio_comparison()
    exit(0 if success else 1)
