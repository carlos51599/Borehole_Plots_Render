"""
State Models

This module defines the data models for managing application state.
These models provide type safety, validation, and clear interfaces
for state management throughout the application.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime


@dataclass
class BoreholeData:
    """Model for borehole data management."""

    loca_df: Optional[pd.DataFrame] = None
    filename_map: Dict[str, str] = field(default_factory=dict)
    all_borehole_ids: List[str] = field(default_factory=list)
    ags_file: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def is_loaded(self) -> bool:
        """Check if borehole data is loaded."""
        return self.loca_df is not None and not self.loca_df.empty

    def get_borehole_count(self) -> int:
        """Get the number of loaded boreholes."""
        if self.loca_df is None:
            return 0
        return len(self.loca_df)

    def get_borehole_by_id(self, borehole_id: str) -> Optional[pd.Series]:
        """Get a specific borehole by ID."""
        if not self.is_loaded:
            return None

        matches = self.loca_df[self.loca_df["LOCA_ID"] == borehole_id]
        if matches.empty:
            return None
        return matches.iloc[0]


@dataclass
class MapState:
    """Model for map-related state."""

    center: Tuple[float, float] = (51.5, -0.1)  # Default UK coordinates
    zoom: int = 6
    bounds: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None
    last_user_interaction: Optional[datetime] = None
    auto_zoom_enabled: bool = True

    def update_center(self, lat: float, lon: float, zoom: Optional[int] = None):
        """Update map center and optionally zoom."""
        self.center = (lat, lon)
        if zoom is not None:
            self.zoom = zoom
        self.last_user_interaction = datetime.now()

    def set_bounds_from_coordinates(self, coordinates: List[Tuple[float, float]]):
        """Calculate and set bounds from a list of coordinates."""
        if not coordinates:
            return

        lats = [coord[0] for coord in coordinates]
        lons = [coord[1] for coord in coordinates]

        self.bounds = ((min(lats), min(lons)), (max(lats), max(lons)))


@dataclass
class SelectionState:
    """Model for borehole selection state."""

    selected_borehole_ids: List[str] = field(default_factory=list)
    selection_method: Optional[str] = None  # 'shape', 'checkbox', 'search', 'marker'
    last_polyline: Optional[List[Tuple[float, float]]] = None
    buffer_meters: float = 50.0
    polyline_feature: Optional[Dict[str, Any]] = None
    is_polyline_selection: bool = False
    last_selection_time: datetime = field(default_factory=datetime.now)

    def clear_selection(self):
        """Clear all selection state."""
        self.selected_borehole_ids.clear()
        self.selection_method = None
        self.last_polyline = None
        self.polyline_feature = None
        self.is_polyline_selection = False
        self.last_selection_time = datetime.now()

    def update_selection(self, borehole_ids: List[str], method: str):
        """Update the current selection."""
        self.selected_borehole_ids = borehole_ids.copy()
        self.selection_method = method
        self.last_selection_time = datetime.now()

    def add_polyline_selection(
        self,
        borehole_ids: List[str],
        polyline_coords: List[Tuple[float, float]],
        buffer_meters: float = 50.0,
    ):
        """Add a polyline-based selection."""
        self.selected_borehole_ids = borehole_ids.copy()
        self.selection_method = "polyline"
        self.last_polyline = polyline_coords.copy()
        self.buffer_meters = buffer_meters
        self.is_polyline_selection = True
        self.last_selection_time = datetime.now()


@dataclass
class PlotState:
    """Model for plot generation state."""

    show_labels: bool = False
    last_generated_section: Optional[bytes] = None
    last_generated_log: Optional[Dict[str, Any]] = None
    generation_in_progress: bool = False
    last_error: Optional[str] = None
    last_generation_time: Optional[datetime] = None

    def start_generation(self):
        """Mark plot generation as in progress."""
        self.generation_in_progress = True
        self.last_error = None

    def complete_generation(self, success: bool, error_message: Optional[str] = None):
        """Mark plot generation as complete."""
        self.generation_in_progress = False
        self.last_generation_time = datetime.now()
        if not success:
            self.last_error = error_message

    def clear_plots(self):
        """Clear all generated plots."""
        self.last_generated_section = None
        self.last_generated_log = None
        self.last_error = None


@dataclass
class UploadState:
    """Model for file upload state."""

    files_uploaded: List[str] = field(default_factory=list)
    upload_in_progress: bool = False
    total_size_mb: float = 0.0
    upload_errors: List[str] = field(default_factory=list)
    last_upload_time: Optional[datetime] = None

    def start_upload(self):
        """Mark upload as in progress."""
        self.upload_in_progress = True
        self.upload_errors.clear()

    def complete_upload(
        self, files: List[str], total_size: float, errors: List[str] = None
    ):
        """Mark upload as complete."""
        self.upload_in_progress = False
        self.files_uploaded = files.copy()
        self.total_size_mb = total_size
        self.upload_errors = errors.copy() if errors else []
        self.last_upload_time = datetime.now()

    def clear_upload(self):
        """Clear upload state."""
        self.files_uploaded.clear()
        self.upload_in_progress = False
        self.total_size_mb = 0.0
        self.upload_errors.clear()
        self.last_upload_time = None
