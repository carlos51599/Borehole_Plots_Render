import dash
from dash import html
import logging
import socket

# Simple logging setup
logging.basicConfig(level=logging.INFO)

# Get hostname info
hostname = socket.gethostname()
try:
    host_ip = socket.gethostbyname(hostname)
    logging.info(f"Hostname: {hostname}")
    logging.info(f"IP address: {host_ip}")
except Exception as e:
    logging.error(f"Error getting network info: {str(e)}")

# Create the simplest possible Dash app
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H1("Minimal Dash Test"),
        html.P("If you can see this, everything is working!"),
        html.P(f"Server hostname: {hostname}"),
        html.P(f"Server IP: {host_ip}"),
    ]
)

if __name__ == "__main__":
    print("=" * 50)
    print(" Starting minimal test app")
    print(" Available at:")
    print("   http://localhost:8050")
    print("   http://127.0.0.1:8050")
    if host_ip:
        print(f"   http://{host_ip}:8050")
    print("=" * 50)

    # Use debug=False for this test to minimize complexity
    app.run(debug=False, host="0.0.0.0", port=8050)
