#!/usr/bin/env python3
"""
Optimization Baseline Test Script

This script tests the current performance and behavior of key application components
before implementing optimizations, providing a baseline for comparison.

Tests covered:
1. Matplotlib logging verbosity and font loading
2. Marker click handler logging efficiency
3. Coordinate transformation performance (individual vs batch)
4. DataFrame memory usage and optimization
5. Error handling behavior
"""

import logging
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
from io import StringIO
import tracemalloc

# Import application modules
from coordinate_service import get_coordinate_service
from callbacks_split import transform_coordinates


def setup_test_logging():
    """Set up logging for testing baseline behavior"""
    # Create a StringIO buffer to capture log output
    log_buffer = StringIO()

    # Set up logging to capture to buffer
    handler = logging.StreamHandler(log_buffer)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    return log_buffer


def test_matplotlib_verbosity():
    """Test matplotlib font manager verbosity"""
    print("\n" + "=" * 80)
    print("TESTING MATPLOTLIB VERBOSITY (BASELINE)")
    print("=" * 80)

    log_buffer = setup_test_logging()

    # Force matplotlib font loading (simulates borehole plot generation)
    print("Creating matplotlib figure to trigger font loading...")
    start_time = time.time()

    fig, ax = plt.subplots(figsize=(8, 11))
    ax.text(0.5, 0.5, "Test Text", fontfamily="Arial", fontsize=12)
    ax.text(0.3, 0.7, "Another Text", fontfamily="DejaVu Sans", fontsize=10)
    plt.close(fig)

    end_time = time.time()

    # Get log output
    log_output = log_buffer.getvalue()
    font_manager_lines = [
        line for line in log_output.split("\n") if "font_manager" in line.lower()
    ]

    print(f"Figure creation time: {end_time - start_time:.3f} seconds")
    print(f"Total log lines captured: {len(log_output.split('\\n'))}")
    print(f"Font manager log lines: {len(font_manager_lines)}")

    if font_manager_lines:
        print("Sample font manager log lines:")
        for i, line in enumerate(font_manager_lines[:5]):
            print(f"  {i+1}: {line}")
        if len(font_manager_lines) > 5:
            print(f"  ... and {len(font_manager_lines) - 5} more lines")

    return {
        "figure_creation_time": end_time - start_time,
        "total_log_lines": len(log_output.split("\\n")),
        "font_manager_lines": len(font_manager_lines),
        "log_sample": font_manager_lines[:10],
    }


def test_marker_click_logging():
    """Test marker click handler logging verbosity"""
    print("\n" + "=" * 80)
    print("TESTING MARKER CLICK LOGGING (BASELINE)")
    print("=" * 80)

    log_buffer = setup_test_logging()

    # Simulate marker click scenario with 94 markers (from debug report)
    num_markers = 94
    marker_clicks = [0] * num_markers
    marker_clicks[42] = 1  # Simulate clicking marker 42

    print(f"Simulating marker click handler with {num_markers} markers...")
    start_time = time.time()

    # Simulate the logging that happens in marker click handler
    logging.info("=== MARKER CLICK CALLBACK ===")
    logging.info(f"Triggered by marker click")
    logging.info(f"Marker states: {marker_clicks}")

    # Find clicked marker
    clicked_index = None
    max_clicks = 0
    for i, clicks in enumerate(marker_clicks):
        if clicks and clicks > max_clicks:
            max_clicks = clicks
            clicked_index = i
            logging.debug(f"Checking marker {i}: {clicks} clicks")

    if clicked_index is not None:
        logging.info(f"Marker {clicked_index} was clicked ({max_clicks} times)")

    end_time = time.time()

    # Analyze log output
    log_output = log_buffer.getvalue()
    log_lines = log_output.split("\\n")
    marker_state_lines = [line for line in log_lines if "Marker states:" in line]
    debug_lines = [line for line in log_lines if "DEBUG" in line]

    print(f"Marker click processing time: {end_time - start_time:.3f} seconds")
    print(f"Total log lines: {len(log_lines)}")
    print(f"Debug lines: {len(debug_lines)}")
    print(f"Marker state lines: {len(marker_state_lines)}")

    # Check size of marker state logging
    if marker_state_lines:
        marker_state_size = len(marker_state_lines[0])
        print(f"Marker state log line size: {marker_state_size} characters")

    return {
        "processing_time": end_time - start_time,
        "total_log_lines": len(log_lines),
        "debug_lines": len(debug_lines),
        "marker_state_size": len(marker_state_lines[0]) if marker_state_lines else 0,
    }


def test_coordinate_transformation():
    """Test coordinate transformation performance (individual vs potential batch)"""
    print("\n" + "=" * 80)
    print("TESTING COORDINATE TRANSFORMATION (BASELINE)")
    print("=" * 80)

    # Generate test data similar to real borehole coordinates
    num_points = 94  # From debug report
    test_eastings = np.random.uniform(400000, 600000, num_points)
    test_northings = np.random.uniform(100000, 400000, num_points)

    coordinate_service = get_coordinate_service()

    print(f"Testing transformation of {num_points} coordinate pairs...")

    # Test individual transformations (current approach)
    print("\\nTesting individual transformations (current approach):")
    start_time = time.time()
    individual_results = []

    for i in range(num_points):
        lat, lon = transform_coordinates(test_eastings[i], test_northings[i])
        individual_results.append((lat, lon))
        if i == 0:
            print(
                f"  First result: BNG({test_eastings[i]:.1f}, {test_northings[i]:.1f}) -> WGS84({lat:.6f}, {lon:.6f})"
            )

    individual_time = time.time() - start_time
    print(f"  Individual transformation time: {individual_time:.3f} seconds")
    print(f"  Average time per point: {individual_time/num_points*1000:.2f} ms")

    # Test batch transformation (optimized approach)
    print("\\nTesting batch transformation (optimized approach):")
    start_time = time.time()

    batch_lats, batch_lons = coordinate_service.transform_bng_to_wgs84(
        test_eastings, test_northings
    )

    batch_time = time.time() - start_time
    print(f"  Batch transformation time: {batch_time:.3f} seconds")
    print(f"  Average time per point: {batch_time/num_points*1000:.2f} ms")
    print(f"  Speed improvement: {individual_time/batch_time:.1f}x faster")

    # Verify results are equivalent
    if len(individual_results) > 0:
        first_individual = individual_results[0]
        first_batch = (batch_lats[0], batch_lons[0])
        lat_diff = abs(first_individual[0] - first_batch[0])
        lon_diff = abs(first_individual[1] - first_batch[1])
        print(
            f"  Result verification - Lat diff: {lat_diff:.10f}, Lon diff: {lon_diff:.10f}"
        )

        if lat_diff < 1e-8 and lon_diff < 1e-8:
            print("  ✓ Batch results match individual results")
        else:
            print("  ✗ Batch results differ from individual results!")

    return {
        "num_points": num_points,
        "individual_time": individual_time,
        "batch_time": batch_time,
        "speed_improvement": individual_time / batch_time,
        "avg_individual_ms": individual_time / num_points * 1000,
        "avg_batch_ms": batch_time / num_points * 1000,
    }


def test_dataframe_optimization():
    """Test DataFrame memory usage and optimization opportunities"""
    print("\n" + "=" * 80)
    print("TESTING DATAFRAME OPTIMIZATION (BASELINE)")
    print("=" * 80)

    # Create sample DataFrame similar to borehole data
    num_rows = 94
    sample_data = {
        "LOCA_ID": [f"BH{i:03d}" for i in range(num_rows)],
        "LOCA_NATE": np.random.uniform(400000, 600000, num_rows),
        "LOCA_NATN": np.random.uniform(100000, 400000, num_rows),
        "lat": np.random.uniform(50, 55, num_rows),
        "lon": np.random.uniform(-3, 0, num_rows),
        "easting": np.random.uniform(400000, 600000, num_rows),
        "northing": np.random.uniform(100000, 400000, num_rows),
        "ags_file": ["sample_file.ags"] * num_rows,
        "Geology_Code": np.random.choice(["SC", "CL", "ML", "CH", "MH"], num_rows),
        "Description": ["Clay with sand and gravel"] * num_rows,
        "Depth_Top": np.random.uniform(0, 5, num_rows),
        "Depth_Base": np.random.uniform(5, 20, num_rows),
    }

    # Test memory usage before optimization
    tracemalloc.start()
    df_original = pd.DataFrame(sample_data)

    print(f"DataFrame shape: {df_original.shape}")
    print(f"DataFrame dtypes:")
    for col, dtype in df_original.dtypes.items():
        print(f"  {col}: {dtype}")

    # Calculate memory usage
    memory_usage = df_original.memory_usage(deep=True)
    total_memory = memory_usage.sum()

    print(f"\\nMemory usage (bytes):")
    for col, usage in memory_usage.items():
        if usage > 0:
            print(f"  {col}: {usage:,} bytes")
    print(f"  Total: {total_memory:,} bytes ({total_memory/1024/1024:.2f} MB)")

    # Test optimization opportunities
    print("\\nOptimization opportunities:")

    # 1. Categorical data
    categorical_candidates = ["LOCA_ID", "ags_file", "Geology_Code", "Description"]
    categorical_savings = 0

    for col in categorical_candidates:
        if col in df_original.columns:
            original_size = df_original[col].memory_usage(deep=True)
            unique_values = df_original[col].nunique()
            unique_ratio = unique_values / len(df_original)

            print(f"  {col}: {unique_values} unique values ({unique_ratio:.2%})")

            # Estimate categorical memory savings
            if unique_ratio < 0.5:  # Good candidate for categorical
                # Rough estimate: categorical uses int codes + string mapping
                estimated_categorical = len(df_original) * 4 + sum(
                    len(str(v)) for v in df_original[col].unique()
                )
                potential_savings = original_size - estimated_categorical
                categorical_savings += potential_savings
                print(
                    f"    Current: {original_size:,} bytes, Categorical: ~{estimated_categorical:,} bytes"
                )
                print(
                    f"    Potential savings: {potential_savings:,} bytes ({potential_savings/original_size:.1%})"
                )

    print(
        f"\\nTotal potential categorical savings: {categorical_savings:,} bytes ({categorical_savings/total_memory:.1%})"
    )

    # 2. Numeric data type optimization
    numeric_cols = df_original.select_dtypes(include=[np.number]).columns
    print(f"\\nNumeric columns optimization:")

    for col in numeric_cols:
        original_dtype = df_original[col].dtype
        min_val = df_original[col].min()
        max_val = df_original[col].max()

        # Check if we can downcast
        if original_dtype == "float64":
            if (
                min_val >= np.finfo(np.float32).min
                and max_val <= np.finfo(np.float32).max
            ):
                original_size = df_original[col].memory_usage(deep=True)
                potential_size = original_size // 2  # float64 -> float32
                print(
                    f"  {col}: float64 -> float32 potential, savings: {original_size - potential_size:,} bytes"
                )

    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "dataframe_shape": df_original.shape,
        "total_memory_bytes": total_memory,
        "categorical_savings_bytes": categorical_savings,
        "categorical_savings_percent": categorical_savings / total_memory,
        "peak_memory_bytes": peak_memory,
    }


def test_error_handling():
    """Test current error handling behavior"""
    print("\n" + "=" * 80)
    print("TESTING ERROR HANDLING (BASELINE)")
    print("=" * 80)

    log_buffer = setup_test_logging()

    test_results = {
        "coordinate_transform_invalid": False,
        "coordinate_transform_recovery": False,
        "matplotlib_memory_pressure": False,
        "file_processing_invalid": False,
    }

    # Test 1: Invalid coordinate transformation
    print("Testing coordinate transformation error handling:")
    try:
        lat, lon = transform_coordinates(None, 999999999)
        print("  ✗ Should have failed with invalid coordinates")
    except Exception as e:
        print(f"  ✓ Correctly handled invalid coordinates: {type(e).__name__}")
        test_results["coordinate_transform_invalid"] = True

    # Test 2: Coordinate transformation recovery
    print("Testing coordinate transformation recovery:")
    try:
        lat, lon = transform_coordinates(500000, 200000)  # Valid BNG coordinates
        if lat is not None and lon is not None:
            print(f"  ✓ Successfully recovered: ({lat:.6f}, {lon:.6f})")
            test_results["coordinate_transform_recovery"] = True
        else:
            print("  ✗ Failed to recover from error")
    except Exception as e:
        print(f"  ✗ Recovery failed: {e}")

    # Test 3: Matplotlib with memory pressure (simulate)
    print("Testing matplotlib under memory pressure:")
    try:
        # Create multiple figures quickly to test memory handling
        figures = []
        for i in range(5):
            fig, ax = plt.subplots(figsize=(10, 10))
            ax.plot(np.random.random(1000), np.random.random(1000))
            figures.append(fig)

        # Clean up
        for fig in figures:
            plt.close(fig)

        print("  ✓ Matplotlib handled multiple figures correctly")
        test_results["matplotlib_memory_pressure"] = True
    except Exception as e:
        print(f"  ✗ Matplotlib failed under memory pressure: {e}")

    # Analyze error logging
    log_output = log_buffer.getvalue()
    error_lines = [line for line in log_output.split("\\n") if "ERROR" in line]
    warning_lines = [line for line in log_output.split("\\n") if "WARNING" in line]

    print(f"\\nError handling summary:")
    print(f"  Error log lines: {len(error_lines)}")
    print(f"  Warning log lines: {len(warning_lines)}")
    print(f"  Tests passed: {sum(test_results.values())}/{len(test_results)}")

    return test_results


def run_comprehensive_baseline():
    """Run all baseline tests and generate a comprehensive report"""
    print("\\n" + "=" * 80)
    print("OPTIMIZATION BASELINE TESTING - COMPREHENSIVE REPORT")
    print("=" * 80)
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    results = {}

    try:
        results["matplotlib_verbosity"] = test_matplotlib_verbosity()
    except Exception as e:
        print(f"Matplotlib verbosity test failed: {e}")
        results["matplotlib_verbosity"] = {"error": str(e)}

    try:
        results["marker_click_logging"] = test_marker_click_logging()
    except Exception as e:
        print(f"Marker click logging test failed: {e}")
        results["marker_click_logging"] = {"error": str(e)}

    try:
        results["coordinate_transformation"] = test_coordinate_transformation()
    except Exception as e:
        print(f"Coordinate transformation test failed: {e}")
        results["coordinate_transformation"] = {"error": str(e)}

    try:
        results["dataframe_optimization"] = test_dataframe_optimization()
    except Exception as e:
        print(f"DataFrame optimization test failed: {e}")
        results["dataframe_optimization"] = {"error": str(e)}

    try:
        results["error_handling"] = test_error_handling()
    except Exception as e:
        print(f"Error handling test failed: {e}")
        results["error_handling"] = {"error": str(e)}

    # Generate summary
    print("\\n" + "=" * 80)
    print("BASELINE TEST SUMMARY")
    print("=" * 80)

    # Matplotlib findings
    if (
        "matplotlib_verbosity" in results
        and "error" not in results["matplotlib_verbosity"]
    ):
        mv = results["matplotlib_verbosity"]
        print(f"Matplotlib Verbosity:")
        print(f"  Figure creation time: {mv['figure_creation_time']:.3f}s")
        print(f"  Font manager log lines: {mv['font_manager_lines']}")
        print(f"  Total log lines: {mv['total_log_lines']}")
        if mv["font_manager_lines"] > 100:
            print("  🔴 HIGH: Excessive font manager logging detected")
        elif mv["font_manager_lines"] > 10:
            print("  🟡 MEDIUM: Moderate font manager logging")
        else:
            print("  🟢 LOW: Minimal font manager logging")

    # Marker click findings
    if (
        "marker_click_logging" in results
        and "error" not in results["marker_click_logging"]
    ):
        mcl = results["marker_click_logging"]
        print(f"\\nMarker Click Logging:")
        print(f"  Processing time: {mcl['processing_time']:.3f}s")
        print(f"  Debug lines: {mcl['debug_lines']}")
        print(f"  Marker state size: {mcl['marker_state_size']} characters")
        if mcl["marker_state_size"] > 1000:
            print("  🔴 HIGH: Excessive marker state logging")
        elif mcl["marker_state_size"] > 500:
            print("  🟡 MEDIUM: Moderate marker state logging")
        else:
            print("  🟢 LOW: Reasonable marker state logging")

    # Coordinate transformation findings
    if (
        "coordinate_transformation" in results
        and "error" not in results["coordinate_transformation"]
    ):
        ct = results["coordinate_transformation"]
        print(f"\\nCoordinate Transformation:")
        print(f"  Individual avg: {ct['avg_individual_ms']:.2f}ms per point")
        print(f"  Batch avg: {ct['avg_batch_ms']:.2f}ms per point")
        print(f"  Speed improvement: {ct['speed_improvement']:.1f}x")
        if ct["speed_improvement"] > 5:
            print("  🟢 HIGH: Significant batch optimization opportunity")
        elif ct["speed_improvement"] > 2:
            print("  🟡 MEDIUM: Moderate batch optimization opportunity")
        else:
            print("  🔴 LOW: Limited batch optimization benefit")

    # DataFrame optimization findings
    if (
        "dataframe_optimization" in results
        and "error" not in results["dataframe_optimization"]
    ):
        do = results["dataframe_optimization"]
        print(f"\\nDataFrame Optimization:")
        print(f"  Current memory: {do['total_memory_bytes']/1024/1024:.2f} MB")
        print(f"  Categorical savings: {do['categorical_savings_percent']:.1%}")
        if do["categorical_savings_percent"] > 0.2:
            print("  🟢 HIGH: Significant categorical optimization opportunity")
        elif do["categorical_savings_percent"] > 0.1:
            print("  🟡 MEDIUM: Moderate categorical optimization opportunity")
        else:
            print("  🔴 LOW: Limited categorical optimization benefit")

    print(f"\\nBaseline testing completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return results


if __name__ == "__main__":
    # Set up matplotlib to ensure we're testing the current configuration
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend

    # Run comprehensive baseline testing
    baseline_results = run_comprehensive_baseline()

    # Save results for later comparison
    import json

    with open("optimization_baseline_results.json", "w") as f:
        # Convert numpy types to regular Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            return obj

        json_results = {}
        for key, value in baseline_results.items():
            if isinstance(value, dict):
                json_results[key] = {k: convert_numpy(v) for k, v in value.items()}
            else:
                json_results[key] = convert_numpy(value)

        json.dump(json_results, f, indent=2)

    print(f"\\nBaseline results saved to: optimization_baseline_results.json")
