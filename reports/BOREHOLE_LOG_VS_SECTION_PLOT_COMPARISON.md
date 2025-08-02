# Borehole Log vs Section Plot: Architecture Comparison & Fix Strategy

## Executive Summary

After analyzing both systems, the **borehole log works correctly** while the **section plot has systematic aspect ratio issues**. The key difference is in figure handling: borehole log preserves exact dimensions while section plot crops them.

## Critical Differences Identified

### 1. Figure Conversion Strategy

**Borehole Log System (WORKING):**
```python
# archive/borehole_log_professional.py:382 & 1653
# borehole_log/overflow.py:298
fig.savefig(buf, format="png", dpi=dpi, bbox_inches=None)
```

**Section Plot System (BROKEN):**
```python
# callbacks/plot_generation.py:165
figure.savefig(buf, format='png', dpi=300, bbox_inches='tight')
```

**Result**: `bbox_inches=None` preserves exact A4 dimensions, `bbox_inches='tight'` crops and distorts proportions.

### 2. CSS Styling Approach

**Borehole Log System:**
- Uses natural image dimensions
- No forced aspect ratio constraints
- Responsive scaling without distortion

**Section Plot System:**
- Forces width: 100%, height: 500px in MAP_CENTER_STYLE
- Ignores native image proportions
- Creates systematic stretching

### 3. Callback Architecture

**Borehole Log:**
- Single conversion path through archive implementation
- Consistent bbox_inches=None usage
- No competing conversion systems

**Section Plot:**
- Dual conversion paths (callbacks vs utils)
- Conflicting bbox_inches settings
- Competing aspect ratio control

## Root Cause Analysis

The section plot has **multiple competing systems** trying to control aspect ratio:

1. **Figure Creation**: Creates correct A4 landscape (11.69" x 8.27")
2. **Utils Conversion**: Preserves proportions with bbox_inches=None 
3. **Callback Override**: Destroys proportions with bbox_inches='tight'
4. **CSS Styling**: Forces incompatible dimensions regardless of image aspect ratio

## Implementation Strategy

### Phase 1: Fix Callback Processing (CRITICAL)

**File**: `callbacks/plot_generation.py`
**Issue**: Line 165 uses `bbox_inches='tight'` instead of `bbox_inches=None`
**Solution**: Change to match working borehole log implementation

### Phase 2: Fix CSS Styling 

**File**: `config_modules/styles.py`
**Issue**: MAP_CENTER_STYLE forces width: 100%, height: 500px
**Solution**: Use responsive styling that preserves aspect ratio

### Phase 3: Eliminate Dual Conversion Paths

**Current**: Both `_process_plot_figure()` and `section.utils.convert_figure_to_base64()` exist
**Solution**: Use single conversion path following borehole log pattern

## Technical Specifications

### A4 Landscape Target
- **Dimensions**: 11.69" x 8.27" (297mm x 210mm)
- **Aspect Ratio**: 1.414:1
- **DPI**: 300 for professional quality

### Working Borehole Log Pattern
```python
def convert_to_base64(fig, dpi=300):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches=None)  # KEY: bbox_inches=None
    buf.seek(0)
    img_bytes = buf.read()
    buf.close()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{img_b64}"
```

## Quality Assurance

### Success Criteria
1. Section plot displays as true A4 landscape proportions
2. No stretching or distortion in browser
3. Consistent behavior across different screen sizes
4. Single conversion path like borehole log system

### Validation Steps
1. Generate section plot with test data
2. Measure aspect ratio in browser
3. Compare to borehole log output quality
4. Test responsive behavior

## Action Items

- [ ] Fix `bbox_inches='tight'` → `bbox_inches=None` in callbacks/plot_generation.py
- [ ] Update MAP_CENTER_STYLE to preserve aspect ratio
- [ ] Remove duplicate conversion logic
- [ ] Test with real AGS data
- [ ] Validate across different browsers

**Priority**: CRITICAL - This is the core architectural issue causing all stretching problems.
