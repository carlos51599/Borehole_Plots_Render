#!/usr/bin/env python3
"""
Test script to analyze current section plot implementation.
"""

import matplotlib.pyplot as plt
import numpy as np
from section_plot_professional import plot_professional_borehole_sections
import pandas as pd


# Create sample data for testing
def create_sample_data():
    """Create sample geological and location data for testing."""

    # Sample geological data
    geol_data = {
        "LOCA_ID": ["BH01", "BH01", "BH01", "BH02", "BH02", "BH02"],
        "GEOL_TOP": [0.0, 2.0, 5.0, 0.0, 1.5, 4.0],
        "GEOL_BASE": [2.0, 5.0, 8.0, 1.5, 4.0, 7.5],
        "GEOL_LEG": ["FILL", "CLAY", "SAND", "FILL", "CLAY", "GRAVEL"],
        "GEOL_DESC": [
            "Made Ground FILL",
            "CLAY brown stiff",
            "SAND fine yellow",
            "Made Ground FILL",
            "CLAY grey soft",
            "GRAVEL sandy",
        ],
    }
    geol_df = pd.DataFrame(geol_data)

    # Sample location data
    loca_data = {
        "LOCA_ID": ["BH01", "BH02"],
        "LOCA_NATE": [525000.0, 525050.0],
        "LOCA_NATN": [185000.0, 185000.0],
        "LOCA_GL": [100.0, 98.0],
    }
    loca_df = pd.DataFrame(loca_data)

    return geol_df, loca_df


def test_current_implementation():
    """Test the current section plot implementation."""

    print("=== Testing Current Section Plot Implementation ===")

    # Create sample data
    geol_df, loca_df = create_sample_data()

    print(f"GEOL DataFrame shape: {geol_df.shape}")
    print(f"LOCA DataFrame shape: {loca_df.shape}")

    # Test current plot function
    try:
        fig = plot_professional_borehole_sections(
            geol_df=geol_df,
            loca_df=loca_df,
            abbr_df=None,
            ags_title="Test Geological Section",
            section_line=None,
            show_labels=True,
            vertical_exaggeration=3.0,
            save_high_res=False,
            output_filename=None,
            color_alpha=1.0,
            hatch_alpha=1.0,
        )

        if fig is not None:
            print(f"Figure created successfully!")
            print(f"Figure size: {fig.get_size_inches()}")
            print(f"Figure DPI: {fig.dpi}")

            # Get figure bounds and layout
            bbox = fig.get_tightbbox()
            if bbox:
                print(f"Tight bbox: {bbox.bounds}")

            # Check axes
            axes = fig.get_axes()
            print(f"Number of axes: {len(axes)}")

            if axes:
                ax = axes[0]
                print(f"Axis position: {ax.get_position().bounds}")
                print(f"X limits: {ax.get_xlim()}")
                print(f"Y limits: {ax.get_ylim()}")

            # Save test image
            fig.savefig("test_current_section.png", dpi=300, bbox_inches="tight")
            print("Test image saved as 'test_current_section.png'")

            # Show current return type
            print(f"Return type: {type(fig)}")

            plt.close(fig)

        else:
            print("ERROR: No figure returned!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_current_implementation()
