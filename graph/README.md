# Enhanced Dependency Graph System (graph/)

## Overview
This directory contains the complete modular implementation of the Enhanced Dependency Graph System for Python projects. It provides deep architectural analysis and interactive visualization of code dependencies, designed for maintainability, extensibility, and clarity.

## Directory Structure
```
graph/
├── enhanced_dependency_graph_modular.py   # Main entry point
├── graph_modules/                        # Modular analysis and visualization components
│   ├── __init__.py
│   ├── dependency_analyzer.py
│   ├── graph_styles.py
│   ├── hierarchical_layout.py
│   ├── force_directed_layout.py
│   ├── graph_visualization.py
│   ├── graph_controls.py
│   └── html_generator.py
├── graph_output/                         # Generated HTML and JSON visualizations
│   ├── enhanced_dependency_graph.html
│   └── enhanced_graph_data.json
```

## How the App Works: Path & Flow

1. **enhanced_dependency_graph_modular.py** (Entry Point)
   - Imports and calls `main()` from `graph_modules`.
   - Orchestrates the entire analysis and visualization pipeline.

2. **graph_modules/__init__.py**
   - Exposes the `main()` function and key analysis/visualization utilities.
   - Allows easy import and modular access.

3. **main()** (in `html_generator.py` via `__init__.py`)
   - Instantiates `EnhancedDependencyAnalyzer`.
   - Runs full project analysis (auto-detects root, excludes `graph/`).
   - Passes results to HTML generator for visualization.
   - Saves output to `graph_output/`.

4. **dependency_analyzer.py**
   - Scans all Python files (except `graph/`).
   - Builds dependency graph, calculates importance, detects cycles, etc.
   - Outputs structured graph data for visualization.

5. **html_generator.py**
   - Assembles the interactive HTML visualization using D3.js and custom styles.
   - Integrates all modules for layout, controls, and rendering.
   - Saves both HTML and JSON data to `graph_output/`.

6. **Other Modules**
   - Each module provides a focused capability (see below).
   - All are imported and used by `html_generator.py`.

## Module Summaries

### enhanced_dependency_graph_modular.py
- **Purpose:** Main entry point. Sets up and runs the modular dependency graph system.
- **Key Actions:** Imports `main` from `graph_modules`, triggers analysis and visualization.

### graph_modules/__init__.py
- **Purpose:** Package initializer. Exposes main analysis and visualization functions.
- **Key Actions:** Imports `EnhancedDependencyAnalyzer`, `generate_enhanced_html_visualization`, and `main`.

### graph_modules/dependency_analyzer.py
- **Purpose:** Core dependency analysis logic.
- **Key Features:**
  - Scans all Python files (except excluded folders)
  - Maps import relationships (internal/external)
  - Calculates module importance (PageRank-style)
  - Detects circular dependencies
  - Outputs nodes, edges, statistics, clusters

### graph_modules/graph_styles.py
- **Purpose:** CSS styling for the visualization.
- **Key Features:**
  - Provides color schemes, layout styles, and visual cues for the graph
  - Ensures a professional, readable appearance

### graph_modules/hierarchical_layout.py
- **Purpose:** Hierarchical layout algorithms.
- **Key Features:**
  - Arranges nodes based on dependency depth and importance
  - Supports tree-like and layered visualizations

### graph_modules/force_directed_layout.py
- **Purpose:** Force-directed layout algorithms.
- **Key Features:**
  - Uses physics simulation to position nodes
  - Allows dynamic, interactive graph layouts

### graph_modules/graph_visualization.py
- **Purpose:** Core D3.js rendering and visualization utilities.
- **Key Features:**
  - Renders nodes, edges, and clusters
  - Integrates with D3.js for interactive features

### graph_modules/graph_controls.py
- **Purpose:** UI controls and event handling.
- **Key Features:**
  - Provides filtering, toggling, and user interaction controls
  - Handles events for graph navigation and exploration

### graph_modules/html_generator.py
- **Purpose:** HTML template assembly and main orchestration.
- **Key Features:**
  - Combines all modules into a complete HTML visualization
  - Integrates styles, layouts, controls, and data
  - Saves output files to `graph_output/`

## Output
- **graph_output/enhanced_dependency_graph.html**: Interactive HTML visualization of the codebase.
- **graph_output/enhanced_graph_data.json**: Raw graph data (nodes, edges, statistics) for further analysis or integration.

## Usage
From the `graph/` directory:
```bash
python enhanced_dependency_graph_modular.py
```
Or from the project root:
```bash
python graph/enhanced_dependency_graph_modular.py
```

## Notes
- The system auto-detects its location and always analyzes the parent project directory, excluding the `graph/` folder itself.
- All output is saved to `graph/graph_output/`.
- Designed for extensibility: add new modules to `graph_modules/` as needed.

---
For further details, see the docstrings in each module or the generated HTML visualization.
