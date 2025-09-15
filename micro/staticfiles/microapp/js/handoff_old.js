/**
 * Handoff Interface JavaScript
 * Microfilm Processing System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let selectedMethod = null;
    let selectedProject = null;
    let transferActive = false;
    let transferProgress = 0;
    let transferInterval = null;
    
    // DOM elements
    const methodCards = document.querySelectorAll('.method-card');
    const configSections = document.querySelectorAll('.config-section');
    const backButtons = document.querySelectorAll('.back-to-methods-btn');
    const directHandoffButtons = document.querySelectorAll('.direct-handoff-btn');
    const projectSearchInput = document.getElementById('project-search');
    const statusFilter = document.getElementById('status-filter');
    const dateFilter = document.getElementById('date-filter');
    
    // Initialize event handlers
    initializeEventHandlers();
    
    // Initialize charts
    initializeCharts();
    
    // Main functions
    function initializeEventHandlers() {
        // Method selection
        methodCards.forEach(card => {
            card.addEventListener('click', function() {
                selectMethod(this.id.split('-')[0]);
            });
            
            // Also handle the button click separately to prevent bubbling issues
            const selectBtn = card.querySelector('.select-method-btn');
            if (selectBtn) {
                selectBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    selectMethod(this.getAttribute('data-method'));
                });
            }
        });
        
        // Back buttons
        backButtons.forEach(btn => {
            btn.addEventListener('click', goBackToMethodSelection);
        });
        
        // Direct handoff buttons
        directHandoffButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                startHandoffProcess(this.getAttribute('data-method'));
            });
        });
        
        // Project search
        if (projectSearchInput) {
            projectSearchInput.addEventListener('input', filterProjects);
        }
        
        // Filters
        if (statusFilter) {
            statusFilter.addEventListener('change', filterProjects);
        }
        
        if (dateFilter) {
            dateFilter.addEventListener('change', filterProjects);
        }
        
        // Network auth type change
        const networkAuth = document.getElementById('network-auth');
        if (networkAuth) {
            networkAuth.addEventListener('change', function() {
                const credentialsSection = document.querySelector('.network-credentials');
                if (this.value === 'custom') {
                    credentialsSection.style.display = 'block';
                } else {
                    credentialsSection.style.display = 'none';
                }
            });
        }
        
        // USB drive refresh
        const refreshUsbBtn = document.getElementById('refresh-usb-drives');
        if (refreshUsbBtn) {
            refreshUsbBtn.addEventListener('click', refreshUsbDrives);
        }
        
        // Expand log button
        const expandLogBtn = document.getElementById('expand-log-btn');
        if (expandLogBtn) {
            expandLogBtn.addEventListener('click', toggleExpandLog);
        }
        
        // Cancel transfer button
        const cancelTransferBtn = document.getElementById('cancel-transfer');
        if (cancelTransferBtn) {
            cancelTransferBtn.addEventListener('click', cancelTransfer);
        }
        
        // Pause transfer button
        const pauseTransferBtn = document.getElementById('pause-transfer');
        if (pauseTransferBtn) {
            pauseTransferBtn.addEventListener('click', togglePauseTransfer);
        }
        
        // View history button
        const viewHistoryBtn = document.querySelector('.view-history-btn');
        if (viewHistoryBtn) {
            viewHistoryBtn.addEventListener('click', function() {
                // Scroll to history section
                document.querySelector('.historical-section').scrollIntoView({ behavior: 'smooth' });
            });
        }
        
        // Project selection in the project cards
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('select-project-btn') || 
                e.target.closest('.select-project-btn')) {
                const projectCard = e.target.closest('.project-card');
                if (projectCard) {
                    selectProject(projectCard);
                }
            }
        });
        
        // Action buttons in history table
        document.querySelectorAll('.action-icon-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.querySelector('i').classList.contains('fa-eye') ? 'view' : 'repeat';
                const row = this.closest('tr');
                const projectName = row.cells[1].textContent;
                
                if (action === 'view') {
                    alert(`Viewing details for ${projectName}`);
                } else {
                    alert(`Repeating transfer for ${projectName}`);
                }
            });
        });
    }
    
    function selectMethod(method) {
        // Hide all config sections
        configSections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Show the selected method's config section
        const configSection = document.getElementById(`${method}-config`);
        if (configSection) {
            configSection.style.display = 'block';
            
            // Scroll to the config section
            configSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Update selected method
        selectedMethod = method;
        
        // Show project selection section
        document.querySelector('.project-selection-section').style.display = 'block';
        
        // Load projects (in a real app, this would fetch from the server)
        loadProjects();
    }
    
    function goBackToMethodSelection() {
        // Hide all config sections
        configSections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Hide project selection section
        document.querySelector('.project-selection-section').style.display = 'none';
        
        // Reset selected method
        selectedMethod = null;
        
        // Scroll back to method cards
        document.querySelector('.method-cards').scrollIntoView({ behavior: 'smooth' });
    }
    
    function loadProjects() {
        // In a real app, this would fetch projects from the server
        // For now, we'll just use the template to create some mock projects
        const projectContainer = document.querySelector('.project-cards');
        if (!projectContainer) return;
        
        // Clear existing projects
        projectContainer.innerHTML = '';
        
        // Get the template
        const template = document.getElementById('project-card-template');
        if (!template) return;
        
        // Create some mock projects
        const mockProjects = [
            {
                name: 'Financial Records 2023',
                date: '2023-06-24',
                documents: 125,
                films: 4,
                size: '24.5 MB',
                types: ['CSV', 'PDF', 'IMG']
            },
            {
                name: 'Historical Manuscripts',
                date: '2023-05-15',
                documents: 87,
                films: 2,
                size: '18.2 MB',
                types: ['PDF', 'IMG']
            },
            {
                name: 'Corporate Archives Q1',
                date: '2023-04-10',
                documents: 203,
                films: 6,
                size: '35.7 MB',
                types: ['CSV', 'XLSX', 'PDF']
            },
            {
                name: 'Legal Documentation',
                date: '2023-03-22',
                documents: 64,
                films: 1,
                size: '12.8 MB',
                types: ['PDF', 'DOCX']
            }
        ];
        
        // Create project cards
        mockProjects.forEach(project => {
            const card = document.importNode(template.content, true);
            
            // Update card content
            card.querySelector('.project-name').textContent = project.name;
            card.querySelector('.project-date').textContent = project.date;
            card.querySelectorAll('.stat-value')[0].textContent = project.documents;
            card.querySelectorAll('.stat-value')[1].textContent = project.films;
            card.querySelectorAll('.stat-value')[2].textContent = project.size;
            
            // Update file types
            const typesContainer = card.querySelector('.project-types');
            typesContainer.innerHTML = '';
            
            project.types.forEach(type => {
                const typeSpan = document.createElement('span');
                typeSpan.className = 'file-type';
                
                let icon = 'file';
                if (type === 'CSV') icon = 'file-csv';
                else if (type === 'PDF') icon = 'file-pdf';
                else if (type === 'IMG') icon = 'file-image';
                else if (type === 'XLSX') icon = 'file-excel';
                else if (type === 'DOCX') icon = 'file-word';
                
                typeSpan.innerHTML = `<i class="fas fa-${icon}"></i> ${type}`;
                typesContainer.appendChild(typeSpan);
            });
            
            // Add to container
            projectContainer.appendChild(card);
        });
    }
    
    function selectProject(projectCard) {
        // Remove selection from all projects
        document.querySelectorAll('.project-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection to clicked project
        projectCard.classList.add('selected');
        
        // Store selected project
        selectedProject = {
            name: projectCard.querySelector('.project-name').textContent,
            size: projectCard.querySelector('.stat-value:nth-child(3)').textContent
        };
        
        // Enable the handoff button
        const handoffButtons = document.querySelectorAll('.direct-handoff-btn');
        handoffButtons.forEach(btn => {
            btn.disabled = false;
        });
    }
    
    function filterProjects() {
        const searchTerm = projectSearchInput.value.toLowerCase();
        const statusValue = statusFilter.value;
        const dateValue = dateFilter.value;
        
        document.querySelectorAll('.project-card').forEach(card => {
            const projectName = card.querySelector('.project-name').textContent.toLowerCase();
            const projectDate = card.querySelector('.project-date').textContent;
            
            // Simple search filter
            const matchesSearch = projectName.includes(searchTerm);
            
            // In a real app, we would have actual status and date filtering
            // For now, we'll just show all projects
            const matchesStatus = true;
            const matchesDate = true;
            
            if (matchesSearch && matchesStatus && matchesDate) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    function startHandoffProcess(method) {
        if (!selectedProject) {
            alert('Please select a project first');
            return;
        }
        
        // Hide config sections
        configSections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Hide project selection
        document.querySelector('.project-selection-section').style.display = 'none';
        
        // Show transaction section
        const transactionSection = document.querySelector('.transaction-section');
        transactionSection.style.display = 'block';
        
        // Scroll to transaction section
        transactionSection.scrollIntoView({ behavior: 'smooth' });
        
        // Update transaction details
        document.getElementById('transfer-project-name').textContent = selectedProject.name;
        document.getElementById('transfer-method').textContent = getMethodDisplayName(method);
        document.getElementById('transfer-size').textContent = selectedProject.size;
        
        // Set current date/time
        const now = new Date();
        document.getElementById('transfer-started').textContent = formatDateTime(now);
        
        // Reset progress
        transferProgress = 0;
        document.getElementById('transfer-percentage').textContent = '0%';
        document.querySelector('.progress-bar').style.width = '0%';
        
        // Clear log
        const logEntries = document.querySelector('.log-entries');
        logEntries.innerHTML = '';
        
        // Add initial log entries
        addLogEntry('Starting transfer process...');
        addLogEntry('Preparing files for transfer');
        
        // Set transfer as active
        transferActive = true;
        
        // Update status badge
        const statusBadge = document.getElementById('transfer-status-badge');
        statusBadge.innerHTML = '<i class="fas fa-clock"></i><span>Processing</span>';
        statusBadge.className = 'transfer-badge processing';
        
        // Update progress steps
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.remove('completed', 'active');
        });
        
        document.querySelector('.progress-step:first-child').classList.add('completed');
        document.querySelector('.progress-step:nth-child(3)').classList.add('active');
        document.querySelector('.progress-connector:first-child').classList.add('active');
        
        // Start progress simulation
        startProgressSimulation(method);
    }
    
    function startProgressSimulation(method) {
        // Clear any existing interval
        if (transferInterval) {
            clearInterval(transferInterval);
        }
        
        // Set transfer speed based on method
        let incrementAmount = 0;
        let intervalTime = 0;
        
        switch (method) {
            case 'email':
                incrementAmount = 1;
                intervalTime = 300;
                break;
            case 'usb':
                incrementAmount = 2;
                intervalTime = 200;
                break;
            case 'network':
                incrementAmount = 3;
                intervalTime = 150;
                break;
            default:
                incrementAmount = 1;
                intervalTime = 300;
        }
        
        // Start interval
        transferInterval = setInterval(() => {
            if (transferProgress < 100) {
                transferProgress += incrementAmount;
                if (transferProgress > 100) transferProgress = 100;
                
                // Update progress bar
                document.getElementById('transfer-percentage').textContent = `${Math.round(transferProgress)}%`;
                document.querySelector('.progress-bar').style.width = `${transferProgress}%`;
                
                // Add log entries at certain points
                if (transferProgress === incrementAmount) {
                    addLogEntry('Beginning upload...');
                } else if (transferProgress >= 25 && transferProgress < 25 + incrementAmount) {
                    const size = selectedProject.size;
                    const transferredSize = (parseFloat(size) * 0.25).toFixed(1) + ' MB';
                    addLogEntry(`Transferred ${transferredSize} / ${size}`);
                } else if (transferProgress >= 50 && transferProgress < 50 + incrementAmount) {
                    const size = selectedProject.size;
                    const transferredSize = (parseFloat(size) * 0.5).toFixed(1) + ' MB';
                    addLogEntry(`Transferred ${transferredSize} / ${size}`);
                } else if (transferProgress >= 75 && transferProgress < 75 + incrementAmount) {
                    const size = selectedProject.size;
                    const transferredSize = (parseFloat(size) * 0.75).toFixed(1) + ' MB';
                    addLogEntry(`Transferred ${transferredSize} / ${size}`);
                }
                
                // Update ETA
                const remainingPercentage = 100 - transferProgress;
                const remainingTime = Math.round(remainingPercentage / incrementAmount) * (intervalTime / 1000);
                document.getElementById('transfer-eta').textContent = formatTime(remainingTime);
                
            } else {
                // Transfer complete
                clearInterval(transferInterval);
                transferInterval = null;
                
                // Update status badge
                const statusBadge = document.getElementById('transfer-status-badge');
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i><span>Completed</span>';
                statusBadge.className = 'transfer-badge success';
                
                // Update progress steps
                document.querySelectorAll('.progress-step').forEach(step => {
                    step.classList.add('completed');
                    step.classList.remove('active');
                });
                
                document.querySelectorAll('.progress-connector').forEach(connector => {
                    connector.classList.add('active');
                });
                
                // Add completion log entries
                addLogEntry('Transfer completed successfully');
                addLogEntry('Verifying data integrity...');
                addLogEntry('Verification complete. All files transferred successfully.');
                
                // Set transfer as inactive
                transferActive = false;
                
                // Update buttons
                document.getElementById('pause-transfer').disabled = true;
                document.getElementById('cancel-transfer').disabled = true;
                
                // Add to history (in a real app, this would be saved to the server)
                addToHistory();
            }
        }, intervalTime);
    }
    
    function togglePauseTransfer() {
        if (!transferActive) return;
        
        const pauseButton = document.getElementById('pause-transfer');
        
        if (transferInterval) {
            // Currently running, pause it
            clearInterval(transferInterval);
            transferInterval = null;
            pauseButton.innerHTML = '<i class="fas fa-play"></i> Resume Transfer';
            addLogEntry('Transfer paused by user');
            
            // Update status badge
            const statusBadge = document.getElementById('transfer-status-badge');
            statusBadge.innerHTML = '<i class="fas fa-pause"></i><span>Paused</span>';
            statusBadge.className = 'transfer-badge paused';
        } else {
            // Currently paused, resume it
            startProgressSimulation(selectedMethod);
            pauseButton.innerHTML = '<i class="fas fa-pause"></i> Pause Transfer';
            addLogEntry('Transfer resumed');
            
            // Update status badge
            const statusBadge = document.getElementById('transfer-status-badge');
            statusBadge.innerHTML = '<i class="fas fa-clock"></i><span>Processing</span>';
            statusBadge.className = 'transfer-badge processing';
        }
    }
    
    function cancelTransfer() {
        if (!transferActive) return;
        
        // Show confirmation dialog
        if (confirm('Are you sure you want to cancel this transfer? This cannot be undone.')) {
            // Clear interval if running
            if (transferInterval) {
                clearInterval(transferInterval);
                transferInterval = null;
            }
            
            // Add log entry
            addLogEntry('Transfer cancelled by user');
            
            // Update status badge
            const statusBadge = document.getElementById('transfer-status-badge');
            statusBadge.innerHTML = '<i class="fas fa-times-circle"></i><span>Cancelled</span>';
            statusBadge.className = 'transfer-badge danger';
            
            // Set transfer as inactive
            transferActive = false;
            
            // Update buttons
            document.getElementById('pause-transfer').disabled = true;
            document.getElementById('cancel-transfer').disabled = true;
        }
    }
    
    function addLogEntry(message) {
        const logEntries = document.querySelector('.log-entries');
        const now = new Date();
        const timeString = now.toTimeString().split(' ')[0];
        
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
            <span class="log-time">${timeString}</span>
            <span class="log-message">${message}</span>
        `;
        
        logEntries.appendChild(entry);
        
        // Scroll to bottom
        logEntries.scrollTop = logEntries.scrollHeight;
    }
    
    function toggleExpandLog() {
        const logEntries = document.querySelector('.log-entries');
        const expandButton = document.getElementById('expand-log-btn');
        
        if (logEntries.classList.contains('expanded')) {
            logEntries.classList.remove('expanded');
            expandButton.innerHTML = '<i class="fas fa-expand-alt"></i>';
        } else {
            logEntries.classList.add('expanded');
            expandButton.innerHTML = '<i class="fas fa-compress-alt"></i>';
        }
    }
    
    function refreshUsbDrives() {
        const usbDriveSelect = document.getElementById('usb-drive');
        
        // Clear existing options
        while (usbDriveSelect.options.length > 0) {
            usbDriveSelect.remove(0);
        }
        
        // Add loading option
        const loadingOption = document.createElement('option');
        loadingOption.text = 'Scanning for drives...';
        loadingOption.disabled = true;
        loadingOption.selected = true;
        usbDriveSelect.add(loadingOption);
        
        // Simulate scanning
        setTimeout(() => {
            // Remove loading option
            usbDriveSelect.remove(0);
            
            // Add mock drives
            const drives = [
                { value: 'E:', text: 'USB Drive (E:) - 32GB' },
                { value: 'F:', text: 'External Drive (F:) - 500GB' },
                { value: 'G:', text: 'Removable Disk (G:) - 16GB' }
            ];
            
            drives.forEach(drive => {
                const option = document.createElement('option');
                option.value = drive.value;
                option.text = drive.text;
                usbDriveSelect.add(option);
            });
            
            // Select first option
            usbDriveSelect.selectedIndex = 0;
        }, 1500);
    }
    
    function addToHistory() {
        // In a real app, this would save to the server
        // For now, we'll just add a row to the history table
        
        const historyTable = document.querySelector('.history-table tbody');
        if (!historyTable) return;
        
        const now = new Date();
        const dateString = formatDateTime(now);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${dateString}</td>
            <td>${selectedProject.name}</td>
            <td><i class="fas fa-${getMethodIcon(selectedMethod)}"></i> ${getMethodDisplayName(selectedMethod)}</td>
            <td><span class="status-badge success">Completed</span></td>
            <td>${selectedProject.size}</td>
            <td>
                <button class="action-icon-btn"><i class="fas fa-eye"></i></button>
                <button class="action-icon-btn"><i class="fas fa-redo-alt"></i></button>
            </td>
        `;
        
        // Add at the top of the table
        historyTable.insertBefore(row, historyTable.firstChild);
        
        // Add event listeners to the new buttons
        row.querySelectorAll('.action-icon-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.querySelector('i').classList.contains('fa-eye') ? 'view' : 'repeat';
                
                if (action === 'view') {
                    alert(`Viewing details for ${selectedProject.name}`);
                } else {
                    alert(`Repeating transfer for ${selectedProject.name}`);
                }
            });
        });
    }
    
    function initializeCharts() {
        // In a real app, this would use Chart.js or similar to create actual charts
        // For now, we'll just use the placeholder charts in the HTML
    }
    
    // Helper functions
    function getMethodDisplayName(method) {
        switch (method) {
            case 'email': return 'Email';
            case 'usb': return 'USB';
            case 'network': return 'Network';
            default: return 'Unknown';
        }
    }
    
    function getMethodIcon(method) {
        switch (method) {
            case 'email': return 'envelope';
            case 'usb': return 'usb';
            case 'network': return 'network-wired';
            default: return 'question-circle';
        }
    }
    
    function formatDateTime(date) {
        return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}:${padZero(date.getSeconds())}`;
    }
    
    function padZero(num) {
        return num.toString().padStart(2, '0');
    }
    
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${padZero(remainingSeconds)}`;
    }
});
