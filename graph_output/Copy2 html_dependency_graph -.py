"""
HTML-based Dependency Graph Generator
Migrated from SVG injection to pure HTML + D3.js solution for maximum flexibility
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List


class DependencyAnalyzer:
    """Analyzes Python files and extracts dependency information."""

    def __init__(self, exclude_folders: List[str] = None):
        self.exclude_folders = exclude_folders or ["tests", "__pycache__"]

    def extract_imports(self, file_path: str) -> List[str]:
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

    def get_subfolder_colors(self) -> Dict[str, str]:
        """Define color scheme for different subfolders."""
        return {
            "root": "#E3F2FD",  # Light Blue - for root files
            "archive": "#FFEBEE",  # Light Red - for archived files
            "callbacks": "#E8F5E8",  # Light Green - for callback modules
            "tests": "#FFF3E0",  # Light Orange - for test files
            "state_management": "#F3E5F5",  # Light Purple - for state management
            "flowchart_visualization": "#E0F2F1",  # Light Teal - for flowchart
            "old_streamlit_files": "#FFF8E1",  # Light Yellow - for old files
            "graph_output": "#FAFAFA",  # Light Grey - for graph output
            "reports": "#FFFDE7",  # Light Lime - for reports
            "assets": "#F1F8E9",  # Light Light Green - for assets
        }

    def get_file_subfolder(self, file_path: str) -> str:
        """Get the subfolder name for a file, or 'root' if it's in the root directory."""
        path_parts = Path(file_path).parts
        if len(path_parts) > 1:
            return path_parts[0]  # First directory in the path
        return "root"

    def scan_python_files(self, base_path: str = ".") -> List[str]:
        """Recursively find all .py files, excluding specified folders."""
        py_files = []
        for file_path in Path(base_path).rglob("*.py"):
            if file_path.is_file():
                # Check if any excluded folder is in the path
                if not any(
                    excluded in file_path.parts for excluded in self.exclude_folders
                ):
                    py_files.append(str(file_path))
        return py_files

    def generate_unique_id(self, file_path: str) -> str:
        """Generate unique ID that includes folder context to handle duplicates."""
        path_obj = Path(file_path)
        stem = path_obj.stem

        # Get parent folder (or 'root' if in base directory)
        parent = path_obj.parent
        if str(parent) == ".":
            folder_context = "root"
        else:
            folder_context = str(parent).replace("\\", "_").replace("/", "_")

        return f"{folder_context}__{stem}"

    def analyze_dependencies(self, py_files: List[str]) -> Dict:
        """Analyze dependencies and return structured data for visualization."""
        local_modules = {}  # Map unique_id -> stem for lookup
        module_info = {}  # Map unique_id -> file info

        # Get unique IDs and build lookup maps
        for file_path in py_files:
            unique_id = self.generate_unique_id(file_path)
            stem = Path(file_path).stem
            local_modules[unique_id] = stem
            module_info[unique_id] = {
                "stem": stem,
                "file_path": file_path,
                "folder": self.get_file_subfolder(file_path),
            }

        # Extract dependencies for each file
        dependencies = {}
        for file_path in py_files:
            unique_id = self.generate_unique_id(file_path)
            info = module_info[unique_id]
            imports = self.extract_imports(file_path)

            # Filter to only local dependencies and convert to unique IDs
            local_imports = []
            for imp in imports:
                # Find matching unique_id for this import stem
                for uid, stem in local_modules.items():
                    if stem == imp and uid != unique_id:
                        local_imports.append(uid)
                        break

            dependencies[unique_id] = {
                "imports": local_imports,
                "file_path": file_path,
                "folder": info["folder"],
                "stem": info["stem"],
                "display_name": (
                    f"{info['stem']} ({info['folder']})"
                    if info["folder"] != "root"
                    else info["stem"]
                ),
            }

        # Build folder information
        folder_colors = self.get_subfolder_colors()
        subfolder_info = {}

        for unique_id, info in module_info.items():
            folder = info["folder"]
            if folder not in subfolder_info:
                subfolder_info[folder] = {
                    "color": folder_colors.get(folder, "#F0F0F0"),
                    "modules": [],
                }
            subfolder_info[folder]["modules"].append(unique_id)

        # Build nodes and edges for D3.js
        nodes = []
        edges = []
        node_index = {}

        # Create nodes
        for i, (unique_id, info) in enumerate(dependencies.items()):
            nodes.append(
                {
                    "id": unique_id,
                    "name": info["display_name"],
                    "stem": info["stem"],
                    "folder": info["folder"],
                    "color": folder_colors.get(info["folder"], "#F0F0F0"),
                    "file_path": info["file_path"],
                    "imports_count": len(info["imports"]),
                    "index": i,
                }
            )
            node_index[unique_id] = i

        # Create edges
        for unique_id, info in dependencies.items():
            source_index = node_index[unique_id]
            for imported_id in info["imports"]:
                if imported_id in node_index and imported_id != unique_id:
                    target_index = node_index[imported_id]
                    edges.append(
                        {
                            "source": source_index,
                            "target": target_index,
                            "source_name": unique_id,
                            "target_name": imported_id,
                            "source_folder": dependencies[unique_id]["folder"],
                            "target_folder": dependencies[imported_id]["folder"],
                        }
                    )

        return {
            "nodes": nodes,
            "edges": edges,
            "subfolder_info": subfolder_info,
            "dependencies": dependencies,
        }


class HTMLGraphGenerator:
    """Generates HTML-based interactive dependency graph."""

    def __init__(self, output_dir: str = "graph_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_html(self, graph_data: Dict, title: str = "Dependency Graph") -> str:
        """Generate complete HTML file with D3.js visualization."""

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .container {{
            display: flex;
            gap: 20px;
            height: calc(100vh - 40px);
        }}
        
        .sidebar {{
            width: 300px;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-y: auto;
        }}
        
        .graph-container {{
            flex: 1;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
        }}
        
        .sidebar h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        
        .folder-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            padding: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        
        .folder-item:hover {{
            background-color: #f0f0f0;
        }}
        
        .folder-checkbox {{
            margin-right: 10px;
            font-size: 16px;
            user-select: none;
        }}
        
        .folder-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 10px;
            border: 1px solid #ccc;
        }}
        
        .folder-label {{
            flex: 1;
            font-size: 14px;
        }}
        
        .folder-count {{
            font-size: 12px;
            color: #666;
            font-weight: normal;
        }}
        
        .instructions {{
            margin-top: 20px;
            padding: 15px;
            background-color: #e8f4fd;
            border-radius: 4px;
            font-size: 13px;
            color: #0c5460;
        }}
        
        .instructions h3 {{
            margin-top: 0;
            color: #0c5460;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .node.dimmed {{
            opacity: 0.2;
        }}
        
        .node.highlighted {{
            opacity: 1;
        }}
        
        .node-rect {{
            stroke: #333;
            stroke-width: 1;
            rx: 5;
            ry: 5;
            transition: all 0.2s ease;
        }}
        
        .node-rect.highlighted {{
            stroke: #ff6600;
            stroke-width: 3px;
        }}
        
        .node-rect.dimmed {{
            opacity: 0.3;
        }}
        
        .link {{
            fill: none;
            stroke: #999;
            stroke-width: 2;
            transition: all 0.2s ease;
        }}
        
        .link.dimmed {{
            opacity: 0.1;
        }}
        
        .link.highlighted {{
            stroke: #ff6600;
            stroke-width: 3px;
            opacity: 1;
        }}
        
        .link.hidden {{
            opacity: 0;
        }}
        
        .node-label {{
            font-size: 11px;
            font-family: Arial, sans-serif;
            text-anchor: middle;
            dominant-baseline: central;
            pointer-events: none;
            fill: #333;
            font-weight: 500;
        }}
        
        .folder-label-text {{
            font-size: 9px;
            fill: #666;
            text-anchor: middle;
            dominant-baseline: central;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        
        .stats {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            font-size: 13px;
        }}
        
        .stats h3 {{
            margin-top: 0;
            color: #333;
        }}
        
        .reset-button {{
            width: 100%;
            padding: 10px;
            background-color: #007acc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 15px;
        }}
        
        .reset-button:hover {{
            background-color: #005a9e;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
                height: auto;
            }}
            
            .sidebar {{
                width: auto;
                order: 2;
            }}
            
            .graph-container {{
                height: 60vh;
                order: 1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>Folder Legend</h2>
            <div id="folder-controls" role="group" aria-label="Folder filtering controls"></div>
            
            <div class="instructions">
                <h3>Instructions</h3>
                <ul>
                    <li>Click any node to highlight its direct path connections</li>
                    <li>Toggle folder checkboxes to show/hide modules</li>
                    <li>Click empty space to reset highlighting</li>
                    <li>Hover nodes for details</li>
                </ul>
            </div>
            
            <div class="stats" id="stats" role="region" aria-label="Graph statistics">
                <h3>Statistics</h3>
                <div id="stats-content"></div>
            </div>
            
            <button class="reset-button" onclick="resetAllFilters()"
                    aria-label="Reset all folder filters">Reset All Filters</button>
        </div>
        
        <div class="graph-container">
            <svg id="graph" width="100%" height="100%" role="img" aria-label="Dependency graph visualization"></svg>
            <div class="tooltip" id="tooltip" role="tooltip" aria-hidden="true"></div>
        </div>
    </div>

    <script>
        // Graph data
        const graphData = {json.dumps(graph_data, indent=2)};
        
        // State management
        let checkedFolders = new Set(Object.keys(graphData.subfolder_info));
        let selectedNode = null;
        let highlightedNodes = new Set();
        
        // D3.js setup
        const svg = d3.select("#graph");
        const tooltip = d3.select("#tooltip");
        let width, height;
        
        function updateDimensions() {{
            const container = document.querySelector('.graph-container');
            width = container.clientWidth;
            height = container.clientHeight;
            svg.attr("width", width).attr("height", height);
        }}
        
        // Initialize visualization
        function initializeVisualization() {{
            updateDimensions();
            
            // Clear any existing content
            svg.selectAll("*").remove();
            
            // Create main graph group
            const g = svg.append("g").attr("id", "main-group");
            
            // Add zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }});
            
            svg.call(zoom);
            
            // Calculate hierarchical layout
            const layout = calculateHierarchicalLayout();
            
            // Create arrow markers
            createArrowMarkers();
            
            // Create curved links
            const linkGroup = g.append("g").attr("class", "links");
            const link = linkGroup.selectAll("path")
                .data(graphData.edges)
                .enter().append("path")
                .attr("class", "link")
                .attr("d", d => createCurvedPath(d))
                .attr("marker-end", "url(#arrowhead)");
            
            // Create node groups
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
            
            // Add rectangles to nodes
            node.append("rect")
                .attr("class", "node-rect")
                .attr("width", d => d.width)
                .attr("height", d => d.height)
                .attr("x", d => -d.width/2)
                .attr("y", d => -d.height/2)
                .attr("fill", d => d.color);
            
            // Add main text labels
            node.append("text")
                .attr("class", "node-label")
                .text(d => d.stem)
                .attr("dy", "-2px");
            
            // Add folder labels if not root
            node.filter(d => d.folder !== "root")
                .append("text")
                .attr("class", "folder-label-text")
                .text(d => `(${{d.folder}})`)
                .attr("dy", "10px");
            
            // Add event listeners
            node.on("click", handleNodeClick)
                .on("mouseover", handleMouseOver)
                .on("mouseout", handleMouseOut);
            
            svg.on("click", function(event) {{
                if (event.target === this) {{
                    resetHighlighting();
                }}
            }});
            
            // Store references for global access
            window.graphElements = {{ node, link, g }};
            
            // Initial updates
            updateFolderControls();
            updateStats();
            updateVisibility();
        }}
        
        // Create arrow markers
        function createArrowMarkers() {{
            const defs = svg.select("defs").empty() ? svg.append("defs") : svg.select("defs");
            
            // Normal arrow
            defs.append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
            
            // Dimmed arrow
            defs.append("marker")
                .attr("id", "arrowhead-dimmed")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ddd");
            
            // Highlighted arrow
            defs.append("marker")
                .attr("id", "arrowhead-highlighted")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ff6600");
        }}
        
        // Calculate text dimensions and node sizes
        function calculateNodeDimensions(d) {{
            // Estimate text width (rough approximation)
            const stemWidth = d.stem.length * 8;
            const folderWidth = d.folder !== "root" ? d.folder.length * 6 : 0;
            const maxWidth = Math.max(stemWidth, folderWidth);
            
            return {{
                width: Math.max(120, maxWidth + 20),
                height: d.folder !== "root" ? 40 : 30
            }};
        }}
        
        // Create curved path for connections
        function createCurvedPath(d) {{
            const source = graphData.nodes[d.source];
            const target = graphData.nodes[d.target];
            
            const sourceX = source.x + source.width/2;
            const sourceY = source.y;
            const targetX = target.x - target.width/2;
            const targetY = target.y;
            
            const dx = targetX - sourceX;
            const dy = targetY - sourceY;
            const dr = Math.sqrt(dx * dx + dy * dy) * 0.3;
            
            return `M${{sourceX}},${{sourceY}}A${{dr}},${{dr}} 0 0,1 ${{targetX}},${{targetY}}`;
        }}
        
        // Hierarchical layout calculation - COMPLETELY REWRITTEN
        function calculateHierarchicalLayout() {{
            console.log("Starting layout calculation with", graphData.nodes.length, "nodes");
            
            // First, calculate node dimensions
            graphData.nodes.forEach(d => {{
                const dims = calculateNodeDimensions(d);
                d.width = dims.width;
                d.height = dims.height;
            }});
            
            // Build adjacency maps
            const incomingEdges = new Map();
            const outgoingEdges = new Map();
            
            // Initialize maps
            graphData.nodes.forEach(node => {{
                incomingEdges.set(node.index, []);
                outgoingEdges.set(node.index, []);
            }});
            
            // Populate adjacency maps
            graphData.edges.forEach(edge => {{
                incomingEdges.get(edge.target).push(edge.source);
                outgoingEdges.get(edge.source).push(edge.target);
            }});
            
            // Calculate dependency levels using topological sort
            const levels = [];
            const nodeToLevel = new Map();
            const visited = new Set();
            const inDegree = new Map();
            
            // Calculate in-degrees
            graphData.nodes.forEach(node => {{
                inDegree.set(node.index, incomingEdges.get(node.index).length);
            }});
            
            // Process nodes level by level
            let currentLevel = 0;
            while (visited.size < graphData.nodes.length) {{
                levels[currentLevel] = [];
                
                // Find nodes with zero in-degree for this level
                const currentLevelNodes = [];
                graphData.nodes.forEach(node => {{
                    if (!visited.has(node.index) && inDegree.get(node.index) === 0) {{
                        currentLevelNodes.push(node.index);
                    }}
                }});
                
                // If no zero in-degree nodes, pick remaining nodes with minimum in-degree
                if (currentLevelNodes.length === 0) {{
                    const remainingNodes = graphData.nodes.filter(n => !visited.has(n.index));
                    if (remainingNodes.length > 0) {{
                        const minDegree = Math.min(...remainingNodes.map(n => inDegree.get(n.index)));
                        remainingNodes.forEach(node => {{
                            if (inDegree.get(node.index) === minDegree) {{
                                currentLevelNodes.push(node.index);
                            }}
                        }});
                    }}
                }}
                
                // Add nodes to current level
                currentLevelNodes.forEach(nodeIndex => {{
                    levels[currentLevel].push(nodeIndex);
                    nodeToLevel.set(nodeIndex, currentLevel);
                    visited.add(nodeIndex);
                    
                    // Decrease in-degree of connected nodes
                    outgoingEdges.get(nodeIndex).forEach(targetIndex => {{
                        if (!visited.has(targetIndex)) {{
                            inDegree.set(targetIndex, inDegree.get(targetIndex) - 1);
                        }}
                    }});
                }});
                
                currentLevel++;
                
                // Safety break
                if (currentLevel > graphData.nodes.length) {{
                    console.error("Layout calculation stuck in infinite loop");
                    break;
                }}
            }}
            
            console.log("Created", levels.length, "levels:", levels.map(l => l.length));
            
            // Calculate positions
            const margin = 50;
            const levelWidth = Math.max(250, (width - 2 * margin) / Math.max(1, levels.length));
            const nodeSpacing = 35;  // Reduced from 60 to handle larger levels better
            
            levels.forEach((level, levelIndex) => {{
                const x = margin + levelIndex * levelWidth;
                const totalHeight = level.length * nodeSpacing;
                const startY = Math.max(margin, (height - totalHeight) / 2);
                
                level.forEach((nodeIndex, positionIndex) => {{
                    const node = graphData.nodes[nodeIndex];
                    node.x = x;
                    node.y = startY + positionIndex * nodeSpacing;
                }});
            }});
            
            console.log("Layout completed. Sample positions:", 
                graphData.nodes.slice(0, 3).map(n => `${{n.stem}}: (${{n.x}}, ${{n.y}})`));
            
            return {{ levels, nodeToLevel }};
        }}
        
        // Update positions function - REWRITTEN for rectangular nodes
        function updatePositions() {{
            const {{ node, link }} = window.graphElements;
            
            if (!node || !link) return;
            
            // Update node positions
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            
            // Update curved link paths
            link.attr("d", d => createCurvedPath(d));
        }}
        
        // Event handlers
        function handleNodeClick(event, d) {{
            event.stopPropagation();
            highlightDirectPath(d);
        }}
        
        function handleMouseOver(event, d) {{
            const depInfo = graphData.dependencies[d.id];
            const imports = depInfo.imports;
            const importNames = imports.map(id => graphData.dependencies[id].stem).join(", ");
            
            tooltip.style("opacity", 1)
                .attr("aria-hidden", "false")
                .html(`
                    <strong>${{d.stem}}</strong><br/>
                    Folder: ${{d.folder}}<br/>
                    Imports: ${{imports.length}}<br/>
                    Dependencies: ${{importNames || "None"}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function handleMouseOut() {{
            tooltip.style("opacity", 0)
                .attr("aria-hidden", "true");
        }}
        
        // Drag functions
        function dragstarted(event, d) {{
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
            d.x = event.x;
            d.y = event.y;
            updatePositions();
        }}
        
        function dragended(event, d) {{
            d.fx = null;
            d.fy = null;
        }}
        
        // Core functionality - UPDATED for rectangular nodes
        function highlightDirectPath(clickedNode) {{
            selectedNode = clickedNode;
            const connected = findDirectConnections(clickedNode.id);
            
            // Reset all nodes and their rectangles
            window.graphElements.node.classed("dimmed highlighted", false);
            window.graphElements.node.selectAll(".node-rect").classed("dimmed highlighted", false);
            window.graphElements.link
                .classed("dimmed highlighted", false)
                .attr("marker-end", "url(#arrowhead)");
            
            // Highlight connected nodes
            window.graphElements.node
                .classed("highlighted", d => connected.has(d.id))
                .classed("dimmed", d => !connected.has(d.id));
            
            // Highlight node rectangles specifically
            window.graphElements.node.selectAll(".node-rect")
                .classed("highlighted", function() {{
                    const nodeData = d3.select(this.parentNode).datum();
                    return connected.has(nodeData.id);
                }})
                .classed("dimmed", function() {{
                    const nodeData = d3.select(this.parentNode).datum();
                    return !connected.has(nodeData.id);
                }});
            
            // Highlight connected edges and update arrow markers
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
        
        function findDirectConnections(nodeId) {{
            const connected = new Set([nodeId]);
            
            // Find all direct incoming and outgoing connections
            graphData.edges.forEach(edge => {{
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
        
        function toggleFolder(folder) {{
            if (checkedFolders.has(folder)) {{
                checkedFolders.delete(folder);
            }} else {{
                checkedFolders.add(folder);
            }}
            updateFolderControls();
            updateVisibility();
            updateStats();
        }}
        
        function updateFolderControls() {{
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
                
                item.append("span")
                    .attr("class", "folder-label")
                    .html(`${{folder}} <span class="folder-count">(${{info.modules.length}} modules)</span>`);
            }});
        }}
        
        function updateVisibility() {{
            if (!window.graphElements) return;
            
            // Update nodes
            window.graphElements.node
                .style("opacity", d => checkedFolders.has(d.folder) ? 1 : 0.1);
            
            // Update links
            window.graphElements.link
                .classed("hidden", d => !checkedFolders.has(d.source_folder) || !checkedFolders.has(d.target_folder));
        }}
        
        function updateStats() {{
            const visibleNodes = graphData.nodes.filter(n => checkedFolders.has(n.folder));
            const visibleEdges = graphData.edges.filter(e => 
                checkedFolders.has(e.source_folder) && checkedFolders.has(e.target_folder)
            );
            
            const stats = `
                <div>Total Modules: ${{graphData.nodes.length}}</div>
                <div>Visible Modules: ${{visibleNodes.length}}</div>
                <div>Total Dependencies: ${{graphData.edges.length}}</div>
                <div>Visible Dependencies: ${{visibleEdges.length}}</div>
                <div>Folders: ${{Object.keys(graphData.subfolder_info).length}}</div>
                <div>Active Folders: ${{checkedFolders.size}}</div>
            `;
            
            document.getElementById("stats-content").innerHTML = stats;
        }}
        
        function resetAllFilters() {{
            checkedFolders = new Set(Object.keys(graphData.subfolder_info));
            resetHighlighting();
            updateFolderControls();
            updateVisibility();
            updateStats();
        }}
        
        // Initialize on load
        window.addEventListener("resize", updateDimensions);
        document.addEventListener("DOMContentLoaded", initializeVisualization);
    </script>
</body>
</html>"""

        return html_template

    def save_html(
        self, html_content: str, filename: str = "dependency_graph.html"
    ) -> str:
        """Save HTML content to file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filepath


def main():
    """Main function to generate HTML-based dependency graph."""
    print("🚀 Starting HTML-based dependency graph generation...")

    # Initialize components
    analyzer = DependencyAnalyzer()
    generator = HTMLGraphGenerator()

    # Step 1: Scan for Python files
    print("📁 Scanning for Python files...")
    py_files = analyzer.scan_python_files()
    if not py_files:
        print("❌ No Python files found!")
        return
    print(f"✅ Found {len(py_files)} Python files")

    # Step 2: Analyze dependencies
    print("🔍 Analyzing dependencies...")
    graph_data = analyzer.analyze_dependencies(py_files)
    print(
        f"✅ Analyzed {len(graph_data['nodes'])} modules with {len(graph_data['edges'])} dependencies"
    )

    # Step 3: Generate HTML
    print("🎨 Generating HTML visualization...")
    html_content = generator.generate_html(graph_data, "Python Dependency Graph")

    # Step 4: Save files
    html_file = generator.save_html(html_content)

    # Also save the raw data for potential future use
    data_file = os.path.join(generator.output_dir, "graph_data.json")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)

    print(f"✅ HTML graph generated: {html_file}")
    print(f"📊 Graph data saved: {data_file}")
    print(f"🌐 Open {html_file} in your browser to view the interactive graph!")


if __name__ == "__main__":
    main()
