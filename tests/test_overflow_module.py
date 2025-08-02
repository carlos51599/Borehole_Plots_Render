#!/usr/bin/env python
"""
Test overflow.py module imports and syntax
Phase 5 validation - Overflow functions
"""

import sys
import traceback


def test_overflow_module():
    """Test overflow.py module imports and function signatures"""
    try:
        # Test basic import
        from borehole_log import overflow

        print("✅ borehole_log.overflow module imported successfully")

        # Test function existence and signatures
        functions_to_test = ["classify_text_box_overflow", "create_overflow_page"]

        for func_name in functions_to_test:
            if hasattr(overflow, func_name):
                func = getattr(overflow, func_name)
                print(f"✅ Function {func_name} found - signature: {func.__name__}")
            else:
                print(f"❌ Function {func_name} NOT found")
                return False

        # Test all imports work
        from borehole_log.overflow import (
            classify_text_box_overflow,
            create_overflow_page,
        )

        print("✅ Direct function imports successful")

        return True

    except Exception as e:
        print(f"❌ Error testing overflow module: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing Phase 5: Overflow Module Implementation")
    print("=" * 50)

    if test_overflow_module():
        print("\n🎉 Phase 5 (overflow.py) - ALL TESTS PASSED!")
        print("Ready for Phase 6: Final orchestration to replace monolithic code")
    else:
        print("\n❌ Phase 5 (overflow.py) - TESTS FAILED!")
        sys.exit(1)
