"""
Enhanced Dependency Graph Validation Script
Tests all critical functionality and generates validation report
"""

import json
import os
from pathlib import Path
import webbrowser
import subprocess
import sys


def test_data_generation():
    """Test that the enhanced dependency graph generates proper data."""
    print("🔍 Testing data generation...")

    # Import and run the analyzer
    try:
        from graph_output.enhanced_dependency_graph import EnhancedDependencyAnalyzer

        analyzer = EnhancedDependencyAnalyzer()
        graph_data = analyzer.analyze_project()

        # Validate required fields
        required_fields = [
            "nodes",
            "edges",
            "dependencies",
            "subfolder_info",
            "importance_scores",
            "statistics",
        ]
        for field in required_fields:
            assert field in graph_data, f"Missing required field: {field}"

        # Validate nodes structure
        if graph_data["nodes"]:
            node = graph_data["nodes"][0]
            required_node_fields = [
                "id",
                "name",
                "stem",
                "folder",
                "color",
                "file_path",
                "imports_count",
                "importance",
                "is_test",
                "is_init",
                "size",
                "index",
            ]
            for field in required_node_fields:
                assert field in node, f"Missing required node field: {field}"

        # Validate edges structure
        if graph_data["edges"]:
            edge = graph_data["edges"][0]
            required_edge_fields = [
                "source",
                "target",
                "source_name",
                "target_name",
                "source_folder",
                "target_folder",
                "is_cross_folder",
                "is_test_related",
            ]
            for field in required_edge_fields:
                assert field in edge, f"Missing required edge field: {field}"

        print(f"✅ Data generation test passed!")
        print(f"   - {len(graph_data['nodes'])} nodes found")
        print(f"   - {len(graph_data['edges'])} edges found")
        print(f"   - {len(graph_data['subfolder_info'])} folders found")

        return True, graph_data

    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        return False, None


def test_html_generation():
    """Test that HTML is generated correctly."""
    print("\n🔍 Testing HTML generation...")

    try:
        from graph_output.enhanced_dependency_graph import (
            generate_enhanced_html_visualization,
        )

        # Use minimal test data
        test_data = {
            "nodes": [
                {
                    "id": "root__test1",
                    "name": "test1",
                    "stem": "test1",
                    "folder": "root",
                    "color": "#E3F2FD",
                    "file_path": "./test1.py",
                    "imports_count": 0,
                    "importance": 0.5,
                    "is_test": False,
                    "is_init": False,
                    "size": 1000,
                    "index": 0,
                },
                {
                    "id": "root__test2",
                    "name": "test2",
                    "stem": "test2",
                    "folder": "root",
                    "color": "#E3F2FD",
                    "file_path": "./test2.py",
                    "imports_count": 1,
                    "importance": 0.3,
                    "is_test": False,
                    "is_init": False,
                    "size": 800,
                    "index": 1,
                },
            ],
            "edges": [
                {
                    "source": 0,
                    "target": 1,
                    "source_name": "root__test1",
                    "target_name": "root__test2",
                    "source_folder": "root",
                    "target_folder": "root",
                    "is_cross_folder": False,
                    "is_test_related": False,
                }
            ],
            "dependencies": {
                "root__test1": {"imports": ["root__test2"], "stem": "test1"},
                "root__test2": {"imports": [], "stem": "test2"},
            },
            "subfolder_info": {
                "root": {
                    "color": "#E3F2FD",
                    "modules": ["test1", "test2"],
                    "test_modules": [],
                    "count": 2,
                }
            },
            "importance_scores": {"root__test1": 0.5, "root__test2": 0.3},
            "statistics": {
                "total_files": 2,
                "total_dependencies": 1,
                "cross_folder_dependencies": 0,
                "test_files": 0,
                "folders": 1,
            },
        }

        html_content = generate_enhanced_html_visualization(test_data)

        # Validate HTML structure
        assert "<!DOCTYPE html>" in html_content, "Missing DOCTYPE declaration"
        assert (
            '<script src="https://d3js.org/d3.v7.min.js"></script>' in html_content
        ), "Missing D3.js import"
        assert "const graphData = " in html_content, "Missing graph data injection"
        assert (
            "function createEnhancedArrowMarkers" in html_content
        ), "Missing arrow markers function"
        assert (
            "function handleEnhancedNodeClick" in html_content
        ), "Missing node click handler"
        assert (
            "function handleEnhancedMouseOver" in html_content
        ), "Missing mouse over handler"
        assert (
            "function shouldShowNode" in html_content
        ), "Missing shouldShowNode function"
        assert (
            'let currentLayout = "hierarchical"' in html_content
        ), "Missing layout state variable"

        print("✅ HTML generation test passed!")
        print("   - All required HTML elements present")
        print("   - JavaScript functions properly included")
        print("   - Data properly injected")

        return True, html_content

    except Exception as e:
        print(f"❌ HTML generation test failed: {e}")
        return False, None


def test_file_outputs():
    """Test that output files are created and valid."""
    print("\n🔍 Testing file outputs...")

    try:
        output_dir = Path("graph_output")

        # Check that files exist
        html_file = output_dir / "enhanced_dependency_graph.html"
        json_file = output_dir / "enhanced_graph_data.json"

        assert html_file.exists(), "HTML file not generated"
        assert json_file.exists(), "JSON file not generated"

        # Validate JSON file
        with open(json_file, "r") as f:
            json_data = json.load(f)
            assert "nodes" in json_data, "JSON missing nodes"
            assert "edges" in json_data, "JSON missing edges"

        # Validate HTML file
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
            assert len(html_content) > 1000, "HTML file too small"
            assert "Enhanced Dependency Graph" in html_content, "HTML missing title"

        print("✅ File output test passed!")
        print(f"   - HTML file: {html_file} ({len(html_content)} characters)")
        print(f"   - JSON file: {json_file} ({len(json.dumps(json_data))} characters)")

        return True

    except Exception as e:
        print(f"❌ File output test failed: {e}")
        return False


def test_javascript_syntax():
    """Test JavaScript syntax validity using Node.js if available."""
    print("\n🔍 Testing JavaScript syntax...")

    try:
        # Extract JavaScript from HTML
        html_file = Path("graph_output") / "enhanced_dependency_graph.html"
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Find JavaScript section
        script_start = html_content.find("<script>")
        script_end = html_content.find("</script>", script_start)

        if script_start == -1 or script_end == -1:
            print("❌ No JavaScript section found in HTML")
            return False

        js_content = html_content[script_start + 8 : script_end]

        # Create temporary JS file for syntax checking
        temp_js = Path("temp_validation.js")
        with open(temp_js, "w", encoding="utf-8") as f:
            # Add basic DOM simulation for Node.js
            f.write(
                """
// Mock DOM objects for syntax validation
const document = { querySelector: () => ({}), addEventListener: () => {} };
const window = { addEventListener: () => {} };
const d3 = { select: () => ({}) };

"""
            )
            f.write(js_content)

        # Try to validate with Node.js
        try:
            result = subprocess.run(
                ["node", "-c", str(temp_js)], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✅ JavaScript syntax test passed!")
                print("   - No syntax errors found")
                success = True
            else:
                print(f"❌ JavaScript syntax errors found: {result.stderr}")
                success = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Node.js not available, do basic checks
            print("⚠️  Node.js not available, doing basic validation...")

            # Check for common syntax issues
            issues = []
            if js_content.count("{") != js_content.count("}"):
                issues.append("Mismatched curly braces")
            if js_content.count("(") != js_content.count(")"):
                issues.append("Mismatched parentheses")
            if "{{" in js_content and "}}" not in js_content:
                issues.append("Template formatting issue")

            if issues:
                print(f"❌ Basic syntax validation failed: {', '.join(issues)}")
                success = False
            else:
                print("✅ Basic JavaScript validation passed!")
                print("   - No obvious syntax errors")
                success = True

        # Cleanup
        if temp_js.exists():
            temp_js.unlink()

        return success

    except Exception as e:
        print(f"❌ JavaScript syntax test failed: {e}")
        return False


def generate_validation_report():
    """Generate comprehensive validation report."""
    print("\n" + "=" * 60)
    print("🚀 ENHANCED DEPENDENCY GRAPH VALIDATION COMPLETE")
    print("=" * 60)

    # Run all tests
    tests = [
        ("Data Generation", test_data_generation),
        ("HTML Generation", test_html_generation),
        ("File Outputs", test_file_outputs),
        ("JavaScript Syntax", test_javascript_syntax),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            if test_name == "Data Generation":
                success, data = test_func()
                results.append((test_name, success, data))
            else:
                success = test_func()
                results.append((test_name, success, None))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False, None))

    # Summary
    print("\n📊 VALIDATION SUMMARY:")
    print("-" * 40)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, data in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 ALL TESTS PASSED! The Enhanced Dependency Graph is working correctly."
        )
        print("\n🌐 To view the visualization:")
        print("   1. Open graph_output/enhanced_dependency_graph.html in a web browser")
        print("   2. All interactive features should be functional")
        print("   3. Data should be visible and controls should work")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = generate_validation_report()
    sys.exit(0 if success else 1)
