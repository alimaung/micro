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
        
        // Initialize state
        this.state = this.getInitialState();
        
        // Set up event subscriptions
        this.initializeEventHandlers();
        
        // Log initialization
        this.ui.addLogEntry('Transfer system initialized');
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
            },
            addToDatabase: true
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
        
        // Start transfer button
        this.eventManager.subscribe('start-transfer-clicked', () => {
            this.handleStartTransferClicked();
        });
        
        // Cancel transfer button
        this.eventManager.subscribe('cancel-transfer-clicked', () => {
            this.handleCancelTransferClicked();
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
        
        // Add to database toggle
        this.eventManager.subscribe('add-to-database-toggle-changed', (data) => {
            this.state.addToDatabase = data.checked;
            this.ui.addLogEntry(`Database storage ${data.checked ? 'enabled' : 'disabled'}`);
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
            
            // Validate overall project status
            this.validateProjectStatus();
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
        this.validateProjectStatus();
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
        
        // Log entry
        this.ui.addLogEntry(`PDF folder selected: ${path}`);
        
        // Validate project status
        this.validateProjectStatus();
    }
    
    /**
     * Handle COMList file selected
     * @param {string} path - Selected COMList file path
     */
    handleComlistFileSelected(path) {
        // Update state
        this.state.projectInfo.comlistPath = path;
        
        // Log entry
        this.ui.addLogEntry(`COMList file selected: ${path}`);
        
        // Validate project status
        this.validateProjectStatus();
    }
    
    /**
     * Handle auto-parse toggle changed
     * @param {boolean} checked - Whether auto-parse is checked
     */
    handleAutoParseToggleChanged(checked) {
        this.state.uiState.autoParseEnabled = checked;
        this.ui.toggleFieldsEditability(!checked);
        
        if (checked && this.state.sourceData.folderName) {
            this.parseProjectInfo(this.state.sourceData.folderName);
        }
        
        this.validateProjectStatus();
    }
    
    /**
     * Handle auto-select path toggle changed
     * @param {boolean} checked - Whether auto-select path is checked
     */
    handleAutoSelectPathToggleChanged(checked) {
        this.state.uiState.autoSelectPathEnabled = checked;
        
        if (checked && this.state.sourceData.folderName) {
            this.updateDestinationPreview();
        }
        
        this.validateProjectStatus();
    }
    
    /**
     * Handle auto-find PDF toggle changed
     * @param {boolean} checked - Whether auto-find PDF is checked
     */
    handleAutoFindPdfToggleChanged(checked) {
        this.state.uiState.autoFindPdfEnabled = checked;
        
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
        
        this.validateProjectStatus();
    }
    
    /**
     * Handle auto-find COMList toggle changed
     * @param {boolean} checked - Whether auto-find COMList is checked
     */
    handleAutoFindComlistToggleChanged(checked) {
        this.state.uiState.autoFindComlistEnabled = checked;
        
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
        
        this.validateProjectStatus();
    }
    
    /**
     * Handle subfolder toggle changed
     * @param {boolean} checked - Whether create subfolder is checked
     */
    handleSubfolderToggleChanged(checked) {
        this.state.uiState.createSubfolderEnabled = checked;
        this.updateDestinationPreview();
        this.validateProjectStatus();
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
        
        // Log entry
        this.ui.addLogEntry(`Found potential PDF folder: ${path}`);
        if (warningInfo && warningInfo.hasWarning) {
            this.ui.addLogEntry(warningInfo.message);
        }
        
        // Validate project status
        this.validateProjectStatus();
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
        
        // Log entry
        this.ui.addLogEntry(message);
        
        // Validate project status
        this.validateProjectStatus();
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
        
        // Log entry
        this.ui.addLogEntry(`Found potential COMList file: ${path}`);
        if (warningInfo && warningInfo.hasWarning) {
            this.ui.addLogEntry(warningInfo.message);
        }
        
        // Validate project status
        this.validateProjectStatus();
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
        
        // Log entry
        this.ui.addLogEntry(message);
        
        // Validate project status
        this.validateProjectStatus();
    }
    
    /**
     * Handle start transfer button clicked
     */
    async handleStartTransferClicked() {
        // Perform full validation before starting transfer
        const validationResult = this.validator.validateAllRequirements({
            sourceData: this.state.sourceData,
            destinationPath: this.state.destinationPath,
            projectInfo: this.state.projectInfo,
            pdfWarningDisplay: this.ui.elements.pdfWarningDisplay,
            comlistWarningDisplay: this.ui.elements.comlistWarningDisplay
        });
        
        if (validationResult.valid) {
            // First save to database, then start transfer
            if (this.state.addToDatabase) {
                try {
                    this.ui.addLogEntry("Saving project to database before transfer...");
                    const dbResult = await this.saveProjectToDatabase();
                    
                    if (dbResult.status === 'success') {
                        // Store the project ID for future reference
                        this.state.projectId = dbResult.project_id;
                        this.ui.showNotification(`Project saved to database (ID: ${dbResult.project_id})`, 'success');
                        // Now start the transfer
                        this.startTransfer();
                    } else {
                        // Database save failed
                        this.ui.showNotification('Failed to save project to database. Transfer cancelled.', 'error');
                        this.ui.updateStatusBadge('error', 'Database save failed', 'both');
                    }
                } catch (error) {
                    console.error('Database save error:', error);
                    this.ui.showNotification('Error saving to database. Transfer cancelled.', 'error');
                    this.ui.updateStatusBadge('error', 'Database error', 'both');
                }
            } else {
                // If not saving to database, just start transfer
                this.startTransfer();
            }
        } else {
            // Show notification with summary message
            this.ui.showNotification('Transfer cannot start: ' + validationResult.message, 'error');
            
            // Update status badge to show error
            this.ui.updateStatusBadge('error', 'Validation errors found', 'both');
        }
    }
    
    /**
     * Start the transfer process
     */
    startTransfer() {
        // Disable UI controls during transfer
        this.disableUIControls();
        
        // Update status
        this.state.transferState = {
            status: 'in-progress',
            filesTransferred: 0,
            bytesTransferred: 0,
            speed: 0,
            startTime: Date.now(),
            cancelRequested: false
        };
        
        // Update UI
        this.ui.updateTransferStatus('in-progress', 'Transfer in Progress');
        this.ui.addLogEntry('Transfer started');
        
        // Start the transfer process
        this.processTransfer();
    }
    
    /**
     * Process the actual file transfer
     */
    async processTransfer() {
        try {
            // Ensure UI is ready by adding log entry first (will create UI elements if needed)
            this.ui.addLogEntry('Starting file transfer...');
            
            // Update UI to show transfer is starting
            this.ui.updateTransferStatus('in-progress', 'Transfer in Progress');
            
            // Start the actual transfer
            const result = await this.apiService.transferFiles(
                this.state.sourceData.path,
                this.state.destinationPath,
                this.state.sourceData.files,
                this.updateTransferProgress.bind(this)
            );
            
            // Handle transfer result
            if (result.status === 'completed') {
                // Transfer was successful
                this.finishTransfer('completed');
            } else if (result.status === 'cancelled') {
                this.finishTransfer('cancelled');
            } else {
                this.finishTransfer('error');
            }
        } catch (error) {
            console.error('Process transfer error:', error);
            this.ui.addLogEntry(`Transfer error: ${error.message}`);
            this.finishTransfer('error');
        }
    }
    
    /**
     * Update transfer progress
     * @param {Object} progress - Progress object from API
     */
    updateTransferProgress(progress) {
        // Format progress data
        if (progress.bytesTransferred !== undefined) {
            progress.bytesTransferredFormatted = this.utils.formatSize(progress.bytesTransferred);
        }
        
        if (progress.speed !== undefined) {
            progress.speedFormatted = `${this.utils.formatSize(progress.speed)}/s`;
        }
        
        if (progress.timeRemaining !== undefined) {
            progress.timeRemainingFormatted = this.utils.formatTime(progress.timeRemaining);
        }
        
        // Update UI
        this.ui.updateTransferProgress(progress);
        
        // Add log entry for completed file
        if (progress.fileCompleted) {
            this.ui.addLogEntry(`Transferred: ${progress.file} (${progress.fileSizeFormatted})`);
        }
    }
    
    /**
     * Handle cancel transfer button clicked
     */
    handleCancelTransferClicked() {
        if (this.state.transferState.status !== 'in-progress') return;
        
        this.state.transferState.cancelRequested = true;
        this.ui.elements.cancelTransferBtn.disabled = true;
        
        this.ui.updateTransferStatus('cancelled', 'Transfer Cancelled');
        this.ui.addLogEntry('Transfer cancelled by user');
        this.ui.showNotification('Transfer has been cancelled', 'warning');
    }
    
    /**
     * Finish the transfer with a status
     * @param {string} status - Status of the transfer (completed, error, cancelled)
     */
    async finishTransfer(status) {
        // Stop timer if active
        if (this.transferTimer) {
            clearInterval(this.transferTimer);
            this.transferTimer = null;
        }
        
        if (status === 'completed') {
            this.ui.updateTransferStatus('completed', 'Transfer Complete');
            this.ui.addLogEntry("Transfer completed successfully");
            
            // No database saving here anymore - it's done before transfer
            
            // Show completion notification
            this.ui.showNotification('Transfer completed successfully', 'success');
        } else if (status === 'cancelled') {
            this.ui.updateTransferStatus('cancelled', 'Transfer Cancelled');
            this.ui.addLogEntry("Transfer was cancelled by user");
            this.ui.showNotification('Transfer cancelled', 'warning');
        } else {
            this.ui.updateTransferStatus('error', 'Transfer Failed');
            this.ui.addLogEntry("Transfer failed with errors");
            this.ui.showNotification('Transfer failed. Check log for details.', 'error');
        }
        
        // Re-enable UI controls
        this.enableUIControls();
        
        // Update workflow state
        this.state.transferInProgress = false;
        this.state.transferComplete = status === 'completed';
    }
    
    /**
     * Disable UI controls during transfer
     */
    disableUIControls() {
        const elements = this.ui.elements;
        
        elements.sourceBrowseBtn.disabled = true;
        elements.destinationBrowseBtn.disabled = true;
        elements.pdfBrowseBtn.disabled = true;
        elements.comlistBrowseBtn.disabled = true;
        elements.createSubfolder.disabled = true;
        elements.autoParse.disabled = true;
        elements.autoSelectPath.disabled = true;
        elements.autoFindPdf.disabled = true;
        elements.autoFindComlist.disabled = true;
        elements.editButtons.forEach(button => button.disabled = true);
        
        elements.startTransferBtn.disabled = true;
        elements.cancelTransferBtn.disabled = false;
    }
    
    /**
     * Enable UI controls after transfer
     */
    enableUIControls() {
        const elements = this.ui.elements;
        const uiState = this.state.uiState;
        
        elements.sourceBrowseBtn.disabled = false;
        elements.destinationBrowseBtn.disabled = false;
        elements.pdfBrowseBtn.disabled = uiState.autoFindPdfEnabled;
        elements.comlistBrowseBtn.disabled = uiState.autoFindComlistEnabled;
        elements.createSubfolder.disabled = false;
        elements.autoParse.disabled = false;
        elements.autoSelectPath.disabled = false;
        elements.autoFindPdf.disabled = false;
        elements.autoFindComlist.disabled = false;
        elements.editButtons.forEach(button => button.disabled = false);
        
        elements.startTransferBtn.disabled = false;
        elements.cancelTransferBtn.disabled = true;
    }

    /**
     * Save the project to database
     * @returns {Promise<Object>} Database result
     */
    async saveProjectToDatabase() {
        if (!this.state.addToDatabase) {
            return { status: 'skipped', message: 'Database storage disabled by user' };
        }
        
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
                add_to_database: true,
                
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
                this.ui.addLogEntry(`Failed to add project to database: ${result.message}`, 'error');
                return result;
            }
        } catch (error) {
            this.ui.addLogEntry(`Error adding project to database: ${error.message}`, 'error');
            return { status: 'error', message: error.message };
        }
    }
}
