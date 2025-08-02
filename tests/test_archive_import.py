#!/usr/bin/env python3
"""
Test script to verify if the archive import is working correctly.
"""

import sys
import traceback
import time
from pathlib import Path

# Add the workspace root to Python path
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))


def test_archive_import():
    """Test importing the archive module and calling the function."""
    print("Testing archive import...")

    try:
        start_time = time.time()

        # Test the dynamic import that's failing in main.py
        import importlib.util

        archive_path = (
            workspace_root / "archive" / "section_plot_professional_original.py"
        )
        print(f"Archive path: {archive_path}")
        print(f"Archive exists: {archive_path.exists()}")

        # Dynamic import like in main.py
        spec = importlib.util.spec_from_file_location("archive_module", archive_path)
        archive_module = importlib.util.module_from_spec(spec)

        print("Loading archive module...")
        spec.loader.exec_module(archive_module)

        import_time = time.time() - start_time
        print(f"Archive import took: {import_time:.2f} seconds")

        # Check if the function exists
        if hasattr(archive_module, "plot_section_from_ags_content"):
            print("✓ plot_section_from_ags_content function found in archive")
            func = getattr(archive_module, "plot_section_from_ags_content")
            print(f"Function signature: {func.__name__}")
        else:
            print("✗ plot_section_from_ags_content function NOT found in archive")

        return True

    except Exception as e:
        print(f"✗ Archive import failed: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return False


def test_regular_import():
    """Test regular import method."""
    print("\nTesting regular import...")

    try:
        start_time = time.time()

        # Try regular import
        from archive.section_plot_professional_original import (
            plot_section_from_ags_content,
        )

        import_time = time.time() - start_time
        print(f"Regular import took: {import_time:.2f} seconds")
        print("✓ Regular import successful")

        return True

    except Exception as e:
        print(f"✗ Regular import failed: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== Archive Import Test ===")

    # Test dynamic import
    dynamic_success = test_archive_import()

    # Test regular import
    regular_success = test_regular_import()

    print(f"\n=== Results ===")
    print(f"Dynamic import: {'✓ SUCCESS' if dynamic_success else '✗ FAILED'}")
    print(f"Regular import: {'✓ SUCCESS' if regular_success else '✗ FAILED'}")

    if not dynamic_success:
        print(
            "\n💡 Suggestion: The dynamic import in main.py may be causing callback timeouts"
        )
        print(
            "   Consider using regular imports or fixing the archive module dependencies"
        )
