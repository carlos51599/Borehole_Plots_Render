"""
File Validation Module

This module handles all file validation logic extracted from the main file upload callback.
Focuses on size validation, file type checking, and security validation.
"""

from typing import List, Tuple

# Import file limits configuration
try:
    from .file_validation import FILE_LIMITS
except ImportError:
    # Fallback configuration
    class FILE_LIMITS:
        MAX_FILES = 10
        MAX_FILE_SIZE_MB = 50
        MAX_TOTAL_SIZE_MB = 200


def validate_total_upload_size(
    files: List[Tuple[str, str, str]],
) -> Tuple[bool, str, float]:
    """
    Validate total upload size across all files.

    Args:
        files: List of (content_type, content_string, name) tuples

    Returns:
        Tuple of (is_valid, error_message, total_size_mb)
    """
    total_size = 0.0

    for content_type, content_string, name in files:
        # Calculate size in MB (accounting for Base64 overhead)
        size_bytes = len(content_string) * 3 / 4
        size_mb = size_bytes / (1024 * 1024)
        total_size += size_mb

    # Check file count limit
    if len(files) > FILE_LIMITS.MAX_FILES:
        return False, f"Too many files (max {FILE_LIMITS.MAX_FILES})", total_size

    # Check total size limit
    if total_size > FILE_LIMITS.MAX_TOTAL_SIZE_MB:
        return (
            False,
            f"Total size too large (max {FILE_LIMITS.MAX_TOTAL_SIZE_MB}MB)",
            total_size,
        )

    return True, "", total_size


def validate_individual_file_size(
    content_string: str, name: str
) -> Tuple[bool, str, float]:
    """
    Validate individual file size.

    Args:
        content_string: Base64 encoded file content
        name: File name for error messages

    Returns:
        Tuple of (is_valid, error_message, size_mb)
    """
    # Calculate size in MB (accounting for Base64 overhead)
    size_bytes = len(content_string) * 3 / 4
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > FILE_LIMITS.MAX_FILE_SIZE_MB:
        return (
            False,
            f"File {name} too large (max {FILE_LIMITS.MAX_FILE_SIZE_MB}MB)",
            size_mb,
        )

    return True, "", size_mb


def validate_file_type(name: str) -> Tuple[bool, str]:
    """
    Validate file type based on extension.

    Args:
        name: File name

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Invalid file name"

    # AGS files are typically text files with .ags or .txt extension
    valid_extensions = [".ags", ".txt"]
    name_lower = name.lower()

    if not any(name_lower.endswith(ext) for ext in valid_extensions):
        return (
            False,
            f"Unsupported file type. Expected: {', '.join(valid_extensions)}",
        )

    return True, ""


def validate_file_content_security(content_string: str, name: str) -> Tuple[bool, str]:
    """
    Basic security validation of file content.

    Args:
        content_string: Base64 encoded file content
        name: File name for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        import base64

        # Attempt to decode Base64 content
        decoded = base64.b64decode(content_string)
        text_content = decoded.decode("utf-8", errors="ignore")

        # Basic content validation for AGS files
        if len(text_content.strip()) == 0:
            return False, f"File {name} appears to be empty"

        # Check for potential AGS content indicators
        ags_indicators = ["**PROJ", "**LOCA", "**GEOL", "GROUP", "DATA"]
        has_ags_content = any(indicator in text_content for indicator in ags_indicators)

        if not has_ags_content:
            return (False, f"File {name} does not appear to contain valid AGS data")

        return True, ""

    except Exception as e:
        return False, f"File {name} content validation failed: {str(e)}"
