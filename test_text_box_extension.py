#!/usr/bin/env python3
"""
Test script to verify that text boxes extend to match their layer's bottom boundary
when the description is short.
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_text_box_extension():
    """Test that text boxes extend to match layer boundaries when descriptions are short"""

    # Create sample data with mixed description lengths
    # Some short descriptions that should trigger text box extension
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 2.0, 3.0, 6.0, 8.0],
            "Depth_Base": [2.0, 3.0, 6.0, 8.0, 12.0],
            "Geology_Code": ["101", "203", "501", "202", "801"],
            "Description": [
                "Short description",  # Very short - should extend to 2.0m depth
                "Clay",  # Extremely short - should extend to 1m thickness
                "Dense angular gravel with cobbles, very hard drilling, some limestone fragments",  # Long
                "Medium sand",  # Short - should extend to 2m thickness
                "Limestone",  # Short - should extend to 4m thickness
            ],
        }
    )

    print("Creating professional borehole log to test text box extension...")
    print("\nTest data:")
    for i, row in sample_data.iterrows():
        thickness = row["Depth_Base"] - row["Depth_Top"]
        print(
            f"Layer {i+1}: {row['Depth_Top']}-{row['Depth_Base']}m (thickness: {thickness}m) - '{row['Description']}'"
        )

    try:
        # Create professional borehole log
        images = create_professional_borehole_log(
            sample_data,
            "TEST_EXTENSION",
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Text Box Extension to Layer Boundaries",
            figsize=(8.27, 11.69),
            dpi=150,  # Lower DPI for faster testing
        )

        if images:
            print(f"\nSuccessfully generated {len(images)} page(s)")

            # Save the first page to file for inspection
            try:
                with open("test_text_box_extension_output.png", "wb") as f:
                    f.write(base64.b64decode(images[0]))
                print("Saved test output to: test_text_box_extension_output.png")
                print("\nExpected behavior:")
                print(
                    "- Short descriptions should have text boxes that extend to match their layer's bottom boundary"
                )
                print(
                    "- Text content should appear at the top of the extended text boxes"
                )
                print(
                    "- Empty space should appear below the text content within the extended boxes"
                )
                print(
                    "- Long descriptions should still extend beyond layer boundaries if needed"
                )
            except Exception as e:
                print(f"Error saving image file: {e}")

        else:
            print("Error: No images were generated")

    except Exception as e:
        print(f"Error creating borehole log: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_text_box_extension()
