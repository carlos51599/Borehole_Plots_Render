"""
Test script for the professional borehole section plotting functionality.
This script demonstrates how to use the new professional plotting features.
"""

import matplotlib.pyplot as plt
from section_plot_professional import plot_section_from_ags_content


def test_professional_plotting():
    """
    Test the professional plotting functionality with sample data.

    This function demonstrates:
    1. How to call the professional plotting function
    2. Different parameter configurations
    3. High-resolution export capabilities
    """

    print("=== Professional Borehole Section Plotting Test ===")

    # Sample AGS content (you would replace this with real AGS file content)
    sample_ags_content = """
GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
DATA,BH001,0.0,1.5,TS,TOPSOIL Brown silty clay
DATA,BH001,1.5,3.0,CL,CLAY Firm brown clay
DATA,BH001,3.0,5.0,SA,SAND Medium dense sand
DATA,BH002,0.0,1.0,TS,TOPSOIL Brown silty clay
DATA,BH002,1.0,2.5,CL,CLAY Firm brown clay
DATA,BH002,2.5,4.5,GR,GRAVEL Dense sandy gravel
GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH001,400000,300000,50.0
DATA,BH002,400050,300000,48.5
GROUP,ABBR
HEADING,ABBR_CODE,ABBR_DESC
DATA,TS,Topsoil
DATA,CL,Clay
DATA,SA,Sand
DATA,GR,Gravel
"""

    # Test 1: Basic professional plotting
    print("\n1. Testing basic professional plotting...")
    try:
        fig1 = plot_section_from_ags_content(
            ags_content=sample_ags_content, show_labels=True, vertical_exaggeration=3.0
        )

        if fig1 is not None:
            print("✓ Basic professional plotting successful")
            plt.show()  # Display the plot
        else:
            print("✗ Basic professional plotting failed")

    except Exception as e:
        print(f"✗ Basic professional plotting error: {e}")

    # Test 2: High-resolution export
    print("\n2. Testing high-resolution export...")
    try:
        fig2 = plot_section_from_ags_content(
            ags_content=sample_ags_content,
            show_labels=True,
            vertical_exaggeration=3.0,
            save_high_res=True,
            output_filename="test_professional_section",
        )

        if fig2 is not None:
            print("✓ High-resolution export successful")
            print(
                "  Files created: test_professional_section.pdf, test_professional_section.png"
            )
        else:
            print("✗ High-resolution export failed")

    except Exception as e:
        print(f"✗ High-resolution export error: {e}")

    # Test 3: Different vertical exaggerations
    print("\n3. Testing different vertical exaggerations...")

    exaggerations = [1.0, 3.0, 5.0]
    for i, exag in enumerate(exaggerations):
        try:
            fig = plot_section_from_ags_content(
                ags_content=sample_ags_content,
                show_labels=True,
                vertical_exaggeration=exag,
            )

            if fig is not None:
                print(f"✓ Vertical exaggeration {exag}x successful")
                if i == 0:  # Show first one as example
                    plt.show()
            else:
                print(f"✗ Vertical exaggeration {exag}x failed")

        except Exception as e:
            print(f"✗ Vertical exaggeration {exag}x error: {e}")

    # Test 4: Without labels
    print("\n4. Testing without geological labels...")
    try:
        fig4 = plot_section_from_ags_content(
            ags_content=sample_ags_content, show_labels=False, vertical_exaggeration=3.0
        )

        if fig4 is not None:
            print("✓ No labels mode successful")
        else:
            print("✗ No labels mode failed")

    except Exception as e:
        print(f"✗ No labels mode error: {e}")

    print("\n=== Test Summary ===")
    print("Professional plotting test completed.")
    print("Check the generated files and displayed plots for visual verification.")
    print("\nNext steps:")
    print("1. Integrate into your Dash app using the PROFESSIONAL_PLOTTING_GUIDE.md")
    print("2. Test with your actual AGS data files")
    print("3. Customize colors/patterns if needed for your geological units")


def demonstrate_style_comparison():
    """
    Demonstrate the difference between standard and professional styles.
    """
    print("\n=== Style Comparison Demo ===")

    # You can add code here to compare the original vs professional styles
    # if you want to show side-by-side comparisons

    print("Professional style features:")
    print("• Geological hatch patterns (dots for clay, lines for sand, etc.)")
    print("• Professional earth-tone color scheme")
    print("• Arial/sans-serif fonts throughout")
    print("• Enhanced gridlines (major and minor)")
    print("• Ground surface line with markers")
    print("• Professional legend with both color and pattern")
    print("• Configurable vertical exaggeration")
    print("• High-resolution PDF/PNG export")


if __name__ == "__main__":
    # Run the tests
    test_professional_plotting()
    demonstrate_style_comparison()

    print("\n=== Dependencies Check ===")

    # Check if all required packages are installed
    required_packages = ["matplotlib", "pandas", "numpy", "pyproj", "shapely"]

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed - run: pip install {package}")
