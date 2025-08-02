"""
Debug script to identify what's causing the app import to hang.
Tests individual imports systematically to isolate the issue.
"""

import sys
import traceback


def test_import(module_name, description):
    """Test importing a module and report results."""
    try:
        print(f"Testing {description}...")
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"❌ {module_name} failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main debugging function."""
    print("=== Import Debugging Session ===")
    print("Testing individual modules to identify hanging issue...\n")

    # Test basic modules first
    modules_to_test = [
        ("config_modules", "Configuration modules"),
        ("app_constants", "App constants"),
        ("coordinate_service", "Coordinate service"),
        ("data_loader", "Data loader"),
        ("geology_code_utils", "Geology code utilities"),
        ("app_factory", "App factory"),
        ("app_modules", "App modules package"),
        ("callbacks", "Callbacks package"),
        ("section", "Section package"),
        ("state_management", "State management"),
    ]

    failed_modules = []

    for module_name, description in modules_to_test:
        if not test_import(module_name, description):
            failed_modules.append(module_name)
        print()  # Add spacing

    # Try the main app import if all dependencies passed
    if not failed_modules:
        print("All dependencies imported successfully!")
        print("Now testing main app import...")
        if test_import("app", "Main app module"):
            print("🎉 App import successful!")
        else:
            print("💥 App import failed even though dependencies worked!")
    else:
        print(f"Failed modules: {failed_modules}")
        print("Cannot test app import due to dependency failures.")


if __name__ == "__main__":
    main()
