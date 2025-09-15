/**
 * document.js - Document management functionality for the explore module
 */

class DocumentManager {
    constructor() {
        this.documents = [];
        this.filteredDocuments = [];
        this.currentPage = 1;
        this.pageSize = 25;
        this.totalCount = 0;
        this.currentView = 'table';
        this.sortField = 'id';
        this.sortDirection = 'asc';
        this.filters = {
            search: '',
            oversized: '',
            fileType: '',
            project: '',
            roll: '',
            status: '',
            minPages: '',
            maxPages: ''
        };
        this.dbService = new DatabaseService();
    }

    /**
     * Initialize the document manager
     */
    initialize() {
        this.setupEventListeners();
        // Remove automatic data loading - data will be loaded when entity is selected
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('document-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        // Filter controls
        const oversizedFilter = document.getElementById('oversized');
        if (oversizedFilter) {
            oversizedFilter.addEventListener('change', (e) => {
                this.filters.oversized = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        const fileTypeFilter = document.getElementById('file-type');
        if (fileTypeFilter) {
            fileTypeFilter.addEventListener('change', (e) => {
                this.filters.fileType = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        const projectFilter = document.getElementById('document-project');
        if (projectFilter) {
            projectFilter.addEventListener('change', (e) => {
                this.filters.project = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        const statusFilter = document.getElementById('document-status');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        // Apply and clear filters
        const applyFiltersBtn = document.getElementById('apply-document-filters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                this.applyFilters();
            });
        }

        const clearFiltersBtn = document.getElementById('clear-document-filters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Create document button
        const createBtn = document.getElementById('create-document-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.showCreateModal();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-documents-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDocuments();
            });
        }

        // Export button
        const exportBtn = document.getElementById('export-documents-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.showExportModal();
            });
        }

        // Pagination
        const prevPageBtn = document.getElementById('documents-prev-page');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.loadDocuments();
                }
            });
        }

        const nextPageBtn = document.getElementById('documents-next-page');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(this.totalCount / this.pageSize);
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.loadDocuments();
                }
            });
        }

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-documents');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Table sorting
        document.querySelectorAll('.sortable[data-sort]').forEach(header => {
            header.addEventListener('click', (e) => {
                const field = e.target.getAttribute('data-sort');
                this.sortBy(field);
            });
        });

        // Modal events
        this.setupModalEvents();
    }

    /**
     * Set up modal event listeners
     */
    setupModalEvents() {
        // Create/Edit modal
        const createModal = document.getElementById('document-create-modal');
        if (createModal) {
            const closeBtn = createModal.querySelector('.close-modal');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.hideCreateModal();
                });
            }

            const saveBtn = document.getElementById('save-document-btn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    this.saveDocument();
                });
            }
        }

        // Export modal
        const exportModal = document.getElementById('document-export-modal');
        if (exportModal) {
            const closeBtn = exportModal.querySelector('.close-modal');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.hideExportModal();
                });
            }

            const exportBtn = document.getElementById('export-document-data-btn');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => {
                    this.exportDocuments();
                });
            }
        }
    }

    /**
     * Load documents from the server
     */
    async loadDocuments() {
        try {
            this.showLoading(true);
            
            const params = {
                page: this.currentPage,
                page_size: this.pageSize,
                sort_field: this.sortField,
                sort_direction: this.sortDirection,
                ...this.filters
            };

            const response = await this.dbService.getDocuments(params);
            
            this.documents = response.documents || [];
            this.totalCount = response.total || 0;
            
            this.renderCurrentView();
            this.updatePagination();
            this.updateEntityCount();
            
        } catch (error) {
            console.error('Error loading documents:', error);
            this.showError('Failed to load documents');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Apply current filters
     */
    applyFilters() {
        this.currentPage = 1;
        this.loadDocuments();
    }

    /**
     * Clear all filters
     */
    clearFilters() {
        this.filters = {
            search: '',
            oversized: '',
            fileType: '',
            project: '',
            roll: '',
            status: '',
            minPages: '',
            maxPages: ''
        };

        // Reset form inputs
        const searchInput = document.getElementById('document-search');
        if (searchInput) searchInput.value = '';

        const oversizedFilter = document.getElementById('oversized');
        if (oversizedFilter) oversizedFilter.value = '';

        const fileTypeFilter = document.getElementById('file-type');
        if (fileTypeFilter) fileTypeFilter.value = '';

        const projectFilter = document.getElementById('document-project');
        if (projectFilter) projectFilter.value = '';

        const statusFilter = document.getElementById('document-status');
        if (statusFilter) statusFilter.value = '';

        this.currentPage = 1;
        this.loadDocuments();
    }

    /**
     * Sort documents by field
     */
    sortBy(field) {
        if (this.sortField === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortDirection = 'asc';
        }
        
        this.currentPage = 1;
        this.loadDocuments();
        this.updateSortIcons();
    }

    /**
     * Update sort icons in table headers
     */
    updateSortIcons() {
        document.querySelectorAll('.sortable .sort-icon').forEach(icon => {
            icon.className = 'fas fa-sort sort-icon';
        });

        const currentHeader = document.querySelector(`[data-sort="${this.sortField}"] .sort-icon`);
        if (currentHeader) {
            currentHeader.className = `fas fa-sort-${this.sortDirection === 'asc' ? 'up' : 'down'} sort-icon`;
        }
    }

    /**
     * Render the current view (table or cards)
     */
    renderCurrentView() {
        if (this.documents.length === 0) {
            this.showEmpty(true);
            return;
        }

        this.showEmpty(false);
        
        if (this.currentView === 'table') {
            this.renderTableView();
        } else if (this.currentView === 'cards') {
            this.renderCardsView();
        }
    }

    /**
     * Render documents in table view
     */
    renderTableView() {
        const tbody = document.getElementById('documents-results-body');
        if (!tbody) return;
        
        tbody.innerHTML = this.documents.map(document => {
            const documentId = document.id || document.doc_id;
            const documentName = document.name || 'Unknown Document';
            const fileType = document.file_type || 'Unknown';
            const status = document.status || 'Unknown';
            const pages = document.pages || 0;
            const oversized = document.has_oversized || false;
            const fileSize = this.formatFileSize(document.file_size || 0);
            const projectId = document.project_id || 'N/A';
            const rollId = document.roll_id || 'N/A';
            const creationDate = this.formatDate(document.creation_date);

            return `
                <tr class="document-row status-${status.toLowerCase()}">
                    <td>
                        <input type="checkbox" class="document-checkbox" value="${documentId}">
                    </td>
                    <td class="document-id-cell">
                        <span class="document-id">${documentId}</span>
                    </td>
                    <td class="document-name-cell">
                        <span class="document-name" title="${documentName}">${documentName}</span>
                    </td>
                    <td class="file-type-cell">
                        <span class="file-type-badge" data-type="${fileType.toLowerCase()}">${fileType}</span>
                    </td>
                    <td class="status-cell">
                        <span class="document-status-badge ${status.toLowerCase()}">${status}</span>
                    </td>
                    <td class="numeric-cell">${pages}</td>
                    <td class="boolean-cell">
                        <span class="boolean-badge ${oversized}">${oversized ? 'Yes' : 'No'}</span>
                    </td>
                    <td class="file-size-cell">${fileSize}</td>
                    <td class="project-cell">${projectId}</td>
                    <td class="roll-cell">${rollId}</td>
                    <td class="date-cell">${creationDate}</td>
                    <td class="actions-cell">
                        <div class="action-buttons">
                            <button class="action-icon view-document" title="View Details" onclick="documentManager.viewDocument('${documentId}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="action-icon edit-document" title="Edit Document" onclick="documentManager.editDocument('${documentId}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-icon delete-document" title="Delete Document" onclick="documentManager.deleteDocument('${documentId}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    /**
     * Render documents in cards view
     */
    renderCardsView() {
        const container = document.getElementById('documents-results-cards');
        if (!container) return;

        container.innerHTML = this.documents.map(document => {
            const documentId = document.id || document.doc_id;
            const documentName = document.name || 'Unknown Document';
            const fileType = document.file_type || 'Unknown';
            const status = document.status || 'Unknown';
            const pages = document.pages || 0;
            const oversized = document.has_oversized || false;
            const fileSize = this.formatFileSize(document.file_size || 0);
            const projectId = document.project_id || 'N/A';
            const rollId = document.roll_id || 'N/A';
            const creationDate = this.formatDate(document.creation_date);
            const filePath = document.path || 'N/A';

            return `
                <div class="document-card status-${status.toLowerCase()}">
                    <div class="document-card-header">
                        <input type="checkbox" class="document-checkbox" value="${documentId}">
                        <span class="document-card-id">DOC-${documentId}</span>
                        <span class="document-card-status">
                            <span class="document-status-badge ${status.toLowerCase()}">${status}</span>
                        </span>
                    </div>
                    <div class="document-card-body">
                        <h4 class="document-card-title" title="${documentName}">${documentName}</h4>
                        <div class="document-card-details">
                            <div class="document-detail-item">
                                <i class="fas fa-file"></i>
                                <span>Type: ${fileType}</span>
                            </div>
                            <div class="document-detail-item">
                                <i class="fas fa-file-alt"></i>
                                <span>Pages: ${pages}</span>
                            </div>
                            <div class="document-detail-item">
                                <i class="fas fa-hdd"></i>
                                <span>Size: ${fileSize}</span>
                            </div>
                            <div class="document-detail-item">
                                <i class="fas fa-project-diagram"></i>
                                <span>Project: ${projectId}</span>
                            </div>
                            <div class="document-detail-item">
                                <i class="fas fa-film"></i>
                                <span>Roll: ${rollId}</span>
                            </div>
                            ${oversized ? '<div class="document-detail-item oversized"><i class="fas fa-expand-arrows-alt"></i><span>Oversized</span></div>' : ''}
                        </div>
                        <div class="document-card-path">
                            <i class="fas fa-folder"></i>
                            <span title="${filePath}">${filePath}</span>
                        </div>
                    </div>
                    <div class="document-card-date">
                        <i class="fas fa-calendar"></i>
                        <span>Created: ${creationDate}</span>
                    </div>
                    <div class="document-card-actions">
                        <button class="action-icon view-document" title="View Details" onclick="documentManager.viewDocument('${documentId}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-icon edit-document" title="Edit Document" onclick="documentManager.editDocument('${documentId}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-icon delete-document" title="Delete Document" onclick="documentManager.deleteDocument('${documentId}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Switch between table and card views
     */
    switchView(view) {
        this.currentView = view;
        
        // Update view buttons
        document.querySelectorAll('.view-control').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`.view-control[data-view="${view}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        // Show/hide view containers
        const tableView = document.getElementById('documents-table-view');
        const cardsView = document.getElementById('documents-cards-view');
        
        if (tableView && cardsView) {
            if (view === 'table') {
                tableView.style.display = 'block';
                cardsView.style.display = 'none';
            } else {
                tableView.style.display = 'none';
                cardsView.style.display = 'block';
            }
        }
        
        this.renderCurrentView();
    }

    /**
     * Show/hide loading state
     */
    showLoading(show) {
        const tableView = document.getElementById('documents-table-view');
        const cardsView = document.getElementById('documents-cards-view');
        
        if (show) {
            if (tableView) {
                const tbody = tableView.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = '<tr class="loading-row"><td colspan="11"><i class="fas fa-spinner fa-spin"></i> Loading documents...</td></tr>';
                }
            }
            if (cardsView) {
                cardsView.innerHTML = '<div class="loading-message"><i class="fas fa-spinner fa-spin"></i> Loading documents...</div>';
            }
        }
    }

    /**
     * Show/hide empty state
     */
    showEmpty(show) {
        const emptyElement = document.getElementById('document-empty');
        const tableView = document.getElementById('documents-table-view');
        const cardsView = document.getElementById('documents-cards-view');
        
        if (emptyElement) emptyElement.style.display = show ? 'flex' : 'none';
        if (tableView) tableView.style.display = show ? 'none' : (this.currentView === 'table' ? 'block' : 'none');
        if (cardsView) cardsView.style.display = show ? 'none' : (this.currentView === 'cards' ? 'block' : 'none');
    }

    /**
     * Show error message
     */
    showError(message) {
        const tableView = document.getElementById('documents-table-view');
        const cardsView = document.getElementById('documents-cards-view');
        
        const errorHtml = `<div class="error-message"><i class="fas fa-exclamation-triangle"></i> ${message}</div>`;
        
        if (tableView) {
            const tbody = tableView.querySelector('tbody');
            if (tbody) {
                tbody.innerHTML = `<tr class="error-row"><td colspan="11">${errorHtml}</td></tr>`;
            }
        }
        if (cardsView) {
            cardsView.innerHTML = errorHtml;
        }
    }

    /**
     * Update pagination controls
     */
    updatePagination() {
        const totalPages = Math.ceil(this.totalCount / this.pageSize);
        const startItem = (this.currentPage - 1) * this.pageSize + 1;
        const endItem = Math.min(this.currentPage * this.pageSize, this.totalCount);
        
        // Update pagination for table view
        const prevBtn = document.getElementById('documents-prev-page');
        const nextBtn = document.getElementById('documents-next-page');
        const pagesContainer = document.getElementById('documents-page-numbers');
        
        if (prevBtn) prevBtn.disabled = this.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.currentPage >= totalPages;
        
        // Update page numbers
        if (pagesContainer) {
            let pagesHtml = '';
            const maxVisiblePages = 5;
            let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            if (endPage - startPage + 1 < maxVisiblePages) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            for (let i = startPage; i <= endPage; i++) {
                pagesHtml += `
                    <button class="page-number ${i === this.currentPage ? 'active' : ''}" 
                            onclick="documentManager.goToPage(${i})">${i}</button>
                `;
            }
            pagesContainer.innerHTML = pagesHtml;
        }
        
        // Update pagination info
        const paginationInfo = document.getElementById('documents-pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent = `Showing ${startItem}-${endItem} of ${this.totalCount} documents`;
        }
    }

    /**
     * Go to specific page
     */
    goToPage(page) {
        this.currentPage = page;
        this.loadDocuments();
    }

    /**
     * Update entity count in main results header
     */
    updateEntityCount() {
        const countElement = document.getElementById('result-count');
        if (countElement) {
            countElement.textContent = this.totalCount;
        }
    }

    /**
     * Toggle select all documents
     */
    toggleSelectAll(checked) {
        document.querySelectorAll('.document-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
        });
    }

    /**
     * Get selected document IDs
     */
    getSelectedDocuments() {
        const checkboxes = document.querySelectorAll('.document-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    /**
     * View document details
     */
    viewDocument(documentId) {
        const event = new CustomEvent('showDocumentDetails', {
            detail: { documentId }
        });
        document.dispatchEvent(event);
    }

    /**
     * Edit document
     */
    editDocument(documentId) {
        // Find the document
        const document = this.documents.find(d => (d.id || d.doc_id) == documentId);
        if (document) {
            this.showEditModal(document);
        }
    }

    /**
     * Delete document
     */
    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            await this.dbService.deleteDocument(documentId);
            this.loadDocuments();
        } catch (error) {
            console.error('Error deleting document:', error);
            alert('Failed to delete document');
        }
    }

    /**
     * Show create modal
     */
    showCreateModal() {
        const modal = document.getElementById('document-create-modal');
        if (modal) {
            // Reset form
            const form = modal.querySelector('form');
            if (form) form.reset();
            
            modal.style.display = 'flex';
        }
    }

    /**
     * Hide create modal
     */
    hideCreateModal() {
        const modal = document.getElementById('document-create-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Show edit modal
     */
    showEditModal(document) {
        const modal = document.getElementById('document-create-modal');
        if (modal) {
            // Populate form with document data
            const nameInput = modal.querySelector('#document-name');
            const pathInput = modal.querySelector('#document-path');
            const typeInput = modal.querySelector('#document-type');
            const statusInput = modal.querySelector('#document-status');
            const pagesInput = modal.querySelector('#document-pages');
            const oversizedInput = modal.querySelector('#document-oversized');
            const projectInput = modal.querySelector('#document-project-id');
            const rollInput = modal.querySelector('#document-roll-id');

            if (nameInput) nameInput.value = document.name || '';
            if (pathInput) pathInput.value = document.path || '';
            if (typeInput) typeInput.value = document.file_type || '';
            if (statusInput) statusInput.value = document.status || '';
            if (pagesInput) pagesInput.value = document.pages || '';
            if (oversizedInput) oversizedInput.checked = document.has_oversized || false;
            if (projectInput) projectInput.value = document.project_id || '';
            if (rollInput) rollInput.value = document.roll_id || '';

            // Store document ID for saving
            modal.setAttribute('data-document-id', document.id || document.doc_id);
            
            modal.style.display = 'flex';
        }
    }

    /**
     * Save document (create or update)
     */
    async saveDocument() {
        const modal = document.getElementById('document-create-modal');
        if (!modal) return;

        const documentId = modal.getAttribute('data-document-id');
        const isEdit = !!documentId;

        const formData = {
            name: modal.querySelector('#document-name')?.value || '',
            path: modal.querySelector('#document-path')?.value || '',
            file_type: modal.querySelector('#document-type')?.value || '',
            status: modal.querySelector('#document-status')?.value || '',
            pages: parseInt(modal.querySelector('#document-pages')?.value) || 0,
            has_oversized: modal.querySelector('#document-oversized')?.checked || false,
            project_id: modal.querySelector('#document-project-id')?.value || null,
            roll_id: modal.querySelector('#document-roll-id')?.value || null
        };

        try {
            if (isEdit) {
                await this.dbService.updateDocument(documentId, formData);
            } else {
                await this.dbService.createDocument(formData);
            }
            
            this.hideCreateModal();
            this.loadDocuments();
        } catch (error) {
            console.error('Error saving document:', error);
            alert('Failed to save document');
        }
    }

    /**
     * Show export modal
     */
    showExportModal() {
        const modal = document.getElementById('document-export-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    /**
     * Hide export modal
     */
    hideExportModal() {
        const modal = document.getElementById('document-export-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Export documents
     */
    async exportDocuments() {
        const selectedIds = this.getSelectedDocuments();
        const format = document.querySelector('input[name="export-format"]:checked')?.value || 'csv';
        
        try {
            const response = await this.dbService.exportDocuments(selectedIds, format);
            
            // Create download link
            const blob = new Blob([response.data], { type: response.contentType });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.filename || `documents_export.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.hideExportModal();
        } catch (error) {
            console.error('Error exporting documents:', error);
            alert('Failed to export documents');
        }
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Format date for display
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}

// Remove automatic initialization - DocumentManager is now managed by ExploreMain 