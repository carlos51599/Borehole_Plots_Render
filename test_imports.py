"""
Test script to identify imports and potential issues.
"""

import sys
import os
import inspect

# Get the current path
current_path = os.path.dirname(os.path.abspath(__file__))
print(f"Current path: {current_path}")

# Add the current path to sys.path
sys.path.insert(0, current_path)
print(f"Python path: {sys.path}")

# Import our app
print("Importing app module...")
import app

print("\nModule globals in app:")
for name, obj in inspect.getmembers(app):
    if not name.startswith("__"):
        print(f"  {name}: {type(obj)}")

print("\nImported modules:")
for name, module in sys.modules.items():
    if "app" in name or "callback" in name:
        print(f"  {name}")

print("\nTesting app import...")
print(f"App object type: {type(app.app)}")
print(f"App has layout: {hasattr(app.app, 'layout')}")

# Now check what callbacks are registered
print("\nChecking callbacks...")
callbacks = getattr(app.app, "callback_map", {})
print(f"Number of callbacks: {len(callbacks)}")

for i, (callback_id, callback_info) in enumerate(callbacks.items()):
    if i < 5:  # Just show the first 5 to avoid too much output
        print(f"  Callback ID: {callback_id}")
        if hasattr(callback_info, "callback"):
            callback_func = callback_info.callback
            if hasattr(callback_func, "__module__"):
                print(f"    Module: {callback_func.__module__}")
            if hasattr(callback_func, "__name__"):
                print(f"    Name: {callback_func.__name__}")

print(f"Total callbacks: {len(callbacks)}")
