"""
Test script to check for duplicate callback errors in the app.
"""

import logging
import sys
import dash

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

    # Create app
    logging.info("Creating app...")
    app = create_app_with_duplicate_callbacks()

    # Register callbacks
    logging.info("Registering callbacks...")
    register_callbacks(app)

    # Analyze callback registry directly
    logging.info("Analyzing callback registry...")

    # Track outputs by component_id and property
    output_registry = {}

    for pattern, callback in app.callback_map.items():
        # Extract outputs from the callback
        if hasattr(callback, "callback"):
            outputs = callback.callback.outputs
            for output in outputs:
                component_id = output.component_id
                component_property = output.component_property
                output_key = f"{component_id}.{component_property}"

                # Track outputs with allow_duplicate=True separately
                if hasattr(output, "allow_duplicate") and output.allow_duplicate:
                    logging.info(f"Output with allow_duplicate=True: {output_key}")
                    continue

                # Add to registry or mark as duplicate
                if output_key in output_registry:
                    output_registry[output_key].append(pattern)
                else:
                    output_registry[output_key] = [pattern]

    # Check for duplicates
    duplicates = {k: v for k, v in output_registry.items() if len(v) > 1}

    logging.info(f"Total callbacks: {len(app.callback_map)}")
    logging.info(f"Unique outputs: {len(output_registry)}")

    if duplicates:
        logging.warning(f"Found {len(duplicates)} duplicate outputs:")
        for output_key, patterns in duplicates.items():
            logging.warning(f"  {output_key}: {len(patterns)} callbacks")
            for pattern in patterns:
                logging.warning(f"    - {pattern}")
    else:
        logging.info("No duplicate outputs found! 🎉")

    logging.info("Test completed successfully")

except Exception as e:
    logging.error(f"Error during test: {e}")
