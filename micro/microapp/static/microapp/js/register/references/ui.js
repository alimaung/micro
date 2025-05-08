/**
 * References Module - UI
 * Handles all UI updates and DOM manipulations
 */

// UI module using IIFE pattern
const ReferencesUI = (function() {
    /**
     * UI manager for reference sheets
     */
    class ReferencesUIClass {
        /**
         * Initialize the UI manager with element selectors
         */
        constructor() {
            // Cache DOM elements for better performance
            this.elements = {
                // Status elements
                statusBadge: document.querySelector('#step-6 .status-badge'),
                generationStatus: document.getElementById('generation-status'),
                totalDocuments: document.getElementById('total-documents'),
                oversizedDocuments: document.getElementById('oversized-documents'),
                sheetsGenerated: document.getElementById('sheets-generated'),
                
                // Action elements
                generateButton: document.getElementById('generate-references'),
                resetButton: document.getElementById('reset-references'),
                refreshListButton: document.getElementById('refresh-list'),
                
                // Progress elements
                progressBar: document.querySelector('#step-6 .progress-bar-fill'),
                progressPercentage: document.querySelector('#step-6 .progress-percentage'),
                progressStatus: document.getElementById('reference-status'),
                
                // Document list
                documentList: document.getElementById('oversized-document-list'),
                emptyState: document.querySelector('#oversized-document-list .empty-state'),
                
                // Reference visualization section (use the existing one)
                referenceVisualization: document.querySelector('.reference-visualization'),
                visualizationContent: document.querySelector('.visualization-content'),
                referenceAnimation: document.querySelector('.reference-animation'),
                
                // Messages
                inactiveMessage: document.querySelector('.status-message.inactive'),
                
                // Navigation
                backButton: document.getElementById('back-to-step-5'),
                nextButton: document.getElementById('to-step-7'),
                
                // Data output
                dataOutput: document.querySelector('#step-6 .data-output')
            };
            
            // Setup reference sheets list
            this.setupReferenceSheetsList();
            
            // Add CSS styles for reference sheet preview
            this.addReferenceSheetStyles();
        }
        
        /**
         * Setup the reference sheets list inside the visualization content
         */
        setupReferenceSheetsList() {
            if (!this.elements.visualizationContent) return;
            
            // Create reference sheet list if it doesn't exist
            if (!document.getElementById('reference-sheets-list')) {
                // Create reference sheets list element
                const referenceSheetsList = document.createElement('div');
                referenceSheetsList.id = 'reference-sheets-list';
                referenceSheetsList.className = 'reference-sheets-list hidden';
                
                // Create empty state
                const emptyState = document.createElement('div');
                emptyState.className = 'empty-state';
                emptyState.innerHTML = `
                    <p>No reference sheets selected</p>
                    <p>Click on a document to view its reference sheets</p>
                `;
                
                // Create inline PDF viewer
                const pdfViewer = document.createElement('div');
                pdfViewer.id = 'reference-pdf-viewer';
                pdfViewer.className = 'reference-pdf-viewer hidden';
                pdfViewer.innerHTML = `
                    <div class="viewer-header">
                        <span class="viewer-title">Reference Sheet Preview</span>
                        <button class="close-viewer-btn"><i class="fas fa-times"></i></button>
                    </div>
                    <div class="viewer-content">
                        <embed id="pdf-embed" type="application/pdf" width="100%" height="500px" />
                    </div>
                `;
                
                // Add to visualization content after animation
                if (this.elements.referenceAnimation) {
                    this.elements.visualizationContent.appendChild(referenceSheetsList);
                    this.elements.visualizationContent.appendChild(emptyState);
                    this.elements.visualizationContent.appendChild(pdfViewer);
                }
                
                // Update elements cache
                this.elements.referenceSheetsList = document.getElementById('reference-sheets-list');
                this.elements.referenceSheetEmptyState = emptyState;
                this.elements.pdfViewer = pdfViewer;
                
                // Add event listener to close button
                const closeBtn = pdfViewer.querySelector('.close-viewer-btn');
                if (closeBtn) {
                    closeBtn.addEventListener('click', () => this.closeInlinePdfViewer());
                }
            }
        }

        /**
         * Adds CSS styles for the reference sheet preview UI
         */
        addReferenceSheetStyles() {
            // Check if styles already exist
            if (document.getElementById('reference-sheet-styles')) return;
            
            // Create style element
            const style = document.createElement('style');
            style.id = 'reference-sheet-styles';
            style.textContent = `
                /* Reference sheets list */
                .reference-sheets-list {
                    width: 100%;
                    margin-top: 15px;
                }
                
                .preview-description {
                    margin-bottom: 15px;
                    color: #555;
                    font-size: 14px;
                    font-weight: bold;
                }
                
                /* Reference sheet items */
                .reference-sheet-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px;
                    margin-bottom: 10px;
                    background-color: #f8f9fa;
                    border-radius: 6px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    transition: background-color 0.2s;
                }
                
                .reference-sheet-item:hover {
                    background-color: #f0f4f8;
                }
                
                /* Sheet information */
                .sheet-info {
                    flex: 1;
                }
                
                .sheet-title {
                    font-weight: bold;
                    font-size: 16px;
                    color: #0066cc;
                    margin-bottom: 5px;
                }
                
                .sheet-details {
                    font-size: 14px;
                    color: #555;
                }
                
                .sheet-details span {
                    margin-right: 15px;
                }
                
                /* View button */
                .view-sheet-btn {
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background-color 0.2s;
                }
                
                .view-sheet-btn:hover {
                    background-color: #0052a3;
                }
                
                /* Inline PDF Container */
                .inline-pdf-container {
                    margin: -5px 0 15px 0;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    overflow: hidden;
                    background-color: #f5f5f5;
                    width: 100%;
                    animation: slideDown 0.3s ease-out;
                }
                
                @keyframes slideDown {
                    from { opacity: 0; max-height: 0; }
                    to { opacity: 1; max-height: 600px; }
                }
                
                .viewer-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background-color: #f5f5f5;
                    padding: 10px 15px;
                    border-bottom: 1px solid #ddd;
                }
                
                .viewer-title {
                    font-weight: bold;
                    color: #333;
                }
                
                .close-viewer-btn {
                    background: none;
                    border: none;
                    color: #777;
                    cursor: pointer;
                    font-size: 16px;
                }
                
                .close-viewer-btn:hover {
                    color: #333;
                }
                
                .viewer-content {
                    padding: 0;
                    background-color: #f5f5f5;
                }
                
                /* PDF Viewer */
                .reference-pdf-viewer {
                    margin-top: 20px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    overflow: hidden;
                }
                
                /* Reset button */
                .reset-button {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 20px;
                    font-size: 0.95rem;
                    font-weight: 500;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    margin-left: 10px;
                    transition: background-color 0.2s ease;
                }
                
                .reset-button:hover {
                    background-color: #d32f2f;
                }
                
                .reset-button:disabled {
                    background-color: #ffcdd2;
                    cursor: not-allowed;
                }
                
                .reset-button i {
                    margin-right: 8px;
                }
                
                /* Enhanced view button */
                .view-btn {
                    display: flex;
                    align-items: center;
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 0.9rem;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                }
                
                .view-btn:hover {
                    background-color: #1976d2;
                }
                
                .view-btn.active {
                    background-color: #388e3c;
                }
                
                .view-btn i {
                    margin-right: 5px;
                }
                
                /* Selected document highlight */
                .document-item.selected {
                    background-color: #e6f2ff;
                    border-left: 4px solid #0066cc;
                }
                
                /* Make document items clickable */
                .document-item {
                    cursor: pointer;
                    transition: background-color 0.2s;
                }
                
                .document-item:hover {
                    background-color: #f5f5f5;
                }
                
                /* Hide elements with the 'hidden' class */
                .hidden {
                    display: none !important;
                }
            `;
            
            // Add to document head
            document.head.appendChild(style);
        }

        /**
         * Creates a reset button if it doesn't exist
         */
        createResetButton() {
            // Check if reset button already exists
            if (this.elements.resetButton) return;
            
            // Find the action buttons container
            const actionButtons = document.querySelector('.action-buttons');
            if (!actionButtons) return;
            
            // Create reset button
            const resetButton = document.createElement('button');
            resetButton.id = 'reset-references';
            resetButton.className = 'reset-button';
            resetButton.innerHTML = '<i class="fas fa-trash"></i> Reset Reference Sheets';
            
            // Add to action buttons
            actionButtons.appendChild(resetButton);
            
            // Update elements cache
            this.elements.resetButton = resetButton;
        }

        /**
         * Updates the status badge with the current status
         * @param {string} status - Current status (pending, in-progress, completed, error)
         */
        updateStatusBadge(status) {
            if (!this.elements.statusBadge) return;
            
            this.elements.statusBadge.className = 'status-badge ' + status;
            
            switch(status) {
                case 'pending':
                    this.elements.statusBadge.innerHTML = '<i class="fas fa-clock"></i> Pending';
                    break;
                case 'in-progress':
                    this.elements.statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> In Progress';
                    break;
                case 'completed':
                    this.elements.statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Completed';
                    
                    // Create reset button when completed
                    this.createResetButton();
                    
                    // Enable next button
                    this.setNextButtonState(true);
                    break;
                case 'error':
                    this.elements.statusBadge.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error';
                    break;
                default:
                    this.elements.statusBadge.innerHTML = '<i class="fas fa-question-circle"></i> Unknown';
            }
        }
        
        /**
         * Updates the progress bar and related elements
         * @param {number} percentage - Progress percentage (0-100)
         * @param {string} message - Status message to display
         */
        updateProgress(percentage, message) {
            if (this.elements.progressBar) {
                this.elements.progressBar.style.width = `${percentage}%`;
            }
            
            if (this.elements.progressPercentage) {
                this.elements.progressPercentage.textContent = `${percentage}%`;
            }
            
            if (this.elements.progressStatus && message) {
                this.elements.progressStatus.textContent = message;
            }
        }
        
        /**
         * Updates the status metrics in the UI
         * @param {Object} stats - Status metrics object
         */
        updateStatusMetrics(stats) {
            if (this.elements.totalDocuments) {
                this.elements.totalDocuments.textContent = stats.totalDocuments || 0;
            }
            
            if (this.elements.oversizedDocuments) {
                this.elements.oversizedDocuments.textContent = stats.oversizedDocuments || 0;
            }
            
            if (this.elements.sheetsGenerated) {
                this.elements.sheetsGenerated.textContent = stats.sheetsGenerated || 0;
            }
            
            if (this.elements.generationStatus) {
                this.elements.generationStatus.textContent = stats.status || 'Not Started';
            }
        }
        
        /**
         * Renders the list of documents with oversized pages
         * @param {Array} documents - List of documents with oversized pages
         * @param {Function} viewDocumentCallback - Callback function for view button clicks
         */
        renderDocumentList(documents, viewDocumentCallback) {
            if (!this.elements.documentList) return;
            
            // Clear current list
            while (this.elements.documentList.firstChild) {
                if (this.elements.documentList.firstChild === this.elements.emptyState) {
                    break;
                }
                this.elements.documentList.removeChild(this.elements.documentList.firstChild);
            }
            
            // Show empty state if no documents
            if (!documents || documents.length === 0) {
                if (this.elements.emptyState) this.elements.emptyState.classList.remove('hidden');
                return;
            }
            
            // Hide empty state
            if (this.elements.emptyState) this.elements.emptyState.classList.add('hidden');
            
            // Track active document for view button toggle
            this.activeDocumentId = null;
            
            // Add document items
            documents.forEach(doc => {
                const docItem = document.createElement('div');
                docItem.className = 'document-item';
                docItem.dataset.docId = doc.doc_id;
                
                // Create appropriate status indicator
                let statusClass = 'pending';
                let statusIcon = 'clock';
                let statusText = 'Pending';
                
                if (doc.has_reference_sheets) {
                    statusClass = 'completed';
                    statusIcon = 'check-circle';
                    statusText = 'Generated';
                }
                
                docItem.innerHTML = `
                    <div class="document-info">
                        <div class="document-title">${doc.doc_id}</div>
                        <div class="document-details">
                            <span class="document-pages">${doc.page_count} pages</span>
                            <span class="document-oversized">${doc.oversized_ranges ? doc.oversized_ranges.length : 0} oversized ranges</span>
                        </div>
                    </div>
                    <div class="document-status ${statusClass}">
                        <i class="fas fa-${statusIcon}"></i>
                        <span>${statusText}</span>
                    </div>
                    <div class="document-actions">
                        <button class="view-btn" data-doc-id="${doc.doc_id}">
                            <i class="fas fa-eye"></i> View Sheets
                        </button>
                    </div>
                `;
                
                this.elements.documentList.insertBefore(docItem, this.elements.emptyState);
                
                // Add event listener to view button
                const viewBtn = docItem.querySelector('.view-btn');
                if (viewBtn && viewDocumentCallback) {
                    viewBtn.addEventListener('click', (e) => {
                        e.stopPropagation(); // Prevent triggering document item click
                        
                        // Toggle active state
                        const isActive = viewBtn.classList.contains('active');
                        
                        // Remove active state from all buttons
                        document.querySelectorAll('.view-btn').forEach(btn => {
                            btn.classList.remove('active');
                            btn.innerHTML = '<i class="fas fa-eye"></i> View Sheets';
                        });
                        
                        // If clicking the same document, toggle visibility
                        if (this.activeDocumentId === doc.doc_id && isActive) {
                            this.activeDocumentId = null;
                            this.hideReferenceSheets();
                            this.removeDocumentHighlight();
                        } else {
                            // Highlight the selected document
                            this.highlightSelectedDocument(doc.doc_id);
                            // Set active state
                            viewBtn.classList.add('active');
                            viewBtn.innerHTML = '<i class="fas fa-times"></i> Hide Sheets';
                            // Set active document
                            this.activeDocumentId = doc.doc_id;
                            // Call the callback
                            viewDocumentCallback(doc.doc_id);
                        }
                    });
                }
                
                // Make the entire document item clickable
                docItem.addEventListener('click', (e) => {
                    // Don't trigger if clicking on the view button (prevent double execution)
                    if (e.target.closest('.view-btn')) return;
                    
                    const docId = docItem.dataset.docId;
                    const viewBtn = docItem.querySelector('.view-btn');
                    
                    // Remove active state from all buttons
                    document.querySelectorAll('.view-btn').forEach(btn => {
                        btn.classList.remove('active');
                        btn.innerHTML = '<i class="fas fa-eye"></i> View Sheets';
                    });
                    
                    // If clicking the same document, toggle visibility
                    if (this.activeDocumentId === docId) {
                        this.activeDocumentId = null;
                        this.hideReferenceSheets();
                        this.removeDocumentHighlight();
                    } else {
                        // Highlight the selected document
                        this.highlightSelectedDocument(docId);
                        // Set active state
                        if (viewBtn) {
                            viewBtn.classList.add('active');
                            viewBtn.innerHTML = '<i class="fas fa-times"></i> Hide Sheets';
                        }
                        // Set active document
                        this.activeDocumentId = docId;
                        // Call the callback
                        viewDocumentCallback(docId);
                    }
                });
            });
        }
        
        /**
         * Highlights the selected document in the list
         * @param {string} docId - Document ID to highlight
         */
        highlightSelectedDocument(docId) {
            // Remove highlight from all documents
            this.removeDocumentHighlight();
            
            // Add highlight to the selected document
            const selectedDoc = this.elements.documentList.querySelector(`.document-item[data-doc-id="${docId}"]`);
            if (selectedDoc) {
                selectedDoc.classList.add('selected');
            }
        }
        
        /**
         * Removes highlight from all documents
         */
        removeDocumentHighlight() {
            const allDocs = this.elements.documentList.querySelectorAll('.document-item');
            allDocs.forEach(doc => doc.classList.remove('selected'));
        }
        
        /**
         * Hides the reference sheets display
         */
        hideReferenceSheets() {
            // Show animation and hide reference sheets
            if (this.elements.referenceAnimation) {
                this.elements.referenceAnimation.classList.remove('hidden');
            }
            
            if (this.elements.referenceSheetsList) {
                this.elements.referenceSheetsList.classList.add('hidden');
            }
            
            if (this.elements.referenceSheetEmptyState) {
                this.elements.referenceSheetEmptyState.classList.add('hidden');
            }
            
            // Hide PDF viewer
            if (this.elements.pdfViewer) {
                this.elements.pdfViewer.classList.add('hidden');
            }
            
            // Reset the header text
            const header = document.querySelector('.visualization-header h3');
            if (header) {
                header.textContent = 'Reference Sheet Details';
            }
        }
        
        /**
         * Renders the list of reference sheets for a document
         * @param {string} documentId - Document ID
         * @param {Array} referenceSheets - List of reference sheets for the document
         * @param {Function} viewSheetCallback - Callback function for viewing a sheet
         */
        renderReferenceSheetsList(documentId, referenceSheets, viewSheetCallback) {
            if (!this.elements.referenceSheetsList) return;
            
            // Hide the animation and show the reference sheets container
            if (this.elements.referenceAnimation) {
                this.elements.referenceAnimation.classList.add('hidden');
            }
            
            if (this.elements.referenceSheetsList) {
                this.elements.referenceSheetsList.classList.remove('hidden');
            }
            
            // Close any existing inline PDF viewers
            const existingViewers = document.querySelectorAll('.inline-pdf-container');
            existingViewers.forEach(viewer => viewer.remove());
            
            // Update the header text
            const header = document.querySelector('.visualization-header h3');
            if (header) {
                header.textContent = `Reference Sheets for Document: ${documentId}`;
            }
            
            // Clear current list
            this.elements.referenceSheetsList.innerHTML = '';
            
            // Add preview description
            const previewDescription = document.createElement('p');
            previewDescription.className = 'preview-description';
            previewDescription.textContent = `This document has ${referenceSheets.length} reference sheet(s). Click to view or print:`;
            this.elements.referenceSheetsList.appendChild(previewDescription);
            
            // Show empty state if no reference sheets
            if (!referenceSheets || referenceSheets.length === 0) {
                if (this.elements.referenceSheetEmptyState) {
                    this.elements.referenceSheetEmptyState.classList.remove('hidden');
                    const firstParagraph = this.elements.referenceSheetEmptyState.querySelector('p:first-child');
                    if (firstParagraph) {
                        firstParagraph.textContent = 'No reference sheets available for this document';
                    }
                }
                return;
            }
            
            // Hide empty state
            if (this.elements.referenceSheetEmptyState) {
                this.elements.referenceSheetEmptyState.classList.add('hidden');
            }
            
            // Add reference sheet items
            referenceSheets.forEach((sheet, index) => {
                const sheetItem = document.createElement('div');
                sheetItem.className = 'reference-sheet-item';
                sheetItem.dataset.sheetId = sheet.id;
                
                // Format range for display
                const rangeStart = sheet.range[0];
                const rangeEnd = sheet.range[1];
                const rangeText = rangeStart === rangeEnd ? 
                    `Page ${rangeStart}` : 
                    `Pages ${rangeStart}-${rangeEnd}`;
                
                sheetItem.innerHTML = `
                    <div class="sheet-info">
                        <div class="sheet-title">Reference Sheet ${index + 1}</div>
                        <div class="sheet-details">
                            <span class="sheet-range">${rangeText}</span>
                            <span class="sheet-blip">Blip: ${sheet.blip_35mm || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="sheet-actions">
                        <button class="view-sheet-btn" data-sheet-id="${sheet.id}">
                            <i class="fas fa-file-pdf"></i> View
                        </button>
                    </div>
                `;
                
                this.elements.referenceSheetsList.appendChild(sheetItem);
                
                // Add event listener to view button
                const viewBtn = sheetItem.querySelector('.view-sheet-btn');
                if (viewBtn && viewSheetCallback) {
                    viewBtn.addEventListener('click', () => {
                        viewSheetCallback(sheet.id);
                    });
                }
            });
        }
        
        /**
         * Shows or hides the reference animation based on workflow type
         * @param {boolean} show - Whether to show the animation
         */
        toggleReferenceAnimation(show) {
            if (this.elements.referenceAnimation) {
                if (show) {
                    this.elements.referenceAnimation.classList.remove('hidden');
                    
                    // Hide reference sheets when showing animation
                    if (this.elements.referenceSheetsList) {
                        this.elements.referenceSheetsList.classList.add('hidden');
                    }
                    
                    if (this.elements.referenceSheetEmptyState) {
                        this.elements.referenceSheetEmptyState.classList.add('hidden');
                    }
                } else {
                    this.elements.referenceAnimation.classList.add('hidden');
                }
            }
        }
        
        /**
         * Shows or hides the inactive message
         * @param {boolean} show - Whether to show the message
         */
        toggleInactiveMessage(show) {
            if (this.elements.inactiveMessage) {
                if (show) {
                    this.elements.inactiveMessage.classList.remove('hidden');
                } else {
                    this.elements.inactiveMessage.classList.add('hidden');
                }
            }
        }
        
        /**
         * Enables or disables the generate button
         * @param {boolean} enabled - Whether the button should be enabled
         */
        setGenerateButtonState(enabled) {
            if (this.elements.generateButton) {
                this.elements.generateButton.disabled = !enabled;
            }
        }
        
        /**
         * Enables or disables the reset button
         * @param {boolean} enabled - Whether the button should be enabled
         */
        setResetButtonState(enabled) {
            if (this.elements.resetButton) {
                this.elements.resetButton.disabled = !enabled;
            }
        }
        
        /**
         * Enables or disables the next button
         * @param {boolean} enabled - Whether the button should be enabled
         */
        setNextButtonState(enabled) {
            if (this.elements.nextButton) {
                this.elements.nextButton.disabled = !enabled;
            }
        }
        
        /**
         * Updates the debug data output
         * @param {Object} data - Data to display
         */
        updateDataOutput(data) {
            if (this.elements.dataOutput) {
                this.elements.dataOutput.textContent = JSON.stringify(data, null, 2);
            }
        }
        
        /**
         * Shows a notification message
         * @param {string} message - Message to display
         * @param {string} type - Type of notification (success, error, info)
         */
        showNotification(message, type = 'info') {
            // Use the global notification system if available
            if (typeof window.showNotification === 'function') {
                window.showNotification(message, type);
            } else {
                console.log(`[${type.toUpperCase()}] ${message}`);
            }
        }

        /**
         * Shows a reference sheet PDF in an inline viewer directly below the clicked reference sheet card
         * @param {string} documentId - ID of the document
         * @param {string} pdfBase64 - Base64-encoded PDF data
         * @param {number} sheetIndex - Index of the reference sheet (for display purposes)
         * @param {string} sheetId - ID of the reference sheet
         */
        showReferencePdf(documentId, pdfBase64, sheetIndex = 0, sheetId) {
            // Don't hide the reference sheets list anymore - we want to keep it visible
            
            // Find the reference sheet item
            const sheetItem = document.querySelector(`.reference-sheet-item[data-sheet-id="${sheetId}"]`);
            if (!sheetItem) return;
            
            // Toggle behavior: If there's already a viewer beneath this item, remove it and exit
            const existingViewer = sheetItem.nextElementSibling;
            if (existingViewer && existingViewer.classList.contains('inline-pdf-container')) {
                existingViewer.remove();
                
                // Reset the view button for this item
                const viewBtn = sheetItem.querySelector('.view-sheet-btn');
                if (viewBtn) {
                    viewBtn.innerHTML = '<i class="fas fa-file-pdf"></i> View';
                }
                return;
            }
            
            // First, close any other open PDF viewers
            const existingViewers = document.querySelectorAll('.inline-pdf-container');
            existingViewers.forEach(viewer => viewer.remove());
            
            // Reset all view buttons to default state
            document.querySelectorAll('.view-sheet-btn').forEach(btn => {
                btn.innerHTML = '<i class="fas fa-file-pdf"></i> View';
            });
            
            // Update the view button to indicate active state
            const viewBtn = sheetItem.querySelector('.view-sheet-btn');
            if (viewBtn) {
                viewBtn.innerHTML = '<i class="fas fa-times"></i> Hide';
            }
            
            // Create an inline PDF container
            const inlinePdfContainer = document.createElement('div');
            inlinePdfContainer.className = 'inline-pdf-container';
            inlinePdfContainer.innerHTML = `
                <div class="viewer-header">
                    <span class="viewer-title">Reference Sheet ${sheetIndex+1} for ${documentId}</span>
                </div>
                <div class="viewer-content">
                    <embed id="pdf-embed-${sheetId}" type="application/pdf" width="100%" height="500px" />
                </div>
            `;
            
            // Insert after the clicked sheet item
            sheetItem.parentNode.insertBefore(inlinePdfContainer, sheetItem.nextSibling);
            
            // Set the PDF data
            const pdfEmbed = document.getElementById(`pdf-embed-${sheetId}`);
            if (pdfEmbed) {
                pdfEmbed.src = `data:application/pdf;base64,${pdfBase64}`;
            }
        }
        
        /**
         * Closes the inline PDF viewer
         */
        closeInlinePdfViewer() {
            // Remove all inline PDF viewers
            const existingViewers = document.querySelectorAll('.inline-pdf-container');
            existingViewers.forEach(viewer => viewer.remove());
            
            // Reset all view buttons to default state
            document.querySelectorAll('.view-sheet-btn').forEach(btn => {
                btn.innerHTML = '<i class="fas fa-file-pdf"></i> View';
            });
        }
        
        /**
         * Checks and sets the next button state based on current status
         */
        updateNextButtonBasedOnStatus() {
            // Check localStorage for workflow state
            try {
                const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                const referenceState = workflowState.referenceSheets || {};
                
                // Enable next button if status is completed
                if (referenceState.status === 'completed' || referenceState.completed === true) {
                    this.setNextButtonState(true);
                    return true;
                }
                
                // Also check if reference sheets exist in localStorage
                const referenceSheets = JSON.parse(localStorage.getItem('microfilmReferenceSheets') || '{}');
                if (referenceSheets.status === 'success' || 
                    referenceSheets.sheetsCreated > 0 || 
                    (referenceSheets.referenceSheets && Object.keys(referenceSheets.referenceSheets).length > 0)) {
                    this.setNextButtonState(true);
                    return true;
                }
            } catch (e) {
                console.error('Error checking reference sheets status:', e);
            }
            
            return false;
        }
        
        /**
         * Resets the reference sheets UI and data
         */
        resetReferenceSheets() {
            // Clear localStorage
            localStorage.removeItem('microfilmReferenceSheets');
            
            // Update UI
            this.updateStatusBadge('pending');
            this.hideReferenceSheets();
            this.removeDocumentHighlight();
            this.setNextButtonState(false);
            
            // Reset metrics
            this.updateStatusMetrics({
                sheetsGenerated: 0,
                status: 'Not Started'
            });
            
            // Reset view buttons
            document.querySelectorAll('.view-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="fas fa-eye"></i> View Sheets';
            });
            
            // Clear active document
            this.activeDocumentId = null;
            
            // Hide PDF viewer if visible (both inline and old viewer)
            if (this.elements.pdfViewer) {
                this.elements.pdfViewer.classList.add('hidden');
            }
            
            // Remove all inline PDF viewers
            const existingViewers = document.querySelectorAll('.inline-pdf-container');
            existingViewers.forEach(viewer => viewer.remove());
            
            // Reset all view sheet buttons to default state
            document.querySelectorAll('.view-sheet-btn').forEach(btn => {
                btn.innerHTML = '<i class="fas fa-file-pdf"></i> View';
            });
            
            // Show animation
            this.toggleReferenceAnimation(true);
            
            // Show notification
            this.showNotification('Reference sheets have been reset', 'info');
        }

        /**
         * Update document metadata display with enhanced information
         * @param {string} documentId - Document ID
         * @param {Object} metadata - Enhanced document metadata
         */
        updateDocumentMetadata(documentId, metadata) {
            // Find or create metadata container
            let metadataContainer = document.querySelector('.document-metadata');
            if (!metadataContainer) {
                metadataContainer = document.createElement('div');
                metadataContainer.className = 'document-metadata';
                const headerArea = document.querySelector('.visualization-header');
                if (headerArea) {
                    headerArea.appendChild(metadataContainer);
                }
            }
            
            // Create enhanced metadata display
            let metadataContent = `
                <div class="metadata-header">Document Details: ${documentId}</div>
                <div class="metadata-content">
                    <div class="metadata-row">
                        <span class="metadata-label">Total Sheets:</span>
                        <span class="metadata-value">${metadata.sheetCount || 'N/A'}</span>
                    </div>
            `;
            
            // Add human readable ranges if available
            if (metadata.humanRanges && metadata.humanRanges.length > 0) {
                metadataContent += `
                    <div class="metadata-row">
                        <span class="metadata-label">Page Ranges:</span>
                        <span class="metadata-value">${metadata.humanRanges.join(', ')}</span>
                    </div>
                `;
            }
            
            // Add film numbers if available
            if (metadata.filmNumbers && metadata.filmNumbers.length > 0) {
                metadataContent += `
                    <div class="metadata-row">
                        <span class="metadata-label">Film Numbers:</span>
                        <span class="metadata-value">${metadata.filmNumbers.join(', ')}</span>
                    </div>
                `;
            }
            
            metadataContent += '</div>';
            
            metadataContainer.innerHTML = metadataContent;
            
            // Add CSS for metadata display if needed
            this.addMetadataStyles();
        }

        /**
         * Add CSS styles for metadata display
         */
        addMetadataStyles() {
            // Check if styles already exist
            if (document.getElementById('metadata-styles')) return;
            
            // Create style element
            const style = document.createElement('style');
            style.id = 'metadata-styles';
            style.textContent = `
                .document-metadata {
                    margin: 15px 0;
                    padding: 10px 15px;
                    background-color: #f8f9fa;
                    border-radius: 6px;
                    border-left: 4px solid #0066cc;
                }
                
                .metadata-header {
                    font-weight: bold;
                    font-size: 16px;
                    color: #333;
                    margin-bottom: 8px;
                }
                
                .metadata-content {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                
                .metadata-row {
                    display: flex;
                    align-items: baseline;
                }
                
                .metadata-label {
                    font-weight: 500;
                    color: #555;
                    min-width: 120px;
                }
                
                .metadata-value {
                    color: #333;
                }
            `;
            
            // Add to document head
            document.head.appendChild(style);
        }
    }

    // Public API
    return {
        ReferencesUI: ReferencesUIClass
    };
})(); 