#!/usr/bin/env python3
"""
Test Data Mismatch Analysis - Section Plot White Space
====================================================

This test investigates the data mismatch between stored borehole data
and current AGS file that causes section plots to show empty white space.

Expected findings:
1. Stored borehole data contains old borehole IDs (e.g., BH423, BH425)
2. Current AGS file contains different borehole IDs (e.g., LFDS2401, LFDS2402)
3. Shape selection uses stored data, section plotting uses current AGS
4. Result: No matching boreholes → "No data available after filtering"
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
from section.parsing import parse_ags_geol_section_from_string


def analyze_data_mismatch():
    """Analyze the data mismatch between stored and current AGS data."""

    print("=== Data Mismatch Analysis for Section Plot White Space ===")

    # Step 1: Load current AGS data
    print("\n1. Loading current AGS file data...")
    current_ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    try:
        with open(current_ags_file, "r", encoding="utf-8") as f:
            current_ags_content = f.read()
        print(f"✅ Loaded current AGS file: {len(current_ags_content)} characters")

        # Parse current AGS data
        geol_df, loca_df, _ = parse_ags_geol_section_from_string(current_ags_content)
        current_borehole_ids = loca_df["LOCA_ID"].tolist()

        print(f"📊 Current AGS data:")
        print(f"  - Geology records: {len(geol_df)}")
        print(f"  - Location records: {len(loca_df)}")
        print(f"  - Unique boreholes: {len(current_borehole_ids)}")
        print(f"🏷️ Current borehole IDs (first 10): {current_borehole_ids[:10]}")

    except Exception as e:
        print(f"❌ Failed to load current AGS data: {e}")
        return

    # Step 2: Identify typical stored borehole data pattern
    print("\n2. Analyzing debug log patterns...")

    # From debug logs, we know shape selection returns these IDs:
    debug_log_ids = [
        "BH423",
        "BH423A",
        "BH425",
        "BH425A",
        "BH543",
        "BH543A",
        "CPT423",
        "CPT423A",
        "CPT425",
    ]

    print(f"🔍 Debug log borehole IDs: {debug_log_ids}")

    # Step 3: Check for overlap
    print("\n3. Checking for borehole ID overlap...")

    current_set = set(current_borehole_ids)
    debug_set = set(debug_log_ids)
    overlap = current_set.intersection(debug_set)

    print(f"📈 Current AGS IDs: {len(current_set)} unique")
    print(f"📈 Debug log IDs: {len(debug_set)} unique")
    print(f"🔗 Overlap: {len(overlap)} IDs")

    if overlap:
        print(f"✅ Matching IDs: {list(overlap)}")
    else:
        print("❌ NO MATCHING IDs - This confirms the data mismatch!")

    # Step 4: Data structure comparison
    print("\n4. Data structure analysis...")

    print("🎯 Current AGS naming pattern:")
    id_patterns = {}
    for bid in current_borehole_ids[:10]:
        if bid.startswith("LFDS"):
            id_patterns["LFDS"] = id_patterns.get("LFDS", 0) + 1
        elif bid.startswith("BH"):
            id_patterns["BH"] = id_patterns.get("BH", 0) + 1
        elif bid.startswith("CPT"):
            id_patterns["CPT"] = id_patterns.get("CPT", 0) + 1
        else:
            prefix = bid[:3] if len(bid) >= 3 else bid
            id_patterns[prefix] = id_patterns.get(prefix, 0) + 1

    for pattern, count in id_patterns.items():
        print(f"  - {pattern}*: {count} boreholes")

    print("🎯 Debug log naming pattern:")
    debug_patterns = {}
    for bid in debug_log_ids:
        if bid.startswith("BH"):
            debug_patterns["BH"] = debug_patterns.get("BH", 0) + 1
        elif bid.startswith("CPT"):
            debug_patterns["CPT"] = debug_patterns.get("CPT", 0) + 1
        else:
            prefix = bid[:3] if len(bid) >= 3 else bid
            debug_patterns[prefix] = debug_patterns.get(prefix, 0) + 1

    for pattern, count in debug_patterns.items():
        print(f"  - {pattern}*: {count} boreholes")

    # Step 5: Diagnostic summary
    print("\n5. Root Cause Analysis Summary")
    print("=" * 50)

    if not overlap:
        print("🔍 ROOT CAUSE IDENTIFIED:")
        print("  ❌ Data mismatch between stored borehole data and current AGS file")
        print("  ❌ Shape selection uses stored data with old borehole IDs")
        print("  ❌ Section plotting uses current AGS data with new borehole IDs")
        print("  ❌ No matching IDs → filter returns empty → white space in plot")
        print()
        print("💡 SOLUTION APPROACH:")
        print("  ✅ Ensure stored borehole data syncs with current AGS file")
        print("  ✅ Check data loading/storage pipeline for consistency")
        print("  ✅ Verify borehole data store updates when new AGS uploaded")
    else:
        print("🤔 Partial overlap detected - need deeper investigation")

    return {
        "current_ids": current_borehole_ids,
        "debug_ids": debug_log_ids,
        "overlap": list(overlap),
        "mismatch_confirmed": len(overlap) == 0,
    }


if __name__ == "__main__":
    result = analyze_data_mismatch()

    if result["mismatch_confirmed"]:
        print("\n🎯 Next Steps:")
        print("1. Investigate borehole data store update mechanism")
        print("2. Check AGS file upload workflow")
        print("3. Ensure shape selection uses current, not cached data")
        print("4. Test data synchronization after AGS upload")
