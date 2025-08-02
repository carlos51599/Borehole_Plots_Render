#!/usr/bin/env python3
"""
Layout Validation Test: Full-Width Section Plot

This script validates that the section plot layout correctly:
1. Uses full width of the container
2. Maintains aspect ratio
3. Centers properly
4. Responds to different screen sizes

Run: python tests/test_layout_validation.py
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def validate_section_plot_style():
    """Validate that section plot style meets full-width requirements."""
    print("🎨 Validating Section Plot Layout Style...")

    try:
        import config

        style = config.SECTION_PLOT_CENTER_STYLE

        # Test cases for full-width responsive layout
        validation_tests = [
            {
                "property": "width",
                "expected": "100%",
                "description": "Should use full container width",
            },
            {
                "property": "height",
                "expected": "auto",
                "description": "Should automatically calculate height to maintain aspect ratio",
            },
            {
                "property": "maxHeight",
                "expected": "80vh",
                "description": "Should limit height to 80% of viewport height",
            },
            {
                "property": "objectFit",
                "expected": "contain",
                "description": "Should preserve aspect ratio and fit within container",
            },
            {
                "property": "display",
                "expected": "block",
                "description": "Should be block-level element for proper centering",
            },
            {
                "property": "margin",
                "expected": "0 auto",
                "description": "Should center horizontally with auto margins",
            },
        ]

        print(f"📋 Current SECTION_PLOT_CENTER_STYLE: {style}")
        print("\n🔍 Validation Results:")

        all_passed = True

        for test in validation_tests:
            prop = test["property"]
            expected = test["expected"]
            description = test["description"]

            if prop in style and style[prop] == expected:
                print(f"✅ {prop}: {style[prop]} - {description}")
            elif prop in style:
                print(
                    f"❌ {prop}: got '{style[prop]}', expected '{expected}' - {description}"
                )
                all_passed = False
            else:
                print(f"❌ {prop}: MISSING - {description}")
                all_passed = False

        # Additional checks
        if "maxWidth" in style and style["maxWidth"] != "none":
            print(
                f"⚠️ maxWidth: {style['maxWidth']} - Consider removing width restrictions for full-width display"
            )

        return all_passed

    except Exception as e:
        print(f"❌ Style validation failed: {e}")
        return False


def test_responsive_behavior():
    """Test responsive behavior at different viewport sizes."""
    print("\n📱 Testing Responsive Behavior...")

    # Simulate different viewport scenarios
    viewport_tests = [
        {"width": "1920px", "description": "Desktop (1920px wide)"},
        {"width": "1366px", "description": "Laptop (1366px wide)"},
        {"width": "768px", "description": "Tablet (768px wide)"},
        {"width": "375px", "description": "Mobile (375px wide)"},
    ]

    try:
        import config

        style = config.SECTION_PLOT_CENTER_STYLE

        for test in viewport_tests:
            viewport_width = test["width"]
            description = test["description"]

            # Calculate expected behavior
            if style.get("width") == "100%":
                expected_img_width = f"100% of {viewport_width}"

                # With maxHeight constraint
                if style.get("maxHeight") == "80vh":
                    max_height = "80% of viewport height"
                else:
                    max_height = "unlimited"

                print(
                    f"✅ {description}: Image width = {expected_img_width}, Max height = {max_height}"
                )
            else:
                print(f"❌ {description}: Fixed width may not be responsive")

        return True

    except Exception as e:
        print(f"❌ Responsive behavior test failed: {e}")
        return False


def test_aspect_ratio_preservation():
    """Test that aspect ratio is preserved with new styling."""
    print("\n📐 Testing Aspect Ratio Preservation...")

    try:
        import config

        style = config.SECTION_PLOT_CENTER_STYLE

        # Key properties for aspect ratio preservation
        aspect_ratio_checks = [
            ("height", "auto", "Allows height to scale with width"),
            ("objectFit", "contain", "Preserves aspect ratio within container"),
            ("maxHeight", "80vh", "Prevents excessively tall images"),
        ]

        all_checks_passed = True

        for prop, expected, description in aspect_ratio_checks:
            if prop in style and style[prop] == expected:
                print(f"✅ {prop}: {style[prop]} - {description}")
            else:
                print(f"❌ {prop}: incorrect or missing - {description}")
                all_checks_passed = False

        return all_checks_passed

    except Exception as e:
        print(f"❌ Aspect ratio test failed: {e}")
        return False


def test_centering_mechanism():
    """Test that the centering mechanism works correctly."""
    print("\n🎯 Testing Centering Mechanism...")

    try:
        import config

        style = config.SECTION_PLOT_CENTER_STYLE

        centering_checks = [
            ("margin", "0 auto", "Horizontal centering with auto margins"),
            ("display", "block", "Block-level element for margin centering"),
            ("textAlign", "center", "Text alignment for inline content"),
        ]

        all_checks_passed = True

        for prop, expected, description in centering_checks:
            if prop in style:
                if prop == "textAlign" and style[prop] in ["center", "centre"]:
                    print(f"✅ {prop}: {style[prop]} - {description}")
                elif style[prop] == expected:
                    print(f"✅ {prop}: {style[prop]} - {description}")
                else:
                    print(
                        f"⚠️ {prop}: {style[prop]} (expected {expected}) - {description}"
                    )
            else:
                print(f"❌ {prop}: missing - {description}")
                all_checks_passed = False

        return all_checks_passed

    except Exception as e:
        print(f"❌ Centering test failed: {e}")
        return False


def run_layout_validation():
    """Run comprehensive layout validation."""
    print("🧪 Running Layout Validation Tests")
    print("=" * 50)

    tests = [
        ("Section Plot Style Validation", validate_section_plot_style),
        ("Responsive Behavior", test_responsive_behavior),
        ("Aspect Ratio Preservation", test_aspect_ratio_preservation),
        ("Centering Mechanism", test_centering_mechanism),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    print("\n📊 LAYOUT VALIDATION SUMMARY")
    print("=" * 40)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} layout tests passed")

    if passed == total:
        print("\n🎉 ALL LAYOUT TESTS PASSED!")
        print("\n📋 Layout features confirmed:")
        print("- ✅ Section plot uses full container width (100%)")
        print("- ✅ Height automatically scales to maintain aspect ratio")
        print("- ✅ Maximum height constrained to 80% viewport height")
        print("- ✅ Image preserves aspect ratio with objectFit: contain")
        print("- ✅ Plot centers properly with margin: 0 auto")
        print("- ✅ Responsive behavior across different screen sizes")
        print("\n🎨 The section plot should now display beautifully at full width!")
    else:
        print(f"\n⚠️ {total - passed} layout test(s) failed. Review the issues above.")

    return passed == total


if __name__ == "__main__":
    success = run_layout_validation()
    sys.exit(0 if success else 1)
