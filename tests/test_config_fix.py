"""
Comprehensive test script to validate fixes and identify remaining issues.

This script will:
1. Test config import and SEARCH_ZOOM_LEVEL availability
2. Analyze marker click callback registration
3. Test application startup to identify any remaining issues
4. Generate a detailed report

Author: Debug Assistant
Created: July 2025
"""

import sys
import traceback
from datetime import datetime


def test_config_import():
    """Test config import and SEARCH_ZOOM_LEVEL constant."""
    print("=" * 60)
    print("TESTING CONFIG IMPORT AND SEARCH_ZOOM_LEVEL")
    print("=" * 60)

    try:
        # Test basic config import
        print("1. Testing basic config import...")
        import config

        print("✓ Config module imported successfully")

        # Test SEARCH_ZOOM_LEVEL specifically
        print("2. Testing SEARCH_ZOOM_LEVEL access...")
        zoom_level = config.SEARCH_ZOOM_LEVEL
        print(f"✓ SEARCH_ZOOM_LEVEL = {zoom_level}")

        # Test other key constants
        print("3. Testing other key config constants...")
        app_title = config.APP_TITLE
        map_height = config.MAP_HEIGHT
        print(f"✓ APP_TITLE = {app_title}")
        print(f"✓ MAP_HEIGHT = {map_height}")

        # Test styling constants
        print("4. Testing styling constants...")
        header_style = config.HEADER_H1_CENTER_STYLE
        button_style = config.BUTTON_CENTER_STYLE
        print(f"✓ HEADER_H1_CENTER_STYLE keys: {list(header_style.keys())}")
        print(f"✓ BUTTON_CENTER_STYLE keys: {list(button_style.keys())}")

        print("\n✅ CONFIG TEST PASSED - All constants accessible")
        return True

    except ImportError as e:
        print(f"❌ CONFIG IMPORT FAILED: {e}")
        return False
    except AttributeError as e:
        print(f"❌ CONFIG ATTRIBUTE ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED CONFIG ERROR: {e}")
        traceback.print_exc()
        return False


def test_callback_imports():
    """Test callback module imports."""
    print("\n" + "=" * 60)
    print("TESTING CALLBACK MODULE IMPORTS")
    print("=" * 60)

    callback_modules = [
        "callbacks.search_functionality",
        "callbacks.marker_handling",
        "callbacks.map_interactions",
    ]

    results = {}

    for module_name in callback_modules:
        try:
            print(f"Testing import of {module_name}...")
            module = __import__(module_name, fromlist=[""])
            print(f"✓ {module_name} imported successfully")

            # Check for callback registration functions
            if hasattr(module, "register_callbacks"):
                print(f"  ✓ {module_name} has register_callbacks function")
            else:
                print(f"  ⚠ {module_name} missing register_callbacks function")

            results[module_name] = True

        except Exception as e:
            print(f"❌ {module_name} import failed: {e}")
            traceback.print_exc()
            results[module_name] = False

    return results


def analyze_marker_handling():
    """Analyze marker handling callback structure."""
    print("\n" + "=" * 60)
    print("ANALYZING MARKER HANDLING CALLBACK STRUCTURE")
    print("=" * 60)

    try:
        import callbacks.marker_handling as marker_mod

        # Get the module's source file path
        print(f"Marker handling module file: {marker_mod.__file__}")

        # Check for key functions/variables
        attrs = dir(marker_mod)
        callback_related = [
            attr
            for attr in attrs
            if "callback" in attr.lower() or "marker" in attr.lower()
        ]
        print(f"Callback-related attributes: {callback_related}")

        return True

    except Exception as e:
        print(f"❌ Marker handling analysis failed: {e}")
        traceback.print_exc()
        return False


def test_app_startup():
    """Test basic app startup without running server."""
    print("\n" + "=" * 60)
    print("TESTING APPLICATION STARTUP")
    print("=" * 60)

    try:
        print("1. Testing app_factory import...")
        import app_factory

        print("✓ app_factory imported successfully")

        print("2. Testing create_app function...")
        if hasattr(app_factory, "create_app"):
            print("✓ create_app function found")
        else:
            print("❌ create_app function not found")
            return False

        print("3. Testing app creation (without running)...")
        # We'll try to create the app but not run it
        app = app_factory.create_app()
        if app:
            print("✓ App created successfully")
            print(f"  - App title: {app.title if hasattr(app, 'title') else 'Not set'}")
            return True
        else:
            print("❌ App creation returned None")
            return False

    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests and generate report."""
    print("COMPREHENSIVE APPLICATION TEST SUITE")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    print("=" * 80)

    results = {}

    # Run all tests
    results["config_import"] = test_config_import()
    results["callback_imports"] = test_callback_imports()
    results["marker_analysis"] = analyze_marker_handling()
    results["app_startup"] = test_app_startup()

    # Generate summary report
    print("\n" + "=" * 80)
    print("TEST SUMMARY REPORT")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v is True)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} : {status}")

    print("-" * 40)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Config fix appears successful.")
    else:
        print("⚠️  Some tests failed. Review issues above.")

    print(f"\nTest completed at: {datetime.now()}")


if __name__ == "__main__":
    main()
