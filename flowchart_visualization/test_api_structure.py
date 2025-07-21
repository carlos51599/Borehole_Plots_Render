#!/usr/bin/env python3
"""Test script to check the actual API data structure"""

import requests
import json


def test_api_endpoints():
    base_url = "http://127.0.0.1:5000"

    print("Testing API endpoints...")

    # Test the files endpoint
    try:
        response = requests.get(f"{base_url}/api/files")
        if response.status_code == 200:
            files_data = response.json()
            print(f"\n📁 Files endpoint:")
            print(f"  Total files: {len(files_data)}")
            if files_data:
                first_file = list(files_data.keys())[0]
                print(f"  Sample file: {first_file}")
                print(
                    f"  Sample data structure: {json.dumps(files_data[first_file], indent=2)}"
                )
        else:
            print(f"  ❌ Files endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error accessing files endpoint: {e}")

    # Test the dependencies endpoint
    try:
        response = requests.get(f"{base_url}/api/dependencies")
        if response.status_code == 200:
            deps_data = response.json()
            print(f"\n🔗 Dependencies endpoint:")
            print(f"  Total files with dependencies: {len(deps_data)}")
            if deps_data:
                first_dep = list(deps_data.keys())[0]
                print(f"  Sample file: {first_dep}")
                print(f"  Dependencies: {deps_data[first_dep]}")
        else:
            print(f"  ❌ Dependencies endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error accessing dependencies endpoint: {e}")

    # Test the functions endpoint
    try:
        response = requests.get(f"{base_url}/api/functions")
        if response.status_code == 200:
            funcs_data = response.json()
            print(f"\n⚙️ Functions endpoint:")
            print(f"  Total files with functions: {len(funcs_data)}")
            if funcs_data:
                first_func_file = list(funcs_data.keys())[0]
                print(f"  Sample file: {first_func_file}")
                print(
                    f"  Sample functions: {json.dumps(funcs_data[first_func_file][:2], indent=2)}"
                )
        else:
            print(f"  ❌ Functions endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error accessing functions endpoint: {e}")


if __name__ == "__main__":
    test_api_endpoints()
