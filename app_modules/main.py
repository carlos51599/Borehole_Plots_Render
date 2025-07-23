"""
Main application module integration.

This module provides the main interface that coordinates all the modular components
for the Dash application, maintaining backward compatibility.
"""

import logging
from callbacks import register_callbacks
from .app_setup import (
    setup_logging,
    create_application,
    log_layout_ids,
    start_application,
)
from .layout import create_complete_layout
from .clientside_callbacks import register_all_clientside_callbacks
from .server_callbacks import register_all_server_callbacks


def create_and_configure_app(logfile="app_debug.log"):
    """
    Create and configure the complete Dash application.

    Args:
        logfile (str): Path to the log file

    Returns:
        dash.Dash: Fully configured Dash application
    """
    # Setup logging
    setup_logging(logfile)

    # Create application
    app = create_application()

    # Create and assign layout
    logging.info("Creating app layout...")
    app.layout = create_complete_layout()
    logging.info("App layout created successfully")

    # Log all IDs in the layout for debugging
    logging.info("=== LAYOUT COMPONENT IDs ===")
    log_layout_ids(app.layout)
    logging.info("=== END LAYOUT IDs ===")

    # Register clientside callbacks
    register_all_clientside_callbacks(app)

    # Register server-side callbacks
    register_all_server_callbacks(app)

    # Register modular callbacks from the callbacks package
    logging.info("Registering split callbacks...")
    register_callbacks(app)
    logging.info("✅ All callbacks registered successfully!")

    return app


# For backward compatibility - maintain the same interface as the original app.py
def main():
    """
    Main execution function for running the application.
    """
    app = create_and_configure_app()
    start_application(app)


# Expose the app variable for import compatibility
app = None


def get_app():
    """
    Get or create the application instance.

    Returns:
        dash.Dash: Application instance
    """
    global app
    if app is None:
        app = create_and_configure_app()
    return app
