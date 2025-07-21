#!/usr/bin/env python3
"""
Test script to verify the current JavaScript file issues and create a backup
"""


def test_js_file():
    import os

    js_file = "codebase_flowchart.js"
    if os.path.exists(js_file):
        print(f"JavaScript file exists: {js_file}")

        with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        print(f"File size: {len(content)} characters")

        # Check for corruption patterns
        corruption_patterns = [
            "t            </div>",
            "`;chTerm",
            "📍 Preview</h4>",
            "� ${node.code_lines",
        ]

        for pattern in corruption_patterns:
            if pattern in content:
                print(f"Found corruption pattern: {pattern}")

        # Find the line numbers for key functions
        lines = content.split("\n")
        for i, line in enumerate(lines[:50], 1):
            if "showTooltip" in line:
                print(f"showTooltip function at line {i}: {line.strip()}")

    else:
        print(f"JavaScript file not found: {js_file}")


if __name__ == "__main__":
    test_js_file()
