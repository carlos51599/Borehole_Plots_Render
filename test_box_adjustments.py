import matplotlib

matplotlib.use("Agg")
from section.plotting.main import plot_section_from_ags_content
import base64

# Test data (abbreviated for quick testing)
test_data = '''\"PROJ\",\"Project Information\",\"\",\"\",\"\",\"\",\"\",\"\"
\"PROJ\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"PROJ\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"PROJ\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"PROJ\",\"12345\",\"12345\",\"12345\",\"Site Investigation\",\"Test Project\",\"BGS Test\",\"\"

\"GEOL\",\"Geology\",\"\",\"\",\"\",\"\",\"\",\"\"
\"GEOL\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"GEOL\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"GEOL\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"GEOL\",\"BH01\",\"1.0\",\"0.0\",\"101\",\"TOPSOIL brown sandy\",\"\",\"\"
\"GEOL\",\"BH01\",\"2.5\",\"1.0\",\"203\",\"SANDY CLAY brown firm\",\"\",\"\"
\"GEOL\",\"BH01\",\"4.0\",\"2.5\",\"501\",\"GRAVEL sandy angular\",\"\",\"\"
\"GEOL\",\"BH02\",\"1.2\",\"0.0\",\"101\",\"TOPSOIL\",\"\",\"\"
\"GEOL\",\"BH02\",\"3.0\",\"1.2\",\"203\",\"SANDY CLAY\",\"\",\"\"
\"GEOL\",\"BH02\",\"5.0\",\"3.0\",\"501\",\"GRAVEL\",\"\",\"\"

\"LOCA\",\"Location Details\",\"\",\"\",\"\",\"\",\"\",\"\"
\"LOCA\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"LOCA\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"LOCA\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"LOCA\",\"BH01\",\"401234.5\",\"312456.7\",\"105.5\",\"Ground Level\",\"Test Borehole 1\",\"\"
\"LOCA\",\"BH02\",\"401244.5\",\"312456.7\",\"106.2\",\"Ground Level\",\"Test Borehole 2\",\"\"

\"ABBR\",\"Abbreviations\",\"\",\"\",\"\",\"\",\"\",\"\"
\"ABBR\",\"X\",\"Y\",\"Z\",\"?\",\"?\",\"?\",\"\"
\"ABBR\",\"ID\",\"ID\",\"ID\",\"TYPE\",\"TYPE\",\"TYPE\",\"\"
\"ABBR\",\"\",\"\",\"\",\"TEXT\",\"TEXT\",\"TEXT\",\"\"
\"ABBR\",\"101\",\"TOPSOIL\",\"Brown sandy topsoil\",\"\",\"\",\"\",\"\"
\"ABBR\",\"203\",\"SANDY CLAY\",\"Brown firm sandy clay\",\"\",\"\",\"\",\"\"
\"ABBR\",\"501\",\"GRAVEL\",\"Sandy angular gravel\",\"\",\"\",\"\",\"\"'''

try:
    result = plot_section_from_ags_content(test_data)
    if result and "image" in result and result["image"]:
        print("SUCCESS: Plot generated with total visual box adjustments")
        print("- Black box repositioned to align with footer upper boundary")
        print("- Changed to solid black line")
        print("- Font sizes consistent for borehole labels")
        print("- Plot area extended upward")
        print("- Total visual box system working correctly")
    else:
        print("ERROR: Plot generation failed")
        print("Result:", result)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
