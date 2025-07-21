#!/usr/bin/env python3
"""
Interactive Flowchart Setup Script

This script sets up and launches the interactive codebase flowchart.
It handles dependency installation, data generation, and server startup.
"""

import subprocess
import sys
import os
from pathlib import Path
import time


def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("    🗂️ INTERACTIVE CODEBASE FLOWCHART SETUP")
    print("=" * 70)
    print("Setting up advanced visualization for your project...")
    print()


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_requirements():
    """Install required packages"""
    required_packages = ["flask", "networkx"]

    print("\n📦 Installing required packages...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📥 Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    return True


def generate_analysis_data():
    """Generate codebase analysis data"""
    print("\n🔍 Generating codebase analysis...")

    analysis_file = Path("codebase_analysis.json")

    # Check if analysis already exists and is recent
    if analysis_file.exists():
        age_hours = (time.time() - analysis_file.stat().st_mtime) / 3600
        if age_hours < 24:  # Less than 24 hours old
            print(f"✅ Using existing analysis (generated {age_hours:.1f} hours ago)")
            return True
        else:
            print(
                f"🔄 Regenerating analysis (current data is {age_hours:.1f} hours old)"
            )

    # Try enhanced analysis first
    enhanced_script = Path("generate_flowchart_data.py")
    basic_script = Path("analyze_codebase.py")

    if enhanced_script.exists():
        try:
            print("   Running enhanced analysis...")
            result = subprocess.run(
                [sys.executable, str(enhanced_script)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                print("✅ Enhanced analysis completed")
                return True
            else:
                print(f"⚠️ Enhanced analysis failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⚠️ Enhanced analysis timed out")
        except Exception as e:
            print(f"⚠️ Enhanced analysis error: {e}")

    # Fallback to basic analysis
    if basic_script.exists():
        try:
            print("   Running basic analysis...")
            result = subprocess.run(
                [sys.executable, str(basic_script)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print("✅ Basic analysis completed")
                return True
            else:
                print(f"❌ Basic analysis failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Basic analysis error: {e}")

    # Create minimal fallback data
    print("⚠️ Creating minimal analysis data...")
    create_minimal_analysis()
    return True


def create_minimal_analysis():
    """Create minimal analysis data if generation fails"""
    minimal_data = {
        "metadata": {
            "project_name": "Borehole_Plots_Render",
            "total_files": 0,
            "analysis_timestamp": "2025-01-21T00:00:00",
        },
        "files": {},
        "dependencies": {},
        "functions": {},
        "classes": {},
        "imports": {},
    }

    # Scan for Python files
    for py_file in Path(".").rglob("*.py"):
        if any(part.startswith(".") for part in py_file.parts):
            continue  # Skip hidden directories

        rel_path = str(py_file.relative_to("."))
        try:
            stat = py_file.stat()
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            minimal_data["files"][rel_path] = {
                "name": py_file.name,
                "type": "core",
                "complexity": len(content.split("\n")),  # Simple complexity
                "total_lines": len(content.split("\n")),
                "functions_count": content.count("def "),
                "classes_count": content.count("class "),
            }
        except Exception:
            pass  # Skip files we can't read

    minimal_data["metadata"]["total_files"] = len(minimal_data["files"])

    with open("codebase_analysis.json", "w") as f:
        import json

        json.dump(minimal_data, f, indent=2)

    print(f"✅ Created minimal analysis for {len(minimal_data['files'])} files")


def verify_files():
    """Verify required files exist"""
    required_files = [
        "interactive_flowchart.html",
        "codebase_flowchart.js",
        "flowchart_server.py",
        "codebase_analysis.json",
    ]

    print("\n📋 Verifying required files...")
    missing_files = []

    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        print("   Please ensure all flowchart files are in the current directory")
        return False

    return True


def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting interactive flowchart server...")
    print("   URL: http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        # Import and run the server
        import flowchart_server

        flowchart_server.main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except ImportError:
        print("❌ Could not import flowchart_server.py")
        print("   Please check the file exists and is valid Python code")
    except Exception as e:
        print(f"❌ Server error: {e}")


def main():
    """Main setup function"""
    print_banner()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install requirements
    if not install_requirements():
        print("\n❌ Failed to install required packages")
        sys.exit(1)

    # Generate analysis data
    if not generate_analysis_data():
        print("\n❌ Failed to generate analysis data")
        sys.exit(1)

    # Verify files
    if not verify_files():
        print("\n❌ Missing required files")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)

    # Ask user if they want to start the server
    try:
        response = (
            input("\nStart the interactive flowchart server now? (Y/n): ")
            .strip()
            .lower()
        )
        if response in ("", "y", "yes"):
            start_server()
        else:
            print("\n💡 To start the server later, run:")
            print("   python flowchart_server.py")
            print("\n📚 Documentation:")
            print("   • FLOWCHART_IMPLEMENTATION.md - Technical details")
            print("   • FLOWCHART_USER_GUIDE.md - User manual")
    except KeyboardInterrupt:
        print("\n\n👋 Setup completed. Server not started.")


if __name__ == "__main__":
    main()
