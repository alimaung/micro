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
        this.setupEventListeners();
        this.loadProjects();
        
        // Load document types and locations for dropdowns
        this.loadDocumentTypes();
        this.loadLocations();
    }

    /**
     * Set up event listeners for project list functionality
     */
    setupEventListeners() {
        // Filter button event
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.buildFilters();
            this.loadProjects();
        });

        // Reset filters button event
        document.getElementById('reset-filters').addEventListener('click', () => {
            this.resetFilters();
        });

        // Pagination events
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadProjects();
            }
        });

        document.getElementById('next-page').addEventListener('click', () => {
            this.currentPage++;
            this.loadProjects();
        });

        // Page size change event
        document.getElementById('page-size').addEventListener('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            this.currentPage = 1;  // Reset to first page when changing page size
            this.loadProjects();
        });

        // Sort controls
        document.getElementById('sort-field').addEventListener('change', (e) => {
            this.sortField = e.target.value;
            this.loadProjects();
        });

        document.getElementById('sort-order').addEventListener('change', (e) => {
            this.sortOrder = e.target.value;
            this.loadProjects();
        });

        // Select all checkbox
        document.getElementById('select-all-projects').addEventListener('change', (e) => {
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

        // Batch operation buttons
        document.getElementById('batch-update-status').addEventListener('click', () => {
            this.batchUpdateStatus();
        });

        document.getElementById('batch-delete').addEventListener('click', () => {
            this.batchDeleteProjects();
        });

        // Export buttons
        document.getElementById('export-csv').addEventListener('click', () => {
            this.exportProjects('csv');
        });

        document.getElementById('export-excel').addEventListener('click', () => {
            this.exportProjects('excel');
        });

        document.getElementById('export-pdf').addEventListener('click', () => {
            this.exportProjects('pdf');
        });

        document.getElementById('export-json').addEventListener('click', () => {
            this.exportProjects('json');
        });
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
     * Load projects with current filters and pagination
     */
    async loadProjects() {
        const tableBody = document.getElementById('results-body');
        const resultCount = document.getElementById('result-count');
        
        // Show loading state
        tableBody.innerHTML = `<tr><td colspan="9" class="loading-row">Loading projects...</td></tr>`;
        
        try {
            // Add pagination parameters to filters
            const params = {
                ...this.filters,
                page: this.currentPage,
                page_size: this.pageSize
            };
            
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
            document.getElementById('prev-page').disabled = this.currentPage === 1;
            document.getElementById('next-page').disabled = this.currentPage === totalPages || totalPages === 0;
            
            // Render projects in table
            this.renderProjects(projects);
            
            // Restore selection state
            this.restoreSelectionState();
            
        } catch (error) {
            console.error("Error loading projects:", error);
            tableBody.innerHTML = `
                <tr class="error-row">
                    <td colspan="9">
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
        const tableBody = document.getElementById('results-body');
        
        // Clear table
        tableBody.innerHTML = '';
        
        // If no projects, show empty message
        if (!projects || projects.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="9">No projects found. Try adjusting your filters.</td>
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
                <td>${project.project_id}</td>
                <td>${project.archive_id}</td>
                <td>${project.location}</td>
                <td>${project.doc_type || 'N/A'}</td>
                <td>${project.total_pages || 0}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${project.date_created}</td>
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
        // Checkbox selection
        document.querySelectorAll('.project-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const projectId = e.target.dataset.id;
                
                if (e.target.checked) {
                    this.selectedProjects.add(projectId);
                } else {
                    this.selectedProjects.delete(projectId);
                }
                
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
        const pageNumbers = document.getElementById('page-numbers');
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
        
        if (count > 0) {
            batchCounter.textContent = count;
            batchCounter.style.display = 'inline-block';
            batchButtons.forEach(button => button.disabled = false);
        } else {
            batchCounter.style.display = 'none';
            batchButtons.forEach(button => button.disabled = true);
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
            // Determine which projects to export (selected or all filtered)
            let projectIds = [];
            let useFilters = true;
            
            if (this.selectedProjects.size > 0) {
                projectIds = Array.from(this.selectedProjects);
                useFilters = false;
                
                const confirmed = confirm(`Export ${projectIds.length} selected projects as ${format.toUpperCase()}?`);
                if (!confirmed) return;
            } else {
                const confirmed = confirm(`Export all filtered projects as ${format.toUpperCase()}?`);
                if (!confirmed) return;
            }
            
            // Show loading indicator
            const exportButton = document.getElementById(`export-${format}`);
            const originalText = exportButton.innerHTML;
            exportButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
            exportButton.disabled = true;
            
            // Call the appropriate export method
            const blob = await this.dbService.exportProjects(projectIds, format, useFilters ? this.filters : null);
            
            // Create a download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `projects_export_${new Date().toISOString().slice(0, 10)}.${format}`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                exportButton.innerHTML = originalText;
                exportButton.disabled = false;
            }, 100);
        } catch (error) {
            console.error(`Error exporting projects as ${format}:`, error);
            alert(`Error exporting projects: ${error.message || 'Unknown error'}`);
            
            // Reset export button
            const exportButton = document.getElementById(`export-${format}`);
            exportButton.innerHTML = `<i class="fas fa-file-${format}"></i> ${format.toUpperCase()}`;
            exportButton.disabled = false;
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
}

// Export the class for use in the main module
window.ProjectList = ProjectList; 