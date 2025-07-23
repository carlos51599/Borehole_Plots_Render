"""
App Modules Package

Modular structure for the main Dash application, providing clean separation
of concerns for layout, callbacks, and configuration.

Main Functions:
    create_and_configure_app: Main application factory function
    main: Main execution function for standalone running
    get_app: Get or create application instance

Modules:
    app_setup: Application initialization and configuration
    layout: Complete application layout components
    clientside_callbacks: Browser-side callbacks for performance
    server_callbacks: Server-side data processing callbacks
    main: Main application integration and coordination
"""

# Import main functions for easy access
from .main import create_and_configure_app, main, get_app

# Re-export for backward compatibility
create_app = create_and_configure_app

__all__ = [
    "create_and_configure_app",
    "create_app",  # Legacy alias
    "main",
    "get_app",
]

__version__ = "1.0.0"
__author__ = "Geological Cross-Section Renderer"
