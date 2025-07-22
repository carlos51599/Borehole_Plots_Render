"""
Test script to validate the Force-Directed Layout feature in the enhanced dependency graph.
This script performs basic validation of the generated HTML and JavaScript functionality.
"""

import os
import re
from pathlib import Path


def test_force_directed_layout_implementation():
    """Test that the force-directed layout feature is properly implemented."""

    print("🧪 Testing Force-Directed Layout Implementation")
    print("=" * 50)

    # Test files exist
    graph_output_dir = Path("graph_output")
    html_file = graph_output_dir / "enhanced_dependency_graph.html"

    if not html_file.exists():
        print("❌ ERROR: Enhanced dependency graph HTML file not found!")
        return False

    print("✅ HTML file found")

    # Read HTML content
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Test 1: Layout toggle UI elements
    ui_tests = [
        (r'id="layout-toggle"', "Layout toggle container"),
        (r'class="toggle-switch"', "Toggle switch element"),
        (r'id="toggle-switch"', "Toggle switch ID"),
        (r'id="layout-indicator"', "Layout indicator element"),
        (r"🎛️ Layout Control", "Layout control section title"),
        (r"📐 Hierarchical", "Hierarchical label"),
        (r"🌐 Force-Directed", "Force-directed label"),
    ]

    print("\n📋 Testing UI Elements:")
    for pattern, description in ui_tests:
        if re.search(pattern, html_content):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT FOUND")
            return False

    # Test 2: CSS styles for layout toggle
    css_tests = [
        (r"\.layout-toggle\s*\{", "Layout toggle CSS"),
        (r"\.toggle-switch\s*\{", "Toggle switch CSS"),
        (r"\.toggle-slider\s*\{", "Toggle slider CSS"),
        (r"\.toggle-switch\.active", "Active toggle state CSS"),
        (r"\.layout-mode-indicator", "Layout indicator CSS"),
    ]

    print("\n🎨 Testing CSS Styles:")
    for pattern, description in css_tests:
        if re.search(pattern, html_content, re.MULTILINE):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT FOUND")
            return False

    # Test 3: JavaScript functionality
    js_tests = [
        (r'currentLayout\s*=\s*["\']hierarchical["\']', "Layout state variable"),
        (r"simulation\s*=\s*null", "Simulation variable"),
        (
            r"function\s+initializeForceDirectedLayout\s*\(",
            "Force layout initialization",
        ),
        (r"function\s+switchLayout\s*\(", "Layout switching function"),
        (r"function\s+setupLayoutToggle\s*\(", "Layout toggle setup"),
        (r"function\s+updatePositionsForceLayout\s*\(", "Force layout position update"),
        (r"function\s+animateToHierarchicalLayout\s*\(", "Hierarchical animation"),
        (r"d3\.forceSimulation", "D3.js force simulation"),
        (r'\.force\(["\']link["\']', "Link force"),
        (r'\.force\(["\']charge["\']', "Charge force"),
        (r'\.force\(["\']center["\']', "Center force"),
        (r'\.force\(["\']collision["\']', "Collision force"),
    ]

    print("\n⚙️ Testing JavaScript Functions:")
    for pattern, description in js_tests:
        if re.search(pattern, html_content, re.MULTILINE):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT FOUND")
            return False

    # Test 4: Enhanced drag functions
    enhanced_drag_tests = [
        (r"function\s+dragstarted.*currentLayout.*force", "Enhanced drag start"),
        (r"function\s+dragged.*currentLayout.*hierarchical", "Enhanced drag move"),
        (r"function\s+dragended.*currentLayout.*force", "Enhanced drag end"),
    ]

    print("\n🖱️ Testing Enhanced Drag Functions:")
    for pattern, description in enhanced_drag_tests:
        if re.search(pattern, html_content, re.MULTILINE | re.DOTALL):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT FOUND")
            return False

    # Test 5: Integration with existing features
    integration_tests = [
        (r"setupLayoutToggle\(\)", "Layout toggle setup call"),
        (r"shouldShowEdge.*edge.*force", "Edge filtering integration"),
        (r"updatePositions.*currentLayout", "Position update integration"),
    ]

    print("\n🔗 Testing Feature Integration:")
    for pattern, description in integration_tests:
        if re.search(pattern, html_content, re.MULTILINE | re.DOTALL):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT FOUND")
            return False

    # Test 6: Accessibility features
    accessibility_tests = [
        (
            r'(role=["\']switch["\']|setAttribute\(["\']role["\'],\s*["\']switch["\'])',
            "ARIA switch role",
        ),
        (r"aria-checked", "ARIA checked state"),
        (r'tabindex=["\']0["\']', "Keyboard navigation"),
        (r'addEventListener\(["\']keydown["\']', "Keyboard event handling"),
    ]

    print("\n♿ Testing Accessibility Features:")
    for pattern, description in accessibility_tests:
        if re.search(pattern, html_content):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NOT FOUND")
            return False

    print("\n🎉 All Force-Directed Layout Tests Passed!")
    print("=" * 50)

    # File size check
    file_size_kb = len(html_content.encode("utf-8")) / 1024
    print(f"📊 HTML file size: {file_size_kb:.1f} KB")

    if file_size_kb > 500:
        print("⚠️ Warning: Large file size may affect loading performance")

    return True


def test_feature_completeness():
    """Test that all documented features are implemented."""

    print("\n🔍 Testing Feature Completeness")
    print("-" * 30)

    # Check if documentation files exist
    docs = ["FORCE_DIRECTED_LAYOUT_FEATURE.md", "graph_output/README.md"]

    for doc in docs:
        if Path(doc).exists():
            print(f"   ✅ Documentation: {doc}")
        else:
            print(f"   ❌ Missing documentation: {doc}")
            return False

    print("\n✅ All documentation files present")
    return True


def main():
    """Run all tests for the force-directed layout feature."""

    print("🚀 Force-Directed Layout Feature Test Suite")
    print("=" * 60)

    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Run tests
    implementation_ok = test_force_directed_layout_implementation()
    documentation_ok = test_feature_completeness()

    if implementation_ok and documentation_ok:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print(
            "The Force-Directed Layout feature is fully implemented and ready for use."
        )
        print("\nTo test the feature:")
        print("1. Open graph_output/enhanced_dependency_graph.html in a web browser")
        print("2. Look for the 'Layout Control' section in the control panel")
        print("3. Click the toggle switch to switch between layouts")
        print("4. Test dragging nodes in force-directed mode")
        print("5. Verify smooth transitions between layout modes")
    else:
        print("\n❌ TESTS FAILED!")
        print("Please review the implementation and fix any missing components.")

    return implementation_ok and documentation_ok


if __name__ == "__main__":
    main()
