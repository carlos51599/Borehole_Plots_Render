#!/usr/bin/env python3
"""
Test the professional borehole log implementation.
Following instructions.md Stage 5: Test implementation.
"""

from borehole_log import plot_borehole_log_from_ags_content


def test_professional_implementation():
    """Test the new professional borehole log implementation."""
    print("=== Testing Professional Implementation ===")

    sample_ags_content = """
"GROUP","LOCA"
"HEADING","LOCA_ID","LOCA_TYPE","LOCA_STAT","LOCA_NATE","LOCA_NATN","LOCA_GL","LOCA_REM"
"UNIT","","","","m","m","mOD",""
"TYPE","X","PA","PA","2DP","2DP","2DP","X"
"DATA","BH001","CP","","404500.0","206800.0","100.0","Test borehole"

"GROUP","GEOL"
"HEADING","LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC","GEOL_LEG","GEOL_STAT","GEOL_REM"
"UNIT","","m","m","","","",""
"TYPE","X","2DP","2DP","X","X","PA","X"
"DATA","BH001","0.00","1.50","TOPSOIL: Brown silty clay with organic matter","101","","Sample taken"
"DATA","BH001","1.50","3.00","CLAY: Grey clay with gravel fragments","203","","Standard penetration test"
"DATA","BH001","3.00","5.50","SAND: Dense brown sand with fine particles","501","","Good recovery"
"DATA","BH001","5.50","8.00","GRAVEL: Angular limestone gravel with cobbles","801","","Rock fragments noted"
"""

    try:
        print("Testing professional borehole log generation for BH001...")

        # Call the new professional implementation
        images = plot_borehole_log_from_ags_content(
            sample_ags_content, "BH001", show_labels=True
        )

        print(f"Professional implementation returned: {type(images)}")
        print(f"Number of images: {len(images) if images else 0}")

        if images:
            for i, img in enumerate(images):
                print(f"Image {i+1}:")
                print(f"  Type: {type(img)}")
                print(
                    f"  Length: {len(img) if isinstance(img, str) else 'Not a string'}"
                )

                # Check if it's a proper data URL
                if isinstance(img, str):
                    if img.startswith("data:image/png;base64,"):
                        print("  ✓ Valid data URL format")

                        # Check if it has double prefix
                        if img.count("data:image/png;base64,") > 1:
                            print("  ✗ Has double prefix issue")
                        else:
                            print("  ✓ No double prefix")

                        # Test base64 validity
                        try:
                            import base64

                            base64_part = img.split(",", 1)[1]
                            decoded = base64.b64decode(base64_part)
                            if decoded.startswith(b"\x89PNG"):
                                print("  ✓ Valid PNG image")
                            else:
                                print("  ✗ Not a valid PNG")
                        except Exception as e:
                            print(f"  ✗ Base64 decode error: {e}")
                    else:
                        print("  ✗ Not a valid data URL")
                        print(f"  First 100 chars: {img[:100]}")

        else:
            print("✗ No images returned from professional implementation")

    except Exception as e:
        print(f"✗ Error in professional implementation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_professional_implementation()
