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

    # Step 1: Find all .py files in current directory only
    py_files = glob.glob("*.py")
    if not py_files:
        print("No .py files found in the current directory.")
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
    except FileNotFoundError:
        print("Graphviz 'dot' command not found. Please install Graphviz.")
        print("You can download it from: https://graphviz.org/download/")
        print(f"DOT file created at: {dot_file}")
    except Exception as e:
        print(f"Failed to run dot: {e}")
        print(f"DOT file created at: {dot_file}")


if __name__ == "__main__":
    main()
