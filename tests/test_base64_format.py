#!/usr/bin/env python3
"""
Test to understand the base64 format issue.
Following instructions.md Stage 2: Test current state.
"""

from borehole_log import plot_borehole_log_from_ags_content


def test_base64_format():
    """Test the base64 format returned by current implementation."""
    print("=== Testing Base64 Format ===")

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
        images = plot_borehole_log_from_ags_content(
            sample_ags_content, "BH001", show_labels=True
        )

        if images and len(images) > 0:
            img_str = images[0]
            print(f"Full image string length: {len(img_str)}")
            print(f"First 200 characters: {img_str[:200]}")

            # Check if it has the data URL prefix
            if img_str.startswith("data:image/png;base64,"):
                print("✓ Has data URL prefix")
                # Extract just the base64 part
                base64_part = img_str.split(",", 1)[1] if "," in img_str else img_str
                print(f"Base64 part length: {len(base64_part)}")
                print(f"Base64 starts with: {base64_part[:50]}")

                # Test if it's valid base64
                import base64

                try:
                    decoded = base64.b64decode(base64_part)
                    print(f"✓ Valid base64 - decoded length: {len(decoded)} bytes")

                    # Check PNG header
                    if decoded.startswith(b"\x89PNG"):
                        print("✓ Valid PNG image")
                    else:
                        print("✗ Not a valid PNG image")

                except Exception as e:
                    print(f"✗ Invalid base64: {e}")

            else:
                print("✗ No data URL prefix")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_base64_format()
