/**
 * Document Analysis Module Loader
 * 
 * This file serves as the entry point for the document analysis functionality
 * by loading all required modules in the correct order. It handles:
 * - Dynamic loading of required modules
 * - API configuration
 * - Initialization sequence management
 * 
 * Note: The data output panel has been removed from the UI as it is no longer needed.
 * Any code referencing dataOutput or updateDataPanel has been updated accordingly.
 */

// Set up module loading
(function() {
    'use strict';
    
    // Configure API mode - always use real API
    window.useRealAPI = true;
    
    // Define all required modules
    const modulePaths = [
        '/static/microapp/js/register/document/analysis-core.js',
        '/static/microapp/js/register/document/analysis-ui.js',
        '/static/microapp/js/register/document/analysis-data.js',
        '/static/microapp/js/register/document/analysis-document-list.js',
        '/static/microapp/js/register/document/analysis-workflow.js'
    ];
    
    // Counter to track loaded modules
    let loadedModules = 0;
    
    /**
     * Load a JavaScript module dynamically
     * @param {string} src - Path to the JavaScript file
     * @param {Function} callback - Function to call when all modules are loaded
     */
    function loadModule(src, callback) {
        const script = document.createElement('script');
        script.src = src;
        script.async = false; // Maintain loading order
        
        script.onload = function() {
            loadedModules++;
            console.log(`[Analysis Loader] Loaded module (${loadedModules}/${modulePaths.length}): ${src}`);
            
            // If all modules are loaded, call the callback
            if (loadedModules === modulePaths.length && callback) {
                callback();
            }
        };
        
        script.onerror = function() {
            console.error(`[Analysis Loader] Failed to load module: ${src}`);
        };
        
        document.head.appendChild(script);
    }
    
    /**
     * Initialize the document analysis functionality when all modules are loaded
     */
    function initAnalysis() {
        console.log('[Analysis Loader] All modules loaded, initializing...');
        console.log('[Analysis Loader] Using real API mode');
        
        // The initialization will be handled by the core module's DOMContentLoaded event
        // But we can add any additional initialization here if needed
    }
    
    // Load all modules in sequence
    modulePaths.forEach(path => loadModule(path, initAnalysis));
    
    // Export the loader for debugging purposes
    window.analysisLoader = {
        paths: modulePaths,
        loadedModules: loadedModules,
        apiMode: 'real',
        version: '2.0.0'
    };
})();
