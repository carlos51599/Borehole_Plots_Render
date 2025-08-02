# Layout Logic Comparison Report: Borehole Log vs Section Plot

## Executive Summary

This report analyzes the fundamental differences in layout logic between the **borehole log** (perfect implementation) and the **section plot** (problematic implementation). The key issue is that the section plot's footer overlaps the plot area, while the borehole log maintains proper separation through correct boundary box calculations.

## Critical Problem Identified

**Section Plot Issue**: Footer is positioned at `bottom_margin_in / a4_height_in` which places it **inside the plot area** that was calculated **without accounting for footer space**.

**Root Cause**: The section plot calculates plot area space without reserving space for the footer, then places the footer in the same space as the plot area.

---

## 1. Borehole Log Layout (PERFECT Implementation)

### Layout Structure
```
┌─────────────────────────────────────┐
│           TOP MARGIN (0.3")         │
├─────────────────────────────────────┤
│         HEADER AREA (2.0")          │  ← Separate dedicated space
├─────────────────────────────────────┤
│                                     │
│         PLOT AREA                   │  ← Calculated AFTER reserving
│      (log_area_in)                  │    header and footer space
│                                     │
├─────────────────────────────────────┤
│        BOTTOM MARGIN (0.3")         │
└─────────────────────────────────────┘
```

### Key Layout Calculations (A4 Portrait: 8.27" × 11.69")

```python
# CORRECT APPROACH - Reserve space for all components FIRST
a4_height_in = 11.69
top_margin_in = 0.3
header_height_in = 2.0        # ← Dedicated header space
bottom_margin_in = 0.3
# NO FOOTER - or footer would be included in margin calculations

# Calculate remaining space for plot area
log_area_in = a4_height_in - (top_margin_in + header_height_in + bottom_margin_in)
# Result: log_area_in = 11.69 - (0.3 + 2.0 + 0.3) = 8.89 inches

# Position header at top (SEPARATE from plot area)
header_ax = fig.add_axes([
    left_margin_in / a4_width_in,
    (a4_height_in - top_margin_in - header_height_in) / a4_height_in,  # ← Top positioning
    a4_usable_width / a4_width_in,
    header_height_in / a4_height_in,
])

# Position plot area BELOW header (NON-OVERLAPPING)
log_ax = fig.add_axes([
    left_margin_in / a4_width_in,
    bottom_margin_in / a4_height_in,                    # ← Bottom positioning
    a4_usable_width / a4_width_in,
    log_area_in / a4_height_in,                         # ← Uses calculated area
])
```

### Boundary Box Logic
1. **Header**: Positioned at top of page in dedicated space
2. **Plot Area**: Uses remaining space after header reservation
3. **No Footer**: Or footer would be included in margin calculations
4. **Result**: Perfect separation, no overlaps

---

## 2. Section Plot Layout (PROBLEMATIC Implementation)

### Layout Structure (Current)
```
┌─────────────────────────────────────┐
│           TOP MARGIN (0.3")         │
├─────────────────────────────────────┤
│         HEADER AREA (1.5")          │  ← Separate space
├─────────────────────────────────────┤
│                                     │
│         PLOT AREA                   │  ← Calculated WITHOUT considering footer
│                                     │
│    ┌─────────────────────────────┐  │  ← FOOTER OVERLAPS HERE!
│    │       FOOTER (1.5")        │  │     
│    └─────────────────────────────┘  │
├─────────────────────────────────────┤
│        BOTTOM MARGIN (0.3")         │  ← Footer also positioned here
└─────────────────────────────────────┘
```

### Problematic Layout Calculations (A4 Landscape: 11.69" × 8.27")

```python
# INCORRECT APPROACH - Does NOT reserve space for footer
a4_width_in = 11.69
a4_height_in = 8.27
left_margin_in = 0.5
right_margin_in = 0.5
top_margin_in = 0.3
bottom_margin_in = 0.3
header_height_in = 1.5

# Calculate plot area WITHOUT considering footer space
plot_width_in = a4_width_in - left_margin_in - right_margin_in
plot_height_in = a4_height_in - top_margin_in - bottom_margin_in - header_height_in
# Result: plot_height_in = 8.27 - (0.3 + 0.3 + 1.5) = 6.17 inches

# Position plot area (uses full calculated space)
ax.set_position([plot_left, plot_bottom, plot_width_frac, plot_height_frac])

# PROBLEM: Footer positioned at SAME location as plot area bottom!
footer_ax = fig.add_axes([
    left_margin_in / a4_width_in,
    bottom_margin_in / a4_height_in,        # ← SAME as plot area bottom!
    a4_usable_width / a4_width_in,
    footer_height_in / a4_height_in,        # ← 1.5" footer height
])
```

### Problem Analysis
1. **Plot area calculation**: Uses space from `bottom_margin_in` to `top_margin_in + header_height_in`
2. **Footer positioning**: Starts at `bottom_margin_in` - **SAME as plot area bottom**
3. **Result**: Footer overlaps plot area by 1.5 inches

---

## 3. Detailed Coordinate Analysis

### Borehole Log Coordinates (CORRECT)
```python
# A4 Portrait: 8.27" × 11.69"
header_bottom = (11.69 - 0.3 - 2.0) / 11.69 = 0.796  # Header at top
log_bottom = 0.3 / 11.69 = 0.026                      # Plot at bottom
log_top = log_bottom + (8.89 / 11.69) = 0.786         # Plot calculated height

# No overlap: header_bottom (0.796) ≠ log_top (0.786)
# Separation: 0.796 - 0.786 = 0.010 (small gap for clean layout)
```

### Section Plot Coordinates (PROBLEMATIC)
```python
# A4 Landscape: 11.69" × 8.27"
plot_bottom = 0.3 / 8.27 = 0.036                      # Plot area starts here
plot_top = plot_bottom + (6.17 / 8.27) = 0.782        # Plot area ends here

footer_bottom = 0.3 / 8.27 = 0.036                    # Footer starts here - SAME!
footer_top = footer_bottom + (1.5 / 8.27) = 0.218     # Footer extends upward

# OVERLAP: footer extends from 0.036 to 0.218
# Plot area extends from 0.036 to 0.782
# Overlap zone: 0.036 to 0.218 (1.5" of overlap!)
```

---

## 4. Comparison Table

| Aspect | Borehole Log (PERFECT) | Section Plot (BROKEN) |
|--------|------------------------|------------------------|
| **Space Reservation** | ✅ Reserves ALL component space first | ❌ Ignores footer space in calculations |
| **Layout Order** | 1. Reserve margins<br>2. Reserve header<br>3. Calculate remaining plot space | 1. Reserve margins<br>2. Reserve header<br>3. Calculate plot space<br>4. **OVERLAP** footer on plot |
| **Coordinate Logic** | Non-overlapping boundaries | Overlapping boundaries |
| **Footer Position** | N/A (or in margins) | `bottom_margin` - same as plot bottom |
| **Plot Area Calc** | `total - margins - header` | `total - margins - header` (missing footer) |
| **Result** | Perfect separation | Footer overlaps plot by 1.5" |

---

## 5. Root Cause Analysis

### The Fundamental Error
The section plot makes this critical mistake:

```python
# STEP 1: Calculate plot area (WRONG - doesn't include footer)
plot_height_in = a4_height_in - top_margin_in - bottom_margin_in - header_height_in

# STEP 2: Position plot area using calculated height
ax.set_position([plot_left, plot_bottom, plot_width_frac, plot_height_frac])

# STEP 3: Position footer at SAME bottom position (OVERLAP!)
footer_ax = fig.add_axes([
    left_margin_in / a4_width_in,
    bottom_margin_in / a4_height_in,  # ← Same as plot_bottom!
    # ...
])
```

### What Should Happen (Fix)
```python
# STEP 1: Reserve space for ALL components including footer
footer_height_in = 1.5
plot_height_in = (a4_height_in - top_margin_in - bottom_margin_in - 
                  header_height_in - footer_height_in)

# STEP 2: Position plot area ABOVE footer
plot_bottom = (bottom_margin_in + footer_height_in) / a4_height_in
ax.set_position([plot_left, plot_bottom, plot_width_frac, plot_height_frac])

# STEP 3: Position footer at true bottom
footer_ax = fig.add_axes([
    left_margin_in / a4_width_in,
    bottom_margin_in / a4_height_in,  # ← Footer at bottom
    # ...
])
```

---

## 6. Fix Implementation Strategy

### Required Changes to Section Plot

1. **Modify plot area calculation** to reserve footer space:
```python
# BEFORE (broken)
plot_height_in = a4_height_in - top_margin_in - bottom_margin_in - header_height_in

# AFTER (fixed)
footer_height_in = 1.5  # Define footer height
plot_height_in = (a4_height_in - top_margin_in - bottom_margin_in - 
                  header_height_in - footer_height_in)
```

2. **Adjust plot positioning** to sit above footer:
```python
# BEFORE (broken)
plot_bottom = bottom_margin_in / a4_height_in

# AFTER (fixed)
plot_bottom = (bottom_margin_in + footer_height_in) / a4_height_in
```

3. **Keep footer at true bottom** (this part is actually correct):
```python
# This is already correct - footer at bottom margin
footer_bottom = bottom_margin_in / a4_height_in
```

---

## 7. Verification Method

### Test Layout Coordinates
After implementing the fix, verify these coordinates:

```python
# Expected corrected coordinates for A4 landscape (11.69" × 8.27")
margin_bottom = 0.3
margin_top = 0.3
header_height = 1.5
footer_height = 1.5

# Footer: bottom_margin to bottom_margin + footer_height
footer_start = 0.3 / 8.27 = 0.036
footer_end = (0.3 + 1.5) / 8.27 = 0.218

# Plot: footer_end to (total - margin_top - header_height)
plot_start = (0.3 + 1.5) / 8.27 = 0.218
plot_end = (8.27 - 0.3 - 1.5) / 8.27 = 0.782

# Header: plot_end to (total - margin_top)
header_start = (8.27 - 0.3 - 1.5) / 8.27 = 0.782
header_end = (8.27 - 0.3) / 8.27 = 0.964

# Verification: No overlaps
assert footer_end <= plot_start  # Footer below plot
assert plot_end <= header_start  # Plot below header
```

---

## 8. Recommendations

### Immediate Actions
1. **Fix section plot layout calculation** to include footer space reservation
2. **Adjust plot area positioning** to sit above footer instead of overlapping
3. **Test with various figure sizes** to ensure consistent behavior

### Long-term Improvements
1. **Create shared layout utility** that both borehole log and section plot can use
2. **Implement layout validation** to detect overlapping components
3. **Add unit tests** for layout calculations to prevent regression

### Code Pattern to Follow
Use the borehole log's proven approach:
1. Define all component heights first
2. Calculate remaining space for plot area
3. Position components in non-overlapping sequence
4. Verify coordinates don't overlap

---

## Conclusion

The borehole log implementation demonstrates the correct approach to matplotlib figure layout with proper boundary box management. The section plot's footer overlap issue stems from a fundamental error in space reservation logic - it calculates plot area without considering footer space, then positions the footer in the same location as the plot area bottom.

The fix requires modifying the plot area calculation to reserve footer space and adjusting the plot positioning accordingly. This will achieve the same clean separation demonstrated in the borehole log implementation.
