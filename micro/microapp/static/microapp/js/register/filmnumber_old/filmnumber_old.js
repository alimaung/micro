/**
 * Film Number Allocation Module
 * 
 * This module handles the film number allocation step,
 * building on the previously calculated allocation.
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
        isAllocating: false,
        intervalId: null,
        workflowType: 'standard', // 'standard' or 'hybrid'
        projectData: null,
        indexData: null
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
    function resetFilmNumberAllocation() {
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
    
    // Return public API
    return {
        init,
        getState: () => state,
        resetFilmNumberAllocation,
        startFilmNumberAllocation,
        getLocalStorageData,  // Expose the getLocalStorageData function
        CAPACITY_16MM,
        CAPACITY_35MM
    };
})();

const FilmNumberAPI = (function() {
    // Reference to state
    const getState = () => FilmNumberCore.getState();
    
    /**
     * Start the film number allocation process
     */
    function startFilmNumberAllocationProcess() {
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
    function startStatusPolling() {
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
    
    // Return public API
    return {
        startFilmNumberAllocationProcess,
        checkAllocationStatus
    };
})();

const FilmNumberUI = (function() {
    // Cache DOM elements
    let domElements = {};
    
    /**
     * Get DOM elements for UI manipulation
     */
    function getDomElements() {
        if (Object.keys(domElements).length === 0) {
            // Initialize dom element cache
            domElements = {
                // Status and controls
                statusBadge: document.getElementById('filmnumber-status-badge'),
                startFilmNumberBtn: document.getElementById('start-filmnumber'),
                resetFilmNumberBtn: document.getElementById('reset-filmnumber'),
                toNextStepBtn: document.getElementById('to-step-6'),
                backBtn: document.getElementById('back-to-allocation'),
                
                // Project info
                projectId: document.getElementById('project-id'),
                documentCount: document.getElementById('document-count'),
                totalPages: document.getElementById('total-pages'),
                workflowType: document.getElementById('workflow-type'),
                oversizedCount: document.getElementById('oversized-count'),
                
                // Film sections
                film16mmSection: document.getElementById('film-16mm-section'),
                film35mmSection: document.getElementById('film-35mm-section'),
                
                // Roll counts and containers
                rollCount16mm: document.getElementById('roll-count-16mm'),
                pagesAllocated16mm: document.getElementById('pages-allocated-16mm'),
                utilization16mm: document.getElementById('utilization-16mm'),
                filmRolls16mm: document.getElementById('film-rolls-16mm'),
                
                rollCount35mm: document.getElementById('roll-count-35mm'),
                pagesAllocated35mm: document.getElementById('pages-allocated-35mm'),
                utilization35mm: document.getElementById('utilization-35mm'),
                filmRolls35mm: document.getElementById('film-rolls-35mm'),
                
                // Split documents
                splitDocumentsPanel: document.getElementById('split-documents-panel'),
                splitDocumentsTable: document.getElementById('split-documents-table'),
                
                // Details
                filmNumberDetailsJson: document.getElementById('filmnumber-details-json'),
                
                // Progress modal
                progressModal: document.getElementById('filmnumber-progress-modal'),
                progressBar: document.getElementById('filmnumber-progress-bar'),
                progressText: document.getElementById('filmnumber-progress-text')
            };
        }
        return domElements;
    }
    
    /**
     * Update the workflow type UI
     */
    function updateWorkflowTypeUI() {
        const state = FilmNumberCore.getState();
        const dom = getDomElements();
        
        // Update workflow type display
        if (dom.workflowType) {
            dom.workflowType.textContent = state.workflowType === 'hybrid' ? 'Hybrid (16mm + 35mm)' : 'Standard (16mm only)';
        }
        
        // Show/hide 35mm section based on workflow type
        if (dom.film35mmSection) {
            if (state.workflowType === 'hybrid') {
                dom.film35mmSection.classList.remove('hidden');
            } else {
                dom.film35mmSection.classList.add('hidden');
            }
        }
    }
    
    /**
     * Update project information in the UI
     */
    function updateProjectInfo() {
        const state = FilmNumberCore.getState();
        const dom = getDomElements();
        
        if (!state.analysisResults) {
            return;
        }
        
        // Update project ID
        if (dom.projectId) {
            dom.projectId.textContent = state.projectId || '-';
        }
        
        // Get analysis results
        const analysisResults = state.analysisResults.analysisResults || state.analysisResults;
        
        // Update document count
        if (dom.documentCount) {
            dom.documentCount.textContent = analysisResults.totalDocuments || 
                                            analysisResults.documents?.length || '0';
        }
        
        // Update total pages
        if (dom.totalPages) {
            dom.totalPages.textContent = analysisResults.totalPages || '0';
        }
        
        // Update oversized count
        if (dom.oversizedCount) {
            dom.oversizedCount.textContent = analysisResults.oversizedPages || '0';
        }
    }
    
    /**
     * Update allocation summary from allocation results
     */
    function updateAllocationSummary() {
        const state = FilmNumberCore.getState();
        const dom = getDomElements();
        
        if (!state.allocationResults) {
            return;
        }
        
        // Get the allocation results, handling different structure possibilities
        let allocationResults;
        
        // Handle the specific allocationData structure from your application
        if (state.allocationResults.allocationResults && state.allocationResults.allocationResults.results) {
            // This matches the structure in your sample data
            allocationResults = state.allocationResults.allocationResults.results;
        } else if (state.allocationResults.results) {
            allocationResults = state.allocationResults.results;
        } else {
            allocationResults = state.allocationResults;
        }
        
        console.log('Using allocation results structure:', allocationResults);
        
        // Update 16mm summary
        if (dom.rollCount16mm && allocationResults.total_rolls_16mm !== undefined) {
            dom.rollCount16mm.textContent = allocationResults.total_rolls_16mm;
        }
        
        if (dom.pagesAllocated16mm && allocationResults.total_pages_16mm !== undefined) {
            dom.pagesAllocated16mm.textContent = allocationResults.total_pages_16mm;
        }
        
        if (dom.utilization16mm) {
            const utilization = calculateUtilization(
                allocationResults.total_pages_16mm, 
                allocationResults.total_rolls_16mm,
                FilmNumberCore.CAPACITY_16MM
            );
            dom.utilization16mm.textContent = `${utilization}%`;
        }
        
        // Update 35mm summary if in hybrid mode
        if (state.workflowType === 'hybrid') {
            if (dom.rollCount35mm && allocationResults.total_rolls_35mm !== undefined) {
                dom.rollCount35mm.textContent = allocationResults.total_rolls_35mm;
            }
            
            if (dom.pagesAllocated35mm && allocationResults.total_pages_35mm !== undefined) {
                dom.pagesAllocated35mm.textContent = allocationResults.total_pages_35mm;
            }
            
            if (dom.utilization35mm) {
                const utilization = calculateUtilization(
                    allocationResults.total_pages_35mm,
                    allocationResults.total_rolls_35mm,
                    FilmNumberCore.CAPACITY_35MM
                );
                dom.utilization35mm.textContent = `${utilization}%`;
            }
        }
    }
    
    /**
     * Update film number results in the UI
     */
    function updateFilmNumberResults() {
        const state = FilmNumberCore.getState();
        const dom = getDomElements();
        
        if (!state.filmNumberResults) {
            return;
        }
        
        // Update the allocation summary first
        updateAllocationSummary();
        
        // Clear existing roll displays
        clearRollContainers();
        
        // Update 16mm rolls
        if (state.filmNumberResults.rolls_16mm) {
            renderRolls(state.filmNumberResults.rolls_16mm, '16mm');
        }
        
        // Update 35mm rolls if in hybrid mode
        if (state.workflowType === 'hybrid' && state.filmNumberResults.rolls_35mm) {
            renderRolls(state.filmNumberResults.rolls_35mm, '35mm');
        }
        
        // Update split documents if any
        updateSplitDocuments();
        
        // Update JSON details
        if (dom.filmNumberDetailsJson) {
            dom.filmNumberDetailsJson.textContent = JSON.stringify(state.filmNumberResults, null, 2);
        }
    }
    
    /**
     * Render rolls into their containers
     */
    function renderRolls(rolls, filmType) {
        const dom = getDomElements();
        const container = filmType === '16mm' ? dom.filmRolls16mm : dom.filmRolls35mm;
        
        if (!container) return;
        
        // Clear any existing empty state
        const emptyState = container.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        // For each roll, create a roll card with collapsible document sections
        rolls.forEach(roll => {
            const rollCard = createRollCard(roll, filmType);
            container.appendChild(rollCard);
        });
    }
    
    /**
     * Create a roll card element with collapsible document sections
     */
    function createRollCard(roll, filmType) {
        const rollCard = document.createElement('div');
        rollCard.className = 'roll-card';
        
        // Create header with film number
        const cardHeader = document.createElement('div');
        cardHeader.className = 'roll-card-header';
        
        // Add film number prominently
        const filmNumberEl = document.createElement('div');
        filmNumberEl.className = 'film-number';
        filmNumberEl.innerHTML = `<strong>Film #:</strong> ${roll.film_number || 'Pending'}`;
        cardHeader.appendChild(filmNumberEl);
        
        // Add roll ID and type
        const rollInfoEl = document.createElement('div');
        rollInfoEl.className = 'roll-info';
        rollInfoEl.innerHTML = `<span>Roll ID: ${roll.roll_id}</span> <span>Type: ${filmType}</span>`;
        cardHeader.appendChild(rollInfoEl);
        
        rollCard.appendChild(cardHeader);
        
        // Create usage statistics
        const usageStats = document.createElement('div');
        usageStats.className = 'usage-stats';
        
        // Calculate utilization
        const utilization = Math.round((roll.pages_used / roll.capacity) * 100);
        
        usageStats.innerHTML = `
            <div class="usage-bar">
                <div class="usage-fill" style="width: ${utilization}%"></div>
            </div>
            <div class="usage-text">
                <span>${roll.pages_used} pages used / ${roll.capacity} capacity (${utilization}%)</span>
            </div>
        `;
        
        rollCard.appendChild(usageStats);
        
        // Create document list with collapse functionality
        if (roll.document_segments && roll.document_segments.length > 0) {
            const docsContainer = document.createElement('div');
            docsContainer.className = 'documents-container';
            
            // Create collapsible header
            const docsHeader = document.createElement('div');
            docsHeader.className = 'docs-header';
            docsHeader.innerHTML = `
                <h5>
                    <i class="fas fa-file-alt"></i>
                    Documents (${roll.document_segments.length})
                </h5>
                <span class="toggle-icon">
                    <i class="fas fa-chevron-down"></i>
                </span>
            `;
            docsContainer.appendChild(docsHeader);
            
            // Create content container
            const docsContent = document.createElement('div');
            docsContent.className = 'docs-content';
            
            // Create table for documents
            const docsTable = document.createElement('table');
            docsTable.className = 'docs-table';
            docsTable.innerHTML = `
                <thead>
                    <tr>
                        <th>Doc ID</th>
                        <th>Pages</th>
                        <th>Start Blip</th>
                        <th>End Blip</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            // Add document segments
            roll.document_segments.forEach(segment => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${segment.doc_id || segment.document_id}</td>
                    <td>${segment.pages}</td>
                    <td>${segment.blip || 'Pending'}</td>
                    <td>${segment.blipend || 'Pending'}</td>
                `;
                docsTable.querySelector('tbody').appendChild(row);
            });
            
            docsContent.appendChild(docsTable);
            docsContainer.appendChild(docsContent);
            rollCard.appendChild(docsContainer);
            
            // Add click event for collapsing/expanding
            docsHeader.addEventListener('click', function() {
                // Toggle collapsed class on header
                this.classList.toggle('collapsed');
                
                // Toggle collapsed class on content
                const content = this.nextElementSibling;
                if (content.classList.contains('collapsed')) {
                    content.classList.remove('collapsed');
                    content.style.maxHeight = content.scrollHeight + 'px';
                    // Animate icon
                    const icon = this.querySelector('.toggle-icon i');
                    icon.className = 'fas fa-chevron-down';
                    icon.classList.add('rotate-icon');
                    setTimeout(() => icon.classList.remove('rotate-icon'), 300);
                } else {
                    content.classList.add('collapsed');
                    content.style.maxHeight = '0';
                    // Animate icon
                    const icon = this.querySelector('.toggle-icon i');
                    icon.className = 'fas fa-chevron-right';
                    icon.classList.add('rotate-icon');
                    setTimeout(() => icon.classList.remove('rotate-icon'), 300);
                }
            });
        }
        
        return rollCard;
    }
    
    /**
     * Clear roll containers
     */
    function clearRollContainers() {
        const dom = getDomElements();
        
        // Clear 16mm container
        if (dom.filmRolls16mm) {
            // Keep empty state but hide it
            const emptyState = dom.filmRolls16mm.querySelector('.empty-state');
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            
            // Remove all roll cards
            const cards = dom.filmRolls16mm.querySelectorAll('.roll-card');
            cards.forEach(card => card.remove());
        }
        
        // Clear 35mm container
        if (dom.filmRolls35mm) {
            // Keep empty state but hide it
            const emptyState = dom.filmRolls35mm.querySelector('.empty-state');
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            
            // Remove all roll cards
            const cards = dom.filmRolls35mm.querySelectorAll('.roll-card');
            cards.forEach(card => card.remove());
        }
    }
    
    /**
     * Update split documents display
     */
    function updateSplitDocuments() {
        const state = FilmNumberCore.getState();
        const dom = getDomElements();
        
        if (!state.filmNumberResults || !dom.splitDocumentsPanel || !dom.splitDocumentsTable) {
            return;
        }
        
        // Find split documents (documents that appear in multiple rolls)
        const documentSegments = [];
        
        // Process 16mm segments
        if (state.filmNumberResults.rolls_16mm) {
            state.filmNumberResults.rolls_16mm.forEach(roll => {
                if (roll.document_segments) {
                    roll.document_segments.forEach(segment => {
                        documentSegments.push({
                            doc_id: segment.doc_id || segment.document_id,
                            pages: segment.pages,
                            roll_id: roll.roll_id,
                            film_number: roll.film_number,
                            blip: segment.blip,
                            film_type: '16mm'
                        });
                    });
                }
            });
        }
        
        // Process 35mm segments
        if (state.filmNumberResults.rolls_35mm) {
            state.filmNumberResults.rolls_35mm.forEach(roll => {
                if (roll.document_segments) {
                    roll.document_segments.forEach(segment => {
                        documentSegments.push({
                            doc_id: segment.doc_id || segment.document_id,
                            pages: segment.pages,
                            roll_id: roll.roll_id,
                            film_number: roll.film_number,
                            blip: segment.blip,
                            film_type: '35mm'
                        });
                    });
                }
            });
        }
        
        // Group by document ID
        const docGroups = {};
        documentSegments.forEach(segment => {
            if (!docGroups[segment.doc_id]) {
                docGroups[segment.doc_id] = {
                    doc_id: segment.doc_id,
                    totalPages: 0,
                    segments: []
                };
            }
            
            docGroups[segment.doc_id].segments.push(segment);
            docGroups[segment.doc_id].totalPages += segment.pages;
        });
        
        // Filter to only split documents (more than one segment)
        const splitDocs = Object.values(docGroups).filter(doc => doc.segments.length > 1);
        
        // If we have split documents, show the panel
        if (splitDocs.length > 0) {
            dom.splitDocumentsPanel.classList.remove('hidden');
            
            // Clear the table
            const tbody = dom.splitDocumentsTable.querySelector('tbody');
            if (tbody) {
                tbody.innerHTML = '';
                
                // Add each split document
                splitDocs.forEach(doc => {
                    const row = document.createElement('tr');
                    
                    // Format rolls as comma-separated list
                    const rollsText = doc.segments.map(seg => 
                        `${seg.film_number} (${seg.film_type})`
                    ).join(', ');
                    
                    // Format blips
                    const blipsText = doc.segments.map(seg => 
                        seg.blip || 'Pending'
                    ).join(', ');
                    
                    row.innerHTML = `
                        <td>${doc.doc_id}</td>
                        <td>${doc.totalPages}</td>
                        <td>${doc.segments.length} parts</td>
                        <td>${rollsText}</td>
                        <td>${blipsText}</td>
                    `;
                    
                    tbody.appendChild(row);
                });
                
                // Hide empty state
                const emptyState = dom.splitDocumentsPanel.querySelector('.empty-state');
                if (emptyState) {
                    emptyState.style.display = 'none';
                }
            }
        } else {
            // No split documents, hide the panel
            dom.splitDocumentsPanel.classList.add('hidden');
        }
    }
    
    /**
     * Clear film number results
     */
    function clearFilmNumberResults() {
        // Clear roll containers
        clearRollContainers();
        
        // Hide split documents panel
        const dom = getDomElements();
        if (dom.splitDocumentsPanel) {
            dom.splitDocumentsPanel.classList.add('hidden');
        }
        
        // Clear JSON details
        if (dom.filmNumberDetailsJson) {
            dom.filmNumberDetailsJson.textContent = '{}';
        }
    }
    
    /**
     * Update status badge
     */
    function updateStatusBadge(status, text) {
        const dom = getDomElements();
        if (!dom.statusBadge) return;
        
        // Remove existing status classes
        dom.statusBadge.classList.remove('pending', 'in-progress', 'completed', 'error', 'warning');
        
        // Add new status class
        dom.statusBadge.classList.add(status);
        
        // Update icon
        let icon = 'fa-clock';
        switch (status) {
            case 'in-progress':
                icon = 'fa-spinner fa-spin';
                break;
            case 'completed':
                icon = 'fa-check-circle';
                break;
            case 'error':
                icon = 'fa-exclamation-circle';
                break;
            case 'warning':
                icon = 'fa-exclamation-triangle';
                break;
        }
        
        // Update HTML
        dom.statusBadge.innerHTML = `<i class="fas ${icon}"></i> <span>${text}</span>`;
    }
    
    /**
     * Show progress modal
     */
    function showProgressModal() {
        const dom = getDomElements();
        if (dom.progressModal) {
            dom.progressModal.classList.add('show');
        }
    }
    
    /**
     * Hide progress modal
     */
    function hideProgressModal() {
        const dom = getDomElements();
        if (dom.progressModal) {
            dom.progressModal.classList.remove('show');
        }
    }
    
    /**
     * Update progress bar
     */
    function updateProgress(progress) {
        const dom = getDomElements();
        if (dom.progressBar) {
            dom.progressBar.style.width = `${progress}%`;
            dom.progressBar.setAttribute('aria-valuenow', progress);
        }
    }
    
    /**
     * Update progress text
     */
    function updateProgressText(text) {
        const dom = getDomElements();
        if (dom.progressText) {
            dom.progressText.textContent = text;
        }
    }
    
    /**
     * Show error message
 */
function showError(message) {
        console.error('Film number allocation error:', message);
        
        // Create or update error container
        let errorContainer = document.getElementById('filmnumber-error-container');
        
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'filmnumber-error-container';
            errorContainer.className = 'error-container';
            
            // Insert after status badge
            const dom = getDomElements();
            if (dom.statusBadge && dom.statusBadge.parentNode) {
                dom.statusBadge.parentNode.insertBefore(errorContainer, dom.statusBadge.nextSibling);
            } else {
                // Fallback - insert at the beginning of the component
                const component = document.querySelector('.allocation-component');
                if (component) {
                    component.insertBefore(errorContainer, component.firstChild);
                }
            }
        }
        
        errorContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                ${message}
            </div>
        `;
        
        errorContainer.style.display = 'block';
    }
    
    /**
     * Calculate utilization percentage
     */
    function calculateUtilization(pagesUsed, rollCount, capacity) {
        if (!rollCount || rollCount === 0 || !capacity) return 0;
        
        const totalCapacity = rollCount * capacity;
        return Math.round((pagesUsed / totalCapacity) * 100);
    }
    
    /**
     * Pre-populate UI with allocation data before film numbers are assigned
     */
    function prePopulateFromAllocation() {
        const state = FilmNumberCore.getState();
        const dom = getDomElements();
        
        if (!state.allocationResults) {
            return;
        }
        
        // Update allocation summary
        updateAllocationSummary();
        
        // Clear existing roll displays
        clearRollContainers();
        
        // Get allocation results in the correct structure
        let allocationData;
        if (state.allocationResults.allocationResults && state.allocationResults.allocationResults.results) {
            allocationData = state.allocationResults.allocationResults.results;
        } else if (state.allocationResults.results) {
            allocationData = state.allocationResults.results;
        } else {
            allocationData = state.allocationResults;
        }
        
        console.log('Pre-populating UI with allocation data:', allocationData);
        
        // Display 16mm rolls
        if (allocationData.rolls_16mm && allocationData.rolls_16mm.length > 0) {
            renderPreAllocatedRolls(allocationData.rolls_16mm, '16mm');
        }
        
        // Display 35mm rolls if in hybrid mode
        if (state.workflowType === 'hybrid' && allocationData.rolls_35mm && allocationData.rolls_35mm.length > 0) {
            renderPreAllocatedRolls(allocationData.rolls_35mm, '35mm');
        }
        
        // Update JSON details
        if (dom.filmNumberDetailsJson) {
            dom.filmNumberDetailsJson.textContent = JSON.stringify(allocationData, null, 2);
    }
}

/**
     * Render rolls before film number allocation with collapsible document sections
     */
    function renderPreAllocatedRolls(rolls, filmType) {
        const dom = getDomElements();
        const container = filmType === '16mm' ? dom.filmRolls16mm : dom.filmRolls35mm;
        
        if (!container) return;
        
        // Clear any existing empty state
        const emptyState = container.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        // For each roll, create a roll card without film numbers
        rolls.forEach(roll => {
            const rollCard = document.createElement('div');
            rollCard.className = 'roll-card pre-allocated';
            
            // Create header with placeholder for film number
            const cardHeader = document.createElement('div');
            cardHeader.className = 'roll-card-header';
            
            // Add film number placeholder with "pending" state
            const filmNumberEl = document.createElement('div');
            filmNumberEl.className = 'film-number pending';
            filmNumberEl.innerHTML = `<strong>Film #:</strong> <span class="pending-badge">Pending Allocation</span>`;
            cardHeader.appendChild(filmNumberEl);
            
            // Add roll ID and type
            const rollInfoEl = document.createElement('div');
            rollInfoEl.className = 'roll-info';
            rollInfoEl.innerHTML = `<span>Roll ID: ${roll.roll_id}</span> <span>Type: ${filmType}</span>`;
            cardHeader.appendChild(rollInfoEl);
            
            rollCard.appendChild(cardHeader);
            
            // Create usage statistics
            const usageStats = document.createElement('div');
            usageStats.className = 'usage-stats';
            
            // Calculate utilization
            const capacity = filmType === '16mm' ? FilmNumberCore.CAPACITY_16MM : FilmNumberCore.CAPACITY_35MM;
            const utilization = Math.round((roll.pages_used / capacity) * 100);
            
            usageStats.innerHTML = `
                <div class="usage-bar">
                    <div class="usage-fill" style="width: ${utilization}%"></div>
                </div>
                <div class="usage-text">
                    <span>${roll.pages_used} pages used / ${capacity} capacity (${utilization}%)</span>
                </div>
            `;
            
            rollCard.appendChild(usageStats);
            
            // Create document list with collapsible functionality
            if (roll.document_segments && roll.document_segments.length > 0) {
                const docsContainer = document.createElement('div');
                docsContainer.className = 'documents-container';
                
                // Create collapsible header
                const docsHeader = document.createElement('div');
                docsHeader.className = 'docs-header';
                docsHeader.innerHTML = `
                    <h5>
                        <i class="fas fa-file-alt"></i>
                        Documents (${roll.document_segments.length})
                    </h5>
                    <span class="toggle-icon">
                        <i class="fas fa-chevron-down"></i>
                    </span>
                `;
                docsContainer.appendChild(docsHeader);
                
                // Create content container
                const docsContent = document.createElement('div');
                docsContent.className = 'docs-content';
                
                // Create table for documents - use simpler headers without blip info
                const docsTable = document.createElement('table');
                docsTable.className = 'docs-table';
                docsTable.innerHTML = `
                    <thead>
                        <tr>
                            <th>Doc ID</th>
                            <th>Pages</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                `;
                
                // Add document segments
                roll.document_segments.forEach(segment => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${segment.doc_id}</td>
                        <td>${segment.pages}</td>
                    `;
                    docsTable.querySelector('tbody').appendChild(row);
                });
                
                docsContent.appendChild(docsTable);
                docsContainer.appendChild(docsContent);
                rollCard.appendChild(docsContainer);
                
                // Add click event for collapsing/expanding
                docsHeader.addEventListener('click', function() {
                    // Toggle collapsed class on header
                    this.classList.toggle('collapsed');
                    
                    // Toggle collapsed class on content
                    const content = this.nextElementSibling;
                    if (content.classList.contains('collapsed')) {
                        content.classList.remove('collapsed');
                        content.style.maxHeight = content.scrollHeight + 'px';
                        // Animate icon
                        const icon = this.querySelector('.toggle-icon i');
                        icon.className = 'fas fa-chevron-down';
                        icon.classList.add('rotate-icon');
                        setTimeout(() => icon.classList.remove('rotate-icon'), 300);
                    } else {
                        content.classList.add('collapsed');
                        content.style.maxHeight = '0';
                        // Animate icon
                        const icon = this.querySelector('.toggle-icon i');
                        icon.className = 'fas fa-chevron-right';
                        icon.classList.add('rotate-icon');
                        setTimeout(() => icon.classList.remove('rotate-icon'), 300);
                    }
                });
            }
            
            container.appendChild(rollCard);
        });
    }
    
    /**
     * Initialize index table functionality
     */
    function initIndexTable() {
        const state = FilmNumberCore.getState();
        
        // Try to load index data from localStorage using FilmNumberCore's method
        const indexData = FilmNumberCore.getLocalStorageData('microfilmIndexData');
        if (indexData && indexData.indexData) {
            console.log('Found index data in localStorage:', indexData);
            state.indexData = indexData.indexData;
            
            // Update the initial index table
            updateIndexTable(state.indexData);
        } else {
            console.log('No index data found in localStorage');
            // Show message in the index panel
            const tableBody = document.getElementById('index-table-body');
            if (tableBody) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="5" style="text-align: center; padding: 1rem;">
                        <i class="fas fa-info-circle"></i> No index data available. Please complete the index generation step first.
                    </td>
                `;
                tableBody.appendChild(row);
            }
        }
        
        // Bind events for export buttons
        bindIndexExportEvents();
    }
    
    /**
     * Update the index table with data
     * 
     * @param {Object} indexData - The index data to display
     */
    function updateIndexTable(indexData) {
        const tableBody = document.getElementById('index-table-body');
        if (!tableBody) return;
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Handle different index data formats
        let entries = [];
        if (indexData.index && Array.isArray(indexData.index)) {
            entries = indexData.index;
        } else if (Array.isArray(indexData)) {
            entries = indexData;
        } else {
            console.error('Unknown index data format:', indexData);
            return;
        }
        
        // Helper function for natural sorting of document IDs
        const naturalSort = (a, b) => {
            // Sort by docId (first element in entry array)
            const aId = a[0];
            const bId = b[0];
            
            // Extract numbers from document IDs if present
            const aNum = /^(\d+)/.exec(aId);
            const bNum = /^(\d+)/.exec(bId);
            
            // If both IDs start with numbers, compare them numerically
            if (aNum && bNum) {
                return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
            }
            
            // Otherwise, fall back to standard string comparison
            return aId.localeCompare(bId);
        };
        
        // Sort entries naturally by document ID
        const sortedEntries = [...entries].sort(naturalSort);
        
        // Limit display for performance
        const displayLimit = 100;
        const displayEntries = sortedEntries.slice(0, displayLimit);
        
        // Add rows for each index entry
        displayEntries.forEach(entry => {
            const docId = entry[0];
            const comId = entry[1];
            const initialIndex = entry[2] || [0, 0, 0];
            const finalIndex = entry[3] || 'Pending';
            const docIndex = entry[4] || 1;
            
            const rollId = initialIndex[0];
            const frameStart = initialIndex[1];
            const frameEnd = initialIndex[2];
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${docId}</td>
                <td>${comId}</td>
                <td>${rollId}</td>
                <td>${frameStart}-${frameEnd}</td>
                <td>${finalIndex}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Update table info
        const tableInfo = document.getElementById('table-info');
        if (tableInfo) {
            tableInfo.textContent = `Showing ${displayEntries.length} of ${entries.length} entries`;
        }
    }
    
    /**
     * Update the final index table with film numbers
     */
    function updateFinalIndexTable() {
        const state = FilmNumberCore.getState();
        const tableBody = document.getElementById('final-index-table-body');
        if (!tableBody || !state.indexData) return;
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Clone the index data to avoid modifying the original
        const updatedIndexData = JSON.parse(JSON.stringify(state.indexData));
        
        // Handle different index data formats
        let entries = [];
        if (updatedIndexData.index && Array.isArray(updatedIndexData.index)) {
            entries = updatedIndexData.index;
        } else if (Array.isArray(updatedIndexData)) {
            entries = updatedIndexData;
        } else {
            console.error('Unknown index data format:', updatedIndexData);
            return;
        }
        
        // Update entries with film numbers
        let updatedCount = 0;
        let missingCount = 0;
        
        entries.forEach(entry => {
            // The initialIndex is the 3rd element (index 2) in the entry array
            if (entry[2]) {
                const rollId = entry[2][0];
                
                // Try to find film number for this roll
                let filmNumber = "Not assigned";
                
                // If we have film number results, look up the film number
                if (state.filmNumberResults) {
                    // Check 16mm rolls
                    if (state.filmNumberResults.rolls_16mm) {
                        const roll = state.filmNumberResults.rolls_16mm.find(r => r.roll_id === rollId);
                        if (roll && roll.film_number) {
                            filmNumber = roll.film_number;
                            updatedCount++;
                            
                            // Update the final index (4th element, index 3)
                            // Generate a blip-like format: filmNumber-docIndex.frameStart
                            const docIndex = entry[4] || 1;
                            const frameStart = entry[2][1] || 1;
                            entry[3] = `${filmNumber}-${docIndex.toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`;
                        }
                    }
                    
                    // Check 35mm rolls if film number still not found
                    if (filmNumber === "Not assigned" && state.filmNumberResults.rolls_35mm) {
                        const roll = state.filmNumberResults.rolls_35mm.find(r => r.roll_id === rollId);
                        if (roll && roll.film_number) {
                            filmNumber = roll.film_number;
                            updatedCount++;
                            
                            // Update the final index (4th element, index 3)
                            const docIndex = entry[4] || 1;
                            const frameStart = entry[2][1] || 1;
                            entry[3] = `${filmNumber}-${docIndex.toString().padStart(4, '0')}.${frameStart.toString().padStart(5, '0')}`;
                        }
                    }
                }
                
                if (filmNumber === "Not assigned") {
                    missingCount++;
                }
                
                // Create row
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${entry[0]}</td>
                    <td>${entry[1]}</td>
                    <td>${rollId}</td>
                    <td>${filmNumber}</td>
                    <td>${entry[3] || 'Pending'}</td>
                `;
                
                tableBody.appendChild(row);
            }
        });
        
        // Update statistics
        const totalEntriesEl = document.getElementById('total-entries');
        const updatedEntriesEl = document.getElementById('updated-entries');
        const missingEntriesEl = document.getElementById('missing-entries');
        
        if (totalEntriesEl) {
            totalEntriesEl.textContent = entries.length;
        }
        
        if (updatedEntriesEl) {
            updatedEntriesEl.textContent = updatedCount;
        }
        
        if (missingEntriesEl) {
            missingEntriesEl.textContent = missingCount;
        }
        
        // Show the final index panel
        const finalIndexPanel = document.getElementById('final-index-panel');
        if (finalIndexPanel) {
            finalIndexPanel.classList.remove('hidden');
        }
        
        // Store the updated index data
        state.updatedIndexData = updatedIndexData;
        
        // Save to localStorage
        saveUpdatedIndexToLocalStorage(updatedIndexData);
        
        return updatedIndexData;
    }
    
    /**
     * Save updated index data to localStorage
     */
    function saveUpdatedIndexToLocalStorage(updatedIndexData) {
        try {
            localStorage.setItem('microfilmUpdatedIndexData', JSON.stringify({
                projectId: FilmNumberCore.getState().projectId,
                indexData: updatedIndexData,
                timestamp: new Date().toISOString()
            }));
            console.log('Updated index data saved to localStorage');
        } catch (error) {
            console.error('Error saving updated index data to localStorage:', error);
        }
    }
    
    /**
     * Bind events for index export buttons
     */
    function bindIndexExportEvents() {
        // Bind event for download CSV button
        const downloadCsvBtn = document.getElementById('download-csv');
        if (downloadCsvBtn) {
            downloadCsvBtn.addEventListener('click', function() {
                exportIndexToCsv(false);
            });
        }
        
        // Bind event for download final CSV button
        const downloadFinalCsvBtn = document.getElementById('download-final-csv');
        if (downloadFinalCsvBtn) {
            downloadFinalCsvBtn.addEventListener('click', function() {
                exportIndexToCsv(true);
            });
        }
        
        // Bind event for export JSON button
        const exportJsonBtn = document.getElementById('export-json');
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', function() {
                exportIndexToJson();
            });
        }
    }
    
    /**
     * Export index to CSV
     * 
     * @param {boolean} isFinal - Whether to export the final index
     */
    function exportIndexToCsv(isFinal) {
        const state = FilmNumberCore.getState();
        
        const indexData = isFinal ? state.updatedIndexData : state.indexData;
        
        if (!indexData) {
            showToast('No index data to export', 'error');
            return;
        }
        
        // Generate CSV content from index data
        const csvContent = generateCsvFromIndexData(indexData, isFinal);
        
        // Generate filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `index-${state.projectId}-${isFinal ? 'with-film-numbers' : 'initial'}-${timestamp}.csv`;
        
        // Download the file
        downloadFile(csvContent, filename, 'text/csv');
        
        // Show success message
        showToast('CSV exported successfully', 'success');
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
            ? 'Document ID,COM ID,Roll ID,Film Number,Final Index\n' 
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
            
            // For final index, try to get film number
            let filmNumber = "Not assigned";
            if (isFinal) {
                const state = FilmNumberCore.getState();
                if (state.filmNumberResults) {
                    // Check 16mm rolls
                    if (state.filmNumberResults.rolls_16mm) {
                        const roll = state.filmNumberResults.rolls_16mm.find(r => r.roll_id === rollId);
                        if (roll && roll.film_number) {
                            filmNumber = roll.film_number;
                        }
                    }
                    
                    // Check 35mm rolls if film number still not found
                    if (filmNumber === "Not assigned" && state.filmNumberResults.rolls_35mm) {
                        const roll = state.filmNumberResults.rolls_35mm.find(r => r.roll_id === rollId);
                        if (roll && roll.film_number) {
                            filmNumber = roll.film_number;
                        }
                    }
                }
            }
            
            if (isFinal) {
                csv += `${docId},${comId},${rollId},${filmNumber},${finalIndex}\n`;
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
        const state = FilmNumberCore.getState();
        
        if (!state.updatedIndexData) {
            showToast('No updated index data to export', 'error');
            return;
        }
        
        // Generate filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `index-with-film-numbers-${state.projectId}-${timestamp}.json`;
        
        // Download the file
        const jsonString = JSON.stringify(state.updatedIndexData, null, 2);
        downloadFile(jsonString, filename, 'application/json');
        
        // Show success message
        showToast('JSON exported successfully', 'success');
    }
    
    /**
     * Download a file
     * 
     * @param {string} content - The file content
     * @param {string} filename - The filename
     * @param {string} contentType - The content type
     */
    function downloadFile(content, filename, contentType) {
        const a = document.createElement('a');
        const file = new Blob([content], {type: contentType});
        
        a.href = URL.createObjectURL(file);
        a.download = filename;
        a.click();
        
        URL.revokeObjectURL(a.href);
    }
    
    /**
     * Show a toast message
     * 
     * @param {string} message - Message to display
     * @param {string} type - Type of toast ('info', 'success', 'warning', 'error')
     */
    function showToast(message, type = 'info') {
        // Check if toast container exists, create if not
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Auto-remove after delay
        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // Return public API
    return {
        getDomElements,
        updateWorkflowTypeUI,
        updateProjectInfo,
        updateAllocationSummary,
        updateFilmNumberResults,
        prePopulateFromAllocation,
        clearFilmNumberResults,
        updateStatusBadge,
        showProgressModal,
        hideProgressModal,
        updateProgress,
        updateProgressText,
        showError,
        initIndexTable,
        updateIndexTable,
        updateFinalIndexTable,
        showToast,  // Add the showToast function to the public API
        bindIndexExportEvents,
        exportIndexToCsv,
        exportIndexToJson,
        downloadFile,
        generateCsvFromIndexData
    };
})();

const FilmNumberEvents = (function() {
    /**
     * Bind all event listeners
     */
    function bindEvents() {
        const dom = FilmNumberUI.getDomElements();
        
        // Start film number allocation button
        if (dom.startFilmNumberBtn) {
            dom.startFilmNumberBtn.addEventListener('click', FilmNumberCore.startFilmNumberAllocation);
        }
        
        // Reset button
        if (dom.resetFilmNumberBtn) {
            dom.resetFilmNumberBtn.addEventListener('click', FilmNumberCore.resetFilmNumberAllocation);
        }
        
        // Navigation buttons
        if (dom.backBtn) {
            dom.backBtn.addEventListener('click', navigateToAllocation);
        }
        
        if (dom.toNextStepBtn) {
            dom.toNextStepBtn.addEventListener('click', navigateToNextStep);
        }
        
        // Copy and export buttons
        const copyBtn = document.getElementById('copy-filmnumber-data');
        if (copyBtn) {
            copyBtn.addEventListener('click', copyFilmNumberData);
        }
        
        const exportBtn = document.getElementById('export-filmnumber-data');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportFilmNumberData);
        }
        
        // Add event listeners for index table pagination and filtering
        const searchInput = document.getElementById('index-search');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function() {
                filterIndexTable(this.value);
            }, 300));
        }
        
        // Add event listeners for final index table pagination and filtering
        const finalSearchInput = document.getElementById('final-index-search');
        if (finalSearchInput) {
            finalSearchInput.addEventListener('input', debounce(function() {
                filterFinalIndexTable(this.value);
            }, 300));
    }
}

/**
     * Navigate back to allocation
     */
    function navigateToAllocation() {
        const state = FilmNumberCore.getState();
        window.location.href = `/register/allocation/?id=${state.projectId}&flow=${state.workflowType}`;
    }
    
    /**
     * Navigate to the next step
     */
    function navigateToNextStep() {
        const state = FilmNumberCore.getState();
        window.location.href = `/register/indexgen/?id=${state.projectId}&flow=${state.workflowType}`;
    }
    
    /**
     * Copy film number data to clipboard
     */
    function copyFilmNumberData() {
        const dom = FilmNumberUI.getDomElements();
        if (dom.filmNumberDetailsJson) {
            const text = dom.filmNumberDetailsJson.textContent;
            navigator.clipboard.writeText(text)
                .then(() => {
                    // Show success message
                    const copyBtn = document.getElementById('copy-filmnumber-data');
                    if (copyBtn) {
                        const originalTitle = copyBtn.getAttribute('title');
                        copyBtn.setAttribute('title', 'Copied!');
                        copyBtn.classList.add('success');
                        
                        // Reset after short delay
                        setTimeout(() => {
                            copyBtn.setAttribute('title', originalTitle);
                            copyBtn.classList.remove('success');
                        }, 2000);
                    }
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                });
        }
    }
    
    /**
     * Export film number data as JSON file
     */
    function exportFilmNumberData() {
        const state = FilmNumberCore.getState();
        
        if (!state.filmNumberResults) return;
        
        // Prepare data
        const data = JSON.stringify(state.filmNumberResults, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // Create download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `film_number_allocation_${state.projectId}_${new Date().toISOString().slice(0, 10)}.json`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    }
    
    /**
     * Filter index table based on search term
     * 
     * @param {string} searchTerm - Search term to filter by
     */
    function filterIndexTable(searchTerm) {
        const state = FilmNumberCore.getState();
        if (!state.indexData) return;
        
        const tableBody = document.getElementById('index-table-body');
        if (!tableBody) return;
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Get entries
        let entries = [];
        if (state.indexData.index && Array.isArray(state.indexData.index)) {
            entries = state.indexData.index;
        } else if (Array.isArray(state.indexData)) {
            entries = state.indexData;
        } else {
            console.error('Unknown index data format:', state.indexData);
            return;
        }
        
        // Filter entries if search term provided
        let filteredEntries = entries;
        if (searchTerm && searchTerm.trim() !== '') {
            const term = searchTerm.trim().toLowerCase();
            filteredEntries = entries.filter(entry => {
                // Search in doc ID and COM ID
                const docId = String(entry[0]).toLowerCase();
                const comId = String(entry[1]).toLowerCase();
                
                return docId.includes(term) || comId.includes(term);
            });
        }
        
        // Sort entries by document ID (natural sort)
        const sortedEntries = [...filteredEntries].sort((a, b) => {
            const aId = String(a[0]);
            const bId = String(b[0]);
            
            // Extract numbers from document IDs if present
            const aNum = /^(\d+)/.exec(aId);
            const bNum = /^(\d+)/.exec(bId);
            
            // If both IDs start with numbers, compare them numerically
            if (aNum && bNum) {
                return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
            }
            
            // Otherwise, fall back to standard string comparison
            return aId.localeCompare(bId);
        });
        
        // Limit display for performance
        const displayLimit = 100;
        const displayEntries = sortedEntries.slice(0, displayLimit);
        
        // Add rows for each index entry
        displayEntries.forEach(entry => {
            const docId = entry[0];
            const comId = entry[1];
            const initialIndex = entry[2] || [0, 0, 0];
            const finalIndex = entry[3] || 'Pending';
            
            const rollId = initialIndex[0];
            const frameStart = initialIndex[1];
            const frameEnd = initialIndex[2];
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${docId}</td>
                <td>${comId}</td>
                <td>${rollId}</td>
                <td>${frameStart}-${frameEnd}</td>
                <td>${finalIndex}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Update table info
        const tableInfo = document.getElementById('table-info');
        if (tableInfo) {
            tableInfo.textContent = `Showing ${displayEntries.length} of ${filteredEntries.length} entries`;
        }
    }
    
    /**
     * Filter final index table based on search term
     * 
     * @param {string} searchTerm - Search term to filter by
     */
    function filterFinalIndexTable(searchTerm) {
        const state = FilmNumberCore.getState();
        if (!state.updatedIndexData) return;
        
        const tableBody = document.getElementById('final-index-table-body');
        if (!tableBody) return;
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Get entries
        let entries = [];
        if (state.updatedIndexData.index && Array.isArray(state.updatedIndexData.index)) {
            entries = state.updatedIndexData.index;
        } else if (Array.isArray(state.updatedIndexData)) {
            entries = state.updatedIndexData;
        } else {
            console.error('Unknown index data format:', state.updatedIndexData);
            return;
        }
        
        // Filter entries if search term provided
        let filteredEntries = entries;
        if (searchTerm && searchTerm.trim() !== '') {
            const term = searchTerm.trim().toLowerCase();
            filteredEntries = entries.filter(entry => {
                // Search in doc ID, COM ID, and film number
                const docId = String(entry[0]).toLowerCase();
                const comId = String(entry[1]).toLowerCase();
                const rollId = entry[2] ? String(entry[2][0]).toLowerCase() : '';
                const finalIndex = entry[3] ? String(entry[3]).toLowerCase() : '';
                
                return docId.includes(term) || comId.includes(term) || 
                       rollId.includes(term) || finalIndex.includes(term);
            });
        }
        
        // Sort entries by document ID (natural sort)
        const sortedEntries = [...filteredEntries].sort((a, b) => {
            const aId = String(a[0]);
            const bId = String(b[0]);
            
            // Extract numbers from document IDs if present
            const aNum = /^(\d+)/.exec(aId);
            const bNum = /^(\d+)/.exec(bId);
            
            // If both IDs start with numbers, compare them numerically
            if (aNum && bNum) {
                return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
            }
            
            // Otherwise, fall back to standard string comparison
            return aId.localeCompare(bId);
        });
        
        // Limit display for performance
        const displayLimit = 100;
        const displayEntries = sortedEntries.slice(0, displayLimit);
        
        // Add rows for each index entry
        displayEntries.forEach(entry => {
            // Try to find film number for this roll
            const rollId = entry[2] ? entry[2][0] : null;
            let filmNumber = "Not assigned";
            
            // If we have film number results, look up the film number
            if (state.filmNumberResults && rollId) {
                // Check 16mm rolls
                if (state.filmNumberResults.rolls_16mm) {
                    const roll = state.filmNumberResults.rolls_16mm.find(r => r.roll_id === rollId);
                    if (roll && roll.film_number) {
                        filmNumber = roll.film_number;
                    }
                }
                
                // Check 35mm rolls if film number still not found
                if (filmNumber === "Not assigned" && state.filmNumberResults.rolls_35mm) {
                    const roll = state.filmNumberResults.rolls_35mm.find(r => r.roll_id === rollId);
                    if (roll && roll.film_number) {
                        filmNumber = roll.film_number;
                    }
                }
            }
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry[0]}</td>
                <td>${entry[1]}</td>
                <td>${rollId || '-'}</td>
                <td>${filmNumber}</td>
                <td>${entry[3] || 'Pending'}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Update table info
        const finalTableInfo = document.getElementById('final-table-info');
        if (finalTableInfo) {
            finalTableInfo.textContent = `Showing ${displayEntries.length} of ${filteredEntries.length} entries`;
        }
    }
    
    /**
     * Debounce function to limit how often a function is called
     * 
     * @param {Function} func - Function to debounce
     * @param {number} wait - Milliseconds to wait between calls
     * @returns {Function} - Debounced function
     */
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }
    
    // Return public API
    return {
        bindEvents
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', FilmNumberCore.init);