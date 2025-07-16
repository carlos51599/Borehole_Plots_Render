"""Simple test to isolate the issue"""

print("Testing imports...")

try:
    import matplotlib.pyplot as plt

    print("✓ matplotlib imported")
except Exception as e:
    print(f"✗ matplotlib error: {e}")
    exit(1)

try:
    import pandas as pd

    print("✓ pandas imported")
except Exception as e:
    print(f"✗ pandas error: {e}")
    exit(1)

try:
    from geology_code_utils import load_geology_code_mappings

    print("✓ geology_code_utils imported")
except Exception as e:
    print(f"✗ geology_code_utils error: {e}")
    # Don't exit, continue without it

print("Defining function...")


def plot_borehole_log_from_ags_content(ags_content, loca_id, **kwargs):
    """Simple test function"""
    return "Test function works"


print("Function defined successfully")

if __name__ == "__main__":
    print("Module executed as main")
