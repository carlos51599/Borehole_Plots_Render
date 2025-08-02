#!/usr/bin/env python3
"""
Section Plot Layout Diagnosis - Figure Positioning Investigation
==============================================================

This test investigates the figure layout issue where the section plot
only uses the left half of the figure area, leaving the right half blank.

The issue appears to be in the axis positioning calculations or
the way the plot area is positioned within the figure.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section.parsing import parse_ags_geol_section_from_string
from section import plot_section_from_ags_content
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def diagnose_figure_layout():
    """Diagnose the figure layout and positioning issues."""

    print("=== Section Plot Layout Diagnosis ===")
    print()

    # Load AGS data
    ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    try:
        with open(ags_file, "r", encoding="utf-8") as f:
            ags_content = f.read()
        print(f"✅ Loaded AGS file: {len(ags_content)} characters")

        # Parse to get borehole IDs
        geol_df, loca_df, _ = parse_ags_geol_section_from_string(ags_content)
        borehole_ids = loca_df["LOCA_ID"].tolist()[:3]  # Use first 3 boreholes

        print(f"🎯 Testing with boreholes: {borehole_ids}")

    except Exception as e:
        print(f"❌ Failed to load AGS data: {e}")
        return False

    # Test 1: Get the matplotlib figure object and analyze its layout
    print("\n1. Analyzing figure layout...")

    try:
        fig = plot_section_from_ags_content(
            ags_content,
            filter_loca_ids=borehole_ids,
            return_base64=False,  # Get matplotlib Figure object
        )

        if fig is None:
            print("   ❌ Failed to generate figure")
            return False

        print(f"   ✅ Generated figure object: {type(fig)}")

        # Analyze figure properties
        print(f"   📏 Figure size: {fig.get_size_inches()} inches")
        print(f"   📏 Figure DPI: {fig.dpi}")

        # Get all axes in the figure
        axes = fig.get_axes()
        print(f"   📊 Number of axes: {len(axes)}")

        for i, ax in enumerate(axes):
            pos = ax.get_position()
            print(
                f"   📊 Axis {i} position: [left={pos.x0:.3f}, bottom={pos.y0:.3f}, width={pos.width:.3f}, height={pos.height:.3f}]"
            )

            # Check axis limits
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            print(f"   📊 Axis {i} X limits: {xlim}")
            print(f"   📊 Axis {i} Y limits: {ylim}")

        # Test 2: Create a diagnostic figure to visualize layout
        print("\n2. Creating diagnostic layout visualization...")

        # Create a test figure with the same dimensions
        fig_width, fig_height = fig.get_size_inches()
        diag_fig = plt.figure(figsize=(fig_width, fig_height), dpi=100)
        diag_fig.patch.set_facecolor("lightgray")

        # Draw the figure boundaries
        ax_diag = diag_fig.add_axes([0, 0, 1, 1])  # Full figure
        ax_diag.set_xlim(0, 1)
        ax_diag.set_ylim(0, 1)
        ax_diag.set_aspect("equal")

        # Draw the actual plot area position from the original figure
        main_ax = axes[0] if axes else None
        if main_ax:
            pos = main_ax.get_position()

            # Draw the plot area rectangle
            rect = patches.Rectangle(
                (pos.x0, pos.y0),
                pos.width,
                pos.height,
                linewidth=2,
                edgecolor="red",
                facecolor="yellow",
                alpha=0.5,
            )
            ax_diag.add_patch(rect)

            # Add labels
            ax_diag.text(
                pos.x0 + pos.width / 2,
                pos.y0 + pos.height / 2,
                "PLOT AREA",
                ha="center",
                va="center",
                fontsize=14,
                weight="bold",
            )
            ax_diag.text(
                0.02,
                0.98,
                f'Figure: {fig_width:.2f}" x {fig_height:.2f}"',
                ha="left",
                va="top",
                fontsize=10,
            )
            ax_diag.text(
                0.02,
                0.94,
                f"Plot: [{pos.x0:.3f}, {pos.y0:.3f}, {pos.width:.3f}, {pos.height:.3f}]",
                ha="left",
                va="top",
                fontsize=10,
            )

            # Show expected vs actual positioning
            expected_left = 0.5 / fig_width
            expected_right = (fig_width - 0.5) / fig_width
            expected_width = expected_right - expected_left

            ax_diag.text(
                0.02,
                0.90,
                f"Expected left: {expected_left:.3f}",
                ha="left",
                va="top",
                fontsize=10,
                color="blue",
            )
            ax_diag.text(
                0.02,
                0.86,
                f"Actual left: {pos.x0:.3f}",
                ha="left",
                va="top",
                fontsize=10,
                color="red",
            )
            ax_diag.text(
                0.02,
                0.82,
                f"Expected width: {expected_width:.3f}",
                ha="left",
                va="top",
                fontsize=10,
                color="blue",
            )
            ax_diag.text(
                0.02,
                0.78,
                f"Actual width: {pos.width:.3f}",
                ha="left",
                va="top",
                fontsize=10,
                color="red",
            )

            # Check if plot is only using left half
            half_width = 0.5
            if pos.x0 + pos.width < half_width:
                ax_diag.text(
                    0.02,
                    0.74,
                    "❌ PROBLEM: Plot only uses LEFT HALF!",
                    ha="left",
                    va="top",
                    fontsize=12,
                    color="red",
                    weight="bold",
                )
            else:
                ax_diag.text(
                    0.02,
                    0.74,
                    "✅ Plot uses full width",
                    ha="left",
                    va="top",
                    fontsize=12,
                    color="green",
                    weight="bold",
                )

        ax_diag.set_title("Section Plot Layout Diagnosis", fontsize=16, weight="bold")
        ax_diag.axis("off")

        # Save diagnostic figure
        diag_filename = "tests/section_plot_layout_diagnosis.png"
        diag_fig.savefig(diag_filename, dpi=150, bbox_inches="tight")
        print(f"   💾 Saved diagnostic figure: {diag_filename}")

        # Test 3: Check positioning calculations manually
        print("\n3. Manual positioning calculation check...")

        # A4 landscape dimensions (should match the code)
        a4_width_in = 11.69
        a4_height_in = 8.27

        # Margins (should match the code)
        left_margin_in = 0.5
        right_margin_in = 0.5
        top_margin_in = 0.3
        bottom_margin_in = 0.3
        header_height_in = 1.5
        footer_height_in = 1.5

        # Calculate expected positioning
        plot_width_in = a4_width_in - left_margin_in - right_margin_in
        plot_height_in = (
            a4_height_in
            - top_margin_in
            - bottom_margin_in
            - header_height_in
            - footer_height_in
        )

        plot_left = left_margin_in / a4_width_in
        plot_bottom = (bottom_margin_in + footer_height_in) / a4_height_in
        plot_width_frac = plot_width_in / a4_width_in
        plot_height_frac = plot_height_in / a4_height_in

        print(f"   📐 Expected positioning:")
        print(f'      Figure size: {a4_width_in:.2f}" x {a4_height_in:.2f}"')
        print(f'      Plot area size: {plot_width_in:.2f}" x {plot_height_in:.2f}"')
        print(
            f"      Plot position: [left={plot_left:.3f}, bottom={plot_bottom:.3f}, width={plot_width_frac:.3f}, height={plot_height_frac:.3f}]"
        )

        # Check if this matches actual
        if main_ax:
            actual_pos = main_ax.get_position()
            print(f"   📐 Actual positioning:")
            print(
                f"      Plot position: [left={actual_pos.x0:.3f}, bottom={actual_pos.y0:.3f}, width={actual_pos.width:.3f}, height={actual_pos.height:.3f}]"
            )

            # Compare
            left_diff = abs(plot_left - actual_pos.x0)
            width_diff = abs(plot_width_frac - actual_pos.width)

            print(f"   📈 Differences:")
            print(f"      Left position diff: {left_diff:.6f}")
            print(f"      Width diff: {width_diff:.6f}")

            if left_diff < 0.001 and width_diff < 0.001:
                print("   ✅ Positioning calculations match expected values")
            else:
                print(
                    "   ❌ Positioning calculations don't match - this is the problem!"
                )

        # Cleanup
        plt.close(fig)
        plt.close(diag_fig)

        return True

    except Exception as e:
        print(f"   ❌ Figure analysis failed: {e}")
        return False


if __name__ == "__main__":
    success = diagnose_figure_layout()

    if success:
        print("\n🎯 Next steps:")
        print("1. Check the diagnostic image saved in tests/")
        print("2. Verify positioning calculations in section/plotting/main.py")
        print("3. Look for axis sizing or limit issues")
    else:
        print("\n❌ Diagnosis failed - check errors above")

    exit(0 if success else 1)
