// Interactive Codebase Flowchart - JavaScript Implementation
// Advanced D3.js-based visualization for exploring code structure

class CodebaseFlowchart {
    constructor() {
        this.data = null;
        this.nodes = [];
        this.links = [];
        this.simulation = null;
        this.svg = null;
        this.g = null;
        this.tooltip = d3.select("#tooltip");
        this.selectedNode = null;
        this.searchTerm = "";
        this.currentFilter = "all";
        this.currentLayout = "force";
        this.currentView = "files";
        this.isDarkTheme = true;
        
        // Initialize the flowchart
        this.init();
    }

    async init() {
        try {
            // Load the analysis data
            await this.loadData();
            
            // Set up the SVG and simulation
            this.setupSVG();
            this.setupSimulation();
            
            // Create the visualization
            this.createVisualization();
            
            // Set up event handlers
            this.setupEventHandlers();
            
            // Hide loading indicator
            document.getElementById('loading').style.display = 'none';
            
        } catch (error) {
            console.error('Error initializing flowchart:', error);
            this.showError('Failed to load codebase analysis data');
        }
    }

    async loadData() {
        try {
            // Try to load from Flask API first
            const response = await fetch('/api/files');
            if (response.ok) {
                const files = await response.json();
                this.data = {
                    files: files,
                    dependencies: {},
                    functions: {},
                    classes: {},
                    imports: {}
                };
                
                // Try to load the complete analysis data which should include dependencies
                try {
                    const dataResponse = await fetch('/api/data');
                    if (dataResponse.ok) {
                        const completeData = await dataResponse.json();
                        if (completeData.dependencies) {
                            this.data.dependencies = completeData.dependencies;
                        }
                        if (completeData.functions) {
                            this.data.functions = completeData.functions;
                        }
                        if (completeData.classes) {
                            this.data.classes = completeData.classes;
                        }
                        if (completeData.imports) {
                            this.data.imports = completeData.imports;
                        }
                    }
                } catch (e) {
                    console.log('Complete data endpoint not available:', e);
                }
                
                this.processData();
                return;
            }
        } catch (error) {
            console.log('API not available, trying JSON file...');
        }
        
        // Fallback to JSON file
        try {
            const response = await fetch('codebase_analysis.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.data = await response.json();
            this.processData();
        } catch (error) {
            console.error('Error loading data:', error);
            // Final fallback to sample data
            this.createSampleData();
        }
    }

    processData() {
        if (!this.data || !this.data.files) {
            this.createSampleData();
            return;
        }

        // Process nodes (files)
        this.nodes = Object.entries(this.data.files).map(([path, info]) => ({
            id: path,
            name: path.split('/').pop() || path,
            path: path,
            type: this.categorizeFile(path),
            size: Math.max(5, Math.min(25, info.complexity || 10)),
            lines: info.total_lines || 0,
            complexity: info.complexity || 0,
            functions: info.functions_count || 0,
            classes: info.classes_count || 0,
            imports: info.imports_count || 0,
            dependencies: [],
            avg_complexity: info.avg_complexity || 0,
            code_lines: info.code_lines || 0,
            comment_lines: info.comment_lines || 0,
            blank_lines: info.blank_lines || 0,
            file_type: info.type || 'unknown'
        }));

        // Process links (dependencies)
        this.links = [];
        if (this.data.dependencies) {
            Object.entries(this.data.dependencies).forEach(([source, deps]) => {
                deps.forEach(target => {
                    if (this.data.files[target]) {
                        this.links.push({
                            source: source,
                            target: target,
                            type: 'dependency'
                        });
                    }
                });
            });
        }

        console.log(`Processed ${this.nodes.length} nodes and ${this.links.length} links`);
    }

    createSampleData() {
        // Create sample data for demonstration
        this.nodes = [
            { id: 'app.py', name: 'app.py', type: 'main', size: 20, lines: 555, complexity: 45, functions: 8, classes: 2, imports: 12 },
            { id: 'config.py', name: 'config.py', type: 'config', size: 15, lines: 755, complexity: 25, functions: 5, classes: 1, imports: 8 },
            { id: 'data_loader.py', name: 'data_loader.py', type: 'core', size: 12, lines: 156, complexity: 15, functions: 6, classes: 1, imports: 5 },
            { id: 'callbacks_split.py', name: 'callbacks_split.py', type: 'core', size: 25, lines: 2400, complexity: 266, functions: 45, classes: 3, imports: 18 },
            { id: 'utils.py', name: 'utils.py', type: 'utility', size: 8, lines: 110, complexity: 5, functions: 12, classes: 0, imports: 3 },
            { id: 'test_implementation.py', name: 'test_implementation.py', type: 'test', size: 10, lines: 89, complexity: 8, functions: 4, classes: 0, imports: 6 }
        ];

        this.links = [
            { source: 'app.py', target: 'config.py', type: 'dependency' },
            { source: 'app.py', target: 'data_loader.py', type: 'dependency' },
            { source: 'app.py', target: 'callbacks_split.py', type: 'dependency' },
            { source: 'callbacks_split.py', target: 'utils.py', type: 'dependency' },
            { source: 'data_loader.py', target: 'utils.py', type: 'dependency' },
            { source: 'test_implementation.py', target: 'app.py', type: 'dependency' }
        ];
    }

    categorizeFile(path) {
        const filename = path.toLowerCase();
        
        if (filename.includes('test_') || filename.includes('/test')) {
            return 'test';
        } else if (filename.includes('config') || filename.includes('constants')) {
            return 'config';
        } else if (filename.includes('util') || filename.includes('helper')) {
            return 'utility';
        } else if (filename === 'app.py' || filename.includes('main')) {
            return 'main';
        } else {
            return 'core';
        }
    }

    setupSVG() {
        const container = d3.select("#diagram");
        const containerRect = container.node().getBoundingClientRect();
        
        this.width = containerRect.width;
        this.height = containerRect.height;

        this.svg = container
            .attr("width", this.width)
            .attr("height", this.height);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                this.g.attr("transform", event.transform);
            });

        this.svg.call(zoom);

        // Create main group
        this.g = this.svg.append("g");

        // Add background
        this.svg.insert("rect", ":first-child")
            .attr("width", this.width)
            .attr("height", this.height)
            .attr("fill", "transparent")
            .on("click", () => this.clearSelection());
    }

    setupSimulation() {
        this.simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 5));
    }

    createVisualization() {
        // Filter nodes and links based on current filter
        const filteredNodes = this.filterNodes();
        const filteredLinks = this.filterLinks(filteredNodes);

        // Clear existing elements
        this.g.selectAll("*").remove();

        // Create links
        this.linkElements = this.g.selectAll(".link")
            .data(filteredLinks)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke", "rgba(255, 255, 255, 0.3)")
            .attr("stroke-width", 2);

        // Create nodes
        this.nodeElements = this.g.selectAll(".node")
            .data(filteredNodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => this.getNodeColor(d.type))
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .call(this.drag())
            .on("click", (event, d) => this.selectNode(d))
            .on("dblclick", (event, d) => this.focusNode(d))
            .on("mouseover", (event, d) => this.showTooltip(event, d))
            .on("mouseout", () => this.hideTooltip());

        // Create labels
        this.labelElements = this.g.selectAll(".node-label")
            .data(filteredNodes)
            .enter().append("text")
            .attr("class", "node-label")
            .text(d => d.name.length > 15 ? d.name.substring(0, 12) + '...' : d.name)
            .attr("dy", d => d.size + 15);

        // Update simulation
        this.simulation.nodes(filteredNodes);
        this.simulation.force("link").links(filteredLinks);
        this.simulation.alpha(1).restart();

        // Set up simulation tick
        this.simulation.on("tick", () => this.tick());
    }

    filterNodes() {
        let filtered = this.nodes;

        // Apply type filter
        if (this.currentFilter !== 'all') {
            const filterMap = {
                'main': ['main'],
                'tests': ['test'],
                'utils': ['utility'],
                'config': ['config']
            };
            filtered = filtered.filter(node => filterMap[this.currentFilter]?.includes(node.type));
        }

        // Apply search filter
        if (this.searchTerm) {
            filtered = filtered.filter(node => 
                node.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                node.path.toLowerCase().includes(this.searchTerm.toLowerCase())
            );
        }

        return filtered;
    }

    filterLinks(nodes) {
        const nodeIds = new Set(nodes.map(n => n.id));
        return this.links.filter(link => 
            nodeIds.has(link.source.id || link.source) && 
            nodeIds.has(link.target.id || link.target)
        );
    }

    getNodeColor(type) {
        const colors = {
            'main': '#4fc3f7',
            'core': '#81c784',
            'utility': '#ffb74d',
            'test': '#f06292',
            'config': '#ba68c8'
        };
        return colors[type] || '#9e9e9e';
    }

    tick() {
        this.linkElements
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        this.nodeElements
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        this.labelElements
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    }

    drag() {
        return d3.drag()
            .on("start", (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on("drag", (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on("end", (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }

    selectNode(node) {
        // Clear previous selection
        this.clearSelection();
        
        // Set new selection
        this.selectedNode = node;
        
        // Highlight selected node
        this.nodeElements.classed("selected", d => d.id === node.id);
        
        // Find and highlight relationships
        const dependencies = this.links.filter(l => 
            (l.source.id || l.source) === node.id || 
            (l.target.id || l.target) === node.id
        );
        
        // Highlight relationship links
        this.linkElements.classed("highlighted", d => 
            (d.source.id || d.source) === node.id || 
            (d.target.id || d.target) === node.id
        );
        
        // Highlight connected nodes
        const connectedNodeIds = new Set();
        dependencies.forEach(d => {
            connectedNodeIds.add(d.source.id || d.source);
            connectedNodeIds.add(d.target.id || d.target);
        });
        
        this.nodeElements.classed("highlighted", d => connectedNodeIds.has(d.id) && d.id !== node.id);
        
        // Update breadcrumb
        this.updateBreadcrumb(node);
        
        // Show node summary
        this.showNodeSummary(node, dependencies);
    }

    focusNode(node) {
        const scale = 2;
        const translate = [this.width / 2 - scale * node.x, this.height / 2 - scale * node.y];
        
        this.svg.transition()
            .duration(750)
            .call(d3.zoom().transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
    }

    clearSelection() {
        this.selectedNode = null;
        this.nodeElements?.classed("selected highlighted", false);
        this.linkElements?.classed("highlighted", false);
        this.updateBreadcrumb();
        this.hideNodeSummary();
    }

    showNodeSummary(node, relationships) {
        const summaryArea = document.getElementById('summary-area');
        const summaryContent = document.getElementById('summary-content');
        
        // Calculate relationship counts
        const dependencies = relationships.filter(r => (r.target.id || r.target) === node.id);
        const dependents = relationships.filter(r => (r.source.id || r.source) === node.id);
        
        const html = `
            <h3>${node.name}</h3>
            <div class="summary-metrics">
                <div class="summary-metric">
                    <span class="label">Lines of Code</span>
                    <span class="value">${node.lines}</span>
                </div>
                <div class="summary-metric">
                    <span class="label">Complexity</span>
                    <span class="value">${node.complexity}</span>
                </div>
                <div class="summary-metric">
                    <span class="label">Functions</span>
                    <span class="value">${node.functions}</span>
                </div>
                <div class="summary-metric">
                    <span class="label">Classes</span>
                    <span class="value">${node.classes}</span>
                </div>
                <div class="summary-metric">
                    <span class="label">Dependencies</span>
                    <span class="value">${dependencies.length}</span>
                </div>
                <div class="summary-metric">
                    <span class="label">Dependents</span>
                    <span class="value">${dependents.length}</span>
                </div>
            </div>
            ${dependencies.length > 0 ? `
                <div class="summary-relationships">
                    <h4>Dependencies (${dependencies.length})</h4>
                    <div class="relationship-list">${dependencies.map(d => d.source.name || d.source).join(', ')}</div>
                </div>
            ` : ''}
            ${dependents.length > 0 ? `
                <div class="summary-relationships">
                    <h4>Dependents (${dependents.length})</h4>
                    <div class="relationship-list">${dependents.map(d => d.target.name || d.target).join(', ')}</div>
                </div>
            ` : ''}
        `;
        
        summaryContent.innerHTML = html;
        summaryArea.classList.add('visible');
    }

    hideNodeSummary() {
        const summaryArea = document.getElementById('summary-area');
        summaryArea.classList.remove('visible');
    }

    showTooltip(event, node) {
        const tooltip = this.tooltip;
        
        const html = `
            <h3>${node.name}</h3>
            <div class="path">${node.path || node.id}</div>
            <div class="file-type">📂 ${node.file_type || node.type}</div>
            <div class="stats">
                <div class="stat">📄 ${node.lines} total lines</div>
                <div class="stat">💻 ${node.code_lines || 'N/A'} code lines</div>
                <div class="stat">💬 ${node.comment_lines || 'N/A'} comment lines</div>
                <div class="stat">🔧 ${node.complexity} complexity</div>
                <div class="stat">📊 ${node.avg_complexity?.toFixed(1) || 'N/A'} avg complexity</div>
                <div class="stat">⚙️ ${node.functions} functions</div>
                <div class="stat">🏛️ ${node.classes} classes</div>
                <div class="stat">📦 ${node.imports} imports</div>
            </div>
        `;
        
        tooltip.html(html)
            .style("opacity", 1)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px");
    }

    hideTooltip() {
        this.tooltip.style("opacity", 0);
    }

    updateBreadcrumb(node = null, viewContext = null) {
        const breadcrumb = d3.select("#breadcrumb");
        let content = '';
        
        if (node) {
            content = `📍 ${node.path || node.id}`;
        } else if (viewContext) {
            content = `📍 ${viewContext}`;
        } else {
            content = `📍 Root - ${this.currentView.charAt(0).toUpperCase() + this.currentView.slice(1)} View`;
        }
        
        breadcrumb.html(`<span>${content}</span>`);
    }

    setupEventHandlers() {
        // Search input
        d3.select("#search").on("input", (event) => {
            this.searchTerm = event.target.value;
            this.createVisualization();
        });

        // Filter dropdown
        d3.select("#filter").on("change", (event) => {
            this.currentFilter = event.target.value;
            this.createVisualization();
        });

        // Layout dropdown
        d3.select("#layout").on("change", (event) => {
            this.currentLayout = event.target.value;
            this.applyLayout();
        });

        // View mode dropdown
        d3.select("#view-mode").on("change", (event) => {
            this.currentView = event.target.value;
            this.updateVisualizationForView();
        });

        // Keyboard shortcuts
        d3.select("body").on("keydown", (event) => {
            switch(event.code) {
                case 'Space':
                    event.preventDefault();
                    this.resetView();
                    break;
                case 'KeyF':
                    event.preventDefault();
                    if (this.selectedNode) this.focusNode(this.selectedNode);
                    break;
                case 'KeyH':
                    event.preventDefault();
                    toggleHelp();
                    break;
                case 'KeyT':
                    event.preventDefault();
                    toggleTheme();
                    break;
                case 'Escape':
                    event.preventDefault();
                    this.clearSelection();
                    break;
            }
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    applyLayout() {
        if (!this.simulation) return;

        // Clear existing forces
        this.simulation.force("center", null);
        this.simulation.force("charge", null);
        this.simulation.force("link", null);

        switch(this.currentLayout) {
            case 'force':
                this.simulation
                    .force("link", d3.forceLink().id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(this.width / 2, this.height / 2));
                break;
            case 'hierarchical':
                this.simulation
                    .force("link", d3.forceLink().id(d => d.id).distance(150))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(this.width / 2, this.height / 2))
                    .force("y", d3.forceY().strength(0.1));
                break;
            case 'radial':
                this.simulation
                    .force("link", d3.forceLink().id(d => d.id).distance(80))
                    .force("charge", d3.forceManyBody().strength(-400))
                    .force("center", d3.forceCenter(this.width / 2, this.height / 2))
                    .force("radial", d3.forceRadial(200, this.width / 2, this.height / 2));
                break;
        }

        this.simulation.alpha(1).restart();
    }

    resetView() {
        this.svg.transition()
            .duration(750)
            .call(d3.zoom().transform, d3.zoomIdentity);
        
        // Clear selection
        this.clearSelection();
        
        // Restart simulation
        this.simulation.alpha(1).restart();
    }

    handleResize() {
        const container = d3.select("#diagram");
        const containerRect = container.node().getBoundingClientRect();
        
        this.width = containerRect.width;
        this.height = containerRect.height;

        this.svg
            .attr("width", this.width)
            .attr("height", this.height);

        this.simulation
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .alpha(0.3)
            .restart();
    }

    updateVisualizationForView() {
        // Update visualization based on current view mode
        switch(this.currentView) {
            case 'files':
                this.updateFileView();
                break;
            case 'functions':
                this.updateFunctionView();
                break;
            case 'dependencies':
                this.updateDependencyView();
                break;
        }
    }

    updateFileView() {
        // Standard file-based view with complexity-based sizing
        if (this.nodeElements) {
            this.nodeElements
                .attr("r", d => Math.max(5, Math.min(25, d.complexity || 10)))
                .attr("fill", d => this.getNodeColor(d.type));
        }
        this.updateBreadcrumb();
    }

    updateFunctionView() {
        // Function-focused view with function count-based sizing
        if (this.nodeElements) {
            this.nodeElements
                .attr("r", d => Math.max(5, Math.min(30, d.functions * 2 + 5)))
                .attr("fill", d => {
                    // Color based on function density
                    if (d.functions === 0) return '#666';
                    if (d.functions < 5) return '#81c784';
                    if (d.functions < 10) return '#ffb74d';
                    return '#f06292';
                });
        }
        this.updateBreadcrumb(null, "Function Analysis View");
    }

    updateDependencyView() {
        // Dependency-focused view highlighting interconnections
        if (this.nodeElements) {
            this.nodeElements
                .attr("r", d => {
                    const inDegree = this.links.filter(l => (l.target.id || l.target) === d.id).length;
                    const outDegree = this.links.filter(l => (l.source.id || l.source) === d.id).length;
                    return Math.max(5, Math.min(25, (inDegree + outDegree) * 2 + 5));
                })
                .attr("fill", d => {
                    const connections = this.links.filter(l => 
                        (l.target.id || l.target) === d.id || (l.source.id || l.source) === d.id
                    ).length;
                    if (connections === 0) return '#666';
                    if (connections < 3) return '#4fc3f7';
                    if (connections < 6) return '#ffb74d';
                    return '#f06292';
                });
        }
        this.updateBreadcrumb(null, "Dependency Analysis View");
    }

    showError(message) {
        const loading = document.getElementById('loading');
        loading.innerHTML = `
            <div style="color: #f44336;">
                <h3>⚠️ Error</h3>
                <p>${message}</p>
                <p>Please ensure the codebase analysis has been run.</p>
            </div>
        `;
    }
}

// Global functions for HTML event handlers
function resetView() {
    if (flowchart && flowchart.resetView) {
        flowchart.resetView();
    }
}

function resetZoom() {
    if (flowchart && flowchart.resetView) {
        flowchart.resetView();
    }
}

function toggleHelp() {
    const helpOverlay = document.querySelector('.help-overlay');
    if (helpOverlay) {
        helpOverlay.style.display = helpOverlay.style.display === 'flex' ? 'none' : 'flex';
    }
}

function toggleView() {
    const viewMode = document.getElementById('view-mode');
    if (viewMode) {
        const currentIndex = viewMode.selectedIndex;
        const nextIndex = (currentIndex + 1) % viewMode.options.length;
        viewMode.selectedIndex = nextIndex;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        viewMode.dispatchEvent(event);
    }
}

function exportDiagram() {
    // Create SVG export
    const svgElement = document.querySelector("#diagram");
    if (!svgElement) return;
    
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    
    canvas.width = svgElement.width.baseVal.value;
    canvas.height = svgElement.height.baseVal.value;
    
    img.onload = () => {
        ctx.drawImage(img, 0, 0);
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'codebase_flowchart.png';
            a.click();
            URL.revokeObjectURL(url);
        });
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    if (flowchart) {
        flowchart.isDarkTheme = !flowchart.isDarkTheme;
    }
}

// Initialize the flowchart when the page loads
let flowchart;
document.addEventListener('DOMContentLoaded', () => {
    flowchart = new CodebaseFlowchart();
});
