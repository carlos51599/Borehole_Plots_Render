#!/usr/bin/env python3
"""Test imports for professional modules after archiving old files"""

try:
    from borehole_log_professional import plot_borehole_log_from_ags_content

    print("✓ borehole_log_professional imported successfully")
except Exception as e:
    print(f"✗ borehole_log_professional import failed: {e}")

try:
    from section_plot_professional import plot_section_from_ags_content

    print("✓ section_plot_professional imported successfully")
except Exception as e:
    print(f"✗ section_plot_professional import failed: {e}")

try:
    from geology_code_utils import get_color_and_pattern_for_code

    print("✓ geology_code_utils imported successfully")
except Exception as e:
    print(f"✗ geology_code_utils import failed: {e}")

# Test that old modules are not accessible
try:
    from section_plot import plot_section_from_ags_content

    print("✗ Old section_plot still accessible (should be archived)")
except ImportError:
    print("✓ Old section_plot correctly archived")

try:
    from borehole_log import plot_borehole_log_from_ags_content

    print("✗ Old borehole_log still accessible (should be archived)")
except ImportError:
    print("✓ Old borehole_log correctly archived")

print("\n--- Import Test Complete ---")
