# Known Issues

## 1. Old Shapes Not Visually Cleared from Map

**Issue**: When drawing multiple shapes on the map, old shapes remain visually displayed even though only the most recent shape is used for borehole selection and plotting.

**Status**: Unresolved

**Impact**: Visual only - functionality is correct (only the last drawn shape is used for selection)

**Attempted Solutions**:
- Client-side callbacks to modify geojson and trigger clear_all
- Server-side callbacks to trigger clear_all property
- Direct manipulation of Leaflet EditControl instance
- Multiple approaches with allow_duplicate=True

**Root Cause**: The dash-leaflet EditControl component doesn't properly clear previously drawn shapes when new ones are added, despite multiple callback approaches.

**Workaround**: Users can manually use the "Remove All" tool in the drawing toolbar to clear old shapes.

---

## 2. Marker Position Offset During Zoom

**Issue**: Map markers appear at correct positions when fully zoomed in, but offset southeast when zooming out.

**Status**: **FIXED**

**Solution Applied**:
- Improved marker icon configuration with proper `iconAnchor` setting
- Added detailed coordinate transformation logging
- Used standard Leaflet marker dimensions and anchor points
- Enhanced validation of transformed coordinates

**Changes Made**:
- Set `iconAnchor: [12, 41]` to properly anchor the marker icon to its geographical position
- Added coordinate validation in transform_coordinates function
- Improved logging for debugging coordinate transformations

**Impact**: Markers should now stay in correct positions across all zoom levels
