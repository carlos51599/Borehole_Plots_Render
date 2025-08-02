#!/usr/bin/env python3
"""
Final verification test: Archive-style A4 aspect ratio fix with real section data
"""

import sys
import os

sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
from section.utils import convert_figure_to_base64
from archive.section_plot_professional_original import plot_section_from_ags_content
import base64
import io
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)


def test_final_aspect_ratio_fix():
    """Test the final fix with real AGS data to ensure A4 landscape proportions"""

    print("🔧 FINAL TEST: Archive-style A4 aspect ratio fix")
    print("=" * 60)

    # Load real AGS test data
    ags_file_path = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    if not os.path.exists(ags_file_path):
        print(f"❌ Test file not found: {ags_file_path}")
        return False

    print(f"📂 Loading AGS data: {ags_file_path}")

    try:
        with open(ags_file_path, "r", encoding="utf-8", errors="ignore") as f:
            ags_content = f.read()

        print(f"✅ Loaded {len(ags_content)} characters of AGS data")

        # Generate section plot using archive method
        print("🎯 Generating section plot...")

        result = plot_section_from_ags_content(
            ags_content=ags_content,
            filter_loca_ids=None,  # Use all boreholes
            section_line=None,
            show_labels=True,
            vertical_exaggeration=1.0,
            save_high_res=False,
            output_filename=None,
            return_base64=True,
        )

        if not result or not result:
            print("❌ Failed to generate section plot")
            return False

        base64_data = result
        print("✅ Section plot generated successfully")

        # Verify aspect ratio
        print("📏 Checking aspect ratio...")

        # Clean base64 data
        if base64_data.startswith("data:image/png;base64,"):
            base64_clean = base64_data.replace("data:image/png;base64,", "")
        else:
            base64_clean = base64_data

        # Decode and check dimensions
        image_bytes = base64.b64decode(base64_clean)
        image = Image.open(io.BytesIO(image_bytes))

        width, height = image.size
        aspect_ratio = width / height
        expected_ratio = 11.69 / 8.27  # A4 landscape

        print(f"📐 Image dimensions: {width} x {height}")
        print(f"📐 Aspect ratio: {aspect_ratio:.6f}")
        print(f"📐 Expected A4 landscape: {expected_ratio:.6f}")
        print(f"📐 Difference: {abs(aspect_ratio - expected_ratio):.6f}")

        # Verify aspect ratio is correct
        if abs(aspect_ratio - expected_ratio) < 0.01:
            print("✅ PASS: Aspect ratio matches A4 landscape!")
            print("🎉 Figure stretching issue RESOLVED!")
            return True
        else:
            print("❌ FAIL: Aspect ratio still incorrect")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_final_aspect_ratio_fix()

    if success:
        print("\n" + "=" * 60)
        print("🎊 SUCCESS: Archive-style fix achieves perfect A4 proportions!")
        print("✅ Section plots will now display with correct aspect ratio")
        print("✅ No more stretching in web browser display")
        print("✅ Professional A4 landscape standard maintained")
    else:
        print("\n" + "=" * 60)
        print("💥 FAILURE: Aspect ratio issue persists")
        print("❌ Additional investigation required")

    plt.close("all")
