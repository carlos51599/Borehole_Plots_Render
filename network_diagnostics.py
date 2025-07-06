import sys
import os
import socket
import logging
import platform
import traceback
from datetime import datetime

# Set up a clear log file
log_file = "network_debug.log"
with open(log_file, "w") as f:
    f.write(f"Network diagnostics started at {datetime.now()}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Platform: {platform.platform()}\n")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Get hostname and IP address
try:
    hostname = socket.gethostname()
    logging.info(f"Hostname: {hostname}")

    # Try to get all IP addresses
    try:
        host_ip = socket.gethostbyname(hostname)
        logging.info(f"Primary IP: {host_ip}")
    except Exception as e:
        logging.error(f"Failed to get IP for hostname: {str(e)}")

    # Get all network interfaces
    try:
        import psutil

        logging.info("Network interfaces:")
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    logging.info(f"  {iface}: {addr.address}")
    except ImportError:
        logging.warning("psutil not installed, cannot list all network interfaces")
except Exception as e:
    logging.error(f"Error getting network info: {str(e)}")


# Check if ports are in use
def check_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            logging.warning(f"Port {port} is already in use")
            return True
        else:
            logging.info(f"Port {port} is available")
            return False
    except Exception as e:
        logging.error(f"Error checking port {port}: {str(e)}")
        return None
    finally:
        sock.close()


# Check common Dash ports
check_port(8050)
check_port(8080)

# Try to open a listening socket on 0.0.0.0
try:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.bind(("0.0.0.0", 8051))
    logging.info(
        "Successfully bound to 0.0.0.0:8051 - your app should be able to listen on all interfaces"
    )
    test_socket.close()
except Exception as e:
    logging.error(f"Failed to bind to 0.0.0.0:8051: {str(e)}")
    logging.error(
        "This could indicate a firewall issue or another program using this port"
    )


# Try to connect to localhost
def test_local_connection(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, port))
        logging.info(f"Successfully connected to {host}:{port}")
        return True
    except Exception as e:
        logging.error(f"Failed to connect to {host}:{port}: {str(e)}")
        return False
    finally:
        sock.close()


# Create a simple test server to verify local connectivity
import threading
import time
import http.server


def run_test_server():
    try:
        test_port = 8052
        handler = http.server.SimpleHTTPRequestHandler
        httpd = http.server.HTTPServer(("0.0.0.0", test_port), handler)
        logging.info(f"Starting test HTTP server on port {test_port}")
        httpd.handle_request()  # Handle just one request
        httpd.server_close()
        logging.info("Test server stopped")
    except Exception as e:
        logging.error(f"Error running test server: {str(e)}")


# Start test server in a thread
server_thread = threading.Thread(target=run_test_server)
server_thread.daemon = True
server_thread.start()

# Wait a moment for the server to start
time.sleep(1)

# Try to connect to our test server
test_local_connection("localhost", 8052)
test_local_connection("127.0.0.1", 8052)
try:
    test_local_connection(socket.gethostbyname(hostname), 8052)
except:
    logging.error("Could not connect to test server using hostname's IP")

logging.info("Network diagnostics complete")
print(f"\nDiagnostics complete. See {log_file} for results.")
