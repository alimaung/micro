/**
 * References Module - Utilities
 * Contains utility functions used throughout the references module
 */

// Utilities module using IIFE pattern
const ReferencesUtils = (function() {
    /**
     * Gets the CSRF token from cookies
     * @returns {string} CSRF token or empty string if not found
     */
    function getCsrfToken() {
        // Get CSRF token from cookie
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        return cookieValue || '';
    }

    /**
     * Gets a descriptive message based on the progress percentage
     * @param {number} progress - Progress percentage (0-100)
     * @returns {string} Descriptive message
     */
    function getProgressMessage(progress) {
        if (progress < 30) {
            return 'Creating reference templates...';
        } else if (progress < 60) {
            return 'Generating document reference sheets...';
        } else if (progress < 90) {
            return 'Inserting blip data and formatting...';
        } else {
            return 'Finalizing reference sheets...';
        }
    }

    /**
     * Saves data to the workflow state in localStorage
     * @param {Object} data - Data to save
     */
    function saveToWorkflowState(data) {
        try {
            const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            const newState = { ...state, ...data };
            localStorage.setItem('microfilmWorkflowState', JSON.stringify(newState));
        } catch (error) {
            console.error('Error saving to workflow state:', error);
        }
    }

    /**
     * Loads data from the workflow state in localStorage
     * @returns {Object} Workflow state data
     */
    function loadFromWorkflowState() {
        try {
            return JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        } catch (error) {
            console.error('Error loading from workflow state:', error);
            return {};
        }
    }

    /**
     * Gets the project ID from the page
     * @returns {string|null} Project ID or null if not found
     */
    function getProjectIdFromPage() {
        // Try to get from URL
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('project_id')) {
            return urlParams.get('project_id');
        }
        
        // Also check for 'id' parameter for backward compatibility
        if (urlParams.has('id')) {
            return urlParams.get('id');
        }
        
        // Try to get from data attribute
        const projectIdEl = document.querySelector('[data-project-id]');
        if (projectIdEl && projectIdEl.dataset.projectId) {
            return projectIdEl.dataset.projectId;
        }
        
        // Try to get from workflow state
        try {
            const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            if (state.project && state.project.id) {
                return state.project.id;
            }
        } catch (e) {
            console.error('Error parsing workflow state:', e);
        }
        
        return null;
    }

    /**
     * Determines if the workflow is hybrid based on URL parameters or stored state
     * @returns {boolean} True if workflow is hybrid, false if standard
     */
    function isHybridWorkflow() {
        // First check URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('flow')) {
            const flowType = urlParams.get('flow').toLowerCase();
            return flowType === 'hybrid';
        }
        
        // If not specified in URL, check workflow state
        try {
            const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            if (state.workflow && state.workflow.type) {
                return state.workflow.type.toLowerCase() === 'hybrid';
            }
        } catch (e) {
            console.error('Error checking workflow type:', e);
        }
        
        // Default to standard workflow if not specified
        return false;
    }

    // Public API
    return {
        getCsrfToken: getCsrfToken,
        getProgressMessage: getProgressMessage,
        saveToWorkflowState: saveToWorkflowState,
        loadFromWorkflowState: loadFromWorkflowState,
        getProjectIdFromPage: getProjectIdFromPage,
        isHybridWorkflow: isHybridWorkflow
    };
})(); 