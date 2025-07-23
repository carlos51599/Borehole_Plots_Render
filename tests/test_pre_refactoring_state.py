"""
Comprehensive test script to validate all current imports and modules before refactoring.
Tests the existing state to ensure we understand what's working.
"""

import sys
import traceback
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_current_modular_callbacks():
    """Test that the modular callbacks system works."""
    print("Testing modular callbacks system...")

    try:
        # Test callbacks package import
        import callbacks

        print("✓ callbacks package import successful")

        # Test individual callback modules
        from callbacks import file_upload, map_interactions, marker_handling
        from callbacks import search_functionality, plot_generation, base

        print("✓ Individual callback modules import successful")

        # Test that register_callbacks exists
        if hasattr(callbacks, "register_callbacks"):
            print("✓ callbacks.register_callbacks function available")
        else:
            print("✗ callbacks.register_callbacks function NOT available")

        return True

    except Exception as e:
        print(f"✗ Modular callbacks test error: {e}")
        traceback.print_exc()
        return False


def test_current_borehole_log():
    """Test borehole log functionality."""
    print("\nTesting borehole log systems...")

    try:
        # Test new modular borehole_log package
        import borehole_log

        print("✓ New borehole_log package import successful")

        # Test old monolithic file
        from borehole_log_professional import plot_borehole_log_from_ags_content

        print("✓ Old borehole_log_professional import successful")

        return True

    except Exception as e:
        print(f"✗ Borehole log test error: {e}")
        traceback.print_exc()
        return False


def test_current_section_modules():
    """Test section modules."""
    print("\nTesting section modules...")

    try:
        # Test section package
        import section

        print("✓ section package import successful")

        from section import plotting, parsing, utils

        print("✓ section modules import successful")

        return True

    except Exception as e:
        print(f"✗ Section modules test error: {e}")
        traceback.print_exc()
        return False


def test_main_app_components():
    """Test main application components."""
    print("\nTesting main app components...")

    try:
        # Test main imports used by app.py
        import config

        print("✓ config import successful")

        import app_factory

        print("✓ app_factory import successful")

        # Test if we can import the old callbacks_split
        from callbacks_split import register_callbacks

        print("✓ callbacks_split.register_callbacks import successful")

        return True

    except Exception as e:
        print(f"✗ Main app components test error: {e}")
        traceback.print_exc()
        return False


def run_pre_refactoring_tests():
    """Run all pre-refactoring tests."""
    print("=" * 60)
    print("PRE-REFACTORING STATE VALIDATION")
    print("=" * 60)

    test_results = []

    test_results.append(("Modular Callbacks", test_current_modular_callbacks()))
    test_results.append(("Borehole Log Systems", test_current_borehole_log()))
    test_results.append(("Section Modules", test_current_section_modules()))
    test_results.append(("Main App Components", test_main_app_components()))

    # Summary
    print("\n" + "=" * 60)
    print("PRE-REFACTORING TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1

    print(f"\nOVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Current state is stable. Safe to proceed with refactoring.")
        return True
    else:
        print("❌ Some systems not working. Fix issues before refactoring.")
        return False


if __name__ == "__main__":
    success = run_pre_refactoring_tests()
    sys.exit(0 if success else 1)
