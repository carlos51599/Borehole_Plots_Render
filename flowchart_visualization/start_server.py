#!/usr/bin/env python3
"""
Simple launcher for the enhanced flowchart server
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from enhanced_server import start_server

    print("🚀 Starting Enhanced Flowchart Server...")
    print("📊 Features enabled:")
    print("  ✅ Full-width plot area")
    print("  ✅ Function details view")
    print("  ✅ Relationship highlighting (blue=dependencies, orange=dependents)")
    print("  ✅ Enhanced interactivity")
    print("  ✅ Comprehensive testing")
    print("")

    # Start server on port 5000 without opening browser
    start_server(port=5000, debug=False, open_browser=False)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Required packages: flask, requests")
    print("Install with: pip install flask requests")

except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback

    traceback.print_exc()
