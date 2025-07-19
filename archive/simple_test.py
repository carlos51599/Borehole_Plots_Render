"""
A simpler test script to check for duplicate callbacks for specific outputs.
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logging.info("Starting test...")

try:
    # Import the app without running it
    from app_factory import create_app_with_duplicate_callbacks
    from callbacks_split import register_callbacks
    import dash

    # Create app
    app = create_app_with_duplicate_callbacks()

    # Register callbacks
    register_callbacks(app)

    # Add file upload store callback
    @app.callback(
        dash.Output("upload-data-store", "data"),
        dash.Input("upload-ags", "contents"),
        dash.State("upload-ags", "filename"),
    )
    def store_upload_data(contents, filenames):
        return None

    # Create layout with test component
    app.layout = dash.html.Div(
        [
            dash.html.Button("Test", id="test-button"),
            dash.dcc.Input(id="test-input", value=""),
            dash.dcc.Store(id="upload-data-store"),
            dash.dcc.Store(id="borehole-data-store"),
            dash.dcc.Store(id="draw-state-store"),
        ]
    )

    # Run app in test mode to check for errors
    logging.info("Starting app in test mode...")
    app.run(
        debug=True,
        port=8765,
        host="127.0.0.1",
        dev_tools_hot_reload=False,
        use_reloader=False,
    )

except Exception as e:
    logging.error(f"Error during test: {e}")
    import traceback

    traceback.print_exc()
