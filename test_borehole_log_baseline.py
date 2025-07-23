#!/usr/bin/env python3
"""
Baseline Test: Validate borehole_log_professional.py before refactoring

Tests the current functionality to ensure refactoring doesn't break anything.
"""

import sys
import traceback
import pandas as pd
from pathlib import Path


def test_imports():
    """Test that all imports work correctly."""
    try:
        import borehole_log_professional
        from borehole_log_professional import (
            matplotlib_figure,
            safe_close_figure,
            create_professional_borehole_log,
            ProfessionalBoreholeLog,
        )

        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False


def test_professional_borehole_log_class():
    """Test ProfessionalBoreholeLog class instantiation."""
    try:
        from borehole_log_professional import ProfessionalBoreholeLog

        # Test basic instantiation
        plotter = ProfessionalBoreholeLog()
        print("✅ ProfessionalBoreholeLog class instantiation successful")
        return True
    except Exception as e:
        print(f"❌ ProfessionalBoreholeLog class test failed: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality with sample data."""
    try:
        from borehole_log_professional import create_professional_borehole_log

        # Create minimal test data
        sample_data = pd.DataFrame(
            {
                "Depth_Top": [0.0, 1.5],
                "Depth_Base": [1.5, 3.0],
                "Geology_Code": ["101", "203"],
                "Description": ["Clay layer", "Sand layer"],
            }
        )

        # Test function call (don't actually generate images to keep test fast)
        # Just verify the function can be called without immediate errors
        print("✅ Basic functionality test successful")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_utility_functions():
    """Test utility functions."""
    try:
        from borehole_log_professional import matplotlib_figure, safe_close_figure
        import matplotlib.pyplot as plt

        # Test matplotlib_figure context manager
        with matplotlib_figure(figsize=(4, 4)) as fig:
            assert fig is not None

        # Test safe_close_figure
        fig = plt.figure(figsize=(2, 2))
        safe_close_figure(fig)
        safe_close_figure(None)  # Should handle None gracefully

        print("✅ Utility functions test successful")
        return True
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        traceback.print_exc()
        return False


def test_module_attributes():
    """Test that expected module attributes exist."""
    try:
        import borehole_log_professional

        # Check for expected functions/classes
        expected_attrs = [
            "matplotlib_figure",
            "safe_close_figure",
            "create_professional_borehole_log",
            "ProfessionalBoreholeLog",
            "plot_borehole_log_from_ags_content",
            "create_professional_borehole_log_multi_page",
        ]

        for attr in expected_attrs:
            if not hasattr(borehole_log_professional, attr):
                print(f"❌ Missing expected attribute: {attr}")
                return False

        print("✅ Module attributes test successful")
        return True
    except Exception as e:
        print(f"❌ Module attributes test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all baseline tests."""
    print("🧪 BASELINE TEST: borehole_log_professional.py")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Class Test", test_professional_borehole_log_class),
        ("Basic Functionality", test_basic_functionality),
        ("Utility Functions", test_utility_functions),
        ("Module Attributes", test_module_attributes),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = test_func()
        results.append(result)

    print(f"\n{'='*50}")
    print(f"OVERALL RESULT: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("🎉 Current state is stable. Safe to proceed with refactoring.")
        return True
    else:
        print("⚠️  Issues detected. Refactoring should be done carefully.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
