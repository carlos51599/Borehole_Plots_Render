"""
State Management Package

This package provides centralized state management for the application,
eliminating the chaotic "State Spaghetti" pattern identified in the health report.
"""

from .app_state import AppState, get_app_state_manager
from .state_models import (
    BoreholeData,
    MapState,
    SelectionState,
    PlotState,
    UploadState,
)

__all__ = [
    "AppState",
    "get_app_state_manager",
    "BoreholeData",
    "MapState",
    "SelectionState",
    "PlotState",
    "UploadState",
]
