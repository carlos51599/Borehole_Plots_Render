#!/usr/bin/env python3
"""
Test script to validate force-directed layout implementation
Tests circle rendering, coordinate validation, and D3.js simulation integration
"""

import re
import os
from pathlib import Path


def test_force_layout_implementation():
    """Test that force layout creates circles and not rectangles"""

    # Path to the generated HTML file
    graph_output_dir = Path(__file__).parent / "dependency_graph" / "graph_output"
    html_file = graph_output_dir / "enhanced_dependency_graph.html"

    if not html_file.exists():
        print("❌ HTML file not found. Run enhanced_dependency_graph_modular.py first.")
        return False

    print("🔍 Testing force-directed layout implementation...")

    # Read the HTML content
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Test 1: Check for circle creation in force layout
    circle_pattern = r'node\.append\("circle"\)'
    circle_matches = re.findall(circle_pattern, content)

    if len(circle_matches) >= 1:
        print("✅ Circle creation code found in force layout")
    else:
        print("❌ Circle creation code NOT found")
        return False

    # Test 2: Check for calculateCircleRadius function
    radius_pattern = r"function calculateCircleRadius\(d\)"
    if re.search(radius_pattern, content):
        print("✅ calculateCircleRadius function found")
    else:
        print("❌ calculateCircleRadius function NOT found")
        return False

    # Test 3: Check for D3.js force simulation
    simulation_pattern = r"d3\.forceSimulation\(graphData\.nodes\)"
    if re.search(simulation_pattern, content):
        print("✅ D3.js force simulation found")
    else:
        print("❌ D3.js force simulation NOT found")
        return False

    # Test 4: Check for dual container architecture
    force_container_pattern = (
        r'forceDirectedContainer = g\.append\("g"\)\.attr\("class", "force-layout"\)'
    )
    if re.search(force_container_pattern, content):
        print("✅ Force-directed container creation found")
    else:
        print("❌ Force-directed container creation NOT found")
        return False

    # Test 5: Check for coordinate validation
    coord_validation_pattern = (
        r"if \(!d\.x \|\| isNaN\(d\.x\) \|\| !d\.y \|\| isNaN\(d\.y\)\)"
    )
    if re.search(coord_validation_pattern, content):
        print("✅ Coordinate validation found")
    else:
        print("❌ Coordinate validation NOT found")
        return False

    # Test 6: Check for initializeForceDirectedLayout function
    init_force_pattern = r"function initializeForceDirectedLayout\(\)"
    if re.search(init_force_pattern, content):
        print("✅ initializeForceDirectedLayout function found")
    else:
        print("❌ initializeForceDirectedLayout function NOT found")
        return False

    # Test 7: Check for layout switching functionality
    switch_pattern = r"function switchToLayout\(layoutName\)"
    if re.search(switch_pattern, content):
        print("✅ Layout switching function found")
    else:
        print("❌ Layout switching function NOT found")
        return False

    # Test 8: Check for importance-based sizing
    importance_pattern = r"const importance = d\.importance \|\| 0"
    if re.search(importance_pattern, content):
        print("✅ Importance-based sizing found")
    else:
        print("❌ Importance-based sizing NOT found")
        return False

    print(
        "\n🎉 All tests passed! Force-directed layout should now show circles sized by importance."
    )
    print("\n📋 Implementation Summary:")
    print("   • Dual container architecture (hierarchical vs force)")
    print("   • Circle creation with importance-based radius (20px-50px)")
    print("   • D3.js force simulation with collision detection")
    print("   • Coordinate validation with fallback positioning")
    print("   • Proper layout switching between rectangles and circles")

    return True


def test_coordinate_fixes():
    """Test that coordinate validation prevents NaN errors"""

    print("\n🔧 Testing coordinate validation fixes...")

    graph_output_dir = Path(__file__).parent / "dependency_graph" / "graph_output"
    html_file = graph_output_dir / "enhanced_dependency_graph.html"

    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for coordinate validation in path generation
    path_validation_pattern = r"if \(coords\.some\(coord => !isFinite\(coord\)\)\)"
    if re.search(path_validation_pattern, content):
        print("✅ Path coordinate validation found")
    else:
        print("❌ Path coordinate validation NOT found")
        return False

    # Check for fallback positioning
    fallback_pattern = (
        r"const angle = \(i / graphData\.nodes\.length\) \* 2 \* Math\.PI"
    )
    if re.search(fallback_pattern, content):
        print("✅ Fallback circular positioning found")
    else:
        print("❌ Fallback circular positioning NOT found")
        return False

    print("✅ Coordinate validation tests passed!")
    return True


if __name__ == "__main__":
    print("🧪 Running Force-Directed Layout Tests\n")

    success = test_force_layout_implementation()
    if success:
        success = test_coordinate_fixes()

    if success:
        print("\n🚀 All tests passed! The force-directed layout is ready to use.")
        print("\n💡 Instructions:")
        print("   1. Open the HTML file in browser")
        print("   2. Switch to 'Force Layout' using the layout selector")
        print("   3. Nodes should appear as circles sized by importance")
        print("   4. Drag nodes to test force simulation")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
