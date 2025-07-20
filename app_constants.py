"""
Application Constants Configuration

This module centralizes all hardcoded values, magic numbers, and configuration
constants used throughout the application, improving maintainability and
making configuration changes easier.

Usage:
    from app_constants import MAP_CONFIG, PLOT_CONFIG, FILE_LIMITS
"""

# ====================================================================
# FILE PROCESSING LIMITS
# ====================================================================


class FileLimits:
    """File size and processing limits"""

    MAX_FILE_SIZE_MB = 50  # Maximum individual file size
    MAX_TOTAL_FILES_MB = 200  # Maximum total upload size
    MAX_FILES_COUNT = 20  # Maximum number of files per upload
    SUPPORTED_EXTENSIONS = [".ags", ".AGS"]  # Supported file extensions


# ====================================================================
# MAP CONFIGURATION
# ====================================================================


class MapConfig:
    """Map display and interaction constants"""

    # Default map center (UK)
    DEFAULT_CENTER_LAT = 54.5
    DEFAULT_CENTER_LON = -2.0
    DEFAULT_ZOOM = 6

    # Map bounds (UK coverage)
    UK_BOUNDS = {"north": 61.0, "south": 49.0, "east": 2.0, "west": -11.0}

    # Marker icons URLs
    BLUE_MARKER_URL = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
    GREEN_MARKER_URL = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"
    RED_MARKER_URL = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png"
    ORANGE_MARKER_URL = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png"

    # Map tile layers
    DEFAULT_TILE_LAYER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    SATELLITE_TILE_LAYER = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

    # Buffer settings
    DEFAULT_BUFFER_METERS = 50
    MIN_BUFFER_METERS = 10
    MAX_BUFFER_METERS = 1000


# ====================================================================
# PLOT CONFIGURATION
# ====================================================================


class PlotConfig:
    """Plotting and visualization constants"""

    # Figure dimensions (inches)
    BOREHOLE_LOG_WIDTH = 8.27  # A4 width
    BOREHOLE_LOG_HEIGHT = 11.69  # A4 height
    SECTION_PLOT_WIDTH = 11.69  # A4 landscape width
    SECTION_PLOT_HEIGHT = 8.27  # A4 landscape height

    # DPI settings
    DEFAULT_DPI = 300  # High quality for professional output
    PREVIEW_DPI = 150  # Lower DPI for web preview

    # Color schemes
    DEFAULT_COLORMAP = "tab20"
    GEOLOGY_COLORMAP = "Set3"

    # Font settings
    DEFAULT_FONT_SIZE = 8
    TITLE_FONT_SIZE = 12
    LABEL_FONT_SIZE = 10

    # Line widths
    DEFAULT_LINE_WIDTH = 1.0
    THICK_LINE_WIDTH = 2.0
    THIN_LINE_WIDTH = 0.5

    # Margins and spacing
    LEFT_MARGIN = 0.1
    RIGHT_MARGIN = 0.05
    TOP_MARGIN = 0.05
    BOTTOM_MARGIN = 0.1

    # Grid settings
    GRID_ALPHA = 0.3
    GRID_LINE_WIDTH = 0.5


# ====================================================================
# DATA PROCESSING CONFIGURATION
# ====================================================================


class DataConfig:
    """Data processing and validation constants"""

    # AGS file processing
    ENCODING_OPTIONS = ["utf-8", "latin-1", "cp1252"]  # Try these encodings in order
    MAX_ROWS_PREVIEW = 1000  # Maximum rows to show in data preview

    # Coordinate systems
    BNG_EPSG = "EPSG:27700"  # British National Grid
    WGS84_EPSG = "EPSG:4326"  # WGS84 Geographic
    WEB_MERCATOR_EPSG = "EPSG:3857"  # Web Mercator

    # Validation thresholds
    MIN_VALID_COORDINATE = -999999
    MAX_VALID_COORDINATE = 999999
    MIN_DEPTH = 0.0
    MAX_DEPTH = 1000.0  # meters

    # Column mappings for common AGS fields
    REQUIRED_LOCA_COLUMNS = ["LOCA_ID", "LOCA_NATE", "LOCA_NATN"]
    OPTIONAL_LOCA_COLUMNS = ["LOCA_GL", "LOCA_FDEP", "LOCA_TYPE"]


# ====================================================================
# UI CONFIGURATION
# ====================================================================


class UIConfig:
    """User interface constants"""

    # Colors (Dash/HTML color codes)
    PRIMARY_COLOR = "#1f77b4"
    SUCCESS_COLOR = "#2ca02c"
    WARNING_COLOR = "#ff7f0e"
    ERROR_COLOR = "#d62728"
    INFO_COLOR = "#17a2b8"

    # Component styling
    CARD_STYLE = {
        "border": "1px solid #ddd",
        "border-radius": "5px",
        "padding": "15px",
        "margin": "10px 0",
        "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
    }

    BUTTON_STYLE = {
        "margin": "5px",
        "padding": "8px 16px",
        "border-radius": "4px",
        "border": "none",
        "cursor": "pointer",
    }

    # Loading indicators
    LOADING_SPINNER_COLOR = PRIMARY_COLOR
    LOADING_DELAY_MS = 500  # Delay before showing loading indicator

    # Alert messages
    MAX_ALERT_LENGTH = 500  # Maximum characters in alert messages
    ALERT_DURATION_MS = 5000  # How long to show alerts


# ====================================================================
# PERFORMANCE CONFIGURATION
# ====================================================================


class PerformanceConfig:
    """Performance tuning constants"""

    # Caching
    COORDINATE_TRANSFORM_CACHE_SIZE = 128  # LRU cache size for transformations
    DATA_CACHE_SIZE = 32  # Cache size for processed data
    CACHE_TTL_SECONDS = 3600  # Time to live for cached items

    # Processing limits
    MAX_PROCESSING_TIME_SECONDS = 300  # 5 minutes max processing
    BATCH_SIZE = 1000  # Number of records to process in batches
    MAX_CONCURRENT_OPERATIONS = 4  # Maximum parallel operations

    # Memory management
    MAX_MEMORY_USAGE_MB = 512  # Maximum memory usage per process
    GARBAGE_COLLECTION_THRESHOLD = 100  # Objects before triggering GC


# ====================================================================
# LOGGING CONFIGURATION
# ====================================================================


class LoggingConfig:
    """Logging configuration constants"""

    # Log levels
    DEFAULT_LEVEL = "INFO"
    DEBUG_LEVEL = "DEBUG"
    PRODUCTION_LEVEL = "WARNING"

    # Log formats
    DETAILED_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    # File settings
    MAX_LOG_SIZE_MB = 10
    BACKUP_COUNT = 5  # Number of backup log files to keep

    # Log file names
    APP_LOG_FILE = "app.log"
    ERROR_LOG_FILE = "error.log"
    DEBUG_LOG_FILE = "debug.log"


# ====================================================================
# GEOLOGY CODES CONFIGURATION
# ====================================================================


class GeologyConfig:
    """Geology-specific constants"""

    # Default geology file
    DEFAULT_GEOLOGY_FILE = "Geology Codes BGS.csv"

    # Default colors for unknown geology codes
    UNKNOWN_GEOLOGY_COLOR = "#ffffff"
    UNKNOWN_GEOLOGY_PATTERN = "*"

    # Legend settings
    MAX_LEGEND_ITEMS = 20
    LEGEND_FONT_SIZE = 8
    LEGEND_SYMBOL_SIZE = 12


# ====================================================================
# CONVENIENCE EXPORTS
# ====================================================================

# Export all configurations for easy access
FILE_LIMITS = FileLimits()
MAP_CONFIG = MapConfig()
PLOT_CONFIG = PlotConfig()
DATA_CONFIG = DataConfig()
UI_CONFIG = UIConfig()
PERFORMANCE_CONFIG = PerformanceConfig()
LOGGING_CONFIG = LoggingConfig()
GEOLOGY_CONFIG = GeologyConfig()

# Version information
APP_VERSION = "1.0.0"
CONFIG_VERSION = "1.0.0"

# Export list for star imports
__all__ = [
    "FileLimits",
    "MapConfig",
    "PlotConfig",
    "DataConfig",
    "UIConfig",
    "PerformanceConfig",
    "LoggingConfig",
    "GeologyConfig",
    "FILE_LIMITS",
    "MAP_CONFIG",
    "PLOT_CONFIG",
    "DATA_CONFIG",
    "UI_CONFIG",
    "PERFORMANCE_CONFIG",
    "LOGGING_CONFIG",
    "GEOLOGY_CONFIG",
    "APP_VERSION",
    "CONFIG_VERSION",
]

if __name__ == "__main__":
    # Simple test to verify configuration loading
    print("Application Constants Configuration")
    print(f"Version: {APP_VERSION}")
    print(f"Config Version: {CONFIG_VERSION}")
    print("\nAvailable configurations:")
    for config_name in __all__:
        if config_name.endswith("_CONFIG") or config_name.endswith("_LIMITS"):
            print(f"  - {config_name}")
