#!/usr/bin/env python3
"""
Debug Geology Mappings - Test the create_geology_mappings function specifically
"""

import sys
import os
from section.parsing import parse_ags_geol_section_from_string
from section.plotting.geology import create_geology_mappings

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

print("Testing create_geology_mappings function...")

try:
    # Parse the AGS data
    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(test_ags_content)

    # Merge the dataframes
    merged = geol_df.merge(loca_df, on="LOCA_ID", how="left")
    print(f"✅ Data parsed and merged. Shape: {merged.shape}")
    print(f"📊 Columns: {list(merged.columns)}")
    print(f"🔍 Has GEOL_LEG: {'GEOL_LEG' in merged.columns}")

    if "GEOL_LEG" in merged.columns:
        print(f"📈 GEOL_LEG values: {merged['GEOL_LEG'].unique()}")

    # Now test the geology mappings function
    print("\n🎨 Testing create_geology_mappings...")
    color_map, hatch_map, leg_label_map = create_geology_mappings(merged, abbr_df)

    print("✅ Geology mappings created successfully!")
    print(f"🎨 Color map: {color_map}")
    print(f"📊 Hatch map: {hatch_map}")
    print(f"🏷️  Label map: {leg_label_map}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
