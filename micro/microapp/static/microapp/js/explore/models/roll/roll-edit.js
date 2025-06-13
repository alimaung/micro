/**
 * roll-edit.js - Roll editing functionality
 * Handles creating and editing rolls
 */

class RollEdit {
    constructor() {
        this.dbService = new DatabaseService();
        this.currentRollId = null;
        this.isEditing = false;
        this.modal = null;
    }

    /**
     * Initialize the roll edit module
     */
    initialize() {
        this.createEditModal();
        this.setupEventListeners();
    }

    /**
     * Create the edit modal if it doesn't exist
     */
    createEditModal() {
        // Check if modal already exists
        if (document.getElementById('edit-roll-modal')) {
            this.modal = document.getElementById('edit-roll-modal');
            return;
        }

        // Create modal element
        const modalHtml = `
            <div id="edit-roll-modal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 id="edit-roll-title">Edit Roll</h2>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="roll-edit-form">
                            <div class="form-grid">
                                <div class="form-section">
                                    <h3>Basic Information</h3>
                                    
                                    <div class="form-group">
                                        <label for="edit-roll-id">Roll Number:</label>
                                        <input type="text" id="edit-roll-id" name="roll_id" placeholder="Enter roll number">
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-film-number">Film Number:</label>
                                        <input type="text" id="edit-film-number" name="film_number" placeholder="Enter film number">
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-film-type">Film Type:</label>
                                        <select id="edit-film-type" name="film_type" required>
                                            <option value="16mm">16mm</option>
                                            <option value="35mm">35mm</option>
                                        </select>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-project-id">Project:</label>
                                        <select id="edit-project-id" name="project_id" required>
                                            <option value="">Select Project</option>
                                            <!-- Will be populated by JavaScript -->
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <h3>Capacity & Usage</h3>
                                    
                                    <div class="form-group">
                                        <label for="edit-capacity">Total Capacity:</label>
                                        <input type="number" id="edit-capacity" name="capacity" min="0" placeholder="Enter capacity">
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-pages-used">Pages Used:</label>
                                        <input type="number" id="edit-pages-used" name="pages_used" min="0" placeholder="Enter pages used">
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-pages-remaining">Pages Remaining:</label>
                                        <input type="number" id="edit-pages-remaining" name="pages_remaining" min="0" placeholder="Auto-calculated" readonly>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-remaining-capacity">Remaining Capacity:</label>
                                        <input type="number" id="edit-remaining-capacity" name="remaining_capacity" min="0" placeholder="Enter remaining capacity">
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-usable-capacity">Usable Capacity:</label>
                                        <input type="number" id="edit-usable-capacity" name="usable_capacity" min="0" placeholder="Enter usable capacity">
                                    </div>
                                </div>
                                
                                <div class="form-section">
                                    <h3>Status & Properties</h3>
                                    
                                    <div class="form-group">
                                        <label for="edit-status">Status:</label>
                                        <select id="edit-status" name="status">
                                            <option value="active">Active</option>
                                            <option value="full">Full</option>
                                            <option value="partial">Partial</option>
                                            <option value="used">Used</option>
                                            <option value="archived">Archived</option>
                                        </select>
                                    </div>
                                    
                                    <div class="form-group checkbox-group">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="edit-has-split-documents" name="has_split_documents">
                                            <span>Has Split Documents</span>
                                        </label>
                                    </div>
                                    
                                    <div class="form-group checkbox-group">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="edit-is-partial" name="is_partial">
                                            <span>Is Partial</span>
                                        </label>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="edit-film-number-source">Film Number Source:</label>
                                        <input type="text" id="edit-film-number-source" name="film_number_source" placeholder="Enter film number source">
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="secondary-button close-modal">Cancel</button>
                        <button type="button" id="save-roll-btn" class="primary-button">Save Roll</button>
                    </div>
                </div>
            </div>
        `;

        // Append modal to body
        const modalWrapper = document.createElement('div');
        modalWrapper.innerHTML = modalHtml;
        document.body.appendChild(modalWrapper.firstElementChild);

        // Get modal element
        this.modal = document.getElementById('edit-roll-modal');
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Close modal events
        this.modal.querySelectorAll('.close-modal').forEach(button => {
            button.addEventListener('click', () => {
                this.hideEditModal();
            });
        });

        // Save button
        document.getElementById('save-roll-btn').addEventListener('click', () => {
            this.saveRoll();
        });

        // Auto-calculate pages remaining
        document.getElementById('edit-capacity').addEventListener('input', this.calculatePagesRemaining.bind(this));
        document.getElementById('edit-pages-used').addEventListener('input', this.calculatePagesRemaining.bind(this));

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideEditModal();
            }
        });
    }

    /**
     * Create a new roll
     */
    async createRoll() {
        this.isEditing = false;
        this.currentRollId = null;
        
        // Update modal title
        document.getElementById('edit-roll-title').textContent = 'Create New Roll';
        
        // Clear form
        this.clearForm();
        
        // Load projects for selection
        await this.loadProjects();
        
        // Show modal
        this.modal.style.display = 'flex';
    }

    /**
     * Edit an existing roll
     * @param {number|string} rollId - Roll ID
     */
    async editRoll(rollId) {
        this.isEditing = true;
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
            
            console.log('Roll data received for editing:', roll); // Debug log
            
            // Update modal title
            const rollTitle = roll.film_number || roll.roll_id || `#${roll.id}`;
            document.getElementById('edit-roll-title').textContent = `Edit Roll - ${rollTitle}`;
            
            // Load projects for selection
            await this.loadProjects();
            
            // Populate form with roll data
            this.populateForm(roll);
            
            // Show modal
            this.modal.style.display = 'flex';
            
        } catch (error) {
            console.error('Error loading roll for editing:', error);
            console.error('Roll ID:', rollId); // Debug log
            alert(`Error loading roll: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Hide the edit modal
     */
    hideEditModal() {
        this.modal.style.display = 'none';
        this.currentRollId = null;
        this.isEditing = false;
    }

    /**
     * Clear the form
     */
    clearForm() {
        const form = document.getElementById('roll-edit-form');
        form.reset();
        
        // Set default values
        document.getElementById('edit-film-type').value = '16mm';
        document.getElementById('edit-status').value = 'active';
        document.getElementById('edit-capacity').value = '2900'; // Default capacity
    }

    /**
     * Populate form with roll data
     * @param {Object} roll - Roll data
     */
    populateForm(roll) {
        document.getElementById('edit-roll-id').value = roll.roll_id || '';
        document.getElementById('edit-film-number').value = roll.film_number || '';
        document.getElementById('edit-film-type').value = roll.film_type || '16mm';
        document.getElementById('edit-project-id').value = roll.project_id || '';
        document.getElementById('edit-capacity').value = roll.capacity || '';
        document.getElementById('edit-pages-used').value = roll.pages_used || '';
        document.getElementById('edit-pages-remaining').value = roll.pages_remaining || '';
        document.getElementById('edit-remaining-capacity').value = roll.remaining_capacity || '';
        document.getElementById('edit-usable-capacity').value = roll.usable_capacity || '';
        document.getElementById('edit-status').value = roll.status || 'active';
        document.getElementById('edit-has-split-documents').checked = roll.has_split_documents || false;
        document.getElementById('edit-is-partial').checked = roll.is_partial || false;
        document.getElementById('edit-film-number-source').value = roll.film_number_source || '';
    }

    /**
     * Load projects for the project selection dropdown
     */
    async loadProjects() {
        try {
            const response = await this.dbService.listProjects({}, 1, 1000); // Get all projects
            const projects = response.results;
            
            const projectSelect = document.getElementById('edit-project-id');
            
            // Clear existing options except the first one
            while (projectSelect.options.length > 1) {
                projectSelect.remove(1);
            }
            
            // Add project options
            projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.id;
                option.textContent = `${project.archive_id} - ${project.location}`;
                projectSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    /**
     * Calculate pages remaining based on capacity and pages used
     */
    calculatePagesRemaining() {
        const capacity = parseInt(document.getElementById('edit-capacity').value) || 0;
        const pagesUsed = parseInt(document.getElementById('edit-pages-used').value) || 0;
        const pagesRemaining = Math.max(0, capacity - pagesUsed);
        
        document.getElementById('edit-pages-remaining').value = pagesRemaining;
    }

    /**
     * Save the roll (create or update)
     */
    async saveRoll() {
        const form = document.getElementById('roll-edit-form');
        const formData = new FormData(form);
        
        // Convert FormData to object
        const rollData = {};
        for (let [key, value] of formData.entries()) {
            if (key === 'has_split_documents' || key === 'is_partial') {
                rollData[key] = document.getElementById(`edit-${key.replace('_', '-')}`).checked;
            } else if (key === 'capacity' || key === 'pages_used' || key === 'pages_remaining' || 
                      key === 'remaining_capacity' || key === 'usable_capacity' || key === 'project_id') {
                rollData[key] = value ? parseInt(value) : null;
            } else {
                rollData[key] = value || null;
            }
        }
        
        // Validate required fields
        if (!rollData.project_id) {
            alert('Please select a project.');
            return;
        }
        
        if (!rollData.film_type) {
            alert('Please select a film type.');
            return;
        }
        
        // Show loading state
        const saveBtn = document.getElementById('save-roll-btn');
        const originalBtnText = saveBtn.textContent;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        saveBtn.disabled = true;
        
        try {
            if (this.isEditing) {
                // Update existing roll
                await this.dbService.updateRoll(this.currentRollId, rollData);
                alert('Roll updated successfully!');
            } else {
                // Create new roll
                await this.dbService.createRoll(rollData);
                alert('Roll created successfully!');
            }
            
            // Hide modal
            this.hideEditModal();
            
            // Refresh the roll list
            const refreshEvent = new CustomEvent('refreshRolls');
            document.dispatchEvent(refreshEvent);
            
        } catch (error) {
            console.error('Error saving roll:', error);
            alert(`Error saving roll: ${error.message || 'Unknown error'}`);
        } finally {
            // Reset button
            saveBtn.textContent = originalBtnText;
            saveBtn.disabled = false;
        }
    }
}

// Export the class for use in the main module
window.RollEdit = RollEdit;