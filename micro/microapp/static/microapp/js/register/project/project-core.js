/**
 * transfer-core.js - Core business logic for Transfer module
 * Acts as the central coordinator between different modules
 */

// Make the class available globally
window.TransferCore = class TransferCore {
    constructor() {
        // Initialize dependencies
        this.eventManager = new EventManager();
        this.ui = new TransferUI(this.eventManager);
        this.finders = new FileFinders(this.eventManager);
        this.validator = new ValidationService();
        this.apiService = new ApiService();
        this.utils = new Utilities();
        this.dbService = new DatabaseService();
        
        // Check for URL parameters
        this.checkUrlParameters();
        
        // Initialize state
        this.state = this.loadStateFromStorage() || this.getInitialState();
        
        // Set up event subscriptions
        this.initializeEventHandlers();
        
        // Log initialization
        this.ui.addLogEntry('Transfer system initialized');
        
        // Update UI with loaded state
        this.restoreUIFromState();
    }
    
    /**
     * Check URL parameters for project ID, step, or mode
     */
    async checkUrlParameters() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            
            // Check if we have a project ID in the URL
            const projectId = urlParams.get('id');
            if (projectId) {
                this.ui.addLogEntry(`Project ID found in URL: ${projectId}`);
                
                // Check if it matches the stored project
                const savedState = this.loadStateFromStorage();
                
                if (savedState && savedState.projectId && savedState.projectId == projectId) {
                    this.ui.addLogEntry("Project ID matches local storage - using cached data");
                } else {
                    // Try to load the project from the database
                    this.ui.addLogEntry("Attempting to load project data from database...");
                    
                    try {
                        const projectData = await this.dbService.getProject(projectId);
                        
                        if (projectData && projectData.status === 'success') {
                            this.ui.addLogEntry(`Successfully loaded project ${projectId} from database`);
                            
                            // Create a state object from the project data
                            const newState = this.getInitialState();
                            
                            // Update source data
                            newState.sourceData.path = projectData.data.project_path || '';
                            newState.sourceData.folderName = projectData.data.project_folder_name || '';
                            
                            // Update project info
                            newState.projectInfo.archiveId = projectData.data.archive_id || '';
                            newState.projectInfo.location = projectData.data.location || '';
                            newState.projectInfo.documentType = projectData.data.doc_type || '';
                            newState.projectInfo.pdfPath = projectData.data.pdf_folder_path || '';
                            newState.projectInfo.comlistPath = projectData.data.comlist_path || '';
                            newState.projectInfo.isValid = true; // It's from the database, so it's valid
                            
                            // Update destination path
                            newState.destinationPath = projectData.data.output_dir || '';
                            
                            // Set project ID
                            newState.projectId = projectId;
                            
                            // Save this state to localStorage
                            localStorage.setItem('microfilmProjectState', JSON.stringify(newState));
                            
                            // Display success notification
                            this.ui.showNotification(`Project ${projectId} loaded successfully from database`, 'success');
                        } else {
                            this.ui.addLogEntry(`Failed to load project: ${projectData.message || 'Unknown error'}`);
                            this.ui.showNotification(`Couldn't load project ${projectId}. Using local data if available.`, 'warning');
                        }
                    } catch (error) {
                        console.error('Error loading project from database:', error);
                        this.ui.addLogEntry(`Error loading project: ${error.message}`);
                        this.ui.showNotification(`Error loading project ${projectId}`, 'error');
                    }
                }
            }
            
            // Check for workflow mode
            const mode = urlParams.get('mode');
            if (mode) {
                this.ui.addLogEntry(`Workflow mode found in URL: ${mode}`);
                
                // Update the workflow state
                const workflowState = localStorage.getItem('microfilmWorkflowState') ? 
                    JSON.parse(localStorage.getItem('microfilmWorkflowState')) : {};
                
                workflowState.workflowMode = mode;
                localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
                
                // Update the UI mode if we have a progress component
                if (window.progressComponent && typeof window.progressComponent.updateModeIndicator === 'function') {
                    window.progressComponent.updateModeIndicator(mode);
                }
            }
            
            // Check for step parameter - not directly used here, but could be used for navigation
            const step = urlParams.get('step');
            if (step) {
                this.ui.addLogEntry(`Step parameter found in URL: ${step}`);
            }
        } catch (error) {
            console.error('Error processing URL parameters:', error);
        }
    }
    
    /**
     * Save current state to localStorage
     */
    saveStateToStorage() {
        try {
            // Create a copy of the state to save
            const stateToSave = {
                sourceData: {
                    path: this.state.sourceData.path,
                    folderName: this.state.sourceData.folderName,
                    fileCount: this.state.sourceData.fileCount,
                    totalSize: this.state.sourceData.totalSize,
                    totalSizeFormatted: this.state.sourceData.totalSizeFormatted
                    // Omit files and folder structure as they can be large
                },
                destinationPath: this.state.destinationPath,
                projectInfo: {
                    archiveId: this.state.projectInfo.archiveId,
                    location: this.state.projectInfo.location,
                    documentType: this.state.projectInfo.documentType,
                    pdfPath: this.state.projectInfo.pdfPath,
                    comlistPath: this.state.projectInfo.comlistPath,
                    isValid: this.state.projectInfo.isValid
                },
                projectId: this.state.projectId,
                uiState: this.state.uiState,
                isValidated: this.state.projectInfo.isValid && this.state.projectId
            };
            
            localStorage.setItem('microfilmProjectState', JSON.stringify(stateToSave));
            console.log('Project state saved to localStorage');
        } catch (error) {
            console.error('Error saving state to localStorage:', error);
        }
    }
    
    /**
     * Load state from localStorage
     * @returns {Object|null} - Loaded state or null if none exists
     */
    loadStateFromStorage() {
        try {
            const savedState = localStorage.getItem('microfilmProjectState');
            if (!savedState) return null;
            
            const parsedState = JSON.parse(savedState);
            
            // Initialize empty arrays/objects for properties we didn't save
            if (parsedState.sourceData) {
                parsedState.sourceData.files = [];
                parsedState.sourceData.folderStructure = null;
            }
            
            console.log('Project state loaded from localStorage');
            return parsedState;
        } catch (error) {
            console.error('Error loading state from localStorage:', error);
            return null;
        }
    }
    
    /**
     * Reset/clear the state in localStorage
     */
    resetState() {
        try {
            localStorage.removeItem('microfilmProjectState');
            
            // Reset the state to initial values
            this.state = this.getInitialState();
            
            // Update UI
            this.restoreUIFromState();
            
            // Log and notify
            this.ui.addLogEntry('Project state has been reset');
            this.ui.showNotification('Project has been reset', 'info');
            
            // Update UI status
            this.ui.updateStatusBadge('initial', 'Pending', 'both');
            
            // Hide reset button
            if (this.ui.elements.resetStateBtn) {
                this.ui.elements.resetStateBtn.style.display = 'none';
            }
            
            // Disable next step button
            if (this.ui.elements.toStep2Btn) {
                this.ui.elements.toStep2Btn.disabled = true;
            }
            
            console.log('Project state reset');
        } catch (error) {
            console.error('Error resetting state:', error);
            this.ui.showNotification('Error resetting project state', 'error');
        }
    }
    
    /**
     * Update UI with loaded state
     */
    restoreUIFromState() {
        try {
            // Update source folder info
            if (this.state.sourceData && this.state.sourceData.path) {
                this.ui.elements.sourceFolderInput.value = this.state.sourceData.path;
                this.ui.updateSourceInfo(this.state.sourceData);
            }
            
            // Update destination path
            if (this.state.destinationPath) {
                this.ui.elements.destinationFolderInput.value = this.state.destinationPath;
                this.ui.updateDestinationPath(this.state.destinationPath);
            }
            
            // Update project info fields
            if (this.state.projectInfo) {
                this.ui.updateProjectInfo(this.state.projectInfo);
                
                // Show PDF warning if needed
                if (this.state.projectInfo.pdfPath) {
                    this.ui.elements.pdfFolderDisplay.textContent = this.state.projectInfo.pdfPath;
                }
                
                // Show COMList warning if needed
                if (this.state.projectInfo.comlistPath) {
                    this.ui.elements.comlistFileDisplay.textContent = this.state.projectInfo.comlistPath;
                }
            }
            
            // Update UI toggles
            if (this.state.uiState) {
                this.ui.elements.autoParse.checked = this.state.uiState.autoParseEnabled;
                this.ui.elements.autoSelectPath.checked = this.state.uiState.autoSelectPathEnabled;
                this.ui.elements.autoFindPdf.checked = this.state.uiState.autoFindPdfEnabled;
                this.ui.elements.autoFindComlist.checked = this.state.uiState.autoFindComlistEnabled;
                this.ui.elements.createSubfolder.checked = this.state.uiState.createSubfolderEnabled;
                
                // Disable PDF/COMList browse buttons if auto-find is enabled
                this.ui.elements.pdfBrowseBtn.disabled = this.state.uiState.autoFindPdfEnabled;
                this.ui.elements.comlistBrowseBtn.disabled = this.state.uiState.autoFindComlistEnabled;
            }
            
            // If project was validated, update UI accordingly
            if (this.state.projectInfo && this.state.projectInfo.isValid) {
                this.ui.updateStatusBadge('completed', 'Validation successful', 'both');
                
                // Enable next step button
                if (this.ui.elements.toStep2Btn) {
                    this.ui.elements.toStep2Btn.disabled = false;
                }
                
                // Show reset button
                if (this.ui.elements.resetStateBtn) {
                    this.ui.elements.resetStateBtn.style.display = 'inline-block';
                }
            }
            
            console.log('UI restored from saved state');
        } catch (error) {
            console.error('Error restoring UI from state:', error);
        }
    }
    
    /**
     * Get initial state for the application
     * @returns {Object} - Initial state
     */
    getInitialState() {
        return {
            sourceData: {
                path: '',
                folderName: '',
                fileCount: 0,
                totalSize: 0,
                files: [],
                folderStructure: null
            },
            destinationPath: '',
            defaultDestination: 'Y:',
            projectInfo: {
                archiveId: '',
                location: '',
                documentType: '',
                pdfPath: '',
                comlistPath: '',
                isValid: false
            },
            transferState: {
                status: 'initial', // initial, ready, in-progress, completed, error, cancelled
                filesTransferred: 0,
                bytesTransferred: 0,
                speed: 0,
                startTime: null,
                cancelRequested: false
            },
            uiState: {
                autoParseEnabled: true,
                autoSelectPathEnabled: true,
                autoFindPdfEnabled: true,
                autoFindComlistEnabled: true,
                createSubfolderEnabled: true
            }
        };
    }
    
    /**
     * Initialize event handlers to respond to UI events
     */
    initializeEventHandlers() {
        // Source folder selection
        this.eventManager.subscribe('source-folder-selected', async (data) => {
            await this.handleSourceFolderSelected(data.path, data.folderData);
        });
        
        // Destination folder selection
        this.eventManager.subscribe('destination-folder-selected', (data) => {
            this.handleDestinationFolderSelected(data.path);
        });
        
        // PDF folder selection
        this.eventManager.subscribe('pdf-folder-selected', (data) => {
            this.handlePdfFolderSelected(data.path);
        });
        
        // COMList file selection
        this.eventManager.subscribe('comlist-file-selected', (data) => {
            this.handleComlistFileSelected(data.path);
        });
        
        // Auto-parse toggle
        this.eventManager.subscribe('auto-parse-toggle-changed', (data) => {
            this.handleAutoParseToggleChanged(data.checked);
        });
        
        // Auto-select path toggle
        this.eventManager.subscribe('auto-select-path-toggle-changed', (data) => {
            this.handleAutoSelectPathToggleChanged(data.checked);
        });
        
        // Auto-find PDF toggle
        this.eventManager.subscribe('auto-find-pdf-toggle-changed', (data) => {
            this.handleAutoFindPdfToggleChanged(data.checked);
        });
        
        // Auto-find COMList toggle
        this.eventManager.subscribe('auto-find-comlist-toggle-changed', (data) => {
            this.handleAutoFindComlistToggleChanged(data.checked);
        });
        
        // Subfolder toggle
        this.eventManager.subscribe('subfolder-toggle-changed', (data) => {
            this.handleSubfolderToggleChanged(data.checked);
        });
        
        // Field input changes (real-time validation)
        this.eventManager.subscribe('field-input-changed', (data) => {
            this.handleFieldInputChanged(data.fieldId, data.value);
        });
        
        // Field value changes (after editing)
        this.eventManager.subscribe('field-value-changed', (data) => {
            this.handleFieldValueChanged(data.fieldId, data.value);
        });
        
        // Start transfer button - modified to handle validation and database saving
        this.eventManager.subscribe('start-transfer-clicked', () => {
            this.handleValidateClicked();
        });
        
        // Reset state button
        this.eventManager.subscribe('reset-state-clicked', () => {
            this.resetState();
        });
        
        // Cancel transfer button - simplified to just log messages
        this.eventManager.subscribe('cancel-transfer-clicked', () => {
            this.ui.addLogEntry("Cancel functionality has been removed");
            this.ui.showNotification('Cancel functionality has been removed', 'info');
        });
        
        // Navigation to next step
        this.eventManager.subscribe('navigate-to-next-step', () => {
            this.handleNavigateToNextStep();
        });
        
        // PDF folder found by auto-finder
        this.eventManager.subscribe('pdf-folder-found', (data) => {
            this.handlePdfFolderFound(data.path, data.warningInfo);
        });
        
        // PDF folder not found by auto-finder
        this.eventManager.subscribe('pdf-folder-not-found', (data) => {
            this.handlePdfFolderNotFound(data.message, data.error);
        });
        
        // COMList file found by auto-finder
        this.eventManager.subscribe('comlist-file-found', (data) => {
            this.handleComlistFileFound(data.path, data.warningInfo);
        });
        
        // COMList file not found by auto-finder
        this.eventManager.subscribe('comlist-file-not-found', (data) => {
            this.handleComlistFileNotFound(data.message, data.error);
        });
    }
    
    /**
     * Handle source folder selected
     * @param {string} path - Selected source folder path
     * @param {Object} folderData - Additional folder data from the picker
     */
    async handleSourceFolderSelected(path, folderData) {
        this.ui.addLogEntry(`Getting structure of selected folder: ${path}...`);
        
        try {
            // Get folder structure from API
            const folderStructure = await this.apiService.getFolderStructure(path, true);
            
            // Update state
            this.state.sourceData.path = path;
            this.state.sourceData.folderName = this.utils.extractFolderName(path);
            this.state.sourceData.folderStructure = folderStructure;
            
            // Get file statistics
            await this.fetchSourceFileStats();
            
            // Update UI with source information
            this.ui.updateSourceInfo(this.state.sourceData);
            
            // Save state to localStorage
            this.saveStateToStorage();
            
            // Log entry about structure
            this.ui.addLogEntry(`Found ${this.state.sourceData.folderStructure.folders.length} subfolders and ${this.state.sourceData.folderStructure.files.length} files in source folder`);
            
            // If auto features are enabled, trigger them
            if (this.state.uiState.autoSelectPathEnabled) {
                this.updateDestinationPreview();
            }
            
            if (this.state.uiState.autoParseEnabled && this.state.sourceData.folderName) {
                this.parseProjectInfo(this.state.sourceData.folderName);
            }
            
            if (this.state.uiState.autoFindPdfEnabled) {
                this.ui.addLogEntry("Auto-find PDF folder is enabled and will be triggered");
                this.finders.findPdfFolder(this.state.sourceData, this.state.projectInfo);
            }
            
            if (this.state.uiState.autoFindComlistEnabled) {
                this.ui.addLogEntry("Auto-find COMList file is enabled and will be triggered");
                this.finders.findComlistFile(this.state.sourceData, this.state.projectInfo);
            }
            
            // Removed automatic validation
        } catch (error) {
            console.error('Error processing source folder:', error);
            this.ui.showNotification('Failed to process source folder', 'error');
        }
    }
    
    /**
     * Fetch file statistics for the source folder
     */
    async fetchSourceFileStats() {
        try {
            // Get file statistics
            const stats = await this.apiService.getFileStats(this.state.sourceData.path);
            
            // Update state
            this.state.sourceData.fileCount = stats.fileCount;
            this.state.sourceData.totalSize = stats.totalSize;
            this.state.sourceData.files = stats.files;
            this.state.sourceData.totalSizeFormatted = this.utils.formatSize(stats.totalSize);
            
            // Save state to localStorage
            this.saveStateToStorage();
            
            // Log results
            this.ui.addLogEntry(`Source folder selected: ${this.state.sourceData.path}`);
            this.ui.addLogEntry(`Found ${stats.fileCount} files (${this.state.sourceData.totalSizeFormatted})`);
        } catch (error) {
            console.error('Error getting file statistics:', error);
            this.ui.showNotification('Failed to get file statistics', 'error');
        }
    }
    
    /**
     * Handle destination folder selected
     * @param {string} path - Selected destination folder path
     */
    handleDestinationFolderSelected(path) {
        this.state.destinationPath = path;
        this.updateDestinationPreview();
        this.saveStateToStorage();
        // Removed automatic validation
    }
    
    /**
     * Update destination preview based on current state
     */
    updateDestinationPreview() {
        // Use the default destination if the actual destination folder is empty
        const basePath = this.state.destinationPath || this.state.defaultDestination;
        let finalPath = basePath;
        
        if (this.state.uiState.createSubfolderEnabled && this.state.sourceData.folderName) {
            // Ensure the base path ends with a backslash
            const basePathWithSeparator = this.utils.ensureTrailingSlash(basePath);
            finalPath = `${basePathWithSeparator}${this.state.sourceData.folderName}\\`;
        }
        
        this.state.destinationPath = finalPath;
        this.ui.updateDestinationPath(finalPath);
        this.saveStateToStorage();
    }
    
    /**
     * Parse project information from folder name
     * Format: RRDXXX-YYYY_LOCATION_DOCTYPE
     * @param {string} folderName - Folder name to parse
     */
    parseProjectInfo(folderName) {
        // Match the pattern RRDXXX-YYYY_LOCATION_DOCTYPE
        const regex = /^(RRD\d{3}-\d{4})_([A-Z]+)_(.+)$/;
        const match = folderName.match(regex);
        
        if (match) {
            const [_, archiveId, location, docType] = match;
            
            // Keep any existing PDF and COMList paths when parsing
            const pdfPath = this.state.projectInfo.pdfPath || '';
            const comlistPath = this.state.projectInfo.comlistPath || '';
            
            // Update state
            this.state.projectInfo = {
                archiveId: archiveId,
                location: location,
                documentType: docType,
                pdfPath: pdfPath,
                comlistPath: comlistPath,
                isValid: false // Will be validated later
            };
            
            // Update UI
            this.ui.updateProjectInfo(this.state.projectInfo);
            
            // Save state to localStorage
            this.saveStateToStorage();
            
            // Validate fields
            this.validateField('archive-id', archiveId);
            this.validateField('location', location);
            this.validateField('document-type', docType);
            
            // Validate overall status
            this.validateProjectStatus();
            
            this.ui.addLogEntry(`Project info parsed: ID=${archiveId}, Location=${location}, Type=${docType}`);
        } else {
            // Failed to parse, set empty values but preserve PDF and COMList paths
            this.state.projectInfo = {
                archiveId: '',
                location: '',
                documentType: '',
                pdfPath: this.state.projectInfo.pdfPath || '',
                comlistPath: this.state.projectInfo.comlistPath || '',
                isValid: false
            };
            
            // Update UI
            this.ui.updateProjectInfo(this.state.projectInfo);
            
            // Save state to localStorage
            this.saveStateToStorage();
            
            // Clear any field errors
            this.ui.clearFieldError('archive-id');
            this.ui.clearFieldError('location');
            this.ui.clearFieldError('document-type');
            
            this.ui.addLogEntry('Failed to parse project information from folder name');
            this.ui.updateStatusBadge('error', 'Could not parse project info from folder name', 'both');
        }
    }
    
    /**
     * Handle PDF folder selected
     * @param {string} path - Selected PDF folder path
     */
    handlePdfFolderSelected(path) {
        // Update state
        this.state.projectInfo.pdfPath = path;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Log entry
        this.ui.addLogEntry(`PDF folder selected: ${path}`);
        
        // Removed automatic validation
    }
    
    /**
     * Handle COMList file selected
     * @param {string} path - Selected COMList file path
     */
    handleComlistFileSelected(path) {
        // Update state
        this.state.projectInfo.comlistPath = path;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Log entry
        this.ui.addLogEntry(`COMList file selected: ${path}`);
        
        // Removed automatic validation
    }
    
    /**
     * Handle auto-parse toggle changed
     * @param {boolean} checked - Whether auto-parse is checked
     */
    handleAutoParseToggleChanged(checked) {
        this.state.uiState.autoParseEnabled = checked;
        this.ui.toggleFieldsEditability(!checked);
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        if (checked && this.state.sourceData.folderName) {
            this.parseProjectInfo(this.state.sourceData.folderName);
        }
    }
    
    /**
     * Handle auto-select path toggle changed
     * @param {boolean} checked - Whether auto-select path is checked
     */
    handleAutoSelectPathToggleChanged(checked) {
        this.state.uiState.autoSelectPathEnabled = checked;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        if (checked && this.state.sourceData.folderName) {
            this.updateDestinationPreview();
        }
    }
    
    /**
     * Handle auto-find PDF toggle changed
     * @param {boolean} checked - Whether auto-find PDF is checked
     */
    handleAutoFindPdfToggleChanged(checked) {
        this.state.uiState.autoFindPdfEnabled = checked;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        if (checked) {
            this.ui.addLogEntry("Auto-find PDF folder toggled on");
            
            if (this.state.sourceData.path) {
                this.finders.findPdfFolder(this.state.sourceData, this.state.projectInfo);
            } else {
                this.ui.addLogEntry("Select a source folder to activate auto-find PDF folder");
            }
        } else {
            this.ui.addLogEntry("Auto-find PDF folder toggled off");
        }
    }
    
    /**
     * Handle auto-find COMList toggle changed
     * @param {boolean} checked - Whether auto-find COMList is checked
     */
    handleAutoFindComlistToggleChanged(checked) {
        this.state.uiState.autoFindComlistEnabled = checked;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        if (checked) {
            this.ui.addLogEntry("Auto-find COMList file toggled on");
            
            if (this.state.sourceData.path) {
                this.finders.findComlistFile(this.state.sourceData, this.state.projectInfo);
            } else {
                this.ui.addLogEntry("Select a source folder to activate auto-find COMList file");
            }
        } else {
            this.ui.addLogEntry("Auto-find COMList file toggled off");
        }
    }
    
    /**
     * Handle subfolder toggle changed
     * @param {boolean} checked - Whether create subfolder is checked
     */
    handleSubfolderToggleChanged(checked) {
        this.state.uiState.createSubfolderEnabled = checked;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        this.updateDestinationPreview();
    }
    
    /**
     * Handle field input changed (real-time validation)
     * @param {string} fieldId - Field ID
     * @param {string} value - Field value
     */
    handleFieldInputChanged(fieldId, value) {
        const validationResult = this.validator.validateField(fieldId, value);
        
        if (validationResult.isValid) {
            this.ui.clearFieldError(fieldId);
        } else {
            this.ui.showFieldError(fieldId, validationResult.errorMessage);
        }
    }
    
    /**
     * Handle field value changed (after editing)
     * @param {string} fieldId - Field ID
     * @param {string} value - Field value
     */
    handleFieldValueChanged(fieldId, value) {
        this.validateField(fieldId, value);
        this.validateProjectStatus();
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Special case for archive ID changes - refresh auto-find results
        if (fieldId === 'archive-id' && 
            (this.state.uiState.autoFindPdfEnabled || this.state.uiState.autoFindComlistEnabled)) {
            this.refreshAutoFindResults();
        }
    }
    
    /**
     * Validate a specific field
     * @param {string} fieldId - ID of the field to validate
     * @param {string} value - Value to validate
     * @returns {boolean} - Whether the field is valid
     */
    validateField(fieldId, value) {
        const validationResult = this.validator.validateField(fieldId, value);
        
        // Update the appropriate state field
        if (fieldId === 'archive-id') {
            this.state.projectInfo.archiveId = value;
        } else if (fieldId === 'location') {
            this.state.projectInfo.location = value;
        } else if (fieldId === 'document-type') {
            this.state.projectInfo.documentType = value;
        }
        
        // Update UI based on validation result
        if (validationResult.isValid) {
            this.ui.clearFieldError(fieldId);
        } else {
            this.ui.showFieldError(fieldId, validationResult.errorMessage);
            this.ui.updateStatusBadge('error', `${fieldId.replace('-', ' ')} invalid`, 'both');
        }
        
        return validationResult.isValid;
    }
    
    /**
     * Validate the overall project status
     */
    validateProjectStatus() {
        const validationResult = this.validator.validateProjectStatus(
            this.state.projectInfo,
            this.state.sourceData.path,
            this.state.destinationPath
        );
        
        // Update project info validity state
        this.state.projectInfo.isValid = validationResult.isValid;
        
        // Update UI based on validation result
        if (!validationResult.isValid) {
            this.ui.updateStatusBadge('error', validationResult.errorMessage, 'both');
        } else {
            this.ui.updateStatusBadge('completed', 'Valid', 'both');
        }
    }
    
    /**
     * Refresh auto-find results (when archive ID changes)
     */
    refreshAutoFindResults() {
        if (this.state.sourceData.path) {
            if (this.state.uiState.autoFindPdfEnabled) {
                this.finders.findPdfFolder(this.state.sourceData, this.state.projectInfo);
            }
            
            if (this.state.uiState.autoFindComlistEnabled) {
                this.finders.findComlistFile(this.state.sourceData, this.state.projectInfo);
            }
        }
    }
    
    /**
     * Handle PDF folder found by auto-finder
     * @param {string} path - Found PDF folder path
     * @param {Object} warningInfo - Warning information
     */
    handlePdfFolderFound(path, warningInfo) {
        // Update state
        this.state.projectInfo.pdfPath = path;
        
        // Update UI
        this.ui.elements.pdfFolderDisplay.textContent = path;
        this.ui.updatePdfWarning(warningInfo);
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Log entry
        this.ui.addLogEntry(`Found potential PDF folder: ${path}`);
        if (warningInfo && warningInfo.hasWarning) {
            this.ui.addLogEntry(warningInfo.message);
        }
        
        // Removed automatic validation
    }
    
    /**
     * Handle PDF folder not found by auto-finder
     * @param {string} message - Error message
     * @param {boolean} isError - Whether this is an error (vs. warning)
     */
    handlePdfFolderNotFound(message, isError) {
        // Clear PDF path in state
        this.state.projectInfo.pdfPath = '';
        
        // Update UI
        this.ui.elements.pdfFolderDisplay.textContent = "Not set";
        this.ui.updatePdfWarning({
            hasWarning: true,
            message: message,
            type: isError ? "error" : "warning"
        });
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Log entry
        this.ui.addLogEntry(message);
        
        // Removed automatic validation
    }
    
    /**
     * Handle COMList file found by auto-finder
     * @param {string} path - Found COMList file path
     * @param {Object} warningInfo - Warning information
     */
    handleComlistFileFound(path, warningInfo) {
        // Update state
        this.state.projectInfo.comlistPath = path;
        
        // Update UI
        this.ui.elements.comlistFileDisplay.textContent = path;
        this.ui.updateComlistWarning(warningInfo);
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Log entry
        this.ui.addLogEntry(`Found potential COMList file: ${path}`);
        if (warningInfo && warningInfo.hasWarning) {
            this.ui.addLogEntry(warningInfo.message);
        }
        
        // Removed automatic validation
    }
    
    /**
     * Handle COMList file not found by auto-finder
     * @param {string} message - Error message
     * @param {boolean} isError - Whether this is an error (vs. warning)
     */
    handleComlistFileNotFound(message, isError) {
        // Clear COMList path in state
        this.state.projectInfo.comlistPath = '';
        
        // Update UI
        this.ui.elements.comlistFileDisplay.textContent = "Not set";
        this.ui.updateComlistWarning({
            hasWarning: true,
            message: message,
            type: isError ? "error" : "warning"
        });
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Log entry
        this.ui.addLogEntry(message);
        
        // Removed automatic validation
    }
    
    /**
     * Handles the validate button click - validates project and saves to database if valid
     */
    async handleValidateClicked() {
        this.ui.addLogEntry("Starting validation process...");
        
        // Perform full validation
        const validationResult = this.validator.validateAllRequirements({
            sourceData: this.state.sourceData,
            destinationPath: this.state.destinationPath,
            projectInfo: this.state.projectInfo,
            pdfWarningDisplay: this.ui.elements.pdfWarningDisplay,
            comlistWarningDisplay: this.ui.elements.comlistWarningDisplay
        });
        
        if (validationResult.valid) {
            this.ui.addLogEntry("Validation successful!");
            this.ui.updateStatusBadge('completed', 'Validation successful', 'both');
            this.ui.showNotification('Project validation successful', 'success');
            
            // Save to database
            this.ui.addLogEntry("Saving project to database...");
            try {
                const dbResult = await this.saveProjectToDatabase();
                
                if (dbResult.status === 'success') {
                    // Store the project ID for future reference
                    this.state.projectId = dbResult.project_id;
                    this.ui.showNotification(`Project saved to database (ID: ${dbResult.project_id})`, 'success');
                    this.ui.updateStatusBadge('completed', `Saved to database (ID: ${dbResult.project_id})`, 'both');
                    this.ui.addLogEntry(`Project saved to database with ID: ${dbResult.project_id}`);
                    
                    // Enable the next step button
                    if (this.ui.elements.toStep2Btn) {
                        this.ui.elements.toStep2Btn.disabled = false;
                        this.ui.addLogEntry("Next step button enabled - project validated and saved");
                    }
                    
                    // Show the reset button
                    if (this.ui.elements.resetStateBtn) {
                        this.ui.elements.resetStateBtn.style.display = 'inline-block';
                    }
                    
                    // Save state to localStorage
                    this.saveStateToStorage();
                } else {
                    // Database save failed
                    this.ui.showNotification('Failed to save project to database: ' + dbResult.message, 'error');
                    this.ui.updateStatusBadge('error', 'Database save failed', 'both');
                    this.ui.addLogEntry(`Database error: ${dbResult.message}`);
                }
            } catch (error) {
                console.error('Database save error:', error);
                this.ui.showNotification('Error saving to database: ' + error.message, 'error');
                this.ui.updateStatusBadge('error', 'Database error', 'both');
                this.ui.addLogEntry(`Database error: ${error.message}`);
            }
        } else {
            // Show validation errors
            this.ui.addLogEntry("Validation failed: " + validationResult.message);
            this.ui.showNotification('Validation failed: ' + validationResult.message, 'error');
            this.ui.updateStatusBadge('error', 'Validation failed', 'both');
            
            // Ensure next step button is disabled
            if (this.ui.elements.toStep2Btn) {
                this.ui.elements.toStep2Btn.disabled = true;
            }
        }
    }
    
    /**
     * Save the project to database
     * @returns {Promise<Object>} Database result
     */
    async saveProjectToDatabase() {
        try {
            // Create structured project data from current state
            const projectData = {
                archive_id: this.state.projectInfo.archiveId || '',
                location: this.state.projectInfo.location || '',
                doc_type: this.state.projectInfo.documentType || '',
                project_path: this.state.sourceData.path || '',
                project_folder_name: this.state.sourceData.folderName || '',
                comlist_path: this.state.projectInfo.comlistPath || null,
                output_dir: this.state.destinationPath || null,
                
                // Include processed metadata if available
                has_pdf_folder: !!this.state.projectInfo.pdfPath,
                pdf_folder_path: this.state.projectInfo.pdfPath || null,
            };
            
            this.ui.addLogEntry("Saving project to database...");
            
            // Use DatabaseService to make the request
            const result = await this.dbService.createProject(projectData);
            
            if (result.status === 'success') {
                this.ui.addLogEntry(`Project added to database with ID: ${result.project_id}`);
                return result;
            } else {
                this.ui.addLogEntry(`Failed to add project to database: ${result.message}`);
                return result;
            }
        } catch (error) {
            this.ui.addLogEntry(`Error adding project to database: ${error.message}`);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * The following methods are no longer used but kept as stubs for compatibility
     */
    startTransfer() {
        this.ui.addLogEntry("Transfer functionality has been replaced with validation");
    }
    
    async processTransfer() {
        this.ui.addLogEntry("Transfer functionality has been replaced with validation");
    }
    
    updateTransferProgress(progress) {
        // Empty stub for compatibility
    }
    
    handleCancelTransferClicked() {
        this.ui.addLogEntry("Cancel functionality has been removed");
    }
    
    async finishTransfer(status) {
        this.ui.addLogEntry("Transfer functionality has been replaced with validation");
    }

    /**
     * Handle navigation to the next workflow step
     * Called when the user clicks the "Continue to Document Analysis" button
     */
    handleNavigateToNextStep() {
        this.ui.addLogEntry("Navigating to document analysis step...");
        console.log("Navigation requested from: ", new Error().stack);
        
        // Ensure the current state is saved to localStorage
        this.saveStateToStorage();
        
        // Log project ID availability
        console.log("Project state before navigation:", {
            "Project ID in state": this.state.projectId,
            "Project info valid": this.state.projectInfo.isValid,
            "Full state": this.state
        });
        
        // Get the workflow state to access mode
        const workflowState = localStorage.getItem('microfilmWorkflowState') ? 
            JSON.parse(localStorage.getItem('microfilmWorkflowState')) : {};
        
        // Create the URL with parameters
        let nextUrl = '/register/document/';
        const urlWithParams = new URL(nextUrl, window.location.origin);
        
        // Add workflow mode if available
        if (workflowState && workflowState.workflowMode) {
            urlWithParams.searchParams.set('mode', workflowState.workflowMode);
        } else {
            urlWithParams.searchParams.set('mode', 'auto');
        }
        
        // Add project ID if available
        if (this.state.projectId) {
            urlWithParams.searchParams.set('id', this.state.projectId);
            this.ui.addLogEntry(`Adding project ID to URL: ${this.state.projectId}`);
            
            // Also update the workflow state with the project ID
            workflowState.projectId = this.state.projectId;
            localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        } else {
            this.ui.addLogEntry("Warning: No project ID available for navigation");
            console.warn("No project ID available for navigation to next step");
            
            // Check if we can find a project ID in the existing project state
            const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
            if (projectState && projectState.projectId) {
                urlWithParams.searchParams.set('id', projectState.projectId);
                this.ui.addLogEntry(`Using project ID from localStorage: ${projectState.projectId}`);
                
                // Also update the workflow state with the project ID
                workflowState.projectId = projectState.projectId;
                localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
            } else {
                this.ui.addLogEntry("Error: Could not find project ID in any storage");
                this.ui.showNotification("Error: No project ID found", "error");
            }
        }
        
        // Add step parameter (document analysis is step 2)
        urlWithParams.searchParams.set('step', '2');
        
        // Save the current state to sessionStorage for potential use in the next step
        try {
            const stateToSave = {
                projectId: this.state.projectId,
                sourcePath: this.state.sourceData.path,
                destinationPath: this.state.destinationPath,
                archiveId: this.state.projectInfo.archiveId,
                location: this.state.projectInfo.location,
                documentType: this.state.projectInfo.documentType
            };
            
            sessionStorage.setItem('projectState', JSON.stringify(stateToSave));
            this.ui.addLogEntry("Project state saved for next step");
            
            // Log the final URL for debugging
            this.ui.addLogEntry(`Navigating to: ${urlWithParams.toString()}`);
            console.log('Navigating to:', urlWithParams.toString());
            
            // Navigate to the next step with parameters
            window.location.href = urlWithParams.toString();
        } catch (error) {
            console.error('Error saving project state:', error);
            this.ui.addLogEntry("Warning: Could not save project state for next step");
            
            // Navigate anyway, just without the session storage
            window.location.href = urlWithParams.toString();
        }
    }
}
