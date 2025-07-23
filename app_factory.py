"""
Factory module for creating and configuring Dash application instances.

This module handles the creation of Dash applications with proper configuration
for handling duplicate callbacks, which can occur in complex applications with
multiple callback modules or dynamic component generation.

Key Features:
- Prevents callback conflicts in modular callback architecture
- Suppresses callback exceptions for dynamic component creation
- Configures proper initial callback handling

Purpose:
In complex Dash applications with split callback modules (like this project),
duplicate callback IDs can cause conflicts. This factory ensures the app is
properly configured to handle such scenarios.

Usage:
    from app_factory import create_app_with_duplicate_callbacks
    app = create_app_with_duplicate_callbacks()

Author: [Project Team]
Last Modified: July 2025
"""

import dash


def create_app_with_duplicate_callbacks():
    """
    Create a Dash app with settings to handle duplicate callbacks properly.

    This function creates and configures a Dash application instance with settings
    optimized for complex applications that may have:
    - Multiple callback modules
    - Dynamic component generation
    - Potential callback ID conflicts

    Configuration Details:
    - suppress_callback_exceptions=True: Allows callbacks to reference components
      that may not exist at app startup (useful for dynamic layouts)
    - prevent_initial_callbacks="initial_duplicate": Prevents duplicate callback
      execution during initial app load while still allowing legitimate duplicates

    Returns:
        dash.Dash: Configured Dash application instance ready for layout and callbacks

    Example:
        >>> app = create_app_with_duplicate_callbacks()
        >>> app.layout = html.Div(...)
        >>> # Register callbacks from multiple modules without conflicts
    """
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        prevent_initial_callbacks="initial_duplicate",  # Allow duplicate callbacks with initial call
    )
    return app
