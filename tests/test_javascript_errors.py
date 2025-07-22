"""
Browser-Simulation JavaScript Error Detection Tool
Identifies potential JavaScript runtime issues that could prevent graph visualization.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any


class JavaScriptErrorDetector:
    """Detect potential JavaScript runtime errors in HTML files."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_html_for_js_errors(self, html_path: str) -> Dict[str, Any]:
        """Check HTML file for potential JavaScript errors."""
        print(f"🔍 Checking JavaScript in: {html_path}")
        print("-" * 50)

        file_path = Path(html_path)
        if not file_path.exists():
            error = f"File not found: {html_path}"
            self.errors.append(error)
            return {"success": False, "error": error}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()
                self.warnings.append(
                    "File had encoding issues - some characters may be corrupted"
                )

        # Extract JavaScript code
        script_pattern = r"<script[^>]*>(.*?)</script>"
        scripts = re.findall(script_pattern, html_content, re.DOTALL)

        main_script = None
        for script in scripts:
            if "graphData" in script and "initializeEnhancedVisualization" in script:
                main_script = script
                break

        if not main_script:
            error = "Main script with graph initialization not found"
            self.errors.append(error)
            return {"success": False, "error": error}

        print("✅ Main script found")

        # Check for specific JavaScript issues
        self._check_syntax_issues(main_script)
        self._check_data_access_patterns(main_script)
        self._check_d3_usage(main_script)
        self._check_function_definitions(main_script)
        self._check_event_handlers(main_script)

        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "script_length": len(main_script),
        }

    def _check_syntax_issues(self, script: str):
        """Check for common syntax issues."""
        print("🔍 Checking syntax issues...")

        # Check for unmatched braces
        brace_count = script.count("{") - script.count("}")
        if brace_count != 0:
            self.errors.append(f"Unmatched braces: {brace_count} extra opening braces")

        # Check for unmatched parentheses
        paren_count = script.count("(") - script.count(")")
        if paren_count != 0:
            self.errors.append(
                f"Unmatched parentheses: {paren_count} extra opening parentheses"
            )

        # Check for console.log statements that might indicate debugging
        console_logs = len(re.findall(r"console\.log", script))
        if console_logs > 0:
            self.warnings.append(f"Found {console_logs} console.log statements")

        # Check for undefined variables being used
        common_undefined_patterns = [r"undefined\.", r"null\.", r"NaN\."]
        for pattern in common_undefined_patterns:
            matches = re.findall(pattern, script)
            if matches:
                self.errors.append(f"Potential undefined access: {pattern}")

        print(f"✅ Syntax check complete - {len(self.errors)} errors found so far")

    def _check_data_access_patterns(self, script: str):
        """Check for issues in data access patterns."""
        print("🔍 Checking data access patterns...")

        # Check if graphData is properly accessed
        if "graphData.nodes" not in script:
            self.errors.append("graphData.nodes access not found")

        if "graphData.edges" not in script:
            self.errors.append("graphData.edges access not found")

        # Check for potential null/undefined checks
        safe_access_patterns = [
            "graphData && graphData.nodes",
            "graphData?.nodes",
            "graphData.nodes || []",
        ]

        has_safe_access = any(pattern in script for pattern in safe_access_patterns)
        if not has_safe_access:
            self.warnings.append("No null-safe data access patterns found")

        # Check for empty data handling
        empty_data_checks = [
            "graphData.nodes.length === 0",
            "graphData.nodes.length == 0",
            "!graphData.nodes.length",
        ]

        has_empty_check = any(check in script for check in empty_data_checks)
        if not has_empty_check:
            self.warnings.append("No empty data validation found")

        print(f"✅ Data access check complete")

    def _check_d3_usage(self, script: str):
        """Check for D3.js usage issues."""
        print("🔍 Checking D3.js usage...")

        # Check for d3 availability
        if "d3." not in script:
            self.errors.append("No D3.js usage found in script")

        # Check for common D3 patterns
        d3_patterns = ["d3.select", "d3.selectAll", "d3.zoom", "d3.forceSimulation"]

        missing_patterns = []
        for pattern in d3_patterns:
            if pattern not in script:
                missing_patterns.append(pattern)

        if missing_patterns:
            self.warnings.append(f"Missing D3 patterns: {missing_patterns}")

        # Check for SVG manipulation
        if "svg.append" not in script and "svg.select" not in script:
            self.warnings.append("No SVG manipulation found")

        print(f"✅ D3.js check complete")

    def _check_function_definitions(self, script: str):
        """Check for required function definitions."""
        print("🔍 Checking function definitions...")

        required_functions = [
            "initializeEnhancedVisualization",
            "updateEnhancedVisibility",
            "shouldShowNode",
            "shouldShowEdge",
        ]

        missing_functions = []
        for func in required_functions:
            if f"function {func}" not in script and f"{func} =" not in script:
                missing_functions.append(func)

        if missing_functions:
            self.errors.append(f"Missing required functions: {missing_functions}")

        print(f"✅ Function definition check complete")

    def _check_event_handlers(self, script: str):
        """Check for event handler issues."""
        print("🔍 Checking event handlers...")

        # Check for DOM ready handlers
        dom_ready_patterns = [
            'document.addEventListener("DOMContentLoaded"',
            'window.addEventListener("load"',
            "$(document).ready",
        ]

        has_dom_ready = any(pattern in script for pattern in dom_ready_patterns)
        if not has_dom_ready:
            self.warnings.append("No DOM ready event handler found")

        # Check for resize handlers
        if 'window.addEventListener("resize"' not in script:
            self.warnings.append("No window resize handler found")

        print(f"✅ Event handler check complete")

    def generate_fix_suggestions(self) -> List[str]:
        """Generate fix suggestions based on found issues."""
        suggestions = []

        if any("graphData.nodes access not found" in error for error in self.errors):
            suggestions.append(
                "Add proper graphData.nodes access in visualization code"
            )

        if any("Missing required functions" in error for error in self.errors):
            suggestions.append("Implement missing function definitions")

        if any("No null-safe data access" in warning for warning in self.warnings):
            suggestions.append(
                "Add null-safety checks: if (graphData && graphData.nodes) {...}"
            )

        if any("No empty data validation" in warning for warning in self.warnings):
            suggestions.append(
                "Add empty data handling: if (graphData.nodes.length === 0) { /* show message */ }"
            )

        if any("No DOM ready event" in warning for warning in self.warnings):
            suggestions.append(
                "Add DOM ready handler: document.addEventListener('DOMContentLoaded', initializeVisualization)"
            )

        return suggestions


def create_debugging_html():
    """Create a debugging version of the HTML with enhanced error reporting."""
    print("🔧 Creating debugging HTML...")

    debugging_script = """
    <script>
        // Enhanced debugging for graph visualization
        console.log("🔍 Starting graph debugging...");
        
        // Check if D3 is loaded
        if (typeof d3 === 'undefined') {
            console.error("❌ D3.js is not loaded!");
            document.body.innerHTML = "<h1>Error: D3.js not loaded</h1>";
        } else {
            console.log("✅ D3.js loaded successfully");
        }
        
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', function() {
            console.log("✅ DOM ready");
            
            // Check if graphData exists
            if (typeof graphData === 'undefined') {
                console.error("❌ graphData is not defined!");
                document.body.innerHTML = "<h1>Error: graphData not defined</h1>";
                return;
            }
            
            console.log("✅ graphData defined");
            console.log("📊 graphData structure:", {
                nodes: graphData.nodes ? graphData.nodes.length : 'undefined',
                edges: graphData.edges ? graphData.edges.length : 'undefined',
                keys: Object.keys(graphData)
            });
            
            // Check if graphData has expected structure
            if (!graphData.nodes) {
                console.error("❌ graphData.nodes is missing!");
                document.getElementById('graph').innerHTML = "<h2>Error: No nodes data</h2>";
                return;
            }
            
            if (!graphData.edges) {
                console.error("❌ graphData.edges is missing!");
                document.getElementById('graph').innerHTML = "<h2>Error: No edges data</h2>";
                return;
            }
            
            if (graphData.nodes.length === 0) {
                console.warn("⚠️  graphData.nodes is empty!");
                document.getElementById('graph').innerHTML = "<h2>Warning: No nodes to display</h2>";
                return;
            }
            
            console.log("✅ graphData validation passed");
            console.log(`📊 Ready to visualize ${graphData.nodes.length} nodes and ${graphData.edges.length} edges`);
            
            // Check if SVG element exists
            const svg = d3.select("#graph");
            if (svg.empty()) {
                console.error("❌ SVG element #graph not found!");
                return;
            }
            
            console.log("✅ SVG element found");
            
            // Try to call initialization function
            if (typeof initializeEnhancedVisualization === 'function') {
                console.log("🚀 Calling initializeEnhancedVisualization...");
                try {
                    initializeEnhancedVisualization();
                    console.log("✅ Visualization initialized successfully");
                } catch (error) {
                    console.error("❌ Error in visualization initialization:", error);
                    document.getElementById('graph').innerHTML = "<h2>Visualization Error: " + error.message + "</h2>";
                }
            } else {
                console.error("❌ initializeEnhancedVisualization function not found!");
                document.getElementById('graph').innerHTML = "<h2>Error: Initialization function missing</h2>";
            }
        });
        
        // Global error handler
        window.addEventListener('error', function(error) {
            console.error("🚨 Global JavaScript error:", error);
        });
    </script>
    """

    return debugging_script


def main():
    """Main function for JavaScript error detection."""
    print("🔍 JAVASCRIPT ERROR DETECTION")
    print("=" * 50)

    detector = JavaScriptErrorDetector()

    # Check the actual HTML file
    html_file = "graph_output/enhanced_dependency_graph.html"
    result = detector.check_html_for_js_errors(html_file)

    print(f"\n📋 JavaScript Analysis Results:")
    print(f"   - Success: {result['success']}")
    print(f"   - Errors: {len(detector.errors)}")
    print(f"   - Warnings: {len(detector.warnings)}")

    if detector.errors:
        print(f"\n❌ Errors found:")
        for error in detector.errors:
            print(f"   - {error}")

    if detector.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in detector.warnings:
            print(f"   - {warning}")

    # Generate fix suggestions
    suggestions = detector.generate_fix_suggestions()
    if suggestions:
        print(f"\n💡 Fix Suggestions:")
        for suggestion in suggestions:
            print(f"   - {suggestion}")

    # Create debugging HTML snippet
    debug_script = create_debugging_html()
    debug_file = Path("tests/debug_graph.html")

    # Create a minimal HTML file with debugging
    minimal_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Graph Debug</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div id="graph" style="width: 100%; height: 500px; border: 1px solid #ccc;">
        Loading...
    </div>
    
    <script>
        // Test data
        const graphData = {{
            "nodes": [
                {{"id": "test1", "stem": "test", "folder": "root", "x": 100, "y": 100}},
                {{"id": "test2", "stem": "other", "folder": "tests", "x": 200, "y": 200}}
            ],
            "edges": [
                {{"source": 0, "target": 1, "source_name": "test1", "target_name": "test2"}}
            ],
            "dependencies": {{}},
            "subfolder_info": {{}},
            "statistics": {{}}
        }};
        
        function initializeEnhancedVisualization() {{
            console.log("🎨 Initializing test visualization");
            const svg = d3.select("#graph").append("svg")
                .attr("width", "100%")
                .attr("height", "100%");
            
            svg.append("text")
                .attr("x", 50)
                .attr("y", 50)
                .text("Test visualization works! Nodes: " + graphData.nodes.length);
        }}
    </script>
    
    {debug_script}
</body>
</html>"""

    with open(debug_file, "w") as f:
        f.write(minimal_html)

    print(f"\n🛠️  Debug HTML created: {debug_file}")
    print(
        "   - Open this file in a browser and check the console for detailed debugging info"
    )


if __name__ == "__main__":
    main()
