"""
Simple script to find callbacks that have the specific output ID
"""

import importlib
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

# Import the app factory
try:
    from app_factory import create_app_with_duplicate_callbacks
except ImportError:
    print("Could not import app_factory")
    sys.exit(1)

# Create the app
app = create_app_with_duplicate_callbacks()

# Import the callbacks module
try:
    from callbacks_split import register_callbacks

    register_callbacks(app)
except ImportError:
    print("Could not import callbacks_split")
    sys.exit(1)

# Register any callbacks from app.py
try:
    import app as app_module
except ImportError:
    print("Could not import app")
    # Continue as we already have the app instance

print("Checking callbacks...")

# Count the total number of callbacks
print(f"Number of callbacks: {len(app.callback_map)}")

# List all callbacks that output to borehole-map.center
center_callbacks = []

for pattern, callback_info in app.callback_map.items():
    if hasattr(callback_info, "callback"):
        callback = callback_info.callback
        if hasattr(callback, "outputs"):
            for output in callback.outputs:
                if (
                    output.component_id == "borehole-map"
                    and output.component_property == "center"
                ):
                    center_callbacks.append(
                        {
                            "pattern": pattern,
                            "allow_duplicate": getattr(
                                output, "allow_duplicate", False
                            ),
                            "prevent_initial_call": getattr(
                                callback, "prevent_initial_call", False
                            ),
                        }
                    )
                    print(f"  Callback ID: {pattern}")

print(f"Total callbacks: {len(app.callback_map)}")
print(f"Callbacks targeting borehole-map.center: {len(center_callbacks)}")

if center_callbacks:
    print("\nDetails of callbacks targeting borehole-map.center:")
    for i, cb in enumerate(center_callbacks, 1):
        print(f"{i}. Pattern: {cb['pattern']}")
        print(f"   allow_duplicate: {cb['allow_duplicate']}")
        print(f"   prevent_initial_call: {cb['prevent_initial_call']}")
