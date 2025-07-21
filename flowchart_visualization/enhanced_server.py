#!/usr/bin/env python3
"""
Enhanced Flowchart Server

Flask server for the enhanced interactive HTML flowchart with:
- Full-width plot area
- Function details view with all functions as nodes
- Relationship highlighting (blue for dependencies, orange for dependents)
- Enhanced API endpoints
- Improved data processing
"""

from flask import Flask, render_template_string, jsonify, send_from_directory, request
import json
import os
from pathlib import Path
import webbrowser
import threading
import time
import ast
import sys
from collections import defaultdict

app = Flask(__name__)

# Global data storage
codebase_data = None
root_path = Path(__file__).parent.parent  # Go up one level from flowchart_visualization


def analyze_python_file(file_path):
    """Analyze a Python file to extract functions, classes, and their details"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        functions = {}
        classes = {}
        imports = set()
        function_calls = defaultdict(list)

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        # Extract functions and their details
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = calculate_complexity(node)
                func_calls = extract_function_calls(node)

                functions[node.name] = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "complexity": func_complexity,
                    "calls": func_calls,
                    "args": len(node.args.args),
                    "decorators": [
                        d.id if isinstance(d, ast.Name) else str(d)
                        for d in node.decorator_list
                    ],
                }

                function_calls[node.name] = func_calls

            elif isinstance(node, ast.ClassDef):
                class_complexity = sum(
                    calculate_complexity(n)
                    for n in node.body
                    if isinstance(n, ast.FunctionDef)
                )
                class_methods = [
                    n.name for n in node.body if isinstance(n, ast.FunctionDef)
                ]

                classes[node.name] = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "complexity": class_complexity,
                    "methods": class_methods,
                    "method_count": len(class_methods),
                    "bases": [
                        b.id if isinstance(b, ast.Name) else str(b) for b in node.bases
                    ],
                }

        return {
            "functions": functions,
            "classes": classes,
            "imports": list(imports),
            "function_calls": dict(function_calls),
        }

    except Exception as e:
        print(f"Warning: Could not analyze {file_path}: {e}")
        return {"functions": {}, "classes": {}, "imports": [], "function_calls": {}}


def calculate_complexity(node):
    """Calculate cyclomatic complexity for a function"""
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.Lambda):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1

    return complexity


def extract_function_calls(node):
    """Extract function calls from a function node"""
    calls = []

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.append(child.func.attr)

    return calls


def load_enhanced_analysis_data():
    """Load and enhance the codebase analysis data"""
    global codebase_data

    # Try to load existing analysis file
    analysis_file = root_path / "codebase_analysis.json"

    if analysis_file.exists():
        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                codebase_data = json.load(f)
            print(
                f"✅ Loaded existing analysis data: {len(codebase_data.get('files', {}))} files"
            )
        except Exception as e:
            print(f"Error loading analysis file: {e}")
            codebase_data = None

    # If no existing data, create enhanced analysis
    if not codebase_data:
        print("🔍 Creating enhanced analysis data...")
        codebase_data = create_enhanced_analysis()

    # Ensure we have all required fields
    ensure_enhanced_data_structure()


def create_enhanced_analysis():
    """Create enhanced analysis of the codebase"""
    files = {}
    dependencies = defaultdict(list)
    all_functions = {}
    all_classes = {}

    # Find all Python files
    python_files = list(root_path.rglob("*.py"))

    for file_path in python_files:
        if any(
            skip in str(file_path) for skip in [".git", "__pycache__", ".venv", "venv"]
        ):
            continue

        relative_path = str(file_path.relative_to(root_path)).replace("\\", "/")

        # Basic file info
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            total_lines = len(lines)
            code_lines = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ]
            )
            comment_lines = len(
                [line for line in lines if line.strip().startswith("#")]
            )
            blank_lines = len([line for line in lines if not line.strip()])

            # Analyze the file
            analysis = analyze_python_file(file_path)

            # Calculate basic complexity
            base_complexity = max(
                1, len(analysis["functions"]) * 2 + len(analysis["classes"]) * 3
            )
            total_complexity = sum(
                f.get("complexity", 1) for f in analysis["functions"].values()
            )

            files[relative_path] = {
                "name": file_path.name,
                "path": relative_path,
                "type": categorize_file_type(relative_path),
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "complexity": max(base_complexity, total_complexity),
                "functions_count": len(analysis["functions"]),
                "classes_count": len(analysis["classes"]),
                "imports_count": len(analysis["imports"]),
                "functions": list(analysis["functions"].keys()),
                "function_details": analysis["functions"],
                "classes": analysis["classes"],
                "imports": analysis["imports"],
            }

            # Store all functions with file context
            for func_name, func_details in analysis["functions"].items():
                func_id = f"{relative_path}::{func_name}"
                all_functions[func_id] = {
                    **func_details,
                    "file": relative_path,
                    "full_name": func_id,
                }

            # Store all classes
            all_classes[relative_path] = analysis["classes"]

            # Extract dependencies (imports to other project files)
            for imp in analysis["imports"]:
                # Check if import corresponds to a project file
                for other_file in files:
                    if imp in other_file or other_file.replace(".py", "") in imp:
                        dependencies[relative_path].append(other_file)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            # Create minimal entry
            files[relative_path] = {
                "name": file_path.name,
                "path": relative_path,
                "type": categorize_file_type(relative_path),
                "total_lines": 0,
                "complexity": 1,
                "functions_count": 0,
                "classes_count": 0,
                "imports_count": 0,
                "functions": [],
                "function_details": {},
                "classes": {},
                "imports": [],
            }

    return {
        "metadata": {
            "project_name": "Borehole_Plots_Render",
            "total_files": len(files),
            "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_functions": len(all_functions),
            "total_classes": sum(len(classes) for classes in all_classes.values()),
        },
        "files": files,
        "dependencies": dict(dependencies),
        "functions": all_functions,
        "classes": all_classes,
        "function_calls": extract_cross_file_function_calls(files, all_functions),
    }


def categorize_file_type(file_path):
    """Categorize file type based on path and name"""
    file_path_lower = file_path.lower()

    if (
        "test_" in file_path_lower
        or "_test." in file_path_lower
        or "/test/" in file_path_lower
    ):
        return "test"
    elif "config" in file_path_lower or "settings" in file_path_lower:
        return "config"
    elif (
        "util" in file_path_lower
        or "helper" in file_path_lower
        or "common" in file_path_lower
    ):
        return "utility"
    elif (
        file_path_lower.endswith("app.py")
        or file_path_lower.endswith("main.py")
        or file_path_lower.endswith("__init__.py")
    ):
        return "main"
    else:
        return "core"


def extract_cross_file_function_calls(files, all_functions):
    """Extract function calls that cross file boundaries"""
    cross_calls = defaultdict(list)

    for file_path, file_info in files.items():
        if "function_details" in file_info:
            for func_name, func_details in file_info["function_details"].items():
                func_id = f"{file_path}::{func_name}"

                # Check if any calls reference functions in other files
                for call in func_details.get("calls", []):
                    # Look for this function name in other files
                    for other_func_id, other_func in all_functions.items():
                        if (
                            other_func["name"] == call
                            and other_func["file"] != file_path
                        ):
                            cross_calls[func_id].append(other_func_id)

    return dict(cross_calls)


def ensure_enhanced_data_structure():
    """Ensure the data has all required fields for enhanced visualization"""
    global codebase_data

    if not codebase_data:
        return

    # Ensure functions dict exists
    if "functions" not in codebase_data:
        codebase_data["functions"] = {}

    # Ensure each file has function details
    for file_path, file_info in codebase_data.get("files", {}).items():
        if "functions" not in file_info:
            file_info["functions"] = []
        if "function_details" not in file_info:
            file_info["function_details"] = {}
        if "imports" not in file_info:
            file_info["imports"] = []

    # Build functions dict from file data if empty
    if not codebase_data["functions"]:
        for file_path, file_info in codebase_data.get("files", {}).items():
            if "function_details" in file_info:
                for func_name, func_details in file_info["function_details"].items():
                    func_id = f"{file_path}::{func_name}"
                    codebase_data["functions"][func_id] = {
                        **func_details,
                        "file": file_path,
                        "full_name": func_id,
                    }


@app.route("/")
def index():
    """Serve the enhanced flowchart page"""
    try:
        html_file = Path(__file__).parent / "enhanced_flowchart.html"
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return (
            """
        <html>
        <head><title>Enhanced Flowchart Not Found</title></head>
        <body>
            <h1>Enhanced Interactive Flowchart Not Found</h1>
            <p>Please ensure 'enhanced_flowchart.html' exists in the flowchart_visualization directory.</p>
            <p>Run the setup script to generate the required files.</p>
        </body>
        </html>
        """,
            404,
        )


@app.route("/enhanced_flowchart.js")
def js_file():
    """Serve the JavaScript file"""
    try:
        js_file = Path(__file__).parent / "enhanced_flowchart.js"
        with open(js_file, "r", encoding="utf-8") as f:
            js_content = f.read()
        return js_content, 200, {"Content-Type": "application/javascript"}
    except FileNotFoundError:
        return "console.error('Enhanced flowchart JavaScript not found');", 404


@app.route("/api/data")
def get_enhanced_analysis_data():
    """API endpoint to get the enhanced codebase analysis data"""
    if codebase_data is None:
        return jsonify({"error": "No analysis data available"}), 404
    return jsonify(codebase_data)


@app.route("/api/files")
def get_files():
    """API endpoint to get just the files data"""
    if codebase_data is None or "files" not in codebase_data:
        return jsonify({"error": "No files data available"}), 404
    return jsonify(codebase_data["files"])


@app.route("/api/functions")
def get_functions():
    """API endpoint to get function details"""
    if codebase_data is None or "functions" not in codebase_data:
        return jsonify({"error": "No functions data available"}), 404
    return jsonify(codebase_data["functions"])


@app.route("/api/dependencies")
def get_dependencies():
    """API endpoint to get dependency information"""
    if codebase_data is None or "dependencies" not in codebase_data:
        return jsonify({"error": "No dependencies data available"}), 404
    return jsonify(codebase_data["dependencies"])


@app.route("/api/stats")
def get_stats():
    """API endpoint to get project statistics"""
    if codebase_data is None:
        return jsonify({"error": "No data available"}), 404

    files = codebase_data.get("files", {})
    total_lines = sum(f.get("total_lines", 0) for f in files.values())
    total_functions = sum(f.get("functions_count", 0) for f in files.values())
    total_classes = sum(f.get("classes_count", 0) for f in files.values())

    return jsonify(
        {
            "total_files": len(files),
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "avg_complexity": (
                sum(f.get("complexity", 0) for f in files.values()) / len(files)
                if files
                else 0
            ),
        }
    )


@app.route("/api/refresh")
def refresh_data():
    """API endpoint to refresh the analysis data"""
    try:
        load_enhanced_analysis_data()
        return jsonify({"status": "success", "message": "Data refreshed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def start_server(port=5000, debug=False, open_browser=True):
    """Start the enhanced flowchart server"""

    # Load the enhanced analysis data
    print("🔍 Loading enhanced analysis data...")
    load_enhanced_analysis_data()

    if open_browser:
        # Open browser after a short delay
        def open_browser_delayed():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    print(f"🚀 Starting Enhanced Flowchart Server on http://localhost:{port}")
    print("📊 Features:")
    print("  - Full-width plot area")
    print("  - Function details view with all functions as nodes")
    print("  - Relationship highlighting (blue=dependencies, orange=dependents)")
    print("  - Enhanced interactivity and responsiveness")
    print("  - Real-time search and filtering")
    print("\n💡 Press Ctrl+C to stop the server")

    try:
        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Interactive Flowchart Server"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

    args = parser.parse_args()

    start_server(port=args.port, debug=args.debug, open_browser=not args.no_browser)
