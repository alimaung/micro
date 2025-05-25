/**
 * roll-export.js - Roll export functionality
 * Handles exporting roll data in various formats
 */

class RollExport {
    constructor() {
        this.dbService = new DatabaseService();
        this.modal = null;
    }

    /**
     * Initialize the roll export module
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
        if (document.getElementById('export-roll-modal')) {
            this.modal = document.getElementById('export-roll-modal');
            return;
        }
        
        // Create modal element
        const modalHtml = `
            <div id="export-roll-modal" class="export-modal">
                <div class="export-modal-content">
                    <div class="export-modal-header">
                        <h2 id="export-modal-title">Export Rolls</h2>
                        <button class="close-modal">&times;</button>
                    </div>
                    <div class="export-modal-body">
                        <div class="export-options">
                            <div class="export-section">
                                <h3><i class="fas fa-filter"></i> Export Scope</h3>
                                <div class="radio-group">
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="selected" checked>
                                        <span>Selected Rolls (<span id="selected-count">0</span>)</span>
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="filtered">
                                        <span>All Filtered Rolls (<span id="filtered-count">0</span>)</span>
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="export-scope" value="all">
                                        <span>All Rolls</span>
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
                                        <span>Roll ID</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="roll_id" checked>
                                        <span>Roll Number</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="project_archive_id" checked>
                                        <span>Project Archive ID</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="film_number" checked>
                                        <span>Film Number</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="film_type" checked>
                                        <span>Film Type</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="capacity" checked>
                                        <span>Capacity</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="pages_used" checked>
                                        <span>Pages Used</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="pages_remaining" checked>
                                        <span>Pages Remaining</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="utilization" checked>
                                        <span>Utilization %</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="status" checked>
                                        <span>Status</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="has_split_documents">
                                        <span>Has Split Documents</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="is_partial">
                                        <span>Is Partial</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="is_full">
                                        <span>Is Full</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="remaining_capacity">
                                        <span>Remaining Capacity</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="usable_capacity">
                                        <span>Usable Capacity</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="film_number_source">
                                        <span>Film Number Source</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="export-fields" value="creation_date" checked>
                                        <span>Creation Date</span>
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
        this.modal = document.getElementById('export-roll-modal');
    }

    /**
     * Set up event listeners for the export modal
     */
    setupEventListeners() {
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
     * @param {Set<string>} selectedRolls - Set of selected roll IDs
     * @param {number} filteredCount - Number of rolls in filtered view
     */
    openExportModal(format, selectedRolls = new Set(), filteredCount = 0) {
        // Update selected format
        const formatRadio = this.modal.querySelector(`input[name="export-format"][value="${format}"]`);
        if (formatRadio) {
            formatRadio.checked = true;
        }
        
        // Update counts
        const selectedCount = selectedRolls instanceof Set ? selectedRolls.size : 0;
        
        document.getElementById('selected-count').textContent = selectedCount;
        document.getElementById('filtered-count').textContent = filteredCount;
        
        // Handle scope selection logic
        const selectedOption = this.modal.querySelector('input[name="export-scope"][value="selected"]');
        const filteredOption = this.modal.querySelector('input[name="export-scope"][value="filtered"]');
        const allOption = this.modal.querySelector('input[name="export-scope"][value="all"]');
        
        if (selectedCount === 0) {
            // No rolls selected, disable selected option and default to filtered
            selectedOption.disabled = true;
            selectedOption.parentElement.style.opacity = '0.5';
            
            if (filteredCount > 0) {
                filteredOption.checked = true;
            } else {
                allOption.checked = true;
            }
        } else {
            // Rolls are selected, enable selected option and default to it
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
        
        // Get roll IDs based on scope
        let rollIds = [];
        let useFilters = false;
        
        if (scope === 'selected') {
            // Get selected roll IDs from the roll list
            if (window.exploreMain?.rollList?.selectedRolls) {
                rollIds = Array.from(window.exploreMain.rollList.selectedRolls);
            }
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
            let data;
            
            if (format === 'csv') {
                data = await this.exportAsCSV(rollIds, fields, options, useFilters);
            } else if (format === 'excel') {
                data = await this.exportAsExcel(rollIds, fields, options, useFilters);
            } else if (format === 'pdf') {
                data = await this.exportAsPDF(rollIds, fields, options, useFilters);
            } else if (format === 'json') {
                data = await this.exportAsJSON(rollIds, fields, options, useFilters);
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
            console.error(`Error exporting rolls as ${format}:`, error);
            alert(`Error exporting rolls: ${error.message || 'Unknown error'}`);
            
            // Reset button
            exportBtn.textContent = originalBtnText;
            exportBtn.disabled = false;
        }
    }

    /**
     * Export rolls as CSV
     */
    async exportAsCSV(rollIds, fields, options, useFilters) {
        // Get roll data
        const rolls = await this.getRollData(rollIds, useFilters);
        
        // Create CSV content
        let csvContent = '';
        
        // Add header row if requested
        if (options.includeHeader) {
            const headers = fields.map(field => this.getFieldDisplayName(field));
            csvContent += headers.join(options.delimiter) + '\n';
        }
        
        // Add data rows
        rolls.forEach((roll, index) => {
            const row = fields.map(field => {
                let value = roll[field];
                
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
     * Export rolls as Excel
     */
    async exportAsExcel(rollIds, fields, options, useFilters) {
        // Get roll data
        const rolls = await this.getRollData(rollIds, useFilters);
        
        // Create workbook data
        const workbookData = {
            rolls: rolls,
            fields: fields,
            fieldNames: fields.map(field => this.getFieldDisplayName(field)),
            options: options
        };
        
        // Send to backend for Excel generation
        const response = await fetch('/api/rolls/export/excel/', {
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
     * Export rolls as PDF
     */
    async exportAsPDF(rollIds, fields, options, useFilters) {
        // Get roll data
        const rolls = await this.getRollData(rollIds, useFilters);
        
        // Create PDF data
        const pdfData = {
            rolls: rolls,
            fields: fields,
            fieldNames: fields.map(field => this.getFieldDisplayName(field)),
            options: options
        };
        
        // Send to backend for PDF generation
        const response = await fetch('/api/rolls/export/pdf/', {
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
     * Export rolls as JSON
     */
    async exportAsJSON(rollIds, fields, options, useFilters) {
        // Get roll data
        const rolls = await this.getRollData(rollIds, useFilters);
        
        // Filter rolls to only include selected fields
        const filteredRolls = rolls.map(roll => {
            const filteredRoll = {};
            fields.forEach(field => {
                filteredRoll[field] = roll[field];
            });
            return filteredRoll;
        });
        
        // Create JSON object
        const jsonData = {
            rolls: filteredRolls,
            ...(options.includeMetadata && {
                metadata: {
                    exportDate: new Date().toISOString(),
                    totalRolls: filteredRolls.length,
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
     * Get roll data for export
     */
    async getRollData(rollIds, useFilters) {
        if (useFilters) {
            // Get all rolls with current filters
            const currentFilters = window.exploreMain?.rollList?.filters || {};
            const response = await this.dbService.listRolls({
                ...currentFilters,
                page_size: 10000 // Get all results
            });
            return response.results;
        } else if (rollIds.length > 0) {
            // Get specific rolls
            const rolls = [];
            for (const id of rollIds) {
                try {
                    const response = await this.dbService.getRoll(id);
                    
                    // Handle different response structures
                    let roll;
                    if (response.roll) {
                        // Response has a 'roll' property
                        roll = response.roll;
                    } else if (response.id || response.roll_id) {
                        // Response is the roll object directly
                        roll = response;
                    } else if (response.status === 'success' && response.roll) {
                        // Legacy response structure
                        roll = response.roll;
                    }
                    
                    if (roll) {
                        rolls.push(roll);
                    } else {
                        console.warn(`Invalid roll data structure for roll ${id}:`, response);
                    }
                } catch (error) {
                    console.warn(`Could not fetch roll ${id}:`, error);
                }
            }
            return rolls;
        } else {
            // Get all rolls
            const response = await this.dbService.listRolls({ page_size: 10000 });
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
                return `rolls_export_${date}_${time}.csv`;
            case 'excel':
                return `rolls_export_${date}_${time}.xlsx`;
            case 'pdf':
                return `rolls_export_${date}_${time}.pdf`;
            case 'json':
                return `rolls_export_${date}_${time}.json`;
            default:
                return `rolls_export_${date}_${time}`;
        }
    }

    /**
     * Get display name for field
     */
    getFieldDisplayName(field) {
        const fieldNames = {
            'id': 'Roll ID',
            'roll_id': 'Roll Number',
            'project_id': 'Project ID',
            'project_archive_id': 'Project Archive ID',
            'film_number': 'Film Number',
            'film_type': 'Film Type',
            'capacity': 'Capacity',
            'pages_used': 'Pages Used',
            'pages_remaining': 'Pages Remaining',
            'utilization': 'Utilization %',
            'status': 'Status',
            'has_split_documents': 'Has Split Documents',
            'is_partial': 'Is Partial',
            'is_full': 'Is Full',
            'remaining_capacity': 'Remaining Capacity',
            'usable_capacity': 'Usable Capacity',
            'film_number_source': 'Film Number Source',
            'creation_date': 'Creation Date'
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
window.RollExport = RollExport; 