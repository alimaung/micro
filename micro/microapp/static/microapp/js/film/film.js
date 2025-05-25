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
        
        if (!projectList) {
            console.warn('Project list element not found');
            return;
        }
        
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
            const projectName = project.project_folder_name || project.archive_id;
            const archiveId = project.archive_id;
            const location = project.location || 'Unknown';
            const rollCount = 1; // For now, assume 1 roll per project - this could be calculated from actual roll data
            
            return `
                <div class="project-item" data-id="${project.id}" data-archive-id="${project.archive_id}">
                    <span class="project-name">${projectName}</span>
                    <span class="project-id">${archiveId}</span>
                    <span class="project-location">${location}</span>
                    <span class="project-rolls">${rollCount}</span>
                    <span class="project-status">
                        <span class="status-badge ${statusClass}">${status}</span>
                    </span>
                    <span class="project-actions">
                        ${status === 'Completed' ? `
                            <button class="view-button" title="View details">
                                <i class="fas fa-eye"></i> View
                            </button>
                        ` : `
                            <span class="action-hint">Click to select</span>
                        `}
                    </span>
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
        // Project selection functionality - only highlight, don't proceed
        document.querySelectorAll('.project-item').forEach(item => {
            item.addEventListener('click', function(e) {
                // Don't select if clicking on action buttons
                if (!e.target.closest('.project-actions')) {
                    highlightProject(this);
                }
            });
        });
        
        // Remove individual action buttons since we're using the main select button
        // Keep view button for completed projects
        document.querySelectorAll('.view-button').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                const projectId = this.closest('.project-item').getAttribute('data-id');
                viewProjectDetails(projectId);
            });
        });
    }
    
    // Highlight a project and enable the select button
    function highlightProject(projectItem) {
        // Deselect all projects
        document.querySelectorAll('.project-item').forEach(p => p.classList.remove('selected'));
        
        // Select the current project
        projectItem.classList.add('selected');
        
        // Enable the select project button
        const selectProjectBtn = document.getElementById('select-project-btn');
        if (selectProjectBtn) {
            selectProjectBtn.disabled = false;
        }
        
        // Update project status
        const projectName = projectItem.querySelector('.project-name').textContent;
        const projectStatus = document.getElementById('project-status');
        if (projectStatus) {
            projectStatus.textContent = `Project "${projectName}" highlighted - click Select to continue`;
            projectStatus.className = 'status-indicator';
        }
    }
    
    // Proceed with the selected project (moved from selectProject)
    function proceedWithSelectedProject(projectItem) {
        // Get project data
        const projectName = projectItem.querySelector('.project-name').textContent;
        const projectId = projectItem.getAttribute('data-id');
        const projectArchiveId = projectItem.getAttribute('data-archive-id');
        const projectLocation = projectItem.querySelector('.project-location').textContent;
        
        // Update project info in the roll selection card
        const selectedProjectNameElement = document.getElementById('selected-project-name');
        const selectedProjectIdElement = document.getElementById('selected-project-id');
        const selectedProjectLocationElement = document.getElementById('selected-project-location');
        
        if (selectedProjectNameElement) selectedProjectNameElement.textContent = projectName;
        if (selectedProjectIdElement) selectedProjectIdElement.textContent = projectArchiveId;
        if (selectedProjectLocationElement) selectedProjectLocationElement.textContent = projectLocation;
        
        // Update project status
        const projectStatus = document.getElementById('project-status');
        if (projectStatus) {
            projectStatus.textContent = `Project "${projectName}" selected`;
            projectStatus.className = 'status-indicator success';
        }
        
        // Show roll selection card
        showCard('roll-selection-card');
        
        // Load rolls for this project
        loadProjectRolls(projectId);
        
        // Show toast notification
        showToast('success', 'Project Selected', `Selected project: ${projectName}`);
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
        const completedProjects = allProjects.filter(p => getProjectFilmingStatus(p) === 'Completed').length;
        
        // Update stats safely
        const totalProjectsElement = document.getElementById('total-projects');
        const readyRollsElement = document.getElementById('ready-rolls');
        const completedRollsElement = document.getElementById('completed-rolls');
        
        if (totalProjectsElement) totalProjectsElement.textContent = totalProjects;
        if (readyRollsElement) readyRollsElement.textContent = readyForFilming;
        if (completedRollsElement) completedRollsElement.textContent = completedProjects;
    }
    
    // Filter projects based on search and filter criteria
    function filterProjects() {
        const searchElement = document.getElementById('project-search');
        const statusFilterElement = document.getElementById('project-status-filter');
        
        const searchTerm = searchElement ? searchElement.value.toLowerCase() : '';
        const statusFilter = statusFilterElement ? statusFilterElement.value : 'all';
        
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
            
            return matchesSearch && matchesStatus;
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
        // Start filming button - check if exists
        const startFilmingButton = document.getElementById('start-filming');
        if (startFilmingButton) {
            startFilmingButton.addEventListener('click', function() {
                startFilmingProcess(false);
            });
        }
        
        // Filming control buttons - check if they exist
        const pauseButton = document.getElementById('pause-filming');
        const resumeButton = document.getElementById('resume-filming');
        const cancelButton = document.getElementById('cancel-filming');
        const expandLogButton = document.getElementById('expand-log');
        
        if (pauseButton) pauseButton.addEventListener('click', togglePauseFilming);
        if (resumeButton) resumeButton.addEventListener('click', togglePauseFilming);
        if (cancelButton) cancelButton.addEventListener('click', cancelFilming);
        if (expandLogButton) expandLogButton.addEventListener('click', toggleExpandLog);
        
        // Filter and search - check if they exist
        const projectSearch = document.getElementById('project-search');
        const projectStatusFilter = document.getElementById('project-status-filter');
        const searchButton = document.getElementById('search-button');
        
        if (projectSearch) projectSearch.addEventListener('input', filterProjects);
        if (projectStatusFilter) projectStatusFilter.addEventListener('change', filterProjects);
        if (searchButton) {
            searchButton.addEventListener('click', function() {
                filterProjects();
            });
        }
        
        // Project selection button
        const selectProjectBtn = document.getElementById('select-project-btn');
        if (selectProjectBtn) {
            selectProjectBtn.addEventListener('click', function() {
                const selectedProject = document.querySelector('.project-item.selected');
                if (selectedProject) {
                    proceedWithSelectedProject(selectedProject);
                }
            });
        }
        
        // Roll selection buttons
        const selectRollBtn = document.getElementById('select-roll-btn');
        const backToProjectsBtn = document.getElementById('back-to-projects-btn');
        
        if (selectRollBtn) {
            selectRollBtn.addEventListener('click', function() {
                const selectedRoll = document.querySelector('.roll-card.selected');
                if (selectedRoll) {
                    proceedWithSelectedRoll(selectedRoll);
                }
            });
        }
        
        if (backToProjectsBtn) {
            backToProjectsBtn.addEventListener('click', function() {
                hideCard('roll-selection-card');
                showCard('project-selection-card');
                
                // Reset project selection
                document.querySelectorAll('.project-item').forEach(p => p.classList.remove('selected'));
                const selectProjectBtn = document.getElementById('select-project-btn');
                if (selectProjectBtn) selectProjectBtn.disabled = true;
            });
        }
        
        // Validation checklist items
        const checklistItems = document.querySelectorAll('.checklist-item');
        checklistItems.forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.addEventListener('change', updateValidationStatus);
                item.addEventListener('click', function(e) {
                    if (e.target !== checkbox) {
                        checkbox.checked = !checkbox.checked;
                        updateValidationStatus();
                    }
                });
            }
        });
        
        // Validation actions
        const cancelValidationButton = document.getElementById('cancel-validation');
        const startFilmingValidationButton = document.getElementById('start-filming');
        
        if (cancelValidationButton) {
            cancelValidationButton.addEventListener('click', function() {
                showCard('roll-selection-card');
                hideCard('validation-card');
            });
        }
        
        // Completion actions
        const filmAnotherRollButton = document.getElementById('film-another-roll');
        const finishSessionButton = document.getElementById('finish-session');
        
        if (filmAnotherRollButton) {
            filmAnotherRollButton.addEventListener('click', function() {
                resetToRollSelection();
            });
        }
        
        if (finishSessionButton) {
            finishSessionButton.addEventListener('click', function() {
                resetToProjectSelection();
            });
        }
    }
    
    function updateFilmNumber() {
        const selectedProject = document.querySelector('.project-item.selected');
        if (selectedProject) {
            const projectId = selectedProject.getAttribute('data-id');
            // Default to 16mm since we don't have film type selection in current UI
            const filmNumber = `F-16-${projectId.toString().padStart(4, '0')}`;
            const filmNumberElement = document.getElementById('film-number');
            if (filmNumberElement) {
                filmNumberElement.textContent = filmNumber;
            }
        }
    }
    
    function startFilmingProcess(isRecovery) {
        // Hide validation card and show filming process card
        hideCard('validation-card');
        showCard('filming-process-card');
        
        // Get selected roll information
        const selectedRoll = document.querySelector('.roll-card.selected');
        if (!selectedRoll && !isRecovery) {
            showToast('error', 'No Roll Selected', 'Please select a roll to film');
            return;
        }
        
        // Reset progress to initial state
        if (!isRecovery) {
            currentStep = 'initialization';
            mockProgress = 0;
            processedDocuments = 0;
            
            // Get document count from selected roll
            if (selectedRoll) {
                const documentCount = selectedRoll.querySelector('.roll-detail-value').textContent;
                totalDocuments = parseInt(documentCount) || 100;
            }
            
            // Reset progress indicators
            document.querySelectorAll('.progress-step').forEach(step => {
                step.classList.remove('completed', 'active');
                if (step.getAttribute('data-step') === 'initialization') {
                    step.classList.add('active');
                }
            });
            
            // Add initial log entries
            addLogEntry('Initializing SMA application...');
            
            // Start the mock filming process
            setTimeout(() => {
                addLogEntry('Application started successfully');
                advanceToNextStep(); // Advance to preparation
                
                setTimeout(() => {
                    addLogEntry('Selecting template: Portrait - 16mm.TPL');
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
                step.classList.remove('completed', 'active');
                
                const stepName = step.getAttribute('data-step');
                if (stepName === 'initialization' || stepName === 'preparation') {
                    step.classList.add('completed');
                } else if (stepName === 'filming') {
                    step.classList.add('active');
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
        updateActivityLabel();
        
        // Update filming status
        const filmingStatus = document.getElementById('filming-status');
        if (filmingStatus) {
            filmingStatus.textContent = 'Processing documents...';
            filmingStatus.className = 'status-indicator filming';
        }
        
        // Set active filming state
        isFilmingActive = true;
        
        // Update button states
        updateControlButtons();
        
        // Show toast notification
        showToast('info', 'Filming Started', 'Roll filming process has begun');
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
                currentStepElement.classList.remove('active');
                currentStepElement.classList.add('completed');
            }
            
            // Move to next step
            currentStep = steps[currentIndex + 1];
            const nextStepElement = document.querySelector(`.progress-step[data-step="${currentStep}"]`);
            if (nextStepElement) {
                nextStepElement.classList.add('active');
            }
            
            // Update activity label
            updateActivityLabel();
            
            // Add log entry for the step transition
            addLogEntry(`Starting ${formatStepName(currentStep)} phase`);
            
            // If we reached the end, show completion
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
                
                // Show completion after a delay
                setTimeout(() => {
                    showCompletionCard();
                }, 2000);
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
                    stepElement.classList.remove('active');
                    stepElement.classList.add('completed');
                } else if (index === currentIndex) {
                    // Current step is in progress
                    stepElement.classList.remove('completed');
                    stepElement.classList.add('active');
                } else {
                    // Future steps are neither
                    stepElement.classList.remove('completed', 'active');
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
    
    // Card management functions
    function showCard(cardId) {
        const card = document.getElementById(cardId);
        if (card) {
            card.style.display = 'block';
            card.classList.remove('hidden');
            // Smooth scroll to the card
            setTimeout(() => {
                card.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }
    
    function hideCard(cardId) {
        const card = document.getElementById(cardId);
        if (card) {
            card.style.display = 'none';
            card.classList.add('hidden');
        }
    }
    
    // Validation functions
    function updateValidationStatus() {
        const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
        const checkedCount = document.querySelectorAll('.checklist-item input[type="checkbox"]:checked').length;
        const totalCount = checkboxes.length;
        
        // Update checklist item states
        checkboxes.forEach(checkbox => {
            const item = checkbox.closest('.checklist-item');
            if (item) {
                if (checkbox.checked) {
                    item.classList.add('checked');
                } else {
                    item.classList.remove('checked');
                }
            }
        });
        
        // Update start filming button state
        const startButton = document.getElementById('start-filming');
        if (startButton) {
            startButton.disabled = checkedCount < totalCount;
        }
        
        // Update validation status
        const validationStatus = document.getElementById('validation-status');
        if (validationStatus) {
            if (checkedCount === totalCount) {
                validationStatus.textContent = 'All checks completed - Ready to start filming';
                validationStatus.className = 'status-indicator success';
            } else {
                validationStatus.textContent = `${checkedCount}/${totalCount} checks completed`;
                validationStatus.className = 'status-indicator warning';
            }
        }
    }
    
    // Reset functions
    function resetToRollSelection() {
        hideCard('completion-card');
        hideCard('filming-process-card');
        hideCard('validation-card');
        showCard('roll-selection-card');
        
        // Reset filming state
        isFilmingActive = false;
        currentStep = 'initialization';
        mockProgress = 0;
        processedDocuments = 0;
        
        // Clear any intervals
        if (mockInterval) {
            clearInterval(mockInterval);
            mockInterval = null;
        }
    }
    
    function resetToProjectSelection() {
        hideCard('completion-card');
        hideCard('filming-process-card');
        hideCard('validation-card');
        hideCard('roll-selection-card');
        showCard('project-selection-card');
        
        // Reset all state
        isFilmingActive = false;
        currentStep = 'initialization';
        mockProgress = 0;
        processedDocuments = 0;
        
        // Clear any intervals
        if (mockInterval) {
            clearInterval(mockInterval);
            mockInterval = null;
        }
        
        // Deselect all projects
        document.querySelectorAll('.project-item').forEach(p => p.classList.remove('selected'));
    }
    
    // Toast notification system
    function showToast(type, title, message, duration = 5000) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="toast-icon ${iconMap[type] || iconMap.info}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
            <div class="toast-progress" style="width: 100%"></div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after duration
        if (duration > 0) {
            const progressBar = toast.querySelector('.toast-progress');
            if (progressBar) {
                progressBar.style.transition = `width ${duration}ms linear`;
                setTimeout(() => {
                    progressBar.style.width = '0%';
                }, 10);
            }
            
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.classList.add('fade-out');
                    setTimeout(() => {
                        toast.remove();
                    }, 300);
                }
            }, duration);
        }
    }
    
    // Load rolls for a project
    async function loadProjectRolls(projectId) {
        const rollsGrid = document.getElementById('rolls-grid');
        if (!rollsGrid) return;
        
        // Show loading state
        rollsGrid.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading rolls...</p>
            </div>
        `;
        
        try {
            const response = await fetch(`/api/projects/${projectId}/rolls/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            console.log('API Response status:', response.status);
            console.log('API Response headers:', response.headers);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error response:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            console.log('API Response data:', data);
            
            let rolls = [];
            
            // Handle both API response formats
            if (data.status === 'success') {
                // This is from views.get_project_rolls (roll_views.py)
                rolls = data.rolls.map(roll => ({
                    id: roll.id,
                    filmNumber: roll.film_number,
                    filmType: roll.film_type,
                    status: roll.status, // This comes from the API logic
                    documentCount: roll.document_count,
                    pageCount: roll.pages_used || 0,
                    progress: roll.filming_progress_percent || 0,
                    outputDir: roll.output_directory || '',
                    dirExists: roll.output_directory_exists || false,
                    capacity: roll.capacity,
                    pagesRemaining: roll.pages_remaining,
                    filmingStatus: roll.filming_status,
                    // Add temp roll information
                    filmNumberSource: roll.film_number_source,
                    sourceTempRoll: roll.source_temp_roll,
                    isNewRoll: roll.is_new_roll,
                    temp_roll_instructions: roll.temp_roll_instructions
                }));
            } else if (data.rolls) {
                // This is from api.get_rolls (api.py) - current format
                rolls = data.rolls.map(roll => ({
                    id: roll.id,
                    filmNumber: roll.film_number,
                    filmType: roll.film_type,
                    status: roll.status === 'active' ? 'ready' : roll.status, // Convert status
                    documentCount: 0, // Not available in this API
                    pageCount: roll.pages_used || 0,
                    progress: 0, // Not available in this API
                    outputDir: '', // Not available in this API
                    dirExists: false, // Not available in this API
                    capacity: roll.capacity,
                    pagesRemaining: roll.pages_remaining,
                    filmingStatus: 'ready' // Default status
                }));
            } else {
                throw new Error('Invalid API response format');
            }
            
            console.log('Processed rolls:', rolls);
            displayRolls(rolls);
        } catch (error) {
            console.error('Error loading rolls:', error);
            console.error('Response details:', error.response);
            rollsGrid.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load rolls: ${error.message}</p>
                    <button class="retry-button" data-project-id="${projectId}">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
            
            // Add event listener to retry button
            const retryButton = rollsGrid.querySelector('.retry-button');
            if (retryButton) {
                retryButton.addEventListener('click', function() {
                    const projectId = this.getAttribute('data-project-id');
                    loadProjectRolls(projectId);
                });
            }
            
            showToast('error', 'Load Error', `Failed to load rolls: ${error.message}`);
        }
    }
    
    // Display rolls in the grid
    function displayRolls(rolls) {
        const rollsGrid = document.getElementById('rolls-grid');
        if (!rollsGrid) return;
        
        // Store roll data globally for validation card access
        window.currentRollData = rolls;
        
        if (rolls.length === 0) {
            rollsGrid.innerHTML = `
                <div class="rolls-empty-state">
                    <i class="fas fa-film"></i>
                    <h3>No Rolls Found</h3>
                    <p>This project doesn't have any rolls configured for filming.</p>
                </div>
            `;
            return;
        }
        
        rollsGrid.innerHTML = rolls.map(roll => {
            const statusClass = roll.status;
            const progressPercent = roll.progress || 0;
            
            return `
                <div class="roll-card ${statusClass}" data-roll-id="${roll.id}" data-status="${roll.status}">
                    ${roll.status === 'filming' ? `
                        <div class="filming-progress-indicator">
                            <div class="filming-progress-fill" style="width: ${progressPercent}%"></div>
                        </div>
                    ` : ''}
                    
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">${roll.filmNumber}</div>
                            <div class="roll-film-type">${roll.filmType}</div>
                        </div>
                        <div class="roll-status-badge ${statusClass}">
                            ${roll.status.replace('-', ' ')}
                        </div>
                    </div>
                    
                    <div class="roll-details">
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Documents:</span>
                            <span class="roll-detail-value">${roll.documentCount}</span>
                        </div>
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Pages:</span>
                            <span class="roll-detail-value">${roll.pageCount}</span>
                        </div>
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Output:</span>
                            <span class="roll-detail-value">${roll.outputDir}</span>
                        </div>
                        <div class="directory-status ${roll.dirExists ? 'exists' : 'missing'}">
                            <i class="fas ${roll.dirExists ? 'fa-check' : 'fa-times'}"></i>
                            Directory ${roll.dirExists ? 'exists' : 'missing'}
                        </div>
                    </div>
                    
                    ${roll.status === 'filming' ? `
                        <div class="roll-progress">
                            <div class="roll-progress-label">
                                <span>Progress</span>
                                <span>${progressPercent}%</span>
                            </div>
                            <div class="roll-progress-bar">
                                <div class="roll-progress-fill" style="width: ${progressPercent}%"></div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="roll-actions">
                        ${roll.status === 'ready' ? `
                            <span class="action-hint">Click to select</span>
                        ` : `
                            <span class="status-text ${roll.status}">
                                <i class="fas ${roll.status === 'completed' ? 'fa-check' : 'fa-exclamation-triangle'}"></i>
                                ${roll.status === 'completed' ? 'Completed' : 'Not Ready'}
                            </span>
                        `}
                        <button class="roll-info-button" title="Roll details">
                            <i class="fas fa-info"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        // Attach event listeners to roll cards
        attachRollEventListeners();
    }
    
    // Attach event listeners to roll cards
    function attachRollEventListeners() {
        document.querySelectorAll('.roll-card').forEach(card => {
            const infoButton = card.querySelector('.roll-info-button');
            
            // Only allow selection of ready rolls
            if (card.classList.contains('ready') || card.dataset.status === 'ready') {
                card.addEventListener('click', function(e) {
                    // Don't select if clicking on info button
                    if (!e.target.closest('.roll-info-button')) {
                        highlightRoll(card);
                    }
                });
            }
            
            if (infoButton) {
                infoButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    showRollInfo(card.getAttribute('data-roll-id'));
                });
            }
        });
    }
    
    // Highlight a roll and enable the select button
    function highlightRoll(rollCard) {
        // Deselect all rolls
        document.querySelectorAll('.roll-card').forEach(card => card.classList.remove('selected'));
        
        // Select the current roll
        rollCard.classList.add('selected');
        
        // Enable the select roll button
        const selectRollBtn = document.getElementById('select-roll-btn');
        if (selectRollBtn) {
            selectRollBtn.disabled = false;
        }
        
        // Update roll status
        const filmNumber = rollCard.querySelector('.roll-film-number').textContent;
        const rollStatus = document.getElementById('roll-status');
        if (rollStatus) {
            rollStatus.textContent = `Roll ${filmNumber} highlighted - click Select to continue`;
            rollStatus.className = 'status-indicator';
        }
    }
    
    // Proceed with the selected roll (renamed from selectRoll)
    function proceedWithSelectedRoll(rollCard) {
        // Get roll data
        const rollId = rollCard.getAttribute('data-roll-id');
        const filmNumber = rollCard.querySelector('.roll-film-number').textContent;
        const filmType = rollCard.querySelector('.roll-film-type').textContent;
        const documentCount = rollCard.querySelector('.roll-detail-value').textContent;
        const outputDir = rollCard.querySelectorAll('.roll-detail-value')[2].textContent;
        const dirExists = rollCard.querySelector('.directory-status').classList.contains('exists');
        
        // Get the full roll data from the processed rolls
        const rollData = window.currentRollData ? window.currentRollData.find(r => r.id == rollId) : null;
        
        // Update validation card with roll info
        updateValidationCard(rollId, filmNumber, filmType, documentCount, outputDir, dirExists, rollData);
        
        // Show validation card
        showCard('validation-card');
        
        // Update roll status
        const rollStatus = document.getElementById('roll-status');
        if (rollStatus) {
            rollStatus.textContent = `Roll ${filmNumber} selected for validation`;
            rollStatus.className = 'status-indicator success';
        }
        
        // Show toast notification
        showToast('success', 'Roll Selected', `Selected roll: ${filmNumber}`);
    }
    
    // Update validation card with roll information
    function updateValidationCard(rollId, filmNumber, filmType, documentCount, outputDir, dirExists, rollData) {
        // Update validation summary
        const elements = {
            'validation-film-number': filmNumber,
            'validation-film-type': filmType,
            'validation-document-count': documentCount,
            'validation-page-count': parseInt(documentCount) * 2, // Assume 2 pages per document
            'validation-output-dir': outputDir,
            'validation-dir-status': dirExists ? 'Exists' : 'Missing'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                if (id === 'validation-dir-status') {
                    element.className = `summary-value ${dirExists ? 'success' : 'error'}`;
                }
            }
        });
        
        // Update roll source information
        const rollSourceElement = document.getElementById('validation-roll-source');
        if (rollSourceElement && rollData && rollData.temp_roll_instructions) {
            const instructions = rollData.temp_roll_instructions;
            if (instructions.use_temp_roll) {
                rollSourceElement.textContent = `Temp Roll #${instructions.temp_roll_id}`;
                rollSourceElement.className = 'summary-value temp-roll';
            } else {
                rollSourceElement.textContent = 'New Roll';
                rollSourceElement.className = 'summary-value new-roll';
            }
        } else {
            if (rollSourceElement) {
                rollSourceElement.textContent = 'New Roll';
                rollSourceElement.className = 'summary-value new-roll';
            }
        }
        
        // Add highlighting to film type if using temp roll
        const filmTypeElement = document.getElementById('validation-film-type');
        if (filmTypeElement && rollData && rollData.temp_roll_instructions && rollData.temp_roll_instructions.use_temp_roll) {
            filmTypeElement.className = 'summary-value temp-roll';
        } else if (filmTypeElement) {
            filmTypeElement.className = 'summary-value';
        }
        
        // Update camera head instruction
        const cameraHeadInstruction = document.getElementById('camera-head-instruction');
        if (cameraHeadInstruction) {
            cameraHeadInstruction.textContent = `Use ${filmType} camera head`;
        }
        
        // Update temp roll instruction based on roll data
        const tempRollInstruction = document.getElementById('temp-roll-instruction');
        const tempRollDetails = document.getElementById('temp-roll-details');
        
        if (rollData && rollData.temp_roll_instructions) {
            const instructions = rollData.temp_roll_instructions;
            if (tempRollInstruction) {
                tempRollInstruction.textContent = instructions.instruction;
            }
            if (tempRollDetails) {
                tempRollDetails.textContent = instructions.details;
                // Add visual indicator for temp roll vs new roll
                if (instructions.use_temp_roll) {
                    tempRollDetails.style.color = 'var(--color-warning)';
                    tempRollDetails.style.fontWeight = 'bold';
                } else {
                    tempRollDetails.style.color = 'var(--color-text-secondary)';
                    tempRollDetails.style.fontWeight = 'normal';
                }
            }
        } else {
            // Fallback if no roll data
            if (tempRollInstruction) {
                tempRollInstruction.textContent = `Insert new ${filmType} film roll`;
            }
            if (tempRollDetails) {
                tempRollDetails.textContent = `New roll with standard capacity`;
            }
        }
        
        // Reset validation checklist
        document.querySelectorAll('.checklist-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        updateValidationStatus();
    }
    
    // Show roll information
    function showRollInfo(rollId) {
        // For now, show an alert. In the future, this could open a modal
        showToast('info', 'Roll Information', `Detailed information for roll ID: ${rollId}`);
    }
    
    // Show completion card
    function showCompletionCard() {
        // Hide filming process card and show completion card
        hideCard('filming-process-card');
        showCard('completion-card');
        
        // Get selected roll information
        const selectedRoll = document.querySelector('.roll-card.selected');
        const filmNumber = selectedRoll ? selectedRoll.querySelector('.roll-film-number').textContent : 'Unknown';
        
        // Update completion card with results
        const completedFilmNumber = document.getElementById('completed-film-number');
        const completionDocuments = document.getElementById('completion-documents');
        const completionPages = document.getElementById('completion-pages');
        const completionDuration = document.getElementById('completion-duration');
        
        if (completedFilmNumber) completedFilmNumber.textContent = filmNumber;
        if (completionDocuments) completionDocuments.textContent = totalDocuments;
        if (completionPages) completionPages.textContent = totalDocuments * 2; // Assume 2 pages per document
        if (completionDuration) completionDuration.textContent = '15:32'; // Mock duration
        
        // Update completion status
        const completionStatus = document.getElementById('completion-status');
        if (completionStatus) {
            completionStatus.textContent = 'Roll filming completed successfully';
            completionStatus.className = 'status-indicator success';
        }
        
        // Show success toast
        showToast('success', 'Filming Complete', `Roll ${filmNumber} has been successfully filmed`);
        
        // Update roll status in the background (for when user goes back)
        if (selectedRoll) {
            selectedRoll.classList.remove('ready');
            selectedRoll.classList.add('completed');
            const statusBadge = selectedRoll.querySelector('.roll-status-badge');
            if (statusBadge) {
                statusBadge.textContent = 'completed';
                statusBadge.className = 'roll-status-badge completed';
            }
        }
    }
});