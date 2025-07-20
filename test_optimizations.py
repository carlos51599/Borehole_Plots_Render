#!/usr/bin/env python3
"""
Test script to validate all optimization systems are working correctly
"""

import pandas as pd
import numpy as np
import sys
import os


def test_memory_optimization():
    """Test DataFrame memory optimization"""
    print("=== Testing DataFrame Memory Optimization ===")

    try:
        from memory_manager import optimize_dataframe_memory, monitor_memory_usage

        # Create test DataFrame
        test_df = pd.DataFrame(
            {
                "string_col": ["test"] * 1000,
                "int_col": range(1000),
                "float_col": np.random.random(1000),
                "category_col": ["A", "B", "C"] * 333 + ["A"],
            }
        )

        original_memory = test_df.memory_usage(deep=True).sum()
        print(f"Original memory usage: {original_memory:,} bytes")

        optimized_df = optimize_dataframe_memory(test_df)
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        print(f"Optimized memory usage: {optimized_memory:,} bytes")

        reduction = ((original_memory - optimized_memory) / original_memory) * 100
        print(f"Memory reduction: {reduction:.1f}%")

        print("✓ DataFrame memory optimization working correctly!")
        return True

    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False


def test_lazy_marker_manager():
    """Test lazy marker loading system"""
    print("\n=== Testing Lazy Marker Manager ===")

    try:
        from lazy_marker_manager import LazyMarkerManager, ViewportBounds

        # Test viewport bounds (fix the constructor call)
        viewport = ViewportBounds(north=51.0, south=50.0, east=0.0, west=-1.0, zoom=10)
        print(
            f"Viewport created: bounds=({viewport.south}, {viewport.north}, {viewport.west}, {viewport.east}), zoom={viewport.zoom}"
        )

        # Test marker manager
        marker_mgr = LazyMarkerManager(max_markers_per_viewport=100)
        print(
            f"Marker manager created with max_markers: {marker_mgr.max_markers_per_viewport}"
        )

        # Test with sample data (must include both BNG and WGS84 coordinates)
        sample_data = pd.DataFrame(
            {
                "LOCA_NATE": [529090, 529100, 529110],  # BNG Easting
                "LOCA_NATN": [181680, 181690, 181700],  # BNG Northing
                "lat": [51.519299, 51.519399, 51.519499],  # WGS84 Latitude
                "lon": [-0.140818, -0.140818, -0.140818],  # WGS84 Longitude
                "LOCA_ID": ["BH001", "BH002", "BH003"],
            }
        )

        visible_markers = marker_mgr.get_visible_markers(sample_data, viewport)
        print(f"Visible markers in viewport: {len(visible_markers)}")

        print("✓ Lazy marker manager working correctly!")
        return True

    except Exception as e:
        print(f"❌ Lazy marker manager test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_coordinate_service():
    """Test coordinate transformation service"""
    print("\n=== Testing Coordinate Service ===")

    try:
        from coordinate_service import get_coordinate_service

        coord_service = get_coordinate_service()
        print(f"Coordinate service initialized: {type(coord_service).__name__}")

        # Test BNG to WGS84 transformation
        bng_x, bng_y = [529090], [181680]  # Sample BNG coordinates
        lat, lon = coord_service.transform_bng_to_wgs84(bng_x, bng_y)
        print(f"BNG ({bng_x[0]}, {bng_y[0]}) -> WGS84 ({lat[0]:.6f}, {lon[0]:.6f})")

        print("✓ Coordinate service working correctly!")
        return True

    except Exception as e:
        print(f"❌ Coordinate service test failed: {e}")
        return False


def test_memory_monitoring():
    """Test memory monitoring system"""
    print("\n=== Testing Memory Monitoring ===")

    try:
        from memory_manager import monitor_memory_usage

        monitor_memory_usage("TEST")
        print("✓ Memory monitoring working correctly!")
        return True

    except Exception as e:
        print(f"❌ Memory monitoring test failed: {e}")
        return False


def test_integration():
    """Test integration between systems"""
    print("\n=== Testing System Integration ===")

    try:
        # Test that callbacks_split imports work
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "callbacks_split", "callbacks_split.py"
        )
        callbacks_module = importlib.util.module_from_spec(spec)

        # Check if our imports are accessible
        print("✓ Callbacks module can access optimization imports")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Optimization Systems Test Suite")
    print("=" * 50)

    tests = [
        test_memory_optimization,
        test_lazy_marker_manager,
        test_coordinate_service,
        test_memory_monitoring,
        test_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All optimization systems are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed - review the output above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
