import sys
import traceback
from datetime import datetime

# First, set up a simple error capture mechanism before anything else
startup_error_file = "startup_errors.log"
try:
    with open(startup_error_file, "w") as f:
        f.write(f"Starting app at {datetime.now()}\n")
except Exception as e:
    print(f"Cannot write to {startup_error_file}: {str(e)}")

try:
    # Import all dependencies with error handling
    try:
        import dash
        from dash import html, dcc, Output, Input, State
        from dash.dependencies import ALL

        with open(startup_error_file, "a") as f:
            f.write("Dash imports successful\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(f"ERROR importing Dash: {str(e)}\n{traceback.format_exc()}\n")
        raise

    try:
        import dash_leaflet as dl
        from dash_leaflet import EditControl

        with open(startup_error_file, "a") as f:
            f.write("Dash Leaflet imports successful\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(
                f"ERROR importing Dash Leaflet: {str(e)}\n{traceback.format_exc()}\n"
            )
        raise

    try:
        import base64
        import io
        import json
        import logging
        import webbrowser

        with open(startup_error_file, "a") as f:
            f.write("Standard library imports successful\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(
                f"ERROR importing standard libraries: {str(e)}\n{traceback.format_exc()}\n"
            )
        raise

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with open(startup_error_file, "a") as f:
            f.write("Matplotlib imports successful\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(f"ERROR importing Matplotlib: {str(e)}\n{traceback.format_exc()}\n")
        raise

    try:
        # Now import our custom modules
        from data_loader import load_all_loca_data
        from section_plot import plot_section_from_ags_content
        from borehole_log import plot_borehole_log_from_ags_content
        from map_utils import filter_selection_by_shape

        with open(startup_error_file, "a") as f:
            f.write("Custom module imports successful\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(
                f"ERROR importing custom modules: {str(e)}\n{traceback.format_exc()}\n"
            )
        raise

    # Set up enhanced logging format with detailed context
    try:
        logfile = "app_debug.log"
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d %(funcName)s] %(message)s",
            handlers=[logging.FileHandler(logfile, mode="w", encoding="utf-8")],
        )

        # Create root logger and make it extremely verbose
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Log app startup
        logging.info(f"App starting at {datetime.now()}")

        with open(startup_error_file, "a") as f:
            f.write("Logging setup successful\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(f"ERROR setting up logging: {str(e)}\n{traceback.format_exc()}\n")
        raise

    # Create the Dash app
    try:
        app = dash.Dash(__name__, suppress_callback_exceptions=True)
        with open(startup_error_file, "a") as f:
            f.write("Dash app instance created\n")
    except Exception as e:
        with open(startup_error_file, "a") as f:
            f.write(f"ERROR creating Dash app: {str(e)}\n{traceback.format_exc()}\n")
        raise

    # Import the rest of your app.py file here
    # Continue with app.layout and callbacks

    def clear_log_files():
        """Clear log files at startup to make debugging easier"""
        log_files = ["app_debug.log", "upload_test.log"]
        for log_file in log_files:
            try:
                with open(log_file, "w") as f:
                    f.write(f"Log file cleared at {datetime.now()}\n")
                logging.info(f"Cleared log file: {log_file}")
            except Exception as e:
                print(f"Error clearing log file {log_file}: {str(e)}")
                with open(startup_error_file, "a") as f:
                    f.write(f"Error clearing log file {log_file}: {str(e)}\n")

    # Main execution
    if __name__ == "__main__":
        try:
            with open(startup_error_file, "a") as f:
                f.write("Starting main execution\n")

            # Clear log files
            clear_log_files()

            # Open browser and run app
            logging.info("Opening browser and starting Dash server")
            with open(startup_error_file, "a") as f:
                f.write("About to open browser\n")

            webbrowser.open("http://127.0.0.1:8050/")

            with open(startup_error_file, "a") as f:
                f.write("About to run Dash app\n")

            app.run(debug=True)

        except Exception as e:
            error_msg = f"ERROR in main execution: {str(e)}\n{traceback.format_exc()}\n"
            logging.error(error_msg)
            print(error_msg)
            with open(startup_error_file, "a") as f:
                f.write(error_msg)

except Exception as e:
    # Catch-all for any errors not caught above
    error_msg = f"FATAL ERROR: {str(e)}\n{traceback.format_exc()}\n"
    print(error_msg)
    try:
        with open(startup_error_file, "a") as f:
            f.write(error_msg)
    except:
        pass
