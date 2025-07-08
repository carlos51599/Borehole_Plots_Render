"""
Helper module for dealing with duplicate callbacks.
This file should be imported before any other file that contains callbacks.
"""

import dash


# Define a special function to set up an app with proper duplicate callback handling
def create_app_with_duplicate_callbacks():
    """
    Create a Dash app with settings to handle duplicate callbacks properly.
    """
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        prevent_initial_callbacks="initial_duplicate",  # Allow duplicate callbacks with initial call
    )
    return app
