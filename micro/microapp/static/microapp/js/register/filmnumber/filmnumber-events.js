/**
 * Film Number Allocation Events Module
 * 
 * This module handles all event binding and event handling for the film number allocation step.
 * Uses IIFE pattern to encapsulate functionality while exposing a public API.
 */

const FilmNumberEvents = (function() {
    // Import dependencies
    const { getState, startFilmNumberAllocation, resetFilmNumberAllocation } = window.FilmNumberCore || {};
    const FilmNumberUI = window.FilmNumberUI || {};
    
    /**
     * Bind all event listeners
     */
    function bindEvents() {
        const dom = FilmNumberUI.getDomElements ? FilmNumberUI.getDomElements() : {};
        
        // Start film number allocation button
        if (dom.startFilmNumberBtn) {
            dom.startFilmNumberBtn.addEventListener('click', window.FilmNumberCore.startFilmNumberAllocation);
        }
        
        // Reset button
        if (dom.resetFilmNumberBtn) {
            dom.resetFilmNumberBtn.addEventListener('click', window.FilmNumberCore.resetFilmNumberAllocation);
        }
        
        // Navigation buttons
        if (dom.backBtn) {
            dom.backBtn.addEventListener('click', navigateToIndex);
        }
        
        if (dom.toNextStepBtn) {
            dom.toNextStepBtn.addEventListener('click', navigateToNextStep);
        }
        
        // Copy and export buttons
        const copyBtn = document.getElementById('copy-filmnumber-data');
        if (copyBtn) {
            copyBtn.addEventListener('click', copyFilmNumberData);
        }
        
        const exportBtn = document.getElementById('export-filmnumber-data');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportFilmNumberData);
        }
        
        // Add event listener for index table search
        const searchInput = document.getElementById('index-search');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function() {
                filterTable(this.value);
            }, 300));
        }
        
        // Add event listeners for table sorting
        const tableHeaders = document.querySelectorAll('#index-table th');
        if (tableHeaders) {
            tableHeaders.forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.textContent.toLowerCase().replace(/\s+/g, '');
                    sortTable(column);
                });
            });
        }
    }

    /**
     * Navigate back to allocation
     */
    function navigateToIndex() {
        const state = getState();
        window.location.href = `/register/index/?id=${state.projectId}&flow=${state.workflowType}`;
    }

    /**
     * Navigate to the next step
     */
    function navigateToNextStep() {
        const state = getState();
        console.log('Navigating to next step...');
        
        // First, check if we need to create the film data object
        try {
            // Try to get existing film data for current project
            const savedFilmData = window.FilmNumberCore.checkForSavedFilmData();
            
            // If not found, create it now
            if (!savedFilmData && state.filmNumberResults) {
                console.log('Creating film data object before navigation...');
                window.FilmNumberCore.createFilmDataObject();
            }
            
            // Log the saved data (if any)
            console.log('Current film data state before navigation:', 
                window.FilmNumberCore.getLocalStorageData('microfilmFilmData'));
                
        } catch (error) {
            console.error('Error handling film data before navigation:', error);
        }
        
        // Navigate to the next step
        window.location.href = `/register/references/?id=${state.projectId}&flow=${state.workflowType}`;
    }

    /**
     * Copy film number data to clipboard
     */
    function copyFilmNumberData() {
        const dom = FilmNumberUI.getDomElements ? FilmNumberUI.getDomElements() : {};
        if (dom.filmNumberDetailsJson) {
            const text = dom.filmNumberDetailsJson.textContent;
            navigator.clipboard.writeText(text)
                .then(() => {
                    // Show success message
                    const copyBtn = document.getElementById('copy-filmnumber-data');
                    if (copyBtn) {
                        const originalTitle = copyBtn.getAttribute('title');
                        copyBtn.setAttribute('title', 'Copied!');
                        copyBtn.classList.add('success');
                        
                        // Reset after short delay
                        setTimeout(() => {
                            copyBtn.setAttribute('title', originalTitle);
                            copyBtn.classList.remove('success');
                        }, 2000);
                    }
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                });
        }
    }

    /**
     * Export film number data as JSON file
     */
    function exportFilmNumberData() {
        const state = getState();
        
        if (!state.filmNumberResults) return;
        
        // Prepare data
        const data = JSON.stringify(state.filmNumberResults, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // Create download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `film_number_allocation_${state.projectId}_${new Date().toISOString().slice(0, 10)}.json`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    }

    /**
     * Filter table based on search term
     */
    function filterTable(searchTerm) {
        const state = getState();
        
        // First check if we have the new filmIndexData structure, and if not fall back to indexData
        const indexDataToUse = state.filmIndexData || state.indexData;
        
        if (!indexDataToUse || !indexDataToUse.entries) return;
        
        const tableBody = document.getElementById('index-table-body');
        if (!tableBody) return;
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Filter entries if search term provided
        let filteredEntries = indexDataToUse.entries;
        if (searchTerm && searchTerm.trim() !== '') {
            const term = searchTerm.trim().toLowerCase();
            filteredEntries = indexDataToUse.entries.filter(entry => {
                return (
                    String(entry.docId).toLowerCase().includes(term) ||
                    String(entry.comId).toLowerCase().includes(term) ||
                    String(entry.rollId).toLowerCase().includes(term) ||
                    String(entry.filmNumber).toLowerCase().includes(term) ||
                    String(entry.finalIndex).toLowerCase().includes(term) ||
                    String(entry.status).toLowerCase().includes(term)
                );
            });
        }
        
        // Sort entries
        const sortedEntries = sortEntries(filteredEntries);
        
        // Limit display for performance
        const displayLimit = 100;
        const displayEntries = sortedEntries.slice(0, displayLimit);
        
        // Add rows for each filtered entry
        displayEntries.forEach(entry => {
            const row = document.createElement('tr');
            
            // Add status-based class
            if (entry.status === 'Updated') {
                row.className = 'updated-entry';
            }
            
            row.innerHTML = `
                <td>${entry.docId}</td>
                <td>${entry.comId}</td>
                <td>${entry.rollId || '-'}</td>
                <td>${entry.frameStart ? `${entry.frameStart}-${entry.frameEnd}` : '-'}</td>
                <td>${entry.filmNumber || 'N/A'}</td>
                <td>${entry.finalIndex || 'Pending'}</td>
                <td><span class="status-badge ${entry.status.toLowerCase()}">${entry.status}</span></td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Update table info
        const tableInfo = document.getElementById('table-info');
        if (tableInfo) {
            tableInfo.textContent = `Showing ${displayEntries.length} of ${filteredEntries.length} entries`;
        }
    }

    /**
     * Sort entries by specified column
     */
    function sortTable(column) {
        const state = getState();
        
        // First check if we have the new filmIndexData structure, and if not fall back to indexData
        const indexDataToUse = state.filmIndexData || state.indexData;
        
        if (!indexDataToUse || !indexDataToUse.entries) return;
        
        // Toggle sort direction
        state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
        state.sortColumn = column;
        
        // Update UI to show sort direction
        updateSortIndicators(column);
        
        // Refresh table display
        FilmNumberUI.updateIndexTable();
    }

    /**
     * Update sort direction indicators in table headers
     */
    function updateSortIndicators(activeColumn) {
        const headers = document.querySelectorAll('#index-table th');
        headers.forEach(header => {
            const column = header.textContent.toLowerCase().replace(/\s+/g, '');
            const icon = header.querySelector('.sort-icon') || document.createElement('i');
            icon.className = 'sort-icon fas';
            
            if (column === activeColumn) {
                icon.className += getState().sortDirection === 'asc' ? ' fa-sort-up' : ' fa-sort-down';
            } else {
                icon.className += ' fa-sort';
            }
            
            if (!header.querySelector('.sort-icon')) {
                header.appendChild(icon);
            }
        });
    }

    /**
     * Sort entries based on current sort column and direction
     */
    function sortEntries(entries) {
        const state = getState();
        const column = state.sortColumn || 'docid';
        const direction = state.sortDirection || 'asc';
        
        return [...entries].sort((a, b) => {
            let valueA = a[column] || '';
            let valueB = b[column] || '';
            
            // Handle numeric values
            if (!isNaN(valueA) && !isNaN(valueB)) {
                valueA = Number(valueA);
                valueB = Number(valueB);
            } else {
                valueA = String(valueA).toLowerCase();
                valueB = String(valueB).toLowerCase();
            }
            
            if (valueA < valueB) return direction === 'asc' ? -1 : 1;
            if (valueA > valueB) return direction === 'asc' ? 1 : -1;
            return 0;
        });
    }

    /**
     * Debounce function to limit how often a function is called
     * 
     * @param {Function} func - Function to debounce
     * @param {number} wait - Milliseconds to wait between calls
     * @returns {Function} - Debounced function
     */
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }

    // Return public API
    return {
        bindEvents,
        navigateToIndex,
        navigateToNextStep,
        copyFilmNumberData,
        exportFilmNumberData,
        filterTable,
        sortTable
    };
})();

// Make FilmNumberEvents available globally
window.FilmNumberEvents = FilmNumberEvents; 