/**
 * Film Allocation API Module
 * 
 * This module handles all API calls and data processing for film allocation.
 */
const AllocationAPI = (function() {
    /**
     * Load analysis results for the current project
     */
    function loadAnalysisResults() {
        const state = AllocationCore.getState();
        
        // Show loading state
        AllocationUI.updateStatusBadge('pending', 'Loading analysis results...');

        try {
            // First try to get analysis results from localStorage
            const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            
            // Check if we have analysis results in localStorage
            if (workflowState.analysisResults) {
                // Store analysis results in the core state
                const stateRef = AllocationCore.getState();
                stateRef.analysisResults = workflowState.analysisResults;
                
                // Update project info
                AllocationUI.updateProjectInfo();
                
                // Update status
                AllocationUI.updateStatusBadge('pending', 'Ready for allocation');
                
                const dom = AllocationUI.getDomElements();
                if (dom.startAllocationBtn) {
                    dom.startAllocationBtn.disabled = false;
                }
                
                return; // Exit early since we found the data
            }
        } catch (error) {
            console.error('Error reading from localStorage:', error);
        }
        
        // If we get here, either localStorage didn't have the data or there was an error reading it
        // Fetch analysis results from API as fallback
        fetch(`/api/documents/analysis-results?projectId=${state.projectId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load analysis results from API');
                }
                return response.json();
            })
            .then(data => {
                // Store analysis results
                const stateRef = AllocationCore.getState();
                stateRef.analysisResults = data.results;
                
                // Update project info
                AllocationUI.updateProjectInfo();
                
                // Update status
                AllocationUI.updateStatusBadge('pending', 'Ready for allocation');
                
                const dom = AllocationUI.getDomElements();
                if (dom.startAllocationBtn) {
                    dom.startAllocationBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error loading analysis results from API:', error);
                
                const stateRef = AllocationCore.getState();
                
                // Create mock analysis results for testing/fallback
                stateRef.analysisResults = {
                    projectId: state.projectId,
                    documentCount: 0,
                    totalPages: 0,
                    hasOversized: state.workflowType === 'hybrid',
                    oversizedPages: 0
                };
                
                // Try to get workflow state one more time for any partial data
                try {
                    const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                    if (workflowState.projectId === state.projectId) {
                        // If we have some project information, use it
                        if (workflowState.analysis) {
                            Object.assign(stateRef.analysisResults, workflowState.analysis);
                        }
                    }
                } catch (e) {
                    console.error('Error getting partial data from localStorage:', e);
                }
                
                AllocationUI.updateProjectInfo();
                AllocationUI.updateStatusBadge('error', 'Could not load analysis results. Using default values.');
                
                // Still enable the start button for testing
                const dom = AllocationUI.getDomElements();
                if (dom.startAllocationBtn) {
                    dom.startAllocationBtn.disabled = false;
                }
            });
    }
    
    /**
     * Start the allocation process via API
     */
    function startAllocationProcess() {
        const state = AllocationCore.getState();
        
        // Start allocation API call
        fetch('/api/allocation/allocate-film', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                projectId: state.projectId,
                analysisResults: state.analysisResults
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to start allocation');
            }
            return response.json();
        })
        .then(data => {
            // Store the task ID
            const stateRef = AllocationCore.getState();
            stateRef.taskId = data.taskId;
            
            // Start polling for status
            startStatusPolling();
        })
        .catch(error => {
            console.error('Error starting allocation:', error);
            AllocationUI.updateStatusBadge('error', 'Failed to start allocation');
            AllocationUI.hideProgressModal();
            
            const stateRef = AllocationCore.getState();
            stateRef.isAllocating = false;
            
            const dom = AllocationUI.getDomElements();
            if (dom.startAllocationBtn) {
                dom.startAllocationBtn.disabled = false;
            }
        });
    }
    
    /**
     * Start polling for allocation status
     */
    function startStatusPolling() {
        const state = AllocationCore.getState();
        if (!state.taskId) return;
        
        // Clear any existing interval
        if (state.intervalId) {
            clearInterval(state.intervalId);
        }
        
        // Set up interval for polling
        const stateRef = AllocationCore.getState();
        stateRef.intervalId = setInterval(() => {
            fetch(`/api/allocation/allocation-status?taskId=${state.taskId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to get allocation status');
                    }
                    return response.json();
                })
                .then(data => {
                    // Update progress
                    AllocationUI.updateProgress(data.progress, data.status);
                    
                    // Check if allocation is complete
                    if (data.status === 'completed') {
                        // Stop polling
                        clearInterval(state.intervalId);
                        stateRef.intervalId = null;
                        
                        // Hide progress modal
                        AllocationUI.hideProgressModal();
                        
                        // Update state
                        stateRef.isAllocating = false;
                        
                        // Fetch full allocation results
                        fetchAllocationResults();
                    } else if (data.status === 'error') {
                        // Stop polling
                        clearInterval(state.intervalId);
                        stateRef.intervalId = null;
                        
                        // Hide progress modal
                        AllocationUI.hideProgressModal();
                        
                        // Update state
                        stateRef.isAllocating = false;
                        
                        const dom = AllocationUI.getDomElements();
                        dom.startAllocationBtn.disabled = false;
                        
                        // Show error
                        AllocationUI.updateStatusBadge('error', 'Allocation failed');
                        
                        console.error('Allocation failed', data.errors);
                    }
                })
                .catch(error => {
                    console.error('Error checking allocation status:', error);
                });
        }, 1000);
    }
    
    /**
     * Fetch allocation results after completion
     */
    function fetchAllocationResults() {
        const state = AllocationCore.getState();
        
        fetch(`/api/allocation/allocation-results?projectId=${state.projectId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch allocation results');
                }
                return response.json();
            })
            .then(data => {
                // Store allocation results - maintain the original response structure 
                // since UI will handle extracting the nested results
                const stateRef = AllocationCore.getState();
                stateRef.allocationResults = data.results || data;
                
                // Update UI with results
                AllocationUI.updateAllocationResults();
            })
            .catch(error => {
                console.error('Error fetching allocation results:', error);
                AllocationUI.updateStatusBadge('error', 'Failed to fetch allocation results');
            });
    }
    
    // Return public API
    return {
        loadAnalysisResults,
        startAllocationProcess,
        fetchAllocationResults
    };
})(); 