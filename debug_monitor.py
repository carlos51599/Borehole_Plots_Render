#!/usr/bin/env python3
"""
Simple script to check if drawing operations are being triggered
"""

import time
import os
import sys


def monitor_logs():
    """Monitor for drawing operations in the app"""
    print("=== DASH APP DRAWING MONITOR ===")
    print("Start the Dash app in another terminal and draw shapes on the map.")
    print("This script will monitor for drawing operations...")
    print("Press Ctrl+C to stop.")
    print()

    # Check if app is likely running by looking for log file
    log_file = "app_debug.log"

    last_size = 0
    drawing_detected = False

    try:
        while True:
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                if current_size > last_size:
                    # New log entries
                    try:
                        with open(log_file, "r", encoding="utf-8") as f:
                            f.seek(last_size)
                            new_content = f.read()

                            # Look for drawing indicators
                            if "PROCESSING DRAWN SHAPE" in new_content:
                                print("🎯 DRAWING OPERATION DETECTED!")
                                drawing_detected = True

                            if "No boreholes found in drawn area" in new_content:
                                print("❌ NO BOREHOLES FOUND")

                            if (
                                "Selected" in new_content
                                and "boreholes:" in new_content
                            ):
                                print("✅ BOREHOLES FOUND AND SELECTED")

                            if "filter_selection_by_shape" in new_content:
                                print("🔍 Filtering operation in progress...")

                            # Print recent log lines for debugging
                            lines = new_content.strip().split("\n")
                            for line in lines[-10:]:  # Last 10 lines
                                if line.strip():
                                    print(f"LOG: {line}")

                    except Exception as e:
                        print(f"Error reading log: {e}")

                    last_size = current_size
                else:
                    if not drawing_detected:
                        print(".", end="", flush=True)  # Progress indicator
            else:
                print("⚠️  Log file not found - is the app running?")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n=== MONITORING STOPPED ===")
        if drawing_detected:
            print("✓ Drawing operations were detected during monitoring.")
        else:
            print("⚠️  No drawing operations detected.")
            print("Make sure to:")
            print("1. Upload an AGS file first")
            print("2. Draw shapes (rectangles, polygons) on the map around the markers")

        # Show last few log lines
        if os.path.exists(log_file):
            print("\nLast few log entries:")
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-20:]:  # Last 20 lines
                        print(f"  {line.rstrip()}")
            except Exception as e:
                print(f"Could not read log file: {e}")


def check_current_state():
    """Check current state of files and logs"""
    print("=== CURRENT STATE CHECK ===")

    # Check if log file exists and has content
    log_file = "app_debug.log"
    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        print(f"✓ Log file exists: {log_file} ({size} bytes)")

        if size > 0:
            # Show last few lines
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    print(f"Log has {len(lines)} lines. Last 5 lines:")
                    for line in lines[-5:]:
                        print(f"  {line.rstrip()}")
            except Exception as e:
                print(f"Could not read log file: {e}")
        else:
            print("Log file is empty - app may not be running")
    else:
        print("❌ Log file not found - app is not running")

    # Check for app.py
    if os.path.exists("app.py"):
        print("✓ app.py found")
    else:
        print("❌ app.py not found")

    print()


if __name__ == "__main__":
    check_current_state()

    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_logs()
    else:
        print("Usage:")
        print("  python debug_monitor.py           - Check current state")
        print("  python debug_monitor.py monitor   - Monitor for drawing operations")
        print()
        print("To monitor drawing operations:")
        print("1. Start the Dash app: python app.py")
        print("2. In another terminal: python debug_monitor.py monitor")
        print("3. Use the app and draw shapes on the map")
