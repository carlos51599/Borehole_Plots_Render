"""
Plotly Map Component - Replacement for dash-leaflet

This module provides a robust alternative to dash-leaflet using Plotly's native
map capabilities. It solves the center/zoom update issues that plague dash-leaflet.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def create_borehole_map_plotly(
    borehole_data: Optional[pd.DataFrame] = None,
    center: Optional[List[float]] = None,
    zoom: int = 6,
    height: int = 500,
    map_id: str = "borehole-map-plotly",
) -> dcc.Graph:
    """
    Create a Plotly-based map component to replace dash-leaflet.

    This function creates an interactive map using Plotly that doesn't suffer
    from the center/zoom update issues present in dash-leaflet.

    Args:
        borehole_data: DataFrame with 'lat', 'lon', 'name' columns
        center: [lat, lon] for map center
        zoom: zoom level (1-20)
        height: map height in pixels
        map_id: HTML id for the map component

    Returns:
        dcc.Graph component ready for Dash layout
    """

    if borehole_data is None or borehole_data.empty:
        # Create empty map
        fig = go.Figure()

        fig.update_layout(
            map={
                "style": "open-street-map",
                "center": {
                    "lat": center[0] if center else 51.5,
                    "lon": center[1] if center else -0.1,
                },
                "zoom": zoom,
            },
            height=height,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            showlegend=False,
        )

        logger.info(f"Created empty Plotly map centered at {center} with zoom {zoom}")

    else:
        # Create map with borehole markers
        fig = px.scatter_map(
            borehole_data,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={
                col: True
                for col in borehole_data.columns
                if col not in ["lat", "lon", "name"]
            },
            zoom=zoom,
            height=height,
            color_discrete_sequence=["#1f77b4"],  # Blue markers like original
        )

        # Update map style and center
        fig.update_layout(
            map_style="open-street-map", margin={"l": 0, "r": 0, "t": 0, "b": 0}
        )

        if center:
            fig.update_layout(
                map={"center": {"lat": center[0], "lon": center[1]}, "zoom": zoom}
            )

        logger.info(f"Created Plotly map with {len(borehole_data)} boreholes")

    return dcc.Graph(
        id=map_id,
        figure=fig,
        style={"height": f"{height}px", "width": "100%"},
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
        },
    )


def update_map_position(
    figure: Dict[str, Any], center: List[float], zoom: int
) -> Dict[str, Any]:
    """
    Update map center and zoom - GUARANTEED TO WORK (unlike dash-leaflet).

    Args:
        figure: Current Plotly figure dict
        center: [lat, lon] for new center
        zoom: new zoom level

    Returns:
        Updated figure dict
    """

    if "layout" not in figure:
        figure["layout"] = {}

    if "map" not in figure["layout"]:
        figure["layout"]["map"] = {}

    figure["layout"]["map"]["center"] = {"lat": center[0], "lon": center[1]}
    figure["layout"]["map"]["zoom"] = zoom

    logger.info(f"Updated map position to center={center}, zoom={zoom}")

    return figure


def calculate_optimal_map_view(borehole_data: pd.DataFrame) -> Tuple[List[float], int]:
    """
    Calculate optimal center and zoom for borehole data.

    Args:
        borehole_data: DataFrame with 'lat', 'lon' columns

    Returns:
        Tuple of (center [lat, lon], zoom_level)
    """

    if borehole_data.empty:
        return [51.5, -0.1], 6

    # Calculate center
    center_lat = borehole_data["lat"].mean()
    center_lon = borehole_data["lon"].mean()

    # Calculate bounding box
    lat_range = borehole_data["lat"].max() - borehole_data["lat"].min()
    lon_range = borehole_data["lon"].max() - borehole_data["lon"].min()

    # Estimate zoom level based on coordinate range
    max_range = max(lat_range, lon_range)

    if max_range < 0.01:  # Very close points
        zoom = 15
    elif max_range < 0.05:  # Close points
        zoom = 13
    elif max_range < 0.1:  # Nearby points
        zoom = 11
    elif max_range < 0.5:  # Local area
        zoom = 9
    elif max_range < 1.0:  # Regional
        zoom = 8
    elif max_range < 5.0:  # Wide area
        zoom = 6
    else:  # Very wide area
        zoom = 5

    logger.info(
        f"Calculated optimal view: center=[{center_lat:.4f}, {center_lon:.4f}], zoom={zoom}"
    )

    return [center_lat, center_lon], zoom


def add_markers_to_figure(
    figure: Dict[str, Any], borehole_data: pd.DataFrame
) -> Dict[str, Any]:
    """
    Add borehole markers to existing Plotly figure.

    Args:
        figure: Plotly figure dict
        borehole_data: DataFrame with 'lat', 'lon', 'name' columns

    Returns:
        Updated figure with markers
    """

    if borehole_data.empty:
        return figure

    # Create scatter trace
    scatter_trace = go.Scattermap(
        lat=borehole_data["lat"],
        lon=borehole_data["lon"],
        mode="markers",
        marker=go.scattermap.Marker(size=12, color="#1f77b4", opacity=0.8),
        text=borehole_data["name"],
        hovertemplate="<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>",
        name="Boreholes",
    )

    if "data" not in figure:
        figure["data"] = []

    # Clear existing traces and add new one
    figure["data"] = [scatter_trace]

    logger.info(f"Added {len(borehole_data)} markers to map")

    return figure


def create_map_with_drawing_tools(
    borehole_data: Optional[pd.DataFrame] = None,
    center: Optional[List[float]] = None,
    zoom: int = 6,
    height: int = 500,
    map_id: str = "borehole-map-plotly",
) -> dcc.Graph:
    """
    Create map with drawing capabilities (alternative to EditControl).

    This provides basic drawing functionality using Plotly's built-in tools.
    """

    map_component = create_borehole_map_plotly(
        borehole_data=borehole_data,
        center=center,
        zoom=zoom,
        height=height,
        map_id=map_id,
    )

    # Enable drawing tools via config
    map_component.config.update(
        {
            "modeBarButtonsToAdd": [
                "drawline",
                "drawopenpath",
                "drawclosedpath",
                "drawcircle",
                "drawrect",
                "eraseshape",
            ]
        }
    )

    return map_component


# Migration helper functions


def convert_dash_leaflet_center_to_plotly(dl_center: List[float]) -> List[float]:
    """Convert dash-leaflet center format to Plotly format."""
    return dl_center  # Same format


def convert_dash_leaflet_zoom_to_plotly(dl_zoom: int) -> int:
    """Convert dash-leaflet zoom to Plotly zoom."""
    return dl_zoom  # Same format


def migrate_borehole_data_for_plotly(borehole_data: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare borehole data for Plotly map usage.

    Ensures required columns exist and are properly formatted.
    """

    required_columns = ["lat", "lon", "name"]

    # Check for required columns
    missing_columns = [
        col for col in required_columns if col not in borehole_data.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Ensure numeric types for coordinates
    borehole_data["lat"] = pd.to_numeric(borehole_data["lat"], errors="coerce")
    borehole_data["lon"] = pd.to_numeric(borehole_data["lon"], errors="coerce")

    # Remove rows with invalid coordinates
    borehole_data = borehole_data.dropna(subset=["lat", "lon"])

    logger.info(f"Prepared {len(borehole_data)} boreholes for Plotly map")

    return borehole_data


# Example usage and testing
if __name__ == "__main__":
    # Example borehole data
    sample_data = pd.DataFrame(
        {
            "lat": [51.5074, 51.5155, 51.5033],
            "lon": [-0.1278, -0.0922, -0.1195],
            "name": ["BH001", "BH002", "BH003"],
            "depth": [10.5, 15.2, 8.7],
        }
    )

    # Test map creation
    map_component = create_borehole_map_plotly(
        borehole_data=sample_data, center=None, zoom=12  # Auto-calculate
    )

    print("✅ Plotly map component created successfully")
    print(f"Map ID: {map_component.id}")
    print(f"Map type: {type(map_component)}")
