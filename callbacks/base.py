"""
Base Callback Classes

This module contains the base classes for all callback types,
separated to avoid circular import issues.
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
