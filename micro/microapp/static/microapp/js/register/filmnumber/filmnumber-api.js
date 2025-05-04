/**
 * Film Number Allocation API Module
 * 
 * This module handles API interactions for the film number allocation step.
 */

const FilmNumberAPI = (function() {
    // Get reference to core module
    function getCore() {
        return window.FilmNumberCore;
    }

    function getUI() {
        return window.FilmNumberUI;
    }
    
    /**
     * Start the film number allocation process
     */
    function startFilmNumberAllocationProcess() {
        const state = getCore().getState();
        
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
        
        console.log('Starting film number allocation with data:', requestData);
        
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
                setTimeout(() => startStatusPolling(), 2000);
            } else {
                getUI().showError('No task ID received from server');
            }
        })
        .catch(error => {
            console.error('Error starting film number allocation:', error);
            getUI().showError(`Error starting film number allocation: ${error.message}`);
            getUI().hideProgressModal();
            
            // Re-enable start button
            const dom = getUI().getDomElements();
            if (dom.startFilmNumberBtn) {
                dom.startFilmNumberBtn.disabled = false;
            }
        });
    }
    
    /**
     * Start polling for status updates
     */
    function startStatusPolling() {
        const state = getCore().getState();
        
        // IMPORTANT: Clear any existing intervals first
        stopStatusPolling();
        
        // Set up new interval with a reasonable delay
        state.intervalId = setInterval(checkAllocationStatus, 2000);
        
        // Initial check immediately
        checkAllocationStatus();
    }
    
    /**
     * Stop polling for status updates
     */
    function stopStatusPolling() {
        const state = getCore().getState();
        if (state.intervalId) {
            clearInterval(state.intervalId);
            state.intervalId = null;
        }
    }
    
    /**
     * Check the status of the film number allocation
     */
    function checkAllocationStatus() {
        const state = getCore().getState();
        const ui = getUI();
        
        // If we're not allocating anymore, stop polling
        if (!state.isAllocating || !state.taskId) {
            stopStatusPolling();
            return;
        }
        
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
                ui.updateProgress(data.progress);
                ui.updateProgressText(getProgressText(data));
                
                // Handle completed or error states
                if (data.status === 'completed') {
                    stopStatusPolling();  // Stop polling before handling completion
                    handleAllocationCompleted(data);
                } else if (data.status === 'error') {
                    stopStatusPolling();  // Stop polling before handling error
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
                    stopStatusPolling();
                    ui.showError(`Failed to check status: ${error.message}`);
                    ui.hideProgressModal();
                }
            });
    }
    
    /**
     * Handle successful allocation completion
     */
    function handleAllocationCompleted(data) {
        const state = getCore().getState();
        
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
            
            // Try to adapt to the actual structure
            if (state.filmNumberResults.project_id) {
                reconstructRollDataWithFilmNumbers(state.filmNumberResults);
            }
        }
        
        // Update index data with film numbers
        mergeFilmNumberResults(state.filmNumberResults);
        
        state.isAllocating = false;
        
        // Update localStorage with film number results - now handled by mergeFilmNumberResults
        // No need for separate saveResultsToLocalStorage call that might modify original data
        // saveResultsToLocalStorage(state.filmNumberResults);
        
        // Update UI
        getUI().hideProgressModal();
        getUI().updateFilmNumberResults();
        getUI().updateStatusBadge('completed', 'Film number allocation complete');
        
        // Update the index table
        getUI().updateIndexTable();
        
        // Get DOM elements for button updates
        const dom = getUI().getDomElements();
        
        // Enable reset button 
        if (dom.resetFilmNumberBtn) {
            dom.resetFilmNumberBtn.disabled = false;
        }
        
        // Create dedicated film data object
        try {
            // Create the dedicated microfilmFilmData object
            const filmData = getCore().createFilmDataObject();
            console.log('Film data object created:', filmData);
            
            // Temporarily disable next button (for testing purposes)
            if (dom.toNextStepBtn) {
                dom.toNextStepBtn.disabled = true;
                
                // Re-enable after 3 seconds (just to show we can control it)
                setTimeout(() => {
                    console.log('Re-enabling next button after save...');
                    dom.toNextStepBtn.disabled = false;
                }, 3000);
            }
        } catch (error) {
            console.error('Error creating film data object:', error);
        }
        
        // Remove task ID from session storage
        sessionStorage.removeItem('filmNumberTaskId');
        
        // Show success toast
        getUI().showToast('Film number allocation completed successfully', 'success');
    }

    /**
     * Merge film number results with index data
     */
    function mergeFilmNumberResults(results) {
        const state = getCore().getState();
        if (!state.indexData || !state.indexData.entries || !results) return;

        // Create a map of document segments for quick lookup
        const docSegmentMap = new Map();
        
        // Process 16mm rolls
        if (results.rolls_16mm) {
            results.rolls_16mm.forEach(roll => {
                roll.document_segments.forEach(segment => {
                    docSegmentMap.set(segment.doc_id, {
                        filmNumber: roll.film_number,
                        rollId: roll.roll_id,
                        blip: segment.blip,
                        blipend: segment.blipend
                    });
                });
            });
        }
        
        // Process 35mm rolls
        if (results.rolls_35mm) {
            results.rolls_35mm.forEach(roll => {
                roll.document_segments.forEach(segment => {
                    docSegmentMap.set(segment.doc_id, {
                        filmNumber: roll.film_number,
                        rollId: roll.roll_id,
                        blip: segment.blip,
                        blipend: segment.blipend
                    });
                });
            });
        }
        
        // Create a new entries array with film number information without modifying original
        const updatedEntries = state.indexData.entries.map(entry => {
            const segmentInfo = docSegmentMap.get(entry.docId);
            if (segmentInfo) {
                return {
                    ...entry,
                    filmNumber: segmentInfo.filmNumber,
                    finalIndex: segmentInfo.blip,
                    status: 'Updated'
                };
            }
            return { ...entry };
        });

        // Calculate status
        const updatedStatus = getCore().calculateIndexStatus(updatedEntries);
        
        // Create a new data structure for the film index data instead of updating the original
        const filmIndexData = {
            entries: updatedEntries,
            status: updatedStatus
        };
        
        // Store the new data in a separate state property
        state.filmIndexData = filmIndexData;
        
        // Save to separate localStorage item instead of overwriting the original
        try {
            localStorage.setItem('microfilmFilmIndexData', JSON.stringify({
                projectId: state.projectId,
                indexData: filmIndexData,
                timestamp: new Date().toISOString()
            }));
            
            // Also save the complete server response to a dedicated storage key
            localStorage.setItem('microfilmFilmNumberResults', JSON.stringify({
                projectId: state.projectId,
                results: results,
                timestamp: new Date().toISOString()
            }));
            
            // Update workflow state to record completion
            const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            workflowState.filmNumberAllocation = {
                completed: true,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
            
            console.log('Film index data saved to localStorage (original index data preserved)');
            console.log('Complete film number allocation results saved separately');
        } catch (error) {
            console.error('Error saving film data to localStorage:', error);
        }
        
        console.log('Created film index data from original:', filmIndexData);
    }

    /**
     * Update index data with allocated film numbers
     */
    function updateIndexDataWithFilmNumbers() {
        const state = getCore().getState();
        if (!state.indexData || !state.indexData.entries || !state.filmNumberResults) return;
        
        state.indexData.entries = state.indexData.entries.map(entry => {
            if (!entry.rollId) return entry;
            
            // Try to find film number for this roll
            let filmNumber = null;
            let roll = null;
            
            // Check 16mm rolls
            if (state.filmNumberResults.rolls_16mm) {
                roll = state.filmNumberResults.rolls_16mm.find(r => r.roll_id === entry.rollId);
                if (roll && roll.film_number) {
                    filmNumber = roll.film_number;
                }
            }
            
            // Check 35mm rolls if not found
            if (!filmNumber && state.filmNumberResults.rolls_35mm) {
                roll = state.filmNumberResults.rolls_35mm.find(r => r.roll_id === entry.rollId);
                if (roll && roll.film_number) {
                    filmNumber = roll.film_number;
                }
            }
            
            if (filmNumber) {
                // Generate blip format for final index
                const docIndex = entry.docIndex || 1;
                const frameStart = entry.frameStart || 1;
                const blip = `${filmNumber}-${docIndex.toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`;
                
                return {
                    ...entry,
                    filmNumber: filmNumber,
                    finalIndex: blip,
                    status: 'Updated'
                };
            }
            
            return entry;
        });
        
        // Update status counts
        state.indexData.status = getCore().calculateIndexStatus(state.indexData.entries);
        
        // Save to localStorage
        saveUpdatedIndexToLocalStorage(state.indexData);
    }

    /**
     * Save updated index data to localStorage
     */
    function saveUpdatedIndexToLocalStorage(indexData) {
        try {
            const core = getCore();
            const state = core.getState();
            
            localStorage.setItem('microfilmIndexData', JSON.stringify({
                projectId: state.projectId,
                indexData: indexData,
                timestamp: new Date().toISOString()
            }));
            console.log('Updated index data saved to localStorage');
        } catch (error) {
            console.error('Error saving updated index data to localStorage:', error);
        }
    }

    /**
     * Reconstruct roll data with film numbers based on allocation data and server response
     */
    function reconstructRollDataWithFilmNumbers(serverResponse) {
        const state = getCore().getState();
        
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
        
        // Create enriched result with film numbers
        const enrichedResults = {
            project_id: serverResponse.project_id,
            archive_id: serverResponse.archive_id,
            film_allocation_complete: serverResponse.film_allocation_complete,
            total_rolls_16mm: allocationData.total_rolls_16mm || 0,
            total_rolls_35mm: allocationData.total_rolls_35mm || 0,
            total_pages_16mm: allocationData.total_pages_16mm || 0,
            total_pages_35mm: allocationData.total_pages_35mm || 0,
            rolls_16mm: [],
            rolls_35mm: []
        };

        // Process 16mm rolls
        if (allocationData.rolls_16mm) {
            enrichedResults.rolls_16mm = allocationData.rolls_16mm.map((roll, index) => {
                const filmNumber = roll.film_number || `PENDING-${index+1}`;
                return {
                    ...roll,
                    film_number: filmNumber,
                    document_segments: (roll.document_segments || []).map((segment, docIndex) => {
                        const frameStart = segment.start_frame || 1;
                        const frameEnd = segment.end_frame || (frameStart + segment.pages - 1);
                        return {
                            ...segment,
                            blip: `${filmNumber}-${(docIndex + 1).toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`,
                            blipend: `${filmNumber}-${(docIndex + 1).toString().padStart(4, '0')}.${frameEnd.toString().padStart(5, '0')}`
                        };
                    })
                };
            });
        }

        // Process 35mm rolls
        if (allocationData.rolls_35mm) {
            enrichedResults.rolls_35mm = allocationData.rolls_35mm.map((roll, index) => {
                const filmNumber = roll.film_number || `PENDING-35-${index+1}`;
                return {
                    ...roll,
                    film_number: filmNumber,
                    document_segments: (roll.document_segments || []).map((segment, docIndex) => {
                        const frameStart = segment.start_frame || 1;
                        const frameEnd = segment.end_frame || (frameStart + segment.pages - 1);
                        return {
                            ...segment,
                            blip: `${filmNumber}-${(docIndex + 1).toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`,
                            blipend: `${filmNumber}-${(docIndex + 1).toString().padStart(4, '0')}.${frameEnd.toString().padStart(5, '0')}`
                        };
                    })
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
        const state = getCore().getState();
        const ui = getUI();
        
        // Make sure polling is stopped
        stopStatusPolling();
        
        // Show error
        ui.hideProgressModal();
        ui.showError(`Error in film number allocation: ${data.errors?.[0] || 'Unknown error'}`);
        ui.updateStatusBadge('error', 'Film number allocation failed');
        
        // Reset state
        state.isAllocating = false;
        state.taskId = null;
        
        // Re-enable start button
        const dom = ui.getDomElements();
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
            // Save film number results
            localStorage.setItem('microfilmFilmNumberData', JSON.stringify(results));
            
            // Update workflow state
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
    
    // Return public API
    return {
        startFilmNumberAllocationProcess,
        startStatusPolling,
        checkAllocationStatus,
        handleAllocationCompleted,
        handleAllocationError,
        saveResultsToLocalStorage,
        getProgressText
    };
})();

// Make FilmNumberAPI available globally
window.FilmNumberAPI = FilmNumberAPI;