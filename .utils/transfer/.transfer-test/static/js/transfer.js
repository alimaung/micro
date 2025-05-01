/**
 * transfer.js - Folder Transfer Tool functionality
 * Handles the multi-step transfer wizard process
 */

// Create a namespace for the Transfer component to avoid global variable conflicts
window.MicroTransfer = (function() {
    // Private variables - only accessible within this module
    let selectedType = '';
    let selectedFolders = []; // Array for multiple folder selection
    let targetPath = '';
    let currentStep = 1;

    // DOM elements
    const progressBar = document.getElementById('progress-bar');
    const steps = document.querySelectorAll('.step');
    const optionCards = document.querySelectorAll('.option-card');
    const targetPathInput = document.getElementById('targetPath');
    const pathWarning = document.getElementById('pathWarning');
    const loading = document.getElementById('loading');
    const currentStepNumber = document.getElementById('current-step-number');
    const selectedCount = document.getElementById('selectedCount');
    const clearSelectionBtn = document.getElementById('clearSelectionBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');

    // Buttons
    const nextBtn1 = document.getElementById('nextBtn1');
    const nextBtn2 = document.getElementById('nextBtn2');
    const nextBtn3 = document.getElementById('nextBtn3');
    const backBtn2 = document.getElementById('backBtn2');
    const backBtn3 = document.getElementById('backBtn3');
    const backBtn4 = document.getElementById('backBtn4');
    const transferBtn = document.getElementById('transferBtn');
    const browseBtn = document.getElementById('browseBtn');
    const closeDetailsBtn = document.getElementById('closeDetailsBtn');

    // Summary elements
    const summaryType = document.getElementById('summaryType');
    const selectedFoldersList = document.getElementById('selectedFoldersList');
    const summaryFoldersCount = document.getElementById('summaryFoldersCount');
    const summaryTarget = document.getElementById('summaryTarget');

    // Modal elements
    const transferDetailsModal = document.getElementById('transferDetailsModal');
    const transferResultsSummary = document.getElementById('transferResultsSummary');
    const transferSuccessList = document.getElementById('transferSuccessList');
    const transferFailedList = document.getElementById('transferFailedList');

    // Initialize the transfer component
    function init() {
        // Only initialize if we're on the transfer page
        if (!document.querySelector('.transfer-card')) {
            return;
        }
        
        initTransferUI();
        initModal();
    }

    // Initialize all the UI elements and event listeners
    function initTransferUI() {
        // Set up location option cards
        optionCards.forEach(card => {
            card.addEventListener('click', function() {
                optionCards.forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                selectedType = this.getAttribute('data-value');
                nextBtn1.disabled = false;
            });
        });
        
        // Set up target path with browse button
        if (browseBtn) {
            browseBtn.addEventListener('click', function() {
                // Show loading indicator
                loading.style.display = 'flex';
                
                // Send request to server to open file dialog
                fetch('/browse_folder', {
                    method: 'GET'
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    
                    if (data.error) {
                        // Use translated error message
                        const errorPrefix = window.i18n ? window.i18n.__('error_folder_browser') : 'Error opening folder browser';
                        window.MicroCore.showNotification(`${errorPrefix}: ${data.error}`, 'error');
                        console.error('Folder browser error:', data.error);
                        return;
                    }
                    
                    if (data.path) {
                        console.log('Selected path:', data.path);
                        targetPathInput.value = data.path;
                        validatePath(data.path);
                    } else if (data.message) {
                        window.MicroCore.showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    loading.style.display = 'none';
                    // Use translated error message
                    const errorMsg = window.i18n ? window.i18n.__('error_folder_browser') : 'Error opening folder browser';
                    window.MicroCore.showNotification(errorMsg, 'error');
                    console.error('Fetch error:', error);
                });
            });
        }
        
        // Set up target path validation
        if (targetPathInput) {
            targetPathInput.addEventListener('input', function() {
                validatePath(this.value);
            });
            
            // Initial validation if path exists
            if (targetPathInput.value) {
                validatePath(targetPathInput.value);
            }
        }
        
        // Set up folder selection controls
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', handleSelectAll);
        }
        
        if (clearSelectionBtn) {
            clearSelectionBtn.addEventListener('click', clearSelection);
        }
        
        // Set up navigation buttons
        if (nextBtn1) nextBtn1.addEventListener('click', () => {
            fetchFolders(selectedType);
            goToStep(2);
        });
        if (nextBtn2) nextBtn2.addEventListener('click', () => goToStep(3));
        if (nextBtn3) nextBtn3.addEventListener('click', () => {
            // Update summary before showing confirmation screen
            if (summaryType) summaryType.textContent = selectedType === 'OU' ? 'Oberursel (OU)' : 'Dahlewitz (DW)';
            updateSelectedFoldersList();
            if (summaryTarget) summaryTarget.textContent = targetPath;
            goToStep(4);
        });
        
        if (backBtn2) backBtn2.addEventListener('click', () => goToStep(1));
        if (backBtn3) backBtn3.addEventListener('click', () => goToStep(2));
        if (backBtn4) backBtn4.addEventListener('click', () => goToStep(3));
        
        // Set up transfer button
        if (transferBtn) transferBtn.addEventListener('click', performTransfer);
    }
    
    // Initialize modal functionality
    function initModal() {
        if (!transferDetailsModal) return;
        
        // Get the <span> element that closes the modal
        const closeButton = transferDetailsModal.querySelector(".close");
        
        // When the user clicks on <span> (x), close the modal
        if (closeButton) {
            closeButton.onclick = function() {
                transferDetailsModal.style.display = "none";
            }
        }
        
        // When the user clicks on close button
        if (closeDetailsBtn) {
            closeDetailsBtn.onclick = function() {
                transferDetailsModal.style.display = "none";
            }
        }
        
        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function(event) {
            if (event.target == transferDetailsModal) {
                transferDetailsModal.style.display = "none";
            }
        }
    }

    // Fetch folders for the selected location type
    function fetchFolders(folderType) {
        if (loading) loading.style.display = 'flex';
        
        fetch(`/get_folders/${folderType}`)
            .then(response => response.json())
            .then(folders => {
                const folderGrid = document.getElementById('folderGrid');
                if (!folderGrid) return;
                
                folderGrid.innerHTML = ''; // Clear previous content
                
                // Filter out any hidden folders (those starting with .)
                // This is an additional safeguard in case the backend didn't filter them out
                const visibleFolders = folders.filter(folder => !folder.startsWith('.'));
                
                if (visibleFolders.length === 0) {
                    // Use translated text for "No folders available"
                    const noFoldersText = window.i18n ? window.i18n.__('no_folders') : 'No folders available';
                    folderGrid.innerHTML = `<p>${noFoldersText}</p>`;
                } else {
                    visibleFolders.forEach(folder => {
                        const card = document.createElement('div');
                        card.className = 'folder-card';
                        card.setAttribute('data-folder', folder);
                        
                        // Create checkbox for multiple selection
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.className = 'folder-checkbox';
                        checkbox.value = folder;
                        
                        card.innerHTML = `
                            <div class="folder-icon"><i class="fas fa-folder"></i></div>
                            <div>${folder}</div>
                        `;
                        
                        // Add checkbox to the card
                        card.appendChild(checkbox);
                        
                        // Handle card click (select the checkbox)
                        card.addEventListener('click', function(e) {
                            // Don't trigger if clicking on the checkbox directly
                            if (e.target !== checkbox) {
                                checkbox.checked = !checkbox.checked;
                                updateFolderSelection(checkbox);
                            }
                        });
                        
                        // Handle checkbox changes
                        checkbox.addEventListener('change', function(e) {
                            e.stopPropagation(); // Prevent card click from being triggered
                            updateFolderSelection(this);
                        });
                        
                        folderGrid.appendChild(card);
                    });
                }
                
                if (loading) loading.style.display = 'none';
            })
            .catch(error => {
                // Use translated error message
                const errorMsg = window.i18n ? window.i18n.__('error_loading_folders') : 'Error loading folders';
                window.MicroCore.showNotification(errorMsg, 'error');
                if (loading) loading.style.display = 'none';
            });
    }
    
    // Update folder selection when checkbox is clicked
    function updateFolderSelection(checkbox) {
        const folder = checkbox.value;
        const folderCard = checkbox.closest('.folder-card');
        
        if (checkbox.checked) {
            folderCard.classList.add('selected');
            // Add folder to selected folders if not already there
            if (!selectedFolders.includes(folder)) {
                selectedFolders.push(folder);
            }
        } else {
            folderCard.classList.remove('selected');
            // Remove folder from selected folders
            const index = selectedFolders.indexOf(folder);
            if (index > -1) {
                selectedFolders.splice(index, 1);
            }
        }
        
        // Update selection count
        if (selectedCount) {
            selectedCount.textContent = selectedFolders.length;
        }
        
        // Enable/disable buttons based on selection
        if (nextBtn2) {
            nextBtn2.disabled = selectedFolders.length === 0;
        }
        
        if (clearSelectionBtn) {
            clearSelectionBtn.disabled = selectedFolders.length === 0;
        }
    }
    
    // Select all folders
    function handleSelectAll() {
        const checkboxes = document.querySelectorAll('.folder-checkbox');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = !allChecked;
            updateFolderSelection(checkbox);
        });
        
        // Update button text
        if (selectAllBtn) {
            const selectAllText = window.i18n ? window.i18n.__('select_all') : 'Select All';
            const deselectAllText = window.i18n ? window.i18n.__('deselect_all') : 'Deselect All';
            
            selectAllBtn.innerHTML = !allChecked ? 
                `<i class="fas fa-times-square"></i> <span>${deselectAllText}</span>` :
                `<i class="fas fa-check-square"></i> <span>${selectAllText}</span>`;
        }
    }
    
    // Clear all folder selections
    function clearSelection() {
        const checkboxes = document.querySelectorAll('.folder-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
            checkbox.closest('.folder-card').classList.remove('selected');
        });
        
        selectedFolders = [];
        
        // Update UI
        if (selectedCount) {
            selectedCount.textContent = 0;
        }
        
        if (nextBtn2) {
            nextBtn2.disabled = true;
        }
        
        if (clearSelectionBtn) {
            clearSelectionBtn.disabled = true;
        }
        
        // Reset "Select All" button text
        if (selectAllBtn) {
            const selectAllText = window.i18n ? window.i18n.__('select_all') : 'Select All';
            selectAllBtn.innerHTML = `<i class="fas fa-check-square"></i> <span>${selectAllText}</span>`;
        }
    }
    
    // Update the selected folders list in the summary
    function updateSelectedFoldersList() {
        if (!selectedFoldersList || !summaryFoldersCount) return;
        
        selectedFoldersList.innerHTML = '';
        
        selectedFolders.forEach(folder => {
            const li = document.createElement('li');
            li.textContent = folder;
            selectedFoldersList.appendChild(li);
        });
        
        summaryFoldersCount.textContent = selectedFolders.length;
    }

    // Validate the target path
    function validatePath(path) {
        fetch('/check_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `path=${encodeURIComponent(path)}`
        })
        .then(response => response.json())
        .then(data => {
            console.log('Path validation response:', data);
            if (data.valid) {
                targetPathInput.classList.remove('invalid-path');
                pathWarning.style.display = 'none';
                nextBtn3.disabled = false;
                targetPath = path;
            } else {
                targetPathInput.classList.add('invalid-path');
                pathWarning.style.display = 'block';
                nextBtn3.disabled = true;
            }
        });
    }

    // Update UI for the current step
    function goToStep(step) {
        currentStep = step;
        
        if (!steps || !progressBar) {
            return;
        }
        
        steps.forEach((s, index) => {
            if (index + 1 === step) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        });
        
        // Update progress bar
        progressBar.style.width = `${step * 25}%`;
        
        // Update step number in badge
        if (currentStepNumber) currentStepNumber.textContent = step;
        
        // Update status badge class based on step
        const stepStatusBadge = document.getElementById('step-status-badge');
        if (stepStatusBadge) {
            stepStatusBadge.className = 'status-badge';
            
            if (step === 1) {
                stepStatusBadge.classList.add('initial');
                // Update status badge text
                updateStatusBadgeContent(stepStatusBadge, 'step_indicator', 'step_of');
            } else if (step < 4) {
                stepStatusBadge.classList.add('in-progress');
                // Update status badge text
                updateStatusBadgeContent(stepStatusBadge, 'step_indicator', 'step_of');
            } else {
                stepStatusBadge.classList.add('pending');
                // Update status badge text
                updateStatusBadgeContent(stepStatusBadge, 'step_indicator', 'step_of');
            }
        }
    }

    // Update status badge content with i18n support
    function updateStatusBadgeContent(badge, stepKey, ofKey) {
        const stepText = window.i18n ? window.i18n.__(stepKey) : 'Step';
        const ofText = window.i18n ? window.i18n.__(ofKey) : 'of';
        const currentStepSpan = `<span id="current-step-number">${currentStep}</span>`;
        
        badge.innerHTML = `
            <i class="fas fa-${currentStep < 4 ? 'clock' : 'sync fa-spin'}"></i>
            <span data-i18n="${stepKey}">${stepText}</span>&nbsp;${currentStepSpan}&nbsp;<span data-i18n="${ofKey}">${ofText}</span>&nbsp;4
        `;
    }

    // Perform the transfer operation
    function performTransfer() {
        if (loading) loading.style.display = 'flex';
        
        // Update status badges to "in progress"
        const mainStatusBadge = document.getElementById('main-status-badge');
        const stepStatusBadge = document.getElementById('step-status-badge');
        
        // Use i18n translation for status
        const transferringText = window.i18n ? window.i18n.__('status_transferring') : 'Transferring';
        const processingText = window.i18n ? window.i18n.__('status_processing') : 'Processing';
        
        if (mainStatusBadge) {
            mainStatusBadge.innerHTML = `<i class="fas fa-sync fa-spin"></i> <span data-i18n="status_transferring">${transferringText}</span>`;
            mainStatusBadge.className = 'status-badge in-progress';
        }
        
        if (stepStatusBadge) {
            stepStatusBadge.innerHTML = `<i class="fas fa-sync fa-spin"></i> <span data-i18n="status_processing">${processingText}</span>`;
            stepStatusBadge.className = 'status-badge in-progress';
        }
        
        const formData = new FormData();
        formData.append('folder_type', selectedType);
        
        // Add all selected folders
        selectedFolders.forEach(folder => {
            formData.append('selected_folders[]', folder);
        });
        
        formData.append('target_path', targetPath);
        
        fetch('/transfer', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            if (loading) loading.style.display = 'none';
            
            if (result.success) {
                // Update status badges to "completed"
                const completedText = window.i18n ? window.i18n.__('status_completed') : 'Completed';
                
                if (mainStatusBadge) {
                    mainStatusBadge.innerHTML = `<i class="fas fa-check-circle"></i> <span data-i18n="status_completed">${completedText}</span>`;
                    mainStatusBadge.className = 'status-badge completed';
                }
                
                if (stepStatusBadge) {
                    stepStatusBadge.innerHTML = `<i class="fas fa-check-circle"></i> <span data-i18n="status_completed">${completedText}</span>`;
                    stepStatusBadge.className = 'status-badge completed';
                }
                
                // Show success notification
                window.MicroCore.showNotification(result.message, 'success');
                
                // Show detailed results if multiple folders
                if (result.details && result.details.length > 1) {
                    showTransferDetails(result);
                } else {
                    // For single folder transfers, maintain backward compatibility
                    // Create success notification with view files button
                    if (result.destination_path) {
                        // Automatically open folder after a delay
                        setTimeout(() => {
                            window.MicroCore.openFolder(result.destination_path);
                        }, 1000);
                    }
                }
                
                // Reset the form after successful transfer
                setTimeout(() => {
                    resetForm();
                }, 5000);
            } else {
                // Update status badges to "error"
                const errorText = window.i18n ? window.i18n.__('status_error') : 'Error';
                const failedText = window.i18n ? window.i18n.__('status_failed') : 'Failed';
                
                if (mainStatusBadge) {
                    mainStatusBadge.innerHTML = `<i class="fas fa-exclamation-circle"></i> <span data-i18n="status_error">${errorText}</span>`;
                    mainStatusBadge.className = 'status-badge error';
                }
                
                if (stepStatusBadge) {
                    stepStatusBadge.innerHTML = `<i class="fas fa-exclamation-circle"></i> <span data-i18n="status_failed">${failedText}</span>`;
                    stepStatusBadge.className = 'status-badge error';
                }
                
                window.MicroCore.showNotification(result.message, 'error');
                
                // Show detailed results if they exist
                if (result.details) {
                    showTransferDetails(result);
                }
            }
        })
        .catch(error => {
            if (loading) loading.style.display = 'none';
            
            // Update status badges to "error"
            const errorText = window.i18n ? window.i18n.__('status_error') : 'Error';
            const failedText = window.i18n ? window.i18n.__('status_failed') : 'Failed';
            
            if (mainStatusBadge) {
                mainStatusBadge.innerHTML = `<i class="fas fa-exclamation-circle"></i> <span data-i18n="status_error">${errorText}</span>`;
                mainStatusBadge.className = 'status-badge error';
            }
            
            if (stepStatusBadge) {
                stepStatusBadge.innerHTML = `<i class="fas fa-exclamation-circle"></i> <span data-i18n="status_failed">${failedText}</span>`;
                stepStatusBadge.className = 'status-badge error';
            }
            
            const errorMsg = window.i18n ? window.i18n.__('error_during_transfer') : 'Error during transfer operation';
            window.MicroCore.showNotification(errorMsg, 'error');
        });
    }
    
    // Show transfer details in a modal
    function showTransferDetails(result) {
        if (!transferDetailsModal || !transferResultsSummary || !transferSuccessList || !transferFailedList) {
            return;
        }
        
        // Clear previous content
        transferResultsSummary.innerHTML = '';
        transferSuccessList.innerHTML = '';
        transferFailedList.innerHTML = '';
        
        // Add summary information
        const summaryHtml = `<h3>${result.message}</h3>`;
        transferResultsSummary.innerHTML = summaryHtml;
        
        // Add successful transfers
        if (result.successful_folders && result.successful_folders.length > 0) {
            const successTitle = document.createElement('h4');
            successTitle.innerHTML = '<i class="fas fa-check-circle"></i> Successful Transfers';
            transferSuccessList.appendChild(successTitle);
            
            result.successful_folders.forEach(folder => {
                const div = document.createElement('div');
                div.className = 'success-item';
                div.innerHTML = `<i class="fas fa-folder"></i> ${folder}`;
                transferSuccessList.appendChild(div);
            });
        }
        
        // Add failed transfers
        if (result.failed_folders && result.failed_folders.length > 0) {
            const failedTitle = document.createElement('h4');
            failedTitle.innerHTML = '<i class="fas fa-times-circle"></i> Failed Transfers';
            transferFailedList.appendChild(failedTitle);
            
            // Find error messages for failed folders
            const errorDetails = result.details.filter(detail => !detail.success);
            
            errorDetails.forEach(detail => {
                const div = document.createElement('div');
                div.className = 'failed-item';
                div.innerHTML = `<i class="fas fa-folder"></i> ${detail.folder}: ${detail.message}`;
                transferFailedList.appendChild(div);
            });
        }
        
        // Add a button to open the target directory if available
        if (result.destination_path && result.successful_folders.length > 0) {
            const openButton = document.createElement('button');
            openButton.className = 'primary-btn';
            openButton.innerHTML = '<i class="fas fa-folder-open"></i> Open Target Directory';
            openButton.addEventListener('click', () => {
                window.MicroCore.openFolder(result.destination_path);
            });
            
            transferResultsSummary.appendChild(document.createElement('br'));
            transferResultsSummary.appendChild(openButton);
        }
        
        // Show the modal
        transferDetailsModal.style.display = 'block';
    }

    // Reset the form after transfer
    function resetForm() {
        // Reset selections
        selectedType = '';
        selectedFolders = [];
        
        // Reset UI
        if (optionCards) {
            optionCards.forEach(c => c.classList.remove('selected'));
        }
        
        if (nextBtn1) nextBtn1.disabled = true;
        if (nextBtn2) nextBtn2.disabled = true;
        
        if (selectedCount) {
            selectedCount.textContent = '0';
        }
        
        if (clearSelectionBtn) {
            clearSelectionBtn.disabled = true;
        }
        
        // Reset status badges
        const mainStatusBadge = document.getElementById('main-status-badge');
        const stepStatusBadge = document.getElementById('step-status-badge');
        
        // Use translated text
        const pendingText = window.i18n ? window.i18n.__('status_pending') : 'Pending';
        const stepText = window.i18n ? window.i18n.__('step_indicator') : 'Step';
        const ofText = window.i18n ? window.i18n.__('step_of') : 'of';
        
        if (mainStatusBadge) {
            mainStatusBadge.innerHTML = `<i class="fas fa-clock"></i> <span data-i18n="status_pending">${pendingText}</span>`;
            mainStatusBadge.className = 'status-badge initial';
        }
        
        if (stepStatusBadge) {
            stepStatusBadge.innerHTML = `<i class="fas fa-clock"></i> <span data-i18n="step_indicator">${stepText}</span> <span id="current-step-number">1</span> <span data-i18n="step_of">${ofText}</span> 4`;
            stepStatusBadge.className = 'status-badge initial';
            
            // Make sure the current step number element is accessible again after resetting the HTML
            const currentStepElement = document.getElementById('current-step-number');
            if (currentStepElement) currentStepElement.textContent = '1';
        }
        
        // Go back to step 1
        goToStep(1);
    }

    // Register the initialization function to run when the DOM is loaded
    document.addEventListener('DOMContentLoaded', init);

    // Return public methods and properties
    return {
        init: init
    };
})(); 