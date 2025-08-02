#!/usr/bin/env python3
"""
Comprehensive Error Detection and Testing Script

This script performs a thorough analysis of the current application state,
identifies active errors, and provides diagnostic information for debugging.
"""

import sys
import traceback
import logging
import importlib
import os
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ApplicationDiagnostics:
    """Comprehensive application diagnostics and error detection."""

    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive testing and diagnostics."""
        print("🔍 Starting Comprehensive Application Diagnostics")
        print("=" * 60)

        # Test 1: Core Module Imports
        self.test_core_imports()

        # Test 2: Section Plotting Functionality
        self.test_section_plotting()

        # Test 3: Borehole Log Functionality
        self.test_borehole_log()

        # Test 4: Error Handling System
        self.test_error_handling()

        # Test 5: Data Processing Functions
        self.test_data_processing()

        # Test 6: Configuration Loading
        self.test_configuration()

        # Test 7: File System Access
        self.test_file_system()

        # Final Report
        self.generate_report()

        return self.results

    def test_core_imports(self):
        """Test core module imports."""
        print("\n📦 Testing Core Module Imports")
        print("-" * 30)

        modules_to_test = [
            "app",
            "app_constants",
            "error_handling",
            "data_loader",
            "coordinate_service",
            "borehole_log_professional",
            "section.plotting.main",
            "section.plotting.geology",
            "section.plotting.coordinates",
            "section.plotting.layout",
            "section.parsing",
        ]

        import_results = {}

        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                print(f"✅ {module_name}")
                import_results[module_name] = "success"
            except Exception as e:
                print(f"❌ {module_name}: {str(e)}")
                import_results[module_name] = str(e)
                self.errors.append(f"Import error for {module_name}: {str(e)}")

        self.results["imports"] = import_results

    def test_section_plotting(self):
        """Test section plotting functionality."""
        print("\n🗺️ Testing Section Plotting")
        print("-" * 30)

        try:
            from section.plotting.main import plot_section_from_ags_content

            print("✅ Section plotting import successful")

            # Test with minimal AGS data
            test_ags = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_GL,LOCA_NATE,LOCA_NATN
UNITS,<blank>,<blank>,m,m,m
TYPE,ID,X,2DP,2DP,2DP
DATA,BH01,RC,100.00,451000,290000

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_DESC
UNITS,<blank>,m,m,<blank>
TYPE,ID,2DP,2DP,X
DATA,BH01,0.00,2.50,TOPSOIL: Dark brown sandy clay
DATA,BH01,2.50,8.00,CLAY: Firm brown clay"""

            # Test the function call
            result = plot_section_from_ags_content(
                ags_content=test_ags, filename="test.ags", return_base64=False
            )

            if hasattr(result, "figure"):
                print(
                    "✅ Section plotting executed successfully - returned Figure object"
                )
                self.results["section_plotting"] = "success"
            elif str(type(result)) == "<class 'matplotlib.figure.Figure'>":
                print(
                    "✅ Section plotting executed successfully - returned matplotlib Figure"
                )
                self.results["section_plotting"] = "success"
            else:
                print(f"⚠️ Section plotting returned unexpected type: {type(result)}")
                self.warnings.append(
                    f"Section plotting returned unexpected type: {type(result)}"
                )
                self.results["section_plotting"] = f"unexpected_type_{type(result)}"

        except Exception as e:
            print(f"❌ Section plotting error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            traceback.print_exc()
            self.errors.append(f"Section plotting error: {str(e)}")
            self.results["section_plotting"] = str(e)

    def test_borehole_log(self):
        """Test borehole log functionality."""
        print("\n📊 Testing Borehole Log")
        print("-" * 30)

        try:
            from borehole_log_professional import plot_borehole_log_from_ags_content

            print("✅ Borehole log import successful")

            # Test with minimal AGS data
            test_ags = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_GL,LOCA_NATE,LOCA_NATN
UNITS,<blank>,<blank>,m,m,m
TYPE,ID,X,2DP,2DP,2DP
DATA,BH01,RC,100.00,451000,290000

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_DESC
UNITS,<blank>,m,m,<blank>
TYPE,ID,2DP,2DP,X
DATA,BH01,0.00,2.50,TOPSOIL: Dark brown sandy clay
DATA,BH01,2.50,8.00,CLAY: Firm brown clay"""

            # Test the function call
            result = plot_borehole_log_from_ags_content(
                ags_content=test_ags, loca_id="BH01", return_base64=False
            )

            if (
                hasattr(result, "figure")
                or str(type(result)) == "<class 'matplotlib.figure.Figure'>"
            ):
                print("✅ Borehole log executed successfully")
                self.results["borehole_log"] = "success"
            else:
                print(f"⚠️ Borehole log returned unexpected type: {type(result)}")
                self.warnings.append(
                    f"Borehole log returned unexpected type: {type(result)}"
                )
                self.results["borehole_log"] = f"unexpected_type_{type(result)}"

        except Exception as e:
            print(f"❌ Borehole log error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            self.errors.append(f"Borehole log error: {str(e)}")
            self.results["borehole_log"] = str(e)

    def test_error_handling(self):
        """Test error handling system."""
        print("\n🚨 Testing Error Handling System")
        print("-" * 30)

        try:
            from error_handling import ErrorHandler, get_error_handler

            # Test error handler creation
            handler = get_error_handler()
            print("✅ Error handler created successfully")

            # Test error creation
            from error_handling import ErrorCategory, ErrorSeverity

            test_error = handler.create_error(
                message="Test error",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.INFO,
            )
            print("✅ Error creation successful")

            self.results["error_handling"] = "success"

        except Exception as e:
            print(f"❌ Error handling test failed: {str(e)}")
            self.errors.append(f"Error handling test failed: {str(e)}")
            self.results["error_handling"] = str(e)

    def test_data_processing(self):
        """Test data processing functions."""
        print("\n📋 Testing Data Processing")
        print("-" * 30)

        try:
            from data_loader import parse_ags_content

            print("✅ Data loader import successful")

            # Test with simple AGS content
            test_ags = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_GL
UNITS,<blank>,<blank>,m
TYPE,ID,X,2DP
DATA,BH01,RC,100.00"""

            result = parse_ags_content(test_ags)
            if result:
                print("✅ AGS parsing successful")
                self.results["data_processing"] = "success"
            else:
                print("⚠️ AGS parsing returned empty result")
                self.warnings.append("AGS parsing returned empty result")
                self.results["data_processing"] = "empty_result"

        except Exception as e:
            print(f"❌ Data processing error: {str(e)}")
            self.errors.append(f"Data processing error: {str(e)}")
            self.results["data_processing"] = str(e)

    def test_configuration(self):
        """Test configuration loading."""
        print("\n⚙️ Testing Configuration")
        print("-" * 30)

        try:
            import app_constants

            print("✅ App constants loaded")

            # Check for key constants
            if hasattr(app_constants, "A4_LANDSCAPE_WIDTH"):
                print("✅ Layout constants available")
            else:
                print("⚠️ Layout constants missing")
                self.warnings.append("Layout constants missing from app_constants")

            self.results["configuration"] = "success"

        except Exception as e:
            print(f"❌ Configuration error: {str(e)}")
            self.errors.append(f"Configuration error: {str(e)}")
            self.results["configuration"] = str(e)

    def test_file_system(self):
        """Test file system access."""
        print("\n📁 Testing File System Access")
        print("-" * 30)

        try:
            # Check for critical files
            critical_files = [
                "Geology Codes BGS.csv",
                "app.py",
                "borehole_log_professional.py",
            ]

            missing_files = []
            for file_path in critical_files:
                if os.path.exists(file_path):
                    print(f"✅ {file_path}")
                else:
                    print(f"❌ {file_path} - Missing")
                    missing_files.append(file_path)

            if missing_files:
                self.errors.append(f"Missing critical files: {missing_files}")
                self.results["file_system"] = f"missing_files: {missing_files}"
            else:
                self.results["file_system"] = "success"

        except Exception as e:
            print(f"❌ File system test error: {str(e)}")
            self.errors.append(f"File system test error: {str(e)}")
            self.results["file_system"] = str(e)

    def generate_report(self):
        """Generate comprehensive diagnostic report."""
        print("\n📋 COMPREHENSIVE DIAGNOSTIC REPORT")
        print("=" * 60)

        print(
            f"\n✅ SUCCESSES: {len([r for r in self.results.values() if r == 'success'])}"
        )
        print(f"⚠️ WARNINGS: {len(self.warnings)}")
        print(f"❌ ERRORS: {len(self.errors)}")

        if self.errors:
            print("\n🚨 ACTIVE ERRORS:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        # Determine overall system health
        error_count = len(self.errors)
        warning_count = len(self.warnings)

        if error_count == 0 and warning_count == 0:
            health_status = "🟢 EXCELLENT"
        elif error_count == 0 and warning_count <= 2:
            health_status = "🟡 GOOD (Minor warnings)"
        elif error_count <= 2:
            health_status = "🟠 FAIR (Some issues)"
        else:
            health_status = "🔴 POOR (Multiple errors)"

        print(f"\n🏥 OVERALL SYSTEM HEALTH: {health_status}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if error_count == 0:
            print("  • System appears healthy - continue normal operations")
        else:
            print("  • Address the errors listed above")
            print("  • Run tests after each fix to verify resolution")

        if (
            "section_plotting" in self.results
            and self.results["section_plotting"] != "success"
        ):
            print("  • Focus on section plotting issues first")

        return {
            "overall_health": health_status,
            "error_count": error_count,
            "warning_count": warning_count,
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }


def main():
    """Main execution function."""
    try:
        diagnostics = ApplicationDiagnostics()
        results = diagnostics.run_comprehensive_test()

        # Save results to file for reference
        import json

        with open("diagnostic_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Diagnostic results saved to: diagnostic_results.json")

        return results

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR in diagnostics: {str(e)}")
        traceback.print_exc()
        return {"critical_error": str(e)}


if __name__ == "__main__":
    main()
