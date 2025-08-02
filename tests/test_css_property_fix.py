#!/usr/bin/env python3
"""
Test CSS Property Fix Validation
===============================

This test verifies that:
1. CSS properties use correct camelCase format for React compatibility
2. App starts without React CSS warnings
3. Layout components render properly with fixed CSS properties
4. Section plot aspect ratio fix continues to work

Author: AI Assistant
Date: 2025-08-01
"""

import sys
import os
import re
import subprocess
import time
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_css_property_formatting():
    """Test that all CSS properties use camelCase format"""
    print("🔍 Testing CSS property formatting...")

    layout_file = project_root / "app_modules" / "layout.py"

    with open(layout_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for kebab-case CSS properties that should be camelCase
    kebab_case_patterns = [
        r"margin-left",
        r"margin-right",
        r"margin-top",
        r"margin-bottom",
        r"padding-left",
        r"padding-right",
        r"padding-top",
        r"padding-bottom",
        r"border-left",
        r"border-right",
        r"border-top",
        r"border-bottom",
        r"font-size",
        r"font-weight",
        r"font-family",
        r"background-color",
        r"border-radius",
        r"text-align",
        r"line-height",
    ]

    issues_found = []
    for pattern in kebab_case_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues_found.extend([(pattern, len(matches))])

    if issues_found:
        print("❌ Found kebab-case CSS properties:")
        for prop, count in issues_found:
            print(f"   - {prop}: {count} occurrences")
        return False
    else:
        print("✅ All CSS properties use correct camelCase format")
        return True


def test_app_startup():
    """Test that app starts without React CSS errors"""
    print("\n🚀 Testing app startup without CSS errors...")

    try:
        # Start app process
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Give app time to start
        time.sleep(5)

        # Check if app is running
        try:
            response = requests.get("http://localhost:8050", timeout=5)
            app_running = response.status_code == 200
        except:
            app_running = False

        # Check stdout and stderr for CSS errors
        stdout_output = ""
        stderr_output = ""

        # Read available output without blocking
        while process.poll() is None:
            try:
                stdout_line = process.stdout.readline()
                if stdout_line:
                    stdout_output += stdout_line
                stderr_line = process.stderr.readline()
                if stderr_line:
                    stderr_output += stderr_line

                # Stop reading after we get enough output
                if len(stdout_output) > 1000:
                    break
            except:
                break

        # Clean up process
        process.terminate()
        process.wait(timeout=5)

        # Check for CSS-related warnings
        css_warnings = []
        error_patterns = [
            r"Warning: Unsupported style property.*Did you mean",
            r"margin-left.*marginLeft",
            r"padding-left.*paddingLeft",
            r"border-left.*borderLeft",
        ]

        combined_output = stdout_output + stderr_output
        for pattern in error_patterns:
            if re.search(pattern, combined_output, re.IGNORECASE):
                css_warnings.append(pattern)

        if css_warnings:
            print("❌ Found CSS warnings:")
            for warning in css_warnings:
                print(f"   - {warning}")
            return False
        elif app_running:
            print("✅ App started successfully without CSS errors")
            return True
        else:
            print("❌ App failed to start properly")
            return False

    except Exception as e:
        print(f"❌ Error testing app startup: {e}")
        return False


def test_aspect_ratio_preservation():
    """Test that aspect ratio fix is still in place"""
    print("\n📐 Testing aspect ratio fix preservation...")

    plot_generation_file = project_root / "callbacks" / "plot_generation.py"

    with open(plot_generation_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for bbox_inches=None pattern (our fix)
    if "bbox_inches=None" in content:
        print("✅ Aspect ratio fix preserved (bbox_inches=None found)")

        # Check that bbox_inches="tight" is not used
        if 'bbox_inches="tight"' in content:
            print(
                "❌ Warning: bbox_inches='tight' still present - may cause stretching"
            )
            return False
        else:
            print("✅ No bbox_inches='tight' found - aspect ratio protected")
            return True
    else:
        print("❌ Aspect ratio fix missing (bbox_inches=None not found)")
        return False


def test_responsive_css():
    """Test that responsive CSS is properly configured"""
    print("\n📱 Testing responsive CSS configuration...")

    styles_file = project_root / "config_modules" / "styles.py"

    with open(styles_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for camelCase properties in MAP_CENTER_STYLE
    if "maxWidth" in content and "marginTop" in content:
        print("✅ Responsive CSS uses correct camelCase properties")

        # Check that kebab-case is not used
        if "max-width" in content or "margin-top" in content:
            print("❌ Warning: kebab-case properties found in styles")
            return False
        else:
            print("✅ No kebab-case properties in styles configuration")
            return True
    else:
        print("❌ Responsive CSS properties not found or incorrectly formatted")
        return False


def main():
    """Run all CSS property fix tests"""
    print("🧪 CSS Property Fix Validation Tests")
    print("=" * 50)

    tests = [
        test_css_property_formatting,
        test_responsive_css,
        test_aspect_ratio_preservation,
        test_app_startup,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All CSS property fix tests PASSED!")
        print("✅ App is now functional with correct aspect ratios")
        return True
    else:
        print("⚠️  Some tests failed - check issues above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
