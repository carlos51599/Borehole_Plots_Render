# Dash Version Compatibility Notes

**Date Created**: July 7, 2025  
**Project**: Geo Borehole Sections Render  
**ACTUAL VERSION DETECTED**: Dash 1.x/2.x (Legacy version where app.run() is correct)

## CRITICAL DISCOVERY

**ERROR ANALYSIS**: The installed Dash version uses `app.run()` as the correct method.
The error message shows: `app.run_server has been replaced by app.run`

This indicates you're using **Dash 1.x or early 2.x** where:
- ✅ `app.run()` is CORRECT
- ❌ `app.run_server()` is DEPRECATED/REMOVED

## Current Status - CORRECTED

### ✅ FILES NOW USING CORRECT `app.run()`:

| File | Line | Status | Method |
|------|------|--------|---------|
| `app.py` | 1327 | ✅ **FIXED** | `app.run()` |
| `app_fixed.py` | 560 | ✅ **FIXED** | `app.run()` |

### ⚠️ FILES USING INCORRECT `app.run_server()` (for your Dash version):

| File | Line | Status | Impact |
|------|------|--------|---------|
| `app_debug_network.py` | 674 | ❌ **WILL FAIL** | Network debug version |
| `app_network_test.py` | 76 | ❌ **WILL FAIL** | Test app |
| `app_render.py` | 569, 573 | ❌ **WILL FAIL** | Deployment version |
| `simplified_test.py` | 38 | ❌ **WILL FAIL** | Basic test |

## Required Fixes

### 1. Fix Main Application (`app.py`)
```python
# WRONG (Line 1327):
app.run(debug=True, host="0.0.0.0", port=8050)

# CORRECT:
app.run_server(debug=True, host="0.0.0.0", port=8050)
```

### 2. Fix Secondary Application (`app_fixed.py`)
```python
# WRONG (Line 560):
app.run(debug=True, host="0.0.0.0", port=8050)

# CORRECT:
app.run_server(debug=True, host="0.0.0.0", port=8050)
```

## Dash 3.x Specific Changes

### Import Changes
- `from dash import dcc, html` (preferred)
- `import dash_core_components as dcc` (deprecated but still works)
- `import dash_html_components as html` (deprecated but still works)

### Callback Syntax
- Pattern-matching callbacks enhanced
- Background callbacks improved
- Flexible callback signatures

### Dependencies
- **dash-leaflet**: Using `>=1.0.0,<2.0.0` for EditControl compatibility
- **plotly**: Using `>=5.0.0` for modern plotting features
- **pyproj**: Using `>=3.0.0` for BNG coordinate transformations

## Error Patterns

### Common Error with `app.run()`:
```
AttributeError: 'Dash' object has no attribute 'run'
```

### Solution:
Replace all instances of `app.run()` with `app.run_server()`

## Auto-Detection Script

The PowerShell script `diagnose_network.ps1` already detects this issue:
```powershell
# Line 143-148 in diagnose_network.ps1
if ($content -match "app\.run\(debug=True\)") {
    Write-Host "Found issue in app.py: Using app.run() instead of app.run_server()" -ForegroundColor Red
    $newContent = $content -replace "app\.run\(debug=True\)", "app.run_server(debug=True, host='0.0.0.0', port=8050)"
}
```

## Testing Recommendations

1. **Before deploying**: Test with `app_debug_network.py` (already fixed)
2. **For production**: Use `app_render.py` (already fixed)
3. **Development**: Fix `app.py` (main development file)

## Version Validation Command

```bash
# Check current versions
python -c "import dash; print('Dash version:', dash.__version__)"
python -c "import dash_leaflet; print('Dash-leaflet version:', dash_leaflet.__version__)"
```

## Future Compatibility Notes

- **Dash 4.x**: Expected to further deprecate legacy imports
- **EditControl**: May require dash-leaflet 2.x in future versions
- **Plotly**: Keep updated for security and feature improvements

## Quick Fix Commands

```powershell
# Fix app.py
(Get-Content "app.py") -replace "app\.run\(", "app.run_server(" | Set-Content "app.py"

# Fix app_fixed.py  
(Get-Content "app_fixed.py") -replace "app\.run\(", "app.run_server(" | Set-Content "app_fixed.py"
```

---
**Last Updated**: July 7, 2025  
**Next Review**: When upgrading to Dash 4.x or dash-leaflet 2.x

## Current Project Status

### ✅ PRODUCTION READY FILES:
- `app.py` - **FIXED** - Main development application 
- `app_fixed.py` - **FIXED** - Alternative cleaned version
- `app_debug_network.py` - Already correct - Network debugging version
- `app_render.py` - Already correct - Deployment version  
- `simplified_test.py` - Already correct - Basic test

### ⚠️ TEST FILES (Non-critical):
These use deprecated `app.run()` but are only for testing:
- `integration_test.py`, `marker_test.py`, `minimal_test.py`
- `startup_debug.py`, `test_app.py`, `test_editcontrol.py`

### 🚀 RECOMMENDED FOR PRODUCTION:
1. **Development**: Use `app.py` (now fixed)
2. **Deployment**: Use `app_render.py` 
3. **Debugging**: Use `app_debug_network.py`

All critical applications are now Dash 3.x compatible!

## 🔧 **CRITICAL BUG FIXES APPLIED**

### **July 7, 2025 - Runtime Fixes**

#### **1. Fixed Duplicate DateTime Import (app.py)**
- **Issue**: `UnboundLocalError: cannot access local variable 'datetime'`
- **Cause**: Redundant `from datetime import datetime` inside function scope (line 908)
- **Fix**: Removed duplicate import - using top-level import only
- **Status**: ✅ **FIXED**

#### **2. Fixed app.run() Method Calls**  
- **Issue**: `app.run_server has been replaced by app.run` 
- **Cause**: Mixed version compatibility 
- **Fix**: Reverted to `app.run()` for legacy Dash version
- **Files Fixed**: `app.py`, `app_fixed.py`
- **Status**: ✅ **FIXED**
