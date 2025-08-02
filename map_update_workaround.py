"""
Map Update Workaround for Dash-Leaflet

Based on research findings from dash-leaflet GitHub issues, the component
has a known bug where center and zoom properties don't update visually
even when properly returned from callbacks.

This module provides a workaround using component key refresh technique.
"""

import time
from typing import List, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


def create_map_update_key() -> str:
    """
    Create a unique key for forcing map component refresh.

    Returns:
        str: Unique key based on current timestamp
    """
    return f"map-{int(time.time() * 1000)}"


def force_map_refresh_with_new_position(
    center: List[float], zoom: int, children: List[Any] = None
) -> Tuple[int, List[float], int, List[Any]]:
    """
    Create new map invalidateSize value and position data to force visual refresh.

    This workaround addresses the dash-leaflet bug where center/zoom
    properties don't update visually by forcing map invalidation.

    Args:
        center: New map center [lat, lon]
        zoom: New zoom level
        children: Map children components (markers, etc.)

    Returns:
        tuple: (invalidateSize_value, center, zoom, children)
    """
    invalidate_value = int(time.time() * 1000)  # Unique timestamp
    logger.info(
        f"🔄 Force map refresh: invalidateSize={invalidate_value}, center={center}, zoom={zoom}"
    )

    return invalidate_value, center, zoom, children or []


def should_update_map_position(
    current_center: Optional[List[float]],
    current_zoom: Optional[int],
    new_center: List[float],
    new_zoom: int,
    tolerance: float = 0.001,
) -> bool:
    """
    Determine if map position has changed enough to warrant update.

    Args:
        current_center: Current map center
        current_zoom: Current zoom level
        new_center: Proposed new center
        new_zoom: Proposed new zoom
        tolerance: Minimum change threshold for center coordinates

    Returns:
        bool: True if update is needed
    """
    if not current_center or current_zoom is None:
        return True

    # Check zoom difference
    if current_zoom != new_zoom:
        return True

    # Check center difference
    if len(current_center) != 2 or len(new_center) != 2:
        return True

    lat_diff = abs(current_center[0] - new_center[0])
    lon_diff = abs(current_center[1] - new_center[1])

    return lat_diff > tolerance or lon_diff > tolerance


class MapUpdateHelper:
    """Helper class for managing map updates with workarounds."""

    def __init__(self):
        self._last_update_time = 0
        self._min_update_interval = 0.5  # Minimum seconds between updates

    def can_update(self) -> bool:
        """Check if enough time has passed since last update."""
        current_time = time.time()
        if current_time - self._last_update_time >= self._min_update_interval:
            self._last_update_time = current_time
            return True
        return False

    def prepare_map_update(
        self,
        center: List[float],
        zoom: int,
        current_center: Optional[List[float]] = None,
        current_zoom: Optional[int] = None,
        children: List[Any] = None,
    ) -> Tuple[bool, Optional[int], List[float], int, List[Any]]:
        """
        Prepare map update with rate limiting and change detection.

        Returns:
            tuple: (should_update, invalidateSize_value, center, zoom, children)
        """
        # Check if update is needed
        if not should_update_map_position(current_center, current_zoom, center, zoom):
            logger.debug("Map position unchanged, skipping update")
            return False, None, center, zoom, children or []

        # Check rate limiting
        if not self.can_update():
            logger.debug("Rate limited, skipping map update")
            return False, None, center, zoom, children or []

        # Prepare update with forced refresh
        invalidate_value, final_center, final_zoom, final_children = (
            force_map_refresh_with_new_position(center, zoom, children)
        )

        return True, invalidate_value, final_center, final_zoom, final_children
