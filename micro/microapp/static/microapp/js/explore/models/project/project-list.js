/**
 * project-list.js - Project listing functionality
 * Handles displaying, filtering, and paginating projects
 */

class ProjectList {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentPage = 1;
        this.pageSize = 25;
        this.filters = {};
        this.sortField = 'id';
        this.sortOrder = 'desc';
        this.selectedProjects = new Set();
    }

    /**
     * Initialize the project list module
     */
    initialize() {
        console.log('Initializing ProjectList...');
        
        // Don't set up event listeners here since templates aren't loaded yet
        // Event listeners will be set up when the project entity is selected
        
        // Initialize state
        this.selectedProjects = new Set();
        this.currentPage = 1;
        this.pageSize = 25;
        this.sortField = 'id';
        this.sortOrder = 'asc';
    }

    /**
     * Set up event listeners after templates are loaded
     */
    setupEventListeners() {
        console.log('Setting up ProjectList event listeners...');
        
        // Check if elements exist before adding listeners
        const applyFiltersBtn = document.getElementById('apply-filters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                this.currentPage = 1;  // Reset to first page when applying filters
                this.buildFilters();
                this.loadProjects();
            });
        }

        const resetFiltersBtn = document.getElementById('reset-filters');
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', () => {
                this.resetFilters();
            });
        }

        // Pagination events
        const prevPageBtn = document.getElementById('projects-prev-page');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.loadProjects();
                }
            });
        }

        const nextPageBtn = document.getElementById('projects-next-page');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                this.currentPage++;
                this.loadProjects();
            });
        }

        // Page size change event
        const pageSizeSelect = document.getElementById('page-size');
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', (e) => {
                this.pageSize = parseInt(e.target.value);
                this.currentPage = 1;  // Reset to first page when changing page size
                this.loadProjects();
            });
        }

        // Sort controls (dropdown)
        const sortFieldSelect = document.getElementById('sort-field');
        if (sortFieldSelect) {
            sortFieldSelect.addEventListener('change', (e) => {
                this.sortField = e.target.value;
                this.updateSortIndicators();
                this.loadProjects();
            });
        }

        const sortOrderSelect = document.getElementById('sort-order');
        if (sortOrderSelect) {
            sortOrderSelect.addEventListener('change', (e) => {
                this.sortOrder = e.target.value;
                this.updateSortIndicators();
                this.loadProjects();
            });
        }

        // Sortable table headers
        this.setupSortableHeaders();

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-projects');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.project-checkbox');
                const isChecked = e.target.checked;
                
                checkboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    
                    if (isChecked) {
                        this.selectedProjects.add(checkbox.dataset.id);
                    } else {
                        this.selectedProjects.delete(checkbox.dataset.id);
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
                this.batchDeleteProjects();
            });
        }

        // Export buttons
        const exportCsvBtn = document.getElementById('export-csv');
        if (exportCsvBtn) {
            exportCsvBtn.addEventListener('click', () => {
                this.exportProjects('csv');
            });
        }

        const exportExcelBtn = document.getElementById('export-excel');
        if (exportExcelBtn) {
            exportExcelBtn.addEventListener('click', () => {
                this.exportProjects('excel');
            });
        }

        const exportPdfBtn = document.getElementById('export-pdf');
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', () => {
                this.exportProjects('pdf');
            });
        }

        const exportJsonBtn = document.getElementById('export-json');
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', () => {
                this.exportProjects('json');
            });
        }

        // Search button event
        const searchBtn = document.getElementById('search-button');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.currentPage = 1;
                this.buildFilters();
                this.loadProjects();
            });
        }

        // Search input Enter key event
        const searchInput = document.getElementById('search-term');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.currentPage = 1;
                    this.buildFilters();
                    this.loadProjects();
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
                
                console.log('Sorting by field:', sortField); // Debug log
                
                // If clicking the same field, toggle order
                if (this.sortField === sortField) {
                    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    // New field, default to ascending
                    this.sortField = sortField;
                    this.sortOrder = 'asc';
                }
                
                console.log('Sort field:', this.sortField, 'Sort order:', this.sortOrder); // Debug log
                
                // Update the dropdown controls to match
                const sortFieldSelect = document.getElementById('sort-field');
                const sortOrderSelect = document.getElementById('sort-order');
                
                if (sortFieldSelect) sortFieldSelect.value = this.sortField;
                if (sortOrderSelect) sortOrderSelect.value = this.sortOrder;
                
                // Update visual indicators
                this.updateSortIndicators();
                
                // Reset to first page and reload
                this.currentPage = 1;
                this.loadProjects();
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
            console.log('Updated sort indicator for:', this.sortField, this.sortOrder); // Debug log
        } else {
            console.log('Could not find header for sort field:', this.sortField); // Debug log
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
        
        // Get project-specific filters
        const docType = document.getElementById('doc-type').value;
        if (docType) {
            filters.doc_type = docType;
        }
        
        const location = document.getElementById('location').value;
        if (location) {
            filters.location = location;
        }
        
        // Map status dropdown values to actual database fields
        const status = document.getElementById('project-status').value;
        if (status) {
            switch (status) {
                case 'draft':
                    // Draft means no processing, no allocation
                    filters.processing_complete = 'false';
                    filters.has_pdf_folder = 'false';
                    break;
                case 'processing':
                    // Processing means has PDF folder but not complete
                    filters.has_pdf_folder = 'true';
                    filters.processing_complete = 'false';
                    break;
                case 'allocated':
                    // Allocated means processing complete but allocation not complete
                    filters.processing_complete = 'true';
                    filters.film_allocation_complete = 'false';
                    break;
                case 'complete':
                    // Complete means processing and allocation complete
                    filters.processing_complete = 'true';
                    filters.film_allocation_complete = 'true';
                    break;
            }
        }
        
        const oversized = document.getElementById('has-oversized').value;
        if (oversized !== '') {
            filters.has_oversized = oversized === 'true';
        }
        
        const processingComplete = document.getElementById('processing-complete').value;
        if (processingComplete !== '') {
            filters.processing_complete = processingComplete === 'true';
        }
        
        // Map sort field to backend field names if needed
        let sortField = this.sortField;
        
        // The backend already handles field mapping correctly, so we don't need to map here
        // Just pass the field name as-is from the data-sort attributes
        
        // Set sort parameters
        filters.sort_field = sortField;
        filters.sort_order = this.sortOrder;
        
        console.log('Built filters:', filters); // Debug log
        console.log('Sort field being sent to backend:', sortField); // Additional debug log
        
        this.filters = filters;
        
        // Debug log the stored filters
        console.log('Stored filters in this.filters:', this.filters);
    }

    /**
     * Reset all filters to default values
     */
    resetFilters() {
        // Reset all filter inputs
        document.querySelectorAll('select, input[type="text"], input[type="date"]').forEach(input => {
            input.value = '';
        });
        
        // Reset advanced filters if they exist
        const filterConditions = document.querySelectorAll('.filter-condition');
        if (filterConditions.length > 0) {
            filterConditions.forEach((condition, index) => {
                if (index > 0) {
                    condition.remove();
                } else {
                    const fieldSelect = condition.querySelector('.condition-field');
                    const operatorSelect = condition.querySelector('.condition-operator');
                    const valueInput = condition.querySelector('.condition-value');
                    
                    if (fieldSelect) fieldSelect.value = '';
                    if (operatorSelect) operatorSelect.value = 'equals';
                    if (valueInput) valueInput.value = '';
                }
            });
            
            // Reset join type if it exists
            const joinType = document.querySelector('input[name="join-type"][value="AND"]');
            if (joinType) joinType.checked = true;
        }
        
        // Reset SQL query if it exists
        const sqlQuery = document.getElementById('sql-query');
        if (sqlQuery) sqlQuery.value = '';
        
        // Clear filters and reload
        this.filters = {};
        this.currentPage = 1;
        this.loadProjects();
    }

    /**
     * Load and display projects
     */
    async loadProjects() {
        const tableBody = document.getElementById('projects-results-body');
        const resultCount = document.getElementById('result-count');
        
        // Show loading state
        tableBody.innerHTML = `<tr><td colspan="26" class="loading-row">Loading projects...</td></tr>`;
        
        try {
            // Always build filters first to ensure current sort parameters are included
            this.buildFilters();
            
            // Add pagination parameters to filters
            const params = {
                ...this.filters,
                page: this.currentPage,
                page_size: this.pageSize
            };
            
            // Debug log the filters being used
            console.log('Loading projects with filters:', this.filters);
            
            // Fetch projects from API
            const response = await this.dbService.listProjects(params);
            const projects = response.results;
            const totalProjects = response.total;
            const totalPages = response.total_pages;
            
            // Update count display
            resultCount.textContent = `(${totalProjects})`;
            
            // Update pagination UI
            this.updatePagination(totalPages);
            
            // Enable/disable pagination buttons
            document.getElementById('projects-prev-page').disabled = this.currentPage === 1;
            document.getElementById('projects-next-page').disabled = this.currentPage === totalPages || totalPages === 0;
            
            // Render projects based on active view
            const activeView = document.querySelector('.view-control.active')?.getAttribute('data-view') || 'table';
            
            if (activeView === 'cards') {
                this.renderProjectsAsCards(projects);
            } else if (activeView === 'visualization') {
                this.renderProjectsAsVisualization(projects);
            } else {
                this.renderProjects(projects);
            }
            
            // Restore selection state
            this.restoreSelectionState();
            
            // Update sort indicators
            this.updateSortIndicators();
            
        } catch (error) {
            console.error("Error loading projects:", error);
            tableBody.innerHTML = `
                <tr class="error-row">
                    <td colspan="26">
                        <div class="error-message">
                            Error loading projects: ${error.message || 'Unknown error'}
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Render projects in the table
     * @param {Array} projects - List of project objects to render
     */
    renderProjects(projects) {
        const tableBody = document.getElementById('projects-results-body');
        
        // Clear table
        tableBody.innerHTML = '';
        
        // If no projects, show empty message
        if (!projects || projects.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="26">No projects found. Try adjusting your filters.</td>
                </tr>
            `;
            return;
        }
        
        // Add rows for each project
        projects.forEach(project => {
            // Get status badge class and text
            let statusClass = 'draft';
            let statusText = 'Draft';
            
            if (project.processing_complete) {
                statusClass = 'complete';
                statusText = 'Complete';
            } else if (project.film_allocation_complete) {
                statusClass = 'in-process';
                statusText = 'Film Allocated';
            } else if (project.has_pdf_folder) {
                statusClass = 'pending';
                statusText = 'Processing';
            }
            
            // Create table row
            const row = document.createElement('tr');
            row.className = `project-row status-${statusClass}`;
            row.dataset.id = project.project_id;
            
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="batch-checkbox project-checkbox" data-id="${project.project_id}">
                </td>
                <td>${project.project_id || project.id}</td>
                <td>${project.archive_id || 'N/A'}</td>
                <td>${project.location || 'N/A'}</td>
                <td>${project.doc_type || 'N/A'}</td>
                <td class="path-cell" title="${project.project_path || 'N/A'}">${project.project_path || 'N/A'}</td>
                <td class="path-cell" title="${project.project_folder_name || 'N/A'}">${project.project_folder_name || 'N/A'}</td>
                <td class="path-cell" title="${project.pdf_folder_path || 'N/A'}">${project.pdf_folder_path || 'N/A'}</td>
                <td class="path-cell" title="${project.comlist_path || 'N/A'}">${project.comlist_path || 'N/A'}</td>
                <td class="path-cell" title="${project.output_dir || 'N/A'}">${project.output_dir || 'N/A'}</td>
                <td><span class="boolean-badge ${project.has_pdf_folder ? 'true' : 'false'}">${project.has_pdf_folder ? 'Yes' : 'No'}</span></td>
                <td><span class="boolean-badge ${project.processing_complete ? 'true' : 'false'}">${project.processing_complete ? 'Yes' : 'No'}</span></td>
                <td><span class="boolean-badge ${project.retain_sources ? 'true' : 'false'}">${project.retain_sources ? 'Yes' : 'No'}</span></td>
                <td><span class="boolean-badge ${project.add_to_database ? 'true' : 'false'}">${project.add_to_database ? 'Yes' : 'No'}</span></td>
                <td><span class="boolean-badge ${project.has_oversized ? 'true' : 'false'}">${project.has_oversized ? 'Yes' : 'No'}</span></td>
                <td class="numeric-cell">${project.total_pages || 0}</td>
                <td class="numeric-cell">${project.total_pages_with_refs || 0}</td>
                <td class="numeric-cell">${project.documents_with_oversized || 0}</td>
                <td class="numeric-cell">${project.total_oversized || 0}</td>
                <td class="date-cell">${project.created_at || project.date_created || 'N/A'}</td>
                <td class="date-cell">${project.updated_at || 'N/A'}</td>
                <td>${project.owner || 'N/A'}</td>
                <td class="path-cell" title="${project.index_path || 'N/A'}">${project.index_path || 'N/A'}</td>
                <td class="path-cell" title="${project.data_dir || 'N/A'}">${project.data_dir || 'N/A'}</td>
                <td><span class="boolean-badge ${project.film_allocation_complete ? 'true' : 'false'}">${project.film_allocation_complete ? 'Yes' : 'No'}</span></td>
                <td><span class="boolean-badge ${project.distribution_complete ? 'true' : 'false'}">${project.distribution_complete ? 'Yes' : 'No'}</span></td>
                <td class="actions-cell">
                    <button class="action-icon view-details" data-id="${project.project_id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-icon edit-item" data-id="${project.project_id}" title="Edit Project">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-icon delete-item" data-id="${project.project_id}" title="Delete Project">
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
        // Debug: Log how many checkboxes we're setting up
        const checkboxes = document.querySelectorAll('.project-checkbox');
        console.log(`Setting up event listeners for ${checkboxes.length} project checkboxes`);
        
        // Checkbox selection
        checkboxes.forEach((checkbox, index) => {
            console.log(`Setting up checkbox ${index + 1}: data-id="${checkbox.dataset.id}"`);
            
            checkbox.addEventListener('change', (e) => {
                const projectId = e.target.dataset.id;
                
                console.log(`Checkbox changed: projectId=${projectId}, checked=${e.target.checked}`);
                console.log('Before update - selectedProjects size:', this.selectedProjects.size);
                console.log('Before update - selectedProjects contents:', Array.from(this.selectedProjects));
                
                if (e.target.checked) {
                    this.selectedProjects.add(projectId);
                    console.log(`Added project ${projectId} to selection. Total selected: ${this.selectedProjects.size}`);
                } else {
                    this.selectedProjects.delete(projectId);
                    console.log(`Removed project ${projectId} from selection. Total selected: ${this.selectedProjects.size}`);
                }
                
                console.log('After update - selectedProjects contents:', Array.from(this.selectedProjects));
                
                this.updateBatchCount();
            });
        });
        
        // View details buttons
        document.querySelectorAll('.view-details').forEach(button => {
            button.addEventListener('click', (e) => {
                const projectId = e.target.closest('.action-icon').dataset.id;
                const projectDetailsEvent = new CustomEvent('showProjectDetails', {
                    detail: { projectId }
                });
                document.dispatchEvent(projectDetailsEvent);
            });
        });
        
        // Edit buttons
        document.querySelectorAll('.edit-item').forEach(button => {
            button.addEventListener('click', (e) => {
                const projectId = e.target.closest('.action-icon').dataset.id;
                const editProjectEvent = new CustomEvent('editProject', {
                    detail: { projectId }
                });
                document.dispatchEvent(editProjectEvent);
            });
        });
        
        // Delete buttons
        document.querySelectorAll('.delete-item').forEach(button => {
            button.addEventListener('click', (e) => {
                const projectId = e.target.closest('.action-icon').dataset.id;
                this.deleteProject(projectId);
            });
        });
    }
    
    /**
     * Update pagination controls
     * @param {number} totalPages - Total number of pages
     */
    updatePagination(totalPages) {
        const pageNumbers = document.getElementById('projects-page-numbers');
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
                this.loadProjects();
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
                    this.loadProjects();
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
                this.loadProjects();
            });
            pageNumbers.appendChild(pageSpan);
        }
    }
    
    /**
     * Update batch operations counter and button states
     */
    updateBatchCount() {
        const count = this.selectedProjects.size;
        const batchCounter = document.getElementById('batch-counter');
        const batchButtons = document.querySelectorAll('.batch-action');
        
        console.log(`updateBatchCount called: count=${count}`);
        console.log('batchCounter element found:', !!batchCounter);
        console.log('batchButtons found:', batchButtons.length);
        
        if (count > 0) {
            if (batchCounter) {
                batchCounter.textContent = count;
                batchCounter.style.display = 'inline-block';
                console.log(`Batch counter updated to show ${count}`);
            }
            batchButtons.forEach(button => button.disabled = false);
            console.log('Batch buttons enabled');
        } else {
            if (batchCounter) {
                batchCounter.style.display = 'none';
                console.log('Batch counter hidden');
            }
            batchButtons.forEach(button => button.disabled = true);
            console.log('Batch buttons disabled');
        }
    }
    
    /**
     * Restore selection state after table refresh
     */
    restoreSelectionState() {
        if (this.selectedProjects.size === 0) return;
        
        const checkboxes = document.querySelectorAll('.project-checkbox');
        checkboxes.forEach(checkbox => {
            const projectId = checkbox.dataset.id;
            if (this.selectedProjects.has(projectId)) {
                checkbox.checked = true;
            }
        });
        
        this.updateBatchCount();
    }
    
    /**
     * Delete a single project
     * @param {string|number} projectId - ID of the project to delete
     */
    async deleteProject(projectId) {
        try {
            const confirmed = confirm(`Are you sure you want to delete Project #${projectId}? This action cannot be undone.`);
            if (confirmed) {
                await this.dbService.deleteProject(projectId);
                alert("Project deleted successfully!");
                
                // Remove from selected projects if present
                this.selectedProjects.delete(projectId.toString());
                
                // Reload projects
                this.loadProjects();
            }
        } catch (error) {
            console.error("Error deleting project:", error);
            alert(`Error deleting project: ${error.message || 'Unknown error'}`);
        }
    }
    
    /**
     * Batch update status for selected projects
     */
    async batchUpdateStatus() {
        if (this.selectedProjects.size === 0) return;
        
        const newStatus = prompt("Enter new status (processing_complete): true/false");
        if (newStatus !== null) {
            try {
                // Convert to boolean
                const statusValue = newStatus.toLowerCase() === 'true';
                
                // Update all selected projects
                const projectIds = Array.from(this.selectedProjects);
                
                // We'll add this method to the database service
                await this.dbService.batchUpdateProjects(
                    projectIds.map(id => ({ 
                        project_id: id,
                        processing_complete: statusValue
                    }))
                );
                
                alert(`Updated status for ${projectIds.length} projects`);
                this.loadProjects();
            } catch (error) {
                console.error("Error updating projects:", error);
                alert(`Error updating projects: ${error.message || 'Unknown error'}`);
            }
        }
    }
    
    /**
     * Batch delete selected projects
     */
    async batchDeleteProjects() {
        if (this.selectedProjects.size === 0) return;
        
        const projectIds = Array.from(this.selectedProjects);
        const confirmed = confirm(`Are you sure you want to delete ${projectIds.length} projects? This action cannot be undone.`);
        
        if (confirmed) {
            try {
                // We'll add this method to the database service
                await this.dbService.batchDeleteProjects(projectIds);
                alert(`Deleted ${projectIds.length} projects successfully`);
                
                // Clear selected projects
                this.selectedProjects.clear();
                
                // Reload projects
                this.loadProjects();
            } catch (error) {
                console.error("Error deleting projects:", error);
                alert(`Error deleting projects: ${error.message || 'Unknown error'}`);
            }
        }
    }
    
    /**
     * Export projects in the specified format
     * @param {string} format - Export format (csv, excel, pdf, json)
     */
    async exportProjects(format) {
        try {
            // Get current filtered count from the result count display
            const resultCountElement = document.getElementById('result-count');
            const resultCountText = resultCountElement ? resultCountElement.textContent : '(0)';
            const filteredCount = parseInt(resultCountText.replace(/[()]/g, '')) || 0;
            
            // Get the project export module
            const projectExport = window.exploreMain?.projectExport;
            
            if (projectExport) {
                // Open export modal with the selected format, selected projects, and filtered count
                projectExport.openExportModal(format, this.selectedProjects, filteredCount);
            } else {
                console.error('ProjectExport module not available');
                alert('Export functionality is not available. Please refresh the page and try again.');
            }
        } catch (error) {
            console.error(`Error opening export modal for ${format}:`, error);
            alert(`Error opening export modal: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Load document types and populate the dropdown
     */
    async loadDocumentTypes() {
        try {
            const docTypeSelect = document.getElementById('doc-type');
            if (!docTypeSelect) return;
            
            // Keep the first option (All Types) and remove the rest
            while (docTypeSelect.options.length > 1) {
                docTypeSelect.remove(1);
            }
            
            // Fetch document types
            const documentTypes = await this.dbService.getDocumentTypes();
            
            // Add options
            documentTypes.forEach(type => {
                if (type) { // Skip empty values
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    docTypeSelect.appendChild(option);
                }
            });
        } catch (error) {
            console.error("Error loading document types:", error);
        }
    }
    
    /**
     * Load locations and populate the dropdown
     */
    async loadLocations() {
        try {
            const locationSelect = document.getElementById('location');
            if (!locationSelect) return;
            
            // Keep the first option (All Locations) and remove the rest
            while (locationSelect.options.length > 1) {
                locationSelect.remove(1);
            }
            
            // Fetch locations
            const locations = await this.dbService.getLocations();
            
            // Add options
            locations.forEach(location => {
                if (location) { // Skip empty values
                    const option = document.createElement('option');
                    option.value = location;
                    option.textContent = location;
                    locationSelect.appendChild(option);
                }
            });
        } catch (error) {
            console.error("Error loading locations:", error);
        }
    }

    /**
     * Render projects as cards
     * @param {Array} projects - List of project objects to render
     */
    renderProjectsAsCards(projects) {
        const cardsContainer = document.getElementById('projects-results-cards');
        
        // Clear container
        cardsContainer.innerHTML = '';
        
        // If no projects, show empty message
        if (!projects || projects.length === 0) {
            cardsContainer.innerHTML = `
                <div class="empty-message">
                    <i class="fas fa-folder-open"></i>
                    <p>No projects found. Try adjusting your filters.</p>
                </div>
            `;
            return;
        }
        
        // Add cards for each project
        projects.forEach(project => {
            // Get status badge class and text
            let statusClass = 'draft';
            let statusText = 'Draft';
            
            if (project.processing_complete) {
                statusClass = 'complete';
                statusText = 'Complete';
            } else if (project.film_allocation_complete) {
                statusClass = 'in-process';
                statusText = 'Film Allocated';
            } else if (project.has_pdf_folder) {
                statusClass = 'pending';
                statusText = 'Processing';
            }
            
            // Create card element
            const card = document.createElement('div');
            card.className = `project-card status-${statusClass}`;
            card.dataset.id = project.project_id;
            
            card.innerHTML = `
                <div class="card-header">
                    <div class="card-checkbox">
                        <input type="checkbox" class="batch-checkbox project-checkbox" data-id="${project.project_id}">
                    </div>
                    <div class="card-id">#${project.project_id || project.id}</div>
                    <div class="card-status">
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                </div>
                
                <div class="card-body">
                    <h3 class="card-title">${project.archive_id || 'N/A'}</h3>
                    <div class="card-details">
                        <div class="detail-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${project.location || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-file-alt"></i>
                            <span>${project.doc_type || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-file-pdf"></i>
                            <span>${project.total_pages || 0} pages</span>
                        </div>
                        ${project.has_oversized ? `
                        <div class="detail-item oversized">
                            <i class="fas fa-expand-arrows-alt"></i>
                            <span>${project.total_oversized || 0} oversized</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div class="card-path">
                        <i class="fas fa-folder"></i>
                        <span title="${project.project_folder_name || 'N/A'}">${project.project_folder_name || 'N/A'}</span>
                    </div>
                    
                    <div class="card-date">
                        <i class="fas fa-calendar"></i>
                        <span>${project.created_at || project.date_created || 'N/A'}</span>
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="action-icon view-details" data-id="${project.project_id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-icon edit-item" data-id="${project.project_id}" title="Edit Project">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-icon delete-item" data-id="${project.project_id}" title="Delete Project">
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
     * Render projects as visualization
     * @param {Array} projects - List of project objects to render
     */
    renderProjectsAsVisualization(projects) {
        const chartCanvas = document.getElementById('projects-results-chart');
        const vizContainer = chartCanvas ? chartCanvas.parentElement : null;
        
        if (!vizContainer) {
            console.warn('Visualization container not found');
            return;
        }

        // Clear container
        vizContainer.innerHTML = '';
        
        // If no projects, show empty message
        if (!projects || projects.length === 0) {
            vizContainer.innerHTML = `
                <div class="empty-message">
                    <i class="fas fa-chart-bar"></i>
                    <p>No projects found. Try adjusting your filters.</p>
                </div>
            `;
            return;
        }
        
        // Create visualization content
        vizContainer.innerHTML = `
            <div class="viz-header">
                <h3>Project Statistics</h3>
                <div class="viz-controls">
                    <select id="viz-type">
                        <option value="status">By Status</option>
                        <option value="location">By Location</option>
                        <option value="doc-type">By Document Type</option>
                        <option value="pages">By Page Count</option>
                    </select>
                </div>
            </div>
            
            <div class="viz-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${projects.length}</div>
                        <div class="stat-label">Total Projects</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${projects.filter(p => p.processing_complete).length}</div>
                        <div class="stat-label">Completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${projects.filter(p => p.has_oversized).length}</div>
                        <div class="stat-label">With Oversized</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${projects.reduce((sum, p) => sum + (p.total_pages || 0), 0)}</div>
                        <div class="stat-label">Total Pages</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="projects-chart" width="400" height="200"></canvas>
                </div>
                
                <div class="project-list-viz">
                    ${projects.map(project => `
                        <div class="project-viz-item" data-id="${project.project_id}">
                            <div class="project-viz-info">
                                <span class="project-viz-id">#${project.project_id}</span>
                                <span class="project-viz-name">${project.archive_id}</span>
                                <span class="project-viz-pages">${project.total_pages || 0} pages</span>
                            </div>
                            <div class="project-viz-bar">
                                <div class="bar-fill" style="width: ${Math.min(100, (project.total_pages || 0) / 10)}%"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

// Export the class for use in the main module
window.ProjectList = ProjectList; 