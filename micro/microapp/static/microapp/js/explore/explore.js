/**
 * explore.js - Microfilm Database Explorer
 * This script handles the UI and API interactions for the explore page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Database Service for API calls
    const dbService = new DatabaseService();
    
    // Entity selection
    const entityOptions = document.querySelectorAll('.entity-option');
    const entityFilters = document.querySelectorAll('.entity-filters');
    
    entityOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Update selection
            entityOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            
            // Show corresponding filters
            const entity = this.getAttribute('data-entity');
            entityFilters.forEach(filter => filter.classList.remove('active'));
            document.getElementById(`${entity}-filters`).classList.add('active');
            
            // Update table headers based on selected entity
            updateTableHeaders(entity);
            
            // Update results based on selected entity
            updateResults(entity);
            
            // Show/hide batch operations based on entity
            if (entity === 'projects') {
                document.getElementById('batch-operations').style.display = 'flex';
            } else {
                document.getElementById('batch-operations').style.display = 'none';
            }
        });
    });
    
    // Toggle advanced filters
    const toggleAdvancedButton = document.getElementById('toggle-advanced');
    const advancedFilters = document.getElementById('advanced-filters');
    
    toggleAdvancedButton.addEventListener('click', function() {
        advancedFilters.classList.toggle('visible');
        this.classList.toggle('active');
    });
    
    // Add condition in advanced filters
    const addConditionButton = document.getElementById('add-condition');
    const filterBuilder = document.querySelector('.filter-builder');
    
    addConditionButton.addEventListener('click', function() {
        const newCondition = document.createElement('div');
        newCondition.className = 'filter-condition';
        newCondition.innerHTML = `
            <select class="condition-field">
                <option value="">Select field</option>
                <optgroup label="Projects">
                    <option value="project_id">Project ID</option>
                    <option value="archive_id">Archive ID</option>
                    <option value="total_pages">Total Pages</option>
                    <option value="has_oversized">Oversized</option>
                </optgroup>
                <optgroup label="Rolls">
                    <option value="film_number">Film Number</option>
                    <option value="capacity">Capacity</option>
                    <option value="pages_used">Pages Used</option>
                    <option value="pages_remaining">Pages Remaining</option>
                </optgroup>
                <optgroup label="Documents">
                    <option value="document_name">Document Name</option>
                    <option value="com_id">COM ID</option>
                    <option value="blip">Blip</option>
                </optgroup>
            </select>
            
            <select class="condition-operator">
                <option value="equals">equals</option>
                <option value="not_equals">not equals</option>
                <option value="greater_than">greater than</option>
                <option value="less_than">less than</option>
                <option value="contains">contains</option>
                <option value="starts_with">starts with</option>
                <option value="ends_with">ends with</option>
            </select>
            
            <input type="text" class="condition-value" placeholder="Value">
            
            <button class="remove-condition">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        filterBuilder.appendChild(newCondition);
        
        // Add event listener to remove button
        newCondition.querySelector('.remove-condition').addEventListener('click', function() {
            newCondition.remove();
        });
    });
    
    // View controls
    const viewControls = document.querySelectorAll('.view-control');
    const resultViews = document.querySelectorAll('.result-view');
    
    viewControls.forEach(control => {
        control.addEventListener('click', function() {
            const view = this.getAttribute('data-view');
            
            // Update control buttons
            viewControls.forEach(ctrl => ctrl.classList.remove('active'));
            this.classList.add('active');
            
            // Update view
            resultViews.forEach(v => v.classList.remove('active'));
            document.getElementById(`${view}-view`).classList.add('active');
            
            // If switching to visualization, initialize/update chart
            if (view === 'visualization') {
                initializeChart();
            }
        });
    });
    
    // Apply filters
    const applyFiltersButton = document.getElementById('apply-filters');
    const resetFiltersButton = document.getElementById('reset-filters');
    
    applyFiltersButton.addEventListener('click', function() {
        const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
        updateResults(selectedEntity);
    });
    
    resetFiltersButton.addEventListener('click', function() {
        // Reset all filter inputs
        document.querySelectorAll('select, input[type="text"], input[type="date"]').forEach(input => {
            input.value = '';
        });
        
        // Reset advanced filters
        document.querySelectorAll('.filter-condition').forEach((condition, index) => {
            if (index > 0) {
                condition.remove();
            } else {
                condition.querySelector('.condition-field').value = '';
                condition.querySelector('.condition-operator').value = 'equals';
                condition.querySelector('.condition-value').value = '';
            }
        });
        
        // Reset join type
        document.querySelector('input[name="join-type"][value="AND"]').checked = true;
        
        // Reset SQL query
        document.getElementById('sql-query').value = '';
        
        // Reset results
        const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
        updateResults(selectedEntity, true);
    });
    
    // Update table headers based on entity
    function updateTableHeaders(entity) {
        const tableHead = document.querySelector('.results-table thead tr');
        
        // Clear existing headers
        tableHead.innerHTML = '';
        
        // Add appropriate headers based on entity
        if (entity === 'projects') {
            tableHead.innerHTML = `
                <th>
                    <input type="checkbox" id="select-all-projects" class="batch-checkbox">
                </th>
                <th>ID</th>
                <th>Archive ID</th>
                <th>Location</th>
                <th>Document Type</th>
                <th>Total Pages</th>
                <th>Status</th>
                <th>Date Created</th>
                <th>Actions</th>
            `;
            
            // Add select all functionality
            document.getElementById('select-all-projects').addEventListener('change', function() {
                const checkboxes = document.querySelectorAll('.project-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
                updateBatchCount();
            });
        } else if (entity === 'rolls') {
            tableHead.innerHTML = `
                <th>ID</th>
                <th>Film Number</th>
                <th>Film Type</th>
                <th>Pages Used</th>
                <th>Pages Remaining</th>
                <th>Status</th>
                <th>Actions</th>
            `;
        } else if (entity === 'documents') {
            tableHead.innerHTML = `
                <th>ID</th>
                <th>Document Name</th>
                <th>COM ID</th>
                <th>Roll ID</th>
                <th>Page Range</th>
                <th>Blip</th>
                <th>Actions</th>
            `;
        } else if (entity === 'temp-rolls') {
            tableHead.innerHTML = `
                <th>ID</th>
                <th>Film Type</th>
                <th>Capacity</th>
                <th>Usable Capacity</th>
                <th>Status</th>
                <th>Creation Date</th>
                <th>Actions</th>
            `;
        }
    }
    
    // Update results based on entity and filters
    async function updateResults(entity, isReset = false) {
        const tableBody = document.getElementById('results-body');
        const cardsContainer = document.getElementById('results-cards');
        const resultCount = document.getElementById('result-count');
        
        // Show loading state
        tableBody.innerHTML = `<tr><td colspan="9" class="text-center">Loading data...</td></tr>`;
        cardsContainer.innerHTML = `<div class="loading-spinner">Loading data...</div>`;
        
        try {
            // Build filter object based on selected entity and form inputs
            const filters = buildFilterObject(entity, isReset);
            
            // Get pagination and sorting parameters
            const page = 1; // Start with first page
            const pageSize = parseInt(document.getElementById('page-size').value);
            
            // Fetch data from API based on entity
            let data;
            let totalRecords;
            let totalPages;
            
            if (entity === 'projects') {
                const response = await dbService.listProjects(filters, page, pageSize);
                data = response.results;
                totalRecords = response.total;
                totalPages = response.total_pages;
            } else if (entity === 'rolls') {
                // Implementation for rolls will be added later
                data = [];
                totalRecords = 0;
                totalPages = 0;
                alert("Roll management is not yet implemented");
            } else if (entity === 'documents') {
                // Implementation for documents will be added later
                data = [];
                totalRecords = 0;
                totalPages = 0;
                alert("Document management is not yet implemented");
            } else if (entity === 'temp-rolls') {
                // Implementation for temp rolls will be added later
                data = [];
                totalRecords = 0;
                totalPages = 0;
                alert("Temp Roll management is not yet implemented");
            }
            
            // Update count
            resultCount.textContent = `(${totalRecords})`;
            
            // Update pagination controls
            updatePageNumbers(totalPages, page);
            updatePageNumbersCards(totalPages, page);
            
            // Enable/disable pagination buttons
            document.getElementById('prev-page').disabled = page === 1;
            document.getElementById('next-page').disabled = page === totalPages || totalPages === 0;
            document.getElementById('prev-page-cards').disabled = page === 1;
            document.getElementById('next-page-cards').disabled = page === totalPages || totalPages === 0;
            
            // Add pagination event listeners
            document.getElementById('prev-page').onclick = function() {
                if (page > 1) {
                    const newPage = page - 1;
                    changePage(entity, newPage, pageSize);
                }
            };
            
            document.getElementById('next-page').onclick = function() {
                if (page < totalPages) {
                    const newPage = page + 1;
                    changePage(entity, newPage, pageSize);
                }
            };
            
            document.getElementById('prev-page-cards').onclick = function() {
                if (page > 1) {
                    const newPage = page - 1;
                    changePage(entity, newPage, pageSize);
                }
            };
            
            document.getElementById('next-page-cards').onclick = function() {
                if (page < totalPages) {
                    const newPage = page + 1;
                    changePage(entity, newPage, pageSize);
                }
            };
            
            // Render data in table and cards
            renderPage(data, page, pageSize, entity);
            renderPageCards(data, page, pageSize, entity);
            
            // Update chart if visualization is active
            if (document.getElementById('visualization-view').classList.contains('active')) {
                initializeChart(data, entity);
            }
            
            // Reset batch selection
            updateBatchCount();
            
        } catch (error) {
            console.error("Error fetching data:", error);
            tableBody.innerHTML = `<tr><td colspan="9" class="text-center">Error loading data: ${error.message}</td></tr>`;
            cardsContainer.innerHTML = `<div class="error-message">Error loading data: ${error.message}</div>`;
        }
    }
    
    // Build filter object based on UI inputs
    function buildFilterObject(entity, isReset = false) {
        if (isReset) {
            return {};
        }
        
        const filters = {};
        
        // Get search term
        const searchTerm = document.getElementById('search-term').value;
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
        
        // Get entity-specific filters
        if (entity === 'projects') {
            const docType = document.getElementById('doc-type').value;
            if (docType) {
                filters.doc_type = docType;
            }
            
            const location = document.getElementById('location').value;
            if (location) {
                filters.location = location;
            }
            
            const status = document.getElementById('project-status').value;
            if (status) {
                filters.status = status;
            }
            
            const oversized = document.getElementById('has-oversized').value;
            if (oversized !== '') {
                filters.has_oversized = oversized === 'true';
            }
            
            const processingComplete = document.getElementById('processing-complete').value;
            if (processingComplete !== '') {
                filters.processing_complete = processingComplete === 'true';
            }
        } 
        // Add other entity filters when those entity types are implemented
        
        // Get sort parameters
        const sortField = document.getElementById('sort-field').value;
        if (sortField) {
            filters.sort_field = sortField;
        }
        
        const sortOrder = document.getElementById('sort-order').value;
        if (sortOrder) {
            filters.sort_order = sortOrder;
        }
        
        // Advanced filters will be added in a future update
        
        return filters;
    }
    
    // Change page for pagination
    async function changePage(entity, page, pageSize) {
        const filters = buildFilterObject(entity, false);
        
        try {
            let data;
            let totalPages;
            
            if (entity === 'projects') {
                const response = await dbService.listProjects(filters, page, pageSize);
                data = response.results;
                totalPages = response.total_pages;
            } else {
                // Handle other entities when implemented
                return;
            }
            
            // Update pagination UI
            updatePageNumbers(totalPages, page);
            updatePageNumbersCards(totalPages, page);
            
            // Enable/disable pagination buttons
            document.getElementById('prev-page').disabled = page === 1;
            document.getElementById('next-page').disabled = page === totalPages || totalPages === 0;
            document.getElementById('prev-page-cards').disabled = page === 1;
            document.getElementById('next-page-cards').disabled = page === totalPages || totalPages === 0;
            
            // Render data
            renderPage(data, page, pageSize, entity);
            renderPageCards(data, page, pageSize, entity);
            
        } catch (error) {
            console.error("Error changing page:", error);
        }
    }
    
    // Render table page
    function renderPage(data, page, pageSize, entity) {
        const tableBody = document.getElementById('results-body');
        
        // Clear table
        tableBody.innerHTML = '';
        
        // If no data, show empty message
        if (!data || data.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="9">No data available. Try adjusting your filters.</td>
                </tr>
            `;
            return;
        }
        
        // Add rows
        data.forEach(item => {
            const row = document.createElement('tr');
            
            if (entity === 'projects') {
                // Get status badge class
                let statusClass = 'draft';
                let statusText = 'Draft';
                
                if (item.processing_complete) {
                    statusClass = 'complete';
                    statusText = 'Complete';
                } else if (item.film_allocation_complete) {
                    statusClass = 'in-process';
                    statusText = 'Film Allocated';
                } else if (item.has_pdf_folder) {
                    statusClass = 'pending';
                    statusText = 'Processing';
                }
                
                row.innerHTML = `
                    <td>
                        <input type="checkbox" class="batch-checkbox project-checkbox" data-id="${item.project_id}">
                    </td>
                    <td>${item.project_id}</td>
                    <td>${item.archive_id}</td>
                    <td>${item.location}</td>
                    <td>${item.doc_type || 'N/A'}</td>
                    <td>${item.total_pages || 0}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td>${item.date_created}</td>
                    <td>
                        <button class="action-icon view-details" data-id="${item.project_id}" data-type="project" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-icon edit-item" data-id="${item.project_id}" data-type="project" title="Edit Project">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-icon process-project" data-id="${item.project_id}" title="Process Project">
                            <i class="fas fa-cogs"></i>
                        </button>
                        <button class="action-icon delete-item" data-id="${item.project_id}" data-type="project" title="Delete Project">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
            } 
            // Other entity types will be added later
            
            tableBody.appendChild(row);
        });
        
        // Add event listeners to checkboxes
        document.querySelectorAll('.project-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateBatchCount();
            });
        });
        
        // Add event listeners to view details buttons
        document.querySelectorAll('.view-details').forEach(button => {
            button.addEventListener('click', function() {
                showItemDetails(this.getAttribute('data-id'), this.getAttribute('data-type'));
            });
        });
        
        // Add event listeners to edit buttons
        document.querySelectorAll('.edit-item').forEach(button => {
            button.addEventListener('click', function() {
                editItem(this.getAttribute('data-id'), this.getAttribute('data-type'));
            });
        });
        
        // Add event listeners to process buttons
        document.querySelectorAll('.process-project').forEach(button => {
            button.addEventListener('click', function() {
                processProject(this.getAttribute('data-id'));
            });
        });
        
        // Add event listeners to delete buttons
        document.querySelectorAll('.delete-item').forEach(button => {
            button.addEventListener('click', function() {
                deleteItem(this.getAttribute('data-id'), this.getAttribute('data-type'));
            });
        });
    }
    
    // Render cards page
    function renderPageCards(data, page, pageSize, entity) {
        const cardsContainer = document.getElementById('results-cards');
        
        // Clear container
        cardsContainer.innerHTML = '';
        
        // If no data, show empty message
        if (!data || data.length === 0) {
            cardsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>No data available. Try adjusting your filters.</p>
                </div>
            `;
            return;
        }
        
        // Add cards
        data.forEach(item => {
            const card = document.createElement('div');
            card.className = 'item-card';
            
            if (entity === 'projects') {
                // Get status badge class
                let statusClass = 'draft';
                let statusText = 'Draft';
                
                if (item.processing_complete) {
                    statusClass = 'complete';
                    statusText = 'Complete';
                } else if (item.film_allocation_complete) {
                    statusClass = 'in-process';
                    statusText = 'Film Allocated';
                } else if (item.has_pdf_folder) {
                    statusClass = 'pending';
                    statusText = 'Processing';
                }
                
                card.innerHTML = `
                    <div class="card-header">
                        <h3>${item.project_folder_name || 'Unnamed Project'}</h3>
                        <span class="card-id">${item.archive_id}</span>
                    </div>
                    <div class="card-body">
                        <div class="card-property">
                            <span class="property-label">Type:</span>
                            <span class="property-value">${item.doc_type || 'N/A'}</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Location:</span>
                            <span class="property-value">${item.location}</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Pages:</span>
                            <span class="property-value">${item.total_pages || 0}</span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Status:</span>
                            <span class="property-value">
                                <span class="status-badge ${statusClass}">${statusText}</span>
                            </span>
                        </div>
                        <div class="card-property">
                            <span class="property-label">Date:</span>
                            <span class="property-value">${item.date_created}</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="card-button view-details" data-id="${item.project_id}" data-type="project">
                            <i class="fas fa-eye"></i> Details
                        </button>
                        <button class="card-button edit-item" data-id="${item.project_id}" data-type="project">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                    </div>
                `;
            }
            // Other entity types will be added later
            
            cardsContainer.appendChild(card);
        });
        
        // Add event listeners to view details buttons
        document.querySelectorAll('.card-button.view-details').forEach(button => {
            button.addEventListener('click', function() {
                showItemDetails(this.getAttribute('data-id'), this.getAttribute('data-type'));
            });
        });
        
        // Add event listeners to edit buttons
        document.querySelectorAll('.card-button.edit-item').forEach(button => {
            button.addEventListener('click', function() {
                editItem(this.getAttribute('data-id'), this.getAttribute('data-type'));
            });
        });
    }
    
    // Update page numbers for table view
    function updatePageNumbers(totalPages, currentPage) {
        const pageNumbers = document.getElementById('page-numbers');
        pageNumbers.innerHTML = '';
        
        // Show at most 5 page numbers
        const maxPages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
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
                const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                const pageSize = parseInt(document.getElementById('page-size').value);
                changePage(entity, 1, pageSize);
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
            pageSpan.className = 'page-number' + (i === currentPage ? ' active' : '');
            pageSpan.textContent = i;
            pageSpan.addEventListener('click', () => {
                if (i !== currentPage) {
                    const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                    const pageSize = parseInt(document.getElementById('page-size').value);
                    changePage(entity, i, pageSize);
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
                const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                const pageSize = parseInt(document.getElementById('page-size').value);
                changePage(entity, totalPages, pageSize);
            });
            pageNumbers.appendChild(pageSpan);
        }
    }
    
    // Update page numbers for cards view
    function updatePageNumbersCards(totalPages, currentPage) {
        const pageNumbers = document.getElementById('page-numbers-cards');
        pageNumbers.innerHTML = '';
        
        // Show at most 5 page numbers
        const maxPages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
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
                const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                const pageSize = parseInt(document.getElementById('page-size').value);
                changePage(entity, 1, pageSize);
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
            pageSpan.className = 'page-number' + (i === currentPage ? ' active' : '');
            pageSpan.textContent = i;
            pageSpan.addEventListener('click', () => {
                if (i !== currentPage) {
                    const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                    const pageSize = parseInt(document.getElementById('page-size').value);
                    changePage(entity, i, pageSize);
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
                const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                const pageSize = parseInt(document.getElementById('page-size').value);
                changePage(entity, totalPages, pageSize);
            });
            pageNumbers.appendChild(pageSpan);
        }
    }
    
    // Process project
    async function processProject(id) {
        try {
            const confirmed = confirm(`Start processing for Project #${id}?`);
            if (confirmed) {
                const dbService = new DatabaseService();
                await dbService.processProject(id);
                alert("Project processing started successfully!");
                
                // Refresh data
                const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                updateResults(selectedEntity);
            }
        } catch (error) {
            console.error("Error processing project:", error);
            alert(`Error processing project: ${error.message}`);
        }
    }
    
    // Update batch operation counter
    function updateBatchCount() {
        const selectedCount = document.querySelectorAll('.project-checkbox:checked').length;
        const batchCounter = document.getElementById('batch-counter');
        const batchButtons = document.querySelectorAll('.batch-action');
        
        if (selectedCount > 0) {
            batchCounter.textContent = selectedCount;
            batchCounter.style.display = 'inline-block';
            batchButtons.forEach(button => button.disabled = false);
        } else {
            batchCounter.style.display = 'none';
            batchButtons.forEach(button => button.disabled = true);
        }
    }
    
    // Handle batch operations
    function initializeBatchOperations() {
        const batchUpdateStatus = document.getElementById('batch-update-status');
        const batchDelete = document.getElementById('batch-delete');
        const batchProcess = document.getElementById('batch-process');
        
        batchUpdateStatus.addEventListener('click', async function() {
            const selectedIds = Array.from(document.querySelectorAll('.project-checkbox:checked'))
                .map(checkbox => checkbox.getAttribute('data-id'));
            
            if (selectedIds.length === 0) return;
            
            const newStatus = prompt("Enter new status (processing_complete): true/false");
            if (newStatus !== null) {
                try {
                    const dbService = new DatabaseService();
                    await Promise.all(selectedIds.map(id => {
                        return dbService.updateProject(id, { processing_complete: newStatus === 'true' });
                    }));
                    
                    alert(`Updated status for ${selectedIds.length} projects`);
                    
                    // Refresh data
                    const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                    updateResults(selectedEntity);
                } catch (error) {
                    console.error("Error updating projects:", error);
                    alert(`Error updating projects: ${error.message}`);
                }
            }
        });
        
        batchDelete.addEventListener('click', async function() {
            const selectedIds = Array.from(document.querySelectorAll('.project-checkbox:checked'))
                .map(checkbox => checkbox.getAttribute('data-id'));
            
            if (selectedIds.length === 0) return;
            
            const confirmed = confirm(`Are you sure you want to delete ${selectedIds.length} projects? This action cannot be undone.`);
            if (confirmed) {
                try {
                    const dbService = new DatabaseService();
                    await Promise.all(selectedIds.map(id => dbService.deleteProject(id)));
                    
                    alert(`Deleted ${selectedIds.length} projects successfully`);
                    
                    // Refresh data
                    const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                    updateResults(selectedEntity);
                } catch (error) {
                    console.error("Error deleting projects:", error);
                    alert(`Error deleting projects: ${error.message}`);
                }
            }
        });
        
        batchProcess.addEventListener('click', async function() {
            const selectedIds = Array.from(document.querySelectorAll('.project-checkbox:checked'))
                .map(checkbox => checkbox.getAttribute('data-id'));
            
            if (selectedIds.length === 0) return;
            
            const confirmed = confirm(`Start processing for ${selectedIds.length} projects?`);
            if (confirmed) {
                try {
                    const dbService = new DatabaseService();
                    await Promise.all(selectedIds.map(id => dbService.processProject(id)));
                    
                    alert(`Started processing for ${selectedIds.length} projects`);
                    
                    // Refresh data
                    const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                    updateResults(selectedEntity);
                } catch (error) {
                    console.error("Error processing projects:", error);
                    alert(`Error processing projects: ${error.message}`);
                }
            }
        });
    }
    
    // Export buttons functionality
    const exportButtons = document.querySelectorAll('.export-button');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.id.split('-')[1]; // Extract the format from button id
            const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
            exportData(selectedEntity, format);
        });
    });
    
    // Initialize content on page load
    initialize();
    
    function initialize() {
        // Load initial data for projects (default view)
        updateResults('projects');
        
        // Initialize event handlers for modals
        initializeModals();
        
        // Initialize batch operations
        initializeBatchOperations();
    }
});