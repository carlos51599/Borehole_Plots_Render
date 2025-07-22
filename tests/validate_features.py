#!/usr/bin/env python3
"""
Validation script for dependency graph features.
Tests all implemented functionality systematically.
"""

import json
import os
from pathlib import Path


def validate_features():
    """Validate all implemented features."""
    base_dir = Path(__file__).parent
    svg_file = base_dir / "graph_output" / "graph.svg"
    dot_file = base_dir / "graph_output" / "graph.dot"
    json_file = base_dir / "graph_output" / "graph_folders.json"

    print("🔍 Validating dependency graph features...")
    print("=" * 50)

    # Check if all files exist
    files_to_check = [svg_file, dot_file, json_file]
    for file_path in files_to_check:
        if file_path.exists():
            print(f"✅ {file_path.name} exists")
        else:
            print(f"❌ {file_path.name} missing")
            return False

    # Validate JSON structure
    print("\n📊 Validating subfolder data...")
    try:
        with open(json_file, "r") as f:
            subfolder_data = json.load(f)

        print(f"✅ Found {len(subfolder_data)} subfolders:")
        total_modules = 0
        for folder, info in subfolder_data.items():
            module_count = len(info["modules"])
            total_modules += module_count
            color = info["color"]
            print(f"   📁 {folder}: {module_count} modules, color: {color}")

        print(f"📈 Total modules: {total_modules}")

    except Exception as e:
        print(f"❌ Error validating JSON: {e}")
        return False

    # Validate DOT file has colors
    print("\n🎨 Validating colored nodes in DOT file...")
    try:
        with open(dot_file, "r") as f:
            dot_content = f.read()

        # Check for fillcolor attributes
        fillcolor_count = dot_content.count("fillcolor=")
        if fillcolor_count > 0:
            print(f"✅ Found {fillcolor_count} nodes with fillcolor attributes")
        else:
            print("❌ No fillcolor attributes found in DOT file")
            return False

    except Exception as e:
        print(f"❌ Error validating DOT file: {e}")
        return False

    # Validate SVG has interactive elements
    print("\n🖱️ Validating interactive elements in SVG...")
    try:
        with open(svg_file, "r", encoding="utf-8") as f:
            svg_content = f.read()

        required_elements = [
            'class="legend"',
            "checkbox-",
            "findDirectPath",
            "toggleFolder",
            "updateFolderVisibility",
            "highlighted",
            "dimmed",
        ]

        for element in required_elements:
            if element in svg_content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
                return False

    except Exception as e:
        print(f"❌ Error validating SVG file: {e}")
        return False

    print("\n🎉 All features validated successfully!")
    print("\n📋 Manual testing checklist:")
    print("1. Open graph.svg in a web browser")
    print("2. Verify nodes have different colors for different subfolders")
    print("3. Check legend shows all subfolders with checkboxes")
    print("4. Click checkboxes to hide/show nodes from subfolders")
    print("5. Click any node to highlight ALL connected nodes (transitive)")
    print("6. Verify edges are dimmed/highlighted appropriately")

    return True


if __name__ == "__main__":
    success = validate_features()
    exit(0 if success else 1)
