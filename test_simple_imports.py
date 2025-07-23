"""
Simple test for import updates
"""

try:
    from section import (
        plot_section_from_ags_content,
        parse_ags_geol_section_from_string,
    )

    print("✅ All imports working")
except Exception as e:
    print(f"❌ Error: {e}")
