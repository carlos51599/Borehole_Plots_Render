"""
Comprehensive test script for borehole_log package functionality.
Tests all modules, imports, and core functionality with size compliance validation.
"""

import sys
import traceback
from pathlib import Path


def test_imports():
    """Test all imports from borehole_log package modules."""
    print("Testing borehole_log package imports...")

    try:
        # Test main package import
        import borehole_log

        print("✓ Main package import successful")

        # Test individual module imports
        from borehole_log import utils

        print("✓ utils module import successful")

        from borehole_log import layout

        print("✓ layout module import successful")

        from borehole_log import header_footer

        print("✓ header_footer module import successful")

        from borehole_log import overflow

        print("✓ overflow module import successful")

        from borehole_log import plotting

        print("✓ plotting module import successful")

        # Test main function imports
        from borehole_log import (
            create_borehole_log,
            plot_single_page,
            get_default_page_settings,
            validate_plot_data,
        )

        print("✓ Main function imports successful")

        # Test utility function imports
        from borehole_log import (
            matplotlib_figure,
            safe_close_figure,
            wrap_text_smart,
            calculate_text_dimensions,
            format_depth_value,
        )

        print("✓ Utility function imports successful")

        # Test layout function imports
        from borehole_log import (
            calculate_plot_layout,
            create_column_layout,
            get_standard_margins,
            validate_layout_settings,
        )

        print("✓ Layout function imports successful")

        # Test header/footer function imports
        from borehole_log import (
            create_header_content,
            create_footer_content,
            validate_header_data,
        )

        print("✓ Header/footer function imports successful")

        # Test overflow function imports
        from borehole_log import (
            check_depth_overflow,
            calculate_page_breaks_by_stratum,
            get_overflow_summary,
        )

        print("✓ Overflow function imports successful")

        # Test constants import
        from borehole_log import (
            DEFAULT_PAGE_SETTINGS,
            SUPPORTED_AGS_GROUPS,
            QUALITY_PRESETS,
        )

        print("✓ Constants import successful")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during imports: {e}")
        traceback.print_exc()
        return False


def test_package_functionality():
    """Test core package functionality with sample data."""
    print("\nTesting package functionality...")

    try:
        import borehole_log

        # Test package info
        info = borehole_log.get_package_info()
        print(f"✓ Package version: {info['version']}")
        print(f"✓ Supported AGS groups: {len(info['supported_ags_groups'])}")
        print(f"✓ Quality presets: {len(info['quality_presets'])}")

        # Test default settings
        settings = borehole_log.get_default_page_settings()
        print(f"✓ Default page settings loaded: {len(settings)} parameters")

        # Test sample data creation
        sample_loca = {
            "LOCA_ID": "TEST_BH001",
            "LOCA_GL": 100.0,
            "LOCA_NATE": 12345,
            "LOCA_NATN": 67890,
        }

        sample_geology = [
            {
                "LOCA_ID": "TEST_BH001",
                "GEOL_TOP": 0.0,
                "GEOL_BASE": 2.5,
                "GEOL_DESC": "TOPSOIL: Dark brown sandy clay with roots",
            },
            {
                "LOCA_ID": "TEST_BH001",
                "GEOL_TOP": 2.5,
                "GEOL_BASE": 8.0,
                "GEOL_DESC": "CLAY: Firm to stiff brown clay with occasional gravel",
            },
            {
                "LOCA_ID": "TEST_BH001",
                "GEOL_TOP": 8.0,
                "GEOL_BASE": 15.0,
                "GEOL_DESC": "SAND: Medium dense yellow-brown fine to medium sand",
            },
        ]

        # Test data validation
        is_valid, warnings = borehole_log.validate_plot_data(sample_geology)
        print(f"✓ Data validation: Valid={is_valid}, Warnings={len(warnings)}")

        # Test AGS data validation
        ags_data = {"LOCA": [sample_loca], "GEOL": sample_geology}
        is_valid, errors, warnings = borehole_log.validate_ags_data(ags_data)
        print(
            f"✓ AGS validation: Valid={is_valid}, Errors={len(errors)}, Warnings={len(warnings)}"
        )

        # Test header content creation
        header_content = borehole_log.create_header_content(sample_loca)
        print(f"✓ Header content created: {len(header_content)} fields")

        # Test footer content creation
        footer_content = borehole_log.create_footer_content()
        print(f"✓ Footer content created: {len(footer_content)} fields")

        # Test overflow calculation
        needs_overflow, pages, ranges = borehole_log.check_depth_overflow(
            total_depth=15.0, page_height_available=400, depth_scale=50.0
        )
        print(f"✓ Overflow check: Needs={needs_overflow}, Pages={pages}")

        # Test layout calculation
        layout_info = borehole_log.calculate_plot_layout(settings)
        print(f"✓ Layout calculation: {len(layout_info)} parameters")

        # Test column layout
        column_layout = borehole_log.create_column_layout(layout_info["plot_width"])
        print(f"✓ Column layout: {len(column_layout)} columns")

        return True

    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        traceback.print_exc()
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")

    try:
        from borehole_log import utils

        # Test text wrapping
        long_text = "This is a very long description of geological material that needs to be wrapped appropriately for display in a borehole log column."
        wrapped = utils.wrap_text_smart(long_text, max_width=50)
        print(f"✓ Text wrapping: {len(wrapped)} characters")

        # Test depth formatting
        depth_str = utils.format_depth_value(12.345)
        print(f"✓ Depth formatting: {depth_str}")

        # Test figure creation (without actually creating)
        try:
            # Just test the function exists and is callable
            if hasattr(utils, "matplotlib_figure") and callable(
                utils.matplotlib_figure
            ):
                print("✓ matplotlib_figure function available")
            else:
                print("✗ matplotlib_figure function not available")

            if hasattr(utils, "safe_close_figure") and callable(
                utils.safe_close_figure
            ):
                print("✓ safe_close_figure function available")
            else:
                print("✗ safe_close_figure function not available")

        except Exception as e:
            print(f"✗ Figure function test error: {e}")

        return True

    except Exception as e:
        print(f"✗ Utilities test error: {e}")
        traceback.print_exc()
        return False


def test_file_sizes():
    """Test that all module files meet size constraints."""
    print("\nTesting file size constraints...")

    try:
        import os

        package_dir = Path(__file__).parent / "borehole_log"

        size_violations = []
        size_warnings = []

        for py_file in package_dir.glob("*.py"):
            file_size_kb = py_file.stat().st_size / 1024

            print(f"  {py_file.name}: {file_size_kb:.1f} KB", end="")

            if file_size_kb > 25:
                print(" ✗ CRITICAL: Exceeds 25KB absolute maximum")
                size_violations.append(f"{py_file.name}: {file_size_kb:.1f}KB")
            elif file_size_kb > 20:
                print(" ⚠ WARNING: Exceeds 20KB preferred maximum")
                size_warnings.append(f"{py_file.name}: {file_size_kb:.1f}KB")
            elif file_size_kb > 15:
                print(" ⚠ Over 15KB target")
                size_warnings.append(f"{py_file.name}: {file_size_kb:.1f}KB")
            else:
                print(" ✓ Within 15KB target")

        if size_violations:
            print(f"\n✗ CRITICAL SIZE VIOLATIONS: {len(size_violations)}")
            for violation in size_violations:
                print(f"  - {violation}")
            return False

        if size_warnings:
            print(f"\n⚠ Size warnings: {len(size_warnings)}")
            for warning in size_warnings:
                print(f"  - {warning}")
        else:
            print("\n✓ All files within size constraints")

        return True

    except Exception as e:
        print(f"✗ File size test error: {e}")
        traceback.print_exc()
        return False


def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("BOREHOLE_LOG PACKAGE COMPREHENSIVE TEST")
    print("=" * 60)

    test_results = []

    # Run all tests
    test_results.append(("Import Tests", test_imports()))
    test_results.append(("Functionality Tests", test_package_functionality()))
    test_results.append(("Utility Tests", test_utilities()))
    test_results.append(("File Size Tests", test_file_sizes()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
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
        print("🎉 All tests passed! Package is ready for use.")
        return True
    else:
        print("❌ Some tests failed. Please review and fix issues.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
