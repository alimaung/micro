/**
 * Enhanced SMA Filming Interface JavaScript
 * Integrates with the enhanced backend SMA service for comprehensive filming management
 */

class SMAFilmingController {
    constructor() {
        this.currentStep = 'selection';
        this.selectedProject = null;
        this.selectedRoll = null;
        this.currentSession = null;
        this.websocketClient = null;
        this.sessionTimer = null;
        this.logUpdateInterval = null;
        this.healthCheckInterval = null;
        this.lastAction = null;
        this.sessionStartTime = null;
        
        // Enhanced state tracking
        this.sessionState = {
            id: null,
            status: 'idle',
            workflow_state: 'initialization',
            progress_percent: 0,
            total_documents: 0,
            processed_documents: 0,
            health: null,
            statistics: null
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkSMAConnection();
        this.loadActiveSessions();
        this.loadProjects();
        this.initWebSocket();
        this.startPeriodicUpdates();
    }
    
    bindEvents() {
        // Connection testing
        $('#test-connection-btn').on('click', () => this.testSMAConnection());
        
        // Session management
        $('#refresh-sessions-btn').on('click', () => this.loadActiveSessions());
        $('#cleanup-sessions-btn').on('click', () => this.cleanupSessions());
        
        // Project and roll selection
        $('#project-search').on('input', (e) => this.filterProjects(e.target.value));
        $('#project-filter').on('change', (e) => this.filterProjects($('#project-search').val(), e.target.value));
        $(document).on('click', '.project-item', (e) => this.selectProject(e.currentTarget));
        $(document).on('click', '.roll-item', (e) => this.selectRoll(e.currentTarget));
        
        // Workflow navigation
        $('#continue-to-config-btn').on('click', () => this.goToConfiguration());
        $('#back-to-selection-btn').on('click', () => this.goToSelection());
        $('#start-filming-btn').on('click', () => this.startFilming());
        
        // Configuration
        $('#film-type-select').on('change', (e) => this.updateFilmTypeInstructions(e.target.value));
        $('#workflow-mode').on('change', (e) => this.updateWorkflowMode(e.target.value));
        $('.checklist-item input[type="checkbox"]').on('change', () => this.validateConfiguration());
        
        // Filming controls
        $('#pause-filming-btn').on('click', () => this.pauseFilming());
        $('#resume-filming-btn').on('click', () => this.resumeFilming());
        $('#cancel-filming-btn').on('click', () => this.cancelFilming());
        $('#terminate-filming-btn').on('click', () => this.terminateFilming());
        $('#complete-filming-btn').on('click', () => this.completeFilming());
        
        // Enhanced controls
        $('#force-checkpoint-btn').on('click', () => this.forceCheckpoint());
        $('#view-health-btn').on('click', () => this.viewSessionHealth());
        $('#view-statistics-btn').on('click', () => this.viewSessionStatistics());
        
        // Log controls
        $('#clear-logs-btn').on('click', () => this.clearLogs());
        $('#download-logs-btn').on('click', () => this.downloadLogs());
        $('#filter-logs-select').on('change', (e) => this.filterLogs(e.target.value));
        
        // Completion actions
        $('#view-session-details-btn').on('click', () => this.viewSessionDetails());
        $('#start-new-session-btn').on('click', () => this.startNewSession());
        $('#go-to-develop-btn').on('click', () => this.goToDevelop());
        
        // Modal controls
        $('.modal-close').on('click', (e) => this.closeModal($(e.target).closest('.modal')));
        $('#retry-action-btn').on('click', () => this.retryLastAction());
        $('#recover-session-btn').on('click', () => this.recoverSession());
        
        // Click outside modal to close
        $('.modal').on('click', (e) => {
            if (e.target === e.currentTarget) {
                this.closeModal($(e.currentTarget));
            }
        });
        
        // Keyboard shortcuts
        $(document).on('keydown', (e) => this.handleKeyboardShortcuts(e));
    }
    
    // Enhanced Connection Management
    async checkSMAConnection() {
        try {
            const response = await fetch('/api/sma/test-connection/', {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            this.updateConnectionStatus(data.connected, data.message, data.response_time);
        } catch (error) {
            console.error('Connection test failed:', error);
            this.updateConnectionStatus(false, 'Connection test failed');
        }
    }
    
    async testSMAConnection() {
        $('#test-connection-btn').addClass('loading');
        await this.checkSMAConnection();
        $('#test-connection-btn').removeClass('loading');
    }
    
    updateConnectionStatus(connected, message, responseTime = null) {
        const statusEl = $('#sma-connection-status');
        const iconEl = statusEl.find('i');
        const textEl = statusEl.find('span');
        
        statusEl.removeClass('connected disconnected warning');
        
        if (connected) {
            statusEl.addClass('connected');
            iconEl.removeClass('fa-circle fa-times-circle fa-exclamation-triangle fa-check-circle');
            iconEl.addClass('fa-check-circle');
            
            let statusText = 'Connected';
            if (responseTime !== null) {
                statusText += ` (${responseTime}ms)`;
            }
            textEl.text(statusText);
        } else {
            statusEl.addClass('disconnected');
            iconEl.removeClass('fa-circle fa-times-circle fa-exclamation-triangle fa-check-circle');
            iconEl.addClass('fa-times-circle');
            textEl.text(message || 'Disconnected');
        }
    }
    
    // Enhanced Session Management
    async loadActiveSessions() {
        try {
            const response = await fetch('/api/sma/filming/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.renderActiveSessions(data.active_sessions);
                this.updateSessionsSummary(data.summary);
            } else {
                this.showError('Failed to load active sessions: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to load active sessions:', error);
            this.showError('Failed to load active sessions');
        }
    }
    
    renderActiveSessions(sessions) {
        const container = $('#active-sessions-grid');
        
        if (sessions.length === 0) {
            container.html(`
                <div class="no-sessions-message">
                    <i class="fas fa-info-circle"></i>
                    <p>No active filming sessions</p>
                    <small>Start a new session to begin filming</small>
                </div>
            `);
            return;
        }
        
        const sessionsHtml = sessions.map(session => `
            <div class="session-card ${session.status} ${session.is_process_active ? 'process-active' : 'process-inactive'}" 
                 data-session-id="${session.session_id}">
                <div class="session-header">
                    <h4>${session.project_name}</h4>
                    <div class="session-badges">
                        <span class="session-status ${session.status}">${session.status}</span>
                        <span class="workflow-state ${session.workflow_state}">${session.workflow_state}</span>
                        ${session.recovery_mode ? '<span class="recovery-badge">Recovery</span>' : ''}
                    </div>
                </div>
                <div class="session-details">
                    <div class="detail-item">
                        <span class="label">Roll:</span>
                        <span class="value">${session.roll_number}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Film Type:</span>
                        <span class="value">${session.film_type}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Progress:</span>
                        <span class="value">${session.progress_percent.toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Started:</span>
                        <span class="value">${this.formatDateTime(session.started_at)}</span>
                    </div>
                    ${session.process_pid ? `
                    <div class="detail-item">
                        <span class="label">Process:</span>
                        <span class="value">PID ${session.process_pid}</span>
                    </div>
                    ` : ''}
                    ${session.cpu_percent !== undefined ? `
                    <div class="detail-item">
                        <span class="label">CPU:</span>
                        <span class="value">${session.cpu_percent.toFixed(1)}%</span>
                    </div>
                    ` : ''}
                    ${session.memory_mb !== undefined ? `
                    <div class="detail-item">
                        <span class="label">Memory:</span>
                        <span class="value">${session.memory_mb.toFixed(1)}MB</span>
                    </div>
                    ` : ''}
                </div>
                <div class="session-actions">
                    <button class="icon-btn" onclick="smaController.monitorSession('${session.session_id}')" 
                            title="Monitor Session">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="icon-btn" onclick="smaController.viewSessionHealth('${session.session_id}')" 
                            title="View Health">
                        <i class="fas fa-heartbeat"></i>
                    </button>
                    ${session.status === 'running' ? `
                    <button class="icon-btn warning" onclick="smaController.controlSession('${session.session_id}', 'pause')" 
                            title="Pause Session">
                        <i class="fas fa-pause"></i>
                    </button>
                    ` : ''}
                    ${session.status === 'paused' ? `
                    <button class="icon-btn success" onclick="smaController.controlSession('${session.session_id}', 'resume')" 
                            title="Resume Session">
                        <i class="fas fa-play"></i>
                    </button>
                    ` : ''}
                    <button class="icon-btn danger" onclick="smaController.controlSession('${session.session_id}', 'cancel')" 
                            title="Cancel Session">
                        <i class="fas fa-stop"></i>
                    </button>
                    <button class="icon-btn" onclick="smaController.viewSessionStatistics('${session.session_id}')" 
                            title="View Statistics">
                        <i class="fas fa-chart-line"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        container.html(sessionsHtml);
    }
    
    updateSessionsSummary(summary) {
        if (summary) {
            const summaryEl = $('#sessions-summary');
            if (summaryEl.length === 0) {
                // Add summary element if it doesn't exist
                $('.panel-header').append(`
                    <div id="sessions-summary" class="sessions-summary">
                        <span class="summary-item">
                            <i class="fas fa-play-circle"></i>
                            Active: <span id="active-count">0</span>
                        </span>
                        <span class="summary-item">
                            <i class="fas fa-cogs"></i>
                            Processes: <span id="process-count">0</span>
                        </span>
                    </div>
                `);
            }
            
            $('#active-count').text(summary.total_active || 0);
            $('#process-count').text(summary.process_count || 0);
        }
    }
    
    async cleanupSessions() {
        if (!confirm('This will clean up completed sessions older than 24 hours. Continue?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/sma/sessions/cleanup/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    max_age_hours: 24
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.loadActiveSessions();
                this.showNotification(`Cleaned up ${data.cleaned_up} sessions`, 'success');
                if (data.errors > 0) {
                    this.showNotification(`${data.errors} errors during cleanup`, 'warning');
                }
            } else {
                this.showError('Failed to cleanup sessions: ' + data.error);
            }
        } catch (error) {
            console.error('Cleanup failed:', error);
            this.showError('Failed to cleanup sessions');
        }
    }
    
    // Enhanced Project and Roll Selection
    async loadProjects() {
        try {
            const response = await fetch('/api/projects/', {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.renderProjects(data.projects);
            } else {
                this.showError('Failed to load projects: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.showError('Failed to load projects');
        }
    }
    
    renderProjects(projects) {
        const container = $('#projects-list');
        
        if (projects.length === 0) {
            container.html(`
                <div class="no-projects-message">
                    <i class="fas fa-folder-open"></i>
                    <p>No projects available for filming</p>
                    <small>Create a project in the Register section first</small>
                </div>
            `);
            return;
        }
        
        const projectsHtml = projects.map(project => `
            <div class="project-item" data-project-id="${project.id}">
                <div class="project-header">
                    <h4>${project.name}</h4>
                    <span class="project-status ${project.status}">${project.status}</span>
                    </div>
                <div class="project-details">
                    <div class="detail-item">
                        <span class="label">Archive ID:</span>
                        <span class="value">${project.archive_id || 'N/A'}</span>
                </div>
                    <div class="detail-item">
                        <span class="label">Documents:</span>
                        <span class="value">${project.document_count || 0}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Rolls:</span>
                        <span class="value">${project.roll_count || 0}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Created:</span>
                        <span class="value">${this.formatDate(project.created_at)}</span>
                    </div>
                </div>
                <div class="project-path">
                    <i class="fas fa-folder"></i>
                    <span>${project.folder_path}</span>
                </div>
            </div>
        `).join('');
        
        container.html(projectsHtml);
    }
    
    filterProjects(searchTerm, statusFilter = 'all') {
        const projects = $('.project-item');
        
        projects.each(function() {
            const $project = $(this);
            const projectName = $project.find('h4').text().toLowerCase();
            const projectStatus = $project.find('.project-status').text().toLowerCase();
            const archiveId = $project.find('.detail-item .value').first().text().toLowerCase();
            
            const matchesSearch = !searchTerm || 
                projectName.includes(searchTerm.toLowerCase()) ||
                archiveId.includes(searchTerm.toLowerCase());
            
            const matchesStatus = statusFilter === 'all' || projectStatus === statusFilter;
            
            $project.toggle(matchesSearch && matchesStatus);
        });
    }
    
    selectProject(element) {
        $('.project-item').removeClass('selected');
        $(element).addClass('selected');
        
        const projectId = $(element).data('project-id');
        this.selectedProject = projectId;
        
        this.loadProjectRolls(projectId);
        $('#roll-selection').show();
        this.updateSelectionStatus();
    }
    
    async loadProjectRolls(projectId) {
        try {
            const response = await fetch(`/api/sma/project/${projectId}/rolls/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.renderProjectInfo(data.project);
                this.renderRolls(data.rolls);
            } else {
                this.showError('Failed to load project rolls: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to load project rolls:', error);
            this.showError('Failed to load project rolls');
        }
    }
    
    renderProjectInfo(project) {
        const infoHtml = `
            <div class="project-info-card">
                <h4>${project.name}</h4>
                <div class="project-meta">
                    <div class="meta-item">
                        <span class="label">Archive ID:</span>
                        <span class="value">${project.archive_id || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <span class="label">Total Rolls:</span>
                        <span class="value">${project.total_rolls || 0}</span>
                    </div>
                    <div class="meta-item">
                        <span class="label">Folder Path:</span>
                        <span class="value" title="${project.folder_path}">${project.folder_path}</span>
                    </div>
                </div>
            </div>
        `;
        
        $('#selected-project-info').html(infoHtml);
    }
    
    renderRolls(rolls) {
        const container = $('#rolls-grid');
        
        if (rolls.length === 0) {
            container.html(`
                <div class="no-rolls-message">
                    <i class="fas fa-film"></i>
                    <p>No rolls available for filming</p>
                    <small>Complete the allocation process first</small>
                </div>
            `);
            return;
        }
        
        const rollsHtml = rolls.map(roll => {
            const isAvailable = roll.filming_status === 'not_started' || roll.filming_status === 'error';
            const isInProgress = roll.filming_status === 'filming';
            const isCompleted = roll.filming_status === 'completed';
            
            return `
                <div class="roll-item ${isAvailable ? 'available' : ''} ${isInProgress ? 'in-progress' : ''} ${isCompleted ? 'completed' : ''}" 
                     data-roll-id="${roll.id}" ${!isAvailable ? 'data-disabled="true"' : ''}>
                <div class="roll-header">
                        <h5>Roll ${roll.roll_number}</h5>
                        <span class="filming-status ${roll.filming_status}">${roll.filming_status.replace('_', ' ')}</span>
                </div>
                <div class="roll-details">
                    <div class="detail-item">
                            <span class="label">Capacity:</span>
                            <span class="value">${roll.capacity}</span>
                    </div>
                    <div class="detail-item">
                            <span class="label">Pages Used:</span>
                            <span class="value">${roll.pages_used}</span>
                    </div>
                    <div class="detail-item">
                            <span class="label">Remaining:</span>
                            <span class="value">${roll.pages_remaining}</span>
                    </div>
                        ${roll.filming_progress_percent !== null ? `
                    <div class="detail-item">
                            <span class="label">Progress:</span>
                            <span class="value">${roll.filming_progress_percent.toFixed(1)}%</span>
                    </div>
                        ` : ''}
                        ${roll.filming_started_at ? `
                        <div class="detail-item">
                            <span class="label">Started:</span>
                            <span class="value">${this.formatDateTime(roll.filming_started_at)}</span>
                </div>
                        ` : ''}
                        ${roll.filming_completed_at ? `
                        <div class="detail-item">
                            <span class="label">Completed:</span>
                            <span class="value">${this.formatDateTime(roll.filming_completed_at)}</span>
                    </div>
                ` : ''}
            </div>
                    <div class="roll-output">
                        <i class="fas fa-folder"></i>
                        <span>${roll.output_directory}</span>
                    </div>
                    ${!isAvailable ? `
                    <div class="roll-overlay">
                        <i class="fas fa-${isCompleted ? 'check-circle' : 'clock'}"></i>
                        <span>${isCompleted ? 'Completed' : 'In Progress'}</span>
                    </div>
                    ` : ''}
                    ${roll.recent_sessions && roll.recent_sessions.length > 0 ? `
                    <div class="recent-sessions">
                        <small>Recent Sessions:</small>
                        ${roll.recent_sessions.slice(0, 2).map(session => `
                            <div class="session-ref ${session.status}">
                                <span>${session.session_id.substring(0, 8)}...</span>
                                <span>${session.status}</span>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        container.html(rollsHtml);
    }
    
    selectRoll(element) {
        if ($(element).data('disabled')) {
            this.showNotification('This roll is not available for filming', 'warning');
            return;
        }
        
        $('.roll-item').removeClass('selected');
        $(element).addClass('selected');
        
        const rollId = $(element).data('roll-id');
        this.selectedRoll = rollId;
        
        this.updateSelectionStatus();
    }
    
    updateSelectionStatus() {
        const hasProject = this.selectedProject !== null;
        const hasRoll = this.selectedRoll !== null;
        
        $('#continue-to-config-btn').prop('disabled', !(hasProject && hasRoll));
        
        if (hasProject && hasRoll) {
            $('#selection-status').text('Project and roll selected - ready to configure');
        } else if (hasProject) {
            $('#selection-status').text('Project selected - choose a roll');
        } else {
            $('#selection-status').text('Select project and roll');
        }
    }
    
    // Enhanced Workflow Navigation
    goToConfiguration() {
        if (!this.selectedProject || !this.selectedRoll) {
            this.showError('Please select both project and roll');
            return;
        }
        
        this.loadRollSummary();
        this.showStep('configuration');
        this.currentStep = 'configuration';
    }
    
    goToSelection() {
        this.showStep('selection');
        this.currentStep = 'selection';
    }
    
    showStep(stepId) {
        $('.workflow-step').hide();
        $(`#step-${stepId}`).show();
    }
    
    async loadRollSummary() {
        try {
            const response = await fetch(`/api/rolls/${this.selectedRoll}/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.renderRollSummary(data.roll);
            } else {
                this.showError('Failed to load roll summary: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to load roll summary:', error);
            this.showError('Failed to load roll summary');
        }
    }
    
    renderRollSummary(roll) {
        const summaryHtml = `
            <div class="summary-item">
                <span class="label">Roll Number:</span>
                <span class="value">${roll.roll_number}</span>
            </div>
            <div class="summary-item">
                <span class="label">Capacity:</span>
                <span class="value">${roll.capacity} pages</span>
            </div>
            <div class="summary-item">
                <span class="label">Pages Used:</span>
                <span class="value">${roll.pages_used} pages</span>
            </div>
            <div class="summary-item">
                <span class="label">Pages Remaining:</span>
                <span class="value">${roll.pages_remaining} pages</span>
            </div>
            <div class="summary-item">
                <span class="label">Output Directory:</span>
                <span class="value" title="${roll.output_directory}">${roll.output_directory}</span>
            </div>
            <div class="summary-item">
                <span class="label">Current Status:</span>
                <span class="value status-${roll.filming_status}">${roll.filming_status.replace('_', ' ')}</span>
            </div>
        `;
        
        $('#roll-summary-grid').html(summaryHtml);
    }
    
    updateFilmTypeInstructions(filmType) {
        const instruction = filmType === '16mm' ? '16mm film loaded in camera' : '35mm film loaded in camera';
        $('#film-type-instruction').text(instruction);
    }
    
    updateWorkflowMode(mode) {
        const recoveryOptions = $('#recovery-options');
        if (mode === 'recovery') {
            if (recoveryOptions.length === 0) {
                $('#workflow-mode').parent().after(`
                    <div id="recovery-options" class="recovery-options">
                        <label>
                            <input type="checkbox" id="force-recovery">
                            Force recovery (ignore checkpoint validation)
                        </label>
                        <small>Use this option if normal recovery fails</small>
                    </div>
                `);
            }
        } else {
            recoveryOptions.remove();
        }
    }
    
    validateConfiguration() {
        const checkboxes = $('.checklist-item input[type="checkbox"]');
        const allChecked = checkboxes.length === checkboxes.filter(':checked').length;
        
        $('#start-filming-btn').prop('disabled', !allChecked);
        
        if (allChecked) {
            $('#config-status').text('Configuration complete - ready to start filming');
        } else {
            $('#config-status').text('Complete the pre-flight checklist');
        }
    }
    
    // Enhanced Filming Process
    async startFilming() {
        if (!this.selectedProject || !this.selectedRoll) {
            this.showError('Project and roll selection required');
            return;
        }
        
        const filmType = $('#film-type-select').val();
        const workflowMode = $('#workflow-mode').val();
        const recovery = workflowMode === 'recovery';
        const forceRecovery = recovery && $('#force-recovery').is(':checked');
        
        this.lastAction = {
            action: 'start_filming',
            params: {
                project_id: this.selectedProject,
                roll_id: this.selectedRoll,
                film_type: filmType,
                recovery: recovery,
                force_recovery: forceRecovery
            }
        };
        
        $('#start-filming-btn').addClass('loading').prop('disabled', true);
            
        try {
            const response = await fetch('/api/sma/filming/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project_id: this.selectedProject,
                    roll_id: this.selectedRoll,
                    film_type: filmType,
                    recovery: recovery,
                    force_recovery: forceRecovery
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = data.session_id;
                this.sessionState.id = data.session_id;
                this.sessionState.status = data.status;
                this.sessionState.workflow_state = data.workflow_state;
                this.sessionStartTime = new Date();
                
                this.goToFilming();
                this.showNotification(`Filming started: ${data.message}`, 'success');
                
                // Subscribe to WebSocket updates for this session
                if (this.websocketClient) {
                    this.websocketClient.subscribeToSession(data.session_id);
                }
            } else {
                this.showError('Failed to start filming: ' + data.error);
                
                // Handle specific error cases
                if (data.existing_session) {
                    this.showRecoveryOptions(data.session_id);
                }
            }
        } catch (error) {
            console.error('Failed to start filming:', error);
            this.showError('Failed to start filming: ' + error.message);
        } finally {
            $('#start-filming-btn').removeClass('loading').prop('disabled', false);
        }
    }
    
    goToFilming() {
        this.showStep('filming');
        this.currentStep = 'filming';
        this.initializeFilmingInterface();
        this.startSessionMonitoring();
        this.startPeriodicUpdates();
    }
    
    initializeFilmingInterface() {
        // Set session info
        $('#current-session-id').text(this.currentSession || 'N/A');
        $('#session-start-time').text(this.formatDateTime(this.sessionStartTime));
        
        // Reset progress
        this.updateProgress(0, 0, 0);
        
        // Reset workflow states
        $('.workflow-state').removeClass('active completed error').addClass('pending');
        $('#state-initialization').addClass('active');
        
        // Clear logs
        this.clearLogs();
        
        // Update control buttons
        this.updateControlButtons('running');
        
        // Start session timer
        this.startSessionTimer();
    }
    
    startSessionMonitoring() {
        if (!this.currentSession) return;
        
        // Monitor session status every 2 seconds
        this.sessionMonitorInterval = setInterval(() => {
            this.updateSessionStatus();
        }, 2000);
        
        // Monitor logs every 5 seconds
        this.logUpdateInterval = setInterval(() => {
            this.updateSessionLogs();
        }, 5000);
    }
    
    stopSessionMonitoring() {
        if (this.sessionMonitorInterval) {
            clearInterval(this.sessionMonitorInterval);
            this.sessionMonitorInterval = null;
        }
        
        if (this.logUpdateInterval) {
            clearInterval(this.logUpdateInterval);
            this.logUpdateInterval = null;
        }
        
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
            this.sessionTimer = null;
        }
    }
    
    async updateSessionStatus() {
        if (!this.currentSession) return;
        
        try {
            const response = await fetch(`/api/sma/session/${this.currentSession}/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.updateFilmingInterface(data.status);
                this.sessionState = { ...this.sessionState, ...data.status };
            }
        } catch (error) {
            console.error('Failed to update session status:', error);
        }
    }
    
    updateFilmingInterface(status) {
        // Update progress
        this.updateProgress(
            status.progress_percent || 0,
            status.processed_documents || 0,
            status.total_documents || 0
        );
        
        // Update workflow state
        this.updateWorkflowState(status.workflow_state || 'initialization');
        
        // Update status message
        $('#filming-status').text(this.getStatusMessage(status));
        
        // Update control buttons
        this.updateControlButtons(status.status);
        
        // Handle completion
        if (status.status === 'completed') {
            this.onSessionComplete(status);
        } else if (status.status === 'failed' || status.status === 'cancelled') {
            this.onSessionError(status);
        }
    }
    
    updateProgress(percentage, processed, total) {
        $('#progress-percentage').text(`${percentage.toFixed(1)}%`);
        $('#progress-fill').css('width', `${percentage}%`);
        $('#progress-documents').text(`${processed} / ${total} documents`);
        
        // Calculate ETA if we have progress
        if (percentage > 0 && this.sessionStartTime) {
            const elapsed = Date.now() - this.sessionStartTime.getTime();
            const totalEstimated = (elapsed / percentage) * 100;
            const remaining = totalEstimated - elapsed;
            
            if (remaining > 0) {
                $('#progress-eta').text(`ETA: ${this.formatDuration(remaining)}`);
            } else {
                $('#progress-eta').text('ETA: Calculating...');
            }
        } else {
            $('#progress-eta').text('ETA: Calculating...');
        }
    }
    
    updateWorkflowState(currentState) {
        const states = ['initialization', 'monitoring', 'advanced_finish', 'completed'];
        const currentIndex = states.indexOf(currentState);
        
        states.forEach((state, index) => {
            const stateEl = $(`#state-${state.replace('_', '-')}`);
            stateEl.removeClass('active completed pending error');
            
            if (index < currentIndex) {
                stateEl.addClass('completed');
                stateEl.find('.state-status').text('completed');
            } else if (index === currentIndex) {
                stateEl.addClass('active');
                stateEl.find('.state-status').text('active');
            } else {
                stateEl.addClass('pending');
                stateEl.find('.state-status').text('pending');
            }
        });
    }
    
    getStatusMessage(status) {
        const messages = {
            'pending': 'Session is pending...',
            'running': `Filming in progress - ${status.workflow_state || 'initializing'}`,
            'paused': 'Session is paused',
            'completed': 'Filming completed successfully',
            'failed': `Filming failed: ${status.error_message || 'Unknown error'}`,
            'cancelled': 'Filming was cancelled',
            'terminated': 'Session was terminated'
        };
        
        return messages[status.status] || `Status: ${status.status}`;
    }
    
    updateControlButtons(status) {
        const pauseBtn = $('#pause-filming-btn');
        const resumeBtn = $('#resume-filming-btn');
        const cancelBtn = $('#cancel-filming-btn');
        const terminateBtn = $('#terminate-filming-btn');
        const completeBtn = $('#complete-filming-btn');
        
        // Hide all buttons first
        [pauseBtn, resumeBtn, cancelBtn, terminateBtn, completeBtn].forEach(btn => btn.hide());
        
        switch (status) {
            case 'running':
                pauseBtn.show();
                cancelBtn.show();
                terminateBtn.show();
                break;
            case 'paused':
                resumeBtn.show();
                cancelBtn.show();
                terminateBtn.show();
                break;
            case 'completed':
                completeBtn.show();
                break;
            case 'failed':
            case 'cancelled':
            case 'terminated':
                // Show recovery options
                break;
        }
    }
    
    startSessionTimer() {
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
        }
        
        this.sessionTimer = setInterval(() => {
            if (this.sessionStartTime) {
                const duration = Date.now() - this.sessionStartTime.getTime();
                $('#session-duration').text(this.formatDuration(duration));
            }
        }, 1000);
    }
    
    // Enhanced Session Control
    async pauseFilming() {
        await this.controlSession('pause');
    }
    
    async resumeFilming() {
        await this.controlSession('resume');
    }
    
    async cancelFilming() {
        if (!confirm('Are you sure you want to cancel the filming session? This cannot be undone.')) {
            return;
        }
        await this.controlSession('cancel');
    }
    
    async terminateFilming() {
        if (!confirm('Are you sure you want to terminate the filming session? This will force-stop the process.')) {
            return;
        }
        await this.controlSession('terminate', { force: true });
    }
    
    async controlSession(action, params = {}, sessionId = null) {
        const targetSessionId = sessionId || this.currentSession;
        if (!targetSessionId) {
            this.showError('No active session to control');
            return;
        }
        
        this.lastAction = {
            action: 'control_session',
            params: { action, sessionId: targetSessionId, ...params }
        };
        
        try {
            const response = await fetch(`/api/sma/session/${targetSessionId}/`, {
                method: 'PATCH',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action, ...params })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`Session ${action}ed successfully`, 'success');
                
                // Update interface immediately
                if (action === 'cancel' || action === 'terminate') {
                    this.stopSessionMonitoring();
                    this.stopPeriodicUpdates();
                }
            } else {
                this.showError(`Failed to ${action} session: ${data.error}`);
            }
        } catch (error) {
            console.error(`Failed to ${action} session:`, error);
            this.showError(`Failed to ${action} session`);
        }
    }
    
    async forceCheckpoint() {
        if (!this.currentSession) {
            this.showError('No active session');
            return;
        }
        
        try {
            const response = await fetch(`/api/sma/session/${this.currentSession}/checkpoint/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Checkpoint saved successfully', 'success');
            } else {
                this.showError('Failed to save checkpoint: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to save checkpoint:', error);
            this.showError('Failed to save checkpoint');
        }
    }
    
    // Enhanced Log Management
    async updateSessionLogs() {
        if (!this.currentSession) return;
        
        try {
            const logLevel = $('#filter-logs-select').val() || '';
            const url = `/api/sma/session/${this.currentSession}/logs/?limit=50${logLevel ? `&level=${logLevel}` : ''}`;
            
            const response = await fetch(url, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.renderLogs(data.logs);
            }
        } catch (error) {
            console.error('Failed to update logs:', error);
        }
    }
    
    renderLogs(logs) {
        const container = $('#log-content');
        
        if (logs.length === 0) {
            container.html('<div class="no-logs">No log entries available</div>');
            return;
        }
        
        const logsHtml = logs.map(log => `
            <div class="log-entry ${log.level}">
                <div class="log-header">
                <span class="log-timestamp">${this.formatTime(log.timestamp)}</span>
                    <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                    ${log.workflow_state ? `<span class="log-workflow">${log.workflow_state}</span>` : ''}
                </div>
                <div class="log-message">${this.escapeHtml(log.message)}</div>
            </div>
        `).join('');
        
        container.html(logsHtml);
        
        // Auto-scroll to bottom
            container.scrollTop(container[0].scrollHeight);
    }
    
    addLogEntry(logData) {
        const container = $('#log-content');
        const logHtml = `
            <div class="log-entry ${logData.level} new-entry">
                <div class="log-header">
                    <span class="log-timestamp">${this.formatTime(logData.timestamp)}</span>
                    <span class="log-level ${logData.level}">${logData.level.toUpperCase()}</span>
                    ${logData.workflow_state ? `<span class="log-workflow">${logData.workflow_state}</span>` : ''}
                </div>
                <div class="log-message">${this.escapeHtml(logData.message)}</div>
            </div>
        `;
        
        container.append(logHtml);
        
        // Remove new-entry class after animation
        setTimeout(() => {
            container.find('.new-entry').removeClass('new-entry');
        }, 500);
        
        // Auto-scroll to bottom
        container.scrollTop(container[0].scrollHeight);
        
        // Limit log entries to prevent memory issues
        const entries = container.find('.log-entry');
        if (entries.length > 200) {
            entries.slice(0, entries.length - 200).remove();
        }
    }
    
    filterLogs(level) {
        if (level) {
            $('.log-entry').hide();
            $(`.log-entry.${level}`).show();
        } else {
            $('.log-entry').show();
        }
    }
    
    clearLogs() {
        $('#log-content').empty();
    }
    
    async downloadLogs() {
        if (!this.currentSession) {
            this.showError('No active session');
            return;
        }
        
        try {
            const response = await fetch(`/api/sma/session/${this.currentSession}/logs/?limit=1000`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                const logText = data.logs.map(log => 
                    `[${log.timestamp}] ${log.level.toUpperCase()}: ${log.message}`
                ).join('\n');
                
                this.downloadFile(`sma_session_${this.currentSession}_logs.txt`, logText);
            } else {
                this.showError('Failed to download logs: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to download logs:', error);
            this.showError('Failed to download logs');
        }
    }
    
    // Session Completion
    onSessionComplete(status) {
        this.stopSessionMonitoring();
        this.goToCompletion(true, status);
    }
    
    onSessionError(status) {
        this.stopSessionMonitoring();
        this.showError(`Session ${status.status}: ${status.error_message || 'Unknown error'}`);
    }
    
    goToCompletion(success, status = null) {
        this.currentStep = 'completion';
        this.showStep('step-completion');
        
        if (success && status) {
            this.renderCompletionStats(status);
        }
    }
    
    renderCompletionStats(status) {
        const stats = `
            <div class="stat-card">
                <span class="stat-value">${status.total_documents || 0}</span>
                <span class="stat-label">Documents Processed</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${status.duration || 'Unknown'}</span>
                <span class="stat-label">Total Duration</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${status.progress_percent?.toFixed(1) || 0}%</span>
                <span class="stat-label">Completion Rate</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${status.film_type || 'Unknown'}</span>
                <span class="stat-label">Film Type</span>
            </div>
        `;
        
        $('#completion-stats').html(stats);
    }
    
    async completeFilming() {
        if (!this.currentSession) return;
        
        try {
            const response = await fetch(`/api/sma/mark-complete/${this.currentSession}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Roll marked as filmed successfully', 'success');
                this.goToCompletion(true);
            } else {
                this.showError(data.error || 'Failed to mark roll as filmed');
            }
        } catch (error) {
            this.showError('Failed to mark roll as filmed');
        }
    }
    
    // Completion Actions
    async viewSessionDetails() {
        if (!this.currentSession) return;
        
        try {
            const response = await fetch(`/api/sma/statistics/${this.currentSession}/`);
            const data = await response.json();
            
            if (data.success) {
                this.showSessionDetailsModal(data.statistics);
            }
        } catch (error) {
            this.showError('Failed to load session details');
        }
    }
    
    showSessionDetailsModal(stats) {
        const content = `
            <div class="session-details">
                <div class="detail-section">
                    <h3>Session Information</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Session ID:</span>
                            <span class="value">${stats.session_id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Project:</span>
                            <span class="value">${stats.project_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Roll:</span>
                            <span class="value">${stats.roll_number}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Film Type:</span>
                            <span class="value">${stats.film_type}</span>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Performance Metrics</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Total Documents:</span>
                            <span class="value">${stats.total_documents}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Processed:</span>
                            <span class="value">${stats.processed_documents}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Progress:</span>
                            <span class="value">${stats.progress_percent?.toFixed(1)}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Duration:</span>
                            <span class="value">${stats.duration || 'Unknown'}</span>
                        </div>
                        ${stats.documents_per_minute ? `
                        <div class="detail-item">
                            <span class="label">Processing Rate:</span>
                            <span class="value">${stats.documents_per_minute} docs/min</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Timeline</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Created:</span>
                            <span class="value">${this.formatDateTime(stats.created_at)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Started:</span>
                            <span class="value">${this.formatDateTime(stats.started_at)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Completed:</span>
                            <span class="value">${this.formatDateTime(stats.completed_at)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#session-details-content').html(content);
        this.showModal('#session-details-modal');
    }
    
    startNewSession() {
        this.currentSession = null;
        this.selectedProject = null;
        this.selectedRoll = null;
        this.goToSelection();
        this.loadProjects();
        $('#roll-selection').hide();
    }
    
    goToDevelop() {
        window.location.href = '/develop/';
    }
    
    // WebSocket Integration
    initWebSocket() {
        if (typeof SMAWebSocketClient !== 'undefined') {
            this.websocketClient = new SMAWebSocketClient();
            
            this.websocketClient.onSMAUpdate = (data) => {
                this.handleWebSocketUpdate(data);
            };
            
            this.websocketClient.onConnectionChange = (connected) => {
                this.updateWebSocketStatus(connected);
            };
        }
    }
    
    handleWebSocketUpdate(data) {
        if (data.session_id !== this.currentSession) {
            return; // Not for current session
        }
        
        switch (data.type) {
            case 'sma_progress':
                this.updateProgress(
                    data.data.progress_percent || 0,
                    data.data.processed_documents || 0,
                    data.data.total_documents || 0
                );
                break;
                
            case 'sma_workflow_state':
            this.updateWorkflowState(data.data.new_state);
                break;
                
            case 'sma_log':
                this.addLogEntry(data.data);
                break;
                
            case 'sma_error':
                this.showNotification(`Session error: ${data.data.error}`, 'error');
                break;
                
            case 'sma_completed':
                this.onSessionComplete(data.data);
                break;
        }
    }
    
    updateWebSocketStatus(connected) {
        const statusEl = $('#websocket-status');
        if (statusEl.length === 0) {
            $('.sma-header .connection-status').append(`
                <div id="websocket-status" class="websocket-status">
                    <i class="fas fa-wifi"></i>
                    <span>WebSocket</span>
            </div>
            `);
        }
        
        $('#websocket-status').removeClass('connected disconnected')
            .addClass(connected ? 'connected' : 'disconnected');
    }
    
    // Keyboard Shortcuts
    handleKeyboardShortcuts(e) {
        // Only handle shortcuts when not in input fields
        if ($(e.target).is('input, textarea, select')) {
            return;
        }
        
        switch (e.key) {
            case 'Escape':
                $('.modal:visible').each((i, modal) => {
                    this.closeModal($(modal));
                });
                break;
                
            case ' ': // Spacebar
                if (this.currentStep === 'filming') {
                    e.preventDefault();
                    if (this.sessionState.status === 'running') {
                        this.pauseFilming();
                    } else if (this.sessionState.status === 'paused') {
                        this.resumeFilming();
        }
    }
                break;
                
            case 'r':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.loadActiveSessions();
                }
                break;
        }
    }
    
    // Enhanced Utility Functions
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
    
    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    formatTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleTimeString();
    }
    
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    downloadFile(filename, content) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    showModal(selector) {
        $(selector).addClass('show');
        $('body').addClass('modal-open');
    }
    
    closeModal(selector) {
        $(selector).removeClass('show');
        $('body').removeClass('modal-open');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let container = $('#notification-container');
        if (container.length === 0) {
            $('body').append('<div id="notification-container"></div>');
            container = $('#notification-container');
        }
        
        const notification = $(`
            <div class="notification ${type}">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `);
        
        container.append(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.fadeOut(() => notification.remove());
        }, 5000);
        
        // Manual close
        notification.find('.notification-close').on('click', () => {
            notification.fadeOut(() => notification.remove());
        });
    }
    
    showError(message) {
        this.showNotification(message, 'error');
        console.error('SMA Error:', message);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Session Monitoring and Recovery
    async monitorSession(sessionId) {
        this.currentSession = sessionId;
        this.sessionState.id = sessionId;
        
        // Get session details
        try {
            const response = await fetch(`/api/sma/session/${sessionId}/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                const status = data.status;
                this.sessionState = { ...this.sessionState, ...status };
                
                // Set session start time from status
                if (status.started_at) {
                    this.sessionStartTime = new Date(status.started_at);
                }
                
                // Go to filming interface
                this.goToFilming();
                
                // Subscribe to WebSocket updates
                if (this.websocketClient) {
                    this.websocketClient.subscribeToSession(sessionId);
                }
                
                this.showNotification(`Now monitoring session ${sessionId}`, 'info');
            } else {
                this.showError('Failed to load session details: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to monitor session:', error);
            this.showError('Failed to monitor session');
        }
    }
    
    async recoverSession(sessionId = null) {
        const targetSessionId = sessionId || this.currentSession;
        if (!targetSessionId) {
            this.showError('No session to recover');
            return;
        }
        
        this.lastAction = {
            action: 'recover_session',
            params: { sessionId: targetSessionId }
        };
        
        try {
            const response = await fetch(`/api/sma/session/${targetSessionId}/recover/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = targetSessionId;
                this.sessionState.id = targetSessionId;
                
                // Go to filming interface
                this.goToFilming();
                
                // Subscribe to WebSocket updates
                if (this.websocketClient) {
                    this.websocketClient.subscribeToSession(targetSessionId);
                }
                
                this.showNotification('Session recovered successfully', 'success');
            } else {
                this.showError('Failed to recover session: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to recover session:', error);
            this.showError('Failed to recover session');
        }
    }
    
    async forceNewSession() {
        // Retry the last start filming action with force flag
        if (this.lastAction && this.lastAction.action === 'start_filming') {
            const params = { ...this.lastAction.params, force: true };
            
            try {
                const response = await fetch('/api/sma/filming/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.currentSession = data.session_id;
                    this.sessionState.id = data.session_id;
                    this.sessionStartTime = new Date();
                    
                    this.goToFilming();
                    this.showNotification('New session started successfully', 'success');
                    
                    if (this.websocketClient) {
                        this.websocketClient.subscribeToSession(data.session_id);
                    }
                } else {
                    this.showError('Failed to start new session: ' + data.error);
                }
            } catch (error) {
                console.error('Failed to start new session:', error);
                this.showError('Failed to start new session');
            }
        } else {
            this.showError('No previous action to retry');
        }
    }
    
    retryLastAction() {
        if (!this.lastAction) {
            this.showError('No action to retry');
            return;
        }
        
        switch (this.lastAction.action) {
            case 'start_filming':
                this.startFilming();
                break;
            case 'control_session':
                const { action, sessionId, ...params } = this.lastAction.params;
                this.controlSession(action, params, sessionId);
                break;
            case 'recover_session':
                this.recoverSession(this.lastAction.params.sessionId);
                break;
            default:
                this.showError('Unknown action to retry');
        }
    }
    
    // Enhanced Session Details and Statistics
    async viewSessionHealth(sessionId = null) {
        const targetSessionId = sessionId || this.currentSession;
        if (!targetSessionId) {
            this.showError('No session selected');
            return;
        }
        
        try {
            const response = await fetch(`/api/sma/session/${targetSessionId}/health/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSessionHealthModal(data.health);
            } else {
                this.showError('Failed to get session health: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to get session health:', error);
            this.showError('Failed to get session health');
        }
    }
    
    async viewSessionStatistics(sessionId = null) {
        const targetSessionId = sessionId || this.currentSession;
        if (!targetSessionId) {
            this.showError('No session selected');
            return;
        }
        
        try {
            const response = await fetch(`/api/sma/session/${targetSessionId}/statistics/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSessionStatisticsModal(data.statistics);
            } else {
                this.showError('Failed to get session statistics: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to get session statistics:', error);
            this.showError('Failed to get session statistics');
        }
    }
    
    showSessionHealthModal(health) {
        const modal = $('#health-modal');
        if (modal.length === 0) {
            $('body').append(`
                <div class="modal" id="health-modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2><i class="fas fa-heartbeat"></i> Session Health</h2>
                            <button class="modal-close">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="modal-body" id="health-modal-content">
                        </div>
                    </div>
                </div>
            `);
        }
        
        const healthHtml = `
            <div class="health-overview ${health.healthy ? 'healthy' : 'unhealthy'}">
                <div class="health-status">
                    <i class="fas fa-${health.healthy ? 'check-circle' : 'exclamation-triangle'}"></i>
                    <span>${health.healthy ? 'Healthy' : 'Issues Detected'}</span>
                </div>
                <div class="health-timestamp">
                    Last checked: ${this.formatDateTime(health.timestamp)}
                </div>
            </div>
            
            ${health.issues && health.issues.length > 0 ? `
            <div class="health-section">
                <h3><i class="fas fa-exclamation-circle"></i> Issues</h3>
                <ul class="health-list issues">
                    ${health.issues.map(issue => `<li>${issue}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
            
            ${health.warnings && health.warnings.length > 0 ? `
            <div class="health-section">
                <h3><i class="fas fa-exclamation-triangle"></i> Warnings</h3>
                <ul class="health-list warnings">
                    ${health.warnings.map(warning => `<li>${warning}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
            
            <div class="health-actions">
                <button id="refresh-health-btn" class="secondary-btn">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
                <button id="force-checkpoint-health-btn" class="primary-btn">
                    <i class="fas fa-save"></i> Force Checkpoint
                </button>
            </div>
        `;
        
        $('#health-modal-content').html(healthHtml);
        
        $('#refresh-health-btn').on('click', () => {
            this.viewSessionHealth();
        });
        
        $('#force-checkpoint-health-btn').on('click', () => {
            this.forceCheckpoint();
            this.closeModal($('#health-modal'));
        });
        
        this.showModal('#health-modal');
    }
    
    showSessionStatisticsModal(stats) {
        const modal = $('#statistics-modal');
        if (modal.length === 0) {
            $('body').append(`
                <div class="modal" id="statistics-modal">
                    <div class="modal-content large">
                        <div class="modal-header">
                            <h2><i class="fas fa-chart-line"></i> Session Statistics</h2>
                            <button class="modal-close">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="modal-body" id="statistics-modal-content">
                        </div>
                    </div>
                </div>
            `);
        }
        
        const statsHtml = `
            <div class="statistics-grid">
                <div class="stat-section">
                    <h3>Progress</h3>
                    <div class="stat-items">
                        <div class="stat-item">
                            <span class="stat-label">Total Documents:</span>
                            <span class="stat-value">${stats.total_documents || 0}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Processed:</span>
                            <span class="stat-value">${stats.processed_documents || 0}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Progress:</span>
                            <span class="stat-value">${(stats.progress_percent || 0).toFixed(1)}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Workflow State:</span>
                            <span class="stat-value">${stats.workflow_state || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="stat-section">
                    <h3>Timing</h3>
                    <div class="stat-items">
                        ${stats.started_at ? `
                        <div class="stat-item">
                            <span class="stat-label">Started:</span>
                            <span class="stat-value">${this.formatDateTime(stats.started_at)}</span>
                        </div>
                        ` : ''}
                        ${stats.completed_at ? `
                        <div class="stat-item">
                            <span class="stat-label">Completed:</span>
                            <span class="stat-value">${this.formatDateTime(stats.completed_at)}</span>
                        </div>
                        ` : ''}
                        ${stats.total_duration ? `
                        <div class="stat-item">
                            <span class="stat-label">Total Duration:</span>
                            <span class="stat-value">${stats.total_duration}</span>
                        </div>
                        ` : ''}
                        ${stats.current_duration ? `
                        <div class="stat-item">
                            <span class="stat-label">Current Duration:</span>
                            <span class="stat-value">${stats.current_duration}</span>
                        </div>
                        ` : ''}
                        ${stats.processing_rate_docs_per_minute ? `
                        <div class="stat-item">
                            <span class="stat-label">Processing Rate:</span>
                            <span class="stat-value">${stats.processing_rate_docs_per_minute} docs/min</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                ${stats.process_stats ? `
                <div class="stat-section">
                    <h3>Process</h3>
                    <div class="stat-items">
                        <div class="stat-item">
                            <span class="stat-label">CPU Usage:</span>
                            <span class="stat-value">${stats.process_stats.cpu_percent?.toFixed(1) || 'N/A'}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Memory Usage:</span>
                            <span class="stat-value">${stats.process_stats.memory_mb?.toFixed(1) || 'N/A'} MB</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Memory %:</span>
                            <span class="stat-value">${stats.process_stats.memory_percent?.toFixed(1) || 'N/A'}%</span>
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${stats.log_counts ? `
                <div class="stat-section">
                    <h3>Log Summary</h3>
                    <div class="stat-items">
                        ${Object.entries(stats.log_counts).map(([level, count]) => `
                        <div class="stat-item">
                            <span class="stat-label">${level.toUpperCase()}:</span>
                            <span class="stat-value">${count}</span>
                        </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        $('#statistics-modal-content').html(statsHtml);
        this.showModal('#statistics-modal');
    }
    
    // Utility Methods
    getCSRFToken() {
        return $('[name=csrfmiddlewaretoken]').val() || 
               $('meta[name=csrf-token]').attr('content') ||
               document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
}

// Initialize the SMA Filming Controller when the page loads
let smaController;

$(document).ready(function() {
    smaController = new SMAFilmingController();
});

// Export for global access
window.SMAFilmingController = SMAFilmingController; 