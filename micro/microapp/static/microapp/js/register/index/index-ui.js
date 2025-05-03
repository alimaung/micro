/**
 * Film Index UI Module
 * 
 * This module handles UI updates and DOM manipulations for film index generation.
 */
const IndexUI = (function() {
    // Cache DOM elements - lazy loaded to avoid null references
    const dom = {
        // Safely get an element, returning null if not found
        get: function(id) {
            return document.getElementById(id);
        },
        
        // Status elements
        get statusBadge() { return this.get('index-status-badge'); },
        get statusText() { 
            const badge = this.statusBadge;
            return badge ? badge.querySelector('span') : null; 
        },
        
        // Action buttons
        get generateIndexBtn() { return this.get('generate-index'); },
        get resetIndexBtn() { return this.get('reset-index'); },
        get updateIndexBtn() { return this.get('update-index'); },
        
        // Project info elements
        get projectIdEl() { return this.get('project-id'); },
        get archiveIdEl() { return this.get('archive-id'); },
        get documentCountEl() { return this.get('document-count'); },
        get rollCount16mmEl() { return this.get('roll-count-16mm'); },
        
        // COM List elements
        get comListPathEl() { return this.get('com-list-path'); },
        get comListStatusEl() { return this.get('com-list-status'); },
        get browseComListBtn() { return this.get('browse-com-list'); },
        
        // Index generation elements
        get generationStatusEl() { return this.get('generation-status'); },
        
        // Index preview elements
        get indexPreviewPanel() { return this.get('index-preview-panel'); },
        get indexTableBody() { return this.get('index-table-body'); },
        get tableInfo() { return this.get('table-info'); },
        get downloadCsvBtn() { return this.get('download-csv'); },
        
        // Film number elements
        get filmNumberPanel() { return this.get('film-number-panel'); },
        get updateStatusEl() { return this.get('update-status'); },
        
        // Final index elements
        get finalIndexPanel() { return this.get('final-index-panel'); },
        get finalIndexTableBody() { return this.get('final-index-table-body'); },
        get totalEntriesEl() { return this.get('total-entries'); },
        get updatedEntriesEl() { return this.get('updated-entries'); },
        get missingEntriesEl() { return this.get('missing-entries'); },
        get exportJsonBtn() { return this.get('export-json'); },
        get downloadFinalCsvBtn() { return this.get('download-final-csv'); },
        
        // Raw index data elements
        get indexDataPanel() { return this.get('index-data-panel'); },
        get indexDataContent() { return this.get('index-data-content'); },
        get indexDataJson() { return this.get('index-data-json'); },
        get toggleDataPanelBtn() { return this.get('toggle-data-panel'); },
        
        // Navigation buttons
        get backToAllocationBtn() { return this.get('back-to-allocation'); },
        get toFilmNumberBtn() { return this.get('to-step-5'); },
        
        // Modal elements
        get progressModal() { return this.get('index-progress-modal'); },
        get progressBar() { return this.get('index-progress-bar'); },
        get progressText() { return this.get('index-progress-text'); },
        get modalTitle() { return this.get('index-progress-modal').querySelector('.modal-title'); }
    };
    
    /**
     * Update project information in the UI
     */
    function updateProjectInfo() {
        const state = IndexCore.getState();
        
        // Get project ID from state
        const projectId = state.projectId || 'Unknown';
        
        // Get archive ID from various possible sources
        let archiveId = 'Unknown';
        let documentCount = 0;
        let rollCount16mm = 0;
        
        // Try to get archive ID from project info first
        if (state.projectInfo && state.projectInfo.archiveId) {
            archiveId = state.projectInfo.archiveId;
            console.log('Got archive ID from project info:', archiveId);
        }
        
        // If we have allocation results, get document count and roll count
        if (state.allocationResults) {
            console.log('Allocation results structure:', state.allocationResults);
            
            // Get top-level properties first
            if (state.allocationResults.archive_id) {
                archiveId = state.allocationResults.archive_id;
                console.log('Got archive ID from allocation results (top level):', archiveId);
            }
            
            // Get document count from top level
            if (state.allocationResults.documentCount) {
                documentCount = state.allocationResults.documentCount;
                console.log('Got document count from allocation results (top level):', documentCount);
            }
            
            // Check if we have nested results property
            const nestedResults = state.allocationResults.results || {};
            
            // If nested results have archive_id and we haven't found it yet, use it
            if (nestedResults.archive_id && archiveId === 'Unknown') {
                archiveId = nestedResults.archive_id;
                console.log('Got archive ID from nested results:', archiveId);
            }
            
            // Get roll counts
            if (nestedResults.rolls_16mm) {
                rollCount16mm = nestedResults.rolls_16mm.length;
                console.log('Got 16mm roll count from nested results:', rollCount16mm);
            } else if (state.allocationResults.partial_rolls_16mm) {
                // Try from top-level partial_rolls property
                rollCount16mm = state.allocationResults.partial_rolls_16mm.length;
                console.log('Got 16mm roll count from top-level partial_rolls:', rollCount16mm);
            }
            
            // If we still don't have document count, try from nested results
            if (documentCount === 0 && nestedResults.documentCount) {
                documentCount = nestedResults.documentCount;
                console.log('Got document count from nested results:', documentCount);
            }
            
            console.log('Final counts from allocation results:', { 
                archiveId, 
                documentCount, 
                rollCount16mm 
            });
        }
        
        // Update DOM elements with project info
        const projectIdElement = document.getElementById('project-id');
        const archiveIdElement = document.getElementById('archive-id');
        const documentCountElement = document.getElementById('document-count');
        const rollCountElement = document.getElementById('roll-count-16mm');
        
        if (projectIdElement) projectIdElement.textContent = projectId;
        if (archiveIdElement) archiveIdElement.textContent = archiveId;
        if (documentCountElement) documentCountElement.textContent = documentCount.toString();
        if (rollCountElement) rollCountElement.textContent = rollCount16mm.toString();
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
     * Update the index display with data
     */
    function updateIndexDisplay() {
        const state = IndexCore.getState();
        if (!state.indexData) return;
        
        // Show the index preview panel
        showIndexPreviewPanel();
        
        // Update the index table
        updateIndexTable(state.indexData);
        
        // Enable next step button
        if (dom.toFilmNumberBtn) {
            dom.toFilmNumberBtn.disabled = false;
        }
        
        // Update the raw index data
        if (dom.indexDataJson) {
            dom.indexDataJson.textContent = JSON.stringify(state.indexData, null, 2);
        }
        
        // Update the generation status
        if (dom.generationStatusEl) {
            dom.generationStatusEl.textContent = 'Status: Index generated';
            dom.generationStatusEl.style.borderLeftColor = '#4caf50';
        }
        
        // Update the status badge
        updateStatusBadge('completed', 'Index generated');
    }
    
    /**
     * Update the index table with data
     * 
     * @param {Object} indexData - The index data to display
     */
    function updateIndexTable(indexData) {
        if (!dom.indexTableBody) return;
        
        // Clear the table
        dom.indexTableBody.innerHTML = '';
        
        // Helper function for natural sorting of document IDs
        const naturalSort = (a, b) => {
            // Sort by docId (first element in entry array)
            const aId = a[0];
            const bId = b[0];
            
            // Extract numbers from document IDs if present
            const aNum = /^(\d+)/.exec(aId);
            const bNum = /^(\d+)/.exec(bId);
            
            // If both IDs start with numbers, compare them numerically
            if (aNum && bNum) {
                return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
            }
            
            // Otherwise, fall back to standard string comparison
            return aId.localeCompare(bId);
        };
        
        // Add rows for each index entry (limit to first 100 for performance)
        const entries = indexData.index || [];
        
        // Sort entries naturally by document ID
        const sortedEntries = [...entries].sort(naturalSort);
        
        const displayLimit = 100;
        const displayEntries = sortedEntries.slice(0, displayLimit);
        
        displayEntries.forEach(entry => {
            const docId = entry[0];
            const comId = entry[1];
            const initialIndex = entry[2] || [0, 0, 0];
            const finalIndex = entry[3] || '-';
            const docIndex = entry[4] || 1;
            
            const rollId = initialIndex[0];
            const frameStart = initialIndex[1];
            const frameEnd = initialIndex[2];
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${docId}</td>
                <td>${comId}</td>
                <td>${rollId}</td>
                <td>${frameStart}-${frameEnd}</td>
                <td>${finalIndex}</td>
            `;
            
            dom.indexTableBody.appendChild(row);
        });
        
        // Update table info
        if (dom.tableInfo) {
            dom.tableInfo.textContent = `Showing ${displayEntries.length} of ${entries.length} entries`;
        }
    }
    
    /**
     * Update the final index table with data
     * 
     * @param {Object} indexData - The final index data to display
     */
    function updateFinalIndexTable(indexData) {
        if (!dom.finalIndexTableBody) return;
        
        // Clear the table
        dom.finalIndexTableBody.innerHTML = '';
        
        // Helper function for natural sorting of document IDs
        const naturalSort = (a, b) => {
            // Sort by docId (first element in entry array)
            const aId = a[0];
            const bId = b[0];
            
            // Extract numbers from document IDs if present
            const aNum = /^(\d+)/.exec(aId);
            const bNum = /^(\d+)/.exec(bId);
            
            // If both IDs start with numbers, compare them numerically
            if (aNum && bNum) {
                return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
            }
            
            // Otherwise, fall back to standard string comparison
            return aId.localeCompare(bId);
        };
        
        // Add rows for each index entry (limit to first 100 for performance)
        const entries = indexData.index || [];
        
        // Sort entries naturally by document ID
        const sortedEntries = [...entries].sort(naturalSort);
        
        const displayLimit = 100;
        const displayEntries = sortedEntries.slice(0, displayLimit);
        
        displayEntries.forEach(entry => {
            const docId = entry[0];
            const comId = entry[1];
            const initialIndex = entry[2] || [0, 0, 0];
            const finalIndex = entry[3] || '-';
            
            const rollId = initialIndex[0];
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${docId}</td>
                <td>${comId}</td>
                <td>${rollId}</td>
                <td>${finalIndex}</td>
            `;
            
            dom.finalIndexTableBody.appendChild(row);
        });
        
        // Update statistics
        if (dom.totalEntriesEl) {
            dom.totalEntriesEl.textContent = entries.length;
        }
        
        if (dom.updatedEntriesEl && indexData.metadata) {
            dom.updatedEntriesEl.textContent = indexData.metadata.updated_count || 0;
        }
        
        if (dom.missingEntriesEl && indexData.metadata) {
            dom.missingEntriesEl.textContent = indexData.metadata.missing_count || 0;
        }
    }
    
    /**
     * Show the index preview panel
     */
    function showIndexPreviewPanel() {
        if (dom.indexPreviewPanel) {
            dom.indexPreviewPanel.classList.remove('hidden');
        }
    }
    
    /**
     * Hide the index preview panel
     */
    function hideIndexPreviewPanel() {
        if (dom.indexPreviewPanel) {
            dom.indexPreviewPanel.classList.add('hidden');
        }
    }
    
    /**
     * Show the film number panel
     */
    function showFilmNumberPanel() {
        if (dom.filmNumberPanel) {
            dom.filmNumberPanel.classList.remove('hidden');
        }
    }
    
    /**
     * Hide the film number panel
     */
    function hideFilmNumberPanel() {
        if (dom.filmNumberPanel) {
            dom.filmNumberPanel.classList.add('hidden');
        }
    }
    
    /**
     * Show the final index panel
     */
    function showFinalIndexPanel() {
        if (dom.finalIndexPanel) {
            dom.finalIndexPanel.classList.remove('hidden');
        }
    }
    
    /**
     * Hide the final index panel
     */
    function hideFinalIndexPanel() {
        if (dom.finalIndexPanel) {
            dom.finalIndexPanel.classList.add('hidden');
        }
    }
    
    /**
     * Show the progress modal
     * 
     * @param {string} title - Optional title for the modal
     * @param {string} text - Optional initial text for the progress
     */
    function showProgressModal(title, text) {
        if (!dom.progressModal) return;
        
        // Set title if provided
        if (title && dom.modalTitle) {
            dom.modalTitle.textContent = title;
        } else if (dom.modalTitle) {
            dom.modalTitle.textContent = 'Generating Film Index';
        }
        
        // Set initial text if provided
        if (text && dom.progressText) {
            dom.progressText.textContent = text;
        } else if (dom.progressText) {
            dom.progressText.textContent = 'Starting index generation...';
        }
        
        // Reset progress bar
        if (dom.progressBar) {
            dom.progressBar.style.width = '0%';
        }
        
        // Show the modal
        dom.progressModal.classList.add('show');
    }
    
    /**
     * Hide the progress modal
     */
    function hideProgressModal() {
        if (!dom.progressModal) return;
        
        dom.progressModal.classList.remove('show');
    }
    
    /**
     * Update the progress
     * 
     * @param {number} progress - Progress percentage (0-100)
     * @param {string} status - Status of the task
     */
    function updateProgress(progress, status) {
        if (dom.progressBar) {
            dom.progressBar.style.width = `${progress}%`;
        }
        
        if (dom.progressText && status) {
            dom.progressText.textContent = status;
        }
    }
    
    /**
     * Clear the index display
     */
    function clearIndexDisplay() {
        // Clear tables
        if (dom.indexTableBody) {
            dom.indexTableBody.innerHTML = '';
        }
        
        if (dom.finalIndexTableBody) {
            dom.finalIndexTableBody.innerHTML = '';
        }
        
        // Clear JSON view
        if (dom.indexDataJson) {
            dom.indexDataJson.textContent = '{}';
        }
        
        // Hide panels
        hideIndexPreviewPanel();
        hideFilmNumberPanel();
        hideFinalIndexPanel();
        
        // Reset generation status
        if (dom.generationStatusEl) {
            dom.generationStatusEl.textContent = 'Status: Not started';
            dom.generationStatusEl.style.borderLeftColor = '#ddd';
        }
        
        // Reset update status
        if (dom.updateStatusEl) {
            dom.updateStatusEl.textContent = 'Status: Not updated';
        }
        
        // Disable next button
        if (dom.toFilmNumberBtn) {
            dom.toFilmNumberBtn.disabled = true;
        }
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
    
    /**
     * Update the COM list information in the UI
     */
    function updateComListInfo() {
        const state = IndexCore.getState();
        let comListPath = state.comListPath;
        
        console.log('Updating COM list info with path:', comListPath);
        
        // If comListPath is not set, try to get it from projectInfo
        if (!comListPath && state.projectInfo && state.projectInfo.comlistPath) {
            comListPath = state.projectInfo.comlistPath;
            console.log('Using COM list path from project info:', comListPath);
            
            // Also update the state
            state.comListPath = comListPath;
        }
        
        // Update DOM elements
        if (dom.comListPathEl) {
            if (comListPath) {
                // Show the COM list path
                dom.comListPathEl.textContent = comListPath;
                
                // Get just the filename from the path
                const fileName = comListPath.split('\\').pop().split('/').pop();
                
                // Update status
                if (dom.comListStatusEl) {
                    dom.comListStatusEl.textContent = `COM list file: ${fileName}`;
                    dom.comListStatusEl.style.color = '#4caf50';
                }
                
                // Disable the browse button since we already have a COM list
                if (dom.browseComListBtn) {
                    dom.browseComListBtn.disabled = true;
                    dom.browseComListBtn.title = 'COM list already set';
                }
            } else {
                // No COM list path
                dom.comListPathEl.textContent = 'No COM list available';
                
                // Update status
                if (dom.comListStatusEl) {
                    dom.comListStatusEl.textContent = 'No COM list file found. Placeholder IDs will be used.';
                    dom.comListStatusEl.style.color = '#ff9800';
                }
            }
        }
    }
    
    // Return public API
    return {
        getDomElements: () => dom,
        updateProjectInfo,
        updateStatusBadge,
        updateIndexDisplay,
        updateProgress,
        showProgressModal,
        hideProgressModal,
        clearIndexDisplay,
        showFilmNumberPanel,
        hideFilmNumberPanel,
        showFinalIndexPanel,
        hideFinalIndexPanel,
        updateFinalIndexTable,
        updateComListInfo,
        showToast
    };
})(); 