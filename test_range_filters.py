#!/usr/bin/env python3
"""
Test script to validate the range filter implementation
"""
import sys
import os
from pathlib import Path

# Add the dependency graph modules to the path
sys.path.insert(0, str(Path(__file__).parent / "dependency_graph"))


def test_imports():
    """Test that main module imports correctly"""
    try:
        from dependency_graph.graph_modules.html_generator import main

        print("✅ Main imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_graph_generation():
    """Test that the graph can be generated with the range filters"""
    try:
        # Get the current workspace root
        current_dir = Path(__file__).parent

        # Run the graph generator with our current directory
        from dependency_graph.graph_modules.html_generator import main

        output_file = main(str(current_dir))

        if Path(output_file).exists():
            print(f"✅ Graph HTML generated successfully: {output_file}")

            # Check if the HTML contains the range filter elements
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            required_elements = [
                "predecessors-min-filter",
                "predecessors-max-filter",
                "successors-min-filter",
                "successors-max-filter",
                "size-min-filter",
                "size-max-filter",
                "predecessorsRangeFilter",
                "successorsRangeFilter",
                "sizeRangeFilter",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)

            if missing_elements:
                print(f"❌ Missing elements in HTML: {missing_elements}")
                return False
            else:
                print("✅ All range filter elements present in HTML")
                return True
        else:
            print(f"❌ Graph HTML file not found: {output_file}")
            return False

    except Exception as e:
        print(f"❌ Graph generation error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Range Filter Implementation...")
    print("=" * 50)

    # Test imports
    if not test_imports():
        sys.exit(1)

    # Test graph generation
    if not test_graph_generation():
        sys.exit(1)

    print("=" * 50)
    print("✅ All tests passed! Range filter implementation is working correctly.")
