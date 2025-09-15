/**
 * Film Number Allocation API Module
 * 
 * This module handles API interactions for the film number allocation step.
 */

import { getState } from './core.js';
import * as FilmNumberUI from './ui.js';

/**
 * Start the film number allocation process
 */
export function startFilmNumberAllocationProcess() {
    const state = getState();
    
    // Prepare data for API request
    const requestData = {
        projectId: state.projectId,
        projectData: state.projectData || {
            projectId: state.projectId,
            workflowType: state.workflowType,
            hasOversized: state.analysisResults?.hasOversized || false
        },
        analysisData: state.analysisResults,
        allocationData: state.allocationResults,
        indexData: state.indexData?.indexData || null
    };
    
    // Log the data being sent
    console.log('Starting film number allocation with data:', requestData);
    
    // Use the correct endpoint
    fetch('/api/filmnumber/allocate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Film number allocation started:', data);
        
        if (data.taskId) {
            // Store task ID for status polling
            state.taskId = data.taskId;
            sessionStorage.setItem('filmNumberTaskId', data.taskId);
            
            // Start polling for status
            startStatusPolling();
        } else {
            FilmNumberUI.showError('No task ID received from server');
        }
    })
    .catch(error => {
        console.error('Error starting film number allocation:', error);
        FilmNumberUI.showError(`Error starting film number allocation: ${error.message}`);
        FilmNumberUI.hideProgressModal();
        
        // Re-enable start button
        const dom = FilmNumberUI.getDomElements();
        if (dom.startFilmNumberBtn) {
            dom.startFilmNumberBtn.disabled = false;
        }
    });
}

/**
 * Start polling for status updates
 */
export function startStatusPolling() {
    const state = getState();
    
    // Clear any existing interval
    if (state.intervalId) {
        clearInterval(state.intervalId);
    }
    
    // Set up new interval for polling
    state.intervalId = setInterval(checkAllocationStatus, 2000);
}

/**
 * Check the status of the film number allocation
 */
function checkAllocationStatus() {
    const state = getState();
    
    if (!state.taskId) {
        // No task ID, stop polling
        if (state.intervalId) {
            clearInterval(state.intervalId);
            state.intervalId = null;
        }
        return;
    }
    
    // Use the correct endpoint
    fetch(`/api/filmnumber/status/?taskId=${state.taskId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Film number allocation status:', data);
        
        // Update UI with progress
        FilmNumberUI.updateProgress(data.progress);
        FilmNumberUI.updateProgressText(getProgressText(data));
        
        // Handle completed or error states
        if (data.status === 'completed') {
            handleAllocationCompleted(data);
        } else if (data.status === 'error') {
            handleAllocationError(data);
        }
    })
    .catch(error => {
        console.error('Error checking film number allocation status:', error);
        
        // After multiple fails, stop checking
        if (state.errorCount === undefined) {
            state.errorCount = 1;
        } else {
            state.errorCount++;
        }
        
        if (state.errorCount > 5) {
            clearInterval(state.intervalId);
            state.intervalId = null;
            FilmNumberUI.showError(`Failed to check status: ${error.message}`);
            FilmNumberUI.hideProgressModal();
        }
    });
}

/**
 * Handle successful allocation completion
 */
function handleAllocationCompleted(data) {
    const state = getState();
    
    // Stop polling
    if (state.intervalId) {
        clearInterval(state.intervalId);
        state.intervalId = null;
    }
    
    console.log('Film number allocation completed with results:', data);
    
    // Store results - handle different response structures
    if (data.results) {
        state.filmNumberResults = data.results;
    } else {
        // If results aren't in a nested property, the whole response might be the results
        state.filmNumberResults = data;
    }
    
    // Check if we have the expected data structure
    if (!state.filmNumberResults.rolls_16mm && !state.filmNumberResults.rolls_35mm) {
        console.warn('Received unexpected data structure from server:', state.filmNumberResults);
        
        // Try to adapt to the actual structure - inspect the response to find roll data
        if (state.filmNumberResults.project_id) {
            // This might be a summary only, we need to construct roll data from pre-allocation
            reconstructRollDataWithFilmNumbers(state.filmNumberResults);
        }
    }
    
    state.isAllocating = false;
    
    // Update localStorage with results
    saveResultsToLocalStorage(state.filmNumberResults);
    
    // Update UI
    FilmNumberUI.hideProgressModal();
    FilmNumberUI.updateFilmNumberResults();
    FilmNumberUI.updateStatusBadge('completed', 'Film number allocation complete');
    
    // Update the final index table with film numbers
    FilmNumberUI.updateFinalIndexTable();
    
    // Enable navigation to next step
    const dom = FilmNumberUI.getDomElements();
    if (dom.toNextStepBtn) {
        dom.toNextStepBtn.disabled = false;
    }
    if (dom.resetFilmNumberBtn) {
        dom.resetFilmNumberBtn.disabled = false;
    }
    
    // Clear session storage task ID
    sessionStorage.removeItem('filmNumberTaskId');
    
    // Show success toast
    FilmNumberUI.showToast('Film number allocation completed successfully', 'success');
}

/**
 * Reconstruct roll data with film numbers based on allocation data and server response
 */
function reconstructRollDataWithFilmNumbers(serverResponse) {
    const state = getState();
    
    // If server doesn't return full roll data, we'll build it from allocation data + film numbers
    if (!state.allocationResults) return;
    
    // Get allocation data in correct structure
    let allocationData;
    if (state.allocationResults.allocationResults && state.allocationResults.allocationResults.results) {
        allocationData = state.allocationResults.allocationResults.results;
    } else if (state.allocationResults.results) {
        allocationData = state.allocationResults.results;
    } else {
        allocationData = state.allocationResults;
    }
    
    // Get film numbers from server response if available
    const filmNumbers = serverResponse.film_numbers || [];
    
    // Create enriched result with film numbers
    const enrichedResults = {
        project_id: serverResponse.project_id,
        archive_id: serverResponse.archive_id,
        film_allocation_complete: true,
        total_rolls_16mm: allocationData.total_rolls_16mm || 0,
        total_rolls_35mm: allocationData.total_rolls_35mm || 0,
        total_pages_16mm: allocationData.total_pages_16mm || 0,
        total_pages_35mm: allocationData.total_pages_35mm || 0,
        rolls_16mm: [],
        rolls_35mm: []
    };
    
    // Enrich 16mm rolls with film numbers
    if (allocationData.rolls_16mm) {
        enrichedResults.rolls_16mm = allocationData.rolls_16mm.map((roll, index) => {
            const filmNumber = filmNumbers[index] || `PENDING-${index+1}`;
            return {
                ...roll,
                film_number: filmNumber
            };
        });
    }
    
    // Enrich 35mm rolls with film numbers
    if (allocationData.rolls_35mm) {
        const startIdx = enrichedResults.rolls_16mm.length;
        enrichedResults.rolls_35mm = allocationData.rolls_35mm.map((roll, index) => {
            const filmNumber = filmNumbers[startIdx + index] || `PENDING-35-${index+1}`;
            return {
                ...roll,
                film_number: filmNumber
            };
        });
    }
    
    // Update the state with the enriched results
    state.filmNumberResults = enrichedResults;
    console.log('Reconstructed film number results:', state.filmNumberResults);
}

/**
 * Handle allocation error
 */
function handleAllocationError(data) {
    const state = getState();
    
    // Stop polling
    if (state.intervalId) {
        clearInterval(state.intervalId);
        state.intervalId = null;
    }
    
    // Show error
    FilmNumberUI.hideProgressModal();
    FilmNumberUI.showError(`Error in film number allocation: ${data.errors?.[0] || 'Unknown error'}`);
    FilmNumberUI.updateStatusBadge('error', 'Film number allocation failed');
    
    // Reset state
    state.isAllocating = false;
    state.taskId = null;
    
    // Re-enable start button
    const dom = FilmNumberUI.getDomElements();
    if (dom.startFilmNumberBtn) {
        dom.startFilmNumberBtn.disabled = false;
    }
    
    // Clear session storage task ID
    sessionStorage.removeItem('filmNumberTaskId');
}

/**
 * Save results to localStorage
 */
function saveResultsToLocalStorage(results) {
    try {
        // Save film number results using the correct key
        localStorage.setItem('microfilmFilmNumberData', JSON.stringify(results));
        
        // Also update the workflow state if needed
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        workflowState.filmNumberAllocation = {
            completed: true,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        
        console.log('Film number results saved to localStorage');
    } catch (error) {
        console.error('Error saving results to localStorage:', error);
    }
}

/**
 * Get progress text based on status
 */
function getProgressText(data) {
    switch (data.status) {
        case 'pending':
            return 'Preparing film number allocation...';
        case 'processing':
            if (data.progress < 10) {
                return 'Initializing film number allocation...';
            } else if (data.progress < 30) {
                return 'Processing 16mm rolls...';
            } else if (data.progress < 60) {
                return 'Processing 35mm rolls...';
            } else if (data.progress < 90) {
                return 'Generating blip codes...';
            } else {
                return 'Finalizing film number allocation...';
            }
        case 'completed':
            return 'Film number allocation completed successfully!';
        case 'error':
            return `Error: ${data.errors?.[0] || 'Unknown error'}`;
        default:
            return 'Processing...';
    }
} 