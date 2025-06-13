/**
 * explore_details.js - Support functions for explore page details
 * This script provides functions for viewing and editing item details
 */

// Show item details
async function showItemDetails(id, type) {
    const modal = document.getElementById('detail-modal');
    const modalTitle = document.getElementById('modal-title');
    const detailProperties = document.querySelector('.detail-properties');
    const relatedItems = document.querySelector('.related-items');
    const historyTimeline = document.querySelector('.history-timeline');
    
    // Show loading state
    detailProperties.innerHTML = '<div class="loading">Loading details...</div>';
    relatedItems.innerHTML = '<div class="loading">Loading related items...</div>';
    historyTimeline.innerHTML = '<div class="loading">Loading history...</div>';
    
    // Set modal title based on item type
    if (type === 'project') {
        modalTitle.textContent = 'Project Details';
        
        try {
            // Fetch the project details from API
            const dbService = new DatabaseService();
            const response = await dbService.getProject(id);
            const item = response.project;
            
            // Get status text and class
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
                    <span class="detail-value">${item.doc_type || 'N/A'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Path:</span>
                    <span class="detail-value">${item.project_path}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Folder Name:</span>
                    <span class="detail-value">${item.project_folder_name}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">PDF Folder:</span>
                    <span class="detail-value">${item.pdf_folder_path || 'Not Set'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Has PDF Folder:</span>
                    <span class="detail-value">${item.has_pdf_folder ? 'Yes' : 'No'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Oversized:</span>
                    <span class="detail-value">${item.has_oversized ? 'Yes' : 'No'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Total Pages:</span>
                    <span class="detail-value">${item.total_pages || 0}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Pages with References:</span>
                    <span class="detail-value">${item.total_pages_with_refs || 0}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Date Created:</span>
                    <span class="detail-value">${item.date_created}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Last Updated:</span>
                    <span class="detail-value">${item.updated_at || 'N/A'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Processing Complete:</span>
                    <span class="detail-value">${item.processing_complete ? 'Yes' : 'No'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Film Allocation Complete:</span>
                    <span class="detail-value">${item.film_allocation_complete ? 'Yes' : 'No'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Distribution Complete:</span>
                    <span class="detail-value">${item.distribution_complete ? 'Yes' : 'No'}</span>
                </div>
                <div class="detail-property">
                    <span class="detail-label">Retain Sources:</span>
                    <span class="detail-value">${item.retain_sources ? 'Yes' : 'No'}</span>
                </div>
            `;
            
            // Try to fetch related items
            try {
                const relatedRolls = await dbService.getProjectRolls(id);
                if (relatedRolls && relatedRolls.length > 0) {
                    let rollsHtml = '<h3>Rolls</h3><div class="related-list">';
                    relatedRolls.forEach(roll => {
                        rollsHtml += `
                            <div class="related-item">
                                <span class="related-item-id">${roll.roll_id}</span>
                                <span class="related-item-name">${roll.film_number || 'No Film Number'}</span>
                                <span class="related-item-meta">${roll.film_type} / ${roll.pages_used} pages</span>
                                <span class="status-badge ${roll.status}">${roll.status}</span>
                                <button class="view-related" data-id="${roll.roll_id}" data-type="roll">View</button>
                            </div>
                        `;
                    });
                    rollsHtml += '</div>';
                    relatedItems.innerHTML = rollsHtml;
                    
                    // Add event listeners to view roll buttons
                    document.querySelectorAll('.view-related').forEach(button => {
                        button.addEventListener('click', function() {
                            showItemDetails(this.getAttribute('data-id'), this.getAttribute('data-type'));
                        });
                    });
                } else {
                    relatedItems.innerHTML = `
                        <div class="empty-related">
                            <p>No rolls have been allocated to this project yet.</p>
                            <button id="allocate-films" class="primary-button" data-id="${id}">
                                <i class="fas fa-film"></i> Allocate Films
                            </button>
                        </div>
                    `;
                    
                    // Add event listener to allocate films button
                    document.getElementById('allocate-films').addEventListener('click', function() {
                        allocateFilms(this.getAttribute('data-id'));
                    });
                }
            } catch (error) {
                console.error("Error fetching related items:", error);
                relatedItems.innerHTML = `
                    <div class="error-message">
                        <p>Error loading related items: ${error.message}</p>
                    </div>
                `;
            }
            
            // Try to fetch project history
            try {
                const history = await dbService.getProjectHistory(id);
                if (history && history.length > 0) {
                    let historyHtml = '';
                    history.forEach(event => {
                        historyHtml += `
                            <div class="timeline-item">
                                <div class="timeline-date">${event.timestamp}</div>
                                <div class="timeline-content">
                                    <div class="timeline-title">${event.action}</div>
                                    <div class="timeline-description">${event.description}</div>
                                </div>
                            </div>
                        `;
                    });
                    historyTimeline.innerHTML = historyHtml;
                } else {
                    historyTimeline.innerHTML = `
                        <div class="timeline-item">
                            <div class="timeline-date">${item.date_created}</div>
                            <div class="timeline-content">
                                <div class="timeline-title">Created</div>
                                <div class="timeline-description">Project was created</div>
                            </div>
                        </div>
                        <div class="timeline-item">
                            <div class="timeline-date">${item.updated_at || item.date_created}</div>
                            <div class="timeline-content">
                                <div class="timeline-title">Last Modified</div>
                                <div class="timeline-description">Project was updated</div>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error("Error fetching project history:", error);
                historyTimeline.innerHTML = `
                    <div class="timeline-item">
                        <div class="timeline-date">${item.date_created}</div>
                        <div class="timeline-content">
                            <div class="timeline-title">Created</div>
                            <div class="timeline-description">Project was created</div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-date">${item.updated_at || item.date_created}</div>
                        <div class="timeline-content">
                            <div class="timeline-title">Last Modified</div>
                            <div class="timeline-description">Project was updated</div>
                        </div>
                    </div>
                `;
            }
            
            // Add process button if not already processed
            const modalFooter = document.querySelector('.modal-footer');
            if (!item.processing_complete) {
                if (!document.getElementById('process-project-btn')) {
                    const processButton = document.createElement('button');
                    processButton.id = 'process-project-btn';
                    processButton.className = 'primary-button';
                    processButton.innerHTML = '<i class="fas fa-cogs"></i> Process Project';
                    processButton.dataset.id = id;
                    
                    modalFooter.insertBefore(processButton, document.getElementById('edit-item'));
                    
                    processButton.addEventListener('click', function() {
                        processProject(this.dataset.id);
                        modal.style.display = 'none';
                    });
                }
            } else if (document.getElementById('process-project-btn')) {
                document.getElementById('process-project-btn').remove();
            }
            
            // Set edit button action
            document.getElementById('edit-item').onclick = () => {
                editItem(id, type);
                modal.style.display = 'none';
            };
            
        } catch (error) {
            console.error("Error fetching project details:", error);
            detailProperties.innerHTML = `<div class="error">Error loading project details: ${error.message}</div>`;
            relatedItems.innerHTML = '';
            historyTimeline.innerHTML = '';
        }
    } else {
        // Placeholder for other entity types
        detailProperties.innerHTML = `<div class="info">Details for ${type} #${id} will be available in future updates.</div>`;
        relatedItems.innerHTML = '';
        historyTimeline.innerHTML = '';
    }
    
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
}

// Process project from details view
async function processProject(id) {
    try {
        const confirmed = confirm(`Start processing for Project #${id}?`);
        if (confirmed) {
            const dbService = new DatabaseService();
            await dbService.processProject(id);
            alert("Project processing started successfully!");
            
            // Refresh data in the main view
            const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
            updateResults(selectedEntity);
        }
    } catch (error) {
        console.error("Error processing project:", error);
        alert(`Error processing project: ${error.message}`);
    }
}

// Allocate films to project
async function allocateFilms(id) {
    try {
        const confirmed = confirm(`Start film allocation for Project #${id}?`);
        if (confirmed) {
            const dbService = new DatabaseService();
            await dbService.allocateFilms(id);
            alert("Film allocation started successfully!");
            
            // Refresh data in the main view
            const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
            updateResults(selectedEntity);
            
            // Close the modal
            document.getElementById('detail-modal').style.display = 'none';
        }
    } catch (error) {
        console.error("Error allocating films:", error);
        alert(`Error allocating films: ${error.message}`);
    }
}

// Edit item
async function editItem(id, type) {
    // For this version, we'll use a simple prompt
    // In a future version, this would open a more complex form
    if (type === 'project') {
        try {
            const dbService = new DatabaseService();
            
            // Fetch current project data
            const response = await dbService.getProject(id);
            const project = response.project;
            
            // Create modal content for editing project
            const formHtml = `
                <form id="edit-project-form">
                    <div class="form-group">
                        <label for="archive_id">Archive ID:</label>
                        <input type="text" id="archive_id" value="${project.archive_id}" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="location">Location:</label>
                        <input type="text" id="location" value="${project.location}" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="doc_type">Document Type:</label>
                        <input type="text" id="doc_type" value="${project.doc_type || ''}" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="has_oversized">Has Oversized:</label>
                        <select id="has_oversized" class="form-control">
                            <option value="true" ${project.has_oversized ? 'selected' : ''}>Yes</option>
                            <option value="false" ${!project.has_oversized ? 'selected' : ''}>No</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="total_pages">Total Pages:</label>
                        <input type="number" id="total_pages" value="${project.total_pages || 0}" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="processing_complete">Processing Complete:</label>
                        <select id="processing_complete" class="form-control">
                            <option value="true" ${project.processing_complete ? 'selected' : ''}>Yes</option>
                            <option value="false" ${!project.processing_complete ? 'selected' : ''}>No</option>
                        </select>
                    </div>
                </form>
            `;
            
            // For this version, we'll use a simple prompt
            // In a future version, this would use a modal dialog with a proper form
            const confirmed = confirm("Edit Project #" + id + "?\n\nIn a future version, this will open a form dialog to edit the project.");
            
            if (confirmed) {
                try {
                    // For now, we'll just update one field as a test
                    const updateData = {
                        processing_complete: !project.processing_complete
                    };
                    
                    await dbService.updateProject(id, updateData);
                    
                    // Refresh data after update
                    alert("Project updated successfully!\n\nRefreshing data...");
                    const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                    updateResults(selectedEntity);
                    
                } catch (updateError) {
                    console.error("Error updating project:", updateError);
                    alert("Error updating project: " + updateError.message);
                }
            }
            
        } catch (error) {
            console.error("Error preparing to edit project:", error);
            alert("Error preparing to edit project: " + error.message);
        }
    } else {
        alert(`Editing ${type} with ID ${id} is not yet implemented.`);
    }
}

// Delete item
async function deleteItem(id, type) {
    if (type === 'project') {
        const confirmed = confirm(`Are you sure you want to delete Project #${id}? This action cannot be undone.`);
        
        if (confirmed) {
            try {
                const dbService = new DatabaseService();
                await dbService.deleteProject(id);
                
                // Refresh data after deletion
                alert("Project deleted successfully!");
                const selectedEntity = document.querySelector('.entity-option.selected').getAttribute('data-entity');
                updateResults(selectedEntity);
                
            } catch (error) {
                console.error("Error deleting project:", error);
                alert("Error deleting project: " + error.message);
            }
        }
    } else {
        alert(`Deleting ${type} with ID ${id} is not yet implemented.`);
    }
}

// Initialize modal handlers
function initializeModals() {
    // Close modal functionality
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.getElementById('detail-modal').style.display = 'none';
        });
    });
    
    // Close when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('detail-modal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Chart functions
function initializeChart(data, entity) {
    const chartType = document.getElementById('chart-type').value;
    const xAxis = document.getElementById('x-axis').value;
    const yAxis = document.getElementById('y-axis').value;
    
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
    
    if (!data || data.length === 0) {
        result.labels = ['No Data'];
        result.values = [0];
        result.datasetLabel = 'No Data Available';
        return result;
    }
    
    // Group data by x-axis
    const groups = {};
    
    data.forEach(item => {
        let xValue;
        
        // Get x-axis value based on the selected field
        switch(xAxis) {
            case 'doc_type':
                xValue = entity === 'projects' ? (item.doc_type || 'Unknown') : 'N/A';
                break;
            case 'location':
                xValue = entity === 'projects' ? item.location : 'N/A';
                break;
            case 'creation_date':
                // For simplicity, use just month and year
                const date = new Date(item.date_created);
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
        }
    });
    
    // Calculate average pages per group
    Object.keys(groups).forEach(key => {
        const group = groups[key];
        group.avgPages = group.items.length > 0 ? group.totalPages / group.items.length : 0;
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
                result.values.push(group.avgPages);
                result.datasetLabel = 'Average Pages';
                break;
            default:
                result.values.push(group.count);
                result.datasetLabel = 'Count';
        }
    }
    
    return result;
}

// Export data
function exportData(entity, format) {
    alert(`Exporting ${entity} data in ${format} format will be implemented in a future update.`);
} 