#!/usr/bin/env python3
"""
Simple test to verify EditControl is properly registered
"""

import dash
from dash import html, dcc, Output, Input
import dash_leaflet as dl
from dash_leaflet import EditControl

print("Testing EditControl registration...")
print(f"Dash version: {dash.__version__}")
print(f"Dash-leaflet version: {dl.__version__}")

# Create a minimal test app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("EditControl Test"),
        html.P("This tests if EditControl can be properly registered."),
        dl.Map(
            [
                dl.TileLayer(),
                EditControl(
                    id="test-draw-control",
                    draw={
                        "polyline": False,
                        "circle": False,
                        "marker": False,
                        "rectangle": True,
                        "polygon": True,
                    },
                    edit={"edit": True, "remove": True},
                ),
                dl.FeatureGroup([], id="test-feature-group"),
            ],
            id="test-map",
            center=[51.5, -0.1],
            zoom=6,
            style={"width": "100%", "height": "400px"},
        ),
        html.Div(id="test-output"),
    ]
)


@app.callback(Output("test-output", "children"), Input("test-draw-control", "geojson"))
def display_geojson(geojson):
    if geojson:
        return f"EditControl working! Features: {len(geojson.get('features', []))}"
    return "EditControl registered, waiting for shapes..."


if __name__ == "__main__":
    print("Starting EditControl test app...")
    print("Go to http://127.0.0.1:8051")
    try:
        app.run(debug=True, host="127.0.0.1", port=8051)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
