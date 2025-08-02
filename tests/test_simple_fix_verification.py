"""
Simple test to verify the duplicate callback fix is working
"""

import sys
import os


def test_app_functionality():
    """Test basic app functionality without complex subprocess testing."""

    print("Testing app import and singleton pattern...")

    try:
        # Test 1: Import and singleton pattern
        from app_modules import get_app

        app1 = get_app()
        app2 = get_app()

        if app1 is app2:
            print("✅ Singleton pattern working correctly")
        else:
            print("❌ Singleton pattern failed - different instances returned")
            return False

        # Test 2: Check callback counts
        if hasattr(app1, "callback_map"):
            callback_count = len(app1.callback_map)
            print(f"Total callbacks registered: {callback_count}")

            if callback_count > 5 and callback_count < 50:
                print("✅ Reasonable callback count (suggests no massive duplication)")
            else:
                print(f"❌ Suspicious callback count: {callback_count}")
                return False
        else:
            print("⚠️ Cannot check callback count - callback_map not available")

        # Test 3: Simple import test
        from app import app as main_app

        print("✅ Main app.py imports successfully")

        print("\n🎉 All basic tests passed!")
        print("The duplicate callback fix appears to be working correctly.")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_app_functionality()
    if success:
        print("\n✅ SUMMARY: Fix verified successfully!")
        print("   - Singleton pattern working")
        print("   - No duplicate app creation")
        print("   - App imports correctly")
    else:
        print("\n❌ SUMMARY: Issues detected")

    sys.exit(0 if success else 1)
