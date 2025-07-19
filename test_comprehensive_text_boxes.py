#!/usr/bin/env python3
"""
Comprehensive test script for the text box implementation in borehole_log_professional.py
Tests various scenarios including short/long descriptions and edge cases.
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_comprehensive_text_boxes():
    """Test the text box implementation with various scenarios"""

    # Test case 1: Mixed length descriptions
    test_data_1 = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.5, 4.0, 6.0],
            "Depth_Base": [1.0, 2.5, 4.0, 6.0, 8.0],
            "Geology_Code": ["101", "203", "501", "202", "801"],
            "Description": [
                "Clay",  # Very short
                "Medium dense fine to coarse sand with occasional gravel particles and shells from marine environment",  # Long
                "Gravel",  # Short
                "Stiff grey clay with limestone fragments, becoming softer with depth, some oxidation staining and organic material present throughout the layer",  # Very long
                "Limestone",  # Short
            ],
        }
    )

    print("Test 1: Creating borehole log with mixed description lengths...")
    images_1 = create_professional_borehole_log(
        test_data_1,
        "TEST_MIXED",
        title="Test Mixed Description Lengths",
        figsize=(8.27, 11.69),
        dpi=150,
    )

    if images_1:
        print(f"Test 1 SUCCESS: Generated {len(images_1)} page(s)")
        with open("test_mixed_lengths.png", "wb") as f:
            f.write(base64.b64decode(images_1[0]))
        print("Saved test_mixed_lengths.png")
    else:
        print("Test 1 FAILED: No images generated")

    # Test case 2: All very long descriptions
    test_data_2 = pd.DataFrame(
        {
            "Depth_Top": [0.0, 2.0, 4.0, 6.0],
            "Depth_Base": [2.0, 4.0, 6.0, 8.0],
            "Geology_Code": ["101", "203", "501", "202"],
            "Description": [
                "Soft brown silty clay with occasional organic matter, some small roots and debris from topsoil contamination, becoming denser with depth and showing signs of weathering and oxidation",
                "Medium dense fine to coarse sand with occasional gravel particles and marine shells, some iron staining and calcrete nodules, variable density throughout the layer with softer zones at boundaries",
                "Dense angular gravel with cobbles and boulders, very hard drilling conditions encountered, some limestone and sandstone fragments with occasional clay binding material creating variable permeability",
                "Stiff grey clay with limestone fragments and chalk pieces, becoming softer with depth below 6.5m, some oxidation staining and organic material present throughout with occasional shell fragments",
            ],
        }
    )

    print("\nTest 2: Creating borehole log with all long descriptions...")
    images_2 = create_professional_borehole_log(
        test_data_2,
        "TEST_LONG",
        title="Test All Long Descriptions",
        figsize=(8.27, 11.69),
        dpi=150,
    )

    if images_2:
        print(f"Test 2 SUCCESS: Generated {len(images_2)} page(s)")
        with open("test_long_descriptions.png", "wb") as f:
            f.write(base64.b64decode(images_2[0]))
        print("Saved test_long_descriptions.png")
    else:
        print("Test 2 FAILED: No images generated")

    # Test case 3: Many layers (test stacking)
    many_layers = []
    for i in range(15):
        many_layers.append(
            {
                "Depth_Top": i * 0.5,
                "Depth_Base": (i + 1) * 0.5,
                "Geology_Code": ["101", "203", "501", "202", "801"][i % 5],
                "Description": f"Layer {i+1}: Description of varying length - some short, some much longer with detailed geological information about the stratum composition and characteristics found at this particular depth interval.",
            }
        )

    test_data_3 = pd.DataFrame(many_layers)

    print("\nTest 3: Creating borehole log with many layers...")
    images_3 = create_professional_borehole_log(
        test_data_3,
        "TEST_MANY",
        title="Test Many Layers Stacking",
        figsize=(8.27, 11.69),
        dpi=150,
    )

    if images_3:
        print(f"Test 3 SUCCESS: Generated {len(images_3)} page(s)")
        with open("test_many_layers.png", "wb") as f:
            f.write(base64.b64decode(images_3[0]))
        print("Saved test_many_layers.png")
    else:
        print("Test 3 FAILED: No images generated")

    print("\n=== ALL TESTS COMPLETED ===")
    print("Check the generated PNG files to verify:")
    print("1. Text boxes are properly stacked without overlapping")
    print("2. Text is wrapped within the description column boundaries")
    print("3. Text boxes are centered in the description column")
    print("4. No diagonal connector lines are present")


if __name__ == "__main__":
    test_comprehensive_text_boxes()
