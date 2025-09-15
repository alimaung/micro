/**
 * project-edit.js - Project editing functionality
 * Handles editing and updating project information
 */

class ProjectEdit {
    constructor() {
        this.dbService = new DatabaseService();
        this.modal = null;
        this.form = null;
        this.currentProject = null;
        this.isEditing = false;
    }

    /**
     * Initialize the project edit module
     */
    initialize() {
        // Create edit modal if it doesn't exist
        this.createEditModal();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Create the edit modal if it doesn't exist in the DOM
     */
    createEditModal() {
        // Check if modal already exists
        if (document.getElementById('edit-project-modal')) {
            this.modal = document.getElementById('edit-project-modal');
            this.form = document.getElementById('edit-project-form');
            return;
        }
        
        // Create modal element
        const modalHtml = `
            <div id="edit-project-modal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 id="edit-modal-title">Edit Project</h2>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="edit-project-form">
                            <div class="form-grid">
                                <div class="form-group">
                                    <label for="edit-archive-id">Archive ID</label>
                                    <input type="text" id="edit-archive-id" name="archive_id" required 
                                           placeholder="Format: RRDxxx-yyyy">
                                    <div class="field-hint">Format: RRDxxx-yyyy</div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-location">Location</label>
                                    <select id="edit-location" name="location" required>
                                        <option value="">Select Location</option>
                                        <option value="OU">OU</option>
                                        <option value="DW">DW</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-doc-type">Document Type</label>
                                    <input type="text" id="edit-doc-type" name="doc_type" 
                                           placeholder="Document type (optional)">
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-project-path">Project Path</label>
                                    <input type="text" id="edit-project-path" name="project_path" required
                                           placeholder="Full path to project folder">
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-project-folder-name">Folder Name</label>
                                    <input type="text" id="edit-project-folder-name" name="project_folder_name" required
                                           placeholder="Project folder name">
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-pdf-folder-path">PDF Folder Path</label>
                                    <input type="text" id="edit-pdf-folder-path" name="pdf_folder_path"
                                           placeholder="Path to PDF folder (optional)">
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-comlist-path">Comlist Path</label>
                                    <input type="text" id="edit-comlist-path" name="comlist_path"
                                           placeholder="Path to comlist Excel file (optional)">
                                </div>
                                
                                <div class="form-group">
                                    <label for="edit-output-dir">Output Directory</label>
                                    <input type="text" id="edit-output-dir" name="output_dir"
                                           placeholder="Output directory (optional)">
                                </div>
                                
                                <div class="form-group checkbox-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="edit-has-pdf-folder" name="has_pdf_folder">
                                        Has PDF Folder
                                    </label>
                                </div>
                                
                                <div class="form-group checkbox-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="edit-processing-complete" name="processing_complete">
                                        Processing Complete
                                    </label>
                                </div>
                                
                                <div class="form-group checkbox-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="edit-retain-sources" name="retain_sources">
                                        Retain Sources
                                    </label>
                                </div>
                                
                                <div class="form-group checkbox-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="edit-add-to-database" name="add_to_database">
                                        Add to Database
                                    </label>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="secondary-button close-modal">Cancel</button>
                        <button id="save-project-btn" class="primary-button">Save Project</button>
                    </div>
                </div>
            </div>
        `;
        
        // Append modal to body
        const modalWrapper = document.createElement('div');
        modalWrapper.innerHTML = modalHtml;
        document.body.appendChild(modalWrapper.firstElementChild);
        
        // Get modal elements
        this.modal = document.getElementById('edit-project-modal');
        this.form = document.getElementById('edit-project-form');
    }

    /**
     * Set up event listeners for the edit modal
     */
    setupEventListeners() {
        // Listen for editProject events
        document.addEventListener('editProject', (event) => {
            const { projectId } = event.detail;
            this.editProject(projectId);
        });
        
        // Save button
        document.getElementById('save-project-btn').addEventListener('click', () => {
            this.saveProject();
        });
        
        // Close modal buttons
        this.modal.querySelectorAll('.close-modal').forEach(button => {
            button.addEventListener('click', () => {
                this.modal.style.display = 'none';
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
        
        // Form validation
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProject();
        });
        
        // Auto-update folder name when path changes
        document.getElementById('edit-project-path').addEventListener('blur', (e) => {
            const path = e.target.value.trim();
            const folderNameInput = document.getElementById('edit-project-folder-name');
            
            // Only auto-fill if the folder name is empty
            if (path && !folderNameInput.value) {
                // Extract folder name from path
                const parts = path.split(/[/\\]/);
                const folderName = parts[parts.length - 1];
                folderNameInput.value = folderName;
            }
        });
        
        // Toggle PDF folder path based on checkbox
        document.getElementById('edit-has-pdf-folder').addEventListener('change', (e) => {
            const pdfFolderInput = document.getElementById('edit-pdf-folder-path');
            
            if (e.target.checked) {
                pdfFolderInput.removeAttribute('disabled');
            } else {
                pdfFolderInput.setAttribute('disabled', 'disabled');
                pdfFolderInput.value = '';
            }
        });
    }

    /**
     * Edit a project
     * @param {string|number} projectId - ID of the project to edit
     */
    async editProject(projectId) {
        // Set editing flag
        this.isEditing = true;
        
        // Update modal title
        document.getElementById('edit-modal-title').textContent = 'Edit Project';
        
        try {
            // Fetch project data
            const response = await this.dbService.getProject(projectId);
            const project = response.project;
            
            // Store current project
            this.currentProject = project;
            
            // Populate form with project data
            this.populateForm(project);
            
            // Show the modal
            this.modal.style.display = 'flex';
        } catch (error) {
            console.error("Error loading project for editing:", error);
            alert(`Error loading project: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Create a new project
     */
    createProject() {
        // Set editing flag to false (creating)
        this.isEditing = false;
        
        // Update modal title
        document.getElementById('edit-modal-title').textContent = 'Create Project';
        
        // Reset form
        this.form.reset();
        
        // Set default values
        document.getElementById('edit-retain-sources').checked = true;
        document.getElementById('edit-add-to-database').checked = true;
        
        // Show the modal
        this.modal.style.display = 'flex';
    }

    /**
     * Populate form with project data
     * @param {Object} project - Project data to populate form with
     */
    populateForm(project) {
        // Reset the form first
        this.form.reset();
        
        // Set field values
        document.getElementById('edit-archive-id').value = project.archive_id || '';
        document.getElementById('edit-location').value = project.location || '';
        document.getElementById('edit-doc-type').value = project.doc_type || '';
        document.getElementById('edit-project-path').value = project.project_path || '';
        document.getElementById('edit-project-folder-name').value = project.project_folder_name || '';
        document.getElementById('edit-pdf-folder-path').value = project.pdf_folder_path || '';
        document.getElementById('edit-comlist-path').value = project.comlist_path || '';
        document.getElementById('edit-output-dir').value = project.output_dir || '';
        
        // Set checkbox values
        document.getElementById('edit-has-pdf-folder').checked = project.has_pdf_folder || false;
        document.getElementById('edit-processing-complete').checked = project.processing_complete || false;
        document.getElementById('edit-retain-sources').checked = project.retain_sources !== false; // Default to true
        document.getElementById('edit-add-to-database').checked = project.add_to_database !== false; // Default to true
        
        // Enable/disable PDF folder path based on has_pdf_folder
        const pdfFolderInput = document.getElementById('edit-pdf-folder-path');
        if (project.has_pdf_folder) {
            pdfFolderInput.removeAttribute('disabled');
        } else {
            pdfFolderInput.setAttribute('disabled', 'disabled');
        }
    }

    /**
     * Save project (create or update)
     */
    async saveProject() {
        // Validate form
        if (!this.validateForm()) {
            return;
        }
        
        // Collect form data
        const formData = this.collectFormData();
        
        try {
            let response;
            
            if (this.isEditing) {
                // Update existing project
                response = await this.dbService.updateProject(this.currentProject.project_id, formData);
                alert("Project updated successfully!");
            } else {
                // Create new project
                response = await this.dbService.createProject(formData);
                alert("Project created successfully!");
            }
            
            // Hide the modal
            this.modal.style.display = 'none';
            
            // Refresh the projects list
            const refreshProjectsEvent = new CustomEvent('refreshProjects');
            document.dispatchEvent(refreshProjectsEvent);
            
        } catch (error) {
            console.error("Error saving project:", error);
            alert(`Error saving project: ${error.message || 'Unknown error'}`);
        }
    }

    /**
     * Validate the edit form
     * @returns {boolean} - Whether the form is valid
     */
    validateForm() {
        // Required fields
        const requiredFields = [
            { id: 'edit-archive-id', name: 'Archive ID' },
            { id: 'edit-location', name: 'Location' },
            { id: 'edit-project-path', name: 'Project Path' },
            { id: 'edit-project-folder-name', name: 'Folder Name' }
        ];
        
        // Check required fields
        for (const field of requiredFields) {
            const input = document.getElementById(field.id);
            if (!input.value.trim()) {
                alert(`${field.name} is required.`);
                input.focus();
                return false;
            }
        }
        
        // Validate archive ID format (RRDxxx-yyyy)
        const archiveIdInput = document.getElementById('edit-archive-id');
        const archiveIdPattern = /^[A-Z]{3}\d{3}-\d{4}$/;
        
        if (!archiveIdPattern.test(archiveIdInput.value)) {
            alert('Archive ID must be in the format RRDxxx-yyyy');
            archiveIdInput.focus();
            return false;
        }
        
        // If has_pdf_folder is checked, pdf_folder_path is required
        const hasPdfFolder = document.getElementById('edit-has-pdf-folder').checked;
        const pdfFolderPath = document.getElementById('edit-pdf-folder-path').value.trim();
        
        if (hasPdfFolder && !pdfFolderPath) {
            alert('PDF Folder Path is required when Has PDF Folder is checked.');
            document.getElementById('edit-pdf-folder-path').focus();
            return false;
        }
        
        return true;
    }

    /**
     * Collect form data into an object
     * @returns {Object} - Form data object
     */
    collectFormData() {
        const formData = {
            archive_id: document.getElementById('edit-archive-id').value.trim(),
            location: document.getElementById('edit-location').value,
            doc_type: document.getElementById('edit-doc-type').value.trim(),
            project_path: document.getElementById('edit-project-path').value.trim(),
            project_folder_name: document.getElementById('edit-project-folder-name').value.trim(),
            pdf_folder_path: document.getElementById('edit-pdf-folder-path').value.trim(),
            comlist_path: document.getElementById('edit-comlist-path').value.trim(),
            output_dir: document.getElementById('edit-output-dir').value.trim(),
            has_pdf_folder: document.getElementById('edit-has-pdf-folder').checked,
            processing_complete: document.getElementById('edit-processing-complete').checked,
            retain_sources: document.getElementById('edit-retain-sources').checked,
            add_to_database: document.getElementById('edit-add-to-database').checked
        };
        
        // Remove empty strings
        Object.keys(formData).forEach(key => {
            if (formData[key] === '') {
                formData[key] = null;
            }
        });
        
        return formData;
    }
}

// Export the class for use in the main module
window.ProjectEdit = ProjectEdit; 