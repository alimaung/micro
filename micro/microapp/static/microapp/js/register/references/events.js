/**
 * References Module - Events
 * Handles all event listeners and user interactions
 */

// Events module using IIFE pattern
const ReferencesEvents = (function() {
    /**
     * Event handler for references module
     */
    class ReferencesEventsClass {
        /**
         * Initialize the event handler
         * @param {Object} ui - UI manager instance
         * @param {Object} api - API manager instance
         * @param {Object} core - Core manager instance
         */
        constructor(ui, api, core) {
            this.ui = ui;
            this.api = api;
            this.core = core;
            this.isGenerating = false;
            this.progressInterval = null;
        }

        /**
         * Initialize all event listeners
         */
        init() {
            // Generate button click
            if (this.ui.elements.generateButton) {
                this.ui.elements.generateButton.addEventListener('click', () => this.onGenerateClick());
            }
            
            // Reset button click (will be created dynamically when generation completes)
            document.addEventListener('click', (e) => {
                if (e.target && (e.target.id === 'reset-references' || e.target.closest('#reset-references'))) {
                    this.onResetClick();
                }
            });
            
            // Refresh list button click
            if (this.ui.elements.refreshListButton) {
                this.ui.elements.refreshListButton.addEventListener('click', () => this.onRefreshListClick());
            }
            
            // Navigation button clicks
            if (this.ui.elements.backButton) {
                this.ui.elements.backButton.addEventListener('click', () => this.onBackClick());
            }
            
            if (this.ui.elements.nextButton) {
                this.ui.elements.nextButton.addEventListener('click', () => this.onNextClick());
            }
            
            // Check button state on initialization
            this.ui.updateNextButtonBasedOnStatus();
        }
        
        /**
         * Handles generate button click
         */
        onGenerateClick() {
            if (this.isGenerating) return;
            
            // Update UI
            this.isGenerating = true;
            this.ui.updateStatusBadge('in-progress');
            this.ui.setGenerateButtonState(false);
            this.ui.updateProgress(0, 'Starting reference sheet generation...');
            
            // Start fake progress
            let progress = 0;
            this.progressInterval = setInterval(() => {
                progress += 2;
                this.ui.updateProgress(progress, ReferencesUtils.getProgressMessage(progress));
                
                if (progress >= 95) {
                    clearInterval(this.progressInterval);
                }
            }, 100);
            
            // Call API to generate reference sheets
            this.api.generateReferenceSheets()
                .then(result => {
                    clearInterval(this.progressInterval);
                    
                    if (result.status === 'success' || result.status === 'skipped') {
                        // Update UI with success
                        this.ui.updateProgress(100, 'Reference sheet generation complete!');
                        this.ui.updateStatusBadge('completed');
                        this.ui.showNotification(result.message, 'success');
                        
                        // Enable next button
                        this.ui.setNextButtonState(true);
                        
                        // Update status and refresh
                        this.core.setStatus('completed');
                        this.isGenerating = false;
                        
                        // Save to workflow state
                        ReferencesUtils.saveToWorkflowState({
                            referenceSheets: {
                                status: 'completed',
                                message: result.message,
                                sheets_created: result.sheets_created
                            }
                        });
                        
                        // Refresh data
                        this.core.refreshData();
                    } else {
                        // Handle error case
                        this.ui.updateProgress(100, 'Generation completed with warnings');
                        this.ui.updateStatusBadge('error');
                        this.ui.showNotification(result.message, 'warning');
                        this.ui.setGenerateButtonState(true);
                        this.isGenerating = false;
                    }
                })
                .catch(error => {
                    clearInterval(this.progressInterval);
                    console.error('Error generating reference sheets:', error);
                    
                    // Update UI with error
                    this.ui.updateProgress(0, 'Error generating reference sheets');
                    this.ui.updateStatusBadge('error');
                    this.ui.showNotification('Failed to generate reference sheets: ' + error.message, 'error');
                    
                    // Re-enable generate button
                    this.ui.setGenerateButtonState(true);
                    this.isGenerating = false;
                });
        }
        
        /**
         * Handles reset button click
         */
        onResetClick() {
            // Confirm reset
            if (confirm('Are you sure you want to reset all reference sheets? This action cannot be undone.')) {
                // Reset reference sheets
                this.ui.resetReferenceSheets();
                
                // Update core status
                this.core.setStatus('pending');
                
                // Re-enable generate button and disable reset button
                this.ui.setGenerateButtonState(true);
                this.ui.setResetButtonState(false);
                
                // Disable next button
                this.ui.setNextButtonState(false);
                
                // Save to workflow state
                ReferencesUtils.saveToWorkflowState({
                    referenceSheets: {
                        status: 'pending',
                        message: 'Reference sheets reset',
                        sheets_created: 0
                    }
                });
            }
        }
        
        /**
         * Handles refresh list button click
         */
        onRefreshListClick() {
            this.core.refreshData();
        }
        
        /**
         * Handles back button click
         */
        onBackClick() {
            // Preserve workflow type in URL when navigating
            const nextUrl = '/register/filmnumber/';
            this.navigateWithParams(nextUrl);
        }
        
        /**
         * Handles next button click
         */
        onNextClick() {
            // Save current state
            ReferencesUtils.saveToWorkflowState({
                referenceSheets: {
                    status: this.core.getStatus(),
                    completed: this.core.getStatus() === 'completed'
                }
            });
            
            // Get current URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            
            // Navigate to next step with workflow parameter preserved
            const nextUrl = '/register/distribution/';
            this.navigateWithParams(nextUrl, urlParams);
        }
        
        /**
         * Navigate to URL while preserving workflow parameter
         * @param {string} baseUrl - The base URL to navigate to
         */
        navigateWithParams(baseUrl) {
            // Check if we need to preserve the flow parameter
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('flow')) {
                const flowType = urlParams.get('flow');
                const projectId = urlParams.get('project_id') || '';
                
                // Add parameters to URL
                const separator = baseUrl.includes('?') ? '&' : '?';
                const paramsToAdd = [];
                
                if (flowType) {
                    paramsToAdd.push(`flow=${flowType}`);
                }
                
                if (projectId) {
                    paramsToAdd.push(`project_id=${projectId}`);
                }
                
                if (paramsToAdd.length > 0) {
                    window.location.href = `${baseUrl}${separator}${paramsToAdd.join('&')}`;
                    return;
                }
            }
            
            // Default navigation if no parameters to preserve
            window.location.href = baseUrl;
        }
        
        /**
         * Handles view document button click
         * @param {string} documentId - ID of the document to view
         */
        onViewDocument(documentId) {
            // Get reference sheets for this document
            const referenceSheets = this.core.getReferenceSheets();
            const docSheets = referenceSheets[documentId] || [];
            
            if (docSheets.length === 0) {
                this.ui.showNotification('No reference sheets found for this document', 'info');
                return;
            }
            
            // Render the list of reference sheets for this document
            this.ui.renderReferenceSheetsList(documentId, docSheets, (sheetId) => {
                this.onViewReferenceSheet(documentId, sheetId);
            });
        }

        /**
         * Handles viewing a specific reference sheet
         * @param {string} documentId - ID of the document
         * @param {number} sheetId - ID of the reference sheet
         */
        onViewReferenceSheet(documentId, sheetId) {
            // Get reference sheets for this document
            const referenceSheets = this.core.getReferenceSheets();
            const docSheets = referenceSheets[documentId] || [];
            
            // Find the specific sheet by ID
            const sheetIndex = docSheets.findIndex(sheet => sheet.id === sheetId);
            if (sheetIndex === -1) {
                this.ui.showNotification('Reference sheet not found', 'error');
                return;
            }
            
            // Fetch the PDF data
            this.api.getReferenceSheetPdf(sheetId)
                .then(result => {
                    if (result.status === 'success' && result.pdf_data) {
                        // Show PDF in inline viewer - pass sheetId to allow toggling
                        this.ui.showReferencePdf(documentId, result.pdf_data, sheetIndex, sheetId);
                    } else {
                        this.ui.showNotification('Failed to load reference sheet PDF', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error fetching PDF:', error);
                    this.ui.showNotification('Failed to load reference sheet PDF', 'error');
                });
        }

        /**
         * Handle document selection
         * @param {string} documentId - The selected document ID
         */
        onSelectDocument(documentId) {
            // Update UI to highlight selected document
            this.ui.highlightDocument(documentId);
            
            // Get reference sheets for this document
            const referenceSheets = this.core.getReferenceSheets()[documentId] || [];
            
            // Render the reference sheets list
            this.ui.renderReferenceSheetsList(documentId, referenceSheets, (sheetId) => {
                this.onViewReferenceSheet(documentId, sheetId);
            });
            
            // Display enhanced metadata if available
            this.core.displayEnhancedDocumentInfo(documentId);
        }
    }

    // Public API
    return {
        ReferencesEvents: ReferencesEventsClass
    };
})(); 