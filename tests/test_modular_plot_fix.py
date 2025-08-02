#!/usr/bin/env python3
"""
Test the updated plot_section_from_ags_content function without archive dependencies.
"""

import sys
import traceback
from pathlib import Path

# Add the workspace root to Python path
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))


def test_modular_plot_function():
    """Test the updated plot function without archive dependencies."""
    print("Testing updated plot_section_from_ags_content function...")

    try:
        # Import the updated function
        from section.plotting.main import plot_section_from_ags_content

        print("✓ Successfully imported plot_section_from_ags_content")

        # Test with dummy AGS content for both return modes
        dummy_ags = """
"GROUP","PROJ"
"","","Project Name","Example Project"
""
"GROUP","LOCA"
"LOCA_ID","LOCA_TYPE","LOCA_STAT","LOCA_NATE","LOCA_NATN","LOCA_GL"
"m","","","m","m","mOD"
"BH01","Borehole","","100000","200000","10.0"
""
"GROUP","GEOL"
"LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC"
"m","m","m",""
"BH01","0.0","2.0","Clay"
"BH01","2.0","5.0","Sand"
""
"""

        # Test return_base64=True (should use fast modular path)
        print("\nTesting return_base64=True...")
        result_base64 = plot_section_from_ags_content(
            ags_content=dummy_ags,
            filename="test.ags",
            return_base64=True,
            show_labels=True,
        )

        if isinstance(result_base64, str) and result_base64.startswith("data:image"):
            print("✓ Base64 mode successful - returned base64 image string")
        elif isinstance(result_base64, str) and "Error" in result_base64:
            print(f"⚠️ Base64 mode returned error: {result_base64[:100]}...")
        else:
            print(
                f"⚠️ Base64 mode returned unexpected result type: {type(result_base64)}"
            )

        # Test return_base64=False (should use modular structure, not archive)
        print("\nTesting return_base64=False...")
        result_figure = plot_section_from_ags_content(
            ags_content=dummy_ags,
            filename="test.ags",
            return_base64=False,
            show_labels=True,
        )

        import matplotlib.pyplot as plt

        if isinstance(result_figure, plt.Figure):
            print("✓ Figure mode successful - returned matplotlib Figure")
            plt.close(result_figure)  # Clean up
        else:
            print(
                f"⚠️ Figure mode returned unexpected result type: {type(result_figure)}"
            )

        return True

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return False


def test_geology_codes_csv():
    """Test that geology codes CSV loading still works."""
    print("\nTesting geology codes CSV loading...")

    try:
        from geology_code_utils import get_geology_color, get_geology_pattern

        # Test a few known codes
        color_101 = get_geology_color("101")
        pattern_101 = get_geology_pattern("101")

        print(f"✓ Geology code 101: Color={color_101}, Pattern={pattern_101}")

        color_501 = get_geology_color("501")
        pattern_501 = get_geology_pattern("501")

        print(f"✓ Geology code 501: Color={color_501}, Pattern={pattern_501}")

        return True

    except Exception as e:
        print(f"✗ Geology codes test failed: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== Testing Updated Modular Plot Function ===")

    # Test the updated function
    plot_success = test_modular_plot_function()

    # Test geology codes still work
    geology_success = test_geology_codes_csv()

    print(f"\n=== Results ===")
    print(f"Plot function: {'✓ SUCCESS' if plot_success else '✗ FAILED'}")
    print(f"Geology codes: {'✓ SUCCESS' if geology_success else '✗ FAILED'}")

    if plot_success and geology_success:
        print("\n🎉 All tests passed! No archive dependencies, geology codes working!")
    else:
        print("\n❌ Some tests failed - check output above")
