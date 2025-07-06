#!/usr/bin/env python3
"""
Test script to verify marker creation works correctly
"""

import dash
from dash import html, dcc, Output, Input, State
import dash_leaflet as dl

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Marker Test"),
        html.Button("Add Test Markers", id="add-markers-btn", n_clicks=0),
        dl.Map(
            [
                dl.TileLayer(),
                dl.FeatureGroup([], id="test-markers"),
            ],
            id="test-map",
            center=[51.5, -0.1],
            zoom=6,
            style={"width": "100%", "height": "400px"},
        ),
        html.Div(id="marker-output"),
    ]
)


@app.callback(
    [
        Output("test-markers", "children"),
        Output("test-map", "center"),
        Output("marker-output", "children"),
    ],
    Input("add-markers-btn", "n_clicks"),
)
def add_test_markers(n_clicks):
    if n_clicks == 0:
        return [], [51.5, -0.1], "No markers added yet."

    # Create test markers
    test_markers = [
        dl.Marker(
            position=[51.5, -0.1],
            children=dl.Tooltip("London"),
            id={"type": "test-marker", "index": 0},
        ),
        dl.Marker(
            position=[52.5, -1.9],
            children=dl.Tooltip("Birmingham"),
            id={"type": "test-marker", "index": 1},
        ),
        dl.Marker(
            position=[53.4, -2.2],
            children=dl.Tooltip("Manchester"),
            id={"type": "test-marker", "index": 2},
        ),
    ]

    # Calculate center (median)
    lats = [51.5, 52.5, 53.4]
    lons = [-0.1, -1.9, -2.2]

    import statistics

    center_lat = statistics.median(lats)
    center_lon = statistics.median(lons)

    return (
        test_markers,
        [center_lat, center_lon],
        f"Added {len(test_markers)} test markers, centered at [{center_lat:.2f}, {center_lon:.2f}]",
    )


if __name__ == "__main__":
    print("Starting marker test app...")
    print("Go to http://127.0.0.1:8053 to test markers")
    app.run(debug=True, host="127.0.0.1", port=8053)
