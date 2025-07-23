"""
Test script to validate that app.py works with the updated modular callbacks.
"""

import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_app_imports():
    """Test that app.py can import everything it needs."""
    print("Testing app.py imports...")

    try:
        # Test the main imports from app.py
        import dash

        print("✓ dash import successful")

        from dash import html, dcc

        print("✓ dash components import successful")

        import dash_leaflet as dl

        print("✓ dash_leaflet import successful")

        import config

        print("✓ config import successful")

        from callbacks import register_callbacks

        print("✓ callbacks.register_callbacks import successful")

        from app_factory import create_app_with_duplicate_callbacks

        print("✓ app_factory import successful")

        # Test that we can call the register_callbacks function
        if callable(register_callbacks):
            print("✓ register_callbacks is callable")
        else:
            print("✗ register_callbacks is not callable")
            return False

        return True

    except Exception as e:
        print(f"✗ App imports test error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_app_can_be_imported():
    """Test that we can import app.py without errors."""
    print("\nTesting app.py module import...")

    try:
        # This should work without creating the actual Dash app
        import app

        print("✓ app.py import successful")

        # Check if it has the expected functions/variables
        if hasattr(app, "app"):
            print("✓ app.app object exists")

        return True

    except Exception as e:
        print(f"✗ App module import error: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_app_tests():
    """Run all app-related tests."""
    print("=" * 60)
    print("APP MODULE TESTS")
    print("=" * 60)

    test_results = []

    test_results.append(("App Imports", test_app_imports()))
    test_results.append(("App Module Import", test_app_can_be_imported()))

    # Summary
    print("\n" + "=" * 60)
    print("APP TEST SUMMARY")
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
        print("🎉 App module is working correctly!")
        return True
    else:
        print("❌ App module has issues.")
        return False


if __name__ == "__main__":
    success = run_app_tests()
    sys.exit(0 if success else 1)
