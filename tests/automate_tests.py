#!/usr/bin/env python3
"""
Test Automation Script for Continuous Integration

This script provides automated testing capabilities for CI/CD pipelines,
implementing the complete Comprehensive Post-Restructuring Test Action Plan.

Features:
- Automated test execution with multiple output formats
- Performance benchmarking and trend analysis
- Integration with popular CI/CD systems
- Detailed reporting and metrics collection
- Failure analysis and recommendations

Usage in CI/CD:
    # Basic CI test run
    python automate_tests.py --ci

    # Full test suite with detailed reporting
    python automate_tests.py --full --output-format json --save-metrics

    # Quick health check
    python automate_tests.py --health-check

Author: GitHub Copilot
Date: July 23, 2025
"""

import sys
import os
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

# Add workspace to path
sys.path.insert(0, os.path.abspath("."))


class TestAutomationEngine:
    """Automated testing engine for CI/CD integration."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(__file__).parent.parent
        self.results_dir = self.workspace_root / "test_results"
        self.results_dir.mkdir(exist_ok=True)

        self.test_history = []
        self.performance_metrics = {}

    def run_health_check(self) -> bool:
        """Quick health check for essential functionality."""
        print("🏥 HEALTH CHECK - Essential Functionality")
        print("=" * 50)

        health_tests = [
            ("Import Core Modules", self._test_core_imports),
            ("App Creation", self._test_app_creation),
            ("Config Access", self._test_config_access),
            ("Basic Syntax", self._test_basic_syntax),
        ]

        results = {}
        overall_health = True

        for test_name, test_func in health_tests:
            print(f"🔍 {test_name}...", end=" ")

            try:
                start_time = time.time()
                success = test_func()
                duration = time.time() - start_time

                status = "✅" if success else "❌"
                print(f"{status} ({duration:.2f}s)")

                results[test_name] = {"success": success, "duration": duration}

                if not success:
                    overall_health = False

            except Exception as e:
                print(f"❌ ERROR: {e}")
                results[test_name] = {"success": False, "error": str(e)}
                overall_health = False

        # Save health check results
        self._save_health_results(results, overall_health)

        status = "HEALTHY" if overall_health else "UNHEALTHY"
        print(f"\n🏥 Health Check: {status}")

        return overall_health

    def _test_core_imports(self) -> bool:
        """Test core module imports."""
        try:
            import app_modules  # noqa: F401
            import config_modules  # noqa: F401
            import borehole_log  # noqa: F401
            import section  # noqa: F401
            import state_management  # noqa: F401

            return True
        except ImportError:
            return False

    def _test_app_creation(self) -> bool:
        """Test basic app creation."""
        try:
            from app_modules import create_and_configure_app

            app = create_and_configure_app()
            return app is not None
        except Exception:
            return False

    def _test_config_access(self) -> bool:
        """Test configuration access."""
        try:
            from config_modules import APP_TITLE, MAP_HEIGHT

            return bool(APP_TITLE and MAP_HEIGHT)
        except Exception:
            return False

    def _test_basic_syntax(self) -> bool:
        """Test basic syntax validation on key files."""
        try:
            key_files = [
                "app.py",
                "config.py",
                "app_modules/__init__.py",
                "config_modules/__init__.py",
            ]

            for file_path in key_files:
                full_path = self.workspace_root / file_path
                if full_path.exists():
                    with open(full_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    compile(source, str(full_path), "exec")

            return True
        except SyntaxError:
            return False

    def run_ci_tests(self) -> Dict[str, Any]:
        """Run tests optimized for CI/CD environments."""
        print("🔄 CI/CD TEST EXECUTION")
        print("=" * 50)

        ci_start_time = time.time()

        # Run core test suite
        ci_results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "CI/CD",
            "tests": {},
        }

        # Essential tests for CI
        test_commands = [
            ("import_syntax", ["python", "tests\\test_import_syntax_validation.py"]),
            (
                "comprehensive_quick",
                ["python", "tests\\run_comprehensive_tests.py", "--quick"],
            ),
        ]

        for test_name, command in test_commands:
            print(f"🧪 Running {test_name}...")

            try:
                result = subprocess.run(
                    command,
                    cwd=str(self.workspace_root),
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                success = result.returncode == 0

                ci_results["tests"][test_name] = {
                    "success": success,
                    "returncode": result.returncode,
                    "stdout_lines": len(result.stdout.splitlines()),
                    "stderr_lines": len(result.stderr.splitlines()),
                    "has_output": bool(result.stdout.strip()),
                }

                status = "✅" if success else "❌"
                print(f"  {status} {test_name}: {'PASSED' if success else 'FAILED'}")

            except subprocess.TimeoutExpired:
                print(f"  ⏰ {test_name}: TIMEOUT")
                ci_results["tests"][test_name] = {"success": False, "error": "timeout"}
            except Exception as e:
                print(f"  ❌ {test_name}: ERROR - {e}")
                ci_results["tests"][test_name] = {"success": False, "error": str(e)}

        ci_duration = time.time() - ci_start_time
        ci_results["duration"] = ci_duration

        # Calculate success metrics
        total_tests = len(ci_results["tests"])
        passed_tests = sum(
            1 for t in ci_results["tests"].values() if t.get("success", False)
        )

        ci_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "overall_success": passed_tests == total_tests,
        }

        # Save CI results
        self._save_ci_results(ci_results)

        print(
            f"\n📊 CI Results: {passed_tests}/{total_tests} tests passed ({ci_results['summary']['success_rate']:.1f}%)"
        )
        print(f"⏱️ Total Duration: {ci_duration:.2f} seconds")

        return ci_results

    def run_full_test_suite(self, save_metrics: bool = False) -> Dict[str, Any]:
        """Run complete test suite with detailed analysis."""
        print("🎯 FULL TEST SUITE EXECUTION")
        print("=" * 50)

        full_start_time = time.time()

        # Health check first
        health_ok = self.run_health_check()

        if not health_ok:
            print("\n⚠️ Health check failed - proceeding with caution")

        # Run comprehensive tests
        print(f"\n🚀 Running comprehensive test suite...")

        try:
            result = subprocess.run(
                ["python", "tests\\run_comprehensive_tests.py"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            full_duration = time.time() - full_start_time

            # Parse results
            full_results = {
                "timestamp": datetime.now().isoformat(),
                "environment": "full_suite",
                "health_check": health_ok,
                "comprehensive_test": {
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "duration": full_duration,
                    "output_lines": len(result.stdout.splitlines()),
                },
            }

            # Try to load detailed results if available
            results_file = self.workspace_root / "test_results.json"
            if results_file.exists():
                try:
                    with open(results_file, "r") as f:
                        detailed_results = json.load(f)
                        full_results["detailed"] = detailed_results
                except Exception:
                    pass

            # Save performance metrics
            if save_metrics:
                self._save_performance_metrics(full_results)

            # Save full results
            self._save_full_results(full_results)

            status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
            print(f"\n🎯 Full Test Suite: {status}")
            print(f"⏱️ Total Duration: {full_duration:.2f} seconds")

            return full_results

        except subprocess.TimeoutExpired:
            print(f"\n⏰ Full test suite timed out")
            return {
                "timestamp": datetime.now().isoformat(),
                "environment": "full_suite",
                "error": "timeout",
                "duration": time.time() - full_start_time,
            }
        except Exception as e:
            print(f"\n❌ Full test suite error: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "environment": "full_suite",
                "error": str(e),
                "duration": time.time() - full_start_time,
            }

    def generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis from historical test data."""
        print("📈 TREND ANALYSIS")
        print("=" * 30)

        # Load historical results
        history_files = list(self.results_dir.glob("*_results.json"))
        history_files.sort(key=lambda x: x.stat().st_mtime)

        if len(history_files) < 2:
            print("📊 Insufficient historical data for trend analysis")
            return {"status": "insufficient_data"}

        # Analyze trends
        trends = {
            "test_count_trend": [],
            "success_rate_trend": [],
            "duration_trend": [],
            "analysis": {},
        }

        for history_file in history_files[-10:]:  # Last 10 runs
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)

                timestamp = data.get("timestamp", "")
                summary = data.get("summary", {})

                trends["success_rate_trend"].append(
                    {
                        "timestamp": timestamp,
                        "success_rate": summary.get("success_rate", 0),
                    }
                )

                trends["duration_trend"].append(
                    {"timestamp": timestamp, "duration": data.get("duration", 0)}
                )

            except Exception:
                continue

        # Calculate trend analysis
        if trends["success_rate_trend"]:
            recent_success_rates = [
                t["success_rate"] for t in trends["success_rate_trend"][-5:]
            ]
            avg_success_rate = sum(recent_success_rates) / len(recent_success_rates)

            trends["analysis"] = {
                "average_success_rate": avg_success_rate,
                "trend_direction": "stable",  # Could be enhanced with actual trend calculation
                "recommendation": (
                    "Monitor success rate"
                    if avg_success_rate < 95
                    else "Excellent performance"
                ),
            }

        print(
            f"📊 Average Success Rate (last 5 runs): {trends['analysis'].get('average_success_rate', 0):.1f}%"
        )
        print(f"💡 Recommendation: {trends['analysis'].get('recommendation', 'N/A')}")

        return trends

    def _save_health_results(self, results: Dict, overall_health: bool):
        """Save health check results."""
        health_file = (
            self.results_dir / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": overall_health,
            "tests": results,
        }

        with open(health_file, "w") as f:
            json.dump(health_data, f, indent=2)

    def _save_ci_results(self, results: Dict):
        """Save CI test results."""
        ci_file = (
            self.results_dir / f"ci_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(ci_file, "w") as f:
            json.dump(results, f, indent=2)

    def _save_full_results(self, results: Dict):
        """Save full test suite results."""
        full_file = (
            self.results_dir / f"full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(full_file, "w") as f:
            json.dump(results, f, indent=2)

    def _save_performance_metrics(self, results: Dict):
        """Save performance metrics for trending."""
        metrics_file = self.results_dir / "performance_metrics.json"

        # Load existing metrics
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                metrics = json.load(f)
        else:
            metrics = {"history": []}

        # Add current metrics
        current_metrics = {
            "timestamp": results["timestamp"],
            "duration": results.get("duration", 0),
            "success": results.get("comprehensive_test", {}).get("success", False),
        }

        metrics["history"].append(current_metrics)

        # Keep only last 50 entries
        metrics["history"] = metrics["history"][-50:]

        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)


def main():
    """Main entry point for test automation."""
    parser = argparse.ArgumentParser(
        description="Test Automation Engine for CI/CD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--health-check", action="store_true", help="Run quick health check only"
    )

    parser.add_argument(
        "--ci", action="store_true", help="Run CI/CD optimized test suite"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run complete test suite with detailed analysis",
    )

    parser.add_argument(
        "--save-metrics",
        action="store_true",
        help="Save performance metrics for trending",
    )

    parser.add_argument(
        "--trend-analysis",
        action="store_true",
        help="Generate trend analysis from historical data",
    )

    parser.add_argument(
        "--output-format",
        choices=["console", "json"],
        default="console",
        help="Output format for results",
    )

    args = parser.parse_args()

    # Create automation engine
    engine = TestAutomationEngine()

    success = True
    results = {}

    try:
        if args.health_check:
            success = engine.run_health_check()

        elif args.ci:
            results = engine.run_ci_tests()
            success = results.get("summary", {}).get("overall_success", False)

        elif args.full:
            results = engine.run_full_test_suite(save_metrics=args.save_metrics)
            success = results.get("comprehensive_test", {}).get("success", False)

        elif args.trend_analysis:
            results = engine.generate_trend_analysis()
            success = True  # Trend analysis doesn't fail

        else:
            # Default: run health check
            success = engine.run_health_check()

        # Output results
        if args.output_format == "json" and results:
            print(json.dumps(results, indent=2))

        exit_code = 0 if success else 1

        print(f"\n🏁 Automation completed with exit code: {exit_code}")
        return exit_code

    except KeyboardInterrupt:
        print("\n⚠️ Test automation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test automation error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
