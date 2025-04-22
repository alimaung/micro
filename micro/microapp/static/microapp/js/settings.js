/**
 * Settings Dashboard Functionality
 * Microfilm Processing System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab navigation
    initializeTabs();
    
    // Initialize form controls
    initializeFormControls();
    
    // Initialize table functionality
    initializeTableFunctionality();
    
    // Add Machine Management initialization to the tab change logic
    if (typeof tabLinks !== 'undefined' && tabLinks.length) {
        tabLinks.forEach(tabLink => {
            tabLink.addEventListener('click', function() {
                // ... existing tab click handler code ...
                
                // Initialize Machine Management when its tab is active
                if (this.getAttribute('data-tab') === 'machine-management') {
                    initializeMachineManagement();
                    updateMachineMetrics(); // Initial update
                    setupMachineMetricsInterval();
                } else if (metricsInterval) {
                    // Clear interval when leaving machine tab
                    clearInterval(metricsInterval);
                }
            });
        });
    }
    
    // Initialize Machine Management tab if it's the active tab on page load
    const activeTab = document.querySelector('.tabs-nav .active');
    if (activeTab && activeTab.getAttribute('data-tab') === 'machine-management') {
        initializeMachineManagement();
        updateMachineMetrics();
        setupMachineMetricsInterval();
    }
});

/**
 * Initializes tab navigation
 */
function initializeTabs() {
    const navTabs = document.querySelectorAll('.nav-tabs li');
    const settingsTabs = document.querySelectorAll('.settings-tab');
    
    navTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            navTabs.forEach(t => t.classList.remove('active'));
            settingsTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show corresponding content tab
            const tabId = this.getAttribute('data-tab');
            const contentTab = document.getElementById(`${tabId}-tab`);
            if (contentTab) {
                contentTab.classList.add('active');
            }
        });
    });
    
    // Handle subtabs
    const subtabs = document.querySelectorAll('.subtab');
    subtabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const parentSubtabs = this.parentElement.querySelectorAll('.subtab');
            parentSubtabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // In a real app, would update content based on selected subtab
            console.log(`Subtab selected: ${this.textContent.trim()}`);
        });
    });
}

/**
 * Initializes form controls
 */
function initializeFormControls() {
    // Range slider functionality
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        const valueDisplay = input.nextElementSibling;
        if (valueDisplay && valueDisplay.classList.contains('range-value')) {
            input.addEventListener('input', function() {
                // Update display value
                let displayText = this.value;
                
                // Custom formatting based on input id
                if (this.id === 'backup-frequency') {
                    displayText = `${this.value} day${this.value !== '1' ? 's' : ''}`;
                }
                
                valueDisplay.textContent = displayText;
            });
        }
    });
    
    // Toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-buttons button');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from siblings
            const siblings = this.parentElement.querySelectorAll('button');
            siblings.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
        });
    });
    
    // Form submission
    const saveButtons = document.querySelectorAll('.btn.primary');
    saveButtons.forEach(button => {
        button.addEventListener('click', function() {
            // In a real app, would save form data
            showNotification('Settings saved successfully!');
        });
    });
    
    // Reset buttons
    const resetButtons = document.querySelectorAll('.btn.secondary');
    resetButtons.forEach(button => {
        if (button.textContent.includes('Reset')) {
            button.addEventListener('click', function() {
                if (confirm('Are you sure you want to reset to default settings? This action cannot be undone.')) {
                    // In a real app, would reset form to defaults
                    showNotification('Settings reset to defaults.');
                }
            });
        }
    });
}

/**
 * Initializes table functionality
 */
function initializeTableFunctionality() {
    // Table header checkboxes (select all)
    const headerCheckboxes = document.querySelectorAll('th .checkbox input');
    headerCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const table = this.closest('table');
            const tableBody = table.querySelector('tbody');
            const checkboxes = tableBody.querySelectorAll('.checkbox input');
            
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
            });
        });
    });
    
    // Table sorting
    const sortableHeaders = document.querySelectorAll('th i.fa-sort');
    sortableHeaders.forEach(icon => {
        icon.addEventListener('click', function() {
            const columnName = this.parentElement.textContent.trim();
            
            // Toggle sort direction
            if (this.classList.contains('fa-sort')) {
                this.classList.remove('fa-sort');
                this.classList.add('fa-sort-up');
            } else if (this.classList.contains('fa-sort-up')) {
                this.classList.remove('fa-sort-up');
                this.classList.add('fa-sort-down');
            } else {
                this.classList.remove('fa-sort-down');
                this.classList.add('fa-sort');
            }
            
            // In a real app, would sort the table data
            console.log(`Sorting by ${columnName}`);
        });
    });
    
    // Row action buttons
    const actionButtons = document.querySelectorAll('.actions-cell .icon-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.querySelector('i').className;
            const row = this.closest('tr');
            const userName = row.querySelector('.user-info span').textContent;
            
            if (action.includes('edit')) {
                // Show edit user modal/form
                console.log(`Edit user: ${userName}`);
                showNotification(`Editing user: ${userName}`);
            } else if (action.includes('key')) {
                // Password reset functionality
                console.log(`Reset password for: ${userName}`);
                if (confirm(`Send password reset email to ${userName}?`)) {
                    showNotification(`Password reset email sent to ${userName}`);
                }
            } else if (action.includes('trash')) {
                // Delete user functionality
                console.log(`Delete user: ${userName}`);
                if (confirm(`Are you sure you want to delete ${userName}? This action cannot be undone.`)) {
                    // In a real app, would delete the user
                    row.style.opacity = '0.5';
                    setTimeout(() => {
                        row.remove();
                    }, 500);
                    showNotification(`User ${userName} has been deleted`);
                }
            }
        });
    });
    
    // Pagination buttons
    const paginationButtons = document.querySelectorAll('.pagination-pages button');
    paginationButtons.forEach(button => {
        button.addEventListener('click', function() {
            paginationButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // In a real app, would load page data
            console.log(`Page ${this.textContent} selected`);
        });
    });
    
    // Prev/Next pagination buttons
    const prevButton = document.querySelector('.pagination-btn:first-child');
    const nextButton = document.querySelector('.pagination-btn:last-child');
    
    if (prevButton && nextButton) {
        prevButton.addEventListener('click', function() {
            const activePage = document.querySelector('.pagination-pages button.active');
            const prevPage = activePage.previousElementSibling;
            
            if (prevPage && prevPage.tagName === 'BUTTON') {
                activePage.classList.remove('active');
                prevPage.classList.add('active');
                
                // In a real app, would load previous page data
                console.log(`Navigated to page ${prevPage.textContent}`);
            }
        });
        
        nextButton.addEventListener('click', function() {
            const activePage = document.querySelector('.pagination-pages button.active');
            const nextPage = activePage.nextElementSibling;
            
            if (nextPage && nextPage.tagName === 'BUTTON') {
                activePage.classList.remove('active');
                nextPage.classList.add('active');
                
                // In a real app, would load next page data
                console.log(`Navigated to page ${nextPage.textContent}`);
            }
        });
    }
}

/**
 * Shows a notification message
 * @param {string} message - The message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getIconForType(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Add event listener to close button
    const closeButton = notification.querySelector('.notification-close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            notification.classList.add('notification-closing');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        });
    }
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.add('notification-closing');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 10);
}

/**
 * Gets the appropriate icon class for notification type
 * @param {string} type - Type of notification
 * @returns {string} - FontAwesome icon class
 */
function getIconForType(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'error':
            return 'fa-exclamation-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        case 'info':
            return 'fa-info-circle';
        default:
            return 'fa-info-circle';
    }
}

/**
 * Add custom CSS for notifications if not already in the CSS file
 */
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
.notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 1rem;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    z-index: 1000;
    max-width: 400px;
    transform: translateY(100px);
    opacity: 0;
    transition: transform 0.3s, opacity 0.3s;
}

.notification-show {
    transform: translateY(0);
    opacity: 1;
}

.notification-closing {
    transform: translateY(100px);
    opacity: 0;
}

.notification.success {
    border-left: 4px solid #34a853;
}

.notification.error {
    border-left: 4px solid #ea4335;
}

.notification.warning {
    border-left: 4px solid #fbbc04;
}

.notification.info {
    border-left: 4px solid #1a73e8;
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.notification-content i {
    font-size: 1.2rem;
}

.notification.success i {
    color: #34a853;
}

.notification.error i {
    color: #ea4335;
}

.notification.warning i {
    color: #fbbc04;
}

.notification.info i {
    color: #1a73e8;
}

.notification-close {
    background: none;
    border: none;
    color: #5f6368;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 50%;
    transition: background-color 0.2s;
}

.notification-close:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

@media (max-width: 480px) {
    .notification {
        left: 20px;
        right: 20px;
        max-width: none;
    }
}
`;

document.head.appendChild(notificationStyle);

// Machine Management Tab Functionality
function initializeMachineManagement() {
    console.log('Initializing Machine Management Tab');
    
    // View Toggle
    const gridViewBtn = document.getElementById('grid-view');
    const listViewBtn = document.getElementById('list-view');
    const machineGrid = document.querySelector('.machine-grid');
    
    if (gridViewBtn && listViewBtn && machineGrid) {
        gridViewBtn.addEventListener('change', function() {
            if (this.checked) {
                machineGrid.classList.remove('list-mode');
            }
        });
        
        listViewBtn.addEventListener('change', function() {
            if (this.checked) {
                machineGrid.classList.add('list-mode');
            }
        });
    }
    
    // Filter Controls
    const osTypeSelect = document.getElementById('os-type-filter');
    const groupSelect = document.getElementById('group-filter');
    const statusSelect = document.getElementById('status-filter');
    const searchInput = document.getElementById('machine-search');
    
    const filterControls = [osTypeSelect, groupSelect, statusSelect, searchInput];
    
    filterControls.forEach(control => {
        if (control) {
            control.addEventListener('change', filterMachines);
        }
    });
    
    if (searchInput) {
        searchInput.addEventListener('keyup', filterMachines);
    }
    
    // Initialize Machine Cards
    initializeMachineCards();
    
    // Sub-tab navigation
    const machineSubtabs = document.querySelectorAll('.machine-subtabs .subtab');
    const machineSubtabContents = document.querySelectorAll('.machine-subtab-content');
    
    if (machineSubtabs.length && machineSubtabContents.length) {
        machineSubtabs.forEach(tab => {
            tab.addEventListener('click', function() {
                machineSubtabs.forEach(t => t.classList.remove('active'));
                machineSubtabContents.forEach(c => c.classList.remove('active'));
                
                this.classList.add('active');
                const targetId = this.getAttribute('data-target');
                const targetContent = document.getElementById(targetId);
                
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }
    
    // Add Machine Button
    const addMachineBtn = document.getElementById('add-machine-btn');
    
    if (addMachineBtn) {
        addMachineBtn.addEventListener('click', function() {
            showNotification('Add Machine feature will be implemented in the next release', 'info');
        });
    }
}

function initializeMachineCards() {
    const machineCards = document.querySelectorAll('.machine-card');
    
    machineCards.forEach(card => {
        // Power Button
        const powerBtn = card.querySelector('.action-power');
        if (powerBtn) {
            powerBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const machineName = card.querySelector('.machine-name').textContent;
                const isOffline = card.classList.contains('offline');
                
                if (isOffline) {
                    showNotification(`Cannot power on offline machine: ${machineName}`, 'warning');
                } else {
                    showNotification(`Powering off ${machineName}...`, 'info');
                    
                    // Simulate powering off
                    setTimeout(() => {
                        card.classList.add('offline');
                        card.querySelector('.machine-status span').textContent = 'Offline';
                        card.querySelector('.ping-dot').classList.add('offline');
                        showNotification(`${machineName} powered off successfully`, 'success');
                    }, 2000);
                }
            });
        }
        
        // Sync Button
        const syncBtn = card.querySelector('.action-sync');
        if (syncBtn) {
            syncBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const machineName = card.querySelector('.machine-name').textContent;
                const isOffline = card.classList.contains('offline');
                
                if (isOffline) {
                    showNotification(`Cannot sync offline machine: ${machineName}`, 'warning');
                } else {
                    showNotification(`Syncing with ${machineName}...`, 'info');
                    
                    // Simulate sync
                    setTimeout(() => {
                        showNotification(`${machineName} synced successfully`, 'success');
                    }, 1500);
                }
            });
        }
        
        // Terminal Button
        const terminalBtn = card.querySelector('.action-terminal');
        if (terminalBtn) {
            terminalBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const machineName = card.querySelector('.machine-name').textContent;
                const isOffline = card.classList.contains('offline');
                
                if (isOffline) {
                    showNotification(`Cannot access terminal of offline machine: ${machineName}`, 'warning');
                } else {
                    showNotification(`Opening terminal for ${machineName}...`, 'info');
                }
            });
        }
        
        // Dropdown Menu Items
        const dropdownItems = card.querySelectorAll('.dropdown-menu a');
        dropdownItems.forEach(item => {
            item.addEventListener('click', function(e) {
                if (this.classList.contains('disabled')) {
                    e.preventDefault();
                    return;
                }
                
                const machineName = card.querySelector('.machine-name').textContent;
                const action = this.getAttribute('data-action');
                
                switch(action) {
                    case 'edit':
                        showNotification(`Editing machine: ${machineName}`, 'info');
                        break;
                    case 'remote':
                        showNotification(`Establishing remote connection to ${machineName}...`, 'info');
                        break;
                    case 'update':
                        showNotification(`Updating software on ${machineName}...`, 'info');
                        break;
                    case 'logs':
                        showNotification(`Fetching logs from ${machineName}...`, 'info');
                        break;
                    case 'decommission':
                        if (confirm(`Are you sure you want to decommission ${machineName}? This action cannot be undone.`)) {
                            showNotification(`Decommissioning ${machineName}...`, 'warning');
                            
                            // Simulate decommissioning
                            setTimeout(() => {
                                card.style.opacity = 0;
                                setTimeout(() => {
                                    card.remove();
                                    showNotification(`${machineName} has been decommissioned`, 'success');
                                }, 300);
                            }, 1500);
                        }
                        break;
                }
            });
        });
    });
}

function filterMachines() {
    console.log('Filtering machines...');
    const osTypeFilter = document.getElementById('os-type-filter')?.value || 'all';
    const groupFilter = document.getElementById('group-filter')?.value || 'all';
    const statusFilter = document.getElementById('status-filter')?.value || 'all';
    const searchTerm = document.getElementById('machine-search')?.value.toLowerCase() || '';
    
    const machineCards = document.querySelectorAll('.machine-card');
    
    machineCards.forEach(card => {
        const osType = card.getAttribute('data-os').toLowerCase();
        const group = card.getAttribute('data-group').toLowerCase();
        const status = card.classList.contains('offline') ? 'offline' : 
                       card.classList.contains('maintenance') ? 'maintenance' : 'online';
        const machineName = card.querySelector('.machine-name').textContent.toLowerCase();
        
        const matchesOs = osTypeFilter === 'all' || osType.includes(osTypeFilter.toLowerCase());
        const matchesGroup = groupFilter === 'all' || group === groupFilter.toLowerCase();
        const matchesStatus = statusFilter === 'all' || status === statusFilter.toLowerCase();
        const matchesSearch = searchTerm === '' || machineName.includes(searchTerm);
        
        if (matchesOs && matchesGroup && matchesStatus && matchesSearch) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

function updateMachineMetrics() {
    // This would be replaced with real-time data from an API
    const onlineMachines = document.querySelectorAll('.machine-card:not(.offline):not(.maintenance)');
    
    onlineMachines.forEach(machine => {
        const cpuMetric = machine.querySelector('.metric[data-type="cpu"] .circular-progress');
        const ramMetric = machine.querySelector('.metric[data-type="ram"] .circular-progress');
        const diskMetric = machine.querySelector('.metric[data-type="disk"] .circular-progress');
        
        const updateMetric = (metric) => {
            if (!metric) return;
            
            const currentValue = parseInt(metric.style.getPropertyValue('--progress') || 0);
            // Random fluctuation for demo purposes
            let newValue = currentValue + (Math.random() > 0.5 ? 1 : -1) * Math.floor(Math.random() * 5);
            
            // Ensure within bounds
            newValue = Math.max(5, Math.min(95, newValue));
            
            metric.style.setProperty('--progress', newValue);
            metric.querySelector('.progress-value').textContent = `${newValue}%`;
        };
        
        updateMetric(cpuMetric);
        updateMetric(ramMetric);
        updateMetric(diskMetric);
    });
}

// Initialize machine metrics update interval
let metricsInterval;

function setupMachineMetricsInterval() {
    if (metricsInterval) {
        clearInterval(metricsInterval);
    }
    metricsInterval = setInterval(updateMachineMetrics, 5000);
} 