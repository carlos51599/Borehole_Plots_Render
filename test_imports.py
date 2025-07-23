#!/usr/bin/env python3
"""
Comprehensive import and syntax testing for all modules.

This script tests the current state of all modules to understand
dependencies and ensure everything imports correctly before refactoring.
"""

import sys
import traceback
from pathlib import Path


def test_all_imports():
    """Test all module imports to understand current state."""
    print("🧪 Testing Current Module Imports")
    print("=" * 50)

    # Test core modules
    modules_to_test = [
        "callbacks_split",
        "section_plot_professional",
        "borehole_log_professional",
        "app_factory",
        "app",
        "config",
        "data_loader",
        "map_utils",
        "coordinate_service",
        "dataframe_optimizer",
        "app_constants",
        "loading_indicators",
        "memory_manager",
        "geology_code_utils",
        "polyline_utils",
        "enhanced_error_handling",
        "error_handling",
        "error_recovery",
        "lazy_marker_manager",
        "debug_module",
    ]

    results = {}

    for module_name in modules_to_test:
        try:
            print(f"Testing {module_name}...", end=" ")
            # Try to import the module
            imported_module = __import__(module_name)
            print(f"✅ Success")
            results[module_name] = {"status": "success", "error": None}

            # Test if it has key functions/classes
            if hasattr(imported_module, "__all__"):
                print(f"   - Exports: {len(imported_module.__all__)} items")
            elif hasattr(imported_module, "__dict__"):
                public_items = [
                    k for k in imported_module.__dict__.keys() if not k.startswith("_")
                ]
                print(f"   - Public items: {len(public_items)}")

        except ImportError as e:
            print(f"❌ Import Error: {e}")
            results[module_name] = {"status": "import_error", "error": str(e)}
        except Exception as e:
            print(f"⚠️ Other Error: {e}")
            results[module_name] = {"status": "other_error", "error": str(e)}

    # Summary
    print("\n📊 Import Test Results:")
    print("=" * 50)

    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_count = len(results)

    print(f"✅ Successful imports: {success_count}/{total_count}")

    # Show failures
    failures = {k: v for k, v in results.items() if v["status"] != "success"}
    if failures:
        print(f"❌ Failed imports: {len(failures)}")
        for module, info in failures.items():
            print(f"   - {module}: {info['error']}")

    return results


def test_key_functions():
    """Test key functions from the main modules."""
    print("\n🔧 Testing Key Functions")
    print("=" * 50)

    try:
        from callbacks_split import register_callbacks

        print("✅ callbacks_split.register_callbacks found")
    except Exception as e:
        print(f"❌ callbacks_split.register_callbacks error: {e}")

    try:
        from section_plot_professional import plot_professional_borehole_sections

        print("✅ section_plot_professional.plot_professional_borehole_sections found")
    except Exception as e:
        print(
            f"❌ section_plot_professional.plot_professional_borehole_sections error: {e}"
        )

    try:
        from borehole_log_professional import plot_borehole_log_from_ags_content

        print("✅ borehole_log_professional.plot_borehole_log_from_ags_content found")
    except Exception as e:
        print(
            f"❌ borehole_log_professional.plot_borehole_log_from_ags_content error: {e}"
        )


def test_file_structure():
    """Analyze current file structure."""
    print("\n📁 Current File Structure Analysis")
    print("=" * 50)

    current_dir = Path(".")

    # Get all Python files
    py_files = list(current_dir.glob("*.py"))
    print(f"Python files in root: {len(py_files)}")

    # Check existing folders
    folders = [
        p for p in current_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    ]
    print(f"Existing folders: {[f.name for f in folders]}")

    # Check callbacks folder specifically
    callbacks_folder = current_dir / "callbacks"
    if callbacks_folder.exists():
        callbacks_files = list(callbacks_folder.glob("*.py"))
        print(f"Files in callbacks/: {len(callbacks_files)}")
        for f in callbacks_files:
            print(f"   - {f.name}")
    else:
        print("❌ callbacks/ folder not found")

    # Check for large files that need refactoring
    large_files = []
    for py_file in py_files:
        try:
            lines = len(py_file.read_text().splitlines())
            if lines > 500:  # Consider files > 500 lines as large
                large_files.append((py_file.name, lines))
        except Exception:
            pass

    if large_files:
        print(f"\n📏 Large files (>500 lines) that need refactoring:")
        for filename, line_count in sorted(
            large_files, key=lambda x: x[1], reverse=True
        ):
            print(f"   - {filename}: {line_count} lines")


if __name__ == "__main__":
    print("🚀 Comprehensive Import and Structure Testing")
    print("=" * 80)

    # Test imports
    import_results = test_all_imports()

    # Test key functions
    test_key_functions()

    # Analyze file structure
    test_file_structure()

    print("\n🎯 Test Complete!")
    print("=" * 80)
