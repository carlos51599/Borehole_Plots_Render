"""
Main Dash application entry point - Modular Version

This is a refactored version of the main application that uses modular components
from the app_modules package for better maintainability and file size management.

This file maintains full backward compatibility with the original app.py while
providing a clean, modular structure that follows best practices.
"""

# Configure matplotlib backend BEFORE any other imports that might use matplotlib
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for server environments

# Third-party imports
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Configure Sentry before app initialization
sentry_sdk.init(
    dsn="https://74e17ca3be6e1f11a9c3415ee132a6d7@o4509734367395840.ingest.de.sentry.io/4509734463144016",
    integrations=[
        FlaskIntegration(transaction_style="endpoint"),
        LoggingIntegration(
            level=None,  # Capture logs from all levels
            event_level=30,  # Send logs with level INFO or above as events
        ),
    ],
    # Performance monitoring - sample 100% of transactions for development
    traces_sample_rate=1.0,
    # Add data like request headers and IP for users
    send_default_pii=True,
    # Session tracking
    auto_session_tracking=True,
    # Environment tag
    environment="development",  # Change to "production" when deploying
    # Release tracking (optional - use your versioning scheme)
    release="geo-borehole-render@1.0.0",
)

# Local imports (after Sentry initialization)
from app_modules import get_app, main

# Get the application instance using the singleton pattern to prevent duplicate registrations
app = get_app()

# Main execution block - runs when script is executed directly
if __name__ == "__main__":
    main()
