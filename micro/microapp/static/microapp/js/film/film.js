document.addEventListener('DOMContentLoaded', function() {
    // Main state variables
    let currentStep = 'initialization';
    let isFilmingActive = false;
    let mockInterval = null;
    let mockProgress = 30; // Starting at 30%
    let totalDocuments = 423;
    let processedDocuments = 127;
    let allProjects = []; // Store all loaded projects
    let filteredProjects = []; // Store filtered projects
    
    // Initialize the application
    initializeApp();
    
    async function initializeApp() {
        // Initialize charts
        initializeCharts();
        
        // Initialize event handlers
        initializeEventHandlers();
        
        // Load projects from API
        await loadProjects();
        
        // Initialize interface
        updateProgressIndicators();
        updateQuickStats();
        
        // Disable start filming button initially
        document.getElementById('start-filming').disabled = true;
        
        // Handle dark mode for stat-items
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
    }
    
    // Load projects from the API
    async function loadProjects() {
        try {
            showLoadingState();
            
            const response = await fetch('/api/projects/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Handle the response format from views.list_projects
            if (data.status === 'success') {
                allProjects = data.results || [];
            } else {
                throw new Error(data.message || 'Failed to load projects');
            }
            
            // Filter projects that are ready for filming
            filteredProjects = allProjects.filter(project => {
                // Projects are ready for filming if they have documents and are not already completed
                return !project.film_allocation_complete && (project.total_pages > 0 || project.has_oversized);
            });
            
            displayProjects(filteredProjects);
            hideLoadingState();
            
        } catch (error) {
            console.error('Error loading projects:', error);
            showErrorState('Failed to load projects. Please try again.');
        }
    }
    
    // Display projects in the list
    function displayProjects(projects) {
        const projectList = document.getElementById('project-list');
        
        if (projects.length === 0) {
            projectList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>No projects available for filming</p>
                    <small>Projects need to have documents processed before they can be filmed.</small>
                </div>
            `;
            return;
        }
        
        projectList.innerHTML = projects.map(project => {
            const status = getProjectFilmingStatus(project);
            const statusClass = getStatusClass(status);
            const projectType = project.doc_type || 'Document';
            const totalPages = project.total_pages || 0;
            const location = project.location || 'Unknown';
            
            return `
                <div class="project-item" data-id="${project.id}" data-archive-id="${project.archive_id}">
                    <div class="project-info">
                        <div class="project-name">${project.project_folder_name || project.archive_id}</div>
                        <div class="project-id">${project.archive_id}</div>
                        <div class="project-location">${location}</div>
                        <div class="project-pages">${totalPages}</div>
                        <div class="project-type">${projectType}</div>
                        <div class="project-status">
                            <span class="status-badge ${statusClass}">${status}</span>
                        </div>
                    </div>
                    <div class="project-actions">
                        ${status === 'Ready' ? `
                            <button class="select-button" title="Select for filming">
                                <i class="fas fa-check"></i> Select
                            </button>
                        ` : status === 'In Progress' ? `
                            <button class="resume-button" title="Resume filming">
                                <i class="fas fa-play"></i> Resume
                            </button>
                        ` : `
                            <button class="view-button" title="View details">
                                <i class="fas fa-eye"></i> View
                            </button>
                        `}
                    </div>
                </div>
            `;
        }).join('');
        
        // Re-attach event listeners to new project items
        attachProjectEventListeners();
    }
    
    // Determine project filming status
    function getProjectFilmingStatus(project) {
        if (project.film_allocation_complete) {
            return 'Completed';
        } else if (project.processing_complete && project.total_pages > 0) {
            return 'Ready';
        } else if (project.total_pages > 0) {
            return 'In Progress';
        } else {
            return 'Pending';
        }
    }
    
    // Get CSS class for status
    function getStatusClass(status) {
        switch (status) {
            case 'Ready': return 'ready';
            case 'In Progress': return 'in-progress';
            case 'Completed': return 'completed';
            case 'Pending': return 'pending';
            default: return 'pending';
        }
    }
    
    // Attach event listeners to project items
    function attachProjectEventListeners() {
        // Project selection functionality
        document.querySelectorAll('.project-item').forEach(item => {
            item.addEventListener('click', function(e) {
                // Don't select if clicking on action buttons
                if (!e.target.closest('.project-actions')) {
                    selectProject(this);
                }
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
                viewProjectDetails(projectId);
            });
        });
    }
    
    // Show loading state
    function showLoadingState() {
        const projectList = document.getElementById('project-list');
        projectList.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading projects...</p>
            </div>
        `;
    }
    
    // Hide loading state
    function hideLoadingState() {
        // Loading state will be replaced by displayProjects()
    }
    
    // Show error state
    function showErrorState(message) {
        const projectList = document.getElementById('project-list');
        projectList.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button onclick="location.reload()" class="retry-button">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }
    
    // Update quick stats
    function updateQuickStats() {
        const totalProjects = allProjects.length;
        const readyForFilming = allProjects.filter(p => getProjectFilmingStatus(p) === 'Ready').length;
        const totalPages = allProjects.reduce((sum, p) => sum + (p.total_pages || 0), 0);
        
        document.getElementById('total-projects').textContent = totalProjects;
        document.getElementById('ready-filming').textContent = readyForFilming;
        document.getElementById('total-pages').textContent = totalPages.toLocaleString();
    }
    
    // Filter projects based on search and filter criteria
    function filterProjects() {
        const searchTerm = document.getElementById('project-search').value.toLowerCase();
        const statusFilter = document.getElementById('project-status-filter').value;
        const typeFilter = document.getElementById('project-type-filter').value;
        
        filteredProjects = allProjects.filter(project => {
            // Search filter
            const matchesSearch = !searchTerm || 
                (project.archive_id && project.archive_id.toLowerCase().includes(searchTerm)) ||
                (project.project_folder_name && project.project_folder_name.toLowerCase().includes(searchTerm)) ||
                (project.location && project.location.toLowerCase().includes(searchTerm));
            
            // Status filter
            const projectStatus = getProjectFilmingStatus(project);
            const matchesStatus = statusFilter === 'all' || 
                (statusFilter === 'ready' && projectStatus === 'Ready') ||
                (statusFilter === 'in-progress' && projectStatus === 'In Progress') ||
                (statusFilter === 'completed' && projectStatus === 'Completed');
            
            // Type filter
            const projectType = (project.doc_type || 'document').toLowerCase();
            const matchesType = typeFilter === 'all' || projectType === typeFilter;
            
            return matchesSearch && matchesStatus && matchesType;
        });
        
        displayProjects(filteredProjects);
    }
    
    // View project details
    function viewProjectDetails(projectId) {
        // For now, show an alert. In the future, this could open a modal or navigate to a details page
        const project = allProjects.find(p => p.id == projectId);
        if (project) {
            alert(`Project Details:\n\nArchive ID: ${project.archive_id}\nLocation: ${project.location}\nType: ${project.doc_type}\nPages: ${project.total_pages}\nStatus: ${getProjectFilmingStatus(project)}`);
        }
    }
    
    // Get CSRF token for API requests
    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

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
    
    // Main functions
    function initializeEventHandlers() {
        // Start filming button
        document.getElementById('start-filming').addEventListener('click', function() {
            startFilmingProcess(false);
        });
        
        // Filming control buttons
        const pauseButton = document.getElementById('pause-filming');
        const cancelButton = document.getElementById('cancel-filming');
        const expandLogButton = document.getElementById('expand-log');
        
        if (pauseButton) pauseButton.addEventListener('click', togglePauseFilming);
        if (cancelButton) cancelButton.addEventListener('click', cancelFilming);
        if (expandLogButton) expandLogButton.addEventListener('click', toggleExpandLog);
        
        // Filter and search
        document.getElementById('project-search').addEventListener('input', filterProjects);
        document.getElementById('project-status-filter').addEventListener('change', filterProjects);
        document.getElementById('project-type-filter').addEventListener('change', filterProjects);
        
        // Search button
        document.getElementById('search-button').addEventListener('click', function() {
            filterProjects();
        });
        
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
        
        // Enable start filming button
        document.getElementById('start-filming').disabled = false;
    }
    
    function updateFilmNumber() {
        const selectedProject = document.querySelector('.project-item.selected');
        if (selectedProject) {
            const projectId = selectedProject.getAttribute('data-id');
            const filmType = document.querySelector('input[name="film-type"]:checked').value;
            const filmNumber = `F-${filmType}-${projectId.toString().padStart(4, '0')}`;
            document.getElementById('film-number').textContent = filmNumber;
        }
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
                const processingRateElement = document.getElementById('processing-rate');
                if (processingRateElement) {
                    processingRateElement.textContent = `${(Math.random() * 1.5 + 2.5).toFixed(1)} docs/sec`;
                }
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
        const steps = ['initialization', 'preparation', 'filming', 'finalization'];
        const currentIndex = steps.indexOf(currentStep);
        
        if (currentIndex < steps.length - 1) {
            // Mark current step as completed
            const currentStepElement = document.querySelector(`.progress-step[data-step="${currentStep}"]`);
            if (currentStepElement) {
                currentStepElement.classList.remove('in-progress');
                currentStepElement.classList.add('completed');
            }
            
            // Move to next step
            currentStep = steps[currentIndex + 1];
            const nextStepElement = document.querySelector(`.progress-step[data-step="${currentStep}"]`);
            if (nextStepElement) {
                nextStepElement.classList.add('in-progress');
            }
            
            // Update activity label
            updateActivityLabel();
            
            // Add log entry for the step transition
            addLogEntry(`Starting ${formatStepName(currentStep)} phase`);
            
            // If we reached the end, show completion message
            if (currentStep === 'finalization') {
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
            case 'finalization':
                activityLabel.textContent = 'Process Complete';
                break;
        }
    }
    
    function updateProgressBar() {
        const progressBar = document.querySelector('.progress-bar-fill');
        const progressText = document.querySelector('.progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${mockProgress}%`;
        }
        if (progressText) {
            progressText.textContent = `${mockProgress.toFixed(1)}%`;
        }
    }
    
    function updateDocumentCounters() {
        const processedElement = document.getElementById('processed-docs');
        const totalElement = document.getElementById('total-docs');
        const progressTextElement = document.querySelector('.progress-text');
        const etaTextElement = document.querySelector('.eta-text');
        
        if (processedElement) processedElement.textContent = processedDocuments;
        if (totalElement) totalElement.textContent = totalDocuments;
        if (progressTextElement) progressTextElement.textContent = `${mockProgress.toFixed(1)}%`;
        if (etaTextElement) etaTextElement.textContent = calculateMockETA();
    }
    
    function updateProgressIndicators() {
        // Get all steps
        const steps = ['initialization', 'preparation', 'filming', 'finalization'];
        const currentIndex = steps.indexOf(currentStep);
        
        // Update each step's status
        steps.forEach((step, index) => {
            const stepElement = document.querySelector(`.progress-step[data-step="${step}"]`);
            
            if (stepElement) {
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
            }
        });
    }
    
    function updateControlButtons() {
        const pauseButton = document.getElementById('pause-filming');
        const cancelButton = document.getElementById('cancel-filming');
        
        if (pauseButton && cancelButton) {
            if (isFilmingActive) {
                pauseButton.disabled = false;
                cancelButton.disabled = false;
                
                // Reset pause button text
                pauseButton.innerHTML = '<i class="fas fa-pause"></i> Pause Filming';
            } else {
                pauseButton.disabled = true;
                cancelButton.disabled = true;
            }
        }
    }
    
    function toggleExpandLog() {
        const logContent = document.querySelector('.log-content');
        const expandButton = document.getElementById('expand-log');
        
        if (logContent && expandButton) {
            if (logContent.classList.contains('expanded')) {
                logContent.classList.remove('expanded');
                expandButton.innerHTML = '<i class="fas fa-expand-alt"></i>';
            } else {
                logContent.classList.add('expanded');
                expandButton.innerHTML = '<i class="fas fa-compress-alt"></i>';
            }
        }
    }
    
    function addLogEntry(message) {
        const logContent = document.querySelector('.log-content');
        if (!logContent) return;
        
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
            case 'finalization': return 'Finalization';
            default: return step;
        }
    }
    
    function initializeCharts() {
        // Initialize Chart.js chart for filming statistics
        const ctx = document.getElementById('filmingChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress', 'Pending'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#4CAF50', '#2196F3', '#FFC107']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
});