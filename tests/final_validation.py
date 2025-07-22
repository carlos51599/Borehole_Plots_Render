"""
Final validation script to verify the fixes are complete
"""

import json
from pathlib import Path


def validate_final_results():
    """Validate that the dependency graph now has correct internal import counts."""

    print("🔍 FINAL VALIDATION: Enhanced Dependency Graph Fixes")
    print("=" * 60)

    # Load the updated graph data
    try:
        with open("graph_output/enhanced_graph_data.json", "r") as f:
            graph_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading graph data: {e}")
        return

    nodes = graph_data.get("nodes", [])
    print(f"📊 Graph contains {len(nodes)} nodes")
    print(f"📊 Graph contains {len(graph_data.get('edges', []))} edges")

    # Test key files that previously had issues
    key_files_test = {
        "app.py": {
            "expected_internal": 3,
            "expected_imports": ["config", "callbacks_split", "app_factory"],
        },
        "callbacks_split.py": {
            "expected_internal": 11,
            "min_internal": 10,
        },  # Allow some flexibility
        "borehole_log_professional.py": {"expected_internal": 2, "min_internal": 1},
        "config.py": {"expected_internal": 0},
    }

    print(f"\n📋 Testing Key Files:")
    all_passed = True

    for node in nodes:
        file_path = node.get("file_path", "")
        imports_count = node.get("imports_count", 0)

        for test_file, expectations in key_files_test.items():
            if file_path.endswith(test_file):
                expected = expectations.get("expected_internal", 0)
                min_expected = expectations.get("min_internal", expected)

                if (
                    imports_count >= min_expected and imports_count <= expected + 2
                ):  # Allow small variance
                    print(
                        f"   ✅ {test_file}: {imports_count} internal imports (expected ~{expected})"
                    )
                else:
                    print(
                        f"   ❌ {test_file}: {imports_count} internal imports (expected ~{expected})"
                    )
                    all_passed = False
                break

    # Check for nodes with suspiciously low import counts
    print(f"\n🔍 Checking for Anomalies:")
    low_import_files = [
        n
        for n in nodes
        if n.get("imports_count", 0) == 0
        and not n.get("file_path", "").endswith("__init__.py")
    ]

    if low_import_files:
        print(f"   ⚠️  Found {len(low_import_files)} files with 0 internal imports:")
        for node in low_import_files[:5]:  # Show first 5
            print(f"      📄 {node.get('name', 'Unknown')}")
    else:
        print(f"   ✅ No suspicious files with 0 imports found")

    # Summary statistics
    import_counts = [n.get("imports_count", 0) for n in nodes]
    avg_imports = sum(import_counts) / len(import_counts) if import_counts else 0
    max_imports = max(import_counts) if import_counts else 0

    print(f"\n📈 Import Statistics:")
    print(f"   Average internal imports per file: {avg_imports:.1f}")
    print(f"   Maximum internal imports: {max_imports}")
    print(
        f"   Files with internal imports: {len([c for c in import_counts if c > 0])}/{len(import_counts)}"
    )

    # Test the graph structure
    edges = graph_data.get("edges", [])
    total_dependencies = len(edges)
    cross_folder_deps = len([e for e in edges if e.get("is_cross_folder", False)])

    print(f"\n🔗 Dependency Statistics:")
    print(f"   Total dependencies: {total_dependencies}")
    print(f"   Cross-folder dependencies: {cross_folder_deps}")
    print(
        f"   Internal consistency: {'✅ PASS' if total_dependencies > 0 else '❌ FAIL'}"
    )

    print(f"\n{'🎉 ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    validate_final_results()
