// Development Dashboard JavaScript

class DevelopmentDashboard {
    constructor() {
        this.selectedRoll = null;
        this.currentSession = null;
        this.timerInterval = null;
        this.progressInterval = null;
        this.refreshInterval = null;
        this.isLightMode = undefined;
        this.isRelayConnected = false;
        
        // Timer state for restoration
        this.startTime = null;
        this.totalDuration = null;
        this.developmentDuration = null;
        this.filmLength = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.restoreStateFromStorage();
        this.loadInitialData();
        this.startAutoRefresh();
        
        // Initialize lighting mode state after a delay
        setTimeout(() => {
            this.initializeLightingMode();
        }, 2000);
    }
    
    // ===== LOCALSTORAGE PERSISTENCE METHODS =====
    
    saveStateToStorage() {
        const state = {
            selectedRoll: this.selectedRoll,
            isLightMode: this.isLightMode,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem('developmentDashboardState', JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save state to localStorage:', error);
        }
    }
    
    restoreStateFromStorage() {
        try {
            const savedState = localStorage.getItem('developmentDashboardState');
            if (savedState) {
                const state = JSON.parse(savedState);
                
                // Check if state is not too old (24 hours)
                const maxAge = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
                if (Date.now() - state.timestamp < maxAge) {
                    // Restore lighting mode preference
                    if (state.isLightMode !== undefined) {
                        this.isLightMode = state.isLightMode;
                    }
                    
                    // Note: selectedRoll will be restored after loading rolls from server
                    // to ensure the roll still exists and has current data
                    this.pendingRollSelection = state.selectedRoll;
                } else {
                    // Clear old state
                    this.clearStoredState();
                }
            }
        } catch (error) {
            console.warn('Failed to restore state from localStorage:', error);
            this.clearStoredState();
        }
    }
    
    clearStoredState() {
        try {
            localStorage.removeItem('developmentDashboardState');
        } catch (error) {
            console.warn('Failed to clear localStorage:', error);
        }
    }
    
    // ===== ACTIVE SESSION RESTORATION =====
    
    async checkForActiveSession() {
        try {
            const response = await fetch('/api/development/active-session/');
            const data = await response.json();
            
            if (data.success && data.session) {
                const session = data.session;
                this.currentSession = session.session_id;
                this.developmentDuration = session.duration_minutes;
                this.filmLength = session.film_length_meters;
                
                // Restore timer from server start time
                if (session.started_at) {
                    this.restoreTimerFromServerTime(session.started_at, session.duration_minutes);
                }
                
                // Find and select the roll being developed
                if (session.roll_id) {
                    this.restoreRollSelection(session.roll_id);
                }
                
                console.log('Restored active development session:', session.session_id);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error checking for active session:', error);
            return false;
        }
    }
    
    restoreTimerFromServerTime(startTimeISO, durationMinutes) {
        const serverStartTime = new Date(startTimeISO).getTime();
        const now = Date.now();
        const elapsed = now - serverStartTime;
        const totalDuration = durationMinutes * 60 * 1000; // Convert to milliseconds
        
        // Check if development should be complete
        if (elapsed >= totalDuration) {
            // Development time has passed, automatically complete it
            this.showDevelopmentTimer();
            this.showTimerComplete();
            
            // Show notification and auto-complete after delay
            this.showNotification('info', 'Development Time Exceeded', 
                'Development time has already passed. Automatically completing development.');
            
            setTimeout(() => {
                this.completeDevelopment();
            }, 3000); // 3 second delay to show the message
            return;
        }
        
        // Set timer state for ongoing development
        this.startTime = serverStartTime;
        this.totalDuration = totalDuration;
        
        // Show timer and start countdown from current position
        this.showDevelopmentTimer();
        this.updateLocalTimer(); // Update display immediately
        
        // Start interval for continued updates
        this.timerInterval = setInterval(() => {
            this.updateLocalTimer();
        }, 1000);
        
        console.log(`Timer restored: ${elapsed/1000}s elapsed of ${totalDuration/1000}s total`);
    }
    
    showTimerComplete() {
        const timeElement = document.getElementById('timer-time');
        const progressElement = document.getElementById('development-progress');
        const progressCircle = document.getElementById('timer-progress-circle');
        
        if (timeElement) {
            timeElement.textContent = '00:00';
            timeElement.style.color = '#28a745'; // Green color
        }
        
        if (progressElement) {
            progressElement.textContent = '100.0%';
        }
        
        if (progressCircle) {
            progressCircle.style.strokeDashoffset = 0; // Full circle
        }
        
        // Flash the timer to draw attention
        this.flashTimer();
        
        // Show completion notification
        this.showNotification('success', 'Development Time Complete!', 
            'The development timer has finished. Please check the development and mark as complete.');
    }
    
    async restoreRollSelection(rollId) {
        // This will be called after rolls are loaded
        this.pendingRollSelectionById = rollId;
    }
    
    bindEvents() {
        // Refresh buttons
        document.getElementById('refresh-dashboard').addEventListener('click', () => {
            this.loadInitialData();
        });
        
        document.getElementById('refresh-rolls').addEventListener('click', () => {
            this.loadRolls();
        });
        
        document.getElementById('refresh-chemicals').addEventListener('click', () => {
            this.loadChemicalStatus();
        });
        
        // Development actions
        document.getElementById('start-development').addEventListener('click', () => {
            this.startDevelopment();
        });
        
        document.getElementById('complete-development').addEventListener('click', () => {
            this.completeDevelopment();
        });
        
        document.getElementById('cancel-development').addEventListener('click', () => {
            this.cancelDevelopment();
        });
        
        // Create and print label button
        document.getElementById('create-label').addEventListener('click', () => {
            this.createAndPrintLabel();
        });
        
        // Lighting mode toggle for film handling
        document.getElementById('toggle-lighting-mode').addEventListener('click', () => {
            this.toggleLightingMode();
        });
        
        // Spacebar hotkey for lighting mode toggle (always available)
        document.addEventListener('keydown', (event) => {
            // Handle spacebar for lighting toggle - always available
            if (event.key === ' ') {
                // Check if we're not focused on an input field
                const activeElement = document.activeElement;
                const isInputFocused = activeElement && (
                    activeElement.tagName === 'INPUT' || 
                    activeElement.tagName === 'TEXTAREA' || 
                    activeElement.contentEditable === 'true'
                );
                
                if (!isInputFocused) {
                    const toggleBtn = document.getElementById('toggle-lighting-mode');
                    if (toggleBtn && !toggleBtn.disabled) {
                        this.toggleLightingMode();
                        event.preventDefault(); // Prevent page scrolling
                    }
                }
            }
        });
        
        // Chemical reset buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.chemical-reset-btn')) {
                const chemicalType = e.target.closest('.chemical-reset-btn').dataset.chemical;
                this.showChemicalResetModal(chemicalType);
            }
        });
        
        // Chemical insertion button
        document.getElementById('insert-chemicals').addEventListener('click', () => {
            this.showChemicalInsertionModal();
        });
        
        // Modal events
        document.getElementById('confirm-reset').addEventListener('click', () => {
            this.confirmChemicalReset();
        });
        
        document.getElementById('confirm-chemical-insertion').addEventListener('click', () => {
            this.confirmChemicalInsertion();
        });
        
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideModal();
            });
        });
        
        // Close modal on outside click
        document.getElementById('chemical-reset-modal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.hideModal();
            }
        });
        
        document.getElementById('chemical-insertion-modal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.hideModal();
            }
        });
        
        // Chemical checklist handling
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('chemical-checkbox')) {
                this.updateChemicalChecklist();
            }
        });
        
        // Density tracking
        const saveButton = document.getElementById('save-density');
        if (saveButton) {
            saveButton.addEventListener('click', () => this.saveDensityMeasurement());
        }
    }
    
    async loadInitialData() {
        try {
            // First check for active development session
            await this.checkForActiveSession();
            
            // Then load all data
            await Promise.all([
                this.loadRolls(),
                this.loadChemicalStatus(),
                this.loadDevelopmentHistory()
            ]);
            this.updateStatusOverview();
            
            // Ensure lighting toggle button is always visible in header
            const lightingToggleBtn = document.getElementById('toggle-lighting-mode');
            if (lightingToggleBtn) {
                lightingToggleBtn.style.display = 'inline-flex';
            }
            
            // Update lighting button state after a short delay to allow connections to be established
            setTimeout(() => {
                this.updateLightingModeButton();
            }, 2000);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('error', 'Error', 'Failed to load dashboard data');
        }
    }
    
    async loadRolls() {
        try {
            const response = await fetch('/api/development/rolls/');
            const data = await response.json();
            
            if (data.success) {
                this.renderRolls(data.rolls);
                this.updateStatusCounts(data.rolls);
                
                // Handle pending roll selections after rolls are loaded
                this.handlePendingRollSelection(data.rolls);
            } else {
                throw new Error(data.error || 'Failed to load rolls');
            }
        } catch (error) {
            console.error('Error loading rolls:', error);
            this.showNotification('error', 'Error', 'Failed to load rolls for development');
        }
    }
    
    handlePendingRollSelection(rolls) {
        // Handle roll selection by ID (from active session)
        if (this.pendingRollSelectionById) {
            const roll = rolls.find(r => r.id === this.pendingRollSelectionById);
            if (roll) {
                this.selectRoll(roll);
                console.log('Restored roll selection from active session:', roll.film_number);
            }
            this.pendingRollSelectionById = null;
        }
        // Handle roll selection from localStorage (if no active session)
        else if (this.pendingRollSelection && !this.currentSession) {
            const roll = rolls.find(r => r.id === this.pendingRollSelection.id);
            if (roll) {
                this.selectRoll(roll);
                console.log('Restored roll selection from localStorage:', roll.film_number);
            }
            this.pendingRollSelection = null;
        }
    }
    
    renderRolls(rolls) {
        const container = document.getElementById('ready-rolls-grid');
        
        if (rolls.length === 0) {
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-film"></i>
                    <p>No rolls available for development</p>
                    <small>Complete filming first to see rolls here</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = rolls.map(roll => {
            const isSelected = this.selectedRoll && this.selectedRoll.id === roll.id;
            const isDeveloping = roll.is_developing;
            const isCompleted = roll.is_completed;
            const canDevelop = roll.can_develop;
            
            let statusClass = 'pending';
            let statusIcon = 'fas fa-clock';
            let statusText = 'Ready';
            
            if (isDeveloping) {
                statusClass = 'developing';
                statusIcon = 'fas fa-cog fa-spin';
                statusText = 'Developing';
            } else if (isCompleted) {
                statusClass = 'completed';
                statusIcon = 'fas fa-check-circle';
                statusText = 'Completed';
            } else if (!canDevelop) {
                statusClass = 'error';
                statusIcon = 'fas fa-exclamation-triangle';
                statusText = 'Cannot Develop';
            }
            
            return `
                <div class="roll-card ${statusClass} ${isSelected ? 'selected' : ''}" 
                     data-roll-id="${roll.id}" 
                     onclick="window.developmentDashboard.selectRoll(${JSON.stringify(roll).replace(/"/g, '&quot;')})">
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">${roll.film_number}</div>
                            <div class="roll-film-type">${roll.film_type}</div>
                        </div>
                        <div class="roll-status">
                            <i class="${statusIcon}"></i>
                            <span>${statusText}</span>
                        </div>
                    </div>
                    <div class="roll-details">
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Project:</span>
                            <span class="roll-detail-value">${roll.project_name}</span>
                        </div>
                        <div class="roll-detail-item">
                            <span class="roll-detail-label">Pages:</span>
                            <span class="roll-detail-value">${roll.pages_used}</span>
                        </div>
                        ${roll.development_completed_at ? `
                            <div class="roll-detail-item">
                                <span class="roll-detail-label">Completed:</span>
                                <span class="roll-detail-value">${this.formatDateTime(roll.development_completed_at)}</span>
                            </div>
                        ` : ''}
                        ${roll.development_progress > 0 ? `
                            <div class="roll-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${roll.development_progress}%"></div>
                                </div>
                                <span class="progress-text">${roll.development_progress.toFixed(1)}%</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    selectRoll(roll) {
        this.selectedRoll = roll;
        
        // Save state to localStorage
        this.saveStateToStorage();
        
        // Update UI selection
        document.querySelectorAll('.roll-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-roll-id="${roll.id}"]`).classList.add('selected');
        
        // Show roll info
        this.showSelectedRollInfo(roll);
        
        // Calculate development duration for this roll
        const totalFrames = roll.pages_used + 100; // Add leader/trailer
        const filmLengthM = totalFrames / 100.0; // 1cm per frame, convert to meters
        const developmentDuration = filmLengthM; // 1 minute per meter
        
        // Enable/disable start button based on roll status
        const startBtn = document.getElementById('start-development');
        const createLabelBtn = document.getElementById('create-label');
        const isDeveloping = roll.is_developing;
        const isCompleted = roll.is_completed;
        const canDevelop = roll.can_develop;
        
        // Update button state and text
        if (isDeveloping) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-cog fa-spin"></i> Currently Developing';
            createLabelBtn.style.display = 'none';
            // Timer should already be restored from active session check
            if (!this.timerInterval && this.currentSession) {
                this.showDevelopmentTimer();
            }
        } else if (isCompleted) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-check"></i> Already Developed';
            createLabelBtn.style.display = 'inline-flex';
            this.hideDevelopmentTimer();
            this.stopLocalTimer();
        } else if (canDevelop) {
            startBtn.disabled = false;
            startBtn.innerHTML = `<i class="fas fa-play"></i> Start Development (${developmentDuration.toFixed(1)} min)`;
            createLabelBtn.style.display = 'none';
            this.hideDevelopmentTimer();
            this.stopLocalTimer();
        } else {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-times"></i> Cannot Develop';
            createLabelBtn.style.display = 'none';
            this.hideDevelopmentTimer();
            this.stopLocalTimer();
        }
        
        // Ensure lighting toggle button is always visible and updated
        const lightingToggleBtn = document.getElementById('toggle-lighting-mode');
        if (lightingToggleBtn) {
            lightingToggleBtn.style.display = 'inline-flex';
            this.updateLightingModeButton();
        }
    }
    
    showSelectedRollInfo(roll) {
        const infoContainer = document.getElementById('selected-roll-info');
        const noSelectionMessage = document.getElementById('no-selection-message');
        
        // Calculate film metrics
        const totalFrames = roll.pages_used + 100; // Add leader/trailer
        const filmLengthM = totalFrames / 100.0; // 1cm per frame, convert to meters
        const developmentDuration = filmLengthM; // 1 minute per meter
        
        document.getElementById('selected-film-number').textContent = roll.film_number;
        document.getElementById('selected-film-type').textContent = roll.film_type;
        document.getElementById('selected-project').textContent = roll.project_name;
        document.getElementById('selected-pages').textContent = `${roll.pages_used} pages (${filmLengthM.toFixed(1)}m film, ${developmentDuration.toFixed(1)} min dev)`;
        
        infoContainer.style.display = 'block';
        noSelectionMessage.style.display = 'none';
    }
    
    async startDevelopment() {
        if (!this.selectedRoll) return;
        
        try {
            const response = await fetch('/api/development/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    roll_id: this.selectedRoll.id
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = data.session_id;
                this.developmentDuration = data.duration_minutes;
                this.filmLength = data.film_length_meters;
                
                // Save state to localStorage
                this.saveStateToStorage();
                
                let successMessage = `Development started for roll ${this.selectedRoll.film_number} - Duration: ${this.developmentDuration.toFixed(1)} minutes (${this.filmLength.toFixed(1)}m film)`;
                
                // Show chemical warnings if any (but still allow development to proceed)
                if (data.chemical_warnings && data.chemical_warnings.length > 0) {
                    this.showNotification('warning', 'Chemical Level Warning', 
                        `Development started successfully, but note: ${data.chemical_warnings.join(', ')}`);
                } else {
                    this.showNotification('success', 'Development Started', successMessage);
                }
                
                // Update UI and start local timer with actual duration
                this.showDevelopmentTimer();
                this.startLocalTimer(this.developmentDuration);
                
                // Refresh data once
                this.loadRolls();
                this.loadChemicalStatus();
            } else {
                if (data.warnings && data.warnings.length > 0) {
                    this.showNotification('error', 'Chemical Capacity Exceeded', 
                        `Cannot start development: ${data.warnings.join(', ')}`);
                } else {
                    this.showNotification('error', 'Error', data.error || 'Failed to start development');
                }
            }
        } catch (error) {
            console.error('Error starting development:', error);
            this.showNotification('error', 'Error', 'Failed to start development');
        }
    }
    
    async completeDevelopment() {
        if (!this.currentSession) return;
        
        try {
            console.log('Completing development for session:', this.currentSession);
            
            const csrfToken = this.getCSRFToken();
            console.log('CSRF token obtained:', csrfToken ? 'Yes' : 'No');
            
            const response = await fetch('/api/development/complete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    session_id: this.currentSession
                })
            });
            
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                this.showNotification('success', 'Development Complete', 
                    `Development completed for roll ${this.selectedRoll.film_number}`);
                
                // Reset UI and state
                this.hideDevelopmentTimer();
                this.stopLocalTimer();
                this.currentSession = null;
                this.startTime = null;
                this.totalDuration = null;
                
                // Update selected roll status
                if (this.selectedRoll) {
                    this.selectedRoll.is_completed = true;
                    this.selectedRoll.is_developing = false;
                    this.selectedRoll.development_status = 'completed';
                    
                    // Show create label button for completed roll
                    const createLabelBtn = document.getElementById('create-label');
                    if (createLabelBtn) {
                        createLabelBtn.style.display = 'inline-flex';
                    }
                    
                    // Update start button
                    const startBtn = document.getElementById('start-development');
                    if (startBtn) {
                        startBtn.disabled = true;
                        startBtn.innerHTML = '<i class="fas fa-check"></i> Already Developed';
                    }
                }
                
                // Save cleared state to localStorage
                this.saveStateToStorage();
                
                // Refresh data
                this.loadRolls();
                this.loadDevelopmentHistory();
            } else {
                this.showNotification('error', 'Error', data.error || 'Failed to complete development');
            }
        } catch (error) {
            console.error('Error completing development:', error);
            this.showNotification('error', 'Error', 'Failed to complete development');
        }
    }
    
    cancelDevelopment() {
        // Reset UI and state
        this.hideDevelopmentTimer();
        this.stopLocalTimer();
        this.currentSession = null;
        this.startTime = null;
        this.totalDuration = null;
        
        // Save cleared state to localStorage
        this.saveStateToStorage();
        
        this.loadRolls();
    }
    
    showDevelopmentTimer() {
        const timerElement = document.getElementById('development-timer');
        const startBtn = document.getElementById('start-development');
        const completeBtn = document.getElementById('complete-development');
        const cancelBtn = document.getElementById('cancel-development');
        const createLabelBtn = document.getElementById('create-label');
        const lightingToggleBtn = document.getElementById('toggle-lighting-mode');
        
        if (timerElement) {
            timerElement.style.display = 'block';
        }
        
        // Update button visibility
        if (startBtn) startBtn.style.display = 'none';
        if (completeBtn) completeBtn.style.display = 'inline-flex';
        if (cancelBtn) cancelBtn.style.display = 'inline-flex';
        if (createLabelBtn) createLabelBtn.style.display = 'none';
        // Keep lighting toggle always visible in header
        if (lightingToggleBtn) {
            lightingToggleBtn.style.display = 'inline-flex';
            this.updateLightingModeButton();
        }
        
        // Also show density tracking
        this.showDensityTracking();
        
        // Set timer info
        if (this.selectedRoll) {
            const startedTime = new Date().toLocaleTimeString();
            const completionTime = new Date(Date.now() + (this.developmentDuration * 60 * 1000)).toLocaleTimeString();
            
            document.getElementById('development-started').textContent = startedTime;
            document.getElementById('development-completion').textContent = completionTime;
        }
    }
    
    hideDevelopmentTimer() {
        const timerElement = document.getElementById('development-timer');
        const startBtn = document.getElementById('start-development');
        const completeBtn = document.getElementById('complete-development');
        const cancelBtn = document.getElementById('cancel-development');
        const lightingToggleBtn = document.getElementById('toggle-lighting-mode');
        
        if (timerElement) {
            timerElement.style.display = 'none';
        }
        
        // Update button visibility
        if (startBtn) startBtn.style.display = 'inline-flex';
        if (completeBtn) completeBtn.style.display = 'none';
        if (cancelBtn) cancelBtn.style.display = 'none';
        // Keep lighting toggle always visible in header
        if (lightingToggleBtn) {
            lightingToggleBtn.style.display = 'inline-flex';
            this.updateLightingModeButton();
        }
        
        // Hide density tracking
        this.hideDensityTracking();
    }
    
    startLocalTimer(durationMinutes) {
        if (!this.currentSession) return;
        
        this.startTime = Date.now();
        this.totalDuration = durationMinutes * 60 * 1000; // Convert to milliseconds
        
        // Update timer display immediately
        this.updateLocalTimer();
        
        // Update every second for smooth countdown
        this.timerInterval = setInterval(() => {
            this.updateLocalTimer();
        }, 1000);
    }
    
    updateLocalTimer() {
        const elapsed = Date.now() - this.startTime;
        const remaining = Math.max(0, this.totalDuration - elapsed);
        const progress = Math.min(100, (elapsed / this.totalDuration) * 100);
        
        // Update timer display
        const remainingMinutes = Math.floor(remaining / (60 * 1000));
        const remainingSeconds = Math.floor((remaining % (60 * 1000)) / 1000);
        
        const timeElement = document.getElementById('timer-time');
        const progressElement = document.getElementById('development-progress');
        const progressCircle = document.getElementById('timer-progress-circle');
        
        if (timeElement) {
            timeElement.textContent = `${remainingMinutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
        if (progressElement) {
            progressElement.textContent = `${progress.toFixed(1)}%`;
        }
        
        // Update progress circle
        if (progressCircle) {
            const circumference = 283; // 2 * π * 45
            const offset = circumference - (progress / 100) * circumference;
            progressCircle.style.strokeDashoffset = offset;
        }
        
        // Check if timer is complete
        if (remaining <= 0) {
            this.onTimerComplete();
        }
    }
    
    onTimerComplete() {
        // Stop the timer
        this.stopLocalTimer();
        
        // Get the actual duration that was completed
        const durationText = this.developmentDuration ? 
            `${this.developmentDuration.toFixed(1)}-minute` : 
            '30-minute';
        
        // Show alarm notification
        this.showNotification('success', 'Development Complete!', 
            `${durationText} development timer finished for roll ${this.selectedRoll.film_number}. Automatically completing development.`);
        
        // Play alarm sound (if browser supports it)
        this.playAlarmSound();
        
        // Change timer display to show completion
        const timeElement = document.getElementById('timer-time');
        if (timeElement) {
            timeElement.textContent = '00:00';
            timeElement.style.color = '#28a745'; // Green color
        }
        
        // Flash the timer to draw attention
        this.flashTimer();
        
        // Automatically complete development after a short delay
        setTimeout(() => {
            this.completeDevelopment();
        }, 2000); // 2 second delay to allow user to see the completion
    }
    
    playAlarmSound() {
        try {
            // Create airplane seatbelt chime sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // First chime (higher pitch)
            const oscillator1 = audioContext.createOscillator();
            const gainNode1 = audioContext.createGain();
            
            oscillator1.connect(gainNode1);
            gainNode1.connect(audioContext.destination);
            
            oscillator1.frequency.value = 1000; // 1000 Hz
            oscillator1.type = 'sine';
            gainNode1.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode1.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.1);
            gainNode1.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.5);
            
            oscillator1.start(audioContext.currentTime);
            oscillator1.stop(audioContext.currentTime + 0.5);
            
            // Second chime (lower pitch) - starts slightly after first
            const oscillator2 = audioContext.createOscillator();
            const gainNode2 = audioContext.createGain();
            
            oscillator2.connect(gainNode2);
            gainNode2.connect(audioContext.destination);
            
            oscillator2.frequency.value = 800; // 800 Hz
            oscillator2.type = 'sine';
            gainNode2.gain.setValueAtTime(0, audioContext.currentTime + 0.6);
            gainNode2.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.7);
            gainNode2.gain.linearRampToValueAtTime(0, audioContext.currentTime + 1.2);
            
            oscillator2.start(audioContext.currentTime + 0.6);
            oscillator2.stop(audioContext.currentTime + 1.2);
            
        } catch (error) {
            console.log('Could not play seatbelt chime sound:', error);
        }
    }
    
    flashTimer() {
        const timerContainer = document.getElementById('development-timer');
        let flashCount = 0;
        const maxFlashes = 6;
        
        const flashInterval = setInterval(() => {
            if (timerContainer) {
                timerContainer.style.backgroundColor = flashCount % 2 === 0 ? '#28a745' : '';
            }
            flashCount++;
            
            if (flashCount >= maxFlashes) {
                clearInterval(flashInterval);
                if (timerContainer) {
                    timerContainer.style.backgroundColor = '';
                }
            }
        }, 500);
    }
    
    stopLocalTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    // Density tracking methods
    showDensityTracking() {
        const densitySection = document.getElementById('density-tracking');
        if (densitySection) {
            densitySection.style.display = 'block';
            this.loadDensityMeasurements();
        }
    }

    hideDensityTracking() {
        const densitySection = document.getElementById('density-tracking');
        if (densitySection) {
            densitySection.style.display = 'none';
        }
    }

    async saveDensityMeasurement() {
        if (!this.currentSession) {
            this.showNotification('error', 'Error', 'No active development session');
            return;
        }

        const timeSelect = document.getElementById('measurement-time');
        const valueInput = document.getElementById('density-value');
        const notesInput = document.getElementById('density-notes');

        const measurementTime = parseInt(timeSelect.value);
        const densityValue = parseFloat(valueInput.value);
        const notes = notesInput.value.trim();

        // Validation
        if (isNaN(densityValue) || densityValue < 0 || densityValue > 2) {
            this.showNotification('error', 'Error', 'Please enter a valid density value between 0.0 and 2.0');
            return;
        }

        try {
            const response = await fetch('/api/development/density/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    density_value: densityValue,
                    measurement_time_minutes: measurementTime,
                    notes: notes
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('success', 'Success', 
                    `Density measurement saved: ${densityValue} at ${measurementTime} minutes`);
                
                // Clear form
                valueInput.value = '';
                notesInput.value = '';
                
                // Reload measurements
                this.loadDensityMeasurements();
            } else {
                this.showNotification('error', 'Error', data.error || 'Failed to save density measurement');
            }
        } catch (error) {
            console.error('Error saving density measurement:', error);
            this.showNotification('error', 'Error', 'Error saving density measurement');
        }
    }

    async loadDensityMeasurements() {
        if (!this.currentSession) {
            return;
        }

        try {
            const response = await fetch(`/api/development/density/get/?session_id=${this.currentSession}`);
            const data = await response.json();

            if (data.success) {
                this.renderDensityMeasurements(data.measurements);
            }
        } catch (error) {
            console.error('Error loading density measurements:', error);
        }
    }

    renderDensityMeasurements(measurements) {
        const measurementsList = document.getElementById('measurements-list');
        
        if (!measurementsList) return;

        if (measurements.length === 0) {
            measurementsList.innerHTML = `
                <div class="no-measurements">
                    <i class="fas fa-info-circle"></i>
                    <p>No measurements recorded yet. Take your first measurement at 10 minutes.</p>
                </div>
            `;
            return;
        }

        measurementsList.innerHTML = measurements.map(measurement => {
            const statusText = {
                'too_low': 'TOO LOW',
                'low': 'LOW', 
                'optimal': 'OPTIMAL',
                'high': 'HIGH',
                'too_high': 'TOO HIGH'
            }[measurement.quality_status] || 'UNKNOWN';

            return `
                <div class="measurement-item">
                    <div class="measurement-info">
                        <div class="measurement-time">${measurement.measurement_time_minutes} minutes</div>
                        <div class="measurement-value" style="color: ${measurement.quality_color}">
                            ${measurement.density_value}
                        </div>
                        ${measurement.notes ? `<div class="measurement-notes">${measurement.notes}</div>` : ''}
                    </div>
                    <div class="measurement-status ${measurement.quality_status}">
                        ${statusText}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Lighting mode control methods
    toggleLightingMode() {
        console.log('toggleLightingMode called - using WebSocket consumer');
        
        const lightingToggleBtn = document.getElementById('toggle-lighting-mode');
        
        // Add switching animation
        if (lightingToggleBtn) {
            lightingToggleBtn.classList.add('switching');
            lightingToggleBtn.disabled = true;
        }
        
        // Determine target mode (opposite of current)
        const targetMode = this.isLightMode ? 'dark' : 'light';
        
        // Send command to WebSocket consumer
        this.sendLightingCommand(targetMode)
            .then(success => {
                if (success) {
                    // Toggle our internal state
                    this.isLightMode = !this.isLightMode;
                    
                    // Save state to localStorage
                    this.saveStateToStorage();
                    
                    const currentMode = this.isLightMode ? 'light' : 'dark';
                    
                    this.showNotification('success', 'Lighting Mode Changed', 
                        `Switched to ${currentMode} mode for film handling`);
                } else {
                    this.showNotification('error', 'Error', 'Failed to toggle lighting mode');
                }
            })
            .finally(() => {
                // Remove animation and re-enable button
                if (lightingToggleBtn) {
                    lightingToggleBtn.classList.remove('switching');
                    lightingToggleBtn.disabled = false;
                }
                
                // Update button text
                this.updateLightingModeButton();
            });
    }
    
    async sendLightingCommand(mode) {
        try {
            const response = await fetch('/control_relay/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
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
    
    updateLightingModeButton() {
        const lightingToggleBtn = document.getElementById('toggle-lighting-mode');
        const lightingModeText = document.getElementById('lighting-mode-text');
        
        if (!lightingToggleBtn || !lightingModeText) return;
        
        // Always show as available since we assume relay is connected
        if (this.isLightMode) {
            lightingModeText.textContent = 'Switch to Dark Mode';
            lightingToggleBtn.className = 'btn btn-warning';
            lightingToggleBtn.disabled = false;
            lightingToggleBtn.innerHTML = '<i class="fas fa-moon"></i> <span id="lighting-mode-text">Switch to Dark Mode</span>';
        } else {
            lightingModeText.textContent = 'Switch to Light Mode';
            lightingToggleBtn.className = 'btn btn-info';
            lightingToggleBtn.disabled = false;
            lightingToggleBtn.innerHTML = '<i class="fas fa-sun"></i> <span id="lighting-mode-text">Switch to Light Mode</span>';
        }
    }

    async initializeLightingMode() {
        // Check if we have a saved lighting mode preference
        if (this.isLightMode === undefined) {
            // Default to light mode if no preference saved
            this.isLightMode = true;
        }
        
        this.isRelayConnected = true; // Assume relay is available
        
        console.log('Initialized lighting mode:', this.isLightMode ? 'light' : 'dark');
        
        // Update button state
        this.updateLightingModeButton();
    }
    
    // Chemical status and other methods (simplified for brevity)
    async loadChemicalStatus() {
        try {
            console.log('Loading chemical status...');
            const response = await fetch('/api/development/chemicals/');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Chemical status response:', data);
            
            if (data.success) {
                this.renderChemicalStatus(data.chemicals);
            } else {
                console.error('Chemical status API returned error:', data.error);
                this.showNotification('error', 'Error', `Failed to load chemical status: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error loading chemical status:', error);
            this.showNotification('error', 'Error', `Failed to load chemical status: ${error.message}`);
        }
    }
    
    renderChemicalStatus(chemicals) {
        // Implementation for chemical status rendering
        console.log('Rendering chemical status:', chemicals);
        
        // Update each chemical container
        Object.entries(chemicals).forEach(([chemicalType, data]) => {
            const container = document.querySelector(`[data-chemical="${chemicalType}"]`);
            if (!container) {
                console.warn(`Chemical container not found for: ${chemicalType}`);
                return;
            }
            
            // Update level fill
            const levelFill = container.querySelector(`#${chemicalType}-fill`);
            if (levelFill) {
                levelFill.style.height = `${data.capacity_percent}%`;
                
                // Set color based on capacity
                if (data.capacity_percent >= 20) {
                    levelFill.style.backgroundColor = '#28a745'; // Green
                } else if (data.capacity_percent >= 10) {
                    levelFill.style.backgroundColor = '#ffc107'; // Yellow/Orange
                } else {
                    levelFill.style.backgroundColor = '#dc3545'; // Red
                }
            }
            
            // Update percentage text
            const percentageElement = container.querySelector(`#${chemicalType}-percentage`);
            if (percentageElement) {
                percentageElement.textContent = `${data.capacity_percent.toFixed(1)}%`;
                
                // Set text color based on capacity
                if (data.capacity_percent >= 20) {
                    percentageElement.style.color = '#28a745';
                } else if (data.capacity_percent >= 10) {
                    percentageElement.style.color = '#ffc107';
                } else {
                    percentageElement.style.color = '#dc3545';
                }
            }
            
            // Update date/batch info
            const dateElement = container.querySelector(`#${chemicalType}-date`);
            if (dateElement) {
                if (data.batch_id && data.batch_id !== 'No active batch') {
                    const createdDate = data.created_at ? new Date(data.created_at).toLocaleDateString() : 'Unknown';
                    dateElement.textContent = `Batch: ${data.batch_id} (${createdDate})`;
                    dateElement.style.color = '#6c757d';
                } else {
                    dateElement.textContent = 'No active batch';
                    dateElement.style.color = '#dc3545';
                }
            }
            
            // Update container class based on status
            container.classList.remove('good', 'low', 'critical');
            container.classList.add(data.status);
            
            // Show/hide reset button based on batch status
            const resetBtn = container.querySelector('.chemical-reset-btn');
            if (resetBtn) {
                if (data.batch_id === 'No active batch' || data.is_critical) {
                    resetBtn.style.display = 'block';
                    resetBtn.style.backgroundColor = data.is_critical ? '#dc3545' : '#007bff';
                } else {
                    resetBtn.style.display = 'none';
                }
            }
        });
        
        // Update chemical usage summary
        this.updateChemicalSummary(chemicals);
        
        // Don't show automatic chemical alerts - only check when starting development
    }
    
    updateChemicalSummary(chemicals) {
        // Calculate totals from all chemical types (they should all be the same)
        const firstChemical = Object.values(chemicals)[0];
        if (!firstChemical) return;
        
        // Update summary stats
        const total16mmElement = document.getElementById('total-16mm-rolls');
        const total35mmElement = document.getElementById('total-35mm-rolls');
        const totalAreaElement = document.getElementById('total-area-used');
        const remainingCapacityElement = document.getElementById('remaining-capacity');
        
        if (total16mmElement) {
            total16mmElement.textContent = firstChemical.used_16mm_rolls || 0;
        }
        
        if (total35mmElement) {
            total35mmElement.textContent = firstChemical.used_35mm_rolls || 0;
        }
        
        if (totalAreaElement) {
            totalAreaElement.textContent = `${firstChemical.used_area?.toFixed(3) || '0.000'} m²`;
        }
        
        if (remainingCapacityElement) {
            remainingCapacityElement.textContent = `${firstChemical.remaining_capacity?.toFixed(3) || '0.000'} m²`;
        }
    }
    
    async loadDevelopmentHistory() {
        try {
            const response = await fetch('/api/development/history/');
            const data = await response.json();
            
            if (data.success) {
                this.renderDevelopmentHistory(data.sessions);
            }
        } catch (error) {
            console.error('Error loading development history:', error);
        }
    }
    
    renderDevelopmentHistory(sessions) {
        // Implementation for history rendering
        console.log('Rendering development history:', sessions);
        
        const historyList = document.getElementById('development-history-list');
        if (!historyList) {
            console.warn('Development history list element not found');
            return;
        }
        
        if (!sessions || sessions.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <p>No development history available</p>
                </div>
            `;
            return;
        }
        
        historyList.innerHTML = sessions.map(session => {
            const startTime = new Date(session.started_at).toLocaleString();
            const duration = session.duration || 'Unknown';
            const status = session.status || 'unknown';
            const rollNumber = session.roll_number || 'Unknown';
            const filmType = session.film_type || 'Unknown';
            
            // Calculate completion time if available
            let completionInfo = '';
            if (session.completed_at) {
                const completedTime = new Date(session.completed_at).toLocaleString();
                completionInfo = `<div class="history-completion">Completed: ${completedTime}</div>`;
            } else if (session.estimated_completion) {
                const estimatedTime = new Date(session.estimated_completion).toLocaleString();
                completionInfo = `<div class="history-estimated">Estimated completion: ${estimatedTime}</div>`;
            }
            
            // Status icon and color
            let statusIcon = 'fas fa-question-circle';
            let statusClass = 'unknown';
            
            switch (status) {
                case 'completed':
                    statusIcon = 'fas fa-check-circle';
                    statusClass = 'completed';
                    break;
                case 'developing':
                    statusIcon = 'fas fa-spinner fa-spin';
                    statusClass = 'developing';
                    break;
                case 'cancelled':
                    statusIcon = 'fas fa-times-circle';
                    statusClass = 'cancelled';
                    break;
                case 'failed':
                    statusIcon = 'fas fa-exclamation-circle';
                    statusClass = 'failed';
                    break;
            }
            
            return `
                <div class="history-item ${statusClass}">
                    <div class="history-header">
                        <div class="history-roll">
                            <i class="fas fa-film"></i>
                            <span class="roll-number">${rollNumber}</span>
                            <span class="film-type">${filmType}</span>
                        </div>
                        <div class="history-status">
                            <i class="${statusIcon}"></i>
                            <span class="status-text">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                        </div>
                    </div>
                    <div class="history-details">
                        <div class="history-time">Started: ${startTime}</div>
                        ${completionInfo}
                        <div class="history-duration">Duration: ${duration}</div>
                        ${session.session_id ? `<div class="history-session">Session: ${session.session_id}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    updateStatusCounts(rolls) {
        const readyCount = rolls.filter(r => r.can_develop && !r.is_developing && !r.is_completed).length;
        const developingCount = rolls.filter(r => r.is_developing).length;
        const completedCount = rolls.filter(r => r.is_completed).length;
        
        document.getElementById('rolls-ready-count').textContent = readyCount;
        document.getElementById('rolls-developing-count').textContent = developingCount;
        document.getElementById('rolls-completed-count').textContent = completedCount;
    }
    
    updateStatusOverview() {
        // Update overview stats
    }
    
    // Modal and other UI methods
    showChemicalResetModal(chemicalType) {
        const modal = document.getElementById('chemical-reset-modal');
        const chemicalNameElement = document.getElementById('reset-chemical-name');
        const newBatchIdInput = document.getElementById('new-batch-id');
        const maxAreaInput = document.getElementById('max-area');
        
        if (modal && chemicalNameElement) {
            // Set the chemical type name
            const chemicalNames = {
                'developer': 'Developer',
                'fixer': 'Fixer',
                'cleaner1': 'Cleaner 1',
                'cleaner2': 'Cleaner 2'
            };
            
            chemicalNameElement.textContent = chemicalNames[chemicalType] || chemicalType;
            
            // Generate a default batch ID
            const now = new Date();
            const timestamp = now.toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
            newBatchIdInput.value = `${chemicalType}_${timestamp}`;
            
            // Set default max area
            maxAreaInput.value = '10.0';
            
            // Store the chemical type for later use
            modal.dataset.chemicalType = chemicalType;
            
            // Show the modal
            modal.style.display = 'flex';
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.opacity = '1';
            }, 10);
        }
    }
    
    hideModal() {
        const modals = [
            document.getElementById('chemical-reset-modal'),
            document.getElementById('chemical-insertion-modal')
        ];
        
        modals.forEach(modal => {
            if (modal) {
                modal.style.opacity = '0';
                setTimeout(() => {
                    modal.style.display = 'none';
                }, 300);
            }
        });
    }
    
    async confirmChemicalReset() {
        const modal = document.getElementById('chemical-reset-modal');
        const chemicalType = modal?.dataset.chemicalType;
        const newBatchIdInput = document.getElementById('new-batch-id');
        const maxAreaInput = document.getElementById('max-area');
        
        if (!chemicalType || !newBatchIdInput || !maxAreaInput) {
            this.showNotification('error', 'Error', 'Missing required information for chemical reset');
            return;
        }
        
        const batchId = newBatchIdInput.value.trim();
        const maxArea = parseFloat(maxAreaInput.value);
        
        if (!batchId) {
            this.showNotification('error', 'Error', 'Please enter a batch ID');
            return;
        }
        
        if (isNaN(maxArea) || maxArea <= 0) {
            this.showNotification('error', 'Error', 'Please enter a valid maximum area');
            return;
        }
        
        try {
            const response = await fetch(`/api/development/chemicals/reset/${chemicalType}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    batch_id: batchId,
                    max_area: maxArea
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Chemical Reset Complete', 
                    `${chemicalType} batch has been reset with new batch ID: ${batchId}`);
                
                // Hide modal and refresh chemical status
                this.hideModal();
                this.loadChemicalStatus();
            } else {
                this.showNotification('error', 'Reset Failed', data.error || 'Failed to reset chemical batch');
            }
        } catch (error) {
            console.error('Error resetting chemical batch:', error);
            this.showNotification('error', 'Error', 'Failed to reset chemical batch');
        }
    }
    
    showChemicalInsertionModal() {
        const modal = document.getElementById('chemical-insertion-modal');
        const batchDateInput = document.getElementById('batch-date');
        const batchCapacityInput = document.getElementById('batch-capacity');
        const confirmButton = document.getElementById('confirm-chemical-insertion');
        
        if (modal) {
            // Set today's date
            if (batchDateInput) {
                const today = new Date().toISOString().split('T')[0];
                batchDateInput.value = today;
            }
            
            // Set default capacity
            if (batchCapacityInput) {
                batchCapacityInput.value = '10.0';
            }
            
            // Reset all checkboxes
            const checkboxes = modal.querySelectorAll('.chemical-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Disable confirm button initially
            if (confirmButton) {
                confirmButton.disabled = true;
            }
            
            // Show the modal
            modal.style.display = 'flex';
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.opacity = '1';
            }, 10);
        }
    }
    
    updateChemicalChecklist() {
        const modal = document.getElementById('chemical-insertion-modal');
        const confirmButton = document.getElementById('confirm-chemical-insertion');
        
        if (!modal || !confirmButton) return;
        
        // Check if all four chemicals are checked
        const checkboxes = modal.querySelectorAll('.chemical-checkbox');
        const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
        
        // Enable/disable confirm button based on whether all chemicals are checked
        confirmButton.disabled = !allChecked;
        
        if (allChecked) {
            confirmButton.innerHTML = '<i class="fas fa-check"></i> Confirm Installation Complete';
            confirmButton.className = 'btn btn-success';
        } else {
            confirmButton.innerHTML = '<i class="fas fa-check"></i> Confirm Installation Complete';
            confirmButton.className = 'btn btn-success';
        }
    }
    
    async confirmChemicalInsertion() {
        const modal = document.getElementById('chemical-insertion-modal');
        const batchCapacityInput = document.getElementById('batch-capacity');
        const batchNotesInput = document.getElementById('batch-notes');
        const confirmButton = document.getElementById('confirm-chemical-insertion');
        
        if (!modal || !batchCapacityInput) {
            this.showNotification('error', 'Error', 'Missing required modal elements');
            return;
        }
        
        // Validate that all chemicals are checked
        const checkboxes = modal.querySelectorAll('.chemical-checkbox');
        const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
        
        if (!allChecked) {
            this.showNotification('error', 'Incomplete Installation', 
                'Please check all four chemical types to confirm they have been installed');
            return;
        }
        
        const capacity = parseFloat(batchCapacityInput.value);
        const notes = batchNotesInput?.value?.trim() || '';
        
        if (isNaN(capacity) || capacity <= 0) {
            this.showNotification('error', 'Error', 'Please enter a valid capacity value');
            return;
        }
        
        try {
            // Show loading state
            const originalText = confirmButton.innerHTML;
            confirmButton.disabled = true;
            confirmButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Installing Chemicals...';
            
            const response = await fetch('/api/development/chemicals/insert/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    capacity: capacity,
                    notes: notes
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Chemical Installation Complete', 
                    `Successfully installed ${data.batches?.length || 4} chemical batches with ${capacity}m² capacity each`);
                
                // Hide modal and refresh chemical status
                this.hideModal();
                this.loadChemicalStatus();
                
                // Show detailed results if available
                if (data.batches && data.batches.length > 0) {
                    console.log('New chemical batches created:', data.batches);
                }
            } else {
                this.showNotification('error', 'Installation Failed', data.error || 'Failed to install chemical batches');
                
                // Reset button
                confirmButton.disabled = false;
                confirmButton.innerHTML = originalText;
            }
        } catch (error) {
            console.error('Error installing chemicals:', error);
            this.showNotification('error', 'Error', 'Failed to install chemical batches');
            
            // Reset button
            if (confirmButton) {
                confirmButton.disabled = false;
                confirmButton.innerHTML = '<i class="fas fa-check"></i> Confirm Installation Complete';
            }
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (!this.currentSession) {
                this.loadRolls();
                this.loadChemicalStatus();
            }
        }, 30000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString();
    }
    
    getCSRFToken() {
        // Try multiple ways to get the CSRF token
        let token = null;
        
        // Method 1: Look for hidden input with name csrfmiddlewaretoken
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput && csrfInput.value) {
            token = csrfInput.value;
        }
        
        // Method 2: Look for meta tag with csrf-token
        if (!token) {
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta && csrfMeta.content) {
                token = csrfMeta.content;
            }
        }
        
        // Method 3: Try to get from cookie
        if (!token) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    token = value;
                    break;
                }
            }
        }
        
        // If still no token, log error but don't throw
        if (!token) {
            console.error('CSRF token not found. Please ensure the page includes {% csrf_token %}');
            return '';
        }
        
        return token;
    }
    
    showNotification(type, title, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${this.getNotificationIcon(type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        // Add to container
        const container = document.getElementById('notifications-container');
        if (container) {
            container.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 5000);
            
            // Add close button functionality
            notification.querySelector('.notification-close').addEventListener('click', () => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            });
        }
    }
    
    getNotificationIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    destroy() {
        this.stopLocalTimer();
        this.stopAutoRefresh();
    }
    
    async createAndPrintLabel() {
        if (!this.selectedRoll || !this.selectedRoll.is_completed) {
            this.showNotification('error', 'Error', 'Please select a completed roll to create a label');
            return;
        }
        
        try {
            console.log('Creating label for roll:', this.selectedRoll.film_number);
            
            // Show loading state
            const createLabelBtn = document.getElementById('create-label');
            const originalText = createLabelBtn.innerHTML;
            createLabelBtn.disabled = true;
            createLabelBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Label...';
            
            const csrfToken = this.getCSRFToken();
            console.log('CSRF token for label creation:', csrfToken ? 'Yes' : 'No');
            
            // Generate the label
            const response = await fetch('/api/labels/generate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    roll_ids: [this.selectedRoll.id]
                })
            });
            
            console.log('Label generation response status:', response.status);
            const data = await response.json();
            console.log('Label generation response data:', data);
            
            if (data.success && data.labels && data.labels.length > 0) {
                const label = data.labels[0];
                console.log('Label created successfully:', label.label_id);
                
                // Update button to show printing state
                createLabelBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Printing Label...';
                
                // Print the label immediately
                const printResponse = await fetch(`/api/labels/print/${label.label_id}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        copies: 1
                    })
                });
                
                console.log('Print response status:', printResponse.status);
                const printData = await printResponse.json();
                console.log('Print response data:', printData);
                
                if (printData.success) {
                    this.showNotification('success', 'Label Created & Printed', 
                        `Label for roll ${this.selectedRoll.film_number} has been created and sent to printer successfully`);
                    
                    // Update button to show success
                    createLabelBtn.innerHTML = '<i class="fas fa-check"></i> Label Printed';
                    createLabelBtn.className = 'btn btn-success';
                    
                    // Reset button after 3 seconds
                    setTimeout(() => {
                        createLabelBtn.innerHTML = originalText;
                        createLabelBtn.className = 'btn btn-info';
                        createLabelBtn.disabled = false;
                    }, 3000);
                } else {
                    // Label created but printing failed
                    this.showNotification('warning', 'Label Created', 
                        `Label created successfully but printing failed: ${printData.error}. You can print it manually from the Label page.`);
                    
                    // Reset button
                    createLabelBtn.innerHTML = originalText;
                    createLabelBtn.disabled = false;
                }
            } else {
                throw new Error(data.error || 'Failed to create label');
            }
        } catch (error) {
            console.error('Error creating and printing label:', error);
            this.showNotification('error', 'Error', `Failed to create label: ${error.message}`);
            
            // Reset button
            const createLabelBtn = document.getElementById('create-label');
            if (createLabelBtn) {
                createLabelBtn.innerHTML = '<i class="fas fa-tag"></i> Create & Print Label';
                createLabelBtn.className = 'btn btn-info';
                createLabelBtn.disabled = false;
            }
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.developmentDashboard = new DevelopmentDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.developmentDashboard) {
        window.developmentDashboard.destroy();
    }
}); 