"""
Debug script to test section plot functionality.
This script will help identify why the section plot is not appearing.
"""

import logging
import sys
import pandas as pd
from section_plot_professional import plot_section_from_ags_content

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

def test_section_plot_with_mock_data():
    """Test the section plot with mock AGS data"""
    
    # Create minimal mock AGS content in correct format
    mock_ags_content = """GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
DATA,BH01,0.00,2.00,101,Brown silty CLAY
DATA,BH01,2.00,5.00,203,Medium dense fine SAND
DATA,BH01,5.00,8.00,501,Dense sandy GRAVEL
DATA,BH02,0.00,1.50,101,Brown silty CLAY
DATA,BH02,1.50,4.00,203,Medium dense fine SAND
DATA,BH02,4.00,7.00,501,Dense sandy GRAVEL
DATA,BH03,0.00,3.00,101,Brown silty CLAY
DATA,BH03,3.00,6.00,203,Medium dense fine SAND
DATA,BH03,6.00,9.00,501,Dense sandy GRAVEL

GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH01,401000.00,201000.00,50.00
DATA,BH02,401050.00,201000.00,52.00
DATA,BH03,401100.00,201000.00,48.00

GROUP,ABBR
HEADING,ABBR_CODE,ABBR_DESC
DATA,101,CLAY
DATA,203,SAND
DATA,501,GRAVEL
"""

    logger.info("Testing section plot with mock data...")
    
    try:
        # Test with all boreholes
        logger.info("Testing plot generation...")
        result = plot_section_from_ags_content(
            mock_ags_content,
            filter_loca_ids=["BH01", "BH02", "BH03"],
            return_base64=True
        )
        
        if result is None:
            logger.error("❌ Section plot returned None!")
            return False
        
        if isinstance(result, str):
            if result.startswith("iVBORw0KGgo") or result.startswith("data:image/png;base64,"):
                logger.info(f"✅ Section plot generated successfully! (Base64 length: {len(result)})")
                return True
            else:
                logger.error(f"❌ Section plot returned unexpected string: {result[:100]}...")
                return False
        else:
            logger.error(f"❌ Section plot returned unexpected type: {type(result)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error generating section plot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_section_plot_functions():
    """Test individual functions used in section plot"""
    
    logger.info("Testing section plot functions...")
    
    try:
        from section_plot_professional import parse_ags_geol_section_from_string
        
        mock_ags_content = """GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
DATA,BH01,0.00,2.00,101,Brown silty CLAY

GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH01,401000.00,201000.00,50.00
"""
        
        logger.info("Testing AGS parsing...")
        geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(mock_ags_content)
        
        logger.info(f"GEOL DataFrame shape: {geol_df.shape}")
        logger.info(f"LOCA DataFrame shape: {loca_df.shape}")
        logger.info(f"GEOL columns: {geol_df.columns.tolist()}")
        logger.info(f"LOCA columns: {loca_df.columns.tolist()}")
        
        if geol_df.empty or loca_df.empty:
            logger.error("❌ Parsed DataFrames are empty!")
            return False
        
        logger.info("✅ AGS parsing successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing section plot functions: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=== SECTION PLOT DEBUG TEST ===")
    
    # Test parsing functions first
    functions_ok = test_section_plot_functions()
    
    # Test full plot generation
    plot_ok = test_section_plot_with_mock_data()
    
    if functions_ok and plot_ok:
        logger.info("✅ All tests passed! Section plot should be working.")
    else:
        logger.error("❌ Some tests failed. Check logs above for details.")
        
    logger.info("=== END DEBUG TEST ===")
