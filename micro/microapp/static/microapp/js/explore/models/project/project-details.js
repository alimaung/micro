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
            const project = response.project;
            
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
        try {
            // Try to fetch related rolls
            const relatedRolls = await this.dbService.getProjectRolls(projectId);
            
            if (relatedRolls && relatedRolls.length > 0) {
                let rollsHtml = '<h3>Film Rolls</h3><div class="related-list">';
                
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
                
                // Add documents section header
                rollsHtml += '<h3 class="related-section-header">Documents</h3>';
                
                // Try to fetch related documents
                try {
                    const relatedDocuments = await this.dbService.getProjectDocuments(projectId);
                    
                    if (relatedDocuments && relatedDocuments.length > 0) {
                        rollsHtml += '<div class="related-list">';
                        
                        relatedDocuments.forEach(doc => {
                            const docHasOversized = doc.has_oversized ? 
                                `<span class="badge badge-warning">Oversized</span>` : '';
                                
                            rollsHtml += `
                                <div class="related-item">
                                    <span class="related-item-id">${doc.doc_id}</span>
                                    <span class="related-item-name">${doc.path.split('/').pop()}</span>
                                    <span class="related-item-meta">${doc.pages} pages ${docHasOversized}</span>
                                    <button class="view-related" data-id="${doc.doc_id}" data-type="document">View</button>
                                </div>
                            `;
                        });
                        
                        rollsHtml += '</div>';
                    } else {
                        rollsHtml += `
                            <div class="empty-related">
                                <p>No documents found for this project.</p>
                            </div>
                        `;
                    }
                } catch (docError) {
                    console.error("Error fetching project documents:", docError);
                    rollsHtml += `
                        <div class="error-message">
                            <p>Error loading documents: ${docError.message || 'Unknown error'}</p>
                        </div>
                    `;
                }
                
                this.relatedItems.innerHTML = rollsHtml;
                
                // Add event listeners to view roll/document buttons
                document.querySelectorAll('.view-related').forEach(button => {
                    button.addEventListener('click', (e) => {
                        const id = e.target.getAttribute('data-id');
                        const type = e.target.getAttribute('data-type');
                        
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
            } else {
                // No rolls found
                this.relatedItems.innerHTML = `
                    <div class="empty-related">
                        <p>No rolls have been allocated to this project yet.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error("Error loading related items:", error);
            this.relatedItems.innerHTML = `
                <div class="error-message">
                    <p>Error loading related items: ${error.message || 'Unknown error'}</p>
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
}

// Export the class for use in the main module
window.ProjectDetails = ProjectDetails; 