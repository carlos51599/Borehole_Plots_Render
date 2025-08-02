#!/usr/bin/env python3
"""
Debug script to compare parsing between archive and modular implementations.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test AGS content with proper numeric GEOL_LEG codes
test_ags_content = """GROUP,PROJ
HEADING,PROJ_ID,PROJ_NAME,PROJ_LOC,PROJ_CLNT,PROJ_CONT,PROJ_ENG
UNITS,,,,,, 
TYPE,ID,X,X,X,X,X
DATA,12345,Test Section,Test Site,Test Client,Test Contractor,Test Engineer

GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
UNITS,,,m,m,m
TYPE,X,X,2DP,2DP,2DP
DATA,BH001,BH,400000.00,300000.00,100.00
DATA,BH002,BH,400020.00,300010.00,105.50

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG,GEOL_DESC
UNITS,,m,m,,,
TYPE,X,2DP,2DP,X,X,X
DATA,BH001,0.00,1.50,TOPSOIL,101,TOPSOIL dark brown organic
DATA,BH001,1.50,4.00,SANDY CLAY,203,SANDY CLAY brown stiff
DATA,BH002,0.00,0.80,TOPSOIL,101,TOPSOIL dark brown organic
DATA,BH002,0.80,3.20,SANDY CLAY,203,SANDY CLAY grey firm
"""

print("🔍 Debugging Parser Comparison...")
print("=" * 50)

# Test archive implementation
try:
    from archive.section_plot_professional_original import (
        parse_ags_geol_section_from_string as archive_parse,
    )

    print("\n📁 Archive Implementation:")
    geol_df_archive, loca_df_archive, abbr_df_archive = archive_parse(test_ags_content)
    print(
        f"   GEOL DataFrame: {len(geol_df_archive)} rows, columns: {list(geol_df_archive.columns)}"
    )
    print(
        f"   LOCA DataFrame: {len(loca_df_archive)} rows, columns: {list(loca_df_archive.columns)}"
    )
    print(
        f"   GEOL_LEG values: {geol_df_archive['GEOL_LEG'].unique() if 'GEOL_LEG' in geol_df_archive.columns else 'Not found'}"
    )

except Exception as e:
    print(f"❌ Archive parser error: {e}")

# Test modular implementation
try:
    from section.parsing import parse_ags_geol_section_from_string as modular_parse

    print("\n🔧 Modular Implementation:")
    geol_df_modular, loca_df_modular, abbr_df_modular = modular_parse(test_ags_content)
    print(
        f"   GEOL DataFrame: {len(geol_df_modular)} rows, columns: {list(geol_df_modular.columns)}"
    )
    print(
        f"   LOCA DataFrame: {len(loca_df_modular)} rows, columns: {list(loca_df_modular.columns)}"
    )
    print(
        f"   GEOL_LEG values: {geol_df_modular['GEOL_LEG'].unique() if 'GEOL_LEG' in geol_df_modular.columns else 'Not found'}"
    )

except Exception as e:
    print(f"❌ Modular parser error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 50)
print("🎯 Key Points:")
print("- Both parsers should handle numeric GEOL_LEG codes (101, 203, etc.)")
print("- Archive implementation is the reference standard")
print("- Modular parser should match archive functionality")
