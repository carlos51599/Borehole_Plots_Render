"""
Professional borehole log plotting module matching Openground style standards.

This module creates professional borehole logs with separate columns for
lithology, depth, and layer description using color and hatch patterns
from CSV geology code mapping with Openground-style formatting and layout.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import logging
from typing import Optional, Tuple

# Import shared geology code mapping utility
from geology_code_utils import load_geology_code_mappings

# Configure matplotlib for professional rendering
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.linewidth"] = 0.5
plt.rcParams["lines.linewidth"] = 1.0

logger = logging.getLogger(__name__)


def plot_borehole_log_from_ags_content(
    ags_content,
    loca_id,
    show_labels=True,
    fig_height=11.69,
    fig_width=4.0,
    geology_csv_path=None,
    title=None,
    dpi=300,
):
    """
    Parse AGS content and plot a professional borehole log for the given borehole ID.

    Args:
        ags_content: AGS file content as string
        loca_id: Borehole ID to plot
        show_labels: (compatibility, not used)
        fig_height: Figure height in inches (default A4 portrait)
        fig_width: Figure width in inches
        geology_csv_path: Path to geology code mapping CSV
        title: Optional plot title
        dpi: Figure DPI

    Returns:
        matplotlib Figure object, or None if no data found
    """
    try:
        # Import parser from section_plot_professional (shared logic)
        from section_plot_professional import parse_ags_geol_section_from_string
    except ImportError as e:
        logger.error(f"Failed to import section_plot_professional: {e}")
        return None

    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)
    geol_bh = geol_df[geol_df["LOCA_ID"] == loca_id]
    if geol_bh.empty:
        return None

    # Use GEOL_DESC if available, else fallback to empty string
    desc_col = "GEOL_DESC" if "GEOL_DESC" in geol_bh.columns else None

    # Build DataFrame for professional plotting
    borehole_data = pd.DataFrame(
        {
            "Depth_Top": geol_bh["GEOL_TOP"].astype(float),
            "Depth_Base": geol_bh["GEOL_BASE"].astype(float),
            "Geology_Code": geol_bh["GEOL_LEG"],
            "Description": (
                geol_bh[desc_col] if desc_col else ["" for _ in range(len(geol_bh))]
            ),
        }
    )

    # Sort by top depth
    borehole_data = borehole_data.sort_values("Depth_Top").reset_index(drop=True)

    # Use the professional plotting function
    fig = create_professional_borehole_log(
        borehole_data=borehole_data,
        borehole_id=loca_id,
        geology_csv_path=geology_csv_path,
        title=title,
        figsize=(fig_width, fig_height),
        dpi=dpi,
    )
    return fig


class ProfessionalBoreholeLog:
    """Professional borehole log plotter with Openground-style formatting."""

    def __init__(self, geology_csv_path: Optional[str] = None):
        """
        Initialize the professional borehole log plotter.

        Args:
            geology_csv_path: Path to CSV file containing geology code mappings
        """
        self.geology_mapping = {}
        if geology_csv_path:
            try:
                self.geology_mapping = load_geology_code_mappings(geology_csv_path)
                logger.info(
                    f"Loaded {len(self.geology_mapping)} geology codes from {geology_csv_path}"
                )
            except Exception as e:
                logger.error(f"Failed to load geology mapping: {e}")

    def create_borehole_log(
        self,
        borehole_data: pd.DataFrame,
        borehole_id: str,
        title: Optional[str] = None,
        figsize: Tuple[float, float] = (8.27, 11.69),
        dpi: int = 300,
    ) -> plt.Figure:
        """
        Create a professional borehole log plot.

        Args:
            borehole_data: DataFrame with columns including 'Depth_Top', 'Depth_Base',
                          'Geology_Code', 'Description'
            borehole_id: Identifier for the borehole
            title: Optional title for the plot
            figsize: Figure size (width, height) in inches
            dpi: Resolution for the plot

        Returns:
            matplotlib Figure object
        """
        logger.info(f"Creating professional borehole log for {borehole_id}")

        # Create figure and subplots
        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor="white")

        # Define column layout (similar to Openground style)
        # Depth | Lithology | Description columns
        depth_width = 0.15  # Depth column
        litho_width = 0.25  # Lithology column (visual representation)
        desc_width = 0.55  # Description column
        margin = 0.025  # Small margins

        # Calculate positions
        depth_left = margin
        litho_left = depth_left + depth_width + margin
        desc_left = litho_left + litho_width + margin

        # Create subplots for each column
        ax_depth = fig.add_axes([depth_left, 0.1, depth_width, 0.8])
        ax_litho = fig.add_axes([litho_left, 0.1, litho_width, 0.8])
        ax_desc = fig.add_axes([desc_left, 0.1, desc_width, 0.8])

        # Get depth range
        if borehole_data.empty:
            logger.warning(f"No data available for borehole {borehole_id}")
            return fig

        max_depth = borehole_data["Depth_Base"].max()
        min_depth = borehole_data["Depth_Top"].min()

        # Plot each column
        self._plot_depth_column(ax_depth, borehole_data, min_depth, max_depth)
        self._plot_lithology_column(
            ax_litho, borehole_data, min_depth, max_depth, self.geology_mapping
        )
        self._plot_description_column(ax_desc, borehole_data, min_depth, max_depth)

        # Add title
        if title:
            fig.suptitle(title, fontsize=14, fontweight="bold", y=0.95)
        else:
            fig.suptitle(
                f"Borehole Log: {borehole_id}", fontsize=14, fontweight="bold", y=0.95
            )

        # Add column headers
        self._add_column_headers(
            fig, depth_left, litho_left, desc_left, depth_width, litho_width, desc_width
        )

        logger.info(f"Professional borehole log created for {borehole_id}")
        return fig

    def _plot_depth_column(
        self, ax, data: pd.DataFrame, min_depth: float, max_depth: float
    ):
        """Plot the depth column with professional formatting."""
        ax.set_xlim(0, 1)
        ax.set_ylim(max_depth, min_depth)  # Inverted Y-axis for depth

        # Add depth markers at layer boundaries
        depths = []
        for _, row in data.iterrows():
            depths.extend([row["Depth_Top"], row["Depth_Base"]])
        depths = sorted(set(depths))

        # Plot depth markers
        for depth in depths:
            ax.text(
                0.5,
                depth,
                f"{depth:.2f}m",
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
            )

        # Add horizontal lines at boundaries
        for depth in depths:
            ax.axhline(y=depth, color="black", linewidth=0.5, alpha=0.7)

        # Format axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["top"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["right"].set_visible(True)

        # Set spine properties
        for spine in ax.spines.values():
            spine.set_linewidth(1.0)
            spine.set_color("black")

    def _plot_lithology_column(
        self,
        ax,
        data: pd.DataFrame,
        min_depth: float,
        max_depth: float,
        geology_mapping: dict,
    ):
        """Plot the lithology column with colors and hatching."""
        ax.set_xlim(0, 1)
        ax.set_ylim(max_depth, min_depth)  # Inverted Y-axis for depth

        # Plot each geological layer
        for _, row in data.iterrows():
            top_depth = row["Depth_Top"]
            base_depth = row["Depth_Base"]
            geology_code = row.get("Geology_Code", "UNKNOWN")

            # Get color and hatch pattern from mapping
            layer_props = geology_mapping.get(
                geology_code, {"color": "#D3D3D3", "hatch": None}  # Light gray default
            )

            color = layer_props.get("color", "#D3D3D3")
            hatch = layer_props.get("hatch", None)

            # Create rectangle for the layer
            height = base_depth - top_depth
            rect = patches.Rectangle(
                (0, top_depth),
                1,
                height,
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
                hatch=hatch,
                alpha=0.8,
            )
            ax.add_patch(rect)

            # Add geology code text in center of layer
            mid_depth = (top_depth + base_depth) / 2
            if height > 0.5:  # Only add text if layer is thick enough
                ax.text(
                    0.5,
                    mid_depth,
                    geology_code,
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontweight="bold",
                    rotation=0,
                )

        # Format axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["top"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["right"].set_visible(True)

        # Set spine properties
        for spine in ax.spines.values():
            spine.set_linewidth(1.0)
            spine.set_color("black")

    def _plot_description_column(
        self, ax, data: pd.DataFrame, min_depth: float, max_depth: float
    ):
        """Plot the description column with text descriptions."""
        ax.set_xlim(0, 1)
        ax.set_ylim(max_depth, min_depth)  # Inverted Y-axis for depth

        # Plot descriptions for each layer
        for _, row in data.iterrows():
            top_depth = row["Depth_Top"]
            base_depth = row["Depth_Base"]
            description = row.get("Description", "No description available")

            # Calculate text position
            mid_depth = (top_depth + base_depth) / 2
            height = base_depth - top_depth

            # Adjust font size based on layer thickness
            if height > 2.0:
                fontsize = 9
            elif height > 1.0:
                fontsize = 8
            else:
                fontsize = 7

            # Word wrap for long descriptions
            wrapped_text = self._wrap_text(description, max_chars=40)

            # Add description text
            ax.text(
                0.05,
                mid_depth,
                wrapped_text,
                ha="left",
                va="center",
                fontsize=fontsize,
                wrap=True,
                verticalalignment="center",
            )

            # Add horizontal separator line
            ax.axhline(y=base_depth, color="gray", linewidth=0.3, alpha=0.5)

        # Format axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["top"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["right"].set_visible(True)

        # Set spine properties
        for spine in ax.spines.values():
            spine.set_linewidth(1.0)
            spine.set_color("black")

    def _add_column_headers(
        self,
        fig,
        depth_left: float,
        litho_left: float,
        desc_left: float,
        depth_width: float,
        litho_width: float,
        desc_width: float,
    ):
        """Add column headers to the plot."""
        header_y = 0.92
        header_fontsize = 12
        header_fontweight = "bold"

        # Depth column header
        fig.text(
            depth_left + depth_width / 2,
            header_y,
            "Depth (m)",
            ha="center",
            va="center",
            fontsize=header_fontsize,
            fontweight=header_fontweight,
        )

        # Lithology column header
        fig.text(
            litho_left + litho_width / 2,
            header_y,
            "Lithology",
            ha="center",
            va="center",
            fontsize=header_fontsize,
            fontweight=header_fontweight,
        )

        # Description column header
        fig.text(
            desc_left + desc_width / 2,
            header_y,
            "Description",
            ha="center",
            va="center",
            fontsize=header_fontsize,
            fontweight=header_fontweight,
        )

    def _wrap_text(self, text: str, max_chars: int = 40) -> str:
        """Simple text wrapping function."""
        if len(text) <= max_chars:
            return text

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)


def create_professional_borehole_log(
    borehole_data: pd.DataFrame,
    borehole_id: str,
    geology_csv_path: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8.27, 11.69),
    dpi: int = 300,
) -> plt.Figure:
    """
    Convenience function to create a professional borehole log plot.

    Args:
        borehole_data: DataFrame with geological layer data
        borehole_id: Identifier for the borehole
        geology_csv_path: Path to geology code mapping CSV
        title: Optional title for the plot
        figsize: Figure size (width, height) in inches
        dpi: Resolution for the plot

    Returns:
        matplotlib Figure object
    """
    plotter = ProfessionalBoreholeLog(geology_csv_path)
    return plotter.create_borehole_log(borehole_data, borehole_id, title, figsize, dpi)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create sample data
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.5, 3.0, 5.5, 8.0],
            "Depth_Base": [1.5, 3.0, 5.5, 8.0, 12.0],
            "Geology_Code": ["CLAY", "SAND", "GRAV", "CLAY", "ROCK"],
            "Description": [
                "Soft brown clay with occasional organic matter",
                "Medium dense fine to coarse sand",
                "Dense angular gravel with cobbles",
                "Stiff grey clay with limestone fragments",
                "Weathered limestone bedrock",
            ],
        }
    )

    # Create professional borehole log
    fig = create_professional_borehole_log(
        sample_data, "BH001", title="Example Professional Borehole Log"
    )

    plt.show()
