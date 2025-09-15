/**
 * roll-details.js - Roll details functionality
 * Handles displaying detailed information about rolls
 */

class RollDetails {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentRollId = null;
    }

    /**
     * Initialize the roll details module
     */
    initialize() {
        // Set up event listeners for detail modal
        this.setupEventListeners();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for showRollDetails events
        document.addEventListener('showRollDetails', (event) => {
            const { rollId } = event.detail;
            this.showDetails(rollId);
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
            if (this.currentRollId) {
                const editEvent = new CustomEvent('editRoll', {
                    detail: { rollId: this.currentRollId }
                });
                document.dispatchEvent(editEvent);
                this.hideDetails();
            }
        });
    }

    /**
     * Show roll details in modal
     * @param {number|string} rollId - Roll ID
     */
    async showDetails(rollId) {
        this.currentRollId = rollId;
        
        try {
            // Fetch roll data
            const response = await this.dbService.getRoll(rollId);
            
            // Handle different response structures
            let roll;
            if (response.roll) {
                // Response has a 'roll' property
                roll = response.roll;
            } else if (response.id || response.roll_id) {
                // Response is the roll object directly
                roll = response;
            } else {
                throw new Error('Invalid response structure: no roll data found');
            }
            
            // Validate that we have a roll object
            if (!roll) {
                throw new Error('Roll data is null or undefined');
            }
            
            console.log('Roll data received:', roll); // Debug log
            
            // Update modal title
            const rollTitle = roll.film_number || roll.roll_id || `#${roll.id}`;
            document.getElementById('modal-title').textContent = `Roll Details - ${rollTitle}`;
            
            // Populate details tab
            this.populateDetailsTab(roll);
            
            // Load related items
            this.loadRelatedItems(rollId);
            
            // Load history
            this.loadHistory(rollId);
            
            // Show modal
            document.getElementById('detail-modal').style.display = 'flex';
            
            // Switch to details tab by default
            this.switchTab('details');
            
        } catch (error) {
            console.error('Error loading roll details:', error);
            console.error('Roll ID:', rollId); // Debug log
            alert(`Error loading roll details: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Hide the details modal
     */
    hideDetails() {
        document.getElementById('detail-modal').style.display = 'none';
        this.currentRollId = null;
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
     * Populate the details tab with roll information
     * @param {Object} roll - Roll data
     */
    populateDetailsTab(roll) {
        const detailsContainer = document.querySelector('#details-tab .detail-properties');
        
        // Validate roll object
        if (!roll) {
            detailsContainer.innerHTML = '<div class="error-message">No roll data available</div>';
            return;
        }
        
        // Calculate utilization with null checks
        const capacity = roll.capacity || 0;
        const pagesUsed = roll.pages_used || 0;
        const utilization = capacity > 0 ? (pagesUsed / capacity * 100).toFixed(1) : 0;
        
        // Determine status display with null checks
        let statusDisplay = roll.status || 'Active';
        let statusClass = 'active';
        
        if (roll.is_full) {
            statusDisplay = 'Full';
            statusClass = 'full';
        } else if (roll.is_partial) {
            statusDisplay = 'Partial';
            statusClass = 'partial';
        }
        
        // Safe property access with fallbacks
        const rollId = roll.id || 'N/A';
        const rollNumber = roll.roll_id || 'N/A';
        const filmNumber = roll.film_number || 'N/A';
        const filmType = roll.film_type || 'Unknown';
        const projectArchiveId = roll.project_archive_id || 'N/A';
        const projectId = roll.project_id || 'N/A';
        const pagesRemaining = roll.pages_remaining || 0;
        const remainingCapacity = roll.remaining_capacity || 0;
        const usableCapacity = roll.usable_capacity || 0;
        const hasSplitDocuments = roll.has_split_documents || false;
        const isPartial = roll.is_partial || false;
        const isFull = roll.is_full || false;
        const filmNumberSource = roll.film_number_source || 'N/A';
        const creationDate = roll.creation_date || 'N/A';
        
        detailsContainer.innerHTML = `
            <div class="detail-grid">
                <div class="detail-section">
                    <h3>Basic Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Roll ID:</span>
                        <span class="detail-value">${rollId}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Roll Number:</span>
                        <span class="detail-value">${rollNumber}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Film Number:</span>
                        <span class="detail-value">${filmNumber}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Film Type:</span>
                        <span class="detail-value">
                            <span class="film-type-badge" data-type="${filmType}">${filmType}</span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Status:</span>
                        <span class="detail-value">
                            <span class="status-badge ${statusClass}">${statusDisplay}</span>
                        </span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Project Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Project Archive ID:</span>
                        <span class="detail-value">${projectArchiveId}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Project ID:</span>
                        <span class="detail-value">${projectId}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Capacity & Usage</h3>
                    <div class="detail-row">
                        <span class="detail-label">Total Capacity:</span>
                        <span class="detail-value">${capacity} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Pages Used:</span>
                        <span class="detail-value">${pagesUsed} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Pages Remaining:</span>
                        <span class="detail-value">${pagesRemaining} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Utilization:</span>
                        <span class="detail-value">
                            <div class="utilization-display">
                                <div class="utilization-bar">
                                    <div class="utilization-fill" style="width: ${utilization}%"></div>
                                </div>
                                <span class="utilization-text">${utilization}%</span>
                            </div>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Remaining Capacity:</span>
                        <span class="detail-value">${remainingCapacity} pages</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Usable Capacity:</span>
                        <span class="detail-value">${usableCapacity} pages</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Additional Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Has Split Documents:</span>
                        <span class="detail-value">
                            <span class="boolean-badge ${hasSplitDocuments ? 'true' : 'false'}">
                                ${hasSplitDocuments ? 'Yes' : 'No'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Is Partial:</span>
                        <span class="detail-value">
                            <span class="boolean-badge ${isPartial ? 'true' : 'false'}">
                                ${isPartial ? 'Yes' : 'No'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Is Full:</span>
                        <span class="detail-value">
                            <span class="boolean-badge ${isFull ? 'true' : 'false'}">
                                ${isFull ? 'Yes' : 'No'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Film Number Source:</span>
                        <span class="detail-value">${filmNumberSource}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Creation Date:</span>
                        <span class="detail-value">${creationDate}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load related items (documents, projects, etc.)
     * @param {number|string} rollId - Roll ID
     */
    async loadRelatedItems(rollId) {
        const relatedContainer = document.querySelector('#related-tab .related-items');
        
        relatedContainer.innerHTML = `
            <div class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading related items...</p>
            </div>
        `;
        
        try {
            let relatedHtml = '<div class="related-items-container">';
            
            // Get the current roll data to extract project information
            const rollResponse = await this.dbService.getRoll(rollId);
            let roll;
            if (rollResponse.roll) {
                roll = rollResponse.roll;
            } else if (rollResponse.id || rollResponse.roll_id) {
                roll = rollResponse;
            } else {
                throw new Error('Invalid roll data structure');
            }
            
            // Project Information Section
            try {
                console.log(`Loading project information for roll ${rollId}...`);
                
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
                
                if (roll.project_id) {
                    try {
                        const projectResponse = await this.dbService.getProject(roll.project_id);
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
                        console.error('Error fetching project details:', projectError);
                        relatedHtml += `
                            <div class="related-items-grid">
                                <div class="related-item project-item">
                                    <div class="related-item-header">
                                        <div class="related-item-main">
                                            <div class="related-item-title">Project ID: ${roll.project_id}</div>
                                            <div class="related-item-subtitle">Archive ID: ${roll.project_archive_id || 'Unknown'}</div>
                                        </div>
                                        <div class="related-item-id">Project</div>
                                    </div>
                                    <div class="related-item-meta">
                                        <span class="meta-tag error">Details unavailable</span>
                                    </div>
                                    <div class="related-item-actions">
                                        <button class="view-related" data-id="${roll.project_id}" data-type="project">
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
                            <div class="empty-related-subtitle">This roll is not currently assigned to any project.</div>
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
            
            // Documents Section
            try {
                console.log(`Loading documents for roll ${rollId}...`);
                
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-file-alt"></i>
                                </div>
                                Documents on Roll
                            </h3>
                            <span class="category-count">-</span>
                        </div>
                `;
                
                // Try to fetch roll documents (this endpoint might not exist yet)
                try {
                    const documentsResponse = await this.dbService._apiRequest(`rolls/${rollId}/documents/`);
                    const rollDocuments = documentsResponse.documents || documentsResponse;
                    
                    if (rollDocuments && rollDocuments.length > 0) {
                        // Update count
                        relatedHtml = relatedHtml.replace('<span class="category-count">-</span>', `<span class="category-count">${rollDocuments.length}</span>`);
                        
                        relatedHtml += '<div class="related-items-grid">';
                        
                        rollDocuments.forEach(doc => {
                            const docId = doc.id || doc.doc_id;
                            const fullPath = doc.path || doc.name || 'Unknown Document';
                            const docName = fullPath.split(/[/\\]/).pop();
                            const pages = doc.pages || 0;
                            const hasOversized = doc.has_oversized;
                            const startPage = doc.start_page || 'N/A';
                            const endPage = doc.end_page || 'N/A';
                            
                            relatedHtml += `
                                <div class="related-item document-item">
                                    <div class="related-item-header">
                                        <div class="related-item-main">
                                            <div class="related-item-title">${docName}</div>
                                            <div class="related-item-subtitle">Pages ${startPage}-${endPage} on roll</div>
                                        </div>
                                        <div class="related-item-id">Doc</div>
                                    </div>
                                    <div class="related-item-meta">
                                        <span class="meta-tag pages">${pages} pages</span>
                                        ${hasOversized ? '<span class="meta-tag oversized">Oversized</span>' : ''}
                                        ${doc.is_split ? '<span class="meta-tag split">Split Document</span>' : ''}
                                    </div>
                                    <div class="related-item-actions">
                                        <button class="view-related" data-id="${docId}" data-type="document">
                                            <i class="fas fa-eye"></i>
                                            View Document
                                        </button>
                                    </div>
                                </div>
                            `;
                        });
                        
                        relatedHtml += '</div>';
                    } else {
                        relatedHtml = relatedHtml.replace('<span class="category-count">-</span>', '<span class="category-count">0</span>');
                        relatedHtml += `
                            <div class="empty-related">
                                <i class="fas fa-file-alt empty-related-icon"></i>
                                <div class="empty-related-title">No Documents Found</div>
                                <div class="empty-related-subtitle">No documents have been allocated to this roll yet.</div>
                            </div>
                        `;
                    }
                } catch (docError) {
                    // Check if it's a 404 error (endpoint not implemented)
                    if (docError.message && docError.message.includes('404')) {
                        console.log('Roll documents endpoint not available, showing informative placeholder');
                        relatedHtml = relatedHtml.replace('<span class="category-count">-</span>', '<span class="category-count">?</span>');
                        
                        // Show information based on roll properties
                        if (roll.has_split_documents) {
                            relatedHtml += `
                                <div class="related-items-grid">
                                    <div class="related-item document-item">
                                        <div class="related-item-header">
                                            <div class="related-item-main">
                                                <div class="related-item-title">Split Documents Detected</div>
                                                <div class="related-item-subtitle">This roll contains split documents</div>
                                            </div>
                                            <div class="related-item-id">Info</div>
                                        </div>
                                        <div class="related-item-meta">
                                            <span class="meta-tag split">Contains Split Documents</span>
                                            <span class="meta-tag pages">${roll.pages_used || 0} pages used</span>
                                        </div>
                                        <div class="related-item-actions">
                                            <button class="view-related disabled" disabled>
                                                <i class="fas fa-clock"></i>
                                                Details Coming Soon
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            relatedHtml += `
                                <div class="empty-related">
                                    <i class="fas fa-info-circle empty-related-icon"></i>
                                    <div class="empty-related-title">Document Details Coming Soon</div>
                                    <div class="empty-related-subtitle">Document allocation details will be available once the document management API is implemented.</div>
                                    <div class="empty-related-note">
                                        <small><i class="fas fa-lightbulb"></i> This roll has ${roll.pages_used || 0} pages used out of ${roll.capacity || 0} total capacity.</small>
                                    </div>
                                </div>
                            `;
                        }
                    } else {
                        // Other errors
                        console.error('Error fetching roll documents:', docError);
                        relatedHtml = relatedHtml.replace('<span class="category-count">-</span>', '<span class="category-count">Error</span>');
                        relatedHtml += `
                            <div class="error-message">
                                <i class="fas fa-exclamation-triangle"></i>
                                <p>Error loading documents: ${docError.message || 'Unknown error'}</p>
                            </div>
                        `;
                    }
                }
                
                relatedHtml += '</div>'; // Close related-category
                
            } catch (docError) {
                console.error('Error loading documents:', docError);
                relatedHtml += `
                    <div class="related-category">
                        <div class="related-category-header">
                            <h3 class="category-title">
                                <div class="category-icon">
                                    <i class="fas fa-file-alt"></i>
                                </div>
                                Documents on Roll
                            </h3>
                            <span class="category-count">Error</span>
                        </div>
                        <div class="error-message">
                            <p>Error loading documents: ${docError.message || 'Unknown error'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Roll Statistics Section
            relatedHtml += `
                <div class="related-category">
                    <div class="related-category-header">
                        <h3 class="category-title">
                            <div class="category-icon">
                                <i class="fas fa-chart-bar"></i>
                            </div>
                            Roll Statistics
                        </h3>
                        <span class="category-count">Info</span>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${roll.capacity || 0}</div>
                            <div class="stat-label">Total Capacity</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${roll.pages_used || 0}</div>
                            <div class="stat-label">Pages Used</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${roll.pages_remaining || 0}</div>
                            <div class="stat-label">Pages Remaining</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${roll.capacity > 0 ? ((roll.pages_used || 0) / roll.capacity * 100).toFixed(1) : 0}%</div>
                            <div class="stat-label">Utilization</div>
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
                        } else if (type === 'document') {
                            const showDocumentEvent = new CustomEvent('showDocumentDetails', {
                                detail: { documentId: id }
                            });
                            document.dispatchEvent(showDocumentEvent);
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
     * Load roll history
     * @param {number|string} rollId - Roll ID
     */
    async loadHistory(rollId) {
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
                    <p>Roll history tracking coming soon!</p>
                </div>
            `;
        } catch (error) {
            console.error('Error loading roll history:', error);
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
window.RollDetails = RollDetails; 