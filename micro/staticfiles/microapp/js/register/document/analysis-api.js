/**
 * Analyze documents with API integration
 */
function analyzeDocumentsWithAPI() {
    console.log('[Analysis API] Starting document analysis for path:', analysisState.documentsPath);
    
    // Create API request to start analysis
    fetch('/api/documents/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            projectId: analysisState.projectId,
            documentsPath: analysisState.documentsPath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Get the task ID from the response
        const taskId = data.taskId;
        
        // Start polling for status
        pollAnalysisStatus(taskId);
    })
    .catch(error => {
        console.error('[Analysis API] Error starting document analysis:', error);
        
        // Update status
        updateStatusBadge('error', 'Analysis Error');
        analysisState.analysisStatusText.textContent = `Error: ${error.message}`;
        
        // Enable reset button
        if (analysisState.resetAnalysisBtn) {
            analysisState.resetAnalysisBtn.disabled = false;
        }
    });
}

/**
 * Poll for analysis task status
 * @param {string} taskId - The ID of the analysis task
 */
function pollAnalysisStatus(taskId) {
    const pollInterval = setInterval(() => {
        fetch(`/api/documents/analysis-status?taskId=${taskId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update UI with current status
            updateAnalysisUI(
                data.documentCount || 0,
                data.totalPages || 0,
                data.oversizedPages || 0,
                true  // Enable animation
            );
            
            // Update current document
            if (data.currentFile) {
                updateCurrentDocument(data.currentFile);
            }
            
            // Update document list if results are available
            if (data.results && data.results.length > 0) {
                // Use the document data from results array
                updateDocumentList(data.results);
                
                // Keep track of how many documents we've processed
                console.log(`[Analysis API] Processing ${data.results.length} documents, total count: ${data.documentCount}`);
            }
            
            // Handle completion or error
            if (data.status === 'completed') {
                clearInterval(pollInterval);
                
                // Save analysis data
                saveAnalysisData(data);
                
                // Complete the analysis
                completeAnalysis();
            } else if (data.status === 'error') {
                clearInterval(pollInterval);
                
                // Show error
                updateStatusBadge('error', 'Analysis Error');
                analysisState.analysisStatusText.textContent = `Error: ${data.errors.join(', ')}`;
                
                // Enable reset button
                if (analysisState.resetAnalysisBtn) {
                    analysisState.resetAnalysisBtn.disabled = false;
                }
            }
        })
        .catch(error => {
            console.error('[Analysis API] Error polling analysis status:', error);
            // Don't clear the interval, just try again
        });
    }, 1000); // Poll every second
}

/**
 * Save analysis data to state and localStorage
 */
function saveAnalysisData(data) {
    // Update analysis state
    // Don't overwrite the DOM element reference, store results separately
    analysisState.documents = data.results || [];
    console.log('[Analysis API] Storing document results in analysisState.documents:', analysisState.documents.length);
    
    analysisState.totalDocuments = data.documentCount || 0;
    analysisState.totalPages = data.totalPages || 0;
    analysisState.totalOversized = data.oversizedPages || 0;
    analysisState.documentsWithOversized = data.documentsWithOversized || 0;
    
    // Save to localStorage
    saveStepData('analysis', {
        projectId: analysisState.projectId,
        documentsPath: analysisState.documentsPath,
        totalDocuments: analysisState.totalDocuments,
        totalPages: analysisState.totalPages,
        totalOversized: analysisState.totalOversized,
        documents: analysisState.documents, // Use the documents property
        hasOversized: analysisState.totalOversized > 0
    });
}

/**
 * Complete the analysis process
 */
function completeAnalysis() {
    // Update status badge and text
    updateStatusBadge('complete', 'Analysis Complete');
    
    // Log the final counts for debugging
    console.log('[Analysis API] Analysis complete with counts:', {
        documents: analysisState.totalDocuments,
        pages: analysisState.totalPages,
        oversized: analysisState.totalOversized
    });
    
    // Update status text with correct document counts
    analysisState.analysisStatusText.textContent = `Analyzed ${analysisState.totalDocuments} documents with ${analysisState.totalPages} pages (${analysisState.totalOversized} oversized)`;
    
    // Enable reset button
    if (analysisState.resetAnalysisBtn) {
        analysisState.resetAnalysisBtn.disabled = false;
    }
    
    // Enable continue button
    if (analysisState.toStep3Btn) {
        analysisState.toStep3Btn.disabled = false;
        analysisState.toStep3Btn.classList.remove('disabled');
    }
    
    // Update workflow recommendation based on oversized pages
    const recommendedWorkflow = analysisState.totalOversized > 0 ? 'hybrid' : 'standard';
    analysisState.recommendedWorkflow = recommendedWorkflow;
    
    // Call workflow recommendation function if available
    if (typeof updateWorkflowRecommendation === 'function') {
        updateWorkflowRecommendation(recommendedWorkflow);
    }
    
    // If we have a handleAnalysisComplete function, call it
    if (typeof handleAnalysisComplete === 'function') {
        // Ensure we're passing the correct data
        console.log('[Analysis API] Calling handleAnalysisComplete with correct data');
        handleAnalysisComplete({
            documentCount: analysisState.totalDocuments,
            totalPages: analysisState.totalPages,
            oversizedPages: analysisState.totalOversized,
            documentsWithOversized: analysisState.documentsWithOversized,
            hasOversized: analysisState.totalOversized > 0,
            results: analysisState.documents,
            // Add a timestamp for debugging
            completedAt: new Date().toISOString()
        });
    } else {
        // If we have oversized documents, calculate reference sheets
        if (analysisState.totalOversized > 0 && typeof calculateReferenceSheets === 'function') {
            calculateReferenceSheets();
        }
    }
}

// Export functions
window.analyzeDocumentsWithAPI = analyzeDocumentsWithAPI; 