document.addEventListener('DOMContentLoaded', function() {
    // Main state variables
    let currentStep = 'initialization';
    let isFilmingActive = false;
    let filmingSession = null;
    let websocket = null;
    let notificationWebSocket = null;
    let totalDocuments = 0;
    let processedDocuments = 0;
    
    // Database service instance
    const dbService = new DatabaseService();
    
    // Initialize interface
    initializeCharts();
    initializeEventHandlers();
    initializeWebSockets();
    loadProjects();
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

    function initializeEventHandlers() {
        // Project selection functionality
        document.addEventListener('click', function(e) {
            if (e.target.closest('.project-item')) {
                selectProject(e.target.closest('.project-item'));
            }
        });

        // Start filming button
        document.getElementById('start-filming').addEventListener('click', () => startFilmingProcess(false));
        
        // Control buttons
        document.getElementById('pause-filming').addEventListener('click', pauseFilming);
        document.getElementById('resume-filming').addEventListener('click', resumeFilming);
        document.getElementById('cancel-filming').addEventListener('click', cancelFilming);
        
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

    function initializeWebSockets() {
        // Initialize general notification WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        try {
            notificationWebSocket = new WebSocket(wsUrl);
            
            notificationWebSocket.onopen = function(event) {
                console.log('Notification WebSocket connected');
            };
            
            notificationWebSocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleNotificationMessage(data);
            };
            
            notificationWebSocket.onclose = function(event) {
                console.log('Notification WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(initializeWebSockets, 5000);
            };
            
            notificationWebSocket.onerror = function(error) {
                console.error('Notification WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to initialize notification WebSocket:', error);
        }
    }

    function connectSMAWebSocket(sessionId) {
        if (websocket) {
            websocket.close();
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/sma/${sessionId}/`;
        
        try {
            websocket = new WebSocket(wsUrl);
            
            websocket.onopen = function(event) {
                console.log('SMA WebSocket connected for session:', sessionId);
            };
            
            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleSMAMessage(data);
            };
            
            websocket.onclose = function(event) {
                console.log('SMA WebSocket disconnected');
            };
            
            websocket.onerror = function(error) {
                console.error('SMA WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to connect SMA WebSocket:', error);
        }
    }

    function handleSMAMessage(data) {
        switch (data.type) {
            case 'progress_update':
                updateProgressFromWebSocket(data.data);
                break;
            case 'log_entry':
                addLogEntry(data.data.message, data.data.level || 'info');
                break;
            case 'status_change':
                updateSessionStatus(data.data.status);
                break;
            case 'completion':
                handleCompletionFromWebSocket(data.data);
                break;
            default:
                console.log('Unknown SMA message type:', data.type);
        }
    }

    function handleNotificationMessage(data) {
        if (data.type === 'notification') {
            const notification = data.data;
            showToast(notification.message, notification.level || 'info');
        }
    }

    async function loadProjects() {
        try {
            // Load projects with distribution_complete=true filter
            const response = await dbService.listProjects({
                distribution_complete: true
            }, 1, 100); // Load first 100 projects
            
            if (response.status === 'success') {
                displayProjects(response.results);
                updateProjectStats(response.results);
            } else {
                console.error('Failed to load projects:', response.message);
                showToast('Failed to load projects', 'error');
            }
        } catch (error) {
            console.error('Error loading projects:', error);
            showToast('Error loading projects', 'error');
        }
    }

    function displayProjects(projects) {
        const projectList = document.getElementById('project-list');
        if (!projectList) return;
        
        projectList.innerHTML = '';
        
        if (projects.length === 0) {
            projectList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>No projects ready for filming</p>
                    <small>Projects must complete distribution before filming</small>
                </div>
            `;
            return;
        }
        
        projects.forEach(project => {
            const projectItem = document.createElement('div');
            projectItem.className = 'project-item';
            projectItem.setAttribute('data-id', project.id);
            
            projectItem.innerHTML = `
                <div class="project-header">
                    <span class="project-name">${project.project_folder_name}</span>
                    <span class="project-id">${project.archive_id}</span>
                </div>
                <div class="project-details">
                    <span class="project-location">${project.location}</span>
                    <span class="project-type">${project.doc_type}</span>
                    <span class="project-pages">${project.total_pages || 0}</span>
                </div>
                <div class="project-status">
                    <span class="status-badge ready">Ready for Filming</span>
                </div>
            `;
            
            projectList.appendChild(projectItem);
        });
    }

    function updateProjectStats(projects) {
        const stats = {
            total: projects.length,
            totalPages: projects.reduce((sum, p) => sum + (p.total_pages || 0), 0),
            readyForFilming: projects.length
        };
        
        document.getElementById('total-projects').textContent = stats.total;
        document.getElementById('total-pages').textContent = stats.totalPages.toLocaleString();
        document.getElementById('ready-filming').textContent = stats.readyForFilming;
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
            const filmNumber = `F-${filmType}-${projectId.toString().padStart(4, '0')}`;
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

    async function startFilmingProcess(isRecovery) {
        const selectedProject = document.querySelector('.project-item.selected');
        if (!selectedProject) {
            showToast('Please select a project to film', 'warning');
            return;
        }
        
        try {
            const projectId = selectedProject.getAttribute('data-id');
            const filmType = document.querySelector('input[name="film-type"]:checked').value;
            
            // Get project details
            const project = await dbService.getProject(projectId);
            if (project.status !== 'success') {
                throw new Error('Failed to load project details');
            }
            
            // Prepare SMA parameters
            const smaParams = {
                project_id: projectId,
                project_path: project.data.project_path,
                output_dir: project.data.output_dir,
                template: filmType,
                film_number: document.getElementById('film-number').textContent
            };
            
            // Start SMA session
            const response = await fetch('/api/sma/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(smaParams)
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                filmingSession = result.data;
                connectSMAWebSocket(filmingSession.session_id);
                
                // Display the filming process section
                document.getElementById('filming-process-section').style.display = 'block';
                
                // Reset progress to initial state
                currentStep = 'initialization';
                processedDocuments = 0;
                
                // Reset progress indicators
                document.querySelectorAll('.progress-step').forEach(step => {
                    step.classList.remove('completed', 'in-progress');
                    if (step.getAttribute('data-step') === 'initialization') {
                        step.classList.add('in-progress');
                    }
                });
                
                // Add initial log entry
                addLogEntry('SMA session started successfully');
                
                // Update UI for active filming
                isFilmingActive = true;
                updateControlButtons();
                
            } else {
                throw new Error(result.message || 'Failed to start filming session');
            }
            
        } catch (error) {
            console.error('Error starting filming process:', error);
            showToast('Failed to start filming: ' + error.message, 'error');
        }
    }

    async function pauseFilming() {
        if (!filmingSession) return;
        
        try {
            const response = await fetch('/api/sma/control/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    session_id: filmingSession.session_id,
                    action: 'pause'
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                addLogEntry('Filming paused');
                updateControlButtons();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error pausing filming:', error);
            showToast('Failed to pause filming: ' + error.message, 'error');
        }
    }

    async function resumeFilming() {
        if (!filmingSession) return;
        
        try {
            const response = await fetch('/api/sma/control/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    session_id: filmingSession.session_id,
                    action: 'resume'
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                addLogEntry('Filming resumed');
                updateControlButtons();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error resuming filming:', error);
            showToast('Failed to resume filming: ' + error.message, 'error');
        }
    }

    async function cancelFilming() {
        if (!filmingSession) return;
        
        if (!confirm('Are you sure you want to cancel the filming process?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/sma/control/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    session_id: filmingSession.session_id,
                    action: 'cancel'
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                addLogEntry('Filming cancelled');
                resetFilmingInterface();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error cancelling filming:', error);
            showToast('Failed to cancel filming: ' + error.message, 'error');
        }
    }

    function updateProgressFromWebSocket(progressData) {
        processedDocuments = progressData.processed || 0;
        totalDocuments = progressData.total || totalDocuments;
        
        const progressPercent = totalDocuments > 0 ? (processedDocuments / totalDocuments) * 100 : 0;
        
        // Update progress bar
        const progressBar = document.querySelector('.progress-bar-fill');
        if (progressBar) {
            progressBar.style.width = `${progressPercent}%`;
        }
        
        // Update progress text
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${progressData.processed || 0} / ${progressData.total || 0} documents (${progressPercent.toFixed(1)}%)`;
        }
        
        // Update ETA if available
        if (progressData.eta) {
            const etaElement = document.querySelector('.eta-text');
            if (etaElement) {
                etaElement.textContent = `ETA: ${progressData.eta}`;
            }
        }
        
        // Update document counters
        updateDocumentCounters();
        
        // Update progress steps based on percentage
        updateProgressSteps(progressPercent);
    }

    function updateProgressSteps(progressPercent) {
        const steps = document.querySelectorAll('.progress-step');
        
        steps.forEach(step => {
            step.classList.remove('completed', 'in-progress');
        });
        
        if (progressPercent < 10) {
            currentStep = 'initialization';
        } else if (progressPercent < 95) {
            currentStep = 'filming';
        } else {
            currentStep = 'finalization';
        }
        
        // Update step indicators
        steps.forEach(step => {
            const stepName = step.getAttribute('data-step');
            if (stepName === currentStep) {
                step.classList.add('in-progress');
            } else if (shouldStepBeCompleted(stepName, progressPercent)) {
                step.classList.add('completed');
            }
        });
    }

    function shouldStepBeCompleted(stepName, progressPercent) {
        switch (stepName) {
            case 'initialization':
                return progressPercent >= 10;
            case 'preparation':
                return progressPercent >= 15;
            case 'filming':
                return progressPercent >= 95;
            case 'finalization':
                return progressPercent >= 100;
            default:
                return false;
        }
    }

    function updateSessionStatus(status) {
        const statusBadge = document.querySelector('.filming-status');
        if (statusBadge) {
            statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            statusBadge.className = `filming-status ${status}`;
        }
        
        if (status === 'completed') {
            handleCompletionFromWebSocket({ status: 'completed' });
        }
    }

    function handleCompletionFromWebSocket(data) {
        addLogEntry('Filming completed successfully!', 'success');
        isFilmingActive = false;
        updateControlButtons();
        
        // Update UI to show completion
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.remove('in-progress');
            step.classList.add('completed');
        });
        
        // Show completion message
        showToast('Filming completed successfully!', 'success');
        
        // Reload projects to update the list
        setTimeout(() => {
            loadProjects();
            loadRecentFilms();
        }, 2000);
    }

    function updateControlButtons() {
        const startBtn = document.getElementById('start-filming');
        const pauseBtn = document.getElementById('pause-filming');
        const resumeBtn = document.getElementById('resume-filming');
        const cancelBtn = document.getElementById('cancel-filming');
        
        if (isFilmingActive) {
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            resumeBtn.disabled = true;
            cancelBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            pauseBtn.disabled = true;
            resumeBtn.disabled = true;
            cancelBtn.disabled = true;
        }
    }

    function resetFilmingInterface() {
        isFilmingActive = false;
        filmingSession = null;
        currentStep = 'initialization';
        
        // Hide filming process section
        document.getElementById('filming-process-section').style.display = 'none';
        
        // Reset progress indicators
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.remove('completed', 'in-progress');
        });
        
        // Clear log
        const logContent = document.querySelector('.log-content');
        if (logContent) {
            logContent.innerHTML = '';
        }
        
        // Update control buttons
        updateControlButtons();
        
        // Close WebSocket
        if (websocket) {
            websocket.close();
            websocket = null;
        }
    }

    async function loadRecentFilms() {
        try {
            // Load recently completed filming sessions
            const response = await fetch('/api/sma/active-sessions/');
            const result = await response.json();
            
            if (result.status === 'success') {
                displayRecentFilms(result.data.completed || []);
            }
        } catch (error) {
            console.error('Error loading recent films:', error);
        }
    }

    function displayRecentFilms(sessions) {
        const recentFilmsGrid = document.querySelector('.recent-films-grid');
        if (!recentFilmsGrid) return;
        
        recentFilmsGrid.innerHTML = '';
        
        if (sessions.length === 0) {
            recentFilmsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-film"></i>
                    <p>No recent films</p>
                    <small>Completed films will appear here</small>
                </div>
            `;
            return;
        }
        
        sessions.slice(0, 6).forEach(session => { // Show last 6 sessions
            const filmCard = document.createElement('div');
            filmCard.className = 'recent-film';
            
            const completedDate = new Date(session.completed_at).toLocaleDateString();
            const duration = session.duration || 'N/A';
            
            filmCard.innerHTML = `
                <div class="film-header">
                    <span class="film-title">${session.project_name || 'Unknown Project'}</span>
                    <span class="film-date">${completedDate}</span>
                </div>
                <div class="film-details">
                    <div class="film-detail-item">
                        <span class="detail-label">Film #:</span>
                        <span class="detail-value">${session.film_number || 'N/A'}</span>
                    </div>
                    <div class="film-detail-item">
                        <span class="detail-label">Pages:</span>
                        <span class="detail-value">${session.total_documents || 0}</span>
                    </div>
                    <div class="film-detail-item">
                        <span class="detail-label">Type:</span>
                        <span class="detail-value">${session.template || 'N/A'}</span>
                    </div>
                    <div class="film-detail-item">
                        <span class="detail-label">Duration:</span>
                        <span class="detail-value">${duration}</span>
                    </div>
                </div>
                <div class="film-actions">
                    <button class="film-action-button" onclick="viewFilmLog('${session.session_id}')">
                        <i class="fas fa-file-alt"></i> View Log
                    </button>
                    <button class="film-action-button" onclick="viewFilmDetails('${session.session_id}')">
                        <i class="fas fa-info-circle"></i> Details
                    </button>
                </div>
            `;
            
            recentFilmsGrid.appendChild(filmCard);
        });
    }

    // Global functions for film actions
    window.viewFilmLog = async function(sessionId) {
        try {
            const response = await fetch(`/api/sma/logs/${sessionId}/`);
            const result = await response.json();
            
            if (result.status === 'success') {
                showLogModal(result.data.logs);
            } else {
                showToast('Failed to load film log', 'error');
            }
        } catch (error) {
            console.error('Error loading film log:', error);
            showToast('Error loading film log', 'error');
        }
    };

    window.viewFilmDetails = async function(sessionId) {
        try {
            const response = await fetch(`/api/sma/status/${sessionId}/`);
            const result = await response.json();
            
            if (result.status === 'success') {
                showDetailsModal(result.data);
            } else {
                showToast('Failed to load film details', 'error');
            }
        } catch (error) {
            console.error('Error loading film details:', error);
            showToast('Error loading film details', 'error');
        }
    };

    function updateDocumentCounters() {
        const processedEl = document.getElementById('processed-docs');
        const totalEl = document.getElementById('total-docs');
        
        if (processedEl) processedEl.textContent = processedDocuments.toLocaleString();
        if (totalEl) totalEl.textContent = totalDocuments.toLocaleString();
    }

    function addLogEntry(message, level = 'info') {
        const logContent = document.querySelector('.log-content');
        if (!logContent) return;
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        
        const timestamp = new Date().toLocaleTimeString();
        logEntry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-message">${message}</span>
        `;
        
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    }

    function toggleExpandLog() {
        const logContainer = document.querySelector('.log-container');
        if (logContainer) {
            logContainer.classList.toggle('expanded');
        }
    }

    function showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 5000);
    }

    function showLogModal(logs) {
        // Implementation for showing log modal
        console.log('Show log modal:', logs);
    }

    function showDetailsModal(details) {
        // Implementation for showing details modal
        console.log('Show details modal:', details);
    }

    function getCsrfToken() {
        const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenElement) return tokenElement.value;
        
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
    }

    function updateProgressIndicators() {
        // Update any static progress indicators
        updateDocumentCounters();
    }

    function initializeCharts() {
        // Initialize Chart.js charts for statistics
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
                    maintainAspectRatio: false
                }
            });
        }
    }

    // Load recent films on page load
    loadRecentFilms();
    
    // Periodically refresh data
    setInterval(() => {
        if (!isFilmingActive) {
            loadProjects();
            loadRecentFilms();
        }
    }, 30000); // Refresh every 30 seconds when not filming
});