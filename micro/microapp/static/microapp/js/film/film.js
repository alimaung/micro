document.addEventListener('DOMContentLoaded', function() {
    // Main state variables
    let currentStep = 'initialization';
    let isFilmingActive = false;
    let currentSessionId = null;
    let websocketClient = null;
    let allProjects = []; // Store all loaded projects
    let filteredProjects = []; // Store filtered projects
    let currentProjectId = null;
    let currentRollId = null;
    let sessionStartTime = null;
    
    // Initialize the application
    initializeApp();
    
    async function initializeApp() {
        console.log('🎬 Initializing SMA Filming Interface...');
        
        // Check for active sessions FIRST before showing any UI
        const activeSessions = await checkForActiveSessions();
        
        if (activeSessions && activeSessions.length > 0) {
            console.log('🔄 Found active session, restoring automatically...');
            // Automatically restore the active session
            await restoreActiveSession(activeSessions[0]);
        } else {
            console.log('📋 No active sessions found, showing project selection...');
            // Normal initialization - show project selection
            await loadProjects();
            showCard('project-selection-card');
        }
        
    // Initialize event handlers
    initializeEventHandlers();
        
        // Initialize WebSocket connection
        initializeWebSocket();
    
    // Initialize interface
        updateQuickStats();
        
        // Disable start filming button initially (if in normal mode)
        const startFilmingButton = document.getElementById('start-filming');
        if (startFilmingButton && !isFilmingActive) {
            startFilmingButton.disabled = true;
        }
        
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
        
        // Add navigation warning for active sessions
        setupNavigationWarning();
        
        // Test log entry to verify log system is working
        setTimeout(() => {
            addLogEntry('SMA Filming Interface initialized successfully', 'info');
            console.log('Test log entry added');
        }, 1000);
    }
    
    // Setup navigation warning to prevent accidental page leaving during filming
    function setupNavigationWarning() {
        window.addEventListener('beforeunload', function(e) {
            if (isFilmingActive && currentSessionId) {
                const message = 'You have an active filming session. Are you sure you want to leave? The session will continue running in the background.';
                e.preventDefault();
                e.returnValue = message;
                return message;
            }
        });
    }
    
    // Initialize WebSocket connection for real-time updates
    function initializeWebSocket() {
        if (typeof WebSocketClient !== 'undefined') {
            websocketClient = new WebSocketClient();
            websocketClient.connect();
            
            // Set up WebSocket event handlers
            websocketClient.onMessage = handleWebSocketMessage;
            websocketClient.onConnect = () => {
                console.log('WebSocket connected for filming interface');
            };
            websocketClient.onDisconnect = () => {
                console.log('WebSocket disconnected');
            };
        }
    }
    
    // Handle WebSocket messages for real-time updates
    function handleWebSocketMessage(event) {
        console.log('🔌 WebSocket message received (raw):', event); // Debug logging
        
        // Parse the JSON data from the MessageEvent
        let data;
        try {
            data = JSON.parse(event.data);
            console.log('🔌 Parsed WebSocket data:', data);
        } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error, event.data);
            return;
        }
        
        if (data.type === 'connection_established') {
            console.log('WebSocket connection established:', data.message);
            return;
        }
        
        if (data.type === 'session_joined') {
            console.log('Joined session:', data.session_id);
            return;
        }
        
        if (data.type === 'pong') {
            console.log('WebSocket pong received');
            return;
        }
        
        // Handle SMA-specific messages
        console.log('🔍 Checking session ID:', {
            messageSessionId: data.session_id,
            currentSessionId: currentSessionId,
            messageType: data.type
        });
        
        // For log messages, be more permissive during debugging
        if (data.type === 'sma_log') {
            console.log('📝 Processing sma_log message (bypassing session filter):', data);
            // Handle log entries from SMA process
            const logData = data.log || data.data;
            if (logData) {
                const message = logData.message || 'Unknown log message';
                const level = logData.level || 'info';
                const source = logData.source || 'sma';
                
                console.log('📝 Extracted log data:', { message, level, source });
                
                // Add source prefix for SMA logs
                const displayMessage = source === 'sma_stdout' ? `[SMA] ${message}` : message;
                console.log('📝 Adding log entry:', displayMessage);
                addLogEntry(displayMessage, level);
                
                // Show important logs as notifications
                if (level === 'error' || level === 'critical') {
                    showNotification('error', 'SMA Error', message, 8000);
                } else if (level === 'warning') {
                    showNotification('warning', 'SMA Warning', message, 5000);
                }
            } else {
                console.warn('❌ sma_log message missing log data:', data);
            }
            return; // Early return after handling log
        }
        
        // For other messages, check session ID
        if (!data.session_id || data.session_id !== currentSessionId) {
            console.log('⏭️ Ignoring message for different session');
            return; // Ignore messages for other sessions
        }
        
        switch (data.type) {
            case 'sma_progress':
                updateProgressFromWebSocket(data.progress || data.data);
                break;
            case 'sma_workflow_state':
                updateWorkflowState(data.new_state);
                break;
            case 'sma_status':
                updateWorkflowState(data.status.workflow_state);
                break;
            case 'sma_error':
                // Handle SMA error messages
                const errorData = data.error || data.data;
                if (errorData) {
                    const errorMessage = errorData.message || 'SMA process error occurred';
                    addLogEntry(`[ERROR] ${errorMessage}`, 'error');
                    showNotification('error', 'SMA Process Error', errorMessage, 10000);
                    
                    // Update workflow state to error
                    updateWorkflowState('error');
                    
                    // Show error modal for critical errors or initialization failures
                    if (errorData.critical || errorData.phase === 'initialization' || 
                        errorMessage.toLowerCase().includes('initialization') ||
                        errorMessage.toLowerCase().includes('failed to start') ||
                        errorMessage.toLowerCase().includes('connection') ||
                        errorMessage.toLowerCase().includes('timeout')) {
                        
                        showErrorModal(errorMessage, errorData);
                    }
                }
                break;
            case 'sma_completed':
                // Handle SMA completion messages
                const completionData = data.completion || data.data;
                if (completionData) {
                    const completionMessage = completionData.message || 'SMA process completed successfully';
                    addLogEntry(`[COMPLETED] ${completionMessage}`, 'success');
                    showNotification('success', 'SMA Process Complete', completionMessage, 8000);
                    
                    // Update workflow state to completed
                    updateWorkflowState('completed');
                }
                break;
            case 'session_complete':
                handleSessionComplete(data);
                break;
            case 'session_error':
                handleSessionError(data);
                break;
        }
    }
    
    // Check for active sessions on page load
    async function checkForActiveSessions() {
        try {
            const response = await fetch('/api/sma/active-sessions/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (!response.ok) {
                console.warn('Failed to check for active sessions:', response.status);
                return [];
            }
            
            const data = await response.json();
            
            if (data.success && data.active_sessions) {
                // Filter sessions for current user and prioritize running sessions
                const userSessions = data.active_sessions.filter(session => {
                    // For now, we'll show all sessions since we don't have user context in frontend
                    // In production, you might want to add user filtering on backend
                    return true;
                });
                
                // Prioritize running/paused sessions over completed ones
                const runningSessions = userSessions.filter(session => 
                    ['running', 'paused'].includes(session.status) && session.is_process_active
                );
                
                const completedSessions = userSessions.filter(session => 
                    session.status === 'completed'
                );
                
                // Return running sessions first, then recent completed sessions
                const prioritizedSessions = [...runningSessions, ...completedSessions.slice(0, 1)];
                
                console.log(`Found ${runningSessions.length} running and ${completedSessions.length} completed sessions`);
                return prioritizedSessions;
            }
            
            return [];
            
        } catch (error) {
            console.error('Error checking for active sessions:', error);
            return [];
        }
    }
    
    // Load projects from the SMA API
    async function loadProjects() {
        try {
            showLoadingState();
            
            // Use SMA-specific projects endpoint
            const response = await fetch('/api/sma/projects/', {
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
            
            // Handle the response format from SMA service
            if (data.success) {
                allProjects = data.projects || [];
            } else {
                throw new Error(data.error || 'Failed to load projects');
            }
            
            // Projects are already filtered by SMA service for filming readiness
            filteredProjects = allProjects;
            
            displayProjects(filteredProjects);
            hideLoadingState();
            
        } catch (error) {
            console.error('Error loading projects:', error);
            showErrorState('Failed to load projects. Please try again.');
            showNotification('error', 'Load Error', `Failed to load projects: ${error.message}`);
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
                    <small>Projects need to be processed and have available rolls for SMA filming.</small>
                </div>
            `;
            return;
        }
        
        projectList.innerHTML = projects.map(project => {
            const status = project.filming_status || 'ready';
            const statusClass = getStatusClass(status);
            const projectName = project.name || project.archive_id;
            const archiveId = project.archive_id;
            const location = project.location || 'Unknown';
            const rollCount = project.available_rolls || 0;
            
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
                        ${status === 'completed' ? `
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
                (project.name && project.name.toLowerCase().includes(searchTerm)) ||
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
        
        if (pauseButton) pauseButton.addEventListener('click', pauseSession);
        if (resumeButton) resumeButton.addEventListener('click', resumeSession);
        if (cancelButton) cancelButton.addEventListener('click', cancelSession);
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
        
        // Get selected project and roll information
        const selectedProject = document.querySelector('.project-item.selected');
        const selectedRoll = document.querySelector('.roll-card.selected');
        
        if (!selectedProject || !selectedRoll) {
            showNotification('error', 'Selection Required', 'Please select a project and roll');
            return;
        }
        
        currentProjectId = selectedProject.getAttribute('data-id');
        currentRollId = selectedRoll.getAttribute('data-roll-id');
        
        // Start real SMA filming session
        startSMAFilmingSession(isRecovery);
    }
    
    // Start real SMA filming session
    async function startSMAFilmingSession(isRecovery = false) {
        try {
            // Get film type from validation card
            const filmType = document.getElementById('validation-film-type').textContent || '16mm';
            
            // Prepare request data
            const requestData = {
                project_id: parseInt(currentProjectId),
                roll_id: parseInt(currentRollId),
                film_type: filmType,
                recovery: isRecovery
            };
            
            // Add initial log entry
            addLogEntry('Starting SMA filming session...', 'info');
            
            // Call SMA filming API
            const response = await fetch('/api/sma/filming/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Session started successfully
                currentSessionId = data.session_id;
                sessionStartTime = new Date();
                isFilmingActive = true;
                
                // Update session info
                document.getElementById('current-session-id').textContent = currentSessionId;
                document.getElementById('session-start-time').textContent = sessionStartTime.toLocaleTimeString();
                
                // Subscribe to WebSocket updates for this session
                if (websocketClient) {
                    websocketClient.subscribeToSession(currentSessionId);
                }
                
                // Update UI
                updateControlButtons();
                addLogEntry(`Session ${currentSessionId} started successfully`, 'info');
                addLogEntry(`Project: ${data.project_name || 'Unknown'}, Roll: ${data.roll_number || 'Unknown'}`, 'info');
                
                // Start session monitoring
                startSessionMonitoring();
                
                showNotification('success', 'Session Started', `Filming session ${currentSessionId} started`);
                
            } else {
                // Handle errors
                if (data.existing_session) {
                    // Show recovery options
                    showRecoveryModal(data.session_id);
                } else {
                    throw new Error(data.error || 'Failed to start filming session');
                }
            }
            
        } catch (error) {
            console.error('Error starting filming session:', error);
            addLogEntry(`Error starting session: ${error.message}`, 'error');
            
            // Reset UI state
            isFilmingActive = false;
        updateControlButtons();
        
            // Show error modal for initialization failures
            showErrorModal(error.message, { error: error.message, phase: 'initialization' });
        }
    }
    
    // Start monitoring the filming session
    function startSessionMonitoring() {
        // Update session duration every second
        setInterval(() => {
            if (sessionStartTime && isFilmingActive) {
                const duration = new Date() - sessionStartTime;
                const hours = Math.floor(duration / 3600000);
                const minutes = Math.floor((duration % 3600000) / 60000);
                const seconds = Math.floor((duration % 60000) / 1000);
                
                const durationStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                document.getElementById('session-duration').textContent = durationStr;
            }
        }, 1000);
        
        // Poll session status every 5 seconds as backup to WebSocket
        setInterval(async () => {
            if (currentSessionId && isFilmingActive) {
                await updateSessionStatus();
            }
        }, 5000);
    }
    
    // Update session status from API
    async function updateSessionStatus() {
        try {
            const response = await fetch(`/api/sma/session/${currentSessionId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    updateProgressFromAPI(data.status);
                }
            }
        } catch (error) {
            console.error('Error updating session status:', error);
        }
    }
    
    // Update progress from WebSocket message
    function updateProgressFromWebSocket(data) {
        updateProgressDisplay(data.progress_percent, data.processed_documents, data.total_documents);
        
        if (data.eta) {
            document.querySelector('.eta-text').textContent = `ETA: ${data.eta}`;
        }
    }
    
    // Update progress from API response
    function updateProgressFromAPI(status) {
        updateProgressDisplay(status.progress_percent, status.processed_documents, status.total_documents);
        
        // Update workflow state
        if (status.workflow_state !== currentStep) {
            updateWorkflowState(status.workflow_state);
        }
        
        // Check if session is complete
        if (status.status === 'completed') {
            handleSessionComplete(status);
        } else if (status.status === 'failed') {
            handleSessionError(status);
        }
    }
    
    // Update progress display
    function updateProgressDisplay(progressPercent, processedDocs, totalDocs) {
        // Update progress bar
        const progressBar = document.querySelector('.progress-bar-fill');
        const progressText = document.querySelector('.progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${progressPercent}%`;
        }
        if (progressText) {
            progressText.textContent = `${progressPercent.toFixed(1)}%`;
        }
        
        // Update document counters
        const processedElement = document.getElementById('processed-docs');
        const totalElement = document.getElementById('total-docs');
        const progressDocsElement = document.getElementById('progress-documents');
        
        if (processedElement) processedElement.textContent = processedDocs;
        if (totalElement) totalElement.textContent = totalDocs;
        if (progressDocsElement) progressDocsElement.textContent = `${processedDocs} / ${totalDocs} documents`;
    }
    
    function updateWorkflowState(state) {
        currentStep = state;
        
        // Update progress indicators
        const steps = ['initialization', 'preparation', 'filming', 'finalization'];
        const currentIndex = steps.indexOf(currentStep);
        
        steps.forEach((step, index) => {
            const stepElement = document.querySelector(`.progress-step[data-step="${step}"]`);
            
            if (stepElement) {
                if (index < currentIndex) {
                    stepElement.classList.remove('active');
                    stepElement.classList.add('completed');
                } else if (index === currentIndex) {
                    stepElement.classList.remove('completed');
                    stepElement.classList.add('active');
                } else {
                    stepElement.classList.remove('completed', 'active');
                }
            }
        });
        
        // Update activity label
        updateActivityLabel();
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
    
    function handleSessionComplete(data) {
        isFilmingActive = false;
        addLogEntry('Filming session completed successfully', 'info');
        showNotification('success', 'Session Complete', 'Filming session has been completed');
        
        // Update final progress
        updateProgressDisplay(100, data.total_documents, data.total_documents);
        
        // Show completion card
        setTimeout(() => {
            showCompletionCard(data);
        }, 2000);
    }
    
    function handleSessionError(data) {
        isFilmingActive = false;
        const errorMessage = data.error_message || data.error || 'Unknown error occurred';
        
        addLogEntry(`Session failed: ${errorMessage}`, 'error');
        showNotification('error', 'Session Failed', `Filming session failed: ${errorMessage}`);
        updateControlButtons();
        
        // Show error modal with retry option for initialization failures
        showErrorModal(errorMessage, data);
    }
    
    // Show error modal with retry functionality
    function showErrorModal(errorMessage, errorData) {
        // Create and show error modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay error-modal';
        modal.innerHTML = `
            <div class="modal-content error-content">
                <div class="error-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>SMA Process Failed</h3>
                </div>
                <div class="error-body">
                    <p class="error-message">${errorMessage}</p>
                    <div class="error-details">
                        <p><strong>What happened:</strong> The SMA filming process encountered an error and could not continue.</p>
                        <p><strong>What you can do:</strong></p>
                        <ul>
                            <li>Check that the SMA machine is properly connected and powered on</li>
                            <li>Verify that the film is properly inserted and aligned</li>
                            <li>Ensure the output directory is accessible</li>
                            <li>Try starting the process again</li>
                        </ul>
                    </div>
                </div>
                <div class="modal-actions">
                    <button id="retry-process-btn" class="primary-button">
                        <i class="fas fa-redo"></i> Retry Process
                    </button>
                    <button id="back-to-validation-btn" class="secondary-button">
                        <i class="fas fa-arrow-left"></i> Back to Validation
                    </button>
                    <button id="cancel-error-btn" class="secondary-button">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('#retry-process-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            addLogEntry('Retrying SMA process...', 'info');
            // Retry the filming process
            startFilmingProcess(false);
        });
        
        modal.querySelector('#back-to-validation-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            // Go back to validation card
            hideCard('filming-process-card');
            showCard('validation-card');
            // Reset filming state
            isFilmingActive = false;
            currentSessionId = null;
            sessionStartTime = null;
            updateControlButtons();
        });
        
        modal.querySelector('#cancel-error-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            // Reset to project selection
            resetToProjectSelection();
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                resetToProjectSelection();
            }
        });
    }
    
    function showRecoveryModal(sessionId) {
        // Create and show recovery modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Session Recovery</h3>
                <p>An existing filming session was found for this project and roll.</p>
                <p>Session ID: ${sessionId}</p>
                <div class="modal-actions">
                    <button id="recover-session-btn" class="primary-button">
                        <i class="fas fa-undo"></i> Recover Session
                    </button>
                    <button id="force-new-session-btn" class="secondary-button">
                        <i class="fas fa-plus"></i> Start New Session
                    </button>
                    <button id="cancel-recovery-btn" class="secondary-button">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('#recover-session-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            recoverSession(sessionId);
        });
        
        modal.querySelector('#force-new-session-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            startSMAFilmingSession(false); // Force new session
        });
        
        modal.querySelector('#cancel-recovery-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }
    
    async function recoverSession(sessionId) {
        try {
            const response = await fetch(`/api/sma/session/${sessionId}/recover/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            const data = await response.json();
            if (data.success) {
                currentSessionId = sessionId;
                isFilmingActive = true;
                
                // Subscribe to WebSocket updates
                if (websocketClient) {
                    websocketClient.subscribeToSession(currentSessionId);
                }
                
                addLogEntry('Session recovered successfully', 'info');
                showNotification('success', 'Session Recovered', 'Filming session has been recovered');
                
                // Start monitoring
                startSessionMonitoring();
                updateControlButtons();
            } else {
                throw new Error(data.error || 'Failed to recover session');
                }
        } catch (error) {
            console.error('Error recovering session:', error);
            addLogEntry(`Error recovering session: ${error.message}`, 'error');
            showNotification('error', 'Recovery Error', `Failed to recover session: ${error.message}`);
            }
    }
    
    function updateControlButtons() {
        const pauseButton = document.getElementById('pause-filming');
        const resumeButton = document.getElementById('resume-filming');
        const cancelButton = document.getElementById('cancel-filming');
        
        if (pauseButton && resumeButton && cancelButton) {
        if (isFilmingActive) {
            pauseButton.disabled = false;
                resumeButton.disabled = true;
            cancelButton.disabled = false;
        } else {
            pauseButton.disabled = true;
                resumeButton.disabled = false;
            cancelButton.disabled = true;
            }
        }
    }
    
    function addLogEntry(message, level = 'info') {
        console.log('📝 addLogEntry called:', { message, level });
        
        const logContent = document.querySelector('.log-content');
        console.log('📝 Log content element:', logContent);
        
        if (!logContent) {
            console.error('❌ Log content element not found!');
            return;
        }
        
        const now = new Date();
        const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        logEntry.innerHTML = `<span class="timestamp">${timestamp}</span><span class="log-text">${message}</span>`;
        
        console.log('📝 Created log entry element:', logEntry);
        
        logContent.appendChild(logEntry);
        
        // Auto-scroll to bottom to show newest entries
        scrollLogToBottom();
        
        console.log('📝 Log entry added to DOM, total entries:', logContent.children.length);
    }
    
    // Helper function to ensure consistent auto-scrolling
    function scrollLogToBottom() {
        const logContainer = document.querySelector('.log-container');
        if (logContainer) {
            // Use requestAnimationFrame to ensure DOM has updated
            requestAnimationFrame(() => {
                logContainer.scrollTop = logContainer.scrollHeight;
            });
        }
    }
    
    // Notification system
    function showNotification(type, title, message, duration = 5000) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="${iconMap[type] || iconMap.info}"></i>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.add('fade-out');
                    setTimeout(() => {
                        notification.remove();
                    }, 300);
                }
            }, duration);
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
        currentSessionId = null;
        sessionStartTime = null;
        currentStep = 'initialization';
        
        // Disconnect WebSocket session subscription
        if (websocketClient && currentSessionId) {
            websocketClient.unsubscribeFromSession(currentSessionId);
        }
        
        // Clear logs
        const logContent = document.querySelector('.log-content');
        if (logContent) {
            logContent.innerHTML = '';
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
        currentSessionId = null;
        sessionStartTime = null;
        currentStep = 'initialization';
        currentProjectId = null;
        currentRollId = null;
        
        // Disconnect WebSocket session subscription
        if (websocketClient && currentSessionId) {
            websocketClient.unsubscribeFromSession(currentSessionId);
        }
        
        // Deselect all projects
        document.querySelectorAll('.project-item').forEach(p => p.classList.remove('selected'));
        
        // Reset project selection button
        const selectProjectBtn = document.getElementById('select-project-btn');
        if (selectProjectBtn) selectProjectBtn.disabled = true;
        
        // Clear logs
        const logContent = document.querySelector('.log-content');
        if (logContent) {
            logContent.innerHTML = '';
        }
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
    
    // Load rolls for a project using SMA API
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
            // Use SMA-specific rolls endpoint
            const response = await fetch(`/api/sma/project/${projectId}/rolls/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            let rolls = [];
            
            if (data.success) {
                rolls = data.rolls.map(roll => ({
                    id: roll.id,
                    filmNumber: roll.film_number,
                    filmType: roll.film_type,
                    status: roll.filming_status || 'ready',
                    documentCount: roll.document_count || 0,
                    pageCount: roll.pages_used || 0,
                    progress: roll.filming_progress_percent || 0,
                    outputDir: roll.output_directory || '',
                    dirExists: roll.output_directory_exists || false,
                    capacity: roll.capacity,
                    pagesRemaining: roll.pages_remaining,
                    // Enhanced SMA-specific data
                    isAvailable: roll.is_available_for_filming,
                    lastFilmedAt: roll.last_filmed_at,
                    sessionId: roll.current_session_id
                }));
                
                // Debug directory existence issues
                console.log('Roll directory debug info:', data.rolls.map(roll => ({
                    id: roll.id,
                    film_number: roll.film_number,
                    output_directory: roll.output_directory,
                    output_directory_exists: roll.output_directory_exists,
                    debug_info: roll.debug_directory_info
                })));
            } else {
                throw new Error(data.error || 'Failed to load rolls');
            }
            
            displayRolls(rolls);
        } catch (error) {
            console.error('Error loading rolls:', error);
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
            
            showNotification('error', 'Load Error', `Failed to load rolls: ${error.message}`);
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
    function showCompletionCard(data) {
        // Don't hide filming process card - keep it visible so users can see logs
        // hideCard('filming-process-card');
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
        if (completionDocuments) completionDocuments.textContent = data.total_documents || 0;
        if (completionPages) completionPages.textContent = (data.total_documents || 0) * 2; // Assume 2 pages per document
        
        // Calculate duration
        if (sessionStartTime) {
            const duration = new Date() - sessionStartTime;
            const minutes = Math.floor(duration / 60000);
            const seconds = Math.floor((duration % 60000) / 1000);
            if (completionDuration) completionDuration.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Update completion status
        const completionStatus = document.getElementById('completion-status');
        if (completionStatus) {
            completionStatus.textContent = 'Roll filming completed successfully';
            completionStatus.className = 'status-indicator success';
        }
        
        // Update temp roll instructions
        updateTempRollInstructions(data);
        
        // Show success notification
        showNotification('success', 'Filming Complete', `Roll ${filmNumber} has been successfully filmed`);
        
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
        
        // Scroll to completion card but keep filming process visible
        setTimeout(() => {
            document.getElementById('completion-card').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 500);
    }
    
    // Update temp roll instructions based on completion data
    function updateTempRollInstructions(data) {
        const instructionsContainer = document.getElementById('temp-roll-instructions');
        
        if (!instructionsContainer) {
            // Create the instructions container if it doesn't exist
            const completionContent = document.querySelector('.completion-content');
            if (completionContent) {
                const instructionsDiv = document.createElement('div');
                instructionsDiv.id = 'temp-roll-instructions';
                instructionsDiv.className = 'temp-roll-instructions';
                
                // Insert before the completion actions
                const actionsDiv = completionContent.querySelector('.completion-actions');
                if (actionsDiv) {
                    completionContent.insertBefore(instructionsDiv, actionsDiv);
                } else {
                    completionContent.appendChild(instructionsDiv);
                }
            }
        }
        
        const container = document.getElementById('temp-roll-instructions');
        if (!container) return;
        
        // Check if temp roll should be created based on completion data
        const shouldCreateTempRoll = data.temp_roll_info && data.temp_roll_info.create_temp_roll;
        
        if (shouldCreateTempRoll) {
            const tempRollInfo = data.temp_roll_info;
            container.innerHTML = `
                <div class="temp-roll-instruction-card">
                    <div class="instruction-header">
                        <i class="fas fa-cut"></i>
                        <h4>Temp Roll Creation Required</h4>
                    </div>
                    <div class="instruction-content">
                        <p><strong>Cut the tape and create a temporary roll:</strong></p>
                        <ul class="instruction-list">
                            <li><strong>Temp Roll ID:</strong> ${tempRollInfo.temp_roll_id}</li>
                            <li><strong>Remaining Capacity:</strong> ${tempRollInfo.remaining_capacity} pages</li>
                            <li><strong>Film Type:</strong> ${tempRollInfo.film_type}</li>
                        </ul>
                        <div class="instruction-note">
                            <i class="fas fa-info-circle"></i>
                            This temp roll can be used for future filming sessions.
                        </div>
                    </div>
                </div>
            `;
        } else {
            // No temp roll needed - discard the rest
            container.innerHTML = `
                <div class="temp-roll-instruction-card discard">
                    <div class="instruction-header">
                        <i class="fas fa-trash-alt"></i>
                        <h4>Film Roll Complete</h4>
                    </div>
                    <div class="instruction-content">
                        <p><strong>Cut the tape and discard the remaining film.</strong></p>
                        <div class="instruction-note">
                            <i class="fas fa-check-circle"></i>
                            This roll has been fully utilized - no temp roll needed.
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    // Control functions for filming session
    async function pauseSession() {
        if (!currentSessionId || !isFilmingActive) return;
        
        try {
            const response = await fetch(`/api/sma/session/${currentSessionId}/pause/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            const data = await response.json();
            if (data.success) {
                addLogEntry('Session paused by user', 'info');
                showNotification('info', 'Session Paused', 'Filming session has been paused');
                updateControlButtons();
            } else {
                throw new Error(data.error || 'Failed to pause session');
            }
        } catch (error) {
            console.error('Error pausing session:', error);
            addLogEntry(`Error pausing session: ${error.message}`, 'error');
            showNotification('error', 'Pause Error', `Failed to pause session: ${error.message}`);
        }
    }
    
    async function resumeSession() {
        if (!currentSessionId) return;
        
        try {
            const response = await fetch(`/api/sma/session/${currentSessionId}/resume/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            const data = await response.json();
            if (data.success) {
                addLogEntry('Session resumed by user', 'info');
                showNotification('info', 'Session Resumed', 'Filming session has been resumed');
                updateControlButtons();
            } else {
                throw new Error(data.error || 'Failed to resume session');
            }
        } catch (error) {
            console.error('Error resuming session:', error);
            addLogEntry(`Error resuming session: ${error.message}`, 'error');
            showNotification('error', 'Resume Error', `Failed to resume session: ${error.message}`);
        }
    }
    
    async function cancelSession() {
        if (!currentSessionId || !isFilmingActive) return;
        
        if (!confirm('Are you sure you want to cancel the filming session? This cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/sma/session/${currentSessionId}/cancel/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            const data = await response.json();
            if (data.success) {
                isFilmingActive = false;
                addLogEntry('Session cancelled by user', 'warning');
                showNotification('warning', 'Session Cancelled', 'Filming session has been cancelled');
                updateControlButtons();
                
                // Reset to project selection
                setTimeout(() => {
                    resetToProjectSelection();
                }, 2000);
            } else {
                throw new Error(data.error || 'Failed to cancel session');
            }
        } catch (error) {
            console.error('Error cancelling session:', error);
            addLogEntry(`Error cancelling session: ${error.message}`, 'error');
            showNotification('error', 'Cancel Error', `Failed to cancel session: ${error.message}`);
        }
    }
    
    function toggleExpandLog() {
        const logContent = document.querySelector('.log-content');
        const logContainer = document.querySelector('.log-container');
        const expandButton = document.getElementById('expand-log');
        
        if (logContent && logContainer && expandButton) {
            if (logContent.classList.contains('expanded')) {
                logContent.classList.remove('expanded');
                logContainer.classList.remove('expanded');
                expandButton.innerHTML = '<i class="fas fa-expand-alt"></i>';
                expandButton.title = 'Expand log';
            } else {
                logContent.classList.add('expanded');
                logContainer.classList.add('expanded');
                expandButton.innerHTML = '<i class="fas fa-compress-alt"></i>';
                expandButton.title = 'Collapse log';
            }
            
            // Ensure we scroll to bottom after expanding/collapsing
            setTimeout(() => {
                logContainer.scrollTop = logContainer.scrollHeight;
            }, 350); // Wait for transition to complete
        }
    }
    
    // Automatically restore an active session
    async function restoreActiveSession(session) {
        try {
            console.log('🔄 Restoring active session:', session.session_id);
            console.log('📊 Session details:', {
                project: session.project_name,
                roll: session.roll_number,
                status: session.status,
                progress: session.progress_percent
            });
            
            // Set global state variables
            currentSessionId = session.session_id;
            currentProjectId = session.project_id;
            currentRollId = session.roll_id;
            isFilmingActive = session.status === 'running';
            sessionStartTime = session.started_at ? new Date(session.started_at) : new Date();
            
            // Hide all selection cards and show filming interface
            hideCard('project-selection-card');
            hideCard('roll-selection-card');
            hideCard('validation-card');
            
            // Determine which card to show based on session status
            if (session.status === 'completed') {
                showCard('completion-card');
                await restoreCompletionState(session);
            } else {
                showCard('filming-process-card');
                await restoreFilmingState(session);
            }
            
            // Load projects in background for potential future use
            await loadProjects();
            
            // Show restoration notification
            showNotification('info', 'Session Restored', 
                `Resumed filming session for ${session.project_name} - ${session.roll_number}`);
            
        } catch (error) {
            console.error('Error restoring session:', error);
            showNotification('error', 'Restoration Error', 
                'Failed to restore session. Starting fresh.');
            
            // Fall back to normal initialization
            await loadProjects();
            showCard('project-selection-card');
        }
    }
    
    // Restore filming interface state
    async function restoreFilmingState(session) {
        // Restore session information display
        const sessionIdElement = document.getElementById('current-session-id');
        const startTimeElement = document.getElementById('session-start-time');
        
        if (sessionIdElement) sessionIdElement.textContent = session.session_id;
        if (startTimeElement && session.started_at) {
            const startTime = new Date(session.started_at);
            startTimeElement.textContent = startTime.toLocaleTimeString();
        }
        
        // Restore progress display
        updateProgressDisplay(
            session.progress_percent || 0,
            session.processed_documents || 0,
            session.total_documents || 0
        );
        
        // Restore workflow state
        updateWorkflowState(session.workflow_state || 'initialization');
        
        // Update control buttons based on session status
        updateControlButtons();
        
        // Subscribe to WebSocket updates for this session
        if (websocketClient) {
            websocketClient.subscribeToSession(currentSessionId);
        }
        
        // Start session monitoring
        startSessionMonitoring();
        
        // Load recent logs
        await loadRecentLogs(session.session_id);
        
        // Add restoration log entry
        addLogEntry(`Session restored - continuing from ${session.progress_percent?.toFixed(1) || 0}% progress`, 'info');
    }
    
    // Restore completion state
    async function restoreCompletionState(session) {
        // Show completion card with session results
        const completedFilmNumber = document.getElementById('completed-film-number');
        const completionDocuments = document.getElementById('completion-documents');
        const completionPages = document.getElementById('completion-pages');
        const completionDuration = document.getElementById('completion-duration');
        
        if (completedFilmNumber) completedFilmNumber.textContent = session.roll_number || 'Unknown';
        if (completionDocuments) completionDocuments.textContent = session.total_documents || 0;
        if (completionPages) completionPages.textContent = (session.total_documents || 0) * 2;
        
        // Calculate and display duration
        if (session.started_at && session.completed_at) {
            const startTime = new Date(session.started_at);
            const endTime = new Date(session.completed_at);
            const duration = endTime - startTime;
            const minutes = Math.floor(duration / 60000);
            const seconds = Math.floor((duration % 60000) / 1000);
            if (completionDuration) {
                completionDuration.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }
        
        // Update completion status
        const completionStatus = document.getElementById('completion-status');
        if (completionStatus) {
            completionStatus.textContent = 'Roll filming completed successfully';
            completionStatus.className = 'status-indicator success';
        }
        
        // Update temp roll instructions for restored session
        if (session.completion_data) {
            updateTempRollInstructions(session.completion_data);
        }
    }
    
    // Load recent logs for restored session
    async function loadRecentLogs(sessionId, limit = 50) {
        try {
            const response = await fetch(`/api/sma/session/${sessionId}/logs/?limit=${limit}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.logs) {
                    // Clear existing logs and add recent ones
                    const logContent = document.querySelector('.log-content');
                    if (logContent) {
                        logContent.innerHTML = '';
                        
                        // Add logs in chronological order
                        data.logs.reverse().forEach(log => {
                            const timestamp = new Date(log.timestamp).toLocaleTimeString();
                            addLogEntryDirect(log.message, log.level, timestamp);
                        });
                        
                        // Scroll to bottom after loading all logs
                        scrollLogToBottom();
                    }
                }
            }
        } catch (error) {
            console.error('Error loading recent logs:', error);
        }
    }
    
    // Helper function to add log entry with custom timestamp
    function addLogEntryDirect(message, level = 'info', timestamp = null) {
        const logContent = document.querySelector('.log-content');
        if (!logContent) return;
        
        if (!timestamp) {
            const now = new Date();
            timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        }
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        logEntry.innerHTML = `<span class="timestamp">${timestamp}</span><span class="log-text">${message}</span>`;
        
        logContent.appendChild(logEntry);
        
        // Auto-scroll to bottom to show newest entries
        scrollLogToBottom();
    }
});