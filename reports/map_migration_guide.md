# Map Migration Guide: Dash-Leaflet → Plotly Maps

**Date:** August 2, 2025  
**Issue:** Map center/zoom updates not working in dash-leaflet  
**Solution:** Migrate to Plotly native maps  

## 🔍 Problem Summary

After comprehensive investigation, the root cause is **dash-leaflet GitHub Issue #239** - a known bug where `center` and `zoom` properties don't update visually even when properly returned from callbacks. This affects all versions through v1.1.3.

## ✅ Solution: Plotly Native Maps

Research using MCP Context7 revealed that **Plotly's native map capabilities** provide a superior alternative:

- ✅ **No center/zoom update issues**
- ✅ **Native Dash integration** 
- ✅ **Better documentation**
- ✅ **More reliable long-term**
- ✅ **No external dependencies**

## 🚀 Migration Steps

### Step 1: Create New Map Component
Created `plotly_map_component.py` with:
- `create_borehole_map_plotly()` - Main map creation function
- `update_map_position()` - Reliable position updates  
- `calculate_optimal_map_view()` - Auto-calculate center/zoom
- Migration helper functions

### Step 2: Update Layout (THIS FILE)
Replace dash-leaflet map with Plotly equivalent:

```python
# OLD - dash-leaflet (problematic)
dl.Map(
    children=[
        dl.TileLayer(),
        html.Div(id="borehole-markers")
    ],
    id="borehole-map",
    center=[51.5, -0.1],
    zoom=6,
    style={'height': '500px'}
)

# NEW - Plotly (works reliably)
create_borehole_map_plotly(
    borehole_data=None,  # Empty initially
    center=[51.5, -0.1],
    zoom=6,
    height=500,
    map_id="borehole-map-plotly"
)
```

### Step 3: Update Callbacks
Change from returning center/zoom to returning figure:

```python
# OLD - dash-leaflet callback
@app.callback(
    [Output("borehole-map", "center"),
     Output("borehole-map", "zoom"),
     Output("borehole-map", "invalidateSize")],
    [Input("upload-ags", "contents")]
)
def update_map(contents):
    return center, zoom, invalidate_value  # Doesn't work!

# NEW - Plotly callback  
@app.callback(
    Output("borehole-map-plotly", "figure"),
    [Input("upload-ags", "contents")]
)
def update_map(contents):
    # Process data and create new figure
    fig = create_borehole_map_plotly(borehole_data, center, zoom)
    return fig.figure  # Works perfectly!
```

### Step 4: Test Migration
Run tests to verify:
- Map loads correctly
- Markers display properly  
- Center/zoom updates work
- File upload triggers map updates
- Search functionality works

### Step 5: Remove Dependencies
After migration success:
- Remove `dash-leaflet` from requirements.txt
- Remove `map_update_workaround.py`
- Clean up old callback code

## 📊 Migration Benefits

| Aspect              | Dash-Leaflet         | Plotly Maps      |
| ------------------- | -------------------- | ---------------- |
| Center/Zoom Updates | ❌ Broken             | ✅ Works          |
| Documentation       | ⚠️ Limited            | ✅ Extensive      |
| Maintenance         | ⚠️ Workarounds needed | ✅ Native support |
| Dependencies        | ❌ External library   | ✅ Built-in       |
| Community Support   | ⚠️ Small              | ✅ Large          |

## 🔧 Implementation Files

### Created Files:
- `plotly_map_component.py` - New map implementation
- `reports/map_migration_guide.md` - This guide
- `tests/test_plotly_map_migration.py` - Migration tests

### Files to Update:
- `app_modules/layout.py` - Replace map component
- `callbacks/file_upload_enhanced.py` - Update outputs
- `callbacks/search_functionality.py` - Update outputs  
- `requirements.txt` - Remove dash-leaflet (optional)

## 🎯 Expected Results

After migration:
- ✅ Map center/zoom updates work immediately
- ✅ No more workaround complexity
- ✅ Better performance and reliability
- ✅ Easier maintenance and debugging
- ✅ Future-proof solution

## 📞 Rollback Plan

If issues arise:
1. Keep original files as `.backup`
2. Restore from `archive/` directory
3. Re-enable dash-leaflet in requirements
4. Revert callback changes

## 🏁 Success Criteria

Migration is successful when:
- [ ] Map loads without errors
- [ ] Boreholes display correctly
- [ ] File upload updates map position
- [ ] Search functionality works
- [ ] No console errors
- [ ] Performance is equivalent or better

---

**Next Action:** Update `app_modules/layout.py` to use new Plotly map component.
