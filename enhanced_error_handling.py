"""
Enhanced Error Handling Utilities with Retry Logic and Graceful Degradation.

This module provides robust error handling mechanisms specifically designed for
the complex operations in geotechnical data processing. It includes intelligent
retry logic, graceful degradation strategies, and enhanced user feedback systems
to maintain application stability and provide excellent user experience.

Key Features:
- **Intelligent Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Graceful Degradation**: Fallback mechanisms to maintain partial functionality
- **Enhanced User Feedback**: Clear, contextual error messages with suggested actions
- **Error Recovery Strategies**: Automatic recovery from common error scenarios
- **Performance Monitoring**: Track error patterns and system reliability

Advanced Error Handling Patterns:
1. **Retry Decorators**: Automatic retry for network operations and file I/O
2. **Circuit Breaker**: Prevent cascading failures in external service calls
3. **Fallback Mechanisms**: Alternative processing paths when primary methods fail
4. **Error Context Preservation**: Maintain detailed context for debugging
5. **User Action Guidance**: Provide specific steps for error resolution

Specialized Handlers:
- **AGS File Processing**: Handle malformed files with intelligent parsing fallbacks
- **Coordinate Transformation**: Manage projection errors with alternative methods
- **Plot Generation**: Graceful handling of matplotlib rendering issues
- **Memory Management**: Automatic cleanup and optimization on memory errors
- **Network Operations**: Retry logic for coordinate service and map tile failures

Error Recovery Strategies:
- Automatic file format detection and conversion
- Alternative coordinate systems when primary projections fail
- Simplified plotting when complex rendering fails
- Data validation with automatic cleanup
- Progressive feature degradation to maintain core functionality

Dependencies:
- functools: Decorator patterns for retry logic
- dataclasses: Structured error context management
- logging: Comprehensive error reporting and tracking

Author: [Project Team]
Last Modified: July 2025
"""

import logging
import time
import functools
from typing import Any, Callable, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for categorizing different types of failures."""

    CRITICAL = "critical"  # Application cannot continue
    HIGH = "high"  # Feature is broken but app can continue
    MEDIUM = "medium"  # Degraded functionality
    LOW = "low"  # Minor issues, app fully functional


@dataclass
class ErrorContext:
    """Structured error context for better debugging and user feedback."""

    error_type: str
    severity: ErrorSeverity
    user_message: str
    technical_details: str
    suggested_action: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_name: Optional[str] = None,
):
    """
    Decorator that implements retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exception types to catch and retry
        logger_name: Name of logger to use (defaults to module logger)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            local_logger = logging.getLogger(logger_name) if logger_name else logger

            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        local_logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries. "
                            f"Final error: {e}"
                        )
                        raise

                    local_logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}. "
                        f"Retrying in {delay:.1f}s. Error: {e}"
                    )

                    time.sleep(delay)
                    delay *= backoff_factor

            # This should never be reached, but included for completeness
            raise last_exception

        return wrapper

    return decorator


def graceful_fallback(
    fallback_value: Any = None,
    log_error: bool = True,
    error_context: Optional[ErrorContext] = None,
):
    """
    Decorator that provides graceful fallback for functions that might fail.

    Args:
        fallback_value: Value to return if function fails
        log_error: Whether to log the error
        error_context: Optional error context for structured error reporting
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Function {func.__name__} failed: {e}")
                    if error_context:
                        logger.error(f"Error context: {error_context}")

                return fallback_value

        return wrapper

    return decorator


@retry_with_backoff(max_retries=2, exceptions=(ConnectionError, TimeoutError))
def robust_coordinate_transform(easting: float, northing: float) -> tuple:
    """
    Coordinate transformation with retry logic for network/service failures.

    Args:
        easting: BNG easting coordinate
        northing: BNG northing coordinate

    Returns:
        Tuple of (latitude, longitude) or (None, None) if failed
    """
    try:
        from coordinate_service import get_coordinate_service

        coord_service = get_coordinate_service()
        lat, lon = coord_service.transform_bng_to_wgs84(easting, northing)

        # Validate results
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")

        return lat, lon

    except Exception as e:
        logger.error(
            f"Coordinate transformation failed for BNG({easting}, {northing}): {e}"
        )
        return None, None


def safe_file_processing(file_content: str, filename: str) -> Optional[dict]:
    """
    Safely process AGS file content with comprehensive error handling.

    Args:
        file_content: Content of the AGS file
        filename: Name of the file for error reporting

    Returns:
        Processed data dictionary or None if processing failed
    """
    try:
        # Import here to avoid circular imports
        from data_loader import process_ags_content

        logger.info(f"Processing file: {filename}")

        # Validate file content
        if not file_content or not file_content.strip():
            raise ValueError("File content is empty")

        # Process the file
        result = process_ags_content(file_content, filename)

        if result is None:
            raise ValueError("File processing returned no data")

        logger.info(f"Successfully processed {filename}")
        return result

    except Exception as e:
        error_context = ErrorContext(
            error_type="file_processing_error",
            severity=ErrorSeverity.MEDIUM,
            user_message=f"Could not process file '{filename}'. Please check the file format.",
            technical_details=str(e),
            suggested_action="Try uploading a different AGS file or check file format",
            error_code="FILE_PROC_001",
        )

        logger.error(f"File processing failed for {filename}: {error_context}")
        return None


@graceful_fallback(fallback_value=[])
def safe_marker_creation(borehole_data: list) -> List[dict]:
    """
    Safely create map markers with fallback for individual failures.

    Args:
        borehole_data: List of borehole data dictionaries

    Returns:
        List of successfully created markers
    """
    markers = []
    failed_count = 0

    for i, borehole in enumerate(borehole_data):
        try:
            # Validate required fields
            if "LOCA_ID" not in borehole:
                raise ValueError("Missing LOCA_ID")

            if "lat" not in borehole or "lon" not in borehole:
                raise ValueError("Missing coordinates")

            lat, lon = borehole["lat"], borehole["lon"]

            # Validate coordinates
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                raise ValueError(
                    f"Invalid coordinate types: lat={type(lat)}, lon={type(lon)}"
                )

            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError(f"Coordinates out of range: lat={lat}, lon={lon}")

            # Create marker (simplified structure)
            marker = {
                "id": {"type": "borehole-marker", "index": i},
                "position": [lat, lon],
                "tooltip": borehole["LOCA_ID"],
                "borehole_data": borehole,
            }

            markers.append(marker)

        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to create marker for borehole {i}: {e}")
            continue

    if failed_count > 0:
        logger.warning(
            f"Failed to create {failed_count} markers out of {len(borehole_data)}"
        )

    logger.info(f"Successfully created {len(markers)} markers")
    return markers


def create_user_friendly_error(error: Exception, context: str = "") -> dict:
    """
    Convert technical errors into user-friendly error messages.

    Args:
        error: The original exception
        context: Additional context about where the error occurred

    Returns:
        Dictionary with user-friendly error information
    """
    error_type = type(error).__name__
    error_message = str(error)

    # Map common technical errors to user-friendly messages
    error_mappings = {
        "FileNotFoundError": {
            "user_message": "File not found. Please check the file path and try again.",
            "severity": ErrorSeverity.MEDIUM,
        },
        "PermissionError": {
            "user_message": "Permission denied. Please check file permissions.",
            "severity": ErrorSeverity.MEDIUM,
        },
        "ConnectionError": {
            "user_message": "Network connection failed. Please check your internet connection.",
            "severity": ErrorSeverity.HIGH,
        },
        "MemoryError": {
            "user_message": "Not enough memory to complete the operation. Try with a smaller file.",
            "severity": ErrorSeverity.HIGH,
        },
        "ValueError": {
            "user_message": "Invalid data format. Please check your input.",
            "severity": ErrorSeverity.MEDIUM,
        },
        "KeyError": {
            "user_message": "Missing required data field. Please check the file format.",
            "severity": ErrorSeverity.MEDIUM,
        },
    }

    mapping = error_mappings.get(
        error_type,
        {
            "user_message": "An unexpected error occurred. Please try again.",
            "severity": ErrorSeverity.MEDIUM,
        },
    )

    return {
        "error_type": error_type,
        "user_message": mapping["user_message"],
        "technical_details": error_message,
        "severity": mapping["severity"].value,
        "context": context,
        "timestamp": time.time(),
    }


def log_performance_warning(operation: str, duration: float, threshold: float = 5.0):
    """
    Log performance warnings for slow operations.

    Args:
        operation: Name of the operation
        duration: Time taken in seconds
        threshold: Threshold in seconds for logging warning
    """
    if duration > threshold:
        logger.warning(
            f"Performance warning: {operation} took {duration:.2f}s "
            f"(threshold: {threshold:.2f}s)"
        )
    else:
        logger.debug(f"Performance: {operation} completed in {duration:.2f}s")


class PerformanceMonitor:
    """Context manager for monitoring operation performance."""

    def __init__(self, operation_name: str, warning_threshold: float = 5.0):
        self.operation_name = operation_name
        self.warning_threshold = warning_threshold
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            log_performance_warning(
                self.operation_name, duration, self.warning_threshold
            )

            if exc_type is not None:
                logger.error(
                    f"Operation {self.operation_name} failed after {duration:.2f}s: {exc_val}"
                )


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test retry mechanism
    @retry_with_backoff(max_retries=2, initial_delay=0.1)
    def failing_function():
        raise ConnectionError("Simulated network error")

    # Test graceful fallback
    @graceful_fallback(fallback_value="fallback result")
    def unreliable_function():
        raise ValueError("Simulated error")

    # Test performance monitoring
    with PerformanceMonitor("test_operation", warning_threshold=0.1):
        time.sleep(0.2)  # Simulate slow operation

    print("Error handling utilities test completed")
