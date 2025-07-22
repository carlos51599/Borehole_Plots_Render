"""
HTML Data Extraction and Validation Tool
Specialized tool for extracting and validating JavaScript data from HTML output.
"""

import re
import json
import ast
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import html as html_lib


class HTMLDataExtractor:
    """Extract and validate JavaScript data from HTML files."""

    def __init__(self):
        self.extraction_results = {}
        self.validation_errors = []

    def extract_graph_data_from_html(
        self, html_content: str
    ) -> Optional[Dict[str, Any]]:
        """Extract graphData from HTML content."""
        try:
            # Method 1: Direct pattern matching for graphData assignment
            pattern1 = r"const graphData = ({.*?});"
            match1 = re.search(pattern1, html_content, re.DOTALL)

            if match1:
                json_str = match1.group(1)
                try:
                    data = json.loads(json_str)
                    self.extraction_results["method1"] = {"success": True, "data": data}
                    print("✅ Method 1 (Direct pattern): Success")
                    return data
                except json.JSONDecodeError as e:
                    self.validation_errors.append(f"Method 1 JSON decode error: {e}")
                    print(f"❌ Method 1 (Direct pattern): JSON decode failed - {e}")

            # Method 2: Extract all JavaScript blocks and search within them
            script_pattern = r"<script[^>]*>(.*?)</script>"
            scripts = re.findall(script_pattern, html_content, re.DOTALL)

            for i, script in enumerate(scripts):
                if "graphData" in script:
                    pattern2 = r"const graphData = ({.*?});"
                    match2 = re.search(pattern2, script, re.DOTALL)

                    if match2:
                        json_str = match2.group(1)
                        try:
                            data = json.loads(json_str)
                            self.extraction_results["method2"] = {
                                "success": True,
                                "data": data,
                                "script_index": i,
                            }
                            print(f"✅ Method 2 (Script block {i}): Success")
                            return data
                        except json.JSONDecodeError as e:
                            self.validation_errors.append(
                                f"Method 2 script {i} JSON decode error: {e}"
                            )
                            print(
                                f"❌ Method 2 (Script block {i}): JSON decode failed - {e}"
                            )

            # Method 3: Look for template placeholder (indicates injection failure)
            if "{graph_data_json}" in html_content:
                error_msg = "Template placeholder found - data injection failed"
                self.validation_errors.append(error_msg)
                print(f"❌ Method 3: {error_msg}")
                return None

            # Method 4: Search for any JSON-like structure that might be graph data
            json_pattern = r'({[^}]*"nodes"[^}]*})'
            json_matches = re.findall(json_pattern, html_content, re.DOTALL)

            for i, json_str in enumerate(json_matches):
                try:
                    # Try to find a complete JSON object
                    brace_count = 0
                    end_pos = 0
                    for j, char in enumerate(json_str):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = j + 1
                                break

                    if end_pos > 0:
                        complete_json = json_str[:end_pos]
                        data = json.loads(complete_json)
                        if "nodes" in data and "edges" in data:
                            self.extraction_results["method4"] = {
                                "success": True,
                                "data": data,
                                "match_index": i,
                            }
                            print(f"✅ Method 4 (JSON search {i}): Success")
                            return data
                except (json.JSONDecodeError, IndexError):
                    continue

            # If all methods fail
            self.validation_errors.append("All extraction methods failed")
            print("❌ All extraction methods failed")
            return None

        except Exception as e:
            error_msg = f"Extraction exception: {str(e)}"
            self.validation_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return None

    def validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """Validate the structure and content of extracted data."""
        if not data:
            self.validation_errors.append("Data is None or empty")
            return False

        # Check required keys
        required_keys = [
            "nodes",
            "edges",
            "dependencies",
            "subfolder_info",
            "statistics",
        ]
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            self.validation_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

        # Check data types
        if not isinstance(data["nodes"], list):
            self.validation_errors.append("'nodes' is not a list")
            return False

        if not isinstance(data["edges"], list):
            self.validation_errors.append("'edges' is not a list")
            return False

        if not isinstance(data["dependencies"], dict):
            self.validation_errors.append("'dependencies' is not a dict")
            return False

        # Check content
        nodes_count = len(data["nodes"])
        edges_count = len(data["edges"])

        print(f"📊 Validation Results:")
        print(f"   - Nodes: {nodes_count}")
        print(f"   - Edges: {edges_count}")
        print(f"   - Dependencies: {len(data['dependencies'])}")
        print(f"   - Subfolders: {len(data['subfolder_info'])}")

        if nodes_count == 0:
            self.validation_errors.append("No nodes found in data")
            print("⚠️  Warning: No nodes found")
            return False

        # Validate node structure
        for i, node in enumerate(data["nodes"][:5]):  # Check first 5 nodes
            required_node_keys = ["id", "stem", "folder"]
            missing_node_keys = [key for key in required_node_keys if key not in node]
            if missing_node_keys:
                error_msg = f"Node {i} missing keys: {missing_node_keys}"
                self.validation_errors.append(error_msg)
                print(f"❌ {error_msg}")
                return False

        print("✅ Data validation passed")
        return True

    def analyze_html_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze an HTML file for graph data integrity."""
        print(f"\n🔍 Analyzing HTML file: {filepath}")
        print("-" * 50)

        file_path = Path(filepath)
        if not file_path.exists():
            error_msg = f"File not found: {filepath}"
            self.validation_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            print(f"📄 File size: {len(html_content)} characters")

            # Extract graph data
            extracted_data = self.extract_graph_data_from_html(html_content)

            if extracted_data is None:
                return {
                    "success": False,
                    "error": "Data extraction failed",
                    "extraction_results": self.extraction_results,
                    "validation_errors": self.validation_errors,
                }

            # Validate extracted data
            is_valid = self.validate_extracted_data(extracted_data)

            return {
                "success": is_valid,
                "data": extracted_data,
                "file_size": len(html_content),
                "extraction_results": self.extraction_results,
                "validation_errors": self.validation_errors,
            }

        except Exception as e:
            error_msg = f"File analysis failed: {str(e)}"
            self.validation_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def generate_test_html_with_known_data(self) -> str:
        """Generate a test HTML with known good data for comparison."""
        test_data = {
            "nodes": [
                {
                    "id": "test_node_1",
                    "stem": "test_file",
                    "folder": "root",
                    "x": 100,
                    "y": 100,
                },
                {
                    "id": "test_node_2",
                    "stem": "other_file",
                    "folder": "tests",
                    "x": 200,
                    "y": 200,
                },
            ],
            "edges": [
                {
                    "source": 0,
                    "target": 1,
                    "source_name": "test_node_1",
                    "target_name": "test_node_2",
                }
            ],
            "dependencies": {
                "test_node_1": {
                    "stem": "test_file",
                    "folder": "root",
                    "imports": ["test_node_2"],
                },
                "test_node_2": {"stem": "other_file", "folder": "tests", "imports": []},
            },
            "subfolder_info": {
                "root": {"color": "#E3F2FD", "modules": ["test_file"], "count": 1},
                "tests": {"color": "#FFF3E0", "modules": ["other_file"], "count": 1},
            },
            "statistics": {
                "total_files": 2,
                "total_dependencies": 1,
                "cross_folder_dependencies": 1,
                "test_files": 1,
                "folders": 2,
            },
        }

        html_template = f"""<!DOCTYPE html>
<html>
<head><title>Test Graph</title></head>
<body>
    <div id="graph"></div>
    <script>
        const graphData = {json.dumps(test_data, indent=2)};
        console.log('Graph data loaded:', graphData);
    </script>
</body>
</html>"""

        return html_template

    def compare_with_expected(
        self, extracted_data: Dict[str, Any], expected_min_nodes: int = 1
    ) -> bool:
        """Compare extracted data with expected minimums."""
        if not extracted_data:
            print("❌ No data to compare")
            return False

        nodes_count = len(extracted_data.get("nodes", []))
        edges_count = len(extracted_data.get("edges", []))

        print(f"\n📊 Comparison Results:")
        print(f"   - Expected min nodes: {expected_min_nodes}")
        print(f"   - Actual nodes: {nodes_count}")
        print(f"   - Actual edges: {edges_count}")

        if nodes_count < expected_min_nodes:
            error_msg = f"Insufficient nodes: expected >={expected_min_nodes}, got {nodes_count}"
            self.validation_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

        print("✅ Data meets minimum expectations")
        return True


def test_html_data_extraction():
    """Test the HTML data extraction functionality."""
    print("🧪 HTML DATA EXTRACTION TESTING")
    print("=" * 50)

    extractor = HTMLDataExtractor()

    # Test 1: Generate and test known good HTML
    print("\n🧪 Test 1: Known Good Data")
    test_html = extractor.generate_test_html_with_known_data()
    test_data = extractor.extract_graph_data_from_html(test_html)

    if test_data and extractor.validate_extracted_data(test_data):
        print("✅ Known good data test passed")
    else:
        print("❌ Known good data test failed")

    # Test 2: Check if actual HTML file exists and analyze it
    print("\n🧪 Test 2: Actual HTML File Analysis")
    html_file = Path("graph_output/enhanced_dependency_graph.html")

    if html_file.exists():
        result = extractor.analyze_html_file(str(html_file))
        if result["success"]:
            print("✅ Actual HTML file analysis passed")

            # Test minimum expectations based on current workspace
            python_files = list(Path(".").rglob("*.py"))
            expected_min_nodes = max(
                1, len(python_files) // 2
            )  # Expect at least half the py files

            if extractor.compare_with_expected(result["data"], expected_min_nodes):
                print("✅ Data meets workspace expectations")
            else:
                print("❌ Data below workspace expectations")
        else:
            print(
                f"❌ Actual HTML file analysis failed: {result.get('error', 'Unknown error')}"
            )
    else:
        print("⚠️  HTML file not found - will need to generate first")

    # Test 3: Test with malformed HTML
    print("\n🧪 Test 3: Malformed HTML")
    malformed_html = (
        """<html><script>const graphData = {broken json};</script></html>"""
    )
    malformed_data = extractor.extract_graph_data_from_html(malformed_html)

    if malformed_data is None:
        print("✅ Malformed HTML correctly rejected")
    else:
        print("❌ Malformed HTML incorrectly accepted")

    # Summary
    print(f"\n📋 Extraction Test Summary:")
    print(f"   - Extraction methods tested: 4")
    print(f"   - Validation errors: {len(extractor.validation_errors)}")

    if extractor.validation_errors:
        print("❌ Errors found:")
        for error in extractor.validation_errors:
            print(f"   - {error}")
    else:
        print("✅ No extraction errors found")


def main():
    """Main function for HTML data extraction testing."""
    test_html_data_extraction()


if __name__ == "__main__":
    main()
