document.addEventListener('DOMContentLoaded', function() {
    // Main state variables
    let currentStep = 'initialization';
    let isFilmingActive = false;
    let currentSessionId = null;
    let websocketClient = null;
    let allRolls = []; // Store all loaded rolls
    let filteredRolls = []; // Store filtered rolls
    let currentRollId = null;
    let sessionStartTime = null;
    let selectedRollData = null; // Store selected roll data for validation
    let isLightMode = true; // Default to light mode for film handling
    
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
            console.log('📋 No active sessions found, loading rolls...');
            // Normal initialization - load rolls first
            await loadRolls();
            
            // Try to restore roll selection state
            const stateRestored = restoreRollSelectionState();
            
            if (!stateRestored) {
                // No saved state, show roll selection
                showCard('roll-selection-card');
            }
        }
        
        // Initialize event handlers
        initializeEventHandlers();
        
        // Initialize WebSocket connection
        initializeWebSocket();
    
        // Initialize interface
        updateQuickStats();
        
        // Initialize lighting mode
        initializeFilmingLightingMode();
        
        // Initialize toggle position (default to ALL)
        setTimeout(() => {
            updateTogglePosition('all');
        }, 100);
        
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
    
    // Load all rolls from the SMA API
    async function loadRolls() {
        try {
            showLoadingState();
            
            // Use SMA-specific rolls endpoint to get all rolls
            const response = await fetch('/api/sma/rolls/', {
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
                allRolls = data.rolls || [];
            } else {
                throw new Error(data.error || 'Failed to load rolls');
            }
            
            // Apply initial filtering to match default filter values (ready status + 16mm)
            filteredRolls = allRolls.filter(roll => {
                // Only show rolls ready for filming
                const rollStatus = roll.filming_status || 'ready';
                const isReady = rollStatus === 'ready';
                
                // Only show 16mm rolls
                const rollFilmType = roll.film_type || '16mm';
                const is16mm = rollFilmType === '16mm';
                
                return isReady && is16mm;
            });
            
            displayRolls(filteredRolls);
            
            // Display filming priority summary for ready rolls
            displayFilmingPrioritySummary(allRolls);
            
            hideLoadingState();
            
        } catch (error) {
            console.error('Error loading rolls:', error);
            showErrorState('Failed to load rolls. Please try again.');
            showNotification('error', 'Load Error', `Failed to load rolls: ${error.message}`);
        }
    }
    
    // Display rolls in the grid
    function displayRolls(rolls) {
        const rollsGrid = document.getElementById('rolls-grid');
        
        if (!rollsGrid) {
            console.warn('Rolls grid element not found');
            return;
        }
        
        if (rolls.length === 0) {
            rollsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-film"></i>
                    <p>No rolls available for filming</p>
                    <small>Rolls need to be processed and have available documents for SMA filming.</small>
                </div>
            `;
            return;
        }
        
        rollsGrid.innerHTML = rolls.map(roll => {
            const status = roll.filming_status || 'ready';
            const statusClass = getStatusClass(status);
            const filmNumber = roll.film_number || 'Unknown';
            const filmType = roll.film_type || '16mm';
            const projectName = roll.project_name || 'Unknown Project';
            const archiveId = roll.project_archive_id || 'Unknown';
            const documentCount = roll.document_count || 0;
            const pageCount = roll.pages_used || 0;
            const progressPercent = roll.filming_progress_percent || 0;
            const isCompleted = status === 'completed';
            const isReFilming = roll.is_re_filming || false;
            
            // Determine dependency information
            let dependencyInfo = '';
            let dependencyClass = '';
            
            if (status === 'ready' && roll.filming_priority) {
                const priority = roll.filming_priority;
                
                switch (priority.priority_tier) {
                    case 'creator':
                        dependencyInfo = `<i class="fas fa-star" title="Creates temp roll for ${priority.blocks_count || 0} other rolls"></i> Priority: Creates for ${priority.blocks_count || 0} rolls`;
                        dependencyClass = 'priority-creator';
                        break;
                    case 'immediate':
                        dependencyInfo = `<i class="fas fa-check-circle" title="Ready to film immediately"></i> Ready Now`;
                        dependencyClass = 'priority-immediate';
                        break;
                    case 'waiting':
                        dependencyInfo = `<i class="fas fa-clock" title="Waiting for dependencies"></i> Waiting`;
                        dependencyClass = 'priority-waiting';
                        break;
                    case 'problem':
                        dependencyInfo = `<i class="fas fa-exclamation-triangle" title="Has issues that need resolution"></i> Needs Attention`;
                        dependencyClass = 'priority-problem';
                        break;
                    default:
                        if (roll.source_temp_roll && roll.created_temp_roll) {
                            dependencyInfo = `<i class="fas fa-exchange-alt" title="Uses temp roll and creates temp roll"></i> Chain`;
                            dependencyClass = 'dependency-chain';
                        } else if (roll.source_temp_roll) {
                            dependencyInfo = `<i class="fas fa-arrow-right" title="Uses temp roll - may depend on other rolls"></i> Uses Temp`;
                            dependencyClass = 'dependency-consumer';
                        } else if (roll.created_temp_roll) {
                            dependencyInfo = `<i class="fas fa-arrow-left" title="Creates temp roll for other rolls"></i> Creates Temp`;
                            dependencyClass = 'dependency-creator';
                        } else {
                            dependencyInfo = `<i class="fas fa-circle" title="Independent roll - no temp roll dependencies"></i> Independent`;
                            dependencyClass = 'dependency-independent';
                        }
                }
            } else {
                // Fallback to old logic for non-ready rolls
                if (roll.source_temp_roll && roll.created_temp_roll) {
                    dependencyInfo = `<i class="fas fa-exchange-alt" title="Uses temp roll and creates temp roll"></i> Chain`;
                    dependencyClass = 'dependency-chain';
                } else if (roll.source_temp_roll) {
                    dependencyInfo = `<i class="fas fa-arrow-right" title="Uses temp roll - may depend on other rolls"></i> Uses Temp`;
                    dependencyClass = 'dependency-consumer';
                } else if (roll.created_temp_roll) {
                    dependencyInfo = `<i class="fas fa-arrow-left" title="Creates temp roll for other rolls"></i> Creates Temp`;
                    dependencyClass = 'dependency-creator';
                } else {
                    dependencyInfo = `<i class="fas fa-circle" title="Independent roll - no temp roll dependencies"></i> Independent`;
                    dependencyClass = 'dependency-independent';
                }
            }
            
            // Build CSS classes - avoid duplication
            const cardClasses = ['roll-card', statusClass, dependencyClass];
            if (isCompleted && statusClass !== 'completed') {
                cardClasses.push('completed');
            }
            
            return `
                <div class="${cardClasses.join(' ')}" 
                     data-roll-id="${roll.id}" 
                     data-status="${status}"
                     data-film-type="${filmType}">
                    
                    ${status === 'filming' ? `
                        <div class="filming-progress-indicator">
                            <div class="filming-progress-fill" style="width: ${progressPercent}%"></div>
                        </div>
                    ` : ''}
                    
                    ${isCompleted ? `
                        <div class="completed-badge">
                            <i class="fas fa-check-circle"></i>
                            <span>Completed</span>
                        </div>
                    ` : ''}
                    
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">
                                ${getLocationIndicator(filmNumber)}${filmNumber}
                            </div>
                            <div class="roll-film-type">${filmType}</div>
                        </div>
                        ${!isCompleted ? `
                            <div class="roll-status-badge ${statusClass}">
                                ${status.replace('-', ' ')}
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="roll-project-info">
                        <div class="project-name">${projectName}</div>
                        <div class="archive-id">${archiveId}</div>
                    </div>
                    
                    <div class="roll-details">
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Documents:</span>
                            <span class="roll-detail-value">${documentCount}</span>
                        </div>
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Pages:</span>
                            <span class="roll-detail-value">${pageCount}</span>
                        </div>
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Output:</span>
                            <span class="roll-detail-value">${roll.output_directory || 'Not set'}</span>
                        </div>
                        ${dependencyInfo ? `
                            <div class="roll-detail-item dependency-info">
                                <span class="roll-detail-label">Filming:</span>
                                <span class="roll-detail-value dependency-badge">${dependencyInfo}</span>
                            </div>
                        ` : ''}
                        <div class="directory-status ${roll.output_directory_exists ? 'exists' : 'missing'}">
                            <i class="fas ${roll.output_directory_exists ? 'fa-check' : 'fa-times'}"></i>
                            Directory ${roll.output_directory_exists ? 'exists' : 'missing'}
                        </div>
                    </div>
                    
                    ${status === 'filming' ? `
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
                        ${status === 'ready' || isCompleted ? `
                            <span class="action-hint">
                                ${isCompleted ? 'Click to re-film' : 'Click to select'}
                            </span>
                        ` : `
                            <span class="status-text ${status}">
                                <i class="fas ${status === 'filming' ? 'fa-spinner fa-spin' : 'fa-exclamation-triangle'}"></i>
                                ${status === 'filming' ? 'Currently Filming' : 'Not Ready'}
                            </span>
                            ${status === 'filming' ? `
                                <button class="revert-to-ready-btn" title="Revert to Ready">
                                    <i class="fas fa-undo"></i>
                                </button>
                            ` : ''}
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
    
    // Get CSS class for status
    function getStatusClass(status) {
        switch (status) {
            case 'ready': return 'ready';
            case 'filming': return 'filming';
            case 'completed': return 'completed';
            case 'error': return 'error';
            default: return 'pending';
        }
    }
    
    // Get location indicator based on film number
    function getLocationIndicator(filmNumber) {
        if (!filmNumber || filmNumber.length < 1) {
            return '<span class="location-indicator unknown"></span>';
        }
        
        const firstDigit = filmNumber.charAt(0);
        if (firstDigit === '1') {
            return '<span class="location-indicator ou" title="OU Location"></span>';
        } else if (firstDigit === '2') {
            return '<span class="location-indicator dw" title="DW Location"></span>';
        } else {
            return '<span class="location-indicator unknown" title="Unknown Location"></span>';
        }
    }
    
    // Attach event listeners to roll cards
    function attachRollEventListeners() {
        document.querySelectorAll('.roll-card').forEach(card => {
            const infoButton = card.querySelector('.roll-info-button');
            const status = card.dataset.status;
            
            // Allow selection of ready rolls and completed rolls (for re-filming)
            if (status === 'ready' || status === 'completed') {
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
            
            const revertBtn = card.querySelector('.revert-to-ready-btn');
            if (revertBtn) {
                revertBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const rollId = card.getAttribute('data-roll-id');
                    revertRollToReady(rollId, card);
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
        const isCompleted = rollCard.classList.contains('completed');
        const rollStatus = document.getElementById('roll-status');
        if (rollStatus) {
            rollStatus.textContent = `Roll ${filmNumber} highlighted - ${isCompleted ? 'Re-filming' : 'Filming'} - click Select to continue`;
            rollStatus.className = 'status-indicator';
        }
        
        // Save selection state (but not validation state yet)
        const rollId = rollCard.getAttribute('data-roll-id');
        const rollData = allRolls.find(r => r.id == rollId);
        if (rollData) {
            selectedRollData = rollData;
            saveRollSelectionState();
        }
    }
    
    // Proceed with the selected roll
    function proceedWithSelectedRoll(rollCard) {
        // Get roll data
        const rollId = rollCard.getAttribute('data-roll-id');
        const filmNumber = rollCard.querySelector('.roll-film-number').textContent;
        const filmType = rollCard.querySelector('.roll-film-type').textContent;
        const projectName = rollCard.querySelector('.project-name').textContent;
        const archiveId = rollCard.querySelector('.archive-id').textContent;
        const documentCount = rollCard.querySelectorAll('.roll-detail-value')[0].textContent;
        const pageCount = rollCard.querySelectorAll('.roll-detail-value')[1].textContent;
        const outputDir = rollCard.querySelectorAll('.roll-detail-value')[2].textContent;
        const dirExists = rollCard.querySelector('.directory-status').classList.contains('exists');
        const isCompleted = rollCard.classList.contains('completed');
        
        // Get the full roll data from the processed rolls
        const rollData = allRolls.find(r => r.id == rollId);
        selectedRollData = rollData;
        
        // Update validation card with roll info
        updateValidationCard(rollId, filmNumber, filmType, projectName, archiveId, documentCount, pageCount, outputDir, dirExists, rollData, isCompleted);
        
        // Show validation card
        showCard('validation-card');
        
        // Save state with validation card visible
        saveRollSelectionState();
        
        // Update roll status
        const rollStatus = document.getElementById('roll-status');
        if (rollStatus) {
            rollStatus.textContent = `Roll ${filmNumber} selected for validation`;
            rollStatus.className = 'status-indicator success';
        }
        
        // Show toast notification
        showToast('success', 'Roll Selected', `Selected roll: ${filmNumber} ${isCompleted ? '(Re-filming)' : ''}`);
    }
    
    // Update validation card with roll information
    function updateValidationCard(rollId, filmNumber, filmType, projectName, archiveId, documentCount, pageCount, outputDir, dirExists, rollData, isReFilming) {
        // Update validation summary
        const elements = {
            'validation-film-number': filmNumber,
            'validation-film-type': filmType,
            'validation-project-name': projectName,
            'validation-archive-id': archiveId,
            'validation-document-count': documentCount,
            'validation-page-count': pageCount,
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
        
        // Show/hide re-filming warning
        const reFilmingWarning = document.getElementById('re-filming-warning');
        const reFilmingCheckItem = document.getElementById('check-re-filming-item');
        
        if (isReFilming) {
            if (reFilmingWarning) reFilmingWarning.style.display = 'block';
            if (reFilmingCheckItem) reFilmingCheckItem.style.display = 'block';
            
            // Fetch temp roll preview for re-filming
            fetchTempRollPreview(rollId, filmType, pageCount, true);
        } else {
            if (reFilmingWarning) reFilmingWarning.style.display = 'none';
            if (reFilmingCheckItem) reFilmingCheckItem.style.display = 'none';
            
            // For new filming, also check for available temp rolls (efficient usage)
            fetchTempRollPreview(rollId, filmType, pageCount, false);
        }
        
        // Update camera head instruction
        const cameraHeadInstruction = document.getElementById('camera-head-instruction');
        if (cameraHeadInstruction) {
            cameraHeadInstruction.textContent = `Use ${filmType} camera head`;
        }
        
        // Reset validation checklist
        document.querySelectorAll('.checklist-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        updateValidationStatus();
    }
    
    // Fetch temp roll preview for filming (preview only, no updates)
    async function fetchTempRollPreview(rollId, filmType, requiredPages, isReFilming = true) {
        try {
            // Show loading state for roll source
            updateRollSourceDisplay('Checking available temp rolls...', 'loading');
            
            const response = await fetch(`/api/sma/temp-roll-preview/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    roll_id: rollId,
                    film_type: filmType,
                    required_pages: parseInt(requiredPages),
                    preview_only: true  // Important: this is just a preview
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    displayTempRollPreview(data.temp_roll_strategy, isReFilming);
                } else {
                    console.warn('Temp roll preview failed:', data.error);
                    updateRollSourceDisplay('New Roll (temp roll check failed)', 'new-roll');
                }
            } else {
                console.warn('Temp roll preview request failed:', response.status);
                updateRollSourceDisplay('New Roll (temp roll service unavailable)', 'new-roll');
            }
        } catch (error) {
            console.error('Error fetching temp roll preview:', error);
            updateRollSourceDisplay('New Roll (temp roll check error)', 'new-roll');
        }
    }
    
    // Display temp roll preview information
    function displayTempRollPreview(strategy, isReFilming = true) {
        // Get refilming status from strategy if available, fallback to parameter
        const actuallyReFilming = strategy.is_refilming !== undefined ? strategy.is_refilming : isReFilming;
        
        if (strategy.use_temp_roll) {
            // Will use existing temp roll
            const tempRoll = strategy.temp_roll;
            
            // Update roll source display with more context
            let sourceText = `Temp Roll #${tempRoll.temp_roll_id} (${tempRoll.remaining_capacity} pages available)`;
            if (!actuallyReFilming) {
                sourceText = `Pre-allocated: ${sourceText}`;
            }
            
            updateRollSourceDisplay(sourceText, 'temp-roll');
            
            // Update temp roll instruction with context
            let instructionTitle = `Insert Temp Roll #${tempRoll.temp_roll_id}`;
            let instructionDetails;
            
            if (actuallyReFilming) {
                instructionDetails = `Re-filming: Using available temp roll with ${tempRoll.remaining_capacity} pages capacity. Will use ${strategy.pages_to_use} pages.`;
            } else {
                instructionDetails = `Using pre-allocated temp roll from registration with ${tempRoll.remaining_capacity} pages capacity. Will use ${strategy.pages_to_use} pages.`;
            }
            
            updateTempRollInstruction(instructionTitle, instructionDetails);
            
            // Show preview of what will happen
            showTempRollPreviewInfo(strategy, actuallyReFilming);
        } else {
            // Will use new roll
            let rollSourceText;
            if (actuallyReFilming) {
                rollSourceText = 'New Roll (Re-filming)';
            } else {
                rollSourceText = 'New Roll (First filming)';
            }
            
            updateRollSourceDisplay(rollSourceText, 'new-roll');
            
            // Update temp roll instruction with context
            let rollTypeDesc;
            if (actuallyReFilming) {
                rollTypeDesc = 'new roll for re-filming';
            } else {
                rollTypeDesc = 'new roll for first filming';
            }
            
            let instructionDetails = `${rollTypeDesc.charAt(0).toUpperCase() + rollTypeDesc.slice(1)} with ${strategy.new_roll_capacity} pages capacity. `;
            
            if (strategy.will_create_temp_roll) {
                instructionDetails += 'Will create temp roll after filming.';
            } else {
                instructionDetails += 'Roll will be fully used.';
            }
            
            updateTempRollInstruction(
                `Insert new ${strategy.film_type} film roll`,
                instructionDetails
            );
            
            // Show preview of what will happen
            showTempRollPreviewInfo(strategy, actuallyReFilming);
        }
        
        // Show the strategy reason if available
        if (strategy.reason) {
            showStrategyReason(strategy.reason);
        }
    }
    
    // Update roll source display
    function updateRollSourceDisplay(text, className) {
        const rollSourceElement = document.getElementById('validation-roll-source');
        if (rollSourceElement) {
            rollSourceElement.textContent = text;
            rollSourceElement.className = `summary-value ${className}`;
        }
        
        // Also update film type highlighting
        const filmTypeElement = document.getElementById('validation-film-type');
        if (filmTypeElement) {
            if (className === 'temp-roll') {
                filmTypeElement.className = 'summary-value temp-roll';
            } else {
                filmTypeElement.className = 'summary-value';
            }
        }
    }
    
    // Update temp roll instruction
    function updateTempRollInstruction(instruction, details) {
        const tempRollInstruction = document.getElementById('temp-roll-instruction');
        const tempRollDetails = document.getElementById('temp-roll-details');
        
        if (tempRollInstruction) {
            tempRollInstruction.textContent = instruction;
        }
        
        if (tempRollDetails) {
            tempRollDetails.textContent = details;
            // Style based on whether it's temp roll or new roll
            if (instruction.includes('Temp Roll')) {
                tempRollDetails.style.color = 'var(--color-warning)';
                tempRollDetails.style.fontWeight = 'bold';
            } else {
                tempRollDetails.style.color = 'var(--color-text-secondary)';
                tempRollDetails.style.fontWeight = 'normal';
            }
        }
    }
    
    // Show temp roll preview information
    function showTempRollPreviewInfo(strategy, isReFilming = true) {
        // Create or update a preview section in the validation card
        let previewSection = document.getElementById('temp-roll-preview');
        
        if (!previewSection) {
            // Create preview section
            previewSection = document.createElement('div');
            previewSection.id = 'temp-roll-preview';
            previewSection.className = 'temp-roll-preview-section';
            
            // Insert after the roll summary
            const rollSummary = document.querySelector('.roll-summary');
            if (rollSummary && rollSummary.parentNode) {
                rollSummary.parentNode.insertBefore(previewSection, rollSummary.nextSibling);
            }
        }
        
        // Build preview content
        let previewTitle;
        if (isReFilming) {
            previewTitle = 'Re-filming Strategy Preview';
        } else {
            previewTitle = 'First Filming Strategy Preview';
        }
        
        let previewContent = `
            <h3>${previewTitle}</h3>
            <div class="preview-info">
        `;
        
        if (strategy.use_temp_roll) {
            const tempRoll = strategy.temp_roll;
            const remainingAfter = tempRoll.remaining_capacity - strategy.pages_to_use;
            
            previewContent += `
                <div class="preview-item">
                    <span class="preview-label">Will Use:</span>
                    <span class="preview-value temp-roll">Temp Roll #${tempRoll.temp_roll_id}</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">Source:</span>
                    <span class="preview-value">${isReFilming ? 'Available temp roll' : 'Pre-allocated from registration'}</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">Current Capacity:</span>
                    <span class="preview-value">${tempRoll.remaining_capacity} pages</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">Pages Needed:</span>
                    <span class="preview-value">${strategy.pages_to_use} pages</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">After Filming:</span>
                    <span class="preview-value">${remainingAfter} pages remaining${remainingAfter <= 0 ? ' (temp roll exhausted)' : ''}</span>
                </div>
            `;
        } else {
            const remainingAfter = strategy.new_roll_capacity - strategy.pages_to_use;
            
            previewContent += `
                <div class="preview-item">
                    <span class="preview-label">Will Use:</span>
                    <span class="preview-value new-roll">New ${strategy.film_type} Roll</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">Source:</span>
                    <span class="preview-value">${isReFilming ? 'New roll for re-filming' : 'Allocated new roll from registration'}</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">Roll Capacity:</span>
                    <span class="preview-value">${strategy.new_roll_capacity} pages</span>
                </div>
                <div class="preview-item">
                    <span class="preview-label">Pages Needed:</span>
                    <span class="preview-value">${strategy.pages_to_use} pages</span>
                </div>
            `;
            
            if (strategy.will_create_temp_roll) {
                previewContent += `
                    <div class="preview-item">
                        <span class="preview-label">Will Create:</span>
                        <span class="preview-value temp-roll">New Temp Roll (${remainingAfter} pages)</span>
                    </div>
                `;
            } else {
                previewContent += `
                    <div class="preview-item">
                        <span class="preview-label">After Filming:</span>
                        <span class="preview-value">Roll fully used, no temp roll created</span>
                    </div>
                `;
            }
        }
        
        previewContent += `
            </div>
            <div class="preview-note">
                <i class="fas fa-info-circle"></i>
                This is a preview. Temp rolls will be updated when filming starts.
            </div>
        `;
        
        previewSection.innerHTML = previewContent;
    }
    
    // Show loading state
    function showLoadingState() {
        const rollsGrid = document.getElementById('rolls-grid');
        rollsGrid.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading rolls...</p>
            </div>
        `;
    }
    
    // Hide loading state
    function hideLoadingState() {
        // Loading state will be replaced by displayRolls()
    }
    
    // Show error state
    function showErrorState(message) {
        const rollsGrid = document.getElementById('rolls-grid');
        rollsGrid.innerHTML = `
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
        const totalRolls = allRolls.length;
        const readyRolls = allRolls.filter(r => r.filming_status === 'ready').length;
        const completedRolls = allRolls.filter(r => r.filming_status === 'completed').length;
        
        // Update stats safely
        const totalRollsElement = document.getElementById('total-rolls');
        const readyRollsElement = document.getElementById('ready-rolls');
        const completedRollsElement = document.getElementById('completed-rolls');
        
        if (totalRollsElement) totalRollsElement.textContent = totalRolls;
        if (readyRollsElement) readyRollsElement.textContent = readyRolls;
        if (completedRollsElement) completedRollsElement.textContent = completedRolls;
    }
    
    // Filter rolls based on search and filter criteria
    function filterRolls() {
        const searchElement = document.getElementById('roll-search');
        const statusFilterElement = document.getElementById('roll-status-filter');
        const filmTypeFilterElement = document.getElementById('film-type-filter');
        const activeTogglePosition = document.querySelector('.toggle-position.active');
        const dependencyInfoPanel = document.getElementById('dependency-info-panel');
        
        const searchTerm = searchElement ? searchElement.value.toLowerCase() : '';
        const statusFilter = statusFilterElement ? statusFilterElement.value : 'all';
        const filmTypeFilter = filmTypeFilterElement ? filmTypeFilterElement.value : 'all';
        const locationFilter = activeTogglePosition ? activeTogglePosition.dataset.position : 'all';
        
        // Show dependency info panel only for "ready" status
        if (dependencyInfoPanel) {
            dependencyInfoPanel.style.display = (statusFilter === 'ready') ? 'block' : 'none';
        }
        
        filteredRolls = allRolls.filter(roll => {
            // Search filter
            const matchesSearch = !searchTerm || 
                (roll.film_number && roll.film_number.toLowerCase().includes(searchTerm)) ||
                (roll.project_name && roll.project_name.toLowerCase().includes(searchTerm)) ||
                (roll.project_archive_id && roll.project_archive_id.toLowerCase().includes(searchTerm));
            
            // Status filter
            const rollStatus = roll.filming_status || 'ready';
            const matchesStatus = statusFilter === 'all' || rollStatus === statusFilter;
            
            // Film type filter
            const rollFilmType = roll.film_type || '16mm';
            const matchesFilmType = filmTypeFilter === 'all' || rollFilmType === filmTypeFilter;
            
            // Location filter based on first digit of film number
            let matchesLocation = true;
            if (locationFilter !== 'all' && roll.film_number && roll.film_number.length >= 1) {
                const firstDigit = roll.film_number.charAt(0);
                if (locationFilter === 'ou') {
                    matchesLocation = firstDigit === '1';
                } else if (locationFilter === 'dw') {
                    matchesLocation = firstDigit === '2';
                }
            }
            
            return matchesSearch && matchesStatus && matchesFilmType && matchesLocation;
        });
        
        displayRolls(filteredRolls);
    }
    
    // Show roll information
    function showRollInfo(rollId) {
        const roll = allRolls.find(r => r.id == rollId);
        if (roll) {
            const info = `Roll Information:
            
Film Number: ${roll.film_number}
Film Type: ${roll.film_type}
Project: ${roll.project_name}
Archive ID: ${roll.project_archive_id}
Status: ${roll.filming_status}
Documents: ${roll.document_count}
Pages: ${roll.pages_used}
Output Directory: ${roll.output_directory}
Directory Exists: ${roll.output_directory_exists ? 'Yes' : 'No'}`;
            
            alert(info);
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
        // Roll selection handlers
        document.getElementById('select-roll-btn').addEventListener('click', function() {
            const selectedCard = document.querySelector('.roll-card.selected');
            if (selectedCard) {
                proceedWithSelectedRoll(selectedCard);
            }
        });
        
        // Search and filter handlers
        document.getElementById('roll-search').addEventListener('input', filterRolls);
        document.getElementById('roll-status-filter').addEventListener('change', filterRolls);
        document.getElementById('film-type-filter').addEventListener('change', filterRolls);
        
        // Three-way toggle handlers
        const togglePositions = document.querySelectorAll('.toggle-position');
        const toggleSlider = document.getElementById('toggle-slider');
        const toggleContainer = document.querySelector('.three-way-toggle');
        
        togglePositions.forEach(position => {
            position.addEventListener('click', function() {
                const location = this.dataset.location;
                console.log('Toggle position clicked:', location);
                
                // Remove active class from all positions
                togglePositions.forEach(pos => pos.classList.remove('active'));
                
                // Add active class to clicked position
                this.classList.add('active');
                
                // Update slider position and container class
                updateTogglePosition(location);
                
                // Filter rolls
                filterRolls();
            });
        });
        
        // Also allow clicking on the slider itself to cycle through positions
        if (toggleSlider) {
            toggleSlider.addEventListener('click', function(e) {
                e.stopPropagation();
                cycleTogglePosition();
            });
        }
        
        // Validation handlers
        document.getElementById('cancel-validation').addEventListener('click', resetToRollSelection);
        document.getElementById('start-filming').addEventListener('click', () => startFilmingProcess(false));
        
        // Filming control handlers
        document.getElementById('pause-filming').addEventListener('click', pauseSession);
        document.getElementById('resume-filming').addEventListener('click', resumeSession);
        document.getElementById('cancel-filming').addEventListener('click', cancelSession);
        
        // Log expansion handler
        document.getElementById('expand-log').addEventListener('click', toggleExpandLog);
        
        // Completion handlers
        document.getElementById('film-another-roll').addEventListener('click', filmAnotherRoll);
        document.getElementById('finish-session').addEventListener('click', finishSession);
        
        // Checklist handlers
        const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateValidationStatus);
        });
        
        // Lighting mode toggle handler
        const lightingToggleBtn = document.getElementById('toggle-filming-lighting-mode');
        if (lightingToggleBtn) {
            lightingToggleBtn.addEventListener('click', toggleFilmingLightingMode);
        }
        
        // Spacebar hotkey for lighting mode toggle
        document.addEventListener('keydown', (event) => {
            if (event.key === ' ') {
                // Check if we're not focused on an input field
                const activeElement = document.activeElement;
                const isInputFocused = activeElement && (
                    activeElement.tagName === 'INPUT' || 
                    activeElement.tagName === 'TEXTAREA' || 
                    activeElement.contentEditable === 'true'
                );
                
                if (!isInputFocused) {
                    const toggleBtn = document.getElementById('toggle-filming-lighting-mode');
                    if (toggleBtn && !toggleBtn.disabled) {
                        toggleFilmingLightingMode();
                        event.preventDefault(); // Prevent page scrolling
                    }
                }
            }
        });
    }
    
    function updateFilmNumber() {
        const selectedRoll = document.querySelector('.roll-card.selected');
        if (selectedRoll) {
            const rollId = selectedRoll.getAttribute('data-roll-id');
            // Default to 16mm since we don't have film type selection in current UI
            const filmNumber = `F-16-${rollId.toString().padStart(4, '0')}`;
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
        
        if (!selectedRoll) {
            showNotification('error', 'Selection Required', 'Please select a roll');
            return;
        }
        
        currentRollId = selectedRoll.getAttribute('data-roll-id');
        
        // Start real SMA filming session
        startSMAFilmingSession(isRecovery);
    }
    
    // Start real SMA filming session
    async function startSMAFilmingSession(isRecovery = false) {
        try {
            // Get film type from validation card
            const filmType = document.getElementById('validation-film-type').textContent || '16mm';
            
            // Check if this is a re-filming operation
            const isReFilming = selectedRollData && selectedRollData.filming_status === 'completed';
            
            // Prepare request data
            const requestData = {
                roll_id: parseInt(currentRollId),
                film_type: filmType,
                recovery: isRecovery,
                re_filming: isReFilming  // Add re-filming flag
            };
            
            // Add initial log entry
            addLogEntry('Starting SMA filming session...', 'info');
            if (isReFilming) {
                addLogEntry('Re-filming operation - temp rolls will be updated', 'warning');
            }
            
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
                
                // Clear saved roll selection state since filming has started
                clearRollSelectionState();
                
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
                addLogEntry(`Roll: ${data.roll_number || 'Unknown'}, Film Type: ${filmType}`, 'info');
                
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
    
    // Update toggle position and styling
    function updateTogglePosition(location) {
        const toggleSlider = document.getElementById('toggle-slider');
        const toggleContainer = document.querySelector('.three-way-toggle');
        
        if (!toggleSlider || !toggleContainer) return;
        
        // Remove all position classes from slider
        toggleSlider.classList.remove('left', 'center', 'right');
        
        // Remove all active classes from container
        toggleContainer.classList.remove('ou-active', 'all-active', 'dw-active');
        
        // Add appropriate classes based on location
        switch (location) {
            case 'ou':
                toggleSlider.classList.add('left');
                toggleContainer.classList.add('ou-active');
                break;
            case 'all':
                toggleSlider.classList.add('center');
                toggleContainer.classList.add('all-active');
                break;
            case 'dw':
                toggleSlider.classList.add('right');
                toggleContainer.classList.add('dw-active');
                break;
        }
    }
    
    // Cycle through toggle positions when clicking on slider
    function cycleTogglePosition() {
        const activePosition = document.querySelector('.toggle-position.active');
        const allPositions = document.querySelectorAll('.toggle-position');
        
        if (!activePosition || !allPositions.length) return;
        
        let nextLocation = 'all'; // default fallback
        
        const currentLocation = activePosition.dataset.location;
        switch (currentLocation) {
            case 'ou':
                nextLocation = 'all';
                break;
            case 'all':
                nextLocation = 'dw';
                break;
            case 'dw':
                nextLocation = 'ou';
                break;
        }
        
        // Find and click the next position
        const nextPosition = document.querySelector(`[data-location="${nextLocation}"]`);
        if (nextPosition) {
            nextPosition.click();
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
            // Reset to roll selection
            resetToRollSelection();
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                resetToRollSelection();
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
                <p>An existing filming session was found for this roll.</p>
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
        // Only count visible checkboxes (exclude hidden re-filming checkbox when not applicable)
        const allCheckboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
        const visibleCheckboxes = Array.from(allCheckboxes).filter(checkbox => {
            const checklistItem = checkbox.closest('.checklist-item');
            return checklistItem && checklistItem.style.display !== 'none';
        });
        
        const checkedCount = visibleCheckboxes.filter(checkbox => checkbox.checked).length;
        const totalCount = visibleCheckboxes.length;
        
        // Update checklist item states
        visibleCheckboxes.forEach(checkbox => {
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
        
        // Save checklist state
        saveChecklistState();
    }
    
    // Reset functions
    function resetToRollSelection() {
        hideCard('completion-card');
        hideCard('filming-process-card');
        hideCard('validation-card');
        showCard('roll-selection-card');
        
        // Clean up temp roll preview
        cleanupTempRollPreview();
        
        // Clear saved state
        clearRollSelectionState();
        
        // Reset filming state
        isFilmingActive = false;
        currentSessionId = null;
        sessionStartTime = null;
        currentStep = 'initialization';
        currentRollId = null;
        selectedRollData = null;
        
        // Disconnect WebSocket session subscription
        if (websocketClient && currentSessionId) {
            websocketClient.unsubscribeFromSession(currentSessionId);
        }
        
        // Deselect all rolls
        document.querySelectorAll('.roll-card').forEach(card => card.classList.remove('selected'));
        
        // Reset roll selection button
        const selectRollBtn = document.getElementById('select-roll-btn');
        if (selectRollBtn) selectRollBtn.disabled = true;
        
        // Clear logs
        const logContent = document.querySelector('.log-content');
        if (logContent) {
            logContent.innerHTML = '';
        }
        
        // Reload rolls to get updated status
        loadRolls();
    }
    
    function resetToProjectSelection() {
        hideCard('completion-card');
        hideCard('filming-process-card');
        hideCard('validation-card');
        hideCard('roll-selection-card');
        showCard('project-selection-card');
        
        // Clear saved state
        clearRollSelectionState();
        
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
        // This function is no longer needed since we load all rolls directly
        // Keeping for compatibility but redirecting to loadRolls
        await loadRolls();
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
        
        // Use processed_documents (actual documents filmed) instead of total_documents
        const actualDocuments = data.processed_documents || data.total_documents || 0;
        if (completionDocuments) completionDocuments.textContent = actualDocuments;
        
        // Use actual pages from roll data, not documents × 2
        const actualPages = data.roll_info ? data.roll_info.pages_used : (actualDocuments || 0);
        if (completionPages) completionPages.textContent = actualPages;
        
        // Calculate duration
        if (sessionStartTime) {
            const duration = new Date() - sessionStartTime;
            const minutes = Math.floor(duration / 60000);
            const seconds = Math.floor((duration % 60000) / 1000);
            if (completionDuration) completionDuration.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else if (data.duration) {
            // Use duration from session data if available
            if (completionDuration) completionDuration.textContent = formatDuration(data.duration);
        }
        
        // Update completion status
        const completionStatus = document.getElementById('completion-status');
        if (completionStatus) {
            completionStatus.textContent = 'Roll filming completed successfully';
            completionStatus.className = 'status-indicator success';
        }
        
            // Fetch and update temp roll instructions from database
    console.log('📊 Session completion data being passed to fetchTempRollInstructions:', data);
    fetchTempRollInstructions(data);
        
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
    
    // Format duration string (e.g., "0:49:28.968528" -> "49:28")
    function formatDuration(durationStr) {
        if (!durationStr) return '0:00';
        
        // Handle different duration formats
        if (durationStr.includes(':')) {
            const parts = durationStr.split(':');
            if (parts.length >= 3) {
                const hours = parseInt(parts[0]);
                const minutes = parseInt(parts[1]);
                const seconds = parseInt(parts[2].split('.')[0]); // Remove microseconds
                
                if (hours > 0) {
                    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                } else {
                    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            }
        }
        
        return durationStr;
    }
    
    // Fetch temp roll instructions from database
    async function fetchTempRollInstructions(sessionData) {
        try {
            console.log('🔍 Fetching temp roll instructions, session data:', sessionData);
            
            // First check if temp roll info is already in session data
            if (sessionData.roll_info && sessionData.roll_info.temp_roll_info) {
                console.log('✅ Using temp roll info from session data:', sessionData.roll_info.temp_roll_info);
                updateTempRollInstructionsFromData(sessionData.roll_info.temp_roll_info);
                return;
            }
            
            // Check if we have roll information for API call
            if (!sessionData.roll_info || !sessionData.roll_info.id) {
                console.warn('⚠️ No roll information available for temp roll check');
                updateTempRollInstructionsFromData(null);
                return;
            }
            
            const rollId = sessionData.roll_info.id;
            
            console.log('🌐 Fetching temp roll info from API for roll:', rollId);
            
            // Fetch temp roll information from the database (now uses the correct endpoint with temp roll info)
            const response = await fetch(`/api/rolls/${rollId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                const rollData = await response.json();
                console.log('📥 Received roll data from API:', rollData);
                
                if (rollData.success) {
                    // Check if a temp roll was created
                    const tempRollInfo = rollData.roll.temp_roll_info;
                    console.log('🎯 Extracted temp roll info from API response:', tempRollInfo);
                    updateTempRollInstructionsFromData(tempRollInfo);
                } else {
                    console.warn('❌ Failed to fetch roll data:', rollData.error);
                    updateTempRollInstructionsFromData(null);
                }
            } else {
                console.warn('❌ Failed to fetch roll data, status:', response.status);
                updateTempRollInstructionsFromData(null);
            }
            
        } catch (error) {
            console.error('❌ Error fetching temp roll instructions:', error);
            updateTempRollInstructionsFromData(null);
        }
    }
    
    // Update temp roll instructions based on database data
    function updateTempRollInstructionsFromData(tempRollInfo) {
        console.log('🔧 updateTempRollInstructionsFromData called with:', tempRollInfo);
        
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
                console.log('📦 Created temp roll instructions container');
            }
        }
        
        const container = document.getElementById('temp-roll-instructions');
        if (!container) {
            console.error('❌ Could not find or create temp roll instructions container');
            return;
        }
        
        // Check if temp roll was created
        if (tempRollInfo && tempRollInfo.created_temp_roll) {
            console.log('✅ Temp roll was created, displaying instructions');
            const tempRoll = tempRollInfo.created_temp_roll;
            container.innerHTML = `
                <div class="temp-roll-instruction-card">
                    <div class="instruction-header">
                        <i class="fas fa-cut"></i>
                        <h4>Temp Roll Created</h4>
                    </div>
                    <div class="instruction-content">
                        <p><strong>A temporary roll has been created from the remaining film:</strong></p>
                        <ul class="instruction-list">
                            <li><strong>Temp Roll ID:</strong> ${tempRoll.temp_roll_id}</li>
                            <li><strong>Remaining Capacity:</strong> ${tempRoll.usable_capacity} pages</li>
                            <li><strong>Film Type:</strong> ${tempRoll.film_type}</li>
                            <li><strong>Status:</strong> ${tempRoll.status}</li>
                        </ul>
                        <div class="instruction-note">
                            <i class="fas fa-info-circle"></i>
                            Cut the tape and store this temp roll for future filming sessions.
                        </div>
                    </div>
                </div>
            `;
        } else {
            console.log('ℹ️ No temp roll was created, displaying standard completion message');
            // No temp roll created - check if roll is full or nearly full
            container.innerHTML = `
                <div class="temp-roll-instruction-card discard">
                    <div class="instruction-header">
                        <i class="fas fa-check-circle"></i>
                        <h4>Film Roll Complete</h4>
                    </div>
                    <div class="instruction-content">
                        <p><strong>Cut the tape and remove the film roll.</strong></p>
                        <div class="instruction-note">
                            <i class="fas fa-info-circle"></i>
                            ${tempRollInfo && tempRollInfo.reason ? tempRollInfo.reason : 'This roll has been fully utilized - no temp roll needed.'}
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
    
    async function revertRollToReady(rollId, rollCardElement) {
        try {
            if (!confirm('Revert this roll to Ready? This will cancel any active session and reset its status.')) {
                return;
            }
            addLogEntry(`Reverting roll ${rollId} to Ready...`, 'warning');
            
            // Attempt to cancel any active sessions for this roll
            let cancelledSessions = 0;
            try {
                const sessionsResp = await fetch('/api/sma/active-sessions/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                });
                if (sessionsResp.ok) {
                    const sessionsData = await sessionsResp.json();
                    if (sessionsData.success && Array.isArray(sessionsData.active_sessions)) {
                        const related = sessionsData.active_sessions.filter(s => String(s.roll_id) === String(rollId));
                        await Promise.all(related.map(async (s) => {
                            try {
                                const cancelResp = await fetch(`/api/sma/session/${s.session_id}/cancel/`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': getCsrfToken()
                                    }
                                });
                                const cancelData = await cancelResp.json();
                                if (cancelResp.ok && cancelData.success) {
                                    cancelledSessions += 1;
                                }
                            } catch (err) {
                                console.warn('Failed to cancel session', s.session_id, err);
                            }
                        }));
                    }
                }
            } catch (e) {
                console.warn('Failed to query/cancel active sessions for roll', rollId, e);
            }
            
            // Reset roll status to ready
            const resp = await fetch(`/api/rolls/${rollId}/filming-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ status: 'ready' })
            });
            const data = await resp.json();
            
            if (resp.ok && (data.status === 'success' || data.success)) {
                showNotification('success', 'Reverted', `Roll reverted to Ready${cancelledSessions ? ` (cancelled ${cancelledSessions} session${cancelledSessions>1?'s':''})` : ''}`, 4000);
                addLogEntry(`Roll ${rollId} set to Ready`, 'info');
                
                // Refresh list to reflect the new state
                await loadRolls();
                updateQuickStats();
            } else {
                throw new Error(data.message || data.error || 'Failed to update roll status');
            }
        } catch (error) {
            console.error('Revert to Ready failed:', error);
            showNotification('error', 'Revert Failed', error.message || 'Could not revert roll to Ready', 6000);
            addLogEntry(`Revert failed: ${error.message}`, 'error');
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
    
    // Completion action handlers
    function filmAnotherRoll() {
        // Reset to roll selection to film another roll
        addLogEntry('Starting new roll selection...', 'info');
        showNotification('info', 'New Roll', 'Selecting another roll for filming');
        
        // Reset to roll selection
        resetToRollSelection();
    }
    
    function finishSession() {
        // Finish the filming session and return to main interface
        addLogEntry('Finishing filming session...', 'info');
        showNotification('success', 'Session Complete', 'Filming session finished successfully');
        
        // Clean up session state
        isFilmingActive = false;
        currentSessionId = null;
        sessionStartTime = null;
        currentStep = 'initialization';
        currentRollId = null;
        selectedRollData = null;
        
        // Disconnect WebSocket session subscription
        if (websocketClient && currentSessionId) {
            websocketClient.unsubscribeFromSession(currentSessionId);
        }
        
        // Clear saved state
        clearRollSelectionState();
        
        // Return to roll selection
        resetToRollSelection();
        
        // Show completion message
        setTimeout(() => {
            showNotification('info', 'Ready for Next Session', 'You can now start a new filming session');
        }, 1000);
    }
    
    // Automatically restore an active session
    async function restoreActiveSession(session) {
        try {
            console.log('🔄 Restoring active session:', session.session_id);
            console.log('📊 Session details:', {
                roll: session.roll_number,
                status: session.status,
                progress: session.progress_percent
            });
            
            // Set global state variables
            currentSessionId = session.session_id;
            currentRollId = session.roll_id;
            isFilmingActive = session.status === 'running';
            sessionStartTime = session.started_at ? new Date(session.started_at) : new Date();
            
            // Hide all selection cards and show filming interface
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
            
            // Load rolls in background for potential future use
            await loadRolls();
            
            // Show restoration notification
            showNotification('info', 'Session Restored', 
                `Resumed filming session for ${session.roll_number}`);
            
        } catch (error) {
            console.error('Error restoring session:', error);
            showNotification('error', 'Restoration Error', 
                'Failed to restore session. Starting fresh.');
            
            // Fall back to normal initialization
            await loadRolls();
            showCard('roll-selection-card');
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
        
        // Use processed_documents (actual documents filmed) instead of total_documents
        const actualDocuments = session.processed_documents || session.total_documents || 0;
        if (completionDocuments) completionDocuments.textContent = actualDocuments;
        
        // Use actual pages from roll data, not documents × 2
        const actualPages = session.roll_info ? session.roll_info.pages_used : (actualDocuments || 0);
        if (completionPages) completionPages.textContent = actualPages;
        
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
        } else if (session.duration) {
            // Use duration from session data if available
            if (completionDuration) completionDuration.textContent = formatDuration(session.duration);
        }
        
        // Update completion status
        const completionStatus = document.getElementById('completion-status');
        if (completionStatus) {
            completionStatus.textContent = 'Roll filming completed successfully';
            completionStatus.className = 'status-indicator success';
        }
        
        // Fetch and update temp roll instructions for restored session
        fetchTempRollInstructions(session);
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
    
    // Clean up temp roll preview section
    function cleanupTempRollPreview() {
        // Remove any existing temp roll preview sections
        const existingPreview = document.querySelector('.temp-roll-preview-section');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        // Remove any existing strategy reason sections
        const existingStrategyReason = document.getElementById('temp-roll-strategy-reason');
        if (existingStrategyReason) {
            existingStrategyReason.remove();
        }
    }
    
    // Lighting mode control functions
    function toggleFilmingLightingMode() {
        console.log('toggleFilmingLightingMode called - using WebSocket consumer');
        
        const lightingToggleBtn = document.getElementById('toggle-filming-lighting-mode');
        
        // Add switching animation
        if (lightingToggleBtn) {
            lightingToggleBtn.classList.add('switching');
            lightingToggleBtn.disabled = true;
        }
        
        // Determine target mode (opposite of current)
        const targetMode = isLightMode ? 'dark' : 'light';
        
        // Send command to WebSocket consumer
        sendLightingCommand(targetMode)
            .then(success => {
                if (success) {
                    // Toggle our internal state
                    isLightMode = !isLightMode;
                    
                    // Save state to localStorage
                    localStorage.setItem('filmingLightMode', isLightMode.toString());
                    
                    const currentMode = isLightMode ? 'light' : 'dark';
                    
                    showNotification('success', 'Lighting Mode Changed', 
                        `Switched to ${currentMode} mode for film handling`, 3000);
                } else {
                    showNotification('error', 'Error', 'Failed to toggle lighting mode', 5000);
                }
            })
            .finally(() => {
                // Remove animation and re-enable button
                if (lightingToggleBtn) {
                    lightingToggleBtn.classList.remove('switching');
                    lightingToggleBtn.disabled = false;
                }
                
                // Update button text
                updateFilmingLightingModeButton();
            });
    }
    
    async function sendLightingCommand(mode) {
        try {
            const response = await fetch('/control_relay/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: new URLSearchParams({
                    'action': mode
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                console.log('Lighting command sent successfully:', mode);
                return true;
            } else {
                console.error('Lighting command failed:', data.message || 'Unknown error');
                return false;
            }
        } catch (error) {
            console.error('Error sending lighting command:', error);
            return false;
        }
    }
    
    function updateFilmingLightingModeButton() {
        const lightingToggleBtn = document.getElementById('toggle-filming-lighting-mode');
        const lightingModeText = document.getElementById('filming-lighting-mode-text');
        
        if (!lightingToggleBtn || !lightingModeText) return;
        
        // Always show as available since we assume relay is connected
        if (isLightMode) {
            lightingModeText.textContent = 'Switch to Dark Mode';
            lightingToggleBtn.className = 'btn btn-sm btn-warning';
            lightingToggleBtn.disabled = false;
            lightingToggleBtn.innerHTML = '<i class="fas fa-moon"></i> <span id="filming-lighting-mode-text">Switch to Dark Mode</span>';
        } else {
            lightingModeText.textContent = 'Switch to Light Mode';
            lightingToggleBtn.className = 'btn btn-sm btn-info';
            lightingToggleBtn.disabled = false;
            lightingToggleBtn.innerHTML = '<i class="fas fa-sun"></i> <span id="filming-lighting-mode-text">Switch to Light Mode</span>';
        }
    }
    
    function initializeFilmingLightingMode() {
        // Check if we have a saved lighting mode preference
        const savedMode = localStorage.getItem('filmingLightMode');
        if (savedMode !== null) {
            isLightMode = savedMode === 'true';
        }
        
        console.log('Initialized filming lighting mode:', isLightMode ? 'light' : 'dark');
        
        // Update button state
        updateFilmingLightingModeButton();
    }
    
    // State persistence functions
    function saveRollSelectionState() {
        try {
            const selectedCard = document.querySelector('.roll-card.selected');
            if (selectedCard && selectedRollData) {
                const state = {
                    rollId: selectedCard.getAttribute('data-roll-id'),
                    rollData: selectedRollData,
                    timestamp: Date.now(),
                    validationCardVisible: document.getElementById('validation-card').style.display !== 'none'
                };
                
                localStorage.setItem('film_selected_roll', JSON.stringify(state));
                console.log('Roll selection state saved:', state.rollId);
            }
        } catch (error) {
            console.error('Error saving roll selection state:', error);
        }
    }
    
    function saveChecklistState() {
        try {
            const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
            const checklistState = {};
            
            checkboxes.forEach(checkbox => {
                checklistState[checkbox.id] = checkbox.checked;
            });
            
            localStorage.setItem('film_checklist_state', JSON.stringify({
                state: checklistState,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.error('Error saving checklist state:', error);
        }
    }
    
    function restoreRollSelectionState() {
        try {
            const savedState = localStorage.getItem('film_selected_roll');
            if (!savedState) return false;
            
            const state = JSON.parse(savedState);
            
            // Check if state is not too old (24 hours)
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            if (Date.now() - state.timestamp > maxAge) {
                localStorage.removeItem('film_selected_roll');
                return false;
            }
            
            // Find the roll in the loaded rolls
            const roll = allRolls.find(r => r.id == state.rollId);
            if (!roll) {
                console.log('Previously selected roll no longer available');
                localStorage.removeItem('film_selected_roll');
                return false;
            }
            
            // Restore the selection
            selectedRollData = state.rollData;
            
            // Find and select the roll card
            const rollCard = document.querySelector(`[data-roll-id="${state.rollId}"]`);
            if (rollCard) {
                highlightRoll(rollCard);
                
                // If validation card was visible, restore it
                if (state.validationCardVisible) {
                    const filmNumber = rollCard.querySelector('.roll-film-number').textContent;
                    const filmType = rollCard.querySelector('.roll-film-type').textContent;
                    const projectName = rollCard.querySelector('.project-name').textContent;
                    const archiveId = rollCard.querySelector('.archive-id').textContent;
                    const documentCount = rollCard.querySelectorAll('.roll-detail-value')[0].textContent;
                    const pageCount = rollCard.querySelectorAll('.roll-detail-value')[1].textContent;
                    const outputDir = rollCard.querySelectorAll('.roll-detail-value')[2].textContent;
                    const dirExists = rollCard.querySelector('.directory-status').classList.contains('exists');
                    const isCompleted = rollCard.classList.contains('completed');
                    
                    // Update validation card and show it
                    updateValidationCard(state.rollId, filmNumber, filmType, projectName, archiveId, documentCount, pageCount, outputDir, dirExists, roll, isCompleted);
                    showCard('validation-card');
                    
                    // Restore checklist state
                    setTimeout(() => restoreChecklistState(), 100);
                    
                    console.log('Roll selection and validation state restored for roll:', filmNumber);
                    showNotification('info', 'State Restored', `Restored selection for roll ${filmNumber}`, 3000);
                    
                    return true;
                }
            }
            
            return false;
        } catch (error) {
            console.error('Error restoring roll selection state:', error);
            localStorage.removeItem('film_selected_roll');
            return false;
        }
    }
    
    function restoreChecklistState() {
        try {
            const savedState = localStorage.getItem('film_checklist_state');
            if (!savedState) return;
            
            const state = JSON.parse(savedState);
            
            // Check if state is not too old (24 hours)
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            if (Date.now() - state.timestamp > maxAge) {
                localStorage.removeItem('film_checklist_state');
                return;
            }
            
            // Restore checkbox states
            Object.entries(state.state).forEach(([checkboxId, checked]) => {
                const checkbox = document.getElementById(checkboxId);
                if (checkbox) {
                    checkbox.checked = checked;
                }
            });
            
            // Update validation status after restoring
            updateValidationStatus();
            
            console.log('Checklist state restored');
        } catch (error) {
            console.error('Error restoring checklist state:', error);
            localStorage.removeItem('film_checklist_state');
        }
    }
    
    function clearRollSelectionState() {
        try {
            localStorage.removeItem('film_selected_roll');
            localStorage.removeItem('film_checklist_state');
            console.log('Roll selection state cleared');
        } catch (error) {
            console.error('Error clearing roll selection state:', error);
        }
    }
    
    /**
     * Show the strategy reason in a dedicated section
     */
    function showStrategyReason(reason) {
        let reasonSection = document.getElementById('temp-roll-strategy-reason');
        
        if (!reasonSection) {
            // Create reason section
            reasonSection = document.createElement('div');
            reasonSection.id = 'temp-roll-strategy-reason';
            reasonSection.className = 'strategy-reason-section';
            
            // Insert after the temp roll instructions
            const tempRollInstructions = document.getElementById('temp-roll-instructions');
            if (tempRollInstructions && tempRollInstructions.parentNode) {
                tempRollInstructions.parentNode.insertBefore(reasonSection, tempRollInstructions.nextSibling);
            }
        }
        
        reasonSection.innerHTML = `
            <div class="strategy-reason">
                <i class="fas fa-info-circle"></i>
                <span>${reason}</span>
            </div>
        `;
    }
    
    // Display filming priority summary
    function displayFilmingPrioritySummary(rolls) {
        if (!rolls || rolls.length === 0) return;
        
        // Count rolls by priority
        const priorityCounts = {
            creator: 0,
            immediate: 0,
            waiting: 0,
            problem: 0,
            total_ready: 0
        };
        
        let recommendedNext = null;
        
        rolls.forEach(roll => {
            if (roll.filming_status === 'ready' && roll.filming_priority) {
                const tier = roll.filming_priority.priority_tier;
                if (priorityCounts.hasOwnProperty(tier)) {
                    priorityCounts[tier]++;
                }
                if (tier === 'creator' || tier === 'immediate') {
                    priorityCounts.total_ready++;
                    if (!recommendedNext && tier === 'creator') {
                        recommendedNext = roll;
                    }
                }
                if (!recommendedNext && tier === 'immediate') {
                    recommendedNext = roll;
                }
            }
        });
        
        // Create or update priority summary panel
        let summaryPanel = document.getElementById('filming-priority-summary');
        if (!summaryPanel) {
            summaryPanel = document.createElement('div');
            summaryPanel.id = 'filming-priority-summary';
            summaryPanel.className = 'priority-summary-panel';
            
            // Insert after search filters, before dependency info
            const searchFilter = document.querySelector('.search-filter');
            if (searchFilter && searchFilter.parentNode) {
                searchFilter.parentNode.insertBefore(summaryPanel, searchFilter.nextSibling);
            }
        }
        
        // Generate summary content
        let summaryHTML = `
            <div class="priority-summary-header">
                <h4><i class="fas fa-chart-bar"></i> Filming Priority Summary</h4>
            </div>
            <div class="priority-summary-content">
                <div class="priority-stats">
                    <div class="stat-item priority-creator-stat">
                        <div class="stat-number">${priorityCounts.creator}</div>
                        <div class="stat-label">High Priority<br/><small>Creates temp rolls</small></div>
                    </div>
                    <div class="stat-item priority-immediate-stat">
                        <div class="stat-number">${priorityCounts.immediate}</div>
                        <div class="stat-label">Ready Now<br/><small>Independent</small></div>
                    </div>
                    <div class="stat-item priority-waiting-stat">
                        <div class="stat-number">${priorityCounts.waiting}</div>
                        <div class="stat-label">Waiting<br/><small>Need dependencies</small></div>
                    </div>
                    <div class="stat-item priority-problem-stat">
                        <div class="stat-number">${priorityCounts.problem}</div>
                        <div class="stat-label">Need Attention<br/><small>Have issues</small></div>
                    </div>
                </div>
        `;
        
        if (recommendedNext) {
            const reason = recommendedNext.filming_priority.priority_tier === 'creator' 
                ? `Creates temp roll for other rolls` 
                : 'Ready to film immediately';
            
            summaryHTML += `
                <div class="recommended-next">
                    <div class="recommendation-header">
                        <i class="fas fa-bullseye"></i> Recommended Next
                    </div>
                    <div class="recommendation-content">
                        <strong>Roll ${recommendedNext.id}</strong> - ${recommendedNext.project_archive_id} 
                        <span class="recommendation-reason">${reason}</span>
                        <button class="btn-film-recommended" onclick="selectRollForFilming(${recommendedNext.id})">
                            <i class="fas fa-video"></i> Film This Roll
                        </button>
                    </div>
                </div>
            `;
        } else if (priorityCounts.total_ready === 0) {
            summaryHTML += `
                <div class="no-ready-rolls">
                    <i class="fas fa-info-circle"></i> No rolls ready for immediate filming. 
                    Check waiting and problem rolls above.
                </div>
            `;
        }
        
        summaryHTML += `
            </div>
        `;
        
        summaryPanel.innerHTML = summaryHTML;
        
        // Show/hide based on filter
        const statusFilter = document.getElementById('roll-status-filter');
        const showSummary = !statusFilter || statusFilter.value === 'all' || statusFilter.value === 'ready';
        summaryPanel.style.display = showSummary ? 'block' : 'none';
    }
    
    // Function to handle filming a recommended roll
    window.selectRollForFilming = function(rollId) {
        // Find the roll card and trigger filming
        const rollCard = document.querySelector(`.roll-card[data-roll-id="${rollId}"]`);
        if (rollCard) {
            const filmButton = rollCard.querySelector('.btn-film');
            if (filmButton) {
                filmButton.click();
            }
        }
    };
});