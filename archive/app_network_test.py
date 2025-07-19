import dash
from dash import html, dcc
import socket
import logging
import sys
from datetime import datetime

# Set up basic logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Get hostname and IP information
try:
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    logging.info(f"Hostname: {hostname}")
    logging.info(f"IP address: {host_ip}")
except Exception as e:
    logging.error(f"Error getting network info: {str(e)}")

# Create a very simple Dash app for testing
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Network Test App"),
        html.P("If you can see this page, network connectivity is working!"),
        html.Div([html.H3("Network Information:"), html.Pre(id="network-info")]),
        dcc.Interval(
            id="interval-component",
            interval=1 * 1000,  # in milliseconds (update every second)
            n_intervals=0,
        ),
    ]
)


@app.callback(
    dash.Output("network-info", "children"),
    dash.Input("interval-component", "n_intervals"),
)
def update_network_info(n):
    try:
        hostname = socket.gethostname()
        host_ip = socket.gethostbyname(hostname)

        info = [
            f"Current time: {datetime.now()}",
            f"Hostname: {hostname}",
            f"IP address: {host_ip}",
            f"Using port: 8050",
            f"Access this app at:",
            f"  http://localhost:8050",
            f"  http://127.0.0.1:8050",
            f"  http://{host_ip}:8050",
            f"Update count: {n}",
        ]
        return "\n".join(info)
    except Exception as e:
        return f"Error getting network info: {str(e)}"


if __name__ == "__main__":
    print("=" * 50)
    print(" Starting simple network test app")
    print(" Try accessing the app at:")
    print("   http://localhost:8050")
    print("   http://127.0.0.1:8050")
    print("=" * 50)

    # Start the server with explicit host/port configuration
    # Using host="0.0.0.0" makes the server available externally
    app.run(debug=True, host="0.0.0.0", port=8050)
