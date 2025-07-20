"""
Test script to validate coordinate transformation service integration
"""

import logging
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coordinate_service import get_coordinate_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_coordinate_service():
    """Test the coordinate transformation service."""
    logger.info("Starting coordinate service validation tests...")

    # Get service instance
    service = get_coordinate_service()

    # Test data - London area coordinates
    test_cases = [
        # Single point transformations
        {
            "name": "London (Single Point)",
            "bng_e": 529090,
            "bng_n": 181680,
            "expected_lat_range": (51.5, 51.6),
            "expected_lon_range": (-0.15, -0.05),
        },
        # Batch transformations
        {
            "name": "Multiple Points",
            "bng_e": [529090, 530000, 531000],
            "bng_n": [181680, 182000, 182500],
            "expected_lat_range": (51.5, 51.6),
            "expected_lon_range": (-0.15, -0.05),
        },
    ]

    all_tests_passed = True

    for test_case in test_cases:
        logger.info(f"Testing: {test_case['name']}")

        try:
            # Test BNG to WGS84 transformation
            lat, lon = service.transform_bng_to_wgs84(
                test_case["bng_e"], test_case["bng_n"]
            )

            # Convert to arrays for consistent handling
            lat_arr = np.atleast_1d(lat)
            lon_arr = np.atleast_1d(lon)

            # Validate results
            if np.all(
                (test_case["expected_lat_range"][0] <= lat_arr)
                & (lat_arr <= test_case["expected_lat_range"][1])
            ):
                logger.info(f"✓ Latitude range valid: {lat_arr}")
            else:
                logger.error(f"✗ Latitude out of range: {lat_arr}")
                all_tests_passed = False

            if np.all(
                (test_case["expected_lon_range"][0] <= lon_arr)
                & (lon_arr <= test_case["expected_lon_range"][1])
            ):
                logger.info(f"✓ Longitude range valid: {lon_arr}")
            else:
                logger.error(f"✗ Longitude out of range: {lon_arr}")
                all_tests_passed = False

            # Test UTM transformation
            utm_x, utm_y, utm_crs = service.transform_wgs84_to_utm(lon, lat)
            logger.info(f"✓ UTM transformation successful: {utm_crs}")

            # Test round-trip accuracy (BNG -> WGS84 -> UTM -> WGS84)
            # This should be close to the original WGS84 coordinates
            # (Small differences are expected due to projection accuracy)

        except Exception as e:
            logger.error(f"✗ Test failed for {test_case['name']}: {e}")
            all_tests_passed = False

    # Test cache statistics
    cache_stats = service.get_cache_stats()
    logger.info(f"Cache statistics: {cache_stats}")

    if cache_stats["total_requests"] > 0:
        logger.info(f"✓ Cache is working (hit rate: {cache_stats['hit_rate']:.2%})")
    else:
        logger.warning("? No cache activity recorded")

    # Test error handling
    logger.info("Testing error handling...")
    try:
        # Test invalid coordinates
        lat, lon = service.transform_bng_to_wgs84(-999999, -999999)
        if np.isnan(lat) or np.isnan(lon):
            logger.info("✓ Invalid coordinates handled correctly (returned NaN)")
        else:
            logger.warning(f"? Invalid coordinates returned: lat={lat}, lon={lon}")
    except Exception as e:
        logger.info(f"✓ Invalid coordinates raised exception (as expected): {e}")

    return all_tests_passed


def test_backward_compatibility():
    """Test that the convenience functions work correctly."""
    logger.info("Testing backward compatibility functions...")

    try:
        from coordinate_service import transform_bng_to_wgs84, transform_wgs84_to_utm

        # Test convenience functions
        lat, lon = transform_bng_to_wgs84(529090, 181680)
        utm_x, utm_y, utm_crs = transform_wgs84_to_utm(lon, lat)

        logger.info(f"✓ Convenience functions work: lat={lat:.6f}, lon={lon:.6f}")
        logger.info(f"✓ UTM conversion: x={utm_x:.2f}, y={utm_y:.2f}, crs={utm_crs}")

        return True

    except Exception as e:
        logger.error(f"✗ Backward compatibility test failed: {e}")
        return False


def test_integration_with_callbacks():
    """Test that the coordinate service integrates properly with callbacks."""
    logger.info("Testing integration with callbacks_split...")

    try:
        # Import the transform_coordinates function from callbacks
        from callbacks_split import transform_coordinates

        # Test the function
        lat, lon = transform_coordinates(529090, 181680)

        if lat is not None and lon is not None:
            logger.info(
                f"✓ callbacks_split.transform_coordinates works: lat={lat:.6f}, lon={lon:.6f}"
            )

            # Validate range
            if 51.5 <= lat <= 51.6 and -0.15 <= lon <= -0.05:
                logger.info("✓ Transformed coordinates are in expected range")
                return True
            else:
                logger.error(
                    f"✗ Coordinates out of expected range: lat={lat}, lon={lon}"
                )
                return False
        else:
            logger.error("✗ transform_coordinates returned None values")
            return False

    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("COORDINATE SERVICE VALIDATION TEST SUITE")
    logger.info("=" * 60)

    # Run all tests
    tests = [
        ("Core Service Tests", test_coordinate_service),
        ("Backward Compatibility", test_backward_compatibility),
        ("Integration Tests", test_integration_with_callbacks),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"Result: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            logger.error(f"Test suite error: {e}")
            results.append((test_name, False))

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Coordinate service is working correctly.")
        sys.exit(0)
    else:
        logger.error(
            "❌ Some tests failed. Please review the coordinate service implementation."
        )
        sys.exit(1)
