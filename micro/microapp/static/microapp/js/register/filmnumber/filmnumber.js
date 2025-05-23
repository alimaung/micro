/**
 * Film Number Allocation Module - Main Entry Point
 * 
 * This is the main entry point for the Film Number Allocation module.
 * It loads the required modules and initializes the application.
 * 
 * Module Dependencies:
 * - filmnumber-core.js - Core functionality and state management
 * - filmnumber-ui.js - UI updates and DOM manipulations
 * - filmnumber-api.js - API calls and data processing
 * - filmnumber-events.js - Event bindings and handlers
 */

/**
 * Film Number Allocation Initialization Module
 */

document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM Content Loaded - Initializing Film Number modules...');
    
    // Wait for all required modules to be available
    if (!window.FilmNumberCore || !window.FilmNumberUI || !window.FilmNumberAPI || !window.FilmNumberEvents) {
        console.error('Required modules not found:', {
            core: !!window.FilmNumberCore,
            ui: !!window.FilmNumberUI,
            api: !!window.FilmNumberAPI,
            events: !!window.FilmNumberEvents
        });
        return;
    }
    
    try {
        // Initialize core module first
        console.log('Initializing FilmNumberCore...');
        window.FilmNumberCore.init();
        
        // Initialize UI module
        console.log('Initializing FilmNumberUI...');
        window.FilmNumberUI.initialize();
        
        // Initialize core after DOM
        console.log('Running FilmNumberCore.initAfterDOM...');
        window.FilmNumberCore.initAfterDOM();
        
        console.log('Film Number module initialization complete');
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});