"""
Graph Modules Package
====================

Modular components for enhanced dependency graph visualization.

Modules:
- dependency_analyzer: Core dependency analysis functionality
- graph_styles: CSS styling for the visualization
- graph_controls: JavaScript UI controls and event handling
- hierarchical_layout: Hierarchical layout algorithms
- force_directed_layout: Force-directed layout algorithms
- graph_visualization: Core D3.js rendering and utilities
- html_generator: HTML template assembly and generation
"""

__version__ = "1.0.0"
__author__ = "Enhanced Dependency Graph System"

# Import main components for easy access
from .dependency_analyzer import EnhancedDependencyAnalyzer
from .html_generator import generate_enhanced_html_visualization, main

__all__ = ["EnhancedDependencyAnalyzer", "generate_enhanced_html_visualization", "main"]
