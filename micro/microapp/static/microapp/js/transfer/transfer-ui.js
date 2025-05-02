/**
 * transfer-ui.js - UI interactions for Transfer module
 * Handles DOM interactions and UI updates
 */

// Make the class available globally
window.TransferUI = class TransferUI {
    constructor(eventManager) {
        this.eventManager = eventManager;
        this.elements = this.cacheElements();
        this.bindEventListeners();
        
        // Initialize the database service
        this.dbService = new DatabaseService();
    }
    
    /**
     * Cache DOM elements for better performance
     * @returns {Object} - Cached DOM elements
     */
    cacheElements() {
        return {
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
            addToDatabase: document.getElementById('add-to-database'),
            
            // Project info elements
            archiveId: document.getElementById('archive-id'),
            archiveIdDisplay: document.getElementById('archive-id-display'),
            location: document.getElementById('location'),
            locationDisplay: document.getElementById('location-display'),
            documentType: document.getElementById('document-type'),
            documentTypeDisplay: document.getElementById('document-type-display'),
            projectInfoStatusBadge: document.getElementById('project-info-status'),
            editButtons: document.querySelectorAll('.edit-field'),
            
            // Transfer elements - using existing elements from HTML template
            transferStatus: document.getElementById('transfer-status'),
            transferProgress: document.getElementById('transfer-progress-bar'),
            progressPercentage: document.getElementById('progress-percentage'),
            filesTransferred: document.getElementById('files-transferred'),
            transferSpeed: document.getElementById('transfer-speed'),
            timeRemaining: document.getElementById('time-remaining'),
            currentFile: document.getElementById('current-file'),
            startTransferBtn: document.getElementById('start-transfer-btn'),
            cancelTransferBtn: document.getElementById('cancel-transfer-btn'),
            toggleLogBtn: document.getElementById('toggle-log'),
            transferLog: document.getElementById('transfer-log'),
            
            // Cache source folder input
            sourceFolderInput: document.getElementById('source-folder'),
            destinationFolderInput: document.getElementById('destination-folder'),
            selectSourceBtn: document.getElementById('select-source-btn'),
            selectDestinationBtn: document.getElementById('select-destination-btn')
        };
    }
    
    /**
     * Bind event listeners to UI elements
     */
    bindEventListeners() {
        // Source folder button
        this.elements.sourceBrowseBtn.addEventListener('click', () => this.handleSourceBrowse());
        
        // Destination folder button
        this.elements.destinationBrowseBtn.addEventListener('click', () => this.handleDestinationBrowse());
        
        // PDF folder button
        this.elements.pdfBrowseBtn.addEventListener('click', () => this.handlePdfBrowse());
        
        // COMList file button
        this.elements.comlistBrowseBtn.addEventListener('click', () => this.handleComlistBrowse());
        
        // Create subfolder toggle
        this.elements.createSubfolder.addEventListener('change', () => {
            this.eventManager.publish('subfolder-toggle-changed', {
                checked: this.elements.createSubfolder.checked
            });
        });
        
        // Auto-parse toggle
        this.elements.autoParse.addEventListener('change', () => {
            this.eventManager.publish('auto-parse-toggle-changed', {
                checked: this.elements.autoParse.checked
            });
        });
        
        // Auto-select path toggle
        this.elements.autoSelectPath.addEventListener('change', () => {
            this.eventManager.publish('auto-select-path-toggle-changed', {
                checked: this.elements.autoSelectPath.checked
            });
        });
        
        // Auto-find PDF folder toggle
        this.elements.autoFindPdf.addEventListener('change', () => {
            const isChecked = this.elements.autoFindPdf.checked;
            this.elements.pdfBrowseBtn.disabled = isChecked;
            
            this.eventManager.publish('auto-find-pdf-toggle-changed', {
                checked: isChecked
            });
        });
        
        // Auto-find COMList toggle
        this.elements.autoFindComlist.addEventListener('change', () => {
            const isChecked = this.elements.autoFindComlist.checked;
            this.elements.comlistBrowseBtn.disabled = isChecked;
            
            this.eventManager.publish('auto-find-comlist-toggle-changed', {
                checked: isChecked
            });
        });
        
        // Edit buttons for editable fields
        this.elements.editButtons.forEach(button => {
            const fieldId = button.getAttribute('data-field');
            if (fieldId === 'archive-id' || fieldId === 'location' || fieldId === 'document-type') {
                button.addEventListener('click', () => this.handleFieldEdit(button, fieldId));
            }
        });
        
        // Manual info inputs
        const infoFields = [
            this.elements.archiveId, 
            this.elements.location, 
            this.elements.documentType
        ];
        
        infoFields.forEach(field => {
            // On input validation
            field.addEventListener('input', () => {
                this.eventManager.publish('field-input-changed', {
                    fieldId: field.id,
                    value: field.value.trim()
                });
            });
            
            // On blur, save changes
            field.addEventListener('blur', () => this.handleFieldBlur(field));
            
            // On enter key, trigger blur
            field.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    field.blur();
                }
            });
        });
        
        // Start transfer button
        this.elements.startTransferBtn.addEventListener('click', () => {
            this.eventManager.publish('start-transfer-clicked');
        });
        
        // Cancel transfer button
        this.elements.cancelTransferBtn.addEventListener('click', () => {
            this.eventManager.publish('cancel-transfer-clicked');
        });
        
        // Toggle log button
        this.elements.toggleLogBtn.addEventListener('click', () => {
            this.elements.toggleLogBtn.classList.toggle('expanded');
            this.elements.transferLog.classList.toggle('expanded');
        });
        
        // Add to database toggle
        this.elements.addToDatabase.addEventListener('change', () => {
            this.eventManager.publish('add-to-database-toggle-changed', {
                checked: this.elements.addToDatabase.checked
            });
        });
    }
    
    /**
     * Handle source folder browse button click
     */
    async handleSourceBrowse() {
        try {
            const folderPicker = document.querySelector('.folder-picker-modal');
            folderPicker.classList.add('show');
            
            // First select the source folder, without scanning subdirectories yet
            const selectedResult = await FolderPicker.show(false, 'folders', null, 'Select Source Folder', false);
            folderPicker.classList.remove('show');
            
            if (selectedResult && selectedResult.path) {
                this.elements.sourceFolder.value = selectedResult.path;
                
                // Publish source folder selected event
                this.eventManager.publish('source-folder-selected', {
                    path: selectedResult.path,
                    folderData: selectedResult
                });
            }
        } catch (error) {
            console.error('Error selecting folder:', error);
            this.showNotification('Failed to select folder', 'error');
        }
    }
    
    /**
     * Handle destination folder browse button click
     */
    async handleDestinationBrowse() {
        try {
            const folderPicker = document.querySelector('.folder-picker-modal');
            folderPicker.classList.add('show');
            
            // Open folder picker
            const selectedResult = await FolderPicker.show(false, 'folders', null, 'Select Destination Folder');
            folderPicker.classList.remove('show');
            
            if (selectedResult && selectedResult.path) {
                this.elements.destinationFolder.value = selectedResult.path;
                
                // Publish destination folder selected event
                this.eventManager.publish('destination-folder-selected', {
                    path: selectedResult.path
                });
            }
        } catch (error) {
            console.error('Error selecting folder:', error);
            this.showNotification('Failed to select destination folder', 'error');
        }
    }
    
    /**
     * Handle PDF folder browse button click
     */
    async handlePdfBrowse() {
        try {
            const folderPicker = document.querySelector('.folder-picker-modal');
            folderPicker.classList.add('show');
            
            // Open folder picker
            const selectedResult = await FolderPicker.show(false, 'folders', null, 'Select PDF Folder');
            folderPicker.classList.remove('show');
            
            if (selectedResult && selectedResult.path) {
                // Disable auto-find if manually selecting
                if (this.elements.autoFindPdf.checked) {
                    this.elements.autoFindPdf.checked = false;
                    this.addLogEntry("Auto-find PDF folder disabled due to manual selection");
                    
                    this.eventManager.publish('auto-find-pdf-toggle-changed', {
                        checked: false
                    });
                }
                
                this.elements.pdfFolder.value = selectedResult.path;
                this.elements.pdfFolderDisplay.textContent = selectedResult.path;
                
                // Clear any warning messages
                this.elements.pdfWarningDisplay.textContent = "";
                this.elements.pdfWarningDisplay.className = "";
                
                // Publish PDF folder selected event
                this.eventManager.publish('pdf-folder-selected', {
                    path: selectedResult.path
                });
            }
        } catch (error) {
            console.error('Error selecting PDF folder:', error);
            this.showNotification('Failed to select PDF folder', 'error');
        }
    }
    
    /**
     * Handle COMList file browse button click
     */
    async handleComlistBrowse() {
        try {
            const folderPicker = document.querySelector('.folder-picker-modal');
            folderPicker.classList.add('show');
            
            // Open folder picker, allowing only Excel files
            const selectedResult = await FolderPicker.show(false, 'files', ['xlsx', 'xls'], 'Select COMList File');
            folderPicker.classList.remove('show');
            
            if (selectedResult && selectedResult.path) {
                // Disable auto-find if manually selecting
                if (this.elements.autoFindComlist.checked) {
                    this.elements.autoFindComlist.checked = false;
                    this.addLogEntry("Auto-find COMList file disabled due to manual selection");
                    
                    this.eventManager.publish('auto-find-comlist-toggle-changed', {
                        checked: false
                    });
                }
                
                this.elements.comlistFile.value = selectedResult.path;
                this.elements.comlistFileDisplay.textContent = selectedResult.path;
                
                // Clear any warning messages
                this.elements.comlistWarningDisplay.textContent = "";
                this.elements.comlistWarningDisplay.className = "";
                
                // Publish COMList file selected event
                this.eventManager.publish('comlist-file-selected', {
                    path: selectedResult.path
                });
            }
        } catch (error) {
            console.error('Error selecting COMList file:', error);
            this.showNotification('Failed to select COMList file', 'error');
        }
    }
    
    /**
     * Handle field edit button click
     * @param {Element} button - Edit button element
     * @param {string} fieldId - Field ID
     */
    handleFieldEdit(button, fieldId) {
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
            
            // Publish field value changed event
            this.eventManager.publish('field-value-changed', {
                fieldId,
                value
            });
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
    }
    
    /**
     * Handle field blur event
     * @param {Element} field - Field element
     */
    handleFieldBlur(field) {
        const container = field.closest('.field-value-container');
        if (container && container.classList.contains('editing')) {
            const displayId = container.querySelector('.edit-field').getAttribute('data-display');
            const displayEl = document.getElementById(displayId);
            
            const value = field.value.trim();
            displayEl.textContent = value || 'Not set';
            
            // Exit edit mode
            container.classList.remove('editing');
            
            // Publish field value changed event
            this.eventManager.publish('field-value-changed', {
                fieldId: field.id,
                value
            });
        }
    }
    
    /**
     * Update source information in UI
     * @param {Object} sourceData - Source data object
     */
    updateSourceInfo(sourceData) {
        if (sourceData.path) {
            this.elements.sourceFolderDisplay.textContent = sourceData.path;
            
            if (sourceData.fileCount !== undefined) {
                this.elements.sourceFileCount.textContent = sourceData.fileCount.toString();
            }
            
            if (sourceData.totalSize !== undefined) {
                this.elements.sourceSize.textContent = sourceData.totalSizeFormatted || sourceData.totalSize.toString();
            }
        } else {
            this.elements.sourceFolderDisplay.textContent = 'Not set';
            this.elements.sourceFileCount.textContent = '0';
            this.elements.sourceSize.textContent = '0 B';
        }
    }
    
    /**
     * Update destination path display
     * @param {string} path - Destination path
     */
    updateDestinationPath(path) {
        this.elements.destinationPathDisplay.textContent = path || 'Not set';
    }
    
    /**
     * Update project information in UI
     * @param {Object} projectInfo - Project info object
     */
    updateProjectInfo(projectInfo) {
        // Update Archive ID
        this.elements.archiveId.value = projectInfo.archiveId || '';
        this.elements.archiveIdDisplay.textContent = projectInfo.archiveId || 'Not set';
        
        // Update Location
        this.elements.location.value = projectInfo.location || '';
        this.elements.locationDisplay.textContent = projectInfo.location || 'Not set';
        
        // Update Document Type
        this.elements.documentType.value = projectInfo.documentType || '';
        this.elements.documentTypeDisplay.textContent = projectInfo.documentType || 'Not set';
        
        // Update PDF path
        if (projectInfo.pdfPath) {
            this.elements.pdfFolder.value = projectInfo.pdfPath;
            this.elements.pdfFolderDisplay.textContent = projectInfo.pdfPath;
        }
        
        // Update COMList path
        if (projectInfo.comlistPath) {
            this.elements.comlistFile.value = projectInfo.comlistPath;
            this.elements.comlistFileDisplay.textContent = projectInfo.comlistPath;
        }
    }
    
    /**
     * Update PDF folder warning display
     * @param {Object} warningInfo - Warning info object
     */
    updatePdfWarning(warningInfo) {
        if (!warningInfo || !warningInfo.hasWarning) {
            this.elements.pdfWarningDisplay.textContent = '';
            this.elements.pdfWarningDisplay.className = '';
            return;
        }
        
        this.elements.pdfWarningDisplay.textContent = warningInfo.message;
        this.elements.pdfWarningDisplay.className = `warning-message ${warningInfo.type || 'warning'}`;
    }
    
    /**
     * Update COMList file warning display
     * @param {Object} warningInfo - Warning info object
     */
    updateComlistWarning(warningInfo) {
        if (!warningInfo || !warningInfo.hasWarning) {
            this.elements.comlistWarningDisplay.textContent = '';
            this.elements.comlistWarningDisplay.className = '';
            return;
        }
        
        this.elements.comlistWarningDisplay.textContent = warningInfo.message;
        this.elements.comlistWarningDisplay.className = `warning-message ${warningInfo.type || 'warning'}`;
    }
    
    /**
     * Toggle editability of project info fields
     * @param {boolean} enabled - Whether fields should be editable
     */
    toggleFieldsEditability(enabled) {
        this.elements.archiveId.disabled = !enabled;
        this.elements.location.disabled = !enabled;
        this.elements.documentType.disabled = !enabled;
        
        // Close any open editors
        document.querySelectorAll('.field-value-container.editing').forEach(container => {
            container.classList.remove('editing');
        });
    }
    
    /**
     * Update status badge
     * @param {string} status - Status class (initial, pending, completed, error)
     * @param {string} message - Status message
     * @param {string} target - Which badge(s) to update ('main', 'info', or 'both')
     */
    updateStatusBadge(status, message, target = 'both') {
        let icon = 'clock';
        if (status === 'completed') icon = 'check-circle';
        if (status === 'error') icon = 'exclamation-circle';
        if (status === 'pending') icon = 'sync';
        
        const badgeHtml = `<i class="fas fa-${icon}"></i> ${message}`;
        
        if (target === 'main' || target === 'both') {
            this.elements.mainStatusBadge.className = `status-badge ${status}`;
            this.elements.mainStatusBadge.innerHTML = badgeHtml;
        }
        
        if (target === 'info' || target === 'both') {
            this.elements.projectInfoStatusBadge.className = `status-badge ${status}`;
            this.elements.projectInfoStatusBadge.innerHTML = badgeHtml;
        }
    }
    
    /**
     * Show field error
     * @param {string} fieldId - ID of the field
     * @param {string} message - Error message
     */
    showFieldError(fieldId, message) {
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
    }
    
    /**
     * Clear field error
     * @param {string} fieldId - ID of the field
     */
    clearFieldError(fieldId) {
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
    }
    
    /**
     * Update transfer progress UI
     * @param {Object} progress - Progress info
     */
    updateTransferProgress(progress) {
        if (!progress) return;
        
        // Update current file
        if (progress.file && this.elements.currentFile) {
            this.elements.currentFile.textContent = progress.file;
        }
        
        // Update progress bar and percentage
        if (progress.overallProgress !== undefined) {
            const percentage = Math.round(progress.overallProgress * 100);
            
            // Update progress bar width
            if (this.elements.transferProgress) {
                this.elements.transferProgress.style.width = `${percentage}%`;
            }
            
            // Update percentage text
            if (this.elements.progressPercentage) {
                this.elements.progressPercentage.textContent = `${percentage}%`;
            }
        }
        
        // Update files transferred counter
        if (progress.filesTransferred !== undefined && 
            progress.totalFiles !== undefined && 
            this.elements.filesTransferred) {
            this.elements.filesTransferred.textContent = `${progress.filesTransferred}/${progress.totalFiles}`;
        }
        
        // Update transfer speed
        if (progress.speed !== undefined && this.elements.transferSpeed) {
            this.elements.transferSpeed.textContent = progress.speedFormatted || 
                `${progress.speed.toFixed(1)} B/s`;
        }
        
        // Update estimated time remaining
        if (progress.timeRemaining !== undefined && this.elements.timeRemaining) {
            this.elements.timeRemaining.textContent = progress.timeRemainingFormatted || 
                progress.timeRemaining.toString();
        }
    }
    
    /**
     * Update transfer status
     * @param {string} status - Status string (in-progress, completed, error, cancelled)
     * @param {string} message - Status message
     */
    updateTransferStatus(status, message) {
        const headerStatusBadge = document.querySelector('.transfer-header .status-badge');
        
        // Set default message if not provided
        if (!message) {
            if (status === 'in-progress') message = 'Transfer in Progress';
            else if (status === 'completed') message = 'Transfer Complete';
            else if (status === 'error') message = 'Transfer Failed';
            else if (status === 'cancelled') message = 'Transfer Cancelled';
        }
        
        // Map status to CSS class and icon
        let cssClass, icon;
        switch (status) {
            case 'in-progress':
                cssClass = 'pending';
                icon = 'sync fa-spin';
                break;
            case 'completed':
                cssClass = 'completed';
                icon = 'check-circle';
                break;
            case 'error':
                cssClass = 'error';
                icon = 'exclamation-circle';
                break;
            case 'cancelled':
                cssClass = 'error';
                icon = 'times-circle';
                break;
            default:
                cssClass = 'initial';
                icon = 'clock';
        }
        
        // Update header badge
        if (headerStatusBadge) {
            headerStatusBadge.className = `status-badge ${cssClass}`;
            headerStatusBadge.innerHTML = `<i class="fas fa-${icon}"></i> ${message}`;
        }
        
        // Update transfer status badge
        this.elements.transferStatus.className = `status-badge ${cssClass}`;
        this.elements.transferStatus.innerHTML = `<i class="fas fa-${icon}"></i> ${status === 'in-progress' ? 'In Progress' : message}`;
        
        // Update project status badges
        this.updateStatusBadge(
            status === 'in-progress' ? 'pending' : 
            status === 'completed' ? 'completed' : 'error',
            message,
            'both'
        );
    }
    
    /**
     * Add a log entry
     * @param {string} message - Log message
     */
    addLogEntry(message) {
        const now = new Date();
        const timeString = now.toTimeString().split(' ')[0];
        
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="log-time">${timeString}</span>
            <span class="log-message">${message}</span>
        `;
        
        this.elements.transferLog.appendChild(logEntry);
        this.elements.transferLog.scrollTop = this.elements.transferLog.scrollHeight;
    }
    
    /**
     * Show notification message
     * @param {string} message - Message to display
     * @param {string} type - Notification type (success, error, warning, info)
     */
    showNotification(message, type = 'info') {
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
    
    /**
     * Get CSRF token
     * @returns {string} CSRF token
     */
    getCsrfToken() {
        // Use DatabaseService to get CSRF token
        return this.dbService._getCsrfToken();
    }

    /**
     * Add a method to collect current project info
     * @returns {Object} Current project info
     */
    getProjectInfo() {
        return {
            archiveId: this.elements.archiveId.value.trim(),
            location: this.elements.location.value.trim(),
            documentType: this.elements.documentType.value.trim(),
            pdfPath: this.elements.pdfFolder.value.trim(),
            comlistPath: this.elements.comlistFile.value.trim(),
            
            // Include other properties as needed for your database
            addToDatabase: this.elements.addToDatabase.checked,
            autoSelectPath: this.elements.autoSelectPath.checked,
            autoParse: this.elements.autoParse.checked,
            autoFindPdf: this.elements.autoFindPdf.checked,
            autoFindComlist: this.elements.autoFindComlist.checked,
            createSubfolder: this.elements.createSubfolder.checked
        };
    }

    /**
     * Update database status in UI
     * @param {Object} dbResult - Database operation result
     */
    updateDatabaseStatus(dbResult) {
        if (dbResult.status === 'success') {
            this.addLogEntry(`Project saved to database with ID: ${dbResult.project_id}`);
            
            // Update status badge to show database ID if needed
            const dbBadge = document.createElement('span');
            dbBadge.className = 'database-badge';
            dbBadge.innerHTML = `<i class="fas fa-database"></i> ID: ${dbResult.project_id}`;
            
            // Add to status area if you have one
            const statusArea = document.querySelector('.database-status');
            if (statusArea) {
                statusArea.innerHTML = '';
                statusArea.appendChild(dbBadge);
            }
        } else if (dbResult.status === 'error') {
            this.addLogEntry(`Database error: ${dbResult.message}`);
        } else if (dbResult.status === 'skipped') {
            this.addLogEntry('Database storage skipped (disabled by user)');
        }
    }
}
