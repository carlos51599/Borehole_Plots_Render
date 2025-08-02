"""
Test Shape Selection Functionality Fix

This test verifies that:
1. Shape drawing and borehole selection works without import errors
2. Missing config constants are properly imported
3. CSS property warnings are eliminated
"""

import sys
import os
import pandas as pd
import unittest
from unittest.mock import Mock, patch
import logging

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Test imports that were causing issues
try:
    from config_modules import (
        DESCRIPTION_TEXT_STYLE,
        CHECKBOX_LABEL_STYLE,
        CHECKBOX_LEFT_STYLE,
        CHECKBOX_INSTRUCTIONS,
    )

    CONFIG_IMPORTS_OK = True
    CONFIG_IMPORT_ERROR = None
except ImportError as e:
    CONFIG_IMPORTS_OK = False
    CONFIG_IMPORT_ERROR = str(e)

# Test map interactions callback
try:
    from callbacks.map_interactions import MapInteractionCallback

    MAP_CALLBACK_IMPORTS_OK = True
    MAP_CALLBACK_IMPORT_ERROR = None
except ImportError as e:
    MAP_CALLBACK_IMPORTS_OK = False
    MAP_CALLBACK_IMPORT_ERROR = str(e)

# Test shape filtering utility
try:
    from map_utils import filter_selection_by_shape

    MAP_UTILS_IMPORTS_OK = True
    MAP_UTILS_IMPORT_ERROR = None
except ImportError as e:
    MAP_UTILS_IMPORTS_OK = False
    MAP_UTILS_IMPORT_ERROR = str(e)


class TestShapeSelectionFix(unittest.TestCase):
    """Test that shape selection functionality works properly."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger(__name__)

        # Sample borehole data for testing
        self.sample_borehole_data = {
            "loca_df": {
                "LOCA_ID": ["BH001", "BH002", "BH003"],
                "LOCA_NATE": [500000, 500100, 500200],
                "LOCA_NATN": [200000, 200100, 200200],
                "LOCA_GREF": ["BNG", "BNG", "BNG"],
            }
        }

        # Sample GeoJSON polygon for testing
        self.sample_polygon_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [499950, 199950],  # Bottom-left
                                [500250, 199950],  # Bottom-right
                                [500250, 200250],  # Top-right
                                [499950, 200250],  # Top-left
                                [499950, 199950],  # Close polygon
                            ]
                        ],
                    },
                    "properties": {},
                }
            ],
        }

    def test_config_imports(self):
        """Test that all required config constants can be imported."""
        if not CONFIG_IMPORTS_OK:
            self.fail(f"Config imports failed: {CONFIG_IMPORT_ERROR}")

        # Verify the constants exist and have expected structure
        self.assertIsInstance(DESCRIPTION_TEXT_STYLE, dict)
        self.assertIsInstance(CHECKBOX_LABEL_STYLE, dict)
        self.assertIsInstance(CHECKBOX_LEFT_STYLE, dict)
        self.assertIsInstance(CHECKBOX_INSTRUCTIONS, str)

        # Verify style dictionaries have expected properties
        self.assertIn("fontSize", DESCRIPTION_TEXT_STYLE)
        self.assertIn("color", DESCRIPTION_TEXT_STYLE)

        print("✅ All config constants imported successfully")

    def test_map_callback_imports(self):
        """Test that map interactions callback can be imported."""
        if not MAP_CALLBACK_IMPORTS_OK:
            self.fail(f"Map callback imports failed: {MAP_CALLBACK_IMPORT_ERROR}")

        print("✅ Map interactions callback imported successfully")

    def test_map_utils_imports(self):
        """Test that map utilities can be imported."""
        if not MAP_UTILS_IMPORTS_OK:
            self.fail(f"Map utils imports failed: {MAP_UTILS_IMPORT_ERROR}")

        print("✅ Map utilities imported successfully")

    def test_checkbox_grid_creation(self):
        """Test that checkbox grid can be created without import errors."""
        if not MAP_CALLBACK_IMPORTS_OK:
            self.skipTest("Map callback import failed")

        try:
            # Create callback instance
            callback = MapInteractionCallback()

            # Mock logger to avoid setup requirements
            callback.logger = Mock()

            # Test checkbox grid creation
            borehole_ids = ["BH001", "BH002", "BH003"]
            current_checked = ["BH001"]

            checkbox_grid = callback._create_checkbox_grid(
                borehole_ids, current_checked
            )

            # Verify it returns a component (not None or error)
            self.assertIsNotNone(checkbox_grid)

            print("✅ Checkbox grid creation works without import errors")

        except Exception as e:
            self.fail(f"Checkbox grid creation failed: {e}")

    def test_polygon_selection_workflow(self):
        """Test the complete polygon selection workflow."""
        if not MAP_CALLBACK_IMPORTS_OK:
            self.skipTest("Map callback import failed")

        try:
            # Create callback instance
            callback = MapInteractionCallback()
            callback.logger = Mock()

            # Convert sample data to DataFrame
            loca_df = pd.DataFrame(self.sample_borehole_data["loca_df"])

            # Test polygon selection handler
            result = callback._handle_polygon_selection(
                feature=self.sample_polygon_geojson["features"][0],
                loca_df=loca_df,
                stored_data=self.sample_borehole_data,
            )

            # Verify result structure
            self.assertIsInstance(result, tuple)
            self.assertGreater(len(result), 0)

            print("✅ Polygon selection workflow completes without errors")

        except Exception as e:
            self.fail(f"Polygon selection workflow failed: {e}")

    def test_css_property_format(self):
        """Test that style dictionaries use proper React CSS format."""
        if not CONFIG_IMPORTS_OK:
            self.skipTest("Config imports failed")

        # Check that style dictionaries use camelCase, not kebab-case
        for style_name, style_dict in [
            ("DESCRIPTION_TEXT_STYLE", DESCRIPTION_TEXT_STYLE),
            ("CHECKBOX_LABEL_STYLE", CHECKBOX_LABEL_STYLE),
            ("CHECKBOX_LEFT_STYLE", CHECKBOX_LEFT_STYLE),
        ]:
            for key in style_dict.keys():
                # Should not contain kebab-case properties
                self.assertNotIn(
                    "-", key, f"Style {style_name} contains kebab-case property: {key}"
                )

                # Common React properties should be camelCase
                if "borderradius" in key.lower().replace("-", ""):
                    self.assertEqual(
                        key,
                        "borderRadius",
                        f"Style {style_name} should use borderRadius, not {key}",
                    )
                if "backgroundcolor" in key.lower().replace("-", ""):
                    self.assertEqual(
                        key,
                        "backgroundColor",
                        f"Style {style_name} should use backgroundColor, not {key}",
                    )

        print("✅ CSS properties use proper React camelCase format")


def main():
    """Run the tests and display results."""
    print("=== Testing Shape Selection Fix ===")
    print("Testing that shape drawing and borehole selection works properly...")
    print()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestShapeSelectionFix)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n=== Test Summary ===")
    if result.wasSuccessful():
        print("🎉 All tests passed! Shape selection functionality is working.")
        print("\nFixed Issues:")
        print("✅ Missing config constants resolved")
        print("✅ Import errors eliminated")
        print("✅ CSS properties use proper React format")
        print("✅ Shape drawing and selection workflow functional")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")

        for test, error in result.failures + result.errors:
            print(f"   - {test}: {error}")

    return result.wasSuccessful()


if __name__ == "__main__":
    main()
