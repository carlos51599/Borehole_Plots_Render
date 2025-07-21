import os
import subprocess
import glob
import sys
import ast
from pathlib import Path


def extract_imports(file_path):
    """Extract imports from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])

        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def create_dependency_graph(py_files, dot_file):
    """Create a DOT file showing dependencies between Python files."""
    dependencies = {}
    local_modules = set()

    # Get base names of local modules (without .py extension)
    for file_path in py_files:
        module_name = Path(file_path).stem
        local_modules.add(module_name)

    # Extract dependencies for each file
    for file_path in py_files:
        module_name = Path(file_path).stem
        imports = extract_imports(file_path)

        # Filter to only local dependencies
        local_imports = [imp for imp in imports if imp in local_modules]
        dependencies[module_name] = local_imports

    # Generate DOT file
    with open(dot_file, "w") as f:
        f.write("digraph Dependencies {\n")
        f.write("    rankdir=LR;\n")
        f.write("    node [shape=box, style=filled, fillcolor=lightblue];\n")

        # Add all nodes
        for module in local_modules:
            f.write(f'    "{module}";\n')

        # Add edges
        for module, imports in dependencies.items():
            for imported in imports:
                if imported != module:  # Avoid self-loops
                    f.write(f'    "{module}" -> "{imported}";\n')

        f.write("}\n")


def main():
    output_dir = "graph_output"
    dot_file = os.path.join(output_dir, "graph.dot")
    svg_file = os.path.join(output_dir, "graph.svg")

    # Step 1: Recursively find all .py files in current directory and subfolders, excluding 'tests' subfolder
    py_files = [
        str(p)
        for p in Path(".").rglob("*.py")
        if p.is_file() and "tests" not in p.parts
    ]
    if not py_files:
        print(
            "No .py files found in the current directory or subfolders (excluding 'tests')."
        )
        return

    # Step 5: Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Step 2: Create dependency graph using custom parser
    try:
        create_dependency_graph(py_files, dot_file)
        print(f"Dependency graph created: {dot_file}")
    except Exception as e:
        print(f"Failed to create dependency graph: {e}")
        return

    # Step 4: Run dot to generate SVG
    try:
        dot_cmd = ["dot", "-Tsvg", dot_file, "-o", svg_file]
        subprocess.run(dot_cmd, check=True)
        print(f"Graph generated successfully: {svg_file}")

        # Step 5: Inject interactivity into SVG
        inject_interactivity(svg_file)
        print("SVG interactivity injected.")
    except FileNotFoundError:
        print("Graphviz 'dot' command not found. Please install Graphviz.")
        print("You can download it from: https://graphviz.org/download/")
        print(f"DOT file created at: {dot_file}")
    except Exception as e:
        print(f"Failed to run dot: {e}")
        print(f"DOT file created at: {dot_file}")


def inject_interactivity(svg_file):
    """Injects JavaScript and CSS into the SVG for interactive node highlighting."""
    try:
        with open(svg_file, "r", encoding="utf-8") as f:
            svg = f.read()

        # Insert CSS for dimming/highlighting
        style = """<style type="text/css">
            .dimmed { opacity: 0.2; }
            .highlighted { opacity: 1.0; stroke: #ff6600 !important; }
        </style>"""

        script = """<script type=\"text/ecmascript\"><![CDATA[
                function resetAll() {
                    var nodes = document.querySelectorAll('g.node');
                    var edges = document.querySelectorAll('g.edge');
                    nodes.forEach(function(n) { n.classList.remove('dimmed','highlighted'); });
                    edges.forEach(function(e) { e.classList.remove('dimmed','highlighted'); });
                }
                function getNodeTitle(node) {
                    var title = node.querySelector('title');
                    return title ? title.textContent.trim() : (node.getAttribute('data-title') || node.id || '');
                }
                function highlightConnections(nodeId) {
                    resetAll();
                    var nodes = document.querySelectorAll('g.node');
                    var edges = document.querySelectorAll('g.edge');
                    var connected = new Set();
                    // Highlight edges and collect connected nodes
                    edges.forEach(function(e) {
                        var title = e.querySelector('title');
                        if (title) {
                            var txt = title.textContent;
                            var parts = txt.split('->').map(function(s){return s.trim();});
                            if (parts.length === 2 && (parts[0] === nodeId || parts[1] === nodeId)) {
                                e.classList.add('highlighted');
                                connected.add(parts[0]);
                                connected.add(parts[1]);
                            } else {
                                e.classList.add('dimmed');
                            }
                        } else {
                            e.classList.add('dimmed');
                        }
                    });
                    // Highlight connected nodes by <title> content
                    nodes.forEach(function(n) {
                        var ntitle = getNodeTitle(n);
                        if (connected.has(ntitle)) {
                            n.classList.add('highlighted');
                        } else {
                            n.classList.add('dimmed');
                        }
                    });
                }
                window.addEventListener('DOMContentLoaded', function() {
                    var nodes = document.querySelectorAll('g.node');
                    nodes.forEach(function(n) {
                        var ntitle = getNodeTitle(n);
                        n.style.cursor = 'pointer';
                        n.addEventListener('click', function() { highlightConnections(ntitle); });
                    });
                    document.documentElement.addEventListener('click', function(e) {
                        if (e.target.closest('g.node') == null) resetAll();
                    });
                });
            ]]></script>"""

        # Insert style and script immediately after opening <svg ...> tag
        import re

        svg_open_tag = re.search(r"<svg[^>]*>", svg)
        if svg_open_tag:
            insert_index = svg_open_tag.end()
            svg = svg[:insert_index] + style + script + svg[insert_index:]
        else:
            print("Could not find <svg> tag for injection.")

        # Add IDs to nodes for easier selection
        import re

        def add_node_ids(match):
            label = re.search(r"<title>(.*?)</title>", match.group(0))
            if label:
                node_id = label.group(1)
                return match.group(0).replace("<g ", f'<g id="{node_id}" ')
            return match.group(0)

        svg = re.sub(r'<g class="node"[\s\S]*?</g>', add_node_ids, svg)

        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg)
    except Exception as e:
        print(f"Failed to inject interactivity: {e}")


if __name__ == "__main__":
    main()
