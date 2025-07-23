#!/usr/bin/env python3
"""
Phase 4 Baseline Test - Critical Files Functionality
Test current state before refactoring remaining critical files.
"""

import sys
import os
import traceback

# Add current directory to Python path (remove parent to avoid conflicts)
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(current_dir)
sys.path.insert(0, workspace_root)


def test_critical_file_imports():
    """Test that all critical files can be imported successfully."""
    print("=" * 80)
    print("PHASE 4 BASELINE TESTS")
    print("=" * 80)

    test_results = []

    # Test 1: borehole_log_professional.py
    print("Testing borehole_log_professional.py imports...")
    try:
        from borehole_log_professional import plot_borehole_log_from_ags_content

        print("✓ borehole_log_professional import successful")
        assert callable(
            plot_borehole_log_from_ags_content
        ), "plot_borehole_log_from_ags_content not callable"
        print("✓ plot_borehole_log_from_ags_content is callable")
        test_results.append(("Borehole Log Professional", True))
    except Exception as e:
        print(f"❌ borehole_log_professional error: {e}")
        test_results.append(("Borehole Log Professional", False))

    # Test 2: callbacks/file_upload.py
    print("\nTesting callbacks/file_upload.py imports...")
    try:
        from callbacks.file_upload import FileUploadCallback

        print("✓ callbacks.file_upload import successful")
        assert callable(FileUploadCallback), "FileUploadCallback not callable"
        print("✓ FileUploadCallback is callable")
        test_results.append(("Callbacks File Upload", True))
    except Exception as e:
        print(f"❌ callbacks.file_upload error: {e}")
        test_results.append(("Callbacks File Upload", False))

    # Test 3: section/plotting.py
    print("\nTesting section/plotting.py imports...")
    try:
        from section.plotting import plot_section_from_ags_content

        print("✓ section.plotting import successful")
        assert callable(
            plot_section_from_ags_content
        ), "plot_section_from_ags_content not callable"
        print("✓ plot_section_from_ags_content is callable")
        test_results.append(("Section Plotting", True))
    except Exception as e:
        print(f"❌ section.plotting error: {e}")
        test_results.append(("Section Plotting", False))

    # Test 4: app.py
    print("\nTesting app.py imports...")
    try:
        import app

        print("✓ app.py import successful")
        assert hasattr(app, "app"), "app.app not found"
        print("✓ app.app object exists")
        test_results.append(("Main App", True))
    except Exception as e:
        print(f"❌ app.py error: {e}")
        test_results.append(("Main App", False))

    # Test 5: config.py
    print("\nTesting config.py imports...")
    try:
        import config

        print("✓ config.py import successful")
        # Check some key config items
        expected_attrs = [
            "DEFAULT_BUFFER_DISTANCE",
            "DEFAULT_MARKER_SIZE",
            "LOGGING_CONFIG",
        ]
        for attr in expected_attrs:
            if hasattr(config, attr):
                print(f"✓ config.{attr} exists")
            else:
                print(f"⚠ config.{attr} missing")
        test_results.append(("Config", True))
    except Exception as e:
        print(f"❌ config.py error: {e}")
        test_results.append(("Config", False))

    return test_results


if __name__ == "__main__":
    print("Phase 4 Baseline Testing - Critical Files")
    print("Testing functionality before refactoring critical files...")

    test_results = test_critical_file_imports()

    print("\n" + "=" * 80)
    print("PHASE 4 BASELINE TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")

    print(f"\nOVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Current state is stable. Safe to proceed with refactoring.")
    else:
        print("⚠️ Some tests failed. Address issues before refactoring.")

    sys.exit(0 if passed == total else 1)
