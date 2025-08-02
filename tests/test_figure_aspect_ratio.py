#!/usr/bin/env python3
"""
Figure Aspect Ratio Diagnosis
=============================

This test diagnoses the figure stretching issue by analyzing the generated image dimensions
and aspect ratios to ensure proper A4 landscape proportions are maintained.
"""

import sys
import os
import base64
from PIL import Image
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section import plot_section_from_ags_content


def analyze_figure_aspect_ratio():
    """Analyze the aspect ratio and dimensions of generated figures."""

    print("=== Figure Aspect Ratio Diagnosis ===")
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

    print("\n🔍 Analyzing figure dimensions and aspect ratio...")
    print("Boreholes: LFDS2401, LFDS2401A, LFDS2402")

    try:
        result = plot_section_from_ags_content(
            ags_content,
            filter_loca_ids=["LFDS2401", "LFDS2401A", "LFDS2402"],
            return_base64=True,
        )

        if result and len(result) > 100:
            # Decode the base64 image to analyze dimensions
            image_data = base64.b64decode(result[22:])  # Remove data URL prefix

            # Open image with PIL to get dimensions
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            actual_aspect_ratio = width / height

            # Calculate expected A4 landscape dimensions at 300 DPI
            a4_landscape_width_in = 11.69
            a4_landscape_height_in = 8.27
            expected_aspect_ratio = a4_landscape_width_in / a4_landscape_height_in

            expected_width_px = int(a4_landscape_width_in * 300)  # 300 DPI
            expected_height_px = int(a4_landscape_height_in * 300)  # 300 DPI

            print(f"\n📊 Image Analysis Results:")
            print(f"- Actual dimensions: {width} x {height} pixels")
            print(
                f"- Expected A4 landscape @ 300 DPI: {expected_width_px} x {expected_height_px} pixels"
            )
            print(f"- Actual aspect ratio: {actual_aspect_ratio:.3f}")
            print(f"- Expected A4 aspect ratio: {expected_aspect_ratio:.3f}")
            print(
                f"- Aspect ratio difference: {abs(actual_aspect_ratio - expected_aspect_ratio):.3f}"
            )

            # Determine if there's a significant aspect ratio issue
            aspect_tolerance = 0.05  # 5% tolerance
            if abs(actual_aspect_ratio - expected_aspect_ratio) > aspect_tolerance:
                print(f"\n🚨 ASPECT RATIO ISSUE DETECTED:")
                print(
                    f"- The image aspect ratio deviates significantly from A4 landscape"
                )
                print(f"- This will cause stretching when displayed in web interface")
                print(f"- Root cause likely: bbox_inches='tight' in savefig")

                print(f"\n💡 RECOMMENDED FIXES:")
                print(f"1. Remove bbox_inches='tight' to preserve figure proportions")
                print(f"2. Use figure-level sizing instead of content-based cropping")
                print(f"3. Ensure tight_layout is properly configured")
                print(f"4. Verify CSS in web interface preserves aspect ratio")

            else:
                print(f"\n✅ Aspect ratio is within acceptable tolerance")
                print(f"✅ Figure should display properly without stretching")

            # Save for visual inspection
            with open("test_results/aspect_ratio_diagnosis.png", "wb") as f:
                f.write(image_data)
            print(f"\n📏 Saved for inspection: test_results/aspect_ratio_diagnosis.png")

            return abs(actual_aspect_ratio - expected_aspect_ratio) <= aspect_tolerance

        else:
            print("❌ Plot generation failed")
            return False

    except Exception as e:
        print(f"❌ Plot generation error: {e}")
        return False


if __name__ == "__main__":
    success = analyze_figure_aspect_ratio()
    exit(0 if success else 1)
