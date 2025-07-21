#!/usr/bin/env python3
"""
Test the current API data structure to understand issues
"""

import requests
import json


def test_api():
    base_url = "http://127.0.0.1:5000"

    try:
        # Test the data endpoint
        response = requests.get(f"{base_url}/api/data")
        if response.status_code == 200:
            data = response.json()

            print("API Data Structure Analysis:")
            print(f"Total files: {len(data.get('files', {}))}")

            # Check a sample file's data
            files = data.get("files", {})
            if files:
                sample_file = list(files.keys())[0]
                sample_data = files[sample_file]
                print(f"\nSample file: {sample_file}")
                print(f"Data keys: {list(sample_data.keys())}")
                print(f"Total lines: {sample_data.get('total_lines', 'missing')}")
                print(f"Complexity: {sample_data.get('complexity', 'missing')}")
                print(f"Type: {sample_data.get('type', 'missing')}")

            # Check functions data
            functions = data.get("functions", {})
            print(
                f"\nFunctions data available: {len(functions)} files have function data"
            )

            # Check dependencies
            dependencies = data.get("dependencies", {})
            print(f"Dependencies data: {len(dependencies)} files have dependencies")

        else:
            print(f"API request failed: {response.status_code}")

    except Exception as e:
        print(f"Error testing API: {e}")


if __name__ == "__main__":
    test_api()
