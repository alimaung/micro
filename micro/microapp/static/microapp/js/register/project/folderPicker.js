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
    _resolve: null,
    _reject: null,
    currentPath: 'Y:\\',
    breadcrumbs: [],
    newFolderForm: null,
    folderNameInput: null,
    pathDisplay: null,
    driveList: null,
    drives: [],

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
     * Show the folder picker dialog and fetch either drives or Y: folders
     * @param {boolean} openYDirectly - Whether to open Y: drive directly
     * @returns {Promise<string>} Selected folder path or rejection if dialog is closed
     */
    show: function(openYDirectly = false) {
        return new Promise((resolve, reject) => {
            this._resolve = resolve;
            this._reject = reject;
            
            // Reset state
            this.selectedFolder = null;
            this.hideNewFolderForm();
            
            if (openYDirectly) {
                // Open Y: drive directly
                this.currentPath = 'Y:\\';
                this.showFolderSelectionView();
                this.fetchFolders(this.currentPath);
                this.modal.querySelector('.modal-title').textContent = 'Select Folder (Y: Drive)';
            } else {
                // Show drive selection view (which will also fetch drives)
                this.showDriveSelectionView();
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
        this.modal.querySelector('.modal-title').textContent = 'Select Drive';
        
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
        this.modal.querySelector('.modal-title').textContent = 'Select Folder';
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
                } else if (drive === 'Y:\\') {
                    icon = 'fas fa-network-wired';
                } else if (drive.charCodeAt(0) >= 69) { // E: and above often removable
                    icon = 'fab fa-usb';
                }
                
                item.innerHTML = `
                    <span class="drive-icon"><i class="${icon}"></i></span>
                    <span class="drive-label">${drive}</span>
                `;
                
                item.addEventListener('click', () => {
                    this.currentPath = drive;
                    this.showFolderSelectionView();
                    this.fetchFolders(drive);
                });
                
                this.driveList.appendChild(item);
            });
        }
    },

    /**
     * Fetch folders for the specified path
     * @param {string} path - The path to fetch folders for
     */
    fetchFolders: function(path) {
        fetch('/list-drive-folders/?path=' + encodeURIComponent(path), {
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

            if (!Array.isArray(data.folders)) {
                throw new Error('Invalid folder data received from server');
            }

            this.folders = data.folders;
            this.currentPath = data.currentPath || path;
            this.renderFolders();
            this.renderBreadcrumbs();
        })
        .catch(error => {
            console.error('Error fetching folders:', error);
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
        this.fetchFolders(path);
        this.selectButton.disabled = true;
        this.selectedFolder = null;
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
     * Render the folder list in the dialog
     */
    renderFolders: function() {
        this.folderList.innerHTML = '';
        
        if (this.folders.length === 0) {
            const message = document.createElement('div');
            message.className = 'folder-list-message';
            message.textContent = 'No folders found in this directory';
            this.folderList.appendChild(message);
        } else {
            this.folders.forEach(folder => {
                const item = document.createElement('div');
                item.className = 'folder-item';
                item.innerHTML = '<i class="fas fa-folder"></i><span>' + folder + '</span>';
                
                item.addEventListener('click', (event) => {
                    if (event.detail === 1) {
                        // Single click selects the folder
                        this.handleFolderClick(item, folder);
                    } else if (event.detail === 2) {
                        // Double click navigates into the folder
                        this.navigateTo(this.currentPath + folder + '\\');
                    }
                });
                
                this.folderList.appendChild(item);
            });
        }
    },

    /**
     * Handle folder item click
     * @param {HTMLElement} item - The clicked folder item element
     * @param {string} folder - The folder name
     */
    handleFolderClick: function(item, folder) {
        // Deselect all other folders
        this.folderList.querySelectorAll('.folder-item').forEach(el => {
            el.classList.remove('selected');
        });
        // Select this folder
        item.classList.add('selected');
        this.selectedFolder = folder;
        this.selectButton.disabled = false;
    },

    /**
     * Handle select button click
     */
    handleSelect: function() {
        if (this.selectedFolder && this._resolve) {
            // Return full path including selected folder
            this._resolve(this.currentPath + this.selectedFolder);
            this.hide();
        } else if (this._resolve) {
            // Return current directory path if no specific folder is selected
            this._resolve(this.currentPath);
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
            this.fetchFolders(this.currentPath);
            
            // Show success message using a custom notification
            this.showNotification(`Folder "${folderName}" created successfully`, 'success');
        })
        .catch(error => {
            console.error('Error creating folder:', error);
            this.showNotification(`Failed to create folder: ${error.message}`, 'error');
            
            // Refresh the folder list anyway
            this.fetchFolders(this.currentPath);
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