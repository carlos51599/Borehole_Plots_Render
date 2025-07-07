#!/usr/bin/env python3
"""
Integration test to verify file upload and drawing tools work together
"""

import dash
from dash import html, dcc, Output, Input, State
import dash_leaflet as dl
from dash_leaflet import EditControl

print("Testing integrated app with file upload and drawing tools...")
print(f"Dash version: {dash.__version__}")
print(f"Dash-leaflet version: {dl.__version__}")

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Integration Test - File Upload + Drawing Tools"),
        # File upload component
        dcc.Upload(
            id="test-upload",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        # Map with both markers and drawing tools
        dl.Map(
            [
                dl.TileLayer(),
                dl.FeatureGroup(
                    [
                        # Test marker
                        dl.Marker(
                            position=[51.5, -0.1], children=dl.Tooltip("Test Marker")
                        )
                    ],
                    id="test-markers",
                ),
                dl.FeatureGroup(
                    [
                        EditControl(
                            id="test-draw-control",
                            draw={
                                "polyline": True,
                                "polygon": True,
                                "circle": False,
                                "rectangle": True,
                                "marker": False,
                            },
                            edit={"edit": True, "remove": True},
                        ),
                    ],
                    id="test-draw-group",
                ),
            ],
            id="test-map",
            center=[51.5, -0.1],
            zoom=6,
            style={"width": "100%", "height": "400px"},
        ),
        html.Div(id="test-output"),
    ]
)


@app.callback(
    Output("test-output", "children"),
    [Input("test-upload", "contents"), Input("test-draw-control", "n_clicks")],
    [State("test-upload", "filename"), State("test-draw-control", "geojson")],
)
def handle_test(upload_contents, draw_clicks, filenames, geojson):
    outputs = []

    if upload_contents:
        if isinstance(filenames, list):
            outputs.append(
                html.Div(f"Uploaded {len(filenames)} files: {', '.join(filenames)}")
            )
        else:
            outputs.append(html.Div(f"Uploaded: {filenames}"))

    if draw_clicks and geojson and geojson.get("features"):
        num_features = len(geojson["features"])
        outputs.append(html.Div(f"Drew {num_features} shapes"))

    if not outputs:
        return "No activity yet. Try uploading files or drawing shapes."

    return outputs


if __name__ == "__main__":
    print("Starting integration test app...")
    print("Go to http://127.0.0.1:8052 to test")
    app.run(debug=True, host="127.0.0.1", port=8052)
