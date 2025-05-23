/**
 * Distribution Module - Main entry point for the Document Distribution functionality
 * Uses modular architecture with core, events, api, and ui sub-modules
 */

const MicroDistribution = (function() {
    'use strict';

    // Private module references
    let core;
    let events;
    let api;
    let ui;

    /**
     * Initialize the distribution module and its components
     * @param {Object} config - Configuration options
     */
    function init(config = {}) {
        // Get project ID from URL or config
        const projectId = config.projectId || getProjectIdFromUrl();
        
        // Log project ID for debugging
        console.log('Initializing distribution with project ID:', projectId);
        
        // Initialize sub-modules
        core = MicroDistributionCore.init({
            projectId: projectId,
            storagePrefix: 'micro_distribution_'
        });

        api = MicroDistributionAPI.init({
            baseUrl: config.baseUrl || '/api/distribution/',
            projectId: projectId
        });

        ui = MicroDistributionUI.init({
            selectors: {
                container: '#step-7',
                statusIndicator: '#distribution-status-indicator',
                progressBar: '#distribution-progress-bar',
                progressStatus: '#distribution-progress-status',
                startButton: '#start-distribution-btn',
                resetButton: '#reset-distribution-btn',
                backButton: '#back-to-step-6',
                nextButton: '#to-step-8',
                roll16mmTable: '#rolls-16mm-table-body',
                roll35mmTable: '#rolls-35mm-table-body',
                logContainer: '#distribution-logs-container',
                errorList: '#error-list'
            },
            core: core
        });

        events = MicroDistributionEvents.init({
            ui: ui,
            core: core,
            api: api
        });

        // Give a small delay to ensure all modules are fully initialized
        setTimeout(() => {
            // Load data and check if we have saved distribution results
            console.log('Checking for saved distribution results...');
            loadData()
                .then(loaded => {
                    if (loaded) {
                        console.log('Distribution data loaded successfully');
                    } else {
                        console.warn('Could not load all distribution data');
                    }
                })
                .catch(error => {
                    console.error('Error loading distribution data:', error);
                });
        }, 100);

        // Return public interface
        return publicInterface();
    }

    /**
     * Load initial data needed for the distribution page
     */
    function loadInitialData() {
        // Show loading state
        ui.setStatusLoading();

        // Check if we have saved state first
        if (core.hasSavedState()) {
            core.loadSavedState();
            ui.refreshAllViews();
            checkDistributionStatus();
            return;
        }

        // Otherwise load fresh data through loadData
        loadData()
            .then(loaded => {
                if (loaded) {
                    ui.addLogEntry('info', 'Distribution data loaded successfully');
                } else {
                    ui.addLogEntry('warning', 'Could not load all distribution data');
                }
            })
            .catch(error => {
                console.error('Error in loadInitialData:', error);
                ui.setStatusError();
                ui.addLogEntry('error', `Error loading distribution data: ${error.message}`);
            });
    }

    /**
     * Check the current status of distribution process
     */
    function checkDistributionStatus() {
        const distributionState = core.getDistributionState();
        
        if (distributionState.status === 'completed') {
            ui.setStatusCompleted();
            ui.enableNextButton();
        } else if (distributionState.status === 'in_progress') {
            ui.setStatusInProgress(distributionState.progress);
        } else if (distributionState.status === 'error') {
            ui.setStatusError();
        } else {
            ui.setStatusNotStarted();
        }
    }

    /**
     * Extract project ID from the URL
     * @returns {Number} Project ID
     */
    function getProjectIdFromUrl() {
        // First try to get id from query parameters
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('id')) {
            return parseInt(urlParams.get('id'), 10);
        }
        
        // Fall back to path-based structure if id parameter is not present
        const pathParts = window.location.pathname.split('/');
        for (let i = 0; i < pathParts.length; i++) {
            if (pathParts[i] === 'project' && i + 1 < pathParts.length) {
                return parseInt(pathParts[i + 1], 10);
            }
        }
        
        // Fallback if not found in URL or query parameters
        const projectIdElement = document.getElementById('project-id');
        if (projectIdElement && projectIdElement.textContent) {
            return parseInt(projectIdElement.textContent, 10);
        }
        
        console.error('Could not determine project ID from URL or DOM');
        return null;
    }

    /**
     * Public interface exposed by this module
     */
    function publicInterface() {
        return {
            init: init,
            refreshData: loadInitialData,
            startDistribution: () => events.handleStartDistribution(),
            resetDistribution: () => events.handleResetDistribution(),
            getCore: () => core,
            getUI: () => ui,
            getAPI: () => api,
            loadData: loadData
        };
    }

    /**
     * Load data from local storage
     * @returns {Promise<boolean>} Promise resolving to whether data was successfully loaded
     */
    function loadDataFromJsonFiles() {
        return new Promise((resolve, reject) => {
            try {
                // Get data from localStorage instead of fetching from URLs
                const projectState = getDataFromLocalStorage('microfilmProjectState');
                const allocationData = getDataFromLocalStorage('microfilmAllocationData');
                const referenceSheets = getDataFromLocalStorage('microfilmReferenceSheets');
                const filmNumberResults = getDataFromLocalStorage('microfilmFilmNumberResults');
                
                // Check if we have the minimum required data
                if (!projectState || !allocationData) {
                    console.log('Required data missing from localStorage');
                    resolve(false);
                    return;
                }
                
                // Process and set the data
                processLoadedJsonData(projectState, allocationData, referenceSheets, filmNumberResults);
                resolve(true);
            } catch (error) {
                console.error('Error loading data from localStorage:', error);
                resolve(false);
            }
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
     * Process the loaded data from localStorage and set it in the core module
     * @param {Object} projectState - Project state data
     * @param {Object} allocationData - Allocation data
     * @param {Object} referenceSheets - Reference sheets data
     * @param {Object} filmNumberResults - Film number results data
     */
    function processLoadedJsonData(projectState, allocationData, referenceSheets, filmNumberResults) {
        // Create project data from project state
        const projectData = {
            id: projectState.projectId,
            archive_id: projectState.projectInfo ? projectState.projectInfo.archiveId : '',
            location: projectState.projectInfo ? projectState.projectInfo.location : '',
            document_type: projectState.projectInfo ? projectState.projectInfo.documentType : '',
            total_documents: allocationData.allocationResults ? allocationData.allocationResults.documentCount : 0,
            total_pages: allocationData.allocationResults ? allocationData.allocationResults.totalPages : 0,
            has_oversized_documents: allocationData.allocationResults ? allocationData.allocationResults.hasOversized : false,
            oversized_count: allocationData.allocationResults ? allocationData.allocationResults.documentsWithOversized || 0 : 0
        };
        
        // Process film allocation data
        const processedAllocationData = {
            rolls_16mm_count: 0,
            rolls_35mm_count: 0,
            reference_sheets_count: 0,
            documents: [],
            rolls: []
        };

        // Add allocation data if available
        if (allocationData.allocationResults && allocationData.allocationResults.results) {
            const allocResults = allocationData.allocationResults.results;
            processedAllocationData.rolls_16mm_count = allocResults.rolls_16mm ? allocResults.rolls_16mm.length : 0;
            processedAllocationData.rolls_35mm_count = allocResults.rolls_35mm ? allocResults.rolls_35mm.length : 0;
        }

        // Add reference sheets count if available
        if (referenceSheets) {
            processedAllocationData.reference_sheets_count = 
                referenceSheets.sheets_created || 
                (referenceSheets.reference_sheets ? Object.keys(referenceSheets.reference_sheets).length : 0);
        }

        // Process roll information from film number results if available
        let rolls = [];
        if (filmNumberResults && filmNumberResults.results) {
            // Process 16mm rolls
            if (filmNumberResults.results.rolls_16mm) {
                const rolls16mm = filmNumberResults.results.rolls_16mm.map(roll => ({
                    id: roll.roll_id,
                    film_type: '16mm',
                    film_number: roll.film_number,
                    capacity: roll.capacity,
                    page_count: roll.pages_used,
                    document_count: roll.document_segments ? roll.document_segments.length : 0,
                    status: 'pending'
                }));
                rolls = rolls.concat(rolls16mm);
            }

            // Process 35mm rolls
            if (filmNumberResults.results.rolls_35mm) {
                const rolls35mm = filmNumberResults.results.rolls_35mm.map(roll => ({
                    id: roll.roll_id === 'None' ? `35mm-${roll.film_number}` : roll.roll_id,
                    film_type: '35mm',
                    film_number: roll.film_number,
                    capacity: roll.capacity,
                    page_count: roll.pages_used,
                    document_count: roll.document_segments ? roll.document_segments.length : 0,
                    status: 'pending'
                }));
                rolls = rolls.concat(rolls35mm);
            }
        } else if (allocationData.allocationResults && allocationData.allocationResults.results) {
            // Fallback to allocation data if film number results not available
            const allocResults = allocationData.allocationResults.results;
            
            if (allocResults.rolls_16mm) {
                const rolls16mm = allocResults.rolls_16mm.map(roll => ({
                    id: roll.roll_id,
                    film_type: '16mm',
                    film_number: roll.film_number || `16mm-Roll-${roll.roll_id}`,
                    capacity: roll.capacity,
                    page_count: roll.pages_used,
                    document_count: roll.document_segments ? roll.document_segments.length : 0,
                    status: 'pending'
                }));
                rolls = rolls.concat(rolls16mm);
            }

            if (allocResults.rolls_35mm) {
                const rolls35mm = allocResults.rolls_35mm.map(roll => ({
                    id: roll.roll_id,
                    film_type: '35mm',
                    film_number: roll.film_number || `35mm-Roll-${roll.roll_id}`,
                    capacity: roll.capacity,
                    page_count: roll.pages_used,
                    document_count: roll.document_segments ? roll.document_segments.length : 0,
                    status: 'pending'
                }));
                rolls = rolls.concat(rolls35mm);
            }
        }

        processedAllocationData.rolls = rolls;

        // Create reference data from reference sheets data
        const referenceData = referenceSheets ? {
            sheets_created: referenceSheets.sheets_created || 0,
            reference_sheets: referenceSheets.reference_sheets || {},
            documents_details: referenceSheets.documents_details || {}
        } : null;
        console.log("<<<REFERENCE DATA>>>:", referenceData )
        // Set all the processed data in the core module
        core.setProjectData(projectData);
        core.setAllocationData(processedAllocationData);
        if (referenceData) {
            core.setReferenceData(referenceData);
        }

        // Set distribution state based on allocation status
        const distributionStatus = allocationData.allocationResults ? allocationData.allocationResults.status : 'not_started';
        if (distributionStatus === 'completed') {
            core.updateDistributionState({
                status: 'not_started',
                total: projectData.total_documents || 0
            });
        }
        
        console.log('Processed data from localStorage', { projectData, processedAllocationData, referenceData });
    }

    /**
     * Load all data needed for the distribution page
     * @returns {Promise} Promise that resolves when data is loaded
     */
    function loadData() {
        // Show loading state if UI is initialized
        try {
            // Only call setStatusLoading if ui is initialized and the function exists
            if (ui && typeof ui.setStatusLoading === 'function') {
                ui.setStatusLoading();
            } else {
                console.log('UI not fully initialized, skipping setStatusLoading');
            }
        } catch (e) {
            console.warn('Error setting loading status:', e);
        }

        // First check if we have completed distribution results saved
        const savedResults = getSavedDistributionResults();
        if (savedResults && savedResults.status === 'completed') {
            try {
                if (ui) {
                    ui.addLogEntry('info', 'Loading saved distribution results from previous session');
                    
                    // Update UI to reflect completed state
                    ui.setStatusCompleted();
                    ui.updateDistributionResults(savedResults.results);
                    ui.enableNextButton();
                }
                
                // Update distribution state
                core.updateDistributionState({
                    status: 'completed',
                    progress: 100,
                    distributionResults: savedResults.results
                });
                
                // Also load data from JSON files to populate other UI elements
                return loadDataFromJsonFiles()
                    .then(() => {
                        if (ui && typeof ui.refreshAllViews === 'function') {
                            ui.refreshAllViews();
                        }
                        return Promise.resolve(true);
                    });
            } catch (e) {
                console.error('Error restoring saved distribution results:', e);
            }
        }

        // If no saved results, check if we have saved state
        if (core.hasSavedState()) {
            core.loadSavedState();
            if (ui && typeof ui.refreshAllViews === 'function') {
                ui.refreshAllViews();
            }
            checkDistributionStatus();
            return Promise.resolve(true);
        }

        // Otherwise load fresh data from API
        return api.getDistributionStatus()
            .then(response => {
                if (response.status === 'success') {
                    if (response.distributionComplete) {
                        // Distribution is already complete
                        if (ui) {
                            ui.setStatusCompleted();
                            ui.updateDistributionResults(response.results);
                            ui.enableNextButton();
                        }
                        
                        // Update distribution state
                        core.updateDistributionState({
                            status: 'completed',
                            progress: 100,
                            distributionResults: response.results
                        });
                        
                        // Save to localStorage for future page loads
                        saveDistributionResultsToLocalStorage(response.results);
                    } else {
                        // Distribution not started yet
                        if (ui && typeof ui.setStatusNotStarted === 'function') {
                            ui.setStatusNotStarted();
                        }
                    }
                    return true;
                } else {
                    if (ui && typeof ui.addLogEntry === 'function') {
                        ui.addLogEntry('error', response.message || 'Failed to get distribution status');
                    }
                    return false;
                }
            })
            .catch(error => {
                if (ui && typeof ui.addLogEntry === 'function') {
                    ui.addLogEntry('error', `Error loading distribution status: ${error.message}`);
                }
                return false;
            })
            .finally(() => {
                return loadDataFromJsonFiles();
            });
    }
    
    /**
     * Get saved distribution results from localStorage
     * @returns {Object|null} Saved distribution results or null if not found
     */
    function getSavedDistributionResults() {
        try {
            const savedResults = localStorage.getItem('microfilmDistributionResults');
            if (!savedResults) {
                console.log('No saved distribution results found in localStorage');
                return null;
            }
            
            const results = JSON.parse(savedResults);
            console.log('Found saved distribution results:', results);
            
            // Check if the results are for the current project
            const currentProjectId = getProjectIdFromUrl();
            if (results.projectId !== currentProjectId) {
                console.log(`Results are for project ${results.projectId}, but current project is ${currentProjectId}`);
                return null;
            }
            
            return results;
        } catch (error) {
            console.error('Error loading saved distribution results:', error);
            return null;
        }
    }
    
    /**
     * Save distribution results to localStorage for page reconstruction
     * @param {Object} data - Distribution result data from server
     */
    function saveDistributionResultsToLocalStorage(data) {
        try {
            const distributionResults = {
                results: data,
                projectId: getProjectIdFromUrl(),
                timestamp: new Date().toISOString(),
                status: 'completed'
            };
            
            localStorage.setItem('microfilmDistributionResults', JSON.stringify(distributionResults));
            console.log('Distribution results saved to localStorage');
        } catch (error) {
            console.error('Error saving distribution results to localStorage:', error);
        }
    }

    // Return public interface
    return {
        init: init
    };
})();

// Initialize the distribution module when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the distribution module
    window.microDistribution = MicroDistribution.init();
});
