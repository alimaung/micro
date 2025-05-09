/**
 * Events Module - Handles all event binding and user interactions for distribution functionality
 */

const MicroDistributionEvents = (function() {
    'use strict';

    // Private properties
    let config = {
        ui: null,
        core: null,
        api: null
    };

    /**
     * Initialize the events module
     * @param {Object} options - Configuration options
     */
    function init(options = {}) {
        // Merge options with defaults
        config = Object.assign(config, options);
        
        // Bind UI events
        bindEvents();
        
        // Return public interface
        return publicInterface();
    }

    /**
     * Bind all events to UI elements
     */
    function bindEvents() {
        // Distribution controls
        bindDistributionControls();
        
        // Navigation buttons
        bindNavigationButtons();
        
        // Modal events
        bindModalEvents();
        
        // Log filter events
        bindLogFilterEvents();
        
        // Bind output directory button
        bindOutputDirectoryButton();
    }

    /**
     * Bind events for distribution control buttons
     */
    function bindDistributionControls() {
        // Start distribution button
        const startButton = document.querySelector('#start-distribution-btn');
        if (startButton) {
            startButton.addEventListener('click', handleStartDistribution);
        }
        
        // Reset distribution button
        const resetButton = document.querySelector('#reset-distribution-btn');
        if (resetButton) {
            resetButton.addEventListener('click', handleResetDistribution);
        }
        
        // Retry failed items button
        const retryButton = document.querySelector('#retry-failed-btn');
        if (retryButton) {
            retryButton.addEventListener('click', handleRetryFailed);
        }
        
        // Advanced options toggle
        const useRefsCheckbox = document.querySelector('#use-cached-refs');
        if (useRefsCheckbox) {
            useRefsCheckbox.addEventListener('change', () => {
                const isChecked = useRefsCheckbox.checked;
                localStorage.setItem('use_cached_refs', isChecked ? 'true' : 'false');
            });
            
            // Set initial state from localStorage
            useRefsCheckbox.checked = localStorage.getItem('use_cached_refs') === 'true';
        }
    }

    /**
     * Bind events for navigation buttons
     */
    function bindNavigationButtons() {
        // Back button
        const backButton = document.querySelector('#back-to-step-6');
        if (backButton) {
            backButton.addEventListener('click', handleBackNavigation);
        }
        
        // Next button
        const nextButton = document.querySelector('#to-step-8');
        if (nextButton) {
            nextButton.addEventListener('click', handleNextNavigation);
        }
    }

    /**
     * Bind events for modal dialogs
     */
    function bindModalEvents() {
        // Document preview modal
        const previewModal = document.querySelector('#document-preview-modal');
        const closeButton = document.querySelector('#close-preview-modal');
        
        if (previewModal && closeButton) {
            closeButton.addEventListener('click', () => {
                previewModal.style.display = 'none';
            });
            
            // Close when clicking outside the modal
            window.addEventListener('click', (event) => {
                if (event.target === previewModal) {
                    previewModal.style.display = 'none';
                }
            });
        }
    }

    /**
     * Bind events for log filters
     */
    function bindLogFilterEvents() {
        // Log level filter
        const logLevelFilter = document.querySelector('#log-level-filter');
        if (logLevelFilter) {
            logLevelFilter.addEventListener('change', handleLogFilterChange);
        }
        
        // Log search
        const logSearch = document.querySelector('#log-search');
        if (logSearch) {
            logSearch.addEventListener('input', handleLogSearchInput);
        }
        
        // Copy logs button
        const copyLogsButton = document.querySelector('#copy-logs-btn');
        if (copyLogsButton) {
            copyLogsButton.addEventListener('click', handleCopyLogs);
        }
    }

    /**
     * Bind event for the Open Output Directory button
     */
    function bindOutputDirectoryButton() {
        const openOutputDirBtn = document.querySelector('#open-output-directory-btn');
        if (openOutputDirBtn) {
            openOutputDirBtn.addEventListener('click', handleOpenOutputDirectory);
        }
    }

    /**
     * Handle starting the distribution process
     */
    function handleStartDistribution() {
        // Get UI references
        const startButton = document.querySelector('#start-distribution-btn');
        const filmTypeSelect = document.querySelector('#film-type-select');
        const useCachedRefs = document.querySelector('#use-cached-refs');
        
        // Disable buttons during processing
        if (startButton) startButton.disabled = true;
        
        // Update UI to show processing state
        config.ui.setStatusInProgress(0);
        config.ui.addLogEntry('info', 'Starting distribution process...');
        
        // Get core data
        const projectData = config.core.getProjectData();
        const allocationData = config.core.getAllocationData();
        const referenceData = config.core.getReferenceData();
        
        // Get film number data from localStorage
        const filmNumberData = getDataFromLocalStorage('microfilmFilmNumberResults');
        
        // Get distribution options
        const options = {
            film_types: getSelectedFilmTypes(filmTypeSelect),
            use_cached_references: useCachedRefs ? useCachedRefs.checked : false,
            projectData: projectData,
            allocationData: allocationData,
            referenceData: referenceData,
            filmNumberData: filmNumberData
        };
        
        // Verify project ID is valid
        const projectId = config.api.getProjectId();
        if (!projectId) {
            config.ui.addLogEntry('error', 'Invalid project ID. Please reload the page.');
            config.ui.setStatusError();
            if (startButton) startButton.disabled = false;
            return;
        }
        
        config.ui.addLogEntry('info', `Using project ID: ${projectId}`);
        
        // Update distribution state
        config.core.updateDistributionState({
            status: 'in_progress',
            progress: 0,
            startTime: new Date().toISOString(),
            processed: 0,
            errors: []
        });
        
        // Call API to start distribution
        config.ui.addLogEntry('info', `Calling API: distribute/${projectId}/`);
        config.api.startDistribution(options)
            .then(response => {
                console.log('Distribution API response:', response);
                if (response.status === 'success') {
                    handleDistributionSuccess(response.results || response.data);
                } else {
                    handleDistributionError(response.message || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Distribution API error:', error);
                handleDistributionError(error.message || 'API error occurred');
            });
    }

    /**
     * Get data from localStorage and parse it
     * @param {string} key - The localStorage key
     * @returns {Object|null} The parsed data or null if not found
     */
    function getDataFromLocalStorage(key) {
        try {
            const data = localStorage.getItem(key);
            if (!data) {
                console.log(`No data found in localStorage for key: ${key}`);
                return null;
            }
            return JSON.parse(data);
        } catch (error) {
            console.warn(`Error parsing localStorage data for key ${key}:`, error);
            return null;
        }
    }

    /**
     * Handle successful distribution
     * @param {Object} data - Distribution result data
     */
    function handleDistributionSuccess(data) {
        // Log the full response data for debugging
        console.log('Processing distribution success data:', data);
        
        // Save the complete distribution results to localStorage
        saveDistributionResultsToLocalStorage(data);
        
        // Update UI
        config.ui.setStatusCompleted();
        config.ui.addLogEntry('success', 'Distribution completed successfully');
        config.ui.updateRollTables();
        config.ui.updateDistributionResults(data);
        config.ui.enableNextButton();
        
        // Re-enable start button
        const startButton = document.querySelector('#start-distribution-btn');
        if (startButton) startButton.disabled = false;
        
        // Update distribution state
        config.core.updateDistributionState({
            status: 'completed',
            progress: 100,
            endTime: new Date().toISOString(),
            distributionResults: data
        });
    }
    
    /**
     * Save distribution results to localStorage for page reconstruction
     * @param {Object} data - Distribution result data from server
     */
    function saveDistributionResultsToLocalStorage(data) {
        try {
            const distributionResults = {
                results: data,
                projectId: config.api.getProjectId(),
                timestamp: new Date().toISOString(),
                status: 'completed'
            };
            
            localStorage.setItem('microfilmDistributionResults', JSON.stringify(distributionResults));
            console.log('Distribution results saved to localStorage');
        } catch (error) {
            console.error('Error saving distribution results to localStorage:', error);
        }
    }

    /**
     * Handle distribution error
     * @param {String} errorMessage - Error message
     */
    function handleDistributionError(errorMessage) {
        // Update UI
        config.ui.setStatusError();
        config.ui.addLogEntry('error', `Distribution failed: ${errorMessage}`);
        
        // Re-enable start button
        const startButton = document.querySelector('#start-distribution-btn');
        if (startButton) startButton.disabled = false;
        
        // Update distribution state
        config.core.updateDistributionState({
            status: 'error',
            endTime: new Date().toISOString()
        });
        
        // Add error to core
        config.core.addError({
            time: new Date().toISOString(),
            message: errorMessage
        });
    }

    /**
     * Handle reset distribution button click
     */
    function handleResetDistribution() {
        if (!confirm('Are you sure you want to reset the distribution? This will clear all progress.')) {
            return;
        }
        
        config.ui.addLogEntry('info', 'Resetting distribution...');
        
        // Call API to reset distribution
        config.api.resetDistribution()
            .then(response => {
                if (response.status === 'success') {
                    // Reset local state
                    config.core.resetDistributionState();
                    config.core.clearSavedState();
                    
                    // Update UI
                    config.ui.setStatusNotStarted();
                    config.ui.addLogEntry('info', 'Distribution has been reset');
                    config.ui.updateRollTables();
                    
                    // Reload data
                    location.reload();
                } else {
                    config.ui.addLogEntry('error', `Failed to reset: ${response.message}`);
                }
            })
            .catch(error => {
                config.ui.addLogEntry('error', `Error resetting distribution: ${error.message}`);
            });
    }

    /**
     * Handle retry failed items button click
     */
    function handleRetryFailed() {
        // This would be implemented to retry documents that failed distribution
        config.ui.addLogEntry('info', 'Retrying failed items...');
        
        // Get errors from core
        const errors = config.core.getErrors();
        if (!errors || !errors.length) {
            config.ui.addLogEntry('info', 'No failed items to retry');
            return;
        }
        
        // This would handle retrying logic using the API
        // For now, just log it
        config.ui.addLogEntry('info', `Found ${errors.length} items to retry`);
    }

    /**
     * Handle back navigation button click
     */
    function handleBackNavigation() {
        // Get current URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const flowType = urlParams.get('flow') || '';
        const projectId = urlParams.get('id') || '';
        const mode = urlParams.get('mode') || '';
        const step = urlParams.get('step') || '';
        
        // Build URL parameters string
        let paramsString = '';
        if (flowType || projectId || mode || step) {
            paramsString = '?';
            const params = [];
            
            if (flowType) params.push(`flow=${flowType}`);
            if (projectId) params.push(`id=${projectId}`);
            if (mode) params.push(`mode=${mode}`);
            if (step) params.push(`step=${step}`);
            
            paramsString += params.join('&');
        }
        
        // Navigate to references page with parameters
        window.location.href = `/register/references${paramsString}`;
    }

    /**
     * Handle next navigation button click
     */
    function handleNextNavigation() {
        // Get current URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const flowType = urlParams.get('flow') || '';
        const projectId = urlParams.get('id') || '';
        const mode = urlParams.get('mode') || '';
        const step = urlParams.get('step') || '';
        
        // Build URL parameters string
        let paramsString = '';
        if (flowType || projectId || mode || step) {
            paramsString = '?';
            const params = [];
            
            if (flowType) params.push(`flow=${flowType}`);
            if (projectId) params.push(`id=${projectId}`);
            if (mode) params.push(`mode=${mode}`);
            if (step) params.push(`step=${step}`);
            
            paramsString += params.join('&');
        }
        
        // Navigate to export page with parameters
        window.location.href = `/register/export${paramsString}`;
    }

    /**
     * Handle log filter change
     */
    function handleLogFilterChange() {
        const filterSelect = document.querySelector('#log-level-filter');
        const selectedLevel = filterSelect ? filterSelect.value : 'all';
        
        const logEntries = document.querySelectorAll('.log-entry');
        logEntries.forEach(entry => {
            if (selectedLevel === 'all' || entry.classList.contains(selectedLevel)) {
                entry.style.display = '';
            } else {
                entry.style.display = 'none';
            }
        });
    }

    /**
     * Handle log search input
     */
    function handleLogSearchInput() {
        const searchInput = document.querySelector('#log-search');
        const searchText = searchInput ? searchInput.value.toLowerCase() : '';
        
        const logEntries = document.querySelectorAll('.log-entry');
        logEntries.forEach(entry => {
            const messageText = entry.textContent.toLowerCase();
            if (messageText.includes(searchText)) {
                entry.style.display = '';
            } else {
                entry.style.display = 'none';
            }
        });
    }

    /**
     * Handle copy logs button click
     */
    function handleCopyLogs() {
        const logContainer = document.querySelector('#distribution-logs-container');
        if (!logContainer) return;
        
        const logText = Array.from(logContainer.querySelectorAll('.log-entry'))
            .map(entry => entry.textContent)
            .join('\n');
        
        navigator.clipboard.writeText(logText)
            .then(() => {
                config.ui.addLogEntry('info', 'Logs copied to clipboard');
            })
            .catch(err => {
                config.ui.addLogEntry('error', 'Failed to copy logs: ' + err.message);
            });
    }

    /**
     * Handle opening the output directory in file explorer
     */
    function handleOpenOutputDirectory() {
        const outputPath = document.querySelector('#output-directory-path').textContent;
        
        if (!outputPath || outputPath.trim() === '') {
            config.ui.addLogEntry('warning', 'No output directory available.');
            return;
        }
        
        config.ui.addLogEntry('info', `Opening output directory: ${outputPath}`);
        
        // Call the reveal_in_explorer API endpoint
        const formData = new FormData();
        formData.append('path', outputPath);
        
        fetch('/reveal-in-explorer/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                config.ui.addLogEntry('success', 'Output directory opened in explorer');
            } else {
                config.ui.addLogEntry('error', `Failed to open directory: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            config.ui.addLogEntry('error', `Error opening directory: ${error.message}`);
        });
    }

    /**
     * Helper function to get CSRF token
     */
    function getCsrfToken() {
        const csrfCookie = document.cookie.match(/csrftoken=([^;]+)/);
        return csrfCookie ? csrfCookie[1] : '';
    }

    /**
     * Get selected film types from the select element
     * @param {HTMLSelectElement} select - Film type select element
     * @returns {Array} Array of selected film types
     */
    function getSelectedFilmTypes(select) {
        if (!select) return ['16mm', '35mm'];
        
        const value = select.value;
        if (value === 'both') return ['16mm', '35mm'];
        if (value === '16mm') return ['16mm'];
        if (value === '35mm') return ['35mm'];
        
        return ['16mm', '35mm']; // Default
    }

    /**
     * Public interface exposed by this module
     */
    function publicInterface() {
        return {
            init,
            handleStartDistribution,
            handleResetDistribution,
            handleRetryFailed,
            bindEvents
        };
    }

    // Return public interface
    return {
        init: init
    };
})();