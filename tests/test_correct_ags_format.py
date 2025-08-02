"""
Test AGS parsing with CORRECT AGS format
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_with_correct_ags_format():
    """Test parsing with correct GROUP/HEADING/DATA format"""
    print("=" * 80)
    print("TESTING WITH CORRECT AGS FORMAT")
    print("=" * 80)

    # CORRECT AGS format with GROUP, HEADING, DATA
    correct_ags = """GROUP,PROJ
HEADING,PROJ_ID,PROJ_NAME,PROJ_LOC
DATA,P001,Test Project,Test Location

GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH001,523456,123456,100.0
DATA,BH002,523466,123466,105.0

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG
DATA,BH001,0.0,1.0,TOPSOIL,TS
DATA,BH001,1.0,3.0,CLAY,CL
DATA,BH001,3.0,5.0,SAND,SA
DATA,BH002,0.0,0.5,TOPSOIL,TS
DATA,BH002,0.5,2.5,CLAY,CL
DATA,BH002,2.5,4.0,GRAVEL,GR

GROUP,ABBR
HEADING,ABBR_CODE,ABBR_DESC
DATA,TS,Topsoil
DATA,CL,Clay
DATA,SA,Sand
DATA,GR,Gravel
"""

    print(f"Correct AGS content length: {len(correct_ags)} characters")

    print("\n" + "=" * 60)
    print("TESTING CURRENT MODULAR PARSING WITH CORRECT FORMAT")
    print("=" * 60)

    try:
        from section.parsing import parse_ags_geol_section_from_string as current_parse

        result = current_parse(correct_ags)
        if isinstance(result, tuple) and len(result) == 3:
            geol_df, loca_df, abbr_df = result
            print(f"✓ Current parsing successful with correct format")
            print(f"  GEOL: {len(geol_df)} rows, columns: {list(geol_df.columns)}")
            print(f"  LOCA: {len(loca_df)} rows, columns: {list(loca_df.columns)}")
            print(f"  ABBR: {len(abbr_df) if abbr_df is not None else 0} rows")

            if not geol_df.empty:
                print(f"  GEOL sample data:")
                for i, row in geol_df.head(3).iterrows():
                    loca_id = row.get("LOCA_ID", "N/A")
                    geol_top = row.get("GEOL_TOP", "N/A")
                    geol_base = row.get("GEOL_BASE", "N/A")
                    geol_geol = row.get("GEOL_GEOL", "N/A")
                    geol_leg = row.get("GEOL_LEG", "N/A")
                    print(
                        f"    {loca_id}: {geol_top}-{geol_base}m {geol_geol} ({geol_leg})"
                    )

            if not loca_df.empty:
                print(f"  LOCA sample data:")
                for i, row in loca_df.head(2).iterrows():
                    loca_id = row.get("LOCA_ID", "N/A")
                    nate = row.get("LOCA_NATE", "N/A")
                    natn = row.get("LOCA_NATN", "N/A")
                    gl = row.get("LOCA_GL", "N/A")
                    print(f"    {loca_id}: E{nate} N{natn} GL{gl}m")

            parsing_success = True
        else:
            print(f"❌ Current parsing failed - unexpected result: {type(result)}")
            parsing_success = False

    except Exception as e:
        print(f"❌ Current parsing failed: {e}")
        import traceback

        traceback.print_exc()
        parsing_success = False

    return correct_ags, parsing_success


def test_plot_with_real_data():
    """Test plot generation with real geological data"""
    print("\n" + "=" * 80)
    print("TESTING PLOT GENERATION WITH REAL DATA")
    print("=" * 80)

    correct_ags, parsing_worked = test_with_correct_ags_format()

    if not parsing_worked:
        print("❌ Cannot test plots - parsing failed")
        return

    print("Testing section plot generation with REAL data...")

    try:
        from section.plotting.main import plot_section_from_ags_content

        # Test with return_base64=False but REAL data this time
        print("Testing return_base64=False with real AGS data...")
        result = plot_section_from_ags_content(correct_ags, return_base64=False)

        if hasattr(result, "savefig"):
            print("✓ Returns matplotlib Figure")
            # Check if it's real data or placeholder
            axes = result.get_axes()
            if axes:
                text_objects = []
                for ax in axes:
                    text_objects.extend(ax.texts)

                placeholder_found = any(
                    "Placeholder" in str(text.get_text()) for text in text_objects
                )
                if placeholder_found:
                    print("🔥 STILL PLACEHOLDER DETECTED even with real data!")
                    for text in text_objects:
                        if "Placeholder" in str(text.get_text()):
                            print(f"  Placeholder text: {text.get_text()}")
                else:
                    print("✅ NO PLACEHOLDER - real geological data rendered!")

                    # Count geological elements
                    patches = []
                    for ax in axes:
                        patches.extend(ax.patches)
                    print(f"  Found {len(patches)} plot patches (geological intervals)")

                    lines = []
                    for ax in axes:
                        lines.extend(ax.lines)
                    print(f"  Found {len(lines)} plot lines (ground surface, etc.)")

            result.savefig("test_real_plot.png", dpi=150, bbox_inches="tight")
            print("✓ Saved test plot to test_real_plot.png")

        else:
            print(f"❌ Does not return Figure: {type(result)}")

    except Exception as e:
        print(f"❌ Plot generation failed: {e}")
        import traceback

        traceback.print_exc()

    print("\nTesting borehole log generation with REAL data...")

    try:
        from borehole_log import plot_borehole_log_from_ags_content

        result = plot_borehole_log_from_ags_content(correct_ags, "BH001")

        if isinstance(result, list) and len(result) > 0:
            print(f"✓ Returns list with {len(result)} items")

            # Check if base64 data looks like a real plot or placeholder
            if result[0] and "data:image" in str(result[0]):
                # Decode and check size as indication of content
                import base64

                try:
                    base64_data = result[0].split(",")[1]
                    img_bytes = base64.b64decode(base64_data)
                    print(f"  Image size: {len(img_bytes)} bytes")

                    if len(img_bytes) < 10000:  # Very small = likely placeholder
                        print(
                            "🔥 SUSPICIOUS: Very small image size suggests placeholder"
                        )
                    else:
                        print("✅ Good image size suggests real geological content")

                except Exception as decode_error:
                    print(f"⚠️ Could not decode base64: {decode_error}")
            else:
                print("❌ Does not contain valid base64 image data")
        else:
            print(
                f"❌ Invalid result: {type(result)}, length: {len(result) if hasattr(result, '__len__') else 'N/A'}"
            )

    except Exception as e:
        print(f"❌ Borehole log generation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("CORRECTED PLACEHOLDER INVESTIGATION")
    print("=" * 80)
    print("Testing with proper AGS GROUP/HEADING/DATA format")
    print("=" * 80)

    test_plot_with_real_data()

    print("\n" + "=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)
