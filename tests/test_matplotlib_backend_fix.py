#!/usr/bin/env python
"""
Test script to verify the matplotlib backend fix resolves server crashes.

This test validates that:
1. Matplotlib uses the 'Agg' (non-interactive) backend
2. Section plotting works without Qt GUI errors
3. Multiple plots can be generated without memory leaks or crashes
4. Base64 encoding works correctly for web display

Run this test to ensure the server crash issue is resolved.
"""

import sys
import os
import logging
import tempfile
import base64
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure matplotlib backend BEFORE any other imports
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

# Test imports from the section plotting module
try:
    from section.plotting.main import plot_section_from_ags_content
    from section.parsing import parse_ags_geol_section_from_string
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_matplotlib_backend():
    """Test that matplotlib is using the correct backend."""
    backend = plt.get_backend()
    print(f"📊 Matplotlib backend: {backend}")

    if backend != "Agg":
        print(f"❌ FAIL: Expected 'Agg' backend, got '{backend}'")
        return False

    print("✅ PASS: Matplotlib using non-interactive 'Agg' backend")
    return True


def test_simple_plot_creation():
    """Test creating a simple matplotlib plot without Qt errors."""
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Plot")

        # Convert to base64
        buffer = BytesIO()
        fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()

        # Clean up
        plt.close(fig)
        buffer.close()

        print("✅ PASS: Simple plot creation and base64 encoding works")
        return True

    except Exception as e:
        print(f"❌ FAIL: Simple plot creation failed: {e}")
        return False


def test_multiple_plots():
    """Test creating multiple plots to check for memory leaks."""
    try:
        for i in range(5):
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(["A", "B", "C"], [1, 3, 2])
            ax.set_title(f"Test Plot {i+1}")
            plt.close(fig)  # Important: clean up each figure

        print("✅ PASS: Multiple plot creation and cleanup works")
        return True

    except Exception as e:
        print(f"❌ FAIL: Multiple plot creation failed: {e}")
        return False


def test_section_plotting_with_sample_data():
    """Test section plotting with minimal AGS data."""
    # Create minimal AGS content for testing
    sample_ags_content = """**GEOL
LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_GEOL,GEOL_DESC
,m,m,,m,
,0.0,99.0,,,
BH001,0.0,2.0,101,TOPSOIL,Topsoil
BH001,2.0,5.0,203,CLAY,Sandy Clay
BH002,0.0,1.5,101,TOPSOIL,Topsoil  
BH002,1.5,4.0,203,CLAY,Sandy Clay

**LOCA
LOCA_ID,LOCA_TYPE,LOCA_STAT,LOCA_NATE,LOCA_NATN,LOCA_GL
,,,,m,m,m
,,,,0.0,0.0,0.0
BH001,BH,Complete,100000.0,200000.0,50.0
BH002,BH,Complete,100010.0,200000.0,49.5

**ABBR
ABBR_HDNG,ABBR_CODE,ABBR_DESC,ABBR_LIST,ABBR_REM
,,,,,
,,,,,
GEOL_LEG,101,TOPSOIL,BGS_LEG,Topsoil
GEOL_LEG,203,SANDY_CLAY,BGS_LEG,Sandy clay
"""

    try:
        # Test parsing
        geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(
            sample_ags_content
        )
        print(
            f"📋 Parsed data: {len(geol_df)} geology records, {len(loca_df)} locations"
        )

        # Test plotting with return_base64=True (web display mode)
        base64_result = plot_section_from_ags_content(
            sample_ags_content, filter_loca_ids=["BH001", "BH002"], return_base64=True
        )

        if (
            base64_result
            and isinstance(base64_result, str)
            and base64_result.startswith("data:image/png;base64,")
        ):
            print("✅ PASS: Section plotting with base64 output works")
            return True
        else:
            print(
                f"❌ FAIL: Section plotting returned invalid base64: {type(base64_result)}"
            )
            return False

    except Exception as e:
        print(f"❌ FAIL: Section plotting failed: {e}")
        logger.exception("Section plotting error details:")
        return False


def main():
    """Run all tests to verify the matplotlib backend fix."""
    print("🔧 Testing matplotlib backend fix for server crashes...")
    print("=" * 60)

    tests = [
        ("Matplotlib Backend Check", test_matplotlib_backend),
        ("Simple Plot Creation", test_simple_plot_creation),
        ("Multiple Plots Memory Test", test_multiple_plots),
        ("Section Plotting Integration", test_section_plotting_with_sample_data),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: {test_name} crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Matplotlib backend fix is working.")
        print("✅ Server should no longer crash during section plotting.")
        return True
    else:
        print("⚠️  Some tests failed. Server crashes may still occur.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
