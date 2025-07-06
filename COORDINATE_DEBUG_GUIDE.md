# Coordinate Issues - Debugging Summary

## Key Changes Made

### 1. Fixed Coordinate Storage During File Upload
**Problem**: Coordinates were calculated for markers but not stored in DataFrame for later use.

**Fix**: Added lat/lon columns to DataFrame during file upload:
```python
# Added in app.py during file upload
loca_df["lat"] = None
loca_df["lon"] = None

# Store transformed coordinates back into DataFrame
loca_df.at[i, "lat"] = lat
loca_df.at[i, "lon"] = lon
```

### 2. Enhanced Coordinate Validation
**Problem**: Invalid coordinates causing zoom and selection issues.

**Fix**: Added comprehensive validation:
- UK bounds checking (lat: 49.0-61.0, lon: -8.0-2.0)
- Type validation for numeric coordinates
- BNG range validation (easting: 0-800000, northing: 0-1400000)

### 3. Improved Logging for Drawing Operations
**Problem**: No visibility into why "No boreholes found" occurs.

**Fix**: Added extensive logging:
- Complete GeoJSON structure logging
- Coordinate ranges and sample values
- Point-by-point polygon containment checking
- Distance calculations for debugging

### 4. Fixed DataFrame Handling
**Problem**: Potential DataFrame view issues causing selection problems.

**Fix**: Added `.copy()` to all DataFrame filtering operations to avoid view issues.

## Debugging Steps

### Check Coordinate Transformation
Your debug output shows:
```
First marker (WGS84): [53.87266595289811, -2.1836936523995725]
```

This looks correct for UK coordinates (around Manchester/Lancashire area).

### Check Stored Coordinates
After upload, the logs should show:
```
Storing X valid lat/lon coordinates in DataFrame
Sample stored coordinates: lat=53.872666, lon=-2.183694
```

### Check Drawing Selection
When drawing, logs should show:
- GeoJSON structure with coordinate arrays
- Available borehole coordinates
- Point-by-point containment checking
- Distance calculations if no points are found

## Common Issues and Solutions

### Issue 1: Coordinates Not Stored
**Symptom**: "lat/lon columns missing from stored DataFrame"
**Solution**: Coordinates now stored during file upload

### Issue 2: GeoJSON Format Mismatch  
**Symptom**: "Unsupported geometry type" or no features found
**Solution**: Enhanced logging shows exact GeoJSON structure

### Issue 3: Coordinate System Mismatch
**Symptom**: Markers show but selection doesn't work
**Solution**: Both markers and selection now use same coordinate transformation

### Issue 4: Drawing Tool Geometry Type
**Symptom**: Rectangle drawing doesn't work
**Solution**: Check logs for actual geometry type (likely "Polygon" not "Rectangle")

## Test Your Changes

1. **Upload AGS file** - Check logs for coordinate storage messages
2. **Draw a shape around markers** - Check logs for:
   - GeoJSON structure
   - Available coordinates
   - Point containment results
3. **If still "No boreholes found"** - Check:
   - Are lat/lon columns present?
   - Do coordinate ranges make sense?
   - What geometry type is being generated?

## Expected Log Output

### During Upload:
```
Storing 30 valid lat/lon coordinates in DataFrame
Sample stored coordinates: lat=53.872666, lon=-2.183694
Stored coordinate ranges: lat [53.800000, 53.900000]
Stored coordinate ranges: lon [-2.200000, -2.100000]
```

### During Drawing:
```
✓ lat/lon columns already exist in DataFrame
Using stored coordinates: 30 valid points
Polygon has 5 vertices
Available borehole coordinates:
  BH001: (-2.183694, 53.872666)
  BH002: (-2.185000, 53.873000)
  ...
Point BH001 (-2.183694, 53.872666): True
Selected borehole IDs: ['BH001', 'BH002', ...]
```

The enhanced logging should now clearly show where the selection process is failing.
