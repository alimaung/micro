/**
 * References Module - API
 * Handles all backend API calls related to reference sheets
 */

// API module using IIFE pattern
const ReferencesAPI = (function() {
    /**
     * API class for reference sheet operations
     */
    class ReferencesAPIClass {
        /**
         * Initialize the API with a project ID
         * @param {string} projectId - The project ID
         */
        constructor(projectId) {
            this.projectId = projectId;
        }

        /**
         * Fetches the current reference sheet status
         * @returns {Promise} Promise resolving to status data
         */
        getStatus() {
            return fetch(`/api/references/status/${this.projectId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch reference status');
                    }
                    return response.json();
                });
        }
        
        /**
         * Generate reference sheets for the current project
         * @returns {Promise} Promise that resolves with the generation results
         */
        async generateReferenceSheets() {
            try {
                // Get data from localStorage for sending to backend
                const projectData = this.getLocalStorageItem('microfilmProjectState');
                const analysisData = this.getLocalStorageItem('microfilmAnalysisData');
                const allocationData = this.getLocalStorageItem('microfilmAllocationData');
                const filmNumberResults = this.getLocalStorageItem('microfilmFilmNumberResults');
                
                // Log what data we have available
                console.log('[ReferencesAPI] Generating reference sheets with data:');
                console.log('- projectData:', projectData ? 'available' : 'not found');
                console.log('- analysisData:', analysisData ? 'available' : 'not found');
                console.log('- allocationData:', allocationData ? 'available' : 'not found');
                console.log('- filmNumberResults:', filmNumberResults ? 'available' : 'not found');
                
                // Make the API call
                const response = await fetch(`/api/references/generate/${this.projectId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken
                    },
                    body: JSON.stringify({
                        project_data: projectData,
                        analysis_data: analysisData,
                        allocation_data: allocationData,
                        film_number_results: filmNumberResults
                    })
                });
                
                // Handle errors
                if (!response.ok) {
                    throw new Error(`Error generating reference sheets: ${response.statusText}`);
                }
                
                // Process the response
                const result = await response.json();
                console.log('[ReferencesAPI] Reference sheet generation successful:', result);
                
                // Log detailed information about the response format
                console.log('[ReferencesAPI] Response format details:');
                console.log('- Has reference_sheets field:', 'reference_sheets' in result); // >>> Has reference_sheets and document_details
                //console.log('- Has referenceSheets field:', 'referenceSheets' in result);
                console.log('- Response keys:', Object.keys(result));
                
                // Save the result to localStorage for recovery
                this.saveReferenceResult(result);
                
                return result;
            } catch (error) {
                console.error('[ReferencesAPI] Error generating reference sheets:', error);
                throw error;
            }
        }
        
        /**
         * Fetches all reference sheets for the current project
         * @returns {Promise} Promise resolving to reference sheet data
         */
        getReferenceSheets() {
            return fetch(`/api/references/get/${this.projectId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch reference sheets');
                    }
                    return response.json();
                });
        }
        
        /**
         * Fetches a reference sheet PDF as base64
         * @param {number} referenceSheetId - ID of the reference sheet
         * @returns {Promise} Promise resolving to PDF data
         */
        getReferenceSheetPdf(referenceSheetId) {
            return fetch(`/api/references/pdf/${referenceSheetId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch reference sheet PDF');
                    }
                    return response.json();
                });
        }
        
        /**
         * Inserts reference sheets into a document
         * @param {string} documentId - ID of the document
         * @param {boolean} is35mm - Whether the document is for 35mm film
         * @returns {Promise} Promise resolving to insertion results
         */
        insertReferenceSheets(documentId, is35mm = false) {
            return fetch(`/api/references/insert/${this.projectId}/${documentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': ReferencesUtils.getCsrfToken()
                },
                body: JSON.stringify({
                    is_35mm: is35mm
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to insert reference sheets');
                }
                return response.json();
            });
        }

        /**
         * Gets document ranges for a specific document
         * @param {string} documentId - ID of the document
         * @returns {Promise} Promise resolving to document range data
         */
        getDocumentRanges(documentId) {
            return fetch(`/api/references/ranges/${this.projectId}/${documentId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch document ranges');
                    }
                    return response.json();
                });
        }

        /**
         * Gets all processed documents for the project
         * @returns {Promise} Promise resolving to processed documents data
         */
        getProcessedDocuments() {
            return fetch(`/api/references/processed/${this.projectId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch processed documents');
                    }
                    return response.json();
                });
        }

        /**
         * Get localStorage item and parse as JSON
         * @param {string} key - The localStorage key
         * @returns {Object|null} The parsed data or null if not found
         */
        getLocalStorageItem(key) {
            try {
                const data = localStorage.getItem(key);
                if (!data) {
                    return null;
                }
                return JSON.parse(data);
            } catch (error) {
                console.error(`[ReferencesAPI] Error parsing localStorage item ${key}:`, error);
                return null;
            }
        }

        /**
         * Save reference result to localStorage
         * @param {Object} result - Reference generation result from the API
         */
        saveReferenceResult(result) {
            try {
                // Ensure the result is valid
                if (!result) {
                    console.error('[ReferencesAPI] Cannot save empty reference result');
                    return;
                }

                // Prepare data to save, ensuring both snake_case and camelCase versions exist
                const dataToSave = {
                    projectId: this.projectId,
                    project_id: this.projectId,
                    reference_sheets: result.reference_sheets || result.referenceSheets || {},
                    status: result.status || 'success',
                    sheetsCreated: result.sheets_created || result.sheetsCreated || 0,
                    sheets_created: result.sheets_created || result.sheetsCreated || 0,
                    documents_details: result.documents_details || {},
                    timestamp: new Date().toISOString()
                };

                // Save to localStorage
                localStorage.setItem('microfilmReferenceSheets', JSON.stringify(dataToSave));
                console.log('[ReferencesAPI] Saved reference sheets to localStorage', dataToSave);

                // Update workflow state
                const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                workflowState.referenceSheets = {
                    completed: true,
                    timestamp: new Date().toISOString()
                };
                localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));

            } catch (error) {
                console.error('[ReferencesAPI] Error saving reference result to localStorage:', error);
            }
        }
    }

    // Public API
    return {
        ReferencesAPI: ReferencesAPIClass
    };
})(); 