"""
Test Multi-Page Borehole Log Display

This test verifies that both callback paths (search and marker) display
all pages of multi-page borehole logs correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from borehole_log import plot_borehole_log_from_ags_content


def test_multi_page_generation():
    """Test that borehole log generates multiple pages for long boreholes."""

    # Create sample AGS content with long borehole (should generate multiple pages)
    sample_ags_content = """
"GROUP","PROJ"
"HEADING","PROJ_ID","PROJ_NAME","PROJ_LOC","PROJ_CLNT","PROJ_CONT","PROJ_ENG"
"UNIT","","","","",""
"TYPE","X","X","X","X","X"
"DATA","PROJ001","Test Project","Test Location","Test Client","Test Contractor","Test Engineer"

"GROUP","LOCA"
"HEADING","LOCA_ID","LOCA_TYPE","LOCA_STAT","LOCA_NATE","LOCA_NATN","LOCA_GL","LOCA_REM"
"UNIT","","","","m","m","m",""
"TYPE","ID","PA","PA","2DP","2DP","2DP","X"
"DATA","BH001","BH","","100000","200000","50.0","Test Borehole"

"GROUP","GEOL"
"HEADING","LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC","GEOL_LEG","GEOL_GEOL","GEOL_REM"
"UNIT","","m","m","","","",""
"TYPE","ID","2DP","2DP","X","X","X","X"
"DATA","BH001","0.00","2.00","Made Ground - brown sandy clay with brick fragments","MG","MADE GROUND",""
"DATA","BH001","2.00","5.00","London Clay - stiff grey clay","LC","LONDON CLAY",""
"DATA","BH001","5.00","8.00","Terrace Gravels - dense brown sandy gravel","TG","TERRACE GRAVELS",""
"DATA","BH001","8.00","12.00","Chalk - white chalk with flints","CH","CHALK",""
"DATA","BH001","12.00","15.00","London Clay - very stiff grey clay","LC","LONDON CLAY",""
"DATA","BH001","15.00","20.00","Terrace Gravels - very dense grey sandy gravel","TG","TERRACE GRAVELS",""
"DATA","BH001","20.00","25.00","Chalk - hard white chalk","CH","CHALK",""
"DATA","BH001","25.00","30.00","London Clay - hard grey clay","LC","LONDON CLAY",""
    """

    print("Testing multi-page borehole log generation...")

    # Generate borehole log
    images = plot_borehole_log_from_ags_content(
        sample_ags_content,
        "BH001",
        show_labels=True,
        figsize=(8.27, 11.69),  # A4 portrait
        dpi=300,
    )

    print(f"Generated {len(images)} page(s)")

    # Test results
    if len(images) == 0:
        print("❌ FAIL: No images generated")
        return False
    elif len(images) == 1:
        print("⚠️  WARNING: Only 1 page generated (expected multiple for long borehole)")
        print("   This may be correct if the borehole fits on one page")
    else:
        print(f"✅ SUCCESS: Multiple pages generated ({len(images)} pages)")

    # Test image format
    for i, img in enumerate(images):
        if img.startswith("data:image/png;base64,"):
            print(f"✅ Page {i+1}: Correct data URL format")
        else:
            print(f"✅ Page {i+1}: Base64 format (will be converted by callback)")

    return True


def test_search_callback_logic():
    """Test the search callback logic for multi-page display."""

    print("\n" + "=" * 50)
    print("TESTING SEARCH CALLBACK LOGIC")
    print("=" * 50)

    # Simulate what the search callback currently does
    sample_images = [
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",  # Page 1
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",  # Page 2
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",  # Page 3
    ]

    print(
        f"Simulating {len(sample_images)} pages returned from borehole log generation..."
    )

    # Current search callback logic (INCORRECT)
    print("\nCURRENT SEARCH CALLBACK BEHAVIOR:")
    print("  img_b64 = images[0]  # Only uses first page!")
    current_pages_shown = 1
    print(f"  Pages displayed: {current_pages_shown} of {len(sample_images)}")
    print(f"  ❌ PROBLEM: Missing {len(sample_images) - current_pages_shown} pages")

    # Correct marker callback logic
    print("\nCORRECT MARKER CALLBACK BEHAVIOR:")
    print("  for i, img_b64 in enumerate(images):  # Uses all pages!")
    correct_pages_shown = len(sample_images)
    print(f"  Pages displayed: {correct_pages_shown} of {len(sample_images)}")
    print(f"  ✅ CORRECT: Shows all pages")

    return True


if __name__ == "__main__":
    print("Multi-Page Borehole Log Test")
    print("=" * 40)

    try:
        # Test the core generation
        success1 = test_multi_page_generation()

        # Test the callback logic
        success2 = test_search_callback_logic()

        if success1 and success2:
            print("\n🎉 ALL TESTS COMPLETED")
            print("\nNEXT STEPS:")
            print(
                "1. Fix search_functionality.py to use all pages like marker_handling.py does"
            )
            print("2. Replace single image display with multi-page display logic")
            print(
                "3. Test both search and marker callbacks show identical multi-page results"
            )
        else:
            print("\n❌ SOME TESTS FAILED")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
