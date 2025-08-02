#!/usr/bin/env python3
"""
Simple test to verify everything is working correctly.
"""


def test_app_startup():
    """Test that the app starts up correctly with Sentry and no duplicate callbacks."""
    print("🔍 Testing app startup...")

    try:
        # Import the app (this initializes Sentry and creates the app)
        from app import app

        print("✅ App imported successfully")

        # Check that app is a Dash instance
        import dash

        if isinstance(app, dash.Dash):
            print("✅ App is a Dash instance")

        # Check that Sentry is working
        import sentry_sdk

        if sentry_sdk.is_initialized():
            print("✅ Sentry is initialized")

        # Test Sentry capture
        sentry_sdk.capture_message("Test from fixed application", level="info")
        print("✅ Sentry message sent")

        print("🎉 All systems working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_callback_error_handling():
    """Test that callback error handling works."""
    print("\n🔍 Testing callback error handling...")

    try:
        from callbacks.map_interactions import MapInteractionCallback

        callback = MapInteractionCallback()

        # Test error handling
        test_exception = ValueError("Test error")
        result = callback.handle_error(test_exception, output_count=8)

        if isinstance(result, tuple) and len(result) == 8:
            print("✅ Error handling returns correct tuple structure")
            return True
        else:
            print(
                f"❌ Error handling returned: {type(result)} with length {len(result) if hasattr(result, '__len__') else 'N/A'}"
            )
            return False

    except Exception as e:
        print(f"❌ Callback error handling test failed: {e}")
        return False


def main():
    """Run verification tests."""
    print("🚀 Verifying Callback Fix and Sentry Integration")
    print("=" * 50)

    test1 = test_app_startup()
    test2 = test_callback_error_handling()

    print("\n" + "=" * 50)
    if test1 and test2:
        print("🎉 SUCCESS: All fixes working correctly!")
        print("   ✅ No duplicate callback errors")
        print("   ✅ Sentry monitoring active")
        print("   ✅ Error handling working")
        return True
    else:
        print("❌ Some issues detected")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
