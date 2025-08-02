#!/usr/bin/env python3
"""
Legend Positioning Diagnosis
============================

This test analyzes the legend positioning issue in the footer.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section import plot_section_from_ags_content
import base64


def analyze_legend_positioning():
    """Analyze the legend positioning problem."""

    print("=== Legend Positioning Diagnosis ===")
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

    print("\n🔍 Analyzing legend positioning with clustered boreholes...")
    print("Boreholes: LFDS2401, LFDS2401A, LFDS2402")

    try:
        result = plot_section_from_ags_content(
            ags_content,
            filter_loca_ids=["LFDS2401", "LFDS2401A", "LFDS2402"],
            return_base64=True,
        )

        if result and len(result) > 100:
            # Save the plot for visual inspection
            plot_bytes = base64.b64decode(result[22:])  # Remove data URL prefix
            with open("test_results/legend_positioning_diagnosis.png", "wb") as f:
                f.write(plot_bytes)

            print("✅ Plot generated and saved for visual inspection")
            print(f"📏 File: test_results/legend_positioning_diagnosis.png")

            # Analyze the positioning logic
            print(f"\n📊 Current Legend Positioning Logic:")
            print(f"- Footer left cell width: 70% (0.7 fraction)")
            print(f"- Legend x position: 0.02 (2% from left edge)")
            print(f"- Legend width: left_frac - 0.04 = 0.7 - 0.04 = 0.66")
            print(f"- Column width: legend_width / 2 = 0.66 / 2 = 0.33")
            print(f"- Items per column: 3")

            print(f"\n🚨 POTENTIAL ISSUES:")
            print(f"1. Column width (0.33) may exceed left cell boundary (0.7)")
            print(f"2. Legend items in column 2 start at: 0.02 + 0.33 = 0.35")
            print(f"3. Legend items with long text may extend beyond 0.7")
            print(f"4. No clipping or bounds checking for legend content")

            print(f"\n💡 PROPOSED FIXES:")
            print(f"1. Reduce column width to ensure both columns fit in left cell")
            print(f"2. Add bounds checking for legend item positioning")
            print(f"3. Adjust text positioning to prevent overflow")
            print(f"4. Consider reducing font size or text length if needed")

            return True

        else:
            print(f"❌ Plot generation failed")
            return False

    except Exception as e:
        print(f"❌ Plot generation error: {e}")
        return False


if __name__ == "__main__":
    success = analyze_legend_positioning()
    exit(0 if success else 1)
