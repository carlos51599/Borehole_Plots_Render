"""
Graph Controls Module
====================

JavaScript UI controls, event handling, and filter management.
Handles layout switching, folder toggles, advanced filters, and statistics.
"""


def get_graph_controls_js() -> str:
    """
    Get JavaScript code for UI controls and event handling.

    Returns:
        str: JavaScript code for controls and interaction
    """
    return """
        // Theme management
        let currentTheme = localStorage.getItem('dependency-graph-theme') || 'light';
        
        function initializeTheme() {
            document.documentElement.setAttribute('data-theme', currentTheme);
            updateThemeToggle();
        }
        
        function toggleTheme() {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', currentTheme);
            localStorage.setItem('dependency-graph-theme', currentTheme);
            updateThemeToggle();
            
            // Update node and link colors for the current theme
            if (typeof updateVisualizationForTheme === 'function') {
                updateVisualizationForTheme();
            }
        }
        
        function updateThemeToggle() {
            const toggle = document.querySelector('.theme-toggle');
            if (toggle) {
                const icon = toggle.querySelector('.theme-icon');
                const text = toggle.querySelector('.theme-text');
                if (currentTheme === 'dark') {
                    icon.textContent = '☀️';
                    text.textContent = 'Light';
                } else {
                    icon.textContent = '🌙';
                    text.textContent = 'Dark';
                }
            }
        }
        
        // Enhanced controls management
        function updateEnhancedControls() {
            const container = d3.select("#folder-controls");
            container.selectAll("*").remove();
            
            Object.entries(graphData.subfolder_info)
                .sort((a, b) => Number(b[1].count) - Number(a[1].count))
                .forEach(([folder, info]) => {
                const item = container.append("div")
                    .attr("class", "folder-item")
                    .attr("role", "checkbox")
                    .attr("aria-checked", checkedFolders.has(folder))
                    .attr("tabindex", "0")
                    .on("click", () => toggleFolder(folder))
                    .on("keydown", function(event) {
                        if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            toggleFolder(folder);
                        }
                    });
                
                item.append("span")
                    .attr("class", "folder-checkbox")
                    .text(checkedFolders.has(folder) ? "☑" : "☐");
                
                item.append("div")
                    .attr("class", "folder-color")
                    .style("background-color", info.color);
                
                const labelText = `${folder} <span class="folder-count">(${info.count} modules)</span>`;
                const testText = info.test_modules && info.test_modules.length > 0 ? 
                    ` <span class="test-count">[${info.test_modules.length} tests]</span>` : "";
                
                item.append("span")
                    .attr("class", "folder-label")
                    .html(labelText + testText);
            });
            
            // Test toggle
            const testToggle = d3.select("#test-toggle");
            testToggle.select(".folder-checkbox")
                .text(showTestDependencies ? "☑" : "☐");
            
            testToggle.on("click", toggleTestDependencies);
            
            // Update "Select All" toggle
            const allFolders = Object.keys(graphData.subfolder_info);
            const allSelected = allFolders.every(folder => checkedFolders.has(folder));
            const selectAllToggle = d3.select("#select-all-toggle");
            selectAllToggle.select(".folder-checkbox")
                .text(allSelected ? "☑" : "☐");
        }
        
        function updateEnhancedStats() {
            const visibleNodes = graphData.nodes.filter(n => shouldShowNode(n));
            const visibleEdges = graphData.edges.filter(e => shouldShowEdge(e));
            const testFiles = visibleNodes.filter(n => n.is_test).length;
            const crossFolderEdges = visibleEdges.filter(e => e.is_cross_folder).length;
            
            const stats = [
                { value: graphData.nodes.length, label: "Total Files" },
                { value: visibleNodes.length, label: "Visible Files" },
                { value: graphData.edges.length, label: "Edges" },
                { value: visibleEdges.length, label: "Visible Edges" },
                { value: Object.keys(graphData.subfolder_info).length, label: "Directories" },
                { value: testFiles, label: "Test Files" }
            ];
            
            const container = d3.select("#stats-content");
            container.selectAll("*").remove();
            
            stats.forEach(stat => {
                const item = container.append("div").attr("class", "stat-item");
                item.append("div").attr("class", "stat-value").text(stat.value);
                item.append("div").attr("class", "stat-label").text(stat.label);
            });
        }
        
        function toggleFolder(folder) {
            if (checkedFolders.has(folder)) {
                checkedFolders.delete(folder);
            } else {
                checkedFolders.add(folder);
            }
            updateEnhancedControls();
            updateEnhancedVisibility();
            updateEnhancedStats();
            
            // Update layout if needed
            if (currentLayout === "hierarchical") {
                updateHierarchicalLayout();
            } else if (currentLayout === "force") {
                restartForceSimulation();
            }
        }
        
        function toggleTestDependencies() {
            showTestDependencies = !showTestDependencies;
            updateEnhancedControls();
            updateEnhancedVisibility();
            updateEnhancedStats();
            
            // Update layout if needed
            if (currentLayout === "hierarchical") {
                updateHierarchicalLayout();
            } else if (currentLayout === "force") {
                restartForceSimulation();
            }
        }
        
        function resetAllFilters() {
            checkedFolders = new Set(Object.keys(graphData.subfolder_info));
            showTestDependencies = true;
            
            // Reset advanced filters
            maxPredecessorsFilter = 20;
            maxSuccessorsFilter = 20;
            maxSizeFilter = 100;
            
            // Update UI controls
            document.getElementById('predecessors-filter').value = maxPredecessorsFilter;
            document.getElementById('successors-filter').value = maxSuccessorsFilter;
            document.getElementById('size-filter').value = maxSizeFilter;
            updateFilterLabels();
            
            resetHighlighting();
            updateEnhancedControls();
            updateEnhancedVisibility();
            updateEnhancedStats();
            
            // Update layout
            if (currentLayout === "hierarchical") {
                updateHierarchicalLayout();
            } else if (currentLayout === "force") {
                restartForceSimulation();
            }
        }
        
        // Advanced filter functions
        function updateFilterLabels() {
            document.getElementById('predecessors-filter-value').textContent = maxPredecessorsFilter;
            document.getElementById('successors-filter-value').textContent = maxSuccessorsFilter;
            document.getElementById('size-filter-value').textContent = maxSizeFilter;
        }
        
        function setupAdvancedFilters() {
            // Predecessors filter
            const predecessorsSlider = document.getElementById('predecessors-filter');
            predecessorsSlider.addEventListener('input', function() {
                maxPredecessorsFilter = parseInt(this.value);
                updateFilterLabels();
                updateEnhancedVisibility();
                updateEnhancedStats();
                
                if (currentLayout === "hierarchical") {
                    updateHierarchicalLayout();
                } else if (currentLayout === "force") {
                    restartForceSimulation();
                }
            });
            
            // Successors filter  
            const successorsSlider = document.getElementById('successors-filter');
            successorsSlider.addEventListener('input', function() {
                maxSuccessorsFilter = parseInt(this.value);
                updateFilterLabels();
                updateEnhancedVisibility();
                updateEnhancedStats();
                
                if (currentLayout === "hierarchical") {
                    updateHierarchicalLayout();
                } else if (currentLayout === "force") {
                    restartForceSimulation();
                }
            });
            
            // Size filter
            const sizeSlider = document.getElementById('size-filter');
            sizeSlider.addEventListener('input', function() {
                maxSizeFilter = parseInt(this.value);
                updateFilterLabels();
                updateEnhancedVisibility();
                updateEnhancedStats();
                
                if (currentLayout === "hierarchical") {
                    updateHierarchicalLayout();
                } else if (currentLayout === "force") {
                    restartForceSimulation();
                }
            });
            
            // Select all toggle
            const selectAllToggle = document.getElementById('select-all-toggle');
            selectAllToggle.addEventListener('click', function() {
                const allFolders = Object.keys(graphData.subfolder_info);
                const allSelected = allFolders.every(folder => checkedFolders.has(folder));
                
                if (allSelected) {
                    checkedFolders.clear();
                } else {
                    checkedFolders = new Set(allFolders);
                }
                
                updateEnhancedControls();
                updateEnhancedVisibility();
                updateEnhancedStats();
                
                if (currentLayout === "hierarchical") {
                    updateHierarchicalLayout();
                } else if (currentLayout === "force") {
                    restartForceSimulation();
                }
            });
            
            updateFilterLabels();
        }
        
        // Switch between hierarchical and force-directed layouts
        function switchLayout(newLayout) {
            if (newLayout === currentLayout) return;
            
            console.log(`🔄 Switching from ${currentLayout} to ${newLayout} layout`);
            currentLayout = newLayout;
            
            // Update toggle UI
            const toggleSwitch = document.getElementById('toggle-switch');
            const layoutIndicator = document.getElementById('layout-indicator');
            
            if (newLayout === "force") {
                toggleSwitch.classList.add('active');
                layoutIndicator.textContent = "Current: Force-Directed Layout";
                
                // Initialize force-directed layout
                initializeForceDirectedLayout();
                
            } else {
                toggleSwitch.classList.remove('active');
                layoutIndicator.textContent = "Current: Hierarchical Layout";
                
                // Stop force simulation
                stopForceSimulation();
                
                // Recalculate hierarchical layout
                const layout = calculateEnhancedHierarchicalLayout();
                
                // Animate to hierarchical positions
                animateToHierarchicalLayout();
            }
        }
        
        // Setup layout toggle functionality
        function setupLayoutToggle() {
            const toggleSwitch = document.getElementById('toggle-switch');
            const layoutToggle = document.getElementById('layout-toggle');
            
            function handleToggle() {
                const newLayout = currentLayout === "hierarchical" ? "force" : "hierarchical";
                switchLayout(newLayout);
            }
            
            toggleSwitch.addEventListener('click', handleToggle);
            layoutToggle.addEventListener('click', function(event) {
                if (event.target === toggleSwitch || event.target.closest('.toggle-switch')) {
                    return; // Let the toggle switch handle it
                }
                handleToggle();
            });
            
            // Keyboard accessibility
            toggleSwitch.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    handleToggle();
                }
            });
            
            toggleSwitch.setAttribute('tabindex', '0');
            toggleSwitch.setAttribute('role', 'switch');
            toggleSwitch.setAttribute('aria-checked', 'false');
        }
        
        // Export/import functions for saving/loading graph state
        function exportGraphState() {
            const state = {
                checkedFolders: Array.from(checkedFolders),
                showTestDependencies: showTestDependencies,
                maxImportsFilter: maxImportsFilter,
                maxDependenciesFilter: maxDependenciesFilter,
                maxSizeFilter: maxSizeFilter,
                currentLayout: currentLayout,
                selectedNode: selectedNode?.id || null,
                timestamp: new Date().toISOString()
            };
            
            const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dependency-graph-state.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log("📤 Graph state exported");
        }
        
        function importGraphState(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const state = JSON.parse(e.target.result);
                    
                    // Restore state
                    checkedFolders = new Set(state.checkedFolders || []);
                    showTestDependencies = state.showTestDependencies !== undefined ? state.showTestDependencies : true;
                    maxImportsFilter = state.maxImportsFilter || 20;
                    maxDependenciesFilter = state.maxDependenciesFilter || 20;
                    maxSizeFilter = state.maxSizeFilter || 100;
                    
                    // Update UI
                    document.getElementById('imports-filter').value = maxImportsFilter;
                    document.getElementById('dependencies-filter').value = maxDependenciesFilter;
                    document.getElementById('size-filter').value = maxSizeFilter;
                    updateFilterLabels();
                    
                    updateEnhancedControls();
                    updateEnhancedVisibility();
                    updateEnhancedStats();
                    
                    // Restore layout
                    if (state.currentLayout && state.currentLayout !== currentLayout) {
                        switchLayout(state.currentLayout);
                    }
                    
                    console.log("📥 Graph state imported from", state.timestamp);
                } catch (error) {
                    console.error("❌ Failed to import graph state:", error);
                    alert("Failed to import graph state. Please check the file format.");
                }
            };
            reader.readAsText(file);
        }
        
        // Search functionality
        function setupSearchFunctionality() {
            const searchInput = document.getElementById('search-input');
            if (!searchInput) return;
            
            searchInput.addEventListener('input', function() {
                const query = this.value.toLowerCase().trim();
                
                if (query === '') {
                    resetHighlighting();
                    return;
                }
                
                // Find matching nodes
                const matchingNodes = graphData.nodes.filter(node => 
                    node.stem.toLowerCase().includes(query) ||
                    node.folder.toLowerCase().includes(query) ||
                    node.name.toLowerCase().includes(query)
                );
                
                if (matchingNodes.length > 0) {
                    // Highlight matching nodes
                    const matchingIds = new Set(matchingNodes.map(n => n.id));
                    
                    window.graphElements.node
                        .classed("highlighted", d => matchingIds.has(d.id))
                        .classed("dimmed", d => !matchingIds.has(d.id));
                    
                    window.graphElements.node.selectAll(".node-rect")
                        .classed("highlighted", function() {
                            const nodeData = d3.select(this.parentNode).datum();
                            return matchingIds.has(nodeData.id);
                        })
                        .classed("dimmed", function() {
                            const nodeData = d3.select(this.parentNode).datum();
                            return !matchingIds.has(nodeData.id);
                        });
                    
                    window.graphElements.link.classed("dimmed", true);
                }
            });
        }
        
        // Performance monitoring
        function setupPerformanceMonitoring() {
            let frameCount = 0;
            let lastTime = performance.now();
            
            function updateFPS() {
                const now = performance.now();
                frameCount++;
                
                if (now - lastTime >= 1000) {
                    const fps = Math.round(frameCount * 1000 / (now - lastTime));
                    const fpsElement = document.getElementById('fps-counter');
                    if (fpsElement) {
                        fpsElement.textContent = `FPS: ${fps}`;
                    }
                    
                    frameCount = 0;
                    lastTime = now;
                }
                
                requestAnimationFrame(updateFPS);
            }
            
            requestAnimationFrame(updateFPS);
        }
    """
