"""
Test script for app_modules modular structure.

This script validates that the new modular app structure maintains
all functionality and import compatibility.
"""

import sys
import traceback
from typing import List, Tuple


def test_module_imports() -> Tuple[bool, List[str]]:
    """Test app_modules imports."""
    results = []
    success = True

    # Test individual module imports
    modules_to_test = [
        "app_modules.app_setup",
        "app_modules.layout",
        "app_modules.clientside_callbacks",
        "app_modules.server_callbacks",
        "app_modules.main",
        "app_modules",
    ]

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            results.append(f"✅ {module_name}: Import successful")
        except ImportError as e:
            results.append(f"❌ {module_name}: Import failed - {e}")
            success = False
        except Exception as e:
            results.append(f"❌ {module_name}: Unexpected error - {e}")
            success = False

    return success, results


def test_function_availability() -> Tuple[bool, List[str]]:
    """Test main function availability."""
    results = []
    success = True

    try:
        from app_modules import create_and_configure_app, create_app, main, get_app

        # Check functions are callable
        functions = [
            ("create_and_configure_app", create_and_configure_app),
            ("create_app", create_app),
            ("main", main),
            ("get_app", get_app),
        ]

        for name, func in functions:
            if callable(func):
                results.append(f"✅ {name}: Function available and callable")
            else:
                results.append(f"❌ {name}: Function not callable")
                success = False

    except ImportError as e:
        results.append(f"❌ Function import failed: {e}")
        success = False
    except Exception as e:
        results.append(f"❌ Unexpected error testing functions: {e}")
        success = False

    return success, results


def test_app_creation() -> Tuple[bool, List[str]]:
    """Test application creation without starting server."""
    results = []
    success = True

    try:
        from app_modules import create_and_configure_app

        # Create app (but don't start it)
        app = create_and_configure_app()

        if app is not None:
            results.append("✅ App creation: Success")

            # Check if app has required attributes
            if hasattr(app, "layout"):
                results.append("✅ App layout: Present")
            else:
                results.append("❌ App layout: Missing")
                success = False

            if hasattr(app, "server"):
                results.append("✅ App server: Present")
            else:
                results.append("❌ App server: Missing")
                success = False

        else:
            results.append("❌ App creation: Failed - returned None")
            success = False

    except Exception as e:
        results.append(f"❌ App creation error: {e}")
        success = False

    return success, results


def test_new_app_import() -> Tuple[bool, List[str]]:
    """Test importing the new app.py file."""
    results = []
    success = True

    try:
        # Test importing app_new.py
        import app_new

        if hasattr(app_new, "app"):
            results.append("✅ app_new.app: Available")

            # Check if app is properly configured
            if hasattr(app_new.app, "layout"):
                results.append("✅ app_new.app.layout: Present")
            else:
                results.append("❌ app_new.app.layout: Missing")
                success = False

        else:
            results.append("❌ app_new.app: Not available")
            success = False

    except Exception as e:
        results.append(f"❌ app_new import error: {e}")
        success = False

    return success, results


def test_backward_compatibility() -> Tuple[bool, List[str]]:
    """Test backward compatibility."""
    results = []
    success = True

    try:
        # Test if we can import and use like the original app.py
        import app_new

        # Check if the app can be accessed like the original
        if hasattr(app_new, "app"):
            results.append("✅ Backward compatibility: app object accessible")
        else:
            results.append("❌ Backward compatibility: app object not accessible")
            success = False

    except Exception as e:
        results.append(f"❌ Backward compatibility error: {e}")
        success = False

    return success, results


def main():
    """Run all tests and report results."""
    print("Testing app_modules modular structure...")
    print("=" * 60)

    all_success = True

    # Test 1: Module imports
    print("\n1. Testing module imports:")
    success, results = test_module_imports()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 2: Function availability
    print("\n2. Testing function availability:")
    success, results = test_function_availability()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 3: App creation
    print("\n3. Testing app creation:")
    success, results = test_app_creation()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 4: New app import
    print("\n4. Testing new app import:")
    success, results = test_new_app_import()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 5: Backward compatibility
    print("\n5. Testing backward compatibility:")
    success, results = test_backward_compatibility()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Final result
    print("\n" + "=" * 60)
    if all_success:
        print("🎉 ALL TESTS PASSED - Modular app structure is working correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Test script error: {e}")
        traceback.print_exc()
        sys.exit(1)
