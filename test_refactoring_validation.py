"""
Test for State Management and Callback Refactoring

This test validates that the new state management system and
callback refactoring work correctly.
"""

import logging
import pytest
from unittest.mock import Mock, patch
import pandas as pd

# Set up logging for tests
logging.basicConfig(level=logging.INFO)


def test_state_management_creation():
    """Test that state management objects can be created."""

    from state_management import get_app_state_manager, AppState
    from state_management.state_models import (
        BoreholeData,
        MapState,
        SelectionState,
        PlotState,
        UploadState,
    )

    # Test individual models
    borehole_data = BoreholeData()
    assert not borehole_data.is_loaded
    assert borehole_data.get_borehole_count() == 0

    map_state = MapState()
    assert map_state.center == (51.5, -0.1)
    assert map_state.zoom == 6

    selection_state = SelectionState()
    assert len(selection_state.selected_borehole_ids) == 0
    assert not selection_state.is_polyline_selection

    plot_state = PlotState()
    assert not plot_state.show_labels
    assert not plot_state.generation_in_progress

    upload_state = UploadState()
    assert len(upload_state.files_uploaded) == 0
    assert not upload_state.upload_in_progress

    # Test app state manager
    state_manager = get_app_state_manager()
    assert isinstance(state_manager, AppState)

    # Test singleton behavior
    state_manager2 = get_app_state_manager()
    assert state_manager is state_manager2

    print("✅ State management models created successfully")


def test_callback_base_classes():
    """Test that callback base classes can be created and registered."""

    from callbacks import (
        CallbackManager,
        get_callback_manager,
    )

    # Test callback manager
    manager = CallbackManager()
    assert len(manager.callbacks) == 0

    # Test adding mock callbacks (since base classes are abstract)
    class MockCallback:
        def __init__(self, name, category):
            self.name = name
            self.category = category

        def register(self, app):
            pass

    file_callback = MockCallback("test_file", "file_upload")
    map_callback = MockCallback("test_map", "map_interactions")

    manager.add_callback(file_callback)
    manager.add_callback(map_callback)
    assert len(manager.callbacks) == 2

    summary = manager.get_callback_summary()
    assert summary["total_callbacks"] == 2
    assert "file_upload" in summary["categories"]
    assert "map_interactions" in summary["categories"]

    # Test singleton behavior
    global_manager = get_callback_manager()
    assert isinstance(global_manager, CallbackManager)

    print("✅ Callback base classes created successfully")


def test_error_handling_system():
    """Test that the error handling system works correctly."""

    from error_handling import (
        get_error_handler,
        ErrorHandler,
        ErrorSeverity,
        ErrorCategory,
        ApplicationError,
    )

    # Test error handler creation
    error_handler = get_error_handler()
    assert isinstance(error_handler, ErrorHandler)

    # Test error creation
    error = error_handler.create_error(
        message="Test error",
        category=ErrorCategory.FILE_UPLOAD,
        severity=ErrorSeverity.WARNING,
        details="This is a test error",
    )

    assert isinstance(error, ApplicationError)
    assert error.message == "Test error"
    assert error.category == ErrorCategory.FILE_UPLOAD
    assert error.severity == ErrorSeverity.WARNING
    assert error.details == "This is a test error"

    # Test error history
    history = error_handler.get_error_history()
    assert len(history) >= 1
    assert history[0].message == "Test error"

    # Test user-friendly message
    user_message = error.get_user_friendly_message()
    assert "test error" in user_message.lower()

    print("✅ Error handling system works correctly")


def test_callback_imports():
    """Test that all refactored callbacks can be imported."""

    from callbacks.file_upload import FileUploadCallback, register_file_upload_callbacks
    from callbacks.map_interactions import (
        MapInteractionCallback,
        register_map_interaction_callbacks,
    )

    # Test callback creation
    file_callback = FileUploadCallback()
    assert file_callback.name == "file_upload"
    assert file_callback.category == "file_upload"

    map_callback = MapInteractionCallback()
    assert map_callback.name == "map_interactions"
    assert map_callback.category == "map_interactions"

    # Test registration functions
    from callbacks import get_callback_manager

    manager = get_callback_manager()
    initial_count = len(manager.callbacks)

    register_file_upload_callbacks(manager)
    register_map_interaction_callbacks(manager)

    assert len(manager.callbacks) >= initial_count + 2

    print("✅ All refactored callbacks import successfully")


def test_state_update_integration():
    """Test that state updates work correctly across the system."""

    from state_management import get_app_state_manager
    import pandas as pd

    state_manager = get_app_state_manager()

    # Test borehole data update
    test_df = pd.DataFrame(
        {
            "LOCA_ID": ["BH001", "BH002", "BH003"],
            "LOCA_NATE": [500000, 500100, 500200],
            "LOCA_NATN": [200000, 200100, 200200],
            "lat": [51.5, 51.51, 51.52],
            "lon": [-0.1, -0.09, -0.08],
        }
    )

    state_manager.update_borehole_data(
        loca_df=test_df,
        filename_map={"test.ags": "test content"},
        all_borehole_ids=["BH001", "BH002", "BH003"],
    )

    assert state_manager.borehole_data.is_loaded
    assert state_manager.borehole_data.get_borehole_count() == 3

    # Test selection update
    state_manager.update_selection_state(
        selected_borehole_ids=["BH001", "BH002"], selection_method="shape"
    )

    assert len(state_manager.selection_state.selected_borehole_ids) == 2
    assert state_manager.selection_state.selection_method == "shape"

    # Test map state update
    state_manager.update_map_state(center=(51.5, -0.1), zoom=12)

    assert state_manager.map_state.center == (51.5, -0.1)
    assert state_manager.map_state.zoom == 12

    # Test Dash store format conversion
    dash_format = state_manager.to_dash_store_format()
    assert "loca_df" in dash_format
    assert "selection_boreholes" in dash_format
    assert "map_center" in dash_format
    assert len(dash_format["loca_df"]) == 3
    assert len(dash_format["selection_boreholes"]) == 2

    print("✅ State update integration works correctly")


def test_coordinate_service_integration():
    """Test that the coordinate service is properly integrated."""

    from coordinate_service import get_coordinate_service
    import numpy as np

    coord_service = get_coordinate_service()

    # Test single coordinate transformation
    lat, lon = coord_service.transform_bng_to_wgs84([500000], [200000])
    assert len(lat) == 1
    assert len(lon) == 1
    assert isinstance(lat[0], (float, np.float64))
    assert isinstance(lon[0], (float, np.float64))

    # Test batch transformation
    lats, lons = coord_service.transform_bng_to_wgs84(
        [500000, 500100, 500200], [200000, 200100, 200200]
    )
    assert len(lats) == 3
    assert len(lons) == 3

    print("✅ Coordinate service integration works correctly")


def run_all_tests():
    """Run all tests and report results."""

    print("🧪 Running State Management and Callback Refactoring Tests...")
    print("=" * 60)

    tests = [
        test_state_management_creation,
        test_callback_base_classes,
        test_error_handling_system,
        test_callback_imports,
        test_state_update_integration,
        test_coordinate_service_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"\n🔍 Running {test.__name__}...")
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Refactoring is successful!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
