# Enhanced Dependency Graph Usage Guide

## Overview
The enhanced dependency graph provides an interactive visualization of your Python project's module dependencies with powerful features including **dual layout modes**, advanced filtering, and comprehensive interaction capabilities.

## 🆕 NEW: Force-Directed Layout Toggle

### Layout Modes
The visualization now supports **two distinct layout modes**:

1. **📐 Hierarchical Layout** (Default)
   - Traditional left-to-right dependency flow
   - Nodes organized in layers by dependency depth
   - Clear visual hierarchy and traceability
   - Optimal for understanding dependency chains

2. **🌐 Force-Directed Layout** (NEW!)
   - Physics-based dynamic positioning using D3.js simulation
   - Natural clustering of related modules
   - Reduced edge crossings and visual clutter
   - Interactive drag-and-drop positioning
   - Importance-weighted node positioning

### How to Switch Layouts
- **Location**: Find the "🎛️ Layout Control" section in the control panel
- **Toggle**: Click the switch or anywhere in the control area
- **Transition**: Smooth 1-second animated transition between modes
- **Indicator**: Current layout mode is clearly displayed

## Features

### 1. Basic Node Interaction
- **Click any node** to highlight its connections
- **Click the same node again** to deselect and reset the view
- **Click outside** any node to reset the view

### 2. Highlighting Modes

#### Direct Connections (Default)
- When you click a node, only its direct dependencies are highlighted
- **Orange**: The selected node
- **Blue**: Directly connected nodes
- **Dimmed**: All other nodes and edges

#### Distant Highlighting (Advanced)
- Enable "Highlight all reachable modules" checkbox
- **Orange**: The selected node
- **Green**: Predecessors (modules that can reach the selected node)
- **Red**: Successors (modules reachable from the selected node)
- **Dimmed**: Unconnected modules

### 3. Search Functionality
- Use the search box to quickly find and highlight a specific module
- Type part of a module name to automatically select and highlight it
- Clear the search box to reset the view

### 4. Folder Filtering
- **Filter by Folder** section shows checkboxes for each subfolder in your project
- Uncheck a folder to hide all modules from that folder
- Hidden modules and their connections are completely removed from view
- Useful for focusing on specific parts of your codebase

## Usage Examples

### Find Dependencies of a Specific Module
1. Type the module name in the search box, or click the module node
2. The visualization will show all direct dependencies

### Analyze Impact of Changes
1. Click a module you're planning to modify
2. Enable "Highlight all reachable modules"
3. **Green nodes** show what might break if you change this module
4. **Red nodes** show what this module depends on

### Focus on a Subsystem
1. In the "Filter by Folder" section, uncheck folders you're not interested in
2. The graph will show only the relevant modules and their connections

### Explore Module Relationships
1. Click different nodes to see how modules are interconnected
2. Use the distant highlighting to understand the full dependency chain

### 🌐 Force-Directed Layout Specific Features
- **Natural Clustering**: Related modules automatically group together
- **Interactive Physics**: Drag nodes to reorganize the graph in real-time
- **Importance-Based Forces**: High-importance nodes have stronger gravitational pull
- **Collision Detection**: Nodes automatically avoid overlapping
- **Dynamic Stabilization**: Graph settles into optimal positions over 2-3 seconds

### 📐 Hierarchical Layout Benefits
- **Dependency Flow**: Clear left-to-right progression shows import direction
- **Layer Organization**: Modules organized by dependency depth
- **Consistent Positioning**: Predictable layout for repeated analysis
- **Easy Traceability**: Follow dependency chains visually from left to right

## Layout Comparison

| Feature | Hierarchical | Force-Directed |
|---------|-------------|----------------|
| **Dependency Direction** | ✅ Clear (left→right) | ⚡ Dynamic grouping |
| **Visual Clustering** | ⚡ Layer-based | ✅ Natural clusters |
| **Interactive Positioning** | ⚡ Drag only | ✅ Physics simulation |
| **Edge Crossings** | ⚡ Moderate | ✅ Minimized |
| **Consistency** | ✅ Predictable | ⚡ Dynamic |
| **Learning Curve** | ✅ Intuitive | ⚡ Requires exploration |

*Recommendation: Start with **Hierarchical** for analysis, switch to **Force-Directed** for exploration and presentation.*

## Technical Details

- The graph is generated from Python import statements
- Only local project modules are included (external libraries are filtered out)
- Folder information is automatically extracted from file paths
- The visualization is fully client-side JavaScript for fast interaction

## Tips

- For large projects, use folder filtering to reduce visual complexity
- The search function is case-insensitive and supports partial matches
- Distant highlighting helps identify potential circular dependencies
- The graph layout is generated by Graphviz for optimal visual clarity
