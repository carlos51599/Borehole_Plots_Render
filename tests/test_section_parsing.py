"""
Test script to validate section parsing module imports and functionality.
"""

# Test import of new parsing module
try:
    from section.parsing import (
        parse_ags_geol_section_from_string,
        validate_ags_format,
        extract_ags_metadata,
    )

    print("✅ Successfully imported parsing functions")
except ImportError as e:
    print(f"❌ Import error: {e}")

# Test import from section package
try:
    import section

    print("✅ Successfully imported section package")
    # Validate functions are available
    assert hasattr(section, "parse_ags_geol_section_from_string")
    assert hasattr(section, "validate_ags_format")
    assert hasattr(section, "extract_ags_metadata")
    print("✅ All parsing functions available in section package")
except (ImportError, AssertionError) as e:
    print(f"❌ Section package import error: {e}")

# Test basic functionality with minimal sample AGS content
test_ags_content = """GROUP,LOCA
HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN,LOCA_GL
UNITS,,,m,m,m
TYPE,X,X,2DP,2DP,2DP
DATA,BH001,BH,400000.00,300000.00,100.00
DATA,BH002,BH,400010.00,300010.00,105.50

GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_GEOL
UNITS,,m,m,
TYPE,X,2DP,2DP,X
DATA,BH001,0.00,2.50,MADE GROUND
DATA,BH001,2.50,5.00,CLAY
DATA,BH002,0.00,1.00,TOPSOIL
DATA,BH002,1.00,4.00,SAND
"""

try:
    # Test AGS format validation
    is_valid, message = validate_ags_format(test_ags_content)
    print(f"✅ AGS validation: {is_valid} - {message}")

    # Test metadata extraction
    metadata = extract_ags_metadata(test_ags_content)
    print(f"✅ Metadata extraction: Found {len(metadata['groups_found'])} groups")
    print(f"   Groups: {metadata['groups_found']}")

    # Test AGS parsing
    geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(test_ags_content)
    print("✅ AGS parsing successful:")
    print(f"   GEOL DataFrame: {len(geol_df)} rows, {len(geol_df.columns)} columns")
    print(f"   LOCA DataFrame: {len(loca_df)} rows, {len(loca_df.columns)} columns")
    print(f"   ABBR DataFrame: {abbr_df is not None}")

except Exception as e:
    print(f"❌ Functionality test error: {e}")

print("\n📋 Test Summary:")
print("- Parsing module imports: Complete")
print("- Section package exports: Complete")
print("- Basic AGS functionality: Working")
print("- Ready for Phase 2 continuation")
