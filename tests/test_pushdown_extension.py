#!/usr/bin/env python3
"""
Test script to verify that text boxes extend to match their layer's bottom boundary
in all scenarios, including when they are pushed down due to conflicts but remain
within their layer boundaries.
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_pushed_down_extension():
    """
    Test that text boxes extend to layer boundaries even when pushed down due to conflicts
    """

    # Create sample data designed to cause push-down conflicts
    # - Multiple short descriptions in close proximity to force conflicts
    # - But with enough layer thickness that pushed-down boxes should still extend
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.0, 3.5, 5.0, 7.0],
            "Depth_Base": [1.0, 2.0, 3.5, 5.0, 7.0, 10.0],
            "Geology_Code": ["101", "203", "501", "202", "801", "101"],
            "Description": [
                "Very short",  # 1m layer - should extend to bottom
                "Short text",  # 1m layer - will be pushed down due to conflict
                "Brief desc",  # 1.5m layer - will be pushed down, should still extend
                "Medium length description that might fit",  # 1.5m layer
                "Short",  # 2m layer - will be pushed down, should extend
                "Final layer with some description text",  # 3m layer
            ],
        }
    )

    print("Creating borehole log to test pushed-down text box extension...")
    print("\nTest data (designed to create conflicts):")
    for i, row in sample_data.iterrows():
        thickness = row["Depth_Base"] - row["Depth_Top"]
        print(
            f"Layer {i+1}: {row['Depth_Top']}-{row['Depth_Base']}m "
            f"(thickness: {thickness}m) - '{row['Description']}'"
        )

    print("\nExpected behavior:")
    print("1. First text box should extend to 1.0m depth")
    print("2. Second text box will be pushed down due to conflict with first")
    print("3. If second box bottom is still above 2.0m, it should extend to 2.0m")
    print("4. Similar pattern for subsequent boxes that get pushed down")
    print(
        "5. All text boxes should extend to their layer's bottom boundary when possible"
    )

    try:
        # Create professional borehole log
        images = create_professional_borehole_log(
            sample_data,
            "TEST_PUSHDOWN",
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Push-Down Text Box Extension",
            figsize=(8.27, 11.69),
            dpi=150,  # Lower DPI for faster testing
        )

        if images:
            print(f"\nSuccessfully generated {len(images)} page(s)")

            # Save the first page to file for inspection
            try:
                with open("test_pushdown_extension_output.png", "wb") as f:
                    f.write(base64.b64decode(images[0]))
                print("Saved test output to: test_pushdown_extension_output.png")
                print("\nPlease inspect the output image to verify:")
                print("- All text boxes extend to their layer's bottom boundaries")
                print("- Text content appears at the top of each box")
                print("- Empty space fills the bottom of extended boxes")
                print("- Pushed-down boxes still extend when within layer bounds")
            except Exception as e:
                print(f"Error saving image file: {e}")

        else:
            print("Error: No images were generated")

    except Exception as e:
        print(f"Error creating borehole log: {e}")
        import traceback

        traceback.print_exc()


def test_mixed_scenarios():
    """
    Test a mix of scenarios including very thick layers and very thin layers
    """

    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 0.5, 1.0, 4.0, 4.2, 7.0],
            "Depth_Base": [0.5, 1.0, 4.0, 4.2, 7.0, 12.0],
            "Geology_Code": ["101", "203", "501", "202", "801", "101"],
            "Description": [
                "Short",  # 0.5m layer - very thin
                "Brief",  # 0.5m layer - very thin, will be pushed down
                "This is a longer description for a thick layer that should have plenty of room",  # 3m layer
                "Tiny",  # 0.2m layer - extremely thin
                "Medium description text",  # 2.8m layer - thick
                "Final layer description",  # 5m layer - very thick
            ],
        }
    )

    print("\n" + "=" * 60)
    print("MIXED SCENARIOS TEST")
    print("=" * 60)
    print("\nTest data (mix of thick and thin layers):")
    for i, row in sample_data.iterrows():
        thickness = row["Depth_Base"] - row["Depth_Top"]
        print(
            f"Layer {i+1}: {row['Depth_Top']}-{row['Depth_Base']}m "
            f"(thickness: {thickness}m) - '{row['Description']}'"
        )

    try:
        images = create_professional_borehole_log(
            sample_data,
            "TEST_MIXED",
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Mixed Layer Thickness Scenarios",
            figsize=(8.27, 11.69),
            dpi=150,
        )

        if images:
            print(f"\nSuccessfully generated {len(images)} page(s)")

            with open("test_mixed_scenarios_output.png", "wb") as f:
                f.write(base64.b64decode(images[0]))
            print("Saved test output to: test_mixed_scenarios_output.png")

        else:
            print("Error: No images were generated")

    except Exception as e:
        print(f"Error creating borehole log: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_pushed_down_extension()
    test_mixed_scenarios()
