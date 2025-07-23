"""
Callbacks Package

This package contains all the callback handling functionality for the Dash application,
organized into focused modules for better maintainability and testing.

The package provides:
- Base callback classes with common functionality
- Centralized callback management and registration
- Specialized callback modules for different application areas
- Error handling and state management integration
"""

import logging
from typing import Any, Dict, List, Optional

# Import utilities
from .error_handling import (
    CallbackError,
    create_error_message,
    create_success_message,
    handle_callback_error,
    create_callback_error_response,
)
from .file_validation import (
    validate_file_size,
    validate_total_upload_size,
    validate_file_content,
    safe_filename,
)
from .coordinate_utils import (
    transform_coordinates,
    calculate_map_bounds,
    calculate_map_center_and_zoom,
    create_selection_shape_visual,
    validate_borehole_near_polyline,
    BLUE_MARKER,
    GREEN_MARKER,
)

# Import base classes from separate module to avoid circular imports
from .base import (
    CallbackBase,
    FileUploadCallbackBase,
    MapInteractionCallbackBase,
    PlotGenerationCallbackBase,
    SearchCallbackBase,
    MarkerHandlingCallbackBase,
)

# Import callback implementations
from .file_upload import FileUploadCallback
from .map_interactions import MapInteractionCallback
from .plot_generation import PlotGenerationCallback
from .search_functionality import SearchFunctionalityCallback
from .marker_handling import MarkerHandlingCallback

logger = logging.getLogger(__name__)


class CallbackManager:
    """Manages registration and organization of all callbacks."""

    def __init__(self):
        self.callbacks: List[CallbackBase] = []
        self.logger = logging.getLogger("callbacks")

    def add_callback(self, callback: CallbackBase):
        """Add a callback to the manager."""
        self.callbacks.append(callback)
        self.logger.debug(f"Added callback: {callback.name} ({callback.category})")

    def register_all(self, app):
        """Register all callbacks with the Dash app."""
        for callback in self.callbacks:
            try:
                callback.register(app)
                self.logger.info(f"Registered callback: {callback.name}")
            except Exception as e:
                self.logger.error(f"Failed to register callback {callback.name}: {e}")
                raise

    def get_callback_summary(self) -> Dict[str, Any]:
        """Get a summary of registered callbacks."""
        categories = {}
        for callback in self.callbacks:
            if callback.category not in categories:
                categories[callback.category] = []
            categories[callback.category].append(callback.name)

        return {
            "total_callbacks": len(self.callbacks),
            "categories": categories,
            "callback_names": [cb.name for cb in self.callbacks],
        }


# Global callback manager instance
_callback_manager = None


def get_callback_manager() -> CallbackManager:
    """Get the global callback manager instance."""
    global _callback_manager
    if _callback_manager is None:
        _callback_manager = CallbackManager()
        logger.info("Created global callback manager instance")
    return _callback_manager


def register_all_callbacks(app):
    """
    Convenience function to register all application callbacks.

    This function creates instances of all callback classes and registers
    them with the provided Dash app instance.
    """
    manager = get_callback_manager()

    # Create callback instances
    callbacks = [
        FileUploadCallback(),
        MapInteractionCallback(),
        PlotGenerationCallback(),
        SearchFunctionalityCallback(),
        MarkerHandlingCallback(),
    ]

    # Add to manager and register
    for callback in callbacks:
        manager.add_callback(callback)

    # Register all with the app
    manager.register_all(app)

    summary = manager.get_callback_summary()
    logger.info(
        f"Registered {summary['total_callbacks']} callbacks across {len(summary['categories'])} categories"
    )

    return manager


# Export main classes and functions
__all__ = [
    # Base classes
    "CallbackBase",
    "FileUploadCallbackBase",
    "MapInteractionCallbackBase",
    "PlotGenerationCallbackBase",
    "SearchCallbackBase",
    "MarkerHandlingCallbackBase",
    # Manager
    "CallbackManager",
    "get_callback_manager",
    # Callback implementations
    "FileUploadCallback",
    "MapInteractionCallback",
    "PlotGenerationCallback",
    "SearchFunctionalityCallback",
    "MarkerHandlingCallback",
    # Utility functions
    "register_all_callbacks",
]
