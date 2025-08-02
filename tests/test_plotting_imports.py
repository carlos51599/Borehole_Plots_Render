"""
Test script for plotting.py module imports and basic functionality.
"""

try:
    print("Testing plotting.py module import...")
    from borehole_log.plotting import draw_text_box, draw_geological_layer

    print("✅ draw_text_box and draw_geological_layer functions imported successfully")

    # Test function signatures
    import inspect

    sig1 = inspect.signature(draw_text_box)
    sig2 = inspect.signature(draw_geological_layer)
    print(f"✅ draw_text_box signature: {sig1}")
    print(f"✅ draw_geological_layer signature: {sig2}")

    print("\nTesting geology dependencies...")
    from geology_code_utils import get_geology_color, get_geology_pattern

    print("✅ Geology utilities imported successfully")

    # Test geology functions
    color = get_geology_color("101", "#default")
    pattern = get_geology_pattern("101", None)
    print(f"✅ Geology code 101: color={color}, pattern={pattern}")

    print("\n✅ All plotting.py imports and dependencies working correctly!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
