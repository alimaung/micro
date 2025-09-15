/**
 * References Module - Main Entry Point
 * Initializes and connects all components of the references module
 */

// Main References Manager using IIFE pattern
const ReferencesManager = (function() {
    // Reference to other modules
    let Utils, UI, API, Core, Events;

    /**
     * Main References Manager class
     * Combines all components and manages their lifecycle
     */
    class Manager {
        /**
         * Initialize the References Manager
         * @param {string} projectId - Project ID
         */
        constructor(projectId) {
            // Get project ID if not provided
            if (!projectId) {
                projectId = Utils.getProjectIdFromPage();
                if (!projectId) {
                    console.error('Project ID is required');
                    return;
                }
            }

            // Initialize components
            this.ui = new UI.ReferencesUI();
            this.api = new API.ReferencesAPI(projectId);
            this.core = new Core.ReferencesCore(this.ui, this.api, projectId);
            this.events = new Events.ReferencesEvents(this.ui, this.api, this.core);
            
            // Connect components
            this.core.attachEvents(this.events);
            
            // Initialize
            this.events.init();
            this.core.init();
        }
        
        /**
         * Refresh all data
         */
        refresh() {
            this.core.refreshData();
        }
        
        /**
         * Get the current status
         * @returns {Object} Status information
         */
        getStatus() {
            return {
                status: this.core.getStatus(),
                referenceSheets: this.core.getReferenceSheets()
            };
        }
    }

    // Module initialization function that creates a manager instance
    function init(modules) {
        // Assign modules
        Utils = modules.Utils;
        UI = modules.UI;
        API = modules.API;
        Core = modules.Core;
        Events = modules.Events;
        
        // Get project ID directly (no need to wait for DOMContentLoaded)
        const projectId = Utils.getProjectIdFromPage();
        
        if (projectId) {
            // Create and return manager instance
            const referencesManager = new Manager(projectId);
            
            // Make it globally accessible
            window.referencesManager = referencesManager;
            
            return referencesManager;
        } else {
            console.error('Project ID not found, cannot initialize manager');
            return null;
        }
    }

    // Return public API
    return {
        init: init
    };
})(); 