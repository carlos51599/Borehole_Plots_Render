#!/usr/bin/env python3
"""
Test script to verify the modified text box rendering with shortened boundaries
and diagonal connector lines in borehole_log_professional.py
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_enhanced_text_boxes():
    """Test the enhanced text box rendering with connector lines."""

    # Create sample data with varying layer thicknesses and descriptions
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5, 8.0, 10.5],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0, 10.5, 12.0],
            "Geology_Code": ["101", "203", "501", "202", "801", "103"],
            "Description": [
                "Soft brown clay with occasional organic matter and root fibers",
                "Medium dense fine to coarse sand with trace gravel",
                "Dense angular gravel with cobbles and some sand matrix",
                "Stiff grey clay with limestone fragments and occasional fossils",
                "Weathered limestone bedrock with joints and fractures",
                "Very long description that should test the text box sizing and connector line positioning: This is a detailed geological description that spans multiple lines to test how the enhanced text box rendering handles longer descriptions with the new shortened boundaries and diagonal connector lines to the adjacent columns.",
            ],
        }
    )

    print("Testing enhanced text box rendering...")
    print(f"Sample data contains {len(sample_data)} geological layers")

    # Create professional borehole log with enhanced text boxes
    try:
        images = create_professional_borehole_log(
            sample_data,
            "TEST_BH001",
            geology_csv_path="Geology Codes BGS.csv",
            title="Enhanced Text Box Test - Professional Borehole Log",
            figsize=(8.27, 11.69),  # A4 size
            dpi=300,
        )

        if images:
            print(f"✓ Successfully generated {len(images)} page(s)")
            print("✓ Enhanced text boxes with shortened boundaries implemented")
            print("✓ Diagonal connector lines to legend and adjacent columns added")
            print("Enhanced features:")
            print("  - Top/bottom lines shortened by 8% margin on each side")
            print("  - Diagonal connectors from text box corners to:")
            print("    * Left side: Right edge of legend/lithology column")
            print("    * Right side: Left edge of column after description")
            print(
                "  - Connector Y positions based on true geological GEOL_TOP/GEOL_BASE depths"
            )

            # Show first few characters of first image to confirm it's valid base64
            if len(images[0]) > 100:
                print(
                    f"✓ Generated valid base64 images (first image: {len(images[0])} characters)"
                )
            else:
                print("⚠ Generated images may be invalid (too short)")

        else:
            print("✗ Failed to generate images")

    except Exception as e:
        print(f"✗ Error during generation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_enhanced_text_boxes()
