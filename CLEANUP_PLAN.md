# Repository Cleanup Plan - July 7, 2025

## Current Status Analysis

### 📁 PRODUCTION FILES (Keep)
- `app.py` - ✅ Main development application (FIXED)
- `app_fixed.py` - ✅ Alternative cleaned version (FIXED) 
- `requirements.txt` - ✅ Dependencies
- Core modules: `data_loader.py`, `section_plot.py`, `borehole_log.py`, `map_utils.py`, `utils.py`, `config.py`, `section_logic.py`

### 🧪 TEST/DEBUG FILES (Review for cleanup)
**Multiple app variants:**
- `app_debug_network.py` - Network debugging version (uses incompatible `app.run_server()`)
- `app_render.py` - Deployment version (uses incompatible `app.run_server()`)
- `app_network_test.py` - Network test
- `simplified_test.py` - Basic test

**Test utilities:**
- `test_*.py` files (15+ files)
- `*_test.py` files  
- `minimal_test.py`, `marker_test.py`, `integration_test.py`

**Debug utilities:**
- `debug_monitor.py`
- `diagnose_app.py`
- `diagnose_network.ps1`
- `startup_debug.py`
- `network_diagnostics.py`

### 📄 DOCUMENTATION FILES (Consolidate)
**Status/completion docs:**
- `DEBUG_SUMMARY.md`
- `DRAWING_TOOLS_FIX.md`
- `MARKER_AUTOZOOM_COMPLETE.md`
- `MAP_INTERACTION_FIXES.md`
- `COORDINATE_DEBUG_GUIDE.md`
- `COORDINATE_TRANSFORM_FIX.md`
- `INTEGRATION_COMPLETE.md`
- `DASH_VERSION_COMPATIBILITY_NOTES.md`

### 🗂️ LEGACY FILES
- `old_streamlit_files/` - Archived Streamlit implementation
- `__pycache__/` - Python cache files

### 📝 LOG/TEMP FILES (Clean)
- `*.log` files
- `run_test.bat`, `start_app.bat`
- `render.yaml`, `Dockerfile`

## Cleanup Actions

### Phase 1: Fix Version Compatibility Issues
- [ ] Fix `app.run_server()` calls in remaining files
- [ ] Standardize on working method for current Dash version

### Phase 2: Remove Redundant Files  
- [ ] Keep only 1-2 main app files
- [ ] Remove obsolete test files
- [ ] Archive debug utilities

### Phase 3: Consolidate Documentation
- [ ] Create single comprehensive README
- [ ] Archive status/completion docs
- [ ] Keep only essential guides

### Phase 4: Clean Temporary Files
- [ ] Remove log files
- [ ] Clean cache directories
- [ ] Remove batch files (replace with proper instructions)

### Phase 5: Repository Structure
```
Geo_Borehole_Sections_Render/
├── README.md                    # Main documentation
├── app.py                       # Primary application  
├── requirements.txt             # Dependencies
├── core/                        # Core modules
│   ├── data_loader.py
│   ├── section_plot.py  
│   ├── borehole_log.py
│   ├── map_utils.py
│   └── utils.py
├── config.py                    # Configuration
├── docs/                        # Documentation archive
│   ├── DASH_VERSION_NOTES.md
│   └── TROUBLESHOOTING.md
├── archive/                     # Archived files
│   ├── old_streamlit_files/
│   ├── debug_utilities/
│   └── test_files/
└── deployment/                  # Deployment configs
    ├── Dockerfile
    └── render.yaml
```

## Recommended Actions

1. **IMMEDIATE**: Fix version compatibility in remaining files
2. **Short-term**: Remove redundant app variants 
3. **Medium-term**: Consolidate documentation
4. **Long-term**: Implement proper testing framework

## Files to Keep vs Archive

### ✅ KEEP (Essential)
- `app.py` (main)
- `app_fixed.py` (alternative) 
- Core modules (data_loader, section_plot, etc.)
- `requirements.txt`
- `DASH_VERSION_COMPATIBILITY_NOTES.md`

### 🗃️ ARCHIVE (Historical reference)
- All test_*.py files
- Debug utilities
- Status completion docs
- Old Streamlit files (already archived)

### ❌ DELETE (Obsolete)
- Log files (*.log)
- Cache files (__pycache__)
- Temporary batch files

Would you like me to proceed with this cleanup plan?
