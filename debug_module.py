"""Debug version of professional borehole log"""

print("Starting module import...")

try:
    import matplotlib.pyplot as plt

    print("✓ matplotlib imported")
except Exception as e:
    print(f"✗ matplotlib error: {e}")

try:
    import matplotlib.patches as patches

    print("✓ patches imported")
except Exception as e:
    print(f"✗ patches error: {e}")

try:
    import pandas as pd

    print("✓ pandas imported")
except Exception as e:
    print(f"✗ pandas error: {e}")

try:
    import logging

    print("✓ logging imported")
except Exception as e:
    print(f"✗ logging error: {e}")

try:
    from typing import Optional, Tuple

    print("✓ typing imported")
except Exception as e:
    print(f"✗ typing error: {e}")

try:
    from geology_code_utils import load_geology_mapping

    print("✓ geology_code_utils imported")
except Exception as e:
    print(f"✗ geology_code_utils error: {e}")

print("Attempting to define function...")


def plot_borehole_log_from_ags_content():
    """Test function"""
    return "Function defined successfully"


print("Function defined!")
print("Module import complete!")
