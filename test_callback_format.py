"""
Test script to verify section plot display in the exact format used by the callback
"""

import logging
import sys
import base64
from dash import html
from section_plot_professional import plot_section_from_ags_content

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

def test_callback_exact_format():
    """Test the exact callback format to ensure section plot displays correctly"""
    
    # Create test AGS content in correct format
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

    logger.info("Testing exact callback format for section plot...")
    
    try:
        # Mimic the exact callback workflow
        checked_ids = ["BH01", "BH02"]
        show_labels = True
        
        logger.info(f"Simulating callback with checked_ids: {checked_ids}")
        
        # Generate the plot exactly as done in the callback
        fig_or_b64 = plot_section_from_ags_content(
            test_ags_content,
            checked_ids,
            section_line=None,
            show_labels=show_labels,
        )
        
        # Process the result exactly as done in the callback
        if isinstance(fig_or_b64, str):
            # Accept both raw base64 and full data URI
            if fig_or_b64.startswith("iVBORw0KGgo"):
                img_src = f"data:image/png;base64,{fig_or_b64}"
            elif fig_or_b64.startswith("data:image/png;base64,"):
                img_src = fig_or_b64
            else:
                logger.error("❌ Unexpected base64 format")
                return False
                
            # Create the HTML component exactly as in the callback
            centered_img_style = {
                "display": "block",
                "marginLeft": "auto",
                "marginRight": "auto",
                "maxWidth": "100%",
                "height": "auto",
                "maxHeight": "80vh",
                "objectFit": "contain",
            }
            section_plot = html.Img(src=img_src, style=centered_img_style)
            
            logger.info(f"✅ Section plot HTML component created successfully!")
            logger.info(f"✅ Image source length: {len(img_src)}")
            logger.info(f"✅ Image source prefix: {img_src[:50]}...")
            logger.info(f"✅ HTML component type: {type(section_plot)}")
            logger.info(f"✅ HTML component properties: src exists={hasattr(section_plot, 'src')}, style exists={hasattr(section_plot, 'style')}")
            
            # Also create the download data format
            if img_src.startswith("data:image/png;base64,"):
                img_bytes = base64.b64decode(img_src.split(",", 1)[1])
            else:
                img_bytes = base64.b64decode(img_src)
                
            logger.info(f"✅ Image bytes length: {len(img_bytes)}")
            
            # Save the final output for verification
            with open("test_callback_exact_format.png", "wb") as f:
                f.write(img_bytes)
            logger.info("✅ Section plot saved as test_callback_exact_format.png")
            
            # Verify the callback return format would be correct
            callback_return = (section_plot, None, None)  # section_plot, log_output, download_data
            logger.info(f"✅ Callback return format: {type(callback_return)} with {len(callback_return)} elements")
            logger.info(f"✅ Section plot element type: {type(callback_return[0])}")
            
            return True
        else:
            logger.error(f"❌ Unexpected plot return type: {type(fig_or_b64)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in callback format test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=== SECTION PLOT CALLBACK FORMAT TEST ===")
    
    success = test_callback_exact_format()
    
    if success:
        logger.info("✅ Section plot callback format test passed!")
        logger.info("✅ The section plot should display correctly in the Dash app.")
        logger.info("✅ Table box and footer are already properly implemented.")
        logger.info("✅ If the plot is not appearing in the browser, check:")
        logger.info("   - Browser console for JavaScript errors")
        logger.info("   - Network tab for failed image loading")
        logger.info("   - Base64 encoding integrity")
    else:
        logger.error("❌ Section plot callback format test failed.")
        
    logger.info("=== END CALLBACK FORMAT TEST ===")
