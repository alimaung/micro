/**
 * UI Module - Handles all DOM manipulation and UI updates for distribution functionality
 */

const MicroDistributionUI = (function() {
    'use strict';

    // Private properties
    let config = {
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
            errorList: '#error-list',
            projectInfoFields: {
                projectId: '#project-id',
                archiveId: '#archive-id',
                location: '#location',
                documentType: '#document-type',
                totalDocuments: '#total-documents',
                totalPages: '#total-pages',
                hasOversized: '#has-oversized',
                oversizedDocuments: '#oversized-documents',
                rolls16mm: '#rolls-16mm',
                rolls35mm: '#rolls-35mm',
                referenceSheets: '#reference-sheets'
            }
        },
        core: null
    };

    // Element references
    let elements = {};

    /**
     * Initialize the UI module
     * @param {Object} options - Configuration options
     */
    function init(options = {}) {
        // Set default selectors if not provided
        if (!options.selectors) {
            options.selectors = {};
        }
        
        // Ensure projectInfoFields exists
        if (!options.selectors.projectInfoFields) {
            options.selectors.projectInfoFields = {
                projectId: '#project-id',
                archiveId: '#archive-id',
                location: '#location',
                documentType: '#document-type',
                totalDocuments: '#total-documents',
                totalPages: '#total-pages',
                hasOversized: '#has-oversized',
                oversizedDocuments: '#oversized-documents',
                rolls16mm: '#rolls-16mm',
                rolls35mm: '#rolls-35mm',
                referenceSheets: '#reference-sheets'
            };
        }
        
        // Merge options with defaults
        config = Object.assign(config, options);
        
        // Cache DOM elements
        cacheElements();
        
        // Set up initial UI state
        setupInitialState();
        
        // Return public interface
        return publicInterface();
    }

    /**
     * Cache DOM elements for better performance
     */
    function cacheElements() {
        elements.container = document.querySelector(config.selectors.container);
        elements.statusIndicator = document.querySelector(config.selectors.statusIndicator);
        elements.progressBar = document.querySelector(config.selectors.progressBar);
        elements.progressStatus = document.querySelector(config.selectors.progressStatus);
        elements.startButton = document.querySelector(config.selectors.startButton);
        elements.resetButton = document.querySelector(config.selectors.resetButton);
        elements.backButton = document.querySelector(config.selectors.backButton);
        elements.nextButton = document.querySelector(config.selectors.nextButton);
        elements.roll16mmTable = document.querySelector(config.selectors.roll16mmTable);
        elements.roll35mmTable = document.querySelector(config.selectors.roll35mmTable);
        elements.logContainer = document.querySelector(config.selectors.logContainer);
        elements.errorList = document.querySelector(config.selectors.errorList);
        
        // Cache project info fields
        elements.projectInfo = {};
        Object.keys(config.selectors.projectInfoFields).forEach(key => {
            elements.projectInfo[key] = document.querySelector(config.selectors.projectInfoFields[key]);
        });
    }

    /**
     * Set up initial UI state
     */
    function setupInitialState() {
        // Set status to "Not Started"
        setStatusNotStarted();
        
        // Enable distribution controls initially (changed from disable)
        enableDistributionControls();
        
        // Make collapsible panels work
        setupCollapsiblePanels();
        
        // Setup advanced options toggle
        setupAdvancedOptionsToggle();
    }

    /**
     * Setup collapsible panels
     */
    function setupCollapsiblePanels() {
        const collapsibleHeaders = document.querySelectorAll('.panel-header.collapsible');
        collapsibleHeaders.forEach(header => {
            header.addEventListener('click', () => {
                header.classList.toggle('collapsed');
                const content = header.nextElementSibling;
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        });
    }

    /**
     * Setup advanced options toggle
     */
    function setupAdvancedOptionsToggle() {
        const advancedToggle = document.getElementById('show-advanced-options');
        const advancedContent = document.getElementById('advanced-options-content');
        
        if (advancedToggle && advancedContent) {
            advancedToggle.addEventListener('change', () => {
                advancedContent.classList.toggle('visible', advancedToggle.checked);
            });
        }
    }

    /**
     * Update the project info panel with data from core
     */
    function updateProjectInfoPanel() {
        const projectData = config.core.getProjectData();
        const allocationData = config.core.getAllocationData();
        
        if (!projectData) return;
        
        // Update project info fields
        if (elements.projectInfo.projectId) {
            elements.projectInfo.projectId.textContent = projectData.id || '';
        }
        
        if (elements.projectInfo.archiveId) {
            elements.projectInfo.archiveId.textContent = projectData.archive_id || '';
        }
        
        if (elements.projectInfo.location) {
            elements.projectInfo.location.textContent = projectData.location || '';
        }
        
        if (elements.projectInfo.documentType) {
            elements.projectInfo.documentType.textContent = projectData.document_type || '';
        }
        
        if (elements.projectInfo.totalDocuments) {
            elements.projectInfo.totalDocuments.textContent = projectData.total_documents || '0';
        }
        
        if (elements.projectInfo.totalPages) {
            elements.projectInfo.totalPages.textContent = projectData.total_pages || '0';
        }
        
        // Handle oversized documents visibility
        const hasOversized = !!projectData.has_oversized_documents;
        if (elements.projectInfo.hasOversized) {
            elements.projectInfo.hasOversized.textContent = hasOversized ? 'Yes' : 'No';
        }
        
        const oversizedRow = document.getElementById('oversized-doc-row');
        if (oversizedRow) {
            oversizedRow.style.display = hasOversized ? 'flex' : 'none';
        }
        
        if (hasOversized && elements.projectInfo.oversizedDocuments) {
            elements.projectInfo.oversizedDocuments.textContent = projectData.oversized_count || '0';
        }
        
        // Update allocation summary
        if (allocationData) {
            if (elements.projectInfo.rolls16mm) {
                elements.projectInfo.rolls16mm.textContent = allocationData.rolls_16mm_count || '0';
            }
            
            if (elements.projectInfo.rolls35mm) {
                elements.projectInfo.rolls35mm.textContent = allocationData.rolls_35mm_count || '0';
            }
            
            if (elements.projectInfo.referenceSheets) {
                elements.projectInfo.referenceSheets.textContent = allocationData.reference_sheets_count || '0';
            }
        }
    }

    /**
     * Update the distribution status display
     * @param {Object} status - Status object from API
     */
    function updateDistributionStatus(status) {
        if (!status) return;
        
        if (status.is_completed) {
            setStatusCompleted();
            enableNextButton();
        } else if (status.is_in_progress) {
            setStatusInProgress(status.progress || 0);
        } else if (status.has_error) {
            setStatusError();
        } else {
            setStatusNotStarted();
        }
    }

    /**
     * Set status indicator to "Not Started"
     */
    function setStatusNotStarted() {
        if (elements.statusIndicator) {
            const badge = elements.statusIndicator.querySelector('.status-badge');
            if (badge) {
                badge.className = 'status-badge not-started';
                badge.textContent = 'Not Started';
            }
        }
    }

    /**
     * Set status indicator to "Loading"
     */
    function setStatusLoading() {
        if (elements.statusIndicator) {
            const badge = elements.statusIndicator.querySelector('.status-badge');
            if (badge) {
                badge.className = 'status-badge in-progress';
                badge.textContent = 'Loading...';
            }
        }
    }

    /**
     * Set status indicator to "In Progress" with progress percentage
     * @param {Number} progress - Progress percentage (0-100)
     */
    function setStatusInProgress(progress) {
        if (elements.statusIndicator) {
            const badge = elements.statusIndicator.querySelector('.status-badge');
            if (badge) {
                badge.className = 'status-badge in-progress';
                badge.textContent = `In Progress (${Math.round(progress)}%)`;
            }
        }
        
        // Update progress bar
        updateProgressBar(progress);
        
        if (elements.progressStatus) {
            elements.progressStatus.textContent = `Processing... ${Math.round(progress)}% complete`;
        }
    }

    /**
     * Update the progress bar to show current progress
     * @param {Number} progress - Progress percentage (0-100)
     */
    function updateProgressBar(progress) {
        if (elements.progressBar) {
            elements.progressBar.style.width = `${progress}%`;
        }
    }

    /**
     * Set status indicator to "Completed"
     */
    function setStatusCompleted() {
        if (elements.statusIndicator) {
            const badge = elements.statusIndicator.querySelector('.status-badge');
            if (badge) {
                badge.className = 'status-badge completed';
                badge.textContent = 'Completed';
            }
        }
        
        if (elements.progressBar) {
            elements.progressBar.style.width = '100%';
        }
        
        if (elements.progressStatus) {
            elements.progressStatus.textContent = 'Distribution completed successfully';
        }
    }

    /**
     * Set status indicator to "Error"
     */
    function setStatusError() {
        if (elements.statusIndicator) {
            const badge = elements.statusIndicator.querySelector('.status-badge');
            if (badge) {
                badge.className = 'status-badge error';
                badge.textContent = 'Error';
            }
        }
    }

    /**
     * Enable distribution controls
     */
    function enableDistributionControls() {
        if (elements.startButton) {
            elements.startButton.disabled = false;
        }
        
        if (elements.resetButton) {
            elements.resetButton.disabled = false;
        }
    }

    /**
     * Disable distribution controls with optional reason message
     * @param {String} reason - Optional reason for disabling controls
     */
    function disableDistributionControls(reason) {
        if (elements.startButton) {
            elements.startButton.disabled = true;
        }
        
        if (elements.progressStatus && reason) {
            elements.progressStatus.textContent = reason;
        }
    }

    /**
     * Enable the next button to continue workflow
     */
    function enableNextButton() {
        if (elements.nextButton) {
            elements.nextButton.disabled = false;
        }
    }

    /**
     * Disable the next button
     */
    function disableNextButton() {
        if (elements.nextButton) {
            elements.nextButton.disabled = true;
        }
    }

    /**
     * Add a log entry to the log container
     * @param {String} level - Log level (info, warning, error, success)
     * @param {String} message - Log message
     */
    function addLogEntry(level, message) {
        if (!elements.logContainer) return;
        
        const timestamp = new Date().toISOString().substring(11, 19);
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        
        const logTimestamp = document.createElement('span');
        logTimestamp.className = 'log-timestamp';
        logTimestamp.textContent = `[${timestamp}]`;
        
        const logMessage = document.createElement('span');
        logMessage.className = 'log-message';
        logMessage.textContent = message;
        
        logEntry.appendChild(logTimestamp);
        logEntry.appendChild(logMessage);
        
        elements.logContainer.appendChild(logEntry);
        elements.logContainer.scrollTop = elements.logContainer.scrollHeight;
    }

    /**
     * Update the roll tables with current data
     */
    function updateRollTables() {
        updateRollTable('16mm');
        updateRollTable('35mm');
    }

    /**
     * Update a specific roll table
     * @param {String} type - Film type ('16mm' or '35mm')
     */
    function updateRollTable(type) {
        const tableBody = type === '16mm' ? elements.roll16mmTable : elements.roll35mmTable;
        if (!tableBody) return;
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        // Get rolls from core
        const rolls = config.core.getRolls(type);
        if (!rolls || !rolls.length) return;
        
        // Add row for each roll
        rolls.forEach(roll => {
            const tr = document.createElement('tr');
            
            // Film number cell
            const tdFilmNumber = document.createElement('td');
            tdFilmNumber.textContent = roll.film_number || '';
            tr.appendChild(tdFilmNumber);
            
            // Documents count cell
            const tdDocuments = document.createElement('td');
            tdDocuments.textContent = roll.document_count || '0';
            tr.appendChild(tdDocuments);
            
            // Pages count cell
            const tdPages = document.createElement('td');
            tdPages.textContent = roll.page_count || '0';
            tr.appendChild(tdPages);
            
            // Status cell
            const tdStatus = document.createElement('td');
            const statusSpan = document.createElement('span');
            statusSpan.className = `document-status ${roll.status || 'pending'}`;
            statusSpan.textContent = capitalizeFirstLetter(roll.status || 'pending');
            tdStatus.appendChild(statusSpan);
            tr.appendChild(tdStatus);
            
            // Actions cell
            const tdActions = document.createElement('td');
            const viewButton = document.createElement('button');
            viewButton.className = 'small-button';
            viewButton.innerHTML = '<i class="fas fa-eye"></i> View';
            viewButton.dataset.rollId = roll.id;
            viewButton.addEventListener('click', () => showRollDocuments(roll.id));
            tdActions.appendChild(viewButton);
            tr.appendChild(tdActions);
            
            tableBody.appendChild(tr);
        });
    }

    /**
     * Show documents for a specific roll
     * @param {String} rollId - Roll ID
     */
    function showRollDocuments(rollId) {
        // Implementation to be added in a future update
        console.log(`Showing documents for roll: ${rollId}`);
    }

    /**
     * Refresh all views with current data
     */
    function refreshAllViews() {
        updateProjectInfoPanel();
        updateRollTables();
    }

    /**
     * Capitalize the first letter of a string
     * @param {String} string - String to capitalize
     * @returns {String} Capitalized string
     */
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    /**
     * Update the distribution results panel with data
     * @param {Object} data - Distribution results data
     */
    function updateDistributionResults(data) {
        if (!data) return;
        
        console.log('Updating distribution results with data:', data);
        
        // Update output directory path if available
        if (data.output_dir) {
            const outputDirElement = document.querySelector('#output-directory-path');
            if (outputDirElement) {
                outputDirElement.textContent = data.output_dir;
            }
        }
        
        // Update counts and stats
        const processedDocsElement = document.querySelector('#processed-docs-count');
        if (processedDocsElement) {
            const processed35mm = data.processed_35mm_documents || data.copied_35mm_documents || 0;
            const processed16mm = data.processed_16mm_documents || data.copied_16mm_documents || 0;
            processedDocsElement.textContent = processed35mm + processed16mm;
        }
        
        const refSheetsElement = document.querySelector('#ref-sheets-count');
        if (refSheetsElement) {
            refSheetsElement.textContent = data.reference_sheets || 0;
        }
        
        const docsWithRefsElement = document.querySelector('#docs-with-refs-count');
        if (docsWithRefsElement) {
            docsWithRefsElement.textContent = data.documents_with_references || 0;
        }
        
        // Show the results panel
        const resultsPanel = document.querySelector('#distribution-results-panel');
        if (resultsPanel) {
            resultsPanel.style.display = 'block';
        }
    }

    /**
     * Return public interface for this module
     */
    function publicInterface() {
        return {
            init,
            setStatusNotStarted,
            setStatusLoading,
            setStatusInProgress,
            setStatusCompleted,
            setStatusError,
            updateProgressBar,
            enableDistributionControls,
            disableDistributionControls,
            enableNextButton,
            disableNextButton,
            addLogEntry,
            updateRollTables,
            refreshAllViews,
            updateDistributionResults
        };
    }

    // Return public interface
    return {
        init: init
    };
})(); 