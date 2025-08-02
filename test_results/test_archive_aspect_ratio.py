#!/usr/bin/env python3
"""
Test aspect ratio fix with exact archive implementation
"""

import sys
import os
sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
import matplotlib.figure
from section.utils import convert_figure_to_base64
import base64
import io
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)

def test_archive_style_aspect_ratio():
    """Test that the archive-style implementation preserves A4 landscape aspect ratio"""
    
    print("Testing aspect ratio with archive-style implementation...")
    
    # Create A4 landscape figure (11.69" x 8.27")
    fig = plt.figure(figsize=(11.69, 8.27))
    
    # Add simple content
    ax = fig.add_subplot(111)
    ax.plot([0, 1], [0, 1])
    ax.set_title("Test Plot")
    
    # Convert to base64 using archive-style implementation
    base64_data = convert_figure_to_base64(fig, dpi=150)
    
    # Clean base64 data
    if base64_data.startswith('data:image/png;base64,'):
        base64_clean = base64_data.replace('data:image/png;base64,', '')
    else:
        base64_clean = base64_data
    
    # Decode and check dimensions
    image_bytes = base64.b64decode(base64_clean)
    image = Image.open(io.BytesIO(image_bytes))
    
    width, height = image.size
    aspect_ratio = width / height
    
    print(f"Image dimensions: {width} x {height}")
    print(f"Aspect ratio: {aspect_ratio:.6f}")
    print(f"Expected A4 landscape ratio: 1.414214")
    print(f"Difference: {abs(aspect_ratio - 1.414214):.6f}")
    
    # Check if aspect ratio is correct (within tolerance)
    if abs(aspect_ratio - 1.414214) < 0.001:
        print("✅ PASS: Aspect ratio matches A4 landscape")
        return True
    else:
        print("❌ FAIL: Aspect ratio does not match A4 landscape")
        return False

if __name__ == "__main__":
    success = test_archive_style_aspect_ratio()
    if success:
        print("\n🎉 Archive-style implementation maintains correct A4 aspect ratio!")
    else:
        print("\n💥 Archive-style implementation has aspect ratio issues!")
    
    plt.close('all')
