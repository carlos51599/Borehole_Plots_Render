#!/usr/bin/env python3
"""
Test Complete Section Plotting - Verify the full section plotting pipeline works
"""

import sys
import os
from section.plotting.main import plot_professional_borehole_sections

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test AGS content with GEOL_LEG column
test_ags_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
UNITS,,,m,m,m
TYPE,X,X,2DP,2DP,2DP
DATA,BH001,BH,400000.00,300000.00,100.00
DATA,BH002,BH,400020.00,300010.00,105.50
DATA,BH003,BH,400040.00,300020.00,98.75

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG,GEOL_DESC
UNITS,,m,m,,,
TYPE,X,2DP,2DP,X,X,X
DATA,BH001,0.00,1.50,MADE GROUND,MG,MADE GROUND brown sandy clay
DATA,BH001,1.50,4.00,LONDON CLAY,LC,LONDON CLAY brown stiff clay
DATA,BH001,4.00,8.50,TERRACE GRAVEL,TG,TERRACE GRAVEL dense sandy gravel
DATA,BH002,0.00,0.80,TOPSOIL,TS,TOPSOIL dark brown organic clay
DATA,BH002,0.80,3.20,LONDON CLAY,LC,LONDON CLAY grey firm clay
DATA,BH002,3.20,7.00,TERRACE GRAVEL,TG,TERRACE GRAVEL medium dense gravel
DATA,BH003,0.00,2.10,MADE GROUND,MG,MADE GROUND mixed fill material
DATA,BH003,2.10,5.50,LONDON CLAY,LC,LONDON CLAY brown firm clay
DATA,BH003,5.50,9.20,CHALK,CH,CHALK white weathered chalk
"""

print("Testing complete section plotting pipeline...")

try:
    # Test the main plotting function
    ags_data = [("test_section.ags", test_ags_content)]

    print("🚀 Calling plot_professional_borehole_sections...")
    result = plot_professional_borehole_sections(
        ags_data=ags_data, section_line=None, show_labels=True, output_high_res=False
    )

    print("✅ Function completed successfully!")
    print(f"📊 Result type: {type(result)}")

    if isinstance(result, tuple) and len(result) == 3:
        base64_img, svg_content, pdf_path = result
        if isinstance(base64_img, str) and base64_img.startswith("data:image"):
            print("✅ SUCCESS! Base64 image generated successfully")
            print(f"📏 Base64 length: {len(base64_img)} characters")
        elif "Error" in str(base64_img) or "failed" in str(base64_img):
            print(f"❌ Error in plotting: {base64_img}")
        else:
            print(f"❓ Unexpected result: {base64_img}")
    else:
        print(f"❓ Unexpected result format: {result}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
