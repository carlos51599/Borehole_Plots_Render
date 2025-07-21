#!/usr/bin/env python3
"""
Test script to verify AGS integration with geology code mapping.
"""

from borehole_log_professional import plot_borehole_log_from_ags_content


def test_ags_integration():
    """Test AGS integration with geology code mapping."""

    # Create minimal test AGS content
    test_ags_content = """
GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
DATA,BH01,0.0,1.5,101,TOPSOIL - Brown organic topsoil
DATA,BH01,1.5,3.0,203,Sandy CLAY - Firm brown sandy clay
DATA,BH01,3.0,5.5,501,GRAVEL - Dense angular gravel
DATA,BH01,5.5,8.0,202,Silty CLAY - Stiff grey silty clay
DATA,BH01,8.0,12.0,801,MUDSTONE - Weathered grey mudstone

GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH01,451000,195000,25.5
"""

    print("Testing AGS integration with geology code mapping...")

    # Test the AGS parsing and plotting
    images = plot_borehole_log_from_ags_content(
        ags_content=test_ags_content,
        loca_id="BH01",
        geology_csv_path="Geology Codes BGS.csv",
        title="Test AGS Integration",
    )

    if images and len(images) > 0:
        print(f"SUCCESS: Generated {len(images)} page(s) from AGS content")
        print("✓ AGS parsing integration working correctly")
        return True
    else:
        print("ERROR: Failed to generate borehole log from AGS content")
        return False


if __name__ == "__main__":
    success = test_ags_integration()
    if success:
        print("\n✓ AGS integration test passed! The complete workflow is working.")
    else:
        print("\n✗ AGS integration test failed!")
