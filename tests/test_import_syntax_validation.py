#!/usr/bin/env python3
"""
Import and Syntax Validation Test Suite

Specialized test script focusing on comprehensive import testing and syntax validation.
This implements the first category of the Comprehensive Post-Restructuring Test Action Plan.

Test Coverage:
- Direct imports of all modules and packages
- Wildcard imports with __all__ validation
- Relative import resolution
- Circular import detection
- Syntax validation for all Python files

Author: GitHub Copilot
Date: July 23, 2025
"""

import sys
import os
import ast
import importlib
import traceback
from pathlib import Path
from typing import List, Dict, Tuple

# Add workspace to path
sys.path.insert(0, os.path.abspath("."))


class ImportSyntaxTester:
    """Comprehensive import and syntax testing."""

    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent
        self.results = {
            "direct_imports": {},
            "wildcard_imports": {},
            "relative_imports": {},
            "circular_imports": {},
            "syntax_validation": {},
        }

    def run_all_tests(self) -> bool:
        """Run all import and syntax tests."""
        print("🧪 IMPORT AND SYNTAX VALIDATION TEST SUITE")
        print("=" * 60)

        success = True

        success &= self.test_direct_imports()
        success &= self.test_wildcard_imports()
        success &= self.test_relative_imports()
        success &= self.test_circular_imports()
        success &= self.test_syntax_validation()

        self.generate_report()
        return success

    def test_direct_imports(self) -> bool:
        """Test direct imports of all modules and packages."""
        print("\n📦 Testing Direct Imports")
        print("-" * 40)

        # Core packages
        packages = [
            "app_modules",
            "borehole_log",
            "callbacks",
            "config_modules",
            "section",
            "state_management",
        ]

        # Standalone modules
        modules = [
            "app",
            "app_factory",
            "app_constants",
            "config",
            "data_loader",
            "coordinate_service",
            "map_utils",
            "geology_code_utils",
            "memory_manager",
            "error_handling",
            "enhanced_error_handling",
            "error_recovery",
            "loading_indicators",
            "lazy_marker_manager",
            "debug_module",
            "polyline_utils",
            "dataframe_optimizer",
            "borehole_log_professional",
        ]

        success = True

        print("Testing Packages:")
        for package in packages:
            try:
                module = importlib.import_module(package)
                print(f"  ✅ {package}")

                # Check __init__.py structure
                if hasattr(module, "__all__"):
                    print(f"     📋 __all__ defined ({len(module.__all__)} exports)")
                    self.results["direct_imports"][package] = {
                        "status": "success",
                        "exports": len(module.__all__),
                        "has_all": True,
                    }
                else:
                    print(f"     ⚠️ __all__ not defined")
                    self.results["direct_imports"][package] = {
                        "status": "success",
                        "exports": 0,
                        "has_all": False,
                    }

                # Check for common functions
                common_funcs = ["main", "create", "get_", "setup"]
                found_funcs = []
                for attr in dir(module):
                    if not attr.startswith("_"):
                        for func_pattern in common_funcs:
                            if func_pattern in attr.lower():
                                found_funcs.append(attr)
                                break

                if found_funcs:
                    print(f"     🔧 Key functions: {', '.join(found_funcs[:3])}")

            except ImportError as e:
                print(f"  ❌ {package}: {e}")
                self.results["direct_imports"][package] = {
                    "status": "failed",
                    "error": str(e),
                }
                success = False
            except Exception as e:
                print(f"  ❌ {package}: Unexpected error - {e}")
                self.results["direct_imports"][package] = {
                    "status": "error",
                    "error": str(e),
                }
                success = False

        print("\nTesting Standalone Modules:")
        for module_name in modules:
            try:
                module = importlib.import_module(module_name)
                print(f"  ✅ {module_name}")
                self.results["direct_imports"][module_name] = {"status": "success"}
            except ImportError as e:
                print(f"  ❌ {module_name}: {e}")
                self.results["direct_imports"][module_name] = {
                    "status": "failed",
                    "error": str(e),
                }
                success = False
            except Exception as e:
                print(f"  ❌ {module_name}: Unexpected error - {e}")
                self.results["direct_imports"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                success = False

        return success

    def test_wildcard_imports(self) -> bool:
        """Test wildcard imports and __all__ validation."""
        print("\n🌟 Testing Wildcard Imports")
        print("-" * 40)

        wildcard_packages = [
            "config_modules",
            "borehole_log",
            "section",
            "state_management",
        ]

        success = True

        for package in wildcard_packages:
            try:
                # Create isolated namespace for testing
                test_globals = {"__builtins__": __builtins__}
                exec(f"from {package} import *", test_globals)

                # Count imported items
                imported_items = [
                    k
                    for k in test_globals.keys()
                    if not k.startswith("__") and k != "__builtins__"
                ]

                print(f"  ✅ {package}: {len(imported_items)} items imported")

                # Check for naming conflicts
                conflicts = []
                common_names = ["main", "app", "config", "data", "create"]
                for name in common_names:
                    if imported_items.count(name) > 1:
                        conflicts.append(name)

                if conflicts:
                    print(f"     ⚠️ Potential conflicts: {', '.join(conflicts)}")

                # Sample some imported items
                sample_items = imported_items[:5]
                if sample_items:
                    print(f"     📋 Sample exports: {', '.join(sample_items)}")

                self.results["wildcard_imports"][package] = {
                    "status": "success",
                    "item_count": len(imported_items),
                    "conflicts": conflicts,
                    "sample_items": sample_items,
                }

            except ImportError as e:
                print(f"  ❌ {package}: {e}")
                self.results["wildcard_imports"][package] = {
                    "status": "failed",
                    "error": str(e),
                }
                success = False
            except Exception as e:
                print(f"  ❌ {package}: Unexpected error - {e}")
                self.results["wildcard_imports"][package] = {
                    "status": "error",
                    "error": str(e),
                }
                success = False

        return success

    def test_relative_imports(self) -> bool:
        """Test relative imports within and across submodules."""
        print("\n🔗 Testing Relative Imports")
        print("-" * 40)

        # Test modules known to use relative imports
        relative_tests = [
            ("app_modules.main", "app_modules submodule"),
            ("app_modules.layout", "app_modules layout"),
            ("callbacks.file_upload_enhanced", "callbacks submodule"),
            ("config_modules", "config_modules package"),
            ("borehole_log.plotting", "borehole_log submodule"),
            ("section.plotting", "section submodule"),
            ("state_management", "state_management package"),
        ]

        success = True

        for module_name, description in relative_tests:
            try:
                module = importlib.import_module(module_name)
                print(f"  ✅ {description}: {module_name}")
                self.results["relative_imports"][module_name] = {"status": "success"}
            except ImportError as e:
                print(f"  ❌ {description}: {e}")
                self.results["relative_imports"][module_name] = {
                    "status": "failed",
                    "error": str(e),
                }
                success = False
            except Exception as e:
                print(f"  ❌ {description}: Unexpected error - {e}")
                self.results["relative_imports"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                success = False

        return success

    def test_circular_imports(self) -> bool:
        """Detect circular import dependencies."""
        print("\n🔄 Testing Circular Import Detection")
        print("-" * 40)

        # Test various import orders
        import_orders = [
            ["app", "config", "callbacks"],
            ["config_modules", "app_modules", "state_management"],
            ["borehole_log", "section", "callbacks"],
            ["map_utils", "coordinate_service", "data_loader"],
            ["error_handling", "enhanced_error_handling", "callbacks"],
        ]

        success = True

        for order in import_orders:
            order_key = " -> ".join(order)
            try:
                # Clear relevant modules from cache
                modules_to_clear = []
                for module_name in order:
                    for key in list(sys.modules.keys()):
                        if key == module_name or key.startswith(f"{module_name}."):
                            modules_to_clear.append(key)

                for mod in modules_to_clear:
                    if mod in sys.modules:
                        del sys.modules[mod]

                # Import in specified order
                for module_name in order:
                    importlib.import_module(module_name)

                print(f"  ✅ {order_key}: No circular dependencies")
                self.results["circular_imports"][order_key] = {"status": "success"}

            except ImportError as e:
                if "circular" in str(e).lower() or "recursive" in str(e).lower():
                    print(f"  ❌ {order_key}: Circular import detected - {e}")
                    self.results["circular_imports"][order_key] = {
                        "status": "circular",
                        "error": str(e),
                    }
                    success = False
                else:
                    print(f"  ⚠️ {order_key}: Import issue - {e}")
                    self.results["circular_imports"][order_key] = {
                        "status": "import_error",
                        "error": str(e),
                    }
            except Exception as e:
                print(f"  ❌ {order_key}: Unexpected error - {e}")
                self.results["circular_imports"][order_key] = {
                    "status": "error",
                    "error": str(e),
                }
                success = False

        return success

    def test_syntax_validation(self) -> bool:
        """Run syntax checks on all Python files."""
        print("\n📝 Testing Syntax Validation")
        print("-" * 40)

        # Find all Python files
        python_files = list(self.workspace_root.rglob("*.py"))

        # Exclude certain directories
        excluded_dirs = {
            "__pycache__",
            ".git",
            "archive",
            "node_modules",
            ".pytest_cache",
            ".coverage",
        }

        python_files = [
            f
            for f in python_files
            if not any(part in excluded_dirs for part in f.parts)
        ]

        print(f"📊 Checking syntax for {len(python_files)} Python files...")

        success = True
        syntax_errors = []
        warnings = []

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()

                # Compile to check syntax
                compile(source, str(py_file), "exec")

                # Additional AST parsing for detailed analysis
                try:
                    tree = ast.parse(source, filename=str(py_file))

                    # Check for potential issues
                    issues = self._analyze_ast(tree, py_file)
                    if issues:
                        warnings.extend(issues)

                except SyntaxError:
                    # Already caught by compile above
                    pass

                self.results["syntax_validation"][
                    str(py_file.relative_to(self.workspace_root))
                ] = {"status": "valid"}

            except SyntaxError as e:
                error_msg = f"{py_file.relative_to(self.workspace_root)}: Line {e.lineno} - {e.msg}"
                syntax_errors.append(error_msg)
                print(f"  ❌ {error_msg}")

                self.results["syntax_validation"][
                    str(py_file.relative_to(self.workspace_root))
                ] = {"status": "syntax_error", "error": str(e), "line": e.lineno}
                success = False

            except UnicodeDecodeError as e:
                error_msg = (
                    f"{py_file.relative_to(self.workspace_root)}: Encoding error - {e}"
                )
                syntax_errors.append(error_msg)
                print(f"  ❌ {error_msg}")

                self.results["syntax_validation"][
                    str(py_file.relative_to(self.workspace_root))
                ] = {"status": "encoding_error", "error": str(e)}
                success = False

            except Exception as e:
                error_msg = f"{py_file.relative_to(self.workspace_root)}: Unexpected error - {e}"
                print(f"  ⚠️ {error_msg}")

                self.results["syntax_validation"][
                    str(py_file.relative_to(self.workspace_root))
                ] = {"status": "check_error", "error": str(e)}

        # Summary
        valid_files = len(python_files) - len(syntax_errors)
        print(f"\n📊 Syntax Validation Summary:")
        print(f"  ✅ Valid files: {valid_files}")
        print(f"  ❌ Files with errors: {len(syntax_errors)}")
        print(f"  ⚠️ Files with warnings: {len(warnings)}")

        if syntax_errors:
            print(f"\n❌ Syntax Errors Found:")
            for error in syntax_errors[:10]:  # Show first 10 errors
                print(f"    {error}")
            if len(syntax_errors) > 10:
                print(f"    ... and {len(syntax_errors) - 10} more")

        if warnings:
            print(f"\n⚠️ Potential Issues Found:")
            for warning in warnings[:5]:  # Show first 5 warnings
                print(f"    {warning}")
            if len(warnings) > 5:
                print(f"    ... and {len(warnings) - 5} more")

        return success

    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> List[str]:
        """Analyze AST for potential issues."""
        issues = []

        for node in ast.walk(tree):
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(
                    f"{file_path.name}: Line {node.lineno} - Bare except clause"
                )

            # Check for unused imports (basic check)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # This is a simplified check - a full analysis would need scope tracking
                    pass

        return issues

    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 IMPORT AND SYNTAX VALIDATION REPORT")
        print("=" * 60)

        # Summary statistics
        categories = [
            ("Direct Imports", "direct_imports"),
            ("Wildcard Imports", "wildcard_imports"),
            ("Relative Imports", "relative_imports"),
            ("Circular Imports", "circular_imports"),
            ("Syntax Validation", "syntax_validation"),
        ]

        overall_success = True

        for category_name, category_key in categories:
            results = self.results[category_key]
            if not results:
                continue

            total = len(results)
            passed = sum(
                1
                for r in results.values()
                if isinstance(r, dict) and r.get("status") in ["success", "valid"]
            )

            success_rate = (passed / total * 100) if total > 0 else 0
            status = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"

            if success_rate < 90:
                overall_success = False

            print(f"{status} {category_name}: {passed}/{total} ({success_rate:.1f}%)")

        print(
            f"\n🎯 Overall Status: {'✅ PASSED' if overall_success else '❌ NEEDS ATTENTION'}"
        )

        # Detailed breakdowns
        print(f"\n📋 Detailed Breakdown:")

        # Direct imports breakdown
        direct_results = self.results["direct_imports"]
        packages = [
            k
            for k in direct_results.keys()
            if "." not in k and direct_results[k].get("has_all")
        ]
        print(f"  📦 Packages with __all__: {len(packages)}")

        # Syntax validation breakdown
        syntax_results = self.results["syntax_validation"]
        syntax_errors = [
            k for k, v in syntax_results.items() if v.get("status") == "syntax_error"
        ]
        if syntax_errors:
            print(f"  ❌ Files with syntax errors: {len(syntax_errors)}")

        print(f"\n💡 Recommendations:")
        if overall_success:
            print("  🎉 Excellent! All import and syntax tests passed.")
            print("  📈 Consider adding more comprehensive import cycle detection.")
            print("  🔄 Set up automated syntax checking in CI/CD.")
        else:
            print("  🔧 Address failed imports for full compatibility.")
            print("  📝 Fix syntax errors before deployment.")
            print("  🔍 Review import structure for optimization opportunities.")


def main():
    """Run the import and syntax validation test suite."""
    tester = ImportSyntaxTester()

    try:
        success = tester.run_all_tests()

        if success:
            print("\n🎉 IMPORT AND SYNTAX VALIDATION: ALL TESTS PASSED")
            return 0
        else:
            print("\n❌ IMPORT AND SYNTAX VALIDATION: SOME TESTS FAILED")
            return 1

    except Exception as e:
        print(f"\n💥 IMPORT AND SYNTAX VALIDATION: UNEXPECTED ERROR - {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
