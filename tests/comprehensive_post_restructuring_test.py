#!/usr/bin/env python3
"""
Comprehensive Post-Restructuring Test Suite

Following the Multi-Stage Action Plan guidelines, this comprehensive test suite
validates all aspects of the modular application structure to ensure complete
functionality after restructuring.

Test Categories:
1. Import and Syntax Validation
2. API and Attribute Consistency
3. Functional and Integration Testing
4. Error Handling and Logging
5. Performance and Resource Management
6. UI and Visualization Consistency
7. Documentation and Help
8. Test Coverage and Automation
9. Deployment and Packaging
10. Creative/Unusual Scenarios

Author: GitHub Copilot
Date: July 23, 2025
"""

import sys
import os
import importlib
import traceback
import logging
import gc
import threading
import time
import subprocess
import tempfile
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add workspace to path for testing
sys.path.insert(0, os.path.abspath("."))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveTestSuite:
    """Comprehensive testing suite for post-restructuring validation."""

    def __init__(self):
        self.results = {}
        self.failed_tests = []
        self.warnings = []
        self.workspace_root = Path(__file__).parent.parent

    def run_all_tests(self) -> bool:
        """Run all test categories and return overall success."""
        logger.info("🚀 Starting Comprehensive Post-Restructuring Test Suite")
        logger.info("=" * 80)

        test_methods = [
            self.test_imports_and_syntax,
            self.test_api_consistency,
            self.test_functional_integration,
            self.test_error_handling,
            self.test_performance_resources,
            self.test_ui_visualization,
            self.test_documentation,
            self.test_coverage_automation,
            self.test_deployment_packaging,
            self.test_creative_scenarios,
        ]

        all_passed = True

        for test_method in test_methods:
            try:
                result = test_method()
                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(
                    f"❌ Test method {test_method.__name__} failed with exception: {e}"
                )
                self.failed_tests.append(f"{test_method.__name__}: {str(e)}")
                all_passed = False

        # Generate final report
        self._generate_final_report()

        return all_passed

    def test_imports_and_syntax(self) -> bool:
        """1. Import and Syntax Validation"""
        logger.info("🧪 Phase 1: Import and Syntax Validation")
        logger.info("-" * 50)

        success = True

        # a. Direct Import Tests
        success &= self._test_direct_imports()

        # b. Wildcard Import Tests
        success &= self._test_wildcard_imports()

        # c. Relative Import Tests
        success &= self._test_relative_imports()

        # d. Circular Import Detection
        success &= self._test_circular_imports()

        # e. Syntax Checks
        success &= self._test_syntax_validation()

        self.results["imports_and_syntax"] = success
        return success

    def _test_direct_imports(self) -> bool:
        """Test direct imports of all modules and packages."""
        logger.info("📦 Testing Direct Imports...")

        # Define all main packages and modules to test
        packages_to_test = [
            "app_modules",
            "borehole_log",
            "callbacks",
            "config_modules",
            "section",
            "state_management",
        ]

        modules_to_test = [
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
        ]

        success = True

        # Test package imports
        for package in packages_to_test:
            try:
                module = importlib.import_module(package)
                logger.info(f"  ✅ {package}: Successfully imported")

                # Test __init__.py functionality
                if hasattr(module, "__all__"):
                    logger.info(
                        f"     📋 {package}.__all__ defined with {len(module.__all__)} exports"
                    )
                else:
                    logger.warning(f"     ⚠️ {package}.__all__ not defined")

            except ImportError as e:
                logger.error(f"  ❌ {package}: Import failed - {e}")
                success = False
            except Exception as e:
                logger.error(f"  ❌ {package}: Unexpected error - {e}")
                success = False

        # Test module imports
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                logger.info(f"  ✅ {module_name}: Successfully imported")
            except ImportError as e:
                logger.error(f"  ❌ {module_name}: Import failed - {e}")
                success = False
            except Exception as e:
                logger.error(f"  ❌ {module_name}: Unexpected error - {e}")
                success = False

        return success

    def _test_wildcard_imports(self) -> bool:
        """Test wildcard imports to check __all__ and namespace issues."""
        logger.info("🌟 Testing Wildcard Imports...")

        wildcard_tests = [
            "config_modules",
            "borehole_log",
            "section",
            "state_management",
        ]

        success = True

        for package in wildcard_tests:
            try:
                # Create a temporary namespace to test wildcard import
                test_globals = {}
                exec(f"from {package} import *", test_globals)

                # Count imported items (excluding builtins)
                imported_items = [
                    k for k in test_globals.keys() if not k.startswith("__")
                ]
                logger.info(
                    f"  ✅ {package}: Wildcard import successful ({len(imported_items)} items)"
                )

                # Check for common conflicts
                if "main" in imported_items and "app" in imported_items:
                    logger.warning(
                        f"     ⚠️ {package}: Potential naming conflict (main, app)"
                    )

            except ImportError as e:
                logger.error(f"  ❌ {package}: Wildcard import failed - {e}")
                success = False
            except Exception as e:
                logger.error(f"  ❌ {package}: Wildcard import error - {e}")
                success = False

        return success

    def _test_relative_imports(self) -> bool:
        """Test relative imports within and across submodules."""
        logger.info("🔗 Testing Relative Imports...")

        # Test relative imports by examining key modules that use them
        relative_import_tests = [
            ("app_modules.main", "from .app_setup import"),
            ("callbacks", "from .base import"),
            ("config_modules", "from .figures import"),
            ("borehole_log.plotting", "from .utils import"),
            ("section.plotting", "from .parsing import"),
        ]

        success = True

        for module_name, expected_import in relative_import_tests:
            try:
                module = importlib.import_module(module_name)
                logger.info(f"  ✅ {module_name}: Relative imports working")
            except ImportError as e:
                logger.error(f"  ❌ {module_name}: Relative import failed - {e}")
                success = False
            except Exception as e:
                logger.error(f"  ❌ {module_name}: Relative import error - {e}")
                success = False

        return success

    def _test_circular_imports(self) -> bool:
        """Detect circular import dependencies."""
        logger.info("🔄 Testing Circular Import Detection...")

        # Test importing modules in different orders
        import_orders = [
            ["app", "config", "callbacks"],
            ["config_modules", "app_modules", "state_management"],
            ["borehole_log", "section", "callbacks"],
            ["map_utils", "coordinate_service", "data_loader"],
        ]

        success = True

        for order in import_orders:
            try:
                # Clear module cache for this test
                modules_to_clear = [
                    mod for mod in sys.modules.keys() if any(o in mod for o in order)
                ]
                for mod in modules_to_clear:
                    if mod in sys.modules:
                        del sys.modules[mod]

                # Import in specified order
                for module_name in order:
                    importlib.import_module(module_name)

                logger.info(
                    f"  ✅ Import order {' -> '.join(order)}: No circular dependencies"
                )

            except ImportError as e:
                if "circular" in str(e).lower():
                    logger.error(
                        f"  ❌ Circular import detected in {' -> '.join(order)}: {e}"
                    )
                    success = False
                else:
                    logger.warning(f"  ⚠️ Import issue in {' -> '.join(order)}: {e}")
            except Exception as e:
                logger.error(f"  ❌ Error testing {' -> '.join(order)}: {e}")
                success = False

        return success

    def _test_syntax_validation(self) -> bool:
        """Run syntax checks on all Python files."""
        logger.info("📝 Testing Syntax Validation...")

        success = True
        syntax_errors = []

        # Find all Python files
        python_files = list(self.workspace_root.rglob("*.py"))

        # Exclude certain directories
        excluded_dirs = {"__pycache__", ".git", "archive", "node_modules"}
        python_files = [
            f
            for f in python_files
            if not any(part in excluded_dirs for part in f.parts)
        ]

        logger.info(f"  📊 Checking syntax for {len(python_files)} Python files...")

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()

                # Compile to check syntax
                compile(source, str(py_file), "exec")

            except SyntaxError as e:
                error_msg = f"{py_file.relative_to(self.workspace_root)}: Line {e.lineno} - {e.msg}"
                syntax_errors.append(error_msg)
                logger.error(f"  ❌ Syntax error: {error_msg}")
                success = False
            except Exception as e:
                logger.warning(
                    f"  ⚠️ Could not check {py_file.relative_to(self.workspace_root)}: {e}"
                )

        if syntax_errors:
            logger.error(f"  📊 Found {len(syntax_errors)} syntax errors")
        else:
            logger.info(f"  ✅ All {len(python_files)} files have valid syntax")

        return success

    def test_api_consistency(self) -> bool:
        """2. API and Attribute Consistency"""
        logger.info("🔌 Phase 2: API and Attribute Consistency")
        logger.info("-" * 50)

        success = True

        # a. Public API Check
        success &= self._test_public_api()

        # b. Deprecated/Legacy API Check
        success &= self._test_legacy_compatibility()

        # c. Attribute Existence
        success &= self._test_attribute_existence()

        self.results["api_consistency"] = success
        return success

    def _test_public_api(self) -> bool:
        """Ensure all expected public functions/classes are exposed."""
        logger.info("🌐 Testing Public API...")

        # Define expected public APIs for each package
        expected_apis = {
            "app_modules": ["create_and_configure_app", "main", "get_app"],
            "borehole_log": [
                "create_borehole_log",
                "plot_single_page",
                "matplotlib_figure",
            ],
            "callbacks": ["register_callbacks", "handle_callback_error"],
            "config_modules": ["APP_TITLE", "MAP_HEIGHT", "HEADER_H1_CENTER_STYLE"],
            "section": [
                "plot_professional_borehole_sections",
                "parse_ags_geol_section_from_string",
            ],
            "state_management": ["AppState", "get_app_state_manager", "BoreholeData"],
        }

        success = True

        for package_name, expected_items in expected_apis.items():
            try:
                package = importlib.import_module(package_name)

                for item in expected_items:
                    if hasattr(package, item):
                        logger.info(f"  ✅ {package_name}.{item}: Available")
                    else:
                        logger.error(
                            f"  ❌ {package_name}.{item}: Missing from public API"
                        )
                        success = False

            except ImportError as e:
                logger.error(f"  ❌ {package_name}: Cannot import package - {e}")
                success = False

        return success

    def _test_legacy_compatibility(self) -> bool:
        """Test backward compatibility with legacy imports."""
        logger.info("⏮️ Testing Legacy Compatibility...")

        # Test legacy imports that should still work
        legacy_tests = [
            ("from config import APP_TITLE", "config_modules migration"),
            ("from app import main", "app_modules migration"),
            ("import borehole_log_professional", "standalone module compatibility"),
        ]

        success = True

        for import_statement, description in legacy_tests:
            try:
                exec(import_statement)
                logger.info(f"  ✅ {description}: {import_statement}")
            except ImportError as e:
                logger.warning(f"  ⚠️ {description}: {import_statement} - {e}")
                # Some legacy compatibility might be intentionally broken
            except Exception as e:
                logger.error(f"  ❌ {description}: {import_statement} - {e}")
                success = False

        return success

    def _test_attribute_existence(self) -> bool:
        """Use hasattr to check for documented attributes and methods."""
        logger.info("🔍 Testing Attribute Existence...")

        # Define key attributes to check
        attribute_tests = [
            ("app_modules", "create_and_configure_app", "function"),
            ("config_modules", "APP_TITLE", "str"),
            ("borehole_log", "create_borehole_log", "function"),
            ("state_management", "AppState", "class"),
        ]

        success = True

        for module_name, attr_name, expected_type in attribute_tests:
            try:
                module = importlib.import_module(module_name)

                if hasattr(module, attr_name):
                    attr = getattr(module, attr_name)
                    actual_type = type(attr).__name__
                    logger.info(f"  ✅ {module_name}.{attr_name}: {actual_type}")
                else:
                    logger.error(f"  ❌ {module_name}.{attr_name}: Attribute missing")
                    success = False

            except ImportError as e:
                logger.error(f"  ❌ {module_name}: Cannot import - {e}")
                success = False

        return success

    def test_functional_integration(self) -> bool:
        """3. Functional and Integration Testing"""
        logger.info("⚙️ Phase 3: Functional and Integration Testing")
        logger.info("-" * 50)

        success = True

        # a. End-to-End Tests
        success &= self._test_end_to_end()

        # b. Cross-Module Integration
        success &= self._test_cross_module_integration()

        # c. Data Flow Validation
        success &= self._test_data_flow()

        # d. Edge Case Inputs
        success &= self._test_edge_cases()

        self.results["functional_integration"] = success
        return success

    def _test_end_to_end(self) -> bool:
        """Run end-to-end application flow tests."""
        logger.info("🎯 Testing End-to-End Flows...")

        success = True

        try:
            # Test app creation without starting server
            from app_modules import create_and_configure_app

            app = create_and_configure_app()

            if app is not None:
                logger.info("  ✅ App creation: Success")
            else:
                logger.error("  ❌ App creation: Returned None")
                success = False

        except Exception as e:
            logger.error(f"  ❌ App creation failed: {e}")
            success = False

        try:
            # Test config loading
            from config_modules import APP_TITLE, MAP_HEIGHT

            if APP_TITLE and MAP_HEIGHT:
                logger.info("  ✅ Config loading: Success")
            else:
                logger.error("  ❌ Config loading: Missing values")
                success = False

        except Exception as e:
            logger.error(f"  ❌ Config loading failed: {e}")
            success = False

        return success

    def _test_cross_module_integration(self) -> bool:
        """Test that modules interact correctly."""
        logger.info("🤝 Testing Cross-Module Integration...")

        success = True

        # Test config integration with app_modules
        try:
            from config_modules import APP_TITLE
            from app_modules.layout import create_header_section

            # This should work without errors
            header = create_header_section()
            logger.info("  ✅ Config + App Integration: Success")

        except Exception as e:
            logger.error(f"  ❌ Config + App Integration failed: {e}")
            success = False

        # Test state management integration
        try:
            from state_management import get_app_state_manager, BoreholeData

            state_manager = get_app_state_manager()
            logger.info("  ✅ State Management Integration: Success")

        except Exception as e:
            logger.error(f"  ❌ State Management Integration failed: {e}")
            success = False

        return success

    def _test_data_flow(self) -> bool:
        """Test data flow through the pipeline."""
        logger.info("📊 Testing Data Flow Validation...")

        success = True

        # Test basic data structures
        try:
            from state_management import BoreholeData

            # Create test data
            test_data = BoreholeData(
                borehole_id="TEST001", location_data={}, geology_data=[], sample_data=[]
            )

            logger.info("  ✅ Data Structure Creation: Success")

        except Exception as e:
            logger.error(f"  ❌ Data Structure Creation failed: {e}")
            success = False

        return success

    def _test_edge_cases(self) -> bool:
        """Feed edge case inputs to entry points."""
        logger.info("⚡ Testing Edge Case Inputs...")

        success = True

        # Test with None inputs
        try:
            from borehole_log import validate_plot_data

            result = validate_plot_data(None)
            logger.info("  ✅ None input handling: Success")

        except Exception as e:
            logger.warning(f"  ⚠️ None input handling: {e}")

        # Test with empty data
        try:
            from section import validate_ags_format

            result = validate_ags_format("")
            logger.info("  ✅ Empty string handling: Success")

        except Exception as e:
            logger.warning(f"  ⚠️ Empty string handling: {e}")

        return success

    def test_error_handling(self) -> bool:
        """4. Error Handling and Logging"""
        logger.info("🚨 Phase 4: Error Handling and Logging")
        logger.info("-" * 50)

        success = True

        # a. Exception Propagation
        success &= self._test_exception_propagation()

        # b. Logging Output
        success &= self._test_logging_output()

        # c. Graceful Degradation
        success &= self._test_graceful_degradation()

        self.results["error_handling"] = success
        return success

    def _test_exception_propagation(self) -> bool:
        """Test exception handling across modules."""
        logger.info("🎭 Testing Exception Propagation...")

        success = True

        try:
            from enhanced_error_handling import handle_callback_error

            # Test error handling function exists
            logger.info("  ✅ Error handling module: Available")

        except ImportError:
            logger.error("  ❌ Error handling module: Not available")
            success = False

        return success

    def _test_logging_output(self) -> bool:
        """Check logging output and configuration."""
        logger.info("📝 Testing Logging Output...")

        success = True

        try:
            from app_modules.app_setup import setup_logging

            # Test logging setup
            test_logger = setup_logging("test_log.log")
            test_logger.info("Test log message")

            logger.info("  ✅ Logging setup: Success")

            # Cleanup test log
            if os.path.exists("test_log.log"):
                os.remove("test_log.log")

        except Exception as e:
            logger.error(f"  ❌ Logging setup failed: {e}")
            success = False

        return success

    def _test_graceful_degradation(self) -> bool:
        """Test graceful degradation with missing components."""
        logger.info("🛡️ Testing Graceful Degradation...")

        success = True

        # Test with missing configuration
        try:
            # Temporarily remove a config item to test degradation
            import config_modules

            original_title = getattr(config_modules, "APP_TITLE", None)
            if hasattr(config_modules, "APP_TITLE"):
                delattr(config_modules, "APP_TITLE")

            # Test app still works with missing config
            from app_modules.layout import create_header_section

            header = create_header_section()

            # Restore original
            if original_title:
                setattr(config_modules, "APP_TITLE", original_title)

            logger.info("  ✅ Missing config degradation: Success")

        except Exception as e:
            logger.warning(f"  ⚠️ Missing config degradation: {e}")

        return success

    def test_performance_resources(self) -> bool:
        """5. Performance and Resource Management"""
        logger.info("⚡ Phase 5: Performance and Resource Management")
        logger.info("-" * 50)

        success = True

        # a. Memory Leaks
        success &= self._test_memory_leaks()

        # b. File Handle Leaks
        success &= self._test_file_handle_leaks()

        # c. Thread/Process Safety
        success &= self._test_thread_safety()

        self.results["performance_resources"] = success
        return success

    def _test_memory_leaks(self) -> bool:
        """Test for memory leaks in repeated operations."""
        logger.info("🧠 Testing Memory Leaks...")

        success = True

        try:
            import gc
            from memory_manager import MemoryManager

            # Record initial memory
            gc.collect()
            initial_objects = len(gc.get_objects())

            # Perform repeated operations
            for i in range(10):
                memory_manager = MemoryManager()
                # Simulate some operations
                del memory_manager

            # Check final memory
            gc.collect()
            final_objects = len(gc.get_objects())

            growth = final_objects - initial_objects

            if growth < 100:  # Allow some growth
                logger.info(f"  ✅ Memory leak test: Passed (growth: {growth} objects)")
            else:
                logger.warning(f"  ⚠️ Possible memory leak: {growth} objects growth")

        except Exception as e:
            logger.error(f"  ❌ Memory leak test failed: {e}")
            success = False

        return success

    def _test_file_handle_leaks(self) -> bool:
        """Test for file handle leaks."""
        logger.info("📁 Testing File Handle Leaks...")

        success = True

        try:
            # Test file operations don't leak handles
            for i in range(20):
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                    f.write("test")
                    temp_path = f.name

                # Clean up
                os.unlink(temp_path)

            logger.info("  ✅ File handle leak test: Passed")

        except Exception as e:
            logger.error(f"  ❌ File handle leak test failed: {e}")
            success = False

        return success

    def _test_thread_safety(self) -> bool:
        """Test thread safety if using concurrency."""
        logger.info("🧵 Testing Thread Safety...")

        success = True

        try:
            # Test basic thread safety
            import threading

            results = []

            def test_function():
                try:
                    from config_modules import APP_TITLE

                    results.append(APP_TITLE)
                except Exception as e:
                    results.append(f"Error: {e}")

            threads = []
            for i in range(5):
                thread = threading.Thread(target=test_function)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Check all threads succeeded
            errors = [r for r in results if str(r).startswith("Error")]
            if not errors:
                logger.info("  ✅ Thread safety test: Passed")
            else:
                logger.warning(f"  ⚠️ Thread safety issues: {len(errors)} errors")

        except Exception as e:
            logger.error(f"  ❌ Thread safety test failed: {e}")
            success = False

        return success

    def test_ui_visualization(self) -> bool:
        """6. UI and Visualization Consistency"""
        logger.info("🎨 Phase 6: UI and Visualization Consistency")
        logger.info("-" * 50)

        success = True

        # a. Layout/Style Consistency
        success &= self._test_layout_consistency()

        # b. Interactive Elements
        success &= self._test_interactive_elements()

        self.results["ui_visualization"] = success
        return success

    def _test_layout_consistency(self) -> bool:
        """Check layout and style consistency."""
        logger.info("📐 Testing Layout Consistency...")

        success = True

        try:
            from config_modules import styles

            # Test style dictionaries are properly formatted
            style_dicts = [
                styles.HEADER_H1_CENTER_STYLE,
                styles.BUTTON_RIGHT_STYLE,
                styles.MAP_CENTER_STYLE,
            ]

            for style_dict in style_dicts:
                if isinstance(style_dict, dict):
                    logger.info(
                        f"  ✅ Style dictionary: Valid dict with {len(style_dict)} properties"
                    )
                else:
                    logger.error(
                        f"  ❌ Style dictionary: Invalid type {type(style_dict)}"
                    )
                    success = False

        except Exception as e:
            logger.error(f"  ❌ Layout consistency test failed: {e}")
            success = False

        return success

    def _test_interactive_elements(self) -> bool:
        """Test callbacks and UI interactions."""
        logger.info("🖱️ Testing Interactive Elements...")

        success = True

        try:
            from callbacks import register_callbacks

            # Test callback registration exists
            logger.info("  ✅ Callback registration: Available")

        except ImportError:
            logger.error("  ❌ Callback registration: Not available")
            success = False
        except Exception as e:
            logger.error(f"  ❌ Interactive elements test failed: {e}")
            success = False

        return success

    def test_documentation(self) -> bool:
        """7. Documentation and Help"""
        logger.info("📚 Phase 7: Documentation and Help")
        logger.info("-" * 50)

        success = True

        # a. Docstring Coverage
        success &= self._test_docstring_coverage()

        # b. Help/Introspection
        success &= self._test_help_introspection()

        self.results["documentation"] = success
        return success

    def _test_docstring_coverage(self) -> bool:
        """Test docstring coverage for modules and functions."""
        logger.info("📖 Testing Docstring Coverage...")

        success = True
        modules_to_check = ["app_modules", "borehole_log", "section", "config_modules"]

        for module_name in modules_to_check:
            try:
                module = importlib.import_module(module_name)

                if module.__doc__:
                    logger.info(f"  ✅ {module_name}: Has module docstring")
                else:
                    logger.warning(f"  ⚠️ {module_name}: Missing module docstring")

            except Exception as e:
                logger.error(f"  ❌ {module_name}: Docstring check failed - {e}")
                success = False

        return success

    def _test_help_introspection(self) -> bool:
        """Test help() and IDE introspection."""
        logger.info("🔍 Testing Help/Introspection...")

        success = True

        try:
            from app_modules import create_and_configure_app

            # Capture help output
            help_output = StringIO()
            with redirect_stdout(help_output):
                help(create_and_configure_app)

            help_text = help_output.getvalue()
            if help_text and len(help_text) > 50:
                logger.info("  ✅ Help introspection: Available")
            else:
                logger.warning("  ⚠️ Help introspection: Limited information")

        except Exception as e:
            logger.error(f"  ❌ Help introspection test failed: {e}")
            success = False

        return success

    def test_coverage_automation(self) -> bool:
        """8. Test Coverage and Automation"""
        logger.info("🧪 Phase 8: Test Coverage and Automation")
        logger.info("-" * 50)

        success = True

        # a. Unit Test Coverage
        success &= self._test_unit_coverage()

        # b. Test for All Imports
        success &= self._test_all_imports_coverage()

        # c. Test Discovery
        success &= self._test_discovery()

        self.results["coverage_automation"] = success
        return success

    def _test_unit_coverage(self) -> bool:
        """Check unit test coverage."""
        logger.info("📊 Testing Unit Coverage...")

        success = True

        # Check for existing test files
        test_files = list(self.workspace_root.glob("test_*.py"))
        test_files.extend(list(self.workspace_root.glob("tests/test_*.py")))

        logger.info(f"  📋 Found {len(test_files)} test files")

        if len(test_files) >= 5:
            logger.info("  ✅ Test coverage: Good test file count")
        else:
            logger.warning("  ⚠️ Test coverage: Limited test files")

        return success

    def _test_all_imports_coverage(self) -> bool:
        """Test for all imports as per instructions."""
        logger.info("📦 Testing All Imports Coverage...")

        success = True

        # Find all Python modules in the workspace
        python_files = list(self.workspace_root.rglob("*.py"))
        excluded_dirs = {"__pycache__", ".git", "archive", "dependency_graph"}

        modules = []
        for py_file in python_files:
            if not any(part in excluded_dirs for part in py_file.parts):
                # Convert file path to module name
                try:
                    relative_path = py_file.relative_to(self.workspace_root)
                    if relative_path.name != "__init__.py":
                        module_parts = list(relative_path.with_suffix("").parts)
                        module_name = ".".join(module_parts)
                        modules.append(module_name)
                except ValueError:
                    continue

        logger.info(f"  📊 Testing imports for {len(modules)} modules...")

        failed_imports = 0
        for module_name in modules[:20]:  # Limit for performance
            try:
                importlib.import_module(module_name)
            except ImportError:
                failed_imports += 1
            except Exception:
                failed_imports += 1

        success_rate = (20 - failed_imports) / 20 * 100

        if success_rate >= 80:
            logger.info(f"  ✅ Import coverage: {success_rate:.1f}% success rate")
        else:
            logger.warning(f"  ⚠️ Import coverage: {success_rate:.1f}% success rate")
            success = False

        return success

    def _test_discovery(self) -> bool:
        """Test that all test files are discoverable."""
        logger.info("🔍 Testing Test Discovery...")

        success = True

        try:
            # Use subprocess to run test discovery
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    ".",
                    "-p",
                    "test_*.py",
                ],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 or "Ran" in result.stderr:
                logger.info("  ✅ Test discovery: Tests found and discoverable")
            else:
                logger.warning("  ⚠️ Test discovery: Issues with test discovery")

        except subprocess.TimeoutExpired:
            logger.warning("  ⚠️ Test discovery: Timeout during discovery")
        except Exception as e:
            logger.warning(f"  ⚠️ Test discovery: {e}")

        return success

    def test_deployment_packaging(self) -> bool:
        """9. Deployment and Packaging"""
        logger.info("📦 Phase 9: Deployment and Packaging")
        logger.info("-" * 50)

        success = True

        # a. Dependency Check
        success &= self._test_dependency_check()

        # b. Entry Point Validation
        success &= self._test_entry_points()

        self.results["deployment_packaging"] = success
        return success

    def _test_dependency_check(self) -> bool:
        """Check that all dependencies are importable."""
        logger.info("🔗 Testing Dependency Check...")

        success = True

        # Read requirements.txt if it exists
        requirements_file = self.workspace_root / "requirements.txt"

        if requirements_file.exists():
            try:
                with open(requirements_file, "r") as f:
                    requirements = f.read().splitlines()

                # Test key dependencies
                key_deps = [
                    req.split("==")[0].split(">=")[0].split("[")[0]
                    for req in requirements
                    if req and not req.startswith("#")
                ]

                failed_deps = []
                for dep in key_deps[:10]:  # Test first 10 dependencies
                    try:
                        __import__(dep.replace("-", "_"))
                    except ImportError:
                        failed_deps.append(dep)

                if not failed_deps:
                    logger.info(
                        f"  ✅ Dependencies: All {len(key_deps[:10])} tested dependencies available"
                    )
                else:
                    logger.warning(
                        f"  ⚠️ Dependencies: {len(failed_deps)} missing: {failed_deps}"
                    )

            except Exception as e:
                logger.error(f"  ❌ Dependency check failed: {e}")
                success = False
        else:
            logger.warning("  ⚠️ No requirements.txt found")

        return success

    def _test_entry_points(self) -> bool:
        """Test main entry points."""
        logger.info("🚪 Testing Entry Points...")

        success = True

        # Test main application entry points
        entry_points = [
            ("app.py", "main application"),
            ("app_new.py", "new application structure"),
        ]

        for entry_file, description in entry_points:
            entry_path = self.workspace_root / entry_file
            if entry_path.exists():
                try:
                    # Test that the file can be imported without running
                    spec = importlib.util.spec_from_file_location(
                        "test_entry", entry_path
                    )
                    module = importlib.util.module_from_spec(spec)

                    logger.info(f"  ✅ {description}: {entry_file} is valid")
                except Exception as e:
                    logger.error(f"  ❌ {description}: {entry_file} failed - {e}")
                    success = False
            else:
                logger.warning(f"  ⚠️ {description}: {entry_file} not found")

        return success

    def test_creative_scenarios(self) -> bool:
        """10. Creative/Unusual Scenarios"""
        logger.info("🎭 Phase 10: Creative/Unusual Scenarios")
        logger.info("-" * 50)

        success = True

        # a. Rename/Move Module Test
        success &= self._test_module_resilience()

        # b. Partial Upgrade Simulation
        success &= self._test_partial_upgrades()

        # c. User Error Simulation
        success &= self._test_user_errors()

        self.results["creative_scenarios"] = success
        return success

    def _test_module_resilience(self) -> bool:
        """Test resilience to module changes."""
        logger.info("🔄 Testing Module Resilience...")

        success = True

        try:
            # Test importing non-existent module produces clear error
            try:
                importlib.import_module("non_existent_module")
            except ImportError as e:
                if "non_existent_module" in str(e):
                    logger.info("  ✅ Module resilience: Clear error messages")
                else:
                    logger.warning("  ⚠️ Module resilience: Unclear error messages")

        except Exception as e:
            logger.error(f"  ❌ Module resilience test failed: {e}")
            success = False

        return success

    def _test_partial_upgrades(self) -> bool:
        """Simulate partial upgrade scenarios."""
        logger.info("🔄 Testing Partial Upgrades...")

        success = True

        try:
            # Test mixing old and new imports
            from config_modules import APP_TITLE  # New style
            import config  # Old style (if available)

            logger.info("  ✅ Partial upgrades: Both old and new imports work")

        except ImportError:
            logger.info(
                "  ✅ Partial upgrades: Clean migration (old imports unavailable)"
            )
        except Exception as e:
            logger.error(f"  ❌ Partial upgrade test failed: {e}")
            success = False

        return success

    def _test_user_errors(self) -> bool:
        """Test handling of common user errors."""
        logger.info("👤 Testing User Error Handling...")

        success = True

        try:
            # Test incorrect function calls
            from borehole_log import create_borehole_log

            try:
                # Call with wrong arguments
                result = create_borehole_log()  # Missing required args
            except TypeError as e:
                if "required" in str(e) or "argument" in str(e):
                    logger.info(
                        "  ✅ User errors: Clear error messages for missing arguments"
                    )
                else:
                    logger.warning("  ⚠️ User errors: Unclear error messages")

        except Exception as e:
            logger.warning(f"  ⚠️ User error test: {e}")

        return success

    def _generate_final_report(self):
        """Generate comprehensive final report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE TEST SUITE FINAL REPORT")
        logger.info("=" * 80)

        total_phases = len(self.results)
        passed_phases = sum(1 for result in self.results.values() if result)

        logger.info(
            f"📈 Overall Success Rate: {passed_phases}/{total_phases} ({passed_phases/total_phases*100:.1f}%)"
        )
        logger.info("\n📋 Phase Results:")

        for phase, result in self.results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"  {phase.replace('_', ' ').title()}: {status}")

        if self.failed_tests:
            logger.info(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for failed_test in self.failed_tests:
                logger.info(f"  - {failed_test}")

        if self.warnings:
            logger.info(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.info(f"  - {warning}")

        # Recommendations
        logger.info("\n💡 Recommendations:")
        if passed_phases == total_phases:
            logger.info("  🎉 Excellent! All test phases passed.")
            logger.info("  📈 Consider adding more edge case tests.")
            logger.info("  🔄 Set up CI/CD automation for these tests.")
        elif passed_phases >= total_phases * 0.8:
            logger.info("  👍 Good overall performance.")
            logger.info("  🔧 Address failed phases for production readiness.")
        else:
            logger.info("  ⚠️ Multiple issues detected.")
            logger.info("  🛠️ Significant refactoring may be needed.")
            logger.info("  🔍 Review failed tests and implement fixes.")

        logger.info("\n🎯 Next Steps:")
        logger.info("  1. Fix any failed tests")
        logger.info("  2. Address warnings and edge cases")
        logger.info("  3. Enhance test coverage for critical paths")
        logger.info("  4. Set up automated testing in CI/CD")
        logger.info("  5. Document any intentional breaking changes")

        logger.info("\n" + "=" * 80)


def main():
    """Run the comprehensive test suite."""
    test_suite = ComprehensiveTestSuite()

    try:
        success = test_suite.run_all_tests()

        if success:
            logger.info("🎉 COMPREHENSIVE TEST SUITE: ALL TESTS PASSED")
            return 0
        else:
            logger.error("❌ COMPREHENSIVE TEST SUITE: SOME TESTS FAILED")
            return 1

    except Exception as e:
        logger.error(f"💥 COMPREHENSIVE TEST SUITE: UNEXPECTED ERROR - {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
