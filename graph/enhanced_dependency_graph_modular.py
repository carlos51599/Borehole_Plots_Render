#!/usr/bin/env python3
"""
Enhanced Dependency Graph - Modular Implementation
=================================================

Main entry point for the modularized enhanced dependency graph system.
This replaces the monolithic enhanced_dependency_graph.py with a clean,
maintainable modular architecture.

Usage:
    python enhanced_dependency_graph_modular.py

The original enhanced_dependency_graph.py has been split into focused modules:
- dependency_analyzer.py: Core analysis logic
- graph_styles.py: CSS styling
- hierarchical_layout.py: Hierarchical layout algorithms
- force_directed_layout.py: Force-directed layout algorithms
- graph_visualization.py: Core D3.js rendering
- graph_controls.py: UI controls and event handling
- html_generator.py: HTML template assembly

Author: Enhanced Dependency Graph System
Date: 2025-07-22
"""

from graph_modules import main

if __name__ == "__main__":
    main()
