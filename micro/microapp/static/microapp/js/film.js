document.addEventListener('DOMContentLoaded', function() {
    // Main state variables
    let currentStep = 'initialization';
    let isFilmingActive = false;
    let mockInterval = null;
    let mockProgress = 30; // Starting at 30%
    let totalDocuments = 423;
    let processedDocuments = 127;
    
    // Initialize charts
    initializeCharts();
    
    // Initialize event handlers
    initializeEventHandlers();
    
    // Initialize interface
    updateProgressIndicators();
    
    // Handle dark mode for stat-items
    const handleDarkMode = () => {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const statItems = document.querySelectorAll('.stat-item');
        
        statItems.forEach(item => {
            if (isDarkMode) {
                item.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                item.style.border = '1px solid var(--color-dark-border)';
            } else {
                item.style.backgroundColor = '';
                item.style.border = '';
            }
        });
    };
    
    // Run initially
    handleDarkMode();
    
    // Observe body class changes for dark mode toggle
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                handleDarkMode();
            }
        });
    });
    
    observer.observe(document.body, { attributes: true });
    
    // Main functions
    function initializeEventHandlers() {
        // Project selection functionality
        const projectItems = document.querySelectorAll('.project-item');
        projectItems.forEach(item => {
            item.addEventListener('click', function() {
                selectProject(this);
            });
        });
        
        // Project action buttons
        document.querySelectorAll('.select-button').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                selectProject(this.closest('.project-item'));
            });
        });
        
        // Resume button
        document.querySelectorAll('.resume-button').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                selectProject(this.closest('.project-item'));
                startFilmingProcess(true); // Start with resume flag
            });
        });
        
        // View button
        document.querySelectorAll('.view-button').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                const projectId = this.closest('.project-item').getAttribute('data-id');
                alert(`View details for completed project ${projectId}`);
            });
        });
        
        // Start filming button
        document.getElementById('start-filming').addEventListener('click', function() {
            startFilmingProcess(false);
        });
        
        // Recovery mode button
        document.getElementById('recovery-mode').addEventListener('click', function() {
            startFilmingProcess(true);
        });
        
        // Filming control buttons
        document.getElementById('pause-filming').addEventListener('click', togglePauseFilming);
        document.getElementById('cancel-filming').addEventListener('click', cancelFilming);
        document.getElementById('mock-next-step').addEventListener('click', advanceToNextStep);
        
        // Expand log button
        document.getElementById('expand-log').addEventListener('click', toggleExpandLog);
        
        // Filter and search
        document.getElementById('project-search').addEventListener('input', filterProjects);
        document.getElementById('project-status-filter').addEventListener('change', filterProjects);
        document.getElementById('project-type-filter').addEventListener('change', filterProjects);
        
        // Film type toggle
        document.querySelectorAll('input[name="film-type"]').forEach(radio => {
            radio.addEventListener('change', updateFilmNumber);
        });
    }
    
    function selectProject(projectItem) {
        // Deselect all projects
        document.querySelectorAll('.project-item').forEach(p => p.classList.remove('selected'));
        
        // Select the current project
        projectItem.classList.add('selected');
        
        // Update project info in the filming section
        const projectName = projectItem.querySelector('.project-name').textContent;
        document.getElementById('filming-project-name').textContent = projectName;
        
        // Update film number based on project ID and selected film type
        updateFilmNumber();
        
        // Update document counters
        const pages = parseInt(projectItem.querySelector('.project-pages').textContent);
        totalDocuments = pages;
        processedDocuments = 0;
        updateDocumentCounters();
    }
    
    function updateFilmNumber() {
        const selectedProject = document.querySelector('.project-item.selected');
        if (selectedProject) {
            const projectId = selectedProject.getAttribute('data-id');
            const filmType = document.querySelector('input[name="film-type"]:checked').value;
            const filmNumber = `F-${filmType}-${projectId.slice(-4)}`;
            document.getElementById('film-number').textContent = filmNumber;
        }
    }
    
    function filterProjects() {
        const searchTerm = document.getElementById('project-search').value.toLowerCase();
        const statusFilter = document.getElementById('project-status-filter').value;
        const typeFilter = document.getElementById('project-type-filter').value;
        
        document.querySelectorAll('.project-item').forEach(project => {
            const projectName = project.querySelector('.project-name').textContent.toLowerCase();
            const projectId = project.querySelector('.project-id').textContent.toLowerCase();
            const projectType = project.querySelector('.project-type').textContent.toLowerCase();
            const statusBadge = project.querySelector('.status-badge');
            const projectStatus = statusBadge ? statusBadge.classList[1] : '';
            
            const matchesSearch = projectName.includes(searchTerm) || projectId.includes(searchTerm);
            const matchesStatus = statusFilter === 'all' || projectStatus === statusFilter;
            const matchesType = typeFilter === 'all' || projectType === typeFilter;
            
            if (matchesSearch && matchesStatus && matchesType) {
                project.style.display = '';
            } else {
                project.style.display = 'none';
            }
        });
    }
    
    function startFilmingProcess(isRecovery) {
        const selectedProject = document.querySelector('.project-item.selected');
        if (!selectedProject) {
            alert('Please select a project to film');
            return;
        }
        
        // Display the filming process section
        document.getElementById('filming-process-section').style.display = 'block';
        
        // Reset progress to initial state
        if (!isRecovery) {
            currentStep = 'initialization';
            mockProgress = 0;
            processedDocuments = 0;
            
            // Reset progress indicators
            document.querySelectorAll('.progress-step').forEach(step => {
                step.classList.remove('completed', 'in-progress');
                if (step.getAttribute('data-step') === 'initialization') {
                    step.classList.add('in-progress');
                }
            });
            
            // Add initial log entries
            addLogEntry('Initializing SMA application...');
            
            // Start the mock filming process
            setTimeout(() => {
                addLogEntry('Application started successfully');
                advanceToNextStep(); // Advance to preparation
                
                setTimeout(() => {
                    const filmType = document.querySelector('input[name="film-type"]:checked').value;
                    addLogEntry(`Selecting template: ${filmType === '16' ? 'Portrait - 16mm.TPL' : 'Landscape - 35mm.TPL'}`);
                    advanceToNextStep(); // Advance to filming
                    
                    setTimeout(() => {
                        startMockFilmingProgress();
                    }, 1000);
                }, 1000);
            }, 1500);
        } else {
            // Recovery mode - start from the current state
            currentStep = 'filming';
            mockProgress = 30; // Start at 30%
            processedDocuments = Math.floor(totalDocuments * 0.3);
            
            // Set progress indicators for recovery
            document.querySelectorAll('.progress-step').forEach(step => {
                step.classList.remove('completed', 'in-progress');
                
                const stepName = step.getAttribute('data-step');
                if (stepName === 'initialization' || stepName === 'preparation') {
                    step.classList.add('completed');
                } else if (stepName === 'filming') {
                    step.classList.add('in-progress');
                }
            });
            
            // Add recovery log entries
            addLogEntry('Recovery mode initiated');
            addLogEntry('Reconnecting to SMA application...');
            
            setTimeout(() => {
                addLogEntry('Successfully recovered filming session');
                addLogEntry(`Current progress: ${mockProgress}% (${processedDocuments}/${totalDocuments})`);
                startMockFilmingProgress();
            }, 1500);
        }
        
        // Update counters
        updateDocumentCounters();
        
        // Update interface
        updateProgressIndicators();
        document.getElementById('current-activity-label').textContent = 'Processing Documents';
        
        // Scroll to the filming section
        document.getElementById('filming-process-section').scrollIntoView({ behavior: 'smooth' });
        
        // Set active filming state
        isFilmingActive = true;
        
        // Update button states
        updateControlButtons();
    }
    
    function startMockFilmingProgress() {
        // Clear any existing interval
        if (mockInterval) {
            clearInterval(mockInterval);
        }
        
        // Update progress bar and log entries periodically
        mockInterval = setInterval(() => {
            if (mockProgress < 100) {
                // Increase progress
                mockProgress += 0.5;
                processedDocuments = Math.floor((mockProgress / 100) * totalDocuments);
                
                // Update UI
                updateProgressBar();
                updateDocumentCounters();
                
                // Add log entry every 5%
                if (mockProgress % 5 < 0.5) {
                    addLogEntry(`Progress: ${mockProgress.toFixed(1)}% (${processedDocuments}/${totalDocuments}) - ETA: ${calculateMockETA()}`);
                }
                
                // Update processing rate
                document.getElementById('processing-rate').textContent = `${(Math.random() * 1.5 + 2.5).toFixed(1)} docs/sec`;
            } else {
                // Filming complete
                clearInterval(mockInterval);
                mockInterval = null;
                
                // Move to end symbols step
                addLogEntry('Document processing complete');
                advanceToNextStep(); // End symbols
            }
        }, 500);
    }
    
    function advanceToNextStep() {
        // Get the current and next steps
        const steps = ['initialization', 'preparation', 'filming', 'end-symbols', 'transport', 'completion'];
        const currentIndex = steps.indexOf(currentStep);
        
        if (currentIndex < steps.length - 1) {
            // Mark current step as completed
            const currentStepElement = document.querySelector(`.progress-step[data-step="${currentStep}"]`);
            currentStepElement.classList.remove('in-progress');
            currentStepElement.classList.add('completed');
            
            // Move to next step
            currentStep = steps[currentIndex + 1];
            const nextStepElement = document.querySelector(`.progress-step[data-step="${currentStep}"]`);
            nextStepElement.classList.add('in-progress');
            
            // Update activity label
            updateActivityLabel();
            
            // Add log entry for the step transition
            addLogEntry(`Starting ${formatStepName(currentStep)} phase`);
            
            // If we reached the end, show completion message
            if (currentStep === 'completion') {
                mockProgress = 100;
                processedDocuments = totalDocuments;
                updateProgressBar();
                updateDocumentCounters();
                
                addLogEntry('Filming process completed successfully');
                addLogEntry(`Final count: ${totalDocuments}/${totalDocuments} documents processed`);
                
                // Clear interval if running
                if (mockInterval) {
                    clearInterval(mockInterval);
                    mockInterval = null;
                }
                
                // Set filming inactive
                isFilmingActive = false;
                
                // Update buttons
                updateControlButtons();
            }
            
            // If we're at the transport step, update progress indicators
            if (currentStep === 'transport') {
                document.getElementById('current-activity-label').textContent = 'Film Transport';
                addLogEntry('Film transportation started');
                
                // Simulate film transport completion
                setTimeout(() => {
                    addLogEntry('Film transportation completed');
                    advanceToNextStep(); // Move to completion
                }, 5000);
            }
            
            // If we're at the end symbols step
            if (currentStep === 'end-symbols') {
                document.getElementById('current-activity-label').textContent = 'Adding End Symbols';
                addLogEntry('Adding end symbols to film');
                
                // Simulate end symbols completion
                setTimeout(() => {
                    addLogEntry('End symbols added successfully');
                    advanceToNextStep(); // Move to transport
                }, 3000);
            }
        }
        
        // Update the progress indicators
        updateProgressIndicators();
    }
    
    function togglePauseFilming() {
        if (!isFilmingActive) return;
        
        const pauseButton = document.getElementById('pause-filming');
        
        if (mockInterval) {
            // Currently running, pause it
            clearInterval(mockInterval);
            mockInterval = null;
            pauseButton.innerHTML = '<i class="fas fa-play"></i> Resume Filming';
            addLogEntry('Filming process paused');
            document.getElementById('current-activity-label').textContent += ' (Paused)';
        } else {
            // Currently paused, resume it
            startMockFilmingProgress();
            pauseButton.innerHTML = '<i class="fas fa-pause"></i> Pause Filming';
            addLogEntry('Filming process resumed');
            updateActivityLabel();
        }
    }
    
    function cancelFilming() {
        if (!isFilmingActive) return;
        
        // Show confirmation dialog
        if (confirm('Are you sure you want to cancel the filming process? This cannot be undone.')) {
            // Clear interval if running
            if (mockInterval) {
                clearInterval(mockInterval);
                mockInterval = null;
            }
            
            // Reset progress indicators
            document.querySelectorAll('.progress-step').forEach(step => {
                step.classList.remove('completed', 'in-progress');
            });
            
            // Add log entry
            addLogEntry('Filming process cancelled by user');
            
            // Hide filming section
            document.getElementById('filming-process-section').style.display = 'none';
            
            // Reset state
            isFilmingActive = false;
            currentStep = 'initialization';
            mockProgress = 0;
            processedDocuments = 0;
            
            // Update interface
            updateProgressBar();
            updateDocumentCounters();
            updateControlButtons();
        }
    }
    
    function updateActivityLabel() {
        const activityLabel = document.getElementById('current-activity-label');
        
        switch (currentStep) {
            case 'initialization':
                activityLabel.textContent = 'System Initialization';
                break;
            case 'preparation':
                activityLabel.textContent = 'Preparation';
                break;
            case 'filming':
                activityLabel.textContent = 'Processing Documents';
                break;
            case 'end-symbols':
                activityLabel.textContent = 'Adding End Symbols';
                break;
            case 'transport':
                activityLabel.textContent = 'Film Transport';
                break;
            case 'completion':
                activityLabel.textContent = 'Process Complete';
                break;
        }
    }
    
    function updateProgressBar() {
        const progressBar = document.getElementById('filming-progress-bar');
        const percentage = document.getElementById('progress-percentage');
        
        progressBar.style.width = `${mockProgress}%`;
        percentage.textContent = `${mockProgress.toFixed(1)}%`;
    }
    
    function updateDocumentCounters() {
        document.getElementById('processed-count').textContent = processedDocuments;
        document.getElementById('remaining-count').textContent = totalDocuments - processedDocuments;
        document.getElementById('total-count').textContent = totalDocuments;
        document.getElementById('eta-time').textContent = calculateMockETA();
    }
    
    function updateProgressIndicators() {
        // Get all steps
        const steps = ['initialization', 'preparation', 'filming', 'end-symbols', 'transport', 'completion'];
        const currentIndex = steps.indexOf(currentStep);
        
        // Update each step's status
        steps.forEach((step, index) => {
            const stepElement = document.querySelector(`.progress-step[data-step="${step}"]`);
            
            if (index < currentIndex) {
                // Steps before current are completed
                stepElement.classList.remove('in-progress');
                stepElement.classList.add('completed');
            } else if (index === currentIndex) {
                // Current step is in progress
                stepElement.classList.remove('completed');
                stepElement.classList.add('in-progress');
            } else {
                // Future steps are neither
                stepElement.classList.remove('completed', 'in-progress');
            }
        });
    }
    
    function updateControlButtons() {
        const pauseButton = document.getElementById('pause-filming');
        const cancelButton = document.getElementById('cancel-filming');
        const nextButton = document.getElementById('mock-next-step');
        
        if (isFilmingActive) {
            pauseButton.disabled = false;
            cancelButton.disabled = false;
            nextButton.disabled = false;
            
            // Reset pause button text
            pauseButton.innerHTML = '<i class="fas fa-pause"></i> Pause Filming';
        } else {
            pauseButton.disabled = true;
            cancelButton.disabled = true;
            nextButton.disabled = true;
        }
    }
    
    function toggleExpandLog() {
        const logContent = document.getElementById('log-content');
        const expandButton = document.getElementById('expand-log');
        
        if (logContent.classList.contains('expanded')) {
            logContent.classList.remove('expanded');
            expandButton.innerHTML = '<i class="fas fa-expand-alt"></i>';
        } else {
            logContent.classList.add('expanded');
            expandButton.innerHTML = '<i class="fas fa-compress-alt"></i>';
        }
    }
    
    function addLogEntry(message) {
        const logContent = document.getElementById('log-content');
        const now = new Date();
        const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry info';
        logEntry.innerHTML = `<span class="timestamp">${timestamp}</span><span class="log-text">${message}</span>`;
        
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    }
    
    function calculateMockETA() {
        // Mock ETA calculation
        const now = new Date();
        const minutesToAdd = 16 + Math.floor(Math.random() * 5);
        now.setMinutes(now.getMinutes() + minutesToAdd);
        
        return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    }
    
    function formatStepName(step) {
        // Convert step ID to readable name
        switch (step) {
            case 'initialization': return 'Initialization';
            case 'preparation': return 'Preparation';
            case 'filming': return 'Filming';
            case 'end-symbols': return 'End Symbols';
            case 'transport': return 'Film Transport';
            case 'completion': return 'Completion';
            default: return step;
        }
    }
    
    function initializeCharts() {
        // Temperature chart data
        const tempCtx = document.getElementById('temperature-chart').getContext('2d');
        const tempData = {
            labels: Array.from({length: 30}, (_, i) => `-${29-i}m`),
            datasets: [{
                label: 'Temperature °C',
                data: generateMockTemperatureData(),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4,
                fill: true
            }]
        };
        
        // Processing chart data
        const procCtx = document.getElementById('processing-chart').getContext('2d');
        const procData = {
            labels: Array.from({length: 30}, (_, i) => `-${29-i}m`),
            datasets: [{
                label: 'Docs/Second',
                data: generateMockProcessingData(),
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.4,
                fill: true
            }]
        };
        
        // Chart options
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        };
        
        // Create charts
        new Chart(tempCtx, {
            type: 'line',
            data: tempData,
            options: chartOptions
        });
        
        new Chart(procCtx, {
            type: 'line',
            data: procData,
            options: chartOptions
        });
    }
    
    function generateMockTemperatureData() {
        // Generate realistic temperature data around 28°C
        const baseTemp = 28;
        return Array.from({length: 30}, () => baseTemp + (Math.random() * 1.2 - 0.6));
    }
    
    function generateMockProcessingData() {
        // Generate realistic processing rate data around 3 docs/sec
        const baseRate = 3;
        return Array.from({length: 30}, () => baseRate + (Math.random() * 1.6 - 0.8));
    }
});