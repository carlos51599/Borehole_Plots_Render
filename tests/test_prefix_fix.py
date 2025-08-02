#!/usr/bin/env python3
"""
Test the double prefix fix for borehole log display.
Following instructions.md Stage 5: Test implementation fix.
"""

from borehole_log import plot_borehole_log_from_ags_content


def test_prefix_fix():
    """Test that the prefix handling logic works correctly."""
    print("=== Testing Prefix Fix Logic ===")

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
        # Test the borehole log generation
        images = plot_borehole_log_from_ags_content(
            sample_ags_content, "BH001", show_labels=True
        )

        if images and len(images) > 0:
            img_b64 = images[0]
            print(f"Original image data starts with: {img_b64[:50]}")

            # Test the prefix handling logic (from the fixed callbacks)
            if img_b64.startswith("data:image/png;base64,"):
                # Already has prefix, use as-is
                src_url = img_b64
                print("✓ Detected existing prefix - using as-is")
            else:
                # Add prefix if missing
                src_url = f"data:image/png;base64,{img_b64}"
                print("✓ Added missing prefix")

            print(f"Final src_url starts with: {src_url[:50]}")

            # Verify it's a valid data URL
            if src_url.startswith("data:image/png;base64,") and not src_url.startswith(
                "data:image/png;base64,data:image/png;base64,"
            ):
                print("✓ Valid data URL format - no double prefix")
            else:
                print("✗ Invalid data URL format - might have double prefix")

        else:
            print("✗ No images returned")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_prefix_fix()
