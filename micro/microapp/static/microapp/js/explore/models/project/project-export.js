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
            <div id="export-project-modal" class="export-modal">
                <div class="export-modal-content">
                    <div class="export-modal-header">
                        <h2 id="export-modal-title">Export Projects</h2>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="export-modal-body">
                        <div class="export-options">
                            <div class="export-section">
                                <h3><i class="fas fa-filter"></i> Export Scope</h3>
                                <div class="radio-group">
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="selected" checked>
                                        <span>Selected Projects (<span id="selected-count">0</span>)</span>
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="filtered">
                                        <span>All Filtered Projects (<span id="filtered-count">0</span>)</span>
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="all">
                                        <span>All Projects</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section">
                                <h3><i class="fas fa-file"></i> Export Format</h3>
                                <div class="format-options">
                                    <label class="format-option">
                                        <input type="radio" name="export-format" value="csv" checked>
                                        <div class="format-icon">
                                            <i class="fas fa-file-csv"></i>
                                            <span>CSV</span>
                                        </div>
                                    </label>
                                    <label class="format-option">
                                        <input type="radio" name="export-format" value="excel">
                                        <div class="format-icon">
                                            <i class="fas fa-file-excel"></i>
                                            <span>Excel</span>
                                        </div>
                                    </label>
                                    <label class="format-option">
                                        <input type="radio" name="export-format" value="pdf">
                                        <div class="format-icon">
                                            <i class="fas fa-file-pdf"></i>
                                            <span>PDF</span>
                                        </div>
                                    </label>
                                    <label class="format-option">
                                        <input type="radio" name="export-format" value="json">
                                        <div class="format-icon">
                                            <i class="fas fa-file-code"></i>
                                            <span>JSON</span>
                                        </div>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section">
                                <h3><i class="fas fa-columns"></i> Fields to Include</h3>
                                <div class="field-selection-buttons">
                                    <button type="button" class="select-all-btn">Select All</button>
                                    <button type="button" class="deselect-all-btn">Deselect All</button>
                                </div>
                                <div class="checkbox-grid">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="id" checked>
                                        <span>Project ID</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="archive_id" checked>
                                        <span>Archive ID</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="location" checked>
                                        <span>Location</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="doc_type" checked>
                                        <span>Document Type</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="project_path">
                                        <span>Project Path</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="project_folder_name">
                                        <span>Folder Name</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="pdf_folder_path">
                                        <span>PDF Folder Path</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="has_pdf_folder" checked>
                                        <span>Has PDF Folder</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="has_oversized" checked>
                                        <span>Has Oversized</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="documents_with_oversized">
                                        <span>Oversized Documents</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="total_oversized">
                                        <span>Total Oversized</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="total_pages" checked>
                                        <span>Total Pages</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="total_pages_with_refs">
                                        <span>Pages with References</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="processing_complete" checked>
                                        <span>Processing Complete</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="film_allocation_complete" checked>
                                        <span>Film Allocation Complete</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="distribution_complete">
                                        <span>Distribution Complete</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="date_created" checked>
                                        <span>Date Created</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="updated_at">
                                        <span>Last Updated</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-csv format-specific-options">
                                <h3><i class="fas fa-cog"></i> CSV Options</h3>
                                <div class="form-group">
                                    <label for="csv-delimiter">Delimiter</label>
                                    <select id="csv-delimiter">
                                        <option value="," selected>Comma (,)</option>
                                        <option value=";">Semicolon (;)</option>
                                        <option value="\\t">Tab</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="csv-include-header" checked>
                                        <span>Include Header Row</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-excel format-specific-options">
                                <h3><i class="fas fa-cog"></i> Excel Options</h3>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="excel-autofilter" checked>
                                        <span>Add Auto-Filter</span>
                                    </label>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="excel-freeze-header" checked>
                                        <span>Freeze Header Row</span>
                                    </label>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="excel-include-stats">
                                        <span>Include Summary Statistics</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-pdf format-specific-options">
                                <h3><i class="fas fa-cog"></i> PDF Options</h3>
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
                                        <span>Include Header & Footer</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="export-section format-options-json format-specific-options">
                                <h3><i class="fas fa-cog"></i> JSON Options</h3>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="json-pretty-print" checked>
                                        <span>Pretty Print (Formatted)</span>
                                    </label>
                                </div>
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="json-include-metadata" checked>
                                        <span>Include Export Metadata</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="export-modal-footer">
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
        // Note: Export button click events are handled by project-list.js
        // to ensure proper access to selected projects
        
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
        this.modal.querySelector('.select-all-btn').addEventListener('click', () => {
            const checkboxes = this.modal.querySelectorAll('input[name="export-fields"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });
        
        this.modal.querySelector('.deselect-all-btn').addEventListener('click', () => {
            const checkboxes = this.modal.querySelectorAll('input[name="export-fields"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        });
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
        const selectedCount = selectedProjects instanceof Set ? selectedProjects.size : 0;
        
        document.getElementById('selected-count').textContent = selectedCount;
        document.getElementById('filtered-count').textContent = filteredCount;
        
        // Handle scope selection logic
        const selectedOption = this.modal.querySelector('input[name="export-scope"][value="selected"]');
        const filteredOption = this.modal.querySelector('input[name="export-scope"][value="filtered"]');
        const allOption = this.modal.querySelector('input[name="export-scope"][value="all"]');
        
        if (selectedCount === 0) {
            // No projects selected, disable selected option and default to filtered
            selectedOption.disabled = true;
            selectedOption.parentElement.style.opacity = '0.5';
            
            if (filteredCount > 0) {
                filteredOption.checked = true;
            } else {
                allOption.checked = true;
            }
        } else {
            // Projects are selected, enable selected option and default to it
            selectedOption.disabled = false;
            selectedOption.parentElement.style.opacity = '1';
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
            section.classList.remove('active');
        });
        
        // Show options for selected format
        const selectedFormat = this.modal.querySelector('input[name="export-format"]:checked').value;
        const formatOptions = this.modal.querySelector(`.format-options-${selectedFormat}`);
        if (formatOptions) {
            formatOptions.classList.add('active');
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
        
        if (fields.length === 0) {
            alert('Please select at least one field to export.');
            return;
        }
        
        // Get format-specific options
        const options = this.getFormatOptions(format);
        
        // Debug logging
        console.log('Export scope:', scope);
        console.log('Export format:', format);
        console.log('Selected fields:', fields);
        console.log('Format options:', options);
        
        // Get project IDs based on scope
        let projectIds = [];
        let useFilters = false;
        
        if (scope === 'selected') {
            // Get selected project IDs from the project list
            if (window.exploreMain?.projectList?.selectedProjects) {
                projectIds = Array.from(window.exploreMain.projectList.selectedProjects);
                console.log('Got selected projects from projectList:', projectIds);
            } else {
                // Fallback: dispatch event to get selected projects
                const selectedProjectsEvent = new CustomEvent('getSelectedProjects', {
                    detail: { callback: (selectedProjects) => {
                        projectIds = Array.from(selectedProjects);
                        console.log('Got selected projects from event:', projectIds);
                    }}
                });
                document.dispatchEvent(selectedProjectsEvent);
            }
        } else if (scope === 'filtered') {
            // Use current filters
            useFilters = true;
            console.log('Using filtered projects with filters:', window.exploreMain?.projectList?.filters);
        } else {
            console.log('Using all projects');
        }
        
        // Show loading state
        const exportBtn = document.getElementById('start-export-btn');
        const originalBtnText = exportBtn.textContent;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        exportBtn.disabled = true;
        
        try {
            let data;
            
            if (format === 'csv') {
                data = await this.exportAsCSV(projectIds, fields, options, useFilters);
            } else if (format === 'excel') {
                data = await this.exportAsExcel(projectIds, fields, options, useFilters);
            } else if (format === 'pdf') {
                data = await this.exportAsPDF(projectIds, fields, options, useFilters);
            } else if (format === 'json') {
                data = await this.exportAsJSON(projectIds, fields, options, useFilters);
            }
            
            // Create a download link
            const url = URL.createObjectURL(data);
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
     * Export projects as CSV
     */
    async exportAsCSV(projectIds, fields, options, useFilters) {
        // Get project data
        const projects = await this.getProjectData(projectIds, useFilters);
        
        // Create CSV content
        let csvContent = '';
        
        // Add header row if requested
        if (options.includeHeader) {
            const headers = fields.map(field => this.getFieldDisplayName(field));
            csvContent += headers.join(options.delimiter) + '\n';
        }
        
        // Add data rows
        projects.forEach((project, index) => {
            const row = fields.map(field => {
                let value = project[field];
                
                // Handle null, undefined, and boolean values
                if (value === null || value === undefined) {
                    value = '';
                } else if (typeof value === 'boolean') {
                    value = value ? 'Yes' : 'No';
                } else {
                    value = String(value);
                }
                
                // Escape quotes and wrap in quotes if contains delimiter
                if (typeof value === 'string' && (value.includes(options.delimiter) || value.includes('"') || value.includes('\n'))) {
                    value = '"' + value.replace(/"/g, '""') + '"';
                }
                return value;
            });
            csvContent += row.join(options.delimiter) + '\n';
        });
        
        return new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    }

    /**
     * Export projects as Excel
     */
    async exportAsExcel(projectIds, fields, options, useFilters) {
        // Get project data
        const projects = await this.getProjectData(projectIds, useFilters);
        
        // Create workbook data
        const workbookData = {
            projects: projects,
            fields: fields,
            fieldNames: fields.map(field => this.getFieldDisplayName(field)),
            options: options
        };
        
        // Send to backend for Excel generation
        const response = await fetch('/api/projects/export/excel/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(workbookData)
        });
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }
        
        return await response.blob();
    }

    /**
     * Export projects as PDF
     */
    async exportAsPDF(projectIds, fields, options, useFilters) {
        // Get project data
        const projects = await this.getProjectData(projectIds, useFilters);
        
        // Create PDF data
        const pdfData = {
            projects: projects,
            fields: fields,
            fieldNames: fields.map(field => this.getFieldDisplayName(field)),
            options: options
        };
        
        // Send to backend for PDF generation
        const response = await fetch('/api/projects/export/pdf/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(pdfData)
        });
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }
        
        return await response.blob();
    }

    /**
     * Export projects as JSON
     */
    async exportAsJSON(projectIds, fields, options, useFilters) {
        // Get project data
        const projects = await this.getProjectData(projectIds, useFilters);
        
        // Filter projects to only include selected fields
        const filteredProjects = projects.map(project => {
            const filteredProject = {};
            fields.forEach(field => {
                filteredProject[field] = project[field];
            });
            return filteredProject;
        });
        
        // Create JSON object
        const jsonData = {
            projects: filteredProjects,
            ...(options.includeMetadata && {
                metadata: {
                    exportDate: new Date().toISOString(),
                    totalProjects: filteredProjects.length,
                    fields: fields,
                    exportedBy: 'Microfilm Management System'
                }
            })
        };
        
        // Convert to JSON string
        const jsonString = options.prettyPrint 
            ? JSON.stringify(jsonData, null, 2)
            : JSON.stringify(jsonData);
        
        return new Blob([jsonString], { type: 'application/json;charset=utf-8;' });
    }

    /**
     * Get project data for export
     */
    async getProjectData(projectIds, useFilters) {
        if (useFilters) {
            // Get all projects with current filters
            const currentFilters = window.exploreMain?.projectList?.filters || {};
            const response = await this.dbService.listProjects({
                ...currentFilters,
                page_size: 10000 // Get all results
            });
            return response.results;
        } else if (projectIds.length > 0) {
            // Get specific projects
            const projects = [];
            for (const id of projectIds) {
                try {
                    const response = await this.dbService.getProject(id);
                    
                    // Extract the actual project data from the response
                    if (response.status === 'success' && response.project) {
                        projects.push(response.project);
                    }
                } catch (error) {
                    console.warn(`Could not fetch project ${id}:`, error);
                }
            }
            return projects;
        } else {
            // Get all projects
            const response = await this.dbService.listProjects({ page_size: 10000 });
            return response.results;
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
                    delimiter: document.getElementById('csv-delimiter').value === '\\t' ? '\t' : document.getElementById('csv-delimiter').value,
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

    /**
     * Get display name for field
     */
    getFieldDisplayName(field) {
        const fieldNames = {
            'id': 'Project ID',
            'archive_id': 'Archive ID',
            'location': 'Location',
            'doc_type': 'Document Type',
            'project_path': 'Project Path',
            'project_folder_name': 'Folder Name',
            'pdf_folder_path': 'PDF Folder Path',
            'has_pdf_folder': 'Has PDF Folder',
            'has_oversized': 'Has Oversized',
            'documents_with_oversized': 'Oversized Documents',
            'total_oversized': 'Total Oversized',
            'total_pages': 'Total Pages',
            'total_pages_with_refs': 'Pages with References',
            'processing_complete': 'Processing Complete',
            'film_allocation_complete': 'Film Allocation Complete',
            'distribution_complete': 'Distribution Complete',
            'date_created': 'Date Created',
            'updated_at': 'Last Updated'
        };
        return fieldNames[field] || field;
    }

    /**
     * Get CSRF token for Django requests
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Export the class for use in the main module
window.ProjectExport = ProjectExport;