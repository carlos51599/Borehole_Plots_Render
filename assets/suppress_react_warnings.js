
// React Lifecycle Warnings Suppressor
// Suppresses deprecated lifecycle method warnings from third-party libraries

(function() {
    'use strict';
    
    // Store original console.warn function
    const originalConsoleWarn = console.warn;
    
    // Override console.warn to filter React lifecycle warnings
    console.warn = function(...args) {
        const message = args.join(' ');
        
        // Check if this is a React lifecycle warning we want to suppress
        const reactWarnings = [
            'componentWillMount has been renamed',
            'componentWillReceiveProps has been renamed',
            'componentWillUpdate has been renamed'
        ];
        
        // If it's a React lifecycle warning, suppress it
        for (const warning of reactWarnings) {
            if (message.includes(warning)) {
                // Optionally log to a different level for debugging
                // console.info('Suppressed React warning:', message);
                return;
            }
        }
        
        // For all other warnings, use the original console.warn
        originalConsoleWarn.apply(console, args);
    };
    
    console.info('React lifecycle warnings suppressor loaded');
})();
