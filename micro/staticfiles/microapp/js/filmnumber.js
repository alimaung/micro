/**
 * Film Number Allocation JavaScript
 * 
 * This script handles the film number allocation process in the microapp.
 * It manages the UI, API calls, and progress tracking for film number allocation.
 */

// Global variables
let taskId = null;
let statusCheckInterval = null;
let projectId = null;

/**
 * Initialize the film number allocation functionality.
 * 
 * @param {number} projectIdValue - The ID of the project to initialize.
 */
function initFilmNumberAllocation(projectIdValue) {
    projectId = projectIdValue;
    console.log(`Initializing film number allocation for project ${projectId}`);
    
    // Set up event listeners
    document.getElementById('allocateBtn')?.addEventListener('click', startFilmNumberAllocation);
    
    // Check if we have a stored task ID in session storage
    const storedTaskId = sessionStorage.getItem('filmnumberTaskId');
    if (storedTaskId) {
        // Resume status checking for an existing task
        taskId = storedTaskId;
        checkAllocationStatus();
        startStatusCheckInterval();
    }
}

/**
 * Start the film number allocation process.
 */
function startFilmNumberAllocation() {
    if (!projectId) {
        console.error('No project ID provided');
        showError('No project ID provided');
        return;
    }
    
    // Show the progress panel
    const progressPanel = document.getElementById('progressPanel');
    if (progressPanel) {
        progressPanel.style.display = 'block';
    }
    
    // Disable the allocate button
    const allocateBtn = document.getElementById('allocateBtn');
    if (allocateBtn) {
        allocateBtn.disabled = true;
    }
    
    // Get data from localStorage
    const projectData = getLocalStorageData('microfilmProjectState');
    const analysisData = getLocalStorageData('microfilmAnalysisData');
    const allocationData = getLocalStorageData('microfilmAllocationData');
    const indexData = getLocalStorageData('microfilmIndexData');
    
    // Debug logs for data verification
    console.log('DEBUGGING - Data being sent to backend:');
    console.log('Project data:', projectData);
    console.log('Analysis data:', analysisData);
    console.log('Allocation data:', allocationData);
    console.log('Index data:', indexData);
    
    // Send allocation request
    fetch('/api/filmnumber/allocate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            projectId: projectId,
            projectData: projectData,
            analysisData: analysisData,
            allocationData: allocationData,
            indexData: indexData?.indexData || null
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.taskId) {
            taskId = data.taskId;
            sessionStorage.setItem('filmnumberTaskId', taskId);
            updateStatusMessage('Film number allocation started successfully');
            startStatusCheckInterval();
        } else {
            showError('No task ID received from server');
        }
    })
    .catch(error => {
        console.error('Error starting film number allocation:', error);
        showError(`Error starting film number allocation: ${error.message}`);
        enableAllocateButton();
    });
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
 * Start the interval to check allocation status.
 */
function startStatusCheckInterval() {
    // Clear any existing interval
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    // Set up new interval
    statusCheckInterval = setInterval(checkAllocationStatus, 2000); // Check every 2 seconds
}

/**
 * Check the status of the current allocation task.
 */
function checkAllocationStatus() {
    if (!taskId) {
        clearInterval(statusCheckInterval);
        return;
    }
    
    fetch(`/api/filmnumber/status/?taskId=${taskId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        updateProgressBar(data.progress);
        updateStatusMessage(getStatusMessage(data));
        
        if (data.status === 'completed') {
            handleTaskCompletion(data);
        } else if (data.status === 'error') {
            handleTaskError(data);
        } else if (data.status === 'cancelled') {
            handleTaskCancellation();
        }
    })
    .catch(error => {
        console.error('Error checking allocation status:', error);
        showError(`Error checking allocation status: ${error.message}`);
    });
}

/**
 * Update the progress bar with current progress.
 * 
 * @param {number} progress - The progress percentage (0-100).
 */
function updateProgressBar(progress) {
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = `${progress}%`;
    }
}

/**
 * Update the status message.
 * 
 * @param {string} message - The status message to display.
 */
function updateStatusMessage(message) {
    const statusMessage = document.getElementById('statusMessage');
    if (statusMessage) {
        statusMessage.textContent = message;
    }
}

/**
 * Get a human-readable status message based on task data.
 * 
 * @param {Object} data - The task status data.
 * @returns {string} A human-readable status message.
 */
function getStatusMessage(data) {
    switch (data.status) {
        case 'pending':
            return 'Preparing to allocate film numbers...';
        case 'processing':
            if (data.progress < 10) {
                return 'Initializing film number allocation...';
            } else if (data.progress < 50) {
                return 'Processing film rolls...';
            } else if (data.progress < 80) {
                return 'Assigning film numbers...';
            } else {
                return 'Finalizing allocation...';
            }
        case 'completed':
            return 'Film number allocation completed successfully!';
        case 'error':
            return `Error: ${data.errors?.[0] || 'Unknown error'}`;
        case 'cancelled':
            return 'Film number allocation was cancelled.';
        default:
            return 'Processing...';
    }
}

/**
 * Handle the successful completion of a task.
 * 
 * @param {Object} data - The completed task data.
 */
function handleTaskCompletion(data) {
    clearInterval(statusCheckInterval);
    sessionStorage.removeItem('filmnumberTaskId');
    
    // Save updated index data if available
    if (data.results?.index_data) {
        try {
            const indexData = getLocalStorageData('microfilmIndexData') || {};
            indexData.indexData = data.results.index_data;
            indexData.lastUpdated = new Date().toISOString();
            localStorage.setItem('microfilmIndexData', JSON.stringify(indexData));
            console.log('Updated index data saved to localStorage');
        } catch (error) {
            console.error('Error saving updated index data:', error);
        }
    }
    
    // Show success message
    updateStatusMessage('Film number allocation completed successfully!');
    
    // Update UI for completion
    setTimeout(() => {
        // Redirect to results page or reload to show updates
        if (data.results?.project_id) {
            window.location.href = `/filmnumber/results/${data.results.project_id}/`;
        } else {
            window.location.reload();
        }
    }, 2000);
}

/**
 * Handle a task error.
 * 
 * @param {Object} data - The task data with errors.
 */
function handleTaskError(data) {
    clearInterval(statusCheckInterval);
    sessionStorage.removeItem('filmnumberTaskId');
    
    const errorMessage = data.errors?.[0] || 'Unknown error occurred during film number allocation';
    showError(errorMessage);
    enableAllocateButton();
}

/**
 * Handle task cancellation.
 */
function handleTaskCancellation() {
    clearInterval(statusCheckInterval);
    sessionStorage.removeItem('filmnumberTaskId');
    
    updateStatusMessage('Film number allocation was cancelled.');
    enableAllocateButton();
}

/**
 * Show an error message.
 * 
 * @param {string} message - The error message to display.
 */
function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }
    updateStatusMessage(`Error: ${message}`);
}

/**
 * Re-enable the allocate button.
 */
function enableAllocateButton() {
    const allocateBtn = document.getElementById('allocateBtn');
    if (allocateBtn) {
        allocateBtn.disabled = false;
    }
}

// Export functions for external use
window.initFilmNumberAllocation = initFilmNumberAllocation;
window.startFilmNumberAllocation = startFilmNumberAllocation; 