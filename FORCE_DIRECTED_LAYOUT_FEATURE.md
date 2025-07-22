# Force-Directed Layout Feature

## Overview
The enhanced dependency graph visualization now includes a **Force-Directed Layout Toggle** that allows users to switch between two different layout modes:

1. **Hierarchical Layout** - Traditional dependency-aware positioning with layers
2. **Force-Directed Layout** - Dynamic physics-based node positioning using D3.js force simulation

## Key Features

### 🎛️ Layout Toggle Control
- Located in the "Layout Control" section of the control panel
- Visual toggle switch with clear labels:
  - 📐 Hierarchical (left position)
  - 🌐 Force-Directed (right position)
- Real-time layout indicator showing current mode
- Keyboard accessible (Tab navigation, Enter/Space to toggle)

### 🌐 Force-Directed Layout Benefits
- **Natural clustering** - Related modules group together organically
- **Reduced edge crossings** - Physics simulation minimizes visual clutter
- **Dynamic interactions** - Drag nodes to reorganize the graph
- **Importance-based forces** - High-importance nodes have stronger influence
- **Adaptive distances** - Link distances scale with node importance

### 📐 Hierarchical Layout Benefits
- **Clear dependency flow** - Left-to-right progression shows dependency direction
- **Layer-based organization** - Nodes organized by dependency depth
- **Predictable positioning** - Consistent layout for repeated viewing
- **Easy traceability** - Follow dependency chains visually

## Technical Implementation

### Force Simulation Configuration
```javascript
// Key force simulation parameters:
- Link distance: 150px + importance bonus
- Charge strength: -800 * importance multiplier
- Collision detection: Node width/height + 10px padding
- Center force: Keeps graph centered
- Position constraints: Prevents nodes from drifting off-screen
```

### Smooth Transitions
- **Hierarchical → Force**: Gradual transition with physics warm-up
- **Force → Hierarchical**: Animated return to calculated positions
- **Duration**: 1-second smooth transitions with easing
- **Preservation**: All visual styles, colors, and interactions maintained

### Interactive Features Preserved
- ✅ Node highlighting and path tracing
- ✅ Tooltip information on hover
- ✅ Directory visibility toggles
- ✅ Advanced filtering controls
- ✅ Drag-and-drop node positioning
- ✅ Zoom and pan capabilities

## Usage Instructions

1. **Open the visualization** - Load the enhanced_dependency_graph.html file
2. **Locate the toggle** - Find "Layout Control" in the left control panel
3. **Switch layouts** - Click the toggle switch or the entire control area
4. **Observe transition** - Watch smooth animation between layout modes
5. **Interact freely** - All features work in both layout modes

## Performance Considerations

### Force-Directed Layout
- **Initial positioning**: ~2-3 seconds for stabilization
- **Interactive dragging**: Real-time physics response
- **Node count**: Optimized for up to 100+ nodes
- **Memory usage**: Minimal impact with D3.js simulation

### Layout Switching
- **Switch time**: <1 second transition
- **State preservation**: All filters and selections maintained
- **Smooth performance**: No visual glitches or layout jumps

## Browser Compatibility
- ✅ Modern Chrome (recommended)
- ✅ Firefox 90+
- ✅ Safari 14+
- ✅ Edge 90+

## Accessibility Features
- **Keyboard navigation**: Tab to layout toggle, Enter/Space to activate
- **Screen reader support**: Proper ARIA labels and roles
- **Visual indicators**: Clear current layout status
- **High contrast**: Works well with accessibility settings

## Future Enhancements
- **Custom force parameters**: User-adjustable simulation settings
- **Layout presets**: Save and load preferred layout configurations
- **Animation speed**: Adjustable transition timing
- **Layout memory**: Remember user's preferred layout mode

---

*This feature enhances the dependency graph with modern, interactive layout options while maintaining all existing functionality and visual fidelity.*
