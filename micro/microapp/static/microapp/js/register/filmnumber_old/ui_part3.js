/**
 * Film Number UI Status and Progress Functions - Part 3
 */

import { getState } from './core.js';

/**
 * Update status badge
 */
export function updateStatusBadge(status, text) {
    const dom = getDomElements();
    if (!dom.statusBadge) return;
    
    // Remove existing status classes
    dom.statusBadge.classList.remove('pending', 'in-progress', 'completed', 'error', 'warning');
    
    // Add new status class
    dom.statusBadge.classList.add(status);
    
    // Update icon
    let icon = 'fa-clock';
    switch (status) {
        case 'in-progress':
            icon = 'fa-spinner fa-spin';
            break;
        case 'completed':
            icon = 'fa-check-circle';
            break;
        case 'error':
            icon = 'fa-exclamation-circle';
            break;
        case 'warning':
            icon = 'fa-exclamation-triangle';
            break;
    }
    
    // Update HTML
    dom.statusBadge.innerHTML = `<i class="fas ${icon}"></i> <span>${text}</span>`;
}

/**
 * Show progress modal
 */
export function showProgressModal() {
    const dom = getDomElements();
    if (dom.progressModal) {
        dom.progressModal.classList.add('show');
    }
}

/**
 * Hide progress modal
 */
export function hideProgressModal() {
    const dom = getDomElements();
    if (dom.progressModal) {
        dom.progressModal.classList.remove('show');
    }
}

/**
 * Update progress bar
 */
export function updateProgress(progress) {
    const dom = getDomElements();
    if (dom.progressBar) {
        dom.progressBar.style.width = `${progress}%`;
        dom.progressBar.setAttribute('aria-valuenow', progress);
    }
}

/**
 * Update progress text
 */
export function updateProgressText(text) {
    const dom = getDomElements();
    if (dom.progressText) {
        dom.progressText.textContent = text;
    }
}

/**
 * Show error message
 */
export function showError(message) {
    console.error('Film number allocation error:', message);
    
    // Create or update error container
    let errorContainer = document.getElementById('filmnumber-error-container');
    
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'filmnumber-error-container';
        errorContainer.className = 'error-container';
        
        // Insert after status badge
        const dom = getDomElements();
        if (dom.statusBadge && dom.statusBadge.parentNode) {
            dom.statusBadge.parentNode.insertBefore(errorContainer, dom.statusBadge.nextSibling);
        } else {
            // Fallback - insert at the beginning of the component
            const component = document.querySelector('.allocation-component');
            if (component) {
                component.insertBefore(errorContainer, component.firstChild);
            }
        }
    }
    
    errorContainer.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            ${message}
        </div>
    `;
    
    errorContainer.style.display = 'block';
}

/**
 * Pre-populate UI with allocation data before film numbers are assigned
 */
export function prePopulateFromAllocation() {
    const state = getState();
    const dom = getDomElements();
    
    if (!state.allocationResults) {
        return;
    }
    
    // Update allocation summary
    updateAllocationSummary();
    
    // Clear existing roll displays
    clearRollContainers();
    
    // Get allocation results in the correct structure
    let allocationData;
    if (state.allocationResults.allocationResults && state.allocationResults.allocationResults.results) {
        allocationData = state.allocationResults.allocationResults.results;
    } else if (state.allocationResults.results) {
        allocationData = state.allocationResults.results;
    } else {
        allocationData = state.allocationResults;
    }
    
    console.log('Pre-populating UI with allocation data:', allocationData);
    
    // Display 16mm rolls
    if (allocationData.rolls_16mm && allocationData.rolls_16mm.length > 0) {
        renderPreAllocatedRolls(allocationData.rolls_16mm, '16mm');
    }
    
    // Display 35mm rolls if in hybrid mode
    if (state.workflowType === 'hybrid' && allocationData.rolls_35mm && allocationData.rolls_35mm.length > 0) {
        renderPreAllocatedRolls(allocationData.rolls_35mm, '35mm');
    }
    
    // Update JSON details
    if (dom.filmNumberDetailsJson) {
        dom.filmNumberDetailsJson.textContent = JSON.stringify(allocationData, null, 2);
    }
}

/**
 * Render rolls before film number allocation with collapsible document sections
 */
function renderPreAllocatedRolls(rolls, filmType) {
    const dom = getDomElements();
    const container = filmType === '16mm' ? dom.filmRolls16mm : dom.filmRolls35mm;
    
    if (!container) return;
    
    // Clear any existing empty state
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // For each roll, create a roll card without film numbers
    rolls.forEach(roll => {
        const rollCard = document.createElement('div');
        rollCard.className = 'roll-card pre-allocated';
        
        // Create header with placeholder for film number
        const cardHeader = document.createElement('div');
        cardHeader.className = 'roll-card-header';
        
        // Add film number placeholder with "pending" state
        const filmNumberEl = document.createElement('div');
        filmNumberEl.className = 'film-number pending';
        filmNumberEl.innerHTML = `<strong>Film #:</strong> <span class="pending-badge">Pending Allocation</span>`;
        cardHeader.appendChild(filmNumberEl);
        
        // Add roll ID and type
        const rollInfoEl = document.createElement('div');
        rollInfoEl.className = 'roll-info';
        rollInfoEl.innerHTML = `<span>Roll ID: ${roll.roll_id}</span> <span>Type: ${filmType}</span>`;
        cardHeader.appendChild(rollInfoEl);
        
        rollCard.appendChild(cardHeader);
        
        // Create usage statistics
        const usageStats = document.createElement('div');
        usageStats.className = 'usage-stats';
        
        // Calculate utilization
        const capacity = filmType === '16mm' ? CAPACITY_16MM : CAPACITY_35MM;
        const utilization = Math.round((roll.pages_used / capacity) * 100);
        
        usageStats.innerHTML = `
            <div class="usage-bar">
                <div class="usage-fill" style="width: ${utilization}%"></div>
            </div>
            <div class="usage-text">
                <span>${roll.pages_used} pages used / ${capacity} capacity (${utilization}%)</span>
            </div>
        `;
        
        rollCard.appendChild(usageStats);
        
        // Create document list with collapsible functionality
        if (roll.document_segments && roll.document_segments.length > 0) {
            const docsContainer = document.createElement('div');
            docsContainer.className = 'documents-container';
            
            // Create collapsible header
            const docsHeader = document.createElement('div');
            docsHeader.className = 'docs-header';
            docsHeader.innerHTML = `
                <h5>
                    <i class="fas fa-file-alt"></i>
                    Documents (${roll.document_segments.length})
                </h5>
                <span class="toggle-icon">
                    <i class="fas fa-chevron-down"></i>
                </span>
            `;
            docsContainer.appendChild(docsHeader);
            
            // Create content container
            const docsContent = document.createElement('div');
            docsContent.className = 'docs-content';
            
            // Create table for documents - use simpler headers without blip info
            const docsTable = document.createElement('table');
            docsTable.className = 'docs-table';
            docsTable.innerHTML = `
                <thead>
                    <tr>
                        <th>Doc ID</th>
                        <th>Pages</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            // Add document segments
            roll.document_segments.forEach(segment => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${segment.doc_id}</td>
                    <td>${segment.pages}</td>
                `;
                docsTable.querySelector('tbody').appendChild(row);
            });
            
            docsContent.appendChild(docsTable);
            docsContainer.appendChild(docsContent);
            rollCard.appendChild(docsContainer);
            
            // Add click event for collapsing/expanding
            docsHeader.addEventListener('click', function() {
                // Toggle collapsed class on header
                this.classList.toggle('collapsed');
                
                // Toggle collapsed class on content
                const content = this.nextElementSibling;
                if (content.classList.contains('collapsed')) {
                    content.classList.remove('collapsed');
                    content.style.maxHeight = content.scrollHeight + 'px';
                    // Animate icon
                    const icon = this.querySelector('.toggle-icon i');
                    icon.className = 'fas fa-chevron-down';
                    icon.classList.add('rotate-icon');
                    setTimeout(() => icon.classList.remove('rotate-icon'), 300);
                } else {
                    content.classList.add('collapsed');
                    content.style.maxHeight = '0';
                    // Animate icon
                    const icon = this.querySelector('.toggle-icon i');
                    icon.className = 'fas fa-chevron-right';
                    icon.classList.add('rotate-icon');
                    setTimeout(() => icon.classList.remove('rotate-icon'), 300);
                }
            });
        }
        
        container.appendChild(rollCard);
    });
}

/**
 * Show a toast message
 * 
 * @param {string} message - Message to display
 * @param {string} type - Type of toast ('info', 'success', 'warning', 'error')
 */
export function showToast(message, type = 'info') {
    // Check if toast container exists, create if not
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Auto-remove after delay
    setTimeout(() => {
        toast.classList.add('toast-hide');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, 3000);
}

// Placeholders for functions that will be imported in ui.js
function clearRollContainers() {}
function updateAllocationSummary() {}
const CAPACITY_16MM = 2900;
const CAPACITY_35MM = 110;
function getDomElements() {
    return {};
} 