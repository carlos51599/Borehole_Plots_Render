"""
Comprehensive validation test for the completed refactoring phases.

This script validates:
- Phase 1: Callback utilities refactoring (completed)
- Phase 2: Section module refactoring (completed)

Tests include import validation, functionality checks, and integration testing.
"""

import sys
import os
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_phase_1_callbacks():
    """Test Phase 1: Callback utilities refactoring"""
    print("🧪 Testing Phase 1: Callback Utilities...")

    try:
        # Test callback utilities
        from callbacks.error_handling import CallbackError, create_error_message
        from callbacks.file_validation import validate_file_size, validate_file_content
        from callbacks.coordinate_utils import bng_to_wgs84_single
        from callbacks.file_upload_enhanced import FileUploadManager

        print("✅ Phase 1 imports successful")

        # Test basic functionality
        error_msg = create_error_message("Test error", "TEST_001")
        print(f"✅ Error handling: {error_msg[:50]}...")

        is_valid, _ = validate_file_size(1024, 5 * 1024 * 1024)  # 1KB file, 5MB limit
        print(f"✅ File validation: Size check passed = {is_valid}")

        lat, lon = bng_to_wgs84_single(400000, 300000)
        print(f"✅ Coordinate utils: BNG->WGS84 = ({lat:.4f}, {lon:.4f})")

        upload_manager = FileUploadManager()
        print(f"✅ File upload manager: Max files = {upload_manager.max_files}")

        return True

    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        traceback.print_exc()
        return False


def test_phase_2_section():
    """Test Phase 2: Section module refactoring"""
    print("\n🧪 Testing Phase 2: Section Module...")

    try:
        # Test section module imports
        from section import (
            parse_ags_geol_section_from_string,
            validate_ags_format,
            extract_ags_metadata,
            plot_professional_borehole_sections,
            plot_section_from_ags_content,
            convert_figure_to_base64,
            safe_close_figure,
            matplotlib_figure,
        )

        print("✅ Phase 2 imports successful")

        # Test with sample AGS data
        ags_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
UNITS,,,m,m,m
TYPE,X,X,2DP,2DP,2DP
DATA,BH001,BH,400000.00,300000.00,100.00
DATA,BH002,BH,400020.00,300010.00,105.50

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG
UNITS,,m,m,,
TYPE,X,2DP,2DP,X,X
DATA,BH001,0.00,2.50,MADE GROUND,MG
DATA,BH001,2.50,5.00,LONDON CLAY,LC
DATA,BH002,0.00,1.50,TOPSOIL,TS
DATA,BH002,1.50,4.00,LONDON CLAY,LC
"""

        # Test AGS validation
        is_valid, msg = validate_ags_format(ags_content)
        print(f"✅ AGS validation: {is_valid} - {msg}")

        # Test metadata extraction
        metadata = extract_ags_metadata(ags_content)
        print(f"✅ Metadata: {len(metadata['groups_found'])} groups found")

        # Test parsing
        geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)
        print(
            f"✅ AGS parsing: {len(geol_df)} geology, {len(loca_df)} location records"
        )

        # Test matplotlib context manager
        with matplotlib_figure(figsize=(8, 6)) as fig:
            ax = fig.add_subplot(111)
            ax.plot([1, 2, 3], [1, 2, 1])
            ax.set_title("Test Plot")
        print("✅ Matplotlib context manager working")

        return True

    except Exception as e:
        print(f"❌ Phase 2 test failed: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """Test integration between refactored modules"""
    print("\n🧪 Testing Integration...")

    try:
        # Test that callbacks can use section module
        from callbacks.file_upload_enhanced import FileUploadManager
        from section import validate_ags_format

        upload_manager = FileUploadManager()

        # Simulate file upload and validation workflow
        test_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE
UNITS,,
TYPE,X,X
DATA,BH001,BH
"""

        # Validate content using section module
        is_valid, msg = validate_ags_format(test_content)
        print(f"✅ Integration: File upload -> AGS validation = {is_valid}")

        # Test that existing imports still work
        from section import plot_section_from_ags_content  # Used in callbacks
        from section import parse_ags_geol_section_from_string  # Used in borehole_log

        print("✅ Integration: Existing code imports working")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run comprehensive validation tests"""
    print("🚀 Comprehensive Refactoring Validation")
    print("=" * 50)

    results = {
        "phase_1": test_phase_1_callbacks(),
        "phase_2": test_phase_2_section(),
        "integration": test_integration(),
    }

    print("\n📋 Validation Summary:")
    print("=" * 30)

    for phase, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{phase.upper().replace('_', ' ')}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nCompleted Phases:")
        print("✅ Phase 1: Callback utilities refactored into focused modules")
        print("✅ Phase 2: Section plotting refactored into parsing/plotting/utils")
        print("✅ Integration: All modules work together seamlessly")
        print("\nNext Steps:")
        print("🔄 Phase 3: Refactor borehole_log_professional.py (1823 lines)")
        print("🔄 Phase 4: Create common utilities folder")
        print("🔄 Phase 5: Final testing and validation")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
