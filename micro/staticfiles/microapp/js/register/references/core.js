/**
 * References Module - Core
 * Handles core business logic for reference sheets management
 */

// Core module using IIFE pattern
const ReferencesCore = (function() {
    // Debug flag
    const DEBUG = true;
    
    /**
     * Core manager for references functionality
     */
    class ReferencesCoreClass {
        /**
         * Initialize the core manager
         * @param {Object} ui - UI manager instance
         * @param {Object} api - API manager instance
         * @param {string} projectId - Project ID
         */
        constructor(ui, api, projectId) {
            this.ui = ui;
            this.api = api;
            this.projectId = projectId;
            this.currentStatus = 'pending';
            this.referenceSheets = {};
            this.workflowState = ReferencesUtils.loadFromWorkflowState();
            this.isHybridWorkflow = ReferencesUtils.isHybridWorkflow();
            
            // Log workflow type detection
            DEBUG && console.log('[ReferencesCore] Workflow type detected on load:', this.isHybridWorkflow ? 'hybrid' : 'standard');
        }

        /**
         * Initialize the core functionality
         */
        init() {
            // Immediately set initial UI state based on URL parameters
            this.setInitialUIState();
            
            // Load data from localStorage instead of making API call
            this.loadDataFromLocalStorage();
            
            // Check if we should enable the next button based on stored state
            this.ui.updateNextButtonBasedOnStatus();
        }
        
        /**
         * Load initial data from localStorage
         */
        loadDataFromLocalStorage() {
            DEBUG && console.log('[ReferencesCore] Loading data from localStorage');
            
            // Load data from localStorage
            const projectState = this.getLocalStorageItem('microfilmProjectState');
            const analysisData = this.getLocalStorageItem('microfilmAnalysisData');
            const allocationData = this.getLocalStorageItem('microfilmAllocationData');
            const indexData = this.getLocalStorageItem('microfilmIndexData');
            const filmNumberResults = this.getLocalStorageItem('microfilmFilmNumberResults');
            const referenceSheets = this.getLocalStorageItem('microfilmReferenceSheets');
            
            DEBUG && console.log('[ReferencesCore] LocalStorage data loaded:');
            DEBUG && console.log('- projectState:', projectState ? projectState : 'not found');
            DEBUG && console.log('- analysisData:', analysisData ? analysisData : 'not found');
            DEBUG && console.log('- allocationData:', allocationData ? allocationData : 'not found');
            DEBUG && console.log('- indexData:', indexData ? indexData : 'not found');
            DEBUG && console.log('- filmNumberResults:', filmNumberResults ? filmNumberResults : 'not found');
            DEBUG && console.log('- referenceSheets:', referenceSheets ? referenceSheets : 'not found');
            DEBUG && console.log('- referenceSheets structure:', referenceSheets ? JSON.stringify(referenceSheets, null, 2) : 'not found');
            
            // Check workflow state for completion status
            const workflowState = this.getLocalStorageItem('microfilmWorkflowState') || {};
            const referenceState = workflowState.referenceSheets || {};
            
            // Use reference sheets data if available
            if (referenceSheets) {
                // Initialize a proper document-sheets map
                this.referenceSheets = {};
                
                // Log the detailed structure for debugging
                DEBUG && console.log('[ReferencesCore] Reference sheets keys:', Object.keys(referenceSheets));
                
                // Process data based on structure
                if (referenceSheets.referenceSheets && typeof referenceSheets.referenceSheets === 'object') {
                    // Format is { projectId, referenceSheets: { doc1: [...], doc2: [...] } }
                    DEBUG && console.log('[ReferencesCore] Using reference sheets from camelCase format');
                    this.referenceSheets = this.enrichReferenceSheets(referenceSheets.referenceSheets, referenceSheets);
                } else if (referenceSheets.reference_sheets && typeof referenceSheets.reference_sheets === 'object') {
                    // Format is { project_id, reference_sheets: { doc1: [...], doc2: [...] } }
                    DEBUG && console.log('[ReferencesCore] Using reference sheets from snake_case format');
                    this.referenceSheets = this.enrichReferenceSheets(referenceSheets.reference_sheets, referenceSheets);
                } else if (referenceSheets.projectId === this.projectId && typeof referenceSheets === 'object') {
                    // Look for document keys directly (fallback)
                    DEBUG && console.log('[ReferencesCore] Looking for valid document keys in reference data');
                    
                    // Check each key to see if it looks like a document ID (avoid metadata fields)
                    const docKeys = Object.keys(referenceSheets).filter(key => {
                        // If the value is an array and not a top-level metadata property
                        return Array.isArray(referenceSheets[key]) && 
                               ![
                                   'projectId', 'project_id', 'status', 'timestamp', 
                                   'sheetsCreated', 'sheets_created', 'reference_sheets', 
                                   'referenceSheets', 'enhancedDetails', 'documents_details'
                               ].includes(key);
                    });
                    
                    DEBUG && console.log('[ReferencesCore] Found document keys:', docKeys);
                    
                    // Extract document sheets
                    docKeys.forEach(docKey => {
                        this.referenceSheets[docKey] = referenceSheets[docKey];
                    });
                    
                    // If we didn't find any document keys but enhancedDetails is present
                    if (Object.keys(this.referenceSheets).length === 0 && referenceSheets.enhancedDetails) {
                        DEBUG && console.log('[ReferencesCore] Using enhancedDetails for document data');
                        // Extract documents from enhancedDetails
                        Object.keys(referenceSheets.enhancedDetails).forEach(docKey => {
                            const docDetails = referenceSheets.enhancedDetails[docKey];
                            // Create reference sheet entries for this document
                            this.referenceSheets[docKey] = docDetails.sheet_ids.map((id, index) => {
                                return {
                                    id: id,
                                    range: docDetails.ranges[index],
                                    blip: docDetails.blips ? docDetails.blips[index] : null,
                                    blip_35mm: docDetails.blips ? docDetails.blips[index] : null, // Add for UI compatibility
                                    film_number: docDetails.film_numbers ? docDetails.film_numbers[index] : null,
                                    human_readable_range: docDetails.human_readable_ranges ? docDetails.human_readable_ranges[index] : null
                                };
                            });
                        });
                    }
                }
                
                DEBUG && console.log('[ReferencesCore] Processed reference sheets:', this.referenceSheets);
                
                // Update status based on reference sheet data
                if (this.referenceSheets && Object.keys(this.referenceSheets).length > 0) {
                    this.currentStatus = 'completed';
                    this.ui.updateStatusBadge('completed');
                    
                    // Update metrics
                    this.ui.updateStatusMetrics({
                        totalDocuments: analysisData?.analysisResults?.documentCount || 0,
                        oversizedDocuments: analysisData?.analysisResults?.documentsWithOversized || 0,
                        sheetsGenerated: referenceSheets.sheetsCreated || referenceSheets.sheets_created || 0,
                        status: 'Completed'
                    });
                    
                    // Prepare document list from reference sheets
                    const documents = Object.keys(this.referenceSheets).map(docId => {
                        return {
                            doc_id: docId,
                            has_reference_sheets: this.referenceSheets[docId].length > 0,
                            oversized_ranges: this.referenceSheets[docId],
                            page_count: 0 // Not available from localStorage
                        };
                    });
                    
                    // Use a bound function for the view document callback
                    const viewDocumentCallback = (docId) => {
                        // Assuming events instance has been attached to the core
                        if (this.events) {
                            this.events.onViewDocument(docId);
                        }
                    };
                    
                    this.ui.renderDocumentList(documents, viewDocumentCallback);
                    
                    // Do NOT automatically select the first document - keep animation visible by default
                } else {
                    DEBUG && console.log('[ReferencesCore] No valid reference sheets found in structure');
                }
            }
            
            // Extract relevant data from allocation results if available
            if (allocationData && allocationData.allocationResults) {
                const results = allocationData.allocationResults;
                DEBUG && console.log('[ReferencesCore] Allocation results:', results);
                
                // Extract key metrics
                const totalDocuments = results.documentCount || 0;
                const oversizedDocuments = results.documentsWithOversized || 0;
                const hasOversized = results.hasOversized || false;
                const status = results.status || 'pending';
                
                DEBUG && console.log('[ReferencesCore] Extracted metrics:');
                DEBUG && console.log('- totalDocuments:', totalDocuments);
                DEBUG && console.log('- oversizedDocuments:', oversizedDocuments);
                DEBUG && console.log('- hasOversized:', hasOversized);
                DEBUG && console.log('- status:', status);
                
                // Update UI with localStorage data (only if we don't have reference sheets)
                if (!this.referenceSheets || Object.keys(this.referenceSheets).length === 0) {
                    this.ui.updateStatusMetrics({
                        totalDocuments: totalDocuments,
                        oversizedDocuments: oversizedDocuments,
                        sheetsGenerated: 0, // Default to 0 until API provides actual number
                        status: this.currentStatus === 'completed' ? 'Completed' : 'Pending'
                    });
                }
                
                // Update data output for debugging
                this.ui.updateDataOutput({
                    documentCount: totalDocuments,
                    documentsWithOversized: oversizedDocuments,
                    hasOversized: hasOversized,
                    status: status,
                    source: 'localStorage'
                });
            } else {
                DEBUG && console.log('[ReferencesCore] No allocation data found in localStorage');
            }
        }
        
        /**
         * Helper method to safely get and parse localStorage item
         * @param {string} key - localStorage key
         * @returns {Object|null} Parsed object or null if not found
         */
        getLocalStorageItem(key) {
            try {
                const item = localStorage.getItem(key);
                if (item) {
                    return JSON.parse(item);
                }
            } catch (e) {
                console.error(`Error parsing localStorage item ${key}:`, e);
            }
            return null;
        }
        
        /**
         * Set initial UI state based on URL parameters before any API calls
         */
        setInitialUIState() {
            DEBUG && console.log('[ReferencesCore] Setting initial UI state based on URL parameters');
            
            // Get current URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const isHybrid = urlParams.has('flow') ? urlParams.get('flow').toLowerCase() === 'hybrid' : false;
            
            // Log what we found
            DEBUG && console.log('[ReferencesCore] URL parameter "flow":', urlParams.get('flow'));
            DEBUG && console.log('[ReferencesCore] isHybrid from URL:', isHybrid);
            
            // UI setup based on workflow type
            if (isHybrid) {
                DEBUG && console.log('[ReferencesCore] Configuring UI for hybrid workflow');
                // In hybrid workflow:
                // 1. Show the reference animation
                // 2. Hide the inactive message
                // 3. Enable generate button
                // 4. Disable next button
                // 5. Show all reference-related sections
                DEBUG && console.log('[ReferencesCore] For hybrid workflow - Enable generate, Disable next');
                
                this.ui.toggleReferenceAnimation(true);
                this.ui.toggleInactiveMessage(false);
                this.ui.setGenerateButtonState(true);
                this.ui.setNextButtonState(false);
                
                // Show the document list and visualization
                this.toggleReferenceVisualizationCard(true);
                this.toggleDocumentListContainer(true);
                
                // Update status badge to pending
                this.ui.updateStatusBadge('pending');
            } else {
                DEBUG && console.log('[ReferencesCore] Configuring UI for standard workflow');
                // For standard workflow:
                // 1. Show the inactive message (references not needed)
                // 2. Hide the reference animation
                // 3. Disable generate button
                // 4. Enable next button
                // 5. Hide all reference-related sections
                DEBUG && console.log('[ReferencesCore] For standard workflow - Disable generate, Enable next');
                
                this.ui.toggleReferenceAnimation(false);
                this.ui.toggleInactiveMessage(true);
                this.ui.setGenerateButtonState(false);
                this.ui.setNextButtonState(true);
                
                // Hide the document list and visualization
                this.toggleReferenceVisualizationCard(false);
                this.toggleDocumentListContainer(false);
                
                // Update status badge to completed since this step is skipped
                this.ui.updateStatusBadge('completed');
                
                // Update status to completed
                this.currentStatus = 'completed';
            }
            
            // Save workflow type to localStorage immediately
            ReferencesUtils.saveToWorkflowState({
                workflow: {
                    type: isHybrid ? 'hybrid' : 'standard',
                    ...this.workflowState?.workflow
                }
            });
        }
        
        /**
         * Toggle visibility of the Reference Visualization card
         * @param {boolean} show - Whether to show the card
         */
        toggleReferenceVisualizationCard(show) {
            DEBUG && console.log('[ReferencesCore] Toggling reference visualization card:', show ? 'VISIBLE' : 'HIDDEN');
            const card = document.querySelector('.reference-visualization');
            if (card) {
                card.style.display = show ? 'block' : 'none';
            }
        }
        
        /**
         * Toggle visibility of the Document List container
         * @param {boolean} show - Whether to show the container
         */
        toggleDocumentListContainer(show) {
            DEBUG && console.log('[ReferencesCore] Toggling document list container:', show ? 'VISIBLE' : 'HIDDEN');
            const container = document.querySelector('.document-list-container');
            if (container) {
                container.style.display = show ? 'block' : 'none';
            }
        }
        
        /**
         * Get the current status
         * @returns {string} Current status
         */
        getStatus() {
            return this.currentStatus;
        }
        
        /**
         * Set the current status
         * @param {string} status - New status
         */
        setStatus(status) {
            this.currentStatus = status;
        }
        
        /**
         * Get reference sheets from localStorage
         * @returns {Object} Reference sheet data grouped by document ID
         */
        getReferenceSheets() {
            // First check the cached reference sheets from initialization
            if (this.referenceSheets && Object.keys(this.referenceSheets).length > 0) {
                DEBUG && console.log('[ReferencesCore] Using cached reference sheets:', this.referenceSheets);
                return this.referenceSheets;
            }
            
            // If not cached, try to reprocess from localStorage
            const refsData = this.getLocalStorageItem('microfilmReferenceSheets');
            if (!refsData) {
                DEBUG && console.log('[ReferencesCore] No reference sheets found in localStorage');
                return {};
            }
            
            DEBUG && console.log('[ReferencesCore] Reprocessing reference sheets from localStorage');
            
            // Initialize result
            let result = {};
            
            // Process based on structure
            if (refsData.referenceSheets && typeof refsData.referenceSheets === 'object') {
                // Format is { projectId, referenceSheets: { doc1: [...], doc2: [...] } }
                DEBUG && console.log('[ReferencesCore] Using referenceSheets (camelCase) from localStorage');
                result = this.enrichReferenceSheets(refsData.referenceSheets, refsData);
            } else if (refsData.reference_sheets && typeof refsData.reference_sheets === 'object') {
                // Format is { project_id, reference_sheets: { doc1: [...], doc2: [...] } }
                DEBUG && console.log('[ReferencesCore] Using reference_sheets (snake_case) from localStorage');
                result = this.enrichReferenceSheets(refsData.reference_sheets, refsData);
            } else if (refsData.enhancedDetails && typeof refsData.enhancedDetails === 'object') {
                // Format is { enhancedDetails: { doc1: { ... } } }
                DEBUG && console.log('[ReferencesCore] Using enhancedDetails from localStorage');
                
                // Extract documents from enhancedDetails
                Object.keys(refsData.enhancedDetails).forEach(docKey => {
                    const docDetails = refsData.enhancedDetails[docKey];
                    if (docDetails.sheet_ids && docDetails.ranges) {
                        // Create reference sheet entries for this document
                        result[docKey] = docDetails.sheet_ids.map((id, index) => {
                            return {
                                id: id,
                                range: docDetails.ranges[index],
                                blip: docDetails.blips ? docDetails.blips[index] : null,
                                film_number: docDetails.film_numbers ? docDetails.film_numbers[index] : null,
                                human_readable_range: docDetails.human_readable_ranges ? docDetails.human_readable_ranges[index] : null
                            };
                        });
                    }
                });
            } else {
                // Look for document keys directly (fallback)
                DEBUG && console.log('[ReferencesCore] Looking for valid document keys in reference data');
                
                // Check each key to see if it looks like a document ID (avoid metadata fields)
                const docKeys = Object.keys(refsData).filter(key => {
                    // If the value is an array and not a top-level metadata property
                    return Array.isArray(refsData[key]) && 
                           ![
                               'projectId', 'project_id', 'status', 'timestamp', 
                               'sheetsCreated', 'sheets_created', 'reference_sheets', 
                               'referenceSheets', 'enhancedDetails', 'documents_details'
                           ].includes(key);
                });
                
                DEBUG && console.log('[ReferencesCore] Found document keys:', docKeys);
                
                // Extract document sheets
                docKeys.forEach(docKey => {
                    result[docKey] = refsData[docKey];
                });
            }
            
            DEBUG && console.log('[ReferencesCore] Processed reference sheets result:', result);
            
            // Cache the result for future calls
            this.referenceSheets = result;
            
            return result;
        }
        
        /**
         * Enriches reference sheets with detailed data from documents_details
         * @param {Object} sheetsByDocument - Basic reference sheets by document
         * @param {Object} fullData - The full reference sheets data
         * @returns {Object} Enriched reference sheets with blip data
         */
        enrichReferenceSheets(sheetsByDocument, fullData) {
            // Clone the sheets to avoid modifying the original
            const enrichedSheets = JSON.parse(JSON.stringify(sheetsByDocument));
            
            // Check if we have documents_details to enrich with
            if (fullData.documents_details) {
                DEBUG && console.log('[ReferencesCore] Enriching sheets with documents_details data');
                DEBUG && console.log('[ReferencesCore] documents_details:', fullData.documents_details);
                
                // Process each document
                Object.keys(enrichedSheets).forEach(docId => {
                    // Skip if no document details
                    if (!fullData.documents_details[docId]) {
                        DEBUG && console.log(`[ReferencesCore] No document details for ${docId}`);
                        return;
                    }
                    
                    const docDetails = fullData.documents_details[docId];
                    const sheets = enrichedSheets[docId];
                    
                    DEBUG && console.log(`[ReferencesCore] Enriching ${sheets.length} sheets for ${docId}`);
                    DEBUG && console.log(`[ReferencesCore] Document details:`, docDetails);
                    
                    // Map each sheet to an enriched version
                    enrichedSheets[docId] = sheets.map((sheet, sheetIdx) => {
                        // First try to find by sheet ID
                        let detailIndex = docDetails.sheet_ids ? 
                            docDetails.sheet_ids.findIndex(id => id === sheet.id) : -1;
                        
                        // If not found by ID, try to match by range
                        if (detailIndex === -1 && sheet.range && docDetails.ranges) {
                            DEBUG && console.log(`[ReferencesCore] Sheet ID ${sheet.id} not found, looking for range match`);
                            detailIndex = docDetails.ranges.findIndex(range => 
                                range[0] === sheet.range[0] && range[1] === sheet.range[1]);
                        }
                        
                        // If no match found, try to use index-based matching (fallback)
                        if (detailIndex === -1 && sheetIdx < (docDetails.sheet_ids?.length || 0)) {
                            DEBUG && console.log(`[ReferencesCore] No exact match found for sheet ${sheet.id}, using index ${sheetIdx}`);
                            detailIndex = sheetIdx;
                        }
                        
                        // If we found a matching sheet in details
                        if (detailIndex >= 0) {
                            const blipValue = docDetails.blips ? docDetails.blips[detailIndex] : null;
                            const filmNumber = docDetails.film_numbers ? docDetails.film_numbers[detailIndex] : null;
                            const humanRange = docDetails.human_readable_ranges ? docDetails.human_readable_ranges[detailIndex] : null;
                            
                            DEBUG && console.log(`[ReferencesCore] Found details for sheet ${sheet.id}: blip=${blipValue}, film=${filmNumber}`);
                            
                            return {
                                ...sheet,
                                blip: blipValue,
                                blip_35mm: blipValue, // Add for UI compatibility
                                film_number: filmNumber,
                                human_readable_range: humanRange
                            };
                        } else {
                            DEBUG && console.log(`[ReferencesCore] No matching details found for sheet ${sheet.id}`);
                        }
                        
                        return sheet;
                    });
                    
                    // Log the first enriched sheet to verify data
                    if (enrichedSheets[docId].length > 0) {
                        DEBUG && console.log(`[ReferencesCore] First enriched sheet for ${docId}:`, enrichedSheets[docId][0]);
                    }
                });
            } else {
                DEBUG && console.log('[ReferencesCore] No documents_details available for enrichment');
            }
            
            return enrichedSheets;
        }
        
        /**
         * Get document details from the enhanced response
         * @param {string} documentId - The document ID
         * @returns {Object} Document details or empty object if not available
         */
        getDocumentDetails(documentId) {
            const refsData = this.getLocalStorageItem('microfilmReferenceSheets');
            if (!refsData) {
                DEBUG && console.log(`[ReferencesCore] No reference data found for document ${documentId}`);
                return {};
            }
            
            // First check documents_details (old format)
            if (refsData.documents_details && refsData.documents_details[documentId]) {
                DEBUG && console.log(`[ReferencesCore] Found details for ${documentId} in documents_details`);
                return refsData.documents_details[documentId];
            }
            
            // Then check enhancedDetails (new format)
            if (refsData.enhancedDetails && refsData.enhancedDetails[documentId]) {
                DEBUG && console.log(`[ReferencesCore] Found details for ${documentId} in enhancedDetails`);
                return refsData.enhancedDetails[documentId];
            }
            
            DEBUG && console.log(`[ReferencesCore] No details found for ${documentId}`);
            return {};
        }
        
        /**
         * Display document information
         * @param {string} documentId - The document ID
         */
        displayDocumentInfo(documentId) {
            DEBUG && console.log(`[ReferencesCore] Displaying info for document ${documentId}`);
            
            // Get detailed information if available
            const docDetails = this.getDocumentDetails(documentId);
            
            DEBUG && console.log(`[ReferencesCore] Document details for ${documentId}:`, docDetails);
            
            // Update UI with document information
            if (this.ui && this.ui.updateDocumentMetadata && Object.keys(docDetails).length > 0) {
                // Extract relevant metadata from docDetails structure
                const metadata = {
                    sheetCount: docDetails.sheet_count || (docDetails.sheet_ids ? docDetails.sheet_ids.length : 0),
                    blips: docDetails.blips || [],
                    filmNumbers: docDetails.film_numbers || [],
                    humanRanges: docDetails.human_readable_ranges || [],
                    filePaths: docDetails.file_paths || []
                };
                
                DEBUG && console.log(`[ReferencesCore] Extracted metadata for ${documentId}:`, metadata);
                
                // Update UI
                this.ui.updateDocumentMetadata(documentId, metadata);
            } else {
                DEBUG && console.log(`[ReferencesCore] No metadata to update for ${documentId} or UI not available`);
            }
            
            // If events instance has a selectDocument method, call it
            if (this.events && typeof this.events.onSelectDocument === 'function') {
                DEBUG && console.log(`[ReferencesCore] Calling events.onSelectDocument for ${documentId}`);
                this.events.onSelectDocument(documentId);
            }
        }
        
        /**
         * Refreshes all data from the API - now only called manually, not on page load
         */
        refreshData() {
            DEBUG && console.log('[ReferencesCore] Manually refreshing data from API');
            
            // Fetch reference status
            this.api.getStatus()
                .then(statusData => {
                    // Update status variables
                    this.currentStatus = statusData.status;
                    
                    // Update UI based on status
                    this.ui.updateStatusMetrics({
                        totalDocuments: statusData.documents_with_references + (statusData.total_oversized_documents - statusData.documents_with_references),
                        oversizedDocuments: statusData.total_oversized_documents,
                        sheetsGenerated: statusData.reference_sheet_count,
                        status: this.currentStatus === 'completed' ? 'Completed' : 'Pending'
                    });
                    
                    // Determine if we need reference sheets based on both the API response
                    // and the URL flow parameter
                    const urlParams = new URLSearchParams(window.location.search);
                    const flowType = urlParams.has('flow') ? urlParams.get('flow').toLowerCase() : null;
                    
                    const hasOversized = statusData.has_oversized;
                    const isHybrid = (flowType === 'hybrid');
                    
                    DEBUG && console.log('[ReferencesCore] API Status Check:');
                    DEBUG && console.log('[ReferencesCore] - Flow type from URL:', flowType);
                    DEBUG && console.log('[ReferencesCore] - isHybrid from URL:', isHybrid);
                    DEBUG && console.log('[ReferencesCore] - API has_oversized:', hasOversized);
                    DEBUG && console.log('[ReferencesCore] - Current status:', this.currentStatus);
                    
                    // IMPORTANT: For standard workflow, always respect the URL parameter over API response
                    if (!isHybrid) {
                        DEBUG && console.log('[ReferencesCore] STANDARD workflow - respecting URL parameter over API response');
                        
                        // Hide animation, show inactive message
                        this.ui.toggleReferenceAnimation(false);
                        this.ui.toggleInactiveMessage(true);
                        
                        // Disable generate button, enable next button
                        DEBUG && console.log('[ReferencesCore] - Setting generate button: DISABLED (forced by standard workflow)');
                        DEBUG && console.log('[ReferencesCore] - Setting next button: ENABLED (forced by standard workflow)');
                        
                        this.ui.setGenerateButtonState(false);
                        this.ui.setNextButtonState(true);
                        
                        // Hide the document list and visualization
                        this.toggleReferenceVisualizationCard(false);
                        this.toggleDocumentListContainer(false);
                        
                        // Update status to completed
                        this.currentStatus = 'completed';
                        this.ui.updateStatusBadge('completed');
                        return null;
                    }
                    
                    // For hybrid workflow, use API data to determine UI
                    if (isHybrid) {
                        // HYBRID WORKFLOW: 
                        // In hybrid workflow, always show reference sheets functionality
                        DEBUG && console.log('[ReferencesCore] Applying HYBRID workflow UI settings');
                        
                        // Show animation, hide inactive message
                        this.ui.toggleReferenceAnimation(true);
                        this.ui.toggleInactiveMessage(false);
                        
                        // Show the document list and visualization
                        this.toggleReferenceVisualizationCard(true);
                        this.toggleDocumentListContainer(true);
                        
                        // Only enable generate button if not already completed
                        const generateEnabled = (this.currentStatus !== 'completed');
                        const nextEnabled = (this.currentStatus === 'completed');
                        
                        DEBUG && console.log('[ReferencesCore] - Setting generate button:', generateEnabled ? 'ENABLED' : 'DISABLED');
                        DEBUG && console.log('[ReferencesCore] - Setting next button:', nextEnabled ? 'ENABLED' : 'DISABLED');
                        
                        this.ui.setGenerateButtonState(generateEnabled);
                        this.ui.setNextButtonState(nextEnabled);
                        
                        // Update status badge
                        this.ui.updateStatusBadge(this.currentStatus);
                    }
                    
                    // Save workflow state including workflow type
                    ReferencesUtils.saveToWorkflowState({
                        referenceSheets: {
                            status: this.currentStatus,
                            hasOversized: statusData.has_oversized,
                            completed: this.currentStatus === 'completed'
                        },
                        workflow: {
                            type: isHybrid ? 'hybrid' : 'standard',
                            ...this.workflowState?.workflow
                        }
                    });
                    
                    // Update data output
                    this.ui.updateDataOutput({
                        ...statusData,
                        workflow_type: isHybrid ? 'hybrid' : 'standard'
                    });
                    
                    // If we have reference sheets, fetch them
                    if (statusData.reference_sheet_count > 0) {
                        return this.api.getReferenceSheets();
                    }
                    
                    return null;
                })
                .then(sheetsData => {
                    if (sheetsData && sheetsData.status === 'success') {
                        // Store reference sheets
                        this.referenceSheets = sheetsData.reference_sheets || {};
                        
                        // Update document list with references
                        const documents = Object.keys(this.referenceSheets).map(docId => {
                            return {
                                doc_id: docId,
                                has_reference_sheets: this.referenceSheets[docId].length > 0,
                                oversized_ranges: this.referenceSheets[docId],
                                page_count: 0  // We don't have this info from the API
                            };
                        });
                        
                        // Use a bound function for the view document callback
                        const viewDocumentCallback = (docId) => {
                            // Assuming events instance has been attached to the core
                            if (this.events) {
                                this.events.onViewDocument(docId);
                            }
                        };
                        
                        this.ui.renderDocumentList(documents, viewDocumentCallback);
                        
                        // Do NOT automatically select the first document - keep animation visible by default
                    }
                })
                .catch(error => {
                    console.error('Error refreshing data:', error);
                    this.ui.showNotification('Failed to refresh reference data: ' + error.message, 'error');
                });
        }
        
        /**
         * Attach events manager for callbacks
         * @param {Object} events - Events manager instance
         */
        attachEvents(events) {
            this.events = events;
        }
    }

    // Public API
    return {
        ReferencesCore: ReferencesCoreClass
    };
})(); 