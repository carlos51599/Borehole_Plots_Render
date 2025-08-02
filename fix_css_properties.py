"""
Fix CSS property names in Dash style dictionaries.
Converts kebab-case properties to camelCase for React compatibility.
"""

import os
import re


def fix_style_properties_in_file(filepath):
    """Fix CSS property names in a Python file."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix border-radius -> borderRadius
        content = re.sub(r'"border-radius":', '"borderRadius":', content)

        # Fix background-color -> backgroundColor
        content = re.sub(r'"background-color":', '"backgroundColor":', content)

        # Could add more CSS property fixes here if needed:
        # content = re.sub(r'"font-size":', '"fontSize":', content)
        # content = re.sub(r'"text-align":', '"textAlign":', content)
        # etc.

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Fixed style properties in: {filepath}")
            return True
        else:
            print(f"ℹ️  No changes needed in: {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    """Main function to fix CSS properties across the codebase."""
    print("=== CSS Property Fix ===")
    print("Converting kebab-case to camelCase for React/Dash compatibility...\n")

    # List of files to fix (excluding test files and archive)
    files_to_fix = [
        "callbacks/file_upload_enhanced.py",
        "callbacks/file_upload/ui_components.py",
        "app_constants.py",
        "loading_indicators.py",
    ]

    base_dir = r"c:\Users\dea29431\OneDrive - Rsk Group Limited\Documents\Geotech\AGS Section\Geo_Borehole_Sections_Render"

    fixed_count = 0
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if fix_style_properties_in_file(full_path):
            fixed_count += 1

    print(f"\n=== Summary ===")
    print(f"Fixed {fixed_count} files")
    print("CSS property conversion completed!")


if __name__ == "__main__":
    main()
