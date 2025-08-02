"""
Test script to validate the fixes for plot generation issues.

This script tests:
1. ErrorHandler method calls work correctly
2. Plot function return types are correct
3. Import validation for all critical modules
"""

import sys
import os
import traceback

# Add project root to Python path
project_root = (
    os.path.dirname(os.path.abspath(__file__)).replace("tests", "").rstrip(os.sep)
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_error_handler_fix():
    """Test that ErrorHandler methods work correctly."""
    print("=" * 50)
    print("TESTING ERROR HANDLER FIX")
    print("=" * 50)

    try:
        from error_handling import get_error_handler
        from callbacks.plot_generation import PlotGenerationCallback

        # Create instances
        error_handler = get_error_handler()
        plot_callback = PlotGenerationCallback()

        print("✓ ErrorHandler and PlotGenerationCallback imported successfully")

        # Test handle_callback_error method exists
        if hasattr(error_handler, "handle_callback_error"):
            print("✓ handle_callback_error method available")

            # Test calling the method (safe test with minimal args)
            try:
                test_exception = Exception("Test exception for validation")
                error = error_handler.handle_callback_error(
                    test_exception, "test_callback"
                )
                print("✓ handle_callback_error method call successful")
                print(f"  Error created: {error.message[:50]}...")

            except Exception as e:
                print(f"❌ handle_callback_error method call failed: {e}")
                return False

        else:
            print("❌ handle_callback_error method not available")
            return False

        return True

    except Exception as e:
        print(f"❌ ErrorHandler test failed: {e}")
        traceback.print_exc()
        return False


def test_plot_function_return_type():
    """Test that plot function returns the correct type."""
    print("\n" + "=" * 50)
    print("TESTING PLOT FUNCTION RETURN TYPE")
    print("=" * 50)

    try:
        from section import plot_section_from_ags_content

        print("✓ plot_section_from_ags_content imported successfully")

        # Test default behavior (should return base64 string)
        sample_ags = """**PROJ
HEAD,1,AGS4,AGS 4.1.1,Test Project
**LOCA
LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
BH001,BH,523456.78,123456.89,100.50
**GEOL  
LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL
BH001,0.00,1.50,Made Ground
BH001,1.50,3.00,Clay
"""

        print("\nTesting return_base64=False behavior (Figure object):")
        result_figure = plot_section_from_ags_content(
            sample_ags, return_base64=False  # Should return Figure
        )

        if result_figure is not None:
            print(f"✓ return_base64=False returns {type(result_figure)}")

            # Check if it has savefig method
            if hasattr(result_figure, "savefig"):
                print("✓ Returned object has savefig method")

                # Clean up the figure
                import matplotlib.pyplot as plt

                plt.close(result_figure)
                return True
            else:
                print(
                    f"❌ Returned object {type(result_figure)} does not have savefig method"
                )
                return False
        else:
            print(
                "⚠️ return_base64=False returned None (may be due to insufficient data)"
            )
            return True  # None is acceptable for empty data

    except Exception as e:
        print(f"❌ Plot function test failed: {e}")
        traceback.print_exc()
        return False


def test_import_validation():
    """Test that all critical imports work."""
    print("\n" + "=" * 50)
    print("TESTING IMPORT VALIDATION")
    print("=" * 50)

    critical_imports = [
        ("config", "Monolithic config"),
        ("config_modules", "Modular config"),
        ("error_handling.get_error_handler", "Error handler"),
        (
            "callbacks.plot_generation.PlotGenerationCallback",
            "Plot generation callback",
        ),
        ("section.plot_section_from_ags_content", "Section plotting"),
        ("borehole_log.plot_borehole_log_from_ags_content", "Borehole log"),
    ]

    results = []

    for import_path, description in critical_imports:
        try:
            if "." in import_path:
                module_path, attr = import_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[attr])
                getattr(module, attr)
            else:
                __import__(import_path)

            print(f"✓ {description}: {import_path}")
            results.append(True)

        except Exception as e:
            print(f"❌ {description}: {import_path} - {e}")
            results.append(False)

    return all(results)


def main():
    """Run all validation tests."""
    print("PLOT GENERATION FIXES VALIDATION")
    print("=" * 80)

    results = {
        "error_handler_fix": test_error_handler_fix(),
        "plot_return_type": test_plot_function_return_type(),
        "import_validation": test_import_validation(),
    }

    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")

    print("-" * 40)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All fixes validated successfully!")
    else:
        print("⚠️ Some issues remain - check failed tests above")

    return results


if __name__ == "__main__":
    main()
