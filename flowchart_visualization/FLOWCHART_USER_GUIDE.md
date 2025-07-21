# 🗺️ Interactive Codebase Flowchart - User Guide

## Quick Start

1. **Launch the Flowchart**
   ```bash
   python flowchart_server.py
   ```

2. **Open Browser**
   - Navigate to `http://127.0.0.1:5000`
   - Or wait for auto-launch

3. **Explore Your Codebase**
   - Click nodes to see dependencies
   - Hover for detailed information
   - Use search and filters to navigate

## 🎯 Interface Overview

### Main Components

```
┌─────────────────────────────────────┐
│ 🏠 Header & Title                    │
├─────────────────────────────────────┤
│ 🔍 Search | 📁 Filter | 🎨 Layout   │
├─────────────────────────────────────┤
│                                     │
│     📊 Interactive Diagram          │
│                                     │
│           🔗 Nodes & Links          │
│                                     │
├─────────────────────────────────────┤
│ 📍 Breadcrumb     🎯 Legend         │
└─────────────────────────────────────┘
```

### Control Panel

- **🔍 Search Box**: Find files, functions, or content
- **📁 Filter Dropdown**: Show specific file types
- **🎨 Layout Selector**: Change visualization style
- **🔄 Reset Button**: Return to overview
- **📥 Export Button**: Save diagram as image
- **❓ Help Button**: Show feature guide
- **🌙 Theme Toggle**: Switch dark/light mode

## 🚀 Core Features

### 1. Node Interaction

#### Clicking Nodes
- **Single Click**: Select and highlight dependencies
- **Double Click**: Focus and zoom to specific file
- **Hover**: Show detailed tooltip information

#### Node Information
Each node displays:
- **File name** and path
- **Code metrics** (lines, complexity)
- **Function count** and class count
- **Import dependencies**
- **Git information** (if available)

### 2. Navigation

#### Zoom & Pan
- **Mouse Wheel**: Zoom in/out
- **Click & Drag**: Pan around diagram
- **Double-click Node**: Zoom to focus
- **Reset Button**: Return to overview

#### Search & Filter
- **Real-time Search**: Type to filter instantly
- **File Type Filter**: Show only specific categories
- **Clear Filters**: Reset to show all files

### 3. Visual Elements

#### Node Colors
- 🔵 **Blue**: Main application files (app.py)
- 🟢 **Green**: Core modules and libraries
- 🟠 **Orange**: Utility and helper files
- 🟣 **Pink**: Test files and test utilities
- 🟪 **Purple**: Configuration and constants

#### Node Sizes
- **Small (5-10px)**: Simple files with low complexity
- **Medium (10-20px)**: Standard modules
- **Large (20-25px)**: Complex files with high cyclomatic complexity

#### Connection Lines
- **Thin Gray**: Standard import dependencies
- **Thick Orange**: Highlighted when node selected
- **Opacity**: Indicates dependency strength

## 📋 Step-by-Step Tutorial

### Getting Started

1. **Initial View**
   ```
   When you first load the flowchart, you'll see:
   ✓ All Python files as colored nodes
   ✓ Import relationships as connecting lines
   ✓ Force-directed layout spreading nodes naturally
   ```

2. **Understanding the Layout**
   ```
   The diagram automatically arranges files based on:
   → Dependencies (connected files stay close)
   → File types (similar types cluster together)
   → Complexity (important files get more space)
   ```

### Exploring Dependencies

1. **Select a File**
   ```
   Click on 'app.py' (the blue main node)
   ➜ Node becomes highlighted with yellow border
   ➜ All dependencies turn orange/red
   ➜ Breadcrumb shows current selection
   ```

2. **Follow Dependencies**
   ```
   Click on any highlighted dependency
   ➜ Shows that file's dependencies
   ➜ Builds a dependency chain
   ➜ Breadcrumb tracks your path
   ```

3. **Clear Selection**
   ```
   Click empty space or press Escape
   ➜ Returns to neutral view
   ➜ All highlighting removed
   ```

### Using Search

1. **Find Specific Files**
   ```
   Type in search box: "config"
   ➜ Only shows files with "config" in name
   ➜ Useful for large codebases
   ```

2. **Search Functions**
   ```
   Type: "plot_section"
   ➜ Shows files containing that function
   ➜ Helps find where functionality is implemented
   ```

3. **Content Search**
   ```
   Type: "matplotlib"
   ➜ Shows files that import matplotlib
   ➜ Find files using specific libraries
   ```

### Filtering by Type

1. **Show Only Tests**
   ```
   Filter dropdown ➜ "Test Files"
   ➜ Displays only test_*.py files
   ➜ See test coverage and structure
   ```

2. **Core Modules Only**
   ```
   Filter dropdown ➜ "Core Modules"
   ➜ Shows main business logic files
   ➜ Understand core architecture
   ```

3. **Configuration Files**
   ```
   Filter dropdown ➜ "Configuration"
   ➜ Shows config.py, constants, settings
   ➜ Find configuration dependencies
   ```

### Layout Options

1. **Force Directed (Default)**
   ```
   Natural physics-based layout
   ✓ Files cluster by relationships
   ✓ Connected files stay close
   ✓ Good for exploring connections
   ```

2. **Hierarchical**
   ```
   Organized in vertical layers by type
   ✓ Main files at left
   ✓ Tests at right
   ✓ Clear type separation
   ```

3. **Radial**
   ```
   Circular arrangement from center
   ✓ Central hub for main files
   ✓ Dependencies radiate outward
   ✓ Good for large projects
   ```

## 🔧 Advanced Features

### Keyboard Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Space` | Reset View | Return to overview |
| `F` | Focus Mode | Zoom to selected node |
| `H` | Help | Toggle help overlay |
| `T` | Theme | Switch dark/light theme |
| `Escape` | Clear | Remove current selection |

### Tooltip Information

Hover over any node to see:
- **📄 Lines**: Total lines of code
- **🔧 Complexity**: Cyclomatic complexity score
- **⚙️ Functions**: Number of functions defined
- **🏛️ Classes**: Number of classes defined
- **📦 Imports**: List of imported modules
- **🔗 Dependencies**: Files this file depends on

### Export Options

1. **PNG Export**
   ```
   Click "📥 Export" button
   ➜ Saves current view as PNG image
   ➜ Useful for documentation and presentations
   ```

2. **API Access**
   ```
   GET /api/data
   ➜ Complete analysis data as JSON
   ➜ Integrate with other tools
   ```

## 🎨 Customization

### Theme Switching
- **Dark Theme**: Default, good for development
- **Light Theme**: Better for presentations and printing
- Toggle with button or `T` key

### View Preferences
- **Node Labels**: Can be toggled on/off
- **Dependency Strength**: Adjustable line thickness
- **Animation Speed**: Configurable transition timing

## 🐛 Troubleshooting

### Common Issues

1. **Empty or Missing Nodes**
   ```
   Problem: No files showing
   Solution: Run analysis first
   Command: python generate_flowchart_data.py
   ```

2. **Slow Performance**
   ```
   Problem: Laggy interactions
   Solutions:
   → Filter to fewer files
   → Use hierarchical layout
   → Close browser dev tools
   ```

3. **Missing Dependencies**
   ```
   Problem: No connection lines
   Solutions:
   → Check if analysis found imports
   → Verify file paths are correct
   → Regenerate analysis data
   ```

### Browser Compatibility

✅ **Supported Browsers**
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

❌ **Known Issues**
- Internet Explorer (not supported)
- Very old mobile browsers

## 💡 Tips & Best Practices

### For Large Codebases (100+ files)

1. **Start with Filters**
   ```
   → Begin with "Main Files" filter
   → Add specific file types gradually
   → Use search for targeted exploration
   ```

2. **Use Hierarchical Layout**
   ```
   → Better organization for many files
   → Clearer type separation
   → Easier to find specific categories
   ```

3. **Focus on Key Files**
   ```
   → Double-click main entry points
   → Follow dependency chains
   → Use breadcrumbs to track path
   ```

### For Understanding Architecture

1. **Start with Main Files**
   ```
   → Look for app.py or main.py
   → Click to see immediate dependencies
   → Follow the dependency tree
   ```

2. **Identify Core Modules**
   ```
   → Look for nodes with many connections
   → These are likely central components
   → Check their complexity scores
   ```

3. **Find Test Coverage**
   ```
   → Filter to "Test Files"
   → See which modules have tests
   → Identify untested components
   ```

### For Code Reviews

1. **Find Complex Files**
   ```
   → Look for large nodes (high complexity)
   → Check if they have many dependencies
   → Consider refactoring opportunities
   ```

2. **Identify Hotspots**
   ```
   → Files with many incoming dependencies
   → Central nodes in the graph
   → High-impact change areas
   ```

3. **Check Isolation**
   ```
   → Look for disconnected components
   → Identify utility modules
   → Find potential extraction candidates
   ```

## 📚 Understanding the Data

### Complexity Metrics
- **Low (1-10)**: Simple scripts, configurations
- **Medium (10-30)**: Standard modules with business logic
- **High (30+)**: Complex algorithms, main orchestration files

### File Categories
- **Main**: Entry points and primary application files
- **Core**: Business logic and main functionality
- **Utility**: Helper functions and common operations
- **Test**: Testing files and test utilities
- **Config**: Configuration, constants, and settings
- **Model**: Data structures and domain models

### Dependency Types
- **Import Dependencies**: Direct Python imports
- **Function Calls**: Inter-module function usage
- **Class Inheritance**: Object-oriented relationships

---

## 🎯 Quick Reference

### Essential Actions
1. **🔍 Search**: Type to find files
2. **👆 Click**: Select and highlight
3. **👆👆 Double-click**: Focus and zoom
4. **🖱️ Drag**: Pan around diagram
5. **🎡 Scroll**: Zoom in/out
6. **📱 Hover**: See details

### Key Shortcuts
- `Space` = Reset | `F` = Focus | `T` = Theme | `H` = Help

### Visual Guide
- **Blue** = Main | **Green** = Core | **Orange** = Utils | **Pink** = Tests | **Purple** = Config
- **Size** = Complexity | **Lines** = Dependencies

---

**Happy Exploring! 🚀**

Use this flowchart to understand your codebase structure, find dependencies, and navigate complex projects with ease.
