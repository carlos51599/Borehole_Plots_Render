"""
File validation utilities for callback operations.

This module provides comprehensive file validation, security checks,
and file processing utilities for the application callbacks.
"""

import base64
import logging
from typing import Tuple, List, Optional
from app_constants import FILE_LIMITS

logger = logging.getLogger(__name__)

# File upload security configuration
MAX_FILE_SIZE_MB = FILE_LIMITS.MAX_FILE_SIZE_MB
MAX_TOTAL_FILES_SIZE_MB = FILE_LIMITS.MAX_TOTAL_FILES_MB
MAX_FILES_COUNT = 10  # Maximum number of files that can be uploaded at once


def validate_file_size(
    content_string: str, filename: str
) -> Tuple[bool, Optional[str], float]:
    """
    Validate file size to prevent DoS attacks.

    Args:
        content_string: Base64 encoded file content
        filename: Name of the file being uploaded

    Returns:
        tuple: (is_valid, error_message, size_mb)
    """
    try:
        # Calculate size from base64 content
        # Base64 adds ~33% overhead, so actual size = len * 3/4
        estimated_size_bytes = len(content_string) * 3 / 4
        size_mb = estimated_size_bytes / (1024 * 1024)

        if size_mb > MAX_FILE_SIZE_MB:
            error_msg = (
                f"File '{filename}' is too large ({size_mb:.1f}MB). "
                f"Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
            )
            logger.warning(f"File size validation failed: {error_msg}")
            return False, error_msg, size_mb

        logger.debug(f"File size validation passed: {filename} ({size_mb:.2f}MB)")
        return True, None, size_mb

    except Exception as e:
        error_msg = f"Error validating file size for '{filename}': {str(e)}"
        logger.error(error_msg)
        return False, error_msg, 0.0


def validate_total_upload_size(
    files_data: List[Tuple[str, str, str]],
) -> Tuple[bool, Optional[str], float]:
    """
    Validate total upload size and file count.

    Args:
        files_data: List of tuples containing (content_type, content_string, filename)

    Returns:
        tuple: (is_valid, error_message, total_size_mb)
    """
    if len(files_data) > MAX_FILES_COUNT:
        error_msg = (
            f"Too many files uploaded ({len(files_data)}). "
            f"Maximum allowed is {MAX_FILES_COUNT} files."
        )
        logger.warning(f"File count validation failed: {error_msg}")
        return False, error_msg, 0.0

    total_size = 0
    for _, content_string, filename in files_data:
        is_valid, error_msg, size_mb = validate_file_size(content_string, filename)
        if not is_valid:
            return False, error_msg, 0.0

        total_size += len(content_string) * 3 / 4  # Convert from base64

    total_size_mb = total_size / (1024 * 1024)

    if total_size_mb > MAX_TOTAL_FILES_SIZE_MB:
        error_msg = (
            f"Total upload size too large ({total_size_mb:.1f}MB). "
            f"Maximum allowed is {MAX_TOTAL_FILES_SIZE_MB}MB."
        )
        logger.warning(f"Total size validation failed: {error_msg}")
        return False, error_msg, total_size_mb

    logger.info(
        f"Upload validation passed: {len(files_data)} files, {total_size_mb:.2f}MB total"
    )
    return True, None, total_size_mb


def validate_file_content(
    content_string: str, filename: str
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate and decode file content.

    Args:
        content_string: Base64 encoded file content
        filename: Name of the file

    Returns:
        tuple: (is_valid, error_message, decoded_content)
    """
    try:
        # Decode base64 content
        decoded_bytes = base64.b64decode(content_string)
        decoded_content = decoded_bytes.decode("utf-8")

        # Basic content validation
        if not decoded_content.strip():
            error_msg = f"File '{filename}' appears to be empty."
            logger.warning(error_msg)
            return False, error_msg, None

        # Check for minimum AGS content indicators
        if filename.lower().endswith(".ags"):
            if (
                '"GROUP"' not in decoded_content.upper()
                and '"HEADING"' not in decoded_content.upper()
            ):
                error_msg = f"File '{filename}' does not appear to be a valid AGS file."
                logger.warning(error_msg)
                return False, error_msg, None

        logger.debug(f"Content validation passed for {filename}")
        return True, None, decoded_content

    except UnicodeDecodeError as e:
        error_msg = f"File '{filename}' contains invalid characters: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None
    except Exception as e:
        error_msg = f"Error validating content of '{filename}': {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing or replacing dangerous characters.

    Args:
        filename: Original filename

    Returns:
        str: Safe filename
    """
    if not filename:
        return "unknown_file"

    # Remove path separators and other dangerous characters
    dangerous_chars = ["/", "\\", "..", "<", ">", ":", '"', "|", "?", "*"]
    safe_name = filename

    for char in dangerous_chars:
        safe_name = safe_name.replace(char, "_")

    # Ensure it's not empty after cleaning
    if not safe_name.strip():
        safe_name = "cleaned_file"

    return safe_name
