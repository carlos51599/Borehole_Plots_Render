#!/usr/bin/env python3
"""
Toggle Button Test Script
Tests if the layout toggle button properly switches between hierarchical and force layouts
"""

import webbrowser
import time
from pathlib import Path


def test_toggle_functionality():
    """Test the toggle button functionality manually"""

    # Path to the generated HTML file
    graph_output_dir = Path(__file__).parent / "dependency_graph" / "graph_output"
    html_file = graph_output_dir / "enhanced_dependency_graph.html"

    if not html_file.exists():
        print("❌ HTML file not found. Run enhanced_dependency_graph_modular.py first.")
        return False

    print("🧪 Testing Layout Toggle Button Functionality")
    print("=" * 50)

    # Read the HTML content to verify functions exist
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for required functions
    checks = [
        ("initializeControls function", "function initializeControls()" in content),
        ("setupLayoutToggle function", "function setupLayoutToggle()" in content),
        ("switchLayout function", "function switchLayout(newLayout)" in content),
        (
            "window.switchToLayout exposed",
            "window.switchToLayout = switchToLayout" in content,
        ),
        ("Controls initialization called", "initializeControls();" in content),
        (
            "Layout toggle event listeners",
            "toggleSwitch.addEventListener('click', handleToggle)" in content,
        ),
    ]

    print("🔍 Pre-flight checks:")
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        if not result:
            all_passed = False

    if not all_passed:
        print("\n❌ Some pre-flight checks failed. Toggle may not work properly.")
        return False

    print("\n✅ All pre-flight checks passed!")

    print("\n🌐 Opening the dependency graph in browser...")
    print("\n📋 Manual Test Instructions:")
    print("   1. Look for the layout toggle switch in the top-left panel")
    print("   2. The toggle should show '📐 Hierarchical' and '🌐 Force-Directed'")
    print("   3. Click the toggle switch to change layouts")
    print("   4. In Force-Directed mode, nodes should appear as circles")
    print("   5. In Hierarchical mode, nodes should appear as rectangles")
    print("   6. Check browser console for any errors")

    print("\n🔍 Expected Console Output:")
    print("   • 🎮 Initializing UI controls...")
    print("   • 🔄 Switching from hierarchical to force layout")
    print("   • 🚀 Starting D3.js force simulation...")
    print("   • ✅ All UI controls initialized successfully")

    return True


def create_toggle_test_html():
    """Create a minimal test HTML to isolate toggle functionality"""
    test_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Toggle Test</title>
    <style>
        .layout-toggle {
            padding: 10px;
            margin: 20px;
            border: 1px solid #ccc;
            cursor: pointer;
            background: #f9f9f9;
        }
        .toggle-switch {
            width: 50px;
            height: 25px;
            background: #ddd;
            border-radius: 15px;
            position: relative;
            cursor: pointer;
        }
        .toggle-slider {
            width: 20px;
            height: 20px;
            background: #007bff;
            border-radius: 50%;
            position: absolute;
            top: 2.5px;
            left: 2.5px;
            transition: transform 0.3s;
        }
        .toggle-switch.active .toggle-slider {
            transform: translateX(25px);
        }
    </style>
</head>
<body>
    <h1>Layout Toggle Test</h1>
    
    <div class="layout-toggle" id="layout-toggle">
        <span class="layout-toggle-label">📐 Hierarchical</span>
        <div class="toggle-switch" id="toggle-switch">
            <div class="toggle-slider"></div>
        </div>
        <span class="layout-toggle-label">🌐 Force-Directed</span>
    </div>
    
    <div id="status">Status: Hierarchical Layout</div>
    
    <script>
        let currentLayout = "hierarchical";
        
        // Mock switchToLayout function
        window.switchToLayout = function(layout) {
            console.log("✅ switchToLayout called with:", layout);
            document.getElementById('status').textContent = `Status: ${layout} Layout`;
        };
        
        function switchLayout(newLayout) {
            if (newLayout === currentLayout) return;
            
            console.log(`🔄 Switching from ${currentLayout} to ${newLayout} layout`);
            currentLayout = newLayout;
            
            const toggleSwitch = document.getElementById('toggle-switch');
            
            if (newLayout === "force") {
                toggleSwitch.classList.add('active');
                if (typeof window.switchToLayout === 'function') {
                    window.switchToLayout("force");
                } else {
                    console.error("❌ switchToLayout function not available!");
                }
            } else {
                toggleSwitch.classList.remove('active');
                if (typeof window.switchToLayout === 'function') {
                    window.switchToLayout("hierarchical");
                } else {
                    console.error("❌ switchToLayout function not available!");
                }
            }
        }
        
        function setupLayoutToggle() {
            const toggleSwitch = document.getElementById('toggle-switch');
            const layoutToggle = document.getElementById('layout-toggle');
            
            function handleToggle() {
                const newLayout = currentLayout === "hierarchical" ? "force" : "hierarchical";
                switchLayout(newLayout);
            }
            
            toggleSwitch.addEventListener('click', handleToggle);
            layoutToggle.addEventListener('click', function(event) {
                if (event.target === toggleSwitch || event.target.closest('.toggle-switch')) {
                    return;
                }
                handleToggle();
            });
            
            console.log("✅ Toggle setup complete");
        }
        
        document.addEventListener("DOMContentLoaded", function() {
            console.log("🚀 Initializing toggle test...");
            setupLayoutToggle();
        });
    </script>
</body>
</html>"""

    test_file = Path(__file__).parent / "toggle_test.html"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_html)

    print(f"📄 Created toggle test file: {test_file}")
    return test_file


if __name__ == "__main__":
    print("🧪 Layout Toggle Functionality Test\n")

    # Create isolated test
    test_file = create_toggle_test_html()
    print(f"🔬 Isolated test created: {test_file}")
    print("   Open this file to test toggle functionality in isolation\n")

    # Test main implementation
    success = test_toggle_functionality()

    if success:
        print("\n🎉 Toggle button test setup complete!")
        print("\n💡 Next Steps:")
        print("   1. Open the main HTML file")
        print("   2. Test the layout toggle switch")
        print("   3. Verify circles appear in force-directed mode")
        print("   4. Check browser console for any errors")
    else:
        print("\n❌ Toggle button test setup failed. Check the implementation.")
