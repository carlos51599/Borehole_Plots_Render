# Section Plot Professional Enhancement Implementation Plan

## Current State Analysis

### Current Section Plot (`section_plot_professional.py`)
- **Return Type**: Returns matplotlib Figure object
- **Figure Size**: Dynamic sizing based on number of boreholes (10" x 18" in test)
- **DPI**: 100 (default matplotlib DPI)
- **Orientation**: Portrait by default
- **Output**: Direct matplotlib figure for display/interaction
- **Multiple Boreholes**: Supported, but layout is not optimized for A4

### Current Borehole Log (`borehole_log_professional.py`)
- **Return Type**: Returns base64-encoded PNG image string(s)
- **Figure Size**: A4 Portrait (8.27" x 11.69")
- **DPI**: 300 (high resolution)
- **Orientation**: Portrait (A4)
- **Output**: Static image ready for display/printing
- **Multiple Boreholes**: Single borehole per log

## Required Changes for Section Plot

### 1. Static Image Output
- Change return type from `matplotlib.figure.Figure` to `str` (base64-encoded PNG)
- Implement image conversion using `io.BytesIO()` and `base64.b64encode()`
- Use `fig.savefig()` with PNG format at 300 DPI
- Close figures properly to prevent memory leaks

### 2. A4 Landscape Format
- **Current**: (8.27, 11.69) - A4 Portrait
- **Target**: (11.69, 8.27) - A4 Landscape
- Rationale: Section plots are typically wider than tall due to multiple boreholes

### 3. Professional Layout Standards
#### Margins and Spacing
- Left margin: 0.5"
- Right margin: 0.5" 
- Top margin: 0.3"
- Bottom margin: 0.3"
- Header height: 1.5" (reduced from borehole log's 2.0" for landscape)

#### Font and Styling Standards
- Font family: Arial
- Font size: 10pt base
- Axis label font size: 11pt, bold
- Title font size: 14pt, bold
- Legend font size: 10pt
- Line weights: 0.8pt for axes, 0.5pt for grid

### 4. Feature Parity with Borehole Log

#### Must Implement
1. **Professional figure management**
   - Context manager for figures (`matplotlib_figure`)
   - Safe figure closing (`safe_close_figure`)
   - Memory leak prevention

2. **High-resolution export capabilities**
   - PDF export at 300 DPI
   - PNG export at 300 DPI
   - Proper bbox handling

3. **Professional color and pattern system**
   - Use existing `get_geology_color()` and `get_geology_pattern()`
   - Implement proper alpha transparency (color_alpha, hatch_alpha)
   - Professional legend with color and hatch patterns

4. **Error handling and logging**
   - Comprehensive error handling
   - Debug logging for troubleshooting
   - Warning messages for data issues

5. **Layout optimization**
   - Center plot on page
   - Use full available width efficiently
   - Professional gridlines and ticks
   - Proper spacing and margins

#### Enhanced Features
1. **Multi-borehole optimization**
   - Automatic layout scaling for 1-10 boreholes
   - Intelligent spacing based on borehole count
   - Optimal use of landscape format

2. **Professional title and headers**
   - Project information header
   - Date/time stamps
   - Page numbering (if multi-page support added later)

3. **Enhanced legend**
   - Color swatches with hatch patterns
   - Professional layout and positioning
   - Consistent with borehole log style

### 5. Implementation Steps

#### Phase 1: Core Infrastructure
1. Add base64 image conversion functions
2. Implement A4 landscape figure sizing
3. Add professional matplotlib configuration
4. Implement figure management context managers

#### Phase 2: Layout Optimization  
1. Implement professional margins and spacing
2. Optimize layout for A4 landscape format
3. Add centering and full-width utilization
4. Professional gridlines and axis formatting

#### Phase 3: Feature Parity
1. Implement alpha transparency for colors and hatches
2. Add comprehensive error handling and logging
3. Implement high-resolution export capabilities
4. Add professional title and header formatting

#### Phase 4: Testing and Validation
1. Test with 1-10 boreholes
2. Validate A4 landscape output
3. Verify image quality and resolution
4. Test error handling with invalid data

### 6. Additional Improvements

#### Future Enhancements
1. **Multi-page support** for very wide sections
2. **Interactive legend** toggle (if returning to interactive mode)
3. **Annotation support** for special markers
4. **Scale bar** display
5. **North arrow** for oriented sections
6. **Professional color schemes** (grayscale, colorblind-friendly)

### 7. Backward Compatibility

#### Function Signature Changes
- Add `return_base64: bool = True` parameter for gradual migration
- If `return_base64=False`, return Figure object (current behavior)
- If `return_base64=True`, return base64 string (new behavior)
- Default to `True` for new standard

#### Migration Path
1. Update all calling code to expect base64 strings
2. Test thoroughly with existing workflows
3. Remove Figure return option after validation

### 8. Testing Strategy

#### Unit Tests
- Test image generation with various borehole counts
- Validate A4 landscape dimensions
- Test base64 encoding/decoding
- Verify color and hatch pattern application

#### Integration Tests  
- Test with real AGS data
- Validate multiple coordinate systems
- Test section line projection
- Verify error handling with malformed data

#### Visual Tests
- Compare output quality with borehole logs
- Verify professional appearance
- Test print quality at 300 DPI
- Validate layout on A4 paper

This implementation plan provides a comprehensive roadmap for enhancing the section plot to match the professional standards of the borehole log while maintaining its unique multi-borehole capabilities.
