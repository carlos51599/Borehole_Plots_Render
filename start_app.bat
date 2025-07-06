@echo off
echo Starting ENHANCED Geo Borehole Sections Render App...
echo.
echo FEATURES INCLUDED:
echo - File upload functionality 
echo - Auto-zoom to marker median coordinates
echo - Enhanced debugging output for troubleshooting
echo - Drawing tools (polygon, rectangle, polyline)
echo - Section plot generation from drawn shapes
echo.
echo Checking Python environment...
python -c "import dash; print('Dash version:', dash.__version__)"
python -c "import dash_leaflet; print('Dash-leaflet version:', dash_leaflet.__version__)"
echo.
echo Starting app on http://127.0.0.1:8050
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
