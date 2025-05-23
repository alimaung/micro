/**
 * project-export.js - Project export functionality
 * Handles exporting project data in various formats
 */

class ProjectExport {
    constructor() {
        this.dbService = new DatabaseService();
        this.modal = null;
    }

    /**
     * Initialize the project export module
     */
    initialize() {
        // Create export modal if it doesn't exist
        this.createExportModal();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Create the export modal if it doesn't exist in the DOM
     */
    createExportModal() {
        // Check if modal already exists
        if (document.getElementById('export-project-modal')) {
            this.modal = document.getElementById('export-project-modal');
            return;
        }
        
        // Create modal element
        const modalHtml = `
            <div id="export-project-modal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 id="export-modal-title">Export Projects</h2>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="export-options">
                            <div class="export-section">
                                <h3>Export Scope</h3>
                                <div class="radio-group">
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="selected" checked>
                                        Selected Projects (<span id="selected-count">0</span>)
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="filtered">
                                        All Filtered Projects (<span id="filtered-count">0</span>)
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="all">
                                        All Projects
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section">
                                <h3>Export Format</h3>
                                <div class="radio-group format-options">
                                    <label class="radio-label format-option">
                                        <input type="radio" name="export-format" value="csv" checked>
                                        <div class="format-icon">
                                            <i class="fas fa-file-csv"></i>
                                            <span>CSV</span>
                                        </div>
                                    </label>
                                    <label class="radio-label format-option">
                                        <input type="radio" name="export-format" value="excel">
                                        <div class="format-icon">
                                            <i class="fas fa-file-excel"></i>
                                            <span>Excel</span>
                                        </div>
                                    </label>
                                    <label class="radio-label format-option">
                                        <input type="radio" name="export-format" value="pdf">
                                        <div class="format-icon">
                                            <i class="fas fa-file-pdf"></i>
                                            <span>PDF</span>
                                        </div>
                                    </label>
                                    <label class="radio-label format-option">
                                        <input type="radio" name="export-format" value="json">
                                        <div class="format-icon">
                                            <i class="fas fa-file-code"></i>
                                            <span>JSON</span>
                                        </div>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section">
                                <h3>Fields to Include</h3>
                                <div class="checkbox-grid">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="project_id" checked>
                                        Project ID
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="archive_id" checked>
                                        Archive ID
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="location" checked>
                                        Location
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="doc_type" checked>
                                        Document Type
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="project_path">
                                        Project Path
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="project_folder_name">
                                        Folder Name
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="pdf_folder_path">
                                        PDF Folder Path
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="has_pdf_folder" checked>
                                        Has PDF Folder
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="has_oversized" checked>
                                        Has Oversized
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="documents_with_oversized">
                                        Oversized Documents
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="total_oversized">
                                        Total Oversized
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="total_pages" checked>
                                        Total Pages
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="total_pages_with_refs">
                                        Pages with References
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="processing_complete" checked>
                                        Processing Complete
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="film_allocation_complete" checked>
                                        Film Allocation Complete
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="distribution_complete">
                                        Distribution Complete
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="created_at" checked>
                                        Date Created
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="updated_at">
                                        Last Updated
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-csv format-specific-options">
                                <h3>CSV Options</h3>
                                <div class="form-group">
                                    <label for="csv-delimiter">Delimiter</label>
                                    <select id="csv-delimiter">
                                        <option value="comma" selected>Comma (,)</option>
                                        <option value="semicolon">Semicolon (;)</option>
                                        <option value="tab">Tab</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="csv-include-header" checked>
                                        Include Header Row
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-excel format-specific-options">
                                <h3>Excel Options</h3>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="excel-autofilter" checked>
                                        Add Auto-Filter
                                    </label>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="excel-freeze-header" checked>
                                        Freeze Header Row
                                    </label>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="excel-include-stats">
                                        Include Summary Statistics
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-pdf format-specific-options">
                                <h3>PDF Options</h3>
                                <div class="form-group">
                                    <label for="pdf-page-size">Page Size</label>
                                    <select id="pdf-page-size">
                                        <option value="a4" selected>A4</option>
                                        <option value="letter">Letter</option>
                                        <option value="legal">Legal</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="pdf-orientation">Orientation</label>
                                    <select id="pdf-orientation">
                                        <option value="portrait">Portrait</option>
                                        <option value="landscape" selected>Landscape</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="pdf-include-header-footer" checked>
                                        Include Header & Footer
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-json format-specific-options">
                                <h3>JSON Options</h3>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="json-pretty-print" checked>
                                        Pretty Print (Formatted)
                                    </label>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="json-include-metadata" checked>
                                        Include Export Metadata
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="secondary-button close-modal">Cancel</button>
                        <button id="start-export-btn" class="primary-button">Export</button>
                    </div>
                </div>
            </div>
        `;
        
        // Append modal to body
        const modalWrapper = document.createElement('div');
        modalWrapper.innerHTML = modalHtml;
        document.body.appendChild(modalWrapper.firstElementChild);
        
        // Get modal element
        this.modal = document.getElementById('export-project-modal');
    }

    /**
     * Set up event listeners for the export modal
     */
    setupEventListeners() {
        // Export button click event
        document.querySelectorAll('.export-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const format = e.currentTarget.id.split('-')[1]; // extract format from button id
                this.openExportModal(format);
            });
        });
        
        // Close modal buttons
        this.modal.querySelectorAll('.close-modal').forEach(button => {
            button.addEventListener('click', () => {
                this.modal.style.display = 'none';
            });
        });
        
        // Format radio buttons change event
        this.modal.querySelectorAll('input[name="export-format"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateFormatOptions();
            });
        });
        
        // Start export button
        document.getElementById('start-export-btn').addEventListener('click', () => {
            this.startExport();
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
        
        // Select/deselect all fields
        const selectAllBtn = document.createElement('button');
        selectAllBtn.className = 'select-all-btn';
        selectAllBtn.textContent = 'Select All';
        selectAllBtn.addEventListener('click', () => {
            const checkboxes = this.modal.querySelectorAll('input[name="export-fields"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });
        
        const deselectAllBtn = document.createElement('button');
        deselectAllBtn.className = 'deselect-all-btn';
        deselectAllBtn.textContent = 'Deselect All';
        deselectAllBtn.addEventListener('click', () => {
            const checkboxes = this.modal.querySelectorAll('input[name="export-fields"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        });
        
        // Add buttons after the "Fields to Include" heading
        const fieldsHeading = this.modal.querySelector('.export-section:nth-child(3) h3');
        const buttonWrapper = document.createElement('div');
        buttonWrapper.className = 'field-selection-buttons';
        buttonWrapper.appendChild(selectAllBtn);
        buttonWrapper.appendChild(deselectAllBtn);
        fieldsHeading.appendChild(buttonWrapper);
    }

    /**
     * Open the export modal with a specific format pre-selected
     * @param {string} format - Export format (csv, excel, pdf, json)
     * @param {Set<string>} selectedProjects - Set of selected project IDs
     * @param {number} filteredCount - Number of projects in filtered view
     */
    openExportModal(format, selectedProjects = new Set(), filteredCount = 0) {
        // Update selected format
        const formatRadio = this.modal.querySelector(`input[name="export-format"][value="${format}"]`);
        if (formatRadio) {
            formatRadio.checked = true;
        }
        
        // Update counts
        document.getElementById('selected-count').textContent = selectedProjects.size;
        document.getElementById('filtered-count').textContent = filteredCount;
        
        // Disable selected projects option if none selected
        const selectedOption = this.modal.querySelector('input[name="export-scope"][value="selected"]');
        if (selectedProjects.size === 0) {
            selectedOption.disabled = true;
            this.modal.querySelector('input[name="export-scope"][value="filtered"]').checked = true;
        } else {
            selectedOption.disabled = false;
            selectedOption.checked = true;
        }
        
        // Update format-specific options
        this.updateFormatOptions();
        
        // Show the modal
        this.modal.style.display = 'flex';
    }

    /**
     * Update format-specific options based on selected format
     */
    updateFormatOptions() {
        // Hide all format-specific options
        this.modal.querySelectorAll('.format-specific-options').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show options for selected format
        const selectedFormat = this.modal.querySelector('input[name="export-format"]:checked').value;
        const formatOptions = this.modal.querySelector(`.format-options-${selectedFormat}`);
        if (formatOptions) {
            formatOptions.style.display = 'block';
        }
    }

    /**
     * Start the export process
     */
    async startExport() {
        // Get export scope
        const scope = this.modal.querySelector('input[name="export-scope"]:checked').value;
        
        // Get selected format
        const format = this.modal.querySelector('input[name="export-format"]:checked').value;
        
        // Get selected fields
        const fields = Array.from(
            this.modal.querySelectorAll('input[name="export-fields"]:checked')
        ).map(checkbox => checkbox.value);
        
        // Get format-specific options
        const options = this.getFormatOptions(format);
        
        // Get project IDs based on scope
        let projectIds = [];
        let useFilters = false;
        
        if (scope === 'selected') {
            // Get selected project IDs from parent component
            const selectedProjectsEvent = new CustomEvent('getSelectedProjects', {
                detail: { callback: (selectedProjects) => {
                    projectIds = Array.from(selectedProjects);
                }}
            });
            document.dispatchEvent(selectedProjectsEvent);
        } else if (scope === 'filtered') {
            // Use current filters
            useFilters = true;
        }
        
        // Show loading state
        const exportBtn = document.getElementById('start-export-btn');
        const originalBtnText = exportBtn.textContent;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        exportBtn.disabled = true;
        
        try {
            // Call export method on database service
            const exportParams = {
                projectIds,
                format,
                fields,
                options,
                useFilters
            };
            
            const blob = await this.dbService.exportProjectsAdvanced(exportParams);
            
            // Create a download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.getExportFileName(format);
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                // Hide modal
                this.modal.style.display = 'none';
                
                // Reset button
                exportBtn.textContent = originalBtnText;
                exportBtn.disabled = false;
            }, 100);
        } catch (error) {
            console.error(`Error exporting projects as ${format}:`, error);
            alert(`Error exporting projects: ${error.message || 'Unknown error'}`);
            
            // Reset button
            exportBtn.textContent = originalBtnText;
            exportBtn.disabled = false;
        }
    }

    /**
     * Get format-specific options
     * @param {string} format - Export format
     * @returns {Object} - Format options
     */
    getFormatOptions(format) {
        switch (format) {
            case 'csv':
                return {
                    delimiter: document.getElementById('csv-delimiter').value,
                    includeHeader: document.getElementById('csv-include-header').checked
                };
            case 'excel':
                return {
                    autoFilter: document.getElementById('excel-autofilter').checked,
                    freezeHeader: document.getElementById('excel-freeze-header').checked,
                    includeStats: document.getElementById('excel-include-stats').checked
                };
            case 'pdf':
                return {
                    pageSize: document.getElementById('pdf-page-size').value,
                    orientation: document.getElementById('pdf-orientation').value,
                    includeHeaderFooter: document.getElementById('pdf-include-header-footer').checked
                };
            case 'json':
                return {
                    prettyPrint: document.getElementById('json-pretty-print').checked,
                    includeMetadata: document.getElementById('json-include-metadata').checked
                };
            default:
                return {};
        }
    }

    /**
     * Get export file name based on format and date
     * @param {string} format - Export format
     * @returns {string} - File name
     */
    getExportFileName(format) {
        const date = new Date().toISOString().slice(0, 10);
        const time = new Date().toTimeString().slice(0, 8).replace(/:/g, '-');
        
        switch (format) {
            case 'csv':
                return `projects_export_${date}_${time}.csv`;
            case 'excel':
                return `projects_export_${date}_${time}.xlsx`;
            case 'pdf':
                return `projects_export_${date}_${time}.pdf`;
            case 'json':
                return `projects_export_${date}_${time}.json`;
            default:
                return `projects_export_${date}_${time}`;
        }
    }
}

// Export the class for use in the main module
window.ProjectExport = ProjectExport; 