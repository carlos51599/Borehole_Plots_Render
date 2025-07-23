"""
Server-side callback functions for data handling.

This module contains server-side callbacks that handle data processing,
state management, and other server-side operations.
"""

import dash
import logging


def store_upload_data(contents, filenames):
    """
    Store uploaded file data in a dcc.Store component for use across callbacks.

    This callback processes uploaded AGS files and stores their contents and filenames
    in a Dash Store component, making the data available to other callbacks without
    requiring re-upload or re-processing.

    Args:
        contents (list/str): Base64 encoded file contents from dcc.Upload
        filenames (list/str): Original filenames of uploaded files

    Returns:
        dict/None: Dictionary containing contents and filenames, or None if no upload

    Structure of returned data:
        {
            "contents": [base64_string1, base64_string2, ...],
            "filenames": ["file1.ags", "file2.ags", ...]
        }
    """
    if contents is None:
        logging.info("No upload data to store")
        return None

    try:
        logging.info("=== STORING UPLOAD DATA ===")
        if isinstance(contents, list):
            logging.info(f"Storing {len(contents)} files")
            return {"contents": contents, "filenames": filenames}
        else:
            logging.info("Storing single file")
            return {"contents": [contents], "filenames": [filenames]}
    except Exception as e:
        logging.error(f"Error storing upload data: {str(e)}")
        return None


def register_upload_callback(app):
    """
    Register the upload data store callback.

    Args:
        app (dash.Dash): The Dash application instance
    """

    @app.callback(
        dash.Output("upload-data-store", "data"),
        dash.Input("upload-ags", "contents"),
        dash.State("upload-ags", "filename"),
    )
    def _store_upload_data_callback(contents, filenames):
        return store_upload_data(contents, filenames)


def register_all_server_callbacks(app):
    """
    Register all server-side callbacks for the application.

    Args:
        app (dash.Dash): The Dash application instance
    """
    logging.info("Registering server-side callbacks...")

    register_upload_callback(app)

    logging.info("✅ All server-side callbacks registered successfully!")
