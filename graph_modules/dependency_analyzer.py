"""
Enhanced Dependency Analyzer
============================

Core dependency analysis functionality for Python projects.
Analyzes import relationships, calculates importance scores, and builds graph data.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class EnhancedDependencyAnalyzer:
    """Enhanced dependency analyzer with complete directory inclusion."""

    def __init__(self, exclude_folders: List[str] = None):
        # Remove test exclusion - include all directories
        self.exclude_folders = exclude_folders or ["__pycache__"]
        self.dependencies = {}
        self.node_importance = {}

    def analyze_project(self, root_path: str = ".") -> Dict[str, Any]:
        """Analyze entire project including previously excluded directories."""
        print("🔍 Enhanced dependency analysis - including ALL directories...")

        # Scan for all Python files
        python_files = self._find_python_files(root_path)
        print(f"📁 Found {len(python_files)} Python files across all directories")

        # First pass: Build file registry without dependencies
        self._build_file_registry(python_files)

        # Second pass: Analyze dependencies now that registry is complete
        self._analyze_dependencies(python_files)

        # Calculate node importance (PageRank-style)
        self._calculate_node_importance()

        # Build enhanced graph data
        graph_data = self._build_enhanced_graph_data()

        return graph_data

    def _find_python_files(self, root_path: str) -> List[Path]:
        """Find all Python files, including in previously excluded directories."""
        python_files = []
        root = Path(root_path)

        for file_path in root.rglob("*.py"):
            # Only exclude __pycache__ and hidden directories
            if any(excluded in file_path.parts for excluded in self.exclude_folders):
                continue

            if file_path.name.startswith("."):
                continue

            python_files.append(file_path)

        return python_files

    def _build_file_registry(self, python_files: List[Path]) -> None:
        """Build initial file registry without dependencies (first pass)."""
        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Create unique identifier
                unique_id = self._create_unique_id(file_path)

                self.dependencies[unique_id] = {
                    "file_path": str(file_path),
                    "folder": self._get_folder_name(file_path),
                    "stem": file_path.stem,
                    "display_name": self._create_display_name(file_path),
                    "imports": [],  # Will be filled in second pass
                    "all_imports": [],  # Will be filled in second pass
                    "imports_count": 0,  # Will be filled in second pass
                    "internal_imports_count": 0,  # Will be filled in second pass
                    "is_test": self._is_test_file(file_path),
                    "is_init": file_path.name == "__init__.py",
                    "size": len(content),
                }

            except Exception as e:
                print(f"Error registering {file_path}: {e}")

    def _analyze_dependencies(self, python_files: List[Path]) -> None:
        """Analyze dependencies with enhanced import detection (second pass)."""
        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST for accurate import analysis
                tree = ast.parse(content, filename=str(file_path))
                internal_imports, all_imports = self._extract_imports(tree, file_path)

                # Update existing entry with dependency information
                unique_id = self._create_unique_id(file_path)
                if unique_id in self.dependencies:
                    self.dependencies[unique_id].update(
                        {
                            "imports": internal_imports,
                            "all_imports": all_imports,
                            "imports_count": len(all_imports),
                            "internal_imports_count": len(internal_imports),
                        }
                    )

            except Exception as e:
                print(f"Error analyzing dependencies for {file_path}: {e}")

    def _extract_imports(
        self, tree: ast.AST, file_path: Path
    ) -> Tuple[List[str], List[str]]:
        """Enhanced import extraction with better resolution."""
        internal_imports = []
        all_imports = []
        current_folder = self._get_folder_name(file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    all_imports.append(alias.name)
                    resolved = self._resolve_import_to_file(alias.name, current_folder)
                    if resolved:
                        internal_imports.append(resolved)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module
                    all_imports.append(module_name)

                    # Handle relative imports
                    if module_name.startswith("."):
                        # Relative import - resolve based on current location
                        resolved = self._resolve_relative_import(module_name, file_path)
                        if resolved:
                            internal_imports.append(resolved)
                    else:
                        # Absolute import
                        resolved = self._resolve_import_to_file(
                            module_name, current_folder
                        )
                        if resolved:
                            internal_imports.append(resolved)

        return internal_imports, all_imports

    def _resolve_relative_import(self, import_name: str, current_file: Path) -> str:
        """Resolve relative imports to actual file IDs."""
        # Count dots to determine level
        level = 0
        while level < len(import_name) and import_name[level] == ".":
            level += 1

        if level == 0:
            return None

        # Get the module name after dots
        module_name = import_name[level:] if level < len(import_name) else ""

        # Navigate up the directory tree
        target_dir = current_file.parent
        for _ in range(level - 1):
            target_dir = target_dir.parent

        # If module_name is empty, looking for __init__.py in target_dir
        if not module_name:
            target_file = target_dir / "__init__.py"
        else:
            # Replace dots with path separators
            module_path = module_name.replace(".", os.sep)
            target_file = target_dir / f"{module_path}.py"

            # Also check for __init__.py in directory
            if not target_file.exists():
                target_file = target_dir / module_path / "__init__.py"

        if target_file.exists():
            return self._create_unique_id(target_file)

        return None

    def _resolve_import_to_file(self, import_name: str, current_folder: str) -> str:
        """Enhanced import resolution to map imports to actual files."""
        # Check if this import corresponds to any known file
        import_parts = import_name.split(".")

        # Try different combinations to find the actual file
        for unique_id, info in self.dependencies.items():
            # Direct stem match
            if info["stem"] == import_parts[0]:
                return unique_id

            # Try matching with folder structure
            if len(import_parts) > 1:
                if (
                    info["folder"] == import_parts[0]
                    and info["stem"] == import_parts[1]
                ):
                    return unique_id

            # Try matching full module path
            file_path = Path(info["file_path"])
            try:
                # Convert file path to module notation
                relative_path = file_path.relative_to(Path("."))
                if relative_path.stem == "__init__":
                    module_path = ".".join(relative_path.parent.parts)
                else:
                    module_path = ".".join(relative_path.with_suffix("").parts)

                if module_path == import_name:
                    return unique_id
            except ValueError:
                pass

        return None

    def _create_unique_id(self, file_path: Path) -> str:
        """Create a unique identifier for a file."""
        try:
            relative_path = file_path.relative_to(Path("."))
            return str(relative_path).replace("\\", "/")
        except ValueError:
            return str(file_path).replace("\\", "/")

    def _get_folder_name(self, file_path: Path) -> str:
        """Enhanced folder name detection."""
        try:
            relative_path = file_path.relative_to(Path("."))
            if len(relative_path.parts) > 1:
                return relative_path.parts[0]
            else:
                return "root"
        except ValueError:
            return "external"

    def _create_display_name(self, file_path: Path) -> str:
        """Create a human-readable display name."""
        stem = file_path.stem
        folder = self._get_folder_name(file_path)

        if folder == "root":
            return stem
        else:
            return f"{folder}/{stem}"

    def _is_test_file(self, file_path: Path) -> bool:
        """Enhanced test file detection."""
        stem = file_path.stem.lower()
        folder = self._get_folder_name(file_path).lower()

        # Check file name patterns
        test_patterns = [
            stem.startswith("test_"),
            stem.endswith("_test"),
            stem == "test",
            "test" in folder,
            folder.startswith("test"),
        ]

        return any(test_patterns)

    def _calculate_node_importance(self) -> None:
        """Calculate node importance using PageRank-style algorithm."""
        print("📈 Calculating node importance scores...")

        # Build adjacency matrix
        nodes = list(self.dependencies.keys())
        n = len(nodes)
        node_to_index = {node: i for i, node in enumerate(nodes)}

        # Initialize importance scores
        importance = {node: 1.0 / n for node in nodes}

        # PageRank iterations
        damping = 0.85
        for iteration in range(50):  # 50 iterations should be sufficient
            new_importance = {}

            for node in nodes:
                # Base importance (random walk probability)
                new_importance[node] = (1 - damping) / n

                # Add importance from incoming links
                for other_node, info in self.dependencies.items():
                    if node in info["imports"]:
                        outgoing_count = len(info["imports"])
                        if outgoing_count > 0:
                            new_importance[node] += (
                                damping * importance[other_node] / outgoing_count
                            )

            # Check for convergence
            max_diff = max(
                abs(new_importance[node] - importance[node]) for node in nodes
            )
            importance = new_importance

            if max_diff < 1e-6:
                print(f"   Converged after {iteration + 1} iterations")
                break

        # Normalize to 0-1 range
        max_importance = max(importance.values()) if importance.values() else 1
        self.node_importance = {
            node: score / max_importance for node, score in importance.items()
        }

    def _build_enhanced_graph_data(self) -> Dict[str, Any]:
        """Build enhanced graph data with importance and visual properties."""
        print("🎨 Building enhanced graph visualization data...")

        # Generate distinct colors for folders
        folders = set(info["folder"] for info in self.dependencies.values())
        folder_colors = self._generate_folder_colors(folders)

        nodes = []
        edges = []
        node_index = {}

        # Create nodes with enhanced properties
        for i, (unique_id, info) in enumerate(self.dependencies.items()):
            importance = self.node_importance.get(unique_id, 0)

            nodes.append(
                {
                    "id": unique_id,
                    "name": info["display_name"],
                    "stem": info["stem"],
                    "folder": info["folder"],
                    "color": folder_colors.get(info["folder"], "#F0F0F0"),
                    "file_path": info["file_path"],
                    "imports_count": info[
                        "internal_imports_count"
                    ],  # Use internal imports count
                    "importance": importance,
                    "is_test": info["is_test"],
                    "is_init": info["is_init"],
                    "size": info["size"],
                    "index": i,
                }
            )
            node_index[unique_id] = i

        # Create edges with enhanced properties
        for unique_id, info in self.dependencies.items():
            source_index = node_index[unique_id]
            source_folder = info["folder"]

            for imported_id in info["imports"]:
                if imported_id in node_index:
                    target_index = node_index[imported_id]
                    target_info = self.dependencies[imported_id]
                    target_folder = target_info["folder"]

                    edges.append(
                        {
                            "source": source_index,
                            "target": target_index,
                            "source_name": unique_id,
                            "target_name": imported_id,
                            "source_folder": source_folder,
                            "target_folder": target_folder,
                            "is_cross_folder": source_folder != target_folder,
                            "is_test_related": info["is_test"]
                            or target_info["is_test"],
                        }
                    )

        # Build subfolder info
        subfolder_info = {}
        for folder, color in folder_colors.items():
            folder_modules = [n for n in nodes if n["folder"] == folder]
            subfolder_info[folder] = {
                "color": color,
                "modules": [n["name"] for n in folder_modules],
                "test_modules": [n["name"] for n in folder_modules if n["is_test"]],
                "count": len(folder_modules),
            }

        return {
            "nodes": nodes,
            "edges": edges,
            "dependencies": self.dependencies,
            "subfolder_info": subfolder_info,
            "importance_scores": self.node_importance,
            "statistics": {
                "total_files": len(nodes),
                "total_dependencies": len(edges),
                "cross_folder_dependencies": sum(
                    1 for e in edges if e["is_cross_folder"]
                ),
                "test_files": sum(1 for n in nodes if n["is_test"]),
                "folders": len(subfolder_info),
            },
        }

    def _generate_folder_colors(self, folders: Set[str]) -> Dict[str, str]:
        """Generate visually distinct colors for folders."""
        # Predefined color palette for consistent visualization
        color_palette = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FFEAA7",
            "#DDA0DD",
            "#FFB347",
            "#87CEEB",
            "#DEB887",
            "#F0E68C",
            "#FFA07A",
            "#20B2AA",
            "#87CEFA",
            "#778899",
            "#B0C4DE",
            "#FFFFE0",
            "#00CED1",
            "#FF7F50",
            "#6495ED",
            "#DC143C",
        ]

        folder_list = sorted(folders)
        folder_colors = {}

        for i, folder in enumerate(folder_list):
            folder_colors[folder] = color_palette[i % len(color_palette)]

        return folder_colors
