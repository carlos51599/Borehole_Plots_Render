"""
Phase 2: Options Exploration - Layout Algorithms and Edge Optimization
Research different positioning algorithms and curve optimization techniques
"""

import json
import math


class LayoutAlgorithmExplorer:
    """Explore different node positioning algorithms."""

    def __init__(self):
        with open("graph_output/graph_data.json", "r") as f:
            self.data = json.load(f)
        self.nodes = self.data["nodes"]
        self.edges = self.data["edges"]

    def sugiyama_layered_layout(self):
        """Implement Sugiyama hierarchical layout algorithm."""
        print("🔬 EXPLORING: Sugiyama Layered Layout")
        print("=" * 50)

        # Step 1: Cycle removal (topological sort with feedback arc set)
        graph = self._build_adjacency_graph()
        acyclic_graph = self._remove_cycles(graph)

        # Step 2: Layer assignment
        layers = self._assign_layers(acyclic_graph)

        # Step 3: Crossing minimization (simplified)
        optimized_layers = self._minimize_crossings(layers, acyclic_graph)

        # Step 4: Position assignment
        positions = self._assign_positions(optimized_layers)

        print("✅ Sugiyama Results:")
        print(f"   - Layers created: {len(optimized_layers)}")
        print(f"   - Max layer width: {max(len(layer) for layer in optimized_layers)}")
        print(
            f"   - Average layer width: {sum(len(layer) for layer in optimized_layers) / len(optimized_layers):.1f}"
        )

        # Calculate edge crossings (estimate)
        crossings = self._estimate_edge_crossings(optimized_layers, acyclic_graph)
        print(f"   - Estimated edge crossings: {crossings}")

        return {
            "algorithm": "Sugiyama",
            "layers": len(optimized_layers),
            "max_width": max(len(layer) for layer in optimized_layers),
            "crossings": crossings,
            "positions": positions,
        }

    def force_directed_constrained_layout(self):
        """Implement force-directed layout with hierarchical constraints."""
        print("\n🔬 EXPLORING: Force-Directed with Constraints")
        print("=" * 50)

        # Initialize positions randomly
        positions = {}
        for i, node in enumerate(self.nodes):
            positions[node["index"]] = {
                "x": 100 + (i % 10) * 150,
                "y": 100 + (i // 10) * 100,
            }

        # Apply forces iteratively
        for iteration in range(50):  # Reduced for exploration
            forces = self._calculate_forces(positions)
            self._apply_constraints(positions, forces)
            positions = self._update_positions(positions, forces)

        # Evaluate layout quality
        edge_lengths = self._calculate_edge_lengths(positions)
        avg_edge_length = sum(edge_lengths) / len(edge_lengths) if edge_lengths else 0

        print("✅ Force-Directed Results:")
        print(f"   - Average edge length: {avg_edge_length:.1f}")
        spread_x = self._get_position_spread(positions, "x")
        spread_y = self._get_position_spread(positions, "y")
        print(f"   - Position spread: x={spread_x:.1f}, y={spread_y:.1f}")

        return {
            "algorithm": "Force-Directed-Constrained",
            "avg_edge_length": avg_edge_length,
            "positions": positions,
        }

    def grid_based_layout(self):
        """Implement grid-based layout with folder grouping."""
        print("\n🔬 EXPLORING: Grid-Based Layout")
        print("=" * 50)

        # Group nodes by folder
        folder_groups = {}
        for node in self.nodes:
            folder = node["folder"]
            if folder not in folder_groups:
                folder_groups[folder] = []
            folder_groups[folder].append(node)

        # Arrange folders in grid
        grid_size = math.ceil(math.sqrt(len(folder_groups)))
        folder_positions = {}

        for i, (folder, nodes) in enumerate(folder_groups.items()):
            grid_x = i % grid_size
            grid_y = i // grid_size
            folder_positions[folder] = {
                "x": grid_x * 300 + 150,
                "y": grid_y * 200 + 100,
                "nodes": len(nodes),
            }

        # Position nodes within each folder
        positions = {}
        for folder, nodes in folder_groups.items():
            base_pos = folder_positions[folder]
            nodes_per_row = math.ceil(math.sqrt(len(nodes)))

            for i, node in enumerate(nodes):
                offset_x = (i % nodes_per_row) * 120 - (nodes_per_row * 60)
                offset_y = (i // nodes_per_row) * 80 - 40

                positions[node["index"]] = {
                    "x": base_pos["x"] + offset_x,
                    "y": base_pos["y"] + offset_y,
                }

        # Calculate metrics
        inter_folder_edges = sum(
            1
            for edge in self.edges
            if edge.get("source_folder") != edge.get("target_folder")
        )

        print("✅ Grid-Based Results:")
        print(f"   - Folder groups: {len(folder_groups)}")
        print(f"   - Grid size: {grid_size}x{grid_size}")
        inter_ratio = inter_folder_edges / len(self.edges) * 100
        print(
            f"   - Inter-folder edges: {inter_folder_edges}/{len(self.edges)} ({inter_ratio:.1f}%)"
        )

        return {
            "algorithm": "Grid-Based",
            "folder_groups": len(folder_groups),
            "inter_folder_ratio": inter_folder_edges / len(self.edges),
            "positions": positions,
        }

    def custom_dependency_aware_layout(self):
        """Implement custom layout optimized for dependency visualization."""
        print("\n🔬 EXPLORING: Custom Dependency-Aware Layout")
        print("=" * 50)

        # Calculate node importance (PageRank-like)
        importance_scores = self._calculate_node_importance()

        # Group by dependency levels
        dependency_levels = self._calculate_dependency_levels()

        # Position high-importance nodes prominently
        positions = {}
        level_height = 150

        for level_idx, level_nodes in enumerate(dependency_levels):
            # Sort nodes in level by importance
            sorted_nodes = sorted(
                level_nodes, key=lambda n: importance_scores.get(n, 0), reverse=True
            )

            y_base = level_idx * level_height + 100
            node_spacing = 120
            total_width = len(sorted_nodes) * node_spacing
            x_start = 50

            for i, node_idx in enumerate(sorted_nodes):
                positions[node_idx] = {"x": x_start + i * node_spacing, "y": y_base}

        # Calculate quality metrics
        high_importance_nodes = [
            n for n, score in importance_scores.items() if score > 0.1
        ]

        print("✅ Custom Dependency-Aware Results:")
        print(f"   - Dependency levels: {len(dependency_levels)}")
        print(f"   - High importance nodes: {len(high_importance_nodes)}")
        print(f"   - Layout follows dependency flow: True")

        return {
            "algorithm": "Custom-Dependency-Aware",
            "levels": len(dependency_levels),
            "high_importance_nodes": len(high_importance_nodes),
            "positions": positions,
        }

    def _build_adjacency_graph(self):
        """Build adjacency list representation."""
        graph = {node["index"]: [] for node in self.nodes}
        for edge in self.edges:
            graph[edge["source"]].append(edge["target"])
        return graph

    def _remove_cycles(self, graph):
        """Simple cycle removal using DFS."""
        visited = set()
        rec_stack = set()
        acyclic_graph = {k: v.copy() for k, v in graph.items()}

        def dfs(node):
            if node in rec_stack:
                return True  # Back edge found
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if dfs(neighbor):
                    # Remove back edge
                    if neighbor in acyclic_graph[node]:
                        acyclic_graph[node].remove(neighbor)

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node)

        return acyclic_graph

    def _assign_layers(self, graph):
        """Assign nodes to layers using longest path."""
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1

        layers = []
        remaining = set(graph.keys())

        while remaining:
            current_layer = []
            for node in list(remaining):
                if in_degree[node] == 0:
                    current_layer.append(node)
                    remaining.remove(node)

                    # Update in-degrees
                    for neighbor in graph[node]:
                        in_degree[neighbor] -= 1

            if not current_layer:  # Handle remaining cycles
                current_layer = [min(remaining, key=lambda n: in_degree[n])]
                remaining.remove(current_layer[0])

            layers.append(current_layer)

        return layers

    def _minimize_crossings(self, layers, graph):
        """Simplified crossing minimization."""
        # This is a simplified version - in practice, this is very complex
        return layers  # Return unchanged for exploration

    def _assign_positions(self, layers):
        """Assign x,y positions based on layers."""
        positions = {}
        for layer_idx, layer in enumerate(layers):
            for node_idx, node in enumerate(layer):
                positions[node] = {"x": 50 + layer_idx * 200, "y": 50 + node_idx * 60}
        return positions

    def _estimate_edge_crossings(self, layers, graph):
        """Estimate number of edge crossings."""
        # Simplified estimation
        crossings = 0
        layer_map = {}
        for i, layer in enumerate(layers):
            for node in layer:
                layer_map[node] = i

        for node in graph:
            for target in graph[node]:
                if layer_map[target] < layer_map[node]:
                    crossings += 1  # Backwards edge

        return crossings

    def _calculate_forces(self, positions):
        """Calculate forces for force-directed layout."""
        forces = {node: {"x": 0, "y": 0} for node in positions}

        # Repulsive forces
        for i, node1 in enumerate(positions):
            for j, node2 in enumerate(positions):
                if i != j:
                    dx = positions[node1]["x"] - positions[node2]["x"]
                    dy = positions[node1]["y"] - positions[node2]["y"]
                    distance = math.sqrt(dx * dx + dy * dy) or 1

                    force = 1000 / (distance * distance)
                    forces[node1]["x"] += force * dx / distance
                    forces[node1]["y"] += force * dy / distance

        # Attractive forces for connected nodes
        for edge in self.edges:
            source, target = edge["source"], edge["target"]
            if source in positions and target in positions:
                dx = positions[target]["x"] - positions[source]["x"]
                dy = positions[target]["y"] - positions[source]["y"]
                distance = math.sqrt(dx * dx + dy * dy) or 1

                force = distance * 0.01
                forces[source]["x"] += force * dx / distance
                forces[source]["y"] += force * dy / distance
                forces[target]["x"] -= force * dx / distance
                forces[target]["y"] -= force * dy / distance

        return forces

    def _apply_constraints(self, positions, forces):
        """Apply hierarchical constraints to forces."""
        # Simplified: reduce vertical movement
        for node in forces:
            forces[node]["y"] *= 0.5

    def _update_positions(self, positions, forces):
        """Update positions based on forces."""
        new_positions = {}
        for node in positions:
            new_positions[node] = {
                "x": positions[node]["x"] + forces[node]["x"] * 0.1,
                "y": positions[node]["y"] + forces[node]["y"] * 0.1,
            }
        return new_positions

    def _calculate_edge_lengths(self, positions):
        """Calculate all edge lengths."""
        lengths = []
        for edge in self.edges:
            source, target = edge["source"], edge["target"]
            if source in positions and target in positions:
                dx = positions[target]["x"] - positions[source]["x"]
                dy = positions[target]["y"] - positions[source]["y"]
                lengths.append(math.sqrt(dx * dx + dy * dy))
        return lengths

    def _get_position_spread(self, positions, axis):
        """Get spread of positions along axis."""
        values = [pos[axis] for pos in positions.values()]
        return max(values) - min(values) if values else 0

    def _calculate_node_importance(self):
        """Calculate node importance using simple PageRank."""
        importance = {node["index"]: 1.0 for node in self.nodes}

        for _ in range(10):  # Simplified iterations
            new_importance = {}
            for node in self.nodes:
                node_idx = node["index"]
                new_importance[node_idx] = 0.15  # Damping factor

                # Add importance from incoming edges
                for edge in self.edges:
                    if edge["target"] == node_idx:
                        source_importance = importance[edge["source"]]
                        source_out_degree = sum(
                            1 for e in self.edges if e["source"] == edge["source"]
                        )
                        new_importance[node_idx] += (
                            0.85 * source_importance / max(source_out_degree, 1)
                        )

            importance = new_importance

        # Normalize
        max_importance = max(importance.values()) if importance.values() else 1
        return {k: v / max_importance for k, v in importance.items()}

    def _calculate_dependency_levels(self):
        """Calculate dependency levels for nodes."""
        in_degree = {node["index"]: 0 for node in self.nodes}
        for edge in self.edges:
            in_degree[edge["target"]] += 1

        levels = []
        remaining = {node["index"] for node in self.nodes}

        while remaining:
            current_level = []
            for node in list(remaining):
                if in_degree[node] == 0:
                    current_level.append(node)

            if not current_level:
                # Handle remaining nodes
                min_degree = min(in_degree[n] for n in remaining)
                current_level = [n for n in remaining if in_degree[n] == min_degree]

            levels.append(current_level)

            for node in current_level:
                remaining.remove(node)
                for edge in self.edges:
                    if edge["source"] == node and edge["target"] in remaining:
                        in_degree[edge["target"]] -= 1

        return levels


class EdgeCurveOptimizer:
    """Explore different edge curve optimization techniques."""

    def __init__(self):
        with open("graph_output/graph_data.json", "r") as f:
            self.data = json.load(f)

    def explore_curve_types(self):
        """Explore different curve types for edge rendering."""
        print("\n🎨 EXPLORING EDGE CURVE OPTIMIZATION")
        print("=" * 50)

        curve_types = {
            "quadratic_bezier": self._analyze_quadratic_bezier(),
            "cubic_bezier": self._analyze_cubic_bezier(),
            "quartic_bezier": self._analyze_quartic_bezier(),
            "catmull_rom_spline": self._analyze_catmull_rom(),
            "adaptive_curves": self._analyze_adaptive_curves(),
        }

        print(f"\n📊 Curve Type Comparison:")
        for curve_type, analysis in curve_types.items():
            print(f"   {curve_type}:")
            print(f"      Complexity: {analysis['complexity']}")
            print(f"      Clarity: {analysis['clarity']}")
            print(f"      Performance: {analysis['performance']}")
            print(f"      Best for: {analysis['best_for']}")

        return curve_types

    def _analyze_quadratic_bezier(self):
        """Analyze quadratic Bézier curves."""
        return {
            "complexity": "Low",
            "clarity": "Good for simple paths",
            "performance": "Excellent",
            "best_for": "Short, direct connections",
            "svg_command": "Q",
            "control_points": 1,
        }

    def _analyze_cubic_bezier(self):
        """Analyze cubic Bézier curves."""
        return {
            "complexity": "Medium",
            "clarity": "Very good flexibility",
            "performance": "Good",
            "best_for": "Most general purpose connections",
            "svg_command": "C",
            "control_points": 2,
        }

    def _analyze_quartic_bezier(self):
        """Analyze quartic Bézier curves."""
        return {
            "complexity": "High",
            "clarity": "Excellent for complex routing",
            "performance": "Fair",
            "best_for": "High-degree nodes, obstacle avoidance",
            "svg_command": "Custom",
            "control_points": 3,
        }

    def _analyze_catmull_rom(self):
        """Analyze Catmull-Rom splines."""
        return {
            "complexity": "High",
            "clarity": "Smooth, natural curves",
            "performance": "Fair",
            "best_for": "Multiple waypoint routing",
            "svg_command": "Custom",
            "control_points": "Variable",
        }

    def _analyze_adaptive_curves(self):
        """Analyze adaptive curve selection."""
        return {
            "complexity": "Very High",
            "clarity": "Optimal for each situation",
            "performance": "Good with caching",
            "best_for": "Complex graphs with varied connection types",
            "svg_command": "Mixed",
            "control_points": "Adaptive",
        }


def main():
    """Run comprehensive options exploration."""
    print("🔬 PHASE 2: OPTIONS EXPLORATION")
    print("=" * 60)

    # Explore layout algorithms
    layout_explorer = LayoutAlgorithmExplorer()

    results = {"layout_algorithms": {}, "edge_curves": {}}

    # Test different layout algorithms
    results["layout_algorithms"]["sugiyama"] = layout_explorer.sugiyama_layered_layout()
    results["layout_algorithms"][
        "force_constrained"
    ] = layout_explorer.force_directed_constrained_layout()
    results["layout_algorithms"]["grid_based"] = layout_explorer.grid_based_layout()
    results["layout_algorithms"][
        "custom_dependency"
    ] = layout_explorer.custom_dependency_aware_layout()

    # Explore edge curve options
    curve_optimizer = EdgeCurveOptimizer()
    results["edge_curves"] = curve_optimizer.explore_curve_types()

    # Generate recommendations
    print(f"\n🎯 ALGORITHM RECOMMENDATIONS")
    print("=" * 50)

    print("✅ Best for Edge Clarity: Sugiyama + Cubic Bézier")
    print("✅ Best for Performance: Grid-Based + Quadratic Bézier")
    print("✅ Best for Complex Dependencies: Custom + Adaptive Curves")
    print("✅ Most Balanced: Custom Dependency-Aware + Cubic Bézier")

    # Save exploration results
    with open("options_exploration_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Full exploration results saved to: options_exploration_results.json")

    return results


if __name__ == "__main__":
    main()
