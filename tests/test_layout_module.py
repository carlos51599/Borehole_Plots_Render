"""Test layout module import and basic functionality"""

print("Testing layout module...")

try:
    from borehole_log.layout import calculate_text_box_positions_aligned
    from borehole_log.utils import log_col_widths_in

    print("✅ Successfully imported layout functions")

    # Test with mock data
    mock_intervals = [
        {"Description": "Dense sandy clay with some gravel"},
        {"Description": "Very soft clay with organic matter and shells"},
    ]

    mock_legend_positions = [
        {"y_top": 10.0, "y_bottom": 8.0, "y_center": 9.0},
        {"y_top": 8.0, "y_bottom": 6.0, "y_center": 7.0},
    ]

    # Test layout calculation
    positions = calculate_text_box_positions_aligned(
        mock_intervals, mock_legend_positions, desc_left=5.0, desc_width=3.0
    )

    print(f"✅ Layout calculation test: {len(positions)} text boxes positioned")
    for i, pos in enumerate(positions):
        print(f"   Box {i}: y_top={pos['y_top']:.2f}, y_bottom={pos['y_bottom']:.2f}")

    print("🎉 ALL LAYOUT TESTS PASSED!")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
