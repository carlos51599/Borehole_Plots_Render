#!/usr/bin/env python3
"""
Debug script to test for offset_layout issue
"""

import traceback
import sys
import logging

# Set up logging to see detailed error messages
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    print("Testing import of borehole_log_professional...")
    from borehole_log_professional import plot_borehole_log_from_ags_content

    print("✓ Import successful")

    # Test a simple call
    print("Testing plot_borehole_log_from_ags_content with minimal data...")

    # Simple test data
    test_ags_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_GL,LOCA_NATE,LOCA_NATN
UNITS,<blank>,<blank>,m,m,m
TYPE,ID,X,2DP,2DP,2DP
DATA,BH01,RC,100.00,451000,290000

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
UNITS,<blank>,m,m,<blank>,<blank>
TYPE,ID,2DP,2DP,X,X
DATA,BH01,0.00,1.50,101,TOPSOIL
DATA,BH01,1.50,3.00,203,SAND
DATA,BH01,3.00,5.00,501,GRAVEL"""

    print("Calling plot_borehole_log_from_ags_content...")
    result = plot_borehole_log_from_ags_content(
        test_ags_content, "BH01", show_labels=True, fig_height=11.69, fig_width=8.27
    )

    print(f"✓ Function returned: {type(result)}")
    if result:
        print(
            f"  Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}"
        )

except Exception as e:
    print(f"✗ Error occurred: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

    # Check if the error mentions offset_layout
    if "offset_layout" in str(e):
        print("\n⚠️  ERROR CONTAINS 'offset_layout' REFERENCE!")
        print("This confirms the issue is in the borehole_log_professional module")
    else:
        print("\n🤔 Error does not contain 'offset_layout' reference")

print("\nDebug test completed.")
