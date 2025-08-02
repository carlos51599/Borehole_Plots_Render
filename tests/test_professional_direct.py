#!/usr/bin/env python3
"""
Test the professional borehole log implementation directly.
Following instructions.md Stage 5: Test implementation.
"""

from borehole_log_professional import create_professional_borehole_log_multi_page
import pandas as pd


def test_professional_direct():
    """Test the professional implementation directly."""
    print("=== Testing Professional Implementation Directly ===")

    # Create sample geological data directly
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0],
            "Description": [
                "TOPSOIL: Brown silty clay with organic matter",
                "CLAY: Grey clay with gravel fragments",
                "SAND: Dense brown sand with fine particles",
                "GRAVEL: Angular limestone gravel with cobbles",
            ],
            "Geology_Code": ["101", "203", "501", "801"],
        }
    )

    try:
        print("Testing direct professional borehole log generation...")

        # Call the professional implementation directly
        images = create_professional_borehole_log_multi_page(
            borehole_data=sample_data,
            borehole_id="BH001",
            ground_level=100.0,
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Professional Borehole Log",
            figsize=(8.27, 11.69),
            dpi=300,
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

                # Check if it's base64
                if isinstance(img, str):
                    # Test base64 validity
                    try:
                        import base64

                        decoded = base64.b64decode(img)
                        if decoded.startswith(b"\x89PNG"):
                            print("  ✓ Valid PNG image (base64 encoded)")
                        else:
                            print("  ✗ Not a valid PNG")
                    except Exception as e:
                        print(f"  ✗ Base64 decode error: {e}")

                    print(f"  First 50 chars: {img[:50]}")

        else:
            print("✗ No images returned from professional implementation")

    except Exception as e:
        print(f"✗ Error in professional implementation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_professional_direct()
