#!/usr/bin/env python3
"""
Test script for the new text box implementation in borehole_log_professional.py
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_text_box_implementation():
    """Test the new text box implementation with sample data"""

    # Create sample data with some long descriptions to test wrapping
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5, 8.0],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0, 12.0],
            "Geology_Code": ["101", "203", "501", "202", "801"],
            "Description": [
                "Soft brown clay with occasional organic matter, some small roots and debris",
                "Medium dense fine to coarse sand with occasional gravel particles and shells",
                "Dense angular gravel with cobbles, very hard drilling, some limestone fragments",
                "Stiff grey clay with limestone fragments, becoming softer with depth, some oxidation staining",
                "Weathered limestone bedrock, becoming harder with depth, some fracturing visible",
            ],
        }
    )

    print("Creating professional borehole log with text boxes...")

    try:
        # Create professional borehole log
        images = create_professional_borehole_log(
            sample_data,
            "TEST_BH001",
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Text Box Implementation",
            figsize=(8.27, 11.69),
            dpi=150,  # Lower DPI for faster testing
        )

        if images:
            print(f"Successfully generated {len(images)} page(s)")

            # Save the first page to file for inspection
            if len(images) > 0:
                # Decode base64 and save to PNG file
                img_data = base64.b64decode(images[0])
                with open("test_text_boxes_output.png", "wb") as f:
                    f.write(img_data)
                print("Saved test output to test_text_boxes_output.png")

        else:
            print("No images generated - check for errors")

    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_text_box_implementation()
