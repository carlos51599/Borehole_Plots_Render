#!/usr/bin/env python3
"""
Test script with numbered layers to verify correct stacking order
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_numbered_layers():
    """Test with simple numbered layers to verify stacking order"""

    # Create simple test data with numbered layers
    numbered_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            "Depth_Base": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "Geology_Code": ["101", "203", "501", "202", "801", "101"],
            "Description": [
                "Layer 1 - Should be at the top",
                "Layer 2 - Should be second from top",
                "Layer 3 - Should be third from top",
                "Layer 4 - Should be fourth from top",
                "Layer 5 - Should be fifth from top",
                "Layer 6 - Should be at the bottom",
            ],
        }
    )

    print("Creating borehole log with numbered layers to test stacking order...")

    try:
        images = create_professional_borehole_log(
            numbered_data,
            "TEST_ORDER",
            title="Test Layer Stacking Order",
            figsize=(8.27, 11.69),
            dpi=200,  # Higher DPI for better text clarity
        )

        if images:
            print(f"Successfully generated {len(images)} page(s)")

            # Save the first page to file for inspection
            if len(images) > 0:
                img_data = base64.b64decode(images[0])
                with open("test_layer_order.png", "wb") as f:
                    f.write(img_data)
                print("✅ Saved test_layer_order.png")
                print("\nPlease check the PNG file to verify:")
                print("- Layer 1 should be at the TOP of the description column")
                print("- Layer 2 should be below Layer 1")
                print("- Layer 3 should be below Layer 2")
                print("- And so on... with Layer 6 at the BOTTOM")

        else:
            print("❌ No images generated - check for errors")

    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_numbered_layers()
