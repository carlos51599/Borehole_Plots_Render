#!/usr/bin/env python3
"""
Test Modular File Upload System
Test the new modular file upload structure for functionality and imports.
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.abspath("."))


def test_modular_file_upload_imports():
    """Test that the modular file upload components can be imported."""
    print("Testing modular file upload imports...")

    # Test validation module
    try:
        from callbacks.file_upload.validation import (
            validate_total_upload_size,
            validate_individual_file_size,
            validate_file_content_security,
        )

        print("✓ Validation module imports successful")
    except Exception as e:
        print(f"❌ Validation module import error: {e}")
        return False

    # Test processing module
    try:
        from callbacks.file_upload.processing import (
            process_uploaded_files,
            load_and_optimize_borehole_data,
            transform_coordinates_and_create_markers,
            calculate_optimal_map_view,
        )

        print("✓ Processing module imports successful")
    except Exception as e:
        print(f"❌ Processing module import error: {e}")
        return False

    # Test UI components module
    try:
        from callbacks.file_upload.ui_components import (
            create_upload_summary,
            create_file_success_status,
            create_file_error_status,
        )

        print("✓ UI components module imports successful")
    except Exception as e:
        print(f"❌ UI components module import error: {e}")
        return False

    # Test main module
    try:
        from callbacks.file_upload.main import FileUploadCallback

        print("✓ Main module imports successful")
    except Exception as e:
        print(f"❌ Main module import error: {e}")
        return False

    # Test package import
    try:
        from callbacks.file_upload import FileUploadCallback as PkgFileUploadCallback

        print("✓ Package import successful")
        assert FileUploadCallback == PkgFileUploadCallback, "Import mismatch"
        print("✓ Package import consistency verified")
    except Exception as e:
        print(f"❌ Package import error: {e}")
        return False

    return True


def test_old_vs_new_import():
    """Test that old import still works vs new modular structure."""
    print("\nTesting import compatibility...")

    # Test old-style import from callbacks package
    try:
        from callbacks import FileUploadCallback as OldImport

        print("✓ Old-style import still works")
    except Exception as e:
        print(f"❌ Old-style import failed: {e}")
        return False

    # Test new modular import
    try:
        from callbacks.file_upload import FileUploadCallback as NewImport

        print("✓ New modular import works")
    except Exception as e:
        print(f"❌ New modular import failed: {e}")
        return False

    # Verify they're the same class
    try:
        assert OldImport == NewImport, "Import classes don't match"
        print("✓ Import compatibility verified")
    except Exception as e:
        print(f"❌ Import compatibility error: {e}")
        return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("MODULAR FILE UPLOAD TESTING")
    print("=" * 60)

    # Test imports
    imports_ok = test_modular_file_upload_imports()

    # Test compatibility
    compat_ok = test_old_vs_new_import()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if imports_ok and compat_ok:
        print("🎉 All tests passed! Modular file upload is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
