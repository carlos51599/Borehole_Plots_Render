"""
File Upload Package

This package contains modular file upload functionality split from the original
monolithic file_upload.py for better organization and maintainability.

Structure:
- validation.py: File size, type, and content validation
- processing.py: Data processing and coordinate transformation
- ui_components.py: UI status messages and display components
- main.py: Main callback registration and coordination

Usage:
    from callbacks.file_upload import FileUploadCallback
    # or
    from callbacks.file_upload.main import register_file_upload_callbacks
"""

from .main import FileUploadCallback, register_file_upload_callbacks

__all__ = ["FileUploadCallback", "register_file_upload_callbacks"]
