#!/usr/bin/env python3
"""
Comprehensive test for the new text box overflow management system.
Tests both layer-continues and layer-complete overflow scenarios.
"""

import pandas as pd
import logging
from borehole_log_professional import create_professional_borehole_log
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_overflow_management_system():
    """
    Test the comprehensive overflow management system with various scenarios.
    """

    # Create test data designed to trigger different overflow scenarios
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.0, 2.0, 4.0, 5.0, 6.0, 8.0, 9.0, 11.0],
            "Depth_Base": [1.0, 2.0, 4.0, 5.0, 6.0, 8.0, 9.0, 11.0, 15.0],
            "Geology_Code": [
                "101",
                "203",
                "501",
                "202",
                "801",
                "101",
                "203",
                "501",
                "202",
            ],
            "Description": [
                "Short description",  # 1m layer - should fit normally
                "Medium length description that might cause some issues",  # 1m layer - might overflow
                "Very long description that will definitely cause overflow issues and should trigger "
                "the overflow management system to create special overflow pages",  # 2m layer - will overflow
                "Brief",  # 1m layer - should fit
                "Another medium length description that could cause overflow",  # 1m layer - might overflow
                "Another extremely long description that will span multiple lines and cause overflow "
                "issues requiring the system to handle it appropriately",  # 2m layer - will overflow
                "Short",  # 1m layer - should fit
                "Very long description that will test the overflow system extensively and ensure "
                "it handles multiple overflow scenarios correctly",  # 2m layer - will overflow
                "Final layer with extensive description that spans multiple pages and will test "
                "the layer-continues overflow strategy",  # 4m layer - extends to next page
            ],
        }
    )

    print("=" * 80)
    print("COMPREHENSIVE OVERFLOW MANAGEMENT SYSTEM TEST")
    print("=" * 80)
    print("\nTest data (designed to trigger various overflow scenarios):")

    for i, row in sample_data.iterrows():
        thickness = row["Depth_Base"] - row["Depth_Top"]
        desc_length = len(row["Description"])
        print(
            f"Layer {i+1}: {row['Depth_Top']:.1f}-{row['Depth_Base']:.1f}m "
            f"(thickness: {thickness:.1f}m, desc: {desc_length} chars)"
        )
        print(
            f"  Description: {row['Description'][:60]}{'...' if desc_length > 60 else ''}"
        )
        print()

    print("Expected overflow behaviors:")
    print("1. Layers 3, 6, 8: Long descriptions may create overflow pages")
    print("2. Layer 9: Extends beyond page boundary - layer continues strategy")
    print("3. Some medium descriptions may be pushed down and still extend")
    print("4. System should intelligently classify and handle each scenario")
    print()

    try:
        # Create professional borehole log with overflow management
        images = create_professional_borehole_log(
            sample_data,
            "TEST_OVERFLOW",
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Comprehensive Overflow Management System",
            figsize=(8.27, 11.69),
            dpi=150,  # Lower DPI for faster testing
        )

        if images:
            print(f"SUCCESS: Generated {len(images)} total page(s)")

            # Save all pages for inspection
            for i, img in enumerate(images):
                filename = f"test_overflow_management_page_{i+1}.png"
                try:
                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(img))
                    print(f"Saved: {filename}")
                except Exception as e:
                    print(f"Error saving {filename}: {e}")

            print("\nPlease inspect the output images to verify:")
            print("✓ Regular pages show text boxes that fit within page boundaries")
            print(
                "✓ Overflow pages are created for layers ending on page but text too long"
            )
            print(
                "✓ Layers continuing to next page have their text deferred appropriately"
            )
            print("✓ Page numbering includes overflow page indicators")
            print("✓ Professional formatting is maintained across all page types")

        else:
            print("ERROR: No images were generated")

    except Exception as e:
        print(f"ERROR creating borehole log: {e}")
        import traceback

        traceback.print_exc()


def test_edge_cases():
    """
    Test edge cases for the overflow management system.
    """

    print("\n" + "=" * 60)
    print("EDGE CASES TEST")
    print("=" * 60)

    # Edge case: Very thin layers with long descriptions
    edge_case_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 0.1, 0.3, 5.0, 5.1],
            "Depth_Base": [0.1, 0.3, 5.0, 5.1, 10.0],
            "Geology_Code": ["101", "203", "501", "202", "801"],
            "Description": [
                "This is an extremely long description for a very thin layer that will definitely overflow",
                "Another very long description for another thin layer to test multiple overflow scenarios",
                "Massive description for a thick layer that covers most of the first page and will "
                "test the system extensively with lots of text",
                "Short description for thin layer",
                "Final long description that extends to second page to test layer continues strategy",
            ],
        }
    )

    print("Edge case data:")
    for i, row in edge_case_data.iterrows():
        thickness = row["Depth_Base"] - row["Depth_Top"]
        desc_length = len(row["Description"])
        print(f"Layer {i+1}: {thickness:.1f}m thick, {desc_length} char description")

    try:
        images = create_professional_borehole_log(
            edge_case_data,
            "TEST_EDGE_CASES",
            geology_csv_path="Geology Codes BGS.csv",
            title="Test Edge Cases for Overflow Management",
            figsize=(8.27, 11.69),
            dpi=150,
        )

        if images:
            print(f"\nGenerated {len(images)} page(s) for edge cases")

            for i, img in enumerate(images):
                filename = f"test_edge_cases_page_{i+1}.png"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(img))
                print(f"Saved: {filename}")

        else:
            print("ERROR: No images generated for edge cases")

    except Exception as e:
        print(f"ERROR in edge cases test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_overflow_management_system()
    test_edge_cases()
