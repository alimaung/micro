// Development Dashboard JavaScript

class DevelopmentDashboard {
    constructor() {
        this.selectedRoll = null;
        this.currentSession = null;
        this.timerInterval = null;
        this.progressInterval = null;
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
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
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadRolls(),
                this.loadChemicalStatus(),
                this.loadDevelopmentHistory()
            ]);
            this.updateStatusOverview();
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
            } else {
                throw new Error(data.error || 'Failed to load rolls');
            }
        } catch (error) {
            console.error('Error loading rolls:', error);
            this.showNotification('error', 'Error', 'Failed to load rolls for development');
        }
    }
    
    renderRolls(rolls) {
        const container = document.getElementById('ready-rolls-grid');
        
        if (rolls.length === 0) {
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-film"></i>
                    <p>No rolls ready for development</p>
                    <small>Complete filming first to see rolls here</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = rolls.map(roll => {
            const isSelected = this.selectedRoll && this.selectedRoll.id === roll.id;
            const isDeveloping = roll.development_status === 'developing';
            
            return `
                <div class="roll-card ${isSelected ? 'selected' : ''} ${isDeveloping ? 'developing' : ''}" 
                     data-roll-id="${roll.id}" 
                     ${isDeveloping ? 'data-disabled="true"' : ''}>
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">${roll.film_number}</div>
                            <div class="roll-film-type">${roll.film_type}</div>
                        </div>
                        <div class="roll-status-badge ${roll.development_status}">
                            ${roll.development_status}
                        </div>
                    </div>
                    
                    <div class="roll-details">
                        <div class="detail-item">
                            <span class="label">Project:</span>
                            <span class="value">${roll.project_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Pages:</span>
                            <span class="value">${roll.pages_used}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Filmed:</span>
                            <span class="value">${this.formatDateTime(roll.filming_completed_at)}</span>
                        </div>
                        ${roll.development_progress > 0 ? `
                        <div class="detail-item">
                            <span class="label">Progress:</span>
                            <span class="value">${roll.development_progress.toFixed(1)}%</span>
                        </div>
                        ` : ''}
                        ${roll.estimated_completion ? `
                        <div class="detail-item">
                            <span class="label">ETA:</span>
                            <span class="value">${this.formatDateTime(roll.estimated_completion)}</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    ${isDeveloping ? `
                        <div class="roll-overlay">
                            <i class="fas fa-cog fa-spin"></i>
                            <span>Developing</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        // Attach click events
        container.querySelectorAll('.roll-card').forEach(card => {
            if (!card.dataset.disabled) {
                card.addEventListener('click', () => {
                    const rollId = parseInt(card.dataset.rollId);
                    const roll = rolls.find(r => r.id === rollId);
                    this.selectRoll(roll);
                });
            }
        });
        
        // Check for active development sessions
        const developingRoll = rolls.find(roll => roll.development_status === 'developing');
        if (developingRoll && developingRoll.session_id) {
            this.currentSession = developingRoll.session_id;
            this.selectRoll(developingRoll);
            this.showDevelopmentTimer();
            // Note: We can't restore the exact timer state for existing sessions
            // The user will need to manually track remaining time or restart if needed
        }
    }
    
    selectRoll(roll) {
        this.selectedRoll = roll;
        
        // Update UI selection
        document.querySelectorAll('.roll-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-roll-id="${roll.id}"]`).classList.add('selected');
        
        // Show roll info
        this.showSelectedRollInfo(roll);
        
        // Enable/disable start button
        const startBtn = document.getElementById('start-development');
        const isDeveloping = roll.development_status === 'developing';
        
        startBtn.disabled = isDeveloping;
        
        if (isDeveloping) {
            this.showDevelopmentTimer();
            // For existing development sessions, we can't restore the exact timer state
            // so we'll just show the timer interface without starting a new countdown
        } else {
            this.hideDevelopmentTimer();
            this.stopLocalTimer();
        }
    }
    
    showSelectedRollInfo(roll) {
        const infoContainer = document.getElementById('selected-roll-info');
        const noSelectionMessage = document.getElementById('no-selection-message');
        
        document.getElementById('selected-film-number').textContent = roll.film_number;
        document.getElementById('selected-film-type').textContent = roll.film_type;
        document.getElementById('selected-project').textContent = roll.project_name;
        document.getElementById('selected-pages').textContent = roll.pages_used;
        
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
                    roll_id: this.selectedRoll.id,
                    duration_minutes: 30
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = data.session_id;
                this.showNotification('success', 'Development Started', 
                    `Development started for roll ${this.selectedRoll.film_number}`);
                
                // Update UI and start local timer
                this.showDevelopmentTimer();
                this.startLocalTimer(30); // 30 minutes
                
                // Refresh data once
                this.loadRolls();
                this.loadChemicalStatus();
            } else {
                if (data.warnings && data.warnings.length > 0) {
                    this.showNotification('warning', 'Chemical Warning', data.warnings.join(', '));
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
            const response = await fetch('/api/development/complete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: this.currentSession
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Development Complete', 
                    `Development completed for roll ${this.selectedRoll.film_number}`);
                
                // Reset UI
                this.hideDevelopmentTimer();
                this.stopLocalTimer();
                this.currentSession = null;
                
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
        // For now, just hide the timer - in a real implementation you might want to 
        // actually cancel the session in the backend
        this.hideDevelopmentTimer();
        this.stopLocalTimer();
        this.currentSession = null;
        this.loadRolls();
    }
    
    showDevelopmentTimer() {
        const timerContainer = document.getElementById('development-timer');
        const startBtn = document.getElementById('start-development');
        const completeBtn = document.getElementById('complete-development');
        const cancelBtn = document.getElementById('cancel-development');
        
        timerContainer.style.display = 'flex';
        startBtn.style.display = 'none';
        completeBtn.style.display = 'inline-flex';
        cancelBtn.style.display = 'inline-flex';
    }
    
    hideDevelopmentTimer() {
        const timerContainer = document.getElementById('development-timer');
        const startBtn = document.getElementById('start-development');
        const completeBtn = document.getElementById('complete-development');
        const cancelBtn = document.getElementById('cancel-development');
        
        timerContainer.style.display = 'none';
        startBtn.style.display = 'inline-flex';
        completeBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
        
        startBtn.disabled = !this.selectedRoll;
    }
    
    startProgressTracking() {
        if (!this.currentSession) return;
        
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/development/progress/?session_id=${this.currentSession}`);
                const data = await response.json();
                
                if (data.success) {
                    this.updateTimer(data);
                    
                    if (data.status === 'completed') {
                        this.stopProgressTracking();
                        this.hideDevelopmentTimer();
                        this.loadRolls();
                        this.loadDevelopmentHistory();
                    }
                }
            } catch (error) {
                console.error('Error tracking progress:', error);
            }
        }, 10000); // Update every 10 seconds instead of every second
    }
    
    stopProgressTracking() {
        // Keep this method for compatibility but make it stop the local timer
        this.stopLocalTimer();
    }
    
    updateTimer(progressData) {
        const progress = progressData.progress;
        const timeElement = document.getElementById('timer-time');
        const progressElement = document.getElementById('development-progress');
        const progressCircle = document.getElementById('timer-progress-circle');
        
        // Calculate remaining time (30 minutes total)
        const totalMinutes = 30;
        const remainingMinutes = Math.max(0, totalMinutes * (1 - progress / 100));
        const minutes = Math.floor(remainingMinutes);
        const seconds = Math.floor((remainingMinutes - minutes) * 60);
        
        timeElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        progressElement.textContent = `${progress.toFixed(1)}%`;
        
        // Update progress circle
        const circumference = 283; // 2 * π * 45
        const offset = circumference - (progress / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
        
        // Update other timer info
        if (progressData.started_at) {
            document.getElementById('development-started').textContent = 
                this.formatDateTime(progressData.started_at);
        }
        
        if (progressData.estimated_completion) {
            document.getElementById('development-completion').textContent = 
                this.formatDateTime(progressData.estimated_completion);
        }
    }
    
    async loadChemicalStatus() {
        try {
            const response = await fetch('/api/development/chemicals/');
            const data = await response.json();
            
            if (data.success) {
                this.renderChemicalStatus(data.chemicals);
                this.updateChemicalSummary(data.chemicals);
            } else {
                throw new Error(data.error || 'Failed to load chemical status');
            }
        } catch (error) {
            console.error('Error loading chemical status:', error);
            this.showNotification('error', 'Error', 'Failed to load chemical status');
        }
    }
    
    renderChemicalStatus(chemicals) {
        const chemicalTypes = ['developer', 'fixer', 'cleaner1', 'cleaner2'];
        
        chemicalTypes.forEach(type => {
            const chemical = chemicals[type];
            const fillElement = document.getElementById(`${type}-fill`);
            const percentageElement = document.getElementById(`${type}-percentage`);
            const dateElement = document.getElementById(`${type}-date`);
            
            if (chemical) {
                const percentage = chemical.capacity_percent;
                fillElement.style.height = `${percentage}%`;
                fillElement.style.opacity = percentage / 100;
                
                // Set color based on status
                if (chemical.is_critical) {
                    fillElement.style.backgroundColor = '#dc3545';
                } else if (chemical.is_low) {
                    fillElement.style.backgroundColor = '#ffc107';
                } else {
                    fillElement.style.backgroundColor = 'var(--color-primary)';
                }
                
                percentageElement.textContent = `${percentage.toFixed(1)}%`;
                
                if (chemical.created_at) {
                    const date = new Date(chemical.created_at);
                    dateElement.textContent = `Changed: ${this.formatDate(date)}`;
                } else {
                    dateElement.textContent = chemical.batch_id;
                }
            } else {
                fillElement.style.height = '0%';
                percentageElement.textContent = '0%';
                dateElement.textContent = 'No active batch';
            }
        });
    }
    
    updateChemicalSummary(chemicals) {
        let total16mm = 0;
        let total35mm = 0;
        let totalUsedArea = 0;
        let minRemainingCapacity = Infinity;
        
        Object.values(chemicals).forEach(chemical => {
            total16mm += chemical.used_16mm_rolls;
            total35mm += chemical.used_35mm_rolls;
            totalUsedArea += chemical.used_area;
            minRemainingCapacity = Math.min(minRemainingCapacity, chemical.remaining_capacity);
        });
        
        document.getElementById('total-16mm-rolls').textContent = total16mm;
        document.getElementById('total-35mm-rolls').textContent = total35mm;
        document.getElementById('total-area-used').textContent = `${totalUsedArea.toFixed(3)} m²`;
        document.getElementById('remaining-capacity').textContent = 
            `${minRemainingCapacity === Infinity ? 0 : minRemainingCapacity.toFixed(3)} m²`;
    }
    
    async loadDevelopmentHistory() {
        try {
            const response = await fetch('/api/development/history/');
            const data = await response.json();
            
            if (data.success) {
                this.renderDevelopmentHistory(data.sessions);
            } else {
                throw new Error(data.error || 'Failed to load development history');
            }
        } catch (error) {
            console.error('Error loading development history:', error);
            this.showNotification('error', 'Error', 'Failed to load development history');
        }
    }
    
    renderDevelopmentHistory(sessions) {
        const container = document.getElementById('development-history-list');
        
        if (sessions.length === 0) {
            container.innerHTML = `
                <div class="loading-state">
                    <i class="fas fa-history"></i>
                    <p>No development history</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = sessions.map(session => `
            <div class="history-item">
                <div class="history-info">
                    <div class="history-roll">${session.film_number} (${session.film_type})</div>
                    <div class="history-details">
                        ${session.project_name} • ${session.duration_minutes} min
                        ${session.started_at ? ` • Started: ${this.formatDateTime(session.started_at)}` : ''}
                        ${session.user ? ` • By: ${session.user}` : ''}
                    </div>
                </div>
                <div class="history-status ${session.status}">${session.status}</div>
            </div>
        `).join('');
    }
    
    updateStatusCounts(rolls) {
        const readyCount = rolls.filter(r => r.development_status === 'pending').length;
        const developingCount = rolls.filter(r => r.development_status === 'developing').length;
        
        document.getElementById('rolls-ready-count').textContent = readyCount;
        document.getElementById('rolls-developing-count').textContent = developingCount;
        
        // For completed today, we'd need additional API endpoint
        // For now, just show 0
        document.getElementById('rolls-completed-count').textContent = '0';
    }
    
    updateStatusOverview() {
        // This would be enhanced with more specific data from the backend
        // For now, we'll update what we can from the current data
    }
    
    showChemicalResetModal(chemicalType) {
        const modal = document.getElementById('chemical-reset-modal');
        const chemicalName = document.getElementById('reset-chemical-name');
        const batchIdInput = document.getElementById('new-batch-id');
        
        chemicalName.textContent = chemicalType;
        batchIdInput.value = `${chemicalType}_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}`;
        
        modal.classList.add('show');
        modal.dataset.chemicalType = chemicalType;
    }
    
    hideModal() {
        document.getElementById('chemical-reset-modal').classList.remove('show');
        document.getElementById('chemical-insertion-modal').classList.remove('show');
    }
    
    async confirmChemicalReset() {
        const modal = document.getElementById('chemical-reset-modal');
        const chemicalType = modal.dataset.chemicalType;
        const batchId = document.getElementById('new-batch-id').value;
        const maxArea = parseFloat(document.getElementById('max-area').value);
        
        if (!batchId.trim()) {
            this.showNotification('error', 'Error', 'Please enter a batch ID');
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
                this.showNotification('success', 'Chemical Reset', data.message);
                this.hideModal();
                this.loadChemicalStatus();
            } else {
                this.showNotification('error', 'Error', data.error || 'Failed to reset chemical batch');
            }
        } catch (error) {
            console.error('Error resetting chemical batch:', error);
            this.showNotification('error', 'Error', 'Failed to reset chemical batch');
        }
    }
    
    showChemicalInsertionModal() {
        const modal = document.getElementById('chemical-insertion-modal');
        const dateInput = document.getElementById('batch-date');
        
        // Set current date
        dateInput.value = new Date().toISOString().split('T')[0];
        
        // Reset checklist
        document.querySelectorAll('.chemical-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateChemicalChecklist();
        
        // Clear notes
        document.getElementById('batch-notes').value = '';
        
        modal.classList.add('show');
    }
    
    updateChemicalChecklist() {
        const checkboxes = document.querySelectorAll('.chemical-checkbox');
        const confirmButton = document.getElementById('confirm-chemical-insertion');
        
        // Update visual state of checklist items
        checkboxes.forEach(checkbox => {
            const item = checkbox.closest('.checklist-item');
            if (checkbox.checked) {
                item.classList.add('checked');
            } else {
                item.classList.remove('checked');
            }
        });
        
        // Enable/disable confirm button based on all checkboxes being checked
        const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
        confirmButton.disabled = !allChecked;
    }
    
    async confirmChemicalInsertion() {
        const capacity = parseFloat(document.getElementById('batch-capacity').value);
        const notes = document.getElementById('batch-notes').value;
        
        if (capacity <= 0) {
            this.showNotification('error', 'Error', 'Please enter a valid capacity');
            return;
        }
        
        try {
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
                this.showNotification('success', 'Chemicals Inserted', data.message);
                this.hideModal();
                this.loadChemicalStatus();
            } else {
                this.showNotification('error', 'Error', data.error || 'Failed to insert chemicals');
            }
        } catch (error) {
            console.error('Error inserting chemicals:', error);
            this.showNotification('error', 'Error', 'Failed to insert chemicals');
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadRolls();
            this.loadChemicalStatus();
        }, 30000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    // Utility methods
    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    formatDate(date) {
        return date.toLocaleDateString();
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    showNotification(type, title, message) {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <div>
                <strong>${title}</strong>
                <div>${message}</div>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Cleanup method
    destroy() {
        this.stopLocalTimer();
        this.stopAutoRefresh();
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
        
        timeElement.textContent = `${remainingMinutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        progressElement.textContent = `${progress.toFixed(1)}%`;
        
        // Update progress circle
        const circumference = 283; // 2 * π * 45
        const offset = circumference - (progress / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
        
        // Check if timer is complete
        if (remaining <= 0) {
            this.onTimerComplete();
        }
    }
    
    onTimerComplete() {
        // Stop the timer
        this.stopLocalTimer();
        
        // Show alarm notification
        this.showNotification('success', 'Development Complete!', 
            `30-minute development timer finished for roll ${this.selectedRoll.film_number}. Please check the development and mark as complete.`);
        
        // Play alarm sound (if browser supports it)
        this.playAlarmSound();
        
        // Change timer display to show completion
        const timeElement = document.getElementById('timer-time');
        timeElement.textContent = '00:00';
        timeElement.style.color = '#28a745'; // Green color
        
        // Flash the timer to draw attention
        this.flashTimer();
    }
    
    playAlarmSound() {
        try {
            // Create a simple beep sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800; // 800 Hz tone
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 1);
        } catch (error) {
            console.log('Could not play alarm sound:', error);
        }
    }
    
    flashTimer() {
        const timerContainer = document.getElementById('development-timer');
        let flashCount = 0;
        const maxFlashes = 6;
        
        const flashInterval = setInterval(() => {
            timerContainer.style.backgroundColor = flashCount % 2 === 0 ? '#28a745' : '';
            flashCount++;
            
            if (flashCount >= maxFlashes) {
                clearInterval(flashInterval);
                timerContainer.style.backgroundColor = '';
            }
        }, 500);
    }
    
    stopLocalTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
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
