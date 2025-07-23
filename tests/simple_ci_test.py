#!/usr/bin/env python3
"""
Simple CI Test Runner for Automated Testing

A streamlined testing script designed for CI/CD integration.
Runs essential tests with minimal output and clear exit codes.
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add workspace to path
sys.path.insert(0, os.path.abspath("."))


def run_quick_health_check():
    """Quick health check for essential functionality."""
    print("🏥 Health Check")

    try:
        # Test imports
        import app_modules  # noqa: F401
        import config_modules  # noqa: F401
        import borehole_log  # noqa: F401
        import section  # noqa: F401
        import state_management  # noqa: F401

        print("  ✅ Core imports successful")

        # Test app creation
        from app_modules import create_and_configure_app

        app = create_and_configure_app()
        if app is not None:
            print("  ✅ App creation successful")
        else:
            print("  ❌ App creation failed")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Health check failed: {e}")
        return False


def run_essential_tests():
    """Run essential tests for CI/CD."""
    print("🧪 Essential Tests")

    tests_passed = 0
    total_tests = 0

    # Test 1: Import validation
    print("  Running import validation...")
    try:
        result = subprocess.run(
            [sys.executable, "tests\\test_import_syntax_validation.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.getcwd(),
        )

        if result.returncode == 0:
            print("    ✅ Import validation passed")
            tests_passed += 1
        else:
            print("    ❌ Import validation failed")
            print(f"    Error output: {result.stderr[:200]}...")

        total_tests += 1

    except Exception as e:
        print(f"    ❌ Import validation error: {e}")
        total_tests += 1

    # Test 2: Quick comprehensive test
    print("  Running quick comprehensive test...")
    try:
        result = subprocess.run(
            [sys.executable, "tests\\run_comprehensive_tests.py", "--quick"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=os.getcwd(),
        )

        if result.returncode == 0:
            print("    ✅ Comprehensive test passed")
            tests_passed += 1
        else:
            print("    ❌ Comprehensive test failed")
            print(f"    Error output: {result.stderr[:200]}...")

        total_tests += 1

    except Exception as e:
        print(f"    ❌ Comprehensive test error: {e}")
        total_tests += 1

    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    print(
        f"📊 Essential Tests: {tests_passed}/{total_tests} passed ({success_rate:.1f}%)"
    )

    return tests_passed == total_tests


def save_ci_results(health_ok, tests_ok, duration):
    """Save CI results to JSON."""
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)

    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": "simple_ci",
        "health_check": health_ok,
        "essential_tests": tests_ok,
        "duration": duration,
        "overall_success": health_ok and tests_ok,
    }

    results_file = (
        results_dir / f"simple_ci_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    return results


def main():
    """Main CI testing function."""
    print("🚀 SIMPLE CI TEST RUNNER")
    print("=" * 40)

    start_time = time.time()

    # Run health check
    health_ok = run_quick_health_check()

    # Run essential tests
    tests_ok = run_essential_tests()

    duration = time.time() - start_time

    # Save results
    results = save_ci_results(health_ok, tests_ok, duration)

    # Final status
    overall_success = health_ok and tests_ok
    status = "✅ PASSED" if overall_success else "❌ FAILED"

    print(f"\n🏁 CI Results: {status}")
    print(f"⏱️ Duration: {duration:.2f} seconds")

    if not overall_success:
        print("\n💡 Recommendations:")
        if not health_ok:
            print("  • Fix core module import or app creation issues")
        if not tests_ok:
            print("  • Review failed test outputs for specific issues")
        print("  • Run individual tests manually for detailed debugging")

    return 0 if overall_success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ CI testing interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 CI testing error: {e}")
        sys.exit(2)
