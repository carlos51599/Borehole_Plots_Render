#!/usr/bin/env python3
"""
Minimal EditControl test for debugging the featureGroup error
"""

import dash
from dash import html, dcc, Output, Input, State
import dash_leaflet as dl
from dash_leaflet import EditControl

print("=== MINIMAL EDITCONTROL TEST ===")
print(f"Dash version: {dash.__version__}")
print(f"Dash-leaflet version: {dl.__version__}")

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Minimal EditControl Test"),
        html.P("Testing if EditControl works without featureGroup errors"),
        dl.Map(
            [
                dl.TileLayer(),
                dl.FeatureGroup([], id="markers"),
                EditControl(
                    id="edit-control",
                    draw=True,
                    edit=True,
                ),
            ],
            id="map",
            center=[51.5, -0.1],
            zoom=6,
            style={"width": "100%", "height": "400px"},
        ),
        html.Div(id="output"),
    ]
)


@app.callback(
    Output("output", "children"),
    [Input("edit-control", "n_clicks")],
    [State("edit-control", "geojson")],
)
def handle_edit(n_clicks, geojson):
    if n_clicks and geojson:
        return f"EditControl clicked {n_clicks} times. Features: {len(geojson.get('features', []))}"
    return f"EditControl ready. Clicks: {n_clicks or 0}"


if __name__ == "__main__":
    print("Starting minimal test app on port 8052...")
    print("If this works, the issue is in the main app configuration")
    try:
        app.run(debug=True, host="127.0.0.1", port=8052)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
