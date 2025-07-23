"""
HTML Generator Module
====================

HTML template assembly and main generation function.
Combines all modules into the complete visualization HTML.
"""

import json
from pathlib import Path
from typing import Dict, Any

from .graph_styles import get_graph_styles
from .graph_visualization import get_graph_visualization_js
from .hierarchical_layout import get_hierarchical_layout_js
from .force_directed_layout import get_force_directed_layout_js
from .graph_controls import get_graph_controls_js


def get_html_head() -> str:
    """
    Get HTML head section with meta tags and external dependencies.

    Returns:
        str: HTML head section
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Dependency Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>{styles}</style>
</head>"""


def get_html_body() -> str:
    """
    Get HTML body structure with controls and graph container.

    Returns:
        str: HTML body structure
    """
    return """<body>
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
                    <label for="predecessors-filter" class="filter-label">
                        📥 Max Predecessors (incoming):
                    </label>
                    <input type="range" id="predecessors-filter" min="0" max="20" value="20" style="width: 100%; margin-bottom: 5px;">
                    <div class="filter-value">
                        <span id="predecessors-filter-value">20</span> predecessors
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label for="successors-filter" class="filter-label">
                        📤 Max Successors (outgoing):
                    </label>
                    <input type="range" id="successors-filter" min="0" max="20" value="20" style="width: 100%; margin-bottom: 5px;">
                    <div class="filter-value">
                        <span id="successors-filter-value">20</span> successors
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label for="size-filter" class="filter-label">
                        📄 Max File Size (KB):
                    </label>
                    <input type="range" id="size-filter" min="0" max="100" value="100" style="width: 100%; margin-bottom: 5px;">
                    <div class="filter-value">
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
            <div class="theme-toggle" onclick="toggleTheme()">
                <span class="theme-icon">🌙</span>
                <span class="theme-text">Dark</span>
            </div>
            <svg id="graph"></svg>
            <div id="tooltip" class="tooltip" aria-hidden="true"></div>
        </div>
    </div>

    <script>
        // Enhanced graph data with complete directory inclusion
        const graphData = {graph_data_json};

        {visualization_js}
        {hierarchical_layout_js}
        {force_directed_layout_js}
        {controls_js}
        
        // Initialize on load
        document.addEventListener("DOMContentLoaded", function() {{
            initializeTheme();
            initializeEnhancedVisualization();
        }});
    </script>
</body>
</html>"""


def generate_enhanced_html_visualization(graph_data: Dict[str, Any]) -> str:
    """
    Generate complete HTML visualization by assembling all modules.

    Args:
        graph_data: Complete graph data dictionary from dependency analyzer

    Returns:
        str: Complete HTML document with embedded visualization
    """
    print("🎨 Assembling modular HTML visualization...")

    # Get all component pieces
    styles = get_graph_styles()
    visualization_js = get_graph_visualization_js()
    hierarchical_layout_js = get_hierarchical_layout_js()
    force_directed_layout_js = get_force_directed_layout_js()
    controls_js = get_graph_controls_js()

    # Get HTML structure
    html_head = get_html_head()
    html_body = get_html_body()

    # Assemble complete HTML
    complete_html = html_head.format(styles=styles) + html_body.format(
        graph_data_json=json.dumps(graph_data, indent=2),
        visualization_js=visualization_js,
        hierarchical_layout_js=hierarchical_layout_js,
        force_directed_layout_js=force_directed_layout_js,
        controls_js=controls_js,
    )

    print("✅ Modular HTML visualization assembled successfully")
    return complete_html


def main():
    """Generate enhanced dependency graph with modular architecture."""
    from .dependency_analyzer import EnhancedDependencyAnalyzer

    print("🚀 ENHANCED DEPENDENCY GRAPH - MODULAR IMPLEMENTATION")
    print("=" * 60)

    # Create enhanced analyzer
    analyzer = EnhancedDependencyAnalyzer()

    # Analyze project with all directories
    print("📊 Analyzing complete project structure...")
    graph_data = analyzer.analyze_project()

    # Generate enhanced HTML visualization
    print("🎨 Generating modular visualization...")
    html_content = generate_enhanced_html_visualization(graph_data)

    # Save files - determine if we're in dependency_graph folder and adjust path accordingly
    current_dir = Path.cwd()
    if (
        current_dir.name == "dependency_graph"
        or (current_dir / "graph_modules").exists()
    ):
        output_dir = Path(
            "graph_output"
        )  # We're in dependency_graph folder, use relative path
    else:
        output_dir = (
            Path("dependency_graph") / "graph_output"
        )  # We're in root, use dependency_graph subfolder
    output_dir.mkdir(exist_ok=True)

    # Save enhanced graph data
    with open(output_dir / "enhanced_graph_data.json", "w") as f:
        json.dump(graph_data, f, indent=2)

    # Save enhanced HTML
    with open(
        output_dir / "enhanced_dependency_graph.html", "w", encoding="utf-8"
    ) as f:
        f.write(html_content)

    print("✅ MODULAR DEPENDENCY GRAPH COMPLETE!")
    print("=" * 50)
    print("📊 Analysis Results:")
    stats = graph_data["statistics"]
    print(f"   - Total files analyzed: {stats['total_files']}")
    print(f"   - Total dependencies: {stats['total_dependencies']}")
    print(f"   - Cross-folder dependencies: {stats['cross_folder_dependencies']}")
    print(f"   - Test files included: {stats['test_files']}")
    print(f"   - Directories included: {stats['folders']}")

    print("\n🏗️ Modular Architecture:")
    print("   ✅ dependency_analyzer.py - Core analysis logic")
    print("   ✅ graph_styles.py - CSS styling definitions")
    print("   ✅ hierarchical_layout.py - Hierarchical layout algorithms")
    print("   ✅ force_directed_layout.py - Force-directed layout algorithms")
    print("   ✅ graph_visualization.py - Core D3.js rendering")
    print("   ✅ graph_controls.py - UI controls and event handling")
    print("   ✅ html_generator.py - HTML template assembly")

    print("\n🎯 Key Features:")
    print("   ✅ Modular, maintainable codebase")
    print("   ✅ Easy to extend and debug individual components")
    print("   ✅ Clean separation of concerns")
    print("   ✅ Complete directory inclusion (including tests, assets, reports)")
    print("   ✅ Enhanced hierarchical layout with importance-based positioning")
    print("   ✅ Force-directed layout toggle with D3.js simulation")
    print("   ✅ Smooth layout transitions and animations")
    print("   ✅ Advanced filtering and interactive controls")

    print("\n📄 Generated Files:")
    print("   - Enhanced graph data: graph_output/enhanced_graph_data.json")
    print("   - Enhanced visualization: graph_output/enhanced_dependency_graph.html")
    print("\n📁 Modular Components:")
    print("   - graph_modules/ - All modular components")
    print("   - graph_modules/__init__.py - Package initialization")
    print("   - graph_modules/dependency_analyzer.py - Analysis logic")
    print("   - graph_modules/graph_styles.py - CSS styling")
    print("   - graph_modules/hierarchical_layout.py - Hierarchical layouts")
    print("   - graph_modules/force_directed_layout.py - Force layouts")
    print("   - graph_modules/graph_visualization.py - Core visualization")
    print("   - graph_modules/graph_controls.py - UI controls")
    print("   - graph_modules/html_generator.py - HTML generation")

    return graph_data
