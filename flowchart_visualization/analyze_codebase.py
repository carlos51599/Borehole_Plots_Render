#!/usr/bin/env python3
"""
Codebase Analysis Script for Interactive Flowchart Generation

This script analyzes the project structure, imports, and dependencies
to generate data for the interactive HTML flowchart.
"""

import os
import ast
import json
import re
from pathlib import Path
from collections import defaultdict
import importlib.util

# Configuration
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".vscode",
    "node_modules",
    ".pytest_cache",
    "archive",
}
PYTHON_EXTENSIONS = {".py"}
ANALYSIS_OUTPUT = "codebase_analysis.json"


class CodeAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.files = {}
        self.dependencies = defaultdict(set)
        self.functions = defaultdict(list)
        self.classes = defaultdict(list)
        self.imports = defaultdict(set)

    def should_analyze_file(self, file_path):
        """Check if file should be analyzed"""
        # Skip files in ignore directories
        for part in file_path.parts:
            if part in IGNORE_DIRS:
                return False

        # Only analyze Python files for now
        return file_path.suffix in PYTHON_EXTENSIONS

    def extract_imports(self, content, file_path):
        """Extract import statements from Python file"""
        try:
            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

            return imports
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return set()

    def extract_functions_and_classes(self, content, file_path):
        """Extract function and class definitions"""
        try:
            tree = ast.parse(content)
            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node),
                            "args": [arg.arg for arg in node.args.args],
                        }
                    )
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(
                                {
                                    "name": item.name,
                                    "line": item.lineno,
                                    "docstring": ast.get_docstring(item),
                                }
                            )

                    classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node),
                            "methods": methods,
                        }
                    )

            return functions, classes
        except Exception as e:
            print(f"Error extracting functions/classes from {file_path}: {e}")
            return [], []

    def get_file_info(self, file_path):
        """Get basic file information"""
        try:
            stat = file_path.stat()
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Count lines
            lines = len(content.splitlines())

            # Estimate complexity (simple heuristic)
            complexity = (
                content.count("if ")
                + content.count("for ")
                + content.count("while ")
                + content.count("try:")
            )

            return {
                "path": str(file_path.relative_to(self.root_path)),
                "size_bytes": stat.st_size,
                "lines": lines,
                "complexity": complexity,
                "modified": stat.st_mtime,
                "content_preview": content[:500]
                + ("..." if len(content) > 500 else ""),
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None

    def analyze_file(self, file_path):
        """Analyze a single file"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Basic file info
            file_info = self.get_file_info(file_path)
            if not file_info:
                return

            rel_path = file_path.relative_to(self.root_path)
            self.files[str(rel_path)] = file_info

            # Extract imports
            imports = self.extract_imports(content, file_path)
            self.imports[str(rel_path)] = imports

            # Extract functions and classes
            functions, classes = self.extract_functions_and_classes(content, file_path)
            self.functions[str(rel_path)] = functions
            self.classes[str(rel_path)] = classes

            # Build dependency relationships
            for imp in imports:
                # Check if import is a local file
                potential_file = self.root_path / f"{imp}.py"
                if potential_file.exists():
                    self.dependencies[str(rel_path)].add(imp + ".py")

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def analyze_project(self):
        """Analyze the entire project"""
        print(f"Analyzing project in: {self.root_path}")

        # Walk through all files
        for root, dirs, files in os.walk(self.root_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                file_path = Path(root) / file
                if self.should_analyze_file(file_path):
                    print(f"Analyzing: {file_path.relative_to(self.root_path)}")
                    self.analyze_file(file_path)

    def generate_analysis_report(self):
        """Generate analysis report"""
        total_files = len(self.files)
        total_lines = sum(info["lines"] for info in self.files.values())
        total_functions = sum(len(funcs) for funcs in self.functions.values())
        total_classes = sum(len(classes) for classes in self.classes.values())

        print(f"\n=== Analysis Report ===")
        print(f"Total Python files: {total_files}")
        print(f"Total lines of code: {total_lines}")
        print(f"Total functions: {total_functions}")
        print(f"Total classes: {total_classes}")
        print(
            f"Total dependencies: {sum(len(deps) for deps in self.dependencies.values())}"
        )

        # Most complex files
        complex_files = sorted(
            self.files.items(), key=lambda x: x[1]["complexity"], reverse=True
        )[:10]

        print(f"\nMost complex files:")
        for file_path, info in complex_files:
            print(f"  {file_path}: {info['complexity']} complexity points")

    def save_analysis(self, output_file=None):
        """Save analysis results to JSON"""
        if output_file is None:
            output_file = self.root_path / ANALYSIS_OUTPUT

        # Convert sets to lists for JSON serialization
        analysis_data = {
            "project_info": {
                "root_path": str(self.root_path),
                "total_files": len(self.files),
                "total_lines": sum(info["lines"] for info in self.files.values()),
                "analysis_timestamp": datetime.now().isoformat(),
            },
            "files": self.files,
            "functions": dict(self.functions),
            "classes": dict(self.classes),
            "imports": {k: list(v) for k, v in self.imports.items()},
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, default=str)

        print(f"\nAnalysis saved to: {output_file}")
        return analysis_data


def main():
    """Main analysis function"""
    root_path = Path(__file__).parent
    analyzer = CodeAnalyzer(root_path)

    print("Starting codebase analysis...")
    analyzer.analyze_project()
    analyzer.generate_analysis_report()
    analysis_data = analyzer.save_analysis()

    return analysis_data


if __name__ == "__main__":
    # Import datetime here to avoid issues
    from datetime import datetime

    main()
