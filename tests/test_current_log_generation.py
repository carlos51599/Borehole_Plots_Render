#!/usr/bin/env python3
"""
Test current borehole log generation to confirm issues.
Following instructions.md Stage 2: Test current state.
"""

import sys
import pandas as pd
from borehole_log import plot_borehole_log_from_ags_content


def test_current_log_generation():
    """Test the current borehole log generation that's showing 'image of an image'."""
    print("=== Testing Current Borehole Log Generation ===")

    # Create sample AGS content (simplified for testing)
    sample_ags_content = """
"GROUP","LOCA"
"HEADING","LOCA_ID","LOCA_TYPE","LOCA_STAT","LOCA_NATE","LOCA_NATN","LOCA_GL","LOCA_REM"
"UNIT","","","","m","m","mOD",""
"TYPE","X","PA","PA","2DP","2DP","2DP","X"
"DATA","BH001","CP","","404500.0","206800.0","100.0","Test borehole"

"GROUP","GEOL"
"HEADING","LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC","GEOL_STAT","GEOL_REM"
"UNIT","","m","m","","",""
"TYPE","X","2DP","2DP","X","PA","X"
"DATA","BH001","0.00","1.50","TOPSOIL: Brown silty clay","","Sample taken"
"DATA","BH001","1.50","3.00","CLAY: Grey clay with gravel","","Standard penetration test"
"DATA","BH001","3.00","5.50","SAND: Dense brown sand","","Good recovery"
"DATA","BH001","5.50","8.00","GRAVEL: Angular limestone gravel","","Rock fragments noted"
"""

    try:
        print(f"Testing borehole log generation for BH001...")

        # Call the current implementation
        images = plot_borehole_log_from_ags_content(
            sample_ags_content, "BH001", show_labels=True
        )

        print(f"Current implementation returned: {type(images)}")
        print(f"Number of images: {len(images) if images else 0}")

        if images:
            print(f"First image type: {type(images[0])}")
            print(
                f"First image length: {len(images[0]) if isinstance(images[0], str) else 'Not a string'}"
            )

            # Check if it's a proper base64 image
            if isinstance(images[0], str):
                if images[0].startswith("iVBOR") or images[0].startswith("/9j/"):
                    print("✓ Appears to be valid base64 image data")
                else:
                    print("✗ Does not appear to be valid base64 image data")
                    print(f"First 100 chars: {images[0][:100]}")

        else:
            print("✗ No images returned")

    except Exception as e:
        print(f"✗ Error in current implementation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_current_log_generation()
