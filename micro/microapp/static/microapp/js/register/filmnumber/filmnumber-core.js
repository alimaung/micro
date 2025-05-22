/**
 * Film Number Allocation Core Module
 * 
 * This module handles the core functionality and state management
 * for the film number allocation step.
 */

const FilmNumberCore = (function() {
    // Constants
    const CAPACITY_16MM = 2900;  // Pages per 16mm film roll
    const CAPACITY_35MM = 690;   // Pages per 35mm film roll
    
    // Module state
    const state = {
        projectId: null,
        taskId: null,
        analysisResults: null,
        allocationResults: null,
        filmNumberResults: null,
        filmIndexData: null,  // Add property to store the film number updated index data
        isAllocating: false,
        intervalId: null,
        workflowType: 'standard', // 'standard' or 'hybrid'
        mode: 'auto', // Default mode
        projectData: null,
        indexData: {
            entries: [], // Array of complete entries with all fields
            status: {
                totalEntries: 0,
                updatedEntries: 0,
                pendingEntries: 0
            }
        }
    };
    
    /**
     * Initialize the film number allocation module
     */
    function init() {
        try {
            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            state.projectId = urlParams.get('id');
            state.workflowType = urlParams.get('flow') || 'standard';
            state.mode = urlParams.get('mode') || 'auto';
            
            // Update the progress component's mode indicator if available
            if (window.progressComponent) {
                console.log('Updating progress component mode to:', state.mode);
                window.progressComponent.setWorkflowMode(state.mode);
            } else {
                console.warn('Progress component not available for mode update');
            }
            
            // Load data from localStorage
            loadDataFromStorage();
            
            // Check for task ID in session storage
            const storedTaskId = sessionStorage.getItem('filmNumberTaskId');
            if (storedTaskId) {
                state.taskId = storedTaskId;
                state.isAllocating = true;
            }
        } catch (error) {
            console.error('Error during film number allocation module initialization:', error);
        }
    }
    
    function loadDataFromStorage() {
        console.log('Loading data from storage...');
        
        // Project data
        const projectData = getLocalStorageData('microfilmProjectState');
        console.log('Project data from storage:', projectData);
        if (projectData && projectData.projectId == state.projectId) {
            state.projectData = projectData;
        }
        
        // Analysis data
        const analysisData = getLocalStorageData('microfilmAnalysisData');
        console.log('Analysis data from storage:', analysisData);
        if (analysisData) {
            state.analysisResults = analysisData;
        }
        
        // Allocation data
        const allocationData = getLocalStorageData('microfilmAllocationData');
        console.log('Allocation data from storage:', allocationData);
        if (allocationData) {
            state.allocationResults = allocationData;
        }
        
        // Load and transform index data into unified structure
        const indexData = getLocalStorageData('microfilmIndexData');
        console.log('Index data from storage:', indexData);
        if (indexData) {
            // Transform the data into our new unified structure
            const entries = transformToUnifiedFormat(indexData);
            console.log('Transformed entries:', entries);
            state.indexData = {
                entries: entries,
                status: calculateIndexStatus(entries)
            };
            console.log('Final state.indexData:', state.indexData);
        }
        
        // Load film index data if available (this is the post-allocation version)
        const filmIndexData = getLocalStorageData('microfilmFilmIndexData');
        console.log('Film index data from storage:', filmIndexData);
        if (filmIndexData && filmIndexData.projectId == state.projectId) {
            state.filmIndexData = filmIndexData.indexData;
            console.log('Loaded film index data into state:', state.filmIndexData);
        }
        
        // Load film number results if available (complete server response)
        const storedFilmNumberResults = getLocalStorageData('microfilmFilmNumberResults');
        console.log('Film number results from storage:', storedFilmNumberResults);
        if (storedFilmNumberResults && storedFilmNumberResults.projectId == state.projectId) {
            state.filmNumberResults = storedFilmNumberResults.results;
            console.log('Loaded film number results into state:', state.filmNumberResults);
        }
    }
    
    /**
     * Get data from localStorage as JSON object.
     * 
     * @param {string} key - The localStorage key to retrieve.
     * @returns {Object|null} The parsed JSON object or null if not found.
     */
    function getLocalStorageData(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error(`Error parsing localStorage data for ${key}:`, error);
            return null;
        }
    }
    
    /**
     * Check if we have a saved film data object
     */
    function checkForSavedFilmData() {
        console.log('Checking for saved microfilmFilmData...');
        
        try {
            const savedFilmData = getLocalStorageData('microfilmFilmData');
            
            if (savedFilmData && savedFilmData.projectId === state.projectId) {
                console.log('Found saved microfilmFilmData for current project:', savedFilmData);
                return savedFilmData;
            } else if (savedFilmData) {
                console.log('Found microfilmFilmData but for different project', {
                    saved: savedFilmData.projectId,
                    current: state.projectId
                });
            } else {
                console.log('No saved microfilmFilmData found');
            }
        } catch (error) {
            console.error('Error checking for saved film data:', error);
        }
        
        return null;
    }
    
    /**
     * Initialize after DOM is fully loaded
     */
    function initAfterDOM() {
        try {
            console.log('Initializing after DOM loaded...');
            console.log('Current state:', state);
            
            // Check for saved film data
            const savedFilmData = checkForSavedFilmData();
            if (savedFilmData && savedFilmData.isDone) {
                console.log('Found completed film number data!', savedFilmData);
                // For now, just log it - later we'll implement restoration
            }
            
            // Update UI based on workflow type
            FilmNumberUI.updateWorkflowTypeUI();
            
            // Always update project info if available
            if (state.analysisResults) {
                FilmNumberUI.updateProjectInfo();
            }
            
            // Initialize index table if available
            console.log('About to initialize index table...');
            FilmNumberUI.initIndexTable();
            
            // If we already have film number results, show them
            if (state.filmNumberResults) {
                console.log('Found film number results, updating UI...');
                FilmNumberUI.updateFilmNumberResults();
                FilmNumberUI.updateStatusBadge('completed', 'Film number allocation complete');
                
                // Update the index table
                FilmNumberUI.updateIndexTable();
                
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
            console.error('Error details:', error.stack);
        }
    }
    
    /**
     * Reset the film number allocation results
     */
    function resetFilmNumberAllocation() {
        // Clear film number results
        state.filmNumberResults = null;
        
        // Reset film number related fields in index data
        if (state.indexData && state.indexData.entries) {
            state.indexData.entries = state.indexData.entries.map(entry => ({
                ...entry,
                filmNumber: 'N/A',
                finalIndex: 'Pending',
                status: 'Initial'
            }));
            
            // Update status counts
            state.indexData.status = calculateIndexStatus(state.indexData.entries);
        }
        
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
    function startFilmNumberAllocation() {
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
     * Transform old index data format to new unified format
     */
    function transformToUnifiedFormat(oldData) {
        let entries = [];
        
        // Handle different possible input formats
        const sourceData = oldData.indexData?.index || oldData.index || oldData;
        
        if (Array.isArray(sourceData)) {
            entries = sourceData.map(entry => {
                // Extract roll info from the array format [rollId, startFrame, endFrame]
                const rollInfo = Array.isArray(entry[2]) ? entry[2] : null;
                
                return {
                    docId: entry[0], // document filename
                    comId: entry[1], // COM ID
                    rollId: rollInfo ? String(rollInfo[0]) : null,
                    frameStart: rollInfo ? rollInfo[1] : null,
                    frameEnd: rollInfo ? rollInfo[2] : null,
                    docIndex: entry[4] || null, // Document index in sequence
                    filmNumber: 'N/A',
                    finalIndex: entry[3] || 'Pending',
                    status: 'Initial'
                };
            });
        }
        
        console.log('Transformed entries:', entries);
        return entries;
    }

    /**
     * Calculate index status counts
     */
    function calculateIndexStatus(entries) {
        return {
            totalEntries: entries.length,
            updatedEntries: entries.filter(e => e.status === 'Updated').length,
            pendingEntries: entries.filter(e => e.status === 'Initial' || e.status === 'Pending').length
        };
    }
    
    /**
     * Create a dedicated film number data object to preserve state
     * This is called after successful allocation to capture complete state
     */
    function createFilmDataObject() {
        console.log('Creating dedicated microfilmFilmData object...');
        
        const filmData = {
            version: '1.0',
            timestamp: new Date().toISOString(),
            isDone: true,
            projectId: state.projectId,
            workflowType: state.workflowType,
            projectData: state.projectData,
            analysisResults: state.analysisResults,
            allocationResults: state.allocationResults,
            // Make sure we use the complete film number results
            filmNumberResults: state.filmNumberResults,
            // Use filmIndexData if available, otherwise fall back to indexData
            indexData: state.filmIndexData || state.indexData,
            // Include the original indexData separately for reference
            originalIndexData: state.indexData
        };
        
        // Save to localStorage
        localStorage.setItem('microfilmFilmData', JSON.stringify(filmData));
        
        console.log('Saved complete microfilmFilmData:', filmData);
        
        return filmData;
    }
    
    // Return public API
    return {
        init,
        initAfterDOM,
        getState: () => state,
        resetFilmNumberAllocation,
        startFilmNumberAllocation,
        getLocalStorageData,
        transformToUnifiedFormat,
        calculateIndexStatus,
        createFilmDataObject,
        checkForSavedFilmData,
        CAPACITY_16MM,
        CAPACITY_35MM
    };
})();

// Make FilmNumberCore available globally
window.FilmNumberCore = FilmNumberCore; 