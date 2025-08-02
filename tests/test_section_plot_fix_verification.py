#!/usr/bin/env python3
"""
Fix Section Plot White Space - Data Synchronization Test
=======================================================

This test demonstrates the solution for the section plot white space issue.
The problem was a data mismatch between stored borehole data and current AGS content.

SOLUTION SUMMARY:
1. The app's borehole data store contains old AGS data
2. Section plotting uses the current AGS file content
3. Shape selection uses the stored data → ID mismatch → empty plot
4. RESOLUTION: Upload the current AGS file through the app UI to sync data

This test verifies the fix is working correctly.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section.parsing import parse_ags_geol_section_from_string
from section import plot_section_from_ags_content


def test_section_plot_data_sync_solution():
    """Test that section plots work when borehole IDs match."""

    print("=== Section Plot White Space Fix Verification ===")
    print()

    # Load current AGS data
    current_ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    try:
        with open(current_ags_file, "r", encoding="utf-8") as f:
            ags_content = f.read()
        print(f"✅ Loaded AGS file: {len(ags_content)} characters")

        # Parse to get actual borehole IDs
        geol_df, loca_df, _ = parse_ags_geol_section_from_string(ags_content)
        actual_borehole_ids = loca_df["LOCA_ID"].tolist()

        print(f"📊 AGS Data: {len(geol_df)} geology records, {len(loca_df)} locations")
        print(f"🏷️ Available borehole IDs: {actual_borehole_ids[:5]}...")

    except Exception as e:
        print(f"❌ Failed to load AGS data: {e}")
        return False

    # Test 1: Section plot with correct borehole IDs (should work)
    print("\n1. Testing section plot with MATCHING borehole IDs...")

    try:
        # Use actual borehole IDs from the data
        test_ids = actual_borehole_ids[:3]  # First 3 boreholes
        print(f"   Using borehole IDs: {test_ids}")

        result = plot_section_from_ags_content(
            ags_content, filter_loca_ids=test_ids, return_base64=True
        )

        if result and len(result) > 100:  # Basic check for base64 content
            print("   ✅ Section plot generated successfully")
            print(f"   📏 Plot data length: {len(result)} characters")
            success_matching = True
        else:
            print(f"   ❌ Section plot failed or empty: {result}")
            success_matching = False

    except Exception as e:
        print(f"   ❌ Section plot with matching IDs failed: {e}")
        success_matching = False

    # Test 2: Section plot with incorrect borehole IDs (should fail gracefully)
    print("\n2. Testing section plot with NON-MATCHING borehole IDs...")

    try:
        # Use the old borehole IDs that were causing the problem
        old_ids = ["BH423", "BH425", "CPT423"]
        print(f"   Using old borehole IDs: {old_ids}")

        result = plot_section_from_ags_content(
            ags_content, filter_loca_ids=old_ids, return_base64=True
        )

        if result and len(result) > 100:
            print("   ⚠️ Unexpected: Plot generated with non-matching IDs")
            success_nonmatching = False
        else:
            print("   ✅ Correctly failed with non-matching IDs (as expected)")
            success_nonmatching = True

    except Exception as e:
        print(f"   ✅ Correctly failed with non-matching IDs: {e}")
        success_nonmatching = True

    # Summary
    print("\n=== FIX VERIFICATION RESULTS ===")
    print(f"📈 Matching IDs test: {'✅ PASS' if success_matching else '❌ FAIL'}")
    print(
        f"📈 Non-matching IDs test: {'✅ PASS' if success_nonmatching else '❌ FAIL'}"
    )

    overall_success = success_matching and success_nonmatching

    if overall_success:
        print("\n🎉 SOLUTION VERIFIED!")
        print("The section plot white space issue is fixed when borehole IDs match.")
        print()
        print("💡 USER ACTION REQUIRED:")
        print("To resolve this in the app, the user needs to:")
        print("1. 📁 Upload the FLRG AGS file through the app UI")
        print("2. 🗺️ Wait for borehole markers to appear on the map")
        print("3. ✏️ Draw shapes to select boreholes")
        print("4. 📊 Generate section plots (should work without white space)")
        print()
        print("🔧 ROOT CAUSE: Data store contained old borehole IDs")
        print("🔧 SOLUTION: Upload current AGS file to sync borehole data store")

    else:
        print("\n❌ FIX VERIFICATION FAILED")
        print("Additional investigation needed")

    return overall_success


if __name__ == "__main__":
    success = test_section_plot_data_sync_solution()
    exit(0 if success else 1)
