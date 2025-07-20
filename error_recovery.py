"""
Error Recovery and Graceful Degradation System

Provides comprehensive error recovery mechanisms, graceful degradation,
and user-friendly error handling throughout the application.

Features:
- Automatic retry with exponential backoff
- Graceful degradation for non-critical features
- User-friendly error messages and recovery suggestions
- Error logging and reporting
- Circuit breaker pattern for external dependencies
"""

import logging
import time
import traceback
import functools
from typing import Any, Callable, Optional, Dict, List, Tuple
from contextlib import contextmanager

from app_constants import UI_CONFIG, PERFORMANCE_CONFIG

logger = logging.getLogger(__name__)


class ErrorRecoveryError(Exception):
    """Custom exception for error recovery operations."""

    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for external dependencies.

    Prevents cascading failures by temporarily disabling failing operations
    and allowing them to recover.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise ErrorRecoveryError(
                    "Circuit breaker is OPEN - service unavailable"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker recovered - state: CLOSED")

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPEN - {self.failure_count} failures")


class RetryHandler:
    """
    Handles automatic retries with exponential backoff.
    """

    @staticmethod
    def retry_with_backoff(
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
    ):
        """
        Decorator for automatic retry with exponential backoff.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            backoff_factor: Multiplier for delay after each failure
            max_delay: Maximum delay between retries (seconds)
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None

                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e

                        if attempt == max_retries:
                            logger.error(
                                f"Function {func.__name__} failed after {max_retries} retries: {e}"
                            )
                            break

                        delay = min(base_delay * (backoff_factor**attempt), max_delay)
                        logger.warning(
                            f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}"
                        )
                        time.sleep(delay)

                raise last_exception

            return wrapper

        return decorator


class GracefulDegradation:
    """
    Manages graceful degradation of application features.
    """

    def __init__(self):
        self._disabled_features = set()
        self._fallback_handlers = {}

    def disable_feature(self, feature_name: str, reason: str = ""):
        """Disable a feature temporarily."""
        self._disabled_features.add(feature_name)
        logger.warning(f"Feature '{feature_name}' disabled: {reason}")

    def enable_feature(self, feature_name: str):
        """Re-enable a previously disabled feature."""
        if feature_name in self._disabled_features:
            self._disabled_features.remove(feature_name)
            logger.info(f"Feature '{feature_name}' re-enabled")

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is currently enabled."""
        return feature_name not in self._disabled_features

    def register_fallback(self, feature_name: str, fallback_handler: Callable):
        """Register a fallback handler for a feature."""
        self._fallback_handlers[feature_name] = fallback_handler

    def execute_with_fallback(
        self, feature_name: str, primary_func: Callable, *args, **kwargs
    ) -> Tuple[Any, bool]:
        """
        Execute a function with fallback support.

        Returns:
            Tuple[result, used_fallback]: Result and whether fallback was used
        """
        if not self.is_feature_enabled(feature_name):
            if feature_name in self._fallback_handlers:
                logger.info(f"Using fallback for disabled feature: {feature_name}")
                return self._fallback_handlers[feature_name](*args, **kwargs), True
            else:
                raise ErrorRecoveryError(
                    f"Feature '{feature_name}' is disabled and no fallback available"
                )

        try:
            result = primary_func(*args, **kwargs)
            return result, False
        except Exception as e:
            logger.error(f"Primary function failed for feature '{feature_name}': {e}")

            if feature_name in self._fallback_handlers:
                logger.info(f"Attempting fallback for feature: {feature_name}")
                try:
                    result = self._fallback_handlers[feature_name](*args, **kwargs)
                    return result, True
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback also failed for feature '{feature_name}': {fallback_error}"
                    )
                    raise e
            else:
                raise e


class ErrorHandler:
    """
    Comprehensive error handling and user message generation.
    """

    @staticmethod
    def create_user_friendly_message(
        error: Exception, context: str = ""
    ) -> Dict[str, Any]:
        """
        Create a user-friendly error message with recovery suggestions.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred

        Returns:
            Dict containing error details and user message
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # Common error patterns and user-friendly messages
        error_patterns = {
            "FileNotFoundError": {
                "title": "File Not Found",
                "message": "The requested file could not be found.",
                "suggestions": [
                    "Check that the file path is correct",
                    "Ensure the file hasn't been moved or deleted",
                    "Try uploading the file again",
                ],
                "severity": "error",
            },
            "PermissionError": {
                "title": "Permission Denied",
                "message": "Access to the file or resource was denied.",
                "suggestions": [
                    "Check file permissions",
                    "Try running with appropriate privileges",
                    "Contact your system administrator",
                ],
                "severity": "error",
            },
            "MemoryError": {
                "title": "Insufficient Memory",
                "message": "The operation requires more memory than available.",
                "suggestions": [
                    "Try processing smaller datasets",
                    "Close other applications to free memory",
                    "Consider processing data in batches",
                ],
                "severity": "error",
            },
            "ValueError": {
                "title": "Invalid Data",
                "message": "The data contains invalid or unexpected values.",
                "suggestions": [
                    "Check your data for missing or incorrect values",
                    "Verify the file format is correct",
                    "Try uploading a different file",
                ],
                "severity": "warning",
            },
            "ConnectionError": {
                "title": "Connection Failed",
                "message": "Could not establish a connection to the required service.",
                "suggestions": [
                    "Check your internet connection",
                    "Try again in a few moments",
                    "Contact support if the problem persists",
                ],
                "severity": "error",
            },
            "TimeoutError": {
                "title": "Operation Timed Out",
                "message": "The operation took longer than expected and was cancelled.",
                "suggestions": [
                    "Try again with a smaller dataset",
                    "Check your internet connection",
                    "The server may be busy - try again later",
                ],
                "severity": "warning",
            },
        }

        # Get error details or use generic message
        error_info = error_patterns.get(
            error_type,
            {
                "title": "Unexpected Error",
                "message": f"An unexpected error occurred: {error_msg}",
                "suggestions": [
                    "Try refreshing the page",
                    "Check your input data",
                    "Contact support if the problem persists",
                ],
                "severity": "error",
            },
        )

        return {
            "title": error_info["title"],
            "message": error_info["message"],
            "suggestions": error_info["suggestions"],
            "severity": error_info["severity"],
            "technical_details": {
                "error_type": error_type,
                "error_message": error_msg,
                "context": context,
                "traceback": traceback.format_exc(),
            },
        }

    @staticmethod
    def log_error(error: Exception, context: str = "", user_id: str = "anonymous"):
        """
        Log error details for debugging and monitoring.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            user_id: User identifier for tracking
        """
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user_id": user_id,
            "timestamp": time.time(),
            "traceback": traceback.format_exc(),
        }

        logger.error(f"Error in {context}: {error_details}")


class RecoveryManager:
    """
    Main recovery manager that coordinates all error recovery mechanisms.
    """

    def __init__(self):
        self.circuit_breakers = {}
        self.degradation = GracefulDegradation()
        self.error_counts = {}

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]

    @contextmanager
    def handle_operation(self, operation_name: str, context: str = ""):
        """
        Context manager for handling operations with comprehensive error recovery.

        Usage:
            with recovery_manager.handle_operation("file_upload", "AGS file processing"):
                # Your operation here
                process_file(file_data)
        """
        try:
            yield
        except Exception as e:
            # Log the error
            ErrorHandler.log_error(e, f"{operation_name} - {context}")

            # Track error frequency
            self.error_counts[operation_name] = (
                self.error_counts.get(operation_name, 0) + 1
            )

            # If too many errors, consider disabling feature
            if self.error_counts[operation_name] > 10:
                self.degradation.disable_feature(
                    operation_name,
                    f"Too many errors ({self.error_counts[operation_name]})",
                )

            # Re-raise with enhanced error info
            user_message = ErrorHandler.create_user_friendly_message(e, context)
            enhanced_error = ErrorRecoveryError(user_message["message"])
            enhanced_error.user_info = user_message
            raise enhanced_error

    def reset_error_counts(self):
        """Reset all error counts (for testing or maintenance)."""
        self.error_counts.clear()
        logger.info("Error counts reset")

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        return {
            "circuit_breakers": {
                name: {"state": cb.state, "failures": cb.failure_count}
                for name, cb in self.circuit_breakers.items()
            },
            "disabled_features": list(self.degradation._disabled_features),
            "error_counts": dict(self.error_counts),
            "total_errors": sum(self.error_counts.values()),
        }


# Global recovery manager instance
_recovery_manager = RecoveryManager()


def get_recovery_manager() -> RecoveryManager:
    """Get the global recovery manager instance."""
    return _recovery_manager


# Convenience decorators and functions
def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for adding retry capability to functions."""
    return RetryHandler.retry_with_backoff(max_retries, base_delay)


def with_circuit_breaker(service_name: str):
    """Decorator for adding circuit breaker protection to functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            circuit_breaker = get_recovery_manager().get_circuit_breaker(service_name)
            return circuit_breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


def handle_gracefully(feature_name: str, fallback_func: Optional[Callable] = None):
    """Decorator for graceful degradation support."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            recovery_manager = get_recovery_manager()
            if fallback_func:
                recovery_manager.degradation.register_fallback(
                    feature_name, fallback_func
                )

            result, used_fallback = recovery_manager.degradation.execute_with_fallback(
                feature_name, func, *args, **kwargs
            )
            return result

        return wrapper

    return decorator


if __name__ == "__main__":
    # Test error recovery components
    print("Error Recovery System Test")

    # Test circuit breaker
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=5)
    print(f"✓ Circuit breaker created: {cb.state}")

    # Test retry handler
    @with_retry(max_retries=2)
    def test_function():
        return "success"

    result = test_function()
    print(f"✓ Retry handler test: {result}")

    # Test error message generation
    try:
        raise ValueError("Test error")
    except Exception as e:
        message = ErrorHandler.create_user_friendly_message(e, "test context")
        print(f"✓ Error message generated: {message['title']}")

    # Test recovery manager
    manager = get_recovery_manager()
    health = manager.get_system_health()
    print(f"✓ System health check: {len(health)} metrics")

    print("✓ All error recovery components ready!")
