"""
Main Dash application entry point - Modular Version

This is a refactored version of the main application that uses modular components
from the app_modules package for better maintainability and file size management.

This file maintains full backward compatibility with the original app.py while
providing a clean, modular structure that follows best practices.
"""

from app_modules import create_and_configure_app, main

# Create the application using the modular factory function
app = create_and_configure_app()

# Main execution block - runs when script is executed directly
if __name__ == "__main__":
    main()
