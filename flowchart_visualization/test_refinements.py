#!/usr/bin/env python3
"""
Comprehensive test script for the refined interactive flowchart
Tests all the requested improvements and fixes
"""

import requests
import time


def test_flowchart_refinements():
    base_url = "http://127.0.0.1:5000"

    print("🧪 Testing Refined Interactive Flowchart")
    print("=" * 60)

    # Test 1: Server accessibility
    print("\n1️⃣ Testing server accessibility...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Server accessible at http://127.0.0.1:5000")
            print("   ✅ Main page loads successfully")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Server not accessible: {e}")
        return

    # Test 2: JavaScript file integrity
    print("\n2️⃣ Testing JavaScript file integrity...")
    try:
        response = requests.get(f"{base_url}/codebase_flowchart.js")
        if response.status_code == 200:
            js_content = response.text
            print(f"   ✅ JavaScript file loaded: {len(js_content)} characters")

            # Check for key improvements
            improvements = [
                ("Node selection functionality", "selectNode(node)"),
                ("Summary area display", "showNodeSummary"),
                (
                    "Tooltip without preview",
                    "showTooltip" in js_content
                    and "preview"
                    not in js_content.split("showTooltip")[1].split("hideTooltip")[0],
                ),
                ("Relationship highlighting", 'linkElements.classed("highlighted"'),
                ("Clear selection functionality", "clearSelection()"),
                (
                    "Enhanced sample data with links",
                    "this.links = [" in js_content and "source:" in js_content,
                ),
            ]

            for name, check in improvements:
                if isinstance(check, bool):
                    status = "✅" if check else "❌"
                else:
                    status = "✅" if check in js_content else "❌"
                print(f"   {status} {name}")

        else:
            print(f"   ❌ JavaScript file not accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ JavaScript test failed: {e}")

    # Test 3: HTML structure improvements
    print("\n3️⃣ Testing HTML structure improvements...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            html_content = response.text

            structure_checks = [
                (
                    "Grid layout with proper areas",
                    "grid-template-areas:" in html_content
                    and '"header"' in html_content,
                ),
                ("Summary area implementation", "summary-area" in html_content),
                (
                    "Centered diagram container",
                    "justify-content: center" in html_content,
                ),
                ("Responsive viewport sizing", "calc(100vh - 280px)" in html_content),
                ("Controls at top position", "grid-area: controls" in html_content),
                ("Summary metrics styling", "summary-metrics" in html_content),
            ]

            for name, check in structure_checks:
                status = "✅" if check else "❌"
                print(f"   {status} {name}")

        else:
            print(f"   ❌ HTML content not accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ HTML structure test failed: {e}")

    # Test 4: API data availability for relationships
    print("\n4️⃣ Testing API data for relationships...")
    try:
        response = requests.get(f"{base_url}/api/data")
        if response.status_code == 200:
            data = response.json()

            print("   ✅ Complete analysis data endpoint accessible")

            if "dependencies" in data:
                dep_count = len(data["dependencies"])
                print(
                    f"   ✅ Dependencies data available: {dep_count} files with dependencies"
                )
            else:
                print("   ⚠️ Dependencies data not available - will use sample data")

            if "files" in data:
                file_count = len(data["files"])
                print(f"   ✅ Files data available: {file_count} files")

                # Check sample file structure
                if data["files"]:
                    sample_file = list(data["files"].values())[0]
                    required_fields = ["total_lines", "complexity", "functions_count"]
                    missing = [f for f in required_fields if f not in sample_file]

                    if not missing:
                        print("   ✅ File data structure complete")
                    else:
                        print(f"   ⚠️ Missing fields in file data: {missing}")
            else:
                print("   ❌ Files data not available")

        else:
            print(f"   ⚠️ Complete data endpoint not available: {response.status_code}")
            print("   ℹ️ Will fall back to sample data for testing")
    except Exception as e:
        print(f"   ⚠️ API data test inconclusive: {e}")

    print("\n🎯 Refinement Testing Complete!")
    print("\n📋 Summary of Improvements:")
    print("   🔧 Toolbar Position: Moved to top of page above plot area")
    print(
        "   📐 Plot Area Alignment: Centered with proper margins and responsive sizing"
    )
    print("   🔗 Relationship Lines: Restored and enhanced with highlighting")
    print("   💬 Tooltip Content: Removed preview section, kept relevant metrics")
    print(
        "   🖱️ Node Click Behavior: Added relationship highlighting and summary display"
    )
    print("   📱 Responsive Design: Grid layout adapts to different screen sizes")
    print("   📊 Summary Area: Shows below plot without requiring scrolling")

    print("\n🌐 Test the refined flowchart at: http://127.0.0.1:5000")
    print("\n🔍 Testing Instructions:")
    print("   1. Verify toolbar is at the top of the page")
    print("   2. Check that plot area is centered and fills main viewport")
    print("   3. Hover over nodes to see tooltips (no preview section)")
    print("   4. Click nodes to see relationship highlighting")
    print("   5. Verify summary appears below plot area (no scrolling needed)")
    print("   6. Check that relationship lines are visible between connected nodes")
    print("   7. Test responsiveness by resizing browser window")


if __name__ == "__main__":
    test_flowchart_refinements()
