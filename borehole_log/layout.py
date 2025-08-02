# Professional Borehole Log Layout Module
#
# This module provides text positioning and geological layer alignment calculations
# extracted from the monolithic borehole_log_professional.py implementation.
#
# Phase 2 of 6-phase modularization: Text positioning and geological layer alignment

from .utils import wrap_text_and_calculate_height


def calculate_text_box_positions_aligned(
    intervals, legend_positions, desc_left, desc_width
):
    """
    Calculate text box positions aligned with their geological layers,
    with adjustments for conflicts.

    Args:
        intervals: List of interval dictionaries with lithology data
        legend_positions: List of legend position dictionaries with y_top, y_bottom
        desc_left: Left edge of description column
        desc_width: Width of description column

    Returns:
        list: Text box positions with y_top, y_bottom, x_left, x_width for each interval
    """
    text_positions = []

    # Use full width of description column
    text_box_width = desc_width
    text_box_left = desc_left

    for i, (interval, legend_pos) in enumerate(zip(intervals, legend_positions)):
        # Calculate wrapped text height
        wrapped_lines, text_height = wrap_text_and_calculate_height(
            interval.get("Description", ""), max_width_chars=45
        )

        if legend_pos["y_center"] > 0:  # Valid legend position
            # Start with layer boundaries as default position
            layer_y_top = legend_pos["y_top"]
            layer_y_bottom = legend_pos["y_bottom"]
            layer_height = layer_y_top - layer_y_bottom

            # Default position: align with layer boundaries
            preferred_y_top = layer_y_top

            # Check if text fits within the layer
            if text_height <= layer_height:
                # Text fits within layer - extend text box to match layer's bottom boundary
                final_y_top = preferred_y_top
                final_y_bottom = layer_y_bottom  # Extend to layer's bottom boundary
                # Update text_height to reflect the extended box height
                extended_text_height = final_y_top - final_y_bottom
            else:
                # Text is too tall for layer - extend beyond layer boundary
                final_y_top = preferred_y_top
                final_y_bottom = preferred_y_top - text_height  # Extend to fit all text
                extended_text_height = text_height

        else:
            # No valid legend position - shouldn't happen, but handle gracefully
            final_y_top = 0
            final_y_bottom = -text_height
            extended_text_height = text_height

        text_positions.append(
            {
                "interval_idx": i,
                "y_top": final_y_top,
                "y_bottom": final_y_bottom,
                "x_left": text_box_left,
                "x_width": text_box_width,
                "wrapped_lines": wrapped_lines,
                "text_height": extended_text_height,  # Use extended height for drawing
                "original_text_height": text_height,  # Keep original for text positioning
                "layer_y_top": legend_pos.get("y_top", 0),
                "layer_y_bottom": legend_pos.get("y_bottom", 0),
            }
        )

    # Second pass: resolve conflicts with cascading push-down effect
    # Keep adjusting until no more conflicts exist
    conflicts_resolved = False
    max_iterations = len(text_positions) * 2  # Prevent infinite loops
    iteration = 0

    while not conflicts_resolved and iteration < max_iterations:
        conflicts_resolved = True
        iteration += 1

        for i in range(1, len(text_positions)):
            current = text_positions[i]
            previous = text_positions[i - 1]

            # Check if current text box overlaps with previous
            # Overlap occurs when current y_top is above previous y_bottom
            if current["y_top"] > previous["y_bottom"]:
                # Overlap detected - push current text box down
                current["y_top"] = (
                    previous["y_bottom"] - 0.001
                )  # Small gap to prevent infinite loops
                current["y_bottom"] = current["y_top"] - current["original_text_height"]

                # Check if the pushed-down text box is still within its layer's boundaries
                # If so, extend it to match the layer's bottom boundary
                if current["y_bottom"] > current["layer_y_bottom"]:
                    # Text box bottom is still above layer bottom - extend it
                    current["y_bottom"] = current["layer_y_bottom"]

                # Update the extended height after repositioning
                current["text_height"] = current["y_top"] - current["y_bottom"]
                conflicts_resolved = (
                    False  # Need another pass to check cascading effects
                )

    return text_positions
