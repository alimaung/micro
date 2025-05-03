/**
 * Document Analysis Core Module
 * 
 * Core functionality for the document analysis process:
 * - Initializes state and UI elements
 * - Sets up event listeners
 * - Coordinates the analysis process
 */

// Global state for document analysis (exported to be accessible by other modules)
const analysisState = {
    projectId: null,
    projectInfo: null,
    documentsPath: null,
    analysisStatus: 'idle', // idle, processing, completed, error
    documentList: [],
    totalDocuments: 0,
    totalPages: 0,
    totalOversized: 0,
    documentsWithOversized: 0,
    recommendedWorkflow: null, // 'standard' or 'hybrid'
    progress: 0,
    error: null
};

/**
 * Initialize Document Analysis module
 */
async function initDocumentAnalysis() {
    console.log('[Analysis] Initializing document analysis module');
    
    // Log URL parameters at startup
    const urlParams = new URLSearchParams(window.location.search);
    console.log('[Analysis] URL parameters at initialization:', {
        id: urlParams.get('id'),
        mode: urlParams.get('mode'),
        flow: urlParams.get('flow'),
        step: urlParams.get('step')
    });
    
    // Log global microfilmUrlParams if available
    if (window.microfilmUrlParams) {
        console.log('[Analysis] Global microfilmUrlParams at initialization:', window.microfilmUrlParams);
    }
    
    // Initialize UI elements
    initUIElements();
    
    // Retrieve project information from URL parameters and localStorage
    await getProjectInformation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Debug logging
    setTimeout(debugStateAndParameters, 500);
}

/**
 * Initialize UI element references
 */
function initUIElements() {
    // Buttons
    analysisState.startAnalysisBtn = document.getElementById('start-analysis');
    analysisState.resetAnalysisBtn = document.getElementById('reset-analysis');
    analysisState.toStep3Btn = document.getElementById('to-step-3');
    analysisState.prevStepBtn = document.querySelector('.nav-button.prev-step');
    
    // Status elements
    analysisState.statusBadge = document.querySelector('#step-2 .status-badge');
    analysisState.analysisStatusText = document.getElementById('analysis-status');
    analysisState.progressBar = document.querySelector('#step-2 .progress-bar-fill');
    analysisState.progressPercentage = document.querySelector('#step-2 .progress-percentage');
    
    // Counters
    analysisState.documentCounter = document.querySelector('.document-counter:nth-child(1) .counter-value');
    analysisState.pageCounter = document.querySelector('.document-counter:nth-child(2) .counter-value');
    analysisState.oversizedCounter = document.querySelector('.document-counter:nth-child(3) .counter-value');
    
    // Document list
    analysisState.documentList = document.getElementById('document-list');
    console.log('[Analysis] documentList initialized as DOM element:', analysisState.documentList);
    
    // Workflow recommendation elements
    analysisState.standardWorkflow = document.querySelector('.workflow-branch.standard');
    analysisState.hybridWorkflow = document.querySelector('.workflow-branch.oversized');
    analysisState.standardBadge = analysisState.standardWorkflow.querySelector('.recommendation-badge');
    
    // Project info display elements
    analysisState.projectIdDisplay = document.getElementById('project-id-display');
    analysisState.archiveIdDisplay = document.getElementById('archive-id-display');
    analysisState.locationDisplay = document.getElementById('location-display');
    analysisState.documentTypeDisplay = document.getElementById('document-type-display');
    analysisState.projectSourcePath = document.getElementById('project-source-path');
    
    // Initialize workflow recommendation to empty/pending state
    if (typeof initWorkflowRecommendation === 'function') {
        initWorkflowRecommendation();
    }
    
    // Initialize reference UI elements
    initReferenceUI();
}

/**
 * Set up event listeners for UI interactions
 */
function setupEventListeners() {
    // Start analysis button
    if (analysisState.startAnalysisBtn) {
        analysisState.startAnalysisBtn.addEventListener('click', handleStartAnalysis);
    }
    
    // Reset analysis button
    if (analysisState.resetAnalysisBtn) {
        analysisState.resetAnalysisBtn.addEventListener('click', handleResetAnalysis);
    }
    
    // Navigation buttons - using the new classes
    document.querySelectorAll('.nav-button.prev-step').forEach(button => {
        button.addEventListener('click', handlePreviousStep);
    });
    
    document.querySelectorAll('.nav-button.next-step').forEach(button => {
        button.addEventListener('click', handleNextStep);
    });
}

/**
 * Handle navigation to previous step
 */
function handlePreviousStep(e) {
    e.preventDefault();
    
    // Get URL parameters
    const urlParamsFromSearch = new URLSearchParams(window.location.search);
    console.log('[Analysis] Direct URL parameters for previous step:', {
        id: urlParamsFromSearch.get('id'),
        mode: urlParamsFromSearch.get('mode'),
        flow: urlParamsFromSearch.get('flow')
    });
    
    const urlParams = window.microfilmUrlParams || 
                     (() => {
                         const params = new URLSearchParams(window.location.search);
                         return {
                             projectId: params.get('id'),
                             mode: params.get('mode') || 'auto',
                             flow: params.get('flow') || 'standard'
                         };
                     })();
    
    // Get workflow state from localStorage to ensure consistency
    const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
    
    // Get the most accurate mode value (URL > localStorage > default)
    const processingMode = urlParamsFromSearch.get('mode') || workflowState.workflowMode || 'auto';
    
    // Get flow type (URL > localStorage > default)
    const flowType = urlParamsFromSearch.get('flow') || workflowState.workflowType || 'standard';
    
    // Construct URL with parameters
    let url = '/register/project/?step=1';
    if (urlParams.projectId) {
        url += '&id=' + encodeURIComponent(urlParams.projectId);
    }
    
    // Add the processing mode parameter
    url += '&mode=' + encodeURIComponent(processingMode);
    
    // Add the flow parameter
    url += '&flow=' + encodeURIComponent(flowType);
    
    console.log('[Analysis] Navigating to previous step:', url);
    window.location.href = url;
}

/**
 * Handle navigation to next step
 */
function handleNextStep(e) {
    e.preventDefault();
    
    // Get URL parameters with more detailed logging
    const urlParamsFromSearch = new URLSearchParams(window.location.search);
    console.log('[Analysis] Direct URL parameters:', {
        id: urlParamsFromSearch.get('id'),
        mode: urlParamsFromSearch.get('mode'),
        flow: urlParamsFromSearch.get('flow'),
        step: urlParamsFromSearch.get('step')
    });
    
    const urlParams = window.microfilmUrlParams || 
                     (() => {
                         const params = new URLSearchParams(window.location.search);
                         return {
                             projectId: params.get('id'),
                             mode: params.get('mode') || 'auto',
                             flow: params.get('flow') || 'standard'
                         };
                     })();
    
    console.log('[Analysis] Global URL parameters:', urlParams);
    
    // Get workflow state from localStorage 
    const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
    console.log('[Analysis] workflowState from localStorage:', workflowState);
    
    // Get the processing mode (auto/semi/manual) from the correct source
    // Priority: 1. URL parameter, 2. localStorage, 3. fallback to 'auto'
    const processingMode = urlParamsFromSearch.get('mode') || workflowState.workflowMode || 'auto';
    
    // Get the workflow flow type (standard/hybrid) from analysis recommendation
    const flowType = analysisState.recommendedWorkflow || 'standard';
    
    console.log('[Analysis] Navigation parameters determined:', {
        processingMode: processingMode,
        flowType: flowType
    });
    
    // Construct URL with parameters
    let url = '/register/allocation/?step=3';
    if (urlParams.projectId) {
        url += '&id=' + encodeURIComponent(urlParams.projectId);
    }
    
    // Add the processing mode parameter
    url += '&mode=' + encodeURIComponent(processingMode);
    
    // Add the flow type as a separate parameter
    url += '&flow=' + encodeURIComponent(flowType);
    
    console.log('[Analysis] Navigating to next step:', url);
    console.log('[Analysis] Using processing mode:', processingMode, 'and flow type:', flowType);
    
    window.location.href = url;
}

/**
 * Handle Start Analysis button click
 */
function handleStartAnalysis() {
    if (analysisState.analysisStatus === 'processing') {
        console.log('[Analysis] Analysis already in progress');
        return;
    }
    
    if (!analysisState.documentsPath) {
        showNotification('No document path available for analysis', 'error');
        return;
    }
    
    // Disable buttons and update UI
    analysisState.startAnalysisBtn.disabled = true;
    analysisState.resetAnalysisBtn.disabled = true;
    analysisState.toStep3Btn.disabled = true;
    
    // Clear document list
    clearDocumentList();
    
    // Update status
    updateStatusBadge('in-progress', 'Analysis in Progress');
    analysisState.analysisStatusText.textContent = 'Starting document analysis...';
    
    // Reset progress indicators
    updateAnalysisUI(0, 0, 0, false);
    
    // Set analysis status to processing
    analysisState.analysisStatus = 'processing';
    
    // Start the analysis process
    startDocumentAnalysis();
}

/**
 * Handle Reset Analysis button click
 */
function handleResetAnalysis() {
    console.log('[Analysis] Resetting analysis data');
    
    // Reset all analysis data
    updateAnalysisUI(0, 0, 0, false);
    
    // Reset status
    updateStatusBadge('pending', 'Ready to Analyze');
    analysisState.analysisStatusText.textContent = 'Waiting to start...';
    
    // Clear document list
    clearDocumentList();
    
    // Reset workflow recommendation
    resetWorkflowRecommendation();
    
    // Hide current document display
    const currentDocElement = document.querySelector('.current-document');
    if (currentDocElement) {
        currentDocElement.style.display = 'none';
    }
    
    // Reset reference counters
    if (analysisState.referenceCounter) {
        analysisState.referenceCounter.textContent = '0';
    }
    if (analysisState.totalPagesCounter) {
        analysisState.totalPagesCounter.textContent = '0';
    }
    
    // Hide the oversized documents container
    if (analysisState.oversizedDocumentsContainer) {
        analysisState.oversizedDocumentsContainer.style.display = 'none';
    }
    
    // Clear the oversized documents list
    const oversizedDocsList = document.getElementById('oversized-documents-list');
    if (oversizedDocsList) {
        oversizedDocsList.innerHTML = '<div class="empty-list-message">No oversized documents found</div>';
    }
    
    // Enable/disable buttons
    analysisState.startAnalysisBtn.disabled = false;
    analysisState.toStep3Btn.disabled = true;
    
    // Add disabled styling to navigation buttons
    if (analysisState.toStep3Btn) {
        analysisState.toStep3Btn.classList.add('disabled');
    }
    
    // Reset analysis state
    analysisState.analysisStatus = 'idle';
    analysisState.totalDocuments = 0;
    analysisState.totalPages = 0;
    analysisState.totalOversized = 0;
    analysisState.documentsWithOversized = 0;
    analysisState.totalReferences = 0;
    analysisState.totalPagesWithRefs = 0;
    analysisState.recommendedWorkflow = null;
    analysisState.progress = 0;
    analysisState.documents = [];
    analysisState.hasOversized = false;
    analysisState.showReferenceTable = false;
    
    // Clear saved analysis data from localStorage by setting it to null
    try {
        // First update the main workflow state
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        if (workflowState.analysisResults) {
            console.log('[Analysis] Clearing analysis results from workflowState');
            delete workflowState.analysisResults;
            localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        }
        
        // Then use the saveStepData function to ensure it's properly cleared
        console.log('[Analysis] Clearing analysis data from localStorage');
        saveStepData('analysis', null);
    } catch (error) {
        console.error('[Analysis] Error clearing analysis data from localStorage:', error);
    }
    
    console.log('[Analysis] Analysis data reset complete');
}

/**
 * Debug helper function to log state and parameters
 */
function debugStateAndParameters() {
    console.log('[Analysis Debug] Current state:', {
        projectId: analysisState.projectId,
        documentsPath: analysisState.documentsPath,
        status: analysisState.analysisStatus
    });
    
    // Log URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    console.log('[Analysis Debug] URL parameters:', {
        id: urlParams.get('id'),
        mode: urlParams.get('mode'),
        step: urlParams.get('step')
    });
    
    // Log localStorage state
    try {
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
        console.log('[Analysis Debug] localStorage state:', {
            workflowState,
            projectState
        });
    } catch (e) {
        console.error('[Analysis Debug] Error parsing localStorage:', e);
    }
}

/**
 * Start the document analysis process
 */
function startDocumentAnalysis() {
    console.log('[Analysis] Starting document analysis for path:', analysisState.documentsPath);
    
    try {
        // Check if the API function is available
        if (typeof analyzeDocumentsWithAPI !== 'function') {
            throw new Error('API function analyzeDocumentsWithAPI is not available');
        }
        
        // Call the API implementation
        analyzeDocumentsWithAPI();
    } catch (error) {
        console.error('[Analysis] Error starting document analysis:', error);
        
        // Show error in UI
        updateStatusBadge('error', 'Analysis Error');
        analysisState.analysisStatusText.textContent = `Error: ${error.message}`;
        
        // Enable reset button
        if (analysisState.resetAnalysisBtn) {
            analysisState.resetAnalysisBtn.disabled = false;
        }
    }
}

/**
 * Call API to calculate reference sheets for oversized documents
 */
async function calculateReferenceSheets() {
    console.log('[Analysis] Calculating reference sheets for project:', analysisState.projectId);
    
    try {
        // Show loading state
        analysisState.analysisStatusText.textContent = 'Calculating reference sheets...';
        
        // Make API call to calculate references
        const response = await fetch('/api/documents/calculate-references', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                projectId: analysisState.projectId
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Log the reference calculation results
        console.log('[Analysis] Reference calculation results:', data);
        
        // Update state with reference information
        analysisState.totalReferences = data.totalReferences || 0;
        analysisState.totalPagesWithRefs = data.totalPagesWithRefs || analysisState.totalPages;
        
        // If we have reference sheets, display them
        if (data.hasReferences) {
            displayReferenceInformation(data);
        }
        
        // Update status text
        analysisState.analysisStatusText.textContent = `Analysis complete. ${data.totalReferences} reference sheets needed.`;
        
        // Update localStorage with the reference information
        updateStoredAnalysisWithReferences(data);
        
        return data;
    } catch (error) {
        console.error('[Analysis] Error calculating reference sheets:', error);
        analysisState.analysisStatusText.textContent = `Error calculating references: ${error.message}`;
        showNotification('Error calculating reference sheets', 'warning');
        
        // Fallback to client-side calculation if API call fails
        try {
            console.log('[Analysis] Falling back to client-side reference calculation');
            
            // Check if we have the calculation function available
            if (typeof calculateAllReferences === 'function') {
                // Use client-side calculation
                const refData = calculateAllReferences(analysisState.documents);
                
                // Update state with reference information
                analysisState.totalReferences = refData.totalReferences || 0;
                analysisState.totalPagesWithRefs = refData.totalPagesWithRefs || analysisState.totalPages;
                
                // Display the reference information
                if (refData.hasReferences) {
                    displayReferenceInformation(refData);
                    
                    // Update localStorage with the reference information
                    updateStoredAnalysisWithReferences(refData);
                    
                    analysisState.analysisStatusText.textContent = 
                        `Analysis complete. ${refData.totalReferences} reference sheets calculated locally.`;
                    
                    return refData;
                }
            }
        } catch (fallbackError) {
            console.error('[Analysis] Error in fallback reference calculation:', fallbackError);
        }
        
        return null;
    }
}

/**
 * Update stored analysis results with reference information
 */
function updateStoredAnalysisWithReferences(referenceData) {
    try {
        console.log('[Analysis] Updating stored analysis with reference data:', referenceData);
        
        // Get current workflow state
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        
        if (!workflowState.analysisResults) {
            console.warn('[Analysis] No analysis results found in workflow state');
            return;
        }
        
        // Update analysis results with reference information
        workflowState.analysisResults.totalReferences = referenceData.totalReferences || 0;
        workflowState.analysisResults.totalPagesWithRefs = referenceData.totalPagesWithRefs || 0;
        
        // Update documents with reference information if available
        if (referenceData.documents && referenceData.documents.length > 0) {
            // Create a map for quick lookup of existing documents
            const docMap = {};
            if (workflowState.analysisResults.documents) {
                workflowState.analysisResults.documents.forEach(doc => {
                    if (doc && doc.name) {
                        docMap[doc.name] = doc;
                    }
                });
            }
            
            // Update documents with reference information
            referenceData.documents.forEach(refDoc => {
                if (refDoc && refDoc.name && docMap[refDoc.name]) {
                    // Update existing document with reference information
                    const existingDoc = docMap[refDoc.name];
                    existingDoc.referencePages = refDoc.referencePages || [];
                    existingDoc.totalReferences = refDoc.totalReferences || 0;
                    existingDoc.adjusted_ranges = refDoc.adjusted_ranges || [];
                }
            });
        }
        
        // Ensure the showReferenceTable flag is set
        workflowState.analysisResults.showReferenceTable = true;
        
        // Save back to localStorage
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        
        // Also save in the step-specific data
        saveStepData('analysis', workflowState.analysisResults);
        
        console.log('[Analysis] Successfully updated stored analysis with reference data');
    } catch (error) {
        console.error('[Analysis] Error updating stored analysis with reference data:', error);
    }
}

/**
 * Display reference sheet information in the UI
 */
function displayReferenceInformation(referenceData) {
    console.log('[Analysis] Displaying reference information:', referenceData);
    
    if (!referenceData) {
        console.error('[Analysis] No reference data provided to displayReferenceInformation');
        return;
    }
    
    // Make sure we have the oversized documents container
    if (!analysisState.oversizedDocumentsContainer) {
        analysisState.oversizedDocumentsContainer = document.getElementById('oversized-documents-container');
    }
    
    // If container doesn't exist yet, it may not be in the DOM
    if (!analysisState.oversizedDocumentsContainer) {
        console.warn('[Analysis] Oversized documents container not found in DOM');
        return;
    }
    
    // Make the container visible - always show it for oversized documents
    analysisState.oversizedDocumentsContainer.style.display = 'block';
    console.log('[Analysis] Made reference table container visible');
    
    // Get the table body
    const tableBody = document.getElementById('oversized-documents-list');
    if (!tableBody) {
        console.warn('[Analysis] Oversized documents list not found in DOM');
        return;
    }
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Make sure documents array exists
    if (!referenceData.documents || !Array.isArray(referenceData.documents)) {
        console.warn('[Analysis] No documents array in reference data');
        tableBody.innerHTML = '<tr><td colspan="4" class="no-data">No oversized documents found</td></tr>';
        return;
    }
    
    // Add rows for each document with oversized pages
    let docsWithOversized = [];
    try {
        docsWithOversized = referenceData.documents.filter(doc => doc && doc.hasOversized);
        console.log('[Analysis] Documents with oversized pages:', docsWithOversized.length);
    } catch (error) {
        console.error('[Analysis] Error filtering documents with oversized pages:', error);
    }
    
    if (!docsWithOversized || docsWithOversized.length === 0) {
        // No oversized documents found
        tableBody.innerHTML = '<tr><td colspan="4" class="no-data">No oversized documents found</td></tr>';
        return;
    }
    
    // Sort documents by name
    try {
        // Natural sorting function for document names
        const naturalSort = (a, b) => {
            // Get document names to compare
            const aName = a.name || a.fileName || '';
            const bName = b.name || b.fileName || '';
            
            // Extract numbers from document names if present
            const aNum = /^(\d+)/.exec(aName);
            const bNum = /^(\d+)/.exec(bName);
            
            // If both names start with numbers, compare them numerically
            if (aNum && bNum) {
                return parseInt(aNum[1], 10) - parseInt(bNum[1], 10);
            }
            
            // Otherwise, fall back to standard string comparison
            return aName.localeCompare(bName);
        };
        
        // Sort using natural sort
        docsWithOversized.sort(naturalSort);
    } catch (error) {
        console.warn('[Analysis] Error sorting documents:', error);
    }
    
    // Add each document to the table
    let totalReferencesFound = 0;
    
    docsWithOversized.forEach(doc => {
        try {
            console.log('[Analysis] Adding document to oversized table:', doc.name, 
                        'Oversized pages:', doc.oversizedPages, 
                        'References:', doc.totalReferences, 
                        'Adjusted Ranges:', doc.adjusted_ranges);
            
            const tr = document.createElement('tr');
            
            // Document name column
            const nameCell = document.createElement('td');
            nameCell.className = 'doc-name';
            nameCell.textContent = doc.name || 'Unknown';
            tr.appendChild(nameCell);
            
            // Oversized pages column
            const oversizedCell = document.createElement('td');
            oversizedCell.className = 'doc-oversized';
            oversizedCell.textContent = doc.oversizedPages && Array.isArray(doc.oversizedPages) 
                                      ? doc.oversizedPages.join(', ') 
                                      : 'N/A';
            tr.appendChild(oversizedCell);
            
            // Reference sheets column
            const referencesCell = document.createElement('td');
            referencesCell.className = 'doc-references';
            const refCount = doc.totalReferences || 0;
            referencesCell.textContent = refCount;
            totalReferencesFound += refCount;
            tr.appendChild(referencesCell);
            
            // Adjusted ranges column (replacing reference positions)
            const rangesCell = document.createElement('td');
            rangesCell.className = 'doc-ref-positions';
            
            // Format adjusted ranges in a readable way - handle both formats safely
            if (doc.adjusted_ranges && Array.isArray(doc.adjusted_ranges) && doc.adjusted_ranges.length > 0) {
                try {
                    const rangeTexts = doc.adjusted_ranges.map((range, index) => {
                        // Skip invalid ranges
                        if (!range) return `R${index+1}: N/A`;
                        
                        try {
                            // Handle both object format and array format
                            let original, adjusted, refPage;
                            
                            if (range.original || range.adjusted) {
                                // Object format
                                original = range.original || [0, 0];
                                adjusted = range.adjusted || [0, 0];
                                refPage = range.reference_page || 0;
                            } else if (Array.isArray(range) && range.length >= 2) {
                                // Array format
                                original = range[0] || [0, 0];
                                adjusted = range[1] || [0, 0];
                                refPage = range[2] || 0;
                            } else {
                                return `R${index+1}: Invalid format`;
                            }
                            
                            // Format: "Ref #1: p9 → pp(10-12)"
                            if (Array.isArray(original) && original[0] === original[1]) {
                                // Single page range
                                return `R${index+1}: p${original[0]} → p${Array.isArray(adjusted) ? adjusted[0] : adjusted}`;
                            } else {
                                // Multi-page range
                                if (Array.isArray(adjusted)) {
                                    return `R${index+1}: p${original[0]}-${original[1]} → pp(${adjusted[0]}-${adjusted[1]})`;
                                } else {
                                    return `R${index+1}: p${original[0]} → p${adjusted}`;
                                }
                            }
                        } catch (e) {
                            console.error('[Analysis] Error formatting range:', e, range);
                            return `R${index+1}: Error`;
                        }
                    });
                    
                    rangesCell.textContent = rangeTexts.join('; ');
                } catch (e) {
                    console.error('[Analysis] Error formatting adjusted ranges:', e);
                    rangesCell.textContent = 'Error formatting ranges';
                }
            } else if (doc.referencePages && Array.isArray(doc.referencePages) && doc.referencePages.length > 0) {
                // Fallback to original reference positions if adjusted ranges aren't available
                rangesCell.textContent = doc.referencePages.join(', ');
            } else {
                rangesCell.textContent = 'N/A';
            }
            
            tr.appendChild(rangesCell);
            
            // Add row to table
            tableBody.appendChild(tr);
        } catch (error) {
            console.error('[Analysis] Error adding document to table:', error);
        }
    });
    
    // Update the reference sheets counter - ensure it's always populated
    if (analysisState.referenceCounter) {
        const totalRefs = referenceData.totalReferences || totalReferencesFound || 0;
        analysisState.referenceCounter.textContent = totalRefs;
        analysisState.totalReferences = totalRefs;
        console.log('[Analysis] Updated reference counter with:', totalRefs);
    }
    
    // Update the total pages with references counter - ensure it's always populated
    if (analysisState.totalPagesCounter) {
        const totalPagesWithRefs = referenceData.totalPagesWithRefs || 
                                (analysisState.totalPages + (referenceData.totalReferences || totalReferencesFound || 0));
        analysisState.totalPagesCounter.textContent = totalPagesWithRefs;
        analysisState.totalPagesWithRefs = totalPagesWithRefs;
        console.log('[Analysis] Updated total pages counter with:', totalPagesWithRefs);
    }
    
    console.log('[Analysis] Reference information display completed');
}

/**
 * Handle completion of document analysis
 */
function handleAnalysisComplete(analysisResult) {
    // Log full analysis results for debugging
    console.log('[Analysis] Complete analysis results:', analysisResult);
    
    // Update UI with analysis results
    updateStatusBadge('complete', 'Analysis Complete');
    
    // Enable buttons
    if (analysisState.resetAnalysisBtn) {
        analysisState.resetAnalysisBtn.disabled = false;
    }
    if (analysisState.toStep3Btn) {
        analysisState.toStep3Btn.disabled = false;
        analysisState.toStep3Btn.classList.remove('disabled');
    }
    
    // Update state with analysis results
    analysisState.totalDocuments = analysisResult.documentCount || 0;
    analysisState.totalPages = analysisResult.totalPages || 0;
    analysisState.totalOversized = analysisResult.oversizedPages || 0;
    analysisState.documentsWithOversized = analysisResult.documentsWithOversized || 0;
    
    // Update counters - FIX: Apply the correct data to each counter
    if (analysisState.documentCounter) {
        // Display totalDocuments (documentCount) in the Documents counter
        analysisState.documentCounter.textContent = analysisState.totalDocuments;
    }
    if (analysisState.pageCounter) {
        // Display totalPages in the Pages counter
        analysisState.pageCounter.textContent = analysisState.totalPages;
    }
    if (analysisState.oversizedCounter) {
        // Display totalOversized in the Oversized counter
        analysisState.oversizedCounter.textContent = analysisState.totalOversized;
    }
    
    // Determine recommended workflow based on oversized pages
    analysisState.recommendedWorkflow = analysisState.totalOversized > 0 ? 'hybrid' : 'standard';
    
    // Update workflow recommendation
    updateWorkflowRecommendation(analysisState.recommendedWorkflow);
    
    // Store results in localStorage for next step
    saveAnalysisResults(analysisResult);
    
    // If we have oversized documents, calculate reference sheets
    if (analysisState.totalOversized > 0) {
        calculateReferenceSheets();
    }
}

/**
 * Save analysis results to localStorage
 */
function saveAnalysisResults(analysisResult) {
    try {
        console.log('[Analysis] Saving analysis results to localStorage:', analysisResult);
        
        // Get current workflow state
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        console.log('[Analysis] Current workflow state before update:', workflowState);
        
        // Preserve original processing mode
        const originalMode = workflowState.workflowMode || 'auto';
        
        // Ensure we have the complete documents with all necessary properties
        let documentsToSave = [];
        if (analysisResult.results && analysisResult.results.length > 0) {
            documentsToSave = analysisResult.results;
        } else if (analysisState.documents && analysisState.documents.length > 0) {
            documentsToSave = analysisState.documents;
        } else if (analysisResult.documents && analysisResult.documents.length > 0) {
            documentsToSave = analysisResult.documents;
        }
        
        // Determine if we should show the reference table
        const hasOversized = analysisResult.hasOversized || analysisResult.oversizedPages > 0 || false;
        const showReferenceTable = hasOversized;
        
        // Update with analysis results
        workflowState.analysisResults = {
            status: 'completed',
            documentCount: analysisResult.documentCount || 0,
            totalDocuments: analysisResult.documentCount || 0,
            pageCount: analysisResult.totalPages || 0,
            totalPages: analysisResult.totalPages || 0,
            oversizedCount: analysisResult.oversizedPages || 0,
            totalOversized: analysisResult.oversizedPages || 0,
            documentsWithOversized: analysisResult.documentsWithOversized || 0,
            recommendedWorkflow: analysisState.recommendedWorkflow,
            hasOversized: hasOversized,
            showReferenceTable: showReferenceTable,
            totalReferences: analysisState.totalReferences || 0,
            totalPagesWithRefs: analysisState.totalPagesWithRefs || 0,
            documents: documentsToSave,
            results: documentsToSave, // Include both properties for compatibility
            timestamp: new Date().toISOString()
        };
        
        // Store the workflow type recommendation (standard/hybrid) 
        // but definitely preserve the original processing mode (auto/semi/manual)
        workflowState.workflowType = analysisState.recommendedWorkflow;
        workflowState.workflowMode = originalMode;
        
        console.log('[Analysis] Updated workflow data:', {
            processingMode: workflowState.workflowMode, // This remains unchanged (auto/semi/manual)
            workflowType: workflowState.workflowType    // This is the recommendation (standard/hybrid)
        });
        
        // Save back to localStorage
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        
        // Also save in the step-specific data - include all properties to ensure compatibility
        saveStepData('analysis', workflowState.analysisResults);
        
        console.log('[Analysis] Analysis results saved successfully');
    } catch (error) {
        console.error('[Analysis] Error saving analysis results to localStorage:', error);
    }
}

/**
 * Initialize UI elements for reference sheets
 */
function initReferenceUI() {
    // References counter element
    analysisState.referenceCounter = document.querySelector('.document-counter:nth-child(4) .counter-value');
    analysisState.totalPagesCounter = document.querySelector('.document-counter:nth-child(5) .counter-value');
    
    // Oversized documents container
    analysisState.oversizedDocumentsContainer = document.getElementById('oversized-documents-container');
    
    // Initially hide the oversized documents container
    if (analysisState.oversizedDocumentsContainer) {
        analysisState.oversizedDocumentsContainer.style.display = 'none';
    }
    
    // Initialize showReferenceTable flag (will be updated when data is loaded)
    analysisState.showReferenceTable = false;
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', async function() {
    await initDocumentAnalysis();
});

// Export the analysisState and essential functions for use in other modules
window.analysisState = analysisState;
window.initDocumentAnalysis = initDocumentAnalysis;
window.handleStartAnalysis = handleStartAnalysis;
window.handleResetAnalysis = handleResetAnalysis;
window.updateStoredAnalysisWithReferences = updateStoredAnalysisWithReferences; 