"""
Enhanced Error Handling System for Robust Application Reliability.

This module provides a comprehensive, standardized error handling system designed
to replace inconsistent error handling patterns and provide professional-grade
error management throughout the Geo Borehole Sections Render application.

Key Features:
- **Standardized Error Classification**: Consistent error severity and category system
- **User-Friendly Error Messages**: Technical errors translated to user-understandable messages
- **Comprehensive Error Logging**: Detailed technical information for debugging
- **Error Recovery Strategies**: Automatic fallback mechanisms where possible
- **Error Context Preservation**: Maintain context information for better debugging

Error Classification System:
1. **Severity Levels**: INFO, WARNING, ERROR, CRITICAL
2. **Error Categories**: DATA_PROCESSING, FILE_UPLOAD, COORDINATE_TRANSFORM,
   PLOT_GENERATION, MAP_INTERACTION, SYSTEM_ERROR
3. **Error Context**: Module, function, user action, data involved

User Experience Benefits:
- Clear, actionable error messages for users
- Consistent error presentation across the application
- Prevents application crashes with graceful error handling
- Provides helpful suggestions for error resolution

Technical Benefits:
- Centralized error handling reduces code duplication
- Standardized logging format aids in debugging
- Error categorization helps identify common failure patterns
- Recovery mechanisms maintain application stability

Integration Points:
- File upload validation and processing
- AGS data parsing and validation
- Coordinate transformation operations
- Plot generation and rendering
- Map interaction and selection operations

Dependencies:
- logging: Professional error logging and reporting
- dash: UI error message display components
- dataclasses: Structured error information management

Author: [Project Team]
Last Modified: July 2025
"""

import logging
import traceback
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import dash
from dash import html

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization."""

    FILE_UPLOAD = "file_upload"
    DATA_PROCESSING = "data_processing"
    COORDINATE_TRANSFORM = "coordinate_transform"
    PLOT_GENERATION = "plot_generation"
    MAP_INTERACTION = "map_interaction"
    SEARCH = "search"
    SELECTION = "selection"
    VALIDATION = "validation"
    SYSTEM = "system"


@dataclass
class ApplicationError:
    """Standardized error representation."""

    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    details: Optional[str] = None
    timestamp: datetime = None
    error_code: Optional[str] = None
    user_message: Optional[str] = None
    recovery_suggestions: List[str] = None
    technical_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []
        if self.technical_details is None:
            self.technical_details = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "error_code": self.error_code,
            "user_message": self.user_message,
            "recovery_suggestions": self.recovery_suggestions,
            "technical_details": self.technical_details,
        }

    def get_user_friendly_message(self) -> str:
        """Get a user-friendly error message."""
        if self.user_message:
            return self.user_message

        # Generate user-friendly message based on category
        category_messages = {
            ErrorCategory.FILE_UPLOAD: "There was an issue uploading your files.",
            ErrorCategory.DATA_PROCESSING: "There was an issue processing your data.",
            ErrorCategory.COORDINATE_TRANSFORM: "There was an issue with coordinate calculations.",
            ErrorCategory.PLOT_GENERATION: "There was an issue generating the plot.",
            ErrorCategory.MAP_INTERACTION: "There was an issue with the map interaction.",
            ErrorCategory.SEARCH: "There was an issue with the search function.",
            ErrorCategory.SELECTION: "There was an issue with the selection.",
            ErrorCategory.VALIDATION: "There was a validation error.",
            ErrorCategory.SYSTEM: "There was a system error.",
        }

        base_message = category_messages.get(
            self.category, "An unexpected error occurred."
        )

        if self.details and self.severity != ErrorSeverity.CRITICAL:
            return f"{base_message} {self.details}"

        return base_message


class ErrorHandler:
    """Centralized error handling service."""

    def __init__(self):
        self._error_history: List[ApplicationError] = []
        self._max_history = 100

    def create_error(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[str] = None,
        error_code: Optional[str] = None,
        user_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
        exception: Optional[Exception] = None,
    ) -> ApplicationError:
        """Create a standardized application error."""

        technical_details = {}

        # Include exception details if provided
        if exception:
            technical_details.update(
                {
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "traceback": traceback.format_exc(),
                }
            )

        error = ApplicationError(
            message=message,
            category=category,
            severity=severity,
            details=details,
            error_code=error_code,
            user_message=user_message,
            recovery_suggestions=recovery_suggestions or [],
            technical_details=technical_details,
        )

        # Log the error
        self._log_error(error)

        # Add to history
        self._add_to_history(error)

        return error

    def handle_callback_error(
        self,
        exception: Exception,
        callback_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        state: Optional[Dict[str, Any]] = None,
    ) -> ApplicationError:
        """Handle errors that occur in Dash callbacks."""

        # Determine category from callback name
        category = self._categorize_callback_error(callback_name)

        # Create technical details
        technical_details = {
            "callback_name": callback_name,
            "inputs": inputs,
            "state": state,
        }

        # Determine severity
        severity = ErrorSeverity.ERROR
        if "critical" in str(exception).lower() or "memory" in str(exception).lower():
            severity = ErrorSeverity.CRITICAL
        elif "warning" in str(exception).lower():
            severity = ErrorSeverity.WARNING

        error = self.create_error(
            message=f"Error in callback '{callback_name}': {str(exception)}",
            category=category,
            severity=severity,
            details=str(exception),
            exception=exception,
        )

        return error

    def get_dash_error_response(
        self,
        error: ApplicationError,
        output_count: int = 1,
    ) -> Union[dash.no_update, html.Div, List]:
        """
        Generate appropriate Dash callback response for an error.

        Args:
            error: The application error
            output_count: Number of outputs the callback expects

        Returns:
            Appropriate Dash response (no_update, error div, or list)
        """

        if error.severity == ErrorSeverity.INFO:
            # For info level, don't update
            if output_count == 1:
                return dash.no_update
            return [dash.no_update] * output_count

        # Create error message component
        error_component = self._create_error_component(error)

        if output_count == 1:
            return error_component

        # For multiple outputs, return error for first output and no_update for rest
        response = [error_component]
        response.extend([dash.no_update] * (output_count - 1))
        return response

    def get_error_history(
        self,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        limit: int = 10,
    ) -> List[ApplicationError]:
        """Get recent error history with optional filtering."""

        errors = self._error_history.copy()

        # Apply filters
        if category:
            errors = [e for e in errors if e.category == category]

        if severity:
            errors = [e for e in errors if e.severity == severity]

        # Sort by timestamp (most recent first) and limit
        errors.sort(key=lambda x: x.timestamp, reverse=True)
        return errors[:limit]

    def clear_error_history(self):
        """Clear error history."""
        self._error_history.clear()
        logger.info("Cleared error history")

    def _log_error(self, error: ApplicationError):
        """Log error using appropriate logging level."""

        log_message = f"[{error.category.value}] {error.message}"
        if error.details:
            log_message += f" - {error.details}"

        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra={"error_data": error.to_dict()})
        elif error.severity == ErrorSeverity.ERROR:
            logger.error(log_message, extra={"error_data": error.to_dict()})
        elif error.severity == ErrorSeverity.WARNING:
            logger.warning(log_message, extra={"error_data": error.to_dict()})
        else:
            logger.info(log_message, extra={"error_data": error.to_dict()})

    def _add_to_history(self, error: ApplicationError):
        """Add error to history with size management."""
        self._error_history.append(error)

        # Trim history if too large
        if len(self._error_history) > self._max_history:
            self._error_history = self._error_history[-self._max_history :]

    def _categorize_callback_error(self, callback_name: str) -> ErrorCategory:
        """Determine error category from callback name."""

        callback_name_lower = callback_name.lower()

        if "upload" in callback_name_lower or "file" in callback_name_lower:
            return ErrorCategory.FILE_UPLOAD
        elif "plot" in callback_name_lower or "generate" in callback_name_lower:
            return ErrorCategory.PLOT_GENERATION
        elif "map" in callback_name_lower or "marker" in callback_name_lower:
            return ErrorCategory.MAP_INTERACTION
        elif "search" in callback_name_lower:
            return ErrorCategory.SEARCH
        elif "select" in callback_name_lower or "checkbox" in callback_name_lower:
            return ErrorCategory.SELECTION
        elif "coordinate" in callback_name_lower or "transform" in callback_name_lower:
            return ErrorCategory.COORDINATE_TRANSFORM
        else:
            return ErrorCategory.SYSTEM

    def _create_error_component(self, error: ApplicationError) -> html.Div:
        """Create Dash HTML component for displaying error."""

        # Choose icon and color based on severity
        severity_config = {
            ErrorSeverity.INFO: {"icon": "ℹ️", "color": "#17a2b8"},
            ErrorSeverity.WARNING: {"icon": "⚠️", "color": "#ffc107"},
            ErrorSeverity.ERROR: {"icon": "❌", "color": "#dc3545"},
            ErrorSeverity.CRITICAL: {"icon": "🚨", "color": "#721c24"},
        }

        config = severity_config[error.severity]

        # Create children elements
        children = [
            html.Span(
                f"{config['icon']} ", style={"fontSize": "16px", "marginRight": "8px"}
            ),
            html.Span(error.get_user_friendly_message(), style={"fontWeight": "bold"}),
        ]

        # Add recovery suggestions if available
        if error.recovery_suggestions:
            children.append(html.Br())
            children.append(
                html.Small(
                    "Suggestions: " + "; ".join(error.recovery_suggestions),
                    style={"fontStyle": "italic", "marginTop": "4px"},
                )
            )

        return html.Div(
            children,
            style={
                "color": config["color"],
                "backgroundColor": f"{config['color']}15",
                "border": f"1px solid {config['color']}",
                "borderRadius": "4px",
                "padding": "12px",
                "margin": "8px 0",
                "fontSize": "14px",
            },
        )


# Global error handler instance
_error_handler_instance: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler_instance

    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
        logger.info("Created global error handler instance")

    return _error_handler_instance


def handle_callback_errors(callback_name: str):
    """
    Decorator for handling errors in Dash callbacks.

    Usage:
        @handle_callback_errors("my_callback")
        def my_callback_function(...):
            # callback logic here
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_error_handler()
                error = error_handler.handle_callback_error(
                    exception=e,
                    callback_name=callback_name,
                    inputs={"args": args, "kwargs": kwargs},
                )

                # Return appropriate error response
                # This is a simple implementation - may need adjustment based on callback
                return error_handler.get_dash_error_response(error)

        return wrapper

    return decorator
