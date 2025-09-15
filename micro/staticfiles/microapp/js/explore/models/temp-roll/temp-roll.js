/**
 * temp-roll.js - Temp roll management functionality
 * Handles listing, filtering, and managing temp rolls
 */

class TempRollManager {
    constructor() {
        this.dbService = new DatabaseService();
        this.tempRollDetails = new TempRollDetails();
        this.currentPage = 1;
        this.pageSize = 25;
        this.currentFilters = {};
        this.currentSort = { field: 'temp_roll_id', direction: 'desc' };
        this.currentView = 'table';
        this.tempRolls = [];
        this.totalCount = 0;
        this.selectedTempRolls = new Set();
    }

    /**
     * Initialize the temp roll manager
     */
    initialize() {
        this.setupEventListeners();
        this.tempRollDetails.initialize();
        // Remove automatic data loading - data will be loaded when entity is selected
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // View toggle
        document.querySelectorAll('#temp-roll-container .view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.closest('.view-btn').getAttribute('data-view'));
            });
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-temp-rolls');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadTempRolls();
            });
        }

        // Create temp roll button
        const createBtn = document.getElementById('create-temp-roll');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.showCreateModal();
            });
        }

        // Create first temp roll button
        const createFirstBtn = document.getElementById('create-first-temp-roll');
        if (createFirstBtn) {
            createFirstBtn.addEventListener('click', () => {
                this.showCreateModal();
            });
        }

        // Filter controls
        const applyFiltersBtn = document.getElementById('apply-temp-roll-filters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                this.applyFilters();
            });
        }

        const clearFiltersBtn = document.getElementById('clear-temp-roll-filters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Search input
        const searchInput = document.getElementById('temp-roll-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 500);
            });
        }

        // Pagination
        const prevPageBtn = document.getElementById('temp-rolls-prev-page');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.loadTempRolls();
                }
            });
        }

        const nextPageBtn = document.getElementById('temp-rolls-next-page');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(this.totalCount / this.pageSize);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.loadTempRolls();
                }
            });
        }

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-temp-rolls');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Export dropdown
        document.querySelectorAll('#temp-roll-container .dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const format = e.target.getAttribute('data-format');
                this.exportTempRolls(format);
            });
        });

        // Save temp roll form
        const saveBtn = document.getElementById('save-temp-roll');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveTempRoll();
            });
        }

        // Listen for edit temp roll events
        document.addEventListener('editTempRoll', (event) => {
            const { tempRollId } = event.detail;
            this.showEditModal(tempRollId);
        });

        // Pagination for cards view
        const prevPageBtnCards = document.getElementById('temp-rolls-prev-page-cards');
        if (prevPageBtnCards) {
            prevPageBtnCards.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.loadTempRolls();
                }
            });
        }

        const nextPageBtnCards = document.getElementById('temp-rolls-next-page-cards');
        if (nextPageBtnCards) {
            nextPageBtnCards.addEventListener('click', () => {
                const totalPages = Math.ceil(this.totalCount / this.pageSize);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.loadTempRolls();
                }
            });
        }
    }

    /**
     * Switch between table and card views
     * @param {string} view - View type ('table' or 'cards')
     */
    switchView(view) {
        this.currentView = view;
        
        // Update view buttons in the main view controls
        document.querySelectorAll('.view-control').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`.view-control[data-view="${view}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        // Show/hide view containers
        const tableView = document.getElementById('temp-rolls-table-view');
        const cardsView = document.getElementById('temp-rolls-cards-view');
        
        if (tableView) tableView.style.display = view === 'table' ? 'block' : 'none';
        if (cardsView) cardsView.style.display = view === 'cards' ? 'block' : 'none';
        
        // Re-render current data
        this.renderTempRolls();
    }

    /**
     * Load temp rolls from the database
     */
    async loadTempRolls() {
        this.showLoading(true);
        
        try {
            const response = await this.dbService.getTempRolls({
                ...this.currentFilters,
                page: this.currentPage,
                page_size: this.pageSize,
                sort_field: this.currentSort.field,
                sort_direction: this.currentSort.direction
            });
            
            // Handle different response structures
            if (response.temp_rolls) {
                this.tempRolls = response.temp_rolls;
                this.totalCount = response.total_count || response.temp_rolls.length;
            } else if (Array.isArray(response)) {
                this.tempRolls = response;
                this.totalCount = response.length;
            } else {
                this.tempRolls = [];
                this.totalCount = 0;
            }
            
            this.renderTempRolls();
            this.updatePagination();
            this.updateEntityCount();
            
        } catch (error) {
            console.error('Error loading temp rolls:', error);
            this.showError('Failed to load temp rolls');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Render temp rolls in the current view
     */
    renderTempRolls() {
        if (this.tempRolls.length === 0) {
            this.showEmpty(true);
            return;
        }
        
        this.showEmpty(false);
        
        if (this.currentView === 'table') {
            this.renderTableView();
        } else {
            this.renderCardsView();
        }
    }

    /**
     * Render temp rolls in table view
     */
    renderTableView() {
        const tbody = document.getElementById('temp-rolls-results-body');
        if (!tbody) return;
        
        tbody.innerHTML = this.tempRolls.map(tempRoll => {
            const tempRollId = tempRoll.temp_roll_id || tempRoll.id;
            const filmType = tempRoll.film_type || 'Unknown';
            const status = tempRoll.status || 'Unknown';
            const capacity = tempRoll.capacity || 0;
            const usableCapacity = tempRoll.usable_capacity || 0;
            const utilization = capacity > 0 ? (usableCapacity / capacity * 100).toFixed(1) : 100;
            const creationDate = tempRoll.creation_date ? new Date(tempRoll.creation_date).toLocaleDateString() : 'N/A';
            const sourceRoll = tempRoll.source_roll_id || tempRoll.source_roll?.roll_id || 'None';
            const usedByRoll = tempRoll.used_by_roll_id || tempRoll.used_by_roll?.roll_id || 'None';
            
            return `
                <tr class="temp-roll-row status-${status}" data-temp-roll-id="${tempRollId}">
                    <td>
                        <input type="checkbox" class="temp-roll-checkbox batch-checkbox" value="${tempRollId}">
                    </td>
                    <td class="temp-roll-id">${tempRollId}</td>
                    <td>
                        <span class="temp-roll-film-type-badge" data-type="${filmType}">${filmType}</span>
                    </td>
                    <td>${capacity} pages</td>
                    <td>
                        <div class="temp-roll-capacity-display">
                            <div class="temp-roll-capacity-bar">
                                <div class="temp-roll-capacity-fill" style="width: ${utilization}%"></div>
                            </div>
                            <span class="temp-roll-capacity-text">${usableCapacity} pages</span>
                        </div>
                    </td>
                    <td>
                        <span class="temp-roll-status-badge status-badge ${status}">${status}</span>
                    </td>
                    <td>${sourceRoll}</td>
                    <td>${usedByRoll}</td>
                    <td>${creationDate}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-icon view-temp-roll" data-temp-roll-id="${tempRollId}" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="action-icon edit-temp-roll" data-temp-roll-id="${tempRollId}" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-icon delete-temp-roll" data-temp-roll-id="${tempRollId}" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
        
        // Add event listeners to action buttons
        this.attachActionListeners();
    }

    /**
     * Render temp rolls in cards view
     */
    renderCardsView() {
        const container = document.getElementById('temp-rolls-results-cards');
        if (!container) return;
        
        container.innerHTML = this.tempRolls.map(tempRoll => {
            const tempRollId = tempRoll.temp_roll_id || tempRoll.id;
            const filmType = tempRoll.film_type || 'Unknown';
            const status = tempRoll.status || 'Unknown';
            const capacity = tempRoll.capacity || 0;
            const usableCapacity = tempRoll.usable_capacity || 0;
            const utilization = capacity > 0 ? (usableCapacity / capacity * 100).toFixed(1) : 100;
            const creationDate = tempRoll.creation_date ? new Date(tempRoll.creation_date).toLocaleDateString() : 'N/A';
            const sourceRoll = tempRoll.source_roll_id || tempRoll.source_roll?.roll_id || 'None';
            const usedByRoll = tempRoll.used_by_roll_id || tempRoll.used_by_roll?.roll_id || 'None';
            
            return `
                <div class="item-card temp-roll-card status-${status}" data-temp-roll-id="${tempRollId}">
                    <div class="card-header">
                        <h3>Temp Roll #${tempRollId}</h3>
                        <div class="card-id">
                            <span class="temp-roll-status-badge status-badge ${status}">${status}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="card-property">
                            <span class="property-label">Film Type:</span>
                            <span class="property-value">
                                <span class="temp-roll-film-type-badge" data-type="${filmType}">${filmType}</span>
                            </span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Total Capacity:</span>
                            <span class="property-value">${capacity} pages</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Usable Capacity:</span>
                            <span class="property-value">${usableCapacity} pages</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Efficiency:</span>
                            <span class="property-value">
                                <div class="temp-roll-capacity-display">
                                    <div class="temp-roll-capacity-bar">
                                        <div class="temp-roll-capacity-fill" style="width: ${utilization}%"></div>
                                    </div>
                                    <span class="temp-roll-capacity-text">${utilization}%</span>
                                </div>
                            </span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Source Roll:</span>
                            <span class="property-value">${sourceRoll}</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Used By Roll:</span>
                            <span class="property-value">${usedByRoll}</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Created:</span>
                            <span class="property-value">${creationDate}</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="card-button view-details view-temp-roll" data-temp-roll-id="${tempRollId}">
                            <i class="fas fa-eye"></i>
                            View
                        </button>
                        <button class="card-button edit-item edit-temp-roll" data-temp-roll-id="${tempRollId}">
                            <i class="fas fa-edit"></i>
                            Edit
                        </button>
                        <button class="card-button delete-temp-roll" data-temp-roll-id="${tempRollId}">
                            <i class="fas fa-trash"></i>
                            Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add event listeners to action buttons
        this.attachActionListeners();
    }

    /**
     * Attach event listeners to action buttons
     */
    attachActionListeners() {
        // View temp roll buttons
        document.querySelectorAll('.view-temp-roll').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tempRollId = e.target.closest('.view-temp-roll').getAttribute('data-temp-roll-id');
                const showEvent = new CustomEvent('showTempRollDetails', {
                    detail: { tempRollId }
                });
                document.dispatchEvent(showEvent);
            });
        });

        // Edit temp roll buttons
        document.querySelectorAll('.edit-temp-roll').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tempRollId = e.target.closest('.edit-temp-roll').getAttribute('data-temp-roll-id');
                this.showEditModal(tempRollId);
            });
        });

        // Delete temp roll buttons
        document.querySelectorAll('.delete-temp-roll').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tempRollId = e.target.closest('.delete-temp-roll').getAttribute('data-temp-roll-id');
                this.deleteTempRoll(tempRollId);
            });
        });

        // Checkbox listeners
        document.querySelectorAll('.temp-roll-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const tempRollId = e.target.value;
                if (e.target.checked) {
                    this.selectedTempRolls.add(tempRollId);
                } else {
                    this.selectedTempRolls.delete(tempRollId);
                }
                this.updateSelectAllCheckbox();
            });
        });
    }

    /**
     * Apply current filters
     */
    applyFilters() {
        const filmTypeFilter = document.getElementById('temp-roll-film-type-filter');
        const statusFilter = document.getElementById('temp-roll-status-filter');
        const capacityFilter = document.getElementById('temp-roll-capacity-filter');
        const searchInput = document.getElementById('temp-roll-search');
        
        this.currentFilters = {
            film_type: filmTypeFilter ? filmTypeFilter.value : '',
            status: statusFilter ? statusFilter.value : '',
            min_capacity: capacityFilter ? capacityFilter.value : '',
            search: searchInput ? searchInput.value : ''
        };
        
        // Remove empty filters
        Object.keys(this.currentFilters).forEach(key => {
            if (!this.currentFilters[key]) {
                delete this.currentFilters[key];
            }
        });
        
        this.currentPage = 1;
        this.loadTempRolls();
    }

    /**
     * Clear all filters
     */
    clearFilters() {
        const filmTypeFilter = document.getElementById('temp-roll-film-type-filter');
        const statusFilter = document.getElementById('temp-roll-status-filter');
        const capacityFilter = document.getElementById('temp-roll-capacity-filter');
        const searchInput = document.getElementById('temp-roll-search');
        
        if (filmTypeFilter) filmTypeFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        if (capacityFilter) capacityFilter.value = '';
        if (searchInput) searchInput.value = '';
        
        this.currentFilters = {};
        this.currentPage = 1;
        this.loadTempRolls();
    }

    /**
     * Show create temp roll modal
     */
    showCreateModal() {
        document.getElementById('temp-roll-edit-modal-title').textContent = 'Create Temp Roll';
        document.getElementById('temp-roll-form').reset();
        
        // Load available rolls for dropdowns
        this.loadRollOptions();
        
        document.getElementById('temp-roll-edit-modal').style.display = 'flex';
    }

    /**
     * Show edit temp roll modal
     * @param {number|string} tempRollId - Temp Roll ID
     */
    async showEditModal(tempRollId) {
        try {
            const response = await this.dbService.getTempRoll(tempRollId);
            let tempRoll;
            if (response.temp_roll) {
                tempRoll = response.temp_roll;
            } else if (response.temp_roll_id || response.id) {
                tempRoll = response;
            } else {
                throw new Error('Invalid temp roll data structure');
            }
            
            document.getElementById('temp-roll-edit-modal-title').textContent = 'Edit Temp Roll';
            
            // Populate form fields
            document.getElementById('temp-roll-film-type').value = tempRoll.film_type || '';
            document.getElementById('temp-roll-capacity').value = tempRoll.capacity || '';
            document.getElementById('temp-roll-usable-capacity').value = tempRoll.usable_capacity || '';
            document.getElementById('temp-roll-status').value = tempRoll.status || 'available';
            document.getElementById('temp-roll-source-roll').value = tempRoll.source_roll_id || '';
            document.getElementById('temp-roll-used-by-roll').value = tempRoll.used_by_roll_id || '';
            
            // Store temp roll ID for saving
            document.getElementById('temp-roll-form').setAttribute('data-temp-roll-id', tempRollId);
            
            // Load available rolls for dropdowns
            this.loadRollOptions();
            
            document.getElementById('temp-roll-edit-modal').style.display = 'flex';
            
        } catch (error) {
            console.error('Error loading temp roll for editing:', error);
            alert('Error loading temp roll data');
        }
    }

    /**
     * Load roll options for dropdowns
     */
    async loadRollOptions() {
        try {
            const response = await this.dbService.listRolls();
            let rolls = [];
            
            if (response.rolls) {
                rolls = response.rolls;
            } else if (Array.isArray(response)) {
                rolls = response;
            }
            
            const sourceSelect = document.getElementById('temp-roll-source-roll');
            const usedBySelect = document.getElementById('temp-roll-used-by-roll');
            
            // Clear existing options (except first)
            sourceSelect.innerHTML = '<option value="">No Source Roll</option>';
            usedBySelect.innerHTML = '<option value="">Not Used Yet</option>';
            
            rolls.forEach(roll => {
                const rollId = roll.id || roll.roll_id;
                const rollNumber = roll.roll_id || roll.id;
                const filmNumber = roll.film_number || 'No Film Number';
                const optionText = `Roll ${rollNumber} - ${filmNumber}`;
                
                sourceSelect.innerHTML += `<option value="${rollId}">${optionText}</option>`;
                usedBySelect.innerHTML += `<option value="${rollId}">${optionText}</option>`;
            });
            
        } catch (error) {
            console.error('Error loading roll options:', error);
        }
    }

    /**
     * Save temp roll (create or update)
     */
    async saveTempRoll() {
        const form = document.getElementById('temp-roll-form');
        const tempRollId = form.getAttribute('data-temp-roll-id');
        
        const tempRollData = {
            film_type: document.getElementById('temp-roll-film-type').value,
            capacity: parseInt(document.getElementById('temp-roll-capacity').value),
            usable_capacity: parseInt(document.getElementById('temp-roll-usable-capacity').value),
            status: document.getElementById('temp-roll-status').value,
            source_roll_id: document.getElementById('temp-roll-source-roll').value || null,
            used_by_roll_id: document.getElementById('temp-roll-used-by-roll').value || null
        };
        
        // Validate required fields
        if (!tempRollData.film_type || !tempRollData.capacity || !tempRollData.usable_capacity) {
            alert('Please fill in all required fields');
            return;
        }
        
        try {
            if (tempRollId) {
                // Update existing temp roll
                await this.dbService.updateTempRoll(tempRollId, tempRollData);
            } else {
                // Create new temp roll
                await this.dbService.createTempRoll(tempRollData);
            }
            
            // Close modal and refresh list
            document.getElementById('temp-roll-edit-modal').style.display = 'none';
            this.loadTempRolls();
            
        } catch (error) {
            console.error('Error saving temp roll:', error);
            alert('Error saving temp roll');
        }
    }

    /**
     * Delete a temp roll
     * @param {number|string} tempRollId - Temp Roll ID
     */
    async deleteTempRoll(tempRollId) {
        if (!confirm('Are you sure you want to delete this temp roll?')) {
            return;
        }
        
        try {
            await this.dbService.deleteTempRoll(tempRollId);
            this.loadTempRolls();
        } catch (error) {
            console.error('Error deleting temp roll:', error);
            alert('Error deleting temp roll');
        }
    }

    /**
     * Export temp rolls
     * @param {string} format - Export format
     */
    async exportTempRolls(format) {
        try {
            const selectedIds = Array.from(this.selectedTempRolls);
            const blob = await this.dbService.exportTempRolls(selectedIds.length > 0 ? selectedIds : null, format);
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `temp-rolls.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
        } catch (error) {
            console.error('Error exporting temp rolls:', error);
            alert('Error exporting temp rolls');
        }
    }

    /**
     * Toggle select all temp rolls
     * @param {boolean} checked - Whether to select all
     */
    toggleSelectAll(checked) {
        this.selectedTempRolls.clear();
        
        document.querySelectorAll('.temp-roll-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedTempRolls.add(checkbox.value);
            }
        });
    }

    /**
     * Update select all checkbox state
     */
    updateSelectAllCheckbox() {
        const checkboxes = document.querySelectorAll('.temp-roll-checkbox');
        const selectAllCheckbox = document.getElementById('select-all-temp-rolls');
        
        if (!selectAllCheckbox) return;
        
        if (checkboxes.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (this.selectedTempRolls.size === checkboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (this.selectedTempRolls.size > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    /**
     * Update pagination controls
     */
    updatePagination() {
        const totalPages = Math.ceil(this.totalCount / this.pageSize);
        const startItem = (this.currentPage - 1) * this.pageSize + 1;
        const endItem = Math.min(this.currentPage * this.pageSize, this.totalCount);
        
        // Update pagination for table view
        const prevBtn = document.getElementById('temp-rolls-prev-page');
        const nextBtn = document.getElementById('temp-rolls-next-page');
        const pagesContainer = document.getElementById('temp-rolls-page-numbers');
        
        if (prevBtn) prevBtn.disabled = this.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.currentPage >= totalPages;
        
        if (pagesContainer) {
            pagesContainer.innerHTML = '';
            
            for (let i = Math.max(1, this.currentPage - 2); i <= Math.min(totalPages, this.currentPage + 2); i++) {
                const pageBtn = document.createElement('span');
                pageBtn.className = `page-number ${i === this.currentPage ? 'active' : ''}`;
                pageBtn.textContent = i;
                pageBtn.style.cursor = 'pointer';
                pageBtn.addEventListener('click', () => {
                    this.currentPage = i;
                    this.loadTempRolls();
                });
                pagesContainer.appendChild(pageBtn);
            }
        }
        
        // Update pagination for cards view
        const prevBtnCards = document.getElementById('temp-rolls-prev-page-cards');
        const nextBtnCards = document.getElementById('temp-rolls-next-page-cards');
        const pagesContainerCards = document.getElementById('temp-rolls-page-numbers-cards');
        
        if (prevBtnCards) prevBtnCards.disabled = this.currentPage <= 1;
        if (nextBtnCards) nextBtnCards.disabled = this.currentPage >= totalPages;
        
        if (pagesContainerCards) {
            pagesContainerCards.innerHTML = '';
            
            for (let i = Math.max(1, this.currentPage - 2); i <= Math.min(totalPages, this.currentPage + 2); i++) {
                const pageBtn = document.createElement('span');
                pageBtn.className = `page-number ${i === this.currentPage ? 'active' : ''}`;
                pageBtn.textContent = i;
                pageBtn.style.cursor = 'pointer';
                pageBtn.addEventListener('click', () => {
                    this.currentPage = i;
                    this.loadTempRolls();
                });
                pagesContainerCards.appendChild(pageBtn);
            }
        }
    }

    /**
     * Update entity count display
     */
    updateEntityCount() {
        // Update main result count in explore template
        const resultCount = document.getElementById('result-count');
        if (resultCount) {
            resultCount.textContent = `(${this.totalCount})`;
        }
        
        // Also update temp-roll-specific count if it exists
        const countElement = document.getElementById('temp-roll-count');
        if (countElement) {
            countElement.textContent = this.totalCount;
        }
    }

    /**
     * Show/hide loading state
     * @param {boolean} show - Whether to show loading
     */
    showLoading(show) {
        const loadingElement = document.getElementById('temp-roll-loading');
        const tableView = document.getElementById('temp-rolls-table-view');
        const cardsView = document.getElementById('temp-rolls-cards-view');
        
        if (loadingElement) loadingElement.style.display = show ? 'flex' : 'none';
        if (tableView) tableView.style.display = show ? 'none' : (this.currentView === 'table' ? 'block' : 'none');
        if (cardsView) cardsView.style.display = show ? 'none' : (this.currentView === 'cards' ? 'block' : 'none');
    }

    /**
     * Show/hide empty state
     * @param {boolean} show - Whether to show empty state
     */
    showEmpty(show) {
        const emptyElement = document.getElementById('temp-roll-empty');
        const tableView = document.getElementById('temp-rolls-table-view');
        const cardsView = document.getElementById('temp-rolls-cards-view');
        
        if (emptyElement) emptyElement.style.display = show ? 'flex' : 'none';
        if (tableView) tableView.style.display = show ? 'none' : (this.currentView === 'table' ? 'block' : 'none');
        if (cardsView) cardsView.style.display = show ? 'none' : (this.currentView === 'cards' ? 'block' : 'none');
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // For now, just use alert. Could be enhanced with a proper error display
        alert(message);
    }
}

// Export the class for use in the main module
window.TempRollManager = TempRollManager; 