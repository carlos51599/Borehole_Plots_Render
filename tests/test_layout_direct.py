#!/usr/bin/env python3
"""Test layout module import directly"""

try:
    print("Testing direct layout import...")
    import sys

    sys.path.insert(0, ".")

    from borehole_log.layout import calculate_text_box_positions_aligned

    print("✅ Direct import successful!")
    print(f"Function signature: {calculate_text_box_positions_aligned.__name__}")

except Exception as e:
    print(f"❌ Direct import failed: {e}")
    import traceback

    traceback.print_exc()
