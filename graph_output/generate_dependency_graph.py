import os
import subprocess
import glob
import sys
import ast
import json
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


def get_subfolder_colors():
    """Define color scheme for different subfolders."""
    colors = {
        "root": "#E3F2FD",  # Light Blue - for root files
        "archive": "#FFEBEE",  # Light Red - for archived files
        "callbacks": "#E8F5E8",  # Light Green - for callback modules
        "tests": "#FFF3E0",  # Light Orange - for test files
        "state_management": "#F3E5F5",  # Light Purple - for state management
        "flowchart_visualization": "#E0F2F1",  # Light Teal - for flowchart
        "old_streamlit_files": "#FFF8E1",  # Light Yellow - for old files
        "graph_output": "#FAFAFA",  # Light Grey - for graph output
    }
    return colors


def get_file_subfolder(file_path):
    """Get the subfolder name for a file, or 'root' if it's in the root directory."""
    path_parts = Path(file_path).parts
    if len(path_parts) > 1:
        return path_parts[0]  # First directory in the path
    return "root"


def create_dependency_graph(py_files, dot_file):
    """Create a DOT file showing dependencies between Python files."""
    dependencies = {}
    local_modules = set()
    module_folders = {}  # Track which folder each module belongs to

    # Get base names of local modules (without .py extension) and their folders
    for file_path in py_files:
        module_name = Path(file_path).stem
        local_modules.add(module_name)
        module_folders[module_name] = get_file_subfolder(file_path)

    # Extract dependencies for each file
    for file_path in py_files:
        module_name = Path(file_path).stem
        imports = extract_imports(file_path)

        # Filter to only local dependencies
        local_imports = [imp for imp in imports if imp in local_modules]
        dependencies[module_name] = local_imports

    # Get color scheme
    folder_colors = get_subfolder_colors()

    # Save folder information for the frontend
    subfolder_info = {}
    for module, folder in module_folders.items():
        if folder not in subfolder_info:
            subfolder_info[folder] = {
                "color": folder_colors.get(folder, "#F0F0F0"),
                "modules": [],
            }
        subfolder_info[folder]["modules"].append(module)

    # Save subfolder information to JSON file for the frontend
    folder_info_file = dot_file.replace(".dot", "_folders.json")
    with open(folder_info_file, "w") as f:
        json.dump(subfolder_info, f, indent=2)

    # Generate DOT file with colored nodes
    with open(dot_file, "w") as f:
        f.write("digraph Dependencies {\n")
        f.write("    rankdir=LR;\n")
        f.write("    node [shape=box, style=filled];\n")

        # Add all nodes with their folder-specific colors
        for module in local_modules:
            folder = module_folders[module]
            color = folder_colors.get(folder, "#F0F0F0")
            f.write(f'    "{module}" [fillcolor="{color}"];\n')

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

        # Load folder information
        folder_info_file = svg_file.replace(".svg", "_folders.json")
        subfolder_info = {}
        try:
            with open(folder_info_file, "r") as f:
                subfolder_info = json.load(f)
        except FileNotFoundError:
            print("Warning: Could not load folder information")

        # Insert CSS for dimming/highlighting and legend
        style = """<style type="text/css">
            .dimmed { opacity: 0.2; }
            .highlighted { opacity: 1.0; stroke: #ff6600 !important; stroke-width: 2px; }
            .legend { font-family: Arial, sans-serif; font-size: 12px; }
            .legend-rect { stroke: #333; stroke-width: 1; }
            .legend-text { fill: #333; dominant-baseline: middle; }
            .checkbox-container { font-family: Arial, sans-serif; font-size: 11px; }
            .checkbox { cursor: pointer; }
            .checkbox-text { fill: #333; dominant-baseline: middle; cursor: pointer; }
            .unchecked-folder { opacity: 0.2; }
        </style>"""

        # Create the legend SVG content
        legend_content = create_legend_svg(subfolder_info)

        script = f"""<script type=\"text/ecmascript\"><![CDATA[
                var subfolderInfo = {json.dumps(subfolder_info)};
                var checkedFolders = new Set(Object.keys(subfolderInfo));
                
                function resetAll() {{
                    var nodes = document.querySelectorAll('g.node');
                    var edges = document.querySelectorAll('g.edge');
                    nodes.forEach(function(n) {{ n.classList.remove('dimmed','highlighted'); }});
                    edges.forEach(function(e) {{ e.classList.remove('dimmed','highlighted'); }});
                }}
                
                function getNodeTitle(node) {{
                    var title = node.querySelector('title');
                    return title ? title.textContent.trim() : (node.getAttribute('data-title') || node.id || '');
                }}
                
                function getNodeFolder(nodeTitle) {{
                    for (var folder in subfolderInfo) {{
                        if (subfolderInfo[folder].modules.includes(nodeTitle)) {{
                            return folder;
                        }}
                    }}
                    return 'unknown';
                }}
                
                function updateFolderVisibility() {{
                    var nodes = document.querySelectorAll('g.node');
                    var edges = document.querySelectorAll('g.edge');
                    
                    // Update node visibility based on checked folders
                    nodes.forEach(function(n) {{
                        var nodeTitle = getNodeTitle(n);
                        var nodeFolder = getNodeFolder(nodeTitle);
                        if (checkedFolders.has(nodeFolder)) {{
                            n.classList.remove('unchecked-folder');
                        }} else {{
                            n.classList.add('unchecked-folder');
                        }}
                    }});
                    
                    // Update edge visibility - only show if both nodes are in checked folders
                    edges.forEach(function(e) {{
                        var title = e.querySelector('title');
                        if (title) {{
                            var txt = title.textContent;
                            var parts = txt.split('->').map(function(s){{return s.trim();}});
                            if (parts.length === 2) {{
                                var fromFolder = getNodeFolder(parts[0]);
                                var toFolder = getNodeFolder(parts[1]);
                                if (checkedFolders.has(fromFolder) && checkedFolders.has(toFolder)) {{
                                    e.classList.remove('unchecked-folder');
                                }} else {{
                                    e.classList.add('unchecked-folder');
                                }}
                            }}
                        }}
                    }});
                }}
                
                function toggleFolder(folder) {{
                    if (checkedFolders.has(folder)) {{
                        checkedFolders.delete(folder);
                    }} else {{
                        checkedFolders.add(folder);
                    }}
                    updateFolderVisibility();
                    updateCheckboxes();
                }}
                
                function updateCheckboxes() {{
                    Object.keys(subfolderInfo).forEach(function(folder) {{
                        var checkbox = document.getElementById('checkbox-' + folder);
                        if (checkbox) {{
                            checkbox.textContent = checkedFolders.has(folder) ? '☑' : '☐';
                        }}
                    }});
                }}
                
                function findDirectPath(nodeId) {{
                    var connected = new Set([nodeId]);
                    var edges = document.querySelectorAll('g.edge');
                    
                    // Build adjacency lists for outgoing and incoming edges
                    var outgoing = new Map();
                    var incoming = new Map();
                    
                    edges.forEach(function(e) {{
                        var title = e.querySelector('title');
                        if (title) {{
                            var txt = title.textContent;
                            var parts = txt.split('->').map(function(s){{return s.trim();}});
                            if (parts.length === 2) {{
                                var from = parts[0];
                                var to = parts[1];
                                
                                if (!outgoing.has(from)) outgoing.set(from, []);
                                if (!incoming.has(to)) incoming.set(to, []);
                                
                                outgoing.get(from).push(to);
                                incoming.get(to).push(from);
                            }}
                        }}
                    }});
                    
                    // Follow direct path forward (only single outgoing edges)
                    var current = nodeId;
                    while (outgoing.has(current) && outgoing.get(current).length === 1) {{
                        var next = outgoing.get(current)[0];
                        connected.add(next);
                        current = next;
                    }}
                    
                    // Follow direct path backward (only single incoming edges)
                    current = nodeId;
                    while (incoming.has(current) && incoming.get(current).length === 1) {{
                        var prev = incoming.get(current)[0];
                        connected.add(prev);
                        current = prev;
                    }}
                    
                    return connected;
                }}
                
                function highlightConnections(nodeId) {{
                    resetAll();
                    var nodes = document.querySelectorAll('g.node');
                    var edges = document.querySelectorAll('g.edge');
                    var connected = findDirectPath(nodeId);
                    
                    // Highlight edges between connected nodes
                    edges.forEach(function(e) {{
                        var title = e.querySelector('title');
                        if (title) {{
                            var txt = title.textContent;
                            var parts = txt.split('->').map(function(s){{return s.trim();}});
                            if (parts.length === 2 && connected.has(parts[0]) && connected.has(parts[1])) {{
                                e.classList.add('highlighted');
                            }} else {{
                                e.classList.add('dimmed');
                            }}
                        }} else {{
                            e.classList.add('dimmed');
                        }}
                    }});
                    
                    // Highlight connected nodes
                    nodes.forEach(function(n) {{
                        var ntitle = getNodeTitle(n);
                        if (connected.has(ntitle)) {{
                            n.classList.add('highlighted');
                        }} else {{
                            n.classList.add('dimmed');
                        }}
                    }});
                }}
                
                window.addEventListener('DOMContentLoaded', function() {{
                    var nodes = document.querySelectorAll('g.node');
                    nodes.forEach(function(n) {{
                        var ntitle = getNodeTitle(n);
                        n.style.cursor = 'pointer';
                        n.addEventListener('click', function() {{ highlightConnections(ntitle); }});
                    }});
                    
                    document.documentElement.addEventListener('click', function(e) {{
                        if (e.target.closest('g.node') == null && e.target.closest('.checkbox') == null) {{
                            resetAll();
                        }}
                    }});
                    
                    // Setup checkbox event listeners
                    Object.keys(subfolderInfo).forEach(function(folder) {{
                        var checkbox = document.getElementById('checkbox-' + folder);
                        var checkboxText = document.getElementById('checkbox-text-' + folder);
                        if (checkbox && checkboxText) {{
                            [checkbox, checkboxText].forEach(function(element) {{
                                element.addEventListener('click', function() {{
                                    toggleFolder(folder);
                                }});
                            }});
                        }}
                    }});
                    
                    updateCheckboxes();
                }});
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
        def add_node_ids(match):
            label = re.search(r"<title>(.*?)</title>", match.group(0))
            if label:
                node_id = label.group(1)
                return match.group(0).replace("<g ", f'<g id="{node_id}" ')
            return match.group(0)

        svg = re.sub(r'<g class="node"[\s\S]*?</g>', add_node_ids, svg)

        # Insert legend after the main graph group to ensure it's positioned correctly
        graph_group_pattern = r'(<g id="graph0" class="graph"[^>]*>)'
        graph_match = re.search(graph_group_pattern, svg)
        if graph_match:
            insert_index = graph_match.end()
            svg = svg[:insert_index] + legend_content + svg[insert_index:]
        else:
            print("Warning: Could not find main graph group for legend insertion")

        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg)
    except Exception as e:
        print(f"Failed to inject interactivity: {e}")


def create_legend_svg(subfolder_info):
    """Create SVG content for the legend and checkbox interface."""
    if not subfolder_info:
        return ""

    legend_items = []
    y_offset = 20

    # Legend title
    legend_items.append(
        f'<text x="10" y="{y_offset}" class="legend-text" style="font-weight: bold;">Subfolder Legend</text>'
    )
    y_offset += 25

    # Legend items with checkboxes
    for folder, info in subfolder_info.items():
        color = info["color"]
        module_count = len(info["modules"])

        # Checkbox
        legend_items.append(
            f'<text id="checkbox-{folder}" x="10" y="{y_offset}" class="checkbox-text checkbox" style="font-size: 14px;">☑</text>'
        )

        # Color rectangle
        legend_items.append(
            f'<rect x="25" y="{y_offset-8}" width="15" height="12" fill="{color}" class="legend-rect" />'
        )

        # Folder name and count
        legend_items.append(
            f'<text id="checkbox-text-{folder}" x="45" y="{y_offset}" '
            f'class="legend-text checkbox">{folder} ({module_count} modules)</text>'
        )

        y_offset += 18

    # Add "Select All Connected" instruction
    y_offset += 10
    legend_items.append(
        f'<text x="10" y="{y_offset}" class="legend-text" '
        f'style="font-size: 10px; fill: #666;">'
        f"Click any node to highlight direct path connections</text>"
    )

    # Wrap in a group with background - positioned in graph coordinates
    legend_height = y_offset + 10
    legend_content = f"""
    <g class="legend" transform="translate(-4, -2850)">
        <rect x="0" y="0" width="250" height="{legend_height}" fill="white" stroke="#ccc" stroke-width="1" rx="5" opacity="0.95"/>
        {''.join(legend_items)}
    </g>
    """

    return legend_content


if __name__ == "__main__":
    main()
