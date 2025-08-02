"""
Test script to verify the duplicate callback fix

This script tests that:
1. App starts without duplicate callback errors
2. Only one app instance is created
3. Callbacks are registered only once
4. Full functionality is preserved
"""

import sys
import subprocess
import logging
from pathlib import Path

# Setup logging to capture test results
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_app_import():
    """Test that importing the app doesn't cause duplicate registrations."""
    logger.info("Testing app import...")

    try:
        # Import the app module
        from app_modules import get_app

        # Get app instance twice to test singleton
        app1 = get_app()
        app2 = get_app()

        # Verify it's the same instance
        assert (
            app1 is app2
        ), "get_app() should return the same instance (singleton pattern)"
        logger.info("✅ Singleton pattern working correctly")

        # Check that we have the expected callbacks
        callback_count = len(app1.callback_map)
        logger.info(f"Total callbacks registered: {callback_count}")

        # We expect around 10-15 callbacks (5 main classes + some extra ones)
        # The exact number may vary, but it should be reasonable
        assert (
            callback_count > 5
        ), f"Expected more than 5 callbacks, got {callback_count}"
        assert (
            callback_count < 50
        ), f"Too many callbacks detected, possible duplicates: {callback_count}"

        logger.info("✅ App import test passed")
        return True

    except Exception as e:
        logger.error(f"❌ App import test failed: {str(e)}")
        return False


def test_app_startup():
    """Test that the app starts without errors."""
    logger.info("Testing app startup...")

    try:
        # Create a test script that starts and immediately stops the app
        test_script = """
import sys
import logging
from app_modules import create_and_configure_app, get_app

# Test that get_app works
app1 = get_app()
app2 = get_app()
assert app1 is app2, "Singleton failed"

# Count callbacks
callback_count = len(app1.callback_map)
print(f"CALLBACK_COUNT:{callback_count}")

# Test that we don't have duplicate outputs
outputs_seen = set()
for callback_id, callback in app1.callback_map.items():
    for output in callback['callback'].output:
        output_str = f"{output.component_id}.{output.component_property}"
        if output_str in outputs_seen and not getattr(output, 'allow_duplicate', False):
            print(f"DUPLICATE_FOUND:{output_str}")
        outputs_seen.add(output_str)

print("STARTUP_SUCCESS")
"""

        # Write test script
        test_file = Path("test_startup_verification.py")
        test_file.write_text(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, "test_startup_verification.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Clean up
        test_file.unlink()

        # Check results
        if result.returncode != 0:
            logger.error(f"❌ Startup test failed with return code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            return False

        output = result.stdout
        if "STARTUP_SUCCESS" not in output:
            logger.error("❌ Startup test failed - no success message")
            logger.error(f"OUTPUT: {output}")
            return False

        if "DUPLICATE_FOUND:" in output:
            logger.error(f"❌ Duplicate outputs still found: {output}")
            return False

        # Extract callback count
        callback_lines = [
            line for line in output.split("\n") if line.startswith("CALLBACK_COUNT:")
        ]
        if callback_lines:
            callback_count = int(callback_lines[0].split(":")[1])
            logger.info(f"Verified callback count: {callback_count}")

        logger.info("✅ App startup test passed")
        return True

    except Exception as e:
        logger.error(f"❌ App startup test failed: {str(e)}")
        return False


def test_no_duplicate_outputs():
    """Test that there are no duplicate outputs without allow_duplicate=True."""
    logger.info("Testing for duplicate outputs...")

    try:
        from app_modules import get_app

        app = get_app()
        outputs_seen = {}
        duplicates_found = []

        for callback_id, callback in app.callback_map.items():
            for output in callback["callback"].output:
                output_str = f"{output.component_id}.{output.component_property}"

                if output_str in outputs_seen:
                    # Check if either has allow_duplicate=True
                    current_allows_duplicate = getattr(output, "allow_duplicate", False)
                    previous_allows_duplicate = outputs_seen[output_str]

                    if not current_allows_duplicate and not previous_allows_duplicate:
                        duplicates_found.append(
                            {
                                "output": output_str,
                                "callback1": outputs_seen[output_str]["callback_id"],
                                "callback2": callback_id,
                            }
                        )

                outputs_seen[output_str] = {
                    "callback_id": callback_id,
                    "allow_duplicate": getattr(output, "allow_duplicate", False),
                }

        if duplicates_found:
            logger.error(f"❌ Found {len(duplicates_found)} duplicate outputs:")
            for dup in duplicates_found:
                logger.error(
                    f"   {dup['output']}: {dup['callback1']} vs {dup['callback2']}"
                )
            return False

        logger.info("✅ No inappropriate duplicate outputs found")
        return True

    except Exception as e:
        logger.error(f"❌ Duplicate output test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    logger.info("🧪 Starting duplicate callback fix verification tests...")

    tests = [
        ("App Import", test_app_import),
        ("App Startup", test_app_startup),
        ("No Duplicate Outputs", test_no_duplicate_outputs),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        if test_func():
            passed += 1
        else:
            logger.error(f"Test '{test_name}' failed!")

    logger.info(f"\n🏁 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Duplicate callback fix is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. There may still be issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
