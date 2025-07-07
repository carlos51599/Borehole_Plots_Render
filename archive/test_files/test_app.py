#!/usr/bin/env python3
"""
Simple test to verify Dash and dash-leaflet work correctly
"""

import dash
from dash import html, dcc, Output, Input, State, ALL
import dash_leaflet as dl
from dash_leaflet import EditControl

print("Testing Dash and dash-leaflet imports...")
print(f"Dash version: {dash.__version__}")
print(f"Dash-leaflet version: {dl.__version__}")

# Create a simple test app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Test App - Dash + Leaflet"),
        html.P("This is a test to verify Dash and dash-leaflet work together."),
        dl.Map(
            [
                dl.TileLayer(),
                dl.FeatureGroup(
                    [
                        EditControl(
                            id="draw-control",
                            draw={
                                "polyline": False,
                                "circle": False,
                                "marker": False,
                            },
                            edit={"edit": True, "remove": True},
                        ),
                    ],
                    id="feature-group",
                ),
            ],
            id="test-map",
            center=[51.5, -0.1],
            zoom=6,
            style={"width": "100%", "height": "400px"},
        ),
        html.Div(id="output"),
    ]
)


@app.callback(Output("output", "children"), Input("draw-control", "geojson"))
def display_geojson(geojson):
    if geojson:
        return f"Drew something: {len(geojson.get('features', []))} features"
    return "No shapes drawn yet"


if __name__ == "__main__":
    print("Starting test app...")
    print("Go to http://127.0.0.1:8051 to test")
    try:
        app.run(debug=True, host="127.0.0.1", port=8051)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
