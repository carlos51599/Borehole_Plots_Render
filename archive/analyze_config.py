"""
Analyze config.py structure to understand how to modularize it.
"""

import re


def analyze_config_structure():
    """Analyze the config.py file structure."""

    with open("config.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Find all section headers
    sections = re.findall(r"# ===== (.+) =====", content)
    print("Config sections found:")
    for i, section in enumerate(sections, 1):
        print(f"{i}. {section}")

    # Count lines in each section
    lines = content.split("\n")
    section_lines = {}
    current_section = None

    for line in lines:
        if line.strip().startswith("# ===== ") and line.strip().endswith(" ====="):
            current_section = line.strip()[8:-6].strip()
            section_lines[current_section] = 0
        elif current_section and line.strip() and not line.strip().startswith("#"):
            section_lines[current_section] += 1

    print("\nNon-comment lines per section:")
    for section, count in section_lines.items():
        print(f"{section}: ~{count} lines")

    # Find all constants
    constants = re.findall(r"^[A-Z_]+ = ", content, re.MULTILINE)
    print(f"\nTotal constants found: {len(constants)}")

    # Find style dictionaries
    style_dicts = re.findall(r"^[A-Z_]+_STYLE = \{", content, re.MULTILINE)
    print(f"Style dictionaries found: {len(style_dicts)}")


if __name__ == "__main__":
    analyze_config_structure()
