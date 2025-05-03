/**
 * Film Index Core Module
 * 
 * This module contains the core functionality for film index generation,
 * managing state and initialization.
 */
const IndexCore = (function() {
    // Module state
    const state = {
        projectId: null,
        workflowType: 'hybrid',
        taskId: null,
        allocationResults: null,
        indexData: null,
        comListPath: null,
        projectInfo: null,
        filmNumbers: {},
        isGenerating: false,
        isUpdating: false,
        intervalId: null
    };
    
    /**
     * Initialize the index module
     */
    function init() {
        try {
            // Get URL parameters - check both project_id and id (for backward compatibility)
            const urlParams = new URLSearchParams(window.location.search);
            state.projectId = urlParams.get('id');
            state.workflowType = urlParams.get('flow');
            
            console.log(`Initializing index module for project ${state.projectId} (${state.workflowType})`);
            
            // Try to restore state from localStorage
            loadFromLocalStorage();
            
            // Make sure DOM elements are loaded before using them
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    initAfterDOM();
                });
            } else {
                initAfterDOM();
            }
            
            console.log('Index module initialized');
        } catch (error) {
            console.error('Error during index module initialization:', error);
        }
    }
    
    /**
     * Load state data from localStorage
     */
    function loadFromLocalStorage() {
        try {
            // Load workflow state (for allocation results and index data)
            const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            console.log('Workflow state from localStorage:', workflowState);
            
            // Load project state (for project info and COM list path)
            const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
            console.log('Project state from localStorage:', projectState);

            // Load allocation state (for allocation results)
            const allocationState = JSON.parse(localStorage.getItem('microfilmAllocationState') || '{}');
            console.log('Allocation state from localStorage:', allocationState);
            
            // Try to get the project ID from project state if not in URL
            if (!state.projectId && projectState.projectId) {
                state.projectId = projectState.projectId;
                console.log('Using project ID from project state:', state.projectId);
            }
            
            // If we have a project state, use it (even if the IDs don't match)
            if (projectState.projectId) {
                console.log('Found project state');
                state.projectInfo = projectState.projectInfo || {};
                
                // Get the COM list path from project info
                if (state.projectInfo && state.projectInfo.comlistPath) {
                    state.comListPath = state.projectInfo.comlistPath;
                    console.log('Found COM list path in project state:', state.comListPath);
                }
            }
            
            // If we have a workflow state for this project, use it
            if (workflowState.projectId === state.projectId) {
                console.log('Found workflow state for this project');
                
                // Restore allocation results if available
                if (workflowState.allocationResults) {
                    state.allocationResults = workflowState.allocationResults;
                    console.log('Restored allocation results from workflow state');
                }
                
                // Restore index data if available
                if (workflowState.indexData) {
                    state.indexData = workflowState.indexData;
                    console.log('Restored index data from workflow state');
                }
                
                // Restore COM list path if available in workflow state and not already set
                if (!state.comListPath && workflowState.comListPath) {
                    state.comListPath = workflowState.comListPath;
                    console.log('Restored COM list path from workflow state:', state.comListPath);
                }
                
                // Restore film numbers if available
                if (workflowState.filmNumbers) {
                    state.filmNumbers = workflowState.filmNumbers;
                    console.log('Restored film numbers from workflow state');
                }
            }
            
            // If we still don't have the project ID, try to get it from the workflowState
            if (!state.projectId && workflowState.projectId) {
                state.projectId = workflowState.projectId;
                console.log('Using project ID from workflow state:', state.projectId);
            }
            
            // Log state after loading
            console.log('State after loading from localStorage:', {
                projectId: state.projectId,
                workflowType: state.workflowType,
                hasAllocationResults: !!state.allocationResults,
                hasIndexData: !!state.indexData,
                comListPath: state.comListPath,
                hasProjectInfo: !!state.projectInfo
            });
        } catch (error) {
            console.error('Error loading state from localStorage:', error);
        }
    }
    
    /**
     * Initialize after DOM is fully loaded
     */
    function initAfterDOM() {
        try {
            // Check if we have project ID
            if (!state.projectId) {
                console.error('No project ID found in URL or localStorage');
                IndexUI.updateStatusBadge('error', 'No project ID provided');
                IndexUI.showToast('No project ID found. Please go back to the project page.', 'error');
                return;
            }
            
            // Update the project info and COM list info in the UI
            IndexUI.updateProjectInfo();
            IndexUI.updateComListInfo();
            
            // If we already have index data, show it
            if (state.indexData) {
                console.log('Found existing index data, displaying...');
                IndexUI.updateIndexDisplay();
                IndexUI.updateStatusBadge('completed', 'Index generated');
                
                // Enable reset button
                const dom = IndexUI.getDomElements();
                if (dom.resetIndexBtn) dom.resetIndexBtn.disabled = false;
                
                // If we have film numbers and the index hasn't been updated with them
                if (Object.keys(state.filmNumbers).length > 0) {
                    IndexUI.showFilmNumberPanel();
                }
            } 
            // Otherwise, get allocation results if not already loaded
            else if (state.projectId) {
                // If we already have allocation results, just update project info
                if (state.allocationResults) {
                    console.log('Using cached allocation results');
                    IndexUI.updateStatusBadge('pending', 'Ready for index generation');
                    
                    // Enable generate button
                    const dom = IndexUI.getDomElements();
                    if (dom.generateIndexBtn) dom.generateIndexBtn.disabled = false;
                } else {
                    // For now, just show a message that we need to get allocation results first
                    console.warn('No allocation results found, user should go back to allocation step first');
                    IndexUI.updateStatusBadge('error', 'Complete allocation first');
                    IndexUI.showToast('Please complete the allocation step before generating the index', 'warning');
                }
            } else {
                // Show message if no project ID
                IndexUI.updateStatusBadge('error', 'No project ID provided');
            }
        } catch (error) {
            console.error('Error during DOM initialization:', error);
        }
    }
    
    /**
     * Save state to localStorage
     */
    function saveState() {
        try {
            const stateToSave = {
                projectId: state.projectId,
                workflowType: state.workflowType,
                allocationResults: state.allocationResults,
                indexData: state.indexData,
                comListPath: state.comListPath,
                filmNumbers: state.filmNumbers
            };
            
            localStorage.setItem('microfilmWorkflowState', JSON.stringify(stateToSave));
            console.log('Workflow state saved to localStorage');
        } catch (error) {
            console.error('Error saving state to localStorage:', error);
        }
    }
    
    /**
     * Reset the index data
     */
    function resetIndex() {
        // Clear index data
        state.indexData = null;
        state.taskId = null;
        
        // Save the updated state
        saveState();
        
        // Update UI
        IndexUI.clearIndexDisplay();
        
        // Update status
        IndexUI.updateStatusBadge('pending', 'Ready for index generation');
        
        // Enable generate button, disable reset button
        const dom = IndexUI.getDomElements();
        if (dom.generateIndexBtn) dom.generateIndexBtn.disabled = false;
        if (dom.resetIndexBtn) dom.resetIndexBtn.disabled = true;
        
        // Hide film number panel
        IndexUI.hideFilmNumberPanel();
        
        // Hide final index panel
        IndexUI.hideFinalIndexPanel();
    }
    
    /**
     * Generate index for the project
     */
    function generateIndex() {
        const state = IndexCore.getState();
        
        if (state.isGenerating) {
            console.log('Index generation already in progress');
            return;
        }
        
        // Set generating flag
        state.isGenerating = true;
        
        // Get allocation results from localStorage
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        const allocationResults = workflowState.allocationResults || {};
        
        console.log('Sending allocation results to backend:', allocationResults);
        
        // Show loading indicator
        IndexUI.showProgressModal('Generating Index', 'Starting index generation...');
        
        // Call backend API to generate index
        IndexAPI.generateIndex(state.projectId, allocationResults)
            .then(response => {
                console.log('Index generation initiated:', response);
                
                if (response && response.taskId) {
                    state.taskId = response.taskId;
                    
                    // Start polling for progress
                    IndexEvents.startProgressPolling(response.taskId);
                } else {
                    // Handle case where no task ID is returned - proceed without polling
                    console.log('No task ID returned, skipping polling');
                    // Update UI to show generation is in progress
                    IndexUI.updateProgress(50, 'Processing index...');
                    // Check for results directly after a delay
                    setTimeout(() => {
                        IndexAPI.getIndexResults(state.projectId)
                            .then(resultsResponse => {
                                if (resultsResponse && resultsResponse.results) {
                                    finishGeneration(resultsResponse.results);
                                } else {
                                    throw new Error('No results returned from server');
                                }
                            })
                            .catch(error => {
                                console.error('Error getting index results:', error);
                                state.isGenerating = false;
                                IndexUI.showToast('Failed to get index results: ' + error.message, 'error');
                                IndexUI.hideProgressModal();
                            });
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error generating index:', error);
                state.isGenerating = false;
                IndexUI.showToast('Failed to generate index: ' + error.message, 'error');
                IndexUI.hideProgressModal();
            });
    }
    
    /**
     * Finish the index generation process with results
     * 
     * @param {Object} results - The index generation results
     */
    function finishGeneration(results) {
        console.log('Index generation completed:', results);
        
        // Store index data
        state.indexData = results;
        state.isGenerating = false;
        
        // Save state
        saveState();
        
        // Update UI
        IndexUI.updateIndexDisplay();
        
        // Update status badge
        IndexUI.updateStatusBadge('completed', 'Index generated');
        
        // Enable reset button
        const dom = IndexUI.getDomElements();
        if (dom.resetIndexBtn) dom.resetIndexBtn.disabled = false;
        
        // Show success message
        IndexUI.showToast('Index generated successfully', 'success');
    }
    
    /**
     * Update the index with film numbers
     */
    function updateIndex() {
        if (!state.projectId) {
            console.error('Cannot update index without project ID');
            IndexUI.showToast('Project ID is required', 'error');
            return;
        }
        
        if (!state.indexData) {
            console.error('Cannot update index without index data');
            IndexUI.showToast('Index data is required', 'error');
            return;
        }
        
        if (!state.filmNumbers || Object.keys(state.filmNumbers).length === 0) {
            console.error('Cannot update index without film numbers');
            IndexUI.showToast('Film numbers are required', 'error');
            return;
        }
        
        // Show update in progress state
        state.isUpdating = true;
        IndexUI.updateStatusBadge('in-progress', 'Updating index...');
        
        // Prepare parameters for API call
        const params = {
            projectId: state.projectId,
            filmNumbers: state.filmNumbers
        };
        
        // Call the API to update the index
        IndexAPI.updateIndex(params)
            .then(data => {
                console.log('Index update started:', data);
                
                // Store task ID for status polling
                state.taskId = data.task_id;
                
                // Update status badge
                IndexUI.updateStatusBadge('in-progress', 'Index update in progress...');
                
                // Save state
                saveState();
            })
            .catch(error => {
                console.error('Error updating index:', error);
                state.isUpdating = false;
                
                // Update status badge
                IndexUI.updateStatusBadge('error', 'Error updating index');
                
                // Show error message
                IndexUI.showToast(`Error: ${error.message}`, 'error');
                
                // Enable update button
                const dom = IndexUI.getDomElements();
                if (dom.updateIndexBtn) dom.updateIndexBtn.disabled = false;
                
                // Hide progress modal
                IndexUI.hideProgressModal();
            });
    }
    
    /**
     * Finish the index update process with results
     * 
     * @param {Object} results - The index update results
     */
    function finishUpdate(results) {
        console.log('Index update completed:', results);
        
        // Store updated index data
        state.indexData = results;
        state.isUpdating = false;
        
        // Save state
        saveState();
        
        // Update UI
        IndexUI.updateFinalIndexTable(results);
        IndexUI.showFinalIndexPanel();
        
        // Update status badge
        IndexUI.updateStatusBadge('completed', 'Index updated');
        
        // Update status
        const dom = IndexUI.getDomElements();
        if (dom.updateStatusEl) {
            dom.updateStatusEl.textContent = 'Status: Index updated with film numbers';
            dom.updateStatusEl.style.color = '#4caf50';
        }
        
        // Show success message
        IndexUI.showToast('Index updated successfully', 'success');
    }
    
    // Return public API
    return {
        init,
        getState: () => state,
        saveState,
        resetIndex,
        generateIndex,
        finishGeneration,
        updateIndex,
        finishUpdate
    };
})();

// Initialize the module
IndexCore.init(); 