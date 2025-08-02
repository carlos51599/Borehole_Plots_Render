#!/usr/bin/env python3
"""
Borehole Data Distribution Analysis
=================================

This test analyzes the actual borehole data distribution to understand
why the section plot appears to only use the left half of the figure.

The issue might be that the boreholes are clustered together in a small
area, leaving the rest of the plot empty.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from section.parsing import parse_ags_geol_section_from_string
import numpy as np


def analyze_borehole_distribution():
    """Analyze the actual distribution of borehole positions."""

    print("=== Borehole Data Distribution Analysis ===")
    print()

    # Load AGS data
    ags_file = "FLRG - 2025-03-17 1445 - Preliminary - 3.txt"

    try:
        with open(ags_file, "r", encoding="utf-8") as f:
            ags_content = f.read()
        print(f"✅ Loaded AGS file: {len(ags_content)} characters")

        # Parse AGS data
        geol_df, loca_df, _ = parse_ags_geol_section_from_string(ags_content)

        print(f"📊 Total boreholes: {len(loca_df)}")

        # Get coordinates
        x_coords = loca_df["LOCA_NATE"].values
        y_coords = loca_df["LOCA_NATN"].values
        borehole_ids = loca_df["LOCA_ID"].values

        print(f"📍 Coordinate ranges:")
        print(
            f"   Easting (X): {x_coords.min():.1f} to {x_coords.max():.1f} (span: {x_coords.max()-x_coords.min():.1f}m)"
        )
        print(
            f"   Northing (Y): {y_coords.min():.1f} to {y_coords.max():.1f} (span: {y_coords.max()-y_coords.min():.1f}m)"
        )

        # Test with different borehole selections
        test_scenarios = [
            ("First 3 boreholes", borehole_ids[:3]),
            (
                "Boreholes spread across range",
                [
                    borehole_ids[0],
                    borehole_ids[len(borehole_ids) // 2],
                    borehole_ids[-1],
                ],
            ),
            ("All boreholes", borehole_ids),
        ]

        for scenario_name, test_ids in test_scenarios:
            print(f"\n--- {scenario_name} ---")

            # Get coordinates for selected boreholes
            mask = np.isin(borehole_ids, test_ids)
            selected_x = x_coords[mask]
            selected_y = y_coords[mask]
            selected_ids = borehole_ids[mask]

            print(f"Selected boreholes: {list(selected_ids)}")
            print(f"X coordinates: {selected_x}")
            print(f"Y coordinates: {selected_y}")

            # Calculate relative positions (like the plotting code does)
            rel_x = (
                selected_x - selected_x[0]
            )  # Default: use easting as section orientation

            print(f"Relative X positions: {rel_x}")
            print(
                f"Relative X range: {rel_x.min():.1f} to {rel_x.max():.1f} (span: {rel_x.max()-rel_x.min():.1f}m)"
            )

            # Calculate what the axis limits would be
            total_length = rel_x.max() - rel_x.min() if len(rel_x) > 1 else 50.0
            x_start = rel_x.min() - total_length * 0.05
            x_end = rel_x.max() + total_length * 0.05

            print(f"Expected axis X limits: {x_start:.2f} to {x_end:.2f}")

            # Calculate data utilization of plot width
            if x_end > x_start:
                data_width = rel_x.max() - rel_x.min()
                axis_width = x_end - x_start
                utilization = data_width / axis_width * 100
                print(f"Data utilization: {utilization:.1f}% of axis width")

                if utilization < 50:
                    print(
                        "⚠️  Data uses less than 50% of axis width - this could appear as 'left half only'"
                    )
                else:
                    print("✅ Data uses good portion of axis width")

            # Check borehole spacing
            if len(rel_x) > 1:
                spacings = np.diff(np.sort(rel_x))
                avg_spacing = np.mean(spacings)
                print(f"Average borehole spacing: {avg_spacing:.1f}m")

                if avg_spacing < 5:
                    print(
                        "⚠️  Boreholes are very close together - plot may appear clustered"
                    )

        # Specific test with the original 3 boreholes from the issue
        print(f"\n--- ISSUE REPRODUCTION: First 3 boreholes analysis ---")
        issue_ids = ["LFDS2401", "LFDS2401A", "LFDS2402"]

        issue_mask = np.isin(borehole_ids, issue_ids)
        issue_x = x_coords[issue_mask]
        issue_y = y_coords[issue_mask]
        issue_ids_found = borehole_ids[issue_mask]

        print(f"Issue reproduction boreholes: {list(issue_ids_found)}")
        print(f"X coordinates: {issue_x}")
        print(f"Y coordinates: {issue_y}")

        # Calculate relative positions
        issue_rel_x = issue_x - issue_x[0]
        print(f"Relative X positions: {issue_rel_x}")

        # Check if they're clustered
        x_span = issue_rel_x.max() - issue_rel_x.min()
        print(f"X span of selected boreholes: {x_span:.1f}m")

        if x_span < 10:
            print(
                "❌ PROBLEM IDENTIFIED: Boreholes are clustered in a very small area!"
            )
            print(
                "   This makes the plot data appear only on the left side of the axis."
            )
            print(
                "   The axis spans the full width, but the data is concentrated in one area."
            )
        else:
            print("✅ Boreholes are well distributed")

        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print(
            f"The issue is likely that the selected boreholes have very similar coordinates,"
        )
        print(
            f"so they appear clustered together in the plot, leaving most of the axis empty."
        )
        print(
            f"This creates the visual impression that only the 'left half' is being used."
        )

        print(f"\n💡 SOLUTION SUGGESTIONS:")
        print(f"1. Select boreholes that are more spread out across the site")
        print(f"2. Use all boreholes for better distribution")
        print(f"3. Adjust axis limits to zoom in on the data area")
        print(f"4. Use automatic axis scaling based on actual data extent")

        return True

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False


if __name__ == "__main__":
    success = analyze_borehole_distribution()
    exit(0 if success else 1)
