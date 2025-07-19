#!/usr/bin/env python3
"""
Test script to verify the updated borehole_log_professional functionality.
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log_multi_page

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_multi_page_functionality():
    """Test the multi-page borehole log functionality"""
    print("Testing multi-page borehole log functionality...")

    # Create test data (similar to dummy data)
    test_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 0.5, 2.0, 4.5, 7.0, 10.0],
            "Depth_Base": [0.5, 2.0, 4.5, 7.0, 10.0, 15.0],
            "Geology_Code": ["101", "102", "201", "401", "504", "801"],
            "Description": [
                "Dark brown silty TOPSOIL with roots",
                "Brown MADE GROUND with brick fragments",
                "Firm brown CLAY, slightly silty",
                "Medium dense fine SAND, some gravel",
                "Dense sandy GRAVEL, occasional cobbles",
                "Weathered MUDSTONE, grey, fissured",
            ],
        }
    )

    try:
        # Test with the new multi-page function
        images = create_professional_borehole_log_multi_page(
            borehole_data=test_data,
            borehole_id="TEST_BH01",
            ground_level=62.50,
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Multi-Page Borehole Log",
            figsize=(8.27, 11.69),  # A4 size
            dpi=150,  # Lower DPI for testing
        )

        if images and len(images) > 0:
            print(f"✅ Success! Generated {len(images)} page(s)")
            for i, img_b64 in enumerate(images):
                print(f"   Page {i+1}: {len(img_b64)} characters in base64 string")
            return True
        else:
            print("❌ Failed: No images generated")
            return False

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_multi_page_functionality()
    if success:
        print("\n🎉 All tests passed! The integration is working correctly.")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
