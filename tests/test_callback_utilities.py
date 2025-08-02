"""Test new callback module imports."""


def test_callback_utilities():
    """Test that new callback utilities import correctly."""
    print("🧪 Testing New Callback Utilities...")

    try:
        from callbacks.error_handling import CallbackError, create_error_message

        print("✅ Error handling utilities imported")
    except Exception as e:
        print(f"❌ Error handling import failed: {e}")

    try:
        from callbacks.file_validation import (
            validate_file_size,
            validate_total_upload_size,
        )

        print("✅ File validation utilities imported")
    except Exception as e:
        print(f"❌ File validation import failed: {e}")

    try:
        from callbacks.coordinate_utils import transform_coordinates, BLUE_MARKER

        print("✅ Coordinate utilities imported")
    except Exception as e:
        print(f"❌ Coordinate utilities import failed: {e}")

    try:
        from callbacks.file_upload_enhanced import EnhancedFileUploadCallback

        print("✅ Enhanced file upload callback imported")
    except Exception as e:
        print(f"❌ Enhanced file upload import failed: {e}")


if __name__ == "__main__":
    test_callback_utilities()
