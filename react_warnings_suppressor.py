"""
React Lifecycle Warnings Suppression Utility

This module provides functionality to suppress React lifecycle deprecation warnings
that originate from third-party libraries (Dash/dash-leaflet) during development.

These warnings are cosmetic and do not affect application functionality.
They stem from underlying React components that haven't been updated to modern
lifecycle methods (componentWillMount, componentWillReceiveProps).

Usage:
    # Option 1: Import and initialize in app.py
    from react_warnings_suppressor import suppress_react_warnings
    suppress_react_warnings()

    # Option 2: Add JavaScript to assets/suppress_react_warnings.js
    # This will be automatically loaded by Dash
"""

import logging
import os

logger = logging.getLogger(__name__)


def create_warning_suppression_js():
    """
    Create a JavaScript file to suppress React lifecycle warnings in the browser.

    This creates an assets/suppress_react_warnings.js file that will be automatically
    loaded by Dash and suppress the componentWillMount/componentWillReceiveProps warnings.
    """

    # Ensure assets directory exists
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        logger.info("Created assets directory")

    js_content = """
// React Lifecycle Warnings Suppressor
// Suppresses deprecated lifecycle method warnings from third-party libraries

(function() {
    'use strict';
    
    // Store original console.warn function
    const originalConsoleWarn = console.warn;
    
    // Override console.warn to filter React lifecycle warnings
    console.warn = function(...args) {
        const message = args.join(' ');
        
        // Check if this is a React lifecycle warning we want to suppress
        const reactWarnings = [
            'componentWillMount has been renamed',
            'componentWillReceiveProps has been renamed',
            'componentWillUpdate has been renamed'
        ];
        
        // If it's a React lifecycle warning, suppress it
        for (const warning of reactWarnings) {
            if (message.includes(warning)) {
                // Optionally log to a different level for debugging
                // console.info('Suppressed React warning:', message);
                return;
            }
        }
        
        // For all other warnings, use the original console.warn
        originalConsoleWarn.apply(console, args);
    };
    
    console.info('React lifecycle warnings suppressor loaded');
})();
"""

    js_file_path = os.path.join(assets_dir, "suppress_react_warnings.js")

    try:
        with open(js_file_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        logger.info(f"Created React warnings suppression file: {js_file_path}")
        return js_file_path
    except Exception as e:
        logger.error(f"Failed to create suppression file: {e}")
        return None


def suppress_react_warnings(create_js_file=True):
    """
    Initialize React lifecycle warnings suppression.

    Args:
        create_js_file (bool): Whether to create the JavaScript suppression file

    Returns:
        str: Path to created JS file if successful, None otherwise
    """

    logger.info("Initializing React lifecycle warnings suppression")

    if create_js_file:
        js_file = create_warning_suppression_js()
        if js_file:
            logger.info("React warnings will be suppressed in browser console")
            return js_file
        else:
            logger.warning("Failed to create suppression file")
            return None

    logger.info("React warnings suppression initialized (no JS file created)")
    return None


def remove_suppression():
    """
    Remove the React warnings suppression file.

    Returns:
        bool: True if file was removed or didn't exist, False if removal failed
    """

    js_file_path = os.path.join("assets", "suppress_react_warnings.js")

    try:
        if os.path.exists(js_file_path):
            os.remove(js_file_path)
            logger.info(f"Removed React warnings suppression file: {js_file_path}")
        else:
            logger.info("React warnings suppression file doesn't exist")
        return True
    except Exception as e:
        logger.error(f"Failed to remove suppression file: {e}")
        return False


if __name__ == "__main__":
    # Direct execution - create the suppression file
    print("Creating React lifecycle warnings suppression...")

    result = suppress_react_warnings()
    if result:
        print(f"✓ Created suppression file: {result}")
        print("React lifecycle warnings will now be suppressed in the browser console.")
        print("\nTo remove suppression, run:")
        print("python react_warnings_suppressor.py --remove")
    else:
        print("✗ Failed to create suppression file")

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        print("\nRemoving React warnings suppression...")
        if remove_suppression():
            print("✓ Suppression removed")
        else:
            print("✗ Failed to remove suppression")
