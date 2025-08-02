"""
Check what's available in config_modules to fix the import error.
"""


def main():
    """Check config_modules contents."""
    print("=== Config Modules Analysis ===")

    try:
        import config_modules

        print("Available attributes in config_modules:")
        attrs = [attr for attr in dir(config_modules) if not attr.startswith("_")]
        for attr in sorted(attrs):
            print(f"  - {attr}")

        print("\nChecking for SECTION_PLOT_CENTER_STYLE...")
        if hasattr(config_modules, "SECTION_PLOT_CENTER_STYLE"):
            print("✅ SECTION_PLOT_CENTER_STYLE found!")
        else:
            print("❌ SECTION_PLOT_CENTER_STYLE not found!")
            print("Looking for similar attributes...")
            for attr in attrs:
                if (
                    "SECTION" in attr
                    or "PLOT" in attr
                    or "CENTER" in attr
                    or "STYLE" in attr
                ):
                    print(f"  - Similar: {attr}")

        # Check individual modules
        print("\nChecking individual config modules:")
        from config_modules import styles

        style_attrs = [attr for attr in dir(styles) if not attr.startswith("_")]
        print(f"Styles module has {len(style_attrs)} attributes:")
        for attr in sorted(style_attrs):
            if "SECTION" in attr or "PLOT" in attr or "CENTER" in attr:
                print(f"  - {attr}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
