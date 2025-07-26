"""
Main Dash application entry point - Modular Version

Refactored for modularity and maintainability. Uses components from app_modules.
Maintains backward compatibility with the original app.py.
"""

import sentry_sdk
from app_modules import create_and_configure_app, main

sentry_sdk.init(
    dsn="https://74e17ca3be6e1f11a9c3415ee132a6d7@o4509734367395840.ingest.de.sentry.io/4509734463144016",
    send_default_pii=True,
)

# Create the application using the modular factory function
app = create_and_configure_app()

# Attach Sentry test route to underlying Flask server
server = app.server


# Sentry test route for error verification
@server.route("/sentry-test")
def sentry_test():
    """Route to test Sentry error reporting by raising ZeroDivisionError."""
    1 / 0  # This will raise a ZeroDivisionError and send it to Sentry
    return "<p>Sentry test route</p>"


# Main execution block - runs when script is executed directly
if __name__ == "__main__":
    main()
