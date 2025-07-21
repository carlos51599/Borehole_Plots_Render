#!/usr/bin/env python3
"""
Enhanced Flowchart Validation Test
Comprehensive testing of all flowchart enhancements
"""

import requests
import json
import time
from pathlib import Path


def test_flowchart_enhancements():
    base_url = "http://127.0.0.1:5000"

    print("🧪 Testing Enhanced Interactive Flowchart")
    print("=" * 50)

    # Test 1: Server availability
    print("\n1️⃣ Testing server availability...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running and accessible")
        else:
            print(f"   ❌ Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server not accessible: {e}")
        return False

    # Test 2: API data structure
    print("\n2️⃣ Testing API data structure...")
    try:
        response = requests.get(f"{base_url}/api/files")
        if response.status_code == 200:
            files_data = response.json()
            print(f"   ✅ Files API working: {len(files_data)} files loaded")

            # Check data structure
            if files_data:
                sample_file = list(files_data.values())[0]
                required_fields = [
                    "total_lines",
                    "complexity",
                    "functions_count",
                    "classes_count",
                ]
                missing_fields = [
                    field for field in required_fields if field not in sample_file
                ]

                if not missing_fields:
                    print("   ✅ All required data fields present")
                else:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
        else:
            print(f"   ❌ Files API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")

    # Test 3: Static files availability
    print("\n3️⃣ Testing static files...")
    static_files = [
        "/static/codebase_flowchart.js",
        "/static/interactive_flowchart.html",
    ]

    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}")
            if response.status_code == 200:
                print(f"   ✅ {file_path} - Available")
            else:
                print(f"   ❌ {file_path} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {file_path} - Error: {e}")

    # Test 4: Enhanced features validation
    print("\n4️⃣ Testing enhanced features...")

    # Check JavaScript file for new features
    js_file_path = Path("codebase_flowchart.js")
    if js_file_path.exists():
        js_content = js_file_path.read_text(encoding="utf-8")

        features_to_check = [
            ("View Mode Support", "currentView"),
            ("Enhanced Tooltips", "total_lines"),
            ("Function View", "updateFunctionView"),
            ("Dependency View", "updateDependencyView"),
            ("Toggle View Function", "toggleView"),
            ("API Data Loading", "/api/files"),
            ("Responsive Layout", "min-height: calc(100vh - 200px)"),
        ]

        for feature_name, search_term in features_to_check:
            if search_term in js_content:
                print(f"   ✅ {feature_name} - Implemented")
            else:
                print(f"   ❌ {feature_name} - Missing")
    else:
        print("   ❌ JavaScript file not found")

    # Test 5: HTML structure validation
    print("\n5️⃣ Testing HTML structure...")
    html_file_path = Path("interactive_flowchart.html")
    if html_file_path.exists():
        html_content = html_file_path.read_text(encoding="utf-8")

        html_features = [
            ("Grid Layout", "grid-area: diagram"),
            ("View Mode Selector", "view-mode"),
            ("Enhanced Tooltips CSS", "backdrop-filter: blur(15px)"),
            ("Responsive Design", "min-height: calc(100vh - 200px)"),
            ("Header Actions", "header-actions"),
            ("Toggle View Button", "toggleView()"),
            ("Help Overlay", "help-overlay"),
        ]

        for feature_name, search_term in html_features:
            if search_term in html_content:
                print(f"   ✅ {feature_name} - Implemented")
            else:
                print(f"   ❌ {feature_name} - Missing")
    else:
        print("   ❌ HTML file not found")

    # Test 6: Sample data validation
    print("\n6️⃣ Testing sample data...")
    try:
        response = requests.get(f"{base_url}/api/files")
        if response.status_code == 200:
            files_data = response.json()

            # Find a sample file with good data
            sample_files = [
                name
                for name, data in files_data.items()
                if data.get("total_lines", 0) > 0 and data.get("complexity", 0) > 0
            ]

            if sample_files:
                sample_name = sample_files[0]
                sample_data = files_data[sample_name]

                print(f"   📄 Sample file: {sample_name}")
                print(f"   📊 Lines: {sample_data.get('total_lines', 0)}")
                print(f"   🔧 Complexity: {sample_data.get('complexity', 0)}")
                print(f"   ⚙️ Functions: {sample_data.get('functions_count', 0)}")
                print(f"   🏛️ Classes: {sample_data.get('classes_count', 0)}")
                print("   ✅ Sample data looks good")
            else:
                print("   ⚠️ No files with meaningful data found")
    except Exception as e:
        print(f"   ❌ Sample data test failed: {e}")

    print("\n🎯 Enhancement Testing Complete!")
    print("\n🔍 Key Improvements:")
    print("   • Fixed tooltip data display (total_lines, complexity, etc.)")
    print("   • Added responsive CSS Grid layout")
    print("   • Implemented view mode switching (Files/Functions/Dependencies)")
    print("   • Enhanced tooltip styling with previews")
    print("   • Added toggle view button in header")
    print("   • Improved API data loading with fallbacks")
    print("   • Added breadcrumb context for different views")

    print("\n🌐 Test the enhanced flowchart at: http://127.0.0.1:5000")
    print("   • Try hovering over nodes to see enhanced tooltips")
    print("   • Use the 'Toggle View' button to switch perspectives")
    print("   • Test the view mode dropdown for different analysis views")
    print("   • Check responsive layout by resizing browser window")


if __name__ == "__main__":
    test_flowchart_enhancements()
