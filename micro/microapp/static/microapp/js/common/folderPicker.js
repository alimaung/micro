/**
 * folderPicker.js - Folder selection dialog for microfilm registration system
 * Handles drive and folder selection UI and interactions
 */

const FolderPicker = {
    // State
    modal: null,
    folderList: null,
    selectButton: null,
    folders: [],
    files: [],
    _resolve: null,
    _reject: null,
    currentPath: 'Y:\\',
    breadcrumbs: [],
    newFolderForm: null,
    folderNameInput: null,
    pathDisplay: null,
    driveList: null,
    drives: [],
    driveNames: {}, // Added to store drive names
    specialDriveColors: {
        'microfilm-engineering': '#ff6666', // Red
        'microfilm-archive': '#ffcc00',     // Yellow
        'microfilm-transit': '#00ff00'      // Green
    },
    mode: 'folders', // 'folders', 'files', or 'both'
    fileTypes: null,
    showAllFiles: false,
    customTitle: null, // Add custom title property
    scanSubdirectories: false,
    fullStructure: null,

    /**
     * Initialize the folder picker
     * @throws {Error} If required DOM elements are not found
     */
    initialize: function() {
        this.initializeElements();
        if (!this.modal) {
            throw new Error('Required DOM elements for FolderPicker not found');
        }
        this.addEventListeners();
    },

    /**
     * Initialize DOM element references
     */
    initializeElements: function() {
        this.modal = document.querySelector('.folder-picker-modal');
        
        // Drive selection elements
        this.driveList = this.modal ? this.modal.querySelector('.drive-list') : null;
        this.driveSelectionView = this.modal ? this.modal.querySelector('.drive-selection-view') : null;
        this.driveViewButtons = this.modal ? this.modal.querySelector('.drive-view-buttons') : null;
        
        // Folder selection elements
        this.folderSelectionView = this.modal ? this.modal.querySelector('.folder-selection-view') : null;
        this.folderList = this.modal ? this.modal.querySelector('.folder-list') : null;
        this.selectButton = this.modal ? this.modal.querySelector('.select-button') : null;
        this.browseLocalButton = this.modal ? this.modal.querySelector('.browse-local-button') : null;
        this.breadcrumbsContainer = this.modal ? this.modal.querySelector('.breadcrumbs-container') : null;
        this.newFolderButton = this.modal ? this.modal.querySelector('.new-folder-button') : null;
        this.backToDrivesButton = this.modal ? this.modal.querySelector('.back-to-drives') : null;
        this.folderViewButtons = this.modal ? this.modal.querySelector('.folder-view-buttons') : null;
        
        // New folder form elements
        this.newFolderForm = this.modal ? this.modal.querySelector('.new-folder-form') : null;
        this.folderNameInput = this.modal ? this.modal.querySelector('.folder-name-input') : null;
        this.pathDisplay = this.modal ? this.modal.querySelector('.path-display') : null;
        this.createFolderBtn = this.modal ? this.modal.querySelector('.create-folder-btn') : null;
        this.cancelNewFolderBtn = this.modal ? this.modal.querySelector('.cancel-new-folder') : null;
    },

    /**
     * Add event listeners to dialog buttons
     * @throws {Error} If required button elements are not found
     */
    addEventListeners: function() {
        const closeButton = this.modal.querySelector('.close-button');
        const cancelButton = this.modal.querySelector('.cancel-button');
        
        if (!closeButton || !cancelButton) {
            throw new Error('Required button elements not found');
        }

        // Common modal buttons
        closeButton.addEventListener('click', () => this.hide());
        cancelButton.addEventListener('click', () => this.hide());
        
        // Drive selection view buttons
        
        // Folder selection view buttons
        this.selectButton.addEventListener('click', () => this.handleSelect());
        this.browseLocalButton.addEventListener('click', () => this.openNativeFolderPicker());
        this.newFolderButton.addEventListener('click', () => this.showNewFolderForm());
        this.backToDrivesButton.addEventListener('click', () => this.showDriveSelectionView());
        
        // New folder form event listeners
        if (this.createFolderBtn && this.cancelNewFolderBtn && this.folderNameInput) {
            this.createFolderBtn.addEventListener('click', () => this.submitNewFolderForm());
            this.cancelNewFolderBtn.addEventListener('click', () => this.hideNewFolderForm());
            
            // Allow pressing Enter to submit the form
            this.folderNameInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.submitNewFolderForm();
                } else if (e.key === 'Escape') {
                    this.hideNewFolderForm();
                }
            });
        }
    },

    /**
     * Show the folder picker dialog
     * @param {boolean} openYDirectly - Whether to open Y: drive directly
     * @param {string} mode - 'folders', 'files', or 'both' 
     * @param {string|string[]} fileTypes - Optional file extension(s) to filter by (e.g., 'pdf' or ['pdf', 'csv'])
     * @param {string} dialogTitle - Optional custom title for the dialog
     * @param {boolean} scanSubdirectories - Whether to scan all subdirectories for auto-detection
     * @returns {Promise<object>} Object containing selected path and folder/file structure
     */
    show: function(openYDirectly = false, mode = 'folders', fileTypes = null, dialogTitle = null, scanSubdirectories = false) {
        return new Promise((resolve, reject) => {
            this._resolve = resolve;
            this._reject = reject;
            
            // Reset state
            this.selectedFolder = null;
            this.selectedFile = null;
            this.mode = mode;
            this.fileTypes = fileTypes;
            this.showAllFiles = false; // Default to filtered view when filter is provided
            this.hideNewFolderForm();
            this.customTitle = dialogTitle; // Store the custom title
            this.scanSubdirectories = scanSubdirectories; // Store the scan option
            this.fullStructure = null; // Reset full structure
            
            // Normalize fileTypes to array if provided
            if (this.fileTypes && !Array.isArray(this.fileTypes)) {
                this.fileTypes = [this.fileTypes];
            }
            
            // Convert file extensions to lowercase and ensure they don't include the dot
            if (this.fileTypes) {
                this.fileTypes = this.fileTypes.map(type => 
                    type.toLowerCase().replace(/^\./, '')
                );
            }
            
            // Define title and mode indicator
            let title = this.customTitle || 'Select Folder';
            let modeClass = 'folders-mode';
            let modeIndicator = 'Folders Only';
            
            if (mode === 'files') {
                title = this.customTitle || 'Select File';
                modeClass = 'files-mode';
                modeIndicator = 'Files Only';
                
                if (this.fileTypes && this.fileTypes.length > 0) {
                    const typeList = this.fileTypes.map(t => t.toUpperCase()).join(', ');
                    modeIndicator = `${typeList} Files Only`;
                }
            } else if (mode === 'both') {
                title = this.customTitle || 'Select File or Folder';
                modeClass = 'both-mode';
                modeIndicator = 'Files & Folders';
            }
            
            const modeIndicatorHTML = `<span class="mode-indicator ${modeClass}">${modeIndicator}</span>`;
            
            if (openYDirectly) {
                // Open X: drive directly (changed from Y:)
                this.currentPath = 'X:\\';
                this.showFolderSelectionView();
                this.fetchContents(this.currentPath, this.scanSubdirectories);
                this.modal.querySelector('.modal-title').innerHTML = 
                    `${title} (X: Drive) ${modeIndicatorHTML}`;
            } else {
                // Show drive selection view (which will also fetch drives)
                this.showDriveSelectionView();
                this.modal.querySelector('.modal-title').textContent = this.customTitle || 'Select Drive';
            }
            
            this.modal.style.display = 'block';
        });
    },

    /**
     * Show the drive selection view
     */
    showDriveSelectionView: function() {
        this.driveSelectionView.classList.remove('hidden');
        this.folderSelectionView.classList.remove('active');
        this.driveViewButtons.style.display = 'flex';
        this.folderViewButtons.classList.remove('active');
        this.modal.querySelector('.modal-title').textContent = this.customTitle || 'Select Drive';
        
        // Always fetch and refresh drive data when showing the drive selection view
        this.fetchDrives();
    },

    /**
     * Show the folder selection view
     */
    showFolderSelectionView: function() {
        this.driveSelectionView.classList.add('hidden');
        this.folderSelectionView.classList.add('active');
        this.driveViewButtons.style.display = 'none';
        this.folderViewButtons.classList.add('active');
        
        // Update the title with mode indicator
        let title = this.customTitle || 'Select Folder';
        let modeClass = 'folders-mode';
        let modeIndicator = 'Folders Only';
        
        if (this.mode === 'files') {
            title = this.customTitle || 'Select File';
            modeClass = 'files-mode';
            modeIndicator = 'Files Only';
            
            if (this.fileTypes && this.fileTypes.length > 0) {
                const typeList = this.fileTypes.map(t => t.toUpperCase()).join(', ');
                modeIndicator = `${typeList} Files Only`;
            }
        } else if (this.mode === 'both') {
            title = this.customTitle || 'Select File or Folder';
            modeClass = 'both-mode';
            modeIndicator = 'Files & Folders';
        }
        
        const modeIndicatorHTML = `<span class="mode-indicator ${modeClass}">${modeIndicator}</span>`;
        this.modal.querySelector('.modal-title').innerHTML = `${title} ${modeIndicatorHTML}`;
    },

    /**
     * Fetch available drives from the server
     */
    fetchDrives: function() {
        fetch('/list-drives/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            if (!Array.isArray(data.drives)) {
                throw new Error('Invalid drive data received from server');
            }

            this.drives = data.drives;
            
            // Store drive names if provided by the server
            if (data.driveNames && typeof data.driveNames === 'object') {
                this.driveNames = data.driveNames;
            }
            
            this.renderDrives();
        })
        .catch(error => {
            console.error('Error fetching drives:', error);
            if (this._reject) {
                this._reject(error);
            }
        });
    },

    /**
     * Render the drive list in the dialog
     */
    renderDrives: function() {
        this.driveList.innerHTML = '';
        
        if (this.drives.length === 0) {
            const message = document.createElement('div');
            message.className = 'folder-list-message';
            message.textContent = 'No drives found';
            this.driveList.appendChild(message);
        } else {
            this.drives.forEach(drive => {
                const item = document.createElement('div');
                item.className = 'drive-item';
                
                // Check if it's a special drive to use special icon
                let icon = 'fas fa-hdd';
                if (drive === 'C:\\') {
                    icon = 'fas fa-laptop';
                } else if (drive === 'Y:\\' || drive === 'X:\\') {
                    icon = 'fas fa-network-wired';
                } else if (drive.charCodeAt(0) >= 69) { // E: and above often removable
                    icon = 'fab fa-usb';
                }
                
                // Get drive name if available
                const driveName = this.driveNames[drive] || '';
                
                // Apply special styling for specific drive names
                if (driveName) {
                    // First check by exact drive name
                    if (driveName === "microfilm-engineering") {
                        item.classList.add('special-drive');
                        item.classList.add('drive-microfilm-engineering');
                    } 
                    else if (driveName === "microfilm-archive") {
                        item.classList.add('special-drive');
                        item.classList.add('drive-microfilm-archive');
                    }
                    else if (driveName === "microfilm-transit") {
                        item.classList.add('special-drive');
                        item.classList.add('drive-microfilm-transit');
                    }
                    // Then check by substring in case volume names have variations
                    else {
                        for (const [specialName, color] of Object.entries(this.specialDriveColors)) {
                            if (driveName.toLowerCase().includes(specialName.toLowerCase())) {
                                item.classList.add('special-drive');
                                item.classList.add(`drive-${specialName.toLowerCase()}`);
                                break;
                            }
                        }
                    }
                }
                
                // Add drive letter and name if available
                item.innerHTML = `
                    <span class="drive-icon"><i class="${icon}"></i></span>
                    <div class="drive-info">
                        <span class="drive-letter">${drive}</span>
                        ${driveName ? `<span class="drive-name">${driveName}</span>` : ''}
                    </div>
                `;
                
                item.addEventListener('click', () => {
                    this.currentPath = drive;
                    this.showFolderSelectionView();
                    this.fetchContents(drive, this.scanSubdirectories);
                });
                
                this.driveList.appendChild(item);
            });
        }
    },

    /**
     * Fetch folders and files for the specified path
     * @param {string} path - The path to fetch contents for
     * @param {boolean} scanSubdirectories - Whether to scan all subdirectories (for auto-detection)
     */
    fetchContents: function(path, scanSubdirectories) {
        // Set default value for scanSubdirectories
        scanSubdirectories = scanSubdirectories || false;
        // Always fetch both folders and files, regardless of mode
        let apiEndpoint = '/list-drive-contents/?path=' + encodeURIComponent(path);
        
        // If scanning subdirectories, add a parameter
        if (scanSubdirectories) {
            apiEndpoint += '&scan_subdirectories=true';
        }
        
        fetch(apiEndpoint, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            if (!Array.isArray(data.folders) || !Array.isArray(data.files)) {
                throw new Error('Invalid data received from server');
            }

            this.folders = data.folders;
            this.files = data.files;
            
            // If subdirectories were scanned, store the full structure
            if (scanSubdirectories && data.fullStructure) {
                this.fullStructure = data.fullStructure;
            }
            
            this.currentPath = data.currentPath || path;
            this.renderContents();
            this.renderBreadcrumbs();
        })
        .catch(error => {
            console.error('Error fetching contents:', error);
            if (this._reject) {
                this._reject(error);
            }
        });
    },

    /**
     * Render breadcrumbs navigation
     */
    renderBreadcrumbs: function() {
        if (!this.breadcrumbsContainer) return;
        
        // Parse the current path into breadcrumb segments
        const segments = this.currentPath.split('\\').filter(Boolean);
        this.breadcrumbs = [];
        
        // Start with the drive
        let currentPath = segments[0] + '\\';
        this.breadcrumbs.push({ 
            label: segments[0], 
            path: currentPath,
            isDrive: true // Mark this as a drive for special handling
        });
        
        // Add each folder in the path
        for (let i = 1; i < segments.length; i++) {
            currentPath += segments[i] + '\\';
            this.breadcrumbs.push({ 
                label: segments[i], 
                path: currentPath,
                isDrive: false
            });
        }
        
        // Render breadcrumbs
        this.breadcrumbsContainer.innerHTML = '';
        
        this.breadcrumbs.forEach((crumb, index) => {
            const breadcrumb = document.createElement('span');
            breadcrumb.className = 'breadcrumb';
            breadcrumb.textContent = crumb.label;
            
            breadcrumb.addEventListener('click', () => {
                this.navigateTo(crumb.path);
            });
            
            this.breadcrumbsContainer.appendChild(breadcrumb);
            
            // Add separator except for the last item
            if (index < this.breadcrumbs.length - 1) {
                const separator = document.createElement('span');
                separator.className = 'breadcrumb-separator';
                separator.innerHTML = ' <i class="fas fa-chevron-right"></i> ';
                this.breadcrumbsContainer.appendChild(separator);
            }
        });
    },

    /**
     * Navigate to a specific path
     * @param {string} path - The path to navigate to
     */
    navigateTo: function(path) {
        this.currentPath = path;
        this.fetchContents(path, this.scanSubdirectories);
        this.selectButton.disabled = true;
        this.selectedFolder = null;
        this.selectedFile = null;
        this.hideNewFolderForm();
    },

    /**
     * Hide the folder picker dialog
     */
    hide: function() {
        this.modal.style.display = 'none';
        if (this._reject) {
            this._reject('Dialog closed');
            this._reject = null;
            this._resolve = null;
        }
    },

    /**
     * Render the folder and file list in the dialog
     */
    renderContents: function() {
        this.folderList.innerHTML = '';
        
        // Always add folders for navigation
        let hasContent = this.folders.length > 0;
        let hasFiles = false;
        
        // File type filter status message
        if (this.mode !== 'folders' && this.fileTypes && this.fileTypes.length > 0) {
            const filterBanner = document.createElement('div');
            filterBanner.className = 'file-filter-banner';
            
            const filterTypes = this.fileTypes.map(t => t.toUpperCase()).join(', ');
            filterBanner.innerHTML = `
                <div class="filter-status">
                    <i class="fas fa-filter"></i>
                    <span>Looking for ${filterTypes} files</span>
                </div>
                <div class="filter-toggle">
                    <label class="filter-toggle-label">
                        <input type="checkbox" class="filter-toggle-input" ${this.showAllFiles ? 'checked' : ''}>
                        <span class="filter-toggle-text">Show all files</span>
                    </label>
                </div>
            `;
            
            // Add event listener to toggle filter
            const toggleInput = filterBanner.querySelector('.filter-toggle-input');
            toggleInput.addEventListener('change', () => {
                this.showAllFiles = toggleInput.checked;
                this.renderContents();
            });
            
            this.folderList.appendChild(filterBanner);
        }
        
        // First render folders for navigation
        this.folders.forEach(folder => {
            const item = document.createElement('div');
            item.className = 'folder-item';
            item.innerHTML = '<i class="fas fa-folder"></i><span>' + folder + '</span>';
            
            item.addEventListener('click', (event) => {
                if (event.detail === 1) {
                    // Single click selects the folder only if we're in folders or both mode
                    if (this.mode !== 'files') {
                        this.handleFolderClick(item, folder);
                    }
                } else if (event.detail === 2) {
                    // Double click always navigates into the folder
                    this.navigateTo(this.currentPath + folder + '\\');
                }
            });
            
            this.folderList.appendChild(item);
        });
        
        // Render files if not in folders-only mode
        if (this.mode !== 'folders') {
            this.files.forEach(file => {
                // Skip non-matching files unless showAllFiles is true
                const extension = file.split('.').pop().toLowerCase();
                const matchesFilter = !this.fileTypes || 
                                     this.fileTypes.length === 0 || 
                                     this.fileTypes.includes(extension);
                                     
                if (!matchesFilter && !this.showAllFiles) {
                    return;
                }
                
                hasFiles = true;
                
                const item = document.createElement('div');
                item.className = 'file-item';
                
                // Add classes based on matching status
                if (this.fileTypes && this.fileTypes.length > 0) {
                    if (matchesFilter) {
                        item.classList.add('file-matches-filter');
                    } else {
                        item.classList.add('file-not-matching');
                    }
                }
                
                // Determine file icon based on extension
                let iconClass = 'fas fa-file';
                
                // Basic file type detection
                if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'].includes(extension)) {
                    iconClass = 'fas fa-file-image';
                } else if (['doc', 'docx', 'odt', 'rtf', 'txt'].includes(extension)) {
                    iconClass = 'fas fa-file-alt';
                } else if (['xls', 'xlsx', 'csv'].includes(extension)) {
                    iconClass = 'fas fa-file-excel';
                } else if (['pdf'].includes(extension)) {
                    iconClass = 'fas fa-file-pdf';
                } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
                    iconClass = 'fas fa-file-archive';
                }
                
                // Add file icon and name
                item.innerHTML = `<i class="${iconClass}"></i><span>${file}</span>`;
                
                // Add badge for matching or non-matching files
                if (this.fileTypes && this.fileTypes.length > 0) {
                    if (matchesFilter) {
                        item.innerHTML += '<span class="file-badge match">Valid Format</span>';
                    } else {
                        item.innerHTML += '<span class="file-badge no-match">Invalid Format</span>';
                    }
                }
                
                item.addEventListener('click', () => {
                    // If file doesn't match filter, show warning but don't select
                    if (!matchesFilter && this.fileTypes && this.fileTypes.length > 0) {
                        // Apply shake animation
                        item.classList.add('invalid-shake');
                        setTimeout(() => {
                            item.classList.remove('invalid-shake');
                        }, 500);
                        
                        this.showInvalidFileTypeWarning(file, this.fileTypes);
                    } else {
                        this.handleFileClick(item, file);
                    }
                });
                
                this.folderList.appendChild(item);
            });
        }
        
        // If no content to display
        if (this.folders.length === 0 && (!hasFiles || this.mode === 'folders')) {
            const message = document.createElement('div');
            message.className = 'folder-list-message';
            
            if (this.mode === 'folders') {
                message.textContent = 'No folders found in this directory';
            } else if (this.mode === 'files') {
                if (this.fileTypes && this.fileTypes.length > 0 && !this.showAllFiles) {
                    const typeList = this.fileTypes.map(t => t.toUpperCase()).join(', ');
                    message.innerHTML = `<i class="fas fa-search"></i> No ${typeList} files found in this directory`;
                    message.innerHTML += '<div class="no-files-action"><button class="show-all-files-btn">Show all files</button></div>';
                    
                    const showAllBtn = message.querySelector('.show-all-files-btn');
                    showAllBtn.addEventListener('click', () => {
                        this.showAllFiles = true;
                        this.renderContents();
                    });
                } else {
                    message.textContent = 'No files found in this directory';
                }
            } else {
                message.textContent = 'No files or folders found in this directory';
            }
            
            this.folderList.appendChild(message);
        }
        
        // Update the folder list hint based on mode
        const hintElement = this.modal.querySelector('.folder-list-hint');
        if (hintElement) {
            if (this.mode === 'folders') {
                hintElement.innerHTML = '<i class="fas fa-info-circle"></i> Double-click to open a folder. Single-click to select a folder.';
            } else if (this.mode === 'files') {
                let hintText = 'Double-click to open a folder. Single-click to select a file.';
                if (this.fileTypes && this.fileTypes.length > 0) {
                    const typeList = this.fileTypes.map(t => t.toUpperCase()).join(', ');
                    hintText = `Looking for ${typeList} files. Files with other extensions cannot be selected.`;
                }
                hintElement.innerHTML = `<i class="fas fa-info-circle"></i> ${hintText}`;
            } else {
                hintElement.innerHTML = '<i class="fas fa-info-circle"></i> Double-click to open a folder. Single-click to select an item.';
            }
        }
    },

    /**
     * Handle folder item click
     * @param {HTMLElement} item - The clicked folder item element
     * @param {string} folder - The folder name
     */
    handleFolderClick: function(item, folder) {
        // Deselect all other items
        this.folderList.querySelectorAll('.folder-item, .file-item').forEach(el => {
            el.classList.remove('selected');
        });
        // Select this folder
        item.classList.add('selected');
        this.selectedFolder = folder;
        this.selectedFile = null;
        this.selectButton.disabled = false;
    },

    /**
     * Handle file item click
     * @param {HTMLElement} item - The clicked file item element
     * @param {string} file - The file name
     */
    handleFileClick: function(item, file) {
        // Deselect all other items
        this.folderList.querySelectorAll('.folder-item, .file-item').forEach(el => {
            el.classList.remove('selected');
        });
        // Select this file
        item.classList.add('selected');
        this.selectedFile = file;
        this.selectedFolder = null;
        this.selectButton.disabled = false;
    },

    /**
     * Handle select button click
     */
    handleSelect: function() {
        if (this.selectedFolder && this._resolve) {
            // Return full path including selected folder
            // Also return current folders and files lists for auto-detection features
            this._resolve({
                path: this.currentPath + this.selectedFolder,
                folders: this.folders,
                files: this.files,
                currentPath: this.currentPath
            });
            this.hide();
        } else if (this.selectedFile && this._resolve) {
            // Return full path including selected file
            this._resolve({
                path: this.currentPath + this.selectedFile,
                isFile: true
            });
            this.hide();
        } else if (this._resolve) {
            // Return current directory path if no specific folder or file is selected
            // Also return current folders and files lists for auto-detection features
            this._resolve({
                path: this.currentPath,
                folders: this.folders,
                files: this.files,
                currentPath: this.currentPath
            });
            this.hide();
        }
    },

    /**
     * Show the new folder form 
     */
    showNewFolderForm: function() {
        if (this.newFolderForm && this.pathDisplay && this.folderNameInput) {
            // Display the current path in the form
            this.pathDisplay.textContent = 'Location: ' + this.currentPath;
            
            // Show the form
            this.newFolderForm.classList.add('visible');
            
            // Clear and focus the input
            this.folderNameInput.value = '';
            setTimeout(() => this.folderNameInput.focus(), 50);
        }
    },

    /**
     * Hide the new folder form
     */
    hideNewFolderForm: function() {
        if (this.newFolderForm) {
            this.newFolderForm.classList.remove('visible');
            this.folderNameInput.value = '';
        }
    },

    /**
     * Submit the new folder form
     */
    submitNewFolderForm: function() {
        const folderName = this.folderNameInput.value.trim();
        if (!folderName) {
            // Add some visual feedback if name is empty
            this.folderNameInput.style.borderColor = '#e74c3c';
            setTimeout(() => {
                this.folderNameInput.style.borderColor = '';
            }, 1500);
            return;
        }
        
        // Create the folder
        this.createNewFolder(folderName);
        
        // Hide the form
        this.hideNewFolderForm();
    },

    /**
     * Create a new folder at the current path
     * @param {string} folderName - The name of the folder to create
     */
    createNewFolder: function(folderName) {
        // Create a notification to show while creating
        const notification = document.createElement('div');
        notification.className = 'folder-list-message';
        notification.textContent = 'Creating folder...';
        this.folderList.innerHTML = '';
        this.folderList.appendChild(notification);
        
        fetch('/create-folder/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                path: this.currentPath,
                folderName: folderName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Refresh the folder list
            this.fetchContents(this.currentPath);
            
            // Show success message using a custom notification
            this.showNotification(`Folder "${folderName}" created successfully`, 'success');
        })
        .catch(error => {
            console.error('Error creating folder:', error);
            this.showNotification(`Failed to create folder: ${error.message}`, 'error');
            
            // Refresh the folder list anyway
            this.fetchContents(this.currentPath);
        });
    },
    
    /**
     * Show custom notification inside the modal
     * @param {string} message - Message to display
     * @param {string} type - Notification type (success, error)
     */
    showNotification: function(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // Set icon based on type
        let icon = '';
        if (type === 'success') {
            icon = '<i class="fas fa-check-circle"></i>';
        } else if (type === 'error') {
            icon = '<i class="fas fa-times-circle"></i>';
        } else {
            icon = '<i class="fas fa-info-circle"></i>';
        }
        
        notification.innerHTML = icon + ' ' + message;
        
        // Add to the modal
        this.modal.appendChild(notification);
        
        // Position the notification
        notification.style.position = 'absolute';
        notification.style.bottom = '80px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '4px';
        notification.style.color = '#fff';
        notification.style.fontSize = '14px';
        notification.style.zIndex = '1010';
        notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        
        // Set color based on type
        if (type === 'success') {
            notification.style.backgroundColor = '#4caf50';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#e74c3c';
        } else {
            notification.style.backgroundColor = '#2196f3';
        }
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    },
    
    /**
     * Get CSRF token from cookies
     * @returns {string} CSRF token
     */
    getCsrfToken: function() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    /**
     * Open the native folder picker dialog
     */
    openNativeFolderPicker: function() {
        fetch('/browse-local-folders/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            if (!data.path) {
                throw new Error('No folder path received from server');
            }
            if (this._resolve) {
                this._resolve(data.path);
                this.hide();
            }
        })
        .catch(error => {
            console.error('Error browsing local folders:', error);
        });
    },

    /**
     * Show a warning when user tries to select an invalid file type
     * @param {string} fileName - The file that was clicked
     * @param {string[]} validTypes - Array of valid file extensions
     */
    showInvalidFileTypeWarning: function(fileName, validTypes) {
        // Get the file extension
        const extension = fileName.split('.').pop().toLowerCase();
        
        // Prepare valid extensions list
        const validExtList = validTypes.map(t => t.toUpperCase()).join(', ');
        
        // Create a toast notification instead of a popup
        const toast = document.createElement('div');
        toast.className = 'file-toast-notification';
        toast.innerHTML = `
            <div class="toast-icon"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="toast-message">
                Invalid file type (.${extension.toUpperCase()}). Please select a ${validExtList} file.
            </div>
        `;
        
        // Add to the modal
        this.modal.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
        
        // Highlight the file-filter banner to draw attention to the filter
        const filterBanner = this.folderList.querySelector('.file-filter-banner');
        if (filterBanner) {
            filterBanner.classList.add('highlight-filter');
            setTimeout(() => {
                filterBanner.classList.remove('highlight-filter');
            }, 1500);
        }
    }
};

// Initialize the folder picker when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        FolderPicker.initialize();
    } catch (error) {
        console.error('Failed to initialize FolderPicker:', error);
    }
});