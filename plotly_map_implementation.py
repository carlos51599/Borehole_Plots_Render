
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State
import dash

def create_plotly_map_component(borehole_data=None, center=None, zoom=6):
    """
    Create a Plotly-based map component to replace dash-leaflet
    
    Args:
        borehole_data: DataFrame with 'lat', 'lon', 'name' columns
        center: [lat, lon] for map center
        zoom: zoom level
    
    Returns:
        dcc.Graph component
    """
    
    if borehole_data is None or borehole_data.empty:
        # Empty map
        fig = go.Figure()
        fig.update_layout(
            map=dict(
                style="open-street-map",
                center=dict(lat=center[0] if center else 51.5, 
                           lon=center[1] if center else -0.1),
                zoom=zoom
            ),
            height=500,
            margin=dict(l=0, r=0, t=0, b=0)
        )
    else:
        # Map with borehole data
        fig = px.scatter_map(
            borehole_data,
            lat="lat",
            lon="lon", 
            hover_name="name",
            zoom=zoom,
            height=500
        )
        
        if center:
            fig.update_layout(
                map=dict(
                    center=dict(lat=center[0], lon=center[1]),
                    zoom=zoom
                )
            )
        
        fig.update_layout(
            map_style="open-street-map",
            margin=dict(l=0, r=0, t=0, b=0)
        )
    
    return dcc.Graph(
        id="borehole-map-plotly",
        figure=fig,
        style={'height': '500px', 'width': '100%'}
    )

def update_plotly_map_position(fig, center, zoom):
    """
    Update map center and zoom - THIS ACTUALLY WORKS UNLIKE DASH-LEAFLET
    
    Args:
        fig: Plotly figure object
        center: [lat, lon]
        zoom: zoom level
    
    Returns:
        Updated figure
    """
    fig.update_layout(
        map=dict(
            center=dict(lat=center[0], lon=center[1]),
            zoom=zoom
        )
    )
    return fig

# Example callback for file upload
def register_plotly_map_callbacks(app):
    """Register callbacks for Plotly map updates"""
    
    @app.callback(
        Output("borehole-map-plotly", "figure"),
        [Input("upload-ags", "contents")],
        [State("borehole-map-plotly", "figure")]
    )
    def update_map_on_file_upload(contents, current_fig):
        if not contents:
            return current_fig
            
        # Process AGS file and extract borehole data
        # ... (existing data processing logic) ...
        
        # Create sample data for demonstration
        borehole_data = pd.DataFrame({
            'lat': [51.5074, 51.5155, 51.5033],
            'lon': [-0.1278, -0.0922, -0.1195],
            'name': ['BH001', 'BH002', 'BH003']
        })
        
        # Calculate center and zoom
        center_lat = borehole_data['lat'].mean()
        center_lon = borehole_data['lon'].mean()
        
        # Create new figure
        fig = px.scatter_map(
            borehole_data,
            lat="lat",
            lon="lon",
            hover_name="name",
            zoom=12,
            height=500
        )
        
        fig.update_layout(
            map=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=12
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        return fig
