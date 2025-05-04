/**
 * Film Allocation Core Module
 * 
 * This module contains the core functionality for film allocation,
 * managing state and initialization.
 */
const AllocationCore = (function() {
    // Constants
    const CAPACITY_16MM = 2900;  // Pages per 16mm film roll (for display purposes only)
    const CAPACITY_35MM = 690;   // Pages per 35mm film roll (for display purposes only)
    
    // Module state
    const state = {
        projectId: null,
        taskId: null,
        analysisResults: null,
        allocationResults: null,
        isAllocating: false,
        intervalId: null,
        workflowType: 'standard', // 'standard' or 'hybrid'
        lastSaved: null
    };
    
    /**
     * Initialize the allocation module
     */
    function init() {
        try {
            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            state.projectId = urlParams.get('id');
            state.workflowType = urlParams.get('flow') || 'standard';
            
            console.log('[Allocation] Initializing module for project:', state.projectId, 'flow:', state.workflowType);
            
            // Try to restore from dedicated allocation data storage first
            const dedicatedAllocationData = JSON.parse(localStorage.getItem('microfilmAllocationData') || '{}');
            console.log('DEBUGGING - Allocation data being restored:');
            console.log('From dedicated storage:', dedicatedAllocationData);
            
            // If we have dedicated allocation data for this project, use it
            if (dedicatedAllocationData.projectId === state.projectId && dedicatedAllocationData.completed) {
                console.log('[Allocation] Restoring from dedicated allocation storage');
                if (dedicatedAllocationData.allocationResults) {
                    state.allocationResults = dedicatedAllocationData.allocationResults;
                    console.log('[Allocation] Restored allocation results from dedicated storage');
                }
            }
            
            // Try to restore state from localStorage as a fallback
            const savedState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            console.log('[Allocation] Checking regular workflow state storage:', savedState);
            
            // If we have a saved state for this project, use it
            if (savedState.projectId === state.projectId) {
                console.log('[Allocation] Found matching project ID in workflow state');
                
                // Restore workflow type if available
                if (savedState.workflowType) {
                    state.workflowType = savedState.workflowType;
                    console.log('[Allocation] Restored workflow type:', state.workflowType);
                }
                
                // Restore analysis results if available
                if (savedState.analysisResults) {
                    state.analysisResults = savedState.analysisResults;
                    console.log('[Allocation] Restored analysis results from workflow state');
                }
                
                // Restore allocation results if not already loaded from dedicated storage
                if (!state.allocationResults && savedState.allocation && 
                    savedState.allocation.completed && savedState.allocationResults) {
                    state.allocationResults = savedState.allocationResults;
                    console.log('[Allocation] Restored allocation results from workflow state');
                }
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
            console.error('Error during allocation module initialization:', error);
        }
    }
    
    /**
     * Initialize after DOM is fully loaded
     */
    function initAfterDOM() {
        try {
            console.log('[Allocation] Initializing after DOM loaded');
            
            // Update UI based on workflow type
            AllocationUI.updateWorkflowTypeUI();
            
            // If we already have allocation results, show them
            if (state.allocationResults) {
                console.log('[Allocation] Rendering saved allocation results');
                
                // Make sure we have the correct structure (may be nested in results property)
                // This handles cases where we restore from localStorage with different structures
                if (state.allocationResults.results && !state.allocationResults.rolls_16mm) {
                    // Keep original but add direct access to inner results for backward compatibility
                    const innerResults = state.allocationResults.results;
                    for (const key in innerResults) {
                        if (!state.allocationResults[key]) {
                            state.allocationResults[key] = innerResults[key];
                        }
                    }
                }
                
                AllocationUI.updateAllocationResults();
                AllocationUI.updateStatusBadge('completed', 'Allocation complete');
                
                // Enable/disable buttons as needed
                const dom = AllocationUI.getDomElements();
                if (dom.startAllocationBtn) dom.startAllocationBtn.disabled = false;
                if (dom.resetAllocationBtn) dom.resetAllocationBtn.disabled = false;
                
                // Initialize project info from analysis results
                if (state.analysisResults) {
                    AllocationUI.updateProjectInfo();
                }
                
                console.log('[Allocation] UI updated with saved allocation results');
                AllocationUI.showToast('Allocation results restored from saved data', 'info');
            } 
            // Otherwise, initialize project info if project ID is available
            else if (state.projectId) {
                // If we have analysis results but not allocation results, just update project info
                if (state.analysisResults) {
                    AllocationUI.updateProjectInfo();
                    AllocationUI.updateStatusBadge('pending', 'Ready for allocation');
                    
                    // Enable start button
                    const dom = AllocationUI.getDomElements();
                    if (dom.startAllocationBtn) dom.startAllocationBtn.disabled = false;
                    
                    console.log('[Allocation] UI updated with analysis results only');
                } else {
                    // Load analysis results from API
                    console.log('[Allocation] Loading analysis results from API');
                    AllocationAPI.loadAnalysisResults();
                }
            } else {
                // Show message if no project ID
                AllocationUI.updateStatusBadge('error', 'No project ID provided');
                console.warn('[Allocation] No project ID provided');
            }
            
            // Bind event listeners
            AllocationEvents.bindEvents();
            console.log('[Allocation] Event listeners bound');
        } catch (error) {
            console.error('Error during DOM initialization:', error);
        }
    }
    
    /**
     * Save the current state to localStorage
     */
    function saveState() {
        try {
            // Update workflow state in localStorage
            const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            
            // Update basic information
            workflowState.projectId = state.projectId;
            workflowState.workflowType = state.workflowType;
            
            // Save analysis results if available
            if (state.analysisResults) {
                workflowState.analysisResults = state.analysisResults;
                workflowState.analysis = {
                    completed: true,
                    timestamp: new Date().toISOString()
                };
            }
            
            // Save allocation results if available
            if (state.allocationResults) {
                workflowState.allocationResults = state.allocationResults;
                workflowState.allocation = {
                    completed: true,
                    timestamp: new Date().toISOString()
                };
                
                // Also save to dedicated allocation storage
                try {
                    localStorage.setItem('microfilmAllocationData', JSON.stringify({
                        allocationResults: state.allocationResults,
                        lastUpdated: new Date().toISOString(),
                        projectId: state.projectId,
                        completed: true
                    }));
                    console.log('[Allocation] Saved to dedicated allocation storage');
                } catch (error) {
                    console.error('[Allocation] Error saving to dedicated storage:', error);
                }
            }
            
            // Save the updated workflow state
            localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
            state.lastSaved = new Date().toISOString();
            
            console.log('[Allocation] State saved to localStorage');
            
            return true;
        } catch (error) {
            console.error('[Allocation] Error saving state to localStorage:', error);
            return false;
        }
    }
    
    /**
     * Reset the allocation results
     */
    function resetAllocation() {
        // Clear allocation results
        state.allocationResults = null;
        AllocationUI.clearAllocationResults();
        
        // Update status
        AllocationUI.updateStatusBadge('pending', 'Ready for allocation');
        
        // Enable start button, disable reset button
        const dom = AllocationUI.getDomElements();
        dom.startAllocationBtn.disabled = false;
        dom.resetAllocationBtn.disabled = true;
        
        // Save the updated state
        saveState();
        
        console.log('[Allocation] Allocation reset');
        AllocationUI.showToast('Allocation reset', 'info');
    }
    
    /**
     * Start the allocation process
     */
    function startAllocation() {
        if (!state.analysisResults) {
            console.error('Cannot start allocation without analysis results');
            return;
        }
        
        // Show allocation in progress state
        state.isAllocating = true;
        AllocationUI.updateStatusBadge('in-progress', 'Allocating documents...');
        
        const dom = AllocationUI.getDomElements();
        if (dom.startAllocationBtn) {
            dom.startAllocationBtn.disabled = true;
        }
        
        // Clear any previous allocation results
        AllocationUI.clearAllocationResults();
        
        // Show progress modal
        AllocationUI.showProgressModal();
        
        // Check if document structure is correctly formatted for allocation
        if (state.analysisResults.documents) {
            // Using documents array from analysisResults
        } else if (state.analysisResults.results && Array.isArray(state.analysisResults.results)) {
            // Convert results to proper format expected by backend
            state.analysisResults.documents = state.analysisResults.results;
        }

        // Log the data sent to the API
        console.log('Sending data to API:', {
            projectId: state.projectId,
            analysisResults: state.analysisResults
        });
        
        // Call the API to start allocation
        AllocationAPI.startAllocationProcess();
    }
    
    // Return public API
    return {
        init,
        getState: () => state,
        resetAllocation,
        startAllocation,
        saveState,
        CAPACITY_16MM,
        CAPACITY_35MM
    };
})(); 