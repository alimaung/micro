/**
 * Film Index Events Module
 * 
 * This module handles user interaction events for film index generation.
 */
const IndexEvents = (function() {
    // Reference to DOM elements
    let dom;
    
    /**
     * Initialize the event handlers
     */
    function init() {
        // Get DOM elements
        dom = IndexUI.getDomElements();
        
        // Bind events
        bindGenerateIndexEvent();
        bindResetIndexEvent();
        bindUpdateIndexEvent();
        bindExportEvents();
        bindNavigationEvents();
        bindToggleDataPanelEvent();
    }
    
    /**
     * Bind event for generate index button
     */
    function bindGenerateIndexEvent() {
        if (!dom.generateIndexBtn) return;
        
        dom.generateIndexBtn.addEventListener('click', (event) => {
            event.preventDefault();
            
            // Get the state
            const state = IndexCore.getState();
            
            if (!state.projectId) {
                IndexUI.showToast('Project ID is required', 'error');
                return;
            }
            
            // Disable the button to prevent multiple clicks
            dom.generateIndexBtn.disabled = true;
            
            // Update the status badge
            IndexUI.updateStatusBadge('in-progress', 'Generating index...');
            
            // Show the progress modal
            IndexUI.showProgressModal('Generating Film Index', 'Starting index generation...');
            
            // Generate the index
            IndexCore.generateIndex();
            
            // Start polling for progress updates if we have a task ID
            // (this will be updated by generateIndex with the new task ID)
            // We'll let IndexCore handle the polling now
        });
    }
    
    /**
     * Bind event for reset index button
     */
    function bindResetIndexEvent() {
        if (!dom.resetIndexBtn) return;
        
        dom.resetIndexBtn.addEventListener('click', (event) => {
            event.preventDefault();
            
            if (confirm('Are you sure you want to reset the index? This will clear all generated data.')) {
                // Reset the index
                IndexCore.resetIndex();
                
                // Clear the index display
                IndexUI.clearIndexDisplay();
                
                // Update the status badge
                IndexUI.updateStatusBadge('pending', 'Index not generated');
                
                // Enable the generate button
                if (dom.generateIndexBtn) {
                    dom.generateIndexBtn.disabled = false;
                }
            }
        });
    }
    
    /**
     * Bind event for update index button
     */
    function bindUpdateIndexEvent() {
        if (!dom.updateIndexBtn) return;
        
        dom.updateIndexBtn.addEventListener('click', (event) => {
            event.preventDefault();
            
            // Get the state
            const state = IndexCore.getState();
            
            if (!state.projectId) {
                IndexUI.showToast('Project ID is required', 'error');
                return;
            }
            
            if (!state.filmNumbers || state.filmNumbers.length === 0) {
                IndexUI.showToast('Film numbers are required', 'error');
                return;
            }
            
            // Disable the button to prevent multiple clicks
            dom.updateIndexBtn.disabled = true;
            
            // Update the status badge
            IndexUI.updateStatusBadge('in-progress', 'Updating index...');
            
            // Show the progress modal
            IndexUI.showProgressModal('Updating Film Index', 'Starting index update...');
            
            // Update the index
            IndexCore.updateIndex();
            
            // Start polling for progress updates if we have a task ID
            if (state.taskId) {
                startProgressPolling(state.taskId);
            }
        });
    }
    
    /**
     * Bind events for exporting data
     */
    function bindExportEvents() {
        // Bind event for download CSV button
        if (dom.downloadCsvBtn) {
            dom.downloadCsvBtn.addEventListener('click', (event) => {
                event.preventDefault();
                
                const state = IndexCore.getState();
                if (!state.projectId || !state.indexData) {
                    IndexUI.showToast('No index data available', 'error');
                    return;
                }
                
                exportIndexToCsv(false);
            });
        }
        
        // Bind event for download final CSV button
        if (dom.downloadFinalCsvBtn) {
            dom.downloadFinalCsvBtn.addEventListener('click', (event) => {
                event.preventDefault();
                
                const state = IndexCore.getState();
                if (!state.projectId || !state.indexData) {
                    IndexUI.showToast('No index data available', 'error');
                    return;
                }
                
                exportIndexToCsv(true);
            });
        }
        
        // Bind event for export JSON button
        if (dom.exportJsonBtn) {
            dom.exportJsonBtn.addEventListener('click', (event) => {
                event.preventDefault();
                
                const state = IndexCore.getState();
                if (!state.projectId || !state.indexData) {
                    IndexUI.showToast('No index data available', 'error');
                    return;
                }
                
                exportIndexToJson();
            });
        }
    }
    
    /**
     * Bind events for navigation
     */
    function bindNavigationEvents() {
        // Bind event for back to allocation button
        if (dom.backToAllocationBtn) {
            dom.backToAllocationBtn.addEventListener('click', (event) => {
                event.preventDefault();
                
                // Save the current state
                IndexCore.saveState();
                
                // Redirect to allocation page
                const state = IndexCore.getState();
                const projectId = state.projectId;
                const workflowType = state.workflowType || 'hybrid';
                
                console.log('Navigating to allocation page with:', { projectId, workflowType });
                
                // Ensure we're using the same URL parameter names as the allocation page expects
                window.location.href = `/register/allocation/?id=${projectId}&flow=${workflowType}`;
            });
        }
        
        // Bind event for to film number button
        if (dom.toFilmNumberBtn) {
            dom.toFilmNumberBtn.addEventListener('click', (event) => {
                event.preventDefault();
                
                // Save the current state
                IndexCore.saveState();

                // Log the full workflow state from localStorage for debugging
                console.log('DEBUGGING - Full workflowState from localStorage:');
                const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                console.log(workflowState);
                
                // Log the index data specifically
                console.log('DEBUGGING - Index data being saved:');
                const dedicatedIndexData = JSON.parse(localStorage.getItem('microfilmIndexData') || '{}');
                console.log('From dedicated storage:', dedicatedIndexData);

                // Log the project data specifically
                console.log('DEBUGGING - Project data being saved:');
                const projectData = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
                console.log(projectData);
                
                // Log the analysis data specifically
                console.log('DEBUGGING - Analysis data being saved:');
                const dedicatedAnalysisData = JSON.parse(localStorage.getItem('microfilmAnalysisData') || '{}');
                console.log('From dedicated storage:', dedicatedAnalysisData);

                // Log the allocation data specifically
                console.log('DEBUGGING - Allocation data being saved:');
                const dedicatedAllocationData = JSON.parse(localStorage.getItem('microfilmAllocationData') || '{}');
                console.log('From dedicated storage:', dedicatedAllocationData);


                // Redirect to film number page
                const state = IndexCore.getState();
                const projectId = state.projectId;
                const workflowType = state.workflowType || 'hybrid';
                
                console.log('Navigating to film number page with:', { projectId, workflowType });
                
                // Use the same parameter names as expected by the film number page
                window.location.href = `/register/filmnumber/?id=${projectId}&flow=${workflowType}`;
            });
        }
    }
    
    /**
     * Bind event for toggling data panel
     */
    function bindToggleDataPanelEvent() {
        if (!dom.toggleDataPanelBtn || !dom.indexDataPanel) return;
        
        dom.toggleDataPanelBtn.addEventListener('click', (event) => {
            event.preventDefault();
            
            dom.indexDataPanel.classList.toggle('expanded');
            
            // Update the button text
            const isExpanded = dom.indexDataPanel.classList.contains('expanded');
            dom.toggleDataPanelBtn.textContent = isExpanded ? 'Hide Raw Data' : 'Show Raw Data';
        });
    }
    
    /**
     * Start polling for task progress
     * 
     * @param {string} taskId - Task ID to poll for
     */
    function startProgressPolling(taskId) {
        const state = IndexCore.getState();
        
        // Safety check for taskId
        if (!taskId) {
            console.warn('Task ID is missing for polling, using default behavior');
            setTimeout(() => {
                // After a delay, try to get the index results directly
                IndexAPI.getIndexResults(state.projectId)
                    .then(response => {
                        if (response && response.results) {
                            // Call finishGeneration with the results
                            IndexCore.finishGeneration(response.results);
                        } else {
                            console.warn('No results found, UI may need updating');
                            // Close progress UI anyway
                            IndexUI.hideProgressModal();
                            IndexUI.showToast('Process completed but no results returned', 'warning');
                        }
                    })
                    .catch(error => {
                        console.error('Error getting results:', error);
                        IndexUI.hideProgressModal();
                        IndexUI.showToast('Error: ' + error.message, 'error');
                    });
            }, 3000);
            return;
        }
        
        console.log('Starting progress polling for task:', taskId);
        
        // Set up interval to poll for progress
        state.intervalId = setInterval(() => {
            IndexAPI.getTaskStatus(taskId)
                .then(response => {
                    console.log('Task status response:', response);
                    
                    // Update progress in UI
                    const progress = response.progress || 0;
                    IndexUI.updateProgress(progress);
                    
                    // Check if completed
                    if (response.status === 'completed') {
                        console.log('Task completed, clearing interval');
                        clearInterval(state.intervalId);
                        state.intervalId = null;
                        state.isGenerating = false;
                        
                        // Get the results
                        if (response.results) {
                            console.log('Task completed with results:', response.results);
                            // Call finishGeneration with the results
                            IndexCore.finishGeneration(response.results);
                        } else {
                            console.log('Task completed, fetching results...');
                            IndexAPI.getIndexResults(state.projectId)
                                .then(resultsResponse => {
                                    if (resultsResponse && resultsResponse.results) {
                                        IndexCore.finishGeneration(resultsResponse.results);
                                    } else {
                                        throw new Error('No results returned from server');
                                    }
                                })
                                .catch(error => {
                                    console.error('Error getting index results:', error);
                                    IndexUI.showToast('Failed to get index results: ' + error.message, 'error');
                                });
                        }
                        
                        // Hide the progress modal
                        IndexUI.hideProgressModal();
                        
                        // Update status badge
                        IndexUI.updateStatusBadge('completed', 'Index generated');
                    } else if (response.status === 'error') {
                        console.error('Task error:', response.errors);
                        clearInterval(state.intervalId);
                        state.intervalId = null;
                        state.isGenerating = false;
                        
                        // Hide the progress modal
                        IndexUI.hideProgressModal();
                        
                        // Show error status with details if available
                        const errorMessage = response.errors && response.errors.length > 0 
                            ? response.errors.join('. ') 
                            : 'Unknown error occurred';
                        IndexUI.showToast('Index generation failed: ' + errorMessage, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error polling task status:', error);
                    // Don't clear interval on network errors, try again
                });
        }, 5000); // Poll every 5 seconds
    }
    
    /**
     * Export index to CSV
     * 
     * @param {boolean} isFinal - Whether to export the final index
     */
    function exportIndexToCsv(isFinal) {
        const state = IndexCore.getState();
        
        if (!state.indexData) {
            IndexUI.showToast('No index data to export', 'error');
            return;
        }
        
        // Generate CSV content from index data
        const csvContent = generateCsvFromIndexData(state.indexData, isFinal);
        
        // Generate filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `index-${state.projectId}-${isFinal ? 'final' : 'initial'}-${timestamp}.csv`;
        
        // Download the file
        IndexAPI.downloadFile(csvContent, filename, 'text/csv');
        
        // Show success message
        IndexUI.showToast('CSV exported successfully', 'success');
    }
    
    /**
     * Generate CSV content from index data
     * 
     * @param {Object} indexData - The index data
     * @param {boolean} isFinal - Whether to include final index
     * @returns {string} - CSV content
     */
    function generateCsvFromIndexData(indexData, isFinal) {
        // Handle different data formats
        let entries = [];
        
        if (Array.isArray(indexData)) {
            entries = indexData;
        } else if (indexData.index && Array.isArray(indexData.index)) {
            entries = indexData.index;
        } else if (indexData.data && Array.isArray(indexData.data)) {
            entries = indexData.data;
        } else if (indexData.results && Array.isArray(indexData.results)) {
            entries = indexData.results;
        } else {
            console.error('Unknown index data format:', indexData);
            return '';
        }
        
        // Generate CSV header
        let csv = isFinal 
            ? 'Document ID,COM ID,Roll ID,Final Index\n' 
            : 'Document ID,COM ID,Roll ID,Frame Start,Frame End,Final Index\n';
        
        // Generate CSV rows
        entries.forEach(entry => {
            let docId, comId, initialIndex, finalIndex;
            
            // Handle different entry formats
            if (Array.isArray(entry)) {
                [docId, comId, initialIndex, finalIndex] = entry;
            } else {
                docId = entry.doc_id || entry.docId || '-';
                comId = entry.com_id || entry.comId || '-';
                initialIndex = entry.initial_index || entry.initialIndex || [0, 0, 0];
                finalIndex = entry.final_index || entry.finalIndex || '-';
            }
            
            // Ensure initialIndex is properly formatted
            if (!initialIndex || !Array.isArray(initialIndex)) {
                initialIndex = [0, 0, 0];
            }
            
            const rollId = initialIndex[0];
            const frameStart = initialIndex[1];
            const frameEnd = initialIndex[2];
            
            if (isFinal) {
                csv += `${docId},${comId},${rollId},${finalIndex}\n`;
            } else {
                csv += `${docId},${comId},${rollId},${frameStart},${frameEnd},${finalIndex}\n`;
            }
        });
        
        return csv;
    }
    
    /**
     * Export index to JSON
     */
    function exportIndexToJson() {
        const state = IndexCore.getState();
        
        IndexAPI.exportToJson(state.projectId)
            .then(jsonData => {
                // Generate filename
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const filename = `index-${state.projectId}-${timestamp}.json`;
                
                // Download the file
                const jsonString = JSON.stringify(jsonData, null, 2);
                IndexAPI.downloadFile(jsonString, filename, 'application/json');
                
                // Show success message
                IndexUI.showToast('JSON exported successfully', 'success');
            })
            .catch(error => {
                IndexUI.showToast(`Error exporting JSON: ${error.message}`, 'error');
            });
    }
    
    // Return public API
    return {
        init,
        startProgressPolling
    };
})();

// Initialize events when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    IndexEvents.init();
}); 