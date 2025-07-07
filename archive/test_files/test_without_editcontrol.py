#!/usr/bin/env python3
"""
Test the app without EditControl to isolate the issue
"""

print("=== TESTING APP WITHOUT EDITCONTROL ===")
print("This will help us determine if the issue is:")
print("1. EditControl compatibility with dash-leaflet 1.1.3")
print("2. General app configuration issue")
print("3. Other component conflicts")
print()
print("Expected behavior:")
print("- App should load without errors")
print("- Map should display properly")
print("- File upload should work")
print("- Borehole markers should appear after upload")
print()
print("If this works, the issue is specifically with EditControl.")
print("If this fails, the issue is broader.")
print()

import subprocess
import sys

try:
    # Run the main app
    print("Starting main app...")
    subprocess.run([sys.executable, "app.py"], check=True)
except KeyboardInterrupt:
    print("\nApp stopped by user")
except Exception as e:
    print(f"Error running app: {e}")
