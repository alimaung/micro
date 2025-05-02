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
        workflowType: 'standard' // 'standard' or 'hybrid'
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
            
            // Try to restore state from localStorage if available
            const savedState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            
            // If we have a saved state for this project, use it
            if (savedState.projectId === state.projectId) {
                // Restore workflow type if available
                if (savedState.workflowType) {
                    state.workflowType = savedState.workflowType;
                }
                
                // Restore analysis results if available
                if (savedState.analysisResults) {
                    state.analysisResults = savedState.analysisResults;
                }
                
                // Restore allocation results if completed
                if (savedState.allocation && savedState.allocation.completed && savedState.allocationResults) {
                    state.allocationResults = savedState.allocationResults;
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
            // Update UI based on workflow type
            AllocationUI.updateWorkflowTypeUI();
            
            // If we already have allocation results, show them
            if (state.allocationResults) {
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
                } else {
                    // Load analysis results from API
                    AllocationAPI.loadAnalysisResults();
                }
            } else {
                // Show message if no project ID
                AllocationUI.updateStatusBadge('error', 'No project ID provided');
            }
            
            // Bind event listeners
            AllocationEvents.bindEvents();
        } catch (error) {
            console.error('Error during DOM initialization:', error);
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
        
        // Call the API to start allocation
        AllocationAPI.startAllocationProcess();
    }
    
    // Return public API
    return {
        init,
        getState: () => state,
        resetAllocation,
        startAllocation,
        CAPACITY_16MM,
        CAPACITY_35MM
    };
})(); 