"""
Test script for config_modules modular structure.

This script validates that the new modular config structure maintains
all functionality and import compatibility.
"""

import sys
import traceback
from typing import List, Tuple


def test_module_imports() -> Tuple[bool, List[str]]:
    """Test config_modules imports."""
    results = []
    success = True

    # Test individual module imports
    modules_to_test = [
        "config_modules.figures",
        "config_modules.layout",
        "config_modules.sizing",
        "config_modules.styles",
        "config_modules",
    ]

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            results.append(f"✅ {module_name}: Import successful")
        except ImportError as e:
            results.append(f"❌ {module_name}: Import failed - {e}")
            success = False
        except Exception as e:
            results.append(f"❌ {module_name}: Unexpected error - {e}")
            success = False

    return success, results


def test_backward_compatibility() -> Tuple[bool, List[str]]:
    """Test backward compatibility with original config.py imports."""
    results = []
    success = True

    try:
        # Test common constants that should be available
        from config_modules import (
            APP_TITLE,
            MAP_HEIGHT,
            HEADER_H1_CENTER_STYLE,
            BUTTON_RIGHT_STYLE,
            PRIMARY_COLOR,
        )

        # Check constants are accessible
        constants = [
            ("APP_TITLE", APP_TITLE),
            ("MAP_HEIGHT", MAP_HEIGHT),
            ("HEADER_H1_CENTER_STYLE", HEADER_H1_CENTER_STYLE),
            ("BUTTON_RIGHT_STYLE", BUTTON_RIGHT_STYLE),
            ("PRIMARY_COLOR", PRIMARY_COLOR),
        ]

        for name, value in constants:
            if value is not None:
                results.append(f"✅ {name}: Available and not None")
            else:
                results.append(f"❌ {name}: Available but None")
                success = False

    except ImportError as e:
        results.append(f"❌ Backward compatibility import failed: {e}")
        success = False
    except Exception as e:
        results.append(f"❌ Unexpected error testing backward compatibility: {e}")
        success = False

    return success, results


def test_style_dictionaries() -> Tuple[bool, List[str]]:
    """Test that style dictionaries are properly structured."""
    results = []
    success = True

    try:
        from config_modules import (
            HEADER_H1_CENTER_STYLE,
            MAP_CENTER_STYLE,
            UPLOAD_AREA_CENTER_STYLE,
            BUTTON_RIGHT_STYLE,
        )

        # Test style dictionaries are dict objects
        styles = [
            ("HEADER_H1_CENTER_STYLE", HEADER_H1_CENTER_STYLE),
            ("MAP_CENTER_STYLE", MAP_CENTER_STYLE),
            ("UPLOAD_AREA_CENTER_STYLE", UPLOAD_AREA_CENTER_STYLE),
            ("BUTTON_RIGHT_STYLE", BUTTON_RIGHT_STYLE),
        ]

        for name, style_dict in styles:
            if isinstance(style_dict, dict):
                results.append(f"✅ {name}: Is dict with {len(style_dict)} keys")
            else:
                results.append(f"❌ {name}: Not a dict, is {type(style_dict)}")
                success = False

    except Exception as e:
        results.append(f"❌ Style dictionaries test error: {e}")
        success = False

    return success, results


def test_key_constants() -> Tuple[bool, List[str]]:
    """Test key constants are available."""
    results = []
    success = True

    try:
        from config_modules import (
            # Figure constants
            LOG_FIG_HEIGHT,
            SECTION_BASE_HEIGHT,
            # Layout constants
            APP_TITLE,
            MAP_SECTION_TITLE,
            # Sizing constants
            HEADER_H1_SIZE,
            BUTTON_HEIGHT,
            # Style constants
            PRIMARY_COLOR,
            BORDER_RADIUS,
        )

        # Test constants exist and have expected types
        constants = [
            ("LOG_FIG_HEIGHT", LOG_FIG_HEIGHT, (int, float)),
            ("SECTION_BASE_HEIGHT", SECTION_BASE_HEIGHT, (int, float)),
            ("APP_TITLE", APP_TITLE, str),
            ("MAP_SECTION_TITLE", MAP_SECTION_TITLE, str),
            ("HEADER_H1_SIZE", HEADER_H1_SIZE, str),
            ("BUTTON_HEIGHT", BUTTON_HEIGHT, str),
            ("PRIMARY_COLOR", PRIMARY_COLOR, str),
            ("BORDER_RADIUS", BORDER_RADIUS, str),
        ]

        for name, value, expected_type in constants:
            if isinstance(value, expected_type):
                results.append(f"✅ {name}: Correct type {type(value).__name__}")
            else:
                results.append(
                    f"❌ {name}: Wrong type, got {type(value).__name__}, expected {expected_type}"
                )
                success = False

    except Exception as e:
        results.append(f"❌ Key constants test error: {e}")
        success = False

    return success, results


def main():
    """Run all tests and report results."""
    print("Testing config_modules modular structure...")
    print("=" * 60)

    all_success = True

    # Test 1: Module imports
    print("\n1. Testing module imports:")
    success, results = test_module_imports()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 2: Backward compatibility
    print("\n2. Testing backward compatibility:")
    success, results = test_backward_compatibility()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 3: Style dictionaries
    print("\n3. Testing style dictionaries:")
    success, results = test_style_dictionaries()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Test 4: Key constants
    print("\n4. Testing key constants:")
    success, results = test_key_constants()
    for result in results:
        print(f"   {result}")
    if not success:
        all_success = False

    # Final result
    print("\n" + "=" * 60)
    if all_success:
        print("🎉 ALL TESTS PASSED - Modular config structure is working correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Test script error: {e}")
        traceback.print_exc()
        sys.exit(1)
