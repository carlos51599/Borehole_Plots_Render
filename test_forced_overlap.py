#!/usr/bin/env python3
"""
Test script with forced overlap to debug cascading behavior.
"""

import pandas as pd
from borehole_log_professional import create_professional_borehole_log


def test_forced_overlap():
    """Test with forced overlap to verify push-down behavior."""

    print("Creating test with forced overlap...")

    # Create test data where multiple descriptions will clearly overlap
    test_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 0.5, 1.0, 1.5, 2.0],  # Tight spacing
            "Depth_Base": [0.5, 1.0, 1.5, 2.0, 2.5],
            "Geology_Code": ["101", "102", "104", "202", "203"],
            "Description": [
                # Each description is long enough to require multiple lines
                "VERY LONG DESCRIPTION ONE: This geological layer contains significant clay content with high plasticity and organic material that extends through multiple depth intervals and requires detailed documentation for engineering analysis.",
                "VERY LONG DESCRIPTION TWO: This sandy clay layer exhibits intermediate plasticity with occasional gravel inclusions and moderate permeability characteristics that need comprehensive evaluation.",
                "VERY LONG DESCRIPTION THREE: Dense silty sand with excellent bearing capacity and low compressibility making it suitable for foundation support applications.",
                "VERY LONG DESCRIPTION FOUR: Stiff clay with high bearing capacity and low permeability suitable for construction applications.",
                "VERY LONG DESCRIPTION FIVE: Final layer with mixed composition and variable engineering properties.",
            ],
        }
    )

    # Generate the professional borehole log
    pages_data = create_professional_borehole_log(test_data, "OVERLAP_TEST")
    print(f"Generated {len(pages_data)} page(s)")

    # Save the test image
    filename = "test_forced_overlap.png"
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
    print("1. All text boxes are pushed down to avoid overlaps")
    print("2. No text boxes overlap")
    print("3. Text boxes cascade down properly")


if __name__ == "__main__":
    test_forced_overlap()
