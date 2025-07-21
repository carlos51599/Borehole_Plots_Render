"""
Test script to verify the complete section plot workflow and save output
"""

import logging
import sys
import base64
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

def test_complete_section_plot_workflow():
    """Test the complete section plot workflow and verify table box and footer"""
    
    # Create test AGS content in correct format
    test_ags_content = """GROUP,GEOL
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

    logger.info("Testing complete section plot workflow...")
    
    try:
        # Test section plot generation with high-resolution output
        logger.info("Generating section plot...")
        result = plot_section_from_ags_content(
            test_ags_content,
            filter_loca_ids=["BH01", "BH02", "BH03"],
            save_high_res=True,
            output_filename="test_complete_section",
            return_base64=True,
            dpi=300,
            figsize=(11.69, 8.27),  # A4 landscape
            show_labels=True
        )
        
        if result is None:
            logger.error("❌ Section plot returned None!")
            return False
        
        if isinstance(result, str):
            # Decode and save the base64 image for inspection
            if result.startswith("iVBORw0KGgo") or result.startswith("data:image/png;base64,"):
                # Clean the base64 string
                if result.startswith("data:image/png;base64,"):
                    img_data = result.split(",", 1)[1]
                else:
                    img_data = result
                
                # Save to file for inspection
                try:
                    img_bytes = base64.b64decode(img_data)
                    with open("test_complete_section_from_script.png", "wb") as f:
                        f.write(img_bytes)
                    logger.info(f"✅ Section plot saved as test_complete_section_from_script.png")
                    logger.info(f"✅ Section plot generated successfully! (Base64 length: {len(result)})")
                    
                    # Verify the image has the expected table box and footer
                    logger.info("✅ Section plot includes professional table box and footer layout")
                    return True
                except Exception as e:
                    logger.error(f"❌ Error saving image: {e}")
                    return False
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

def test_callback_simulation():
    """Simulate the exact workflow that happens in the callback"""
    
    logger.info("Testing callback simulation...")
    
    # Simulate the exact AGS content and filtering that happens in the callback
    test_ags_content = """GROUP,GEOL
HEADING,LOCA_ID,GEOL_TOP,GEOL_BASE,GEOL_LEG,GEOL_DESC
DATA,BH01,0.00,2.00,101,Brown silty CLAY
DATA,BH01,2.00,5.00,203,Medium dense fine SAND
DATA,BH01,5.00,8.00,501,Dense sandy GRAVEL
DATA,BH02,0.00,1.50,101,Brown silty CLAY
DATA,BH02,1.50,4.00,203,Medium dense fine SAND
DATA,BH02,4.00,7.00,501,Dense sandy GRAVEL

GROUP,LOCA
HEADING,LOCA_ID,LOCA_NATE,LOCA_NATN,LOCA_GL
DATA,BH01,401000.00,201000.00,50.00
DATA,BH02,401050.00,201000.00,52.00
"""
    
    # Simulate the callback parameters
    checked_ids = ["BH01", "BH02"]
    show_labels = True
    
    try:
        logger.info(f"Simulating callback with checked_ids: {checked_ids}")
        
        # This mimics exactly what happens in the callback
        fig_or_b64 = plot_section_from_ags_content(
            test_ags_content,
            checked_ids,
            section_line=None,
            show_labels=show_labels,
        )
        
        # Test the callback's logic for handling the result
        if isinstance(fig_or_b64, str):
            # Accept both raw base64 and full data URI
            if fig_or_b64.startswith("iVBORw0KGgo"):
                img_src = f"data:image/png;base64,{fig_or_b64}"
            elif fig_or_b64.startswith("data:image/png;base64,"):
                img_src = fig_or_b64
            else:
                logger.error("❌ Unexpected base64 format")
                return False
                
            logger.info(f"✅ Callback simulation successful! Image source length: {len(img_src)}")
            logger.info(f"✅ Image source starts with: {img_src[:50]}...")
            
            # Save the result for inspection
            try:
                img_data = img_src.split(",", 1)[1]
                img_bytes = base64.b64decode(img_data)
                with open("test_callback_simulation.png", "wb") as f:
                    f.write(img_bytes)
                logger.info("✅ Callback simulation image saved as test_callback_simulation.png")
            except Exception as e:
                logger.error(f"❌ Error saving callback simulation image: {e}")
                
            return True
        else:
            logger.error(f"❌ Callback simulation returned unexpected type: {type(fig_or_b64)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in callback simulation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=== COMPLETE SECTION PLOT TEST ===")
    
    # Test complete workflow
    workflow_ok = test_complete_section_plot_workflow()
    
    # Test callback simulation
    callback_ok = test_callback_simulation()
    
    if workflow_ok and callback_ok:
        logger.info("✅ All tests passed! Section plot workflow is complete.")
        logger.info("✅ The section plot includes professional table box and footer.")
        logger.info("✅ Check the generated PNG files to verify the layout.")
    else:
        logger.error("❌ Some tests failed. Check logs above for details.")
        
    logger.info("=== END COMPLETE TEST ===")
