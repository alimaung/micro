/**
 * explore-main.js - Main orchestrator for the explore page
 * Handles switching between different model modules and common functionality
 */

class ExploreMain {
    constructor() {
        // Initialize model modules
        this.projectList = new ProjectList();
        this.projectDetails = new ProjectDetails();
        this.projectEdit = new ProjectEdit();
        this.projectExport = new ProjectExport();
        
        // Current entity being viewed
        this.currentEntity = 'projects';
    }

    /**
     * Initialize the explore page
     */
    initialize() {
        console.log('Initializing explore page...');
        
        // Initialize model modules
        this.projectList.initialize();
        this.projectDetails.initialize();
        this.projectEdit.initialize();
        this.projectExport.initialize();
        
        // Set up entity switching
        this.setupEntitySwitching();
        
        // Set up global event listeners
        this.setupEventListeners();
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
    switchEntity(entity) {
        // Store current entity
        this.currentEntity = entity;
        
        // Show corresponding entity filters
        document.querySelectorAll('.entity-filters').forEach(filter => {
            filter.classList.remove('active');
        });
        document.getElementById(`${entity}-filters`).classList.add('active');
        
        // Update table headers for the entity
        this.updateTableHeaders(entity);
        
        // Show/hide batch operations based on entity
        if (entity === 'projects') {
            document.getElementById('batch-operations').style.display = 'flex';
        } else {
            document.getElementById('batch-operations').style.display = 'none';
        }
        
        // Load entity data
        this.loadEntityData(entity);
    }

    /**
     * Update table headers based on entity
     * @param {string} entity - Entity type
     */
    updateTableHeaders(entity) {
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

    /**
     * Load data for the selected entity
     * @param {string} entity - Entity type
     */
    loadEntityData(entity) {
        if (entity === 'projects') {
            this.projectList.loadProjects();
        } else {
            // For now, just show a message for other entities
            const tableBody = document.getElementById('results-body');
            tableBody.innerHTML = `
                <tr>
                    <td colspan="${entity === 'rolls' || entity === 'temp-rolls' ? 7 : 7}">
                        <div class="coming-soon-message">
                            ${entity.charAt(0).toUpperCase() + entity.slice(1)} management is coming soon!
                        </div>
                    </td>
                </tr>
            `;
            
            const cardsContainer = document.getElementById('results-cards');
            cardsContainer.innerHTML = `
                <div class="coming-soon-message">
                    <i class="fas fa-tools"></i>
                    <p>${entity.charAt(0).toUpperCase() + entity.slice(1)} management is coming soon!</p>
                </div>
            `;
            
            // Update result count
            document.getElementById('result-count').textContent = '(0)';
        }
    }

    /**
     * Set up global event listeners
     */
    setupEventListeners() {
        // Listen for refreshProjects events
        document.addEventListener('refreshProjects', () => {
            if (this.currentEntity === 'projects') {
                this.projectList.loadProjects();
            }
        });
        
        // Listen for getSelectedProjects events
        document.addEventListener('getSelectedProjects', (event) => {
            const { callback } = event.detail;
            callback(this.projectList.selectedProjects);
        });
        
        // Add new project button
        const addButton = document.createElement('button');
        addButton.id = 'add-project-btn';
        addButton.className = 'primary-button';
        addButton.innerHTML = '<i class="fas fa-plus"></i> Add Project';
        
        // Find the header to add the button to
        const resultsHeader = document.querySelector('.results-panel .panel-header');
        if (resultsHeader) {
            resultsHeader.appendChild(addButton);
        }
        
        // Add event listener to create new project
        addButton.addEventListener('click', () => {
            this.projectEdit.createProject();
        });
        
        // Toggle advanced filters
        const toggleAdvancedButton = document.getElementById('toggle-advanced');
        const advancedFilters = document.getElementById('advanced-filters');
        
        if (toggleAdvancedButton && advancedFilters) {
            toggleAdvancedButton.addEventListener('click', () => {
                advancedFilters.classList.toggle('visible');
                toggleAdvancedButton.classList.toggle('active');
            });
        }
        
        // View controls
        const viewControls = document.querySelectorAll('.view-control');
        const resultViews = document.querySelectorAll('.result-view');
        
        viewControls.forEach(control => {
            control.addEventListener('click', () => {
                const view = control.getAttribute('data-view');
                
                // Update control buttons
                viewControls.forEach(ctrl => ctrl.classList.remove('active'));
                control.classList.add('active');
                
                // Update view
                resultViews.forEach(v => v.classList.remove('active'));
                document.getElementById(`${view}-view`).classList.add('active');
            });
        });
    }
}

// Initialize the explore page when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const exploreMain = new ExploreMain();
    exploreMain.initialize();
}); 