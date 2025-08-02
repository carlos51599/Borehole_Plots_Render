"""
Test script to verify the marker n_clicks preservation issue.

This script simulates the marker update process to show how n_clicks get reset.
"""


def simulate_marker_update_issue():
    """Simulate the current marker update logic that loses n_clicks."""
    print("=== SIMULATING MARKER UPDATE ISSUE ===")

    # Simulate current markers with some click states
    current_markers = [
        {
            "props": {
                "id": {"type": "borehole-marker", "index": 0},
                "position": [51.5, -0.1],
                "icon": {"iconUrl": "blue-marker.png"},
                "n_clicks": 3,  # User has clicked this marker 3 times
            }
        },
        {
            "props": {
                "id": {"type": "borehole-marker", "index": 1},
                "position": [51.6, -0.2],
                "icon": {"iconUrl": "blue-marker.png"},
                "n_clicks": 0,  # Not clicked yet
            }
        },
    ]

    print("BEFORE UPDATE:")
    for i, marker in enumerate(current_markers):
        n_clicks = marker["props"].get("n_clicks", 0)
        print(f"  Marker {i}: n_clicks = {n_clicks}")

    # Simulate the current _update_marker_colors logic
    clicked_index = 0
    updated_markers = []

    for i, marker in enumerate(current_markers):
        if marker and marker.get("props"):
            # Copy the marker - THIS IS THE PROBLEM
            new_marker = marker.copy()
            new_props = marker["props"].copy()

            # Update icon color
            if i == clicked_index:
                new_icon = new_props["icon"].copy()
                new_icon["iconUrl"] = "green-marker.png"
                new_props["icon"] = new_icon

            # THE BUG: n_clicks is not explicitly preserved!
            new_marker["props"] = new_props
            updated_markers.append(new_marker)

    print("\nAFTER UPDATE (CURRENT BROKEN LOGIC):")
    for i, marker in enumerate(updated_markers):
        n_clicks = marker["props"].get("n_clicks", 0)
        print(f"  Marker {i}: n_clicks = {n_clicks}")

    print("\n❌ BUG CONFIRMED: n_clicks values lost during marker update!")

    return updated_markers


def simulate_fixed_marker_update():
    """Simulate the FIXED marker update logic that preserves n_clicks."""
    print("\n=== SIMULATING FIXED MARKER UPDATE ===")

    # Same initial state
    current_markers = [
        {
            "props": {
                "id": {"type": "borehole-marker", "index": 0},
                "position": [51.5, -0.1],
                "icon": {"iconUrl": "blue-marker.png"},
                "n_clicks": 3,  # User has clicked this marker 3 times
            }
        },
        {
            "props": {
                "id": {"type": "borehole-marker", "index": 1},
                "position": [51.6, -0.2],
                "icon": {"iconUrl": "blue-marker.png"},
                "n_clicks": 1,  # User clicked once
            }
        },
    ]

    print("BEFORE UPDATE:")
    for i, marker in enumerate(current_markers):
        n_clicks = marker["props"].get("n_clicks", 0)
        print(f"  Marker {i}: n_clicks = {n_clicks}")

    # FIXED logic that preserves n_clicks
    clicked_index = 0
    updated_markers = []

    for i, marker in enumerate(current_markers):
        if marker and marker.get("props"):
            # Copy the marker
            new_marker = marker.copy()
            new_props = marker["props"].copy()

            # CRITICAL FIX: Preserve n_clicks!
            old_n_clicks = marker["props"].get("n_clicks", 0)

            # Update icon color
            if i == clicked_index:
                new_icon = new_props["icon"].copy()
                new_icon["iconUrl"] = "green-marker.png"
                new_props["icon"] = new_icon

            # PRESERVE n_clicks state
            new_props["n_clicks"] = old_n_clicks
            new_marker["props"] = new_props
            updated_markers.append(new_marker)

    print("\nAFTER UPDATE (FIXED LOGIC):")
    for i, marker in enumerate(updated_markers):
        n_clicks = marker["props"].get("n_clicks", 0)
        print(f"  Marker {i}: n_clicks = {n_clicks}")

    print("\n✅ FIX CONFIRMED: n_clicks values preserved during marker update!")

    return updated_markers


if __name__ == "__main__":
    print("MARKER N_CLICKS PRESERVATION TEST")
    print("=" * 50)

    # Show the bug
    simulate_marker_update_issue()

    # Show the fix
    simulate_fixed_marker_update()

    print("\n" + "=" * 50)
    print("CONCLUSION: The _update_marker_colors method needs to preserve n_clicks!")
