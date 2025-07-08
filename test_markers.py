#!/usr/bin/env python3
"""
Test script to verify the polyline marker removal
"""

from polyline_utils import create_polyline_section

# Test polyline data
polyline_feature = {
    "geometry": {"coordinates": [[-0.1278, 51.5074], [-0.1258, 51.5094]]}
}

# Create polyline section
components = create_polyline_section(polyline_feature)
print(f"Number of components returned: {len(components)}")

# Check component types
for i, component in enumerate(components):
    print(f"Component {i}: {type(component).__name__}")
    if hasattr(component, "children"):
        print(f"  Children: {component.children}")

if len(components) == 1:
    print("✅ Test PASSED: Only polyline component returned (no markers)")
else:
    print("❌ Test FAILED: Expected 1 component, got", len(components))
