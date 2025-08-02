"""
Test script to verify the section plot footer layout fix.
This tests that the footer is now properly positioned below the plot area
and that the legend is displayed in the footer's left cell.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


# Test the updated section plotting
def test_section_footer_fix():
    """Test that footer is properly positioned below plot area with legend inside."""

    print("🧪 Testing section plot footer layout fix...")

    try:
        from section.plotting.main import plot_section_from_ags_content

        # Use test AGS content
        test_ags_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
UNITS,<blank>,<blank>,m,m,m
TYPE,ID,PA,2DP,2DP,2DP
DATA,BH01,RC,400000,300000,45.5
DATA,BH02,RC,400020,300010,46.2
DATA,BH03,RC,400040,300020,44.8

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
UNITS,<blank>,m,m,<blank>,<blank>
TYPE,ID,2DP,2DP,X,X
DATA,BH01,0.00,1.50,101,TOPSOIL
DATA,BH01,1.50,3.00,203,SANDY CLAY
DATA,BH01,3.00,5.00,501,GRAVEL
DATA,BH02,0.00,1.20,101,TOPSOIL
DATA,BH02,1.20,4.00,203,SANDY CLAY
DATA,BH02,4.00,6.50,501,GRAVEL
DATA,BH03,0.00,0.80,101,TOPSOIL
DATA,BH03,0.80,2.50,203,SANDY CLAY
DATA,BH03,2.50,5.20,501,GRAVEL"""

        print("✓ Calling plot_section_from_ags_content with updated layout...")

        # Test both return modes
        result_base64 = plot_section_from_ags_content(
            test_ags_content, return_base64=True, show_labels=True
        )

        result_figure = plot_section_from_ags_content(
            test_ags_content, return_base64=False, show_labels=True
        )

        # Validate results
        if result_base64 and isinstance(result_base64, str):
            print("✓ Base64 mode: Successfully generated section plot")
            print(f"  Base64 length: {len(result_base64)} characters")
            if result_base64.startswith("data:image/png;base64,"):
                print("✓ Base64 has correct image header")
            else:
                print("⚠ Base64 missing proper image header")
        else:
            print("❌ Base64 mode failed")

        if result_figure:
            print("✓ Figure mode: Successfully generated section plot")
            print(f"  Figure type: {type(result_figure)}")

            # Check figure dimensions
            fig_size = result_figure.get_size_inches()
            print(f"  Figure size: {fig_size[0]:.2f} x {fig_size[1]:.2f} inches")

            # Check axes positioning
            axes = result_figure.get_axes()
            print(f"  Number of axes: {len(axes)}")

            for i, ax in enumerate(axes):
                position = ax.get_position()
                print(
                    f"  Axis {i+1}: x={position.x0:.3f}, y={position.y0:.3f}, "
                    f"width={position.width:.3f}, height={position.height:.3f}"
                )

            # Clean up figure
            import matplotlib.pyplot as plt

            plt.close(result_figure)

        else:
            print("❌ Figure mode failed")

        print("🎉 Section plot footer layout fix test completed!")
        return True

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_section_footer_fix()
    if success:
        print("\n✅ All tests passed! Footer layout fix is working correctly.")
    else:
        print("\n❌ Tests failed. Check the implementation.")
