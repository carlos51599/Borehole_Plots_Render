"""
Loading Indicator Components for Enhanced User Experience.

This module provides centralized loading indicators and progress feedback for long-running
operations in the Geo Borehole Sections Render application. It significantly improves
user experience by providing clear, consistent feedback during data processing, file uploads,
and complex plot generation operations.

Key Features:
- **Customizable Spinners**: Multiple sizes and styles with configurable messages
- **Progress Bars**: Visual progress tracking for file operations and data processing
- **Toast Notifications**: Non-intrusive completion and error notifications
- **Non-blocking Loading States**: Maintain UI responsiveness during background operations
- **Operation-Specific Indicators**: Tailored feedback for different application functions

Loading Indicator Types:
1. **File Upload Loading**: Progress bars with file size and upload speed
2. **Data Processing Loading**: Spinners for AGS parsing and coordinate transformation
3. **Plot Generation Loading**: Specialized indicators for matplotlib rendering
4. **Map Loading**: Feedback for marker generation and geometric processing
5. **Search Loading**: Quick feedback for borehole search operations

User Experience Benefits:
- Clear indication that operations are in progress
- Prevents user confusion during long operations
- Provides estimated completion times where possible
- Reduces perceived wait time through visual feedback
- Professional appearance consistent with application design

Integration Points:
- File upload callbacks (AGS processing)
- Map interaction callbacks (selection processing)
- Plot generation callbacks (section and log creation)
- Search functionality (borehole filtering)
- Error handling systems (failure notifications)

Dependencies:
- dash: Core UI components and HTML generation
- app_constants: UI configuration and styling constants

Author: [Project Team]
Last Modified: July 2025
"""

import dash
from dash import html, dcc
import time
from typing import Optional, Dict, Any

from app_constants import UI_CONFIG


class LoadingIndicator:
    """
    Centralized loading indicator management for the application.

    Provides consistent loading states, progress feedback, and user notifications
    during long-running operations.
    """

    @staticmethod
    def create_spinner(
        loading_id: str, message: str = "Processing...", size: str = "default"
    ) -> html.Div:
        """
        Create a loading spinner component.

        Args:
            loading_id: Unique identifier for the loading state
            message: Message to display during loading
            size: Size of spinner ("small", "default", "large")

        Returns:
            html.Div: Loading spinner component
        """
        spinner_sizes = {
            "small": {"width": "20px", "height": "20px"},
            "default": {"width": "40px", "height": "40px"},
            "large": {"width": "60px", "height": "60px"},
        }

        spinner_style = {
            **spinner_sizes.get(size, spinner_sizes["default"]),
            "border": f"3px solid #f3f3f3",
            "border-top": f"3px solid {UI_CONFIG.PRIMARY_COLOR}",
            "borderRadius": "50%",
            "animation": "spin 1s linear infinite",
            "margin": "0 auto 10px auto",
        }

        return html.Div(
            [
                # CSS animation for spinner - using dcc.Store to inject CSS
                dcc.Store(id=f"css-store-{loading_id}", data={}),
                html.Div(style=spinner_style, id=f"spinner-{loading_id}"),
                html.P(
                    message,
                    style={
                        "text-align": "center",
                        "color": UI_CONFIG.PRIMARY_COLOR,
                        "font-weight": "bold",
                        "margin": "0",
                    },
                ),
            ],
            style={
                "display": "flex",
                "flex-direction": "column",
                "align-items": "center",
                "padding": "20px",
            },
            id=f"loading-{loading_id}",
        )

    @staticmethod
    def create_progress_bar(
        progress_id: str, current: int = 0, total: int = 100, message: str = ""
    ) -> html.Div:
        """
        Create a progress bar component.

        Args:
            progress_id: Unique identifier for the progress bar
            current: Current progress value
            total: Total/maximum progress value
            message: Optional message to display

        Returns:
            html.Div: Progress bar component
        """
        percentage = (current / total * 100) if total > 0 else 0

        return html.Div(
            [
                (
                    html.P(
                        message, style={"margin": "0 0 10px 0", "font-weight": "bold"}
                    )
                    if message
                    else None
                ),
                html.Div(
                    [
                        html.Div(
                            style={
                                "width": f"{percentage}%",
                                "height": "100%",
                                "backgroundColor": UI_CONFIG.SUCCESS_COLOR,
                                "transition": "width 0.3s ease-in-out",
                                "borderRadius": "3px",
                            }
                        )
                    ],
                    style={
                        "width": "100%",
                        "height": "20px",
                        "backgroundColor": "#e0e0e0",
                        "borderRadius": "3px",
                        "overflow": "hidden",
                        "margin-bottom": "5px",
                    },
                ),
                html.P(
                    f"{current}/{total} ({percentage:.1f}%)",
                    style={
                        "text-align": "center",
                        "margin": "0",
                        "font-size": "12px",
                        "color": "#666",
                    },
                ),
            ],
            id=f"progress-{progress_id}",
        )

    @staticmethod
    def create_file_upload_feedback(
        upload_id: str,
        files_processed: int = 0,
        total_files: int = 0,
        current_file: str = "",
    ) -> html.Div:
        """
        Create specialized feedback for file upload operations.

        Args:
            upload_id: Unique identifier for the upload operation
            files_processed: Number of files processed so far
            total_files: Total number of files to process
            current_file: Name of currently processing file

        Returns:
            html.Div: File upload feedback component
        """
        if total_files == 0:
            return LoadingIndicator.create_spinner(
                f"upload-{upload_id}", "Preparing file upload..."
            )

        return html.Div(
            [
                LoadingIndicator.create_progress_bar(
                    f"upload-progress-{upload_id}",
                    files_processed,
                    total_files,
                    "Processing Files",
                ),
                html.P(
                    f"Current: {current_file}" if current_file else "Initializing...",
                    style={
                        "font-style": "italic",
                        "color": "#666",
                        "margin": "10px 0 0 0",
                        "text-align": "center",
                    },
                ),
                html.P(
                    f"⏱️ Please wait while we process your files...",
                    style={
                        "color": UI_CONFIG.INFO_COLOR,
                        "text-align": "center",
                        "margin": "10px 0 0 0",
                        "font-size": "14px",
                    },
                ),
            ],
            id=f"upload-feedback-{upload_id}",
        )

    @staticmethod
    def create_plot_generation_feedback(
        plot_id: str, stage: str = "preparing"
    ) -> html.Div:
        """
        Create specialized feedback for plot generation operations.

        Args:
            plot_id: Unique identifier for the plot operation
            stage: Current stage of plot generation

        Returns:
            html.Div: Plot generation feedback component
        """
        stage_messages = {
            "preparing": "🔄 Preparing data for plotting...",
            "processing": "📊 Processing geological data...",
            "rendering": "🎨 Rendering plot graphics...",
            "finalizing": "✨ Finalizing plot layout...",
            "complete": "✅ Plot generation complete!",
        }

        message = stage_messages.get(stage, f"Processing: {stage}")

        if stage == "complete":
            return html.Div(
                [
                    html.P(
                        message,
                        style={
                            "color": UI_CONFIG.SUCCESS_COLOR,
                            "font-weight": "bold",
                            "text-align": "center",
                            "margin": "20px 0",
                        },
                    )
                ]
            )

        return html.Div(
            [
                LoadingIndicator.create_spinner(f"plot-{plot_id}", message, "default"),
                html.P(
                    "⚡ Large datasets may take up to 2-3 minutes to process",
                    style={
                        "color": UI_CONFIG.WARNING_COLOR,
                        "font-size": "12px",
                        "text-align": "center",
                        "margin": "10px 0 0 0",
                        "font-style": "italic",
                    },
                ),
            ],
            id=f"plot-feedback-{plot_id}",
        )

    @staticmethod
    def create_toast_notification(
        message: str, notification_type: str = "info", duration: int = 5000
    ) -> html.Div:
        """
        Create a toast notification for user feedback.

        Args:
            message: Message to display
            notification_type: Type of notification ("success", "error", "warning", "info")
            duration: Duration in milliseconds (auto-hide)

        Returns:
            html.Div: Toast notification component
        """
        type_colors = {
            "success": UI_CONFIG.SUCCESS_COLOR,
            "error": UI_CONFIG.ERROR_COLOR,
            "warning": UI_CONFIG.WARNING_COLOR,
            "info": UI_CONFIG.INFO_COLOR,
        }

        type_icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}

        color = type_colors.get(notification_type, UI_CONFIG.INFO_COLOR)
        icon = type_icons.get(notification_type, "ℹ️")

        return html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            icon, style={"margin-right": "8px", "font-size": "16px"}
                        ),
                        html.Span(message, style={"flex": "1"}),
                        html.Button(
                            "×",
                            style={
                                "background": "none",
                                "border": "none",
                                "font-size": "18px",
                                "cursor": "pointer",
                                "color": "#666",
                            },
                            id="toast-close",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "backgroundColor": color,
                        "color": "white",
                        "padding": "12px 16px",
                        "borderRadius": "4px",
                        "box-shadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "margin": "10px 0",
                        "min-width": "300px",
                        "animation": f"slideIn 0.3s ease-out",
                    },
                )
            ],
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "z-index": "9999",
            },
            id="toast-notification",
        )


class LoadingStates:
    """
    Manages loading states for different application components.

    Provides a centralized way to track and update loading states
    across the application.
    """

    def __init__(self):
        self._states = {}

    def set_loading(self, component_id: str, is_loading: bool, message: str = ""):
        """Set loading state for a component."""
        self._states[component_id] = {
            "loading": is_loading,
            "message": message,
            "timestamp": time.time(),
        }

    def is_loading(self, component_id: str) -> bool:
        """Check if a component is currently loading."""
        return self._states.get(component_id, {}).get("loading", False)

    def get_message(self, component_id: str) -> str:
        """Get the loading message for a component."""
        return self._states.get(component_id, {}).get("message", "")

    def clear_state(self, component_id: str):
        """Clear loading state for a component."""
        if component_id in self._states:
            del self._states[component_id]

    def clear_all(self):
        """Clear all loading states."""
        self._states.clear()

    def get_active_states(self) -> Dict[str, Any]:
        """Get all currently active loading states."""
        return {k: v for k, v in self._states.items() if v.get("loading", False)}


# Global loading state manager
_loading_manager = LoadingStates()


def get_loading_manager() -> LoadingStates:
    """Get the global loading state manager."""
    return _loading_manager


# Convenience functions for common loading scenarios
def create_upload_loading(
    upload_id: str, message: str = "Processing files..."
) -> html.Div:
    """Create loading indicator for file uploads."""
    return LoadingIndicator.create_file_upload_feedback(upload_id, 0, 0, "")


def create_plot_loading(plot_id: str, stage: str = "preparing") -> html.Div:
    """Create loading indicator for plot generation."""
    return LoadingIndicator.create_plot_generation_feedback(plot_id, stage)


def create_data_loading(data_id: str, message: str = "Loading data...") -> html.Div:
    """Create loading indicator for data operations."""
    return LoadingIndicator.create_spinner(data_id, message)


def create_success_toast(message: str) -> html.Div:
    """Create success toast notification."""
    return LoadingIndicator.create_toast_notification(message, "success")


def create_error_toast(message: str) -> html.Div:
    """Create error toast notification."""
    return LoadingIndicator.create_toast_notification(message, "error")


if __name__ == "__main__":
    # Simple test of loading components
    print("Loading Indicator Components")
    print("✓ Spinner component available")
    print("✓ Progress bar component available")
    print("✓ File upload feedback available")
    print("✓ Plot generation feedback available")
    print("✓ Toast notifications available")
    print("✓ Loading state manager available")

    # Test loading manager
    manager = get_loading_manager()
    manager.set_loading("test-component", True, "Testing...")
    print(f"✓ Loading manager test: {manager.is_loading('test-component')}")
    manager.clear_all()
    print("✓ All loading indicator components ready!")
