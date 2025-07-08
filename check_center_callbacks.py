"""
Check specifically for duplicate callbacks for borehole-map.center
"""

import logging
import sys
from dash import Output, Input, State

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# Import the app factory
from app_factory import create_app_with_duplicate_callbacks

app = create_app_with_duplicate_callbacks()

# Register callbacks
from callbacks_split import register_callbacks

register_callbacks(app)

# Import app.py callback registrations
from app import store_upload_data

# Print info about callbacks targeting borehole-map.center
center_outputs = []

print("Checking callbacks for borehole-map.center...")

for pattern, callback_info in app.callback_map.items():
    callback = getattr(callback_info, "callback", None)
    if callback:
        outputs = getattr(callback, "outputs", [])
        for output in outputs:
            if (
                output.component_id == "borehole-map"
                and output.component_property == "center"
            ):
                allow_duplicate = getattr(output, "allow_duplicate", False)
                prevent_initial_call = getattr(callback, "prevent_initial_call", False)

                center_outputs.append(
                    {
                        "pattern": pattern,
                        "allow_duplicate": allow_duplicate,
                        "prevent_initial_call": prevent_initial_call,
                    }
                )

                print(f"Found callback targeting borehole-map.center:")
                print(f"  Pattern: {pattern}")
                print(f"  allow_duplicate: {allow_duplicate}")
                print(f"  prevent_initial_call: {prevent_initial_call}")
                print()

print(f"Total callbacks targeting borehole-map.center: {len(center_outputs)}")

# Create a test output to borehole-map.center to see if it causes an error
print("\nTesting a new callback targeting borehole-map.center...")

try:

    @app.callback(
        Output("borehole-map", "center"),
        Input("borehole-data-store", "data"),
    )
    def test_center_callback(data):
        return [51.5, -0.1]

    print("✅ No error when registering a new callback for borehole-map.center")
except Exception as e:
    print(f"❌ Error when registering a new callback: {str(e)}")
