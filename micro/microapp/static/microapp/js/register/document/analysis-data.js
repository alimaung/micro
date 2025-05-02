/**
 * Document Analysis Data Module
 * 
 * Handles data operations:
 * - LocalStorage interaction
 * - API communication
 * - Project data retrieval
 * - Data persistence
 */

/**
 * Retrieve project information from URL parameters and localStorage
 */
async function getProjectInformation() {
    try {
        // Use the consistent project ID function
        analysisState.projectId = getConsistentProjectId();
        
        if (!analysisState.projectId) {
            // If we still don't have a project ID, show an error
            updateStatusBadge('error', 'No project ID found');
            analysisState.analysisStatusText.textContent = 'Error: No project ID found. Please start from the project registration page.';
            analysisState.startAnalysisBtn.disabled = true;
            return;
        }
        
        // Update workflow state with project ID
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        console.log('[Analysis] Current workflow state:', workflowState);
        
        workflowState.projectId = analysisState.projectId;
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        
        // Get project data from localStorage first
        let projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
        console.log('[Analysis] Project state:', projectState);
        
        // Check if we need to fetch project data
        if (!projectState || !projectState.projectId || projectState.projectId !== analysisState.projectId) {
            console.warn('[Analysis] Project data not found in localStorage or ID mismatch');
            
            // Try to fetch project data
            projectState = await fetchProjectDataFromServer(analysisState.projectId);
        }
        
        if (projectState && projectState.projectId) {
            // Use the project data
            analysisState.projectInfo = projectState.projectInfo || {};
            
            // Use PDF path from the project info as the documents path
            if (projectState.projectInfo && projectState.projectInfo.pdfPath) {
                analysisState.documentsPath = projectState.projectInfo.pdfPath;
                console.log('[Analysis] Using PDF path from project data:', analysisState.documentsPath);
            } 
            // Fallback to source data path if PDF path is not available
            else if (projectState.sourceData && projectState.sourceData.path) {
                analysisState.documentsPath = projectState.sourceData.path;
                console.log('[Analysis] Using source path from project data (PDF path not found):', analysisState.documentsPath);
            } else {
                // Fallback to placeholder path
                analysisState.documentsPath = '/document/source/path/' + analysisState.projectId;
                console.warn('[Analysis] No path found, using placeholder path:', analysisState.documentsPath);
            }
            
            // Display project information
            updateProjectInfo(projectState);
            
            // Check for existing workflow state and analysis results
            const existingWorkflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
            console.log('[Analysis] Checking for existing analysis data in workflow state:', existingWorkflowState);
            
            // Explicitly check for analysis data
            if (existingWorkflowState.analysisResults) {
                console.log('[Analysis] Found existing analysis results in workflow state');
                // Update our state with this analysis data
                analysisState.analysisResults = existingWorkflowState.analysisResults;
                analysisState.recommendedWorkflow = existingWorkflowState.workflowMode || existingWorkflowState.analysisResults.recommendedWorkflow;
            }
            
            // Try to load saved analysis data
            loadAnalysisData();
            
            // Update status if we have valid project data
            if (analysisState.projectId && analysisState.documentsPath) {
                if (analysisState.analysisStatus !== 'completed') {
                    updateStatusBadge('pending', 'Ready to Analyze');
                    analysisState.analysisStatusText.textContent = 'Ready to analyze documents. Click "Start Analysis" to begin.';
                    analysisState.startAnalysisBtn.disabled = false;
                }
            }
        } else {
            // No valid project data found
            updateStatusBadge('error', 'Project data not found');
            analysisState.analysisStatusText.textContent = 'Error: Could not load project data.';
            analysisState.startAnalysisBtn.disabled = true;
        }
    } catch (error) {
        console.error('[Analysis] Error retrieving project information:', error);
        updateStatusBadge('error', 'Error loading project');
        analysisState.analysisStatusText.textContent = `Error: ${error.message}`;
        analysisState.startAnalysisBtn.disabled = true;
    }
}

/**
 * Load previously saved analysis data from localStorage
 */
function loadAnalysisData() {
    const savedData = loadStepData('analysis');
    
    console.log('[Analysis] Loading analysis data from localStorage:', savedData);
    
    // Check for valid saved data in various formats
    // Either it has a status of 'completed' OR it has totalDocuments/documentCount > 0
    if (savedData && (
        savedData.status === 'completed' || 
        savedData.documentCount > 0 || 
        savedData.totalDocuments > 0
    )) {
        console.log('[Analysis] Found valid saved analysis data with values');
        console.log('[Analysis] Document count:', savedData.documentCount || savedData.totalDocuments);
        console.log('[Analysis] Page count:', savedData.pageCount || savedData.totalPages);
        console.log('[Analysis] Oversized count:', savedData.oversizedCount || savedData.totalOversized);
        console.log('[Analysis] Has oversized:', savedData.hasOversized);
        console.log('[Analysis] Total references:', savedData.totalReferences);
        console.log('[Analysis] Total pages with refs:', savedData.totalPagesWithRefs);
        console.log('[Analysis] Show reference table:', savedData.showReferenceTable);
        
        // Check for documents array
        if (savedData.documents && savedData.documents.length > 0) {
            console.log('[Analysis] Documents found in savedData.documents:', savedData.documents.length);
            console.log('[Analysis] First document sample:', savedData.documents[0]);
        } else if (savedData.results && savedData.results.length > 0) {
            console.log('[Analysis] Documents found in savedData.results:', savedData.results.length);
            console.log('[Analysis] First document sample:', savedData.results[0]);
        }
        
        // Update status
        updateStatusBadge('completed', 'Analysis Complete');
        
        // Get the document count and page count, with fallbacks
        const documentCount = savedData.documentCount || savedData.totalDocuments || 0;
        const pageCount = savedData.pageCount || savedData.totalPages || 0;
        const oversizedCount = savedData.oversizedCount || savedData.totalOversized || 0;
        const totalReferences = savedData.totalReferences || 0;
        const totalPagesWithRefs = savedData.totalPagesWithRefs || 0;
        
        analysisState.analysisStatusText.textContent = 
            `Analysis complete. Found ${documentCount} documents with ${pageCount} pages.`;
        
        console.log('[Analysis] Updating UI with counts:', { documentCount, pageCount, oversizedCount });
        
        // Update UI with saved values - ensuring correct counters get correct values
        updateAnalysisUI(documentCount, pageCount, oversizedCount, true);
        
        // Store values in state
        analysisState.totalDocuments = documentCount;
        analysisState.totalPages = pageCount;
        analysisState.totalOversized = oversizedCount;
        analysisState.totalReferences = totalReferences;
        analysisState.totalPagesWithRefs = totalPagesWithRefs;
        analysisState.progress = 100; // Ensure progress is set to 100%
        
        // Handle document list population
        if (savedData.documents && savedData.documents.length > 0) {
            console.log('[Analysis] Updating document list from savedData.documents');
            analysisState.documents = savedData.documents;
            updateDocumentList(savedData.documents);
        } else if (savedData.results && savedData.results.length > 0) {
            console.log('[Analysis] Updating document list from savedData.results');
            analysisState.documents = savedData.results;
            updateDocumentList(savedData.results);
        }
        
        // Update workflow recommendation based on oversized documents
        const hasOversized = (oversizedCount > 0 || (savedData.hasOversized === true));
        analysisState.hasOversized = hasOversized;
        
        console.log('[Analysis] Has oversized documents:', hasOversized);
        
        // Check if we should show reference information
        const showReferenceTable = savedData.showReferenceTable || hasOversized;
        analysisState.showReferenceTable = showReferenceTable;
        
        if (hasOversized) {
            // Set recommendation to hybrid workflow
            analysisState.recommendedWorkflow = 'hybrid';
            if (typeof updateWorkflowRecommendation === 'function') {
                console.log('[Analysis] Setting workflow recommendation to hybrid');
                updateWorkflowRecommendation('hybrid');
            }
            
            // If there's reference data or we should show the reference table, display it
            if (showReferenceTable || savedData.totalReferences || savedData.documents) {
                // Check if we should call the reference calculation function
                const hasReferenceData = savedData.documents && 
                                        savedData.documents.some(doc => 
                                            doc.hasOversized && 
                                            (doc.referencePages || doc.adjusted_ranges)
                                        );
                
                console.log('[Analysis] Has reference data:', hasReferenceData);
                
                // If we have reference data, display it
                if (hasReferenceData || showReferenceTable) {
                    console.log('[Analysis] Displaying reference information from saved data');
                    
                    // Check if we need to calculate reference information
                    if (!hasReferenceData && typeof calculateAllReferences === 'function' && savedData.documents) {
                        console.log('[Analysis] Calculating missing reference data client-side');
                        try {
                            // Calculate reference information client-side
                            const referenceData = calculateAllReferences(savedData.documents);
                            
                            if (referenceData && referenceData.hasReferences) {
                                console.log('[Analysis] Successfully calculated reference data:', referenceData);
                                
                                // Update the saved data with reference information
                                savedData.totalReferences = referenceData.totalReferences;
                                savedData.totalPagesWithRefs = referenceData.totalPagesWithRefs;
                                savedData.documents = referenceData.documents;
                                
                                // Update state
                                analysisState.totalReferences = referenceData.totalReferences;
                                analysisState.totalPagesWithRefs = referenceData.totalPagesWithRefs;
                                
                                // Save updated data to localStorage
                                if (typeof updateStoredAnalysisWithReferences === 'function') {
                                    updateStoredAnalysisWithReferences(referenceData);
                                }
                            }
                        } catch (error) {
                            console.error('[Analysis] Error calculating reference data client-side:', error);
                        }
                    }
                    
                    // Display existing reference data
                    displayReferenceInformation({
                        totalReferences: savedData.totalReferences || oversizedCount,
                        totalPagesWithRefs: savedData.totalPagesWithRefs || (pageCount + oversizedCount),
                        documents: savedData.documents,
                        hasReferences: true
                    });
                    
                    // Update reference counters directly if they exist
                    if (analysisState.referenceCounter) {
                        analysisState.referenceCounter.textContent = savedData.totalReferences || 0;
                        console.log('[Analysis] Updated reference counter with:', savedData.totalReferences || 0);
                    }
                    
                    if (analysisState.totalPagesCounter) {
                        analysisState.totalPagesCounter.textContent = savedData.totalPagesWithRefs || 0;
                        console.log('[Analysis] Updated total pages counter with:', savedData.totalPagesWithRefs || 0);
                    }
                }
            }
        } else {
            // Set recommendation to standard workflow
            analysisState.recommendedWorkflow = 'standard';
            if (typeof updateWorkflowRecommendation === 'function') {
                console.log('[Analysis] Setting workflow recommendation to standard');
                updateWorkflowRecommendation('standard');
            }
        }
        
        // Enable navigation to next step
        analysisState.toStep3Btn.disabled = false;
        analysisState.resetAnalysisBtn.disabled = false;
        analysisState.startAnalysisBtn.disabled = true;
        
        // Set analysis status to completed
        analysisState.analysisStatus = 'completed';
        console.log('[Analysis] State restored from saved data, status set to completed');
    } else {
        console.log('[Analysis] No valid saved analysis data found or data is incomplete');
        // For incomplete or missing analysis data, initialize to pending state
        if (typeof initWorkflowRecommendation === 'function') {
            initWorkflowRecommendation();
        }
        
        // Reset counters to zero
        updateAnalysisUI(0, 0, 0, false);
        
        // Clear document list if it exists
        if (typeof clearDocumentList === 'function') {
            clearDocumentList();
        }
        
        // Update status
        updateStatusBadge('pending', 'Ready to Analyze');
        analysisState.analysisStatusText.textContent = 'Ready to analyze documents. Click "Start Analysis" to begin.';
        
        // Enable start analysis button if we have a valid documents path
        if (analysisState.documentsPath) {
            analysisState.startAnalysisBtn.disabled = false;
        }
    }
}

/**
 * Load step data from localStorage 
 */
function loadStepData(stepKey) {
    try {
        // Log raw localStorage contents for debugging
        const rawState = localStorage.getItem('microfilmWorkflowState');
        console.log('[Analysis] Raw localStorage workflowState:', rawState);
        
        const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        console.log('[Analysis] Parsed localStorage state:', state);
        
        // First check if the data exists directly in the state
        if (state[stepKey]) {
            console.log(`[Analysis] Found ${stepKey} data directly in state`);
            return state[stepKey];
        }
        
        // Then check if it's in the analysisResults property
        if (stepKey === 'analysis' && state.analysisResults) {
            console.log('[Analysis] Found data in analysisResults property');
            return state.analysisResults;
        }
        
        console.log(`[Analysis] No ${stepKey} data found in localStorage`);
        return null;
    } catch (error) {
        console.error('[Analysis] Error loading step data:', error);
        return null;
    }
}

/**
 * Save step data to localStorage
 */
function saveStepData(stepKey, data) {
    console.log(`[Analysis] Saving ${stepKey} data to localStorage:`, data);
    
    try {
        const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        
        // Save to specific step key
        state[stepKey] = data;
        
        // If it's analysis data, also save to analysisResults for consistency
        if (stepKey === 'analysis' && data) {
            console.log('[Analysis] Also updating analysisResults for consistency');
            state.analysisResults = data;
        }
        
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
        console.log(`[Analysis] Successfully saved ${stepKey} data`);
    } catch (error) {
        console.error('[Analysis] Error saving step data:', error);
    }
}

/**
 * Check if a global saveStepData function exists that's different from this one
 * Used by other modules to call the main saveStepData implementation
 */
function callGlobalSaveStepData(stepKey, data) {
    // Get the parent window's function if available
    if (window.parent && 
        window.parent.saveStepData && 
        typeof window.parent.saveStepData === 'function' &&
        window.parent.saveStepData !== window.saveStepData) {
        
        window.parent.saveStepData(stepKey, data);
        return true;
    }
    return false;
}

/**
 * Save analysis data to localStorage
 */
function saveAnalysisData(documentCount, pageCount, oversizedCount, documentsWithOversized, status, documents) {
    console.log('[Analysis] Saving analysis data:', { documentCount, pageCount, oversizedCount, status });
    
    // Structure the analysis data
    const analysisData = {
        documentCount: documentCount,
        pageCount: pageCount,
        oversizedCount: oversizedCount,
        documentsWithOversized: documentsWithOversized,
        status: status,
        documentTypes: {
            pdf: Math.floor(documentCount * 0.7),
            tiff: Math.floor(documentCount * 0.2),
            jpeg: Math.floor(documentCount * 0.1)
        },
        sizeDistribution: {
            standard: documentCount - oversizedCount,
            oversized: oversizedCount
        },
        completedAt: new Date().toISOString(),
        documents: documents || []
    };
    
    // Save to local storage - directly access the function to avoid recursion
    try {
        const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        state['analysis'] = analysisData;
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
    } catch (error) {
        console.error('[Analysis] Error saving analysis data:', error);
    }
}

/**
 * Analyze documents using the backend API
 */
function analyzeDocumentsWithAPI() {
    console.log('[Analysis] Starting document analysis with real API');
    
    // Show API call status in UI
    analysisState.analysisStatusText.textContent = 'Connecting to server...';
    
    // Build the request body
    const requestBody = {
        projectId: analysisState.projectId,
        documentsPath: analysisState.documentsPath
    };
    
    // Make the API request to the analyze endpoint
    fetch('/api/documents/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned error ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        // Check if we have a taskId in the response
        if (data.taskId) {
            console.log('[Analysis] Analysis task started with ID:', data.taskId);
            analysisState.analysisStatusText.textContent = 'Analysis started on server. Monitoring progress...';
            
            // Start polling for progress
            startProgressPolling(data.taskId);
        } else {
            // No taskId in response
            handleAnalysisError('Server did not return a task ID');
        }
    })
    .catch(error => {
        handleAnalysisError(`Error starting analysis: ${error.message}`);
    });
}

/**
 * Poll for analysis progress
 * @param {string} taskId - The ID of the task to monitor
 */
function startProgressPolling(taskId) {
    const pollInterval = 1000; // 1 second
    const maxPolls = 180; // Maximum 3 minutes of polling
    let pollCount = 0;
    
    console.log('[Analysis] Starting progress polling for task:', taskId);
    
    // Create the poll function
    const pollForProgress = function() {
        // Request analysis status from server
        fetch(`/api/documents/analysis-status?taskId=${taskId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            pollCount++;
            console.log(`[Analysis] Poll ${pollCount}/${maxPolls}: Status=${data.status}, Progress=${data.progress}%`);
            
            // Process based on status
            if (data.status === 'completed') {
                // Analysis is complete - update UI and finish
                console.log('[Analysis] Task completed successfully');
                
                // For our API, the results may be in data directly
                const results = {
                    totalDocuments: data.documentCount || 0,
                    totalPages: data.totalPages || 0,
                    totalOversized: data.oversizedPages || 0,
                    documentsWithOversized: data.documentsWithOversized || 0,
                    documents: data.results || []
                };
                
                handleAnalysisCompleted(results);
            } 
            else if (data.status === 'in-progress' || data.status === 'processing') {
                // Update progress UI
                updateAnalysisProgress(
                    data.progress || 0, 
                    data.currentFile || 'Processing documents...',
                    data.message || `Processing documents (${data.progress || 0}%)`
                );
                
                // Continue polling if we haven't reached the limit
                if (pollCount < maxPolls) {
                    setTimeout(pollForProgress, pollInterval);
                } else {
                    handleAnalysisError('Analysis timed out after 3 minutes');
                }
            }
            else if (data.status === 'error') {
                // Server reported an error
                handleAnalysisError(data.error || data.message || 'Server reported an error');
            }
            else if (data.status === 'pending') {
                // Task is queued but not started yet
                analysisState.analysisStatusText.textContent = 'Analysis queued, waiting for server...';
                
                // Continue polling
                if (pollCount < maxPolls) {
                    setTimeout(pollForProgress, pollInterval);
                } else {
                    handleAnalysisError('Analysis timed out waiting for server');
                }
            }
            else {
                // Unknown status
                console.warn(`[Analysis] Unknown status received: ${data.status}`);
                
                // Continue polling
                if (pollCount < maxPolls) {
                    setTimeout(pollForProgress, pollInterval);
                } else {
                    handleAnalysisError('Analysis timed out due to unknown status');
                }
            }
        })
        .catch(error => {
            console.error('[Analysis] Error polling for progress:', error);
            
            // Try again unless we've reached the maximum
            if (pollCount < maxPolls) {
                setTimeout(pollForProgress, pollInterval);
            } else {
                handleAnalysisError(`Error checking analysis progress: ${error.message}`);
            }
        });
    };
    
    // Start polling after a short delay
    setTimeout(pollForProgress, pollInterval);
}

/**
 * Handle completed analysis
 */
function handleAnalysisCompleted(results) {
    if (!results) {
        handleAnalysisError('No results returned from analysis');
        return;
    }
    
    console.log('[Analysis] Analysis completed with results:', results);
    
    // Extract key values from results
    const documentCount = results.totalDocuments || results.documentCount || 0;
    const pageCount = results.totalPages || results.pageCount || 0;
    const oversizedCount = results.totalOversized || results.oversizedCount || 0;
    const documentsWithOversized = results.documentsWithOversized || 0;
    
    // Update state with values
    analysisState.totalDocuments = documentCount;
    analysisState.totalPages = pageCount;
    analysisState.totalOversized = oversizedCount;
    analysisState.documentsWithOversized = documentsWithOversized;
    analysisState.hasOversized = oversizedCount > 0;
    analysisState.documents = results.documents || [];
    
    // FIX: Update UI with results - ensuring correct counters get correct values
    updateAnalysisUI(documentCount, pageCount, oversizedCount, true);
    
    // Update document list
    if (results.documents && results.documents.length > 0) {
        updateDocumentList(results.documents);
    }
    
    // Update status
    updateStatusBadge('completed', 'Analysis Complete');
    analysisState.analysisStatusText.textContent = 
        `Analysis complete. Found ${documentCount} documents with ${pageCount} pages.`;
    
    // Update workflow recommendation based on oversized documents
    if (oversizedCount > 0) {
        setWorkflowRecommendation('hybrid');
    } else {
        setWorkflowRecommendation('standard');
    }
    
    // Enable navigation
    analysisState.toStep3Btn.disabled = false;
    analysisState.resetAnalysisBtn.disabled = false;
    
    // Remove disabled styling from navigation buttons
    if (analysisState.toStep3Btn) {
        analysisState.toStep3Btn.classList.remove('disabled');
    }
    
    // Set analysis status
    analysisState.analysisStatus = 'completed';
    
    // Calculate and add default reference counts if oversized documents exist
    let totalReferences = 0;
    let totalPagesWithRefs = pageCount;
    
    if (oversizedCount > 0 && results.documents) {
        // Count reference pages based on oversized pages
        // Each unique oversized page requires one reference sheet
        const docsWithOversized = results.documents.filter(doc => doc && doc.hasOversized);
        
        docsWithOversized.forEach(doc => {
            if (doc.oversizedPages && Array.isArray(doc.oversizedPages)) {
                // Very simple estimation - one reference page per oversized page
                // This will be replaced with more accurate data after proper calculation
                const refCount = doc.totalReferences || doc.oversizedPages.length || 0;
                totalReferences += refCount;
            }
        });
        
        // Add reference sheets to total page count
        totalPagesWithRefs = pageCount + totalReferences;
        
        // Update state with reference information
        analysisState.totalReferences = totalReferences;
        analysisState.totalPagesWithRefs = totalPagesWithRefs;
    }
    
    // Save the analysis results to localStorage
    saveStepData('analysis', {
        status: 'completed',
        documentCount: documentCount,
        pageCount: pageCount,
        oversizedCount: oversizedCount,
        totalReferences: totalReferences,
        totalPagesWithRefs: totalPagesWithRefs,
        hasOversized: oversizedCount > 0,
        showReferenceTable: oversizedCount > 0,
        documents: results.documents || [],
        timestamp: new Date().toISOString()
    });
}

/**
 * Handle analysis errors
 */
function handleAnalysisError(errorMessage) {
    console.error('[Analysis] Error:', errorMessage);
    
    // Update UI to show error
    updateStatusBadge('error', 'Analysis Error');
    analysisState.analysisStatusText.textContent = `Error: ${errorMessage}`;
    
    // Enable reset button
    analysisState.resetAnalysisBtn.disabled = false;
    
    // Set analysis status
    analysisState.analysisStatus = 'error';
    analysisState.error = errorMessage;
    
    // Show notification
    showNotification(`Analysis error: ${errorMessage}`, 'error');
}

/**
 * Helper function to get CSRF token for API requests
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

/**
 * Attempt to fetch project data from the server
 * @param {string} projectId - The project ID to fetch
 * @returns {Promise<Object|null>} The project data or null if not found
 */
async function fetchProjectDataFromServer(projectId) {
    try {
        console.log('[Analysis] Fetching project data from server for ID:', projectId);
        
        // First check if the data is already in localStorage but with a different ID
        // This handles the case where the data exists but the ID doesn't match
        const existingProjectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
        
        if (existingProjectState && existingProjectState.projectId) {
            console.log('[Analysis] Found existing project data in localStorage with ID:', existingProjectState.projectId);
            
            // Just update the project ID to match what's in the URL
            existingProjectState.projectId = projectId;
            localStorage.setItem('microfilmProjectState', JSON.stringify(existingProjectState));
            
            console.log('[Analysis] Using existing project data with updated ID:', projectId);
            return existingProjectState;
        }
        
        // Use the real API to fetch project data
        const response = await fetch(`/api/projects/${projectId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        if (!response.ok) {
            throw new Error(`Server returned error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Create a project state object from the API response
            const projectState = {
                projectId: projectId,
                projectInfo: {
                    archiveId: data.project.archive_id || '',
                    location: data.project.location || '',
                    documentType: data.project.doc_type || '',
                    pdfPath: data.project.pdf_path || data.project.a1_fullroll_path || '', // Add PDF path from API
                    comlistPath: data.project.comlist_path || data.project.comlist_file || ''
                },
                sourceData: {
                    path: data.project.project_path || '',
                    folderName: data.project.project_folder_name || ''
                },
                outputDir: data.project.output_dir || ''
            };
            
            // If PDF path is not provided directly, try to construct it from project path
            if (!projectState.projectInfo.pdfPath && data.project.project_path) {
                // Check if there's an A1_FullRoll_NoTemp subfolder (common pattern in the application)
                projectState.projectInfo.pdfPath = `${data.project.project_path}\\A1_FullRoll_NoTemp`;
                console.log('[Analysis] Constructed PDF path from project path:', projectState.projectInfo.pdfPath);
            }
            
            // Save to localStorage
            localStorage.setItem('microfilmProjectState', JSON.stringify(projectState));
            
            console.log('[Analysis] Project data fetched successfully from server');
            return projectState;
        } else {
            console.error('[Analysis] API error:', data.message);
            throw new Error(data.message || 'Failed to retrieve project data');
        }
    } catch (error) {
        console.error('[Analysis] Error fetching project data from server:', error);
        
        // Try to get project data from sessionStorage as last resort
        try {
            const sessionData = sessionStorage.getItem('projectState');
            if (sessionData) {
                const projectData = JSON.parse(sessionData);
                console.log('[Analysis] Found project data in sessionStorage:', projectData);
                
                // Create a proper project state structure from session data
                const projectState = {
                    projectId: projectId,
                    projectInfo: {
                        archiveId: projectData.archiveId || '',
                        location: projectData.location || '',
                        documentType: projectData.documentType || '',
                        pdfPath: projectData.pdfPath || '' // Add PDF path
                    },
                    sourceData: {
                        path: projectData.sourcePath || '',
                        folderName: projectData.sourcePath ? projectData.sourcePath.split('\\').pop() : ''
                    },
                    destinationPath: projectData.destinationPath || ''
                };
                
                // If PDF path is not provided, try to use sourcePath with A1_FullRoll_NoTemp
                if (!projectState.projectInfo.pdfPath && projectData.sourcePath) {
                    projectState.projectInfo.pdfPath = `${projectData.sourcePath}\\A1_FullRoll_NoTemp`;
                    console.log('[Analysis] Constructed PDF path from source path:', projectState.projectInfo.pdfPath);
                }
                
                // Save to localStorage
                localStorage.setItem('microfilmProjectState', JSON.stringify(projectState));
                
                console.log('[Analysis] Using project data from sessionStorage');
                return projectState;
            }
        } catch (e) {
            console.error('[Analysis] Error reading from sessionStorage:', e);
        }
        
        // Rethrow the original error if we couldn't recover
        throw error;
    }
}

/**
 * Get consistent project ID from various sources
 * This ensures we always have a valid project ID when available
 * @returns {string|null} The project ID or null if not found
 */
function getConsistentProjectId() {
    let projectId = null;
    
    // Try to get project ID from URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    projectId = urlParams.get('id');
    
    if (projectId) {
        console.log('[Analysis] Found project ID in URL parameters:', projectId);
        return projectId;
    }
    
    // Try to get from global variable
    if (window.microfilmUrlParams && window.microfilmUrlParams.projectId) {
        projectId = window.microfilmUrlParams.projectId;
        console.log('[Analysis] Found project ID in global variable:', projectId);
        return projectId;
    }
    
    // Try to get from workflow state in localStorage
    try {
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        if (workflowState.projectId) {
            projectId = workflowState.projectId;
            console.log('[Analysis] Found project ID in workflow state:', projectId);
            return projectId;
        }
    } catch (e) {
        console.error('[Analysis] Error parsing workflow state:', e);
    }
    
    // Try to get from project state in localStorage
    try {
        const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
        if (projectState.projectId) {
            projectId = projectState.projectId;
            console.log('[Analysis] Found project ID in project state:', projectId);
            return projectId;
        }
    } catch (e) {
        console.error('[Analysis] Error parsing project state:', e);
    }
    
    // No project ID found
    console.error('[Analysis] No project ID found in any source');
    return null;
}

/**
 * Calculate reference sheets for oversized documents using the API
 */
function calculateReferencesWithAPI() {
    console.log('[Analysis] Calculating reference sheets for oversized documents');
    
    // Only proceed if analysis is completed and has oversized pages
    if (analysisState.analysisStatus !== 'completed') {
        console.warn('[Analysis] Cannot calculate references: Analysis not completed');
        return;
    }
    
    if (!analysisState.hasOversized) {
        console.log('[Analysis] No oversized documents found, skipping reference calculation');
        return;
    }
    
    // Show status in UI
    analysisState.analysisStatusText.textContent = 'Calculating reference sheets...';
    
    // Build request body
    const requestBody = {
        projectId: analysisState.projectId
    };
    
    // Make the API request
    fetch('/api/documents/calculate-references', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned error ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            console.log('[Analysis] Reference sheets calculated successfully:', data);
            
            // Update the UI with reference information
            if (data.hasReferences) {
                // Update total pages count to include references
                analysisState.totalPagesWithRefs = data.totalPagesWithRefs;
                
                // Update document list with reference information
                if (data.documents && data.documents.length > 0) {
                    updateDocumentList(data.documents);
                }
                
                // Update status message
                analysisState.analysisStatusText.textContent = 
                    `Analysis complete. Found ${analysisState.totalDocuments} documents with ` +
                    `${analysisState.totalPages} pages and ${data.totalReferences} reference sheets.`;
                
                // Set workflow recommendation to hybrid
                setWorkflowRecommendation('hybrid');
            } else {
                // No references needed
                analysisState.analysisStatusText.textContent = 
                    `Analysis complete. Found ${analysisState.totalDocuments} documents with ` +
                    `${analysisState.totalPages} pages. No reference sheets needed.`;
                
                // Set workflow recommendation to standard
                setWorkflowRecommendation('standard');
            }
            
            // Save the updated analysis data
            saveAnalysisData(
                analysisState.totalDocuments,
                analysisState.totalPages,
                analysisState.totalOversized,
                analysisState.documentsWithOversized,
                'completed',
                data.documents || analysisState.documents
            );
            
            // Show notification
            showNotification('Reference sheets calculated successfully', 'success');
        } else {
            console.warn('[Analysis] Reference calculation did not return success status:', data);
        }
    })
    .catch(error => {
        console.error('[Analysis] Error calculating reference sheets:', error);
        showNotification(`Error calculating reference sheets: ${error.message}`, 'warning');
        
        // Continue anyway but with a warning
        analysisState.analysisStatusText.textContent += ' (Reference sheet calculation failed)';
    });
}

/**
 * Check if a global loadStepData function exists that's different from this one
 * Used by other modules to call the main loadStepData implementation
 */
function callGlobalLoadStepData(stepKey) {
    // Get the parent window's function if available
    if (window.parent && 
        window.parent.loadStepData && 
        typeof window.parent.loadStepData === 'function' &&
        window.parent.loadStepData !== window.loadStepData) {
        
        return window.parent.loadStepData(stepKey);
    }
    return null;
}

// Export functions for use in other modules
window.getProjectInformation = getProjectInformation;
window.loadAnalysisData = loadAnalysisData;
window.loadStepData = loadStepData;
window.callGlobalLoadStepData = callGlobalLoadStepData;
window.saveStepData = saveStepData;
window.callGlobalSaveStepData = callGlobalSaveStepData;
window.saveAnalysisData = saveAnalysisData;
window.analyzeDocumentsWithAPI = analyzeDocumentsWithAPI;
window.handleAnalysisCompleted = handleAnalysisCompleted;
window.handleAnalysisError = handleAnalysisError;
window.getCsrfToken = getCsrfToken;
window.fetchProjectDataFromServer = fetchProjectDataFromServer;
window.getConsistentProjectId = getConsistentProjectId;
window.calculateReferencesWithAPI = calculateReferencesWithAPI; 