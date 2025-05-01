/**
 * rename.js - File Rename Tool functionality
 * Handles batch file renaming with pattern matching
 */

// Create a namespace for the Rename component to avoid global variable conflicts
window.MicroRename = (function() {
    // Private variables - only accessible within this module
    let files = [];
    
    // DOM Elements - scoped to this module
    let fileList;
    let directoryPathInput;
    let browseDirectoryBtn;
    let patternForm;
    let renameBtn;
    let resetBtn;
    let startNumberInput;
    let applyNumberBtn;
    let targetPathInput;
    let browseTargetBtn;
    let loadingContainer;
    let tableSelectionHeader;
    let selectAllBtn;
    let deselectAllBtn;
    let selectionDisplayCount;
    let totalFilesCount;
    let openFilesBtn;

    // Global variables
    let selectedFiles = {};
    let currentEditingIndex = -1;
    let currentNotification = null;

    // Initialize the rename component
    function init() {
        // Only initialize if we're on the rename page
        if (!document.querySelector('.file-list')) {
            return;
        }
        
        initRenameUI();
    }

    // Initialize UI and event listeners
    function initRenameUI() {
        // Initialize DOM elements
        fileList = document.getElementById('fileList');
        directoryPathInput = document.getElementById('directoryPath');
        browseDirectoryBtn = document.getElementById('browseDirBtn');
        patternForm = document.getElementById('patternForm');
        renameBtn = document.getElementById('renameBtn');
        resetBtn = document.getElementById('resetBtn');
        startNumberInput = document.getElementById('startNumber');
        applyNumberBtn = document.getElementById('applyNumberBtn');
        targetPathInput = document.getElementById('targetPath');
        browseTargetBtn = document.getElementById('browseTargetBtn');
        loadingContainer = document.getElementById('loadingContainer');
        tableSelectionHeader = document.getElementById('tableSelectionHeader');
        selectAllBtn = document.getElementById('selectAllBtn');
        deselectAllBtn = document.getElementById('deselectAllBtn');
        selectionDisplayCount = document.getElementById('selectionDisplayCount');
        totalFilesCount = document.getElementById('totalFilesCount');
        openFilesBtn = document.getElementById('openFilesBtn');

        // Initialize with empty start number (no default value)
        startNumberInput.value = "";

        // Set up event listeners
        browseDirectoryBtn.addEventListener('click', browseDirectory);
        browseTargetBtn.addEventListener('click', browseTarget);
        applyNumberBtn.addEventListener('click', applyNumbering);
        renameBtn.addEventListener('click', renameFiles);
        resetBtn.addEventListener('click', resetState);
        openFilesBtn.addEventListener('click', openTargetFolder);
        
        // Selection event listeners
        selectAllBtn.addEventListener('click', selectAllFiles);
        deselectAllBtn.addEventListener('click', deselectAllFiles);
        
        // Add live update for start number input
        startNumberInput.addEventListener('input', applyNumbering);

        // Always show pattern form
        patternForm.style.display = 'block';
        
        // Always show reset button instead of hiding it
        resetBtn.style.display = 'block';
        
        // Hide open files button initially
        openFilesBtn.style.display = 'none';
        
        // Initialize with empty table
        displayEmptyTable();
    }

    // Reset the application state
    function resetState() {
        // Clear files array
        files = [];
        
        // Clear selection state
        selectedFiles = {};
        
        // Clear file display
        displayEmptyTable();
        
        // Clear input fields
        directoryPathInput.value = '';
        targetPathInput.value = '';
        startNumberInput.value = '';
        
        // Hide open files button
        openFilesBtn.style.display = 'none';
        
        // Hide selection header
        tableSelectionHeader.style.display = 'none';
        
        // Disable rename button
        renameBtn.disabled = true;
        
        // Show notification
        showNotification('All fields have been reset.', 'info');
    }

    // Custom notification system
    function showNotification(message, type) {
        // Remove any existing notification
        if (currentNotification) {
            document.body.removeChild(currentNotification);
            currentNotification = null;
        }
        
        // Create new notification
        const notification = document.createElement('div');
        notification.className = `micro-notification micro-notification-${type || 'info'}`;
        
        // Determine icon based on type
        let iconClass = 'fa-info-circle';
        if (type === 'success') {
            iconClass = 'fa-check-circle';
        } else if (type === 'error') {
            iconClass = 'fa-exclamation-circle';
        } else if (type === 'warning') {
            iconClass = 'fa-exclamation-triangle';
        }
        
        // Create notification content
        notification.innerHTML = `
            <div class="micro-notification-icon">
                <i class="fas ${iconClass}"></i>
            </div>
            <div class="micro-notification-content">
                <p>${message}</p>
            </div>
            <button class="micro-notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add event listener to close button
        notification.querySelector('.micro-notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                if (currentNotification === notification) {
                    currentNotification = null;
                }
            }, 300);
        });
        
        // Add notification to the DOM
        document.body.appendChild(notification);
        currentNotification = notification;
        
        // Show notification with slight delay to allow CSS transition
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            if (notification.classList.contains('show')) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                    if (currentNotification === notification) {
                        currentNotification = null;
                    }
                }, 300);
            }
        }, 5000);
    }

    // Select/Deselect All Functions
    function selectAllFiles(e) {
        // Prevent default behavior if it's triggered by an event
        if (e) e.preventDefault();
        
        files.forEach((file, index) => {
            selectedFiles[index] = true;
            const checkbox = document.getElementById(`file-check-${index}`);
            if (checkbox) checkbox.checked = true;
        });
        updateSelectedCounter();
        
        // Ensure button text stays as "Select All"
        if (selectAllBtn) {
            selectAllBtn.innerHTML = 'Select All';
        }
    }

    function deselectAllFiles(e) {
        // Prevent default behavior if it's triggered by an event
        if (e) e.preventDefault();
        
        selectedFiles = {};
        files.forEach((file, index) => {
            const checkbox = document.getElementById(`file-check-${index}`);
            if (checkbox) checkbox.checked = false;
        });
        updateSelectedCounter();
        
        // Ensure button text stays as "Deselect All"
        if (deselectAllBtn) {
            deselectAllBtn.innerHTML = 'Deselect All';
        }
    }

    function updateSelectedCounter() {
        const selectedCount = Object.keys(selectedFiles).length;
        selectionDisplayCount.textContent = selectedCount;
        
        // Enable/disable the rename button based on selection
        renameBtn.disabled = selectedCount === 0;
    }

    // Inline Editing Functions
    function startEdit(index) {
        // If there's already an edit in progress, save it first
        if (currentEditingIndex !== -1 && currentEditingIndex !== index) {
            finishEdit(currentEditingIndex, true);
        }
        
        currentEditingIndex = index;
        const fileItem = document.getElementById(`file-item-${index}`);
        const nameCell = fileItem.querySelector('.file-name');
        const currentName = files[index].newName || files[index].name;
        
        // Get filename without extension
        const lastDotIndex = currentName.lastIndexOf('.');
        const fileName = lastDotIndex !== -1 ? currentName.substring(0, lastDotIndex) : currentName;
        const extension = lastDotIndex !== -1 ? currentName.substring(lastDotIndex) : '';
        
        // Create and set up the inline editor
        nameCell.innerHTML = `
            <div class="inline-edit-container">
                <input type="text" class="inline-edit-input" id="edit-input-${index}" value="${fileName}">
                <span class="extension-text">${extension}</span>
                <div class="inline-edit-actions">
                    <button class="inline-save-btn" id="save-edit-${index}"><i class="fas fa-check"></i></button>
                    <button class="inline-cancel-btn" id="cancel-edit-${index}"><i class="fas fa-times"></i></button>
                </div>
            </div>
        `;
        
        // Focus the input field
        const inputField = document.getElementById(`edit-input-${index}`);
        inputField.focus();
        
        // Set up event listeners
        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                finishEdit(index, true);
            }
        });
        
        // Add input event for real-time updates
        inputField.addEventListener('input', function(e) {
            handleFilenameEdit(index, e.target.value);
        });
        
        inputField.addEventListener('blur', function(e) {
            // Only handle blur if it's not caused by clicking on the action buttons
            const relatedTarget = e.relatedTarget;
            if (!relatedTarget || 
                (relatedTarget.id !== `save-edit-${index}` && 
                 relatedTarget.id !== `cancel-edit-${index}` &&
                 !relatedTarget.closest(`#save-edit-${index}`) && 
                 !relatedTarget.closest(`#cancel-edit-${index}`))) {
                finishEdit(index, true);
            }
        });
        
        document.getElementById(`save-edit-${index}`).addEventListener('click', function() {
            finishEdit(index, true);
        });
        
        document.getElementById(`cancel-edit-${index}`).addEventListener('click', function() {
            finishEdit(index, false);
        });
    }

    function finishEdit(index, save) {
        if (index !== currentEditingIndex) return;
        
        const fileItem = document.getElementById(`file-item-${index}`);
        const nameCell = fileItem.querySelector('.file-name');
        const inputField = document.getElementById(`edit-input-${index}`);
        
        if (save && inputField) {
            // Get the new filename
            const newFileName = inputField.value;
            
            // Get the extension
            const currentName = files[index].newName || files[index].name;
            const lastDotIndex = currentName.lastIndexOf('.');
            const extension = lastDotIndex !== -1 ? currentName.substring(lastDotIndex) : '';
            
            // If new filename is empty or same as original, set newName to null to use original name
            if (!newFileName || (newFileName + extension) === files[index].name) {
                files[index].newName = null;
            } else {
                // Otherwise, set the new name
                files[index].newName = newFileName + extension;
            }
        }
        
        // Always update the display regardless of save or cancel
        updateFileDisplay();
        currentEditingIndex = -1;
    }

    // Handle real-time editing of filenames
    function handleFilenameEdit(index, value) {
        if (index < 0 || index >= files.length) return;
        
        // Get the extension
        const currentName = files[index].newName || files[index].name;
        const lastDotIndex = currentName.lastIndexOf('.');
        const extension = lastDotIndex !== -1 ? currentName.substring(lastDotIndex) : '';
        
        // If value is empty, set newName to null to use original name
        files[index].newName = value ? (value + extension) : null;
        
        // We don't update the display here to avoid disrupting the editing
        // But we could update other elements as needed
    }

    // Function to handle file selection toggle
    function toggleFileSelection(index) {
        const checkbox = document.getElementById(`file-check-${index}`);
        
        if (checkbox.checked) {
            selectedFiles[index] = true;
        } else {
            delete selectedFiles[index];
        }
        
        updateSelectedCounter();
    }

    // Browse and file loading functions
    function browseDirectory() {
        fetch('/browse_folder', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.path) {
                directoryPathInput.value = data.path;
                loadFiles(data.path);
            } else if (data.error) {
                showNotification(`Error browsing directory: ${data.error}`, 'error');
            } else if (data.message) {
                showNotification(data.message, 'info');
            }
        })
        .catch(error => {
            console.error('Error browsing directory:', error);
            showNotification(`Error browsing directory: ${error.message}`, 'error');
        });
    }

    function browseTarget() {
        fetch('/browse_folder', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.path) {
                targetPathInput.value = data.path;
                showNotification('Target directory selected', 'success');
            } else if (data.error) {
                showNotification(`Error browsing directory: ${data.error}`, 'error');
            } else if (data.message) {
                showNotification(data.message, 'info');
            }
        })
        .catch(error => {
            console.error('Error browsing target directory:', error);
            showNotification(`Error browsing directory: ${error.message}`, 'error');
        });
    }

    function loadFiles(path) {
        // Show loading indicator
        loadingContainer.style.display = 'flex';
        fileList.style.display = 'none';
        
        // Reset selection state
        selectedFiles = {};
        
        // Create FormData object for the request
        const formData = new FormData();
        formData.append('directory_path', path);
        
        fetch('/get_files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingContainer.style.display = 'none';
            fileList.style.display = 'block';
            
            if (data.files && data.files.length > 0) {
                files = data.files.map(file => ({
                    name: file.name,
                    newName: null  // No new name initially - will display original name
                }));
                
                // Select all files by default
                files.forEach((file, index) => {
                    selectedFiles[index] = true;
                });
                
                // Update file display
                updateFileDisplay();
                
                // Enable rename button
                renameBtn.disabled = false;
                
                // Show selection header and update counts
                tableSelectionHeader.style.display = 'flex';
                totalFilesCount.textContent = files.length;
                updateSelectedCounter();
                
                // Don't apply initial numbering scheme
                // applyNumbering();
                
                // Show notification
                showNotification(`Successfully loaded ${files.length} files`, 'success');
            } else {
                // Show no files message
                fileList.innerHTML = `
                    <div class="no-files">
                        <i class="fas fa-folder-open" style="font-size: 2rem; color: var(--secondary-text-color); margin-bottom: 10px;"></i>
                        <p>No files found in the selected directory</p>
                        <p class="small-text">Choose a different directory or make sure it contains files</p>
                    </div>
                `;
                
                // Hide selection header
                tableSelectionHeader.style.display = 'none';
                
                // Disable rename button
                renameBtn.disabled = true;
                
                // Show notification
                showNotification('No files found in the selected directory', 'warning');
            }
        })
        .catch(error => {
            // Hide loading indicator and show error
            loadingContainer.style.display = 'none';
            fileList.style.display = 'block';
            fileList.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading files: ${error.message}</p>
                </div>
            `;
            
            // Hide selection header
            tableSelectionHeader.style.display = 'none';
            
            console.error('Error loading files:', error);
            
            // Disable rename button
            renameBtn.disabled = true;
            
            // Show notification
            showNotification(`Error loading files: ${error.message}`, 'error');
        });
    }

    function updateFileDisplay() {
        if (!files.length) {
            fileList.innerHTML = `
                <div class="no-files">
                    <i class="fas fa-folder-open" style="font-size: 2rem; color: var(--secondary-text-color); margin-bottom: 10px;"></i>
                    <p>No files found in the selected directory</p>
                    <p class="small-text">Choose a different directory or make sure it contains files</p>
                </div>
            `;
            return;
        }
        
        let fileListHTML = `
            <table class="file-table">
                <thead>
                    <tr>
                        <th class="checkbox-col"></th>
                        <th>Original Name</th>
                        <th>New Name</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        files.forEach((file, index) => {
            const isSelected = selectedFiles[index] || false;
            // Display original name if no new name is assigned
            const displayName = file.newName || file.name;
            
            fileListHTML += `
                <tr id="file-item-${index}" class="${isSelected ? 'selected' : ''}">
                    <td class="checkbox-col">
                        <label class="custom-checkbox">
                            <input type="checkbox" id="file-check-${index}" ${isSelected ? 'checked' : ''} onclick="window.MicroRename.toggleFileSelection(${index})">
                            <span class="checkmark"></span>
                        </label>
                    </td>
                    <td class="original-name" title="${file.name}">${file.name}</td>
                    <td class="file-name" title="${displayName}">${displayName}</td>
                    <td class="actions">
                        <button class="edit-btn" onclick="window.MicroRename.startEdit(${index})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        fileListHTML += `
                </tbody>
            </table>
        `;
        
        fileList.innerHTML = fileListHTML;
        
        // Update the selected files counter
        updateSelectedCounter();
    }

    function applyNumbering() {
        if (!files.length) return;
        
        const startNumberText = startNumberInput.value.trim();
        // Only apply numbering if startNumber has a value
        if (!startNumberText) {
            showNotification('Please enter a starting number', 'warning');
            return;
        }
        
        const startNumber = parseInt(startNumberText) || 1;
        
        files.forEach((file, index) => {
            const fileExtension = file.name.substring(file.name.lastIndexOf('.')) || '';
            const newNumber = startNumber + index;
            file.newName = `${newNumber}${fileExtension}`;
        });
        
        updateFileDisplay();
    }

    function renameFiles() {
        if (!files.length) return;
        
        // Get only the selected files
        const selectedFilesList = Object.keys(selectedFiles).map(index => ({
            original_name: files[index].name,
            new_name: files[index].newName
        }));
        
        if (selectedFilesList.length === 0) {
            showNotification('Please select at least one file to rename', 'warning');
            return;
        }
        
        // Show loading indicator
        loadingContainer.style.display = 'flex';
        
        const requestData = {
            directory_path: directoryPathInput.value,
            target_path: targetPathInput.value || '',
            files: selectedFilesList
        };
        
        fetch('/rename_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingContainer.style.display = 'none';
            
            if (data.success) {
                showNotification(`Successfully renamed ${data.renamed_count} files!`, 'success');
                
                // Show open files button
                openFilesBtn.style.display = 'block';
                
                // Store the target path for the open button
                const targetDirectory = targetPathInput.value || directoryPathInput.value;
                openFilesBtn.setAttribute('data-path', targetDirectory);
                
                // Reload the files to see the new names
                loadFiles(directoryPathInput.value);
            } else if (data.error) {
                showNotification(`Error: ${data.error}`, 'error');
            } else {
                showNotification('Unknown error occurred during file renaming', 'error');
            }
        })
        .catch(error => {
            // Hide loading indicator
            loadingContainer.style.display = 'none';
            
            showNotification(`Error: ${error.message}`, 'error');
            console.error('Error renaming files:', error);
        });
    }

    // Display an empty table with instructions
    function displayEmptyTable() {
        if (!fileList) return;
        
        // Clear existing content and show empty message
        fileList.innerHTML = `
            <div class="no-files">
                <i class="fas fa-folder-open" style="font-size: 2rem; color: var(--secondary-text-color); margin-bottom: 10px;"></i>
                <p>Please select a directory to load files</p>
                <p class="small-text">Use the "Browse & Load" button above to select files for renaming</p>
            </div>
        `;
        
        // Hide selection header
        if (tableSelectionHeader) {
            tableSelectionHeader.style.display = 'none';
        }
    }

    // Function to open the target folder in file explorer
    function openTargetFolder() {
        const folderPath = openFilesBtn.getAttribute('data-path');
        if (!folderPath) {
            showNotification('No folder path available', 'error');
            return;
        }
        
        showNotification('Opening folder...', 'info');
        
        const formData = new FormData();
        formData.append('path', folderPath);
        
        fetch('/open_folder', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Opening folder in file explorer', 'success');
            } else {
                showNotification(`Failed to open folder: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error opening folder:', error);
            showNotification(`Error opening folder: ${error.message}`, 'error');
        });
    }

    // Register the initialization function to run when the DOM is loaded
    document.addEventListener('DOMContentLoaded', init);

    // Return public methods and properties
    return {
        init: init,
        toggleFileSelection: toggleFileSelection,
        startEdit: startEdit
    };
})(); 