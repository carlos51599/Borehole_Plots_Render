"""
Quick brace matcher to find the exact location of the JavaScript syntax error.
"""

import re
from pathlib import Path


def find_brace_mismatch(html_file: str):
    """Find the exact location of brace mismatch in HTML file."""
    print(f"🔍 Analyzing brace structure in: {html_file}")

    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    # Extract the main script block
    script_pattern = r"<script[^>]*>(.*?)</script>"
    scripts = re.findall(script_pattern, content, re.DOTALL)

    main_script = None
    for i, script in enumerate(scripts):
        if "graphData" in script and len(script) > 1000:  # Main script is large
            main_script = script
            print(f"✅ Found main script (block {i}) - {len(script)} characters")
            break

    if not main_script:
        print("❌ Main script not found")
        return

    # Count braces line by line
    lines = main_script.split("\n")
    brace_count = 0
    open_braces = 0
    close_braces = 0

    problem_lines = []

    for line_num, line in enumerate(lines, 1):
        line_open = line.count("{")
        line_close = line.count("}")

        open_braces += line_open
        close_braces += line_close
        brace_count += line_open - line_close

        # Track lines with significant brace imbalances
        if abs(line_open - line_close) > 2:
            problem_lines.append(
                (line_num, line.strip(), line_open, line_close, brace_count)
            )

    print(f"\n📊 Brace Analysis:")
    print(f"   - Total opening braces: {open_braces}")
    print(f"   - Total closing braces: {close_braces}")
    print(f"   - Imbalance: {open_braces - close_braces}")

    if problem_lines:
        print(f"\n🔍 Lines with significant brace imbalances:")
        for (
            line_num,
            line_content,
            line_open,
            line_close,
            running_count,
        ) in problem_lines:
            print(
                f"   Line {line_num}: {line_open} open, {line_close} close, running total: {running_count}"
            )
            print(f"      Content: {line_content[:100]}...")

    # Find the last few lines to see if there's a missing closing brace
    print(f"\n📝 Last 10 lines of script:")
    for i, line in enumerate(lines[-10:], len(lines) - 9):
        print(f"   {i}: {line.strip()}")

    # Check if the issue is at the very end
    if brace_count > 0:
        print(f"\n💡 Missing {brace_count} closing braces at end of script")
        return brace_count
    elif brace_count < 0:
        print(f"\n💡 Extra {abs(brace_count)} closing braces")
        return brace_count
    else:
        print("\n✅ Brace count is balanced - issue might be elsewhere")
        return 0


def fix_brace_mismatch(html_file: str, missing_braces: int):
    """Fix brace mismatch by adding missing closing braces."""
    if missing_braces <= 0:
        print("✅ No missing braces to fix")
        return False

    print(f"🔧 Fixing {missing_braces} missing closing braces...")

    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    # Find the last </script> tag and add braces before it
    script_end_pattern = r"(\s*)(</script>)"

    def replacement(match):
        indent = match.group(1)
        closing_tag = match.group(2)
        added_braces = (
            "\n" + indent + ("}\n" + indent).join([""] * (missing_braces + 1))
        )
        return added_braces + closing_tag

    # Apply the fix
    fixed_content = re.sub(script_end_pattern, replacement, content)

    # Write back the fixed content
    backup_file = html_file.replace(".html", "_backup.html")

    # Create backup
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📁 Backup created: {backup_file}")

    # Write fixed content
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"✅ Fixed HTML written to: {html_file}")
    return True


def main():
    """Main function to find and fix brace mismatch."""
    html_file = "graph_output/enhanced_dependency_graph.html"

    if not Path(html_file).exists():
        print(f"❌ File not found: {html_file}")
        return

    # Find the issue
    missing_braces = find_brace_mismatch(html_file)

    if missing_braces > 0:
        print(f"\n🔧 Attempting to fix {missing_braces} missing braces...")
        fixed = fix_brace_mismatch(html_file, missing_braces)

        if fixed:
            print("\n🔍 Re-analyzing after fix...")
            new_missing = find_brace_mismatch(html_file)
            if new_missing == 0:
                print("🎉 Fix successful! Brace structure is now balanced.")
            else:
                print(
                    f"⚠️  Fix partially successful. Still {new_missing} braces unbalanced."
                )
        else:
            print("❌ Fix failed")
    elif missing_braces < 0:
        print(f"\n💡 You have {abs(missing_braces)} extra closing braces")
        print("   Manual review recommended")
    else:
        print("\n✅ Brace structure appears balanced")
        print(
            "   The issue might be elsewhere (e.g., string escaping, function syntax)"
        )


if __name__ == "__main__":
    main()
