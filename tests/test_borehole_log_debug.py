"""
Borehole Log Generation Test

Test script to debug the "No borehole log data available" issue.
This tests the complete borehole log generation workflow.
"""

import sys
import os

# Add project root to Python path
project_root = (
    os.path.dirname(os.path.abspath(__file__)).replace("tests", "").rstrip(os.sep)
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_borehole_log_generation():
    """Test borehole log generation with sample data."""
    print("=" * 60)
    print("TESTING BOREHOLE LOG GENERATION")
    print("=" * 60)

    try:
        from borehole_log import plot_borehole_log_from_ags_content

        # Create realistic AGS test data
        sample_ags = """**PROJ
PROJ_ID,PROJ_NAME,PROJ_LOC,PROJ_CLNT,PROJ_CONT,PROJ_ENG,
PROJ1,Test Project,Test Location,Test Client,Test Contractor,Test Engineer,

**LOCA
LOCA_ID,LOCA_TYPE,LOCA_STAT,LOCA_NATE,LOCA_NATN,LOCA_GL,LOCA_REM,LOCA_FDEP,LOCA_STAR,LOCA_PURP,LOCA_TERM,LOCA_DIAM,
BH001,BH,Active,523456.78,123456.89,100.50,Test borehole,5.00,2024-01-01,Investigation,Refusal,150,

**GEOL  
LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_GEO2,GEOL_LEG,GEOL_DESC,
BH001,0.00,0.50,TOPSOIL,TS,1,Dark brown topsoil with grass roots,
BH001,0.50,2.00,CLAY,CL,2,Firm brown clay,
BH001,2.00,3.50,SAND,SA,3,Medium dense yellow sand,
BH001,3.50,5.00,CLAY,CL,2,Stiff grey clay,

**ABBR
ABBR_HDNG,ABBR_CODE,ABBR_DESC,ABBR_LIST,
GEOL_GEOL,TOPSOIL,Topsoil,GEOL_GEOL,
GEOL_GEOL,CLAY,Clay,GEOL_GEOL,
GEOL_GEOL,SAND,Sand,GEOL_GEOL,
"""

        print("✓ Sample AGS data created")
        print(f"Sample data length: {len(sample_ags)} characters")

        # Test the function call
        print("\nTesting plot_borehole_log_from_ags_content...")

        result = plot_borehole_log_from_ags_content(
            ags_content=sample_ags,
            loca_id="BH001",
            show_labels=True,
            fig_height=11.69,
            fig_width=8.27,
        )

        print(f"✓ Function call successful")
        print(f"Result type: {type(result)}")

        if result is not None:
            if isinstance(result, list):
                print(f"✓ Returned list with {len(result)} items")

                for i, item in enumerate(result):
                    print(
                        f"  Item {i}: type={type(item)}, length={len(str(item)) if item else 0}"
                    )

                    # Check if it's a base64 string
                    if isinstance(item, str) and len(item) > 100:
                        if item.startswith("data:image") or item.startswith(
                            "iVBORw0KGgo"
                        ):
                            print(
                                f"    ✓ Item {i} appears to be a valid image (base64)"
                            )
                        else:
                            print(
                                f"    ⚠️ Item {i} is a string but may not be valid image data"
                            )
                            print(f"    First 50 chars: {item[:50]}")

                if len(result) > 0 and any(item for item in result):
                    print("✅ BOREHOLE LOG GENERATION: SUCCESS")
                    return True
                else:
                    print("❌ BOREHOLE LOG GENERATION: FAILED - Empty or None results")
                    return False
            else:
                print(f"⚠️ Expected list, got {type(result)}")
                if result:
                    print("✅ BOREHOLE LOG GENERATION: SUCCESS (non-list result)")
                    return True
                else:
                    print("❌ BOREHOLE LOG GENERATION: FAILED")
                    return False
        else:
            print("❌ BOREHOLE LOG GENERATION: FAILED - Function returned None")
            return False

    except Exception as e:
        print(f"❌ BOREHOLE LOG GENERATION: FAILED - Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_borehole_log_with_minimal_data():
    """Test with minimal AGS data to see what fails."""
    print("\n" + "=" * 60)
    print("TESTING WITH MINIMAL AGS DATA")
    print("=" * 60)

    try:
        from borehole_log import plot_borehole_log_from_ags_content

        # Minimal AGS data
        minimal_ags = """**LOCA
LOCA_ID,LOCA_NATE,LOCA_NATN
BH001,523456,123456

**GEOL
LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL
BH001,0.0,1.0,CLAY
"""

        print("Testing with minimal AGS data...")

        result = plot_borehole_log_from_ags_content(
            ags_content=minimal_ags, loca_id="BH001"
        )

        print(f"Result: {type(result)}")
        if result:
            print("✅ Minimal data test: SUCCESS")
            return True
        else:
            print("❌ Minimal data test: FAILED")
            return False

    except Exception as e:
        print(f"❌ Minimal data test: FAILED - {e}")
        return False


def test_marker_handling_integration():
    """Test the marker handling integration."""
    print("\n" + "=" * 60)
    print("TESTING MARKER HANDLING INTEGRATION")
    print("=" * 60)

    try:
        from callbacks.marker_handling import MarkerHandlingCallback

        # Create instance
        marker_handler = MarkerHandlingCallback()
        print("✓ MarkerHandlingCallback created")

        # Test the internal method (if accessible)
        if hasattr(marker_handler, "_generate_borehole_log_display"):
            print("✓ _generate_borehole_log_display method found")
            return True
        else:
            print("⚠️ _generate_borehole_log_display method not found")
            return False

    except Exception as e:
        print(f"❌ Marker handling test: FAILED - {e}")
        return False


def main():
    """Run all borehole log tests."""
    print("BOREHOLE LOG DEBUGGING TEST SUITE")
    print("=" * 80)

    results = {
        "basic_generation": test_borehole_log_generation(),
        "minimal_data": test_borehole_log_with_minimal_data(),
        "marker_integration": test_marker_handling_integration(),
    }

    print("\n" + "=" * 80)
    print("BOREHOLE LOG TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")

    print("-" * 40)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All borehole log tests passed!")
        print("The 'No borehole log data available' issue may be:")
        print("- Data format issue in actual AGS files")
        print("- Parameter passing issue in UI interactions")
        print("- Specific location ID not found in data")
    else:
        print("⚠️ Some borehole log tests failed")
        print("This suggests fundamental issues with borehole log generation")

    return results


if __name__ == "__main__":
    main()
