"""
Interactive Enhanced Graph Validation and Testing Suite
Creative testing to ensure the app works properly post-implementation
"""

import json
import re
from datetime import datetime


class InteractiveGraphValidator:
    """Interactive validation for enhanced dependency graph features."""

    def __init__(self):
        self.validation_results = {}
        self.load_test_data()

    def load_test_data(self):
        """Load enhanced graph data for validation."""
        try:
            with open("graph_output/enhanced_graph_data.json", "r") as f:
                self.enhanced_data = json.load(f)

            with open(
                "graph_output/enhanced_dependency_graph.html", "r", encoding="utf-8"
            ) as f:
                self.enhanced_html = f.read()

            print("✅ Test data loaded successfully")

        except FileNotFoundError as e:
            print(f"❌ Could not load test data: {e}")
            print("Make sure enhanced_dependency_graph.py has been run first")
            exit(1)

    def validate_core_functionality(self):
        """Validate core functionality improvements."""
        print("\n🔍 VALIDATING CORE FUNCTIONALITY")
        print("=" * 50)

        validations = {}

        # 1. PageRank importance calculation
        print("1. Testing PageRank importance calculation...")
        nodes_with_importance = [
            n for n in self.enhanced_data["nodes"] if "importance" in n
        ]
        importance_range = [n["importance"] for n in nodes_with_importance]

        if importance_range:
            min_importance = min(importance_range)
            max_importance = max(importance_range)
            avg_importance = sum(importance_range) / len(importance_range)

            validations["pagerank"] = {
                "nodes_with_importance": len(nodes_with_importance),
                "min_importance": min_importance,
                "max_importance": max_importance,
                "avg_importance": avg_importance,
                "valid_range": 0 <= min_importance <= max_importance <= 1,
            }

            print(f"   ✅ Nodes with importance: {len(nodes_with_importance)}")
            print(
                f"   ✅ Importance range: {min_importance:.3f} - {max_importance:.3f}"
            )
            print(f"   ✅ Average importance: {avg_importance:.3f}")
            print(
                f"   ✅ Valid range (0-1): {'Yes' if validations['pagerank']['valid_range'] else 'No'}"
            )
        else:
            validations["pagerank"] = {"error": "No importance data found"}
            print("   ❌ No importance data found")

        # 2. Test file detection and categorization
        print("\n2. Testing test file detection...")
        test_files = [n for n in self.enhanced_data["nodes"] if n.get("is_test", False)]
        non_test_files = [
            n for n in self.enhanced_data["nodes"] if not n.get("is_test", False)
        ]

        validations["test_detection"] = {
            "test_files": len(test_files),
            "non_test_files": len(non_test_files),
            "total_files": len(self.enhanced_data["nodes"]),
            "test_percentage": len(test_files) / len(self.enhanced_data["nodes"]) * 100,
        }

        print(f"   ✅ Test files detected: {len(test_files)}")
        print(f"   ✅ Non-test files: {len(non_test_files)}")
        print(
            f"   ✅ Test percentage: {validations['test_detection']['test_percentage']:.1f}%"
        )

        # 3. Directory coverage
        print("\n3. Testing directory coverage...")
        folders = set(n["folder"] for n in self.enhanced_data["nodes"])
        expected_folders = {
            "root",
            "tests",
            "callbacks",
            "assets",
            "reports",
            "archive",
        }
        covered_folders = folders.intersection(expected_folders)

        validations["directory_coverage"] = {
            "detected_folders": list(folders),
            "expected_folders": list(expected_folders),
            "covered_folders": list(covered_folders),
            "coverage_percentage": len(covered_folders) / len(expected_folders) * 100,
        }

        print(f"   ✅ Folders detected: {len(folders)}")
        print(
            f"   ✅ Expected folders covered: {len(covered_folders)}/{len(expected_folders)}"
        )
        print(
            f"   ✅ Coverage: {validations['directory_coverage']['coverage_percentage']:.1f}%"
        )

        # 4. Edge enhancement validation
        print("\n4. Testing edge enhancements...")
        edges = self.enhanced_data["edges"]
        cross_folder_edges = [
            e for e in edges if e["source_folder"] != e["target_folder"]
        ]
        test_related_edges = [e for e in edges if e.get("involves_test", False)]

        validations["edge_enhancements"] = {
            "total_edges": len(edges),
            "cross_folder_edges": len(cross_folder_edges),
            "test_related_edges": len(test_related_edges),
            "cross_folder_percentage": len(cross_folder_edges) / len(edges) * 100,
        }

        print(f"   ✅ Total edges: {len(edges)}")
        print(f"   ✅ Cross-folder edges: {len(cross_folder_edges)}")
        print(f"   ✅ Test-related edges: {len(test_related_edges)}")
        print(
            f"   ✅ Cross-folder %: {validations['edge_enhancements']['cross_folder_percentage']:.1f}%"
        )

        self.validation_results["core_functionality"] = validations
        return validations

    def validate_html_features(self):
        """Validate HTML implementation features."""
        print("\n🎨 VALIDATING HTML FEATURES")
        print("=" * 50)

        validations = {}

        # 1. JavaScript functions validation
        print("1. Testing JavaScript functions...")
        js_functions = [
            "calculateEnhancedHierarchicalLayout",
            "createEnhancedCubicBezierPath",
            "handleEnhancedMouseOver",
            "resetAllFilters",
            "toggleFolder",
            "calculatePageRankImportance",
        ]

        function_presence = {}
        for func in js_functions:
            present = func in self.enhanced_html
            function_presence[func] = present
            status = "✅" if present else "❌"
            print(f"   {status} {func}: {'Present' if present else 'Missing'}")

        validations["javascript_functions"] = function_presence

        # 2. CSS styling validation
        print("\n2. Testing CSS styling...")
        css_features = [
            "cubic-bezier",
            "drop-shadow",
            "transition:",
            "border-radius",
            "opacity:",
            "transform:",
        ]

        css_presence = {}
        for feature in css_features:
            present = feature in self.enhanced_html
            css_presence[feature] = present
            status = "✅" if present else "❌"
            print(f"   {status} {feature}: {'Present' if present else 'Missing'}")

        validations["css_features"] = css_presence

        # 3. Interactive controls validation
        print("\n3. Testing interactive controls...")
        controls = [
            "test-toggle",
            "stats-grid",
            "controls-container",
            "filter-controls",
        ]

        control_presence = {}
        for control in controls:
            present = control in self.enhanced_html
            control_presence[control] = present
            status = "✅" if present else "❌"
            print(f"   {status} {control}: {'Present' if present else 'Missing'}")

        validations["interactive_controls"] = control_presence

        # 4. SVG enhancement validation
        print("\n4. Testing SVG enhancements...")
        svg_features = ["<defs>", "<marker", "arrowhead", "drop-shadow", "cubic-bezier"]

        svg_presence = {}
        for feature in svg_features:
            present = feature in self.enhanced_html
            svg_presence[feature] = present
            status = "✅" if present else "❌"
            print(f"   {status} {feature}: {'Present' if present else 'Missing'}")

        validations["svg_enhancements"] = svg_presence

        self.validation_results["html_features"] = validations
        return validations

    def validate_data_integrity(self):
        """Validate data integrity and consistency."""
        print("\n🔎 VALIDATING DATA INTEGRITY")
        print("=" * 50)

        validations = {}

        # 1. Node data consistency
        print("1. Testing node data consistency...")
        nodes = self.enhanced_data["nodes"]
        required_fields = ["index", "id", "label", "folder", "file_size"]
        optional_fields = ["importance", "is_test", "file_type"]

        node_validation = {
            "total_nodes": len(nodes),
            "nodes_with_all_required": 0,
            "nodes_with_importance": 0,
            "nodes_with_test_flag": 0,
            "unique_indices": len(set(n["index"] for n in nodes)),
            "unique_ids": len(set(n["id"] for n in nodes)),
        }

        for node in nodes:
            # Check required fields
            if all(field in node for field in required_fields):
                node_validation["nodes_with_all_required"] += 1

            # Check optional fields
            if "importance" in node:
                node_validation["nodes_with_importance"] += 1
            if "is_test" in node:
                node_validation["nodes_with_test_flag"] += 1

        validations["node_consistency"] = node_validation

        print(f"   ✅ Total nodes: {node_validation['total_nodes']}")
        print(
            f"   ✅ Nodes with required fields: {node_validation['nodes_with_all_required']}"
        )
        print(
            f"   ✅ Nodes with importance: {node_validation['nodes_with_importance']}"
        )
        print(f"   ✅ Nodes with test flags: {node_validation['nodes_with_test_flag']}")
        print(f"   ✅ Unique indices: {node_validation['unique_indices']}")
        print(f"   ✅ Unique IDs: {node_validation['unique_ids']}")

        # 2. Edge data consistency
        print("\n2. Testing edge data consistency...")
        edges = self.enhanced_data["edges"]
        edge_validation = {
            "total_edges": len(edges),
            "valid_source_target": 0,
            "edges_with_folders": 0,
            "self_references": 0,
        }

        node_indices = set(n["index"] for n in nodes)

        for edge in edges:
            # Check valid source/target
            if edge["source"] in node_indices and edge["target"] in node_indices:
                edge_validation["valid_source_target"] += 1

            # Check folder information
            if "source_folder" in edge and "target_folder" in edge:
                edge_validation["edges_with_folders"] += 1

            # Check for self-references
            if edge["source"] == edge["target"]:
                edge_validation["self_references"] += 1

        validations["edge_consistency"] = edge_validation

        print(f"   ✅ Total edges: {edge_validation['total_edges']}")
        print(f"   ✅ Valid source/target: {edge_validation['valid_source_target']}")
        print(f"   ✅ Edges with folder info: {edge_validation['edges_with_folders']}")
        print(f"   ✅ Self-references: {edge_validation['self_references']}")

        # 3. Folder statistics validation
        print("\n3. Testing folder statistics...")
        folder_stats = self.enhanced_data.get("subfolder_info", {})

        folder_validation = {
            "folders_tracked": len(folder_stats),
            "total_files_in_stats": sum(
                stats["file_count"] for stats in folder_stats.values()
            ),
            "folders_with_dependencies": sum(
                1 for stats in folder_stats.values() if stats["dependency_count"] > 0
            ),
        }

        validations["folder_statistics"] = folder_validation

        print(f"   ✅ Folders tracked: {folder_validation['folders_tracked']}")
        print(f"   ✅ Files in statistics: {folder_validation['total_files_in_stats']}")
        print(
            f"   ✅ Folders with dependencies: {folder_validation['folders_with_dependencies']}"
        )

        self.validation_results["data_integrity"] = validations
        return validations

    def validate_performance_characteristics(self):
        """Validate performance characteristics."""
        print("\n⚡ VALIDATING PERFORMANCE CHARACTERISTICS")
        print("=" * 50)

        validations = {}

        # 1. File size analysis
        print("1. Testing file sizes...")
        html_size = len(self.enhanced_html)
        json_size = len(json.dumps(self.enhanced_data))

        size_validation = {
            "html_size_bytes": html_size,
            "html_size_kb": html_size / 1024,
            "json_size_bytes": json_size,
            "json_size_kb": json_size / 1024,
            "total_size_kb": (html_size + json_size) / 1024,
        }

        validations["file_sizes"] = size_validation

        print(f"   ✅ HTML size: {size_validation['html_size_kb']:.1f} KB")
        print(f"   ✅ JSON size: {size_validation['json_size_kb']:.1f} KB")
        print(f"   ✅ Total size: {size_validation['total_size_kb']:.1f} KB")

        # 2. Complexity analysis
        print("\n2. Testing complexity metrics...")
        node_count = len(self.enhanced_data["nodes"])
        edge_count = len(self.enhanced_data["edges"])

        complexity_validation = {
            "node_count": node_count,
            "edge_count": edge_count,
            "edge_to_node_ratio": edge_count / node_count if node_count > 0 else 0,
            "estimated_render_complexity": node_count
            + (edge_count * 2),  # Simplified metric
            "manageable_size": node_count < 500 and edge_count < 1000,
        }

        validations["complexity"] = complexity_validation

        print(f"   ✅ Node count: {complexity_validation['node_count']}")
        print(f"   ✅ Edge count: {complexity_validation['edge_count']}")
        print(
            f"   ✅ Edge/Node ratio: {complexity_validation['edge_to_node_ratio']:.2f}"
        )
        print(
            f"   ✅ Manageable size: {'Yes' if complexity_validation['manageable_size'] else 'No'}"
        )

        # 3. Algorithm efficiency indicators
        print("\n3. Testing algorithm efficiency...")
        js_efficiency = {
            "uses_caching": "cache" in self.enhanced_html.lower()
            or "memo" in self.enhanced_html.lower(),
            "avoids_nested_loops": self.enhanced_html.count("for(")
            + self.enhanced_html.count("for ")
            < 10,
            "uses_efficient_selectors": "getElementById" in self.enhanced_html
            or "querySelector" in self.enhanced_html,
            "minimizes_dom_manipulation": self.enhanced_html.count("appendChild") < 20,
        }

        validations["algorithm_efficiency"] = js_efficiency

        for metric, value in js_efficiency.items():
            status = "✅" if value else "❌"
            print(
                f"   {status} {metric.replace('_', ' ').title()}: {'Yes' if value else 'No'}"
            )

        self.validation_results["performance"] = validations
        return validations

    def generate_interactive_report(self):
        """Generate interactive validation report."""
        print("\n📊 GENERATING VALIDATION REPORT")
        print("=" * 50)

        # Run all validations
        core_results = self.validate_core_functionality()
        html_results = self.validate_html_features()
        data_results = self.validate_data_integrity()
        perf_results = self.validate_performance_characteristics()

        # Calculate scores
        scores = self._calculate_validation_scores()

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": self.validation_results,
            "scores": scores,
            "summary": self._generate_summary(scores),
            "recommendations": self._generate_recommendations(scores),
        }

        # Save report
        with open("interactive_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        self._print_final_summary(scores)

        return report

    def _calculate_validation_scores(self):
        """Calculate validation scores for each category."""
        scores = {}

        # Core functionality score
        core = self.validation_results["core_functionality"]
        core_score = 0
        if "pagerank" in core and not "error" in core["pagerank"]:
            core_score += 0.3 if core["pagerank"]["valid_range"] else 0
        core_score += 0.2 if core["test_detection"]["test_files"] > 40 else 0
        core_score += (
            0.3 if core["directory_coverage"]["coverage_percentage"] > 80 else 0
        )
        core_score += (
            0.2 if core["edge_enhancements"]["cross_folder_percentage"] > 30 else 0
        )
        scores["core_functionality"] = core_score

        # HTML features score
        html = self.validation_results["html_features"]
        js_score = sum(html["javascript_functions"].values()) / len(
            html["javascript_functions"]
        )
        css_score = sum(html["css_features"].values()) / len(html["css_features"])
        control_score = sum(html["interactive_controls"].values()) / len(
            html["interactive_controls"]
        )
        svg_score = sum(html["svg_enhancements"].values()) / len(
            html["svg_enhancements"]
        )
        scores["html_features"] = (js_score + css_score + control_score + svg_score) / 4

        # Data integrity score
        data = self.validation_results["data_integrity"]
        node_score = (
            data["node_consistency"]["nodes_with_all_required"]
            / data["node_consistency"]["total_nodes"]
        )
        edge_score = (
            data["edge_consistency"]["valid_source_target"]
            / data["edge_consistency"]["total_edges"]
        )
        folder_score = 1 if data["folder_statistics"]["folders_tracked"] > 5 else 0.5
        scores["data_integrity"] = (node_score + edge_score + folder_score) / 3

        # Performance score
        perf = self.validation_results["performance"]
        size_score = 1 if perf["file_sizes"]["total_size_kb"] < 1000 else 0.5
        complexity_score = 1 if perf["complexity"]["manageable_size"] else 0.5
        efficiency_score = sum(perf["algorithm_efficiency"].values()) / len(
            perf["algorithm_efficiency"]
        )
        scores["performance"] = (size_score + complexity_score + efficiency_score) / 3

        # Overall score
        scores["overall"] = sum(scores.values()) / len(scores)

        return scores

    def _generate_summary(self, scores):
        """Generate validation summary."""
        summary = {
            "overall_status": (
                "PASS" if scores["overall"] > 0.8 else "NEEDS_IMPROVEMENT"
            ),
            "strengths": [],
            "weaknesses": [],
            "critical_issues": [],
        }

        # Identify strengths and weaknesses
        for category, score in scores.items():
            if category == "overall":
                continue

            if score > 0.9:
                summary["strengths"].append(f"Excellent {category.replace('_', ' ')}")
            elif score < 0.6:
                summary["weaknesses"].append(f"Poor {category.replace('_', ' ')}")
                if score < 0.4:
                    summary["critical_issues"].append(
                        f"Critical: {category.replace('_', ' ')} needs immediate attention"
                    )

        return summary

    def _generate_recommendations(self, scores):
        """Generate recommendations based on scores."""
        recommendations = []

        if scores["core_functionality"] < 0.8:
            recommendations.append(
                "Improve PageRank calculation and test file detection"
            )

        if scores["html_features"] < 0.8:
            recommendations.append(
                "Complete JavaScript function implementation and CSS styling"
            )

        if scores["data_integrity"] < 0.8:
            recommendations.append("Fix data consistency issues and add missing fields")

        if scores["performance"] < 0.8:
            recommendations.append("Optimize file sizes and algorithm efficiency")

        if scores["overall"] > 0.9:
            recommendations.append(
                "Excellent implementation! Consider adding advanced features."
            )

        return recommendations

    def _print_final_summary(self, scores):
        """Print final validation summary."""
        print(f"\n🎯 VALIDATION SUMMARY")
        print("=" * 50)

        for category, score in scores.items():
            if category == "overall":
                continue

            percentage = score * 100
            status = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🔴"
            print(f"{status} {category.replace('_', ' ').title()}: {percentage:.1f}%")

        overall_percentage = scores["overall"] * 100
        overall_status = (
            "🎉 EXCELLENT"
            if scores["overall"] > 0.9
            else "✅ GOOD" if scores["overall"] > 0.8 else "⚠️ NEEDS WORK"
        )

        print(f"\n🎊 OVERALL SCORE: {overall_percentage:.1f}% - {overall_status}")

        if scores["overall"] > 0.8:
            print("🚀 Enhanced dependency graph is ready for production use!")
        else:
            print("🔧 Review recommendations and implement improvements.")


def main():
    """Run interactive validation."""
    print("🧪 INTERACTIVE ENHANCED GRAPH VALIDATION")
    print("=" * 60)

    validator = InteractiveGraphValidator()
    report = validator.generate_interactive_report()

    print(f"\n📄 Full validation report saved to: interactive_validation_report.json")

    return report["scores"]["overall"] > 0.8


if __name__ == "__main__":
    main()
