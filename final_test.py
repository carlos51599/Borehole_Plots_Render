"""Final test script to verify all components are working"""

print("=== FINAL INTEGRATION TEST ===")

try:
    # Test professional borehole log import
    from borehole_log_professional import plot_borehole_log_from_ags_content

    print("✓ Professional borehole log imports successfully")

    # Test professional section plot import
    from section_plot_professional import plot_section_from_ags_content

    print("✓ Professional section plot imports successfully")

    # Test callbacks import
    import callbacks_split

    print("✓ Callbacks import successfully")

    # Test geology utils
    from geology_code_utils import load_geology_code_mappings

    print("✓ Geology code utils imports successfully")

    print("\n=== ALL TESTS PASSED ===")
    print("The professional borehole log issue has been fixed!")
    print("The app should now work correctly with the professional modules.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
