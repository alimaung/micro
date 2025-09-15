/**
 * roll-list.js - Roll listing functionality
 * Handles displaying, filtering, and paginating rolls
 */

class RollList {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentPage = 1;
        this.pageSize = 25;
        this.filters = {};
        this.sortField = 'id';
        this.sortOrder = 'desc';
        this.selectedRolls = new Set();
    }

    /**
     * Initialize the roll list module
     */
    initialize() {
        console.log('Initializing RollList...');
        
        // Don't set up event listeners here since templates aren't loaded yet
        // Event listeners will be set up when the roll entity is selected
        
        // Initialize state
        this.selectedRolls = new Set();
        this.currentPage = 1;
        this.pageSize = 25;
        this.sortField = 'id';
        this.sortOrder = 'desc';
    }

    /**
     * Set up event listeners after templates are loaded
     */
    setupEventListeners() {
        console.log('Setting up RollList event listeners...');
        
        // Check if elements exist before adding listeners
        const applyFiltersBtn = document.getElementById('apply-filters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                this.currentPage = 1;  // Reset to first page when applying filters
                this.buildFilters();
                this.loadRolls();
            });
        }

        const resetFiltersBtn = document.getElementById('reset-filters');
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', () => {
                this.resetFilters();
            });
        }

        // Pagination events
        const prevPageBtn = document.getElementById('rolls-prev-page');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.loadRolls();
                }
            });
        }

        const nextPageBtn = document.getElementById('rolls-next-page');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                this.currentPage++;
                this.loadRolls();
            });
        }

        // Page size change event
        const pageSizeSelect = document.getElementById('page-size');
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', (e) => {
                this.pageSize = parseInt(e.target.value);
                this.currentPage = 1;  // Reset to first page when changing page size
                this.loadRolls();
            });
        }

        // Sort controls (dropdown)
        const sortFieldSelect = document.getElementById('sort-field');
        if (sortFieldSelect) {
            sortFieldSelect.addEventListener('change', (e) => {
                this.sortField = e.target.value;
                this.updateSortIndicators();
                this.loadRolls();
            });
        }

        const sortOrderSelect = document.getElementById('sort-order');
        if (sortOrderSelect) {
            sortOrderSelect.addEventListener('change', (e) => {
                this.sortOrder = e.target.value;
                this.updateSortIndicators();
                this.loadRolls();
            });
        }

        // Sortable table headers
        this.setupSortableHeaders();

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-rolls');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.roll-checkbox');
                const isChecked = e.target.checked;
                
                checkboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    
                    if (isChecked) {
                        this.selectedRolls.add(checkbox.dataset.id);
                    } else {
                        this.selectedRolls.delete(checkbox.dataset.id);
                    }
                });
                
                this.updateBatchCount();
            });
        }

        // Batch operation buttons
        const batchUpdateBtn = document.getElementById('batch-update-status');
        if (batchUpdateBtn) {
            batchUpdateBtn.addEventListener('click', () => {
                this.batchUpdateStatus();
            });
        }

        const batchDeleteBtn = document.getElementById('batch-delete');
        if (batchDeleteBtn) {
            batchDeleteBtn.addEventListener('click', () => {
                this.batchDeleteRolls();
            });
        }

        // Export buttons
        const exportCsvBtn = document.getElementById('export-csv');
        if (exportCsvBtn) {
            exportCsvBtn.addEventListener('click', () => {
                this.exportRolls('csv');
            });
        }

        const exportExcelBtn = document.getElementById('export-excel');
        if (exportExcelBtn) {
            exportExcelBtn.addEventListener('click', () => {
                this.exportRolls('excel');
            });
        }

        const exportPdfBtn = document.getElementById('export-pdf');
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', () => {
                this.exportRolls('pdf');
            });
        }

        const exportJsonBtn = document.getElementById('export-json');
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', () => {
                this.exportRolls('json');
            });
        }

        // Search button event
        const searchBtn = document.getElementById('search-button');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.currentPage = 1;
                this.buildFilters();
                this.loadRolls();
            });
        }

        // Search input Enter key event
        const searchInput = document.getElementById('search-term');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.currentPage = 1;
                    this.buildFilters();
                    this.loadRolls();
                }
            });
        }
    }

    /**
     * Set up sortable table headers
     */
    setupSortableHeaders() {
        const sortableHeaders = document.querySelectorAll('.results-table th.sortable');
        
        if (sortableHeaders.length === 0) {
            console.log('No sortable headers found yet');
            return;
        }
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                const sortField = header.getAttribute('data-sort');
                
                // If clicking the same field, toggle order
                if (this.sortField === sortField) {
                    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    // New field, default to ascending
                    this.sortField = sortField;
                    this.sortOrder = 'asc';
                }
                
                // Update the dropdown controls to match
                const sortFieldSelect = document.getElementById('sort-field');
                const sortOrderSelect = document.getElementById('sort-order');
                
                if (sortFieldSelect) sortFieldSelect.value = this.sortField;
                if (sortOrderSelect) sortOrderSelect.value = this.sortOrder;
                
                // Update visual indicators
                this.updateSortIndicators();
                
                // Reset to first page and reload
                this.currentPage = 1;
                this.loadRolls();
            });
        });
    }

    /**
     * Update sort indicators on table headers
     */
    updateSortIndicators() {
        // Remove all sort classes
        const sortableHeaders = document.querySelectorAll('.results-table th.sortable');
        
        if (sortableHeaders.length === 0) {
            console.log('No sortable headers found for sort indicators');
            return;
        }
        
        sortableHeaders.forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Add sort class to current field
        const currentHeader = document.querySelector(`.results-table th.sortable[data-sort="${this.sortField}"]`);
        if (currentHeader) {
            currentHeader.classList.add(`sort-${this.sortOrder}`);
        }
    }

    /**
     * Build filter object from form inputs
     */
    buildFilters() {
        const filters = {};
        
        // Get search term
        const searchTerm = document.getElementById('search-term').value.trim();
        if (searchTerm) {
            filters.search = searchTerm;
        }
        
        // Get date range
        const dateFrom = document.getElementById('date-from').value;
        if (dateFrom) {
            filters.date_from = dateFrom;
        }
        
        const dateTo = document.getElementById('date-to').value;
        if (dateTo) {
            filters.date_to = dateTo;
        }
        
        // Get roll-specific filters
        const filmType = document.getElementById('film-type').value;
        if (filmType) {
            filters.film_type = filmType;
        }
        
        const status = document.getElementById('roll-status').value;
        if (status) {
            filters.status = status;
        }
        
        const projectId = document.getElementById('project-filter').value;
        if (projectId) {
            filters.project_id = projectId;
        }
        
        const filmNumber = document.getElementById('film-number').value.trim();
        if (filmNumber) {
            filters.film_number = filmNumber;
        }
        
        const hasSplitDocuments = document.getElementById('has-split-documents').value;
        if (hasSplitDocuments !== '') {
            filters.has_split_documents = hasSplitDocuments === 'true';
        }
        
        const isPartial = document.getElementById('is-partial').value;
        if (isPartial !== '') {
            filters.is_partial = isPartial === 'true';
        }
        
        // Set sort parameters
        filters.sort_field = this.sortField;
        filters.sort_order = this.sortOrder;
        
        this.filters = filters;
    }

    /**
     * Reset all filters to default values
     */
    resetFilters() {
        // Reset all filter inputs
        document.querySelectorAll('select, input[type="text"], input[type="date"]').forEach(input => {
            input.value = '';
        });
        
        // Clear filters and reload
        this.filters = {};
        this.currentPage = 1;
        this.loadRolls();
    }

    /**
     * Load rolls with current filters and pagination
     */
    async loadRolls() {
        const tableBody = document.getElementById('rolls-results-body');
        const resultCount = document.getElementById('result-count');
        
        // Show loading state
        tableBody.innerHTML = `<tr><td colspan="20" class="loading-row">Loading rolls...</td></tr>`;
        
        try {
            // Always build filters first to ensure current sort parameters are included
            this.buildFilters();
            
            // Add pagination parameters to filters
            const params = {
                ...this.filters,
                page: this.currentPage,
                page_size: this.pageSize
            };
            
            // Fetch rolls from API
            const response = await this.dbService.listRolls(params);
            const rolls = response.results;
            const totalRolls = response.total;
            const totalPages = response.total_pages;
            
            // Update count display
            resultCount.textContent = `(${totalRolls})`;
            
            // Update pagination UI
            this.updatePagination(totalPages);
            
            // Enable/disable pagination buttons
            document.getElementById('rolls-prev-page').disabled = this.currentPage === 1;
            document.getElementById('rolls-next-page').disabled = this.currentPage === totalPages || totalPages === 0;
            
            // Render rolls based on active view
            const activeView = document.querySelector('.view-control.active')?.getAttribute('data-view') || 'table';
            
            if (activeView === 'cards') {
                this.renderRollsAsCards(rolls);
            } else if (activeView === 'visualization') {
                this.renderRollsAsVisualization(rolls);
            } else {
                this.renderRolls(rolls);
            }
            
            // Restore selection state
            this.restoreSelectionState();
            
            // Update sort indicators
            this.updateSortIndicators();
            
        } catch (error) {
            console.error("Error loading rolls:", error);
            tableBody.innerHTML = `
                <tr class="error-row">
                    <td colspan="20">
                        <div class="error-message">
                            Error loading rolls: ${error.message || 'Unknown error'}
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Render rolls in the table
     * @param {Array} rolls - List of roll objects to render
     */
    renderRolls(rolls) {
        const tableBody = document.getElementById('rolls-results-body');
        
        // Clear table
        tableBody.innerHTML = '';
        
        // If no rolls, show empty message
        if (!rolls || rolls.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="20">No rolls found. Try adjusting your filters.</td>
                </tr>
            `;
            return;
        }
        
        // Add rows for each roll
        rolls.forEach(roll => {
            // Get status badge class and text
            let statusClass = 'active';
            let statusText = roll.status || 'Active';
            
            if (roll.is_full) {
                statusClass = 'full';
                statusText = 'Full';
            } else if (roll.is_partial) {
                statusClass = 'partial';
                statusText = 'Partial';
            }
            
            // Create table row
            const row = document.createElement('tr');
            row.className = `roll-row status-${statusClass}`;
            row.dataset.id = roll.id;
            
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="batch-checkbox roll-checkbox" data-id="${roll.id}">
                </td>
                <td>${roll.id}</td>
                <td>${roll.roll_id || 'N/A'}</td>
                <td>${roll.project_archive_id || 'N/A'}</td>
                <td>${roll.film_number || 'N/A'}</td>
                <td><span class="film-type-badge ${roll.film_type}">${roll.film_type}</span></td>
                <td class="numeric-cell">${roll.capacity || 0}</td>
                <td class="numeric-cell">${roll.pages_used || 0}</td>
                <td class="numeric-cell">${roll.pages_remaining || 0}</td>
                <td class="numeric-cell">
                    <div class="utilization-bar">
                        <div class="utilization-fill" style="width: ${roll.utilization || 0}%"></div>
                        <span class="utilization-text">${roll.utilization || 0}%</span>
                    </div>
                </td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td><span class="boolean-badge ${roll.has_split_documents ? 'true' : 'false'}">${roll.has_split_documents ? 'Yes' : 'No'}</span></td>
                <td><span class="boolean-badge ${roll.is_partial ? 'true' : 'false'}">${roll.is_partial ? 'Yes' : 'No'}</span></td>
                <td class="numeric-cell">${roll.remaining_capacity || 0}</td>
                <td class="numeric-cell">${roll.usable_capacity || 0}</td>
                <td>${roll.film_number_source || 'N/A'}</td>
                <td class="date-cell">${roll.creation_date || 'N/A'}</td>
                <td class="actions-cell">
                    <button class="action-icon view-details" data-id="${roll.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-icon edit-item" data-id="${roll.id}" title="Edit Roll">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-icon delete-item" data-id="${roll.id}" title="Delete Roll">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Add event listeners to checkboxes and buttons
        this.setupRowEventListeners();
    }
    
    /**
     * Set up event listeners for table row elements
     */
    setupRowEventListeners() {
        // Checkbox selection
        document.querySelectorAll('.roll-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const rollId = e.target.dataset.id;
                
                if (e.target.checked) {
                    this.selectedRolls.add(rollId);
                } else {
                    this.selectedRolls.delete(rollId);
                }
                
                this.updateBatchCount();
            });
        });
        
        // View details buttons
        document.querySelectorAll('.view-details').forEach(button => {
            button.addEventListener('click', (e) => {
                const rollId = e.target.closest('.action-icon').dataset.id;
                const rollDetailsEvent = new CustomEvent('showRollDetails', {
                    detail: { rollId }
                });
                document.dispatchEvent(rollDetailsEvent);
            });
        });
        
        // Edit buttons
        document.querySelectorAll('.edit-item').forEach(button => {
            button.addEventListener('click', (e) => {
                const rollId = e.target.closest('.action-icon').dataset.id;
                const editRollEvent = new CustomEvent('editRoll', {
                    detail: { rollId }
                });
                document.dispatchEvent(editRollEvent);
            });
        });
        
        // Delete buttons
        document.querySelectorAll('.delete-item').forEach(button => {
            button.addEventListener('click', (e) => {
                const rollId = e.target.closest('.action-icon').dataset.id;
                this.deleteRoll(rollId);
            });
        });
    }
    
    /**
     * Update pagination controls
     * @param {number} totalPages - Total number of pages
     */
    updatePagination(totalPages) {
        const pageNumbers = document.getElementById('rolls-page-numbers');
        pageNumbers.innerHTML = '';
        
        // Show at most 5 page numbers
        const maxPages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxPages / 2));
        let endPage = Math.min(totalPages, startPage + maxPages - 1);
        
        if (endPage - startPage + 1 < maxPages) {
            startPage = Math.max(1, endPage - maxPages + 1);
        }
        
        // Add first page if not included
        if (startPage > 1) {
            const pageSpan = document.createElement('span');
            pageSpan.className = 'page-number';
            pageSpan.textContent = '1';
            pageSpan.addEventListener('click', () => {
                this.currentPage = 1;
                this.loadRolls();
            });
            pageNumbers.appendChild(pageSpan);
            
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                pageNumbers.appendChild(ellipsis);
            }
        }
        
        // Add page numbers
        for (let i = startPage; i <= endPage; i++) {
            const pageSpan = document.createElement('span');
            pageSpan.className = 'page-number' + (i === this.currentPage ? ' active' : '');
            pageSpan.textContent = i;
            pageSpan.addEventListener('click', () => {
                if (i !== this.currentPage) {
                    this.currentPage = i;
                    this.loadRolls();
                }
            });
            pageNumbers.appendChild(pageSpan);
        }
        
        // Add last page if not included
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                pageNumbers.appendChild(ellipsis);
            }
            
            const pageSpan = document.createElement('span');
            pageSpan.className = 'page-number';
            pageSpan.textContent = totalPages;
            pageSpan.addEventListener('click', () => {
                this.currentPage = totalPages;
                this.loadRolls();
            });
            pageNumbers.appendChild(pageSpan);
        }
    }
    
    /**
     * Update batch operations counter and button states
     */
    updateBatchCount() {
        const count = this.selectedRolls.size;
        const batchCounter = document.getElementById('batch-counter');
        const batchButtons = document.querySelectorAll('.batch-action');
        
        if (count > 0) {
            if (batchCounter) {
                batchCounter.textContent = count;
                batchCounter.style.display = 'inline-block';
            }
            batchButtons.forEach(button => button.disabled = false);
        } else {
            if (batchCounter) {
                batchCounter.style.display = 'none';
            }
            batchButtons.forEach(button => button.disabled = true);
        }
    }
    
    /**
     * Restore selection state after table refresh
     */
    restoreSelectionState() {
        if (this.selectedRolls.size === 0) return;
        
        const checkboxes = document.querySelectorAll('.roll-checkbox');
        checkboxes.forEach(checkbox => {
            const rollId = checkbox.dataset.id;
            if (this.selectedRolls.has(rollId)) {
                checkbox.checked = true;
            }
        });
        
        this.updateBatchCount();
    }
    
    /**
     * Delete a single roll
     * @param {string|number} rollId - ID of the roll to delete
     */
    async deleteRoll(rollId) {
        try {
            const confirmed = confirm(`Are you sure you want to delete Roll #${rollId}? This action cannot be undone.`);
            if (confirmed) {
                await this.dbService.deleteRoll(rollId);
                alert("Roll deleted successfully!");
                
                // Remove from selected rolls if present
                this.selectedRolls.delete(rollId.toString());
                
                // Reload rolls
                this.loadRolls();
            }
        } catch (error) {
            console.error("Error deleting roll:", error);
            alert(`Error deleting roll: ${error.message || 'Unknown error'}`);
        }
    }
    
    /**
     * Batch update status for selected rolls
     */
    async batchUpdateStatus() {
        if (this.selectedRolls.size === 0) return;
        
        const newStatus = prompt("Enter new status (active/full/partial):");
        if (newStatus !== null) {
            try {
                const rollIds = Array.from(this.selectedRolls);
                
                // Update all selected rolls
                for (const rollId of rollIds) {
                    await this.dbService.updateRoll(rollId, { status: newStatus });
                }
                
                alert(`Updated status for ${rollIds.length} rolls`);
                this.loadRolls();
            } catch (error) {
                console.error("Error updating rolls:", error);
                alert(`Error updating rolls: ${error.message || 'Unknown error'}`);
            }
        }
    }
    
    /**
     * Batch delete selected rolls
     */
    async batchDeleteRolls() {
        if (this.selectedRolls.size === 0) return;
        
        const rollIds = Array.from(this.selectedRolls);
        const confirmed = confirm(`Are you sure you want to delete ${rollIds.length} rolls? This action cannot be undone.`);
        
        if (confirmed) {
            try {
                // Delete all selected rolls
                for (const rollId of rollIds) {
                    await this.dbService.deleteRoll(rollId);
                }
                
                alert(`Deleted ${rollIds.length} rolls successfully`);
                
                // Clear selected rolls
                this.selectedRolls.clear();
                
                // Reload rolls
                this.loadRolls();
            } catch (error) {
                console.error("Error deleting rolls:", error);
                alert(`Error deleting rolls: ${error.message || 'Unknown error'}`);
            }
        }
    }
    
    /**
     * Export rolls in the specified format
     * @param {string} format - Export format (csv, excel, pdf, json)
     */
    async exportRolls(format) {
        try {
            // Get current filtered count from the result count display
            const resultCountElement = document.getElementById('result-count');
            const resultCountText = resultCountElement ? resultCountElement.textContent : '(0)';
            const filteredCount = parseInt(resultCountText.replace(/[()]/g, '')) || 0;
            
            // Get the roll export module
            const rollExport = window.exploreMain?.rollExport;
            
            if (rollExport) {
                // Open export modal with the selected format, selected rolls, and filtered count
                rollExport.openExportModal(format, this.selectedRolls, filteredCount);
            } else {
                console.error('RollExport module not available');
                alert('Export functionality is not available. Please refresh the page and try again.');
            }
        } catch (error) {
            console.error(`Error opening export modal for ${format}:`, error);
            alert(`Error opening export modal: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Load film types and populate the dropdown
     */
    async loadFilmTypes() {
        try {
            const filmTypeSelect = document.getElementById('film-type');
            if (!filmTypeSelect) return;
            
            // Film types are predefined
            const filmTypes = ['16mm', '35mm'];
            
            // Keep the first option (All Types) and remove the rest
            while (filmTypeSelect.options.length > 1) {
                filmTypeSelect.remove(1);
            }
            
            // Add options
            filmTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                filmTypeSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error loading film types:", error);
        }
    }
    
    /**
     * Load statuses and populate the dropdown
     */
    async loadStatuses() {
        try {
            const statusSelect = document.getElementById('roll-status');
            if (!statusSelect) return;
            
            // Statuses are predefined
            const statuses = ['active', 'full', 'partial', 'used', 'archived'];
            
            // Keep the first option (All Statuses) and remove the rest
            while (statusSelect.options.length > 1) {
                statusSelect.remove(1);
            }
            
            // Add options
            statuses.forEach(status => {
                const option = document.createElement('option');
                option.value = status;
                option.textContent = status.charAt(0).toUpperCase() + status.slice(1);
                statusSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error loading statuses:", error);
        }
    }

    /**
     * Render rolls as cards
     * @param {Array} rolls - List of roll objects to render
     */
    renderRollsAsCards(rolls) {
        const cardsContainer = document.getElementById('rolls-results-cards');
        
        // Clear container
        cardsContainer.innerHTML = '';
        
        // If no rolls, show empty message
        if (!rolls || rolls.length === 0) {
            cardsContainer.innerHTML = `
                <div class="empty-message">
                    <i class="fas fa-film"></i>
                    <p>No rolls found. Try adjusting your filters.</p>
                </div>
            `;
            return;
        }
        
        // Add cards for each roll
        rolls.forEach(roll => {
            // Get status badge class and text
            let statusClass = 'active';
            let statusText = roll.status || 'Active';
            
            if (roll.is_full) {
                statusClass = 'full';
                statusText = 'Full';
            } else if (roll.is_partial) {
                statusClass = 'partial';
                statusText = 'Partial';
            }
            
            // Create card element
            const card = document.createElement('div');
            card.className = `roll-card status-${statusClass}`;
            card.dataset.id = roll.id;
            
            card.innerHTML = `
                <div class="card-header">
                    <div class="card-checkbox">
                        <input type="checkbox" class="batch-checkbox roll-checkbox" data-id="${roll.id}">
                    </div>
                    <div class="card-id">#${roll.id}</div>
                    <div class="card-status">
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                </div>
                
                <div class="card-body">
                    <h3 class="card-title">${roll.film_number || 'No Film Number'}</h3>
                    <div class="card-details">
                        <div class="detail-item">
                            <i class="fas fa-project-diagram"></i>
                            <span>${roll.project_archive_id || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-film"></i>
                            <span class="film-type-badge ${roll.film_type}">${roll.film_type}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-chart-pie"></i>
                            <span>${roll.utilization || 0}% utilized</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-file-alt"></i>
                            <span>${roll.pages_used || 0}/${roll.capacity || 0} pages</span>
                        </div>
                    </div>
                    
                    <div class="card-utilization">
                        <div class="utilization-bar">
                            <div class="utilization-fill" style="width: ${roll.utilization || 0}%"></div>
                        </div>
                        <span class="utilization-text">${roll.utilization || 0}% Full</span>
                    </div>
                    
                    <div class="card-date">
                        <i class="fas fa-calendar"></i>
                        <span>${roll.creation_date || 'N/A'}</span>
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="action-icon view-details" data-id="${roll.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-icon edit-item" data-id="${roll.id}" title="Edit Roll">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-icon delete-item" data-id="${roll.id}" title="Delete Roll">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            cardsContainer.appendChild(card);
        });
        
        // Add event listeners to checkboxes and buttons
        this.setupRowEventListeners();
    }

    /**
     * Render rolls as visualization
     * @param {Array} rolls - List of roll objects to render
     */
    renderRollsAsVisualization(rolls) {
        const chartCanvas = document.getElementById('rolls-results-chart');
        const vizContainer = chartCanvas ? chartCanvas.parentElement : null;
        
        if (!vizContainer) {
            console.warn('Roll visualization container not found');
            return;
        }
        
        // Clear container
        vizContainer.innerHTML = '';
        
        // If no rolls, show empty message
        if (!rolls || rolls.length === 0) {
            vizContainer.innerHTML = `
                <div class="empty-message">
                    <i class="fas fa-chart-bar"></i>
                    <p>No rolls found. Try adjusting your filters.</p>
                </div>
            `;
            return;
        }
        
        // Create visualization content
        vizContainer.innerHTML = `
            <div class="viz-header">
                <h3>Roll Statistics</h3>
                <div class="viz-controls">
                    <select id="viz-type">
                        <option value="utilization">By Utilization</option>
                        <option value="film-type">By Film Type</option>
                        <option value="status">By Status</option>
                        <option value="capacity">By Capacity</option>
                    </select>
                </div>
            </div>
            
            <div class="viz-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${rolls.length}</div>
                        <div class="stat-label">Total Rolls</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${rolls.filter(r => r.film_type === '16mm').length}</div>
                        <div class="stat-label">16mm Rolls</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${rolls.filter(r => r.film_type === '35mm').length}</div>
                        <div class="stat-label">35mm Rolls</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${Math.round(rolls.reduce((sum, r) => sum + (r.utilization || 0), 0) / rolls.length)}%</div>
                        <div class="stat-label">Avg Utilization</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="rolls-chart" width="400" height="200"></canvas>
                </div>
                
                <div class="roll-list-viz">
                    ${rolls.map(roll => `
                        <div class="roll-viz-item" data-id="${roll.id}">
                            <div class="roll-viz-info">
                                <span class="roll-viz-id">#${roll.id}</span>
                                <span class="roll-viz-name">${roll.film_number || 'No Film Number'}</span>
                                <span class="roll-viz-utilization">${roll.utilization || 0}% full</span>
                            </div>
                            <div class="roll-viz-bar">
                                <div class="bar-fill" style="width: ${roll.utilization || 0}%"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

// Export the class for use in the main module
window.RollList = RollList; 