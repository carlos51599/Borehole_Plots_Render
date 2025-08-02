"""
Test script to validate React lifecycle warnings suppression.

This script validates that:
1. The suppression file is created correctly
2. The JavaScript suppression code is properly formatted
3. The suppression file can be removed
4. The application starts without errors with suppression enabled

Run this script to test the React warnings suppression functionality.
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from react_warnings_suppressor import (
    suppress_react_warnings,
    remove_suppression,
    create_warning_suppression_js,
)

# Configure logging for test output
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_suppression_file_creation():
    """Test that the React warnings suppression file is created correctly."""
    logger.info("Testing suppression file creation...")

    # Clean up any existing file first
    remove_suppression()

    # Create the suppression file
    result = create_warning_suppression_js()

    if result and os.path.exists(result):
        logger.info("✓ Suppression file created: %s", result)

        # Verify file contents
        with open(result, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key components in the JavaScript
        required_elements = [
            "console.warn",
            "componentWillMount has been renamed",
            "componentWillReceiveProps has been renamed",
            "originalConsoleWarn",
            "React lifecycle warnings suppressor loaded",
        ]

        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)

        if missing_elements:
            logger.error("✗ Missing elements in suppression file: %s", missing_elements)
            return False
        else:
            logger.info("✓ Suppression file contains all required elements")
            return True
    else:
        logger.error("✗ Failed to create suppression file")
        return False


def test_suppression_file_removal():
    """Test that the React warnings suppression file can be removed."""
    logger.info("Testing suppression file removal...")

    # Ensure file exists first
    create_warning_suppression_js()

    # Remove the file
    result = remove_suppression()

    suppression_file = os.path.join("assets", "suppress_react_warnings.js")

    if result and not os.path.exists(suppression_file):
        logger.info("✓ Suppression file removed successfully")
        return True
    else:
        logger.error("✗ Failed to remove suppression file")
        return False


def test_application_startup():
    """Test that the application starts correctly with suppression enabled."""
    logger.info("Testing application startup with suppression...")

    # Ensure suppression is enabled
    suppress_react_warnings()

    try:
        # Start the application in a subprocess
        logger.info("Starting Dash application...")

        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root,
        )

        # Wait a few seconds for startup
        time.sleep(8)

        # Check if process is still running (indicating successful startup)
        if process.poll() is None:
            logger.info("✓ Application started successfully")

            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            return True
        else:
            # Process terminated, check output for errors
            stdout, stderr = process.communicate()
            logger.error("✗ Application failed to start")
            logger.error("STDOUT: %s", stdout)
            logger.error("STDERR: %s", stderr)
            return False

    except Exception as e:
        logger.error("✗ Error testing application startup: %s", e)
        return False


def test_python_import():
    """Test that the suppression module can be imported correctly."""
    logger.info("Testing Python module import...")

    try:
        from react_warnings_suppressor import suppress_react_warnings  # noqa: F401

        logger.info("✓ Module imported successfully")
        return True
    except ImportError as e:
        logger.error("✗ Failed to import module: %s", e)
        return False


def run_all_tests():
    """Run all test functions and report results."""
    logger.info("=" * 60)
    logger.info("REACT WARNINGS SUPPRESSION TEST SUITE")
    logger.info("=" * 60)

    tests = [
        ("Python Import", test_python_import),
        ("Suppression File Creation", test_suppression_file_creation),
        ("Suppression File Removal", test_suppression_file_removal),
        ("Application Startup", test_application_startup),
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info("\n--- Running: %s ---", test_name)
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error("✗ Test %s raised exception: %s", test_name, e)
            results[test_name] = False

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info("%-30s : %s", test_name, status)
        if result:
            passed += 1

    logger.info("-" * 60)
    logger.info("Tests passed: %d/%d", passed, total)

    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("\nReact warnings suppression is working correctly.")
        logger.info("The JavaScript file will suppress componentWillMount and")
        logger.info("componentWillReceiveProps warnings in the browser console.")
    else:
        logger.error("❌ SOME TESTS FAILED!")
        logger.error("Please check the error messages above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()

    print("\n" + "=" * 60)
    print("USAGE INSTRUCTIONS")
    print("=" * 60)
    print("1. The suppression file is automatically loaded by Dash")
    print("2. React lifecycle warnings will be suppressed in browser console")
    print("3. To disable: python react_warnings_suppressor.py --remove")
    print("4. To re-enable: python react_warnings_suppressor.py")
    print("\nNote: These warnings are cosmetic and don't affect functionality.")

    sys.exit(0 if success else 1)
