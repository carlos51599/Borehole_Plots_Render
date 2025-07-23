"""
Clientside callbacks for browser-side functionality.

This module contains all clientside callbacks that run in the browser
for better performance, including theme switching and shape handling.
"""

import dash
from dash import dcc
import logging


def register_theme_callbacks(app):
    """
    Register theme switching clientside callbacks.

    Args:
        app (dash.Dash): The Dash application instance
    """
    # Theme switching callback - handles light/dark theme toggle
    app.clientside_callback(
        """
        function(light_clicks, dark_clicks) {
            console.log('=== THEME CALLBACK TRIGGERED ===');
            console.log('Light clicks:', light_clicks);
            console.log('Dark clicks:', dark_clicks);
            
            // Determine which button was clicked
            const ctx = window.dash_clientside.callback_context;
            console.log('Callback context:', ctx);
            
            if (!ctx.triggered.length) {
                console.log('No triggers found');
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            
            const button_id = ctx.triggered[0].prop_id.split('.')[0];
            console.log('Button clicked:', button_id);
            
            if (button_id === 'light-theme-btn') {
                // Switch to light theme
                console.log('Switching to LIGHT theme');
                document.body.className = 'light-theme';
                console.log('Body className after change:', document.body.className);
                console.log('Computed background image:', window.getComputedStyle(document.body).backgroundImage);
                return ['theme-toggle-btn sun-icon active', 'theme-toggle-btn moon-icon'];
            } else if (button_id === 'dark-theme-btn') {
                // Switch to dark theme
                console.log('Switching to DARK theme');
                document.body.className = '';
                console.log('Body className after change:', document.body.className);
                console.log('Computed background image:', window.getComputedStyle(document.body).backgroundImage);
                return ['theme-toggle-btn sun-icon', 'theme-toggle-btn moon-icon active'];
            }
            
            console.log('Unknown button clicked');
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        """,
        [
            dash.Output("light-theme-btn", "className"),
            dash.Output("dark-theme-btn", "className"),
        ],
        [
            dash.Input("light-theme-btn", "n_clicks"),
            dash.Input("dark-theme-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )

    # Theme logo swapper callback - changes logo based on selected theme
    app.clientside_callback(
        """
        function(light_clicks, dark_clicks) {
            // Existing theme logic
            const ctx = window.dash_clientside.callback_context;
            if (!ctx.triggered.length) {
                return window.dash_clientside.no_update;
            }
            const button_id = ctx.triggered[0].prop_id.split('.')[0];
            var logo = document.querySelector('.logo-image');
            if (button_id === 'light-theme-btn') {
                if (logo) logo.src = 'assets/BinniesLogoDark.png';
            } else if (button_id === 'dark-theme-btn') {
                if (logo) logo.src = 'assets/BinniesLogo.png';
            }
            return window.dash_clientside.no_update;
        }
        """,
        dash.Output("logo-container", "children"),
        [
            dash.Input("light-theme-btn", "n_clicks"),
            dash.Input("dark-theme-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )


def register_shape_handling_callbacks(app):
    """
    Register shape handling clientside callbacks for map drawing tools.

    Args:
        app (dash.Dash): The Dash application instance
    """
    # Primary callback: When a new shape is drawn, keep only the latest and update the draw-state-store
    app.clientside_callback(
        """
        function(geojson, oldState) {
            console.log("==== SHAPE CALLBACK TRIGGERED ====");
            if (!geojson || !geojson.features) {
                console.log("No geojson or features available");
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            const timestamp = new Date().getTime();
            console.log(`Time: ${timestamp}, Features count: ${geojson.features.length}`);
            if (geojson.features.length === 0) {
                console.log("No features to process");
                return [window.dash_clientside.no_update, oldState];
            }
            // Only process if it's actually a new shape (check timestamp)
            if (oldState && (timestamp - oldState.lastUpdate < 500)) {
                console.log("Ignoring rapid consecutive updates");
                return [window.dash_clientside.no_update, oldState];
            }
            console.log("Processing new shape, clearing old shapes");
            // Keep only the most recent feature
            const latestFeature = geojson.features[geojson.features.length - 1];
            console.log(`Latest feature type: ${latestFeature.geometry.type}`);
            // Create new state
            const newState = {
                lastUpdate: timestamp,
                featureCount: 1,
                featureType: latestFeature.geometry.type
            };
            // Return the new state with the timestamp to trigger clear_all in the next callback
            return [
                {
                    type: 'FeatureCollection',
                    features: [latestFeature]
                },
                newState
            ];
        }
        """,
        [
            dash.Output("draw-control", "geojson"),
            dash.Output("draw-state-store", "data"),
        ],
        [dash.Input("draw-control", "geojson")],
        [dash.State("draw-state-store", "data")],
        prevent_initial_call=True,
    )

    # Secondary callback: Use state changes to clear all layers
    app.clientside_callback(
        """
        function(state) {
            console.log("==== CLEAR LAYERS CALLBACK ====");
            if (!state || !state.lastUpdate) {
                console.log("No state available");
                return window.dash_clientside.no_update;
            }
            console.log(`Clearing all layers at time: ${state.lastUpdate}`);
            
            // Return a timestamp to trigger clear_all
            return new Date().getTime();
        }
        """,
        dash.Output("draw-control", "clear_all", allow_duplicate=True),
        dash.Input("draw-state-store", "data"),
        prevent_initial_call=True,
    )


def register_all_clientside_callbacks(app):
    """
    Register all clientside callbacks for the application.

    Args:
        app (dash.Dash): The Dash application instance
    """
    logging.info("Registering clientside callbacks...")

    register_theme_callbacks(app)
    register_shape_handling_callbacks(app)

    logging.info("✅ All clientside callbacks registered successfully!")
