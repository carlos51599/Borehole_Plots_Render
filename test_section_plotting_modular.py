"""
Test script for section.plotting modular structure.

This script validates that the new modular structure maintains
all functionality and import compatibility.
"""

import sys
import os
import traceback
from typing import List, Tuple


def test_module_imports() -> Tuple[bool, List[str]]:
    """Test all module imports."""
    results = []
    success = True

    # Test individual module imports
    modules_to_test = [
        "section.plotting.coordinates",
        "section.plotting.geology",
        "section.plotting.layout",
        "section.plotting.main",
        "section.plotting",
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
        from section.plotting import (
            plot_professional_borehole_sections,
            plot_section_from_ags_content,
            plot_professional_section,
            plot_section,
        )

        # Check functions are callable
        functions = [
            (
                "plot_professional_borehole_sections",
                plot_professional_borehole_sections,
            ),
            ("plot_section_from_ags_content", plot_section_from_ags_content),
            ("plot_professional_section", plot_professional_section),
            ("plot_section", plot_section),
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


def test_submodule_functions() -> Tuple[bool, List[str]]:
    """Test key functions from submodules."""
    results = []
    success = True

    # Test coordinates module
    try:
        from section.plotting.coordinates import prepare_coordinate_data

        if callable(prepare_coordinate_data):
            results.append("✅ coordinates.prepare_coordinate_data: Available")
        else:
            results.append("❌ coordinates.prepare_coordinate_data: Not callable")
            success = False
    except Exception as e:
        results.append(f"❌ coordinates module error: {e}")
        success = False

    # Test geology module
    try:
        from section.plotting.geology import (
            create_geology_mappings,
            plot_geological_intervals,
            create_professional_legend,
        )

        geology_functions = [
            ("create_geology_mappings", create_geology_mappings),
            ("plot_geological_intervals", plot_geological_intervals),
            ("create_professional_legend", create_professional_legend),
        ]

        for name, func in geology_functions:
            if callable(func):
                results.append(f"✅ geology.{name}: Available")
            else:
                results.append(f"❌ geology.{name}: Not callable")
                success = False

    except Exception as e:
        results.append(f"❌ geology module error: {e}")
        success = False

    # Test layout module
    try:
        from section.plotting.layout import (
            create_professional_layout,
            add_professional_formatting,
            set_axis_limits_and_aspect,
        )

        layout_functions = [
            ("create_professional_layout", create_professional_layout),
            ("add_professional_formatting", add_professional_formatting),
            ("set_axis_limits_and_aspect", set_axis_limits_and_aspect),
        ]

        for name, func in layout_functions:
            if callable(func):
                results.append(f"✅ layout.{name}: Available")
            else:
                results.append(f"❌ layout.{name}: Not callable")
                success = False

    except Exception as e:
        results.append(f"❌ layout module error: {e}")
        success = False

    return success, results


def test_backward_compatibility() -> Tuple[bool, List[str]]:
    """Test backward compatibility with existing imports."""
    results = []
    success = True

    # Test if we can import the way the existing code does
    try:
        # This should work if section_plot_professional.py imports from section.plotting
        import section.plotting

        results.append("✅ section.plotting package import: Success")

        # Check if main functions are accessible via package
        if hasattr(section.plotting, "plot_professional_borehole_sections"):
            results.append("✅ Main function accessible via package: Success")
        else:
            results.append("❌ Main function not accessible via package")
            success = False

    except Exception as e:
        results.append(f"❌ Backward compatibility error: {e}")
        success = False

    return success, results


def main():
    """Run all tests and report results."""
    print("Testing section.plotting modular structure...")
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

    # Test 3: Submodule functions
    print("\n3. Testing submodule functions:")
    success, results = test_submodule_functions()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 4: Backward compatibility
    print("\n4. Testing backward compatibility:")
    success, results = test_backward_compatibility()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Final result
    print("\n" + "=" * 60)
    if all_success:
        print("🎉 ALL TESTS PASSED - Modular structure is working correctly!")
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
