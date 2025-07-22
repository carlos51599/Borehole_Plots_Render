"""
Test script for modular dependency graph implementation.
Validates that the modular architecture works correctly.
"""

import sys
import traceback
from pathlib import Path


def test_modular_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing modular imports...")

    try:
        # Test individual module imports
        from graph_modules.dependency_analyzer import EnhancedDependencyAnalyzer
        from graph_modules.graph_styles import get_graph_styles
        from graph_modules.hierarchical_layout import get_hierarchical_layout_js
        from graph_modules.force_directed_layout import get_force_directed_layout_js
        from graph_modules.graph_visualization import get_graph_visualization_js
        from graph_modules.graph_controls import get_graph_controls_js
        from graph_modules.html_generator import (
            generate_enhanced_html_visualization,
            main,
        )

        print("✅ All individual modules imported successfully")

        # Test package-level imports
        from graph_modules import (
            EnhancedDependencyAnalyzer,
            generate_enhanced_html_visualization,
            main,
        )

        print("✅ Package-level imports successful")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality of the modular system."""
    print("\n🧪 Testing basic functionality...")

    try:
        from graph_modules import (
            EnhancedDependencyAnalyzer,
            generate_enhanced_html_visualization,
        )

        # Test analyzer creation
        analyzer = EnhancedDependencyAnalyzer()
        print("✅ Analyzer created successfully")

        # Test style generation
        from graph_modules.graph_styles import get_graph_styles

        styles = get_graph_styles()
        assert len(styles) > 1000, "Styles should be substantial"
        print("✅ Styles generated successfully")

        # Test JS module generation
        from graph_modules.hierarchical_layout import get_hierarchical_layout_js
        from graph_modules.force_directed_layout import get_force_directed_layout_js
        from graph_modules.graph_visualization import get_graph_visualization_js
        from graph_modules.graph_controls import get_graph_controls_js

        hierarchical_js = get_hierarchical_layout_js()
        force_js = get_force_directed_layout_js()
        viz_js = get_graph_visualization_js()
        controls_js = get_graph_controls_js()

        assert all(
            len(js) > 500 for js in [hierarchical_js, force_js, viz_js, controls_js]
        ), "All JS modules should be substantial"
        print("✅ JavaScript modules generated successfully")

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_html_generation():
    """Test HTML generation with sample data."""
    print("\n🧪 Testing HTML generation...")

    try:
        from graph_modules.html_generator import generate_enhanced_html_visualization

        # Create minimal test data
        test_data = {
            "nodes": [
                {
                    "id": "test.py",
                    "name": "test",
                    "stem": "test",
                    "folder": "root",
                    "color": "#FF6B6B",
                    "file_path": "test.py",
                    "imports_count": 0,
                    "importance": 0.5,
                    "is_test": False,
                    "is_init": False,
                    "size": 1024,
                    "index": 0,
                }
            ],
            "edges": [],
            "dependencies": {},
            "subfolder_info": {
                "root": {
                    "color": "#FF6B6B",
                    "modules": ["test"],
                    "test_modules": [],
                    "count": 1,
                }
            },
            "importance_scores": {},
            "statistics": {
                "total_files": 1,
                "total_dependencies": 0,
                "cross_folder_dependencies": 0,
                "test_files": 0,
                "folders": 1,
            },
        }

        html = generate_enhanced_html_visualization(test_data)

        # Basic validation
        assert "<!DOCTYPE html>" in html, "Should contain HTML doctype"
        assert "Enhanced Dependency Graph" in html, "Should contain title"
        assert "d3.v7.min.js" in html, "Should include D3.js"
        assert "const graphData = " in html, "Should embed graph data"
        assert len(html) > 10000, "Generated HTML should be substantial"

        print("✅ HTML generation successful")
        return True

    except Exception as e:
        print(f"❌ HTML generation test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 TESTING MODULAR DEPENDENCY GRAPH IMPLEMENTATION")
    print("=" * 60)

    tests = [test_modular_imports, test_basic_functionality, test_html_generation]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 ALL TESTS PASSED! Modular architecture is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
