// Label Management JavaScript

class LabelManager {
    constructor() {
        this.selectedRolls = new Set();
        this.generatedLabels = [];
        this.printQueue = [];
        this.init();
    }
    
    init() {
        console.log('Label Manager initialized');
        this.bindEvents();
        this.loadInitialData();
    }
    
    bindEvents() {
        // Refresh buttons
        document.getElementById('refresh-rolls').addEventListener('click', () => {
            this.loadRolls();
        });
        
        document.getElementById('refresh-queue').addEventListener('click', () => {
            this.loadPrintQueue();
        });
        
        // Bulk actions
        document.getElementById('select-all-rolls').addEventListener('click', () => {
            this.selectAllRolls();
        });
        
        document.getElementById('clear-selection').addEventListener('click', () => {
            this.clearSelection();
        });
        
        document.getElementById('generate-selected').addEventListener('click', () => {
            this.generateSelectedLabels();
        });
        
        document.getElementById('clear-generated').addEventListener('click', () => {
            this.clearGeneratedLabels();
        });
        
        // Dynamic event delegation for roll cards and label actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.roll-card')) {
                this.handleRollClick(e.target.closest('.roll-card'));
            }
            
            if (e.target.closest('.download-label')) {
                this.downloadLabel(e.target.closest('.download-label').dataset.labelId);
            }
            
            if (e.target.closest('.add-to-queue')) {
                this.addToQueue(e.target.closest('.add-to-queue').dataset.labelId);
            }
            
            if (e.target.closest('.remove-from-queue')) {
                this.removeFromQueue(e.target.closest('.remove-from-queue').dataset.queueId);
            }
            
            if (e.target.closest('.print-label')) {
                this.printLabel(e.target.closest('.print-label').dataset.labelId);
            }
        });
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadRolls(),
                this.loadGeneratedLabels(),
                this.loadPrintQueue(),
                this.loadPrinterStatus()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('error', 'Error', 'Failed to load dashboard data');
        }
    }
    
    async loadRolls() {
        try {
            const response = await fetch('/api/labels/rolls/');
            const data = await response.json();
            
            if (data.success) {
                this.renderRolls(data.rolls);
                this.updateSelectionInfo();
            } else {
                throw new Error(data.error || 'Failed to load rolls');
            }
        } catch (error) {
            console.error('Error loading rolls:', error);
            this.showNotification('error', 'Error', 'Failed to load developed rolls');
        }
    }
    
    renderRolls(rolls) {
        const container = document.getElementById('rolls-grid');
        
        if (rolls.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-film"></i>
                    <p>No developed rolls available</p>
                    <small>Complete development first to see rolls here</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = rolls.map(roll => {
            const isSelected = this.selectedRolls.has(roll.id);
            const hasLabel = roll.has_label;
            const isCompleted = roll.label_completed;
            
            return `
                <div class="roll-card ${isSelected ? 'selected' : ''} ${hasLabel ? 'has-label' : ''} ${isCompleted ? 'completed' : ''}" data-roll-id="${roll.id}">
                    <div class="roll-header">
                        <div class="roll-title">
                            <div class="roll-film-number">${roll.film_number}</div>
                            <div class="roll-film-type">${roll.film_type}</div>
                        </div>
                        <div class="roll-status-badge ${hasLabel ? (isCompleted ? 'completed' : 'generated') : 'ready'}">
                            ${hasLabel ? (isCompleted ? 'Completed' : 'Generated') : 'Ready'}
                        </div>
                    </div>
                    
                    <div class="roll-details">
                        <div class="detail-item">
                            <span class="label">Project:</span>
                            <span class="value">${roll.project_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Archive ID:</span>
                            <span class="value">${roll.archive_id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Doc Type:</span>
                            <span class="value">${roll.doc_type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Pages:</span>
                            <span class="value">${roll.pages_used}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Developed:</span>
                            <span class="value">${this.formatDateTime(roll.development_completed_at)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Label Status:</span>
                            <span class="value ${hasLabel ? 'text-success' : (roll.can_generate_label ? 'text-warning' : 'text-error')}">
                                ${hasLabel ? (isCompleted ? 'Completed' : roll.label_status) : (roll.can_generate_label ? 'Ready' : 'Cannot Generate')}
                            </span>
                        </div>
                    </div>
                    
                    ${isCompleted ? `
                        <div class="roll-overlay completed">
                            <i class="fas fa-check-circle"></i>
                            <span>Label Completed</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        this.rolls = rolls; // Store for reference
    }
    
    handleRollClick(card) {
        const rollId = parseInt(card.dataset.rollId);
        const roll = this.rolls.find(r => r.id === rollId);
        
        if (!roll || !roll.can_generate_label) {
            this.showNotification('warning', 'Cannot Select', 'This roll cannot generate labels (missing film number or archive ID)');
            return;
        }
        
        // Don't allow selection of rolls that already have completed labels
        if (roll.label_completed) {
            this.showNotification('info', 'Already Completed', 'This roll already has a completed label');
            return;
        }
        
        // Don't allow selection of rolls that already have labels (unless we want to regenerate)
        if (roll.has_label) {
            this.showNotification('info', 'Label Exists', 'This roll already has a generated label. Check the Generated Labels section.');
            return;
        }
        
        if (this.selectedRolls.has(rollId)) {
            this.selectedRolls.delete(rollId);
            card.classList.remove('selected');
        } else {
            this.selectedRolls.add(rollId);
            card.classList.add('selected');
        }
        
        this.updateSelectionInfo();
    }
    
    selectAllRolls() {
        this.selectedRolls.clear();
        this.rolls.forEach(roll => {
            if (roll.can_generate_label && !roll.has_label && !roll.label_completed) {
                this.selectedRolls.add(roll.id);
            }
        });
        this.updateRollSelection();
        this.updateSelectionInfo();
    }
    
    clearSelection() {
        this.selectedRolls.clear();
        this.updateRollSelection();
        this.updateSelectionInfo();
    }
    
    updateRollSelection() {
        document.querySelectorAll('.roll-card').forEach(card => {
            const rollId = parseInt(card.dataset.rollId);
            if (this.selectedRolls.has(rollId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }
    
    updateSelectionInfo() {
        const count = this.selectedRolls.size;
        document.getElementById('selection-count').textContent = `${count} roll${count !== 1 ? 's' : ''} selected`;
        document.getElementById('generate-selected').disabled = count === 0;
    }
    
    async generateSelectedLabels() {
        if (this.selectedRolls.size === 0) return;
        
        const rollIds = Array.from(this.selectedRolls);
        
        try {
            this.showNotification('info', 'Generating Labels', 'Creating PDF labels and saving to project directories...');
            
            const response = await fetch('/api/labels/generate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    roll_ids: rollIds
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Labels Generated', data.message);
                
                // Clear selection after successful generation
                this.clearSelection();
                
                // Reload all data to show updated status
                await this.loadInitialData();
            } else {
                throw new Error(data.error || 'Failed to generate labels');
            }
        } catch (error) {
            console.error('Error generating labels:', error);
            this.showNotification('error', 'Error', 'Failed to generate labels');
        }
    }
    
    async loadGeneratedLabels() {
        try {
            const response = await fetch('/api/labels/generated/');
            const data = await response.json();
            
            if (data.success) {
                this.generatedLabels = data.labels;
                this.renderGeneratedLabels();
            } else {
                throw new Error(data.error || 'Failed to load generated labels');
            }
        } catch (error) {
            console.error('Error loading generated labels:', error);
            this.showNotification('error', 'Error', 'Failed to load generated labels');
        }
    }
    
    renderGeneratedLabels() {
        const container = document.getElementById('generated-labels');
        
        if (this.generatedLabels.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-pdf"></i>
                    <p>No labels generated yet</p>
                    <small>Select rolls above and click "Generate Labels"</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.generatedLabels.map(label => `
            <div class="label-item ${label.is_completed ? 'completed' : ''}">
                <div class="label-item-header">
                    <div class="label-info">
                        <h4>${label.film_number}</h4>
                        <p>${label.archive_id} - ${label.doc_type}</p>
                        <small>Generated: ${this.formatDateTime(label.generated_at)}</small>
                        ${label.printed_at ? `<small>Printed: ${this.formatDateTime(label.printed_at)}</small>` : ''}
                        ${label.pdf_saved ? '<small class="text-success"><i class="fas fa-check"></i> Saved to project</small>' : ''}
                    </div>
                    <div class="label-status-badge ${label.status}">
                        ${this.getStatusDisplayText(label.status)}
                        ${label.is_completed ? '<i class="fas fa-check-circle"></i>' : ''}
                    </div>
                </div>
                <div class="label-actions">
                    <button class="btn btn-primary btn-small download-label" data-label-id="${label.label_id}">
                        <i class="fas fa-download"></i> Download ${label.download_count > 0 ? `(${label.download_count})` : ''}
                    </button>
                    ${label.status === 'generated' || label.status === 'downloaded' ? `
                        <button class="btn btn-secondary btn-small add-to-queue" data-label-id="${label.label_id}">
                            <i class="fas fa-plus"></i> Add to Queue
                        </button>
                    ` : ''}
                    <button class="btn btn-outline btn-small print-label" data-label-id="${label.label_id}">
                        <i class="fas fa-print"></i> Print ${label.print_count > 0 ? `(${label.print_count})` : ''}
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    clearGeneratedLabels() {
        // Note: This now only clears the UI, not the database records
        this.generatedLabels = [];
        this.renderGeneratedLabels();
        this.showNotification('info', 'View Cleared', 'Generated labels view cleared (labels still saved in database)');
    }
    
    async downloadLabel(labelId) {
        try {
            const response = await fetch(`/api/labels/download/${labelId}/`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `film_label_${labelId}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showNotification('success', 'Downloaded', 'Label PDF downloaded successfully');
                
                // Reload generated labels to show updated download count
                this.loadGeneratedLabels();
            } else {
                throw new Error('Failed to download label');
            }
        } catch (error) {
            console.error('Error downloading label:', error);
            this.showNotification('error', 'Error', 'Failed to download label');
        }
    }
    
    async addToQueue(labelId) {
        try {
            const response = await fetch('/api/labels/print-queue/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    label_ids: [labelId]
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.loadPrintQueue();
                this.loadGeneratedLabels(); // Reload to show updated status
                this.showNotification('success', 'Added to Queue', data.message);
            } else {
                throw new Error(data.error || 'Failed to add to queue');
            }
        } catch (error) {
            console.error('Error adding to queue:', error);
            this.showNotification('error', 'Error', 'Failed to add to print queue');
        }
    }
    
    async loadPrintQueue() {
        try {
            const response = await fetch('/api/labels/print-queue/');
            const data = await response.json();
            
            if (data.success) {
                this.printQueue = data.queue;
                this.renderPrintQueue();
            } else {
                throw new Error(data.error || 'Failed to load print queue');
            }
        } catch (error) {
            console.error('Error loading print queue:', error);
            this.showNotification('error', 'Error', 'Failed to load print queue');
        }
    }
    
    async loadPrinterStatus() {
        try {
            const response = await fetch('/api/labels/printer-status/');
            const data = await response.json();
            
            if (data.success) {
                this.updatePrinterStatusDisplay(data.printer_status);
            } else {
                throw new Error(data.error || 'Failed to load printer status');
            }
        } catch (error) {
            console.error('Error loading printer status:', error);
            this.updatePrinterStatusDisplay({
                default_printer: null,
                available_printers: [],
                system: { windows: false, linux: false, mac: false }
            });
        }
    }
    
    updatePrinterStatusDisplay(status) {
        const statusText = document.getElementById('printer-status-text');
        const detailsText = document.getElementById('printer-details');
        
        if (status.default_printer) {
            statusText.textContent = 'Printing Method: Server-Side Direct Printing';
            detailsText.innerHTML = `
                <strong>Default Printer:</strong> ${status.default_printer}<br>
                <strong>Available Printers:</strong> ${status.available_printers.length} found<br>
                <strong>System:</strong> ${this.getSystemName(status.system)}
            `;
        } else {
            statusText.textContent = 'Printing Method: No Printer Configured';
            detailsText.innerHTML = `
                <span style="color: var(--color-warning);">
                    <i class="fas fa-exclamation-triangle"></i>
                    No default printer found. Please configure a printer in your system settings.
                </span>
            `;
        }
    }
    
    getSystemName(system) {
        if (system.windows) return 'Windows';
        if (system.linux) return 'Linux';
        if (system.mac) return 'macOS';
        return 'Unknown';
    }
    
    renderPrintQueue() {
        const container = document.getElementById('print-queue');
        
        if (this.printQueue.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-print"></i>
                    <p>Print queue is empty</p>
                    <small>Add generated labels to the queue</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.printQueue.map(item => `
            <div class="queue-item">
                <div class="queue-info">
                    <h5>${item.film_number} - ${item.archive_id}</h5>
                    <p>Added: ${this.formatDateTime(item.added_at)}</p>
                    <small>${item.doc_type}</small>
                </div>
                <div class="queue-status ${item.status}">${item.status}</div>
                <button class="btn btn-secondary btn-small remove-from-queue" data-queue-id="${item.queue_id}">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
        `).join('');
    }
    
    async removeFromQueue(queueId) {
        try {
            const response = await fetch(`/api/labels/print-queue/remove/${queueId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.loadPrintQueue();
                this.loadGeneratedLabels(); // Reload to show updated status
                this.showNotification('success', 'Removed', data.message);
            } else {
                throw new Error(data.error || 'Failed to remove from queue');
            }
        } catch (error) {
            console.error('Error removing from queue:', error);
            this.showNotification('error', 'Error', 'Failed to remove from print queue');
        }
    }
    
    async printLabel(labelId) {
        // Server-side printing - no user interaction required
        try {
            this.showNotification('info', 'Printing Label', 'Sending label to printer...');
            
            const response = await fetch(`/api/labels/print/${labelId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    copies: 1  // Default to 1 copy, could be made configurable
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Label Printed', 
                    `Label printed successfully to ${data.printer} using ${data.method}`);
                
                // Reload data to show updated status
                this.loadGeneratedLabels();
                this.loadRolls(); // Update roll status too
            } else {
                throw new Error(data.error || 'Failed to print label');
            }
            
        } catch (error) {
            console.error('Error printing label:', error);
            
            if (error.message.includes('expired')) {
                this.showNotification('warning', 'Label Expired', 'This label has expired from cache. Please regenerate it and try printing again.');
            } else {
                this.showNotification('error', 'Print Error', `Failed to print label: ${error.message}`);
            }
        }
    }
    
    // Utility methods
    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    getStatusDisplayText(status) {
        const statusMap = {
            'generated': 'Generated',
            'downloaded': 'Downloaded',
            'queued': 'Queued',
            'printed': 'Printed',
            'completed': 'Completed'
        };
        return statusMap[status] || status;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    showNotification(type, title, message) {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-${icons[type]}" style="color: var(--color-${type === 'error' ? 'error' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'});"></i>
                <strong style="color: var(--color-text-primary);">${title}</strong>
            </div>
            <div style="color: var(--color-text-secondary); font-size: 0.9rem;">${message}</div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }
}

// Initialize label manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.labelManager = new LabelManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.labelManager) {
        console.log('Label Manager cleanup');
    }
}); 