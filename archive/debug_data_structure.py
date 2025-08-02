#!/usr/bin/env python3
"""
Debug script to examine data structure and fix GEOL_LEG issue
"""

import pandas as pd
from section.parsing import parse_ags_geol_section_from_string


def debug_data_structure():
    """Debug the data structure to understand available columns."""
    print("🔍 Debugging Data Structure")
    print("=" * 50)

    # Test AGS content
    test_ags = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_GL,LOCA_NATE,LOCA_NATN
UNITS,<blank>,<blank>,m,m,m
TYPE,ID,X,2DP,2DP,2DP
DATA,BH01,RC,100.00,451000,290000

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_DESC
UNITS,<blank>,m,m,<blank>
TYPE,ID,2DP,2DP,X
DATA,BH01,0.00,2.50,TOPSOIL: Dark brown sandy clay
DATA,BH01,2.50,8.00,CLAY: Firm brown clay"""

    try:
        # Parse the AGS data
        geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(test_ags)

        print("\n📊 GEOL DataFrame:")
        print(f"Shape: {geol_df.shape}")
        print(f"Columns: {list(geol_df.columns)}")
        print("\nFirst few rows:")
        print(geol_df.head())

        print("\n📍 LOCA DataFrame:")
        print(f"Shape: {loca_df.shape}")
        print(f"Columns: {list(loca_df.columns)}")
        print("\nFirst few rows:")
        print(loca_df.head())

        print("\n📝 ABBR DataFrame:")
        if abbr_df is not None:
            print(f"Shape: {abbr_df.shape}")
            print(f"Columns: {list(abbr_df.columns)}")
        else:
            print("ABBR DataFrame is None")

        # Now merge them to see the final structure
        from section.plotting.coordinates import prepare_coordinate_data

        coord_data = prepare_coordinate_data(geol_df, loca_df, None)
        if coord_data:
            merged_df = coord_data["merged_df"]
            print("\n🔗 MERGED DataFrame:")
            print(f"Shape: {merged_df.shape}")
            print(f"Columns: {list(merged_df.columns)}")
            print("\nFirst few rows:")
            print(merged_df.head())

            # Check for GEOL_LEG column
            if "GEOL_LEG" in merged_df.columns:
                print("✅ GEOL_LEG column found")
            else:
                print("❌ GEOL_LEG column NOT found")
                print("   Available columns that might be used instead:")
                for col in merged_df.columns:
                    if "GEOL" in col:
                        print(f"   - {col}")

    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_data_structure()
