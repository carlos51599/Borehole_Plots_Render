# Professional Borehole Section Plotting - Implementation Guide

## Overview

The new `section_plot_professional.py` module implements a professional-style geological section plotting system that matches the Openground standard. This implementation includes all the recommendations from the `matplotlib_openground_style.md` guide.

## Key Features

### 1. Professional Geological Styling
- **Hatch Patterns**: Comprehensive geological hatch pattern mapping for different soil and rock types
- **Earth Tone Colors**: Professional color scheme using geological earth tones
- **Consistent Fonts**: Arial/sans-serif fonts throughout with proper sizing hierarchy
- **Professional Gridlines**: Major and minor gridlines with appropriate styling

### 2. Enhanced Visual Elements
- **Vertical Exaggeration**: Configurable vertical exaggeration (default 3.0x)
- **Ground Surface Line**: Professional ground level line with markers
- **Borehole Labels**: Clear borehole identification with "BH-" prefix
- **Geological Labels**: Smart geological legend codes with background boxes

### 3. High-Quality Output
- **Vector Output**: PDF export capability for professional publications
- **High-DPI Raster**: 300 DPI PNG export for presentations
- **Professional Layout**: Proper spacing, margins, and legend placement

## Integration with Existing Dash App

### Method 1: Direct Replacement

Replace calls to the original plotting function in your Dash app:

```python
# OLD: Original function
from section_plot import plot_section_from_ags_content

# NEW: Professional function
from section_plot_professional import plot_section_from_ags_content_professional

# In your callback:
fig = plot_section_from_ags_content_professional(
    ags_content=content,
    filter_loca_ids=selected_boreholes,
    section_line=section_line_coords,
    show_labels=True,
    vertical_exaggeration=3.0,
    save_high_res=False,  # Set to True if you want automatic file saving
    output_filename=None   # Specify filename for saving
)
```

### Method 2: Optional Professional Mode

Add a toggle in your Dash app to switch between standard and professional modes:

```python
# In your app layout, add a toggle switch:
dcc.Checklist(
    id='professional-mode-toggle',
    options=[{'label': 'Professional Style', 'value': 'professional'}],
    value=[],
    style={'margin': '10px'}
)

# In your callback:
@app.callback(
    Output('section-plot-graph', 'figure'),
    [Input('professional-mode-toggle', 'value'),
     Input('other-inputs...', 'value')]
)
def update_section_plot(professional_mode, ...):
    if 'professional' in professional_mode:
        from section_plot_professional import plot_section_from_ags_content_professional
        fig = plot_section_from_ags_content_professional(
            ags_content=content,
            filter_loca_ids=selected_boreholes,
            section_line=section_line_coords,
            show_labels=True,
            vertical_exaggeration=3.0
        )
    else:
        from section_plot import plot_section_from_ags_content
        fig = plot_section_from_ags_content(
            ags_content=content,
            filter_loca_ids=selected_boreholes,
            section_line=section_line_coords,
            show_labels=True
        )
    return fig
```

## Function Parameters

### `plot_section_from_ags_content_professional()`

```python
def plot_section_from_ags_content_professional(
    ags_content,                    # AGS file content as string
    filter_loca_ids=None,          # List of borehole IDs to include
    section_line=None,             # Section line coordinates for projection
    show_labels=True,              # Show geological legend codes
    vertical_exaggeration=3.0,     # Vertical exaggeration factor
    save_high_res=False,           # Auto-save high-resolution files
    output_filename=None           # Base filename for saving (no extension)
):
```

### `plot_professional_borehole_sections()`

```python
def plot_professional_borehole_sections(
    geol_df,                       # Geological DataFrame
    loca_df,                       # Location DataFrame  
    abbr_df=None,                  # Abbreviations DataFrame
    ags_title=None,                # Plot title
    section_line=None,             # Section line coordinates
    show_labels=True,              # Show geological labels
    vertical_exaggeration=3.0,     # Vertical exaggeration factor
    save_high_res=False,           # Auto-save high-resolution output
    output_filename=None           # Base filename for saving
):
```

## Geological Pattern Mapping

The system automatically maps geological units to appropriate patterns and colors:

### Hatch Patterns
- **Clay**: `'...'` (dots)
- **Sand**: `'///'` (diagonal lines)
- **Gravel**: `'\\\\\\'` (backslash lines)
- **Limestone**: `'xxx'` (crosses)
- **Topsoil**: `'ooo'` (circles)
- **Made Ground**: `'***'` (stars)
- **Concrete**: `'####'` (hash marks)

### Color Scheme
- **Clay**: Saddle brown (`#8B4513`)
- **Sand**: Sandy brown (`#F4A460`)
- **Gravel**: Dim gray (`#696969`)
- **Limestone**: Beige (`#F5F5DC`)
- **Topsoil**: Dark brown (`#654321`)
- **Made Ground**: Dark red (`#8B0000`)

## Customization Options

### Vertical Exaggeration
```python
# Standard view (1:1 aspect ratio)
fig = plot_section_from_ags_content_professional(
    ags_content, vertical_exaggeration=1.0
)

# Professional geological view (3:1 exaggeration - default)
fig = plot_section_from_ags_content_professional(
    ags_content, vertical_exaggeration=3.0
)

# High exaggeration for detailed stratigraphy (5:1)
fig = plot_section_from_ags_content_professional(
    ags_content, vertical_exaggeration=5.0
)
```

### High-Resolution Export
```python
# Export to both PDF and PNG automatically
fig = plot_section_from_ags_content_professional(
    ags_content,
    save_high_res=True,
    output_filename="geological_section_2024"
)
# Creates: geological_section_2024.pdf and geological_section_2024.png
```

### Custom Pattern/Color Mapping

To add new geological patterns or colors, modify the dictionaries in `section_plot_professional.py`:

```python
# Add new patterns to GEOLOGICAL_HATCH_PATTERNS
GEOLOGICAL_HATCH_PATTERNS.update({
    'YOUR_GEOLOGY': 'your_pattern',
})

# Add new colors to GEOLOGICAL_COLOR_MAP
GEOLOGICAL_COLOR_MAP.update({
    'YOUR_GEOLOGY': '#your_hex_color',
})
```

## Dependencies

The professional plotting module requires:

```bash
pip install matplotlib pandas numpy pyproj shapely
```

## Performance Considerations

- The professional rendering is slightly slower due to hatch patterns and enhanced styling
- For large datasets (>50 boreholes), consider using `show_labels=False` to improve performance
- High-resolution export can take several seconds for complex plots

## Troubleshooting

### Common Issues

1. **Shapely Import Error**: Install shapely with `pip install shapely`
2. **Font Warnings**: Install Arial fonts or modify font preferences in `setup_professional_style()`
3. **Memory Issues**: For very large datasets, consider filtering boreholes or reducing vertical exaggeration

### Debug Mode

Enable debug output by monitoring console prints:
```python
# Debug information is automatically printed for coordinate transformations
# and projection calculations
```

## Migration Checklist

- [ ] Install required dependencies (`shapely`, `pyproj`)
- [ ] Import the new professional plotting module
- [ ] Update callback functions to use new function signatures
- [ ] Test with existing AGS data
- [ ] Configure vertical exaggeration preferences
- [ ] Set up high-resolution export if needed
- [ ] Update UI to include professional mode toggle (optional)

## Output Examples

The professional plotting system produces:

1. **Standard Dash Display**: Interactive plot for web browser display
2. **PDF Export**: Vector graphics suitable for professional reports and publications
3. **High-DPI PNG**: Raster graphics for presentations and documentation

The output maintains consistent professional styling with:
- Clean, readable fonts (Arial/sans-serif)
- Appropriate geological color schemes
- Professional hatch patterns for different lithologies
- Clear gridlines and axis labels
- Proper spacing and margins
- Comprehensive legend with both color and pattern information
