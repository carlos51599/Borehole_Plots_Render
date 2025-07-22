"""
Comprehensive validation suite to prevent and detect graph data issues.
This script should be run after every modification to the enhanced_dependency_graph.py file.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List


class ComprehensiveValidator:
    """Complete validation suite for graph visualization."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.tests_passed = 0
        self.tests_total = 0

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a test and track results."""
        self.tests_total += 1
        print(f"\n{self.tests_total}. {test_name}")
        print("-" * 50)

        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                print(f"✅ PASS: {test_name}")
                return True
            else:
                print(f"❌ FAIL: {test_name}")
                return False
        except Exception as e:
            error_msg = f"Exception in {test_name}: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ ERROR: {error_msg}")
            return False

    def test_python_code_integrity(self) -> bool:
        """Test that the Python code can be imported and run."""
        try:
            sys.path.append(str(Path(".").resolve()))
            from graph_output.enhanced_dependency_graph import (
                EnhancedDependencyAnalyzer,
                generate_enhanced_html_visualization,
            )

            # Test instantiation
            analyzer = EnhancedDependencyAnalyzer()
            print("✅ Python code imports successfully")

            # Test data generation
            graph_data = analyzer.analyze_project(".")
            required_keys = [
                "nodes",
                "edges",
                "dependencies",
                "subfolder_info",
                "statistics",
            ]

            for key in required_keys:
                if key not in graph_data:
                    self.errors.append(f"Missing key in graph_data: {key}")
                    return False

            nodes_count = len(graph_data["nodes"])
            edges_count = len(graph_data["edges"])

            print(
                f"✅ Data generation successful: {nodes_count} nodes, {edges_count} edges"
            )

            if nodes_count == 0:
                self.warnings.append("No nodes generated - check file discovery")
                return False

            return True

        except ImportError as e:
            self.errors.append(f"Import error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Python execution error: {e}")
            return False

    def test_html_generation(self) -> bool:
        """Test HTML generation process."""
        try:
            sys.path.append(str(Path(".").resolve()))
            from graph_output.enhanced_dependency_graph import (
                EnhancedDependencyAnalyzer,
                generate_enhanced_html_visualization,
            )

            analyzer = EnhancedDependencyAnalyzer()
            graph_data = analyzer.analyze_project(".")

            # Generate HTML
            html_content = generate_enhanced_html_visualization(graph_data)

            print(f"✅ HTML generated: {len(html_content)} characters")

            # Check for template injection
            if "{graph_data_json}" in html_content:
                self.errors.append("Template placeholder not replaced")
                return False

            # Check for data presence
            if "const graphData = {" not in html_content:
                self.errors.append("graphData assignment not found in HTML")
                return False

            print("✅ HTML structure is valid")
            return True

        except Exception as e:
            self.errors.append(f"HTML generation error: {e}")
            return False

    def test_javascript_syntax(self) -> bool:
        """Test JavaScript syntax in generated HTML."""
        html_file = Path("graph_output/enhanced_dependency_graph.html")

        if not html_file.exists():
            self.errors.append("HTML file does not exist")
            return False

        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read HTML file: {e}")
            return False

        # Extract JavaScript
        script_pattern = r"<script[^>]*>(.*?)</script>"
        scripts = re.findall(script_pattern, content, re.DOTALL)

        main_script = None
        for script in scripts:
            if "graphData" in script and len(script) > 1000:
                main_script = script
                break

        if not main_script:
            self.errors.append("Main JavaScript block not found")
            return False

        # Check brace balance
        open_braces = main_script.count("{")
        close_braces = main_script.count("}")

        if open_braces != close_braces:
            self.errors.append(
                f"JavaScript brace mismatch: {open_braces} open, {close_braces} close"
            )
            return False

        # Check parentheses balance
        open_parens = main_script.count("(")
        close_parens = main_script.count(")")

        if open_parens != close_parens:
            self.errors.append(
                f"JavaScript parentheses mismatch: {open_parens} open, {close_parens} close"
            )
            return False

        print(
            f"✅ JavaScript syntax valid: {open_braces} braces, {open_parens} parentheses"
        )
        return True

    def test_data_extraction(self) -> bool:
        """Test that data can be extracted from HTML."""
        html_file = Path("graph_output/enhanced_dependency_graph.html")

        if not html_file.exists():
            self.errors.append("HTML file does not exist")
            return False

        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract graphData
            pattern = r"const graphData = ({.*?});"
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                self.errors.append("Could not extract graphData from HTML")
                return False

            json_str = match.group(1)

            # Parse JSON
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                self.errors.append(f"GraphData JSON is invalid: {e}")
                return False

            # Validate structure
            required_keys = ["nodes", "edges", "dependencies", "subfolder_info"]
            for key in required_keys:
                if key not in data:
                    self.errors.append(f"Missing key in extracted data: {key}")
                    return False

            nodes_count = len(data["nodes"])
            edges_count = len(data["edges"])

            print(
                f"✅ Data extraction successful: {nodes_count} nodes, {edges_count} edges"
            )

            if nodes_count == 0:
                self.warnings.append("Extracted data has no nodes")
                return False

            return True

        except Exception as e:
            self.errors.append(f"Data extraction error: {e}")
            return False

    def test_file_completeness(self) -> bool:
        """Test that all expected files exist and are complete."""
        required_files = [
            "graph_output/enhanced_dependency_graph.py",
            "graph_output/enhanced_dependency_graph.html",
        ]

        for file_path in required_files:
            path = Path(file_path)
            if not path.exists():
                self.errors.append(f"Required file missing: {file_path}")
                return False

            # Check file size
            size = path.stat().st_size
            if size < 1000:  # Very small files are likely incomplete
                self.errors.append(
                    f"File suspiciously small: {file_path} ({size} bytes)"
                )
                return False

        print("✅ All required files present and adequately sized")
        return True

    def test_browser_compatibility(self) -> bool:
        """Test browser compatibility markers."""
        html_file = Path("graph_output/enhanced_dependency_graph.html")

        if not html_file.exists():
            self.errors.append("HTML file does not exist")
            return False

        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for required elements
            required_elements = [
                "<!DOCTYPE html>",
                '<meta charset="UTF-8">',
                "https://d3js.org/d3.v7.min.js",
                'id="graph"',
                "DOMContentLoaded",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)

            if missing_elements:
                self.errors.append(
                    f"Missing browser compatibility elements: {missing_elements}"
                )
                return False

            print("✅ Browser compatibility elements present")
            return True

        except Exception as e:
            self.errors.append(f"Browser compatibility check error: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all validation tests."""
        print("🔍 COMPREHENSIVE GRAPH VALIDATION SUITE")
        print("=" * 60)

        # Define all tests
        tests = [
            ("Python Code Integrity", self.test_python_code_integrity),
            ("HTML Generation", self.test_html_generation),
            ("JavaScript Syntax", self.test_javascript_syntax),
            ("Data Extraction", self.test_data_extraction),
            ("File Completeness", self.test_file_completeness),
            ("Browser Compatibility", self.test_browser_compatibility),
        ]

        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        print(f"Tests passed: {self.tests_passed}/{self.tests_total}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        success = self.tests_passed == self.tests_total and len(self.errors) == 0

        if success:
            print("\n🎉 ALL TESTS PASSED! Graph visualization is ready.")
        else:
            print(
                f"\n❌ VALIDATION FAILED! {len(self.errors)} errors need to be fixed."
            )

        return success


def main():
    """Main validation function."""
    validator = ComprehensiveValidator()
    success = validator.run_all_tests()

    if success:
        print("\n✅ GRAPH VALIDATION COMPLETE - NO ISSUES FOUND")
        print("The enhanced dependency graph should work perfectly!")
    else:
        print("\n❌ GRAPH VALIDATION FAILED - ISSUES DETECTED")
        print("Please review and fix the issues above before using the visualization.")

    return success


if __name__ == "__main__":
    main()
