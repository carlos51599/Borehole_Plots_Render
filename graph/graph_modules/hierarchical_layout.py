"""
Hierarchical Layout Module
=========================

Hierarchical layout algorithms for dependency graph visualization.
Implements dependency-aware positioning with enhanced level calculation.
"""


def get_hierarchical_layout_js() -> str:
    """
    Get JavaScript code for hierarchical layout functionality.

    Returns:
        str: JavaScript code for hierarchical layout system
    """
    return """
        // Enhanced hierarchical layout calculation with dependency-aware positioning
        function calculateEnhancedHierarchicalLayout() {
            console.log("📐 Calculating enhanced hierarchical layout...");
            
            // Calculate node dimensions with importance weighting
            graphData.nodes.forEach(d => {
                const importance = d.importance || 0;
                const baseWidth = Math.max(120, d.stem.length * 8 + 20);
                const baseHeight = d.folder !== "root" ? 40 : 30;
                // Scale size based on importance
                const importanceScale = 1 + (importance * 0.5);
                d.width = Math.round(baseWidth * importanceScale);
                d.height = Math.round(baseHeight * importanceScale);
            });
            
            // Build adjacency maps
            const incomingEdges = new Map();
            const outgoingEdges = new Map();
            graphData.nodes.forEach(node => {
                incomingEdges.set(node.index, []);
                outgoingEdges.set(node.index, []);
            });
            
            graphData.edges.forEach(edge => {
                if (shouldShowEdge(edge)) {
                    incomingEdges.get(edge.target).push(edge.source);
                    outgoingEdges.get(edge.source).push(edge.target);
                }
            });
            
            // Enhanced topological sort with cycle handling
            const levels = [];
            const nodeToLevel = new Map();
            const visited = new Set();
            const inDegree = new Map();
            
            // Initialize in-degree counts
            graphData.nodes.forEach(node => {
                inDegree.set(node.index, incomingEdges.get(node.index).length);
            });
            
            let currentLevel = 0;
            while (visited.size < graphData.nodes.length) {
                levels[currentLevel] = [];
                const candidateNodes = [];
                
                // Find nodes with no incoming edges
                for (const node of graphData.nodes) {
                    if (!visited.has(node.index) && inDegree.get(node.index) === 0) {
                        candidateNodes.push(node);
                    }
                }
                
                // If no candidates (cycle detected), pick node with lowest in-degree
                if (candidateNodes.length === 0) {
                    const remainingNodes = graphData.nodes.filter(n => !visited.has(n.index));
                    if (remainingNodes.length > 0) {
                        const minInDegree = Math.min(...remainingNodes.map(n => inDegree.get(n.index)));
                        const nodeWithMinDegree = remainingNodes.find(n => inDegree.get(n.index) === minInDegree);
                        candidateNodes.push(nodeWithMinDegree);
                    }
                }
                
                // Sort candidates by importance (most important first)
                candidateNodes.sort((a, b) => (b.importance || 0) - (a.importance || 0));
                
                // Add candidates to current level
                for (const node of candidateNodes) {
                    levels[currentLevel].push(node.index);
                    nodeToLevel.set(node.index, currentLevel);
                    visited.add(node.index);
                    
                    // Reduce in-degree of target nodes
                    for (const targetIdx of outgoingEdges.get(node.index)) {
                        if (!visited.has(targetIdx)) {
                            inDegree.set(targetIdx, Math.max(0, inDegree.get(targetIdx) - 1));
                        }
                    }
                }
                
                currentLevel++;
                if (currentLevel > graphData.nodes.length) break; // Safety check
            }
            
            // Enhanced position assignment with better spacing
            const margin = 60;
            const levelWidth = Math.max(300, (width - 2 * margin) / Math.max(1, levels.length));
            const nodeSpacing = 45;
            
            levels.forEach((level, levelIndex) => {
                const x = margin + levelIndex * levelWidth;
                
                // Sort nodes in level by importance and folder
                const sortedLevel = level.map(idx => graphData.nodes[idx])
                    .sort((a, b) => {
                        // First by folder to group related nodes
                        if (a.folder !== b.folder) {
                            return a.folder.localeCompare(b.folder);
                        }
                        // Then by importance
                        return (b.importance || 0) - (a.importance || 0);
                    });
                
                const totalHeight = sortedLevel.length * nodeSpacing;
                const startY = Math.max(margin, (height - totalHeight) / 2);
                
                sortedLevel.forEach((node, positionIndex) => {
                    node.x = x;
                    node.y = startY + positionIndex * nodeSpacing;
                });
            });
            
            console.log(`✅ Hierarchical layout complete: ${levels.length} levels, ${visited.size} nodes positioned`);
            return { levels, nodeToLevel };
        }
        
        // Animate nodes to hierarchical positions
        function animateToHierarchicalLayout() {
            if (!window.graphElements) return;
            
            console.log("🎬 Animating to hierarchical layout...");
            const { node, link } = window.graphElements;
            
            // Animate nodes to hierarchical positions
            node.transition()
                .duration(1000)
                .ease(d3.easeQuadInOut)
                .attr("transform", d => `translate(${d.x},${d.y})`);
            
            // Animate links to hierarchical curves
            link.transition()
                .duration(1000)
                .ease(d3.easeQuadInOut)
                .attr("d", d => createEnhancedCubicBezierPath(d));
                
            console.log("✅ Hierarchical animation complete");
        }
        
        // Enhanced cubic Bézier curve generation for hierarchical layout
        function createEnhancedCubicBezierPath(d) {
            const source = graphData.nodes[d.source];
            const target = graphData.nodes[d.target];
            
            if (!source || !target) return "";
            
            const sourceX = source.x + (source.width || 120) / 2;
            const sourceY = source.y;
            const targetX = target.x - (target.width || 120) / 2;
            const targetY = target.y;
            
            const dx = targetX - sourceX;
            const dy = targetY - sourceY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            // Adaptive curve parameters based on distance and direction
            const curveFactor = Math.min(0.6, Math.max(0.2, distance / 400));
            const offsetFactor = Math.abs(dy) / 100;
            
            // Calculate control points for smooth curves
            const cp1x = sourceX + dx * 0.3 + offsetFactor * 20;
            const cp1y = sourceY + dy * 0.1;
            const cp2x = targetX - dx * 0.3 - offsetFactor * 20;
            const cp2y = targetY - dy * 0.1;
            
            return `M${sourceX},${sourceY} C${cp1x},${cp1y} ${cp2x},${cp2y} ${targetX},${targetY}`;
        }
        
        // Handle hierarchical layout updates when filters change
        function updateHierarchicalLayout() {
            if (currentLayout !== "hierarchical") return;
            
            console.log("🔄 Updating hierarchical layout after filter change...");
            
            // Recalculate layout with current visibility settings
            const layout = calculateEnhancedHierarchicalLayout();
            
            // Update positions with animation
            if (window.graphElements) {
                const { node, link } = window.graphElements;
                
                node.transition()
                    .duration(500)
                    .ease(d3.easeQuadInOut)
                    .attr("transform", d => `translate(${d.x},${d.y})`);
                
                link.transition()
                    .duration(500)
                    .ease(d3.easeQuadInOut)
                    .attr("d", d => createEnhancedCubicBezierPath(d));
            }
            
            console.log("✅ Hierarchical layout update complete");
        }
    """
