"""
Test script for header_footer.py module imports and basic functionality.
"""

try:
    print("Testing header_footer.py module import...")
    from borehole_log.header_footer import draw_header

    print("✅ draw_header function imported successfully")

    # Test function signature
    import inspect

    sig = inspect.signature(draw_header)
    print(f"✅ Function signature: {sig}")

    print("\nTesting utils dependencies...")
    from borehole_log.utils import matplotlib_figure, log_col_widths_in

    print("✅ Utils dependencies imported successfully")

    print(f"✅ log_col_widths_in: {log_col_widths_in}")

    print("\n✅ All header_footer.py imports and dependencies working correctly!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
