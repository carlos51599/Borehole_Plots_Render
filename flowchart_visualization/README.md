# Enhanced Interactive Flowchart Visualization

This folder contains all files related to the enhanced browser-based interactive flowchart visualization for the Borehole Plots Render project.

## 🚀 Features

### Plot Area Sizing
- **Full-width design**: The plot/diagram area maximizes horizontal space across the entire page
- **Responsive layout**: Automatically adapts to different screen sizes and orientations
- **Modern styling**: Clean, professional appearance with optimized space utilization

### Function Details View
- **Complete function visibility**: Every function in the codebase is displayed as an individual node
- **Interactive function graph**: Clear visualization of function call relationships
- **Dual view modes**: Switch between file overview and detailed function view

### Advanced Relationship Highlighting
- **Color-coded relationships**: 
  - 🔵 **Blue lines**: Dependencies (what this file/function imports or calls)
  - 🟠 **Orange lines**: Dependents (what imports or calls this file/function)
- **Interactive highlighting**: Click any node to highlight its relationships
- **Visual distinction**: Clear, easy-to-interpret relationship indicators

### Enhanced Interactivity
- **Real-time search**: Find files or functions instantly
- **Smart filtering**: Filter by file type (main, tests, utilities, config)
- **Multiple layouts**: Force-directed, hierarchical, and radial arrangements
- **Keyboard shortcuts**: Space to reset, F to focus, H for help, Escape to clear
- **Export functionality**: Save diagrams as SVG files

## 📁 Files

### Core Files
- **`enhanced_flowchart.html`**: Main HTML file with full-width layout and enhanced UI
- **`enhanced_flowchart.js`**: JavaScript implementation with all enhanced features
- **`enhanced_server.py`**: Flask server with comprehensive data analysis and API endpoints
- **`test_enhanced_flowchart.py`**: Comprehensive test suite for all features

### Supporting Files
- **`README.md`**: This documentation file
- **`test_results.json`**: Generated test results (created after running tests)

## 🛠️ Setup and Usage

### Requirements
```bash
pip install flask requests selenium
```

### Quick Start
1. **Start the enhanced server**:
   ```powershell
   cd flowchart_visualization
   python enhanced_server.py
   ```

2. **Open your browser** to `http://localhost:5000`

3. **Explore the features**:
   - Use the view toggle to switch between file and function views
   - Click nodes to see relationship highlighting
   - Try the search and filter controls
   - Test different layout algorithms

### Advanced Usage
```powershell
# Custom port
python enhanced_server.py --port 8080

# Debug mode
python enhanced_server.py --debug

# Run without auto-opening browser
python enhanced_server.py --no-browser
```

## 🧪 Testing

Run the comprehensive test suite:
```powershell
python test_enhanced_flowchart.py
```

### Test Coverage
- ✅ Plot area sizing and responsiveness
- ✅ Function details view functionality
- ✅ Relationship highlighting with correct colors
- ✅ Interactive features (search, filter, layouts)
- ✅ API endpoints and data integrity
- ✅ Performance testing
- ✅ Edge cases and error handling

## 🎨 Visual Elements

### Node Types
- **🔵 Main Application**: Core application files (app.py, main.py)
- **🟢 Core Modules**: Business logic and main functionality
- **🟡 Utilities**: Helper functions and common utilities
- **🔴 Tests**: Test files and testing utilities
- **🟣 Configuration**: Config files and settings
- **🟣 Functions**: Individual functions (in function detail view)

### Relationship Lines
- **🔵 Blue lines**: Dependencies (this → imports that)
- **🟠 Orange lines**: Dependents (that → imports this)
- **🟣 Purple lines**: Function calls (in function detail view)

### Node Sizes
- Size represents code complexity and importance
- Larger nodes indicate more complex files/functions
- Function nodes are smaller than file nodes for clarity

## 🔧 Technical Implementation

### Enhanced Data Processing
- **AST Analysis**: Deep parsing of Python files for function details
- **Cross-file Analysis**: Detection of function calls across file boundaries
- **Complexity Metrics**: Cyclomatic complexity calculation for functions
- **Real-time Updates**: API endpoints for refreshing analysis data

### Performance Optimizations
- **Efficient D3.js rendering**: Optimized force simulation parameters
- **Smart filtering**: Client-side filtering with opacity transitions
- **Responsive design**: CSS Grid and Flexbox for optimal layouts
- **Memory management**: Proper cleanup of D3 elements

### Browser Compatibility
- **Modern browsers**: Chrome, Firefox, Safari, Edge
- **Responsive design**: Works on desktop, tablet, and mobile
- **Progressive enhancement**: Graceful fallbacks for older browsers

## 📊 API Endpoints

- **`/api/data`**: Complete analysis data including functions and relationships
- **`/api/files`**: File information and metrics
- **`/api/functions`**: Function details and call graphs
- **`/api/dependencies`**: File dependency relationships
- **`/api/stats`**: Project statistics and metrics
- **`/api/refresh`**: Refresh analysis data

## 🎯 Key Improvements

### From Original Implementation
1. **Full-width layout**: Maximizes available screen space
2. **Function-level detail**: Every function shown as individual nodes
3. **Enhanced highlighting**: Color-coded dependency vs dependent relationships
4. **Better organization**: All visualization files in dedicated folder
5. **Comprehensive testing**: Automated test suite for all features
6. **Improved performance**: Optimized rendering and data processing

### User Experience Enhancements
- Cleaner, more modern interface
- Better visual hierarchy and information density
- More intuitive interaction patterns
- Enhanced keyboard navigation
- Improved error handling and feedback

## 🐛 Troubleshooting

### Common Issues
1. **Server won't start**: Check if port 5000 is available
2. **No data showing**: Ensure the parent directory contains Python files
3. **Slow performance**: Try filtering to reduce visible nodes
4. **Browser compatibility**: Use Chrome/Firefox for best experience

### Debug Mode
Run with `--debug` flag for detailed error messages and live reloading.

## 📈 Future Enhancements

- [ ] Real-time code change detection
- [ ] Integration with Git history
- [ ] Collaborative features for team exploration
- [ ] Additional language support beyond Python
- [ ] Performance metrics overlay
- [ ] Code quality indicators

## 📄 License

This enhanced flowchart visualization is part of the Borehole Plots Render project and follows the same licensing terms.
