#!/usr/bin/env python3
"""
Final deployment validation test.
Following instructions.md Stage 7: Prepare for deployment.
"""

import sys


def test_imports_and_syntax():
    """Test that all imports work and syntax is valid in relevant files."""
    print("=== Final Deployment Validation ===")

    tests = [
        (
            "borehole_log module",
            "from borehole_log import plot_borehole_log_from_ags_content",
        ),
        (
            "callbacks.search_functionality",
            "from callbacks.search_functionality import SearchFunctionalityCallback",
        ),
        (
            "callbacks.marker_handling",
            "from callbacks.marker_handling import MarkerHandlingCallback",
        ),
        (
            "config module",
            "from config import LOG_PLOT_CENTER_STYLE, SECTION_PLOT_CENTER_STYLE",
        ),
        (
            "professional implementation",
            "from borehole_log_professional import create_professional_borehole_log_multi_page",
        ),
        (
            "section parsing",
            "from section.parsing import parse_ags_geol_section_from_string",
        ),
    ]

    all_passed = True

    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {test_name}: Import successful")
        except Exception as e:
            print(f"❌ {test_name}: Import failed - {e}")
            all_passed = False

    print("\n=== Integration Test ===")

    # Test the full integration
    try:
        from borehole_log import plot_borehole_log_from_ags_content

        # Simple test data
        test_ags = """
"GROUP","LOCA"
"HEADING","LOCA_ID","LOCA_TYPE","LOCA_STAT","LOCA_NATE","LOCA_NATN","LOCA_GL","LOCA_REM"
"UNIT","","","","m","m","mOD",""
"TYPE","X","PA","PA","2DP","2DP","2DP","X"
"DATA","TEST01","CP","","404500.0","206800.0","100.0","Test borehole"

"GROUP","GEOL"
"HEADING","LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC","GEOL_LEG","GEOL_STAT","GEOL_REM"
"UNIT","","m","m","","","",""
"TYPE","X","2DP","2DP","X","X","PA","X"
"DATA","TEST01","0.00","2.00","Test geology","101","","Test"
"""

        result = plot_borehole_log_from_ags_content(
            test_ags, "TEST01", show_labels=True
        )

        if result and len(result) > 0:
            print(
                "✅ Integration test: Professional borehole log generation successful"
            )
            print(f"   Generated {len(result)} professional log page(s)")
        else:
            print("❌ Integration test: No images generated")
            all_passed = False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        all_passed = False

    print("\n=== Final Result ===")
    if all_passed:
        print("🚀 ALL DEPLOYMENT TESTS PASSED")
        print("✅ Ready for production use")
        return True
    else:
        print("❌ DEPLOYMENT TESTS FAILED")
        print("❌ Issues need to be resolved before deployment")
        return False


if __name__ == "__main__":
    success = test_imports_and_syntax()
    sys.exit(0 if success else 1)
