#!/usr/bin/env python3
"""
Debug script to check app components and diagnose issues
"""

import sys
import os
from pathlib import Path


def check_requirements():
    """Check if all required packages are available"""
    print("=== Checking Requirements ===")

    required_packages = [
        "dash",
        "dash_leaflet",
        "pandas",
        "matplotlib",
        "pyproj",
        "shapely",
        "base64",
        "io",
        "logging",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\nMissing packages: {missing}")
        print("Install with: pip install " + " ".join(missing))
        return False
    else:
        print("✓ All required packages available")
        return True


def check_files():
    """Check if all required files exist"""
    print("\n=== Checking Files ===")

    required_files = [
        "app.py",
        "map_utils.py",
        "data_loader.py",
        "section_plot.py",
        "borehole_log.py",
        "requirements.txt",
    ]

    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            missing.append(file)

    if missing:
        print(f"\nMissing files: {missing}")
        return False
    else:
        print("✓ All required files present")
        return True


def check_imports():
    """Test importing our custom modules"""
    print("\n=== Testing Module Imports ===")

    try:
        from data_loader import load_all_loca_data

        print("✓ data_loader.load_all_loca_data")
    except Exception as e:
        print(f"✗ data_loader error: {e}")
        return False

    try:
        from map_utils import filter_selection_by_shape

        print("✓ map_utils.filter_selection_by_shape")
    except Exception as e:
        print(f"✗ map_utils error: {e}")
        return False

    try:
        from section_plot import plot_section_from_ags_content

        print("✓ section_plot.plot_section_from_ags_content")
    except Exception as e:
        print(f"✗ section_plot error: {e}")
        return False

    try:
        from borehole_log import plot_borehole_log_from_ags_content

        print("✓ borehole_log.plot_borehole_log_from_ags_content")
    except Exception as e:
        print(f"✗ borehole_log error: {e}")
        return False

    print("✓ All module imports successful")
    return True


def run_coordinate_test():
    """Test coordinate transformation"""
    print("\n=== Testing Coordinate Transformation ===")

    try:
        from pyproj import Transformer

        transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

        # Test with London coordinates
        easting, northing = 529090, 181680  # Greenwich
        lon, lat = transformer.transform(easting, northing)

        print(
            f"Test transformation: BNG({easting}, {northing}) -> WGS84({lat:.6f}, {lon:.6f})"
        )

        if 49.0 <= lat <= 61.0 and -8.0 <= lon <= 2.0:
            print("✓ Coordinate transformation working correctly")
            return True
        else:
            print("✗ Transformed coordinates outside UK bounds")
            return False
    except Exception as e:
        print(f"✗ Coordinate transformation error: {e}")
        return False


def check_log_files():
    """Check for existing log files"""
    print("\n=== Checking Log Files ===")

    log_files = ["app_debug.log", "upload_test.log", "network_debug.log"]

    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✓ {log_file} exists ({size} bytes)")

            # Show last few lines if not too big
            if size < 10000:  # Less than 10KB
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if lines:
                            print(f"  Last line: {lines[-1].strip()}")
                except Exception as e:
                    print(f"  Could not read {log_file}: {e}")
        else:
            print(f"- {log_file} not found")


def main():
    """Run all diagnostic checks"""
    print("=== DASH APP DIAGNOSTIC ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    all_good = True

    all_good &= check_requirements()
    all_good &= check_files()
    all_good &= check_imports()
    all_good &= run_coordinate_test()
    check_log_files()

    print("\n=== SUMMARY ===")
    if all_good:
        print("✓ All checks passed - app should work correctly")
        print("\nTo run the app:")
        print("  python app.py")
        print("\nThen open: http://127.0.0.1:8050")
    else:
        print("✗ Some issues found - fix these before running the app")

    return all_good


if __name__ == "__main__":
    main()
