#!/usr/bin/env python3
"""
Run the app and capture debug output for polyline selection issue
"""

import subprocess
import sys
import os
import time


def run_app_debug():
    """Run the app and capture debug output"""

    # Change to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    print("Starting app with debug logging...")
    print("Upload a file and draw a polyline to test the selection.")
    print("Check the app_debug.log file for detailed logging.")
    print("Press Ctrl+C to stop the app.")

    try:
        # Start the app
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Print output in real-time
        for line in iter(process.stdout.readline, ""):
            print(line, end="")

    except KeyboardInterrupt:
        print("\nStopping app...")
        process.terminate()
        process.wait()

    except Exception as e:
        print(f"Error running app: {e}")

    finally:
        if "process" in locals():
            process.terminate()


if __name__ == "__main__":
    run_app_debug()
