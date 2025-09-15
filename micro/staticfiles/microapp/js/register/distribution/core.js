/**
 * Core Module - Handles data management and state for distribution functionality
 * Manages project data, roll data, distribution state, and local storage
 */

const MicroDistributionCore = (function() {
    'use strict';

    // Private properties
    let config = {
        projectId: null,
        storagePrefix: 'micro_distribution_'
    };

    // Data storage
    let projectData = null;
    let allocationData = null;
    let referenceData = null;
    let distributionState = {
        status: 'not_started', // not_started, in_progress, completed, error
        progress: 0,
        startTime: null,
        endTime: null,
        processed: 0,
        total: 0,
        errors: []
    };

    // Roll data storage
    let rolls = {
        '16mm': [],
        '35mm': []
    };

    // Processed documents
    let processedDocuments = [];

    /**
     * Initialize the core module
     * @param {Object} options - Configuration options
     */
    function init(options = {}) {
        // Merge options with defaults
        config = Object.assign(config, options);

        // Return public interface
        return publicInterface();
    }

    /**
     * Set the project data
     * @param {Object} data - Project data from API
     */
    function setProjectData(data) {
        projectData = data;
        saveState();
    }

    /**
     * Get the project data
     * @returns {Object} The current project data
     */
    function getProjectData() {
        return projectData;
    }

    /**
     * Set the allocation data
     * @param {Object} data - Allocation data from API
     */
    function setAllocationData(data) {
        allocationData = data;
        
        // Process roll data
        if (data && data.rolls) {
            rolls['16mm'] = data.rolls.filter(roll => roll.film_type === '16mm');
            rolls['35mm'] = data.rolls.filter(roll => roll.film_type === '35mm');
        }
        
        saveState();
    }

    /**
     * Get the allocation data
     * @returns {Object} The current allocation data
     */
    function getAllocationData() {
        return allocationData;
    }

    /**
     * Get rolls of a specific type
     * @param {String} type - Film type ('16mm' or '35mm')
     * @returns {Array} Array of roll objects
     */
    function getRolls(type) {
        return rolls[type] || [];
    }

    /**
     * Set the reference data
     * @param {Object} data - Reference data from API
     */
    function setReferenceData(data) {
        referenceData = data;
        saveState();
    }

    /**
     * Get the reference data
     * @returns {Object} The current reference data
     */
    function getReferenceData() {
        return referenceData;
    }

    /**
     * Update the distribution state
     * @param {Object} state - New state data
     */
    function updateDistributionState(state) {
        distributionState = Object.assign({}, distributionState, state);
        saveState();
    }

    /**
     * Get the current distribution state
     * @returns {Object} Current distribution state
     */
    function getDistributionState() {
        return distributionState;
    }

    /**
     * Reset the distribution state
     */
    function resetDistributionState() {
        distributionState = {
            status: 'not_started',
            progress: 0,
            startTime: null,
            endTime: null,
            processed: 0,
            total: 0,
            errors: []
        };
        processedDocuments = [];
        saveState();
    }

    /**
     * Add a processed document to the tracking list
     * @param {Object} document - Document data
     */
    function addProcessedDocument(document) {
        processedDocuments.push(document);
        distributionState.processed = processedDocuments.length;
        saveState();
    }

    /**
     * Add an error to the distribution state
     * @param {Object} error - Error data
     */
    function addError(error) {
        distributionState.errors.push(error);
        saveState();
    }

    /**
     * Get all errors from the distribution state
     * @returns {Array} Array of error objects
     */
    function getErrors() {
        return distributionState.errors;
    }

    /**
     * Get all processed documents
     * @returns {Array} Array of processed document objects
     */
    function getProcessedDocuments() {
        return processedDocuments;
    }

    /**
     * Get the project ID
     * @returns {Number} Project ID
     */
    function getProjectId() {
        return config.projectId;
    }

    /**
     * Save the current state to local storage
     */
    function saveState() {
        const state = {
            projectData,
            allocationData,
            referenceData,
            distributionState,
            rolls,
            processedDocuments,
            timestamp: new Date().getTime()
        };
        
        try {
            localStorage.setItem(getStorageKey(), JSON.stringify(state));
        } catch (error) {
            console.error('Error saving state to local storage:', error);
        }
    }

    /**
     * Load state from local storage
     * @returns {Boolean} Whether state was successfully loaded
     */
    function loadSavedState() {
        try {
            const savedState = localStorage.getItem(getStorageKey());
            if (!savedState) return false;
            
            const state = JSON.parse(savedState);
            
            // Validate the state has required properties
            if (!state.projectData || !state.distributionState) {
                return false;
            }
            
            // Update all properties from saved state
            projectData = state.projectData;
            allocationData = state.allocationData;
            referenceData = state.referenceData;
            distributionState = state.distributionState;
            rolls = state.rolls || { '16mm': [], '35mm': [] };
            processedDocuments = state.processedDocuments || [];
            
            return true;
        } catch (error) {
            console.error('Error loading state from local storage:', error);
            return false;
        }
    }

    /**
     * Check if there is saved state in local storage
     * @returns {Boolean} Whether there is saved state
     */
    function hasSavedState() {
        return localStorage.getItem(getStorageKey()) !== null;
    }

    /**
     * Clear the saved state from local storage
     */
    function clearSavedState() {
        localStorage.removeItem(getStorageKey());
    }

    /**
     * Get the storage key for local storage
     * @returns {String} Storage key
     */
    function getStorageKey() {
        return `${config.storagePrefix}${config.projectId}`;
    }

    /**
     * Get documents for a specific roll
     * @param {String} rollId - The roll ID
     * @returns {Array} Array of document objects for the roll
     */
    function getDocumentsForRoll(rollId) {
        if (!allocationData || !allocationData.documents) {
            return [];
        }
        
        return allocationData.documents.filter(doc => doc.roll_id === rollId);
    }

    /**
     * Public interface exposed by this module
     */
    function publicInterface() {
        return {
            init,
            setProjectData,
            getProjectData,
            setAllocationData,
            getAllocationData,
            getRolls,
            setReferenceData,
            getReferenceData,
            updateDistributionState,
            getDistributionState,
            resetDistributionState,
            addProcessedDocument,
            getProcessedDocuments,
            addError,
            getErrors,
            getProjectId,
            saveState,
            loadSavedState,
            hasSavedState,
            clearSavedState,
            getDocumentsForRoll
        };
    }

    // Return public interface
    return {
        init: init
    };
})();