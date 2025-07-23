"""
Graph Styles Module
==================

CSS styling definitions for the enhanced dependency graph visualization.
Contains all visual styling including layout, animations, and theming support.
"""


def get_graph_styles_with_theme_support() -> str:
    """
    Get complete CSS styles with light/dark theme support.

    Returns:
        str: Complete CSS stylesheet with theme variables and toggle support
    """
    return """
        :root {
            /* Light theme variables (default) */
            --bg-primary: #f8f9fa;
            --bg-secondary: #ffffff;
            --bg-container: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --text-primary: #333333;
            --text-secondary: #666666;
            --text-muted: #888888;
            --border-color: #e9ecef;
            --border-color-hover: #dee2e6;
            --shadow-light: rgba(0,0,0,0.1);
            --shadow-medium: rgba(0,0,0,0.2);
            --shadow-heavy: rgba(0,0,0,0.3);
            --accent-color: #ff6600;
            --accent-color-hover: #e55a00;
            --graph-bg: #ffffff;
            --node-stroke: #333333;
            --link-color: #666666;
            --control-bg: #ffffff;
            --control-border: #e9ecef;
            --button-bg: #f8f9fa;
            --button-hover: #e9ecef;
            --input-bg: #ffffff;
            --input-border: #ced4da;
        }

        [data-theme="dark"] {
            /* Dark theme variables */
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-container: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --text-muted: #999999;
            --border-color: #404040;
            --border-color-hover: #555555;
            --shadow-light: rgba(0,0,0,0.3);
            --shadow-medium: rgba(0,0,0,0.5);
            --shadow-heavy: rgba(0,0,0,0.7);
            --accent-color: #ff8533;
            --accent-color-hover: #ff9955;
            --graph-bg: #2d2d2d;
            --node-stroke: #ffffff;
            --link-color: #cccccc;
            --control-bg: #2d2d2d;
            --control-border: #404040;
            --button-bg: #404040;
            --button-hover: #555555;
            --input-bg: #404040;
            --input-border: #555555;
        }

        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        .container {
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        
        .controls {
            width: 400px;  /* Increased width for theme toggle */
            background: var(--control-bg);
            border-right: 2px solid var(--border-color);
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 8px var(--shadow-light);
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--button-bg);
            border: 1px solid var(--border-color);
            border-radius: 25px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            color: var(--text-primary);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
        }
        
        .theme-toggle:hover {
            background: var(--button-hover);
            border-color: var(--border-color-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px var(--shadow-medium);
        }
        
        .theme-icon {
            font-size: 16px;
            transition: transform 0.3s ease;
        }
        
        .theme-toggle:hover .theme-icon {
            transform: rotate(180deg);
        }
        
        .graph-container {
            flex: 1;
            position: relative;
            background: var(--bg-container);
            transition: background 0.3s ease;
        }
        
        #graph {
            width: 100%;
            height: 100%;
            background: var(--graph-bg);
            cursor: grab;
            transition: background-color 0.3s ease;
        }
        
        #graph:active {
            cursor: grabbing;
        }
        
        /* Enhanced node styles with theme support */
        .node-rect {
            stroke: var(--node-stroke);
            stroke-width: 1.5;
            rx: 8;
            ry: 8;
            filter: drop-shadow(2px 2px 4px var(--shadow-medium));
            transition: all 0.2s ease;
        }
        
        .node-rect:hover {
            stroke-width: 2.5;
            filter: drop-shadow(3px 3px 8px var(--shadow-heavy));
        }
        
        .node-rect.highlighted {
            stroke: var(--accent-color);
            stroke-width: 3;
            filter: drop-shadow(0 0 12px var(--accent-color));
        }
        
        .node-rect.dimmed {
            opacity: 0.05;
        }
        
        .node-rect.hotspot {
            stroke: #ff3333;
            stroke-width: 2;
            animation: pulse-hotspot 2s infinite;
        }
        
        @keyframes pulse-hotspot {
            0%, 100% { stroke-opacity: 0.8; }
            50% { stroke-opacity: 1; }
        }
        
        /* Enhanced link styles with theme support */
        .link {
            fill: none;
            stroke: var(--link-color);
            stroke-width: 1.5;
            opacity: 0.8;
            transition: all 0.3s ease;
        }
        
        .link:hover {
            stroke-width: 2.5;
            opacity: 1;
        }
        
        .link.highlighted {
            stroke: var(--accent-color);
            stroke-width: 3;
            opacity: 1;
        }
        
        .link.dimmed {
            opacity: 0.01;
        }
        
        .link.hidden {
            display: none;
        }
        
        .link.test-related {
            stroke-dasharray: 4,4;
        }
        
        /* Enhanced text styles with theme support */
        .node-label {
            font-size: 11px;
            font-weight: 600;
            text-anchor: middle;
            pointer-events: none;
            fill: var(--text-primary);
            transition: fill 0.3s ease;
        }

        .node-label.dimmed {
            opacity: 0.01;
        }
        
        .folder-label-text {
            font-size: 9px;
            text-anchor: middle;
            pointer-events: none;
            fill: var(--text-secondary);
            font-style: italic;
            transition: fill 0.3s ease;
        }
        
        /* Control panel styles with theme support */
        .section {
            margin-bottom: 25px;
            padding: 15px;
            background: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .section h3 {
            margin: 0 0 15px 0;
            color: var(--text-primary);
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: color 0.3s ease;
        }
        
        .folder-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 4px 0;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .folder-item:hover {
            background: #e3f2fd;
            border-color: #90caf9;
        }
        
        .folder-checkbox {
            font-size: 16px;
            margin-right: 10px;
            user-select: none;
        }
        
        .folder-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 10px;
            border: 1px solid #dee2e6;
        }
        
        .folder-label {
            flex: 1;
            font-size: 13px;
            font-weight: 500;
        }
        
        .folder-count {
            font-weight: normal;
            color: #6c757d;
            font-size: 11px;
        }
        
        .test-count {
            font-weight: normal;
            color: #fd7e14;
            font-size: 11px;
        }
        
        .reset-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.2s ease;
            width: 100%;
        }
        
        .reset-button:hover {
            background: #0056b3;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .stat-item {
            background: white;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #007bff;
        }
        
        .stat-label {
            font-size: 11px;
            color: #6c757d;
            text-transform: uppercase;
        }
        
        /* Tooltip styles */
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 6px;
            pointer-events: none;
            font-size: 12px;
            max-width: 300px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        .importance-indicator {
            position: absolute;
            top: -8px;
            right: -8px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #ffc107;
            border: 2px solid white;
            display: none;
        }
        
        .importance-indicator.high {
            display: block;
            background: #dc3545;
        }
        
        .importance-indicator.medium {
            display: block;
            background: #fd7e14;
        }
        
        .importance-indicator.low {
            display: block;
            background: #ffc107;
        }
        
        /* Layout toggle styles */
        .layout-toggle {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin-bottom: 15px;
        }
        
        .layout-toggle-label {
            font-size: 13px;
            font-weight: 500;
            color: #495057;
        }
        
        .toggle-switch {
            position: relative;
            width: 50px;
            height: 24px;
            background-color: #ccc;
            border-radius: 12px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .toggle-switch.active {
            background-color: #007bff;
        }
        
        .toggle-slider {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background-color: white;
            border-radius: 50%;
            transition: transform 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .toggle-switch.active .toggle-slider {
            transform: translateX(26px);
        }
        
        .layout-mode-indicator {
            font-size: 11px;
            color: #6c757d;
            margin-top: 5px;
            text-align: center;
        }
        
        /* Filter range inputs */
        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #dee2e6;
            outline: none;
            -webkit-appearance: none;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #007bff;
            cursor: pointer;
        }
        
        input[type="range"]::-moz-range-thumb {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #007bff;
            cursor: pointer;
            border: none;
        }
        
        /* Filter labels */
        .filter-label {
            display: block;
            font-size: 0.9em;
            margin-bottom: 5px;
            color: #6c757d;
        }
        
        .filter-value {
            font-size: 0.8em;
            color: #6c757d;
            text-align: center;
        }
        
        /* Animation classes */
        .node-transition {
            transition: all 0.5s ease-in-out;
        }
        
        .link-transition {
            transition: all 0.5s ease-in-out;
        }
        
        /* Accessibility improvements */
        .folder-item:focus {
            outline: 2px solid #007bff;
            outline-offset: 2px;
        }
        
        .toggle-switch:focus {
            outline: 2px solid #007bff;
            outline-offset: 2px;
        }
        
        /* Loading states */
        .loading {
            opacity: 0.5;
            pointer-events: none;
        }
        
        .loading::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin: -10px 0 0 -10px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .controls {
                width: 100%;
                height: 300px;
                order: 2;
            }
            
            .graph-container {
                height: calc(100vh - 300px);
                order: 1;
            }
        }
    """


def get_graph_styles() -> str:
    """
    Get complete CSS styles for backward compatibility.
    Uses the enhanced theme-aware styles by default.

    Returns:
        str: Complete CSS stylesheet as string
    """
    return get_graph_styles_with_theme_support()
