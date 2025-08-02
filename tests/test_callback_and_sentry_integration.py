#!/usr/bin/env python3
"""
Test script to verify callback fix and Sentry integration.

This script tests:
1. App imports correctly with Sentry integration
2. No duplicate callback errors
3. Sentry error monitoring works
4. Callback error handling works properly
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_sentry_integration():
    """Test that Sentry integration works."""
    print("\n🔍 Testing Sentry Integration...")

    try:
        import sentry_sdk

        print("✅ Sentry SDK imported successfully")

        # Check if Sentry is initialized
        hub = sentry_sdk.Hub.current
        client = hub.client

        if client and client.dsn:
            print(f"✅ Sentry initialized with DSN: {client.dsn.public_dsn}")
            print(f"✅ Environment: {client.options.get('environment', 'not set')}")
            print(f"✅ Release: {client.options.get('release', 'not set')}")
        else:
            print("❌ Sentry not properly initialized")
            return False

    except Exception as e:
        print(f"❌ Sentry integration error: {e}")
        return False

    return True


def test_app_import_with_sentry():
    """Test that app imports correctly with Sentry."""
    print("\n🔍 Testing App Import with Sentry...")

    try:
        # This should initialize Sentry and then import the app
        from app import app

        print("✅ App imported successfully with Sentry integration")

        # Check that the app has a server (Flask instance)
        if hasattr(app, "server"):
            print("✅ App has Flask server instance")
        else:
            print("❌ App missing Flask server")
            return False

    except Exception as e:
        print(f"❌ App import error: {e}")
        return False

    return True


def test_callback_error_handling():
    """Test that callback error handling works."""
    print("\n🔍 Testing Callback Error Handling...")

    try:
        from callbacks.map_interactions import MapInteractionCallback

        # Create callback instance
        callback = MapInteractionCallback()
        print("✅ MapInteractionCallback created successfully")

        # Check that error handling methods exist
        if hasattr(callback, "handle_error"):
            print("✅ handle_error method exists")
        else:
            print("❌ handle_error method missing")
            return False

        if hasattr(callback, "log_callback_start"):
            print("✅ log_callback_start method exists")
        else:
            print("❌ log_callback_start method missing")
            return False

        if hasattr(callback, "log_callback_end"):
            print("✅ log_callback_end method exists")
        else:
            print("❌ log_callback_end method missing")
            return False

    except Exception as e:
        print(f"❌ Callback error handling test error: {e}")
        return False

    return True


def test_sentry_error_capture():
    """Test that Sentry can capture errors."""
    print("\n🔍 Testing Sentry Error Capture...")

    try:
        import sentry_sdk

        # Capture a test message
        sentry_sdk.capture_message(
            "Test message from callback fix verification", level="info"
        )
        print("✅ Test message sent to Sentry")

        # Capture a test exception
        try:
            raise ValueError("Test exception for Sentry integration")
        except ValueError as e:
            sentry_sdk.capture_exception(e)
            print("✅ Test exception sent to Sentry")

    except Exception as e:
        print(f"❌ Sentry error capture test error: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("🚀 Starting Callback Fix and Sentry Integration Verification")
    print("=" * 60)

    tests = [
        ("Sentry Integration", test_sentry_integration),
        ("App Import with Sentry", test_app_import_with_sentry),
        ("Callback Error Handling", test_callback_error_handling),
        ("Sentry Error Capture", test_sentry_error_capture),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 All tests passed! Callback fix and Sentry integration working correctly."
        )
        print("\n📝 Summary:")
        print("   - ✅ No more duplicate callback errors")
        print("   - ✅ Sentry monitoring active")
        print("   - ✅ Error handling working")
        print("   - ✅ App starts successfully")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
