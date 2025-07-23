"""
Force-Directed Layout Module
===========================

Force-directed layout algorithms using D3.js force simulation.
Implements physics-based node positioning with importance-weighted forces.
"""


def get_force_directed_layout_js() -> str:
    """
    Get JavaScript code for force-directed layout functionality.

    Returns:
        str: JavaScript code for force-directed layout system
    """
    return """
        // Force-directed layout using D3 force simulation
        function initializeForceDirectedLayout() {
            console.log("🌐 Initializing force-directed layout...");
            
            // Calculate node dimensions for force layout
            graphData.nodes.forEach(d => {
                const importance = d.importance || 0;
                const baseWidth = Math.max(120, d.stem.length * 8 + 20);
                const baseHeight = d.folder !== "root" ? 40 : 30;
                
                // Scale size based on importance
                const importanceScale = 1 + (importance * 0.5);
                d.width = Math.round(baseWidth * importanceScale);
                d.height = Math.round(baseHeight * importanceScale);
                
                // Set initial positions if not set
                if (d.x === undefined) d.x = width / 2 + (Math.random() - 0.5) * 200;
                if (d.y === undefined) d.y = height / 2 + (Math.random() - 0.5) * 200;
            });
            
            // Create filtered links for simulation
            const validLinks = graphData.edges
                .filter(edge => shouldShowEdge(edge))
                .map(edge => ({
                    source: edge.source,
                    target: edge.target,
                    strength: 0.5 + (graphData.nodes[edge.source]?.importance || 0) * 0.3
                }));
            
            // Stop any existing simulation
            if (simulation) {
                simulation.stop();
            }
            
            // Create force simulation with enhanced parameters
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(validLinks)
                    .id(d => d.index)
                    .distance(d => {
                        const sourceNode = graphData.nodes[d.source.index || d.source];
                        const targetNode = graphData.nodes[d.target.index || d.target];
                        const baseDistance = 150;
                        const importanceBonus = ((sourceNode?.importance || 0) + (targetNode?.importance || 0)) * 50;
                        return baseDistance + importanceBonus;
                    })
                    .strength(d => d.strength || 0.5)
                )
                .force("charge", d3.forceManyBody()
                    .strength(d => {
                        const importance = d.importance || 0;
                        const baseCharge = -800;
                        const importanceMultiplier = 1 + importance * 2;
                        return baseCharge * importanceMultiplier;
                    })
                )
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide()
                    .radius(d => {
                        // Use circle radius for force-directed layout, rectangle dimensions for hierarchical
                        const baseRadius = 20;
                        const importance = d.importance || 0;
                        const importanceMultiplier = 1 + (importance * 1.5);
                        return baseRadius * importanceMultiplier + 10; // Add padding
                    })
                    .strength(0.7)
                )
                .force("x", d3.forceX(width / 2).strength(0.1))
                .force("y", d3.forceY(height / 2).strength(0.1));
            
            // Update positions during simulation
            simulation.on("tick", () => {
                updatePositionsForceLayout();
            });
            
            // Reduce alpha target for smoother convergence
            simulation.alphaTarget(0.1).restart();
            
            console.log("✅ Force-directed layout initialized");
            return simulation;
        }
        
        // Update positions for force layout
        function updatePositionsForceLayout() {
            if (!window.graphElements) return;
            
            const { node, link } = window.graphElements;
            
            // Update node positions
            node.attr("transform", d => `translate(${d.x},${d.y})`);
            
            // Update link paths with force layout positions
            link.attr("d", d => {
                const source = d.source.x !== undefined ? d.source : graphData.nodes[d.source];
                const target = d.target.x !== undefined ? d.target : graphData.nodes[d.target];
                
                if (!source || !target) return "";
                
                return createForceDirectedLinkPath({
                    source: source.index,
                    target: target.index
                });
            });
        }
        
        // Create optimized link paths for force-directed layout
        function createForceDirectedLinkPath(d) {
            const source = graphData.nodes[d.source];
            const target = graphData.nodes[d.target];
            
            if (!source || !target) return "";
            
            const sourceX = source.x;
            const sourceY = source.y;
            const targetX = target.x;
            const targetY = target.y;
            
            // For force layout, use simpler straight lines or gentle curves
            const dx = targetX - sourceX;
            const dy = targetY - sourceY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
                // Short distances: straight line
                return `M${sourceX},${sourceY} L${targetX},${targetY}`;
            } else {
                // Longer distances: gentle curve
                const midX = (sourceX + targetX) / 2;
                const midY = (sourceY + targetY) / 2;
                const perpX = -dy / distance * 20; // Perpendicular offset
                const perpY = dx / distance * 20;
                const cpX = midX + perpX;
                const cpY = midY + perpY;
                
                return `M${sourceX},${sourceY} Q${cpX},${cpY} ${targetX},${targetY}`;
            }
        }
        
        // Restart force simulation with new parameters
        function restartForceSimulation() {
            if (!simulation || currentLayout !== "force") return;
            
            console.log("🔄 Restarting force simulation...");
            
            // Update links based on current visibility
            const validLinks = graphData.edges
                .filter(edge => shouldShowEdge(edge))
                .map(edge => ({
                    source: edge.source,
                    target: edge.target,
                    strength: 0.5 + (graphData.nodes[edge.source]?.importance || 0) * 0.3
                }));
            
            // Update force simulation
            simulation.force("link")
                .links(validLinks);
            
            // Restart with higher alpha for more movement
            simulation.alpha(0.3).restart();
            
            console.log("✅ Force simulation restarted");
        }
        
        // Stop force simulation
        function stopForceSimulation() {
            if (simulation) {
                console.log("⏹️ Stopping force simulation...");
                simulation.stop();
                simulation = null;
                console.log("✅ Force simulation stopped");
            }
        }
        
        // Apply force-directed clustering by folder
        function applyFolderClustering() {
            if (!simulation || currentLayout !== "force") return;
            
            console.log("📁 Applying folder clustering...");
            
            // Create folder-based positioning forces
            const folderCenters = {};
            const folders = [...new Set(graphData.nodes.map(n => n.folder))];
            
            // Calculate cluster centers in a circle
            folders.forEach((folder, index) => {
                const angle = (index / folders.length) * 2 * Math.PI;
                const radius = Math.min(width, height) * 0.3;
                folderCenters[folder] = {
                    x: width / 2 + radius * Math.cos(angle),
                    y: height / 2 + radius * Math.sin(angle)
                };
            });
            
            // Add clustering force
            simulation.force("cluster", d3.forceX(d => folderCenters[d.folder]?.x || width / 2).strength(0.05))
                     .force("clusterY", d3.forceY(d => folderCenters[d.folder]?.y || height / 2).strength(0.05));
            
            // Restart simulation
            simulation.alpha(0.3).restart();
            
            console.log("✅ Folder clustering applied");
        }
        
        // Remove folder clustering
        function removeFolderClustering() {
            if (!simulation) return;
            
            console.log("🔄 Removing folder clustering...");
            
            simulation.force("cluster", null)
                     .force("clusterY", null);
            
            simulation.alpha(0.3).restart();
            
            console.log("✅ Folder clustering removed");
        }
        
        // Adjust force parameters based on graph size
        function adjustForceParameters() {
            if (!simulation) return;
            
            const nodeCount = graphData.nodes.length;
            const edgeCount = graphData.edges.filter(shouldShowEdge).length;
            
            console.log(`⚙️ Adjusting force parameters for ${nodeCount} nodes, ${edgeCount} edges`);
            
            // Adjust charge strength based on node count
            const baseCharge = nodeCount > 50 ? -300 : -800;
            simulation.force("charge", d3.forceManyBody()
                .strength(d => {
                    const importance = d.importance || 0;
                    const importanceMultiplier = 1 + importance * 2;
                    return baseCharge * importanceMultiplier;
                })
            );
            
            // Adjust link distance based on density
            const density = edgeCount / Math.max(1, nodeCount - 1);
            const baseDistance = density > 2 ? 120 : 150;
            
            simulation.force("link")
                .distance(d => {
                    const sourceNode = graphData.nodes[d.source.index || d.source];
                    const targetNode = graphData.nodes[d.target.index || d.target];
                    const importanceBonus = ((sourceNode?.importance || 0) + (targetNode?.importance || 0)) * 30;
                    return baseDistance + importanceBonus;
                });
            
            console.log(`✅ Force parameters adjusted: charge=${baseCharge}, distance=${baseDistance}`);
        }
    """
