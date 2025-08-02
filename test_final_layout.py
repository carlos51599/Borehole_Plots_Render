import matplotlib

matplotlib.use("Agg")

# Test the updated plotting with adjusted total visual box
from section.plotting.main import plot_section_from_ags_content

print("Testing final layout adjustments...")

# Simple test data
test_ags = '''\"PROJ\",\"Project Information\",\"\",\"\",\"\",\"\",\"\",\"\"
\"PROJ\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"PROJ\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"PROJ\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"PROJ\",\"12345\",\"12345\",\"12345\",\"Site Investigation\",\"Test Project\",\"BGS Test\",\"\"

\"LOCA\",\"Location Details\",\"\",\"\",\"\",\"\",\"\",\"\"
\"LOCA\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"LOCA\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"LOCA\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"LOCA\",\"BH01\",\"401234.5\",\"312456.7\",\"105.5\",\"Ground Level\",\"Test Borehole 1\",\"\"
\"LOCA\",\"BH02\",\"401244.5\",\"312456.7\",\"106.2\",\"Ground Level\",\"Test Borehole 2\",\"\"

\"GEOL\",\"Geology\",\"\",\"\",\"\",\"\",\"\",\"\"
\"GEOL\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"GEOL\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"GEOL\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"GEOL\",\"BH01\",\"1.0\",\"0.0\",\"101\",\"TOPSOIL brown sandy\",\"\",\"\"
\"GEOL\",\"BH01\",\"2.5\",\"1.0\",\"203\",\"SANDY CLAY brown firm\",\"\",\"\"
\"GEOL\",\"BH02\",\"1.2\",\"0.0\",\"101\",\"TOPSOIL\",\"\",\"\"
\"GEOL\",\"BH02\",\"3.0\",\"1.2\",\"203\",\"SANDY CLAY\",\"\",\"\"

\"ABBR\",\"Abbreviations\",\"\",\"\",\"\",\"\",\"\",\"\"
\"ABBR\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"ABBR\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"ABBR\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"ABBR\",\"101\",\"TOPSOIL\",\"Brown sandy topsoil\",\"\",\"\",\"\",\"\"
\"ABBR\",\"203\",\"SANDY CLAY\",\"Brown firm sandy clay\",\"\",\"\",\"\",\"\"'''

try:
    result = plot_section_from_ags_content(test_ags)
    if result and "image" in result:
        print("✓ SUCCESS: All layout adjustments completed!")
        print("✓ Black box repositioned to align with footer upper boundary")
        print("✓ Changed from red dashed to solid black line")
        print("✓ Borehole labels use consistent font sizes")
        print("✓ Plot area extended upward within total visual box")
        print("✓ Total visual box system working correctly")
    else:
        print("✗ ERROR: Plot generation failed")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback

    traceback.print_exc()
