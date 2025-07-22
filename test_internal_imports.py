"""
Test script to verify internal import counting specifically
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


def extract_internal_imports_from_file(
    file_path: Path, known_files: Set[str]
) -> List[str]:
    """Extract only internal imports that resolve to files in the workspace."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        internal_imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_name = alias.name
                    # Check if this import resolves to a known file
                    if resolve_import_to_known_file(
                        import_name, file_path, known_files
                    ):
                        internal_imports.append(import_name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_name = node.module
                    # Check if this import resolves to a known file
                    if resolve_import_to_known_file(
                        import_name, file_path, known_files
                    ):
                        internal_imports.append(import_name)

        return list(set(internal_imports))  # Remove duplicates
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def resolve_import_to_known_file(
    import_name: str, current_file: Path, known_files: Set[str]
) -> bool:
    """Check if an import name resolves to a known file in the workspace."""

    # Handle relative imports
    if import_name.startswith("."):
        # Get the module name after the dots
        module_name = import_name.lstrip(".")
        if not module_name:
            return False

        # For relative imports, look in the current directory or parent
        current_folder = current_file.parent

        if import_name.startswith(".."):
            # Parent directory import
            target_folder = current_folder.parent
        else:
            # Current directory import
            target_folder = current_folder

        potential_file = target_folder / f"{module_name}.py"
        return str(potential_file) in known_files

    # Handle absolute imports - check all known files
    parts = import_name.split(".")
    module_name = parts[0]

    # Check if any known file matches this module name
    for known_file in known_files:
        file_path = Path(known_file)
        if file_path.stem == module_name:
            return True

    return False


def scan_workspace_for_internal_imports():
    """Scan workspace and count only internal imports."""
    root = Path(".")

    # First, find all Python files
    python_files = []
    for file_path in root.rglob("*.py"):
        if "__pycache__" in file_path.parts or file_path.name.startswith("."):
            continue
        python_files.append(file_path)

    # Create set of known file paths
    known_files = {str(f) for f in python_files}

    print(f"🔍 Found {len(python_files)} Python files in workspace")
    print("📁 Sample files:")
    for f in list(python_files)[:5]:
        print(f"   {f}")

    # Analyze each file for internal imports
    results = {}
    for file_path in python_files:
        internal_imports = extract_internal_imports_from_file(file_path, known_files)
        results[str(file_path)] = {
            "path": str(file_path),
            "stem": file_path.stem,
            "folder": file_path.parent.name if file_path.parent.name != "." else "root",
            "internal_imports": internal_imports,
            "internal_import_count": len(internal_imports),
        }

    return results


def test_specific_files():
    """Test specific files that showed discrepancies."""
    print("\n=== TESTING SPECIFIC FILES ===")

    # Get workspace data
    results = scan_workspace_for_internal_imports()

    # Test key files
    test_files = ["app.py", "callbacks_split.py", "config.py"]

    for test_file in test_files:
        found = False
        for file_path, data in results.items():
            if file_path.endswith(test_file):
                print(f"\n📄 {test_file}:")
                print(f"   Path: {file_path}")
                print(f"   Internal imports: {data['internal_import_count']}")
                print(f"   Import list: {data['internal_imports']}")
                found = True
                break

        if not found:
            print(f"\n❌ {test_file} not found!")

    # Compare with graph data
    try:
        with open("graph_output/enhanced_graph_data.json", "r") as f:
            graph_data = json.load(f)

        print(f"\n=== COMPARISON WITH GRAPH DATA ===")

        # Create mapping
        graph_nodes_by_path = {}
        for node in graph_data.get("nodes", []):
            if "file_path" in node:
                graph_nodes_by_path[node["file_path"]] = node

        discrepancies = []
        for file_path, data in results.items():
            if file_path in graph_nodes_by_path:
                graph_node = graph_nodes_by_path[file_path]
                actual_internal = data["internal_import_count"]
                graph_internal = graph_node.get("imports_count", 0)

                if actual_internal != graph_internal:
                    discrepancies.append(
                        {
                            "file": file_path,
                            "actual_internal": actual_internal,
                            "graph_internal": graph_internal,
                            "difference": actual_internal - graph_internal,
                            "actual_imports": data["internal_imports"],
                        }
                    )

        if discrepancies:
            print(
                f"\nFound {len(discrepancies)} files with internal import discrepancies:"
            )
            for disc in sorted(
                discrepancies, key=lambda x: abs(x["difference"]), reverse=True
            )[:10]:
                print(f"\n📁 {disc['file']}")
                print(f"   Actual internal: {disc['actual_internal']}")
                print(f"   Graph internal:  {disc['graph_internal']}")
                print(f"   Difference:      {disc['difference']}")
                print(f"   Internal list:   {disc['actual_imports']}")
        else:
            print("✅ All internal import counts match!")

    except Exception as e:
        print(f"Error loading graph data: {e}")


if __name__ == "__main__":
    test_specific_files()
