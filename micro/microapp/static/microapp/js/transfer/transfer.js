/**
 * transfer.js - Microfilm Transfer functionality
 * Handles importing projects from external drives to the system
 */

// Add CSS styles for warning messages
const styleElement = document.createElement('style');
styleElement.textContent = `
    .warning-message {
        font-size: 0.85rem;
        margin-top: 0.25rem;
        padding: 0.25rem 0.5rem;
        border-radius: 3px;
        display: block;
    }
    
    .warning-message.error {
        color: #fff;
        background-color: #ff453a;
    }
    
    .warning-message.warning {
        color: #fff;
        background-color: #ff9500;
    }
    
    .warning-message.success {
        color: #fff;
        background-color: #34c759;
    }
`;
document.head.appendChild(styleElement);

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing transfer functionality...');
    
    // Verify that required modules are loaded
    if (!FolderPicker) {
        console.error('ERROR: FolderPicker module not loaded');
        document.querySelector('.transfer-container').innerHTML = `
            <div style="padding: 20px; color: #ff453a; text-align: center;">
                <h2>Error Loading Transfer Interface</h2>
                <p>Required module FolderPicker failed to load. Please check the browser console for details.</p>
                <p>Try refreshing the page or contact support if the issue persists.</p>
            </div>
        `;
        return;
    }

    // --- DOM Elements ---
    const elements = {
        // Main status badge
        mainStatusBadge: document.getElementById('main-status-badge'),

        // Source elements
        sourceFolder: document.getElementById('source-folder'),
        sourceBrowseBtn: document.getElementById('source-browse-btn'),
        sourceFileCount: document.getElementById('source-file-count'),
        sourceSize: document.getElementById('source-size'),
        sourceFolderDisplay: document.getElementById('source-folder-display'),
        
        // Destination elements
        destinationFolder: document.getElementById('destination-folder'),
        destinationBrowseBtn: document.getElementById('destination-browse-btn'),
        createSubfolder: document.getElementById('create-subfolder'),
        destinationPathDisplay: document.getElementById('destination-path-display'),
        
        // PDF folder elements
        pdfFolder: document.getElementById('pdf-folder'),
        pdfBrowseBtn: document.getElementById('pdf-browse-btn'),
        pdfFolderDisplay: document.getElementById('pdf-folder-display'),
        pdfWarningDisplay: document.getElementById('pdf-warning-display'),
        
        // COMList file elements
        comlistFile: document.getElementById('comlist-file'),
        comlistBrowseBtn: document.getElementById('comlist-browse-btn'),
        comlistFileDisplay: document.getElementById('comlist-file-display'),
        comlistWarningDisplay: document.getElementById('comlist-warning-display'),
        
        // Option toggles
        autoParse: document.getElementById('auto-parse'),
        autoSelectPath: document.getElementById('auto-select-path'),
        autoFindPdf: document.getElementById('auto-find-pdf'),
        autoFindComlist: document.getElementById('auto-find-comlist'),
        
        // Project info elements
        archiveId: document.getElementById('archive-id'),
        archiveIdDisplay: document.getElementById('archive-id-display'),
        location: document.getElementById('location'),
        locationDisplay: document.getElementById('location-display'),
        documentType: document.getElementById('document-type'),
        documentTypeDisplay: document.getElementById('document-type-display'),
        projectInfoStatusBadge: document.getElementById('project-info-status'),
        editButtons: document.querySelectorAll('.edit-field'),
        
        // Transfer elements
        transferStatus: document.getElementById('transfer-status'),
        transferProgress: document.getElementById('transfer-progress'),
        progressPercentage: document.getElementById('progress-percentage'),
        filesTransferred: document.getElementById('files-transferred'),
        transferSpeed: document.getElementById('transfer-speed'),
        timeRemaining: document.getElementById('time-remaining'),
        currentFile: document.getElementById('current-file'),
        startTransferBtn: document.getElementById('start-transfer-btn'),
        cancelTransferBtn: document.getElementById('cancel-transfer-btn'),
        toggleLogBtn: document.getElementById('toggle-log'),
        transferLog: document.getElementById('transfer-log')
    };

    // --- Transfer Functions ---
    const TransferApp = {
        // State
        sourceData: {
            path: '',
            folderName: '',
            fileCount: 0,
            totalSize: 0,
            files: [],
            folderStructure: null
        },
        destinationPath: '', // Keep this empty initially
        defaultDestination: 'Y:', // Add a default destination to use when needed
        projectInfo: {
            archiveId: '',
            location: '',
            documentType: '',
            pdfPath: '',
            comlistPath: '',
            isValid: false
        },
        transferState: {
            status: 'initial', // initial, ready, in-progress, completed, error
            filesTransferred: 0,
            bytesTransferred: 0,
            speed: 0,
            startTime: null,
            cancelRequested: false
        },
        
        /**
         * Initialize the transfer application
         */
        initialize: function() {
            // Add a flag for tracking manual edits
            this._manualEdit = false;
            
            this.initializeEventListeners();
            
            // Set initial state for destination path display
            elements.destinationPathDisplay.textContent = 'Not set';
            this.initializeLogSection();
        },
        
        /**
         * Initialize event listeners
         */
        initializeEventListeners: function() {
            // Source folder button
            elements.sourceBrowseBtn.addEventListener('click', async () => {
                try {
                    const folderPicker = document.querySelector('.folder-picker-modal');
                    folderPicker.classList.add('show');
                    
                    // First select the source folder, without scanning subdirectories yet
                    const selectedResult = await FolderPicker.show(false, 'folders', null, 'Select Source Folder', false);
                    folderPicker.classList.remove('show');
                    
                    if (selectedResult && selectedResult.path) {
                        elements.sourceFolder.value = selectedResult.path;
                        this.sourceData.path = selectedResult.path;
                        
                        // After selecting the folder, now get its contents with subdirectories scanning
                        // We re-use the folder picker's utility to fetch only the contents of the selected folder
                        this.addLogEntry(`Getting structure of selected folder: ${selectedResult.path}...`);
                        
                        try {
                            // Make API call to scan just the selected folder structure
                            const apiEndpoint = '/list-drive-contents/?path=' + encodeURIComponent(selectedResult.path) + '&scan_subdirectories=true';
                            
                            // Fetch folder structure
                            const response = await fetch(apiEndpoint, {
                                method: 'GET',
                                headers: { 'Accept': 'application/json' }
                            });
                            
                            if (!response.ok) {
                                throw new Error(`Failed to get folder structure: ${response.statusText}`);
                            }
                            
                            const folderData = await response.json();
                            
                            // Store ONLY this folder's structure for auto-finding
                            this.sourceData.folderStructure = {
                                folders: folderData.folders || [],
                                files: folderData.files || [],
                                currentPath: folderData.currentPath || selectedResult.path,
                                fullStructure: folderData.fullStructure || null
                            };
                            
                            this.addLogEntry(`Found ${this.sourceData.folderStructure.folders.length} subfolders and ${this.sourceData.folderStructure.files.length} files in source folder`);
                        } catch (error) {
                            console.error('Error getting folder structure:', error);
                            this.showNotification('Failed to get folder structure for auto-finding', 'warning');
                            
                            // Fallback to basic folder info
                            this.sourceData.folderStructure = {
                                folders: selectedResult.folders || [],
                                files: selectedResult.files || [],
                                currentPath: selectedResult.currentPath || '',
                                fullStructure: null
                            };
                        }
                        
                        // This is the main function that sets the source folder
                        // and triggers auto-parse, auto-select, and auto-find features
                        this.updateSourceFolder(selectedResult.path);
                        
                        // Add an explicit message in the log about auto-find features
                        if (elements.autoFindPdf.checked || elements.autoFindComlist.checked) {
                            this.addLogEntry("Auto-find features are enabled and will be triggered");
                        }
                    }
                } catch (error) {
                    console.error('Error selecting folder:', error);
                    this.showNotification('Failed to select folder', 'error');
                }
            });
            
            // Destination folder button
            elements.destinationBrowseBtn.addEventListener('click', async () => {
                try {
                    const folderPicker = document.querySelector('.folder-picker-modal');
                    folderPicker.classList.add('show');
                    // Open directly to Y: drive
                    const selectedResult = await FolderPicker.show(false, 'folders', null, 'Select Destination Folder');
                    folderPicker.classList.remove('show');
                    if (selectedResult && selectedResult.path) {
                        elements.destinationFolder.value = selectedResult.path;
                        this.destinationPath = selectedResult.path;
                        this.updateDestinationPreview();
                        this.validateProjectStatus();
                    }
                } catch (error) {
                    console.error('Error selecting folder:', error);
                    this.showNotification('Failed to select destination folder', 'error');
                }
            });
            
            // PDF folder button
            elements.pdfBrowseBtn.addEventListener('click', async () => {
                try {
                    const folderPicker = document.querySelector('.folder-picker-modal');
                    folderPicker.classList.add('show');
                    // Allow selection of a folder for PDFs
                    const selectedResult = await FolderPicker.show(false, 'folders', null, 'Select PDF Folder');
                    folderPicker.classList.remove('show');
                    
                    if (selectedResult && selectedResult.path) {
                        // Disable auto-find if manually selecting a PDF folder
                        if (elements.autoFindPdf.checked) {
                            elements.autoFindPdf.checked = false;
                            this.addLogEntry("Auto-find PDF folder disabled due to manual selection");
                        }
                        
                        elements.pdfFolder.value = selectedResult.path;
                        elements.pdfFolderDisplay.textContent = selectedResult.path;
                        this.projectInfo.pdfPath = selectedResult.path;
                        
                        // Clear any warning messages when manually selecting
                        elements.pdfWarningDisplay.textContent = "";
                        elements.pdfWarningDisplay.className = "";
                        
                        this.addLogEntry(`PDF folder selected: ${selectedResult.path}`);
                        
                        // Enable the input field if a folder is selected
                        elements.pdfFolder.disabled = false;
                        this.validateProjectStatus();
                    }
                } catch (error) {
                    console.error('Error selecting PDF folder:', error);
                    this.showNotification('Failed to select PDF folder', 'error');
                }
            });
            
            // COMList file button
            elements.comlistBrowseBtn.addEventListener('click', async () => {
                try {
                    const folderPicker = document.querySelector('.folder-picker-modal');
                    folderPicker.classList.add('show');
                    // Allow selection of only Excel files (.xlsx and .xls)
                    const selectedResult = await FolderPicker.show(false, 'files', ['xlsx', 'xls', 'xlsm'], 'Select COMList File');
                    folderPicker.classList.remove('show');
                    
                    if (selectedResult && selectedResult.path) {
                        // Disable auto-find if manually selecting a COMList file
                        if (elements.autoFindComlist.checked) {
                            elements.autoFindComlist.checked = false;
                            this.addLogEntry("Auto-find COMList file disabled due to manual selection");
                        }
                        
                        elements.comlistFile.value = selectedResult.path;
                        elements.comlistFileDisplay.textContent = selectedResult.path;
                        this.projectInfo.comlistPath = selectedResult.path;
                        
                        // Clear any warning messages when manually selecting
                        elements.comlistWarningDisplay.textContent = "";
                        elements.comlistWarningDisplay.className = "";
                        
                        this.addLogEntry(`COMList file selected: ${selectedResult.path}`);
                        
                        // Enable the input field if a file is selected
                        elements.comlistFile.disabled = false;
                        this.validateProjectStatus();
                    }
                } catch (error) {
                    console.error('Error selecting COMList file:', error);
                    this.showNotification('Failed to select COMList file', 'error');
                }
            });
            
            // Create subfolder toggle
            elements.createSubfolder.addEventListener('change', () => {
                this.updateDestinationPreview();
                this.validateProjectStatus();
            });
            
            // Auto-parse toggle
            elements.autoParse.addEventListener('change', () => {
                const isAutoParse = elements.autoParse.checked;
                this.toggleFieldsEditability(!isAutoParse);
                console.log(this.sourceData.folderName);
                
                if (isAutoParse && this.sourceData.folderName) {
                    this.parseProjectInfo(this.sourceData.folderName);
                }
                
                this.validateProjectStatus();
            });
            
            // Auto-select path toggle
            elements.autoSelectPath.addEventListener('change', () => {
                // If turned on and we have a source folder, update the destination preview
                if (elements.autoSelectPath.checked && this.sourceData.folderName) {
                    this.updateDestinationPreview();
                }
                this.validateProjectStatus();
            });
            
            // Auto-find PDF folder toggle
            elements.autoFindPdf.addEventListener('change', () => {
                if (elements.autoFindPdf.checked) {
                    this.addLogEntry("Auto-find PDF folder toggled on - will be triggered when selecting a source folder");
                    
                    // Disable PDF browse button when auto-find is enabled
                    elements.pdfBrowseBtn.disabled = elements.autoFindPdf.checked;
                    
                    // Only call PDF folder detection if source path is already set
                    if (this.sourceData.path) {
                        this.findPdfFolder();
                    } else {
                        this.addLogEntry("Select a source folder to activate auto-find PDF folder");
                    }
                } else {
                    elements.pdfBrowseBtn.disabled = false;
                    elements.pdfWarningDisplay.textContent = "";
                    elements.pdfWarningDisplay.className = "";
                    this.addLogEntry("Auto-find PDF folder toggled off");
                }
                this.validateProjectStatus();
            });
            
            // Auto-find COMList toggle
            elements.autoFindComlist.addEventListener('change', () => {
                if (elements.autoFindComlist.checked) {
                    this.addLogEntry("Auto-find COMList file toggled on - will be triggered when selecting a source folder");
                    
                    // Disable COMList browse button when auto-find is enabled
                    elements.comlistBrowseBtn.disabled = elements.autoFindComlist.checked;
                    
                    // Only call comlist file detection if source path is already set
                    if (this.sourceData.path) {
                        this.findComlistFile(this.sourceData.path);
                    } else {
                        this.addLogEntry("Select a source folder to activate auto-find COMList file");
                    }
                } else {
                    elements.comlistBrowseBtn.disabled = false;
                    elements.comlistWarningDisplay.textContent = "";
                    elements.comlistWarningDisplay.className = "";
                    this.addLogEntry("Auto-find COMList file toggled off");
                }
                this.validateProjectStatus();
            });
            
            // Field edit buttons - only for archive, location, document type
            elements.editButtons.forEach(button => {
                const fieldId = button.getAttribute('data-field');
                // Only attach event listeners to editable fields
                if (fieldId === 'archive-id' || fieldId === 'location' || fieldId === 'document-type') {
                    button.addEventListener('click', (e) => {
                        const displayId = button.getAttribute('data-display');
                        const field = document.getElementById(fieldId);
                        const container = button.closest('.field-value-container');
                        
                        // If already in edit mode, save the changes
                        if (container.classList.contains('editing')) {
                            // Update display value with input value
                            const displayEl = document.getElementById(displayId);
                            const value = field.value.trim();
                            displayEl.textContent = value || 'Not set';
                            
                            // Exit edit mode
                            container.classList.remove('editing');
                            
                            // Validate this specific field
                            this.validateField(fieldId, value);
                        } else {
                            // Close any other open editors
                            document.querySelectorAll('.field-value-container.editing').forEach(el => {
                                if (el !== container) {
                                    el.classList.remove('editing');
                                }
                            });
                            
                            // Enter edit mode
                            container.classList.add('editing');
                            
                            // Make field editable
                            field.disabled = false;
                            field.focus();
                            
                            // Set field value from display value
                            const displayEl = document.getElementById(displayId);
                            if (displayEl.textContent !== 'Not set') {
                                field.value = displayEl.textContent;
                            }
                        }
                    });
                }
            });
            
            // Manual info inputs - handle blur/enter to finish editing
            const infoFields = [
                elements.archiveId, 
                elements.location, 
                elements.documentType
            ];
            
            infoFields.forEach(field => {
                // On input, mark as manually edited and validate in real-time
                field.addEventListener('input', () => {
                    this._manualEdit = true;
                    // Validate this field as typing occurs
                    this.validateField(field.id, field.value.trim());
                });
                
                // On blur, save the changes
                field.addEventListener('blur', () => {
                    const container = field.closest('.field-value-container');
                    if (container && container.classList.contains('editing')) {
                        const displayId = container.querySelector('.edit-field').getAttribute('data-display');
                        const displayEl = document.getElementById(displayId);
                        
                        const value = field.value.trim();
                        displayEl.textContent = value || 'Not set';
                        
                        // Exit edit mode
                        container.classList.remove('editing');
                        
                        // Ensure validation happens
                        this._manualEdit = true;
                        this.validateField(field.id, value);/* 
                        
                        // If this is the Archive ID field and it was changed, refresh auto-find results
                        if (field.id === 'archive-id') {
                            this.refreshAutoFindResults();
                        } */
                    }
                });
                
                // On enter key, save changes
                field.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        field.blur();
                    }
                });
            });
            
            // Start transfer button - now always enabled, will trigger validation
            elements.startTransferBtn.addEventListener('click', () => {
                // Perform a full validation before starting transfer
                const validationResult = this.validateAllRequirements();
                if (validationResult.valid) {
                    this.startTransfer();
                } else {
                    // Show notification with summary message
                    let errorMessage = 'Transfer cannot start: ';
                    
                    if (validationResult.errors['source']) {
                        errorMessage += 'Source folder required. ';
                    }
                    
                    if (validationResult.errors['destination']) {
                        errorMessage += 'Destination path required. ';
                    }
                    
                    if (validationResult.errors['archive-id'] || 
                        validationResult.errors['location'] || 
                        validationResult.errors['document-type']) {
                        errorMessage += 'Fix project information errors. ';
                    }
                    
                    this.showNotification(errorMessage, 'error');
                    
                    // Update status badge to show error
                    this.updateProjectStatusBadge('error', 'Validation errors found', 'both');
                }
            });
            
            // Cancel transfer button
            elements.cancelTransferBtn.addEventListener('click', () => this.cancelTransfer());
            
            // Toggle log button
            elements.toggleLogBtn.addEventListener('click', () => {
                elements.toggleLogBtn.classList.toggle('expanded');
                elements.transferLog.classList.toggle('expanded');
            });
        },
        
        /**
         * Toggle the editability of project info fields
         * @param {boolean} enabled - Whether fields should be editable
         */
        toggleFieldsEditability: function(enabled) {
            elements.archiveId.disabled = !enabled;
            elements.location.disabled = !enabled;
            elements.documentType.disabled = !enabled;
            
            // Close any open editors
            document.querySelectorAll('.field-value-container.editing').forEach(container => {
                container.classList.remove('editing');
            });
        },
        
        /**
         * Initialize log section
         */
        initializeLogSection: function() {
            this.addLogEntry('Transfer system initialized');
        },
        
        /**
         * Update source folder information
         * @param {string} path - Selected source folder path
         */
        updateSourceFolder: function(path) {
            this.sourceData.path = path;
            
            // Extract folder name from path
            const pathParts = path.split('\\');
            this.sourceData.folderName = pathParts[pathParts.length - 1];
            
            // Update the source folder display
            elements.sourceFolderDisplay.textContent = path;
            
            // Get file statistics from server
            this.getFileStats().then(stats => {
                this.sourceData.fileCount = stats.fileCount;
                this.sourceData.totalSize = stats.totalSize;
                this.sourceData.files = stats.files;
                
                // Update UI
                elements.sourceFileCount.textContent = stats.fileCount;
                elements.sourceSize.textContent = this.formatSize(stats.totalSize);
                
                // Only update destination preview if auto-select path is enabled
                if (elements.autoSelectPath.checked) {
                    this.updateDestinationPreview();
                }
                
                // Parse project info if auto-parse is enabled
                if (elements.autoParse.checked) {
                    this.parseProjectInfo(this.sourceData.folderName);
                }
                
                // Try to auto-find PDF folder if that option is enabled
                if (elements.autoFindPdf.checked) {
                    this.findPdfFolder();
                }
                
                // Try to auto-find COMList file if that option is enabled
                if (elements.autoFindComlist.checked) {
                    this.findComlistFile(path);
                }
                
                // Update project status
                this.validateProjectStatus();
                
                this.addLogEntry(`Source folder selected: ${path}`);
                this.addLogEntry(`Found ${stats.fileCount} files (${this.formatSize(stats.totalSize)})`);
            }).catch(error => {
                console.error('Error getting file statistics:', error);
                this.showNotification('Failed to get file statistics', 'error');
            });
        },
        
        /**
         * Get file statistics from server
         * @returns {Promise<Object>} - File stats
         */
        getFileStats: function() {
            return new Promise((resolve, reject) => {
                // Get source path
                const path = this.sourceData.path;
                if (!path) {
                    reject(new Error('No source path specified'));
                    return;
                }
                
                // Make API call to get file statistics
                const apiEndpoint = '/get-file-statistics/?path=' + encodeURIComponent(path);
                
                fetch(apiEndpoint, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to get file statistics. Status: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    resolve({
                        fileCount: data.fileCount,
                        totalSize: data.totalSize,
                        files: data.files
                    });
                })
                .catch(error => {
                    console.error('Error getting file statistics:', error);
                    reject(error);
                });
            });
        },
        
        /**
         * Mock getting file stats (would be a server call in real implementation)
         * @returns {Promise<Object>} - File stats
         * @deprecated Use getFileStats instead
         */
        mockGetFileStats: function() {
            console.warn('mockGetFileStats is deprecated. Use getFileStats instead.');
            return new Promise(resolve => {
                // Simulate server delay
                setTimeout(() => {
                    // Random number of files between 1 and 100
                    const fileCount = Math.floor(Math.random() * 100) + 1;
                    // Random size between 1MB and 1GB
                    const totalSize = Math.floor(Math.random() * 1000000000) + 1000000;
                    
                    // Generate mock file list
                    const files = [];
                    for (let i = 0; i < fileCount; i++) {
                        files.push({
                            name: `file_${i}.pdf`,
                            size: Math.floor(Math.random() * 10000000) + 100000
                        });
                    }
                    
                    resolve({
                        fileCount,
                        totalSize,
                        files
                    });
                }, 500);
            });
        },
        
        /**
         * Update destination preview
         */
        updateDestinationPreview: function() {
            // Use the default destination if the actual destination folder is empty
            const basePath = elements.destinationFolder.value || this.defaultDestination;
            let finalPath = basePath;
            
            if (elements.createSubfolder.checked && this.sourceData.folderName) {
                // Ensure the base path ends with a backslash
                const basePathWithSeparator = basePath.endsWith('\\') ? basePath : basePath + '\\';
                finalPath = `${basePathWithSeparator}${this.sourceData.folderName}\\`;
            }
            
            elements.destinationPathDisplay.textContent = finalPath;
            this.destinationPath = finalPath;
        },
        
        /**
         * Parse project information from folder name
         * Format: RRDXXX-YYYY_LOCATION_DOCTYPE
         * @param {string} folderName - Folder name to parse
         */
        parseProjectInfo: function(folderName) {
            // Match the pattern RRDXXX-YYYY_LOCATION_DOCTYPE
            const regex = /^(RRD\d{3}-\d{4})_([A-Z]+)_(.+)$/;
            const match = folderName.match(regex);
            
            if (match) {
                const [_, archiveId, location, docType] = match;
                
                // Keep any existing PDF and COMList paths when parsing
                const pdfPath = this.projectInfo.pdfPath || '';
                const comlistPath = this.projectInfo.comlistPath || '';
                
                this.projectInfo = {
                    archiveId: archiveId,
                    location: location,
                    documentType: docType,
                    pdfPath: pdfPath,            // Preserve this value
                    comlistPath: comlistPath,    // Preserve this value
                    isValid: false               // Will be validated later
                };
                
                // Update UI - both inputs and displays
                elements.archiveId.value = archiveId;
                elements.archiveIdDisplay.textContent = archiveId;
                
                elements.location.value = location;
                elements.locationDisplay.textContent = location;
                
                elements.documentType.value = docType;
                elements.documentTypeDisplay.textContent = docType;
                
                // Validate each field individually
                this.validateField('archive-id', archiveId);
                this.validateField('location', location);
                this.validateField('document-type', docType);
                
                /* // Refresh auto-find results with the new archive ID
                this.refreshAutoFindResults(); */
                
                // Then validate overall status
                this.validateProjectStatus();
                
                this.addLogEntry(`Project info parsed: ID=${archiveId}, Location=${location}, Type=${docType}`);
            } else {
                this.projectInfo = {
                    archiveId: '',
                    location: '',
                    documentType: '',
                    pdfPath: this.projectInfo.pdfPath || '',        // Preserve this value
                    comlistPath: this.projectInfo.comlistPath || '', // Preserve this value
                    isValid: false
                };
                
                // Clear only the auto-parsed fields
                elements.archiveId.value = '';
                elements.archiveIdDisplay.textContent = 'Not set';
                
                elements.location.value = '';
                elements.locationDisplay.textContent = 'Not set';
                
                elements.documentType.value = '';
                elements.documentTypeDisplay.textContent = 'Not set';
                
                // Clear any error states
                this.clearFieldError('archive-id');
                this.clearFieldError('location');
                this.clearFieldError('document-type');
                
                this.addLogEntry('Failed to parse project information from folder name');
                this.updateProjectStatusBadge('error', 'Could not parse project info from folder name', 'both');
            }
        },
        
        /**
         * Validate a specific field
         * @param {string} fieldId - ID of the field to validate
         * @param {string} value - Value to validate
         * @returns {boolean} - Whether the field is valid
         */
        validateField: function(fieldId, value) {
            let isValid = false;
            let errorMessage = '';
            
            switch(fieldId) {
                case 'archive-id':
                    // Check if Archive ID matches pattern RRDxxx-yyyy
                    const archiveIdPattern = /^RRD\d{3}-\d{4}$/;
                    isValid = archiveIdPattern.test(value);
                    if (!isValid) {
                        errorMessage = 'Invalid format. Must be RRDxxx-yyyy';
                        this.updateProjectStatusBadge('error', 'Archive ID invalid', 'both');
                    }
                    this.projectInfo.archiveId = value;
                    break;
                    
                case 'location':
                    // Check if location is either OU or DW
                    isValid = value === 'OU' || value === 'DW';
                    if (!isValid) {
                        errorMessage = 'Must be either OU or DW';
                        this.updateProjectStatusBadge('error', 'Location invalid', 'both');
                    }
                    this.projectInfo.location = value;
                    break;
                    
                case 'document-type':
                    // Check if document type is not empty
                    isValid = value.length > 0;
                    if (!isValid) {
                        errorMessage = 'Document type cannot be empty';
                        this.updateProjectStatusBadge('error', 'Document type invalid', 'both');
                    }
                    this.projectInfo.documentType = value;
                    break;
            }
            
            // Update field UI based on validation result
            if (isValid) {
                this.clearFieldError(fieldId);
            } else {
                this.showFieldError(fieldId, errorMessage);
            }
            return isValid;
        },
        
        /**
         * Show error for a field
         * @param {string} fieldId - ID of the field
         * @param {string} message - Error message
         */
        showFieldError: function(fieldId, message) {
            const field = document.getElementById(fieldId);
            const container = field.closest('.field-value-container');
            const projectField = container.closest('.project-field');
            
            // Add error class to field
            field.classList.add('error');
            
            // Add error class to the project field container
            if (projectField) {
                projectField.classList.add('has-error');
            }
            
            // Create or update error message
            let errorElement = container.querySelector('.field-error');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'field-error';
                container.appendChild(errorElement);
            }
            errorElement.textContent = message;
        },
        
        /**
         * Clear error for a field
         * @param {string} fieldId - ID of the field
         */
        clearFieldError: function(fieldId) {
            const field = document.getElementById(fieldId);
            const container = field.closest('.field-value-container');
            const projectField = container.closest('.project-field');
            
            // Remove error class from field
            field.classList.remove('error');
            
            // Remove error class from project field container
            if (projectField) {
                projectField.classList.remove('has-error');
            }
            
            // Remove error message if exists
            const errorElement = container.querySelector('.field-error');
            if (errorElement) {
                errorElement.remove();
            }
        },
        
        /**
         * Validate the overall project status
         */
        validateProjectStatus: function() {
            // Check individual field validations
            const archiveIdValid = this.validateField('archive-id', elements.archiveId.value.trim());
            const locationValid = this.validateField('location', elements.location.value.trim());
            const docTypeValid = this.validateField('document-type', elements.documentType.value.trim());
            
            // Check if source path is set
            const sourceValid = this.sourceData.path !== '';
            
            // Check if destination path is set
            const destinationValid = this.destinationPath && this.destinationPath !== '';
            
            // Project info is valid if all three editable fields are valid
            const projectInfoValid = archiveIdValid && locationValid && docTypeValid;
            this.projectInfo.isValid = projectInfoValid;
            
            // All required paths and info are valid
            const allValid = sourceValid && destinationValid && projectInfoValid;
            
            if (!sourceValid) {
                this.updateProjectStatusBadge('error', 'Source invalid', 'both');
            } else if (!destinationValid) {
                this.updateProjectStatusBadge('error', 'Destination invalid', 'both');
            } else if (!projectInfoValid) {
                this.updateProjectStatusBadge('error', 'Project invalid', 'both');
            } else {
                this.updateProjectStatusBadge('completed', 'Valid', 'both');
            }
        },
        
        /**
         * Update the project status badge in the card header
         * @param {string} status - Status class (initial, pending, completed, error)
         * @param {string} message - Status message
         * @param {string} target - Which badge(s) to update ('main', 'info', or 'both')
         */
        updateProjectStatusBadge: function(status, message, target = 'both') {
            let icon = 'clock';
            if (status === 'completed') icon = 'check-circle';
            if (status === 'error') icon = 'exclamation-circle';
            if (status === 'pending') icon = 'sync';
            
            const badgeHtml = `<i class="fas fa-${icon}"></i> ${message}`;
            
            if (target === 'main' || target === 'both') {
                elements.mainStatusBadge.className = `status-badge ${status}`;
                elements.mainStatusBadge.innerHTML = badgeHtml;
            }
            
            if (target === 'info' || target === 'both') {
                elements.projectInfoStatusBadge.className = `status-badge ${status}`;
                elements.projectInfoStatusBadge.innerHTML = badgeHtml;
            }
        },
        
        /**
         * Validate all requirements before starting transfer
         * @returns {Object} - Validation result with valid flag, errors object, and message
         */
        validateAllRequirements: function() {
            const result = {
                valid: true,
                errors: {},
                message: ''
            };
            
            // Check source path
            if (!this.sourceData.path) {
                result.valid = false;
                result.errors['source'] = 'Source folder not selected';
                result.message += 'Source folder required. ';
            }
            
            // Check destination path
            if (!this.destinationPath) {
                result.valid = false;
                result.errors['destination'] = 'Destination path not set';
                result.message += 'Destination path required. ';
            }
            
            // Check archive ID
            const archiveId = elements.archiveId.value.trim();
            const archiveIdPattern = /^RRD\d{3}-\d{4}$/;
            const archiveIdValid = archiveIdPattern.test(archiveId);
            if (!archiveIdValid) {
                result.valid = false;
                result.errors['archive-id'] = 'Invalid Archive ID format';
                result.message += 'Valid Archive ID required. ';
                // Directly show error
                this.showFieldError('archive-id', 'Invalid format. Must be RRDxxx-yyyy');
            } else {
                this.clearFieldError('archive-id');
            }
            
            // Check location
            const location = elements.location.value.trim();
            const locationValid = location === 'OU' || location === 'DW';
            if (!locationValid) {
                result.valid = false;
                result.errors['location'] = 'Location must be OU or DW';
                result.message += 'Valid Location required. ';
                // Directly show error
                this.showFieldError('location', 'Must be either OU or DW');
            } else {
                this.clearFieldError('location');
            }
            
            // Check document type
            const documentType = elements.documentType.value.trim();
            const docTypeValid = documentType.length > 0;
            if (!docTypeValid) {
                result.valid = false;
                result.errors['document-type'] = 'Document type required';
                result.message += 'Document type required. ';
                // Directly show error
                this.showFieldError('document-type', 'Document type cannot be empty');
            } else {
                this.clearFieldError('document-type');
            }
            
            // Check PDF path if there are error messages
            if (elements.pdfWarningDisplay.className === "warning-message error") {
                result.valid = false;
                result.errors['pdf-folder'] = 'PDF folder error';
                result.message += 'Fix PDF folder errors. ';
            }
            
            // Check COMList path if there are error messages
            if (elements.comlistWarningDisplay.className === "warning-message error") {
                result.valid = false;
                result.errors['comlist-file'] = 'COMList file error';
                result.message += 'Fix COMList file errors. ';
            }
            
            return result;
        },
        
        /**
         * Start the transfer process
         */
        startTransfer: function() {
            // Disable UI elements during transfer
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
            
            this.addLogEntry('Transfer started');
            
            // Update status
            this.transferState = {
                status: 'in-progress',
                filesTransferred: 0,
                bytesTransferred: 0,
                speed: 0,
                startTime: Date.now(),
                cancelRequested: false
            };
            
            const headerStatusBadge = document.querySelector('.transfer-header .status-badge');
            headerStatusBadge.className = 'status-badge pending';
            headerStatusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Transfer in Progress';
            
            elements.transferStatus.className = 'status-badge pending';
            elements.transferStatus.innerHTML = '<i class="fas fa-sync fa-spin"></i> In Progress';
            
            // Update project info status
            this.updateProjectStatusBadge('pending', 'Transfer in progress', 'both');
            
            // Enable cancel button and disable start button
            elements.cancelTransferBtn.disabled = false;
            elements.startTransferBtn.disabled = true;
            
            // Start the mock transfer
            this.mockTransferProcess();
        },
        
        /**
         * Mock transfer process - uses real file data from the source
         */
        mockTransferProcess: function() {
            // Use a timeout to simulate the transfer
            const files = this.sourceData.files;
            const totalFiles = files.length;
            
            // No files to transfer
            if (totalFiles === 0) {
                this.addLogEntry("No files found to transfer");
                this.finishTransfer('completed');
                return;
            }
            
            const totalBytes = this.sourceData.totalSize;
            let filesTransferred = 0;
            let bytesTransferred = 0;
            
            // Process each file with a delay
            const processNextFile = () => {
                // Check if cancel was requested
                if (this.transferState.cancelRequested) {
                    this.finishTransfer('cancelled');
                    return;
                }
                
                // If all files have been processed, we're done
                if (filesTransferred >= totalFiles) {
                    this.finishTransfer('completed');
                    return;
                }
                
                // Get the next file
                const file = files[filesTransferred];
                
                // Update UI to show current file
                elements.currentFile.textContent = file.name;
                
                // Calculate a random delay based on file size (100KB to 1MB per second)
                const bytesPerSecond = 100000 + Math.random() * 900000;
                const fileDelayMs = (file.size / bytesPerSecond) * 1000;
                
                // Update progress during the file transfer
                const updateInterval = Math.min(100, fileDelayMs / 10);
                let fileProgress = 0;
                
                const fileInterval = setInterval(() => {
                    // Don't update progress if cancelled
                    if (this.transferState.cancelRequested) {
                        clearInterval(fileInterval);
                        return;
                    }
                    
                    // Update file progress
                    fileProgress += updateInterval / fileDelayMs;
                    if (fileProgress > 1) fileProgress = 1;
                    
                    // Calculate overall progress
                    const currentBytes = bytesTransferred + (file.size * fileProgress);
                    const overallProgress = currentBytes / totalBytes;
                    
                    // Update progress bars
                    elements.progressBar.style.width = `${overallProgress * 100}%`;
                    elements.progressPercent.textContent = `${Math.round(overallProgress * 100)}%`;
                    
                    // Update bytes transferred
                    elements.bytesTransferred.textContent = this.formatSize(currentBytes);
                    
                    // Calculate speed (bytes per second)
                    const elapsedSec = (Date.now() - this.transferState.startTime) / 1000;
                    const speed = currentBytes / elapsedSec;
                    
                    // Update transfer status with speed
                    elements.transferSpeed.textContent = `${this.formatSize(speed)}/s`;
                    
                    // Calculate ETA
                    const remainingBytes = totalBytes - currentBytes;
                    const etaSec = remainingBytes / speed;
                    elements.transferETA.textContent = this.formatTime(etaSec);
                    
                }, updateInterval);
                
                // When the file is done
                setTimeout(() => {
                    clearInterval(fileInterval);
                    
                    // Add the file size to bytes transferred
                    bytesTransferred += file.size;
                    filesTransferred += 1;
                    
                    // Update the counter
                    elements.filesTransferred.textContent = `${filesTransferred}/${totalFiles}`;
                    
                    // Add log entry
                    this.addLogEntry(`Transferred: ${file.name} (${this.formatSize(file.size)})`);
                    
                    // Process the next file
                    processNextFile();
                    
                }, fileDelayMs);
            };
            
            // Start processing files
            processNextFile();
        },
        
        /**
         * Cancel the transfer process
         */
        cancelTransfer: function() {
            if (this.transferState.status !== 'in-progress') return;
            
            this.transferState.cancelRequested = true;
            elements.cancelTransferBtn.disabled = true;
            
            const headerStatusBadge = document.querySelector('.transfer-header .status-badge');
            headerStatusBadge.className = 'status-badge error';
            headerStatusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Transfer Cancelled';
            
            elements.transferStatus.className = 'status-badge error';
            elements.transferStatus.innerHTML = '<i class="fas fa-times-circle"></i> Cancelled';
            
            this.addLogEntry('Transfer cancelled by user');
            this.showNotification('Transfer has been cancelled', 'warning');
        },
        
        /**
         * Finish the transfer with a status
         * @param {string} status - Status of the transfer (completed, error, cancelled)
         */
        finishTransfer: function(status) {
            // Re-enable UI elements
            elements.sourceBrowseBtn.disabled = false;
            elements.destinationBrowseBtn.disabled = false;
            elements.pdfBrowseBtn.disabled = elements.autoFindPdf.checked;
            elements.comlistBrowseBtn.disabled = elements.autoFindComlist.checked; 
            elements.startTransferBtn.disabled = false;
            elements.createSubfolder.disabled = false;
            elements.autoParse.disabled = false;
            elements.autoSelectPath.disabled = false;
            elements.autoFindPdf.disabled = false;
            elements.autoFindComlist.disabled = false;
            elements.editButtons.forEach(button => button.disabled = false);
            
            // Disable cancel button
            elements.cancelTransferBtn.disabled = true;
            
            // Update status badge
            const headerStatusBadge = document.querySelector('.transfer-header .status-badge');
            elements.transferStatus.className = `status-badge ${status}`;
            
            // Update project info status
            if (status === 'completed') {
                this.updateProjectStatusBadge('completed', 'Transfer completed', 'both');
            } else if (status === 'cancelled') {
                this.updateProjectStatusBadge('error', 'Transfer cancelled', 'both');
            } else {
                this.updateProjectStatusBadge('error', 'Transfer failed', 'both');
            }
            
            let message = '';
            switch (status) {
                case 'completed':
                    headerStatusBadge.className = 'status-badge completed';
                    headerStatusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Transfer Complete';
                    
                    elements.transferStatus.innerHTML = '<i class="fas fa-check-circle"></i> Completed';
                    message = 'Transfer completed successfully';
                    
                    // Update progress bar to 100%
                    elements.transferProgress.style.width = '100%';
                    elements.progressPercentage.textContent = '100%';
                    
                    break;
                    
                case 'error':
                    headerStatusBadge.className = 'status-badge error';
                    headerStatusBadge.innerHTML = '<i class="fas fa-exclamation-circle"></i> Transfer Failed';
                    
                    elements.transferStatus.innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed';
                    message = 'Transfer failed due to an error';
                    break;
                    
                case 'cancelled':
                    headerStatusBadge.className = 'status-badge error';
                    headerStatusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Transfer Cancelled';
                    
                    elements.transferStatus.innerHTML = '<i class="fas fa-times-circle"></i> Cancelled';
                    message = 'Transfer was cancelled';
                    break;
            }
            
            // Add log entry
            this.addLogEntry(message);
            
            // Show notification
            this.showNotification(message, status === 'completed' ? 'success' : 'error');
            
            // Update transferState
            this.transferState.status = status;
        },
        
        /**
         * Add a log entry
         * @param {string} message - Log message
         */
        addLogEntry: function(message) {
            const now = new Date();
            const timeString = now.toTimeString().split(' ')[0];
            
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <span class="log-time">${timeString}</span>
                <span class="log-message">${message}</span>
            `;
            
            elements.transferLog.appendChild(logEntry);
            elements.transferLog.scrollTop = elements.transferLog.scrollHeight;
        },
        
        /**
         * Format file size to human-readable format
         * @param {number} bytes - Size in bytes
         * @returns {string} - Formatted size string
         */
        formatSize: function(bytes) {
            const units = ['B', 'KB', 'MB', 'GB', 'TB'];
            let size = bytes;
            let unitIndex = 0;
            
            while (size >= 1024 && unitIndex < units.length - 1) {
                size /= 1024;
                unitIndex++;
            }
            
            return `${size.toFixed(1)} ${units[unitIndex]}`;
        },
        
        /**
         * Format time to human-readable format
         * @param {number} seconds - Time in seconds
         * @returns {string} - Formatted time string
         */
        formatTime: function(seconds) {
            if (isNaN(seconds) || !isFinite(seconds)) {
                return 'Unknown';
            }
            
            if (seconds < 60) {
                return `${Math.ceil(seconds)} seconds`;
            }
            
            const minutes = Math.floor(seconds / 60);
            if (minutes < 60) {
                return `${minutes} minute${minutes > 1 ? 's' : ''}`;
            }
            
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;
            return `${hours} hour${hours > 1 ? 's' : ''} ${remainingMinutes} minute${remainingMinutes > 1 ? 's' : ''}`;
        },
        
        /**
         * Show notification message
         * @param {string} message - Message to display
         * @param {string} type - Notification type (success, error, warning, info)
         */
        showNotification: function(message, type = 'info') {
            // Create a notification element
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            
            // Set icon based on notification type
            let icon = 'info-circle';
            if (type === 'success') icon = 'check-circle';
            if (type === 'error') icon = 'exclamation-circle';
            if (type === 'warning') icon = 'exclamation-triangle';
            
            notification.innerHTML = `
                <div class="notification-icon">
                    <i class="fas fa-${icon}"></i>
                </div>
                <div class="notification-content">
                    <p>${message}</p>
                </div>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            // Add to notifications container (create if it doesn't exist)
            let notificationsContainer = document.querySelector('.notifications-container');
            if (!notificationsContainer) {
                notificationsContainer = document.createElement('div');
                notificationsContainer.className = 'notifications-container';
                document.body.appendChild(notificationsContainer);
            }
            
            notificationsContainer.appendChild(notification);
            
            // Add close button event
            const closeButton = notification.querySelector('.notification-close');
            closeButton.addEventListener('click', () => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    notification.remove();
                    
                    // Remove container if empty
                    if (notificationsContainer.children.length === 0) {
                        notificationsContainer.remove();
                    }
                }, 300);
            });
            
            // Auto dismiss after 5 seconds for non-error notifications
            if (type !== 'error') {
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.classList.add('fade-out');
                        setTimeout(() => {
                            notification.remove();
                            
                            // Remove container if empty
                            if (notificationsContainer.children.length === 0) {
                                notificationsContainer.remove();
                            }
                        }, 300);
                    }
                }, 5000);
            }
        },
        
        /**
         * Auto-find PDF folder based on archive ID and PDF content
         * Will search for a folder containing the most PDF files and with "pdf" in the name
         */
        findPdfFolder: function() {
            // Prevent duplicate processing
            if (this._findingPdfFolder) {
                console.log("[PDF DEBUG] Already searching for PDF folder, skipping duplicate call");
                return;
            }
            
            this._findingPdfFolder = true;
            
            // Small delay to allow UI to update before processing
            setTimeout(() => {
                this._findingPdfFolder = false;
                
                this.addLogEntry("Searching for PDF folder in source folder...");
                
                // Clear any existing warnings
                elements.pdfWarningDisplay.textContent = "";
                elements.pdfWarningDisplay.className = "";
                
                // Get source path and archive ID
                const sourcePath = this.sourceData.path;
                if (!sourcePath) {
                    this.addLogEntry("Cannot find PDF folder: Source path not set");
                    elements.pdfWarningDisplay.textContent = "Source path not set";
                    elements.pdfWarningDisplay.className = "warning-message error";
                    return;
                }
                
                // Use consistent path formatting
                const normSourcePath = sourcePath.replace(/\\/g, '\\');
                
                // Get archive ID from project info
                const archiveId = this.projectInfo.archiveId;
                if (!archiveId) {
                    this.addLogEntry("Cannot find PDF folder: Archive ID not set");
                    elements.pdfWarningDisplay.textContent = "Archive ID not set";
                    elements.pdfWarningDisplay.className = "warning-message error";
                    elements.pdfFolderDisplay.textContent = "Not set";
                    this.projectInfo.pdfPath = '';
                    this.validateAllRequirements();
                    return;
                }
                
                // Get the base part of the archive ID (without suffix)
                const archiveIdBase = archiveId.match(/^([A-Z0-9]+)-?[A-Z0-9]*/i) ? 
                    archiveId.match(/^([A-Z0-9]+)-?[A-Z0-9]*/i)[1] : null;
                    
                console.log("[PDF DEBUG] Searching for PDF folder in source path:", normSourcePath);
                console.log("[PDF DEBUG] Using Archive ID:", archiveId, "Base ID:", archiveIdBase);
                console.log("[PDF DEBUG] Folder structure:", this.sourceData.folderStructure);
                
                // Check if folder structure exists
                if (!this.sourceData.folderStructure || !this.sourceData.folderStructure.folders) {
                    this.addLogEntry("Cannot find PDF folder: No folder structure information available");
                    elements.pdfWarningDisplay.textContent = "No folder structure information available";
                    elements.pdfWarningDisplay.className = "warning-message error";
                    elements.pdfFolderDisplay.textContent = "Not set";
                    this.projectInfo.pdfPath = '';
                    this.validateAllRequirements();
                    return;
                }
                
                // Create an array to hold folder candidates
                const folderCandidates = [];
                
                // Check root folder for PDF files
                const rootPdfCount = this.countPdfFilesInFolder(this.sourceData.folderStructure.files || []);
                if (rootPdfCount > 0) {
                    folderCandidates.push({
                        name: "Root",
                        path: normSourcePath,
                        pdfCount: rootPdfCount,
                        isPdfFolder: rootPdfCount > 0,
                        inSubfolder: false,
                        containsArchiveId: false,  // Root itself doesn't contain archiveId in name
                        containsPdfKeyword: false  // Root itself doesn't contain "pdf" in name
                    });
                }
                
                // Check for subfolders with PDF files - handle both array and object formats
                if (this.sourceData.folderStructure.folders) {
                    // Check if folders is an array (as seen in the debug output)
                    if (Array.isArray(this.sourceData.folderStructure.folders)) {
                        this.sourceData.folderStructure.folders.forEach((folder, index) => {
                            // For each folder name in the array
                            const folderPath = `${normSourcePath}\\${folder}`;
                            
                            console.log("[PDF DEBUG] Checking folder:", folder);
                            
                            // When we have fullStructure data, we can check actual files in the subfolders
                            let pdfCount = 0;
                            let hasFilesInfo = false;
                            
                            // Try to get PDF file count from fullStructure if available
                            if (this.sourceData.folderStructure.fullStructure && 
                                this.sourceData.folderStructure.fullStructure[folder] &&
                                this.sourceData.folderStructure.fullStructure[folder].files) {
                                
                                const folderFiles = this.sourceData.folderStructure.fullStructure[folder].files;
                                pdfCount = this.countPdfFilesInFolder(folderFiles);
                                hasFilesInfo = true;
                                
                                console.log("[PDF DEBUG] Found", pdfCount, "PDF files in folder", folder);
                            }
                            
                            // Check if folder name contains keywords
                            const folderNameLower = folder.toLowerCase();
                            const containsPdfKeyword = folderNameLower.includes('pdf');
                            
                            // Check if folder contains archive ID
                            const containsArchiveId = archiveId && (
                                folder === archiveId ||
                                folder.startsWith(archiveId + '_') ||
                                folder.includes('_' + archiveId) ||
                                folder.endsWith('_' + archiveId)
                            );
                            
                            const containsArchiveIdBase = archiveIdBase && (
                                folder.startsWith(archiveIdBase + '_') ||
                                folder.includes('_' + archiveIdBase) ||
                                folder.endsWith('_' + archiveIdBase)
                            );
                            
                            console.log("[PDF DEBUG] Folder stats:", {
                                folder,
                                pdfCount,
                                containsPdfKeyword,
                                containsArchiveId,
                                containsArchiveIdBase
                            });
                            
                            // For folders without file information, we'll prioritize folders containing both
                            // the archive ID and "pdf" in the name, as these are most likely to be what we want
                            if (pdfCount > 0 || containsPdfKeyword || containsArchiveId || containsArchiveIdBase) {
                                folderCandidates.push({
                                    name: folder,
                                    path: folderPath,
                                    pdfCount: pdfCount,
                                    isPdfFolder: pdfCount > 0 || containsPdfKeyword, // Consider it a PDF folder if it has PDFs or keyword
                                    inSubfolder: true,
                                    containsArchiveId: containsArchiveId || containsArchiveIdBase,
                                    containsPdfKeyword: containsPdfKeyword,
                                    isEstimate: pdfCount === 0 && containsPdfKeyword // Flag as estimate if we're guessing
                                });
                            }
                            
                            // Also check deeper subfolders if available
                            if (this.sourceData.folderStructure.folders[folder] && typeof this.sourceData.folderStructure.folders[folder] === 'object' && this.sourceData.folderStructure.folders[folder].folders) {
                                Object.keys(this.sourceData.folderStructure.folders[folder].folders).forEach(subfolder => {
                                    const subfolderPath = `${folderPath}\\${subfolder}`;
                                    const subfolderFiles = this.sourceData.folderStructure.folders[folder].folders[subfolder].files || [];
                                    
                                    console.log("[PDF DEBUG] Checking deeper subfolder:", subfolder, "Files:", subfolderFiles);
                                    
                                    // Count PDF files in this subfolder
                                    const subfolderPdfCount = this.countPdfFilesInFolder(subfolderFiles);
                                    
                                    // Check if subfolder name contains keywords
                                    const subfolderNameLower = subfolder.toLowerCase();
                                    const subfolderContainsPdfKeyword = subfolderNameLower.includes('pdf');
                                    
                                    // Check if subfolder contains archive ID
                                    const subfolderContainsArchiveId = archiveId && (
                                        subfolder === archiveId ||
                                        subfolder.startsWith(archiveId + '_') ||
                                        subfolder.includes('_' + archiveId) ||
                                        subfolder.endsWith('_' + archiveId)
                                    );
                                    
                                    const subfolderContainsArchiveIdBase = archiveIdBase && (
                                        subfolder.startsWith(archiveIdBase + '_') ||
                                        subfolder.includes('_' + archiveIdBase) ||
                                        subfolder.endsWith('_' + archiveIdBase)
                                    );
                                    
                                    if (subfolderPdfCount > 0) {
                                        folderCandidates.push({
                                            name: `${folder}\\${subfolder}`,
                                            path: subfolderPath,
                                            pdfCount: subfolderPdfCount,
                                            isPdfFolder: true,
                                            inSubfolder: true,
                                            deepSubfolder: true,
                                            containsArchiveId: subfolderContainsArchiveId || subfolderContainsArchiveIdBase,
                                            containsPdfKeyword: subfolderContainsPdfKeyword
                                        });
                                    }
                                });
                            }
                        });
                    }
                }
                
                console.log("[PDF DEBUG] All folder candidates:", folderCandidates);
                
                // No folders with PDFs found
                if (folderCandidates.length === 0) {
                    this.addLogEntry("No folders with PDF files found in the source folder or its subfolders");
                    elements.pdfWarningDisplay.textContent = "No folders with PDF files found";
                    elements.pdfWarningDisplay.className = "warning-message error";
                    elements.pdfFolderDisplay.textContent = "Not set";
                    this.projectInfo.pdfPath = '';
                    this.validateAllRequirements();
                    return;
                }
                
                // Score and sort folders to find the best match
                folderCandidates.forEach(folder => {
                    folder.score = this.scorePdfFolder(folder);
                    console.log("[PDF DEBUG] Scored folder:", folder.name, "Score:", folder.score);
                });
                
                // Sort by score (highest first)
                folderCandidates.sort((a, b) => b.score - a.score);
                
                // Get highest scored folder
                const bestMatch = folderCandidates[0];
                console.log("[PDF DEBUG] Best match:", bestMatch);
                
                // Decide whether to use the folder based on score threshold
                const minimumScore = 2; // Needs to at least have PDFs and meet some criteria
                
                if (bestMatch.score >= minimumScore) {
                    this.addLogEntry(`Found potential PDF folder: ${bestMatch.path}`);
                    this.projectInfo.pdfPath = bestMatch.path;
                    elements.pdfFolderDisplay.textContent = bestMatch.path;
                    
                    // Clear any existing warnings
                    elements.pdfWarningDisplay.textContent = "";
                    elements.pdfWarningDisplay.className = "";
                    
                    // Show warning if score is not perfect
                    if (bestMatch.score < 5) {
                        let warningMsg = "AutoPDF: ";
                        if (!bestMatch.containsPdfKeyword) warningMsg += "no 'pdf' in name; ";
                        if (!bestMatch.containsArchiveId) warningMsg += "no archive ID in name; ";
                        if (bestMatch.deepSubfolder) warningMsg += "located in deep subfolder; ";
                        else if (bestMatch.inSubfolder) warningMsg += "located in subfolder; ";
                        if (bestMatch.pdfCount < 5) warningMsg += `contains ${bestMatch.pdfCount} files; `;
                        if (bestMatch.isEstimate) warningMsg += "file count is estimated; ";
                        
                        elements.pdfWarningDisplay.textContent = warningMsg;
                        elements.pdfWarningDisplay.className = "warning-message warning";
                        this.addLogEntry(warningMsg);
                    } else {
                        this.addLogEntry("Perfect match found for PDF folder");
                    }
                } else {
                    this.addLogEntry("No suitable PDF folder found matching criteria");
                    elements.pdfWarningDisplay.textContent = "No suitable folders matching PDF criteria found";
                    elements.pdfWarningDisplay.className = "warning-message error";
                    elements.pdfFolderDisplay.textContent = "Not set";
                    this.projectInfo.pdfPath = '';
                }
                
                this.validateAllRequirements();
            }, 100);
        },
        
        /**
         * Helper function to count PDF files in a folder
         * @param {Array} files - Array of filenames
         * @returns {number} - Count of PDF files
         */
        countPdfFilesInFolder: function(files) {
            if (!files || !Array.isArray(files)) return 0;
            
            return files.filter(file => 
                file.toLowerCase().endsWith('.pdf')
            ).length;
        },
        
        /**
         * Score a folder candidate for being a PDF folder (0-5)
         * 0 - No PDF files
         * +1 - Has PDF files
         * +1 - Contains 'pdf' in the folder name
         * +1 - Contains the archive ID in the folder name
         * +1 - Is in the source folder (not a subfolder)
         * +1 - Has significant number of PDF files (5+)
         */
        scorePdfFolder: function(folderCandidate) {
            let score = 0;
            
            // Must have PDF files to be considered
            if (folderCandidate.isPdfFolder) {
                score += 1;
                
                // Contains pdf keyword in name
                if (folderCandidate.containsPdfKeyword) {
                    score += 1;
                }
                
                // Contains archive ID in name
                if (folderCandidate.containsArchiveId) {
                    score += 1;
                }
                
                // Not in a subfolder (directly in source)
                if (!folderCandidate.inSubfolder) {
                    score += 1;
                }
                
                // Has significant number of PDF files
                if (folderCandidate.pdfCount >= 5) {
                    score += 1;
                }
            }
            
            return score;
        },
        
        /**
         * Find COMList file within source path based on certain criteria
         * @param {string} sourcePath - Source folder path to search within
         */
        findComlistFile: function(sourcePath) {
            // Prevent duplicate processing by checking if we're already processing
            if (this._findingComlistFile) return;
            this._findingComlistFile = true;
            
            this.addLogEntry(`Looking for COMList file in source folder...`);
            
            // DEBUG: Log source path and structure
            console.log("[COMLIST DEBUG] Source path:", sourcePath);
            console.log("[COMLIST DEBUG] Folder structure:", this.sourceData.folderStructure);
            
            // Process the real folder structure instead of using mocks
            // This uses the data from FolderPicker that we stored in sourceData.folderStructure
            setTimeout(() => {
                this._findingComlistFile = false;
                
                // Get archive ID to search for (if available)
                const archiveId = elements.archiveId.value.trim();
                if (!archiveId) {
                    this.addLogEntry("Cannot find COMList file: Archive ID not set");
                    elements.comlistWarningDisplay.textContent = "Archive ID not set";
                    elements.comlistWarningDisplay.className = "warning-message error";
                    elements.comlistFileDisplay.textContent = "Not set";
                    this.projectInfo.comlistPath = '';
                    this.validateAllRequirements();
                    return;
                }
                
                let archiveIdBase = '';
                
                // Extract the base part (RRDxxx)
                const parts = archiveId.split('-');
                if (parts.length === 2) {
                    archiveIdBase = parts[0]; // e.g., "RRD017"
                }
                
                // DEBUG: Log archive ID
                console.log("[COMLIST DEBUG] Archive ID:", archiveId, "Base:", archiveIdBase);
                
                // Get the source path without trailing slash
                const normSourcePath = sourcePath.endsWith('\\') ? sourcePath.slice(0, -1) : sourcePath;
                console.log("[COMLIST DEBUG] Normalized source path:", normSourcePath);
                
                // Process each file to find Excel files that might be COMList files
                const fileCandidates = [];
                
                // Check if folder structure exists
                if (!this.sourceData.folderStructure) {
                    this.addLogEntry("Cannot find COMList file: No folder structure information available");
                    elements.comlistWarningDisplay.textContent = "No folder structure information available";
                    elements.comlistWarningDisplay.className = "warning-message error";
                    elements.comlistFileDisplay.textContent = "Not set";
                    this.projectInfo.comlistPath = '';
                    this.validateAllRequirements();
                    return;
                }
                
                // Check files in the root folder if they exist
                if (this.sourceData.folderStructure.files && Array.isArray(this.sourceData.folderStructure.files)) {
                    console.log("[COMLIST DEBUG] Checking files in root folder:", this.sourceData.folderStructure.files);
                    
                    this.sourceData.folderStructure.files.forEach(file => {
                        const filePath = `${normSourcePath}\\${file}`;
                        const extension = file.split('.').pop().toLowerCase();
                        
                        // Check if it's an Excel file
                        const isExcelFile = extension === 'xlsx' || extension === 'xls' || extension === 'xlsm';
                        
                        // Check if filename contains keywords
                        const containsComlistKeyword = file.toLowerCase().includes('comlist');
                        
                        // Fix archive ID comparison - it should be an exact match or specific pattern
                        const containsArchiveId = archiveId && (
                            file === archiveId + '.xlsx' || 
                            file === archiveId + '.xls' ||
                            file.startsWith(archiveId + '_') ||
                            file.includes('_' + archiveId)
                        );
                        
                        const containsArchiveIdBase = archiveIdBase && (
                            file.startsWith(archiveIdBase + '_') ||
                            file.includes('_' + archiveIdBase)
                        );
                        
                        console.log("[COMLIST DEBUG] Checking file:", file, 
                                  "Path:", filePath,
                                  "Extension:", extension,
                                  "Is Excel:", isExcelFile,
                                  "Contains COMList:", containsComlistKeyword,
                                  "Contains Archive ID:", containsArchiveId);
                        
                        if (isExcelFile) {
                            fileCandidates.push({
                                name: file,
                                path: filePath,
                                isExcelFile: true,
                                inSubfolder: false,
                                containsArchiveId: containsArchiveId || containsArchiveIdBase,
                                containsComlistKeyword: containsComlistKeyword
                            });
                        }
                    });
                } else {
                    console.log("[COMLIST DEBUG] No files in root folder or files not in expected format");
                }
                
                // Check folders - handle both array and object formats
                if (this.sourceData.folderStructure.folders) {
                    // Check if folders is an array (as seen in the debug output)
                    if (Array.isArray(this.sourceData.folderStructure.folders)) {
                        console.log("[COMLIST DEBUG] Folders is an array with", this.sourceData.folderStructure.folders.length, "entries");
                        
                        // Since we don't have direct file information, we'll need to make educated guesses
                        // about where COMList files might be located
                        this.sourceData.folderStructure.folders.forEach(folderName => {
                            console.log("[COMLIST DEBUG] Examining folder:", folderName);
                            
                            // If the folder name contains the archive ID, it's likely the right folder
                            const folderMatchesArchiveId = archiveId && (
                                folderName === archiveId ||
                                folderName.startsWith(archiveId + '_') ||
                                folderName.includes('_' + archiveId)
                            );
                            
                            const folderMatchesArchiveIdBase = archiveIdBase && (
                                folderName.startsWith(archiveIdBase + '_') ||
                                folderName.includes('_' + archiveIdBase)
                            );
                            
                            // If this is likely the archive folder, suggest potential COMList file locations
                            if (folderMatchesArchiveId || folderMatchesArchiveIdBase) {
                                console.log("[COMLIST DEBUG] Found potential archive folder:", folderName);
                                
                                // Create potential COMList filename variations - we'll only use the most likely one
                                const potentialComlistName = `${archiveId}_comlist.xlsx`;
                                const filePath = `${normSourcePath}\\${folderName}\\${potentialComlistName}`;
                                
                                // Add a single candidate with a note that it's a suggested location rather than confirmed
                                fileCandidates.push({
                                    name: potentialComlistName,
                                    path: filePath,
                                    isExcelFile: true,
                                    inSubfolder: true,
                                    containsArchiveId: true,
                                    containsComlistKeyword: true,
                                    isSuggested: true // Flag to indicate this is a suggestion, not a confirmed file
                                });
                            }
                        });
                    } else {
                        // Original code for when folders is an object with files
                        Object.keys(this.sourceData.folderStructure.folders).forEach(subfolder => {
                            const subfolderPath = `${normSourcePath}\\${subfolder}`;
                            const subfolderFiles = this.sourceData.folderStructure.folders[subfolder].files || [];
                            
                            console.log("[COMLIST DEBUG] Checking subfolder:", subfolder, "Files:", subfolderFiles);
                            
                            subfolderFiles.forEach(file => {
                                const filePath = `${subfolderPath}\\${file}`;
                                const extension = file.split('.').pop().toLowerCase();
                                
                                // Check if it's an Excel file
                                const isExcelFile = extension === 'xlsx' || extension === 'xls' || extension === 'xlsm';
                                
                                // Check if filename contains keywords
                                const containsComlistKeyword = file.toLowerCase().includes('comlist');
                                
                                // Fix archive ID comparison for subfolder files as well
                                const containsArchiveId = archiveId && (
                                    file === archiveId + '.xlsx' || 
                                    file === archiveId + '.xls' ||
                                    file.startsWith(archiveId + '_') ||
                                    file.includes('_' + archiveId)
                                );
                                
                                const containsArchiveIdBase = archiveIdBase && (
                                    file.startsWith(archiveIdBase + '_') ||
                                    file.includes('_' + archiveIdBase)
                                );
                                
                                console.log("[COMLIST DEBUG] Checking subfolder file:", file, 
                                          "Path:", filePath,
                                          "Extension:", extension,
                                          "Is Excel:", isExcelFile,
                                          "Contains COMList:", containsComlistKeyword,
                                          "Contains Archive ID:", containsArchiveId);
                                
                                if (isExcelFile) {
                                    fileCandidates.push({
                                        name: file,
                                        path: filePath,
                                        isExcelFile: true,
                                        inSubfolder: true,
                                        containsArchiveId: containsArchiveId || containsArchiveIdBase,
                                        containsComlistKeyword: containsComlistKeyword
                                    });
                                }
                            });
                        });
                    }
                }
                
                console.log("[COMLIST DEBUG] All file candidates:", fileCandidates);
                
                // No files found
                if (fileCandidates.length === 0) {
                    this.addLogEntry("No Excel files found in the source folder or its subfolders");
                    elements.comlistWarningDisplay.textContent = "No Excel files found for COMList";
                    elements.comlistWarningDisplay.className = "warning-message error";
                    elements.comlistFileDisplay.textContent = "Not set";
                    this.projectInfo.comlistPath = '';
                    this.validateAllRequirements();
                    return;
                }
                
                // Score and sort files to find the best match
                fileCandidates.forEach(file => {
                    file.score = this.scoreComlistFile(file);
                    console.log("[COMLIST DEBUG] Scored file:", file.name, "Score:", file.score);
                });
                
                // Sort by score (highest first)
                fileCandidates.sort((a, b) => b.score - a.score);
                
                // Get highest scored file
                const bestMatch = fileCandidates[0];
                console.log("[COMLIST DEBUG] Best match:", bestMatch);
                
                // Decide whether to use the file based on score threshold
                const minimumScore = 2; // Needs to at least be an Excel file with either comlist keyword or archiveID
                
                if (bestMatch.score >= minimumScore) {
                    this.addLogEntry(`Found potential COMList file: ${bestMatch.path}`);
                    this.projectInfo.comlistPath = bestMatch.path;
                    elements.comlistFileDisplay.textContent = bestMatch.path;
                    
                    // Clear any existing warnings
                    elements.comlistWarningDisplay.textContent = "";
                    elements.comlistWarningDisplay.className = "";
                    
                    // Show warning if score is not perfect or if this is a suggested file
                    if (bestMatch.score < 4 || bestMatch.isSuggested) {
                        let warningMsg = "AutoCOM: ";
                        if (!bestMatch.containsComlistKeyword) warningMsg += "no 'comlist' keyword; ";
                        if (!bestMatch.containsArchiveId) warningMsg += "no archive ID match; ";
                        if (bestMatch.inSubfolder) warningMsg += "located in subfolder; ";
                        if (bestMatch.isSuggested) warningMsg += "suggested location only; ";
                        
                        elements.comlistWarningDisplay.textContent = warningMsg;
                        elements.comlistWarningDisplay.className = "warning-message warning";
                        this.addLogEntry(warningMsg);
                    } else {
                        this.addLogEntry("Perfect match found for COMList file");
                    }
                } else {
                    this.addLogEntry("No suitable COMList file found matching criteria");
                    elements.comlistWarningDisplay.textContent = "No suitable Excel files matching COMList criteria found";
                    elements.comlistWarningDisplay.className = "warning-message error";
                    elements.comlistFileDisplay.textContent = "Not set";
                    this.projectInfo.comlistPath = '';
                }
                
                this.validateAllRequirements();
            }, 100);
        },
        
        /**
         * Score a file candidate for being a COMList file (0-4)
         * 0 - Not an excel file
         * +1 - Is an excel file
         * +1 - Contains 'comlist' in the filename
         * +1 - Contains the archive ID in the filename
         * +1 - Is in the source folder (not a subfolder)
         */
        scoreComlistFile: function(fileCandidate) {
            let score = 0;
            
            // Must be an Excel file to be considered
            if (fileCandidate.isExcelFile) {
                score += 1;
                
                // Contains comlist keyword
                if (fileCandidate.containsComlistKeyword) {
                    score += 1;
                }
                
                // Contains archive ID 
                if (fileCandidate.containsArchiveId) {
                    score += 1;
                }
                
                // Not in a subfolder (directly in source)
                if (!fileCandidate.inSubfolder) {
                    score += 1;
                }
            }
            
            return score;
        },
        
        /**
         * Refresh auto-find results when Archive ID changes
         * This is called when the archive ID is manually updated
         */
        refreshAutoFindResults: function() {
            // If source path is set and auto-find features are enabled, refresh them
            if (this.sourceData.path) {
                if (elements.autoFindPdf.checked) {
                    this.findPdfFolder();
                }
                
                if (elements.autoFindComlist.checked) {
                    this.findComlistFile(this.sourceData.path);
                }
            }
        }
    };

    // Initialize the Transfer application
    TransferApp.initialize();
});
