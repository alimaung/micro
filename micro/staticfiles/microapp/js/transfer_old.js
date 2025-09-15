/**
 * transfer.js - Microfilm Transfer functionality
 * Handles importing projects from external drives to the system
 */

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
        // Source elements
        sourceFolder: document.getElementById('source-folder'),
        sourceBrowseBtn: document.getElementById('source-browse-btn'),
        sourceFileCount: document.getElementById('source-file-count'),
        sourceSize: document.getElementById('source-size'),
        sourceFolderEdit: document.getElementById('source-folder-edit'),
        sourceFolderDisplay: document.getElementById('source-folder-display'),
        
        // Destination elements
        destinationFolder: document.getElementById('destination-folder'),
        destinationBrowseBtn: document.getElementById('destination-browse-btn'),
        createSubfolder: document.getElementById('create-subfolder'),
        destinationPathPreview: document.getElementById('destination-path-preview'),
        destinationPathDisplay: document.getElementById('destination-path-display'),
        destinationPathEdit: document.getElementById('destination-path-edit'),
        
        // PDF folder elements
        pdfFolder: document.getElementById('pdf-folder'),
        pdfBrowseBtn: document.getElementById('pdf-browse-btn'),
        pdfFolderDisplay: document.getElementById('pdf-folder-display'),
        pdfFolderEdit: document.getElementById('pdf-folder-edit'),
        
        // COMList file elements
        comlistFile: document.getElementById('comlist-file'),
        comlistBrowseBtn: document.getElementById('comlist-browse-btn'),
        comlistFileDisplay: document.getElementById('comlist-file-display'),
        comlistFileEdit: document.getElementById('comlist-file-edit'),
        
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
        validationStatus: document.getElementById('validation-status'),
        validationMessage: document.getElementById('validation-message'),
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
            elements.destinationPathEdit.value = '';
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
                        
                        this.updateSourceFolder(selectedResult.path);
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
                    const selectedPath = await FolderPicker.show(false, 'folders', null, 'Select Destination Folder');
                    folderPicker.classList.remove('show');
                    if (selectedPath) {
                        elements.destinationFolder.value = selectedPath;
                        this.destinationPath = selectedPath;
                        this.updateDestinationPreview();
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
                    const selectedPath = await FolderPicker.show(false, 'folders', null, 'Select PDF Folder');
                    folderPicker.classList.remove('show');
                    if (selectedPath) {
                        elements.pdfFolder.value = selectedPath;
                        elements.pdfFolderDisplay.textContent = selectedPath;
                        elements.pdfFolderEdit.value = selectedPath;
                        this.projectInfo.pdfPath = selectedPath;
                        
                        this.addLogEntry(`PDF folder selected: ${selectedPath}`);
                        
                        // Enable the input field if a folder is selected
                        elements.pdfFolder.disabled = false;
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
                    const selectedPath = await FolderPicker.show(false, 'files', ['xlsx', 'xls', 'xlsm'], 'Select COMList File');
                    folderPicker.classList.remove('show');
                    if (selectedPath) {
                        elements.comlistFile.value = selectedPath;
                        elements.comlistFileDisplay.textContent = selectedPath;
                        elements.comlistFileEdit.value = selectedPath;
                        this.projectInfo.comlistPath = selectedPath;
                        
                        this.addLogEntry(`COMList file selected: ${selectedPath}`);
                        
                        // Enable the input field if a file is selected
                        elements.comlistFile.disabled = false;
                    }
                } catch (error) {
                    console.error('Error selecting COMList file:', error);
                    this.showNotification('Failed to select COMList file', 'error');
                }
            });
            
            // Create subfolder toggle
            elements.createSubfolder.addEventListener('change', () => {
                this.updateDestinationPreview();
            });
            
            // Auto-parse toggle
            elements.autoParse.addEventListener('change', () => {
                const isAutoParse = elements.autoParse.checked;
                this.toggleFieldsEditability(!isAutoParse);
                
                if (isAutoParse && this.sourceData.folderName) {
                    this.parseProjectInfo(this.sourceData.folderName);
                }
            });
            
            // Auto-select path toggle
            elements.autoSelectPath.addEventListener('change', () => {
                // If turned on and we have a source folder, update the destination preview
                if (elements.autoSelectPath.checked && this.sourceData.folderName) {
                    this.updateDestinationPreview();
                }
            });
            
            // Auto-find PDF folder toggle
            elements.autoFindPdf.addEventListener('change', () => {
                if (elements.autoFindPdf.checked && this.sourceData.path) {
                    // Now we can properly call the PDF folder detection
                    this.findPdfFolder(this.sourceData.path);
                } else {
                    elements.pdfBrowseBtn.disabled = false;
                    this.addLogEntry("Auto-find PDF folder toggled off");
                }
            });
            
            // Auto-find COMList toggle
            elements.autoFindComlist.addEventListener('change', () => {
                if (elements.autoFindComlist.checked && this.sourceData.path) {
                    // Now we can properly call the COMList file detection
                    this.findComlistFile(this.sourceData.path);
                } else {
                    elements.comlistBrowseBtn.disabled = false;
                    this.addLogEntry("Auto-find COMList file toggled off");
                }
            });
            
            // Field edit buttons
            elements.editButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const fieldId = button.getAttribute('data-field');
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
                        
                        // Update project info and validate
                        this.validateProjectInfo();
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
            });
            
            // Manual info inputs - handle blur/enter to finish editing
            const infoFields = [
                elements.archiveId, 
                elements.location, 
                elements.documentType, 
                elements.sourceFolderEdit,
                elements.destinationPathEdit,
                elements.pdfFolderEdit,
                elements.comlistFileEdit
            ];
            
            infoFields.forEach(field => {
                // On input, mark as manually edited and validate in real-time
                field.addEventListener('input', () => {
                    this._manualEdit = true;
                    this.validateProjectInfo();
                });
                
                // On blur, save the changes
                field.addEventListener('blur', () => {
                    const container = field.closest('.field-value-container');
                    if (container && container.classList.contains('editing')) {
                        const displayId = container.querySelector('.edit-field').getAttribute('data-display');
                        const displayEl = document.getElementById(displayId);
                        
                        const value = field.value.trim();
                        displayEl.textContent = value || 'Not set';
                        
                        // Update internal state if any of our key fields are edited
                        if (field === elements.sourceFolderEdit) {
                            this.sourceData.path = value;
                            const pathParts = value.split('\\');
                            this.sourceData.folderName = pathParts[pathParts.length - 1];
                        } else if (field === elements.destinationPathEdit) {
                            this.destinationPath = value;
                        } else if (field === elements.pdfFolderEdit) {
                            this.projectInfo.pdfPath = value;
                        } else if (field === elements.comlistFileEdit) {
                            this.projectInfo.comlistPath = value;
                        }
                        
                        // Exit edit mode
                        container.classList.remove('editing');
                        
                        // Ensure validation happens even if auto-parse is enabled
                        this._manualEdit = true;
                        this.validateProjectInfo();
                    }
                });
                
                // On enter key, save changes
                field.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        field.blur();
                    }
                });
            });
            
            // Start transfer button
            elements.startTransferBtn.addEventListener('click', () => this.startTransfer());
            
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
            elements.pdfFolderEdit.disabled = !enabled;
            elements.comlistFileEdit.disabled = !enabled;
            
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
            
            // Update the source folder display and edit field
            elements.sourceFolderDisplay.textContent = path;
            elements.sourceFolderEdit.value = path;
            
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
                    // Now we can properly call the PDF folder detection
                    this.findPdfFolder(path);
                }
                
                // Try to auto-find COMList file if that option is enabled
                if (elements.autoFindComlist.checked) {
                    // Now we can properly call the COMList file detection
                    this.findComlistFile(path);
                }
                
                // Enable start button if everything is valid
                this.updateStartButtonState();
                
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
            
            elements.destinationPathEdit.value = finalPath;
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
                
                // Verify location is either OU or DW
                const isLocationValid = location === 'OU' || location === 'DW';
                
                // Keep any existing PDF and COMList paths when parsing
                const pdfPath = this.projectInfo.pdfPath || '';
                const comlistPath = this.projectInfo.comlistPath || '';
                
                this.projectInfo = {
                    archiveId: archiveId,
                    location: location,
                    documentType: docType,
                    pdfPath: pdfPath,            // Preserve this value
                    comlistPath: comlistPath,    // Preserve this value
                    isValid: isLocationValid     // Only valid if location is valid
                };
                
                // Update UI - both inputs and displays
                elements.archiveId.value = archiveId;
                elements.archiveIdDisplay.textContent = archiveId;
                
                elements.location.value = location;
                elements.locationDisplay.textContent = location;
                
                elements.documentType.value = docType;
                elements.documentTypeDisplay.textContent = docType;
                
                // Don't reset PDF and COMList paths
                
                if (isLocationValid) {
                    this.showValidationStatus(true, 'Project information parsed successfully');
                    this.addLogEntry(`Project info parsed: ID=${archiveId}, Location=${location}, Type=${docType}`);
                } else {
                    this.showValidationStatus(false, 'Location must be either OU or DW');
                    this.addLogEntry(`Invalid location "${location}" - must be either OU or DW`);
                }
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
                
                this.showValidationStatus(false, 'Could not parse project information from folder name');
                this.addLogEntry('Failed to parse project information from folder name');
            }
            
            this.updateStartButtonState();
        },
        
        /**
         * Validate manually entered project information
         */
        validateProjectInfo: function() {
            // Only validate if auto-parse is disabled or a manual edit was made
            if (elements.autoParse.checked && !this._manualEdit) return;

            // Reset manual edit flag after validation
            this._manualEdit = false;
            
            const archiveId = elements.archiveId.value.trim();
            const location = elements.location.value.trim();
            const documentType = elements.documentType.value.trim();
            const destinationPath = elements.destinationPathEdit.value.trim();
            const pdfPath = elements.pdfFolderEdit.value.trim();
            const comlistPath = elements.comlistFileEdit.value.trim();
            
            // Update display values
            elements.archiveIdDisplay.textContent = archiveId || 'Not set';
            elements.locationDisplay.textContent = location || 'Not set';
            elements.documentTypeDisplay.textContent = documentType || 'Not set';
            elements.destinationPathDisplay.textContent = destinationPath || 'Not set';
            elements.pdfFolderDisplay.textContent = pdfPath || 'Not set';
            elements.comlistFileDisplay.textContent = comlistPath || 'Not set';
            
            // Check if Archive ID matches pattern RRDxxx-yyyy
            const archiveIdPattern = /^RRD\d{3}-\d{4}$/;
            const isArchiveIdValid = archiveIdPattern.test(archiveId);
            
            // Check if location is either OU or DW
            const isLocationValid = location === 'OU' || location === 'DW';
            
            // Check if document type is not empty
            const isDocTypeValid = documentType.length > 0;
            
            // Note: PDF path and COMList are optional, so we don't require them for validation
            
            // All required fields must be valid
            const isValid = isArchiveIdValid && isLocationValid && isDocTypeValid;
            
            this.projectInfo = {
                archiveId: archiveId,
                location: location,
                documentType: documentType,
                pdfPath: pdfPath,
                comlistPath: comlistPath,
                isValid: isValid
            };
            
            // Show validation status
            if (!isValid) {
                let message = 'Please fix the following:';
                if (!isArchiveIdValid) message += ' Invalid Archive ID format (should be RRDxxx-yyyy);';
                if (!isLocationValid) message += ' Location must be either OU or DW;';
                if (!isDocTypeValid) message += ' Document Type is required;';
                
                this.showValidationStatus(false, message);
            } else {
                this.showValidationStatus(true, 'Project information looks good');
            }
            
            this.updateStartButtonState();
        },
        
        /**
         * Show validation status
         * @param {boolean} isValid - Whether the validation passed
         * @param {string} message - Validation message
         */
        showValidationStatus: function(isValid, message) {
            elements.validationStatus.className = isValid ? 'validation-status' : 'validation-status error';
            elements.validationStatus.innerHTML = `
                <i class="fas ${isValid ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span id="validation-message">${message}</span>
            `;
        },
        
        /**
         * Update start button state based on validation
         */
        updateStartButtonState: function() {
            const isSourceValid = this.sourceData.path && this.sourceData.fileCount > 0;
            const isDestinationValid = this.destinationPath;
            const isProjectInfoValid = this.projectInfo.isValid;
            
            const canStart = isSourceValid && isDestinationValid && isProjectInfoValid;
            elements.startTransferBtn.disabled = !canStart;
            
            // Update status badge
            const statusBadge = document.querySelector('.transfer-header .status-badge');
            if (canStart) {
                statusBadge.className = 'status-badge pending';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Ready to Transfer';
                
                elements.transferStatus.className = 'status-badge pending';
                elements.transferStatus.innerHTML = '<i class="fas fa-check-circle"></i> Ready';
            } else {
                statusBadge.className = 'status-badge initial';
                statusBadge.innerHTML = '<i class="fas fa-clock"></i> Awaiting Configuration';
                
                elements.transferStatus.className = 'status-badge initial';
                elements.transferStatus.innerHTML = '<i class="fas fa-clock"></i> Not Started';
            }
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
            elements.startTransferBtn.disabled = true;
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
            
            // Enable cancel button
            elements.cancelTransferBtn.disabled = false;
            
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
                    
                    // Update progress bar
                    elements.transferProgress.style.width = `${overallProgress * 100}%`;
                    elements.progressPercentage.textContent = `${Math.round(overallProgress * 100)}%`;
                    
                    // Calculate transfer speed (bytes per second)
                    const elapsedSeconds = (Date.now() - this.transferState.startTime) / 1000;
                    const speed = currentBytes / elapsedSeconds;
                    
                    // Update transfer speed
                    elements.transferSpeed.textContent = `${this.formatSize(speed)}/s`;
                    
                    // Calculate time remaining
                    const remainingBytes = totalBytes - currentBytes;
                    const secondsRemaining = remainingBytes / speed;
                    elements.timeRemaining.textContent = this.formatTime(secondsRemaining);
                    
                    // Update files transferred
                    elements.filesTransferred.textContent = `${filesTransferred}/${totalFiles}`;
                    
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
         * Placeholder method for auto-finding PDF folder
         * To be implemented in the future
         * @param {string} sourcePath - Source folder path to search within
         */
        findPdfFolder: function(sourcePath) {
            // This function will be implemented later
            this.addLogEntry(`Looking for PDF folder in source folder...`);
            
            // Log the folder structure and archive ID
            console.log("[PDF DEBUG] Source path:", this.sourceData.path);
            console.log("[PDF DEBUG] Folder structure:", this.sourceData.folderStructure);
            
            // Check if we have the necessary data
            if (!this.sourceData.folderStructure || !this.sourceData.folderStructure.folders) {
                this.addLogEntry("Cannot find PDF folder: No folder structure information available");
                return;
            }
            
            // Mock implementation that just logs an entry
            setTimeout(() => {
                this.addLogEntry("PDF folder auto-detection not yet fully implemented");
                this.addLogEntry("Using the source folder structure data for scanning");
                this.addLogEntry(`Found ${this.sourceData.folderStructure.folders.length} subfolders to check`);
            }, 500);
        },
        
        /**
         * Placeholder method for auto-finding COMList file
         * To be implemented in the future
         * @param {string} sourcePath - Source folder path to search within
         */
        findComlistFile: function(sourcePath) {
            // This function will be implemented later
            this.addLogEntry(`Looking for COMList file in source folder...`);
            
            // Log the folder structure and archive ID
            console.log("[COMLIST DEBUG] Source path:", this.sourceData.path);
            console.log("[COMLIST DEBUG] Folder structure:", this.sourceData.folderStructure);
            
            // Check if we have the necessary data
            if (!this.sourceData.folderStructure || !this.sourceData.folderStructure.folders) {
                this.addLogEntry("Cannot find COMList file: No folder structure information available");
                return;
            }
            
            // Mock implementation that just logs an entry
            setTimeout(() => {
                this.addLogEntry("COMList file auto-detection not yet fully implemented");
                this.addLogEntry("Using the source folder structure data for scanning");
                
                // Check for Excel files in the root folder
                const excelFiles = this.sourceData.folderStructure.files.filter(file => 
                    file.toLowerCase().endsWith('.xlsx') || file.toLowerCase().endsWith('.xls')
                );
                
                this.addLogEntry(`Found ${excelFiles.length} Excel files in source folder`);
            }, 500);
        }
    };

    // Initialize the Transfer application
    TransferApp.initialize();
});
