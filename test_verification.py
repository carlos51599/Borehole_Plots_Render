#!/usr/bin/env python3
"""
Simple verification test with obvious layer names
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_simple_verification():
    """Test with very simple, obvious layer names"""

    # Create very simple test data
    simple_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.0],
            "Depth_Base": [1.0, 2.0, 3.0],
            "Geology_Code": ["101", "203", "501"],
            "Description": [
                "TOP LAYER (0-1m)",
                "MIDDLE LAYER (1-2m)",
                "BOTTOM LAYER (2-3m)",
            ],
        }
    )

    print("Creating simple verification test...")

    try:
        images = create_professional_borehole_log(
            simple_data,
            "VERIFY",
            title="Verification Test - Check Order",
            figsize=(8.27, 11.69),
            dpi=200,
        )

        if images:
            print(f"Generated {len(images)} page(s)")
            img_data = base64.b64decode(images[0])
            with open("verification_test.png", "wb") as f:
                f.write(img_data)
            print("✅ Saved verification_test.png")
            print("\nIn the description column, you should see:")
            print("1. 'TOP LAYER (0-1m)' at the very top")
            print("2. 'MIDDLE LAYER (1-2m)' in the middle")
            print("3. 'BOTTOM LAYER (2-3m)' at the bottom")

        else:
            print("❌ No images generated")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_simple_verification()
