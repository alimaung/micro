/**
 * project-details.js - Project details functionality
 * Handles displaying and interacting with project details
 */

class ProjectDetails {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentProject = null;
        this.modal = null;
        this.modalTitle = null;
        this.detailProperties = null;
        this.relatedItems = null;
        this.historyTimeline = null;
    }

    /**
     * Initialize the project details module
     */
    initialize() {
        // Get modal elements
        this.modal = document.getElementById('detail-modal');
        this.modalTitle = document.getElementById('modal-title');
        this.detailProperties = document.querySelector('.detail-properties');
        this.relatedItems = document.querySelector('.related-items');
        this.historyTimeline = document.querySelector('.history-timeline');
        
        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Set up event listeners for project details
     */
    setupEventListeners() {
        // Listen for showProjectDetails events
        document.addEventListener('showProjectDetails', (event) => {
            const { projectId } = event.detail;
            this.showProjectDetails(projectId);
        });
        
        // Close modal buttons
        const closeButtons = document.querySelectorAll('.close-modal');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.modal.style.display = 'none';
            });
        });
        
        // Edit button
        document.getElementById('edit-item').addEventListener('click', () => {
            if (this.currentProject) {
                const editProjectEvent = new CustomEvent('editProject', {
                    detail: { projectId: this.currentProject.project_id }
                });
                document.dispatchEvent(editProjectEvent);
                this.modal.style.display = 'none';
            }
        });
        
        // Tab switching
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Remove active class from all tabs and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Add active class to clicked tab and corresponding content
                e.target.classList.add('active');
                const tabId = e.target.getAttribute('data-tab');
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
        
        // Delete modal event listeners
        const deleteModal = document.getElementById('delete-modal');
        if (deleteModal) {
            // Close delete modal buttons
            deleteModal.querySelectorAll('.close-modal').forEach(button => {
                button.addEventListener('click', () => {
                    deleteModal.style.display = 'none';
                });
            });
            
            // Close delete modal when clicking outside
            window.addEventListener('click', (e) => {
                if (e.target === deleteModal) {
                    deleteModal.style.display = 'none';
                }
            });
        }
    }

    /**
     * Show project details in modal
     * @param {string|number} projectId - ID of the project to display
     */
    async showProjectDetails(projectId) {
        // Set modal title
        this.modalTitle.textContent = 'Project Details';
        
        // Show loading state in all tabs
        this.detailProperties.innerHTML = '<div class="loading">Loading project details...</div>';
        this.relatedItems.innerHTML = '<div class="loading">Loading related items...</div>';
        this.historyTimeline.innerHTML = '<div class="loading">Loading history...</div>';
        
        // Display the modal
        this.modal.style.display = 'flex';
        
        try {
            // Fetch the project details from API
            const response = await this.dbService.getProject(projectId);
            
            // Handle different response structures
            let project;
            if (response.project) {
                // Response has a 'project' property
                project = response.project;
            } else if (response.id || response.project_id) {
                // Response is the project object directly
                project = response;
            } else {
                throw new Error('Invalid response structure: no project data found');
            }
            
            // Validate that we have a project object
            if (!project) {
                throw new Error('Project data is null or undefined');
            }
            
            console.log('Project data received:', project); // Debug log
            
            // Store current project
            this.currentProject = project;
            
            // Get status text and class
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
            
            // Populate details tab with enhanced information in a table format
            this.detailProperties.innerHTML = `
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Project ID</td>
                            <td>${project.project_id}</td>
                        </tr>
                        <tr>
                            <td>Archive ID</td>
                            <td>${project.archive_id}</td>
                        </tr>
                        <tr>
                            <td>Location</td>
                            <td>${project.location}</td>
                        </tr>
                        <tr>
                            <td>Document Type</td>
                            <td>${project.doc_type || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td>Status</td>
                            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                        </tr>
                        <tr>
                            <td>Project Path</td>
                            <td>${project.project_path}</td>
                        </tr>
                        <tr>
                            <td>Folder Name</td>
                            <td>${project.project_folder_name}</td>
                        </tr>
                        <tr>
                            <td>PDF Folder</td>
                            <td>${project.pdf_folder_path || 'Not Set'}</td>
                        </tr>
                        <tr>
                            <td>Has PDF Folder</td>
                            <td>${project.has_pdf_folder ? 'Yes' : 'No'}</td>
                        </tr>
                        <tr>
                            <td>Has Oversized</td>
                            <td>${project.has_oversized ? 'Yes' : 'No'}</td>
                        </tr>
                        <tr>
                            <td>Oversized Documents</td>
                            <td>${project.documents_with_oversized || 0}</td>
                        </tr>
                        <tr>
                            <td>Total Oversized Pages</td>
                            <td>${project.total_oversized || 0}</td>
                        </tr>
                        <tr>
                            <td>Total Pages</td>
                            <td>${project.total_pages || 0}</td>
                        </tr>
                        <tr>
                            <td>Pages with References</td>
                            <td>${project.total_pages_with_refs || 0}</td>
                        </tr>
                        <tr>
                            <td>Date Created</td>
                            <td>${project.date_created}</td>
                        </tr>
                        <tr>
                            <td>Last Updated</td>
                            <td>${project.updated_at || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td>Processing Complete</td>
                            <td>${project.processing_complete ? 'Yes' : 'No'}</td>
                        </tr>
                        <tr>
                            <td>Film Allocation Complete</td>
                            <td>${project.film_allocation_complete ? 'Yes' : 'No'}</td>
                        </tr>
                        <tr>
                            <td>Distribution Complete</td>
                            <td>${project.distribution_complete ? 'Yes' : 'No'}</td>
                        </tr>
                        <tr>
                            <td>Retain Sources</td>
                            <td>${project.retain_sources ? 'Yes' : 'No'}</td>
                        </tr>
                        <tr>
                            <td>Add to Database</td>
                            <td>${project.add_to_database ? 'Yes' : 'No'}</td>
                        </tr>
                    </tbody>
                </table>
            `;
            
            // Load related items (rolls and documents)
            this.loadRelatedItems(projectId);
            
            // Load project history
            this.loadProjectHistory(projectId, project);
            
            // Remove process-related buttons
            this.updateModalActions(project);
            
        } catch (error) {
            console.error("Error loading project details:", error);
            this.detailProperties.innerHTML = `
                <div class="error-message">
                    Error loading project details: ${error.message || 'Unknown error'}
                </div>
            `;
            this.relatedItems.innerHTML = '<div class="empty-related">Unable to load related items</div>';
            this.historyTimeline.innerHTML = '<div class="empty-related">Unable to load history</div>';
        }
    }
    
    /**
     * Load related items for the project
     * @param {string|number} projectId - Project ID
     */
    async loadRelatedItems(projectId) {
        console.log(`Loading related items for project ${projectId}`);
        
        try {
            let relatedHtml = '<div class="related-items-container">';
            
            // Film Rolls Section
            try {
                console.log(`Fetching rolls for project ${projectId}...`);
                const rollsResponse = await this.dbService.getProjectRolls(projectId);
                console.log('Rolls response:', rollsResponse);
                
                const relatedRolls = rollsResponse.rolls || rollsResponse;
                console.log('Related rolls:', relatedRolls);
                
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-film"></i>
                                </div>
                                Film Rolls
                            </h3>
                            <span class="category-count">${relatedRolls && relatedRolls.length ? relatedRolls.length : 0}</span>
                        </div>
                `;
                
                if (relatedRolls && relatedRolls.length > 0) {
                    relatedHtml += '<div class="related-items-grid">';
                    
                    relatedRolls.forEach(roll => {
                        const rollId = roll.roll_id || roll.id;
                        const filmNumber = roll.film_number || 'No Film Number';
                        const filmType = roll.film_type || 'Unknown';
                        const pagesUsed = roll.pages_used || 0;
                        const capacity = roll.capacity || 0;
                        const status = roll.status || 'unknown';
                        const pagesRemaining = capacity - pagesUsed;
                        
                        relatedHtml += `
                            <div class="related-item roll-item">
                                <div class="related-item-header">
                                    <div class="related-item-main">
                                        <div class="related-item-title">${filmNumber}</div>
                                        <div class="related-item-subtitle">Roll ID: ${rollId}</div>
                                    </div>
                                    <div class="related-item-id">Roll</div>
                                </div>
                                <div class="related-item-meta">
                                    <span class="meta-tag film-type">${filmType}</span>
                                    <span class="meta-tag pages">${pagesUsed}/${capacity} pages</span>
                                    ${pagesRemaining <= 10 ? '<span class="meta-tag oversized">Low Space</span>' : ''}
                                </div>
                                <div class="related-item-actions">
                                    <button class="view-related" data-id="${rollId}" data-type="roll">
                                        <i class="fas fa-eye"></i>
                                        View Details
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                    
                    relatedHtml += '</div>';
                } else {
                    console.log('No rolls found for project');
                    relatedHtml += `
                        <div class="empty-related">
                            <i class="fas fa-film empty-related-icon"></i>
                            <div class="empty-related-title">No Film Rolls Allocated</div>
                            <div class="empty-related-subtitle">This project hasn't been allocated to any film rolls yet.</div>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (rollError) {
                console.error("Error fetching project rolls:", rollError);
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-film"></i>
                                </div>
                                Film Rolls
                            </h3>
                            <span class="category-count">Error</span>
                        </div>
                        <div class="error-message">
                            <p>Error loading rolls: ${rollError.message || 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Documents Section
            try {
                console.log(`Fetching documents for project ${projectId}...`);
                const documentsResponse = await this.dbService.getProjectDocuments(projectId);
                console.log('Documents response:', documentsResponse);
                
                const relatedDocuments = documentsResponse.documents || documentsResponse;
                console.log('Related documents:', relatedDocuments);
                
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-file-alt"></i>
                                </div>
                                Documents
                            </h3>
                            <span class="category-count">${relatedDocuments && relatedDocuments.length ? relatedDocuments.length : 0}</span>
                        </div>
                `;
                
                if (relatedDocuments && relatedDocuments.length > 0) {
                    relatedHtml += '<div class="related-items-grid">';
                    
                    relatedDocuments.forEach(doc => {
                        const docId = doc.id || doc.doc_id;
                        const fullPath = doc.path || doc.name || 'Unknown Document';
                        const docName = fullPath.split(/[/\\]/).pop();
                        const pages = doc.pages || 0;
                        const hasOversized = doc.has_oversized;
                        
                        relatedHtml += `
                            <div class="related-item document-item">
                                <div class="related-item-header">
                                    <div class="related-item-main">
                                        <div class="related-item-title">${docName}</div>
                                        <div class="related-item-subtitle">${fullPath}</div>
                                    </div>
                                    <div class="related-item-id">Doc</div>
                                </div>
                                <div class="related-item-meta">
                                    <span class="meta-tag pages">${pages} pages</span>
                                    ${hasOversized ? '<span class="meta-tag oversized">Oversized</span>' : ''}
                                </div>
                                <div class="related-item-actions">
                                    <button class="view-related" data-id="${docId}" data-type="document">
                                        <i class="fas fa-eye"></i>
                                        View Details
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                    
                    relatedHtml += '</div>';
                } else {
                    console.log('No documents found for project');
                    relatedHtml += `
                        <div class="empty-related">
                            <i class="fas fa-file-alt empty-related-icon"></i>
                            <div class="empty-related-title">No Documents Found</div>
                            <div class="empty-related-subtitle">No documents have been processed for this project yet.</div>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (docError) {
                console.error("Error fetching project documents:", docError);
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-file-alt"></i>
                                </div>
                                Documents
                            </h3>
                            <span class="category-count">Error</span>
                        </div>
                `;
                
                // If it's a 404, the endpoint doesn't exist yet
                if (docError.status === 404) {
                    relatedHtml += `
                        <div class="empty-related">
                            <i class="fas fa-clock empty-related-icon"></i>
                            <div class="empty-related-title">Documents Not Available</div>
                            <div class="empty-related-subtitle">Document listing will be available once processing is complete.</div>
                        </div>
                    `;
                } else {
                    relatedHtml += `
                        <div class="error-message">
                            <p>Error loading documents: ${docError.message || 'Unknown error'}</p>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
            }
            
            relatedHtml += '</div>'; // Close related-items-container
            
            this.relatedItems.innerHTML = relatedHtml;
            
            // Add event listeners to view roll/document buttons
            document.querySelectorAll('.view-related').forEach(button => {
                button.addEventListener('click', (e) => {
                    const id = e.target.closest('.view-related').getAttribute('data-id');
                    const type = e.target.closest('.view-related').getAttribute('data-type');
                    
                    if (type === 'roll') {
                        const showRollEvent = new CustomEvent('showRollDetails', {
                            detail: { rollId: id }
                        });
                        document.dispatchEvent(showRollEvent);
                    } else if (type === 'document') {
                        const showDocumentEvent = new CustomEvent('showDocumentDetails', {
                            detail: { documentId: id }
                        });
                        document.dispatchEvent(showDocumentEvent);
                    }
                });
            });
            
        } catch (error) {
            console.error("Error loading related items:", error);
            this.relatedItems.innerHTML = `
                <div class="related-items-container">
                    <div class="error-message">
                        <p>Error loading related items: ${error.message || 'Unknown error'}</p>
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * Load project history
     * @param {string|number} projectId - Project ID
     * @param {Object} project - Project data
     */
    async loadProjectHistory(projectId, project) {
        try {
            const history = await this.dbService.getProjectHistory(projectId);
            
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
                
                this.historyTimeline.innerHTML = historyHtml;
            } else {
                // No history found, create basic timeline
                this.historyTimeline.innerHTML = `
                    <div class="timeline-item">
                        <div class="timeline-date">${project.date_created}</div>
                        <div class="timeline-content">
                            <div class="timeline-title">Created</div>
                            <div class="timeline-description">Project was created</div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-date">${project.updated_at || project.date_created}</div>
                        <div class="timeline-content">
                            <div class="timeline-title">Last Modified</div>
                            <div class="timeline-description">Project was updated</div>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error("Error loading project history:", error);
            
            // Create basic timeline on error
            this.historyTimeline.innerHTML = `
                <div class="timeline-item">
                    <div class="timeline-date">${project.date_created}</div>
                    <div class="timeline-content">
                        <div class="timeline-title">Created</div>
                        <div class="timeline-description">Project was created</div>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-date">${project.updated_at || project.date_created}</div>
                    <div class="timeline-content">
                        <div class="timeline-title">Last Modified</div>
                        <div class="timeline-description">Project was updated</div>
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * Update modal action buttons based on project status
     * @param {Object} project - Project data
     */
    updateModalActions(project) {
        const modalFooter = document.querySelector('.modal-footer');
        
        // Remove any existing process or allocate buttons
        const existingProcessBtn = document.getElementById('process-project-btn');
        if (existingProcessBtn) {
            existingProcessBtn.remove();
        }
        
        const existingAllocateBtn = document.getElementById('allocate-films-btn');
        if (existingAllocateBtn) {
            existingAllocateBtn.remove();
        }
    }
    
    /**
     * Show delete confirmation modal
     * @param {Object} item - Item to delete (project, roll, or document)
     * @param {string} itemType - Type of item ('project', 'roll', 'document')
     */
    showDeleteConfirmation(item, itemType) {
        const deleteModal = document.getElementById('delete-modal');
        const deleteTitle = document.getElementById('delete-modal-title');
        const deleteDetails = document.getElementById('delete-item-details');
        const consequencesList = document.getElementById('delete-consequences-list');
        const confirmButton = document.getElementById('confirm-delete');
        
        // Set modal title and details based on item type
        let title, details, consequences = [];
        
        switch (itemType) {
            case 'project':
                title = 'Delete Project';
                details = `Are you sure you want to delete project "${item.archive_id}"? This action cannot be undone.`;
                consequences = [
                    'All associated rolls and film allocations',
                    'All document records and processing data',
                    'All reference sheets and generated files',
                    'Project history and timeline data'
                ];
                break;
            case 'roll':
                title = 'Delete Roll';
                details = `Are you sure you want to delete roll "${item.film_number || item.roll_id}"? This action cannot be undone.`;
                consequences = [
                    'All document segments on this roll',
                    'Film number allocation data',
                    'Scanning and processing records'
                ];
                break;
            case 'document':
                title = 'Delete Document';
                details = `Are you sure you want to delete document "${item.name || item.doc_id}"? This action cannot be undone.`;
                consequences = [
                    'All document segments and allocations',
                    'Reference sheet entries',
                    'Processing and analysis data'
                ];
                break;
        }
        
        // Update modal content
        deleteTitle.textContent = title;
        deleteDetails.textContent = details;
        
        // Clear and populate consequences list
        consequencesList.innerHTML = '';
        consequences.forEach(consequence => {
            const li = document.createElement('li');
            li.textContent = consequence;
            consequencesList.appendChild(li);
        });
        
        // Set up confirm button
        confirmButton.onclick = () => {
            this.confirmDelete(item, itemType);
        };
        
        // Show modal
        deleteModal.style.display = 'flex';
    }
    
    /**
     * Confirm and execute deletion
     * @param {Object} item - Item to delete
     * @param {string} itemType - Type of item
     */
    async confirmDelete(item, itemType) {
        const deleteModal = document.getElementById('delete-modal');
        const confirmButton = document.getElementById('confirm-delete');
        
        try {
            // Show loading state
            confirmButton.textContent = 'Deleting...';
            confirmButton.disabled = true;
            
            let response;
            switch (itemType) {
                case 'project':
                    response = await this.dbService.deleteProject(item.project_id || item.id);
                    break;
                case 'roll':
                    response = await this.dbService.deleteRoll(item.id);
                    break;
                case 'document':
                    response = await this.dbService.deleteDocument(item.id);
                    break;
            }
            
            if (response.status === 'success') {
                // Hide delete modal
                deleteModal.style.display = 'none';
                
                // Hide detail modal if open
                this.modal.style.display = 'none';
                
                // Trigger refresh of the main list
                const refreshEvent = new CustomEvent('refreshProjectList');
                document.dispatchEvent(refreshEvent);
                
                // Show success message
                console.log(`${itemType} deleted successfully`);
            } else {
                throw new Error(response.message || 'Delete failed');
            }
            
        } catch (error) {
            console.error(`Error deleting ${itemType}:`, error);
            alert(`Error deleting ${itemType}: ${error.message}`);
        } finally {
            // Reset button state
            confirmButton.textContent = 'Delete';
            confirmButton.disabled = false;
        }
    }
}

// Export the class for use in the main module
window.ProjectDetails = ProjectDetails; 