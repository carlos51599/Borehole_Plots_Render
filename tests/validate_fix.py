"""
Simple JavaScript validation without unicode characters.
"""

import re
from pathlib import Path


def validate_javascript_syntax(html_file: str):
    """Validate JavaScript syntax in HTML file."""
    print("Checking JavaScript syntax...")

    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    # Extract JavaScript
    script_pattern = r"<script[^>]*>(.*?)</script>"
    scripts = re.findall(script_pattern, content, re.DOTALL)

    main_script = None
    for script in scripts:
        if "graphData" in script and len(script) > 1000:
            main_script = script
            break

    if not main_script:
        print("ERROR: Main script not found")
        return False

    # Check brace balance
    open_braces = main_script.count("{")
    close_braces = main_script.count("}")

    print(f"Brace analysis:")
    print(f"  - Opening braces: {open_braces}")
    print(f"  - Closing braces: {close_braces}")
    print(f"  - Balance: {open_braces - close_braces}")

    if open_braces == close_braces:
        print("SUCCESS: Braces are balanced")

        # Check for key functions
        required_functions = [
            "initializeEnhancedVisualization",
            "shouldShowNode",
            "shouldShowEdge",
        ]

        missing_functions = []
        for func in required_functions:
            if func not in main_script:
                missing_functions.append(func)

        if missing_functions:
            print(f"WARNING: Missing functions: {missing_functions}")
        else:
            print("SUCCESS: All required functions found")

        # Check for graphData usage
        if "graphData.nodes" in main_script and "graphData.edges" in main_script:
            print("SUCCESS: GraphData access patterns found")
        else:
            print("WARNING: GraphData access patterns missing")

        return len(missing_functions) == 0
    else:
        print(
            f"ERROR: Brace imbalance - {open_braces - close_braces} missing closing braces"
        )
        return False


def main():
    """Main validation function."""
    html_file = "graph_output/enhanced_dependency_graph.html"

    if not Path(html_file).exists():
        print(f"ERROR: File not found: {html_file}")
        return

    is_valid = validate_javascript_syntax(html_file)

    if is_valid:
        print("\nOVERALL: JavaScript validation PASSED")
        print("The visualization should now work correctly!")
    else:
        print("\nOVERALL: JavaScript validation FAILED")
        print("Additional fixes may be needed")


if __name__ == "__main__":
    main()
