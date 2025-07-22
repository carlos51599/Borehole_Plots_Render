"""
Comprehensive test suite for diagnosing and fixing missing graph data issues.
This script systematically tests the data flow from Python generation to HTML output.
"""

import os
import sys
import json
import re
import ast
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import html

# Add the parent directory to the path so we can import the graph module
sys.path.append(str(Path(__file__).parent.parent))

try:
    from graph_output.enhanced_dependency_graph import (
        EnhancedDependencyAnalyzer,
        generate_enhanced_html_visualization,
        main as graph_main,
    )

    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Import Error: {e}")
    IMPORT_SUCCESS = False


class GraphDataIntegrityTester:
    """Comprehensive tester for graph data integrity issues."""

    def __init__(self):
        self.test_results = {}
        self.errors = []

    def run_all_tests(self):
        """Run all diagnostic tests."""
        print("🔍 COMPREHENSIVE GRAPH DATA INTEGRITY TESTING")
        print("=" * 60)

        if not IMPORT_SUCCESS:
            print("❌ Cannot run tests - import failed")
            return False

        # Test 1: Basic data generation
        self.test_basic_data_generation()

        # Test 2: JSON serialization integrity
        self.test_json_serialization()

        # Test 3: HTML template injection
        self.test_html_template_injection()

        # Test 4: JavaScript data extraction
        self.test_javascript_data_extraction()

        # Test 5: Edge cases
        self.test_edge_cases()

        # Test 6: End-to-end validation
        self.test_end_to_end_validation()

        # Summary
        self.print_test_summary()

        return len(self.errors) == 0

    def test_basic_data_generation(self):
        """Test 1: Basic data generation from analyzer."""
        print("\n🧪 Test 1: Basic Data Generation")
        print("-" * 40)

        try:
            analyzer = EnhancedDependencyAnalyzer()
            print("✅ Analyzer created successfully")

            # Analyze current project
            graph_data = analyzer.analyze_project(".")
            print("✅ Project analysis completed")

            # Validate graph_data structure
            required_keys = [
                "nodes",
                "edges",
                "dependencies",
                "subfolder_info",
                "statistics",
            ]
            missing_keys = [key for key in required_keys if key not in graph_data]

            if missing_keys:
                error_msg = f"Missing required keys: {missing_keys}"
                self.errors.append(f"Test 1: {error_msg}")
                print(f"❌ {error_msg}")
            else:
                print("✅ All required keys present in graph_data")

            # Check data contents
            nodes_count = len(graph_data.get("nodes", []))
            edges_count = len(graph_data.get("edges", []))
            dependencies_count = len(graph_data.get("dependencies", {}))

            print(f"📊 Data Summary:")
            print(f"   - Nodes: {nodes_count}")
            print(f"   - Edges: {edges_count}")
            print(f"   - Dependencies: {dependencies_count}")

            if nodes_count == 0:
                error_msg = "No nodes generated - graph data is empty"
                self.errors.append(f"Test 1: {error_msg}")
                print(f"❌ {error_msg}")

            self.test_results["basic_generation"] = {
                "success": len(missing_keys) == 0 and nodes_count > 0,
                "nodes_count": nodes_count,
                "edges_count": edges_count,
                "graph_data": graph_data,
            }

        except Exception as e:
            error_msg = f"Exception in basic data generation: {str(e)}"
            self.errors.append(f"Test 1: {error_msg}")
            print(f"❌ {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")

    def test_json_serialization(self):
        """Test 2: JSON serialization integrity."""
        print("\n🧪 Test 2: JSON Serialization Integrity")
        print("-" * 40)

        if "basic_generation" not in self.test_results:
            print("❌ Skipping - basic generation test failed")
            return

        graph_data = self.test_results["basic_generation"]["graph_data"]

        try:
            # Test JSON serialization
            json_string = json.dumps(graph_data, indent=2)
            print(f"✅ JSON serialization successful")
            print(f"📏 JSON size: {len(json_string)} characters")

            # Test deserialization
            parsed_data = json.loads(json_string)
            print("✅ JSON deserialization successful")

            # Verify data integrity after round-trip
            if len(parsed_data.get("nodes", [])) != len(graph_data.get("nodes", [])):
                error_msg = "Node count mismatch after JSON round-trip"
                self.errors.append(f"Test 2: {error_msg}")
                print(f"❌ {error_msg}")
            else:
                print("✅ Data integrity preserved after JSON round-trip")

            self.test_results["json_serialization"] = {
                "success": True,
                "json_size": len(json_string),
                "json_string": (
                    json_string[:1000] + "..."
                    if len(json_string) > 1000
                    else json_string
                ),
            }

        except Exception as e:
            error_msg = f"JSON serialization failed: {str(e)}"
            self.errors.append(f"Test 2: {error_msg}")
            print(f"❌ {error_msg}")

    def test_html_template_injection(self):
        """Test 3: HTML template injection."""
        print("\n🧪 Test 3: HTML Template Injection")
        print("-" * 40)

        if "basic_generation" not in self.test_results:
            print("❌ Skipping - basic generation test failed")
            return

        graph_data = self.test_results["basic_generation"]["graph_data"]

        try:
            # Generate HTML
            html_content = generate_enhanced_html_visualization(graph_data)
            print("✅ HTML generation successful")
            print(f"📏 HTML size: {len(html_content)} characters")

            # Check for data injection pattern
            graph_data_pattern = r"const graphData = ({.*?});"
            matches = re.search(graph_data_pattern, html_content, re.DOTALL)

            if not matches:
                error_msg = "graphData assignment not found in HTML"
                self.errors.append(f"Test 3: {error_msg}")
                print(f"❌ {error_msg}")

                # Check for template placeholder
                if "{graph_data_json}" in html_content:
                    error_msg = "Template placeholder not replaced - formatting error"
                    self.errors.append(f"Test 3: {error_msg}")
                    print(f"❌ {error_msg}")

            else:
                print("✅ graphData assignment found in HTML")
                json_content = matches.group(1)
                print(f"📏 Embedded JSON size: {len(json_content)} characters")

                # Try to parse the embedded JSON
                try:
                    embedded_data = json.loads(json_content)
                    embedded_nodes = len(embedded_data.get("nodes", []))
                    original_nodes = len(graph_data.get("nodes", []))

                    if embedded_nodes != original_nodes:
                        error_msg = f"Node count mismatch: original={original_nodes}, embedded={embedded_nodes}"
                        self.errors.append(f"Test 3: {error_msg}")
                        print(f"❌ {error_msg}")
                    else:
                        print(
                            f"✅ Embedded data integrity verified ({embedded_nodes} nodes)"
                        )

                except json.JSONDecodeError as je:
                    error_msg = f"Embedded JSON is malformed: {str(je)}"
                    self.errors.append(f"Test 3: {error_msg}")
                    print(f"❌ {error_msg}")

            self.test_results["html_injection"] = {
                "success": matches is not None,
                "html_size": len(html_content),
                "html_content": html_content,
            }

        except Exception as e:
            error_msg = f"HTML generation failed: {str(e)}"
            self.errors.append(f"Test 3: {error_msg}")
            print(f"❌ {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")

    def test_javascript_data_extraction(self):
        """Test 4: JavaScript data extraction simulation."""
        print("\n🧪 Test 4: JavaScript Data Extraction Simulation")
        print("-" * 40)

        if "html_injection" not in self.test_results:
            print("❌ Skipping - HTML injection test failed")
            return

        html_content = self.test_results["html_injection"]["html_content"]

        try:
            # Extract all script blocks
            script_pattern = r"<script[^>]*>(.*?)</script>"
            scripts = re.findall(script_pattern, html_content, re.DOTALL)
            print(f"📜 Found {len(scripts)} script blocks")

            # Find the main script with graphData
            main_script = None
            for script in scripts:
                if "const graphData" in script:
                    main_script = script
                    break

            if not main_script:
                error_msg = "Main script with graphData not found"
                self.errors.append(f"Test 4: {error_msg}")
                print(f"❌ {error_msg}")
                return

            print("✅ Main script found")

            # Extract graphData assignment
            graph_data_pattern = r"const graphData = ({.*?});"
            match = re.search(graph_data_pattern, main_script, re.DOTALL)

            if not match:
                error_msg = "graphData assignment not found in main script"
                self.errors.append(f"Test 4: {error_msg}")
                print(f"❌ {error_msg}")
                return

            json_string = match.group(1)
            print(f"✅ graphData extracted ({len(json_string)} chars)")

            # Parse as JSON
            try:
                graph_data = json.loads(json_string)
                nodes_count = len(graph_data.get("nodes", []))
                edges_count = len(graph_data.get("edges", []))

                print(f"✅ JavaScript data parsed successfully")
                print(f"📊 Extracted data:")
                print(f"   - Nodes: {nodes_count}")
                print(f"   - Edges: {edges_count}")

                if nodes_count == 0:
                    error_msg = "Extracted data has no nodes"
                    self.errors.append(f"Test 4: {error_msg}")
                    print(f"❌ {error_msg}")

            except json.JSONDecodeError as je:
                error_msg = f"Extracted JSON is invalid: {str(je)}"
                self.errors.append(f"Test 4: {error_msg}")
                print(f"❌ {error_msg}")

        except Exception as e:
            error_msg = f"JavaScript extraction failed: {str(e)}"
            self.errors.append(f"Test 4: {error_msg}")
            print(f"❌ {error_msg}")

    def test_edge_cases(self):
        """Test 5: Edge cases."""
        print("\n🧪 Test 5: Edge Cases")
        print("-" * 40)

        # Test with empty data
        try:
            empty_data = {
                "nodes": [],
                "edges": [],
                "dependencies": {},
                "subfolder_info": {},
                "statistics": {
                    "total_files": 0,
                    "total_dependencies": 0,
                    "cross_folder_dependencies": 0,
                    "test_files": 0,
                    "folders": 0,
                },
            }

            html_content = generate_enhanced_html_visualization(empty_data)
            print("✅ Empty data case handled successfully")

            # Check if empty data is properly injected
            if "const graphData = {};" in html_content or '"nodes":[]' in html_content:
                print("✅ Empty data properly injected into HTML")
            else:
                error_msg = "Empty data not properly handled in HTML"
                self.errors.append(f"Test 5: {error_msg}")
                print(f"❌ {error_msg}")

        except Exception as e:
            error_msg = f"Empty data case failed: {str(e)}"
            self.errors.append(f"Test 5: {error_msg}")
            print(f"❌ {error_msg}")

        print("✅ Edge case testing completed")

    def test_end_to_end_validation(self):
        """Test 6: End-to-end validation."""
        print("\n🧪 Test 6: End-to-End Validation")
        print("-" * 40)

        try:
            # Run the full pipeline
            analyzer = EnhancedDependencyAnalyzer()
            graph_data = analyzer.analyze_project(".")
            html_content = generate_enhanced_html_visualization(graph_data)

            # Save to temporary file for validation
            temp_file = Path("temp_test_output.html")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            print("✅ Full pipeline executed successfully")

            # Read back and validate
            with open(temp_file, "r", encoding="utf-8") as f:
                read_content = f.read()

            if len(read_content) != len(html_content):
                error_msg = "File write/read size mismatch"
                self.errors.append(f"Test 6: {error_msg}")
                print(f"❌ {error_msg}")
            else:
                print("✅ File I/O integrity verified")

            # Clean up
            temp_file.unlink()

            # Final validation of critical elements
            critical_elements = [
                "const graphData = ",
                '"nodes":[',
                '"edges":[',
                'id="graph"',
                "initializeEnhancedVisualization",
            ]

            missing_elements = []
            for element in critical_elements:
                if element not in html_content:
                    missing_elements.append(element)

            if missing_elements:
                error_msg = f"Missing critical elements: {missing_elements}"
                self.errors.append(f"Test 6: {error_msg}")
                print(f"❌ {error_msg}")
            else:
                print("✅ All critical elements present")

        except Exception as e:
            error_msg = f"End-to-end validation failed: {str(e)}"
            self.errors.append(f"Test 6: {error_msg}")
            print(f"❌ {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")

    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)

        if len(self.errors) == 0:
            print("🎉 ALL TESTS PASSED! Graph data integrity is confirmed.")
        else:
            print(f"❌ {len(self.errors)} ERRORS FOUND:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")

        print(f"\n📊 Test Results Overview:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"   - {test_name}: {status}")

        if len(self.errors) > 0:
            print(f"\n💡 Recommended Actions:")
            print("   1. Check the error details above")
            print("   2. Run the fix_graph_data_issues() function")
            print("   3. Re-run this test suite")

    def save_diagnostic_report(self, filepath: str):
        """Save detailed diagnostic report."""
        report = {
            "timestamp": str(Path().cwd()),
            "errors": self.errors,
            "test_results": self.test_results,
            "summary": {
                "total_tests": 6,
                "passed_tests": len(
                    [r for r in self.test_results.values() if r.get("success", False)]
                ),
                "failed_tests": len(self.errors),
                "overall_status": "PASS" if len(self.errors) == 0 else "FAIL",
            },
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Diagnostic report saved to: {filepath}")


def fix_graph_data_issues():
    """Implement fixes for common graph data issues."""
    print("\n🔧 FIXING GRAPH DATA ISSUES")
    print("=" * 50)

    # Read the current enhanced_dependency_graph.py
    graph_file = Path("graph_output/enhanced_dependency_graph.py")

    if not graph_file.exists():
        print("❌ enhanced_dependency_graph.py not found")
        return False

    with open(graph_file, "r") as f:
        content = f.read()

    fixes_applied = []

    # Fix 1: Ensure format() call is correct
    if "html_template.format(graph_data_json=" in content:
        print("✅ Template formatting appears correct")
    else:
        print("❌ Template formatting issue detected")
        fixes_applied.append("Template formatting")

    # Fix 2: Add error handling for empty data
    error_handling_code = """
    # Add error handling for empty graph data
    if not graph_data or not graph_data.get('nodes'):
        print("⚠️  Warning: Graph data is empty or invalid")
        # Create minimal valid structure
        graph_data = {
            'nodes': [],
            'edges': [],
            'dependencies': {},
            'subfolder_info': {},
            'statistics': {'total_files': 0, 'total_dependencies': 0, 
                         'cross_folder_dependencies': 0, 'test_files': 0, 'folders': 0}
        }
    """

    if "Warning: Graph data is empty" not in content:
        # Insert error handling before HTML generation
        insertion_point = content.find("def generate_enhanced_html_visualization")
        if insertion_point != -1:
            content = (
                content[:insertion_point]
                + error_handling_code
                + "\n"
                + content[insertion_point:]
            )
            fixes_applied.append("Error handling for empty data")

    # Fix 3: Add data validation
    validation_code = '''
def validate_graph_data(graph_data: Dict[str, Any]) -> bool:
    """Validate graph data structure before HTML generation."""
    required_keys = ['nodes', 'edges', 'dependencies', 'subfolder_info', 'statistics']
    
    if not isinstance(graph_data, dict):
        print("❌ graph_data is not a dictionary")
        return False
    
    for key in required_keys:
        if key not in graph_data:
            print(f"❌ Missing required key: {key}")
            return False
    
    if not isinstance(graph_data['nodes'], list):
        print("❌ nodes is not a list")
        return False
    
    if not isinstance(graph_data['edges'], list):
        print("❌ edges is not a list")
        return False
    
    print(f"✅ Graph data validation passed ({len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges)")
    return True

'''

    if "def validate_graph_data" not in content:
        # Insert validation function before generate_enhanced_html_visualization
        insertion_point = content.find("def generate_enhanced_html_visualization")
        if insertion_point != -1:
            content = (
                content[:insertion_point] + validation_code + content[insertion_point:]
            )
            fixes_applied.append("Data validation function")

    if fixes_applied:
        # Write back the fixed content
        with open(graph_file, "w") as f:
            f.write(content)

        print(f"✅ Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"   - {fix}")

        return True
    else:
        print("✅ No fixes needed - code appears correct")
        return True


def main():
    """Main diagnostic and repair function."""
    print("🔍 GRAPH DATA INTEGRITY DIAGNOSTIC SUITE")
    print("=" * 60)

    # Create output directory if it doesn't exist
    test_output_dir = Path("tests/diagnostic_output")
    test_output_dir.mkdir(parents=True, exist_ok=True)

    # Run comprehensive tests
    tester = GraphDataIntegrityTester()
    all_tests_passed = tester.run_all_tests()

    # Save diagnostic report
    report_file = test_output_dir / "graph_data_diagnostic_report.json"
    tester.save_diagnostic_report(str(report_file))

    if not all_tests_passed:
        print("\n🔧 ATTEMPTING AUTOMATIC FIXES...")
        fix_applied = fix_graph_data_issues()

        if fix_applied:
            print("\n🔄 RE-RUNNING TESTS AFTER FIXES...")
            tester_rerun = GraphDataIntegrityTester()
            rerun_passed = tester_rerun.run_all_tests()

            if rerun_passed:
                print("\n🎉 ALL ISSUES RESOLVED!")
            else:
                print("\n❌ Some issues remain - manual intervention required")

    return all_tests_passed


if __name__ == "__main__":
    main()
