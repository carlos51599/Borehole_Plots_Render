#!/usr/bin/env python3
"""
Interactive Flowchart Server

Flask server to serve the interactive HTML flowchart with enhanced features:
- Live code preview
- Real-time search and filtering
- Export capabilities
- RESTful API for data access
"""

from flask import Flask, render_template_string, jsonify, send_from_directory, request
import json
import os
from pathlib import Path
import webbrowser
import threading
import time

app = Flask(__name__)

# Global data storage
codebase_data = None
root_path = Path(__file__).parent


def load_analysis_data():
    """Load the codebase analysis data"""
    global codebase_data
    analysis_file = root_path / "codebase_analysis.json"

    if analysis_file.exists():
        with open(analysis_file, "r", encoding="utf-8") as f:
            codebase_data = json.load(f)
        print(f"✅ Loaded analysis data: {len(codebase_data.get('files', {}))} files")
    else:
        print("⚠️ Analysis data not found, generating sample data...")
        # Create minimal sample data
        codebase_data = {
            "metadata": {
                "project_name": "Borehole_Plots_Render",
                "total_files": 5,
                "analysis_timestamp": "2025-01-21T00:00:00",
            },
            "files": {
                "app.py": {
                    "name": "app.py",
                    "type": "main",
                    "complexity": 45,
                    "total_lines": 555,
                    "functions_count": 0,
                    "classes_count": 0,
                },
                "config.py": {
                    "name": "config.py",
                    "type": "config",
                    "complexity": 25,
                    "total_lines": 755,
                    "functions_count": 0,
                    "classes_count": 0,
                },
            },
            "dependencies": {"app.py": ["config.py"]},
            "functions": {},
            "classes": {},
            "imports": {},
        }


@app.route("/")
def index():
    """Serve the main flowchart page"""
    try:
        with open(root_path / "interactive_flowchart.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return (
            """
        <html>
        <head><title>Flowchart Not Found</title></head>
        <body>
            <h1>Interactive Flowchart Not Found</h1>
            <p>Please ensure 'interactive_flowchart.html' exists in the project directory.</p>
            <p>Run the setup script to generate the required files.</p>
        </body>
        </html>
        """,
            404,
        )


@app.route("/api/data")
def get_analysis_data():
    """API endpoint to get the codebase analysis data"""
    if codebase_data is None:
        return jsonify({"error": "No analysis data available"}), 404
    return jsonify(codebase_data)


@app.route("/api/files")
def get_files():
    """API endpoint to get file list with optional filtering"""
    if not codebase_data:
        return jsonify([])

    files = codebase_data.get("files", {})
    file_type = request.args.get("type")
    search = request.args.get("search", "").lower()

    # Filter by type
    if file_type and file_type != "all":
        files = {k: v for k, v in files.items() if v.get("type") == file_type}

    # Filter by search term
    if search:
        files = {
            k: v
            for k, v in files.items()
            if search in k.lower() or search in v.get("name", "").lower()
        }

    return jsonify(files)


@app.route("/api/file/<path:filepath>")
def get_file_details(filepath):
    """API endpoint to get detailed information about a specific file"""
    if not codebase_data:
        return jsonify({"error": "No data available"}), 404

    files = codebase_data.get("files", {})
    if filepath not in files:
        return jsonify({"error": "File not found"}), 404

    file_info = files[filepath].copy()
    file_info["functions"] = codebase_data.get("functions", {}).get(filepath, [])
    file_info["classes"] = codebase_data.get("classes", {}).get(filepath, [])
    file_info["imports"] = codebase_data.get("imports", {}).get(filepath, [])
    file_info["dependencies"] = codebase_data.get("dependencies", {}).get(filepath, [])

    return jsonify(file_info)


@app.route("/api/code/<path:filepath>")
def get_file_code(filepath):
    """API endpoint to get the actual code content of a file"""
    file_path = root_path / filepath

    if not file_path.exists() or not file_path.is_file():
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return jsonify(
            {
                "filepath": filepath,
                "content": content,
                "lines": len(content.splitlines()),
            }
        )
    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 500


@app.route("/api/dependencies/<path:filepath>")
def get_dependencies(filepath):
    """API endpoint to get dependency information for a file"""
    if not codebase_data:
        return jsonify({"error": "No data available"}), 404

    dependencies = codebase_data.get("dependencies", {})
    file_deps = dependencies.get(filepath, [])

    # Find files that depend on this file (reverse dependencies)
    reverse_deps = []
    for file, deps in dependencies.items():
        if filepath in deps:
            reverse_deps.append(file)

    return jsonify(
        {"file": filepath, "dependencies": file_deps, "dependents": reverse_deps}
    )


@app.route("/api/stats")
def get_project_stats():
    """API endpoint to get project statistics"""
    if not codebase_data:
        return jsonify({"error": "No data available"}), 404

    files = codebase_data.get("files", {})

    stats = {
        "total_files": len(files),
        "total_lines": sum(f.get("total_lines", 0) for f in files.values()),
        "total_complexity": sum(f.get("complexity", 0) for f in files.values()),
        "file_types": {},
        "top_complex_files": [],
        "most_connected_files": [],
    }

    # File type distribution
    for file_info in files.values():
        file_type = file_info.get("type", "unknown")
        stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1

    # Top complex files
    complex_files = sorted(
        files.items(), key=lambda x: x[1].get("complexity", 0), reverse=True
    )
    stats["top_complex_files"] = [
        {"file": f[0], "complexity": f[1].get("complexity", 0)}
        for f in complex_files[:10]
    ]

    # Most connected files
    dependencies = codebase_data.get("dependencies", {})
    connected_files = sorted(
        dependencies.items(), key=lambda x: len(x[1]), reverse=True
    )
    stats["most_connected_files"] = [
        {"file": f[0], "connections": len(f[1])} for f in connected_files[:10]
    ]

    return jsonify(stats)


@app.route("/codebase_flowchart.js")
def serve_js():
    """Serve the JavaScript file"""
    try:
        with open(root_path / "codebase_flowchart.js", "r", encoding="utf-8") as f:
            content = f.read()

        from flask import Response

        return Response(content, mimetype="application/javascript")
    except FileNotFoundError:
        return "// JavaScript file not found", 404


@app.route("/codebase_analysis.json")
def serve_analysis():
    """Serve the analysis JSON file"""
    return send_from_directory(root_path, "codebase_analysis.json")


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")


def main():
    """Main function to run the server"""
    print("🚀 Starting Interactive Flowchart Server...")

    # Load analysis data
    load_analysis_data()

    print("\n" + "=" * 60)
    print("    INTERACTIVE CODEBASE FLOWCHART SERVER")
    print("=" * 60)
    print(
        f"📊 Project: {codebase_data.get('metadata', {}).get('project_name', 'Unknown')}"
    )
    print(f"📁 Files analyzed: {len(codebase_data.get('files', {}))}")
    print(f"🌐 Server URL: http://127.0.0.1:5000")
    print("=" * 60)
    print("\n🔗 Available endpoints:")
    print("   • /                    - Interactive flowchart")
    print("   • /api/data           - Complete analysis data")
    print("   • /api/files          - File list (with filtering)")
    print("   • /api/file/<path>    - Detailed file information")
    print("   • /api/code/<path>    - File source code")
    print("   • /api/dependencies/<path> - File dependencies")
    print("   • /api/stats          - Project statistics")
    print("\n💡 Features:")
    print("   • Interactive node-link diagram")
    print("   • Real-time search and filtering")
    print("   • Hover tooltips with file details")
    print("   • Dependency highlighting")
    print("   • Multiple layout algorithms")
    print("   • Dark/light theme toggle")
    print("   • Export capabilities")
    print("\n🎯 Usage:")
    print("   • Click nodes to explore dependencies")
    print("   • Use search to find specific files")
    print("   • Filter by file type using dropdown")
    print("   • Zoom and pan to navigate large codebases")
    print("\n📝 Press Ctrl+C to stop the server")
    print("-" * 60)

    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Run Flask app
    try:
        app.run(host="127.0.0.1", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")


if __name__ == "__main__":
    main()
