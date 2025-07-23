"""
Base Callback Classes for Modular Callback Architecture.

This module provides the foundation for the application's modular callback system,
defining abstract base classes that establish consistent patterns for callback
registration, error handling, and lifecycle management. It solves circular import
issues while promoting code reusability and standardization across all callback types.

Key Features:
- **Abstract Base Classes**: Enforce consistent callback structure and interface
- **Category Organization**: Logical grouping of callbacks by functionality
- **Logging Integration**: Standardized logging for each callback category
- **Registration Pattern**: Consistent method for registering callbacks with Dash app
- **Error Handling Foundation**: Base error handling patterns for all callbacks

Callback Categories:
1. **FileUploadCallbackBase**: File processing and validation callbacks
2. **MapInteractionCallbackBase**: Map clicks, selections, and drawing interactions
3. **PlotGenerationCallbackBase**: Section plots and borehole log generation
4. **SearchCallbackBase**: Borehole search and filtering functionality
5. **MarkerHandlingCallbackBase**: Map marker management and updates

Design Benefits:
- **Circular Import Prevention**: Separates base classes from implementation
- **Consistent Interface**: All callbacks follow the same registration pattern
- **Maintainable Code**: Clear separation of concerns and standardized structure
- **Debugging Support**: Built-in logging with callback-specific loggers
- **Extensibility**: Easy to add new callback types following established patterns

Implementation Pattern:
    class CustomCallback(CallbackBase):
        def register(self, app):
            @app.callback(...)
            def callback_function(...):
                # Implementation
                pass

Dependencies:
- abc: Abstract base class support for interface definition
- logging: Standardized logging infrastructure for callback debugging

Author: [Project Team]
Last Modified: July 2025
"""

import logging
from abc import ABC, abstractmethod


class CallbackBase(ABC):
    """Abstract base class for all callbacks."""

    def __init__(self, name: str, category: str = None):
        self.name = name
        self.category = category or self.__class__.__name__.lower()
        self.logger = logging.getLogger(f"callbacks.{self.name}")

    @abstractmethod
    def register(self, app):
        """Register this callback with the Dash app."""
        pass


class FileUploadCallbackBase(CallbackBase):
    """Base class for file upload related callbacks."""

    def __init__(self, name: str):
        super().__init__(name, "file_upload")


class MapInteractionCallbackBase(CallbackBase):
    """Base class for map interaction callbacks."""

    def __init__(self, name: str):
        super().__init__(name, "map_interactions")


class PlotGenerationCallbackBase(CallbackBase):
    """Base class for plot generation callbacks."""

    def __init__(self, name: str):
        super().__init__(name, "plot_generation")


class SearchCallbackBase(CallbackBase):
    """Base class for search functionality callbacks."""

    def __init__(self, name: str):
        super().__init__(name, "search")


class MarkerHandlingCallbackBase(CallbackBase):
    """Base class for marker handling callbacks."""

    def __init__(self, name: str):
        super().__init__(name, "marker_interaction")
