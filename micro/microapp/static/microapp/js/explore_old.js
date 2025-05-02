
    document.addEventListener('DOMContentLoaded', function() {
        // Mock database data
        const mockData = {
            projects: [
                { project_id: 1, archive_id: 'ARC-2023-001', location: 'Main Archive', doc_type: 'Document', path: '/archives/doc/001', folderName: 'Financial Records 2023', oversized: false, total_pages: 423, total_pages_with_refs: 450, date_created: '2023-01-15', data_dir: '/data/projects/1', index_path: '/indexes/1' },
                { project_id: 2, archive_id: 'ARC-2023-002', location: 'Satellite Office', doc_type: 'Book', path: '/archives/book/002', folderName: 'Historical Manuscripts', oversized: true, total_pages: 856, total_pages_with_refs: 900, date_created: '2023-02-22', data_dir: '/data/projects/2', index_path: '/indexes/2' },
                { project_id: 3, archive_id: 'ARC-2023-003', location: 'Remote Storage', doc_type: 'Newspaper', path: '/archives/news/003', folderName: 'Daily Chronicle 1950-1960', oversized: true, total_pages: 12450, total_pages_with_refs: 12500, date_created: '2023-03-10', data_dir: '/data/projects/3', index_path: '/indexes/3' },
                { project_id: 4, archive_id: 'ARC-2023-004', location: 'Main Archive', doc_type: 'Archive', path: '/archives/arc/004', folderName: 'Corporate Records', oversized: false, total_pages: 327, total_pages_with_refs: 350, date_created: '2023-04-05', data_dir: '/data/projects/4', index_path: '/indexes/4' },
                { project_id: 5, archive_id: 'ARC-2023-005', location: 'Main Archive', doc_type: 'Document', path: '/archives/doc/005', folderName: 'Legal Documents', oversized: false, total_pages: 189, total_pages_with_refs: 200, date_created: '2023-05-18', data_dir: '/data/projects/5', index_path: '/indexes/5' }
            ],
            rolls: [
                { roll_id: 1, film_number: 'F-16-0001', film_type: '16mm', capacity: 2500, pages_used: 423, pages_remaining: 2077, status: 'In Use', project_id: 1, creation_date: '2023-01-20', source_temp_roll_id: null, created_temp_roll_id: null },
                { roll_id: 2, film_number: 'F-35-0001', film_type: '35mm', capacity: 1000, pages_used: 856, pages_remaining: 144, status: 'Complete', project_id: 2, creation_date: '2023-02-25', source_temp_roll_id: null, created_temp_roll_id: null },
                { roll_id: 3, film_number: 'F-35-0002', film_type: '35mm', capacity: 1000, pages_used: 1000, pages_remaining: 0, status: 'Complete', project_id: 3, creation_date: '2023-03-15', source_temp_roll_id: null, created_temp_roll_id: 1 },
                { roll_id: 4, film_number: 'F-35-0003', film_type: '35mm', capacity: 1000, pages_used: 1000, pages_remaining: 0, status: 'Complete', project_id: 3, creation_date: '2023-03-16', source_temp_roll_id: null, created_temp_roll_id: 2 },
                { roll_id: 5, film_number: 'F-16-0002', film_type: '16mm', capacity: 2500, pages_used: 327, pages_remaining: 2173, status: 'In Use', project_id: 4, creation_date: '2023-04-10', source_temp_roll_id: null, created_temp_roll_id: null }
            ],
            tempRolls: [
                { temp_roll_id: 1, film_type: '35mm', capacity: 1000, usable_capacity: 450, status: 'Available', creation_date: '2023-03-15', source_roll_id: 3, used_by_roll_id: null },
                { temp_roll_id: 2, film_type: '35mm', capacity: 1000, usable_capacity: 500, status: 'Used', creation_date: '2023-03-16', source_roll_id: 4, used_by_roll_id: 6 },
                { temp_roll_id: 3, film_type: '16mm', capacity: 2500, usable_capacity: 1200, status: 'Available', creation_date: '2023-05-25', source_roll_id: null, used_by_roll_id: null }
            ],
            documents: [
                { document_id: 1, document_name: 'Financial Report Q1 2023', com_id: 'COM-001', roll_id: 1, page_range_start: 1, page_range_end: 45, is_oversized: false, filepath: '/archives/doc/001/report.pdf', blip: 'B001', blipend: 'B045', blip_type: '16mm' },
                { document_id: 2, document_name: 'Financial Report Q2 2023', com_id: 'COM-002', roll_id: 1, page_range_start: 46, page_range_end: 92, is_oversized: false, filepath: '/archives/doc/001/report_q2.pdf', blip: 'B046', blipend: 'B092', blip_type: '16mm' },
                { document_id: 3, document_name: 'Historical Manuscript Vol. 1', com_id: 'COM-003', roll_id: 2, page_range_start: 1, page_range_end: 210, is_oversized: true, filepath: '/archives/book/002/vol1.pdf', blip: 'B001', blipend: 'B210', blip_type: '35mm' },
                { document_id: 4, document_name: 'Newspaper Collection Part 1', com_id: 'COM-004', roll_id: 3, page_range_start: 1, page_range_end: 500, is_oversized: true, filepath: '/archives/news/003/part1.pdf', blip: 'B001', blipend: 'B500', blip_type: '35mm' },
                { document_id: 5, document_name: 'Newspaper Collection Part 2', com_id: 'COM-005', roll_id: 4, page_range_start: 501, page_range_end: 1000, is_oversized: true, filepath: '/archives/news/003/part2.pdf', blip: 'B501', blipend: 'B1000', blip_type: '35mm' }
            ]
        };
        
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
                        <option value="oversized">Oversized</option>
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
                                    <th>ID</th>
                                    <th>Archive ID</th>
                                    <th>Location</th>
                                    <th>Document Type</th>
                                    <th>Total Pages</th>
                                    <th>Date Created</th>
                                    <th>Actions</th>
                                `;
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
                        function updateResults(entity, isReset = false) {
                            const tableBody = document.getElementById('results-body');
                            const cardsContainer = document.getElementById('results-cards');
                            const resultCount = document.getElementById('result-count');
                            
                            // Get data for the selected entity
                            let data;
                            switch(entity) {
                                case 'projects':
                                    data = mockData.projects;
                                    break;
                                case 'rolls':
                                    data = mockData.rolls;
                                    break;
                                case 'documents':
                                    data = mockData.documents;
                                    break;
                                case 'temp-rolls':
                                    data = mockData.tempRolls;
                                    break;
                                default:
                                    data = [];
                            }
                            
                            // Apply filters if not resetting
                            if (!isReset) {
                                // Get search term
                                const searchTerm = document.getElementById('search-term').value.toLowerCase();
                                if (searchTerm) {
                                    data = data.filter(item => {
                                        // Search in all string properties
                                        return Object.values(item).some(val => 
                                            typeof val === 'string' && val.toLowerCase().includes(searchTerm)
                                        );
                                    });
                                }
                                
                                // Apply date range if specified
                                const dateFrom = document.getElementById('date-from').value;
                                const dateTo = document.getElementById('date-to').value;
                                
                                if (dateFrom || dateTo) {
                                    data = data.filter(item => {
                                        const itemDate = entity === 'projects' ? item.date_created : 
                                                        (entity === 'temp-rolls' ? item.creation_date : item.creation_date);
                                        
                                        if (dateFrom && dateTo) {
                                            return itemDate >= dateFrom && itemDate <= dateTo;
                                        } else if (dateFrom) {
                                            return itemDate >= dateFrom;
                                        } else {
                                            return itemDate <= dateTo;
                                        }
                                    });
                                }
                                
                                // Apply entity-specific filters
                                if (entity === 'projects') {
                                    const docType = document.getElementById('doc-type').value;
                                    const location = document.getElementById('location').value;
                                    
                                    if (docType) {
                                        data = data.filter(item => item.doc_type === docType);
                                    }
                                    
                                    if (location) {
                                        data = data.filter(item => item.location === location);
                                    }
                                } 
                                else if (entity === 'rolls') {
                                    const filmType = document.getElementById('film-type').value;
                                    const status = document.getElementById('roll-status').value;
                                    
                                    if (filmType) {
                                        data = data.filter(item => item.film_type === filmType);
                                    }
                                    
                                    if (status) {
                                        data = data.filter(item => item.status === status);
                                    }
                                }
                                else if (entity === 'documents') {
                                    const oversized = document.getElementById('oversized').value;
                                    const blipType = document.getElementById('blip-type').value;
                                    
                                    if (oversized) {
                                        data = data.filter(item => item.is_oversized.toString() === oversized);
                                    }
                                    
                                    if (blipType) {
                                        data = data.filter(item => item.blip_type === blipType);
                                    }
                                }
                                else if (entity === 'temp-rolls') {
                                    const filmType = document.getElementById('temp-film-type').value;
                                    const status = document.getElementById('temp-roll-status').value;
                                    
                                    if (filmType) {
                                        data = data.filter(item => item.film_type === filmType);
                                    }
                                    
                                    if (status) {
                                        data = data.filter(item => item.status === status);
                                    }
                                }
                                
                                // Apply advanced filters
                                if (document.getElementById('advanced-filters').classList.contains('visible')) {
                                    // Get filter conditions
                                    const conditions = Array.from(document.querySelectorAll('.filter-condition')).map(condition => {
                                        return {
                                            field: condition.querySelector('.condition-field').value,
                                            operator: condition.querySelector('.condition-operator').value,
                                            value: condition.querySelector('.condition-value').value
                                        };
                                    }).filter(condition => condition.field && condition.value);
                                    
                                    // Get join type
                                    const joinType = document.querySelector('input[name="join-type"]:checked').value;
                                    
                                    // Apply conditions
                                    if (conditions.length > 0) {
                                        data = data.filter(item => {
                                            const results = conditions.map(condition => {
                                                const itemValue = item[condition.field];
                                                
                                                switch(condition.operator) {
                                                    case 'equals':
                                                        return itemValue == condition.value;
                                                    case 'not_equals':
                                                        return itemValue != condition.value;
                                                    case 'greater_than':
                                                        return Number(itemValue) > Number(condition.value);
                                                    case 'less_than':
                                                        return Number(itemValue) < Number(condition.value);
                                                    case 'contains':
                                                        return String(itemValue).toLowerCase().includes(condition.value.toLowerCase());
                                                    case 'starts_with':
                                                        return String(itemValue).toLowerCase().startsWith(condition.value.toLowerCase());
                                                    case 'ends_with':
                                                        return String(itemValue).toLowerCase().endsWith(condition.value.toLowerCase());
                                                    default:
                                                        return true;
                                                }
                                            });
                                            
                                            return joinType === 'AND' ? results.every(Boolean) : results.some(Boolean);
                                        });
                                    }
                                    
                                    // Check for custom SQL (in a real application, this would be sent to the server)
                                    const sqlQuery = document.getElementById('sql-query').value.trim();
                                    if (sqlQuery) {
                                        console.log("SQL Query:", sqlQuery);
                                        // In a real app, this would be sent to the server for execution
                                    }
                                }
                            }
                            
                            // Sort data
                            const sortField = document.getElementById('sort-field').value;
                            const sortOrder = document.getElementById('sort-order').value;
                            
                            data.sort((a, b) => {
                                let fieldA, fieldB;
                                
                                // Map the sort field to actual property
                                switch(sortField) {
                                    case 'id':
                                        fieldA = entity === 'projects' ? a.project_id : 
                                                (entity === 'rolls' ? a.roll_id : 
                                                (entity === 'documents' ? a.document_id : a.temp_roll_id));
                                        fieldB = entity === 'projects' ? b.project_id : 
                                                (entity === 'rolls' ? b.roll_id : 
                                                (entity === 'documents' ? b.document_id : b.temp_roll_id));
                                        break;
                                    case 'created':
                                        fieldA = entity === 'projects' ? a.date_created : a.creation_date;
                                        fieldB = entity === 'projects' ? b.date_created : b.creation_date;
                                        break;
                                    case 'name':
                                        fieldA = entity === 'projects' ? a.folderName : 
                                                (entity === 'rolls' ? a.film_number : 
                                                (entity === 'documents' ? a.document_name : a.film_type));
                                        fieldB = entity === 'projects' ? b.folderName : 
                                                (entity === 'rolls' ? b.film_number : 
                                                (entity === 'documents' ? b.document_name : b.film_type));
                                        break;
                                    default:
                                        fieldA = a.id;
                                        fieldB = b.id;
                                }
                                
                                // Compare based on sort order
                                if (sortOrder === 'asc') {
                                    return fieldA > fieldB ? 1 : -1;
                                } else {
                                    return fieldA < fieldB ? 1 : -1;
                                }
                            });
                            
                            // Update count
                            resultCount.textContent = `(${data.length})`;
                            
                            // Pagination
                            const pageSize = parseInt(document.getElementById('page-size').value);
                            const totalPages = Math.ceil(data.length / pageSize);
                            let currentPage = 1;
                            
                            updatePageNumbers(totalPages, currentPage);
                            updatePageNumbersCards(totalPages, currentPage);
                            
                            // Enable/disable pagination buttons
                            document.getElementById('prev-page').disabled = currentPage === 1;
                            document.getElementById('next-page').disabled = currentPage === totalPages || totalPages === 0;
                            document.getElementById('prev-page-cards').disabled = currentPage === 1;
                            document.getElementById('next-page-cards').disabled = currentPage === totalPages || totalPages === 0;
                            
                            // Add pagination event listeners
                            document.getElementById('prev-page').onclick = function() {
                                if (currentPage > 1) {
                                    currentPage--;
                                    renderPage(data, currentPage, pageSize, entity);
                                    updatePageNumbers(totalPages, currentPage);
                                }
                            };
                            
                            document.getElementById('next-page').onclick = function() {
                                if (currentPage < totalPages) {
                                    currentPage++;
                                    renderPage(data, currentPage, pageSize, entity);
                                    updatePageNumbers(totalPages, currentPage);
                                }
                            };
                            
                            document.getElementById('prev-page-cards').onclick = function() {
                                if (currentPage > 1) {
                                    currentPage--;
                                    renderPageCards(data, currentPage, pageSize, entity);
                                    updatePageNumbersCards(totalPages, currentPage);
                                }
                            };
                            
                            document.getElementById('next-page-cards').onclick = function() {
                                if (currentPage < totalPages) {
                                    currentPage++;
                                    renderPageCards(data, currentPage, pageSize, entity);
                                    updatePageNumbersCards(totalPages, currentPage);
                                }
                            };
                            
                            // Initial render
                            renderPage(data, currentPage, pageSize, entity);
                            renderPageCards(data, currentPage, pageSize, entity);
                            
                            // Update chart if visualization is active
                            if (document.getElementById('visualization-view').classList.contains('active')) {
                                initializeChart(data, entity);
                            }
                        }
                        
                        // Render table page
                        function renderPage(data, page, pageSize, entity) {
                            const tableBody = document.getElementById('results-body');
                            const start = (page - 1) * pageSize;
                            const end = start + pageSize;
                            const paginatedData = data.slice(start, end);
                            
                            // Clear table
                            tableBody.innerHTML = '';
                            
                            // If no data, show empty message
                            if (paginatedData.length === 0) {
                                tableBody.innerHTML = `
                                    <tr class="empty-row">
                                        <td colspan="7">No data available. Try adjusting your filters.</td>
                                    </tr>
                                `;
                                return;
                            }
                            
                            // Add rows
                            paginatedData.forEach(item => {
                                const row = document.createElement('tr');
                                
                                if (entity === 'projects') {
                                    row.innerHTML = `
                                        <td>${item.project_id}</td>
                                        <td>${item.archive_id}</td>
                                        <td>${item.location}</td>
                                        <td>${item.doc_type}</td>
                                        <td>${item.total_pages}</td>
                                        <td>${item.date_created}</td>
                                        <td>
                                            <button class="action-icon view-details" data-id="${item.project_id}" data-type="project">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="action-icon edit-item" data-id="${item.project_id}" data-type="project">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        </td>
                                    `;
                                } else if (entity === 'rolls') {
                                    row.innerHTML = `
                                        <td>${item.roll_id}</td>
                                        <td>${item.film_number}</td>
                                        <td>${item.film_type}</td>
                                        <td>${item.pages_used}</td>
                                        <td>${item.pages_remaining}</td>
                                        <td><span class="status-badge ${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span></td>
                                        <td>
                                            <button class="action-icon view-details" data-id="${item.roll_id}" data-type="roll">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="action-icon edit-item" data-id="${item.roll_id}" data-type="roll">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        </td>
                                    `;
                                } else if (entity === 'documents') {
                                    row.innerHTML = `
                                        <td>${item.document_id}</td>
                                        <td>${item.document_name}</td>
                                        <td>${item.com_id}</td>
                                        <td>${item.roll_id}</td>
                                        <td>${item.page_range_start}-${item.page_range_end}</td>
                                        <td>${item.blip} - ${item.blipend}</td>
                                        <td>
                                            <button class="action-icon view-details" data-id="${item.document_id}" data-type="document">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="action-icon edit-item" data-id="${item.document_id}" data-type="document">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        </td>
                                    `;
                                } else if (entity === 'temp-rolls') {
                                    row.innerHTML = `
                                        <td>${item.temp_roll_id}</td>
                                        <td>${item.film_type}</td>
                                        <td>${item.capacity}</td>
                                        <td>${item.usable_capacity}</td>
                                        <td><span class="status-badge ${item.status.toLowerCase()}">${item.status}</span></td>
                                        <td>${item.creation_date}</td>
                                        <td>
                                            <button class="action-icon view-details" data-id="${item.temp_roll_id}" data-type="temp-roll">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="action-icon edit-item" data-id="${item.temp_roll_id}" data-type="temp-roll">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        </td>
                                    `;
                                }
                                
                                tableBody.appendChild(row);
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
                        }
                        
                        // Render cards page
                        function renderPageCards(data, page, pageSize, entity) {
                            const cardsContainer = document.getElementById('results-cards');
                            const start = (page - 1) * pageSize;
                            const end = start + pageSize;
                            const paginatedData = data.slice(start, end);
                            
                            // Clear container
                            cardsContainer.innerHTML = '';
                            
                            // If no data, show empty message
                            if (paginatedData.length === 0) {
                                cardsContainer.innerHTML = `
                                    <div class="empty-state">
                                        <i class="fas fa-search"></i>
                                        <p>No data available. Try adjusting your filters.</p>
                                    </div>
                                `;
                                return;
                            }
                            
                            // Add cards
                            paginatedData.forEach(item => {
                                const card = document.createElement('div');
                                card.className = 'item-card';
                                
                                if (entity === 'projects') {
                                    card.innerHTML = `
                                        <div class="card-header">
                                            <h3>${item.folderName}</h3>
                                            <span class="card-id">${item.archive_id}</span>
                                        </div>
                                        <div class="card-body">
                                            <div class="card-property">
                                                <span class="property-label">Type:</span>
                                                <span class="property-value">${item.doc_type}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Location:</span>
                                                <span class="property-value">${item.location}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Pages:</span>
                                                <span class="property-value">${item.total_pages}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Date:</span>
                                                <span class="property-value">${item.date_created}</span>
                                            </div>
                                        </div>
                                        <div class="card-footer">
                                            <button class="card-button view-details" data-id="${item.project_id}" data-type="project">
                                                <i class="fas fa-eye"></i> View Details
                                            </button>
                                            <button class="card-button edit-item" data-id="${item.project_id}" data-type="project">
                                                <i class="fas fa-edit"></i> Edit
                                            </button>
                                        </div>
                                    `;
                                } else if (entity === 'rolls') {
                                    card.innerHTML = `
                                        <div class="card-header">
                                            <h3>${item.film_number}</h3>
                                            <span class="status-badge ${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span>
                                        </div>
                                        <div class="card-body">
                                            <div class="card-property">
                                                <span class="property-label">Film Type:</span>
                                                <span class="property-value">${item.film_type}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Project ID:</span>
                                                <span class="property-value">${item.project_id}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Utilization:</span>
                                                <span class="property-value">${Math.round((item.pages_used / item.capacity) * 100)}%</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Date:</span>
                                                <span class="property-value">${item.creation_date}</span>
                                            </div>
                                        </div>
                                        <div class="card-footer">
                                            <button class="card-button view-details" data-id="${item.roll_id}" data-type="roll">
                                                <i class="fas fa-eye"></i> View Details
                                            </button>
                                            <button class="card-button edit-item" data-id="${item.roll_id}" data-type="roll">
                                                <i class="fas fa-edit"></i> Edit
                                            </button>
                                        </div>
                                    `;
                                } else if (entity === 'documents') {
                                    card.innerHTML = `
                                        <div class="card-header">
                                            <h3>${item.document_name}</h3>
                                            <span class="card-id">${item.com_id}</span>
                                        </div>
                                        <div class="card-body">
                                            <div class="card-property">
                                                <span class="property-label">Roll ID:</span>
                                                <span class="property-value">${item.roll_id}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Pages:</span>
                                                <span class="property-value">${item.page_range_start}-${item.page_range_end}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Blip:</span>
                                                <span class="property-value">${item.blip} - ${item.blipend}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Oversized:</span>
                                                <span class="property-value">${item.is_oversized ? 'Yes' : 'No'}</span>
                                            </div>
                                        </div>
                                        <div class="card-footer">
                                            <button class="card-button view-details" data-id="${item.document_id}" data-type="document">
                                                <i class="fas fa-eye"></i> View Details
                                            </button>
                                            <button class="card-button edit-item" data-id="${item.document_id}" data-type="document">
                                                <i class="fas fa-edit"></i> Edit
                                            </button>
                                        </div>
                                    `;
                                } else if (entity === 'temp-rolls') {
                                    card.innerHTML = `
                                        <div class="card-header">
                                            <h3>Temp Roll ${item.temp_roll_id}</h3>
                                            <span class="status-badge ${item.status.toLowerCase()}">${item.status}</span>
                                        </div>
                                        <div class="card-body">
                                            <div class="card-property">
                                                <span class="property-label">Film Type:</span>
                                                <span class="property-value">${item.film_type}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Capacity:</span>
                                                <span class="property-value">${item.capacity}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Usable:</span>
                                                <span class="property-value">${item.usable_capacity}</span>
                                            </div>
                                            <div class="card-property">
                                                <span class="property-label">Date:</span>
                                                <span class="property-value">${item.creation_date}</span>
                                            </div>
                                        </div>
                                        <div class="card-footer">
                                            <button class="card-button view-details" data-id="${item.temp_roll_id}" data-type="temp-roll">
                                                <i class="fas fa-eye"></i> View Details
                                            </button>
                                            <button class="card-button edit-item" data-id="${item.temp_roll_id}" data-type="temp-roll">
                                                <i class="fas fa-edit"></i> Edit
                                            </button>
                                        </div>
                                    `;
                                }
                                
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
                                    goToPage(1);
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
                                    goToPage(i);
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
                                    goToPage(totalPages);
                                });
                                pageNumbers.appendChild(pageSpan);
                            }
                            
                            function goToPage(page) {
                                if (page !== currentPage) {
                                    const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                                    const pageSize = parseInt(document.getElementById('page-size').value);
                                    
                                    let data;
                                    switch(entity) {
                                        case 'projects':
                                            data = mockData.projects;
                                            break;
                                        case 'rolls':
                                            data = mockData.rolls;
                                            break;
                                        case 'documents':
                                            data = mockData.documents;
                                            break;
                                        case 'temp-rolls':
                                            data = mockData.tempRolls;
                                            break;
                                        default:
                                            data = [];
                                    }
                                    
                                    renderPage(data, page, pageSize, entity);
                                    updatePageNumbers(totalPages, page);
                                    
                                    // Update prev/next buttons
                                    document.getElementById('prev-page').disabled = page === 1;
                                    document.getElementById('next-page').disabled = page === totalPages;
                                }
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
                                    goToPage(1);
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
                                    goToPage(i);
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
                                    goToPage(totalPages);
                                });
                                pageNumbers.appendChild(pageSpan);
                            }
                            
                            function goToPage(page) {
                                if (page !== currentPage) {
                                    const entity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                                    const pageSize = parseInt(document.getElementById('page-size').value);
                                    
                                    let data;
                                    switch(entity) {
                                        case 'projects':
                                            data = mockData.projects;
                                            break;
                                        case 'rolls':
                                            data = mockData.rolls;
                                            break;
                                        case 'documents':
                                            data = mockData.documents;
                                            break;
                                        case 'temp-rolls':
                                            data = mockData.tempRolls;
                                            break;
                                        default:
                                            data = [];
                                    }
                                    
                                    renderPageCards(data, page, pageSize, entity);
                                    updatePageNumbersCards(totalPages, page);
                                    
                                    // Update prev/next buttons
                                    document.getElementById('prev-page-cards').disabled = page === 1;
                                    document.getElementById('next-page-cards').disabled = page === totalPages;
                                }
                            }
                        }
                        
                        // Show item details
                        function showItemDetails(id, type) {
                            const modal = document.getElementById('detail-modal');
                            const modalTitle = document.getElementById('modal-title');
                            const detailProperties = document.querySelector('.detail-properties');
                            const relatedItems = document.querySelector('.related-items');
                            const historyTimeline = document.querySelector('.history-timeline');
                            
                            // Set modal title based on item type
                            let item;
                            
                            if (type === 'project') {
                                modalTitle.textContent = 'Project Details';
                                item = mockData.projects.find(p => p.project_id == id);
                                
                                // Populate details tab
                                detailProperties.innerHTML = `
                                    <div class="detail-property">
                                        <span class="detail-label">Project ID:</span>
                                        <span class="detail-value">${item.project_id}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Archive ID:</span>
                                        <span class="detail-value">${item.archive_id}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Location:</span>
                                        <span class="detail-value">${item.location}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Document Type:</span>
                                        <span class="detail-value">${item.doc_type}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Path:</span>
                                        <span class="detail-value">${item.path}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Folder Name:</span>
                                        <span class="detail-value">${item.folderName}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Oversized:</span>
                                        <span class="detail-value">${item.oversized ? 'Yes' : 'No'}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Total Pages:</span>
                                        <span class="detail-value">${item.total_pages}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Pages with References:</span>
                                        <span class="detail-value">${item.total_pages_with_refs}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Date Created:</span>
                                        <span class="detail-value">${item.date_created}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Data Directory:</span>
                                        <span class="detail-value">${item.data_dir}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Index Path:</span>
                                        <span class="detail-value">${item.index_path}</span>
                                    </div>
                                `;
                                
                                // Find related rolls
                                const relatedRolls = mockData.rolls.filter(r => r.project_id == id);
                                
                                // Populate related items tab
                                relatedItems.innerHTML = '<h3>Related Rolls</h3>';
                                
                                if (relatedRolls.length > 0) {
                                    const rollsList = document.createElement('ul');
                                    rollsList.className = 'related-list';
                                    
                                    relatedRolls.forEach(roll => {
                                        const rollItem = document.createElement('li');
                                        rollItem.className = 'related-item';
                                        rollItem.innerHTML = `
                                            <span class="related-item-id">Roll #${roll.roll_id}</span>
                                            <span class="related-item-name">${roll.film_number}</span>
                                            <span class="related-item-status">${roll.status}</span>
                                            <button class="view-related" data-id="${roll.roll_id}" data-type="roll">View</button>
                                        `;
                                        rollsList.appendChild(rollItem);
                                    });
                                    
                                    relatedItems.appendChild(rollsList);
                                } else {
                                    relatedItems.innerHTML += '<p>No related rolls found.</p>';
                                }
                                
                            } else if (type === 'roll') {
                                modalTitle.textContent = 'Roll Details';
                                item = mockData.rolls.find(r => r.roll_id == id);
                                
                                // Populate details tab
                                detailProperties.innerHTML = `
                                    <div class="detail-property">
                                        <span class="detail-label">Roll ID:</span>
                                        <span class="detail-value">${item.roll_id}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Film Number:</span>
                                        <span class="detail-value">${item.film_number}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Film Type:</span>
                                        <span class="detail-value">${item.film_type}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Capacity:</span>
                                        <span class="detail-value">${item.capacity}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Pages Used:</span>
                                        <span class="detail-value">${item.pages_used}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Pages Remaining:</span>
                                        <span class="detail-value">${item.pages_remaining}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Status:</span>
                                        <span class="detail-value status-badge ${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Project:</span>
                                        <span class="detail-value">
                                            <a href="#" class="detail-link" data-id="${item.project_id}" data-type="project">Project #${item.project_id}</a>
                                        </span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Creation Date:</span>
                                        <span class="detail-value">${item.creation_date}</span>
                                    </div>
                                `;
                                
                                // Find related documents
                                const relatedDocs = mockData.documents.filter(d => d.roll_id == id);
                                const relatedTempRolls = mockData.tempRolls.filter(t => t.source_roll_id == id);
                                
                                // Populate related items tab
                                relatedItems.innerHTML = '';
                                
                                if (relatedDocs.length > 0) {
                                    relatedItems.innerHTML += '<h3>Related Documents</h3>';
                                    const docsList = document.createElement('ul');
                                    docsList.className = 'related-list';
                                    
                                    relatedDocs.forEach(doc => {
                                        const docItem = document.createElement('li');
                                        docItem.className = 'related-item';
                                        docItem.innerHTML = `
                                            <span class="related-item-id">Doc #${doc.document_id}</span>
                                            <span class="related-item-name">${doc.document_name}</span>
                                            <span class="related-item-meta">Pages ${doc.page_range_start}-${doc.page_range_end}</span>
                                            <button class="view-related" data-id="${doc.document_id}" data-type="document">View</button>
                                        `;
                                        docsList.appendChild(docItem);
                                    });
                                    
                                    relatedItems.appendChild(docsList);
                                } else {
                                    relatedItems.innerHTML += '<p>No related documents found.</p>';
                                }
                                
                                if (relatedTempRolls.length > 0) {
                                    relatedItems.innerHTML += '<h3>Created Temp Rolls</h3>';
                                    const tempRollsList = document.createElement('ul');
                                    tempRollsList.className = 'related-list';
                                    
                                    relatedTempRolls.forEach(tempRoll => {
                                        const tempRollItem = document.createElement('li');
                                        tempRollItem.className = 'related-item';
                                        tempRollItem.innerHTML = `
                                            <span class="related-item-id">Temp Roll #${tempRoll.temp_roll_id}</span>
                                            <span class="related-item-name">${tempRoll.film_type}</span>
                                            <span class="related-item-meta">Capacity: ${tempRoll.usable_capacity}</span>
                                            <button class="view-related" data-id="${tempRoll.temp_roll_id}" data-type="temp-roll">View</button>
                                        `;
                                        tempRollsList.appendChild(tempRollItem);
                                    });
                                    
                                    relatedItems.appendChild(tempRollsList);
                                }
                                
                            } else if (type === 'document') {
                                modalTitle.textContent = 'Document Details';
                                item = mockData.documents.find(d => d.document_id == id);
                                
                                // Populate details tab
                                detailProperties.innerHTML = `
                                    <div class="detail-property">
                                        <span class="detail-label">Document ID:</span>
                                        <span class="detail-value">${item.document_id}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Document Name:</span>
                                        <span class="detail-value">${item.document_name}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">COM ID:</span>
                                        <span class="detail-value">${item.com_id}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Roll:</span>
                                        <span class="detail-value">
                                            <a href="#" class="detail-link" data-id="${item.roll_id}" data-type="roll">Roll #${item.roll_id}</a>
                                        </span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Page Range:</span>
                                        <span class="detail-value">${item.page_range_start} - ${item.page_range_end}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Total Pages:</span>
                                        <span class="detail-value">${item.page_range_end - item.page_range_start + 1}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Is Oversized:</span>
                                        <span class="detail-value">${item.is_oversized ? 'Yes' : 'No'}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Filepath:</span>
                                        <span class="detail-value">${item.filepath}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Blip Range:</span>
                                        <span class="detail-value">${item.blip} - ${item.blipend}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Blip Type:</span>
                                        <span class="detail-value">${item.blip_type}</span>
                                    </div>
                                `;
                                
                                // Find related items (the roll this document is on)
                                const roll = mockData.rolls.find(r => r.roll_id == item.roll_id);
                                
                                // Populate related items tab
                                relatedItems.innerHTML = '<h3>Related Roll</h3>';
                                
                                if (roll) {
                                    const rollItem = document.createElement('div');
                                    rollItem.className = 'related-item';
                                    rollItem.innerHTML = `
                                        <span class="related-item-id">Roll #${roll.roll_id}</span>
                                        <span class="related-item-name">${roll.film_number}</span>
                                        <span class="related-item-status">${roll.status}</span>
                                        <button class="view-related" data-id="${roll.roll_id}" data-type="roll">View</button>
                                    `;
                                    relatedItems.appendChild(rollItem);
                                } else {
                                    relatedItems.innerHTML += '<p>No related roll found.</p>';
                                }
                                
                            } else if (type === 'temp-roll') {
                                modalTitle.textContent = 'Temporary Roll Details';
                                item = mockData.tempRolls.find(t => t.temp_roll_id == id);
                                
                                // Populate details tab
                                detailProperties.innerHTML = `
                                    <div class="detail-property">
                                        <span class="detail-label">Temp Roll ID:</span>
                                        <span class="detail-value">${item.temp_roll_id}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Film Type:</span>
                                        <span class="detail-value">${item.film_type}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Capacity:</span>
                                        <span class="detail-value">${item.capacity}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Usable Capacity:</span>
                                        <span class="detail-value">${item.usable_capacity}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Status:</span>
                                        <span class="detail-value status-badge ${item.status.toLowerCase()}">${item.status}</span>
                                    </div>
                                    <div class="detail-property">
                                        <span class="detail-label">Creation Date:</span>
                                        <span class="detail-value">${item.creation_date}</span>
                                    </div>
                                `;
                                
                                // Find related source roll and used_by roll
                                const sourceRoll = item.source_roll_id ? mockData.rolls.find(r => r.roll_id == item.source_roll_id) : null;
                                const usedByRoll = item.used_by_roll_id ? mockData.rolls.find(r => r.roll_id == item.used_by_roll_id) : null;
                                
                                // Populate related items tab
                                relatedItems.innerHTML = '';
                                
                                if (sourceRoll) {
                                    relatedItems.innerHTML += '<h3>Source Roll</h3>';
                                    const sourceItem = document.createElement('div');
                                    sourceItem.className = 'related-item';
                                    sourceItem.innerHTML = `
                                        <span class="related-item-id">Roll #${sourceRoll.roll_id}</span>
                                        <span class="related-item-name">${sourceRoll.film_number}</span>
                                        <span class="related-item-status">${sourceRoll.status}</span>
                                        <button class="view-related" data-id="${sourceRoll.roll_id}" data-type="roll">View</button>
                                    `;
                                    relatedItems.appendChild(sourceItem);
                                }
                                
                                if (usedByRoll) {
                                    relatedItems.innerHTML += '<h3>Used By Roll</h3>';
                                    const usedByItem = document.createElement('div');
                                    usedByItem.className = 'related-item';
                                    usedByItem.innerHTML = `
                                        <span class="related-item-id">Roll #${usedByRoll.roll_id}</span>
                                        <span class="related-item-name">${usedByRoll.film_number}</span>
                                        <span class="related-item-status">${usedByRoll.status}</span>
                                        <button class="view-related" data-id="${usedByRoll.roll_id}" data-type="roll">View</button>
                                    `;
                                    relatedItems.appendChild(usedByItem);
                                }
                                
                                if (!sourceRoll && !usedByRoll) {
                                    relatedItems.innerHTML += '<p>No related rolls found.</p>';
                                }
                            }
                            
                            // Populate history tab (mock data)
                            historyTimeline.innerHTML = `
                                <div class="timeline-item">
                                    <div class="timeline-date">2023-05-01 09:15:23</div>
                                    <div class="timeline-content">
                                        <div class="timeline-title">Created</div>
                                        <div class="timeline-description">Item was created by user admin</div>
                                    </div>
                                </div>
                                <div class="timeline-item">
                                    <div class="timeline-date">2023-05-02 14:30:45</div>
                                    <div class="timeline-content">
                                        <div class="timeline-title">Modified</div>
                                        <div class="timeline-description">Metadata updated by user jsmith</div>
                                    </div>
                                </div>
                                <div class="timeline-item">
                                    <div class="timeline-date">2023-05-10 11:05:17</div>
                                    <div class="timeline-content">
                                        <div class="timeline-title">Processed</div>
                                        <div class="timeline-description">Item was processed by system</div>
                                    </div>
                                </div>
                            `;
                            
                            // Add event listeners to detail links
                            document.querySelectorAll('.detail-link').forEach(link => {
                                link.addEventListener('click', function(e) {
                                    e.preventDefault();
                                    showItemDetails(this.getAttribute('data-id'), this.getAttribute('data-type'));
                                });
                            });
                            
                            // Add event listeners to view related buttons
                            document.querySelectorAll('.view-related').forEach(button => {
                                button.addEventListener('click', function() {
                                    showItemDetails(this.getAttribute('data-id'), this.getAttribute('data-type'));
                                });
                            });
                            
                            // Show modal
                            modal.style.display = 'flex';
                            
                            // Tab functionality
                            const tabButtons = document.querySelectorAll('.tab-button');
                            const tabContents = document.querySelectorAll('.tab-content');
                            
                            tabButtons.forEach(button => {
                                button.addEventListener('click', function() {
                                    const tab = this.getAttribute('data-tab');
                                    
                                    // Deactivate all tabs
                                    tabButtons.forEach(btn => btn.classList.remove('active'));
                                    tabContents.forEach(content => content.classList.remove('active'));
                                    
                                    // Activate clicked tab
                                    this.classList.add('active');
                                    document.getElementById(`${tab}-tab`).classList.add('active');
                                });
                            });
                            
                            // Close modal functionality
                            const closeButtons = document.querySelectorAll('.close-modal');
                            closeButtons.forEach(button => {
                                button.addEventListener('click', function() {
                                    modal.style.display = 'none';
                                });
                            });
                            
                            // Close when clicking outside
                            window.addEventListener('click', function(event) {
                                if (event.target === modal) {
                                    modal.style.display = 'none';
                                }
                            });
                        }
                        
                        // Edit item (mock function)
                        function editItem(id, type) {
                            alert(`Editing ${type} with ID ${id}. This functionality would open an edit form.`);
                        }
                        
                        // Initialize chart
                        function initializeChart(data, entity) {
                            const chartType = document.getElementById('chart-type').value;
                            const xAxis = document.getElementById('x-axis').value;
                            const yAxis = document.getElementById('y-axis').value;
                            
                            // Use entity and filters data if not provided
                            if (!data) {
                                const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                                
                                switch(selectedEntity) {
                                    case 'projects':
                                        data = mockData.projects;
                                        break;
                                    case 'rolls':
                                        data = mockData.rolls;
                                        break;
                                    case 'documents':
                                        data = mockData.documents;
                                        break;
                                    case 'temp-rolls':
                                        data = mockData.tempRolls;
                                        break;
                                    default:
                                        data = [];
                                }
                                
                                entity = selectedEntity;
                            }
                            
                            // Prepare data for chart
                            const chartData = prepareChartData(data, entity, xAxis, yAxis);
                            
                            // Create or update chart
                            const chartCanvas = document.getElementById('results-chart');
                            let resultsChart = window.resultsChart;
                            
                            if (resultsChart) {
                                resultsChart.destroy();
                            }
                            
                            resultsChart = new Chart(chartCanvas, {
                                type: chartType,
                                data: {
                                    labels: chartData.labels,
                                    datasets: [{
                                        label: chartData.datasetLabel,
                                        data: chartData.values,
                                        backgroundColor: [
                                            'rgba(54, 162, 235, 0.5)',
                                            'rgba(255, 99, 132, 0.5)',
                                            'rgba(255, 206, 86, 0.5)',
                                            'rgba(75, 192, 192, 0.5)',
                                            'rgba(153, 102, 255, 0.5)'
                                        ],
                                        borderColor: [
                                            'rgba(54, 162, 235, 1)',
                                            'rgba(255, 99, 132, 1)',
                                            'rgba(255, 206, 86, 1)',
                                            'rgba(75, 192, 192, 1)',
                                            'rgba(153, 102, 255, 1)'
                                        ],
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true
                                        }
                                    }
                                }
                            });
                            
                            window.resultsChart = resultsChart;
                            
                            // Add event listeners to chart controls
                            document.getElementById('chart-type').addEventListener('change', function() {
                                initializeChart(data, entity);
                            });
                            
                            document.getElementById('x-axis').addEventListener('change', function() {
                                initializeChart(data, entity);
                            });
                            
                            document.getElementById('y-axis').addEventListener('change', function() {
                                initializeChart(data, entity);
                            });
                        }
                        
                        // Prepare data for charts
                        function prepareChartData(data, entity, xAxis, yAxis) {
                            const result = {
                                labels: [],
                                values: [],
                                datasetLabel: ''
                            };
                            
                            // Group data by x-axis
                            const groups = {};
                            
                            data.forEach(item => {
                                let xValue;
                                
                                // Get x-axis value based on the selected field
                                switch(xAxis) {
                                    case 'doc_type':
                                        xValue = entity === 'projects' ? item.doc_type : 'N/A';
                                        break;
                                    case 'location':
                                        xValue = entity === 'projects' ? item.location : 'N/A';
                                        break;
                                    case 'creation_date':
                                        // For simplicity, use just month and year
                                        const date = entity === 'projects' ? new Date(item.date_created) : new Date(item.creation_date);
                                        xValue = `${date.getMonth() + 1}/${date.getFullYear()}`;
                                        break;
                                    default:
                                        xValue = 'Other';
                                }
                                
                                // Initialize group if not exists
                                if (!groups[xValue]) {
                                    groups[xValue] = {
                                        count: 0,
                                        totalPages: 0,
                                        items: []
                                    };
                                }
                                
                                // Add to group
                                groups[xValue].count++;
                                groups[xValue].items.push(item);
                                
                                // Add pages if available
                                if (entity === 'projects' && item.total_pages) {
                                    groups[xValue].totalPages += item.total_pages;
                                } else if (entity === 'rolls' && item.pages_used) {
                                    groups[xValue].totalPages += item.pages_used;
                                } else if (entity === 'documents' && item.page_range_start && item.page_range_end) {
                                    groups[xValue].totalPages += (item.page_range_end - item.page_range_start + 1);
                                }
                            });
                            
                            // Prepare result based on y-axis
                            for (const [key, group] of Object.entries(groups)) {
                                result.labels.push(key);
                                
                                switch(yAxis) {
                                    case 'count':
                                        result.values.push(group.count);
                                        result.datasetLabel = 'Count';
                                        break;
                                    case 'total_pages':
                                        result.values.push(group.totalPages);
                                        result.datasetLabel = 'Total Pages';
                                        break;
                                    case 'avg_pages':
                                        result.values.push(group.totalPages / group.count);
                                        result.datasetLabel = 'Average Pages';
                                        break;
                                    default:
                                        result.values.push(group.count);
                                        result.datasetLabel = 'Count';
                                }
                            }
                            
                            return result;
                        }
                        
                        // Export functions (mock functionality)
                        document.getElementById('export-csv').addEventListener('click', function() {
                            alert('Exporting to CSV...');
                        });
                        
                        document.getElementById('export-excel').addEventListener('click', function() {
                            alert('Exporting to Excel...');
                        });
                        
                        document.getElementById('export-pdf').addEventListener('click', function() {
                            alert('Exporting to PDF...');
                        });
                        
                        document.getElementById('export-json').addEventListener('click', function() {
                            alert('Exporting to JSON...');
                        });
                        
                        // Initialize with projects selected
                        updateTableHeaders('projects');
                        updateResults('projects');
                    });