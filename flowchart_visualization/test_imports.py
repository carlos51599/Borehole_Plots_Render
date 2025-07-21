print("Testing Python execution in flowchart_visualization folder")
import os

print(f"Current working directory: {os.getcwd()}")
print("Files in current directory:")
for file in os.listdir("."):
    print(f"  - {file}")

# Test that our enhanced server can be imported
try:
    from enhanced_server import categorize_file_type

    print("✅ Enhanced server imports successfully")

    # Test categorization
    test_result = categorize_file_type("app.py")
    print(f"✅ File categorization works: app.py → {test_result}")

except Exception as e:
    print(f"❌ Error importing enhanced server: {e}")
    import traceback

    traceback.print_exc()
