/**
 * project.js - Project setup functionality for microfilm registration system
 * Handles project configuration and validation
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing project setup...');
    
    // Verify that required modules are loaded
    if (!FolderPicker) {
        console.error('ERROR: FolderPicker module not loaded');
        const projectContainer = document.querySelector('#step-1');
        if (projectContainer) {
            projectContainer.innerHTML = `
                <div style="padding: 20px; color: #ff453a; text-align: center;">
                    <h2>Error Loading Project Setup</h2>
                    <p>Required module FolderPicker failed to load. Please check the browser console for details.</p>
                    <p>Try refreshing the page or contact support if the issue persists.</p>
                </div>
            `;
        }
        return;
    }

    // --- DOM Elements ---
    const elements = {
        validateProjectBtn: document.getElementById('validate-project'),
        toStep2Btn: document.getElementById('to-step-2'),
        archiveId: document.getElementById('archive-id'),
        location: document.getElementById('location'),
        documentType: document.getElementById('document-type'),
        projectFolder: document.getElementById('project-folder'),
        outputFolder: document.getElementById('output-folder'),
        pdfFolder: document.getElementById('pdf-folder'),
        pdfBrowseBtn: document.getElementById('pdf-browse-btn'),
        comlistFile: document.getElementById('comlist-file'),
        comlistBrowseBtn: document.getElementById('comlist-browse-btn'),
        autoParse: document.getElementById('auto-parse'),
        
        // Project information elements
        detailsArchiveId: document.getElementById('details-archive-id'),
        detailsLocation: document.getElementById('details-location'),
        detailsDocumentType: document.getElementById('details-document-type'),
        detailsSourcePath: document.getElementById('details-source-path'),
        detailsOutputPath: document.getElementById('details-output-path'),
        detailsPdfFolder: document.getElementById('details-pdf-folder'),
        detailsComlistFile: document.getElementById('details-comlist-file'),
        
        // Edit fields
        editArchiveId: document.getElementById('edit-archive-id'),
        editLocation: document.getElementById('edit-location'),
        editDocumentType: document.getElementById('edit-document-type'),
        editButtons: document.querySelectorAll('.edit-field'),
        
        // Source stats
        sourceFileCount: document.getElementById('source-file-count'),
        sourceSize: document.getElementById('source-size'),
        
        dataOutput: document.querySelector('.data-output')
    };

    // --- Project Setup Functions ---
    const ProjectSetup = {
        // State
        sourceData: {
            path: '',
            fileCount: 0,
            totalSize: 0,
            files: []
        },
        
        /**
         * Update project data display
         */
        updateProjectData: function() {
            const projectData = {
                project: {
                    archiveId: elements.archiveId.value || '',
                    location: elements.location.value || '',
                    documentType: elements.documentType.value || '',
                    sourcePath: elements.projectFolder.value || '',
                    outputPath: elements.outputFolder.value || '',
                    pdfPath: elements.pdfFolder.value || '',
                    comlistPath: elements.comlistFile.value || ''
                }
            };

            // Update details panel with current values
            this.updateDetailsPanel(projectData.project);
        },
        
        /**
         * Update details panel with project data
         * @param {Object} project - Project data object
         */
        updateDetailsPanel: function(project) {
            // Update project information
            elements.detailsArchiveId.textContent = project.archiveId || 'Not set';
            elements.detailsLocation.textContent = project.location || 'Not set';
            elements.detailsDocumentType.textContent = project.documentType || 'Not set';
            
            // Update file paths
            elements.detailsSourcePath.textContent = project.sourcePath || 'Not set';
            elements.detailsOutputPath.textContent = project.outputPath || 'Not set';
            elements.detailsPdfFolder.textContent = project.pdfPath || 'Not set';
            elements.detailsComlistFile.textContent = project.comlistPath || 'Not set';
        },

        /**
         * Parse project information from folder path
         * @param {string} folderPath - Path to parse
         */
        parseFolderPath: function(folderPath) {
            if (!folderPath || !elements.autoParse.checked) return;
            
            try {
                // Extract folder name from path
                const folderName = folderPath.split(/[\\/]/).pop();
                console.log('Parsing folder name:', folderName);
                
                // Try to extract archive ID (RRDxxx-yyyy format)
                const archiveIdMatch = folderName.match(/RRD\d{3}-\d{4}/i);
                if (archiveIdMatch) {
                    elements.archiveId.value = archiveIdMatch[0].toUpperCase();
                }
                
                // Try to extract location based on common patterns (e.g., OU, DW, etc.)
                const locationPatterns = {
                    'OU': /\b(OU|OHIO|UNIVERSITY)\b/i,
                    'DW': /\b(DW|DEWEY|DEWEY LIBRARY)\b/i,
                    'CL': /\b(CL|CENTRAL|CENTRAL LIBRARY)\b/i,
                    'AL': /\b(AL|ARCHIVES|ARCHIVES LIBRARY)\b/i
                };
                
                for (const [code, pattern] of Object.entries(locationPatterns)) {
                    if (pattern.test(folderName)) {
                        elements.location.value = code;
                        break;
                    }
                }
                
                // Try to extract document type
                const docTypePatterns = {
                    'Correspondence': /\b(CORR|CORRESPONDENCE|LETTERS)\b/i,
                    'Minutes': /\b(MIN|MINUTES|MEETING)\b/i,
                    'Reports': /\b(REP|REPORT|REPORTS)\b/i,
                    'Ledgers': /\b(LED|LEDGER|LEDGERS)\b/i,
                    'Photographs': /\b(PHOTO|PHOTOGRAPH|PHOTOGRAPHS)\b/i
                };
                
                for (const [type, pattern] of Object.entries(docTypePatterns)) {
                    if (pattern.test(folderName)) {
                        elements.documentType.value = type;
                        break;
                    }
                }
                
                // Update the details panel
                this.updateProjectData();
                
                if (elements.archiveId.value || elements.location.value || elements.documentType.value) {
                    this.showNotification('Project information detected and populated', 'info');
                }
            } catch (error) {
                console.error('Error parsing folder path:', error);
            }
        },

        /**
         * Validate archive ID format
         * @param {string} id - Archive ID to validate
         * @returns {boolean} - Whether the ID is valid
         */
        validateArchiveId: function(id) {
            // Pattern: RRD followed by exactly 3 digits, then hyphen, then 4 digit year
            const pattern = /^RRD\d{3}-\d{4}/;
            return pattern.test(id);
        },

        /**
         * Validate the form and show error messages
         * @returns {boolean} - Whether the form is valid
         */
        validateForm: function() {
            let isValid = true;
            
            // Remove all existing error messages first
            document.querySelectorAll('.error-message').forEach(msg => msg.remove());
            
            // Required fields validation
            if (!elements.projectFolder.value) {
                isValid = false;
                this.showFieldError(elements.projectFolder, 'Source folder path is required');
            }
            
            if (!elements.archiveId.value) {
                isValid = false;
                this.showNotification('Archive ID is required', 'error');
                
                // Highlight the field in the project information card
                elements.detailsArchiveId.closest('.project-field').classList.add('has-error');
                
                // Add visual indicator that user needs to fill in Archive ID
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                errorDiv.textContent = 'Archive ID is required';
                elements.detailsArchiveId.closest('.field-value-container').appendChild(errorDiv);
            } else if (!this.validateArchiveId(elements.archiveId.value)) {
                isValid = false;
                this.showNotification('Archive ID must be in format RRDxxx-yyyy (e.g., RRD001-2024)', 'error');
                
                // Highlight the field in the project information card
                elements.detailsArchiveId.closest('.project-field').classList.add('has-error');
                
                // Add visual indicator that Archive ID format is incorrect
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                errorDiv.textContent = 'Invalid Archive ID format';
                elements.detailsArchiveId.closest('.field-value-container').appendChild(errorDiv);
            }

            return isValid;
        },
        
        /**
         * Show field error message
         * @param {HTMLElement} field - Field element
         * @param {string} message - Error message
         */
        showFieldError: function(field, message) {
            field.classList.add('error');
            
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message visible';
            errorDiv.textContent = message;
            
            // Insert after input or input container
            const container = field.closest('.folder-input-container') || field;
            container.parentElement.insertBefore(errorDiv, container.nextSibling);
        },

        /**
         * Show notification message
         * @param {string} message - Message to display
         * @param {string} type - Notification type (success, error, warning, info)
         */
        showNotification: function(message, type = 'info') {
            let notification = document.querySelector('.notification');
            if (!notification) {
                notification = document.createElement('div');
                notification.className = 'notification';
                document.body.appendChild(notification);
                notification.style.position = 'fixed';
                notification.style.bottom = '20px';
                notification.style.right = '20px';
                notification.style.padding = '12px 20px';
                notification.style.borderRadius = '8px';
                notification.style.color = '#fff';
                notification.style.fontWeight = '500';
                notification.style.zIndex = '9999';
                notification.style.transform = 'translateY(100px)';
                notification.style.opacity = '0';
                notification.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
                notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                notification.style.display = 'flex';
                notification.style.alignItems = 'center';
                notification.style.gap = '10px';
            }

            let icon = '';
            switch(type) {
                case 'success':
                    icon = '<i class="fas fa-check-circle"></i>';
                    notification.style.backgroundColor = '#34a853';
                    break;
                case 'error':
                    icon = '<i class="fas fa-times-circle"></i>';
                    notification.style.backgroundColor = '#ea4335';
                    break;
                case 'warning':
                    icon = '<i class="fas fa-exclamation-triangle"></i>';
                    notification.style.backgroundColor = '#fbbc04';
                    break;
                default:
                    icon = '<i class="fas fa-info-circle"></i>';
                    notification.style.backgroundColor = '#1a73e8';
            }

            notification.innerHTML = icon + message;
            notification.style.transform = 'translateY(0)';
            notification.style.opacity = '1';

            setTimeout(() => {
                notification.style.transform = 'translateY(100px)';
                notification.style.opacity = '0';
            }, 3000);
        },

        /**
         * Handle editable field buttons
         * @param {HTMLElement} button - Edit button element
         * @param {string} fieldId - Field ID to edit
         */
        handleFieldEdit: function(button, fieldId) {
            const container = button.closest('.field-value-container');
            const displayEl = document.getElementById(button.dataset.display);
            const inputEl = document.getElementById(`edit-${fieldId}`);
            
            // Remove any existing error messages
            container.querySelectorAll('.field-error').forEach(el => el.remove());
            container.closest('.project-field').classList.remove('has-error');
            
            if (container.classList.contains('editing')) {
                // Save the value and exit edit mode
                container.classList.remove('editing');
                displayEl.style.display = 'block';
                inputEl.style.display = 'none';
                
                if (inputEl.value.trim() !== '') {
                    displayEl.textContent = inputEl.value;
                    
                    // Update the corresponding hidden input field
                    if (fieldId === 'archive-id') {
                        elements.archiveId.value = inputEl.value;
                    } else if (fieldId === 'location') {
                        elements.location.value = inputEl.value;
                    } else if (fieldId === 'document-type') {
                        elements.documentType.value = inputEl.value;
                    }
                    
                    this.updateProjectData();
                }
                
                button.innerHTML = '<i class="fas fa-edit"></i>';
            } else {
                // Enter edit mode
                container.classList.add('editing');
                displayEl.style.display = 'none';
                inputEl.style.display = 'block';
                inputEl.disabled = false;
                inputEl.value = displayEl.textContent !== 'Not set' ? displayEl.textContent : '';
                inputEl.focus();
                
                button.innerHTML = '<i class="fas fa-save"></i>';
                
                // Add event listeners for saving
                inputEl.addEventListener('blur', () => {
                    if (container.classList.contains('editing')) {
                        this.handleFieldEdit(button, fieldId);
                    }
                }, { once: true });
                
                inputEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        this.handleFieldEdit(button, fieldId);
                    }
                });
            }
        },

        /**
         * Get folder size and file count
         * @param {string} folderPath - Path to folder
         * @returns {Promise<{fileCount: number, totalSize: number}>} - Folder statistics
         */
        getFolderStats: async function(folderPath) {
            try {
                const apiEndpoint = '/list-drive-contents/?path=' + encodeURIComponent(folderPath) + '&scan_subdirectories=true';
                const response = await fetch(apiEndpoint, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' }
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to get folder statistics: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // Calculate total file size and count
                let totalSize = 0;
                let fileCount = 0;
                
                const processFolder = (folder) => {
                    if (folder.files) {
                        folder.files.forEach(file => {
                            totalSize += file.size || 0;
                            fileCount++;
                        });
                    }
                    
                    if (folder.folders) {
                        folder.folders.forEach(subfolder => {
                            processFolder(subfolder);
                        });
                    }
                };
                
                processFolder(data);
                
                // Update source data
                this.sourceData.path = folderPath;
                this.sourceData.fileCount = fileCount;
                this.sourceData.totalSize = totalSize;
                
                // Update UI
                elements.sourceFileCount.textContent = fileCount.toString();
                elements.sourceSize.textContent = this.formatFileSize(totalSize);
                
                return { fileCount, totalSize };
            } catch (error) {
                console.error('Error getting folder stats:', error);
                this.showNotification('Failed to get folder statistics', 'error');
                return { fileCount: 0, totalSize: 0 };
            }
        },
        
        /**
         * Format file size to human-readable format
         * @param {number} bytes - Size in bytes
         * @returns {string} - Formatted size string
         */
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        /**
         * Initialize event listeners
         */
        initializeEventListeners: function() {
            // No input listeners for hidden fields
            elements.projectFolder.addEventListener('input', () => this.updateProjectData());
            elements.outputFolder.addEventListener('input', () => this.updateProjectData());
            elements.pdfFolder.addEventListener('input', () => this.updateProjectData());
            elements.comlistFile.addEventListener('input', () => this.updateProjectData());
            
            // Auto-parse toggle
            elements.autoParse.addEventListener('change', () => {
                if (elements.autoParse.checked && elements.projectFolder.value) {
                    // Re-parse if folder path exists and auto-parse is enabled
                    this.parseFolderPath(elements.projectFolder.value);
                }
            });

            // Browse button listeners
            document.querySelectorAll('.browse-button').forEach(button => {
                button.addEventListener('click', async function() {
                    const inputElement = this.previousElementSibling;
                    try {
                        // Determine if we're browsing for a folder or file
                        const mode = inputElement.id === 'comlist-file' ? 'files' : 'folders';
                        const fileFilter = mode === 'files' ? ['.xlsx', '.xls', '.csv'] : null;
                        
                        // Open FolderPicker
                        const result = await FolderPicker.show(true, mode, fileFilter);
                        
                        // Handle the folder picker result object
                        if (result && result.path) {
                            // Extract the path from the result object
                            const selectedPath = result.path;
                            inputElement.value = selectedPath;
                            
                            // If this is the source folder input, set the output folder path and parse folder name
                            if (inputElement.id === 'project-folder') {
                                elements.outputFolder.value = `${selectedPath}/.output`;
                                
                                // Parse folder name if auto-parse is enabled
                                if (elements.autoParse.checked) {
                                    ProjectSetup.parseFolderPath(selectedPath);
                                }
                                
                                // Get folder statistics
                                await ProjectSetup.getFolderStats(selectedPath);
                            }
                            
                            ProjectSetup.updateProjectData();
                        }
                    } catch (error) {
                        console.error('Error selecting folder:', error);
                        ProjectSetup.showNotification('Failed to select folder', 'error');
                    }
                });
            });

            // Edit field buttons
            elements.editButtons.forEach(button => {
                const fieldId = button.getAttribute('data-field');
                if (fieldId) {
                    button.addEventListener('click', () => this.handleFieldEdit(button, fieldId));
                }
            });

            // Validate button listener
            elements.validateProjectBtn.addEventListener('click', function() {
                // First, clear any existing error indicators
                document.querySelectorAll('.project-field').forEach(field => {
                    field.classList.remove('has-error');
                    field.querySelectorAll('.field-error').forEach(err => err.remove());
                });
                
                if (!ProjectSetup.validateForm()) {
                    // Update status badge to error state
                    document.querySelector('#step-1 .status-badge').className = 'status-badge error';
                    document.querySelector('#step-1 .status-badge').innerHTML = 
                        '<i class="fas fa-exclamation-circle"></i> Configuration Invalid';
                    
                    ProjectSetup.showNotification('Please fix the validation errors', 'error');
                    return;
                }

                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
                
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-check-circle"></i> Validate Project';
                    
                    // Update status badge
                    document.querySelector('#step-1 .status-badge').className = 'status-badge completed';
                    document.querySelector('#step-1 .status-badge').innerHTML = 
                        '<i class="fas fa-check-circle"></i> Configuration Valid';
                    
                    elements.toStep2Btn.disabled = false;
                    ProjectSetup.showNotification('Project configuration validated successfully!', 'success');
                }, 1500);
            });
            
            // Details panel toggle
            const toggleDetailsBtn = document.getElementById('toggle-details');
            if (toggleDetailsBtn) {
                toggleDetailsBtn.addEventListener('click', function() {
                    const detailsPanel = document.querySelector('.project-info-card');
                    detailsPanel.classList.toggle('collapsed');
                    
                    // Save collapsed state to local storage
                    const isCollapsed = detailsPanel.classList.contains('collapsed');
                    localStorage.setItem('projectDetailsCollapsed', isCollapsed);
                });
                
                // Check if details panel should be collapsed based on saved state
                const shouldCollapse = localStorage.getItem('projectDetailsCollapsed') === 'true';
                if (shouldCollapse) {
                    document.querySelector('.project-info-card').classList.add('collapsed');
                }
            }
        },

        /**
         * Initialize the project setup
         */
        initialize: function() {
            const style = document.createElement('style');
            style.textContent = `
                .invalid, .error {
                    border-color: #ea4335 !important;
                    background-color: #fff8f8;
                }
                .invalid:focus, .error:focus {
                    box-shadow: 0 0 0 2px rgba(234, 67, 53, 0.2) !important;
                }
                
                /* Field editing */
                .field-edit {
                    display: none;
                }
                .field-value-container {
                    position: relative;
                    display: flex;
                    align-items: center;
                }
                .field-value {
                    display: block;
                    padding: 4px 0;
                }
                .icon-button {
                    background: none;
                    border: none;
                    color: var(--color-primary);
                    cursor: pointer;
                    margin-left: 8px;
                    padding: 4px;
                    border-radius: 4px;
                }
                .icon-button:hover {
                    background-color: rgba(var(--color-primary-rgb), 0.1);
                }
                
                /* Error styles for project fields */
                .project-field.has-error {
                    background-color: rgba(234, 67, 53, 0.05);
                    border-color: #ea4335;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 0 -8px 8px;
                }
                
                .field-error {
                    color: #ea4335;
                    font-size: 0.8rem;
                    margin-top: 4px;
                    font-style: italic;
                    position: absolute;
                    bottom: -18px;
                    left: 0;
                }
                
                /* Source stats */
                .source-stats {
                    display: flex;
                    gap: 16px;
                    margin-top: 16px;
                    padding: 12px;
                    background-color: var(--color-surface-alt, #f8f9fa);
                    border-radius: 8px;
                }
                .stat-item {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                .stat-label {
                    font-size: 14px;
                    color: var(--color-text-light);
                }
                .stat-value {
                    font-weight: var(--font-weight-medium);
                    color: var(--color-text);
                }
                
                /* Button customization */
                .browse-button.secondary {
                    background-color: var(--color-secondary, #6c757d);
                }
                .browse-button.secondary:hover {
                    background-color: var(--color-secondary-dark, #5a6268);
                }
            `;
            document.head.appendChild(style);

            this.initializeEventListeners();
            this.updateProjectData();
        }
    };

    // Initialize project setup
    ProjectSetup.initialize();
});

