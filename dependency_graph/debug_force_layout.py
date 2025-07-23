"""
Debug Script for Force-Directed Layout Issues
===========================================

This script will help identify what's preventing circles from appearing in force-directed layout.
"""


def debug_force_directed_issues():
    """
    Check potential issues with force-directed circle implementation.
    """
    print("🔍 DEBUG: Force-Directed Layout Issues")
    print("=" * 50)

    issues_found = []

    print("\n1. Checking node shape generation logic...")
    # Read the addNodeShapes function
    try:
        with open("graph_modules/graph_visualization.py", "r") as f:
            content = f.read()

        if 'currentLayout === "force"' in content:
            print("   ✅ Layout check exists")
        else:
            issues_found.append("❌ Layout check missing")

        if '.append("circle")' in content:
            print("   ✅ Circle creation code exists")
        else:
            issues_found.append("❌ Circle creation code missing")

        if "calculateCircleRadius" in content:
            print("   ✅ Circle radius calculation exists")
        else:
            issues_found.append("❌ Circle radius calculation missing")

    except Exception as e:
        issues_found.append(f"❌ Error reading visualization file: {e}")

    print("\n2. Checking layout switching logic...")
    try:
        with open("graph_modules/graph_controls.py", "r") as f:
            content = f.read()

        if "regenerateNodeShapes" in content:
            print("   ✅ Node shape regeneration exists")
        else:
            issues_found.append("❌ Node shape regeneration missing")

        if "switchLayout" in content:
            print("   ✅ Layout switching function exists")
        else:
            issues_found.append("❌ Layout switching function missing")

    except Exception as e:
        issues_found.append(f"❌ Error reading controls file: {e}")

    print("\n3. Checking for rectangle-specific positioning...")
    try:
        with open("graph_modules/graph_visualization.py", "r") as f:
            content = f.read()

        rect_positioning = []
        if "d.width/2" in content:
            rect_positioning.append("d.width/2 positioning found")
        if "d.height/2" in content:
            rect_positioning.append("d.height/2 positioning found")

        if rect_positioning:
            print("   ⚠️ Rectangle-specific positioning found:")
            for pos in rect_positioning:
                print(f"      - {pos}")
            issues_found.append("❌ Rectangle positioning may affect circles")
        else:
            print("   ✅ No rectangle-specific positioning found")

    except Exception as e:
        issues_found.append(f"❌ Error checking positioning: {e}")

    print("\n4. Summary:")
    if issues_found:
        print("   🚨 Issues Found:")
        for issue in issues_found:
            print(f"      {issue}")
    else:
        print("   ✅ No obvious issues found in code structure")

    print("\n5. Manual Testing Recommendations:")
    print("   1. Open the dependency graph in browser")
    print("   2. Open Developer Tools (F12)")
    print("   3. Check Console for JavaScript errors")
    print("   4. Toggle to force-directed layout")
    print("   5. Inspect DOM to see if circles are created")
    print("   6. Check if currentLayout variable is correctly set")


if __name__ == "__main__":
    debug_force_directed_issues()
