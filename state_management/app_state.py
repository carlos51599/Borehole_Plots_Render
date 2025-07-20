"""
Centralized Application State Manager

This module provides a singleton state manager that maintains all application state
in a centralized, thread-safe manner. This replaces the chaotic "State Spaghetti"
pattern identified in the health report.
"""

import logging
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime

from .state_models import (
    BoreholeData,
    MapState,
    SelectionState,
    PlotState,
    UploadState,
)

logger = logging.getLogger(__name__)


class AppState:
    """
    Centralized application state manager.

    This class provides a single source of truth for all application state,
    with proper synchronization and change tracking.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._borehole_data = BoreholeData()
        self._map_state = MapState()
        self._selection_state = SelectionState()
        self._plot_state = PlotState()
        self._upload_state = UploadState()
        self._state_version = 0
        self._change_listeners = []

        logger.info("Initialized centralized application state manager")

    @property
    def borehole_data(self) -> BoreholeData:
        """Get borehole data state."""
        return self._borehole_data

    @property
    def map_state(self) -> MapState:
        """Get map state."""
        return self._map_state

    @property
    def selection_state(self) -> SelectionState:
        """Get selection state."""
        return self._selection_state

    @property
    def plot_state(self) -> PlotState:
        """Get plot state."""
        return self._plot_state

    @property
    def upload_state(self) -> UploadState:
        """Get upload state."""
        return self._upload_state

    def get_state_version(self) -> int:
        """Get current state version for change tracking."""
        with self._lock:
            return self._state_version

    def update_borehole_data(self, **kwargs) -> None:
        """Update borehole data and increment state version."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._borehole_data, key):
                    setattr(self._borehole_data, key, value)
                else:
                    logger.warning(f"Unknown borehole data attribute: {key}")

            self._borehole_data.last_updated = datetime.now()
            self._increment_version()
            logger.debug(f"Updated borehole data: {list(kwargs.keys())}")

    def update_map_state(self, **kwargs) -> None:
        """Update map state and increment state version."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._map_state, key):
                    setattr(self._map_state, key, value)
                else:
                    logger.warning(f"Unknown map state attribute: {key}")

            self._increment_version()
            logger.debug(f"Updated map state: {list(kwargs.keys())}")

    def update_selection_state(self, **kwargs) -> None:
        """Update selection state and increment state version."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._selection_state, key):
                    setattr(self._selection_state, key, value)
                else:
                    logger.warning(f"Unknown selection state attribute: {key}")

            self._selection_state.last_selection_time = datetime.now()
            self._increment_version()
            logger.debug(f"Updated selection state: {list(kwargs.keys())}")

    def update_plot_state(self, **kwargs) -> None:
        """Update plot state and increment state version."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._plot_state, key):
                    setattr(self._plot_state, key, value)
                else:
                    logger.warning(f"Unknown plot state attribute: {key}")

            self._increment_version()
            logger.debug(f"Updated plot state: {list(kwargs.keys())}")

    def update_upload_state(self, **kwargs) -> None:
        """Update upload state and increment state version."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._upload_state, key):
                    setattr(self._upload_state, key, value)
                else:
                    logger.warning(f"Unknown upload state attribute: {key}")

            self._increment_version()
            logger.debug(f"Updated upload state: {list(kwargs.keys())}")

    def clear_all_state(self) -> None:
        """Clear all application state."""
        with self._lock:
            self._borehole_data = BoreholeData()
            self._map_state = MapState()
            self._selection_state = SelectionState()
            self._plot_state = PlotState()
            self._upload_state = UploadState()
            self._increment_version()
            logger.info("Cleared all application state")

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state for debugging."""
        with self._lock:
            return {
                "state_version": self._state_version,
                "borehole_count": self._borehole_data.get_borehole_count(),
                "selected_boreholes": len(self._selection_state.selected_borehole_ids),
                "map_center": self._map_state.center,
                "map_zoom": self._map_state.zoom,
                "upload_files": len(self._upload_state.files_uploaded),
                "plot_in_progress": self._plot_state.generation_in_progress,
                "last_updated": self._borehole_data.last_updated.isoformat(),
            }

    def add_change_listener(self, callback):
        """Add a callback to be notified of state changes."""
        with self._lock:
            self._change_listeners.append(callback)

    def remove_change_listener(self, callback):
        """Remove a change listener."""
        with self._lock:
            if callback in self._change_listeners:
                self._change_listeners.remove(callback)

    def _increment_version(self):
        """Increment state version and notify listeners."""
        self._state_version += 1
        for listener in self._change_listeners:
            try:
                listener(self._state_version)
            except Exception as e:
                logger.error(f"Error in state change listener: {e}")

    def to_dash_store_format(self) -> Dict[str, Any]:
        """
        Convert state to format suitable for Dash Store components.

        This maintains compatibility with existing callback patterns
        while providing centralized state management.
        """
        with self._lock:
            # Convert borehole DataFrame to dict format for Dash
            loca_df_dict = None
            if self._borehole_data.loca_df is not None:
                loca_df_dict = self._borehole_data.loca_df.to_dict("records")

            return {
                "loca_df": loca_df_dict,
                "filename_map": self._borehole_data.filename_map,
                "all_borehole_ids": self._borehole_data.all_borehole_ids,
                "selection_boreholes": self._selection_state.selected_borehole_ids,
                "last_polyline": self._selection_state.last_polyline,
                "buffer_meters": self._selection_state.buffer_meters,
                "is_polyline": self._selection_state.is_polyline_selection,
                "polyline_feature": self._selection_state.polyline_feature,
                "map_center": list(self._map_state.center),
                "map_zoom": self._map_state.zoom,
                "show_labels": self._plot_state.show_labels,
                "state_version": self._state_version,
            }

    def from_dash_store_format(self, data: Dict[str, Any]) -> None:
        """
        Update state from Dash Store format.

        This allows backwards compatibility with existing Dash Store patterns.
        """
        if not data:
            return

        with self._lock:
            # Update borehole data
            if "loca_df" in data and data["loca_df"]:
                import pandas as pd

                self._borehole_data.loca_df = pd.DataFrame(data["loca_df"])

            if "filename_map" in data:
                self._borehole_data.filename_map = data["filename_map"]

            if "all_borehole_ids" in data:
                self._borehole_data.all_borehole_ids = data["all_borehole_ids"]

            # Update selection state
            if "selection_boreholes" in data:
                self._selection_state.selected_borehole_ids = data[
                    "selection_boreholes"
                ]

            if "last_polyline" in data:
                self._selection_state.last_polyline = data["last_polyline"]

            if "buffer_meters" in data:
                self._selection_state.buffer_meters = data["buffer_meters"]

            if "is_polyline" in data:
                self._selection_state.is_polyline_selection = data["is_polyline"]

            if "polyline_feature" in data:
                self._selection_state.polyline_feature = data["polyline_feature"]

            # Update map state
            if "map_center" in data:
                self._map_state.center = tuple(data["map_center"])

            if "map_zoom" in data:
                self._map_state.zoom = data["map_zoom"]

            # Update plot state
            if "show_labels" in data:
                self._plot_state.show_labels = data["show_labels"]

            self._increment_version()
            logger.debug("Updated state from Dash Store format")


# Global singleton instance
_app_state_instance: Optional[AppState] = None
_instance_lock = threading.Lock()


def get_app_state_manager() -> AppState:
    """
    Get the singleton application state manager.

    Returns:
        AppState: The singleton application state manager
    """
    global _app_state_instance

    if _app_state_instance is None:
        with _instance_lock:
            if _app_state_instance is None:
                _app_state_instance = AppState()
                logger.info("Created singleton application state manager")

    return _app_state_instance


def reset_app_state_manager() -> None:
    """
    Reset the singleton application state manager.

    This should only be used for testing purposes.
    """
    global _app_state_instance

    with _instance_lock:
        _app_state_instance = None
        logger.info("Reset application state manager")
