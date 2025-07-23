"""
Application configuration and setup module.

This module handles all the initialization logic for the Dash application,
including logging configuration, app creation, and startup procedures.
"""

import dash
import dash_leaflet as dl
import logging
import sys
import webbrowser
from datetime import datetime

from app_factory import create_app_with_duplicate_callbacks


def setup_logging(logfile="app_debug.log"):
    """
    Configure enhanced logging for the application.

    Args:
        logfile (str): Path to the log file

    Returns:
        logging.Logger: Configured root logger
    """
    # Set up enhanced logging format with detailed context for debugging and monitoring
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d %(funcName)s] %(message)s",
        handlers=[
            logging.FileHandler(logfile, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),  # Also log to console
        ],
    )

    # Create root logger and make it extremely verbose
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # OPTIMIZATION: Reduce matplotlib logging verbosity to improve performance
    # This addresses the 538 font manager debug lines found in baseline testing
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.pyplot").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(
        logging.INFO
    )  # Keep INFO level for other matplotlib logs

    # Log app startup
    logging.info(f"App starting at {datetime.now()}")
    logging.info(f"Dash version: {dash.__version__}")
    logging.info(f"Dash-leaflet version: {dl.__version__}")
    logging.info("✓ Matplotlib logging optimized for performance")

    return root_logger


def create_application():
    """
    Create and configure the Dash application.

    Returns:
        dash.Dash: Configured Dash application instance
    """
    # Create the Dash app using the factory function for proper duplicate callback handling
    app = create_app_with_duplicate_callbacks()

    logging.info("Dash application created successfully")
    return app


def log_layout_ids(component, prefix=""):
    """
    Recursively log all component IDs in the layout for debugging purposes.

    This function traverses the entire Dash layout tree and logs each component's ID
    to help with debugging callback connections and component identification.

    Args:
        component: Dash component to inspect (html.Div, dcc.Graph, etc.)
        prefix (str): Indentation prefix for nested components (default: "")

    Returns:
        None: Function logs to the configured logger

    Note:
        Used during app startup to verify all components have proper IDs for callbacks
    """
    try:
        if hasattr(component, "id") and component.id:
            logging.info(f"Found component ID: {component.id}")
        if hasattr(component, "children"):
            if isinstance(component.children, list):
                for child in component.children:
                    log_layout_ids(child, prefix + "  ")
            elif component.children is not None:
                log_layout_ids(component.children, prefix + "  ")
    except Exception as e:
        logging.warning(f"Error inspecting component: {e}")


def start_application(app, debug=True, host="0.0.0.0", port=8050, open_browser=True):
    """
    Start the Dash application server.

    Args:
        app (dash.Dash): The Dash application instance
        debug (bool): Whether to run in debug mode
        host (str): Host to bind the server to
        port (int): Port to run the server on
        open_browser (bool): Whether to automatically open the browser
    """
    try:
        if open_browser:
            logging.info(f"Opening browser and starting Dash server on {host}:{port}")
            webbrowser.open(f"http://127.0.0.1:{port}/")
        else:
            logging.info(f"Starting Dash server on {host}:{port}")

        app.run(debug=debug, host=host, port=port)
    except Exception as e:
        logging.error(f"Error starting app: {str(e)}")
        print(f"Error: {str(e)}")
        raise
