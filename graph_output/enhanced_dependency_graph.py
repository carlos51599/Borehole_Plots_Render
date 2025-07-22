"""
Phase 4: Implementation - Enhanced Dependency Graph with Optimized Layout
Implementing custom dependency-aware positioning and cubic Bézier curves
"""

import json
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
                            "imports": internal_imports,  # Only internal project imports for edges
                            "all_imports": all_imports,  # All imports including external
                            "imports_count": len(
                                all_imports
                            ),  # Total import count for display
                            "internal_imports_count": len(
                                internal_imports
                            ),  # Internal dependencies count
                        }
                    )

            except Exception as e:
                print(f"Error analyzing dependencies for {file_path}: {e}")

    def _extract_imports(
        self, tree: ast.AST, file_path: Path
    ) -> Tuple[List[str], List[str]]:
        """Extract imports using AST analysis."""
        internal_imports = []  # Imports that resolve to project files
        all_imports = []  # All imports including external libraries
        current_folder = self._get_folder_name(file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_name = alias.name
                    all_imports.append(import_name)

                    # Check if it resolves to an internal project file
                    import_id = self._resolve_import_to_file(
                        import_name, current_folder
                    )
                    if import_id:
                        internal_imports.append(import_id)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_name = node.module
                    all_imports.append(import_name)

                    # Check if it resolves to an internal project file
                    import_id = self._resolve_import_to_file(
                        import_name, current_folder
                    )
                    if import_id:
                        internal_imports.append(import_id)

        return list(set(internal_imports)), list(set(all_imports))  # Remove duplicates

    def _resolve_import_to_file(self, import_name: str, current_folder: str) -> str:
        """Resolve import name to actual file unique ID."""
        # Check for relative imports
        if import_name.startswith("."):
            # Handle relative imports
            if import_name.startswith(".."):
                # Parent directory import
                parts = (
                    import_name.lstrip(".").split(".")
                    if import_name.lstrip(".")
                    else []
                )
            else:
                # Current directory import
                parts = (
                    import_name.lstrip(".").split(".")
                    if import_name.lstrip(".")
                    else []
                )

            if parts:
                potential_file = parts[0]
                folder_prefix = current_folder if current_folder != "root" else ""
                if folder_prefix:
                    unique_id = f"{folder_prefix}__{potential_file}"
                else:
                    unique_id = f"root__{potential_file}"

                if unique_id in self.dependencies:
                    return unique_id

        # Check for absolute imports
        parts = import_name.split(".")
        potential_file = parts[0]

        # Try different folder combinations
        for folder in [
            "root",
            "archive",
            "callbacks",
            "flowchart_visualization",
            "graph_output",
            "old_streamlit_files",
            "state_management",
            "tests",
            "assets",
            "reports",
        ]:
            if folder == "root":
                unique_id = f"root__{potential_file}"
            else:
                unique_id = f"{folder}__{potential_file}"

            if unique_id in self.dependencies:
                return unique_id

        return None

    def _create_unique_id(self, file_path: Path) -> str:
        """Create unique identifier for file."""
        folder = self._get_folder_name(file_path)
        if folder == "root":
            return f"root__{file_path.stem}"
        else:
            return f"{folder}__{file_path.stem}"

    def _get_folder_name(self, file_path: Path) -> str:
        """Get folder name for file."""
        parts = file_path.parts
        if len(parts) > 1:
            return parts[-2] if parts[-2] != "." else "root"
        return "root"

    def _create_display_name(self, file_path: Path) -> str:
        """Create display name for file."""
        folder = self._get_folder_name(file_path)
        if folder == "root":
            return file_path.stem
        else:
            return f"{file_path.stem} ({folder})"

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return (
            "test" in file_path.parts
            or file_path.stem.startswith("test_")
            or file_path.stem.endswith("_test")
        )

    def _calculate_node_importance(self) -> None:
        """Calculate node importance using PageRank algorithm."""
        # Initialize importance scores
        importance = {node_id: 1.0 for node_id in self.dependencies}

        # Build adjacency graph
        outgoing = {node_id: [] for node_id in self.dependencies}
        incoming = {node_id: [] for node_id in self.dependencies}

        for node_id, info in self.dependencies.items():
            for imported_id in info["imports"]:
                if imported_id in self.dependencies:
                    outgoing[node_id].append(imported_id)
                    incoming[imported_id].append(node_id)

        # Iterative PageRank calculation
        damping_factor = 0.85
        for iteration in range(20):
            new_importance = {}

            for node_id in self.dependencies:
                base_score = (1 - damping_factor) / len(self.dependencies)
                link_score = 0

                for source_id in incoming[node_id]:
                    source_out_degree = len(outgoing[source_id])
                    if source_out_degree > 0:
                        link_score += importance[source_id] / source_out_degree

                new_importance[node_id] = base_score + damping_factor * link_score

            importance = new_importance

        # Normalize to 0-1 range
        max_importance = max(importance.values()) if importance.values() else 1
        self.node_importance = {k: v / max_importance for k, v in importance.items()}

    def _build_enhanced_graph_data(self) -> Dict[str, Any]:
        """Build enhanced graph data structure."""
        nodes = []
        edges = []
        node_index = {}

        # Define enhanced color scheme
        folder_colors = {
            "root": "#E3F2FD",
            "archive": "#FFEBEE",
            "callbacks": "#E8F5E8",
            "flowchart_visualization": "#E0F2F1",
            "graph_output": "#FAFAFA",
            "old_streamlit_files": "#FFF8E1",
            "state_management": "#F3E5F5",
            "tests": "#FFF3E0",  # New: Orange tint for tests
            "assets": "#F1F8E9",  # New: Light green for assets
            "reports": "#FCE4EC",  # New: Pink tint for reports
        }

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


def generate_enhanced_html_visualization(graph_data: Dict[str, Any]) -> str:
    """Generate enhanced HTML visualization with optimized layout and curves."""

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Dependency Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        
        .controls {{
            width: 380px;  /* Increased width for new controls */
            background: white;
            border-right: 2px solid #e9ecef;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 8px rgba(0,0,0,0.1);
        }}
        
        .graph-container {{
            flex: 1;
            position: relative;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        #graph {{
            width: 100%;
            height: 100%;
            background: white;
            cursor: grab;
        }}
        
        #graph:active {{
            cursor: grabbing;
        }}
        
        /* Enhanced node styles */
        .node-rect {{
            stroke: #333;
            stroke-width: 1.5;
            rx: 8;
            ry: 8;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
            transition: all 0.2s ease;
        }}
        
        .node-rect:hover {{
            stroke-width: 2.5;
            filter: drop-shadow(3px 3px 8px rgba(0,0,0,0.3));
        }}
        
        .node-rect.highlighted {{
            stroke: #ff6600;
            stroke-width: 3;
            filter: drop-shadow(0 0 12px rgba(255,102,0,0.6));
        }}
        
        .node-rect.dimmed {{
            opacity: 0.3;
        }}
        
        /* Enhanced link styles */
        .link {{
            fill: none;
            stroke: #666;
            stroke-width: 1.5;
            opacity: 0.8;
            transition: all 0.3s ease;
        }}
        
        .link:hover {{
            stroke-width: 2.5;
            opacity: 1;
        }}
        
        .link.highlighted {{
            stroke: #ff6600;
            stroke-width: 3;
            opacity: 1;
        }}
        
        .link.dimmed {{
            opacity: 0.2;
        }}
        
        .link.hidden {{
            display: none;
        }}
        
        .link.test-related {{
            stroke-dasharray: 4,4;
        }}
        
        /* Enhanced text styles */
        .node-label {{
            font-size: 11px;
            font-weight: 600;
            text-anchor: middle;
            pointer-events: none;
            fill: #333;
        }}
        
        .folder-label-text {{
            font-size: 9px;
            text-anchor: middle;
            pointer-events: none;
            fill: #666;
            font-style: italic;
        }}
        
        /* Control panel styles */
        .section {{
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        
        .section h3 {{
            margin: 0 0 15px 0;
            color: #495057;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .folder-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 4px 0;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .folder-item:hover {{
            background: #e3f2fd;
            border-color: #90caf9;
        }}
        
        .folder-checkbox {{
            font-size: 16px;
            margin-right: 10px;
            user-select: none;
        }}
        
        .folder-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 10px;
            border: 1px solid #dee2e6;
        }}
        
        .folder-label {{
            flex: 1;
            font-size: 13px;
            font-weight: 500;
        }}
        
        .folder-count {{
            font-weight: normal;
            color: #6c757d;
            font-size: 11px;
        }}
        
        .test-count {{
            font-weight: normal;
            color: #fd7e14;
            font-size: 11px;
        }}
        
        .reset-button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.2s ease;
            width: 100%;
        }}
        
        .reset-button:hover {{
            background: #0056b3;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        
        .stat-item {{
            background: white;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #007bff;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: #6c757d;
            text-transform: uppercase;
        }}
        
        /* Tooltip styles */
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 6px;
            pointer-events: none;
            font-size: 12px;
            max-width: 300px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        
        .importance-indicator {{
            position: absolute;
            top: -8px;
            right: -8px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #ffc107;
            border: 2px solid white;
            display: none;
        }}
        
        .importance-indicator.high {{
            display: block;
            background: #dc3545;
        }}
        
        .importance-indicator.medium {{
            display: block;
            background: #fd7e14;
        }}
        
        .importance-indicator.low {{
            display: block;
            background: #ffc107;
        }}
        
        /* Layout toggle styles */
        .layout-toggle {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        
        .layout-toggle-label {{
            font-size: 13px;
            font-weight: 500;
            color: #495057;
        }}
        
        .toggle-switch {{
            position: relative;
            width: 50px;
            height: 24px;
            background-color: #ccc;
            border-radius: 12px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}
        
        .toggle-switch.active {{
            background-color: #007bff;
        }}
        
        .toggle-slider {{
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background-color: white;
            border-radius: 50%;
            transition: transform 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .toggle-switch.active .toggle-slider {{
            transform: translateX(26px);
        }}
        
        .layout-mode-indicator {{
            font-size: 11px;
            color: #6c757d;
            margin-top: 5px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="controls">
            <div class="section">
                <h3>📊 Statistics</h3>
                <div id="stats-content" class="stats-grid"></div>
            </div>
            
            <div class="section">
                <h3>🎛️ Layout Control</h3>
                <div class="layout-toggle" id="layout-toggle">
                    <span class="layout-toggle-label">📐 Hierarchical</span>
                    <div class="toggle-switch" id="toggle-switch">
                        <div class="toggle-slider"></div>
                    </div>
                    <span class="layout-toggle-label">🌐 Force-Directed</span>
                </div>
                <div class="layout-mode-indicator" id="layout-indicator">
                    Current: Hierarchical Layout
                </div>
            </div>
            
            <div class="section">
                <h3>📁 Directories</h3>
                <div class="folder-item" id="select-all-toggle" role="checkbox" tabindex="0" style="border-bottom: 1px solid #e9ecef; margin-bottom: 10px; padding-bottom: 8px; font-weight: bold;">
                    <span class="folder-checkbox">☑</span>
                    <span class="folder-label">Select All Directories</span>
                </div>
                <div id="folder-controls"></div>
            </div>
            
            <div class="section">
                <h3>🔍 Advanced Filters</h3>
                <div style="margin-bottom: 15px;">
                    <label for="imports-filter" style="display: block; font-size: 0.9em; margin-bottom: 5px; color: #6c757d;">
                        📥 Max Internal Imports:
                    </label>
                    <input type="range" id="imports-filter" min="0" max="20" value="20" style="width: 100%; margin-bottom: 5px;">
                    <div style="font-size: 0.8em; color: #6c757d; text-align: center;">
                        <span id="imports-filter-value">20</span> imports
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label for="dependencies-filter" style="display: block; font-size: 0.9em; margin-bottom: 5px; color: #6c757d;">
                        📤 Max Dependencies (outgoing):
                    </label>
                    <input type="range" id="dependencies-filter" min="0" max="20" value="20" style="width: 100%; margin-bottom: 5px;">
                    <div style="font-size: 0.8em; color: #6c757d; text-align: center;">
                        <span id="dependencies-filter-value">20</span> dependencies
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label for="size-filter" style="display: block; font-size: 0.9em; margin-bottom: 5px; color: #6c757d;">
                        📄 Max File Size (KB):
                    </label>
                    <input type="range" id="size-filter" min="0" max="100" value="100" style="width: 100%; margin-bottom: 5px;">
                    <div style="font-size: 0.8em; color: #6c757d; text-align: center;">
                        <span id="size-filter-value">100</span> KB
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3>🧪 Test Controls</h3>
                <div class="folder-item" id="test-toggle" role="checkbox" tabindex="0">
                    <span class="folder-checkbox">☑</span>
                    <span class="folder-label">Show Test Dependencies</span>
                </div>
            </div>
            
            <div class="section">
                <h3>🔧 Controls</h3>
                <button class="reset-button" onclick="resetAllFilters()">Reset All Filters</button>
            </div>
        </div>
        
        <div class="graph-container">
            <svg id="graph"></svg>
            <div id="tooltip" class="tooltip" aria-hidden="true"></div>
        </div>
    </div>

    <script>
        // Enhanced graph data with complete directory inclusion
        const graphData = {graph_data_json};

        // Enhanced state management
        let checkedFolders = new Set(Object.keys(graphData.subfolder_info));
        let showTestDependencies = true;
        let selectedNode = null;
        let highlightedNodes = new Set();

        // Layout state management
        let currentLayout = "hierarchical";
        let simulation = null;

        // Advanced filter state
        let maxImportsFilter = 20;
        let maxDependenciesFilter = 20;
        let maxSizeFilter = 100; // KB

        // D3.js setup with enhanced features
        const svg = d3.select("#graph");
        const tooltip = d3.select("#tooltip");
        let width, height;

        function updateDimensions() {{
            const container = document.querySelector('.graph-container');
            width = container.clientWidth;
            height = container.clientHeight;
            svg.attr("width", width).attr("height", height);
        }}

        // Enhanced layout calculation with dependency-aware positioning (from backup)
        function calculateEnhancedHierarchicalLayout() {{
            // ...backup logic here...
            // Calculate node dimensions with importance weighting
            graphData.nodes.forEach(d => {{
                const importance = d.importance || 0;
                const baseWidth = Math.max(120, d.stem.length * 8 + 20);
                const baseHeight = d.folder !== "root" ? 40 : 30;
                // Scale size based on importance
                const importanceScale = 1 + (importance * 0.5);
                d.width = Math.round(baseWidth * importanceScale);
                d.height = Math.round(baseHeight * importanceScale);
            }});
            // Build adjacency maps
            const incomingEdges = new Map();
            const outgoingEdges = new Map();
            graphData.nodes.forEach(node => {{
                incomingEdges.set(node.index, []);
                outgoingEdges.set(node.index, []);
            }});
            graphData.edges.forEach(edge => {{
                if (shouldShowEdge(edge)) {{
                    incomingEdges.get(edge.target).push(edge.source);
                    outgoingEdges.get(edge.source).push(edge.target);
                }}
            }});
            // Layer assignment
            const levels = [];
            const nodeToLevel = new Map();
            const visited = new Set();
            const inDegree = new Map();
            graphData.nodes.forEach(node => {{
                inDegree.set(node.index, incomingEdges.get(node.index).length);
            }});
            let currentLevel = 0;
            while (visited.size < graphData.nodes.length) {{
                levels[currentLevel] = [];
                const candidateNodes = [];
                for (const node of graphData.nodes) {{
                    if (!visited.has(node.index) && inDegree.get(node.index) === 0) {{
                        candidateNodes.push(node);
                    }}
                }}
                if (candidateNodes.length === 0) {{
                    const remainingNodes = graphData.nodes.filter(n => !visited.has(n.index));
                    if (remainingNodes.length > 0) {{
                        candidateNodes.push(remainingNodes[0]);
                    }}
                }}
                for (const node of candidateNodes) {{
                    levels[currentLevel].push(node.index);
                    nodeToLevel.set(node.index, currentLevel);
                    visited.add(node.index);
                    for (const targetIdx of outgoingEdges.get(node.index)) {{
                        if (!visited.has(targetIdx)) {{
                            inDegree.set(targetIdx, Math.max(0, inDegree.get(targetIdx) - 1));
                        }}
                    }}
                }}
                currentLevel++;
                if (currentLevel > graphData.nodes.length) break;
            }}
            // Position assignment
            const margin = 60;
            const levelWidth = Math.max(300, (width - 2 * margin) / Math.max(1, levels.length));
            const nodeSpacing = 45;
            levels.forEach((level, levelIndex) => {{
                const x = margin + levelIndex * levelWidth;
                const totalHeight = level.length * nodeSpacing;
                const startY = Math.max(margin, (height - totalHeight) / 2);
                level.forEach((nodeIdx, positionIndex) => {{
                    const node = graphData.nodes[nodeIdx];
                    node.x = x;
                    node.y = startY + positionIndex * nodeSpacing;
                }});
            }});
            return {{ levels, nodeToLevel }};
        }}

        // Enhanced cubic Bézier curve generation (from backup)
        function createEnhancedCubicBezierPath(d) {{
            const source = graphData.nodes[d.source];
            const target = graphData.nodes[d.target];
            const sourceX = source.x + source.width/2;
            const sourceY = source.y;
            const targetX = target.x - target.width/2;
            const targetY = target.y;
            const dx = targetX - sourceX;
            const dy = targetY - sourceY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const curveFactor = Math.min(0.6, Math.max(0.2, distance / 400));
            const offsetFactor = Math.abs(dy) / 100;
            const cp1x = sourceX + dx * 0.3 + offsetFactor * 20;
            const cp1y = sourceY + dy * 0.1;
            const cp2x = targetX - dx * 0.3 - offsetFactor * 20;
            const cp2y = targetY - dy * 0.1;
            return `M${{sourceX}},${{sourceY}} C${{cp1x}},${{cp1y}} ${{cp2x}},${{cp2y}} ${{targetX}},${{targetY}}`;
        }}

        // Enhanced visibility logic (from backup)
        function shouldShowEdge(edge) {{
            const sourceNode = graphData.nodes.find(n => n.id === edge.source_name);
            const targetNode = graphData.nodes.find(n => n.id === edge.target_name);
            if (!sourceNode || !targetNode) return false;
            if (!shouldShowNode(sourceNode) || !shouldShowNode(targetNode)) return false;
            if (!showTestDependencies && edge.is_test_related) {{
                return false;
            }}
            return true;
        }}

        // Initialize enhanced visualization (from backup)
        function initializeEnhancedVisualization() {{
            updateDimensions();
            svg.selectAll("*").remove();
            const g = svg.append("g").attr("id", "main-group");
            const zoom = d3.zoom()
                .scaleExtent([0.1, 8])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }});
            svg.call(zoom);
            const layout = calculateEnhancedHierarchicalLayout();
            createEnhancedArrowMarkers();
            const linkGroup = g.append("g").attr("class", "links");
            const link = linkGroup.selectAll("path")
                .data(graphData.edges)
                .enter().append("path")
                .attr("class", d => {{
                    let classes = "link";
                    if (d.is_test_related) classes += " test-related";
                    return classes;
                }})
                .attr("d", d => createEnhancedCubicBezierPath(d))
                .attr("marker-end", "url(#arrowhead)");
            const nodeGroup = g.append("g").attr("class", "nodes");
            const node = nodeGroup.selectAll("g")
                .data(graphData.nodes)
                .enter().append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${{d.x}},${{d.y}})`)
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            const rect = node.append("rect")
                .attr("class", "node-rect")
                .attr("width", d => d.width)
                .attr("height", d => d.height)
                .attr("x", d => -d.width/2)
                .attr("y", d => -d.height/2)
                .attr("fill", d => d.color);
            node.filter(d => d.importance > 0.3)
                .append("circle")
                .attr("class", d => {{
                    if (d.importance > 0.7) return "importance-indicator high";
                    if (d.importance > 0.5) return "importance-indicator medium";
                    return "importance-indicator low";
                }})
                .attr("cx", d => d.width/2 - 8)
                .attr("cy", d => -d.height/2 + 8)
                .attr("r", 6);
            node.append("text")
                .attr("class", "node-label")
                .text(d => d.stem)
                .attr("dy", "-2px");
            node.filter(d => d.folder !== "root")
                .append("text")
                .attr("class", "folder-label-text")
                .text(d => `(${{d.folder}})`)
                .attr("dy", "10px");
            node.on("click", handleEnhancedNodeClick)
                .on("mouseover", handleEnhancedMouseOver)
                .on("mouseout", handleEnhancedMouseOut);
            svg.on("click", function(event) {{
                if (event.target === this) {{
                    resetHighlighting();
                }}
            }});
            window.graphElements = {{ node, link, g }};
            setupAdvancedFilters();
            updateEnhancedControls();
            updateEnhancedStats();
            updateEnhancedVisibility();
            setupLayoutToggle();
        }}

        // Enhanced arrow markers creation
        function createEnhancedArrowMarkers() {{
            const defs = svg.select("defs").empty() ? svg.append("defs") : svg.select("defs");
            
            // Standard arrow
            defs.append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#666");
            
            // Highlighted arrow
            defs.append("marker")
                .attr("id", "arrowhead-highlighted")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ff6600");
            
            // Dimmed arrow
            defs.append("marker")
                .attr("id", "arrowhead-dimmed")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ccc");
        }}
        
        // Enhanced event handlers
        function handleEnhancedNodeClick(event, d) {{
            event.stopPropagation();
            highlightEnhancedDirectPath(d);
        }}
        
        function handleEnhancedMouseOver(event, d) {{
            const depInfo = graphData.dependencies[d.id];
            const imports = depInfo.imports || [];
            const importNames = imports.map(id => {{
                const dep = graphData.dependencies[id];
                return dep ? dep.stem : id;
            }}).join(", ");
            
            const importanceLevel = d.importance > 0.7 ? "High" : 
                                  d.importance > 0.5 ? "Medium" : 
                                  d.importance > 0.3 ? "Low" : "Minimal";
            
            tooltip.style("opacity", 1)
                .attr("aria-hidden", "false")
                .html(`
                    <strong>${{d.stem}}</strong><br/>
                    <strong>Folder:</strong> ${{d.folder}}<br/>
                    <strong>Importance:</strong> ${{importanceLevel}} (${{(d.importance * 100).toFixed(1)}}%)<br/>
                    <strong>Dependencies:</strong> ${{imports.length}}<br/>
                    <strong>File Size:</strong> ${{(d.size / 1024).toFixed(1)}}KB<br/>
                    ${{d.is_test ? "<strong>Type:</strong> Test File<br/>" : ""}}
                    <strong>Imports:</strong> ${{importNames || "None"}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function handleEnhancedMouseOut() {{
            tooltip.style("opacity", 0).attr("aria-hidden", "true");
        }}
        
        // Enhanced highlighting
        function highlightEnhancedDirectPath(clickedNode) {{
            selectedNode = clickedNode;
            const connected = findEnhancedConnections(clickedNode.id);
            
            // Reset all elements
            window.graphElements.node.classed("dimmed highlighted", false);
            window.graphElements.node.selectAll(".node-rect").classed("dimmed highlighted", false);
            window.graphElements.link
                .classed("dimmed highlighted", false)
                .attr("marker-end", "url(#arrowhead)");
            
            // Apply highlighting
            window.graphElements.node
                .classed("highlighted", d => connected.has(d.id))
                .classed("dimmed", d => !connected.has(d.id));
            
            window.graphElements.node.selectAll(".node-rect")
                .classed("highlighted", function() {{
                    const nodeData = d3.select(this.parentNode).datum();
                    return connected.has(nodeData.id);
                }})
                .classed("dimmed", function() {{
                    const nodeData = d3.select(this.parentNode).datum();
                    return !connected.has(nodeData.id);
                }});
            
            window.graphElements.link
                .classed("highlighted", d => connected.has(d.source_name) && connected.has(d.target_name))
                .classed("dimmed", d => !(connected.has(d.source_name) && connected.has(d.target_name)))
                .attr("marker-end", d => {{
                    if (connected.has(d.source_name) && connected.has(d.target_name)) {{
                        return "url(#arrowhead-highlighted)";
                    }} else if (!(connected.has(d.source_name) && connected.has(d.target_name))) {{
                        return "url(#arrowhead-dimmed)";
                    }} else {{
                        return "url(#arrowhead)";
                    }}
                }});
            
            highlightedNodes = connected;
        }}
        
        function findEnhancedConnections(nodeId) {{
            const connected = new Set([nodeId]);
            
            // Find all connections respecting current filters
            graphData.edges.forEach(edge => {{
                if (!shouldShowEdge(edge)) return;
                
                if (edge.source_name === nodeId) {{
                    connected.add(edge.target_name);
                }}
                if (edge.target_name === nodeId) {{
                    connected.add(edge.source_name);
                }}
            }});
            
            return connected;
        }}
        
        function resetHighlighting() {{
            selectedNode = null;
            highlightedNodes.clear();
            window.graphElements.node.classed("dimmed highlighted", false);
            window.graphElements.node.selectAll(".node-rect").classed("dimmed highlighted", false);
            window.graphElements.link
                .classed("dimmed highlighted", false)
                .attr("marker-end", "url(#arrowhead)");
        }}
        
        // Enhanced controls
        function updateEnhancedControls() {{
            const container = d3.select("#folder-controls");
            container.selectAll("*").remove();
            
            Object.entries(graphData.subfolder_info).forEach(([folder, info]) => {{
                const item = container.append("div")
                    .attr("class", "folder-item")
                    .attr("role", "checkbox")
                    .attr("aria-checked", checkedFolders.has(folder))
                    .attr("tabindex", "0")
                    .on("click", () => toggleFolder(folder))
                    .on("keydown", function(event) {{
                        if (event.key === "Enter" || event.key === " ") {{
                            event.preventDefault();
                            toggleFolder(folder);
                        }}
                    }});
                
                item.append("span")
                    .attr("class", "folder-checkbox")
                    .text(checkedFolders.has(folder) ? "☑" : "☐");
                
                item.append("div")
                    .attr("class", "folder-color")
                    .style("background-color", info.color);
                
                const labelText = `${{folder}} <span class="folder-count">(${{info.count}} modules)</span>`;
                const testText = info.test_modules && info.test_modules.length > 0 ? 
                    ` <span class="test-count">[${{info.test_modules.length}} tests]</span>` : "";
                
                item.append("span")
                    .attr("class", "folder-label")
                    .html(labelText + testText);
            }});
            
            // Test toggle
            const testToggle = d3.select("#test-toggle");
            testToggle.select(".folder-checkbox")
                .text(showTestDependencies ? "☑" : "☐");
            
            testToggle.on("click", toggleTestDependencies);
            
            // Update "Select All" toggle
            const allFolders = Object.keys(graphData.subfolder_info);
            const allSelected = allFolders.every(folder => checkedFolders.has(folder));
            const selectAllToggle = d3.select("#select-all-toggle");
            selectAllToggle.select(".folder-checkbox")
                .text(allSelected ? "☑" : "☐");
        }}
        
        function updateEnhancedStats() {{
            const visibleNodes = graphData.nodes.filter(n => shouldShowNode(n));
            const visibleEdges = graphData.edges.filter(e => shouldShowEdge(e));
            const testFiles = visibleNodes.filter(n => n.is_test).length;
            const crossFolderEdges = visibleEdges.filter(e => e.is_cross_folder).length;
            
            const stats = [
                {{ value: graphData.nodes.length, label: "Total Files" }},
                {{ value: visibleNodes.length, label: "Visible Files" }},
                {{ value: graphData.edges.length, label: "Dependencies" }},
                {{ value: visibleEdges.length, label: "Visible Deps" }},
                {{ value: Object.keys(graphData.subfolder_info).length, label: "Directories" }},
                {{ value: testFiles, label: "Test Files" }}
            ];
            
            const container = d3.select("#stats-content");
            container.selectAll("*").remove();
            
            stats.forEach(stat => {{
                const item = container.append("div").attr("class", "stat-item");
                item.append("div").attr("class", "stat-value").text(stat.value);
                item.append("div").attr("class", "stat-label").text(stat.label);
            }});
        }}
        
        function updateEnhancedVisibility() {{
            if (!window.graphElements) return;
            
            // Update node visibility with advanced filtering
            window.graphElements.node
                .style("opacity", d => {{
                    if (!shouldShowNode(d)) return 0.1;
                    if (!showTestDependencies && d.is_test) return 0.3;
                    return 1;
                }})
                .style("display", d => shouldShowNode(d) ? "block" : "none");
            
            // Update link visibility
            window.graphElements.link
                .classed("hidden", d => !shouldShowEdge(d))
                .style("opacity", d => {{
                    if (!shouldShowEdge(d)) return 0;
                    return d.is_test_related && !showTestDependencies ? 0.3 : 0.8;
                }});
        }}
        
        function toggleFolder(folder) {{
            if (checkedFolders.has(folder)) {{
                checkedFolders.delete(folder);
            }} else {{
                checkedFolders.add(folder);
            }}
            updateEnhancedControls();
            updateEnhancedVisibility();
            updateEnhancedStats();
        }}
        
        function toggleTestDependencies() {{
            showTestDependencies = !showTestDependencies;
            updateEnhancedControls();
            updateEnhancedVisibility();
            updateEnhancedStats();
        }}
        
        function resetAllFilters() {{
            checkedFolders = new Set(Object.keys(graphData.subfolder_info));
            showTestDependencies = true;
            
            // Reset advanced filters
            maxImportsFilter = 20;
            maxDependenciesFilter = 20;
            maxSizeFilter = 100;
            
            // Update UI controls
            document.getElementById('imports-filter').value = maxImportsFilter;
            document.getElementById('dependencies-filter').value = maxDependenciesFilter;
            document.getElementById('size-filter').value = maxSizeFilter;
            updateFilterLabels();
            
            resetHighlighting();
            updateEnhancedControls();
            updateEnhancedVisibility();
            updateEnhancedStats();
        }}
        
        // Advanced filter functions
        function updateFilterLabels() {{
            document.getElementById('imports-filter-value').textContent = maxImportsFilter;
            document.getElementById('dependencies-filter-value').textContent = maxDependenciesFilter;
            document.getElementById('size-filter-value').textContent = maxSizeFilter;
        }}
        
        function setupAdvancedFilters() {{
            // Imports filter
            const importsSlider = document.getElementById('imports-filter');
            importsSlider.addEventListener('input', function() {{
                maxImportsFilter = parseInt(this.value);
                updateFilterLabels();
                updateEnhancedVisibility();
                updateEnhancedStats();
            }});
            
            // Dependencies filter  
            const dependenciesSlider = document.getElementById('dependencies-filter');
            dependenciesSlider.addEventListener('input', function() {{
                maxDependenciesFilter = parseInt(this.value);
                updateFilterLabels();
                updateEnhancedVisibility();
                updateEnhancedStats();
            }});
            
            // Size filter
            const sizeSlider = document.getElementById('size-filter');
            sizeSlider.addEventListener('input', function() {{
                maxSizeFilter = parseInt(this.value);
                updateFilterLabels();
                updateEnhancedVisibility();
                updateEnhancedStats();
            }});
            
            // Select all toggle
            const selectAllToggle = document.getElementById('select-all-toggle');
            selectAllToggle.addEventListener('click', function() {{
                const allFolders = Object.keys(graphData.subfolder_info);
                const allSelected = allFolders.every(folder => checkedFolders.has(folder));
                
                if (allSelected) {{
                    checkedFolders.clear();
                }} else {{
                    checkedFolders = new Set(allFolders);
                }}
                
                updateEnhancedControls();
                updateEnhancedVisibility();
                updateEnhancedStats();
            }});
            
            updateFilterLabels();
        }}
        
        function shouldShowNode(node) {{
            // Check folder visibility
            if (!checkedFolders.has(node.folder)) return false;
            
            // Check advanced filters
            if (node.imports_count > maxImportsFilter) return false;
            
            // Count outgoing dependencies
            const outgoingDeps = graphData.edges.filter(e => e.source_name === node.id).length;
            if (outgoingDeps > maxDependenciesFilter) return false;
            
            // Check file size (convert bytes to KB)
            const sizeKB = node.size / 1024;
            if (sizeKB > maxSizeFilter) return false;
            
            return true;
        }}
        
        // Force-directed layout using D3 force simulation
        function initializeForceDirectedLayout() {{
            console.log("🌐 Initializing force-directed layout...");
            
            // Calculate node dimensions for force layout
            graphData.nodes.forEach(d => {{
                const importance = d.importance || 0;
                const baseWidth = Math.max(120, d.stem.length * 8 + 20);
                const baseHeight = d.folder !== "root" ? 40 : 30;
                
                // Scale size based on importance
                const importanceScale = 1 + (importance * 0.5);
                d.width = Math.round(baseWidth * importanceScale);
                d.height = Math.round(baseHeight * importanceScale);
                
                // Set initial positions if not set
                if (d.x === undefined) d.x = width / 2 + (Math.random() - 0.5) * 200;
                if (d.y === undefined) d.y = height / 2 + (Math.random() - 0.5) * 200;
            }});
            
            // Create filtered links for simulation
            const validLinks = graphData.edges
                .filter(edge => shouldShowEdge(edge))
                .map(edge => ({{
                    source: edge.source,
                    target: edge.target,
                    strength: 0.5 + (graphData.nodes[edge.source]?.importance || 0) * 0.3
                }}));
            
            // Stop any existing simulation
            if (simulation) {{
                simulation.stop();
            }}
            
            // Create force simulation
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(validLinks)
                    .id(d => d.index)
                    .distance(d => {{
                        const sourceNode = graphData.nodes[d.source.index || d.source];
                        const targetNode = graphData.nodes[d.target.index || d.target];
                        const baseDistance = 150;
                        const importanceBonus = ((sourceNode?.importance || 0) + (targetNode?.importance || 0)) * 50;
                        return baseDistance + importanceBonus;
                    }})
                    .strength(d => d.strength || 0.5)
                )
                .force("charge", d3.forceManyBody()
                    .strength(d => {{
                        const importance = d.importance || 0;
                        const baseCharge = -800;
                        const importanceMultiplier = 1 + importance * 2;
                        return baseCharge * importanceMultiplier;
                    }})
                )
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide()
                    .radius(d => Math.max(d.width, d.height) / 2 + 10)
                    .strength(0.7)
                )
                .force("x", d3.forceX(width / 2).strength(0.1))
                .force("y", d3.forceY(height / 2).strength(0.1));
            
            // Update positions during simulation
            simulation.on("tick", () => {{
                updatePositionsForceLayout();
            }});
            
            // Reduce alpha target for smoother convergence
            simulation.alphaTarget(0.1).restart();
            
            console.log("✅ Force-directed layout initialized");
            return simulation;
        }}
        
        // Update positions for force layout
        function updatePositionsForceLayout() {{
            if (!window.graphElements) return;
            
            const {{ node, link }} = window.graphElements;
            
            // Update node positions
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            
            // Update link paths with force layout positions
            link.attr("d", d => {{
                const source = d.source.x !== undefined ? d.source : graphData.nodes[d.source];
                const target = d.target.x !== undefined ? d.target : graphData.nodes[d.target];
                
                if (!source || !target) return "";
                
                return createEnhancedCubicBezierPath({{
                    source: source.index,
                    target: target.index
                }});
            }});
        }}
        
        // Switch between hierarchical and force-directed layouts
        function switchLayout(newLayout) {{
            if (newLayout === currentLayout) return;
            
            console.log(`🔄 Switching from ${{currentLayout}} to ${{newLayout}} layout`);
            currentLayout = newLayout;
            
            // Update toggle UI
            const toggleSwitch = document.getElementById('toggle-switch');
            const layoutIndicator = document.getElementById('layout-indicator');
            
            if (newLayout === "force") {{
                toggleSwitch.classList.add('active');
                layoutIndicator.textContent = "Current: Force-Directed Layout";
                
                // Initialize force-directed layout
                initializeForceDirectedLayout();
                
            }} else {{
                toggleSwitch.classList.remove('active');
                layoutIndicator.textContent = "Current: Hierarchical Layout";
                
                // Stop force simulation
                if (simulation) {{
                    simulation.stop();
                    simulation = null;
                }}
                
                // Recalculate hierarchical layout
                const layout = calculateEnhancedHierarchicalLayout();
                
                // Animate to hierarchical positions
                animateToHierarchicalLayout();
            }}
        }}
        
        // Animate nodes to hierarchical positions
        function animateToHierarchicalLayout() {{
            if (!window.graphElements) return;
            
            const {{ node, link }} = window.graphElements;
            
            // Animate nodes to hierarchical positions
            node.transition()
                .duration(1000)
                .ease(d3.easeQuadInOut)
                .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            
            // Animate links to hierarchical curves
            link.transition()
                .duration(1000)
                .ease(d3.easeQuadInOut)
                .attr("d", d => createEnhancedCubicBezierPath(d));
        }}
        
        // Setup layout toggle functionality
        function setupLayoutToggle() {{
            const toggleSwitch = document.getElementById('toggle-switch');
            const layoutToggle = document.getElementById('layout-toggle');
            
            function handleToggle() {{
                const newLayout = currentLayout === "hierarchical" ? "force" : "hierarchical";
                switchLayout(newLayout);
            }}
            
            toggleSwitch.addEventListener('click', handleToggle);
            layoutToggle.addEventListener('click', function(event) {{
                if (event.target === toggleSwitch || event.target.closest('.toggle-switch')) {{
                    return; // Let the toggle switch handle it
                }}
                handleToggle();
            }});
            
            // Keyboard accessibility
            toggleSwitch.addEventListener('keydown', function(event) {{
                if (event.key === 'Enter' || event.key === ' ') {{
                    event.preventDefault();
                    handleToggle();
                }}
            }});
            
            toggleSwitch.setAttribute('tabindex', '0');
            toggleSwitch.setAttribute('role', 'switch');
            toggleSwitch.setAttribute('aria-checked', 'false');
        }}
        
        // Enhanced drag functions with layout awareness
        function dragstarted(event, d) {{
            if (currentLayout === "force" && simulation) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
            }}
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
            d.x = event.x;
            d.y = event.y;
            
            if (currentLayout === "hierarchical") {{
                updatePositions();
            }}
            // For force layout, the simulation handles position updates
        }}
        
        function dragended(event, d) {{
            if (currentLayout === "force" && simulation) {{
                if (!event.active) simulation.alphaTarget(0);
            }}
            d.fx = null;
            d.fy = null;
        }}
        
        function updatePositions() {{
            const {{ node, link }} = window.graphElements;
            if (!node || !link) return;
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            
            if (currentLayout === "hierarchical") {{
                link.attr("d", d => createEnhancedCubicBezierPath(d));
            }} else {{
                // For force layout, use the force layout position update
                updatePositionsForceLayout();
            }}
        }}
        
        // Initialize on load
        window.addEventListener("resize", updateDimensions);
        document.addEventListener("DOMContentLoaded", initializeEnhancedVisualization);
    </script>
</body>
</html>"""

    return html_template.format(graph_data_json=json.dumps(graph_data, indent=2))


def main():
    """Generate enhanced dependency graph with all optimizations."""
    print("🚀 PHASE 4: ENHANCED DEPENDENCY GRAPH IMPLEMENTATION")
    print("=" * 60)

    # Create enhanced analyzer
    analyzer = EnhancedDependencyAnalyzer()

    # Analyze project with all directories
    print("📊 Analyzing complete project structure...")
    graph_data = analyzer.analyze_project()

    # Generate enhanced HTML visualization
    print("🎨 Generating enhanced visualization...")
    html_content = generate_enhanced_html_visualization(graph_data)

    # Save files
    output_dir = Path("graph_output")
    output_dir.mkdir(exist_ok=True)

    # Save enhanced graph data
    with open(output_dir / "enhanced_graph_data.json", "w") as f:
        json.dump(graph_data, f, indent=2)

    # Save enhanced HTML
    with open(
        output_dir / "enhanced_dependency_graph.html", "w", encoding="utf-8"
    ) as f:
        f.write(html_content)

    print("✅ ENHANCED DEPENDENCY GRAPH COMPLETE!")
    print("=" * 50)
    print(f"📊 Analysis Results:")
    stats = graph_data["statistics"]
    print(f"   - Total files analyzed: {stats['total_files']}")
    print(f"   - Total dependencies: {stats['total_dependencies']}")
    print(f"   - Cross-folder dependencies: {stats['cross_folder_dependencies']}")
    print(f"   - Test files included: {stats['test_files']}")
    print(f"   - Directories included: {stats['folders']}")

    print("\n🎯 Key Enhancements:")
    print("   ✅ Complete directory inclusion (including tests, assets, reports)")
    print("   ✅ Enhanced hierarchical layout with importance-based positioning")
    print("   ✅ Force-directed layout toggle with D3.js simulation")
    print("   ✅ Smooth layout transitions and animations")
    print("   ✅ Cubic Bézier curves with adaptive control points")
    print("   ✅ Node importance visualization with PageRank algorithm")
    print("   ✅ Test dependency toggle and visual indicators")
    print("   ✅ Enhanced tooltips with detailed information")
    print("   ✅ Interactive layout switching controls")

    print("\n📄 Generated Files:")
    print("   - Enhanced graph data: graph_output/enhanced_graph_data.json")
    print("   - Enhanced visualization: graph_output/enhanced_dependency_graph.html")

    return graph_data


if __name__ == "__main__":
    main()
