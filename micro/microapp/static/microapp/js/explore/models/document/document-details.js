/**
 * document-details.js - Document details functionality
 * Handles displaying detailed information about documents
 */

class DocumentDetails {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentDocumentId = null;
    }

    /**
     * Initialize the document details module
     */
    initialize() {
        // Set up event listeners for detail modal
        this.setupEventListeners();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for showDocumentDetails events
        document.addEventListener('showDocumentDetails', (event) => {
            const { documentId } = event.detail;
            this.showDetails(documentId);
        });

        // Close modal events
        document.querySelectorAll('.close-modal').forEach(button => {
            button.addEventListener('click', () => {
                this.hideDetails();
            });
        });

        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });

        // Edit button
        document.getElementById('edit-item').addEventListener('click', () => {
            if (this.currentDocumentId) {
                const editEvent = new CustomEvent('editDocument', {
                    detail: { documentId: this.currentDocumentId }
                });
                document.dispatchEvent(editEvent);
                this.hideDetails();
            }
        });
    }

    /**
     * Show document details in modal
     * @param {number|string} documentId - Document ID
     */
    async showDetails(documentId) {
        this.currentDocumentId = documentId;
        
        try {
            // Fetch document data
            const response = await this.dbService.getDocument(documentId);
            
            // Handle different response structures
            let document;
            if (response.document) {
                // Response has a 'document' property
                document = response.document;
            } else if (response.id || response.doc_id) {
                // Response is the document object directly
                document = response;
            } else {
                throw new Error('Invalid response structure: no document data found');
            }
            
            // Validate that we have a document object
            if (!document) {
                throw new Error('Document data is null or undefined');
            }
            
            console.log('Document data received:', document); // Debug log
            
            // Update modal title
            const documentTitle = document.name || document.path || `Document #${document.id}`;
            document.getElementById('modal-title').textContent = `Document Details - ${documentTitle}`;
            
            // Populate details tab
            this.populateDetailsTab(document);
            
            // Load related items
            this.loadRelatedItems(documentId);
            
            // Load history
            this.loadHistory(documentId);
            
            // Show modal
            document.getElementById('detail-modal').style.display = 'flex';
            
            // Switch to details tab by default
            this.switchTab('details');
            
        } catch (error) {
            console.error('Error loading document details:', error);
            console.error('Document ID:', documentId); // Debug log
            alert(`Error loading document details: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Hide the details modal
     */
    hideDetails() {
        document.getElementById('detail-modal').style.display = 'none';
        this.currentDocumentId = null;
    }

    /**
     * Switch between tabs in the modal
     * @param {string} tabName - Tab name (details, related, history)
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    /**
     * Populate the details tab with document information
     * @param {Object} document - Document data
     */
    populateDetailsTab(document) {
        const detailsContainer = document.querySelector('#details-tab .detail-properties');
        
        // Validate document object
        if (!document) {
            detailsContainer.innerHTML = '<div class="error-message">No document data available</div>';
            return;
        }
        
        // Safe property access with fallbacks
        const docId = document.id || 'N/A';
        const docName = document.name || 'Unknown Document';
        const docPath = document.path || 'N/A';
        const pages = document.pages || 0;
        const hasOversized = document.has_oversized || false;
        const isProcessed = document.is_processed || false;
        const projectId = document.project_id || 'N/A';
        const rollId = document.roll_id || 'N/A';
        const startPage = document.start_page || 'N/A';
        const endPage = document.end_page || 'N/A';
        const fileSize = document.file_size || 'N/A';
        const fileType = document.file_type || 'Unknown';
        const creationDate = document.creation_date || 'N/A';
        const lastModified = document.last_modified || 'N/A';
        const checksum = document.checksum || 'N/A';
        
        detailsContainer.innerHTML = `
            <div class="detail-grid">
                <div class="detail-section">
                    <h3>Basic Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Document ID:</span>
                        <span class="detail-value">${docId}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Document Name:</span>
                        <span class="detail-value">${docName}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">File Path:</span>
                        <span class="detail-value" title="${docPath}">${docPath}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">File Type:</span>
                        <span class="detail-value">${fileType}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">File Size:</span>
                        <span class="detail-value">${fileSize}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Document Properties</h3>
                    <div class="detail-row">
                        <span class="detail-label">Total Pages:</span>
                        <span class="detail-value">${pages} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Has Oversized:</span>
                        <span class="detail-value">
                            <span class="boolean-badge ${hasOversized ? 'true' : 'false'}">
                                ${hasOversized ? 'Yes' : 'No'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Is Processed:</span>
                        <span class="detail-value">
                            <span class="boolean-badge ${isProcessed ? 'true' : 'false'}">
                                ${isProcessed ? 'Yes' : 'No'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Checksum:</span>
                        <span class="detail-value" title="${checksum}">${checksum}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Project & Roll Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Project ID:</span>
                        <span class="detail-value">${projectId}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Roll ID:</span>
                        <span class="detail-value">${rollId}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Start Page on Roll:</span>
                        <span class="detail-value">${startPage}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">End Page on Roll:</span>
                        <span class="detail-value">${endPage}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Timestamps</h3>
                    <div class="detail-row">
                        <span class="detail-label">Creation Date:</span>
                        <span class="detail-value">${creationDate}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Last Modified:</span>
                        <span class="detail-value">${lastModified}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load related items (projects, rolls, etc.)
     * @param {number|string} documentId - Document ID
     */
    async loadRelatedItems(documentId) {
        const relatedContainer = document.querySelector('#related-tab .related-items');
        
        relatedContainer.innerHTML = `
            <div class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading related items...</p>
            </div>
        `;
        
        try {
            let relatedHtml = '<div class="related-items-container">';
            
            // Get the current document data to extract project and roll information
            const documentResponse = await this.dbService.getDocument(documentId);
            let document;
            if (documentResponse.document) {
                document = documentResponse.document;
            } else if (documentResponse.id || documentResponse.doc_id) {
                document = documentResponse;
            } else {
                throw new Error('Invalid document data structure');
            }
            
            // Project Information Section
            try {
                console.log(`Loading project information for document ${documentId}...`);
                
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-folder"></i>
                                </div>
                                Project Information
                            </h3>
                            <span class="category-count">1</span>
                        </div>
                `;
                
                if (document.project_id) {
                    try {
                        const projectResponse = await this.dbService.getProject(document.project_id);
                        let project;
                        if (projectResponse.project) {
                            project = projectResponse.project;
                        } else if (projectResponse.id || projectResponse.project_id) {
                            project = projectResponse;
                        }
                        
                        if (project) {
                            // Get project status
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
                            
                            relatedHtml += `
                                <div class="related-items-grid">
                                    <div class="related-item project-item">
                                        <div class="related-item-header">
                                            <div class="related-item-main">
                                                <div class="related-item-title">${project.archive_id}</div>
                                                <div class="related-item-subtitle">${project.location} - ${project.doc_type || 'Unknown Type'}</div>
                                            </div>
                                            <div class="related-item-id">Project</div>
                                        </div>
                                        <div class="related-item-meta">
                                            <span class="meta-tag pages">${project.total_pages || 0} pages</span>
                                            <span class="meta-tag status-${statusClass}">${statusText}</span>
                                            ${project.has_oversized ? '<span class="meta-tag oversized">Has Oversized</span>' : ''}
                                        </div>
                                        <div class="related-item-actions">
                                            <button class="view-related" data-id="${project.project_id || project.id}" data-type="project">
                                                <i class="fas fa-eye"></i>
                                                View Project
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            throw new Error('Project data not found');
                        }
                    } catch (projectError) {
                        console.log('Error fetching project details:', projectError.message || 'Unknown error');
                        relatedHtml += `
                            <div class="related-items-grid">
                                <div class="related-item project-item">
                                    <div class="related-item-header">
                                        <div class="related-item-main">
                                            <div class="related-item-title">Project ID: ${document.project_id}</div>
                                            <div class="related-item-subtitle">Details unavailable</div>
                                        </div>
                                        <div class="related-item-id">Project</div>
                                    </div>
                                    <div class="related-item-meta">
                                        <span class="meta-tag error">Details unavailable</span>
                                    </div>
                                    <div class="related-item-actions">
                                        <button class="view-related" data-id="${document.project_id}" data-type="project">
                                            <i class="fas fa-eye"></i>
                                            View Project
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    relatedHtml += `
                        <div class="empty-related">
                            <i class="fas fa-folder empty-related-icon"></i>
                            <div class="empty-related-title">No Project Assigned</div>
                            <div class="empty-related-subtitle">This document is not currently assigned to any project.</div>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (projectError) {
                console.error('Error loading project information:', projectError);
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-folder"></i>
                                </div>
                                Project Information
                            </h3>
                            <span class="category-count">Error</span>
                        </div>
                        <div class="error-message">
                            <p>Error loading project information: ${projectError.message || 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Roll Information Section
            try {
                console.log(`Loading roll information for document ${documentId}...`);
                
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-film"></i>
                                </div>
                                Roll Information
                            </h3>
                            <span class="category-count">1</span>
                        </div>
                `;
                
                if (document.roll_id) {
                    try {
                        const rollResponse = await this.dbService.getRoll(document.roll_id);
                        let roll;
                        if (rollResponse.roll) {
                            roll = rollResponse.roll;
                        } else if (rollResponse.id || rollResponse.roll_id) {
                            roll = rollResponse;
                        }
                        
                        if (roll) {
                            // Calculate utilization
                            const capacity = roll.capacity || 0;
                            const pagesUsed = roll.pages_used || 0;
                            const utilization = capacity > 0 ? (pagesUsed / capacity * 100).toFixed(1) : 0;
                            
                            // Determine status
                            let statusClass = 'active';
                            let statusDisplay = roll.status || 'Active';
                            
                            if (roll.is_full) {
                                statusDisplay = 'Full';
                                statusClass = 'full';
                            } else if (roll.is_partial) {
                                statusDisplay = 'Partial';
                                statusClass = 'partial';
                            }
                            
                            relatedHtml += `
                                <div class="related-items-grid">
                                    <div class="related-item roll-item">
                                        <div class="related-item-header">
                                            <div class="related-item-main">
                                                <div class="related-item-title">${roll.film_number || 'No Film Number'}</div>
                                                <div class="related-item-subtitle">Roll ID: ${roll.roll_id || roll.id} - ${roll.film_type || 'Unknown'}</div>
                                            </div>
                                            <div class="related-item-id">Roll</div>
                                        </div>
                                        <div class="related-item-meta">
                                            <span class="meta-tag film-type">${roll.film_type || 'Unknown'}</span>
                                            <span class="meta-tag pages">${pagesUsed}/${capacity} pages</span>
                                            <span class="meta-tag status-${statusClass}">${statusDisplay}</span>
                                            <span class="meta-tag utilization">${utilization}% used</span>
                                        </div>
                                        <div class="related-item-actions">
                                            <button class="view-related" data-id="${roll.id || roll.roll_id}" data-type="roll">
                                                <i class="fas fa-eye"></i>
                                                View Roll
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            throw new Error('Roll data not found');
                        }
                    } catch (rollError) {
                        console.log('Error fetching roll details:', rollError.message || 'Unknown error');
                        relatedHtml += `
                            <div class="related-items-grid">
                                <div class="related-item roll-item">
                                    <div class="related-item-header">
                                        <div class="related-item-main">
                                            <div class="related-item-title">Roll ID: ${document.roll_id}</div>
                                            <div class="related-item-subtitle">Details unavailable</div>
                                        </div>
                                        <div class="related-item-id">Roll</div>
                                    </div>
                                    <div class="related-item-meta">
                                        <span class="meta-tag error">Details unavailable</span>
                                    </div>
                                    <div class="related-item-actions">
                                        <button class="view-related" data-id="${document.roll_id}" data-type="roll">
                                            <i class="fas fa-eye"></i>
                                            View Roll
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    relatedHtml += `
                        <div class="empty-related">
                            <i class="fas fa-film empty-related-icon"></i>
                            <div class="empty-related-title">No Roll Assigned</div>
                            <div class="empty-related-subtitle">This document has not been allocated to any roll yet.</div>
                        </div>
                    `;
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (rollError) {
                console.error('Error loading roll information:', rollError);
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-film"></i>
                                </div>
                                Roll Information
                            </h3>
                            <span class="category-count">Error</span>
                        </div>
                        <div class="error-message">
                            <p>Error loading roll information: ${rollError.message || 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Document Statistics Section
            relatedHtml += `
                <div class="related-category">
                    <div class="related-category-header">
                        <h3 class="category-title">
                            <div class="category-icon">
                                <i class="fas fa-chart-bar"></i>
                            </div>
                            Document Statistics
                        </h3>
                        <span class="category-count">Info</span>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${document.pages || 0}</div>
                            <div class="stat-label">Total Pages</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${document.file_size || 'N/A'}</div>
                            <div class="stat-label">File Size</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${document.start_page || 'N/A'}</div>
                            <div class="stat-label">Start Page</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${document.end_page || 'N/A'}</div>
                            <div class="stat-label">End Page</div>
                        </div>
                    </div>
                </div>
            `;
            
            relatedHtml += '</div>'; // Close related-items-container
            
            relatedContainer.innerHTML = relatedHtml;
            
            // Add event listeners to view buttons
            document.querySelectorAll('.view-related').forEach(button => {
                if (!button.disabled) {
                    button.addEventListener('click', (e) => {
                        const id = e.target.closest('.view-related').getAttribute('data-id');
                        const type = e.target.closest('.view-related').getAttribute('data-type');
                        
                        if (type === 'project') {
                            const showProjectEvent = new CustomEvent('showProjectDetails', {
                                detail: { projectId: id }
                            });
                            document.dispatchEvent(showProjectEvent);
                        } else if (type === 'roll') {
                            const showRollEvent = new CustomEvent('showRollDetails', {
                                detail: { rollId: id }
                            });
                            document.dispatchEvent(showRollEvent);
                        }
                    });
                }
            });
            
        } catch (error) {
            console.error('Error loading related items:', error);
            relatedContainer.innerHTML = `
                <div class="related-items-container">
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Error loading related items: ${error.message || 'Unknown error'}</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Load document history
     * @param {number|string} documentId - Document ID
     */
    async loadHistory(documentId) {
        const historyContainer = document.querySelector('#history-tab .history-timeline');
        
        historyContainer.innerHTML = `
            <div class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading history...</p>
            </div>
        `;
        
        try {
            // For now, show a placeholder
            historyContainer.innerHTML = `
                <div class="coming-soon-message">
                    <i class="fas fa-history"></i>
                    <p>Document history tracking coming soon!</p>
                </div>
            `;
        } catch (error) {
            console.error('Error loading document history:', error);
            historyContainer.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading history</p>
                </div>
            `;
        }
    }
}

// Export the class for use in the main module
window.DocumentDetails = DocumentDetails; 