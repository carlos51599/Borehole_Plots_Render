"""
Comprehensive workspace audit to identify import/dependency discrepancies
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


def extract_imports_from_file(file_path: Path) -> List[str]:
    """Extract all import statements from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def scan_workspace_files() -> Dict[str, Any]:
    """Scan all Python files in the workspace."""
    workspace_files = {}
    root = Path(".")

    # Find all Python files
    for file_path in root.rglob("*.py"):
        if "__pycache__" in file_path.parts or file_path.name.startswith("."):
            continue

        imports = extract_imports_from_file(file_path)

        workspace_files[str(file_path)] = {
            "path": str(file_path),
            "stem": file_path.stem,
            "folder": file_path.parent.name if file_path.parent.name != "." else "root",
            "imports": imports,
            "import_count": len(imports),
        }

    return workspace_files


def compare_with_graph_data(workspace_files: Dict[str, Any], graph_data_path: str):
    """Compare workspace scan with graph data."""
    try:
        with open(graph_data_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
    except Exception as e:
        print(f"Error loading graph data: {e}")
        return

    print("=== WORKSPACE AUDIT REPORT ===")
    print(f"Found {len(workspace_files)} Python files in workspace")
    print(f"Found {len(graph_data.get('nodes', []))} nodes in graph data")

    # Create mapping of file paths to graph nodes
    graph_nodes_by_path = {}
    for node in graph_data.get("nodes", []):
        if "file_path" in node:
            graph_nodes_by_path[node["file_path"]] = node

    print("\n=== IMPORT COUNT DISCREPANCIES ===")
    discrepancies = []

    for file_path, file_info in workspace_files.items():
        if file_path in graph_nodes_by_path:
            graph_node = graph_nodes_by_path[file_path]
            actual_imports = file_info["import_count"]
            graph_imports = graph_node.get("imports_count", 0)

            if actual_imports != graph_imports:
                discrepancies.append(
                    {
                        "file": file_path,
                        "actual_imports": actual_imports,
                        "graph_imports": graph_imports,
                        "difference": actual_imports - graph_imports,
                        "actual_import_list": file_info["imports"],
                    }
                )

    if discrepancies:
        print(f"Found {len(discrepancies)} files with import count discrepancies:")
        for disc in sorted(
            discrepancies, key=lambda x: abs(x["difference"]), reverse=True
        ):
            print(f"\n📁 {disc['file']}")
            print(f"   Actual imports: {disc['actual_imports']}")
            print(f"   Graph imports:  {disc['graph_imports']}")
            print(f"   Difference:     {disc['difference']}")
            print(f"   Import list:    {disc['actual_import_list']}")
    else:
        print("✅ No import count discrepancies found!")

    print("\n=== MISSING FILES ===")
    missing_in_graph = []
    for file_path in workspace_files:
        if file_path not in graph_nodes_by_path:
            missing_in_graph.append(file_path)

    if missing_in_graph:
        print(f"Found {len(missing_in_graph)} files missing from graph:")
        for file_path in missing_in_graph:
            print(f"   📄 {file_path}")
    else:
        print("✅ All workspace files are in the graph!")

    print("\n=== EXTRA FILES IN GRAPH ===")
    extra_in_graph = []
    for file_path in graph_nodes_by_path:
        if file_path not in workspace_files:
            extra_in_graph.append(file_path)

    if extra_in_graph:
        print(f"Found {len(extra_in_graph)} extra files in graph:")
        for file_path in extra_in_graph:
            print(f"   📄 {file_path}")
    else:
        print("✅ No extra files in graph!")

    return discrepancies, missing_in_graph, extra_in_graph


def main():
    print("🔍 Starting comprehensive workspace audit...")

    # Scan workspace
    workspace_files = scan_workspace_files()

    # Compare with graph data
    graph_data_path = "graph_output/enhanced_graph_data.json"
    discrepancies, missing, extra = compare_with_graph_data(
        workspace_files, graph_data_path
    )

    print(f"\n=== SUMMARY ===")
    print(f"Total Python files: {len(workspace_files)}")
    print(f"Import discrepancies: {len(discrepancies) if discrepancies else 0}")
    print(f"Missing from graph: {len(missing) if missing else 0}")
    print(f"Extra in graph: {len(extra) if extra else 0}")

    # Focus on key files
    print(f"\n=== KEY FILE ANALYSIS ===")
    key_files = ["app.py", "config.py", "callbacks_split.py"]
    for key_file in key_files:
        for file_path, file_info in workspace_files.items():
            if file_path.endswith(key_file):
                print(f"\n📄 {key_file}:")
                print(f"   Path: {file_path}")
                print(f"   Imports: {file_info['import_count']}")
                print(f"   Import list: {file_info['imports']}")
                break


if __name__ == "__main__":
    main()
