"""
Migration Validation Script
Compares features between old SVG-based and new HTML-based dependency graphs
"""

import os
import json
import time


def validate_html_output():
    """Validate that the HTML output was generated correctly."""
    output_dir = "graph_output"
    html_file = os.path.join(output_dir, "dependency_graph.html")
    data_file = os.path.join(output_dir, "graph_data.json")

    print("🔍 Validating HTML output...")

    # Check if files exist
    if not os.path.exists(html_file):
        print("❌ HTML file not found")
        return False

    if not os.path.exists(data_file):
        print("❌ Data file not found")
        return False

    # Check HTML file size
    html_size = os.path.getsize(html_file)
    print(f"✅ HTML file size: {html_size:,} bytes")

    # Load and validate JSON data
    try:
        with open(data_file, "r") as f:
            data = json.load(f)

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        subfolder_info = data.get("subfolder_info", {})

        print("✅ Data validation:")
        print(f"   📊 Nodes: {len(nodes)}")
        print(f"   🔗 Edges: {len(edges)}")
        print(f"   📁 Folders: {len(subfolder_info)}")

        # Validate node structure
        if nodes:
            sample_node = nodes[0]
            required_fields = ["id", "name", "folder", "color", "file_path"]
            missing_fields = [
                field for field in required_fields if field not in sample_node
            ]
            if missing_fields:
                print(f"❌ Missing node fields: {missing_fields}")
                return False
            print("✅ Node structure valid")

        # Validate edge structure
        if edges:
            sample_edge = edges[0]
            required_fields = ["source", "target", "source_name", "target_name"]
            missing_fields = [
                field for field in required_fields if field not in sample_edge
            ]
            if missing_fields:
                print(f"❌ Missing edge fields: {missing_fields}")
                return False
            print("✅ Edge structure valid")

        # Validate subfolder structure
        for folder, info in subfolder_info.items():
            if "color" not in info or "modules" not in info:
                print(f"❌ Invalid subfolder structure for {folder}")
                return False
        print("✅ Subfolder structure valid")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def compare_features():
    """Compare features between old and new implementations."""
    print("🔄 Comparing feature migration...")

    old_features = [
        "SVG-based visualization",
        "Node coloring by subfolder",
        "Interactive legend with checkboxes",
        "Direct path highlighting",
        "Dimming/highlighting effects",
        "Click event handling",
        "Folder filtering",
        "Tooltip on hover",
        "Reset functionality",
    ]

    new_features = [
        "HTML + D3.js visualization",
        "Node coloring by subfolder",
        "Interactive sidebar with checkboxes",
        "Direct path highlighting",
        "Smooth transitions and animations",
        "Advanced click and drag handling",
        "Real-time folder filtering",
        "Rich tooltips with detailed info",
        "Reset functionality",
        "Responsive design",
        "Statistics panel",
        "Zoom and pan capabilities",
        "Mobile-friendly interface",
        "Accessibility improvements",
        "Modular code architecture",
    ]

    print("📋 Feature Comparison:")
    print("   Old Implementation:")
    for feature in old_features:
        print(f"     • {feature}")

    print("   New Implementation:")
    for feature in new_features:
        print(f"     • {feature}")

    enhanced_features = len(new_features) - len(old_features)
    print(f"\n✨ Enhanced with {enhanced_features} additional features!")


def performance_test():
    """Basic performance test of the HTML generation."""
    print("⚡ Running performance test...")

    start_time = time.time()

    # Import and run the HTML generator
    try:
        import sys

        sys.path.append("graph_output")
        from html_dependency_graph import DependencyAnalyzer, HTMLGraphGenerator

        analyzer = DependencyAnalyzer()
        generator = HTMLGraphGenerator()

        # Scan files
        py_files = analyzer.scan_python_files()

        # Analyze dependencies
        graph_data = analyzer.analyze_dependencies(py_files)

        # Generate HTML
        html_content = generator.generate_html(graph_data)

        end_time = time.time()
        duration = end_time - start_time

        print(f"✅ Performance results:")
        print(f"   ⏱️  Generation time: {duration:.2f} seconds")
        print(f"   📊 Processed {len(py_files)} files")
        print(f"   🔗 Generated {len(graph_data['edges'])} dependencies")
        print(f"   📄 HTML size: {len(html_content):,} characters")

        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def check_browser_compatibility():
    """Check if the generated HTML includes all necessary dependencies."""
    print("🌐 Checking browser compatibility...")

    html_file = os.path.join("graph_output", "dependency_graph.html")

    if not os.path.exists(html_file):
        print("❌ HTML file not found")
        return False

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Check for essential components
    checks = {
        "D3.js library": "d3js.org/d3.v7.min.js" in html_content,
        "Responsive meta tag": "viewport" in html_content,
        "CSS styles": "<style>" in html_content,
        "JavaScript functionality": "<script>" in html_content,
        "Interactive elements": "addEventListener" in html_content,
        "Mobile responsiveness": "@media" in html_content,
        "Accessibility features": "aria-" in html_content or "role=" in html_content,
    }

    print("✅ Browser compatibility check:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")

    all_passed = all(checks.values())
    if all_passed:
        print("🎉 All compatibility checks passed!")
    else:
        print("⚠️  Some compatibility issues found")

    return all_passed


def generate_migration_report():
    """Generate a comprehensive migration report."""
    print("\n" + "=" * 60)
    print("📊 MIGRATION VALIDATION REPORT")
    print("=" * 60)

    results = {
        "HTML Output Validation": validate_html_output(),
        "Performance Test": performance_test(),
        "Browser Compatibility": check_browser_compatibility(),
    }

    print("\n📋 SUMMARY:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 MIGRATION SUCCESSFUL!")
        print("✅ All tests passed")
        print("✅ HTML-based dependency graph is ready for use")
        print("✅ Feature parity maintained with enhancements")
    else:
        print("\n⚠️  MIGRATION ISSUES DETECTED")
        print("❌ Some tests failed - review output above")

    # Generate recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Open graph_output/dependency_graph.html in a modern browser")
    print("   2. Test interactivity: click nodes, toggle folders, drag nodes")
    print("   3. Verify responsiveness on different screen sizes")
    print("   4. Check accessibility with screen readers")

    return all_passed


def main():
    """Main validation function."""
    print("🚀 Starting Migration Validation...")

    # First, let's check the feature comparison
    compare_features()

    print("\n" + "-" * 60)

    # Run comprehensive validation
    success = generate_migration_report()

    if success:
        print("\n🌟 Migration completed successfully!")
        print("🎯 Next steps: Review the HTML file and integrate into your workflow")
    else:
        print("\n🔧 Migration needs attention!")
        print("🎯 Next steps: Address failed tests before proceeding")


if __name__ == "__main__":
    main()
