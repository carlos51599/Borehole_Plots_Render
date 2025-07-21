// Enhanced Interactive Codebase Flowchart - JavaScript Implementation
// Advanced D3.js-based visualization with function details and relationship highlighting

class EnhancedCodebaseFlowchart {
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
        this.highlightedRelationships = new Set();
        
        // Enhanced visualization dimensions for full width
        this.width = window.innerWidth - 32; // Account for margins
        this.height = window.innerHeight - 200; // Account for header/controls
        
        // Initialize the flowchart
        this.init();
    }

    async init() {
        try {
            await this.loadData();
            this.setupSVG();
            this.setupSimulation();
            this.createVisualization();
            this.setupEventHandlers();
            this.setupKeyboardShortcuts();
            
            document.getElementById('loading').style.display = 'none';
            console.log('✅ Enhanced flowchart initialized successfully');
        } catch (error) {
            console.error('Error initializing enhanced flowchart:', error);
            this.showError('Failed to load codebase analysis data');
        }
    }

    async loadData() {
        try {
            // Try to load from Flask API first
            const response = await fetch('/api/data');
            if (response.ok) {
                this.data = await response.json();
                this.processData();
                return;
            }
        } catch (error) {
            console.log('API not available, trying JSON file...');
        }
        
        // Fallback to JSON file
        try {
            const response = await fetch('../codebase_analysis.json');
            if (response.ok) {
                this.data = await response.json();
                this.processData();
                return;
            }
        } catch (error) {
            console.log('JSON file not available, creating sample data...');
        }

        // Final fallback to enhanced sample data
        this.createEnhancedSampleData();
    }

    createEnhancedSampleData() {
        console.log('Creating enhanced sample data with function details...');
        
        this.data = {
            files: {
                'app.py': {
                    name: 'app.py',
                    type: 'main',
                    complexity: 45,
                    total_lines: 555,
                    functions_count: 8,
                    classes_count: 2,
                    imports_count: 12,
                    functions: ['create_app', 'initialize_database', 'setup_routes', 'handle_errors']
                },
                'config.py': {
                    name: 'config.py',
                    type: 'config',
                    complexity: 25,
                    total_lines: 150,
                    functions_count: 3,
                    classes_count: 1,
                    imports_count: 5,
                    functions: ['load_config', 'validate_settings', 'get_database_url']
                },
                'data_loader.py': {
                    name: 'data_loader.py',
                    type: 'core',
                    complexity: 35,
                    total_lines: 420,
                    functions_count: 12,
                    classes_count: 3,
                    imports_count: 8,
                    functions: ['load_ags_data', 'parse_borehole_data', 'validate_data', 'extract_geology']
                },
                'section_plot_professional.py': {
                    name: 'section_plot_professional.py',
                    type: 'core',
                    complexity: 60,
                    total_lines: 890,
                    functions_count: 15,
                    classes_count: 4,
                    imports_count: 18,
                    functions: ['create_section_plot', 'render_boreholes', 'add_geology_layers', 'format_plot']
                },
                'test_section_plot.py': {
                    name: 'test_section_plot.py',
                    type: 'test',
                    complexity: 20,
                    total_lines: 280,
                    functions_count: 8,
                    classes_count: 1,
                    imports_count: 6,
                    functions: ['test_plot_creation', 'test_data_validation', 'test_rendering', 'test_edge_cases']
                },
                'utils/map_utils.py': {
                    name: 'map_utils.py',
                    type: 'utility',
                    complexity: 30,
                    total_lines: 340,
                    functions_count: 10,
                    classes_count: 2,
                    imports_count: 7,
                    functions: ['calculate_coordinates', 'transform_projection', 'validate_coordinates', 'get_distance']
                }
            },
            dependencies: {
                'app.py': ['config.py', 'data_loader.py', 'section_plot_professional.py'],
                'section_plot_professional.py': ['data_loader.py', 'utils/map_utils.py'],
                'test_section_plot.py': ['section_plot_professional.py', 'data_loader.py'],
                'data_loader.py': ['config.py', 'utils/map_utils.py']
            },
            functions: {
                'app.py': {
                    'create_app': { calls: ['load_config', 'initialize_database'], complexity: 12 },
                    'initialize_database': { calls: ['get_database_url'], complexity: 8 },
                    'setup_routes': { calls: ['create_section_plot'], complexity: 15 },
                    'handle_errors': { calls: [], complexity: 5 }
                },
                'config.py': {
                    'load_config': { calls: ['validate_settings'], complexity: 8 },
                    'validate_settings': { calls: [], complexity: 6 },
                    'get_database_url': { calls: [], complexity: 4 }
                },
                'data_loader.py': {
                    'load_ags_data': { calls: ['validate_data', 'parse_borehole_data'], complexity: 18 },
                    'parse_borehole_data': { calls: ['extract_geology'], complexity: 22 },
                    'validate_data': { calls: [], complexity: 10 },
                    'extract_geology': { calls: [], complexity: 15 }
                }
            }
        };
        
        this.processData();
    }

    processData() {
        if (!this.data || !this.data.files) {
            this.createEnhancedSampleData();
            return;
        }

        // Process file nodes
        this.nodes = Object.entries(this.data.files).map(([path, info]) => ({
            id: path,
            name: path.split('/').pop() || path,
            path: path,
            type: this.categorizeFile(path),
            nodeType: 'file',
            size: Math.max(8, Math.min(30, (info.complexity || 10) * 0.8)),
            lines: info.total_lines || 0,
            complexity: info.complexity || 0,
            functions: info.functions_count || 0,
            classes: info.classes_count || 0,
            imports: info.imports_count || 0,
            functionList: info.functions || [],
            x: Math.random() * this.width,
            y: Math.random() * this.height
        }));

        // Add function nodes when in function detail view
        if (this.currentView === 'functions' && this.data.functions) {
            Object.entries(this.data.functions).forEach(([filePath, functions]) => {
                Object.entries(functions).forEach(([funcName, funcInfo]) => {
                    this.nodes.push({
                        id: `${filePath}::${funcName}`,
                        name: funcName,
                        path: filePath,
                        type: 'function',
                        nodeType: 'function',
                        size: Math.max(5, Math.min(15, (funcInfo.complexity || 5) * 0.6)),
                        complexity: funcInfo.complexity || 0,
                        calls: funcInfo.calls || [],
                        parentFile: filePath,
                        x: Math.random() * this.width,
                        y: Math.random() * this.height
                    });
                });
            });
        }

        // Process dependency links
        this.links = [];
        if (this.data.dependencies) {
            Object.entries(this.data.dependencies).forEach(([source, deps]) => {
                deps.forEach(target => {
                    if (this.data.files[target]) {
                        this.links.push({
                            source: source,
                            target: target,
                            type: 'dependency',
                            id: `${source}-${target}`
                        });
                    }
                });
            });
        }

        // Add function call links when in function detail view
        if (this.currentView === 'functions' && this.data.functions) {
            Object.entries(this.data.functions).forEach(([filePath, functions]) => {
                Object.entries(functions).forEach(([funcName, funcInfo]) => {
                    if (funcInfo.calls) {
                        funcInfo.calls.forEach(calledFunc => {
                            // Find the target function
                            const targetId = this.findFunctionNodeId(calledFunc);
                            if (targetId) {
                                this.links.push({
                                    source: `${filePath}::${funcName}`,
                                    target: targetId,
                                    type: 'function_call',
                                    id: `${filePath}::${funcName}-${targetId}`
                                });
                            }
                        });
                    }
                });
            });
        }

        console.log(`✅ Processed ${this.nodes.length} nodes and ${this.links.length} links`);
    }

    findFunctionNodeId(funcName) {
        // Look for a function with this name in any file
        for (const node of this.nodes) {
            if (node.nodeType === 'function' && node.name === funcName) {
                return node.id;
            }
        }
        return null;
    }

    categorizeFile(filePath) {
        const fileName = filePath.toLowerCase();
        
        if (fileName.includes('test_') || fileName.includes('_test.') || fileName.includes('/test/')) {
            return 'test';
        } else if (fileName.includes('config') || fileName.includes('settings') || fileName.includes('.env')) {
            return 'config';
        } else if (fileName.includes('util') || fileName.includes('helper') || fileName.includes('common')) {
            return 'utility';
        } else if (fileName.includes('app.py') || fileName.includes('main.py') || fileName.includes('__init__.py')) {
            return 'main';
        } else {
            return 'core';
        }
    }

    getNodeColor(node) {
        if (node.nodeType === 'function') {
            return '#9C27B0'; // Purple for functions
        }
        
        const colors = {
            'main': '#4fc3f7',
            'core': '#81c784',
            'utility': '#ffb74d',
            'test': '#f06292',
            'config': '#ba68c8'
        };
        return colors[node.type] || '#90a4ae';
    }

    setupSVG() {
        this.svg = d3.select("#diagram")
            .attr("width", this.width)
            .attr("height", this.height)
            .attr("viewBox", [0, 0, this.width, this.height]);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                this.g.attr("transform", event.transform);
            });

        this.svg.call(zoom);

        // Create main group
        this.g = this.svg.append("g");

        // Add arrow markers for directed relationships
        this.svg.append("defs").selectAll("marker")
            .data(["dependency", "dependent", "function_call"])
            .join("marker")
            .attr("id", d => `arrow-${d}`)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 15)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", d => {
                switch(d) {
                    case 'dependency': return '#2196F3';
                    case 'dependent': return '#FF9800';
                    case 'function_call': return '#9C27B0';
                    default: return '#666';
                }
            });
    }

    setupSimulation() {
        this.simulation = d3.forceSimulation(this.nodes)
            .force("link", d3.forceLink(this.links).id(d => d.id).distance(100).strength(0.3))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 5))
            .alphaDecay(0.01)
            .velocityDecay(0.4);
    }

    createVisualization() {
        // Clear existing visualization
        this.g.selectAll("*").remove();

        // Create links
        this.linkElements = this.g.append("g")
            .attr("class", "links")
            .selectAll(".link")
            .data(this.links)
            .join("line")
            .attr("class", d => `link link-${d.type}`)
            .attr("stroke-width", d => d.type === 'function_call' ? 1 : 2)
            .attr("stroke", d => {
                switch(d.type) {
                    case 'dependency': return '#2196F3';
                    case 'function_call': return '#9C27B0';
                    default: return 'rgba(255, 255, 255, 0.3)';
                }
            })
            .attr("marker-end", d => `url(#arrow-${d.type})`);

        // Create nodes
        this.nodeElements = this.g.append("g")
            .attr("class", "nodes")
            .selectAll(".node")
            .data(this.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => this.getNodeColor(d))
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .call(this.drag());

        // Add labels
        this.labelElements = this.g.append("g")
            .attr("class", "labels")
            .selectAll(".node-label")
            .data(this.nodes)
            .join("text")
            .attr("class", "node-label")
            .attr("dy", d => d.nodeType === 'function' ? 4 : 6)
            .attr("font-size", d => d.nodeType === 'function' ? "8px" : "10px")
            .text(d => d.name.length > 15 ? d.name.substring(0, 12) + "..." : d.name);

        // Set up event handlers
        this.setupNodeEvents();

        // Update simulation with new nodes and links
        this.simulation.nodes(this.nodes);
        this.simulation.force("link").links(this.links);
        this.simulation.alpha(1).restart();

        // Update positions on each tick
        this.simulation.on("tick", () => {
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
        });
    }

    setupNodeEvents() {
        this.nodeElements
            .on("mouseover", (event, d) => this.showTooltip(event, d))
            .on("mouseout", () => this.hideTooltip())
            .on("click", (event, d) => this.selectNode(event, d))
            .on("dblclick", (event, d) => this.focusNode(d));
    }

    selectNode(event, node) {
        event.stopPropagation();
        
        // Clear previous selection
        this.clearHighlights();
        
        this.selectedNode = node;
        
        // Highlight selected node
        d3.select(event.currentTarget)
            .classed("selected", true);
        
        // Find and highlight relationships
        this.highlightRelationships(node);
        
        // Update summary
        this.updateSummary(node);
        
        // Update breadcrumb
        this.updateBreadcrumb(node);
        
        console.log(`Selected node: ${node.name} (${node.nodeType})`);
    }

    highlightRelationships(node) {
        this.highlightedRelationships.clear();
        
        // Find dependencies (what this node depends on)
        const dependencies = this.links.filter(link => 
            (typeof link.source === 'object' ? link.source.id : link.source) === node.id
        );
        
        // Find dependents (what depends on this node)
        const dependents = this.links.filter(link => 
            (typeof link.target === 'object' ? link.target.id : link.target) === node.id
        );
        
        // Highlight dependency links (blue)
        dependencies.forEach(link => {
            this.highlightedRelationships.add(link.id);
            this.linkElements
                .filter(d => d.id === link.id)
                .classed("highlighted-dependency", true)
                .attr("stroke", "#2196F3")
                .attr("stroke-width", 3);
            
            // Highlight dependency nodes
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
            this.nodeElements
                .filter(d => d.id === targetId)
                .classed("highlighted", true);
        });
        
        // Highlight dependent links (orange)
        dependents.forEach(link => {
            this.highlightedRelationships.add(link.id);
            this.linkElements
                .filter(d => d.id === link.id)
                .classed("highlighted-dependent", true)
                .attr("stroke", "#FF9800")
                .attr("stroke-width", 3);
            
            // Highlight dependent nodes
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            this.nodeElements
                .filter(d => d.id === sourceId)
                .classed("highlighted", true);
        });
        
        console.log(`Highlighted ${dependencies.length} dependencies and ${dependents.length} dependents`);
    }

    clearHighlights() {
        this.nodeElements.classed("selected highlighted", false);
        this.linkElements
            .classed("highlighted-dependency highlighted-dependent", false)
            .attr("stroke", d => {
                switch(d.type) {
                    case 'dependency': return '#2196F3';
                    case 'function_call': return '#9C27B0';
                    default: return 'rgba(255, 255, 255, 0.3)';
                }
            })
            .attr("stroke-width", d => d.type === 'function_call' ? 1 : 2);
        
        this.highlightedRelationships.clear();
        this.selectedNode = null;
        
        // Hide summary
        document.getElementById('summary-area').classList.remove('visible');
    }

    showTooltip(event, node) {
        let content = `
            <h3>${node.name}</h3>
            <div class="path">${node.path}</div>
            <div class="file-type">${node.nodeType === 'function' ? 'Function' : 'File'} - ${node.type}</div>
        `;
        
        if (node.nodeType === 'function') {
            content += `
                <div class="stats">
                    <div class="stat">Complexity: ${node.complexity}</div>
                    <div class="stat">Calls: ${node.calls ? node.calls.length : 0}</div>
                </div>
            `;
            if (node.calls && node.calls.length > 0) {
                content += `<div style="margin-top: 8px; font-size: 10px;">
                    <strong>Calls:</strong> ${node.calls.join(', ')}
                </div>`;
            }
        } else {
            content += `
                <div class="stats">
                    <div class="stat">Lines: ${node.lines}</div>
                    <div class="stat">Complexity: ${node.complexity}</div>
                    <div class="stat">Functions: ${node.functions}</div>
                    <div class="stat">Classes: ${node.classes}</div>
                </div>
            `;
            if (node.functionList && node.functionList.length > 0) {
                content += `<div style="margin-top: 8px; font-size: 10px;">
                    <strong>Functions:</strong> ${node.functionList.slice(0, 3).join(', ')}${node.functionList.length > 3 ? '...' : ''}
                </div>`;
            }
        }

        this.tooltip
            .style("opacity", 1)
            .html(content)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px");
    }

    hideTooltip() {
        this.tooltip.style("opacity", 0);
    }

    updateSummary(node) {
        const summaryArea = document.getElementById('summary-area');
        const summaryContent = document.getElementById('summary-content');
        
        let content = `<h3>${node.name}</h3>`;
        
        if (node.nodeType === 'function') {
            content += `
                <div class="summary-metrics">
                    <div class="summary-metric">
                        <span class="label">Complexity</span>
                        <span class="value">${node.complexity}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="label">Function Calls</span>
                        <span class="value">${node.calls ? node.calls.length : 0}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="label">Parent File</span>
                        <span class="value">${node.parentFile}</span>
                    </div>
                </div>
            `;
        } else {
            const dependencies = this.links.filter(link => 
                (typeof link.source === 'object' ? link.source.id : link.source) === node.id
            ).length;
            
            const dependents = this.links.filter(link => 
                (typeof link.target === 'object' ? link.target.id : link.target) === node.id
            ).length;
            
            content += `
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
                        <span class="label">Dependencies</span>
                        <span class="value">${dependencies}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="label">Dependents</span>
                        <span class="value">${dependents}</span>
                    </div>
                </div>
            `;
        }
        
        summaryContent.innerHTML = content;
        summaryArea.classList.add('visible');
    }

    updateBreadcrumb(node) {
        const breadcrumb = document.getElementById('breadcrumb');
        if (node.nodeType === 'function') {
            breadcrumb.innerHTML = `<span>📍 ${node.parentFile} → ${node.name}()</span>`;
        } else {
            breadcrumb.innerHTML = `<span>📍 ${node.path}</span>`;
        }
    }

    focusNode(node) {
        // Center the view on the selected node
        const transform = d3.zoomIdentity
            .translate(this.width / 2 - node.x, this.height / 2 - node.y)
            .scale(1.5);
        
        this.svg.transition()
            .duration(750)
            .call(d3.zoom().transform, transform);
    }

    setupEventHandlers() {
        // Search functionality
        document.getElementById('search').addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterVisualization();
        });

        // Filter functionality
        document.getElementById('filter').addEventListener('change', (e) => {
            this.currentFilter = e.target.value;
            this.filterVisualization();
        });

        // Layout change
        document.getElementById('layout').addEventListener('change', (e) => {
            this.currentLayout = e.target.value;
            this.updateLayout();
        });

        // View mode change
        document.getElementById('view-mode').addEventListener('change', (e) => {
            this.currentView = e.target.value;
            this.switchView();
        });

        // Clear selection on empty space click
        this.svg.on("click", () => {
            this.clearHighlights();
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case ' ':
                    e.preventDefault();
                    this.resetZoom();
                    break;
                case 'f':
                case 'F':
                    if (this.selectedNode) {
                        this.focusNode(this.selectedNode);
                    }
                    break;
                case 'h':
                case 'H':
                    this.toggleHelp();
                    break;
                case 'Escape':
                    this.clearHighlights();
                    break;
            }
        });
    }

    switchView() {
        console.log(`Switching to ${this.currentView} view`);
        this.clearHighlights();
        this.processData();
        this.createVisualization();
    }

    filterVisualization() {
        let filteredNodes = this.nodes;

        // Apply search filter
        if (this.searchTerm) {
            filteredNodes = filteredNodes.filter(node => 
                node.name.toLowerCase().includes(this.searchTerm) ||
                node.path.toLowerCase().includes(this.searchTerm)
            );
        }

        // Apply type filter
        if (this.currentFilter !== 'all') {
            filteredNodes = filteredNodes.filter(node => node.type === this.currentFilter);
        }

        // Update visibility
        this.nodeElements.style("opacity", d => 
            filteredNodes.includes(d) ? 1 : 0.1
        );

        this.labelElements.style("opacity", d => 
            filteredNodes.includes(d) ? 1 : 0.1
        );

        // Update links visibility
        const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
        this.linkElements.style("opacity", d => {
            const sourceId = typeof d.source === 'object' ? d.source.id : d.source;
            const targetId = typeof d.target === 'object' ? d.target.id : d.target;
            return filteredNodeIds.has(sourceId) && filteredNodeIds.has(targetId) ? 1 : 0.1;
        });
    }

    updateLayout() {
        // Implement different layout algorithms
        switch(this.currentLayout) {
            case 'hierarchical':
                this.applyHierarchicalLayout();
                break;
            case 'radial':
                this.applyRadialLayout();
                break;
            default:
                this.applyForceLayout();
                break;
        }
    }

    applyForceLayout() {
        this.simulation
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .alpha(1).restart();
    }

    applyHierarchicalLayout() {
        // Simple hierarchical layout
        const levels = this.calculateNodeLevels();
        const levelHeight = this.height / (Object.keys(levels).length + 1);
        
        Object.entries(levels).forEach(([level, nodes]) => {
            const y = (parseInt(level) + 1) * levelHeight;
            const spacing = this.width / (nodes.length + 1);
            
            nodes.forEach((node, i) => {
                node.fx = (i + 1) * spacing;
                node.fy = y;
            });
        });
        
        this.simulation.alpha(1).restart();
    }

    applyRadialLayout() {
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const maxRadius = Math.min(this.width, this.height) / 3;
        
        this.nodes.forEach((node, i) => {
            const angle = (i / this.nodes.length) * 2 * Math.PI;
            const radius = node.nodeType === 'function' ? maxRadius * 0.7 : maxRadius;
            
            node.fx = centerX + Math.cos(angle) * radius;
            node.fy = centerY + Math.sin(angle) * radius;
        });
        
        this.simulation.alpha(1).restart();
    }

    calculateNodeLevels() {
        const levels = {};
        const visited = new Set();
        
        // Find root nodes (no dependencies)
        const rootNodes = this.nodes.filter(node => 
            !this.links.some(link => 
                (typeof link.target === 'object' ? link.target.id : link.target) === node.id
            )
        );
        
        const assignLevel = (node, level) => {
            if (visited.has(node.id)) return;
            visited.add(node.id);
            
            if (!levels[level]) levels[level] = [];
            levels[level].push(node);
            
            // Find children
            const children = this.links
                .filter(link => (typeof link.source === 'object' ? link.source.id : link.source) === node.id)
                .map(link => typeof link.target === 'object' ? link.target : this.nodes.find(n => n.id === link.target));
            
            children.forEach(child => assignLevel(child, level + 1));
        };
        
        rootNodes.forEach(node => assignLevel(node, 0));
        
        return levels;
    }

    handleResize() {
        this.width = window.innerWidth - 32;
        this.height = window.innerHeight - 200;
        
        this.svg
            .attr("width", this.width)
            .attr("height", this.height)
            .attr("viewBox", [0, 0, this.width, this.height]);
        
        this.simulation
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .alpha(0.3).restart();
    }

    resetZoom() {
        this.svg.transition()
            .duration(750)
            .call(d3.zoom().transform, d3.zoomIdentity);
    }

    resetView() {
        this.clearHighlights();
        this.resetZoom();
        document.getElementById('search').value = '';
        document.getElementById('filter').value = 'all';
        this.searchTerm = '';
        this.currentFilter = 'all';
        this.filterVisualization();
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

    exportDiagram() {
        // Create SVG export
        const svgNode = this.svg.node();
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svgNode);
        
        const blob = new Blob([svgString], {type: "image/svg+xml;charset=utf-8"});
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement("a");
        link.href = url;
        link.download = "codebase_flowchart.svg";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    }

    toggleHelp() {
        const helpOverlay = document.getElementById('help-overlay');
        if (helpOverlay.style.display === 'flex') {
            helpOverlay.style.display = 'none';
        } else {
            helpOverlay.style.display = 'flex';
        }
    }

    showError(message) {
        const loading = document.getElementById('loading');
        loading.innerHTML = `
            <div style="color: #f44336; text-align: center;">
                <h3>⚠️ Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()" style="margin-top: 10px;">🔄 Retry</button>
            </div>
        `;
    }
}

// Global functions for HTML event handlers
function toggleView() {
    const viewMode = document.getElementById('view-mode');
    if (viewMode.value === 'files') {
        viewMode.value = 'functions';
    } else {
        viewMode.value = 'files';
    }
    viewMode.dispatchEvent(new Event('change'));
}

function toggleHelp() {
    if (window.flowchart) {
        window.flowchart.toggleHelp();
    }
}

function hideHelp() {
    document.getElementById('help-overlay').style.display = 'none';
}

function resetZoom() {
    if (window.flowchart) {
        window.flowchart.resetZoom();
    }
}

function resetView() {
    if (window.flowchart) {
        window.flowchart.resetView();
    }
}

function exportDiagram() {
    if (window.flowchart) {
        window.flowchart.exportDiagram();
    }
}

// Initialize the enhanced flowchart when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Enhanced Interactive Codebase Flowchart...');
    window.flowchart = new EnhancedCodebaseFlowchart();
});
