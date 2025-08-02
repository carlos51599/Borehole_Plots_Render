#!/usr/bin/env python3
"""
Debug Column Check - Test what columns are present in parsed AGS data
"""

import sys
import os
from section.parsing import parse_ags_geol_section_from_string

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test AGS content with GEOL_LEG column
test_ags_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
UNITS,,,m,m,m
TYPE,X,X,2DP,2DP,2DP
DATA,BH001,BH,400000.00,300000.00,100.00
DATA,BH002,BH,400020.00,300010.00,105.50

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG,GEOL_DESC
UNITS,,m,m,,,
TYPE,X,2DP,2DP,X,X,X
DATA,BH001,0.00,1.50,MADE GROUND,MG,MADE GROUND brown sandy clay
DATA,BH001,1.50,4.00,LONDON CLAY,LC,LONDON CLAY brown stiff clay
DATA,BH002,0.00,0.80,TOPSOIL,TS,TOPSOIL dark brown organic clay
DATA,BH002,0.80,3.20,LONDON CLAY,LC,LONDON CLAY grey firm clay
"""

print("Testing AGS parsing to check columns...")

try:
    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(test_ags_content)

    print("\n✅ Parsing successful!")
    print(f"📊 GEOL DataFrame shape: {geol_df.shape}")
    print(f"📊 LOCA DataFrame shape: {loca_df.shape}")

    print("\n🔍 GEOL DataFrame columns:")
    for i, col in enumerate(geol_df.columns):
        print(f"  {i}: '{col}'")

    print("\n🔍 LOCA DataFrame columns:")
    for i, col in enumerate(loca_df.columns):
        print(f"  {i}: '{col}'")

    print("\n📋 First few rows of GEOL DataFrame:")
    print(geol_df.head())

    # Check if GEOL_LEG exists
    if "GEOL_LEG" in geol_df.columns:
        print("\n✅ GEOL_LEG column found!")
        print(f"📈 Unique GEOL_LEG values: {geol_df['GEOL_LEG'].unique()}")
    else:
        print("\n❌ GEOL_LEG column NOT found!")

    # Check coordinate merging
    print("\n🔗 Testing coordinate merging...")
    merged = geol_df.merge(loca_df, on="LOCA_ID", how="left")
    print(f"📊 Merged DataFrame shape: {merged.shape}")
    print("🔍 Merged DataFrame columns:")
    for i, col in enumerate(merged.columns):
        print(f"  {i}: '{col}'")

    # Check if GEOL_LEG exists in merged dataframe
    if "GEOL_LEG" in merged.columns:
        print("\n✅ GEOL_LEG column found in merged data!")
        print(f"📈 Unique GEOL_LEG values: {merged['GEOL_LEG'].unique()}")
    else:
        print("\n❌ GEOL_LEG column NOT found in merged data!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
