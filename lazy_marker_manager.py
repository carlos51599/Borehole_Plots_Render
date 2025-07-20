"""
Lazy Marker Management Module

This module implements viewport-based lazy loading for map markers to improve performance
with large datasets by only rendering markers that are visible or relevant to the user.
"""

import logging
import pandas as pd
import dash_leaflet as dl
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ViewportBounds:
    """Represents the visible area of the map."""

    north: float
    south: float
    east: float
    west: float
    zoom: float


@dataclass
class MarkerCluster:
    """Represents a cluster of markers for high-density areas."""

    center_lat: float
    center_lon: float
    count: int
    borehole_ids: List[str]
    bounds: ViewportBounds


class LazyMarkerManager:
    """
    Manages map markers with lazy loading and viewport culling for performance.

    Features:
    - Viewport-based marker rendering (only visible markers)
    - Marker clustering for high-density areas
    - Progressive loading based on zoom levels
    - Memory-efficient marker updates
    """

    def __init__(
        self,
        max_markers_per_viewport: int = 100,
        clustering_zoom_threshold: float = 10.0,
    ):
        """
        Initialize the lazy marker manager.

        Args:
            max_markers_per_viewport: Maximum markers to render in viewport
            clustering_zoom_threshold: Zoom level below which to use clustering
        """
        self.max_markers_per_viewport = max_markers_per_viewport
        self.clustering_zoom_threshold = clustering_zoom_threshold
        self.marker_cache = {}  # Cache for rendered markers
        self.cluster_cache = {}  # Cache for marker clusters

        logger.info(
            f"LazyMarkerManager initialized: max_markers={max_markers_per_viewport}, clustering_threshold={clustering_zoom_threshold}"
        )

    def get_visible_markers(
        self,
        loca_df: pd.DataFrame,
        viewport: Optional[ViewportBounds] = None,
        selected_ids: Optional[List[str]] = None,
        force_all: bool = False,
    ) -> List[dl.Marker]:
        """
        Get markers that should be visible based on viewport and zoom level.

        Args:
            loca_df: DataFrame with borehole location data
            viewport: Current map viewport bounds and zoom
            selected_ids: List of selected borehole IDs (always visible)
            force_all: Force rendering all markers (for small datasets)

        Returns:
            List of Dash Leaflet marker components
        """
        try:
            if loca_df.empty:
                return []

            # For small datasets, render all markers
            if len(loca_df) <= 50 or force_all:
                logger.info(
                    f"Rendering all {len(loca_df)} markers (small dataset or forced)"
                )
                return self._create_all_markers(loca_df, selected_ids or [])

            # Use viewport culling for large datasets
            if viewport is None:
                # No viewport info - render first N markers as fallback
                limited_df = loca_df.head(self.max_markers_per_viewport)
                logger.info(
                    f"No viewport info - rendering first {len(limited_df)} markers"
                )
                return self._create_all_markers(limited_df, selected_ids or [])

            # Filter markers by viewport
            visible_df = self._filter_by_viewport(loca_df, viewport)

            # Apply clustering if needed
            if viewport.zoom < self.clustering_zoom_threshold:
                return self._create_clustered_markers(
                    visible_df, viewport, selected_ids or []
                )
            else:
                return self._create_viewport_markers(visible_df, selected_ids or [])

        except Exception as e:
            logger.error(f"Error in get_visible_markers: {e}", exc_info=True)
            # Fallback to first 20 markers on error
            return self._create_all_markers(loca_df.head(20), selected_ids or [])

    def _filter_by_viewport(
        self, loca_df: pd.DataFrame, viewport: ViewportBounds
    ) -> pd.DataFrame:
        """Filter DataFrame to only include markers within viewport bounds."""

        # Add some padding to viewport for smoother panning
        lat_padding = abs(viewport.north - viewport.south) * 0.1
        lon_padding = abs(viewport.east - viewport.west) * 0.1

        # Expand viewport bounds
        expanded_north = viewport.north + lat_padding
        expanded_south = viewport.south - lat_padding
        expanded_east = viewport.east + lon_padding
        expanded_west = viewport.west - lon_padding

        # Handle longitude wraparound at 180/-180
        if expanded_west > expanded_east:  # Crosses 180 meridian
            lon_mask = (loca_df["lon"] >= expanded_west) | (
                loca_df["lon"] <= expanded_east
            )
        else:
            lon_mask = (loca_df["lon"] >= expanded_west) & (
                loca_df["lon"] <= expanded_east
            )

        # Filter by bounds
        viewport_mask = (
            (loca_df["lat"] >= expanded_south)
            & (loca_df["lat"] <= expanded_north)
            & lon_mask
        )

        visible_df = loca_df[viewport_mask]
        logger.info(
            f"Viewport filtering: {len(visible_df)}/{len(loca_df)} markers visible"
        )

        return visible_df

    def _create_viewport_markers(
        self, df: pd.DataFrame, selected_ids: List[str]
    ) -> List[dl.Marker]:
        """Create markers for viewport-filtered data."""

        # Limit markers if still too many
        if len(df) > self.max_markers_per_viewport:
            # Prioritize selected markers
            selected_df = (
                df[df["LOCA_ID"].isin(selected_ids)] if selected_ids else pd.DataFrame()
            )
            remaining_count = max(0, self.max_markers_per_viewport - len(selected_df))

            # Add non-selected markers up to limit
            non_selected_df = (
                df[~df["LOCA_ID"].isin(selected_ids)] if selected_ids else df
            )
            limited_non_selected = non_selected_df.head(remaining_count)

            # Combine selected + limited non-selected
            if not selected_df.empty:
                final_df = pd.concat(
                    [selected_df, limited_non_selected], ignore_index=True
                )
            else:
                final_df = limited_non_selected

            logger.info(
                f"Limited to {len(final_df)} markers ({len(selected_df)} selected + {len(limited_non_selected)} others)"
            )
        else:
            final_df = df

        return self._create_all_markers(final_df, selected_ids)

    def _create_clustered_markers(
        self, df: pd.DataFrame, viewport: ViewportBounds, selected_ids: List[str]
    ) -> List[dl.Marker]:
        """Create clustered markers for zoomed-out views."""

        # Always show selected markers individually
        selected_df = (
            df[df["LOCA_ID"].isin(selected_ids)] if selected_ids else pd.DataFrame()
        )
        selected_markers = (
            self._create_all_markers(selected_df, selected_ids)
            if not selected_df.empty
            else []
        )

        # Cluster non-selected markers
        non_selected_df = df[~df["LOCA_ID"].isin(selected_ids)] if selected_ids else df

        if len(non_selected_df) <= 20:
            # Too few to cluster
            non_selected_markers = self._create_all_markers(non_selected_df, [])
            return selected_markers + non_selected_markers

        # Create clusters using simple grid-based clustering
        clusters = self._create_grid_clusters(non_selected_df, viewport)
        cluster_markers = []

        for cluster in clusters:
            if cluster.count == 1:
                # Single marker - render normally
                single_row = non_selected_df[
                    non_selected_df["LOCA_ID"].isin(cluster.borehole_ids)
                ].iloc[0]
                marker = self._create_single_marker(single_row, is_selected=False)
                cluster_markers.append(marker)
            else:
                # Cluster marker
                cluster_marker = self._create_cluster_marker(cluster)
                cluster_markers.append(cluster_marker)

        logger.info(
            f"Created {len(clusters)} clusters from {len(non_selected_df)} markers"
        )
        return selected_markers + cluster_markers

    def _create_grid_clusters(
        self, df: pd.DataFrame, viewport: ViewportBounds
    ) -> List[MarkerCluster]:
        """Create clusters using a simple grid-based approach."""

        # Calculate grid size based on zoom level
        grid_size = max(0.001, 0.1 / (2**viewport.zoom))  # Smaller grids at higher zoom

        clusters = {}

        for _, row in df.iterrows():
            lat, lon = row["lat"], row["lon"]

            # Calculate grid cell
            grid_lat = int(lat / grid_size) * grid_size
            grid_lon = int(lon / grid_size) * grid_size
            grid_key = (grid_lat, grid_lon)

            if grid_key not in clusters:
                clusters[grid_key] = {
                    "center_lat": grid_lat + grid_size / 2,
                    "center_lon": grid_lon + grid_size / 2,
                    "borehole_ids": [],
                    "lats": [],
                    "lons": [],
                }

            clusters[grid_key]["borehole_ids"].append(row["LOCA_ID"])
            clusters[grid_key]["lats"].append(lat)
            clusters[grid_key]["lons"].append(lon)

        # Convert to MarkerCluster objects
        result = []
        for grid_key, data in clusters.items():
            # Use centroid of actual points, not grid center
            actual_center_lat = sum(data["lats"]) / len(data["lats"])
            actual_center_lon = sum(data["lons"]) / len(data["lons"])

            cluster = MarkerCluster(
                center_lat=actual_center_lat,
                center_lon=actual_center_lon,
                count=len(data["borehole_ids"]),
                borehole_ids=data["borehole_ids"],
                bounds=viewport,  # Reference for cluster bounds
            )
            result.append(cluster)

        return result

    def _create_cluster_marker(self, cluster: MarkerCluster) -> dl.Marker:
        """Create a cluster marker representing multiple boreholes."""

        # Style cluster marker based on count
        if cluster.count <= 5:
            icon_color = "blue"
            size = 35
        elif cluster.count <= 15:
            icon_color = "orange"
            size = 45
        else:
            icon_color = "red"
            size = 55

        cluster_tooltip = f"""
        Cluster: {cluster.count} boreholes
        IDs: {', '.join(cluster.borehole_ids[:5])}
        {'...' if len(cluster.borehole_ids) > 5 else ''}
        Zoom in to see individual markers
        """

        cluster_icon = {
            "iconUrl": f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMTgiIGZpbGw9Intyb2xvcl9uYW1lfSIgZmlsbC1vcGFjaXR5PSIwLjgiLz4KPHR7Zm9udC1mYW1pbHk6IEFyaWFsLCBzYW5zLXNlcmlmOyBmb250LXNpemU6IDEycHg7IGZpbGw6IHdoaXRlOyB0ZXh0LWFuY2hvcjogbWlkZGxlO30KIDx0ZXh0IHg9IjIwIiB5PSIyNCI+e2NvdW50fTwvdGV4dD4KPC9zdmc+".replace(
                "{color_name}", icon_color
            ).replace(
                "{count}", str(cluster.count)
            ),
            "iconSize": [size, size],
            "iconAnchor": [size // 2, size // 2],
            "className": f"marker-cluster cluster-{icon_color}",
        }

        return dl.Marker(
            id={
                "type": "cluster-marker",
                "cluster_id": f"cluster_{cluster.center_lat}_{cluster.center_lon}",
            },
            position=[cluster.center_lat, cluster.center_lon],
            children=dl.Tooltip(cluster_tooltip.strip()),
            icon=cluster_icon,
        )

    def _create_all_markers(
        self, df: pd.DataFrame, selected_ids: List[str]
    ) -> List[dl.Marker]:
        """Create markers for all rows in DataFrame."""

        markers = []
        for i, row in df.iterrows():
            is_selected = row["LOCA_ID"] in selected_ids
            marker = self._create_single_marker(row, is_selected, index=i)
            markers.append(marker)

        return markers

    def _create_single_marker(
        self, row: pd.Series, is_selected: bool, index: Optional[int] = None
    ) -> dl.Marker:
        """Create a single marker from a DataFrame row."""

        lat, lon = row["lat"], row["lon"]
        borehole_id = str(row["LOCA_ID"]).strip()

        # Choose marker color
        icon_url = self._get_marker_icon_url(is_selected)

        # Create marker ID
        marker_id = {"type": "borehole-marker", "index": index or 0}

        # Format tooltip
        ground_level = self._format_depth_value(row.get("LOCA_GL", "N/A"))
        total_depth = self._format_depth_value(row.get("LOCA_FDEP", "N/A"))

        tooltip_text = f"""
        Borehole: {borehole_id}
        Ground Level: {ground_level}
        Total Depth: {total_depth}
        Click to view borehole log
        """

        marker_icon = {
            "iconUrl": icon_url,
            "iconSize": [25, 41],
            "iconAnchor": [12, 41],
            "popupAnchor": [1, -34],
            "shadowSize": [41, 41],
        }

        return dl.Marker(
            id=marker_id,
            position=[lat, lon],
            children=dl.Tooltip(tooltip_text.strip()),
            icon=marker_icon,
            n_clicks=0,
        )

    def _get_marker_icon_url(self, is_selected: bool) -> str:
        """Get the appropriate marker icon URL."""

        if is_selected:
            return "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"
        else:
            return "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"

    def _format_depth_value(self, value) -> str:
        """Format depth values for display."""

        if value == "N/A" or value is None or str(value).strip() == "":
            return "N/A"

        try:
            return f"{float(value):.2f}m"
        except (ValueError, TypeError):
            return "N/A"

    def update_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for monitoring."""

        return {
            "marker_cache_size": len(self.marker_cache),
            "cluster_cache_size": len(self.cluster_cache),
        }

    def clear_cache(self):
        """Clear all caches to free memory."""

        self.marker_cache.clear()
        self.cluster_cache.clear()
        logger.info("Marker cache cleared")


# Global instance
_lazy_marker_manager = None


def get_lazy_marker_manager() -> LazyMarkerManager:
    """Get the global lazy marker manager instance."""

    global _lazy_marker_manager
    if _lazy_marker_manager is None:
        _lazy_marker_manager = LazyMarkerManager()
    return _lazy_marker_manager


def create_viewport_bounds(
    center: List[float], zoom: float, map_width: int = 1000, map_height: int = 500
) -> ViewportBounds:
    """
    Create viewport bounds from map center, zoom, and dimensions.

    Args:
        center: [lat, lon] of map center
        zoom: Current zoom level
        map_width: Map width in pixels
        map_height: Map height in pixels

    Returns:
        ViewportBounds object
    """

    # Approximate degrees per pixel at different zoom levels
    # These are rough approximations for calculating viewport bounds
    meters_per_pixel = 156543.03392 * 2.71828182846 ** (-zoom) / 111139

    # Calculate lat/lon span
    lat_span = (
        (map_height / 2) * meters_per_pixel / 111139
    )  # Rough degrees per meter for latitude
    lon_span = (
        (map_width / 2)
        * meters_per_pixel
        / (111139 * 2.71828182846 ** (center[0] * 3.14159 / 180))
    )  # Adjusted for longitude

    return ViewportBounds(
        north=center[0] + lat_span,
        south=center[0] - lat_span,
        east=center[1] + lon_span,
        west=center[1] - lon_span,
        zoom=zoom,
    )
