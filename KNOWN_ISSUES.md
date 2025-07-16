## Matplotlib Font Scanning Delay

On first plot in a new session, matplotlib scans all system fonts, causing a noticeable delay and many log lines. This is standard behavior and cannot be fully avoided in a Dash app, especially with multiple workers. The delay only occurs once per Python process.
# Known Issues

## 1. Old Shapes Not Visually Cleared from Map

**Issue**: When drawing multiple shapes on the map, old shapes remain visually displayed even though only the most recent shape is used for borehole selection and plotting.

**Status**: **FIXED**

**Solution Applied**:
- Added dedicated `selection-shapes` FeatureGroup to separate selection shapes from persistent markers
- Created `create_selection_shape_visual()` function to display drawn polygons and rectangles
- Updated all callback return statements to clear old selection shapes when new ones are drawn
- Polylines continue to be displayed in `pca-line-group` with their buffer zones
- Borehole markers remain persistent in `borehole-markers` group

**Changes Made**:
- Added `selection-shapes` FeatureGroup to `app.py`
- Modified callback outputs in `callbacks_split.py` to include selection shapes control
- Implemented visual feedback for polygon and rectangle selections
- Old shapes now automatically disappear when new selections are made

**Impact**: Users now get clear visual feedback showing only the current selection, while maintaining all functionality

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
