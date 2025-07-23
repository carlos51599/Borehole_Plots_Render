"""
Graph Visualization Module
=========================

Core D3.js rendering and visualization utilities.
Handles node/link creation, tooltips, event handling, and common graph operations.
"""


def get_graph_visualization_js() -> str:
    """
    Get JavaScript code for core graph visualization functionality.

    Returns:
        str: JavaScript code for graph rendering and utilities
    """
    return """
        // Enhanced state management
        let checkedFolders = new Set(Object.keys(graphData.subfolder_info));
        let showTestDependencies = true;
        let selectedNode = null;
        let highlightedNodes = new Set();

        // Layout state management
        let currentLayout = "hierarchical";
        let simulation = null;

        // Advanced filter state
        let maxPredecessorsFilter = 20;
        let maxSuccessorsFilter = 20;
        let maxSizeFilter = 100; // KB

        // D3.js setup with enhanced features
        const svg = d3.select("#graph");
        const tooltip = d3.select("#tooltip");
        let width, height;

        function updateDimensions() {
            const container = document.querySelector('.graph-container');
            width = container.clientWidth;
            height = container.clientHeight;
            svg.attr("width", width).attr("height", height);
        }

        // Initialize enhanced visualization
        function initializeEnhancedVisualization() {
            console.log("🚀 Initializing enhanced dependency graph visualization...");
            
            updateDimensions();
            svg.selectAll("*").remove();
        
        // Helper function to add appropriate node shapes based on layout
        function addNodeShapes(nodeSelection) {
            console.log(`🔍 DEBUG: addNodeShapes called, currentLayout = "${currentLayout}"`);
            console.log(`🔍 DEBUG: nodeSelection size = ${nodeSelection.size()}`);
            
            if (currentLayout === "force") {
                console.log("🔍 DEBUG: Creating circles for force layout");
                // Use circles for force-directed layout
                const circles = nodeSelection.append("circle")
                    .attr("class", d => {
                        let classes = "node-circle";
                        if (d.hotspot_score && d.hotspot_score > 0.5) classes += " hotspot";
                        if (d.change_classification === "very_high") classes += " very-active";
                        return classes;
                    })
                    .attr("r", d => {
                        const radius = calculateCircleRadius(d);
                        console.log(`🔍 DEBUG: Node ${d.stem}: importance=${d.importance}, radius=${radius}`);
                        return radius;
                    })
                    .attr("fill", d => d.color);
                console.log(`🔍 DEBUG: Created ${circles.size()} circles`);
            } else {
                console.log("🔍 DEBUG: Creating rectangles for hierarchical layout");
                // Use rectangles for hierarchical layout
                const rects = nodeSelection.append("rect")
                    .attr("class", d => {
                        let classes = "node-rect";
                        if (d.hotspot_score && d.hotspot_score > 0.5) classes += " hotspot";
                        if (d.change_classification === "very_high") classes += " very-active";
                        return classes;
                    })
                    .attr("width", d => d.width)
                    .attr("height", d => d.height)
                    .attr("x", d => -d.width/2)
                    .attr("y", d => -d.height/2)
                    .attr("fill", d => d.color);
                console.log(`🔍 DEBUG: Created ${rects.size()} rectangles`);
            }
        }
        
        // Helper function to calculate circle radius based on importance
        function calculateCircleRadius(d) {
            const baseRadius = 20;
            const importance = d.importance || 0;
            const importanceMultiplier = 1 + (importance * 1.5); // Scale up to 2.5x for max importance
            return Math.round(baseRadius * importanceMultiplier);
        }
        
        // Helper function to add importance indicators
        function addImportanceIndicators(nodeSelection) {
            // Only show indicators for rectangular nodes (hierarchical layout)
            if (currentLayout !== "force") {
                nodeSelection.filter(d => d.importance > 0.3)
                    .append("circle")
                    .attr("class", d => {
                        if (d.importance > 0.7) return "importance-indicator high";
                        if (d.importance > 0.5) return "importance-indicator medium";
                        return "importance-indicator low";
                    })
                    .attr("cx", d => d.width/2 - 8)
                    .attr("cy", d => -d.height/2 + 8)
                    .attr("r", 6);
            }
        }
        
        // Helper function to add hotspot indicators
        function addHotspotIndicators(nodeSelection) {
            // Only show indicators for rectangular nodes (hierarchical layout)
            if (currentLayout !== "force") {
                nodeSelection.filter(d => d.hotspot_score && d.hotspot_score > 0.4)
                    .append("circle")
                    .attr("class", "hotspot-indicator")
                    .attr("cx", d => -d.width/2 + 8)
                    .attr("cy", d => -d.height/2 + 8)
                    .attr("r", 4)
                    .attr("fill", "#ff3333")
                    .attr("stroke", "#ffffff")
                    .attr("stroke-width", 1);
            }
        }
        
        // Function to regenerate node shapes when layout changes
        function regenerateNodeShapes() {
            if (!window.graphElements || !window.graphElements.node) return;
            
            console.log(`🔄 DEBUG: Regenerating node shapes for ${currentLayout} layout`);
            
            // Remove existing shapes (rect or circle)
            window.graphElements.node.selectAll(".node-rect, .node-circle").remove();
            
            // Remove layout-specific indicators that only apply to hierarchical
            if (currentLayout === "force") {
                window.graphElements.node.selectAll(".importance-indicator, .hotspot-indicator").remove();
            }
            
            // Remove change badges so they can be repositioned
            window.graphElements.node.selectAll(".change-badge").remove();
            
            // Add new shapes based on current layout
            addNodeShapes(window.graphElements.node);
            
            // Re-add change frequency badges with correct positioning
            addChangeBadges(window.graphElements.node);
            
            // Re-add indicators for hierarchical layout
            if (currentLayout === "hierarchical") {
                addImportanceIndicators(window.graphElements.node);
                addHotspotIndicators(window.graphElements.node);
            }
        }
        
        // Helper function to add change frequency badges with layout-aware positioning
        function addChangeBadges(nodeSelection) {
            nodeSelection.filter(d => d.change_count && d.change_count > 0)
                .append("text")
                .attr("class", "change-badge")
                .attr("x", d => {
                    if (currentLayout === "force") {
                        // For circles, position badges at the right edge
                        const radius = calculateCircleRadius(d);
                        return radius - 8;
                    } else {
                        // For rectangles, use width-based positioning
                        return d.width/2 - 12;
                    }
                })
                .attr("y", d => {
                    if (currentLayout === "force") {
                        // For circles, position badges at the bottom edge
                        const radius = calculateCircleRadius(d);
                        return radius - 4;
                    } else {
                        // For rectangles, use height-based positioning
                        return d.height/2 - 4;
                    }
                })
                .attr("font-size", "10px")
                .attr("fill", "#666")
                .text(d => d.change_count);
        }
            
            const g = svg.append("g").attr("id", "main-group");
            
            // Setup zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 8])
                .on("zoom", (event) => {
                    g.attr("transform", event.transform);
                });
            svg.call(zoom);
            
            // Calculate initial layout
            const layout = calculateEnhancedHierarchicalLayout();
            
            // Create arrow markers
            createEnhancedArrowMarkers();
            
            // Create links
            const linkGroup = g.append("g").attr("class", "links");
            const link = linkGroup.selectAll("path")
                .data(graphData.edges)
                .enter().append("path")
                .attr("class", d => {
                    let classes = "link";
                    if (d.is_test_related) classes += " test-related";
                    return classes;
                })
                .attr("d", d => createEnhancedCubicBezierPath(d))
                .attr("marker-end", "url(#arrowhead)");
            
            // Create nodes
            const nodeGroup = g.append("g").attr("class", "nodes");
            const node = nodeGroup.selectAll("g")
                .data(graphData.nodes)
                .enter().append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${d.x},${d.y})`)
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // Add node shapes based on current layout type
            addNodeShapes(node);
            
            // Add importance indicators
            addImportanceIndicators(node);
            
            // Add hotspot indicators for frequently changing files
            addHotspotIndicators(node);
            
            // Add change frequency badges
            addChangeBadges(node);
            
            // Add node labels
            node.append("text")
                .attr("class", "node-label")
                .text(d => d.stem)
                .attr("dy", "-2px");
            
            // Add folder labels
            node.filter(d => d.folder !== "root")
                .append("text")
                .attr("class", "folder-label-text")
                .text(d => `(${d.folder})`)
                .attr("dy", "10px");
            
            // Setup event handlers
            node.on("click", handleEnhancedNodeClick)
                .on("mouseover", handleEnhancedMouseOver)
                .on("mouseout", handleEnhancedMouseOut);
            
            // Global click handler
            svg.on("click", function(event) {
                if (event.target === this) {
                    resetHighlighting();
                }
            });
            
            // Store references for later use
            window.graphElements = { node, link, g };
            
            // Initialize components
            setupAdvancedFilters();
            updateEnhancedControls();
            updateEnhancedStats();
            updateEnhancedVisibility();
            setupLayoutToggle();
            
            console.log("✅ Enhanced visualization initialized successfully");
        }

        // Enhanced arrow markers creation
        function createEnhancedArrowMarkers() {
            const defs = svg.select("defs").empty() ? svg.append("defs") : svg.select("defs");
            
            // Standard arrow
            defs.append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#666");
            
            // Highlighted arrow
            defs.append("marker")
                .attr("id", "arrowhead-highlighted")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ff6600");
            
            // Dimmed arrow
            defs.append("marker")
                .attr("id", "arrowhead-dimmed")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ccc");
        }
        
        // Enhanced event handlers
        function handleEnhancedNodeClick(event, d) {
            event.stopPropagation();
            highlightEnhancedDirectPath(d);
        }
        
        function handleEnhancedMouseOver(event, d) {
            // Calculate predecessors (incoming) and successors (outgoing)
            const predecessors = graphData.edges.filter(e => e.target_name === d.id).length;
            const successors = graphData.edges.filter(e => e.source_name === d.id).length;
            const predecessorNames = graphData.edges.filter(e => e.target_name === d.id)
                .map(e => {
                    const dep = graphData.nodes.find(n => n.id === e.source_name);
                    return dep ? dep.stem : e.source_name;
                }).join(", ");
            const successorNames = graphData.edges.filter(e => e.source_name === d.id)
                .map(e => {
                    const dep = graphData.nodes.find(n => n.id === e.target_name);
                    return dep ? dep.stem : e.target_name;
                }).join(", ");
            
            const importanceLevel = d.importance > 0.7 ? "High" : 
                                  d.importance > 0.5 ? "Medium" : 
                                  d.importance > 0.3 ? "Low" : "Minimal";
            
            tooltip.style("opacity", 1)
                .attr("aria-hidden", "false")
                .html(`
                    <strong>${d.stem}</strong><br/>
                    <strong>Folder:</strong> ${d.folder}<br/>
                    <strong>Importance:</strong> ${importanceLevel} (${(d.importance * 100).toFixed(1)}%)<br/>
                    <strong>Predecessors:</strong> ${predecessors} ${predecessorNames ? `<span style='color:#888'>[${predecessorNames}]</span>` : ''}<br/>
                    <strong>Successors:</strong> ${successors} ${successorNames ? `<span style='color:#888'>[${successorNames}]</span>` : ''}<br/>
                    <strong>File Size:</strong> ${(d.size / 1024).toFixed(1)}KB<br/>
                    ${d.is_test ? "<strong>Type:</strong> Test File<br/>" : ""}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }
        
        function handleEnhancedMouseOut() {
            tooltip.style("opacity", 0).attr("aria-hidden", "true");
        }
        
        // Enhanced highlighting
        function highlightEnhancedDirectPath(clickedNode) {
            selectedNode = clickedNode;
            const connected = findEnhancedConnections(clickedNode.id);
            
            // Reset all elements
            window.graphElements.node.classed("dimmed highlighted", false);
            window.graphElements.node.selectAll(".node-rect, .node-circle").classed("dimmed highlighted", false);
            window.graphElements.link
                .classed("dimmed highlighted", false)
                .attr("marker-end", "url(#arrowhead)");
            
            // Apply highlighting
            window.graphElements.node
                .classed("highlighted", d => connected.has(d.id))
                .classed("dimmed", d => !connected.has(d.id));
            
            window.graphElements.node.selectAll(".node-rect, .node-circle")
                .classed("highlighted", function() {
                    const nodeData = d3.select(this.parentNode).datum();
                    return connected.has(nodeData.id);
                })
                .classed("dimmed", function() {
                    const nodeData = d3.select(this.parentNode).datum();
                    return !connected.has(nodeData.id);
                });
            
            window.graphElements.link
                .classed("highlighted", d => connected.has(d.source_name) && connected.has(d.target_name))
                .classed("dimmed", d => !(connected.has(d.source_name) && connected.has(d.target_name)))
                .attr("marker-end", d => {
                    if (connected.has(d.source_name) && connected.has(d.target_name)) {
                        return "url(#arrowhead-highlighted)";
                    } else if (!(connected.has(d.source_name) && connected.has(d.target_name))) {
                        return "url(#arrowhead-dimmed)";
                    } else {
                        return "url(#arrowhead)";
                    }
                });
            
            highlightedNodes = connected;
        }
        
        function findEnhancedConnections(nodeId) {
            const connected = new Set([nodeId]);
            
            // Find all connections respecting current filters
            graphData.edges.forEach(edge => {
                if (!shouldShowEdge(edge)) return;
                
                if (edge.source_name === nodeId) {
                    connected.add(edge.target_name);
                }
                if (edge.target_name === nodeId) {
                    connected.add(edge.source_name);
                }
            });
            
            return connected;
        }
        
        function resetHighlighting() {
            selectedNode = null;
            highlightedNodes.clear();
            window.graphElements.node.classed("dimmed highlighted", false);
            window.graphElements.node.selectAll(".node-rect, .node-circle").classed("dimmed highlighted", false);
            window.graphElements.link
                .classed("dimmed highlighted", false)
                .attr("marker-end", "url(#arrowhead)");
        }
        
        // Enhanced drag functions with layout awareness
        function dragstarted(event, d) {
            if (currentLayout === "force" && simulation) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
            }
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
            d.x = event.x;
            d.y = event.y;
            
            if (currentLayout === "hierarchical") {
                updatePositions();
            }
            // For force layout, the simulation handles position updates
        }
        
        function dragended(event, d) {
            if (currentLayout === "force" && simulation) {
                if (!event.active) simulation.alphaTarget(0);
            }
            d.fx = null;
            d.fy = null;
        }
        
        function updatePositions() {
            const { node, link } = window.graphElements;
            if (!node || !link) return;
            
            node.attr("transform", d => `translate(${d.x},${d.y})`);
            
            if (currentLayout === "hierarchical") {
                link.attr("d", d => createEnhancedCubicBezierPath(d));
            } else {
                // For force layout, use the force layout position update
                updatePositionsForceLayout();
            }
        }
        
        // Enhanced visibility logic
        function shouldShowEdge(edge) {
            const sourceNode = graphData.nodes.find(n => n.id === edge.source_name);
            const targetNode = graphData.nodes.find(n => n.id === edge.target_name);
            
            if (!sourceNode || !targetNode) return false;
            if (!shouldShowNode(sourceNode) || !shouldShowNode(targetNode)) return false;
            
            if (!showTestDependencies && edge.is_test_related) {
                return false;
            }
            
            return true;
        }
        
        function shouldShowNode(node) {
            // Check folder visibility
            if (!checkedFolders.has(node.folder)) return false;
            
            // Check advanced filters
            // Count predecessors (incoming edges)
            const predecessors = graphData.edges.filter(e => e.target_name === node.id).length;
            if (predecessors > maxPredecessorsFilter) return false;
            
            // Count successors (outgoing edges)
            const successors = graphData.edges.filter(e => e.source_name === node.id).length;
            if (successors > maxSuccessorsFilter) return false;
            
            // Check file size (convert bytes to KB)
            const sizeKB = node.size / 1024;
            if (sizeKB > maxSizeFilter) return false;
            
            return true;
        }
        
        // Update visibility based on current filters
        function updateEnhancedVisibility() {
            if (!window.graphElements) return;
            
            // Update node visibility with advanced filtering
            window.graphElements.node
                .style("opacity", d => {
                    if (!shouldShowNode(d)) return 0.1;
                    if (!showTestDependencies && d.is_test) return 0.3;
                    return 1;
                })
                .style("display", d => shouldShowNode(d) ? "block" : "none");
            
            // Update link visibility
            window.graphElements.link
                .classed("hidden", d => !shouldShowEdge(d))
                .style("opacity", d => {
                    if (!shouldShowEdge(d)) return 0;
                    return d.is_test_related && !showTestDependencies ? 0.3 : 0.8;
                });
        }
        
        // Resize handler
        window.addEventListener("resize", function() {
            updateDimensions();
            
            // Recalculate layout if needed
            if (currentLayout === "hierarchical") {
                updateHierarchicalLayout();
            } else if (currentLayout === "force" && simulation) {
                // Update force center
                simulation.force("center", d3.forceCenter(width / 2, height / 2));
                simulation.alpha(0.3).restart();
            }
        });
        
        // Expose functions globally for access from other modules
        window.regenerateNodeShapes = regenerateNodeShapes;
        window.addNodeShapes = addNodeShapes;
        window.calculateCircleRadius = calculateCircleRadius;
        window.addChangeBadges = addChangeBadges;
    """
