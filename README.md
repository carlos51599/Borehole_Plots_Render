# Geo Borehole Sections Render

A Dash-based web application for visualizing AGS (Association of Geotechnical and Geoenvironmental Specialists) borehole data with interactive mapping and section plotting capabilities.

## Features

- 📁 **AGS File Upload**: Support for multiple AGS file uploads
- 🗺️ **Interactive Map**: View borehole locations on an interactive map
- ✏️ **Drawing Tools**: Select boreholes using rectangles, polygons, and lines
- 📊 **Section Plots**: Generate cross-sectional plots from selected boreholes
- 🎯 **Auto-zoom**: Automatically center and zoom to uploaded borehole locations
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser** to: http://127.0.0.1:8050

## Usage

1. **Upload AGS Files**: Click "Drag and Drop or Select AGS Files" to upload your data
2. **View Map**: Boreholes will appear as markers on the map
3. **Select Boreholes**: Use drawing tools to select boreholes:
   - Rectangle selection
   - Polygon selection  
   - Line selection
4. **Generate Plots**: Section plots will automatically generate for selected boreholes
5. **Download**: Use the download button to save section plots

## File Structure

```
Geo_Borehole_Sections_Render/
├── app.py                   # Main application (recommended)
├── app_fixed.py             # Alternative cleaned version
├── requirements.txt         # Python dependencies
├── config.py               # Configuration settings
├── data_loader.py          # AGS file parsing
├── section_plot.py         # Section plot generation
├── borehole_log.py         # Borehole log plotting
├── map_utils.py            # Map interaction utilities
├── utils.py                # General utilities
├── section_logic.py        # Section plot logic
├── old_streamlit_files/    # Archived Streamlit version
├── archive/                # Archived files and documentation
│   ├── app_variants/       # Alternative app versions
│   ├── test_files/         # Test scripts
│   ├── debug_utilities/    # Debug tools
│   └── documentation/      # Historical documentation
├── Dockerfile              # Container deployment
└── render.yaml             # Render.com deployment config
```

## Core Modules

### data_loader.py
Handles AGS file parsing and data extraction. Converts AGS format to pandas DataFrames.

### section_plot.py  
Generates cross-sectional plots from borehole data using matplotlib.

### map_utils.py
Provides utilities for:
- Coordinate transformation (British National Grid to WGS84)
- Geometric filtering of boreholes
- Shape-based selection logic

### borehole_log.py
Creates individual borehole log visualizations.

## Configuration

Key settings in `config.py`:
- Coordinate system transformations
- Default map settings
- Plot styling options

## Troubleshooting

### Common Issues

**Q: "app.run_server has been replaced by app.run" error**  
A: You're using the correct Dash version. This project uses `app.run()` which is correct for your version.

**Q: No boreholes appear on map**  
A: Check that your AGS file contains valid LOCA data with NATE/NATN coordinates.

**Q: Drawing tools don't work**  
A: Make sure you've uploaded AGS files first, then draw shapes around the borehole markers.

**Q: Section plots don't generate**  
A: Ensure:
- Boreholes are selected within your drawn shape
- AGS files contain required geological data
- At least 2 boreholes are selected for cross-sections

### Debug Information

The application logs detailed information to help diagnose issues:
- Upload progress and file validation
- Coordinate transformation results  
- Drawing tool interactions
- Plot generation status

## Development

### Running in Debug Mode
```bash
python app.py  # Debug mode enabled by default
```

### Testing
Test files and utilities are archived in `archive/test_files/` and `archive/debug_utilities/`.

### Alternative Versions
- `app_fixed.py` - Simplified version with fewer debug features
- `archive/app_variants/` - Contains deployment and network debug versions

## Deployment

### Docker
```bash
docker build -t geo-borehole-app .
docker run -p 8050:8050 geo-borehole-app
```

### Render.com
This project includes `render.yaml` for easy deployment to Render.com cloud platform.

## Dependencies

Core packages (see `requirements.txt`):
- **dash** - Web application framework
- **dash-leaflet** - Interactive mapping
- **pandas** - Data manipulation
- **matplotlib** - Plotting
- **pyproj** - Coordinate transformations
- **plotly** - Interactive plots

## Version Compatibility

This project is compatible with:
- Dash 1.x/2.x (uses `app.run()` method)
- Python 3.8+
- Modern web browsers

See `DASH_VERSION_COMPATIBILITY_NOTES.md` for detailed version information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review archived documentation in `archive/documentation/`
3. Examine log output for detailed error information
4. Create an issue with reproduction steps

---

**Last Updated**: July 7, 2025  
**Version**: 2.0 (Post-cleanup)  
**Status**: Production Ready
