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
        
        // Destination elements
        destinationFolder: document.getElementById('destination-folder'),
        destinationBrowseBtn: document.getElementById('destination-browse-btn'),
        createSubfolder: document.getElementById('create-subfolder'),
        destinationPathPreview: document.getElementById('destination-path-preview'),
        destinationPathDisplay: document.getElementById('destination-path-display'),
        
        // Project info elements
        autoParse: document.getElementById('auto-parse'),
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
            files: []
        },
        destinationPath: 'Y:\\',
        projectInfo: {
            archiveId: '',
            location: '',
            documentType: '',
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
            this.initializeEventListeners();
            this.updateDestinationPreview();
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
                    // Open the drive selector first to choose a drive
                    const selectedPath = await FolderPicker.show(false);
                    folderPicker.classList.remove('show');
                    if (selectedPath) {
                        elements.sourceFolder.value = selectedPath;
                        this.updateSourceFolder(selectedPath);
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
                    const selectedPath = await FolderPicker.show(true);
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
                        // Disable auto-parse when manually editing
                        elements.autoParse.checked = false;
                        
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
            const infoFields = [elements.archiveId, elements.location, elements.documentType];
            infoFields.forEach(field => {
                // On input, validate in real-time
                field.addEventListener('input', () => this.validateProjectInfo());
                
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
            
            // Mock file stats (would be from server in real implementation)
            this.mockGetFileStats().then(stats => {
                this.sourceData.fileCount = stats.fileCount;
                this.sourceData.totalSize = stats.totalSize;
                this.sourceData.files = stats.files;
                
                // Update UI
                elements.sourceFileCount.textContent = stats.fileCount;
                elements.sourceSize.textContent = this.formatSize(stats.totalSize);
                
                // Update destination preview
                this.updateDestinationPreview();
                
                // Parse project info if auto-parse is enabled
                if (elements.autoParse.checked) {
                    this.parseProjectInfo(this.sourceData.folderName);
                }
                
                // Enable start button if everything is valid
                this.updateStartButtonState();
                
                this.addLogEntry(`Source folder selected: ${path}`);
                this.addLogEntry(`Found ${stats.fileCount} files (${this.formatSize(stats.totalSize)})`);
            });
        },
        
        /**
         * Mock getting file stats (would be a server call in real implementation)
         * @returns {Promise<Object>} - File stats
         */
        mockGetFileStats: function() {
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
            const basePath = elements.destinationFolder.value;
            let finalPath = basePath;
            
            if (elements.createSubfolder.checked && this.sourceData.folderName) {
                finalPath = `${basePath}${this.sourceData.folderName}\\`;
            }
            
            elements.destinationPathPreview.textContent = finalPath;
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
                
                this.projectInfo = {
                    archiveId: archiveId,
                    location: location,
                    documentType: docType,
                    isValid: true
                };
                
                // Update UI - both inputs and displays
                elements.archiveId.value = archiveId;
                elements.archiveIdDisplay.textContent = archiveId;
                
                elements.location.value = location;
                elements.locationDisplay.textContent = location;
                
                elements.documentType.value = docType;
                elements.documentTypeDisplay.textContent = docType;
                
                this.showValidationStatus(true, 'Project information parsed successfully');
                this.addLogEntry(`Project info parsed: ID=${archiveId}, Location=${location}, Type=${docType}`);
            } else {
                this.projectInfo = {
                    archiveId: '',
                    location: '',
                    documentType: '',
                    isValid: false
                };
                
                // Clear both inputs and displays
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
            // Only validate if auto-parse is disabled
            if (elements.autoParse.checked) return;
            
            const archiveId = elements.archiveId.value.trim();
            const location = elements.location.value.trim();
            const documentType = elements.documentType.value.trim();
            
            // Update display values
            elements.archiveIdDisplay.textContent = archiveId || 'Not set';
            elements.locationDisplay.textContent = location || 'Not set';
            elements.documentTypeDisplay.textContent = documentType || 'Not set';
            
            // Check if Archive ID matches pattern RRDxxx-yyyy
            const archiveIdPattern = /^RRD\d{3}-\d{4}$/;
            const isArchiveIdValid = archiveIdPattern.test(archiveId);
            
            // Check if location is not empty
            const isLocationValid = location.length > 0;
            
            // Check if document type is not empty
            const isDocTypeValid = documentType.length > 0;
            
            // All fields must be valid
            const isValid = isArchiveIdValid && isLocationValid && isDocTypeValid;
            
            this.projectInfo = {
                archiveId: archiveId,
                location: location,
                documentType: documentType,
                isValid: isValid
            };
            
            // Show validation status
            if (!isValid) {
                let message = 'Please fix the following:';
                if (!isArchiveIdValid) message += ' Invalid Archive ID format (should be RRDxxx-yyyy);';
                if (!isLocationValid) message += ' Location is required;';
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
            elements.startTransferBtn.disabled = true;
            elements.createSubfolder.disabled = true;
            elements.autoParse.disabled = true;
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
         * Mock transfer process
         */
        mockTransferProcess: function() {
            // Use a timeout to simulate the transfer
            const files = this.sourceData.files;
            const totalFiles = files.length;
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
                    // Increment the bytes transferred by a portion of the file size
                    const increment = file.size / (fileDelayMs / updateInterval);
                    fileProgress += increment;
                    
                    // Calculate total progress
                    const totalProgress = bytesTransferred + fileProgress;
                    const percentage = Math.min(Math.floor((totalProgress / totalBytes) * 100), 100);
                    
                    // Update progress bar
                    elements.transferProgress.style.width = `${percentage}%`;
                    elements.progressPercentage.textContent = `${percentage}%`;
                    
                    // Calculate transfer speed (bytes per second)
                    const elapsedSeconds = (Date.now() - this.transferState.startTime) / 1000;
                    const speed = totalProgress / elapsedSeconds;
                    
                    // Update transfer speed
                    elements.transferSpeed.textContent = `${this.formatSize(speed)}/s`;
                    
                    // Calculate time remaining
                    const remainingBytes = totalBytes - totalProgress;
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
            elements.startTransferBtn.disabled = false;
            elements.createSubfolder.disabled = false;
            elements.autoParse.disabled = false;
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
        }
    };

    // Initialize the Transfer application
    TransferApp.initialize();
});
