#!/usr/bin/env python3
"""
Test script to verify cascading text box push-down behavior.
This test specifically checks if a very long first text box properly pushes
all subsequent text boxes down in a cascading manner.
"""

import pandas as pd
from borehole_log_professional import create_professional_borehole_log


def test_cascading_pushdown():
    """Test cascading push-down behavior with a very long first description."""

    print("Creating test to verify cascading text box push-down behavior...")

    # Create test data with a very long first description that will cascade down
    test_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.0, 3.0, 4.0],
            "Depth_Base": [1.0, 2.0, 3.0, 4.0, 5.0],
            "Geology_Code": ["101", "102", "104", "202", "203"],
            "Description": [
                (
                    "EXTREMELY LONG DESCRIPTION: This is a very detailed geological description that "
                    "contains multiple sentences and should extend well beyond the boundaries of its "
                    "geological layer. It includes information about soil composition, structure, color "
                    "variations, moisture content, compactness, and various other geological characteristics "
                    "that would typically be found in a professional borehole log. This description is "
                    "intentionally verbose to test the cascading push-down behavior of text boxes."
                ),
                "Medium description that normally fits within layer boundaries",
                "SHORT",
                "Another medium length description with some geological details",
                "FINAL",
            ],
        }
    )

    # Generate the professional borehole log
    pages_data = create_professional_borehole_log(test_data, "CASCADE_TEST")
    print(f"Generated {len(pages_data)} page(s)")

    # Save the test image
    filename = "test_cascading.png"
    if pages_data:
        import base64

        # Decode base64 string to bytes
        image_data = base64.b64decode(pages_data[0])
        with open(filename, "wb") as f:
            f.write(image_data)
        print(f"✅ Saved {filename}")
    else:
        print("❌ Failed to generate test image")

    print("\nIn the description column, verify:")
    print("1. First text box (very long) extends far below its layer boundary")
    print("2. Second text box is pushed down below the first (no overlap)")
    print("3. Third text box is pushed down below the second (cascading effect)")
    print("4. All subsequent text boxes cascade down properly")
    print("5. No gaps between consecutive text boxes")
    print("6. No overlapping text boxes")


if __name__ == "__main__":
    test_cascading_pushdown()
