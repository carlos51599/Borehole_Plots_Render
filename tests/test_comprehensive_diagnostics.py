"""
Comprehensive diagnostic test script for the current application state.

This script systematically tests:
1. Config module dependencies and imports
2. Error handling method availability
3. Borehole log functionality
4. Plot generation with different data types

Author: Debug Assistant
Created: July 2025
"""

import sys
import traceback
import os
from datetime import datetime

# Add project root to Python path
project_root = (
    os.path.dirname(os.path.abspath(__file__)).replace("tests", "").rstrip(os.sep)
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path updated: {project_root in sys.path}")


def test_config_dependencies():
    """Test config module dependencies - both monolithic and modular."""
    print("=" * 60)
    print("TESTING CONFIG DEPENDENCIES")
    print("=" * 60)

    # Test 1: Original config.py import
    try:
        print("1. Testing monolithic config.py import...")
        import config

        print("✓ config.py imported successfully")

        # Test key constants
        test_constants = [
            "SEARCH_ZOOM_LEVEL",
            "APP_TITLE",
            "MAP_HEIGHT",
            "HEADER_H1_CENTER_STYLE",
            "BUTTON_CENTER_STYLE",
        ]

        missing_constants = []
        for const in test_constants:
            if hasattr(config, const):
                value = getattr(config, const)
                print(f"  ✓ {const} = {type(value).__name__}({str(value)[:50]}...)")
            else:
                missing_constants.append(const)
                print(f"  ❌ {const} - MISSING")

        if missing_constants:
            print(f"❌ Missing {len(missing_constants)} constants from config.py")
            return False

    except Exception as e:
        print(f"❌ config.py import failed: {e}")
        return False

    # Test 2: Modular config_modules import
    try:
        print("\n2. Testing modular config_modules import...")
        import config_modules

        print("✓ config_modules package imported")

        # Test submodules
        submodules = ["figures", "layout", "sizing", "styles"]
        for module in submodules:
            try:
                submod = getattr(config_modules, module)
                print(f"  ✓ config_modules.{module} available")
            except AttributeError:
                print(f"  ❌ config_modules.{module} not available")

        return True

    except Exception as e:
        print(f"❌ config_modules import failed: {e}")
        return False


def test_error_handling_methods():
    """Test error handling methods and availability."""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING METHODS")
    print("=" * 60)

    try:
        from error_handling import get_error_handler, ErrorCategory

        error_handler = get_error_handler()

        print("✓ ErrorHandler imported successfully")

        # Check available methods
        methods = [
            method for method in dir(error_handler) if not method.startswith("_")
        ]
        print(f"Available methods: {methods}")

        # Test specific methods used in callbacks
        test_methods = ["handle_error", "handle_callback_error", "create_error"]

        for method in test_methods:
            if hasattr(error_handler, method):
                print(f"  ✓ {method} - available")
            else:
                print(f"  ❌ {method} - MISSING")

        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False


def test_borehole_log_functionality():
    """Test borehole log plotting functionality."""
    print("\n" + "=" * 60)
    print("TESTING BOREHOLE LOG FUNCTIONALITY")
    print("=" * 60)

    try:
        # Test import
        from borehole_log import plot_borehole_log_from_ags_content

        print("✓ plot_borehole_log_from_ags_content imported")

        # Test basic function signature
        import inspect

        sig = inspect.signature(plot_borehole_log_from_ags_content)
        print(f"Function signature: {sig}")

        return True

    except Exception as e:
        print(f"❌ Borehole log functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_plot_generation_imports():
    """Test plot generation callback imports."""
    print("\n" + "=" * 60)
    print("TESTING PLOT GENERATION IMPORTS")
    print("=" * 60)

    try:
        from callbacks.plot_generation import PlotGenerationCallback

        plot_callback = PlotGenerationCallback()
        print("✓ PlotGenerationCallback imported")

        # Check error handler
        if hasattr(plot_callback, "error_handler"):
            error_handler = plot_callback.error_handler
            print(f"✓ Error handler available: {type(error_handler)}")

            # Check methods
            if hasattr(error_handler, "handle_error"):
                print("  ✓ handle_error method available")
            elif hasattr(error_handler, "handle_callback_error"):
                print("  ⚠️ handle_callback_error available but handle_error missing")
            else:
                print("  ❌ No error handling methods found")

        return True

    except Exception as e:
        print(f"❌ Plot generation imports failed: {e}")
        traceback.print_exc()
        return False


def test_section_plotting():
    """Test section plotting functionality."""
    print("\n" + "=" * 60)
    print("TESTING SECTION PLOTTING")
    print("=" * 60)

    try:
        from section import plot_section_from_ags_content

        print("✓ plot_section_from_ags_content imported")

        # Test return type expectations
        import inspect

        sig = inspect.signature(plot_section_from_ags_content)
        print(f"Function signature: {sig}")

        return True

    except Exception as e:
        print(f"❌ Section plotting test failed: {e}")
        traceback.print_exc()
        return False


def test_figure_types():
    """Test matplotlib figure handling."""
    print("\n" + "=" * 60)
    print("TESTING FIGURE TYPE HANDLING")
    print("=" * 60)

    try:
        import matplotlib.pyplot as plt

        # Create test figure
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Plot")

        print(f"✓ Created figure type: {type(fig)}")
        print(f"Figure has savefig method: {hasattr(fig, 'savefig')}")

        # Test what happens when we get a string instead
        test_string = "This is a string, not a figure"
        print(f"String type: {type(test_string)}")
        print(f"String has savefig method: {hasattr(test_string, 'savefig')}")

        plt.close(fig)
        return True

    except Exception as e:
        print(f"❌ Figure type test failed: {e}")
        return False


def main():
    """Run all diagnostic tests."""
    print("COMPREHENSIVE APPLICATION DIAGNOSTIC TEST")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    print("=" * 80)

    results = {}

    # Run all tests
    results["config_dependencies"] = test_config_dependencies()
    results["error_handling"] = test_error_handling_methods()
    results["borehole_log"] = test_borehole_log_functionality()
    results["plot_generation"] = test_plot_generation_imports()
    results["section_plotting"] = test_section_plotting()
    results["figure_types"] = test_figure_types()

    # Generate summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} : {status}")

    print("-" * 40)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")

    print(f"\nDiagnostic completed at: {datetime.now()}")

    return results


if __name__ == "__main__":
    main()
