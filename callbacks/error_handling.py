"""
Error handling utilities for callbacks.

This module provides standardized error handling, logging, and user feedback
for all callback functions in the application.
"""

import logging
from dash import html
from typing import Any, Optional


class CallbackError(Exception):
    """
    Custom exception for callback errors with user-friendly messages.

    This exception class enables better error handling by separating technical
    error details (for logging) from user-friendly messages (for display).
    It also supports different error types for appropriate styling.

    Attributes:
        user_message (str): User-friendly error message for display
        technical_message (str): Technical error details for logging
        error_type (str): Type of error - 'error', 'warning', or 'info'

    Example:
        >>> raise CallbackError(
        ...     user_message="Unable to process AGS file. Please check file format.",
        ...     technical_message="AGS parser failed: missing LOCA group header",
        ...     error_type="error"
        ... )
    """

    def __init__(
        self,
        user_message: str,
        technical_message: Optional[str] = None,
        error_type: str = "error",
    ):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        self.error_type = error_type  # 'error', 'warning', 'info'
        super().__init__(self.technical_message)


def create_error_message(error: Exception, context: str = "Operation") -> html.Div:
    """
    Create a standardized error message component for display to users.

    This function takes any error (Exception or CallbackError) and creates
    a styled HTML component for consistent error presentation throughout
    the application.

    Args:
        error (Exception or CallbackError): The error to display
        context (str): Context description where the error occurred
                      (default: "Operation")

    Returns:
        html.Div: Styled Dash HTML component containing the error message

    Error Types and Styling:
        - error: Red border, light red background (for critical errors)
        - warning: Orange border, light orange background (for warnings)
        - info: Blue border, light blue background (for informational messages)

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     return create_error_message(e, "File upload")
    """
    if isinstance(error, CallbackError):
        user_msg = error.user_message
        tech_msg = error.technical_message
        error_type = error.error_type
    else:
        user_msg = f"{context} failed. Please try again."
        tech_msg = str(error)
        error_type = "error"

    # Choose colors based on error type
    colors = {
        "error": {"border": "red", "bg": "#ffebee", "text": "darkred"},
        "warning": {"border": "orange", "bg": "#fff3e0", "text": "darkorange"},
        "info": {"border": "blue", "bg": "#e3f2fd", "text": "darkblue"},
    }

    color_scheme = colors.get(error_type, colors["error"])

    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        f"❌ {user_msg}" if error_type == "error" else f"⚠️ {user_msg}",
                        style={
                            "margin": "0",
                            "fontWeight": "bold",
                            "color": color_scheme["text"],
                        },
                    ),
                    (
                        html.Details(
                            [
                                html.Summary(
                                    "Technical Details",
                                    style={"cursor": "pointer", "marginTop": "10px"},
                                ),
                                html.P(
                                    tech_msg,
                                    style={
                                        "margin": "5px 0",
                                        "fontFamily": "monospace",
                                        "fontSize": "12px",
                                    },
                                ),
                            ],
                            style={"marginTop": "10px"},
                        )
                        if tech_msg != user_msg
                        else None
                    ),
                ]
            )
        ],
        style={
            "border": f"2px solid {color_scheme['border']}",
            "backgroundColor": color_scheme["bg"],
            "padding": "15px",
            "borderRadius": "8px",
            "margin": "10px 0",
        },
    )


def create_success_message(message: str, details: Optional[str] = None) -> html.Div:
    """
    Create a standardized success message for display to users.

    Args:
        message: Success message text
        details: Optional additional details

    Returns:
        html.Div: Styled success message component
    """
    return html.Div(
        [
            html.P(
                f"✅ {message}",
                style={"margin": "0", "fontWeight": "bold", "color": "darkgreen"},
            ),
            (
                html.P(details, style={"margin": "5px 0 0 0", "color": "green"})
                if details
                else None
            ),
        ],
        style={
            "border": "2px solid green",
            "backgroundColor": "#e8f5e8",
            "padding": "15px",
            "borderRadius": "8px",
            "margin": "10px 0",
        },
    )


def handle_callback_error(func):
    """
    Decorator for consistent error handling in callbacks.

    Usage:
        @handle_callback_error
        def my_callback(...):
            # callback logic
            return results
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CallbackError as e:
            logging.error(f"Callback error in {func.__name__}: {e.technical_message}")
            # Return appropriate no_update or error UI based on callback signature
            return create_callback_error_response(e, func.__name__)
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            error = CallbackError(
                f"An unexpected error occurred in {func.__name__.replace('_', ' ')}",
                str(e),
            )
            return create_callback_error_response(error, func.__name__)

    return wrapper


def create_callback_error_response(error: Exception, callback_name: str) -> Any:
    """
    Create appropriate error response based on callback type.
    This is a simplified version - in practice, you'd need to know the expected return structure.
    """
    # For now, return a generic error message
    # In a full implementation, you'd inspect the callback signature or use a registry
    return create_error_message(error, callback_name.replace("_", " ").title())
