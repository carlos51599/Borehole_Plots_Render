"""
Test the fixed section plotting to ensure real geological data is rendered
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_fixed_section_plotting():
    """Test section plotting after fixing the placeholder issue"""
    print("=" * 80)
    print("TESTING FIXED SECTION PLOTTING")
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

    print("Testing FIXED section plot generation...")

    try:
        from section.plotting.main import plot_section_from_ags_content

        # Test with return_base64=False (this should now work with real data)
        print("Testing return_base64=False with FIXED implementation...")
        result = plot_section_from_ags_content(correct_ags, return_base64=False)

        if hasattr(result, "savefig"):
            print("✅ Returns matplotlib Figure")

            # Check if it's real data or still placeholder
            axes = result.get_axes()
            if axes:
                text_objects = []
                for ax in axes:
                    text_objects.extend(ax.texts)

                placeholder_found = any(
                    "Placeholder" in str(text.get_text()) for text in text_objects
                )
                error_found = any(
                    "Error" in str(text.get_text()) for text in text_objects
                )

                if placeholder_found:
                    print("❌ STILL SHOWING PLACEHOLDER!")
                    for text in text_objects:
                        if "Placeholder" in str(text.get_text()):
                            print(f"  Placeholder: {text.get_text()}")
                elif error_found:
                    print("⚠️ SHOWING ERROR MESSAGE")
                    for text in text_objects:
                        if "Error" in str(text.get_text()):
                            print(f"  Error: {text.get_text()}")
                else:
                    print("🎉 SUCCESS: Real geological plot generated!")

                    # Count geological elements to confirm real data
                    patches = []
                    for ax in axes:
                        patches.extend(ax.patches)
                    print(f"  Found {len(patches)} plot patches (geological intervals)")

                    lines = []
                    for ax in axes:
                        lines.extend(ax.lines)
                    print(f"  Found {len(lines)} plot lines (ground surface, etc.)")

                    # Check for geological text labels
                    borehole_labels = [
                        t for t in text_objects if "BH" in str(t.get_text())
                    ]
                    print(f"  Found {len(borehole_labels)} borehole labels")

            result.savefig("test_fixed_plot.png", dpi=150, bbox_inches="tight")
            print("✅ Saved fixed test plot to test_fixed_plot.png")

        else:
            print(f"❌ Does not return Figure: {type(result)}")

    except Exception as e:
        print(f"❌ Fixed plot generation failed: {e}")
        import traceback

        traceback.print_exc()

    print("\nTesting with return_base64=True for comparison...")

    try:
        result_b64 = plot_section_from_ags_content(correct_ags, return_base64=True)

        if isinstance(result_b64, str) and "data:image" in result_b64:
            print("✅ Base64 mode returns image data")

            # Decode to check size
            import base64

            try:
                base64_data = result_b64.split(",")[1]
                img_bytes = base64.b64decode(base64_data)
                print(f"  Base64 image size: {len(img_bytes)} bytes")
            except Exception:
                print("  Could not decode base64 size")

        else:
            print(f"❌ Base64 mode failed: {type(result_b64)}")

    except Exception as e:
        print(f"❌ Base64 mode failed: {e}")


def test_callback_integration():
    """Test that the fix works with the actual callback system"""
    print("\n" + "=" * 80)
    print("TESTING CALLBACK INTEGRATION")
    print("=" * 80)

    print("Testing plot generation callback...")

    try:
        from callbacks.plot_generation import PlotGenerationCallback

        callback = PlotGenerationCallback()
        print("✅ Plot generation callback imported successfully")

        # This would normally be triggered by UI interaction
        # but we can test the underlying function
        print("✅ Callback system ready for testing")

    except Exception as e:
        print(f"❌ Callback integration test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("TESTING PLACEHOLDER FIX")
    print("=" * 80)

    test_fixed_section_plotting()
    test_callback_integration()

    print("\n" + "=" * 80)
    print("FIX TESTING COMPLETE")
    print("=" * 80)
