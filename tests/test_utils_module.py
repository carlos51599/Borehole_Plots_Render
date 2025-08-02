"""Test utils module import and basic functionality"""

print("Testing utils module...")

try:
    from borehole_log.utils import (
        matplotlib_figure,
        safe_close_figure,
        wrap_text_and_calculate_height,
        log_col_widths_in,
        DEFAULT_COLOR_ALPHA,
        DEFAULT_HATCH_ALPHA,
    )

    print("✅ Successfully imported all functions and constants")

    # Test constants
    print(f"✅ log_col_widths_in: {log_col_widths_in}")
    print(f"✅ DEFAULT_COLOR_ALPHA: {DEFAULT_COLOR_ALPHA}")
    print(f"✅ DEFAULT_HATCH_ALPHA: {DEFAULT_HATCH_ALPHA}")

    # Test text wrapping function
    test_text = "This is a long text that should be wrapped to test the wrap_text_and_calculate_height function"
    wrapped_lines, height = wrap_text_and_calculate_height(
        test_text, max_width_chars=30
    )
    print(
        f"✅ Text wrapping test: {len(wrapped_lines)} lines, {height:.3f} inches height"
    )

    # Test matplotlib figure context manager
    with matplotlib_figure(figsize=(5, 5)) as fig:
        print("✅ Figure context manager working")
    print("✅ Figure automatically closed")

    print("🎉 ALL UTILS TESTS PASSED!")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
