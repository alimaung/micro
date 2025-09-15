/**
 * Film Allocation UI Module
 * 
 * This module handles UI updates and DOM manipulations for film allocation.
 */
const AllocationUI = (function() {
    // Cache DOM elements - lazy loaded to avoid null references
    const dom = {
        // Safely get an element, returning null if not found
        get: function(id) {
            return document.getElementById(id);
        },
        
        // Status elements
        get statusBadge() { return this.get('allocation-status-badge'); },
        get statusText() { 
            const badge = this.statusBadge;
            return badge ? badge.querySelector('span') : null; 
        },
        
        // Action buttons
        get startAllocationBtn() { return this.get('start-allocation'); },
        get resetAllocationBtn() { return this.get('reset-allocation'); },
        
        // Project info elements
        get projectIdEl() { return this.get('project-id'); },
        get documentCountEl() { return this.get('document-count'); },
        get totalPagesEl() { return this.get('total-pages'); },
        get workflowTypeEl() { return this.get('workflow-type'); },
        get oversizedCountEl() { return this.get('oversized-count'); },
        
        // Film sections
        get film16mmSection() { return this.get('film-16mm-section'); },
        get film35mmSection() { return this.get('film-35mm-section'); },
        get filmRolls16mm() { return this.get('film-rolls-16mm'); },
        get filmRolls35mm() { return this.get('film-rolls-35mm'); },
        
        // Statistics elements
        get rollCount16mm() { return this.get('roll-count-16mm'); },
        get pagesAllocated16mm() { return this.get('pages-allocated-16mm'); },
        get utilization16mm() { return this.get('utilization-16mm'); },
        
        get rollCount35mm() { return this.get('roll-count-35mm'); },
        get pagesAllocated35mm() { return this.get('pages-allocated-35mm'); },
        get utilization35mm() { return this.get('utilization-35mm'); },
        
        // Split documents elements
        get splitDocumentsPanel() { return this.get('split-documents-panel'); },
        get splitDocumentsTable() { return this.get('split-documents-table'); },
        
        // Allocation details elements
        get allocationDetailsJson() { return this.get('allocation-details-json'); },
        get copyAllocationDataBtn() { return this.get('copy-allocation-data'); },
        get exportAllocationDataBtn() { return this.get('export-allocation-data'); },
        
        // Modal elements
        get progressModal() { return this.get('allocation-progress-modal'); },
        get progressBar() { return this.get('allocation-progress-bar'); },
        get progressText() { return this.get('allocation-progress-text'); }
    };
    
    /**
     * Update UI based on workflow type
     */
    function updateWorkflowTypeUI() {
        const state = AllocationCore.getState();
        
        // Update the workflow type text
        if (dom.workflowTypeEl) {
            dom.workflowTypeEl.textContent = state.workflowType === 'hybrid' ? 'Hybrid (Oversized)' : 'Standard';
        }
        
        // Show/hide 35mm section based on workflow type
        if (dom.film35mmSection) {
            if (state.workflowType === 'hybrid') {
                dom.film35mmSection.classList.remove('hidden');
            } else {
                dom.film35mmSection.classList.add('hidden');
            }
        }
    }
    
    /**
     * Update project information in the UI
     */
    function updateProjectInfo() {
        const state = AllocationCore.getState();
        if (!state.analysisResults) return;
        
        // Update project info elements
        if (dom.projectIdEl) {
            dom.projectIdEl.textContent = state.analysisResults.projectId || state.projectId;
        }
        if (dom.documentCountEl) {
            dom.documentCountEl.textContent = state.analysisResults.documentCount || 0;
        }
        if (dom.totalPagesEl) {
            dom.totalPagesEl.textContent = state.analysisResults.totalPagesWithRefs || state.analysisResults.totalPages || 0;
        }
        if (dom.oversizedCountEl) {
            dom.oversizedCountEl.textContent = state.analysisResults.oversizedPages || 0;
        }
        
        // If project has oversized pages, make sure workflow type is hybrid
        if (state.analysisResults.hasOversized && state.workflowType !== 'hybrid') {
            state.workflowType = 'hybrid';
            updateWorkflowTypeUI();
        }
    }
    
    /**
     * Update the film rolls UI
     * 
     * @param {Array} rolls - Array of film roll objects
     * @param {HTMLElement} container - Container element for the film rolls
     * @param {string} type - Type of film ('16mm' or '35mm')
     */
    function updateFilmRollsUI(rolls, container, type) {
        if (!rolls || !rolls.length) {
            return;
        }
        
        if (!container) {
            return;
        }
        
        // Clear container
        container.innerHTML = '';
        
        // Get capacity based on type
        const capacity = type === '16mm' ? AllocationCore.CAPACITY_16MM : AllocationCore.CAPACITY_35MM;
        
        // Create film roll card grid
        const rollGrid = document.createElement('div');
        rollGrid.className = 'film-roll-grid';
        container.appendChild(rollGrid);
        
        // Create and append film roll elements
        rolls.forEach((roll, index) => {
            // Calculate utilization
            const utilization = Math.round((roll.pages_used / capacity) * 100);
            
            // Determine utilization class
            let utilizationClass = 'low';
            if (utilization > 80) {
                utilizationClass = 'high';
            } else if (utilization > 50) {
                utilizationClass = 'medium';
            }
            
            // Format roll ID with leading zeros
            const formattedRollId = String(roll.roll_id).padStart(3, '0');
            
            // Create film roll element
            const rollElement = document.createElement('div');
            rollElement.className = 'film-roll-card';
            rollElement.innerHTML = `
                <div class="film-roll-header">
                    <div class="roll-id">
                        <i class="fas fa-film"></i>
                        Roll ${type}-${formattedRollId}
                    </div>
                    <div class="roll-status-indicator ${roll.is_partial ? 'partial' : 'full'}">
                        ${roll.is_partial ? 'Partial' : 'Full'}
                    </div>
                </div>
                <div class="roll-usage-bar">
                    <div class="usage-fill ${utilizationClass}" style="width: ${utilization}%"></div>
                </div>
                <div class="roll-stats">
                    <div class="roll-stat">
                        <i class="fas fa-file-alt"></i>
                        <span>${roll.document_segments.length} document${roll.document_segments.length !== 1 ? 's' : ''}</span>
                    </div>
                    <div class="roll-stat">
                        <i class="fas fa-calculator"></i>
                        <span>${roll.pages_used} / ${capacity} pages</span>
                    </div>
                    <div class="roll-stat">
                        <i class="fas fa-tachometer-alt"></i>
                        <span>${utilization}% utilized</span>
                    </div>
                </div>
                <div class="roll-content">
                    <div class="documents-header">
                        <span>Document Allocation</span>
                        <button class="toggle-documents" aria-label="Toggle document list">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                    <div class="documents-list hidden">
                        ${roll.has_split_documents ? 
                        '<div class="roll-info-badge split"><i class="fas fa-cut"></i> Contains split documents</div>' : ''}
                    </div>
                </div>
            `;
            
            // Get unique documents
            const uniqueDocs = new Set();
            if (roll.document_segments && Array.isArray(roll.document_segments)) {
                roll.document_segments.forEach(segment => {
                    uniqueDocs.add(segment.doc_id);
                });
            }
            
            // Add document items to the documents list
            const docsList = rollElement.querySelector('.documents-list');
            if (docsList) {
                // Helper function for natural sorting of document IDs
                const naturalSort = (a, b) => {
                    // Extract numbers from document IDs if present
                    const aNum = /^(\d+)/.exec(a);
                    const bNum = /^(\d+)/.exec(b);
                    
                    // If both IDs start with numbers, compare them numerically
                    if (aNum && bNum) {
                        return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
                    }
                    
                    // Otherwise, fall back to standard string comparison
                    return a.localeCompare(b);
                };
                
                // Convert uniqueDocs Set to Array and sort naturally
                const sortedDocs = Array.from(uniqueDocs).sort(naturalSort);
                
                // Create document items in sorted order
                sortedDocs.forEach(docId => {
                    const segments = roll.document_segments.filter(seg => seg.doc_id === docId);
                    const totalPages = segments.reduce((sum, seg) => sum + seg.pages, 0);
                    const isSplit = segments.length > 1 || roll.has_split_documents;
                    
                    const docItem = document.createElement('div');
                    docItem.className = 'document-item';
                    docItem.innerHTML = `
                        <div class="document-info">
                            <span class="document-id">${docId}</span>
                            ${isSplit ? '<span class="document-badge">Split</span>' : ''}
                        </div>
                        <div class="document-details">
                            <span class="document-pages">${totalPages} pages</span>
                            ${segments.length > 1 ? 
                                `<span class="document-segments">${segments.length} segments</span>` : 
                                ''}
                        </div>
                    `;
                    docsList.appendChild(docItem);
                });
            }
            
            // Add roll to grid
            rollGrid.appendChild(rollElement);
            
            // Add click handler to toggle document list
            const toggleButton = rollElement.querySelector('.toggle-documents');
            if (toggleButton) {
                toggleButton.addEventListener('click', function() {
                    const docsList = rollElement.querySelector('.documents-list');
                    const icon = this.querySelector('i');
                    
                    if (docsList.classList.contains('hidden')) {
                        docsList.classList.remove('hidden');
                        icon.classList.remove('fa-chevron-down');
                        icon.classList.add('fa-chevron-up');
                    } else {
                        docsList.classList.add('hidden');
                        icon.classList.remove('fa-chevron-up');
                        icon.classList.add('fa-chevron-down');
                    }
                });
            }
        });
    }
    
    /**
     * Update the UI for 35mm allocation requests
     * 
     * @param {Array} requests - Array of allocation request objects
     */
    function updateAllocationRequests35mm(requests) {
        if (!requests || !requests.length) {
            return;
        }
        
        // Clear container
        dom.filmRolls35mm.innerHTML = '';
        
        // Create allocation requests grid
        const requestsGrid = document.createElement('div');
        requestsGrid.className = 'film-roll-grid';
        dom.filmRolls35mm.appendChild(requestsGrid);
        
        // Group requests by document ID
        const groupedRequests = {};
        requests.forEach(req => {
            if (!groupedRequests[req.doc_id]) {
                groupedRequests[req.doc_id] = [];
            }
            groupedRequests[req.doc_id].push(req);
        });
        
        // Create allocation request cards for each document
        Object.keys(groupedRequests)
            .sort((a, b) => {
                // Extract numbers from document IDs if present
                const aNum = /^(\d+)/.exec(a);
                const bNum = /^(\d+)/.exec(b);
                
                // If both IDs start with numbers, compare them numerically
                if (aNum && bNum) {
                    return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
                }
                
                // Otherwise, fall back to standard string comparison
                return a.localeCompare(b);
            })
            .forEach(docId => {
            const docRequests = groupedRequests[docId];
            const totalPages = docRequests.reduce((sum, req) => sum + req.pages, 0);
            const isSplit = docRequests.length > 1;
            
            // Create request card element
            const requestElement = document.createElement('div');
            requestElement.className = 'film-roll-card oversized-request';
            requestElement.innerHTML = `
                <div class="film-roll-header">
                    <div class="roll-id">
                        <i class="fas fa-file-alt"></i>
                        ${docId}
                    </div>
                    <div class="roll-status-indicator oversized">
                        Oversized
                    </div>
                </div>
                <div class="roll-stats">
                    <div class="roll-stat">
                        <i class="fas fa-calculator"></i>
                        <span>${totalPages} pages</span>
                    </div>
                    <div class="roll-stat">
                        <i class="fas fa-film"></i>
                        <span>35mm Film</span>
                    </div>
                    ${isSplit ? `
                    <div class="roll-stat">
                        <i class="fas fa-cut"></i>
                        <span>${docRequests.length} segments</span>
                    </div>` : ''}
                </div>
                <div class="roll-content">
                    <div class="documents-header">
                        <span>Allocation Request Details</span>
                        <button class="toggle-documents" aria-label="Toggle request details">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                    <div class="documents-list hidden">
                        ${isSplit ? '<div class="roll-info-badge split"><i class="fas fa-cut"></i> Document split across segments</div>' : ''}
                    </div>
                </div>
            `;
            
            // Add segment details if document is split
            if (isSplit) {
                const segmentsList = requestElement.querySelector('.documents-list');
                docRequests.forEach((req, index) => {
                    const segmentItem = document.createElement('div');
                    segmentItem.className = 'document-item';
                    segmentItem.innerHTML = `
                        <div class="document-info">
                            <span class="document-id">Segment ${index + 1}</span>
                        </div>
                        <div class="document-details">
                            <span class="document-pages">${req.pages} pages</span>
                            <span class="document-range">Pages ${req.page_range[0]}-${req.page_range[1]}</span>
                        </div>
                    `;
                    segmentsList.appendChild(segmentItem);
                });
            }
            
            // Add request to grid
            requestsGrid.appendChild(requestElement);
            
            // Add click handler to toggle details
            const toggleButton = requestElement.querySelector('.toggle-documents');
            if (toggleButton) {
                toggleButton.addEventListener('click', function() {
                    const detailsList = requestElement.querySelector('.documents-list');
                    const icon = this.querySelector('i');
                    
                    if (detailsList.classList.contains('hidden')) {
                        detailsList.classList.remove('hidden');
                        icon.classList.remove('fa-chevron-down');
                        icon.classList.add('fa-chevron-up');
                    } else {
                        detailsList.classList.add('hidden');
                        icon.classList.remove('fa-chevron-up');
                        icon.classList.add('fa-chevron-down');
                    }
                });
            }
        });
    }
    
    /**
     * Update the split documents UI
     * 
     * @param {Object} splitDocs16mm - Object with split documents for 16mm
     * @param {Object} splitDocs35mm - Object with split documents for 35mm
     */
    function updateSplitDocumentsUI(splitDocs16mm, splitDocs35mm) {
        // Combine split documents from both film types
        const splitDocs = { ...splitDocs16mm };
        
        // Check if we have any split documents
        const hasSplitDocs = Object.keys(splitDocs).length > 0;
        
        // Show or hide the panel
        if (hasSplitDocs) {
            dom.splitDocumentsPanel.classList.remove('hidden');
            
            // Clear table body
            const tableBody = dom.splitDocumentsTable.querySelector('tbody');
            tableBody.innerHTML = '';
            
            // Add rows for each split document
            Object.keys(splitDocs)
                .sort((a, b) => {
                    // Extract numbers from document IDs if present
                    const aNum = /^(\d+)/.exec(a);
                    const bNum = /^(\d+)/.exec(b);
                    
                    // If both IDs start with numbers, compare them numerically
                    if (aNum && bNum) {
                        return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
                    }
                    
                    // Otherwise, fall back to standard string comparison
                    return a.localeCompare(b);
                })
                .forEach(docId => {
                    const segments = splitDocs[docId];
                    const rolls = segments.map(seg => `Roll 16mm-${String(seg.roll).padStart(3, '0')}`).join(', ');
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${docId}</td>
                        <td>${segments.reduce((sum, seg) => sum + (seg.pageRange[1] - seg.pageRange[0] + 1), 0)}</td>
                        <td>${segments.length} rolls</td>
                        <td>${rolls}</td>
                    `;
                    tableBody.appendChild(row);
                });
            
            // Hide empty state
            dom.splitDocumentsPanel.querySelector('.empty-state').classList.add('hidden');
            dom.splitDocumentsPanel.querySelector('.data-table').classList.remove('hidden');
        } else {
            dom.splitDocumentsPanel.classList.add('hidden');
        }
    }
    
    /**
     * Update the status badge
     * 
     * @param {string} status - Status ('pending', 'in-progress', 'completed', 'error')
     * @param {string} text - Text to display
     */
    function updateStatusBadge(status, text) {
        if (!dom.statusBadge) return;
        
        // Update badge class
        dom.statusBadge.className = `status-badge ${status}`;
        
        // Update icon and text
        let icon = 'fa-clock';
        if (status === 'in-progress') icon = 'fa-sync fa-spin';
        if (status === 'completed') icon = 'fa-check-circle';
        if (status === 'error') icon = 'fa-exclamation-circle';
        
        dom.statusBadge.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${text}</span>
        `;
    }
    
    /**
     * Show the progress modal
     */
    function showProgressModal() {
        if (!dom.progressModal) return;
        
        dom.progressModal.classList.add('show');
        if (dom.progressBar) {
            dom.progressBar.style.width = '0%';
        }
        if (dom.progressText) {
            dom.progressText.textContent = 'Starting allocation...';
        }
    }
    
    /**
     * Hide the progress modal
     */
    function hideProgressModal() {
        if (!dom.progressModal) return;
        
        dom.progressModal.classList.remove('show');
    }
    
    /**
     * Update the allocation progress
     * 
     * @param {number} progress - Progress percentage (0-100)
     * @param {string} status - Status of the allocation task
     */
    function updateProgress(progress, status) {
        const state = AllocationCore.getState();
        
        dom.progressBar.style.width = `${progress}%`;
        
        let statusText = 'Allocating documents...';
        if (progress < 20) {
            statusText = 'Initializing allocation...';
        } else if (progress < 50) {
            statusText = 'Allocating documents to 16mm film...';
        } else if (progress < 80) {
            statusText = state.workflowType === 'hybrid'
                ? 'Allocating oversized pages to 35mm film...' 
                : 'Finalizing allocation...';
        } else {
            statusText = 'Generating allocation statistics...';
        }
        
        dom.progressText.textContent = statusText;
    }
    
    /**
     * Update the UI with allocation results
     */
    function updateAllocationResults() {
        const state = AllocationCore.getState();
        if (!state.allocationResults) {
            return;
        }
        
        // Check if results are nested inside a 'results' property (from API response)
        const allocationData = state.allocationResults.results ? state.allocationResults.results : state.allocationResults;
        
        // Update status badge
        updateStatusBadge('completed', 'Allocation complete');
        
        // Update 16mm film rolls
        if (allocationData.rolls_16mm && allocationData.rolls_16mm.length > 0) {
            updateFilmRollsUI(
                allocationData.rolls_16mm, 
                dom.filmRolls16mm, 
                '16mm'
            );
        }
        
        // Update statistics for 16mm
        if (dom.rollCount16mm) dom.rollCount16mm.textContent = allocationData.total_rolls_16mm || 0;
        if (dom.pagesAllocated16mm) dom.pagesAllocated16mm.textContent = allocationData.total_pages_16mm || 0;
        
        const avg16mmUtilization = allocationData.avg_utilization_16mm || 0;
        if (dom.utilization16mm) dom.utilization16mm.textContent = `${avg16mmUtilization}%`;
        
        // Update 35mm film rolls if needed
        if (state.workflowType === 'hybrid') {
            // First, check for actual 35mm rolls
            if (allocationData.rolls_35mm && allocationData.rolls_35mm.length > 0) {
                updateFilmRollsUI(
                    allocationData.rolls_35mm, 
                    dom.filmRolls35mm, 
                    '35mm'
                );
            } 
            // If no actual rolls, but we have allocation requests, show those
            else if (allocationData.doc_allocation_requests_35mm && 
                     allocationData.doc_allocation_requests_35mm.length > 0) {
                updateAllocationRequests35mm(allocationData.doc_allocation_requests_35mm);
            }
            
            // Update statistics for 35mm
            if (dom.rollCount35mm) dom.rollCount35mm.textContent = allocationData.total_rolls_35mm || 0;
            if (dom.pagesAllocated35mm) dom.pagesAllocated35mm.textContent = allocationData.total_pages_35mm || 0;
            if (dom.utilization35mm) dom.utilization35mm.textContent = allocationData.avg_utilization_35mm || 'N/A';
        }
        
        // Update split documents if any
        if (allocationData.split_documents_16mm || allocationData.split_documents_35mm) {
            updateSplitDocumentsUI(
                allocationData.split_documents_16mm || {},
                allocationData.split_documents_35mm || {}
            );
        }
        
        // Update JSON viewer
        if (dom.allocationDetailsJson) {
            dom.allocationDetailsJson.textContent = JSON.stringify(allocationData, null, 2);
        }
        
        // Enable reset button
        if (dom.resetAllocationBtn) {
            dom.resetAllocationBtn.disabled = false;
        }
        
        // Enable the "Continue to Index Generation" button
        const toIndexGenerationBtn = document.getElementById('to-step-6');
        if (toIndexGenerationBtn) {
            toIndexGenerationBtn.disabled = false;
        }
    }
    
    /**
     * Clear allocation results from the UI
     */
    function clearAllocationResults() {
        // Clear 16mm film rolls
        if (dom.filmRolls16mm) {
            dom.filmRolls16mm.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-film fa-3x"></i>
                    <p>No film rolls allocated yet. Click "Calculate Allocation" to start.</p>
                </div>
            `;
        }
        
        // Clear 35mm film rolls
        if (dom.filmRolls35mm) {
            dom.filmRolls35mm.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-film fa-3x"></i>
                    <p>No 35mm film rolls allocated yet.</p>
                </div>
            `;
        }
        
        // Reset statistics
        if (dom.rollCount16mm) dom.rollCount16mm.textContent = '0';
        if (dom.pagesAllocated16mm) dom.pagesAllocated16mm.textContent = '0';
        if (dom.utilization16mm) dom.utilization16mm.textContent = '0%';
        
        if (dom.rollCount35mm) dom.rollCount35mm.textContent = '0';
        if (dom.pagesAllocated35mm) dom.pagesAllocated35mm.textContent = '0';
        if (dom.utilization35mm) dom.utilization35mm.textContent = '0%';
        
        // Hide split documents panel
        if (dom.splitDocumentsPanel) {
            dom.splitDocumentsPanel.classList.add('hidden');
        }
        
        // Clear allocation details
        if (dom.allocationDetailsJson) {
            dom.allocationDetailsJson.textContent = '{}';
        }
    }
    
    /**
     * Copy allocation data to clipboard
     */
    function copyAllocationData() {
        const state = AllocationCore.getState();
        if (!state.allocationResults) return;
        
        const allocationJson = JSON.stringify(state.allocationResults, null, 2);
        
        navigator.clipboard.writeText(allocationJson)
            .then(() => {
                // Show success message
                showToast('Allocation data copied to clipboard');
            })
            .catch(err => {
                console.error('Failed to copy allocation data:', err);
            });
    }
    
    /**
     * Export allocation data as JSON file
     */
    function exportAllocationData() {
        const state = AllocationCore.getState();
        if (!state.allocationResults) return;
        
        const allocationJson = JSON.stringify(state.allocationResults, null, 2);
        const blob = new Blob([allocationJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `allocation_${state.projectId}_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    /**
     * Show a toast message
     * 
     * @param {string} message - Message to display
     * @param {string} type - Type of toast ('info', 'success', 'warning', 'error')
     */
    function showToast(message, type = 'info') {
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
    
    // Return public API
    return {
        getDomElements: () => dom,
        updateWorkflowTypeUI,
        updateProjectInfo,
        updateStatusBadge,
        updateProgress,
        updateAllocationResults,
        clearAllocationResults,
        showProgressModal,
        hideProgressModal,
        copyAllocationData,
        exportAllocationData,
        showToast
    };
})(); 