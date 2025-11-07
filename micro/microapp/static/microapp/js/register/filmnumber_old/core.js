/**
 * Film Number Allocation Core Module
 * 
 * This module handles the core functionality and state management
 * for the film number allocation step.
 */

// Import dependencies 
import { FilmNumberUI } from './ui.js';
import { FilmNumberAPI } from './api.js';
import { FilmNumberEvents } from './events.js';

// Export constants
export const CAPACITY_16MM = 2940;  // Pages per 16mm film roll
export const CAPACITY_35MM = 690;   // Pages per 35mm film roll

// Module state
const state = {
    projectId: null,
    taskId: null,
    analysisResults: null,
    allocationResults: null,
    filmNumberResults: null,
    isAllocating: false,
    intervalId: null,
    workflowType: 'standard', // 'standard' or 'hybrid'
    projectData: null,
    indexData: null
};

/**
 * Initialize the film number allocation module
 */
export function init() {
    try {
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        state.projectId = urlParams.get('id');
        state.workflowType = urlParams.get('flow') || 'standard';
        
        // Load data from the dedicated localStorage keys you're using
        // Project data
        const projectData = getLocalStorageData('microfilmProjectState');
        if (projectData && projectData.projectId == state.projectId) {
            console.log('Loaded project data from localStorage:', projectData);
            state.projectData = projectData;
        }
        
        // Analysis data
        const analysisData = getLocalStorageData('microfilmAnalysisData');
        if (analysisData) {
            console.log('Loaded analysis data from localStorage:', analysisData);
            state.analysisResults = analysisData;
        }
        
        // Allocation data - this is the key one for this step
        const allocationData = getLocalStorageData('microfilmAllocationData');
        if (allocationData) {
            console.log('Loaded allocation data from localStorage:', allocationData);
            state.allocationResults = allocationData;
        } else {
            console.warn('No allocation data found in localStorage');
        }
        
        // Index data
        const indexData = getLocalStorageData('microfilmIndexData');
        if (indexData) {
            console.log('Loaded index data from localStorage:', indexData);
            state.indexData = indexData;
        }
        
        // Check for task ID in session storage to resume any in-progress allocation
        const storedTaskId = sessionStorage.getItem('filmNumberTaskId');
        if (storedTaskId) {
            state.taskId = storedTaskId;
            state.isAllocating = true;
        }
        
        // Make sure DOM elements are loaded before using them
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                initAfterDOM();
            });
        } else {
            initAfterDOM();
        }
    } catch (error) {
        console.error('Error during film number allocation module initialization:', error);
    }
}

/**
 * Get data from localStorage as JSON object.
 * 
 * @param {string} key - The localStorage key to retrieve.
 * @returns {Object|null} The parsed JSON object or null if not found.
 */
export function getLocalStorageData(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error(`Error parsing localStorage data for ${key}:`, error);
        return null;
    }
}

/**
 * Initialize after DOM is fully loaded
 */
function initAfterDOM() {
    try {
        // Update UI based on workflow type
        FilmNumberUI.updateWorkflowTypeUI();
        
        // Always update project info if available
        if (state.analysisResults) {
            FilmNumberUI.updateProjectInfo();
        }
        
        // Initialize index table if available
        FilmNumberUI.initIndexTable();
        
        // If we already have film number results, show them
        if (state.filmNumberResults) {
            FilmNumberUI.updateFilmNumberResults();
            FilmNumberUI.updateStatusBadge('completed', 'Film number allocation complete');
            
            // Update the final index table with film numbers
            FilmNumberUI.updateFinalIndexTable();
            
            // Enable/disable buttons as needed
            const dom = FilmNumberUI.getDomElements();
            if (dom.startFilmNumberBtn) dom.startFilmNumberBtn.disabled = false;
            if (dom.resetFilmNumberBtn) dom.resetFilmNumberBtn.disabled = false;
            if (dom.toNextStepBtn) dom.toNextStepBtn.disabled = false;
        } 
        // If allocation is in progress, continue polling
        else if (state.isAllocating && state.taskId) {
            FilmNumberUI.updateStatusBadge('in-progress', 'Allocating film numbers...');
            FilmNumberUI.showProgressModal();
            
            // Start polling for updates
            FilmNumberAPI.startStatusPolling();
        }
        // Otherwise, initialize with allocation data if available
        else if (state.allocationResults) {
            // Pre-populate the UI with the allocation data even before film numbers are assigned
            FilmNumberUI.prePopulateFromAllocation();
            FilmNumberUI.updateStatusBadge('pending', 'Ready for film number allocation');
            
            // Enable start button
            const dom = FilmNumberUI.getDomElements();
            if (dom.startFilmNumberBtn) dom.startFilmNumberBtn.disabled = false;
        } else {
            // No allocation results, show message
            FilmNumberUI.updateStatusBadge('warning', 'Allocation must be completed first');
        }
        
        // Bind event listeners
        FilmNumberEvents.bindEvents();
    } catch (error) {
        console.error('Error during DOM initialization:', error);
    }
}

/**
 * Reset the film number allocation results
 */
export function resetFilmNumberAllocation() {
    // Clear film number results
    state.filmNumberResults = null;
    FilmNumberUI.clearFilmNumberResults();
    
    // Update status
    FilmNumberUI.updateStatusBadge('pending', 'Ready for film number allocation');
    
    // Enable start button, disable reset button
    const dom = FilmNumberUI.getDomElements();
    dom.startFilmNumberBtn.disabled = false;
    dom.resetFilmNumberBtn.disabled = true;
    dom.toNextStepBtn.disabled = true;
    
    // Clear task ID from session storage
    sessionStorage.removeItem('filmNumberTaskId');
}

/**
 * Start the film number allocation process
 */
export function startFilmNumberAllocation() {
    if (!state.allocationResults) {
        console.error('Cannot start film number allocation without allocation results');
        return;
    }
    
    // Show film number allocation in progress state
    state.isAllocating = true;
    FilmNumberUI.updateStatusBadge('in-progress', 'Allocating film numbers...');
    
    const dom = FilmNumberUI.getDomElements();
    if (dom.startFilmNumberBtn) {
        dom.startFilmNumberBtn.disabled = true;
    }
    
    // Clear any previous film number results
    FilmNumberUI.clearFilmNumberResults();
    
    // Show progress modal
    FilmNumberUI.showProgressModal();
    
    // Call the API to start film number allocation
    FilmNumberAPI.startFilmNumberAllocationProcess();
}

/**
 * Get the current state
 */
export function getState() {
    return state;
} 