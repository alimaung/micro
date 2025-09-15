/**
 * explore-main.js - Main controller for the explore page
 * Handles switching between different entity modules and loading templates dynamically
 */

class ExploreMain {
    constructor() {
        // Initialize model modules
        this.projectList = new ProjectList();
        this.projectDetails = new ProjectDetails();
        this.projectEdit = new ProjectEdit();
        this.projectExport = new ProjectExport();
        
        // Initialize roll modules
        this.rollList = new RollList();
        this.rollDetails = new RollDetails();
        this.rollEdit = new RollEdit();
        this.rollExport = new RollExport();
        
        // Initialize document modules
        this.documentManager = new DocumentManager();
        this.documentDetails = new DocumentDetails();
        
        // Initialize temp roll modules
        this.tempRollManager = new TempRollManager();
        
        // Current entity being viewed
        this.currentEntity = 'projects';
        
        // Entity configurations
        this.entityConfigs = {
            projects: {
                name: 'Projects',
                icon: 'fas fa-folder',
                module: 'project',
                listClass: this.projectList,
                detailsClass: this.projectDetails,
                editClass: this.projectEdit,
                exportClass: this.projectExport,
                sortFields: [
                    { value: 'id', label: 'ID' },
                    { value: 'archive_id', label: 'Archive ID' },
                    { value: 'location', label: 'Location' },
                    { value: 'doc_type', label: 'Document Type' },
                    { value: 'project_path', label: 'Project Path' },
                    { value: 'project_folder_name', label: 'Project Folder Name' },
                    { value: 'pdf_folder_path', label: 'PDF Folder Path' },
                    { value: 'has_pdf_folder', label: 'Has PDF Folder' },
                    { value: 'processing_complete', label: 'Processing Complete' },
                    { value: 'retain_sources', label: 'Retain Sources' },
                    { value: 'add_to_database', label: 'Add to Database' },
                    { value: 'has_oversized', label: 'Has Oversized' },
                    { value: 'total_pages', label: 'Total Pages' },
                    { value: 'total_pages_with_refs', label: 'Pages with Refs' },
                    { value: 'documents_with_oversized', label: 'Docs with Oversized' },
                    { value: 'total_oversized', label: 'Total Oversized' },
                    { value: 'created_at', label: 'Created At' },
                    { value: 'updated_at', label: 'Updated At' },
                    { value: 'owner', label: 'Owner' },
                    { value: 'film_allocation_complete', label: 'Film Allocation Complete' },
                    { value: 'distribution_complete', label: 'Distribution Complete' }
                ],
                advancedFields: [
                    { value: 'project_id', label: 'Project ID', group: 'Projects' },
                    { value: 'archive_id', label: 'Archive ID', group: 'Projects' },
                    { value: 'total_pages', label: 'Total Pages', group: 'Projects' },
                    { value: 'oversized', label: 'Oversized', group: 'Projects' }
                ]
            },
            rolls: {
                name: 'Rolls',
                icon: 'fas fa-film',
                module: 'roll',
                listClass: this.rollList,
                detailsClass: this.rollDetails,
                editClass: this.rollEdit,
                exportClass: this.rollExport,
                sortFields: [
                    { value: 'id', label: 'Roll ID' },
                    { value: 'roll_id', label: 'Roll Number' },
                    { value: 'project_archive_id', label: 'Project Archive ID' },
                    { value: 'film_number', label: 'Film Number' },
                    { value: 'film_type', label: 'Film Type' },
                    { value: 'capacity', label: 'Capacity' },
                    { value: 'pages_used', label: 'Pages Used' },
                    { value: 'pages_remaining', label: 'Pages Remaining' },
                    { value: 'utilization', label: 'Utilization' },
                    { value: 'status', label: 'Status' },
                    { value: 'has_split_documents', label: 'Has Split Documents' },
                    { value: 'is_partial', label: 'Is Partial' },
                    { value: 'remaining_capacity', label: 'Remaining Capacity' },
                    { value: 'usable_capacity', label: 'Usable Capacity' },
                    { value: 'film_number_source', label: 'Film Number Source' },
                    { value: 'creation_date', label: 'Creation Date' }
                ],
                advancedFields: [
                    { value: 'film_number', label: 'Film Number', group: 'Rolls' },
                    { value: 'capacity', label: 'Capacity', group: 'Rolls' },
                    { value: 'pages_used', label: 'Pages Used', group: 'Rolls' },
                    { value: 'pages_remaining', label: 'Pages Remaining', group: 'Rolls' }
                ]
            },
            documents: {
                name: 'Documents',
                icon: 'fas fa-file-alt',
                module: 'document',
                listClass: this.documentManager,
                detailsClass: this.documentDetails,
                sortFields: [
                    { value: 'id', label: 'Document ID' },
                    { value: 'name', label: 'Document Name' },
                    { value: 'file_type', label: 'File Type' },
                    { value: 'status', label: 'Status' },
                    { value: 'pages', label: 'Pages' },
                    { value: 'has_oversized', label: 'Has Oversized' },
                    { value: 'file_size', label: 'File Size' },
                    { value: 'project_id', label: 'Project ID' },
                    { value: 'roll_id', label: 'Roll ID' },
                    { value: 'creation_date', label: 'Creation Date' }
                ],
                advancedFields: [
                    { value: 'name', label: 'Document Name', group: 'Documents' },
                    { value: 'file_type', label: 'File Type', group: 'Documents' },
                    { value: 'status', label: 'Status', group: 'Documents' },
                    { value: 'pages', label: 'Pages', group: 'Documents' },
                    { value: 'project_id', label: 'Project ID', group: 'Documents' },
                    { value: 'roll_id', label: 'Roll ID', group: 'Documents' }
                ]
            },
            'temp-rolls': {
                name: 'Temp Rolls',
                icon: 'fas fa-clock',
                module: 'temp-roll',
                listClass: this.tempRollManager,
                detailsClass: this.tempRollManager.tempRollDetails,
                sortFields: [
                    { value: 'temp_roll_id', label: 'Temp Roll ID' },
                    { value: 'film_type', label: 'Film Type' },
                    { value: 'capacity', label: 'Capacity' },
                    { value: 'usable_capacity', label: 'Usable Capacity' },
                    { value: 'status', label: 'Status' },
                    { value: 'creation_date', label: 'Creation Date' }
                ],
                advancedFields: [
                    { value: 'film_type', label: 'Film Type', group: 'Temp Rolls' },
                    { value: 'capacity', label: 'Capacity', group: 'Temp Rolls' },
                    { value: 'usable_capacity', label: 'Usable Capacity', group: 'Temp Rolls' }
                ]
            }
        };
    }

    /**
     * Initialize the explore page
     */
    initialize() {
        console.log('Initializing explore page...');
        
        // Initialize model modules (setup only, no data loading)
        this.projectList.initialize();
        this.projectDetails.initialize();
        this.projectEdit.initialize();
        this.projectExport.initialize();
        
        // Initialize roll modules (setup only, no data loading)
        this.rollList.initialize();
        this.rollDetails.initialize();
        this.rollEdit.initialize();
        this.rollExport.initialize();
        
        // Initialize document modules (setup only, no data loading)
        this.documentManager.initialize();
        this.documentDetails.initialize();
        
        // Initialize temp roll modules (setup only, no data loading)
        this.tempRollManager.initialize();
        
        // Make this instance available globally for cross-module communication
        window.exploreMain = this;
        
        // Set up entity switching
        this.setupEntitySwitching();
        
        // Set up global event listeners
        this.setupEventListeners();
        
        // Initialize with projects by default (this will load only project data)
        this.switchEntity('projects');
    }

    /**
     * Set up entity switching functionality
     */
    setupEntitySwitching() {
        const entityOptions = document.querySelectorAll('.entity-option');
        
        entityOptions.forEach(option => {
            option.addEventListener('click', () => {
                // Update selection
                entityOptions.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                
                // Get selected entity
                const entity = option.getAttribute('data-entity');
                this.switchEntity(entity);
            });
        });
    }

    /**
     * Switch the current entity being viewed
     * @param {string} entity - Entity type (projects, rolls, documents, temp-rolls)
     */
    async switchEntity(entity) {
        console.log(`Switching to entity: ${entity}`);
        
        // Store current entity
        this.currentEntity = entity;
        
        // Show/hide entity-specific filters
        this.showEntityFilters(entity);
        
        // Show/hide entity-specific content
        this.showEntityContent(entity);
        
        // Update sort fields dropdown
        this.updateSortFields(entity);
        
        // Update advanced filter fields
        this.updateAdvancedFields(entity);
        
        // Load data for the entity
        this.loadEntityData(entity);
        
        // Set up event listeners for the current entity
        this.setupEntityEventListeners(entity);
    }

    /**
     * Show/hide entity-specific filters
     * @param {string} entity - Entity type
     */
    showEntityFilters(entity) {
        // Hide all entity filters
        const allFilters = document.querySelectorAll('.entity-filters');
        allFilters.forEach(filter => {
            filter.style.display = 'none';
            filter.classList.remove('active');
        });
        
        // Show the selected entity's filters
        const entityFilter = document.querySelector(`#${entity}-filters`);
        if (entityFilter) {
            entityFilter.style.display = 'block';
            entityFilter.classList.add('active');
        }
    }

    /**
     * Show/hide entity-specific content
     * @param {string} entity - Entity type
     */
    showEntityContent(entity) {
        // Hide all entity content
        const allContent = document.querySelectorAll('.entity-content');
        allContent.forEach(content => {
            content.style.display = 'none';
            content.classList.remove('active');
        });
        
        // Hide all entity action groups
        const allActions = document.querySelectorAll('.action-group');
        allActions.forEach(actionGroup => {
            actionGroup.style.display = 'none';
        });
        
        // Show the selected entity's content
        let entityContent;
        let entityActionsId;
        
        if (entity === 'temp-rolls') {
            // For temp-rolls, show the table view
            entityContent = document.querySelector('#temp-rolls-table-view');
            entityActionsId = 'temp-roll-actions';
        } else if (entity === 'documents') {
            // For documents, show the table view
            entityContent = document.querySelector('#documents-table-view');
            entityActionsId = 'document-actions';
        } else if (entity === 'projects') {
            // For projects, show the table view
            entityContent = document.querySelector('#projects-table-view');
            if (!entityContent) {
                // Fallback to content div
                entityContent = document.querySelector('#projects-content');
            }
            entityActionsId = 'project-actions';
        } else if (entity === 'rolls') {
            // For rolls, show the table view
            entityContent = document.querySelector('#rolls-table-view');
            if (!entityContent) {
                // Fallback to content div
                entityContent = document.querySelector('#rolls-content');
            }
            entityActionsId = 'roll-actions';
        } else {
            // For other entities, try the table view first
            entityContent = document.querySelector(`#${entity}-table-view`);
            if (!entityContent) {
                // Fallback to content div
                entityContent = document.querySelector(`#${entity}-content`);
            }
            // Use singular form for action ID
            const singularEntity = entity.endsWith('s') ? entity.slice(0, -1) : entity;
            entityActionsId = `${singularEntity}-actions`;
        }
        
        // Show entity-specific actions
        if (entityActionsId) {
            const entityActions = document.querySelector(`#${entityActionsId}`);
            if (entityActions) {
                entityActions.style.display = 'flex';
            }
        }
        
        if (entityContent) {
            entityContent.style.display = 'block';
            entityContent.classList.add('active');
        }
    }

    /**
     * Update sort field options based on entity
     * @param {string} entity - Entity type
     */
    updateSortFields(entity) {
        const sortFieldSelect = document.getElementById('sort-field');
        const config = this.entityConfigs[entity];
        
        if (!config || !sortFieldSelect) return;
        
        // Clear existing options
        sortFieldSelect.innerHTML = '';
        
        // Add new options
        config.sortFields.forEach(field => {
            const option = document.createElement('option');
            option.value = field.value;
            option.textContent = field.label;
            sortFieldSelect.appendChild(option);
        });
    }

    /**
     * Update advanced filter fields based on entity
     * @param {string} entity - Entity type
     */
    updateAdvancedFields(entity) {
        const conditionFieldSelect = document.querySelector('.condition-field');
        const config = this.entityConfigs[entity];
        
        if (!config || !conditionFieldSelect) return;
        
        // Clear existing options
        conditionFieldSelect.innerHTML = '<option value="">Select field</option>';
        
        // Group fields by category
        const groups = {};
        config.advancedFields.forEach(field => {
            if (!groups[field.group]) {
                groups[field.group] = [];
            }
            groups[field.group].push(field);
        });
        
        // Add grouped options
        Object.keys(groups).forEach(groupName => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = groupName;
            
            groups[groupName].forEach(field => {
                const option = document.createElement('option');
                option.value = field.value;
                option.textContent = field.label;
                optgroup.appendChild(option);
            });
            
            conditionFieldSelect.appendChild(optgroup);
        });
    }

    /**
     * Load data for the selected entity
     * @param {string} entity - Entity type
     */
    loadEntityData(entity) {
        const config = this.entityConfigs[entity];
        
        if (!config) {
            console.warn(`No configuration found for entity: ${entity}`);
            return;
        }

        if (entity === 'projects' && config.listClass && typeof config.listClass.loadProjects === 'function') {
            // For projects - load data and filter options
            config.listClass.loadProjects();
            
            // Load document types and locations for dropdowns
            if (typeof config.listClass.loadDocumentTypes === 'function') {
                config.listClass.loadDocumentTypes();
            }
            if (typeof config.listClass.loadLocations === 'function') {
                config.listClass.loadLocations();
            }
        } else if (entity === 'rolls' && config.listClass && typeof config.listClass.loadRolls === 'function') {
            // For rolls - load data and filter options
            config.listClass.loadRolls();
            
            // Load filter options for dropdowns
            if (typeof config.listClass.loadFilmTypes === 'function') {
                config.listClass.loadFilmTypes();
            }
            if (typeof config.listClass.loadStatuses === 'function') {
                config.listClass.loadStatuses();
            }
        } else if (entity === 'temp-rolls' && config.listClass && typeof config.listClass.loadTempRolls === 'function') {
            // For temp rolls - load data
            config.listClass.loadTempRolls();
        } else if (entity === 'documents' && config.listClass && typeof config.listClass.loadDocuments === 'function') {
            // For documents - load data
            config.listClass.loadDocuments();
        } else {
            // For entities without implementation yet
            this.showComingSoon(entity);
        }
    }

    /**
     * Show coming soon message for entities not yet implemented
     * @param {string} entity - Entity type
     */
    showComingSoon(entity) {
        const config = this.entityConfigs[entity];
            const tableBody = document.getElementById('results-body');
        const cardsContainer = document.getElementById('results-cards');
        
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="10">
                        <div class="coming-soon-message">
                            <i class="${config.icon}"></i>
                            <p>${config.name} management is coming soon!</p>
                        </div>
                    </td>
                </tr>
            `;
        }
            
        if (cardsContainer) {
            cardsContainer.innerHTML = `
                <div class="coming-soon-message">
                    <i class="${config.icon}"></i>
                    <p>${config.name} management is coming soon!</p>
                </div>
            `;
        }
            
            // Update result count
        const resultCount = document.getElementById('result-count');
        if (resultCount) {
            resultCount.textContent = '(0)';
        }
    }

    /**
     * Set up global event listeners
     */
    setupEventListeners() {
        // Listen for refresh events
        document.addEventListener('refreshProjects', () => {
            if (this.currentEntity === 'projects') {
                this.projectList.loadProjects();
            }
        });
        
        document.addEventListener('refreshRolls', () => {
            if (this.currentEntity === 'rolls') {
                this.rollList.loadRolls();
            }
        });
        
        document.addEventListener('refreshTempRolls', () => {
            if (this.currentEntity === 'temp-rolls') {
                this.tempRollManager.loadTempRolls();
            }
        });
        
        document.addEventListener('refreshDocuments', () => {
            if (this.currentEntity === 'documents') {
                this.documentManager.loadDocuments();
            }
        });
        
        // Listen for getSelected events
        document.addEventListener('getSelectedProjects', (event) => {
            const { callback } = event.detail;
            callback(this.projectList.selectedProjects);
        });
        
        document.addEventListener('getSelectedRolls', (event) => {
            const { callback } = event.detail;
            callback(this.rollList.selectedRolls);
        });
        
        document.addEventListener('getSelectedTempRolls', (event) => {
            const { callback } = event.detail;
            callback(this.tempRollManager.selectedTempRolls);
        });
        
        document.addEventListener('getSelectedDocuments', (event) => {
            const { callback } = event.detail;
            callback(this.documentManager.getSelectedDocuments());
        });
        
        // Listen for entity-specific detail events
        document.addEventListener('showProjectDetails', (event) => {
            const { projectId } = event.detail;
            this.projectDetails.showProjectDetails(projectId);
        });
        
        document.addEventListener('editProject', (event) => {
            const { projectId } = event.detail;
            this.projectEdit.editProject(projectId);
        });
        
        document.addEventListener('showRollDetails', (event) => {
            const { rollId } = event.detail;
            this.rollDetails.showDetails(rollId);
        });
        
        document.addEventListener('editRoll', (event) => {
            const { rollId } = event.detail;
            this.rollEdit.editRoll(rollId);
        });
        
        document.addEventListener('showTempRollDetails', (event) => {
            const { tempRollId } = event.detail;
            this.tempRollManager.tempRollDetails.showDetails(tempRollId);
        });
        
        document.addEventListener('editTempRoll', (event) => {
            const { tempRollId } = event.detail;
            this.tempRollManager.showEditModal(tempRollId);
        });
        
        document.addEventListener('showDocumentDetails', (event) => {
            const { documentId } = event.detail;
            this.documentDetails.showDetails(documentId);
        });
        
        document.addEventListener('editDocument', (event) => {
            const { documentId } = event.detail;
            this.documentManager.editDocument(documentId);
        });
        
        // Create button event listeners
        const createProjectBtn = document.getElementById('create-project');
        if (createProjectBtn) {
            createProjectBtn.addEventListener('click', () => {
                this.projectEdit.createProject();
            });
        }
        
        const createRollBtn = document.getElementById('create-roll');
        if (createRollBtn) {
            createRollBtn.addEventListener('click', () => {
                this.rollEdit.createRoll();
            });
        }
        
        const createDocumentBtn = document.getElementById('create-document');
        if (createDocumentBtn) {
            createDocumentBtn.addEventListener('click', () => {
                this.documentManager.showCreateModal();
            });
        }
        
        const createTempRollBtn = document.getElementById('create-temp-roll');
        if (createTempRollBtn) {
            createTempRollBtn.addEventListener('click', () => {
                this.tempRollManager.showCreateModal();
            });
        }
        
        const createFirstTempRollBtn = document.getElementById('create-first-temp-roll');
        if (createFirstTempRollBtn) {
            createFirstTempRollBtn.addEventListener('click', () => {
                this.tempRollManager.showCreateModal();
            });
        }
        
        // View control switching
        document.querySelectorAll('.view-control').forEach(control => {
            control.addEventListener('click', () => {
                // Update active view control
                document.querySelectorAll('.view-control').forEach(c => c.classList.remove('active'));
                control.classList.add('active');
                
                // Show corresponding view for current entity
                const view = control.getAttribute('data-view');
                const entity = this.currentEntity;
                
                // Hide all views for current entity
                document.querySelectorAll(`[data-entity="${entity}"]`).forEach(v => {
                    v.style.display = 'none';
                    v.classList.remove('active');
                });
                
                // Show the selected view for current entity
                const targetView = document.getElementById(`${entity}-${view}-view`);
                if (targetView) {
                    targetView.style.display = 'block';
                    targetView.classList.add('active');
                }
            });
        });
    }

    /**
     * Get the current entity configuration
     * @returns {Object} - Current entity configuration
     */
    getCurrentEntityConfig() {
        return this.entityConfigs[this.currentEntity];
    }

    /**
     * Get the current entity list module
     * @returns {Object} - Current entity list module
     */
    getCurrentListModule() {
        const config = this.getCurrentEntityConfig();
        return config ? config.listClass : null;
    }

    /**
     * Get the current entity export module
     * @returns {Object} - Current entity export module
     */
    getCurrentExportModule() {
        const config = this.getCurrentEntityConfig();
        return config ? config.exportClass : null;
    }

    /**
     * Set up event listeners for the current entity
     * @param {string} entity - Entity type
     */
    setupEntityEventListeners(entity) {
        const config = this.entityConfigs[entity];
        if (config && config.listClass && config.listClass.setupEventListeners) {
            config.listClass.setupEventListeners();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const exploreMain = new ExploreMain();
    exploreMain.initialize();
}); 