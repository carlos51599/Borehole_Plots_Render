#!/usr/bin/env python3
"""
Test script to validate the enhanced section plot implementation.
Tests both base64 and figure return modes, A4 landscape format, and professional styling.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import base64
import io
from section_plot_professional import (
    plot_professional_borehole_sections,
    plot_section_from_ags_content,
    A4_LANDSCAPE_WIDTH,
    A4_LANDSCAPE_HEIGHT,
    DEFAULT_DPI,
    DEFAULT_COLOR_ALPHA,
    DEFAULT_HATCH_ALPHA,
)


def create_comprehensive_sample_data():
    """Create comprehensive sample geological and location data for testing."""

    # Sample geological data with more varied geology
    geol_data = {
        "LOCA_ID": [
            "BH01",
            "BH01",
            "BH01",
            "BH01",
            "BH02",
            "BH02",
            "BH02",
            "BH03",
            "BH03",
            "BH03",
        ],
        "GEOL_TOP": [0.0, 1.5, 3.0, 6.0, 0.0, 2.0, 5.0, 0.0, 1.0, 4.5],
        "GEOL_BASE": [1.5, 3.0, 6.0, 9.0, 2.0, 5.0, 8.5, 1.0, 4.5, 7.0],
        "GEOL_LEG": [
            "101",
            "301",
            "403",
            "501",
            "101",
            "301",
            "509",
            "202",
            "410",
            "501",
        ],
        "GEOL_DESC": [
            "Made Ground FILL brown",
            "CLAY brown stiff",
            "SAND fine yellow dense",
            "GRAVEL sandy dense",
            "Made Ground FILL mixed",
            "CLAY grey soft to firm",
            "GRAVEL with sand",
            "SILT grey soft",
            "SAND silty medium dense",
            "GRAVEL clean",
        ],
    }
    geol_df = pd.DataFrame(geol_data)

    # Sample location data with realistic spacing
    loca_data = {
        "LOCA_ID": ["BH01", "BH02", "BH03"],
        "LOCA_NATE": [525000.0, 525025.0, 525055.0],
        "LOCA_NATN": [185000.0, 185005.0, 185000.0],
        "LOCA_GL": [100.0, 98.5, 99.2],
    }
    loca_df = pd.DataFrame(loca_data)

    return geol_df, loca_df


def test_base64_return():
    """Test the new base64 return functionality."""

    print("=== Testing Base64 Return Mode ===")

    geol_df, loca_df = create_comprehensive_sample_data()

    try:
        # Test base64 return (new default)
        result = plot_professional_borehole_sections(
            geol_df=geol_df,
            loca_df=loca_df,
            abbr_df=None,
            ags_title="Test A4 Landscape Section - Base64 Mode",
            section_line=None,
            show_labels=True,
            vertical_exaggeration=3.0,
            save_high_res=False,
            output_filename=None,
            return_base64=True,  # New parameter
            figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
            dpi=DEFAULT_DPI,
        )

        if isinstance(result, str):
            print(f"✓ Base64 string returned successfully")
            print(f"✓ Base64 string length: {len(result)} characters")
            print(f"✓ Starts with expected base64 prefix: {result[:50]}...")

            # Validate it's a proper base64 image
            try:
                img_data = base64.b64decode(result)
                print(f"✓ Valid base64 data, decoded size: {len(img_data)} bytes")

                # Save test image to verify
                with open("test_enhanced_section_base64.png", "wb") as f:
                    f.write(img_data)
                print("✓ Test image saved as 'test_enhanced_section_base64.png'")

            except Exception as e:
                print(f"✗ Invalid base64 data: {e}")

        else:
            print(f"✗ Expected string, got {type(result)}")

    except Exception as e:
        print(f"✗ Error in base64 mode: {e}")
        import traceback

        traceback.print_exc()


def test_figure_return():
    """Test backward compatibility with figure return."""

    print("\n=== Testing Figure Return Mode (Backward Compatibility) ===")

    geol_df, loca_df = create_comprehensive_sample_data()

    try:
        # Test figure return (backward compatibility)
        result = plot_professional_borehole_sections(
            geol_df=geol_df,
            loca_df=loca_df,
            abbr_df=None,
            ags_title="Test A4 Landscape Section - Figure Mode",
            section_line=None,
            show_labels=True,
            vertical_exaggeration=3.0,
            save_high_res=False,
            output_filename=None,
            return_base64=False,  # Backward compatibility
            figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
            dpi=DEFAULT_DPI,
        )

        if hasattr(result, "savefig"):  # Check if it's a matplotlib Figure
            print(f"✓ Figure object returned successfully")
            print(f"✓ Figure size: {result.get_size_inches()}")
            print(f"✓ Figure DPI: {result.dpi}")

            # Verify A4 landscape dimensions
            width, height = result.get_size_inches()
            if (
                abs(width - A4_LANDSCAPE_WIDTH) < 0.1
                and abs(height - A4_LANDSCAPE_HEIGHT) < 0.1
            ):
                print(
                    f'✓ Correct A4 landscape dimensions: {width:.2f}" x {height:.2f}"'
                )
            else:
                print(
                    f'✗ Incorrect dimensions: {width:.2f}" x {height:.2f}", expected A4 landscape'
                )

            # Save test image
            result.savefig("test_enhanced_section_figure.png", dpi=DEFAULT_DPI)
            print("✓ Test image saved as 'test_enhanced_section_figure.png'")

            # Clean up
            plt.close(result)

        else:
            print(f"✗ Expected Figure object, got {type(result)}")

    except Exception as e:
        print(f"✗ Error in figure mode: {e}")
        import traceback

        traceback.print_exc()


def test_transparency_and_styling():
    """Test professional transparency and styling features."""

    print("\n=== Testing Professional Styling and Transparency ===")

    geol_df, loca_df = create_comprehensive_sample_data()

    try:
        # Test with custom transparency values
        result = plot_professional_borehole_sections(
            geol_df=geol_df,
            loca_df=loca_df,
            abbr_df=None,
            ags_title="Professional Styling Test",
            section_line=None,
            show_labels=True,
            vertical_exaggeration=2.0,
            save_high_res=False,
            output_filename=None,
            return_base64=True,
            figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
            dpi=DEFAULT_DPI,
            color_alpha=0.8,  # Test custom transparency
            hatch_alpha=0.4,
        )

        if isinstance(result, str):
            print(f"✓ Professional styling test successful")

            # Save image to verify styling
            img_data = base64.b64decode(result)
            with open("test_professional_styling.png", "wb") as f:
                f.write(img_data)
            print("✓ Professional styling test image saved")

        else:
            print(f"✗ Professional styling test failed")

    except Exception as e:
        print(f"✗ Error in styling test: {e}")


def test_high_resolution_export():
    """Test high-resolution export functionality."""

    print("\n=== Testing High-Resolution Export ===")

    geol_df, loca_df = create_comprehensive_sample_data()

    try:
        # Test high-res export with figure return for file saving
        result = plot_professional_borehole_sections(
            geol_df=geol_df,
            loca_df=loca_df,
            abbr_df=None,
            ags_title="High-Resolution Export Test",
            section_line=None,
            show_labels=True,
            vertical_exaggeration=3.0,
            save_high_res=True,
            output_filename="test_high_res_section",
            return_base64=False,  # Use figure mode for file saving
            figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
            dpi=DEFAULT_DPI,
        )

        if hasattr(result, "savefig"):
            print(f"✓ High-resolution export test completed")
            print(
                f"✓ Check for test_high_res_section.pdf and test_high_res_section.png"
            )
            plt.close(result)
        else:
            print(f"✗ High-resolution export test failed")

    except Exception as e:
        print(f"✗ Error in high-resolution export: {e}")


def test_wrapper_function():
    """Test the AGS content wrapper function."""

    print("\n=== Testing AGS Content Wrapper Function ===")

    # Create minimal AGS content string for testing
    ags_content = """GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
DATA,BH01,0.0,2.0,101,Made Ground FILL
DATA,BH01,2.0,5.0,301,CLAY brown stiff
DATA,BH02,0.0,1.5,101,Made Ground FILL
DATA,BH02,1.5,4.0,403,SAND fine dense

GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH01,525000.0,185000.0,100.0
DATA,BH02,525030.0,185000.0,98.0
"""

    try:
        result = plot_section_from_ags_content(
            ags_content=ags_content,
            filter_loca_ids=None,
            section_line=None,
            show_labels=True,
            vertical_exaggeration=3.0,
            save_high_res=False,
            output_filename=None,
            return_base64=True,
            figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT),
            dpi=DEFAULT_DPI,
        )

        if isinstance(result, str):
            print(f"✓ AGS wrapper function test successful")

            # Save image
            img_data = base64.b64decode(result)
            with open("test_ags_wrapper.png", "wb") as f:
                f.write(img_data)
            print("✓ AGS wrapper test image saved")

        else:
            print(f"✗ AGS wrapper function test failed: {type(result)}")

    except Exception as e:
        print(f"✗ Error in AGS wrapper test: {e}")
        import traceback

        traceback.print_exc()


def run_comprehensive_tests():
    """Run all test functions."""

    print("=" * 60)
    print("COMPREHENSIVE SECTION PLOT ENHANCEMENT TESTS")
    print("=" * 60)

    test_base64_return()
    test_figure_return()
    test_transparency_and_styling()
    test_high_resolution_export()
    test_wrapper_function()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nGenerated test files:")
    print("- test_enhanced_section_base64.png")
    print("- test_enhanced_section_figure.png")
    print("- test_professional_styling.png")
    print("- test_high_res_section.pdf")
    print("- test_high_res_section.png")
    print("- test_ags_wrapper.png")


if __name__ == "__main__":
    run_comprehensive_tests()
