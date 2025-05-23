/**
 * Film Allocation Module - Main Entry Point
 * 
 * This is the main entry point for the Film Allocation module.
 * It loads the required modules and initializes the application.
 * 
 * Module Dependencies:
 * - allocation-core.js - Core functionality and state management
 * - allocation-ui.js - UI updates and DOM manipulations
 * - allocation-api.js - API calls and data processing
 * - allocation-events.js - Event bindings and handlers
 */

// Initialize the allocation module when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Make sure all required modules are loaded
    if (
        typeof AllocationCore !== 'undefined' &&
        typeof AllocationUI !== 'undefined' &&
        typeof AllocationAPI !== 'undefined' &&
        typeof AllocationEvents !== 'undefined'
    ) {
        console.log('Initializing Film Allocation module');
        // Initialize the core module
        AllocationCore.init();
    } else {
        console.error('One or more Film Allocation modules are missing!');
    }
});
