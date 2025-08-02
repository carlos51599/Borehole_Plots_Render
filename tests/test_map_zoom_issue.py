"""
Test Script: Dash-Leaflet Map Center and Zoom Update Issue

This test demonstrates the dash-leaflet bug where map center and zoom properties
can be updated via callbacks but don't visually update in the browser.

Based on research findings:
- Issue #239: "Map style not updating" shows similar behavior
- Properties are updated in callback returns but not reflected on webpage
- This is a known issue with dash-leaflet component property updates
"""

import dash
from dash import html, dcc, Output, Input, State
import dash_leaflet as dl
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test coordinates for different locations
test_locations = [
    {"name": "London", "center": [51.5074, -0.1278], "zoom": 10},
    {"name": "Manchester", "center": [53.4808, -2.2426], "zoom": 11},
    {"name": "Edinburgh", "center": [55.9533, -3.1883], "zoom": 12},
    {"name": "Cardiff", "center": [51.4816, -3.1791], "zoom": 13},
]

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Dash-Leaflet Map Center/Zoom Update Test"),
        html.Div(
            [
                html.P(
                    "Testing whether map center and zoom properties update visually when changed via callback:"
                ),
                html.Ul(
                    [
                        html.Li("Click buttons to change map center and zoom"),
                        html.Li("Watch console for callback outputs"),
                        html.Li("Observe if map actually moves/zooms in browser"),
                    ]
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        # Test buttons
        html.Div(
            [
                html.Button(
                    f"Go to {loc['name']} (Zoom {loc['zoom']})",
                    id={"type": "location-btn", "index": i},
                    n_clicks=0,
                    style={"margin": "5px"},
                )
                for i, loc in enumerate(test_locations)
            ],
            style={"marginBottom": "20px"},
        ),
        # Status display
        html.Div(
            id="status-display",
            style={
                "backgroundColor": "#f0f0f0",
                "padding": "10px",
                "borderRadius": "5px",
                "marginBottom": "20px",
            },
        ),
        # The map
        dl.Map(
            id="test-map",
            children=[
                dl.TileLayer(),
                # Add some test markers
                dl.Marker(position=[51.5074, -0.1278], children=[dl.Tooltip("London")]),
                dl.Marker(
                    position=[53.4808, -2.2426], children=[dl.Tooltip("Manchester")]
                ),
                dl.Marker(
                    position=[55.9533, -3.1883], children=[dl.Tooltip("Edinburgh")]
                ),
                dl.Marker(
                    position=[51.4816, -3.1791], children=[dl.Tooltip("Cardiff")]
                ),
            ],
            style={"width": "100%", "height": "60vh"},
            center=[54.0, -2.0],  # Start centered on UK
            zoom=6,
        ),
    ]
)


@app.callback(
    [
        Output("test-map", "center"),
        Output("test-map", "zoom"),
        Output("status-display", "children"),
    ],
    [Input({"type": "location-btn", "index": dash.ALL}, "n_clicks")],
    [State("test-map", "center"), State("test-map", "zoom")],
)
def update_map_location(n_clicks_list, current_center, current_zoom):
    """Update map center and zoom based on button clicks."""

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, "Click a button to test map updates"

    # Find which button was clicked
    button_id = ctx.triggered[0]["prop_id"]

    try:
        # Parse the button index from the triggered prop_id
        import json

        button_info = json.loads(button_id.split(".")[0])
        button_index = button_info["index"]

        # Get the target location
        target_location = test_locations[button_index]
        new_center = target_location["center"]
        new_zoom = target_location["zoom"]

        logger.info(f"=== MAP UPDATE CALLBACK ===")
        logger.info(f"Button clicked: {target_location['name']}")
        logger.info(f"Current center: {current_center}, zoom: {current_zoom}")
        logger.info(f"New center: {new_center}, zoom: {new_zoom}")
        logger.info(f"Returning new values to map component...")

        status_msg = html.Div(
            [
                html.H4("🗺️ Map Update Test Results:", style={"color": "#007bff"}),
                html.P(f"✅ Button clicked: {target_location['name']}"),
                html.P(f"✅ Callback executed successfully"),
                html.P(f"✅ Previous center: {current_center}, zoom: {current_zoom}"),
                html.P(f"✅ New center: {new_center}, zoom: {new_zoom}"),
                html.P(
                    "❓ Did the map actually move? (Check visually)",
                    style={"fontWeight": "bold", "color": "#dc3545"},
                ),
                html.P(
                    "❓ If map didn't move, this confirms the dash-leaflet bug",
                    style={"fontWeight": "bold", "color": "#dc3545"},
                ),
            ]
        )

        return new_center, new_zoom, status_msg

    except Exception as e:
        logger.error(f"Error in callback: {e}")
        error_msg = html.Div(
            [
                html.H4("❌ Callback Error", style={"color": "red"}),
                html.P(f"Error: {e}"),
            ]
        )
        return dash.no_update, dash.no_update, error_msg


if __name__ == "__main__":
    print("Starting Dash-Leaflet Map Update Test...")
    print("This test will help identify if map center/zoom updates work properly.")
    print("\nInstructions:")
    print("1. Open browser to http://127.0.0.1:8050/")
    print("2. Click the location buttons")
    print("3. Watch both the console output AND the map")
    print("4. If console shows updates but map doesn't move, the bug is confirmed")

    app.run(debug=True, port=8050)
