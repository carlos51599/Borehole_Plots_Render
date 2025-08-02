# GitHub Copilot Instructions

This is a **Dash-based geotechnical visualization application** for rendering AGS (Association of Geotechnical and Geoenvironmental Specialists) borehole data. The architecture balances professional geological plotting with interactive web mapping.

## Core Architecture

### 🏗️ **Modular Monolith Pattern**
- **Entry Point**: `app.py` → `app_modules/` → modular callback registration
- **Plot Generation**: Two implementations coexist:
  - `archive/section_plot_professional_original.py` - **Reference implementation** (gospel)
  - `section/` package - **Modular refactor** (coordinate with archive for compatibility)
- **State Management**: Persistent across callbacks via `dcc.Store` components and global variables

### 📊 **AGS Data Pipeline**
```
AGS Upload → data_loader.py → coordinate_service.py → section/parsing.py → plotting
```

**Critical**: AGS files use **numeric BGS geology codes** (101=TOPSOIL, 102=MADE_GROUND, 203=SANDY_CLAY, 501=GRAVEL). Test data with letter codes (MG, LC, TG) is **incorrect format**.

## Essential Patterns

### 🎯 **Callback Architecture**
```python
# callbacks/ directory - modular pattern
from callbacks.base import CallbackBase

class CustomCallback(CallbackBase):
    def register(self, app):
        @app.callback(...)
        def handler(...):
            # Always include error handling
            try:
                # Implementation
                return result
            except Exception as e:
                logger.error(f"Callback error: {e}")
                return error_state
```

### 🗺️ **Coordinate System Transformations**
```python
# British National Grid (EPSG:27700) → WGS84 (EPSG:4326)
from coordinate_service import convert_bng_to_wgs84
# Always validate coordinates before transformation
```

### 🎨 **Professional Plotting Standards**
- **Reference**: Use `archive/section_plot_professional_original.py` as authoritative
- **Colors**: BGS-standard from `Geology Codes BGS.csv`
- **Output**: A4 landscape (11.69" x 8.27"), 300 DPI
- **Base64**: Always return with `data:image/png;base64,` prefix

## Development Workflows

### 🧪 **Testing Strategy**
```bash
# Always test in tests/ folder if it exists
python test_script_name.py  # Direct execution (PowerShell)
```

### 📁 **File Organization**
- **Reports**: Save .md files to `reports/` if exists
- **Tests**: Save test scripts to `tests/` if exists
- **Logs**: Save log files to `logs/` if exists

### 🔧 **Environment Assumptions**
- **Python**: Pre-configured environment (no venv/conda management)
- **Dependencies**: Use existing `requirements.txt`
- **Execution**: Write code to files, run files (not long terminal commands)

## Critical Implementation Details

### 🏛️ **Archive Pattern**
```python
# ALWAYS check archive/ implementations first
from archive.section_plot_professional_original import plot_section_from_ags_content
# Archive code = gospel for professional plotting standards
```

### 🔍 **AGS Parsing**
```python
# Standard AGS format validation
geol_df, loca_df, abbr_df = parse_ags_geol_section_from_string(ags_content)
# GEOL_LEG column contains numeric codes: "101", "203", "501"
# NOT letter codes: "MG", "LC", "TG"
```

### 🎨 **BGS Geology Codes**
```python
from geology_code_utils import get_geology_color, get_geology_pattern
color = get_geology_color("101")  # Returns "#654321" for TOPSOIL
pattern = get_geology_pattern("203")  # Returns "-/" for SANDY CLAY
```

### 📍 **Map Interactions**
```python
# GeoJSON → Shapely geometry → borehole filtering
from map_utils import filter_selection_by_shape
selected_ids = filter_selection_by_shape(geojson, borehole_data)
```

## Performance Considerations

- **Memory**: Use `memory_manager.py` for large datasets
- **Loading**: Implement `loading_indicators.py` for user feedback
- **Markers**: Use `lazy_marker_manager.py` for map performance
- **DataFrames**: Apply `dataframe_optimizer.py` for efficiency

## Quality Standards

### 🔒 **Error Handling**
```python
# Use enhanced error handling with user feedback
from enhanced_error_handling import handle_callback_error
# Always provide graceful degradation
```

### 📝 **Logging**
```python
import logging
logger = logging.getLogger(__name__)
# Comprehensive logging with context
```

### 🧹 **Code Organization**
- Follow modular patterns in `callbacks/`, `section/`, `app_modules/`
- Reference `archive/` for plotting standards
- Use factory pattern in `app_factory.py` for Dash apps

## Key Files Reference

- **`config.py`**: Figure dimensions, fonts, colors (837 lines)
- **`app_constants.py`**: Application limits and thresholds
- **`Geology Codes BGS.csv`**: Standard geology color/pattern mappings
- **`FLRG - 2025-03-17 1445 - Preliminary - 3.txt`**: Real AGS format example
- **`archive/section_plot_professional_original.py`**: Authoritative plotting reference
