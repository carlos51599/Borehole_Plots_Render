#!/usr/bin/env python3
"""
Enhanced Flowchart Data Generator

Creates comprehensive analysis data for the interactive flowchart including:
- File relationships and dependencies
- Function call graphs
- Module interconnections
- Code metrics and complexity analysis
- Git history and change information
"""

import os
import ast
import json
import re
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import importlib.util


class EnhancedCodeAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.files = {}
        self.functions = defaultdict(list)
        self.classes = defaultdict(list)
        self.imports = defaultdict(set)
        self.dependencies = defaultdict(set)
        self.function_calls = defaultdict(list)
        self.git_info = {}

    def analyze_ast_detailed(self, content, file_path):
        """Detailed AST analysis including function calls and complexity"""
        try:
            tree = ast.parse(content)

            # Extract imports
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

            # Extract function definitions with detailed info
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Calculate complexity (cyclomatic complexity approximation)
                    complexity = self.calculate_function_complexity(node)

                    # Extract function calls within this function
                    calls = []
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call):
                            if isinstance(subnode.func, ast.Name):
                                calls.append(subnode.func.id)
                            elif isinstance(subnode.func, ast.Attribute):
                                calls.append(subnode.func.attr)

                    functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "end_line": getattr(node, "end_lineno", node.lineno),
                            "docstring": ast.get_docstring(node),
                            "args": [arg.arg for arg in node.args.args],
                            "complexity": complexity,
                            "calls": calls,
                            "decorators": [
                                d.id if isinstance(d, ast.Name) else str(d)
                                for d in node.decorator_list
                            ],
                        }
                    )

            # Extract class definitions with methods
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            complexity = self.calculate_function_complexity(item)
                            methods.append(
                                {
                                    "name": item.name,
                                    "line": item.lineno,
                                    "docstring": ast.get_docstring(item),
                                    "complexity": complexity,
                                    "is_property": any(
                                        isinstance(d, ast.Name) and d.id == "property"
                                        for d in item.decorator_list
                                    ),
                                }
                            )

                    classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node),
                            "methods": methods,
                            "bases": [
                                base.id if isinstance(base, ast.Name) else str(base)
                                for base in node.bases
                            ],
                        }
                    )

            return imports, functions, classes

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return set(), [], []

    def calculate_function_complexity(self, func_node):
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            # Decision points that increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def get_git_info(self, file_path):
        """Get git information for a file"""
        try:
            rel_path = file_path.relative_to(self.root_path)

            # Get last commit info
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "-1",
                    "--format=%H|%an|%ad|%s",
                    "--date=iso",
                    str(rel_path),
                ],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|", 3)
                if len(parts) >= 4:
                    return {
                        "last_commit": parts[0][:8],
                        "last_author": parts[1],
                        "last_date": parts[2],
                        "last_message": parts[3],
                    }

            # Get commit count
            count_result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD", "--", str(rel_path)],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            commit_count = 0
            if count_result.returncode == 0 and count_result.stdout.strip():
                commit_count = int(count_result.stdout.strip())

            return {"commit_count": commit_count}

        except Exception as e:
            print(f"Error getting git info for {file_path}: {e}")
            return {}

    def analyze_file_detailed(self, file_path):
        """Enhanced file analysis with more metrics"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            rel_path = str(file_path.relative_to(self.root_path))

            # Basic metrics
            lines = content.splitlines()
            total_lines = len(lines)
            code_lines = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ]
            )
            comment_lines = len(
                [line for line in lines if line.strip().startswith("#")]
            )
            blank_lines = total_lines - code_lines - comment_lines

            # File statistics
            stat = file_path.stat()

            # Get git information
            git_info = self.get_git_info(file_path)

            # AST analysis
            imports, functions, classes = self.analyze_ast_detailed(content, file_path)

            # Calculate complexity metrics
            total_complexity = sum(f["complexity"] for f in functions)
            avg_complexity = total_complexity / len(functions) if functions else 0

            # Categorize file
            file_type = self.categorize_file_detailed(rel_path, functions, classes)

            file_info = {
                "path": rel_path,
                "name": file_path.name,
                "size_bytes": stat.st_size,
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "complexity": total_complexity,
                "avg_complexity": round(avg_complexity, 2),
                "modified": stat.st_mtime,
                "type": file_type,
                "functions_count": len(functions),
                "classes_count": len(classes),
                "imports_count": len(imports),
                "content_preview": content[:500]
                + ("..." if len(content) > 500 else ""),
                "git_info": git_info,
            }

            # Store detailed information
            self.files[rel_path] = file_info
            self.functions[rel_path] = functions
            self.classes[rel_path] = classes
            self.imports[rel_path] = imports

            # Build dependencies
            for imp in imports:
                # Check for local file imports
                potential_files = [f"{imp}.py", f"{imp}/__init__.py", f"{imp}/main.py"]

                for potential in potential_files:
                    potential_path = self.root_path / potential
                    if potential_path.exists():
                        self.dependencies[rel_path].add(potential)
                        break

            # Store function calls for call graph
            for func in functions:
                for call in func["calls"]:
                    self.function_calls[rel_path].append(
                        {"function": func["name"], "calls": call, "line": func["line"]}
                    )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def categorize_file_detailed(self, path, functions, classes):
        """Enhanced file categorization"""
        filename = path.lower()

        # Test files
        if "test_" in filename or "/test" in filename or filename.endswith("_test.py"):
            return "test"

        # Configuration files
        if any(word in filename for word in ["config", "settings", "constants", "env"]):
            return "config"

        # Utility files
        if any(word in filename for word in ["util", "helper", "tool", "common"]):
            return "utility"

        # Main application files
        if filename in ["app.py", "main.py", "__main__.py"] or "main" in filename:
            return "main"

        # Model/data files
        if any(word in filename for word in ["model", "data", "schema", "entity"]):
            return "model"

        # API/service files
        if any(word in filename for word in ["api", "service", "endpoint", "handler"]):
            return "service"

        # UI/view files
        if any(word in filename for word in ["ui", "view", "component", "widget"]):
            return "ui"

        # Based on content analysis
        if len(classes) > len(functions) and len(classes) > 2:
            return "model"
        elif len(functions) > 10:
            return "core"
        elif "callback" in filename or "event" in filename:
            return "event"

        return "core"

    def generate_network_metrics(self):
        """Generate network analysis metrics"""
        try:
            import networkx as nx

            # Create directed graph
            G = nx.DiGraph()

            # Add nodes
            for file_path, info in self.files.items():
                G.add_node(file_path, **info)

            # Add edges (dependencies)
            for source, deps in self.dependencies.items():
                for target in deps:
                    if target in self.files:
                        G.add_edge(source, target)

            # Calculate metrics
            metrics = {}

            # Centrality measures
            try:
                betweenness = nx.betweenness_centrality(G)
                closeness = nx.closeness_centrality(G)
                degree = dict(G.degree())
                in_degree = dict(G.in_degree())
                out_degree = dict(G.out_degree())

                for node in G.nodes():
                    metrics[node] = {
                        "betweenness_centrality": round(betweenness.get(node, 0), 3),
                        "closeness_centrality": round(closeness.get(node, 0), 3),
                        "degree": degree.get(node, 0),
                        "in_degree": in_degree.get(node, 0),
                        "out_degree": out_degree.get(node, 0),
                    }
            except:
                # Fallback for disconnected graphs
                for node in G.nodes():
                    metrics[node] = {
                        "degree": G.degree(node),
                        "in_degree": G.in_degree(node),
                        "out_degree": G.out_degree(node),
                    }

            return metrics

        except ImportError:
            print("NetworkX not available, skipping network metrics")
            return {}

    def analyze_project(self):
        """Analyze the entire project with enhanced metrics"""
        print(f"Starting enhanced analysis of: {self.root_path}")

        # Analyze all Python files
        python_files = []
        for root, dirs, files in os.walk(self.root_path):
            # Skip certain directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in {"__pycache__", "node_modules", "archive"}
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        print(f"Found {len(python_files)} Python files to analyze")

        # Analyze each file
        for i, file_path in enumerate(python_files, 1):
            print(
                f"Analyzing ({i}/{len(python_files)}): {file_path.relative_to(self.root_path)}"
            )
            self.analyze_file_detailed(file_path)

        print("Analysis complete!")

    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        total_files = len(self.files)
        total_lines = sum(info["total_lines"] for info in self.files.values())
        total_code_lines = sum(info["code_lines"] for info in self.files.values())
        total_functions = sum(len(funcs) for funcs in self.functions.values())
        total_classes = sum(len(classes) for classes in self.classes.values())
        total_complexity = sum(info["complexity"] for info in self.files.values())

        # File type distribution
        type_counts = Counter(info["type"] for info in self.files.values())

        # Most complex files
        complex_files = sorted(
            self.files.items(), key=lambda x: x[1]["complexity"], reverse=True
        )[:10]

        # Most connected files (highest degree)
        connected_files = sorted(
            self.dependencies.items(), key=lambda x: len(x[1]), reverse=True
        )[:10]

        print(f"\n{'='*60}")
        print(f"    ENHANCED CODEBASE ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"📊 Project Overview:")
        print(f"   • Total Python files: {total_files}")
        print(f"   • Total lines: {total_lines:,}")
        print(f"   • Code lines: {total_code_lines:,}")
        print(f"   • Total functions: {total_functions}")
        print(f"   • Total classes: {total_classes}")
        print(f"   • Total complexity: {total_complexity}")
        print(f"   • Average complexity per file: {total_complexity/total_files:.1f}")

        print(f"\n📁 File Type Distribution:")
        for file_type, count in type_counts.most_common():
            print(f"   • {file_type.title()}: {count} files")

        print(f"\n🔥 Most Complex Files:")
        for file_path, info in complex_files[:10]:
            print(f"   • {file_path}: {info['complexity']} complexity points")

        print(f"\n🕸️  Most Connected Files:")
        for file_path, deps in connected_files[:10]:
            print(f"   • {file_path}: {len(deps)} dependencies")

    def save_enhanced_analysis(self, output_file=None):
        """Save enhanced analysis with all metrics"""
        if output_file is None:
            output_file = self.root_path / "codebase_analysis.json"

        # Generate network metrics
        network_metrics = self.generate_network_metrics()

        # Merge network metrics into file info
        for file_path, metrics in network_metrics.items():
            if file_path in self.files:
                self.files[file_path]["network_metrics"] = metrics

        # Create comprehensive analysis data
        analysis_data = {
            "metadata": {
                "project_name": self.root_path.name,
                "root_path": str(self.root_path),
                "analysis_timestamp": datetime.now().isoformat(),
                "total_files": len(self.files),
                "total_lines": sum(info["total_lines"] for info in self.files.values()),
                "total_complexity": sum(
                    info["complexity"] for info in self.files.values()
                ),
                "analyzer_version": "2.0.0",
            },
            "files": self.files,
            "functions": dict(self.functions),
            "classes": dict(self.classes),
            "imports": {k: list(v) for k, v in self.imports.items()},
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "function_calls": dict(self.function_calls),
            "statistics": {
                "file_types": Counter(info["type"] for info in self.files.values()),
                "complexity_distribution": {
                    "low": len(
                        [f for f in self.files.values() if f["complexity"] < 10]
                    ),
                    "medium": len(
                        [f for f in self.files.values() if 10 <= f["complexity"] < 50]
                    ),
                    "high": len(
                        [f for f in self.files.values() if f["complexity"] >= 50]
                    ),
                },
            },
        }

        # Save to JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, default=str)

        print(f"\n✅ Enhanced analysis saved to: {output_file}")
        print(f"📁 File size: {output_file.stat().st_size / 1024:.1f} KB")

        return analysis_data


def main():
    """Run enhanced analysis"""
    root_path = Path(__file__).parent
    analyzer = EnhancedCodeAnalyzer(root_path)

    print("🚀 Starting enhanced codebase analysis...")
    analyzer.analyze_project()
    analyzer.generate_analysis_report()
    analysis_data = analyzer.save_enhanced_analysis()

    return analysis_data


if __name__ == "__main__":
    main()
