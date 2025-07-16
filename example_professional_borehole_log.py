"""
Example script demonstrating how to use the professional borehole log module.

This script shows how to:
1. Load borehole data
2. Create professional borehole logs with geology code mapping
3. Save or display the results
"""

import pandas as pd
import matplotlib.pyplot as plt
from borehole_log_professional import create_professional_borehole_log
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_professional_borehole_log():
    """Demonstrate creating a professional borehole log."""

    # Create sample geological data
    sample_data = pd.DataFrame(
        {
            "Depth_Top": [0.0, 1.2, 2.8, 4.5, 7.2, 9.1],
            "Depth_Base": [1.2, 2.8, 4.5, 7.2, 9.1, 12.0],
            "Geology_Code": ["CLAY", "SAND", "GRAV", "CLAY", "ROCK", "LTST"],
            "Description": [
                "Soft brown clay with occasional organic matter and root fragments",
                "Medium dense fine to coarse sand, some silt, brown to grey",
                "Dense angular gravel with cobbles, some sand matrix",
                "Stiff grey clay with occasional limestone fragments",
                "Moderately weathered sandstone, closely fractured",
                "Slightly weathered limestone bedrock, widely fractured",
            ],
        }
    )

    logger.info("Sample data created with {} layers".format(len(sample_data)))

    try:
        # Create professional borehole log
        # Note: You can provide a path to your geology code CSV file
        fig = create_professional_borehole_log(
            borehole_data=sample_data,
            borehole_id="BH001",
            geology_csv_path=None,  # Will use default colors if no CSV provided
            title="Professional Borehole Log - Example Site",
            figsize=(8.27, 11.69),  # A4 size
            dpi=300,
        )

        logger.info("Professional borehole log created successfully")

        # Display the plot
        plt.tight_layout()
        plt.show()

        # Optionally save the plot
        fig.savefig("borehole_log_BH001.pdf", dpi=300, bbox_inches="tight")
        logger.info("Plot saved to borehole_log_BH001.pdf")

    except Exception as e:
        logger.error(f"Failed to create borehole log: {e}")
        raise


def load_and_plot_real_data(
    borehole_data_path: str, geology_csv_path: str, borehole_id: str
):
    """
    Load real borehole data and create a professional log.

    Args:
        borehole_data_path: Path to CSV file with borehole data
        geology_csv_path: Path to CSV file with geology code mappings
        borehole_id: ID of the borehole to plot
    """
    try:
        # Load borehole data
        data = pd.read_csv(borehole_data_path)
        logger.info(f"Loaded borehole data with {len(data)} records")

        # Filter for specific borehole if needed
        if "Borehole_ID" in data.columns:
            borehole_data = data[data["Borehole_ID"] == borehole_id].copy()
        else:
            borehole_data = data.copy()

        if borehole_data.empty:
            logger.warning(f"No data found for borehole {borehole_id}")
            return

        # Create professional log
        fig = create_professional_borehole_log(
            borehole_data=borehole_data,
            borehole_id=borehole_id,
            geology_csv_path=geology_csv_path,
            title=f"Professional Borehole Log - {borehole_id}",
            figsize=(8.27, 11.69),
            dpi=300,
        )

        # Display and save
        plt.show()

        # Save to file
        output_file = f"borehole_log_{borehole_id}_professional.pdf"
        fig.savefig(output_file, dpi=300, bbox_inches="tight")
        logger.info(f"Professional log saved to {output_file}")

    except Exception as e:
        logger.error(f"Failed to process real data: {e}")
        raise


if __name__ == "__main__":
    # Run demonstration
    demo_professional_borehole_log()

    # Uncomment and modify these lines to use with real data:
    # load_and_plot_real_data(
    #     borehole_data_path="path/to/your/borehole_data.csv",
    #     geology_csv_path="path/to/your/geology_codes.csv",
    #     borehole_id="BH001"
    # )
