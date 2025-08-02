"""
Test AGS parsing to identify where real data is being lost
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_original_vs_current_parsing():
    """Test original parsing vs current modular parsing"""
    print("=" * 80)
    print("TESTING AGS PARSING: ORIGINAL VS CURRENT")
    print("=" * 80)

    # Sample AGS content that should work
    sample_ags = """**PROJ
HEAD,1,AGS4,AGS 4.1.1,Test Project
**LOCA
LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
BH001,523456,123456,100.0
BH002,523466,123466,105.0
**GEOL
LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG
BH001,0.0,1.0,TOPSOIL,TS
BH001,1.0,3.0,CLAY,CL
BH001,3.0,5.0,SAND,SA
BH002,0.0,0.5,TOPSOIL,TS
BH002,0.5,2.5,CLAY,CL
BH002,2.5,4.0,GRAVEL,GR
**ABBR
ABBR_CODE,ABBR_DESC
TS,Topsoil
CL,Clay
SA,Sand
GR,Gravel
"""

    print(f"Sample AGS content length: {len(sample_ags)} characters")
    print("\n" + "=" * 60)
    print("TESTING ORIGINAL ARCHIVE PARSING")
    print("=" * 60)

    try:
        # Test original parsing from archive
        sys.path.insert(0, os.path.join(project_root, "archive"))
        from section_plot_professional_original import (
            parse_ags_geol_section_from_string as original_parse,
        )

        result = original_parse(sample_ags)
        if isinstance(result, tuple) and len(result) == 3:
            geol_df, loca_df, abbr_df = result
            print(f"✓ Original parsing successful")
            print(f"  GEOL: {len(geol_df)} rows, columns: {list(geol_df.columns)}")
            print(f"  LOCA: {len(loca_df)} rows, columns: {list(loca_df.columns)}")
            print(f"  ABBR: {len(abbr_df) if abbr_df is not None else 0} rows")

            if not geol_df.empty:
                print(f"  GEOL sample data:")
                for i, row in geol_df.head(3).iterrows():
                    print(
                        f"    {row.get('LOCA_ID', 'N/A')}: {row.get('GEOL_TOP', 'N/A')}-{row.get('GEOL_BASE', 'N/A')}m {row.get('GEOL_GEOL', 'N/A')} ({row.get('GEOL_LEG', 'N/A')})"
                    )

            original_success = True
        else:
            print(
                f"❌ Original parsing failed - unexpected result format: {type(result)}"
            )
            original_success = False

    except Exception as e:
        print(f"❌ Original parsing failed: {e}")
        import traceback

        traceback.print_exc()
        original_success = False

    print("\n" + "=" * 60)
    print("TESTING CURRENT MODULAR PARSING")
    print("=" * 60)

    try:
        # Test current modular parsing
        sys.path.insert(0, project_root)
        from section.parsing import parse_ags_geol_section_from_string as current_parse

        result = current_parse(sample_ags)
        if isinstance(result, tuple) and len(result) == 3:
            geol_df, loca_df, abbr_df = result
            print(f"✓ Current parsing successful")
            print(f"  GEOL: {len(geol_df)} rows, columns: {list(geol_df.columns)}")
            print(f"  LOCA: {len(loca_df)} rows, columns: {list(loca_df.columns)}")
            print(f"  ABBR: {len(abbr_df) if abbr_df is not None else 0} rows")

            if not geol_df.empty:
                print(f"  GEOL sample data:")
                for i, row in geol_df.head(3).iterrows():
                    print(
                        f"    {row.get('LOCA_ID', 'N/A')}: {row.get('GEOL_TOP', 'N/A')}-{row.get('GEOL_BASE', 'N/A')}m {row.get('GEOL_GEOL', 'N/A')} ({row.get('GEOL_LEG', 'N/A')})"
                    )

            current_success = True
        else:
            print(
                f"❌ Current parsing failed - unexpected result format: {type(result)}"
            )
            current_success = False

    except Exception as e:
        print(f"❌ Current parsing failed: {e}")
        import traceback

        traceback.print_exc()
        current_success = False

    print("\n" + "=" * 80)
    print("PARSING COMPARISON SUMMARY")
    print("=" * 80)

    if original_success and current_success:
        print("✅ Both parsers working - investigate plot generation next")
    elif original_success and not current_success:
        print("🔥 CRITICAL: Original works, current broken - parser issue identified")
    elif not original_success and current_success:
        print("⚠️ Original broken, current works - may be environment issue")
    else:
        print("❌ Both parsers broken - fundamental AGS parsing issue")

    return original_success, current_success


def test_plot_generation_paths():
    """Test the plot generation paths to find placeholder sources"""
    print("\n" + "=" * 80)
    print("TESTING PLOT GENERATION PATHS")
    print("=" * 80)

    sample_ags = """**LOCA
LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
BH001,523456,123456,100.0
**GEOL
LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL,GEOL_LEG
BH001,0.0,1.0,CLAY,CL
BH001,1.0,2.0,SAND,SA
"""

    print("Testing current section plot generation...")

    try:
        from section.plotting.main import plot_section_from_ags_content

        # Test with return_base64=False (this triggers placeholder in current code)
        print("Testing return_base64=False...")
        result = plot_section_from_ags_content(sample_ags, return_base64=False)

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
                    print("🔥 PLACEHOLDER DETECTED in Figure mode!")
                    for text in text_objects:
                        if "Placeholder" in str(text.get_text()):
                            print(f"  Placeholder text: {text.get_text()}")
                else:
                    print("✓ No placeholder text found")

            result.savefig("test_plot.png", dpi=150, bbox_inches="tight")
            print("✓ Saved test plot to test_plot.png")

        else:
            print(f"❌ Does not return Figure: {type(result)}")

    except Exception as e:
        print(f"❌ Plot generation failed: {e}")
        import traceback

        traceback.print_exc()

    print("\nTesting borehole log generation...")

    try:
        from borehole_log import plot_borehole_log_from_ags_content

        result = plot_borehole_log_from_ags_content(sample_ags, "BH001")

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
                        print("✓ Reasonable image size suggests real content")

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
    print("PLACEHOLDER INVESTIGATION - SYSTEMATIC DEBUG")
    print("=" * 80)

    # Test parsing first
    original_works, current_works = test_original_vs_current_parsing()

    # Test plot generation
    test_plot_generation_paths()

    print("\n" + "=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)
    print("Next steps based on findings above...")
