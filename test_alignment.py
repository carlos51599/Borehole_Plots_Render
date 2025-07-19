#!/usr/bin/env python3
"""
Test script to verify text box alignment with geological layers
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_layer_alignment():
    """Test text box alignment with geological layer boundaries"""

    # Create test data with varying layer thicknesses and description lengths
    alignment_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.5, 4.0, 6.0],
            "Depth_Base": [1.0, 2.5, 4.0, 6.0, 8.0],
            "Geology_Code": ["101", "203", "501", "202", "801"],
            "Description": [
                "Short desc",  # Should fit within layer boundaries
                "This is a longer description that should fit within the medium-thick layer boundaries",  # Should fit
                "Short",  # Should fit in thin layer
                "This is a very long description that will probably extend beyond the layer boundaries and push down into the space below, demonstrating the text box extension behavior",  # Should extend
                "Final layer description of moderate length",  # Should align with layer
            ],
        }
    )

    print("Creating test to verify text box alignment with geological layers...")

    try:
        images = create_professional_borehole_log(
            alignment_data,
            "ALIGN_TEST",
            title="Text Box Alignment Test",
            figsize=(8.27, 11.69),
            dpi=200,
        )

        if images:
            print(f"Generated {len(images)} page(s)")
            img_data = base64.b64decode(images[0])
            with open("test_alignment.png", "wb") as f:
                f.write(img_data)
            print("✅ Saved test_alignment.png")
            print("\nIn the description column, verify:")
            print(
                "1. Text boxes align with their corresponding legend layer boundaries"
            )
            print("2. Short descriptions stay within their layer boundaries")
            print("3. Long descriptions extend below their layer if needed")
            print("4. No gaps between consecutive text boxes")
            print("5. Text boxes don't overlap")

        else:
            print("❌ No images generated")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_layer_alignment()
