# Dash App Debug Summary

## Issues Identified and Fixes Applied

### 1. Inconsistent Zooming After File Upload
**Problem**: Map zooms to random locations instead of centering on borehole markers.

**Root Causes**:
- Invalid coordinate transformations from BNG to WGS84
- Invalid coordinates not being filtered out before median calculation
- No validation of final calculated center coordinates

**Fixes Applied**:
- Enhanced coordinate validation in `transform_coordinates()` function
- Added comprehensive validation in auto-zoom calculation
- Added UK bounds checking (lat: 49.0-61.0, lon: -8.0-2.0)
- Improved error handling for coordinate edge cases
- Added extensive logging to track coordinate transformation process

### 2. Drawing Tools Not Creating Section Plots
**Problem**: Drawing shapes on map results in "No boreholes found in selected area"

**Root Causes**:
- DataFrame filtering function not properly handling lat/lon columns
- Inconsistent return types between filtering functions
- Missing coordinate transformation for stored borehole data
- Potential DataFrame view vs copy issues

**Fixes Applied**:
- Added automatic lat/lon column creation for stored borehole data
- Enhanced `filter_selection_by_shape()` function with comprehensive logging
- Fixed DataFrame filtering to use `.copy()` to avoid view issues
- Improved coordinate validation throughout the filtering process
- Enhanced error handling and logging in drawing operations

### 3. Enhanced Logging System
**Improvements Made**:
- Added extensive logging throughout the main callback
- Detailed logging of GeoJSON structure and feature processing
- Coordinate transformation logging with validation
- Auto-zoom calculation logging with step-by-step breakdown
- Drawing operation logging with detailed error tracking

## Key Files Modified

### app.py
- Enhanced `transform_coordinates()` with validation and logging
- Improved auto-zoom calculation with robust coordinate validation
- Added comprehensive logging in drawing operations section
- Enhanced error handling for edge cases
- Added detailed callback parameter logging

### map_utils.py
- Complete rewrite of `filter_selection_by_shape()` function
- Added individual geometry filtering functions (Rectangle, Polygon, LineString)
- Enhanced error handling and logging for each geometry type
- Fixed DataFrame filtering to use `.copy()` and avoid view issues
- Improved coordinate validation and bounds checking

## Testing Recommendations

1. **Test Different AGS Files**: Upload various AGS files to verify consistent zooming behavior
2. **Test Drawing Tools**: Try drawing rectangles, polygons, and lines to verify selection works
3. **Check Log Files**: Monitor `app_debug.log` for detailed diagnostic information
4. **Verify Coordinates**: Ensure all marker positions are within UK bounds

## Debugging Tips

1. **Check Coordinate Ranges**: In logs, look for coordinate values outside UK bounds
2. **Monitor Drawing Events**: Look for detailed GeoJSON structure logging when drawing
3. **Validate Filtering**: Check if boreholes are being found in drawn areas
4. **Auto-zoom Tracking**: Follow the auto-zoom calculation logs to identify issues

## Expected Behavior After Fixes

1. **File Upload**: Map should consistently center on median marker location with appropriate zoom
2. **Drawing Tools**: Should reliably select boreholes within drawn shapes
3. **Section Plots**: Should generate successfully when boreholes are selected
4. **Error Messages**: Should be clear and actionable when issues occur

## Next Steps

1. Run the app and test with various AGS files
2. Try drawing different shapes (rectangles, polygons, lines)
3. Check the detailed logs in `app_debug.log` for any remaining issues
4. If problems persist, the logs will now provide much more detailed information for further debugging

## Known Limitations

- Coordinate transformation assumes British National Grid (EPSG:27700) input
- UK bounds checking may be too restrictive for some edge cases
- Drawing buffer distance for LineString is fixed at 50 meters
- Polygon validation may auto-fix invalid geometries
