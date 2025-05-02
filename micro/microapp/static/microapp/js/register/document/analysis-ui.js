/**
 * Document Analysis UI Module
 * 
 * Handles all UI-related functionality:
 * - Updating UI elements
 * - Status badges
 * - Animations
 * - Modal interactions
 */

/**
 * Update Analysis UI elements with the current stats
 * @param {number} documentCount - Number of documents
 * @param {number} pageCount - Number of pages
 * @param {number} oversizedCount - Number of oversized pages
 * @param {boolean} animated - Whether to animate the counters
 */
function updateAnalysisUI(documentCount, pageCount, oversizedCount, animated = false) {
    console.log('[Analysis UI] Updating UI with:', { documentCount, pageCount, oversizedCount, animated });
    
    // Verify counter elements exist before using them
    if (!analysisState.documentCounter) {
        console.warn('[Analysis UI] Document counter element not found');
        analysisState.documentCounter = document.querySelector('.document-counter:nth-child(1) .counter-value');
    }
    
    if (!analysisState.pageCounter) {
        console.warn('[Analysis UI] Page counter element not found');
        analysisState.pageCounter = document.querySelector('.document-counter:nth-child(2) .counter-value');
    }
    
    if (!analysisState.oversizedCounter) {
        console.warn('[Analysis UI] Oversized counter element not found');
        analysisState.oversizedCounter = document.querySelector('.document-counter:nth-child(3) .counter-value');
    }
    
    // Update counters with animation if requested
    if (animated) {
        console.log('[Analysis UI] Animating counters');
        
        if (analysisState.documentCounter) {
            animateCounter(analysisState.documentCounter, 0, documentCount);
            console.log('[Analysis UI] Animating document counter to:', documentCount);
        }
        
        if (analysisState.pageCounter) {
            animateCounter(analysisState.pageCounter, 0, pageCount);
            console.log('[Analysis UI] Animating page counter to:', pageCount);
        }
        
        if (analysisState.oversizedCounter) {
            animateCounter(analysisState.oversizedCounter, 0, oversizedCount);
            console.log('[Analysis UI] Animating oversized counter to:', oversizedCount);
        }
    } else {
        // FIX: Ensure the correct counters are updated with the right values
        console.log('[Analysis UI] Directly updating counters');
        
        // Apply document count to the Documents counter
        if (analysisState.documentCounter) {
            analysisState.documentCounter.textContent = documentCount;
            console.log('[Analysis UI] Set document counter to:', documentCount);
        } else {
            console.error('[Analysis UI] Document counter element not available');
        }
        
        // Apply page count to the Pages counter
        if (analysisState.pageCounter) {
            analysisState.pageCounter.textContent = pageCount;
            console.log('[Analysis UI] Set page counter to:', pageCount);
        } else {
            console.error('[Analysis UI] Page counter element not available');
        }
        
        // Apply oversized count to the Oversized counter
        if (analysisState.oversizedCounter) {
            analysisState.oversizedCounter.textContent = oversizedCount;
            console.log('[Analysis UI] Set oversized counter to:', oversizedCount);
        } else {
            console.error('[Analysis UI] Oversized counter element not available');
        }
    }
    
    // Update progress bar
    const progress = analysisState.progress || 0;
    if (analysisState.progressBar) {
        analysisState.progressBar.style.width = `${progress}%`;
        console.log('[Analysis UI] Set progress bar width to:', `${progress}%`);
    }
    
    if (analysisState.progressPercentage) {
        analysisState.progressPercentage.textContent = `${progress}%`;
        console.log('[Analysis UI] Set progress percentage to:', `${progress}%`);
    }
}

/**
 * Animate a counter from start to end value
 * @param {HTMLElement} element - The DOM element to animate
 * @param {number} start - Starting value 
 * @param {number} end - Ending value
 */
function animateCounter(element, start, end) {
    if (!element) return;
    
    const duration = 1000; // 1 second
    const startTime = performance.now();
    const updateInterval = 16; // ~60fps
    
    function updateCounter(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(start + (end - start) * progress);
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = end;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Update the status badge
 * @param {string} status - Status type: 'pending', 'in-progress', 'completed', 'error'
 * @param {string} message - Optional message to display 
 */
function updateStatusBadge(status, message) {
    if (!analysisState.statusBadge) return;
    
    analysisState.statusBadge.className = `status-badge ${status}`;
    
    switch (status) {
        case 'pending':
            analysisState.statusBadge.innerHTML = '<i class="fas fa-clock"></i> Ready to Analyze';
            break;
        case 'in-progress':
            analysisState.statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Analysis in Progress';
            break;
        case 'completed':
            analysisState.statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Analysis Complete';
            break;
        case 'error':
            analysisState.statusBadge.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message || 'Error'}`;
            break;
        default:
            analysisState.statusBadge.innerHTML = message || 'Unknown Status';
    }
}

/**
 * Update project information display in the UI
 * @param {Object} projectState - Project state object
 */
function updateProjectInfo(projectState) {
    if (!projectState) return;
    
    // Update project ID display
    if (analysisState.projectIdDisplay) {
        analysisState.projectIdDisplay.textContent = projectState.projectId || '--';
    }
    
    // Update archive ID display
    if (analysisState.archiveIdDisplay && projectState.projectInfo) {
        analysisState.archiveIdDisplay.textContent = projectState.projectInfo.archiveId || '--';
    }
    
    // Update location display
    if (analysisState.locationDisplay && projectState.projectInfo) {
        analysisState.locationDisplay.textContent = projectState.projectInfo.location || '--';
    }
    
    // Update document type display
    if (analysisState.documentTypeDisplay && projectState.projectInfo) {
        analysisState.documentTypeDisplay.textContent = projectState.projectInfo.documentType || '--';
    }
    
    // Update document path display - Use PDF path from project info if available
    if (analysisState.projectSourcePath && projectState.projectInfo && projectState.projectInfo.pdfPath) {
        analysisState.projectSourcePath.textContent = projectState.projectInfo.pdfPath;
        
        // Update label to indicate this is the PDF documents path
        const pathLabel = document.querySelector('label[for="project-source-path"]');
        if (pathLabel) {
            pathLabel.textContent = 'PDF Documents Path:';
        }
    }
    // Fallback to source data path
    else if (analysisState.projectSourcePath && projectState.sourceData && projectState.sourceData.path) {
        analysisState.projectSourcePath.textContent = projectState.sourceData.path || '--';
    }
    
    console.log('[Analysis] Updated project information display');
}

/**
 * Update analysis progress during processing
 * @param {number} progress - Progress percentage (0-100)
 * @param {string} currentDocument - Currently processing document name
 * @param {string} message - Status message to display
 */
function updateAnalysisProgress(progress, currentDocument, message) {
    // Update progress value
    analysisState.progress = progress;
    
    // Update progress bar
    analysisState.progressBar.style.width = `${progress}%`;
    analysisState.progressPercentage.textContent = `${progress}%`;
    
    // Update current document display if provided
    if (currentDocument) {
        const currentDocElement = document.querySelector('.current-document');
        const currentDocValue = document.getElementById('current-document');
        
        if (currentDocElement && currentDocValue) {
            currentDocElement.style.display = 'block';
            currentDocValue.textContent = currentDocument;
        }
    }
    
    // Update status message
    if (message) {
        analysisState.analysisStatusText.textContent = message;
    } else if (currentDocument) {
        analysisState.analysisStatusText.textContent = `Analyzing document: ${currentDocument}`;
    }
}

/**
 * Show a notification to the user
 * @param {string} message - The message to display
 * @param {string} type - The notification type: 'info', 'success', 'warning', 'error'
 */
function showNotification(message, type = 'info') {
    // Remove the self-referencing check to prevent infinite recursion
    // Previously, this function was checking for window.showNotification, which is itself
    
    // Fallback implementation using console and alert
    console.log(`[Notification - ${type}] ${message}`);
    
    // Only show alerts for errors in development
    if (type === 'error') {
        alert(`Error: ${message}`);
    }
}

/**
 * Check if a global showNotification function exists that's different from this one
 * Used to safely call external notification functions
 */
function callGlobalNotification(message, type = 'info') {
    // Get the parent window's function if available
    if (window.parent && 
        window.parent.showNotification && 
        typeof window.parent.showNotification === 'function' &&
        window.parent.showNotification !== window.showNotification) {
        
        window.parent.showNotification(message, type);
        return true;
    }
    return false;
}

/**
 * Update the workflow recommendation display
 * @param {string} recommendationType - 'standard' or 'hybrid'
 */
function updateWorkflowRecommendation(recommendationType) {
    // Get workflow branch elements
    const standardWorkflow = document.querySelector('.workflow-branch.standard');
    const hybridWorkflow = document.querySelector('.workflow-branch.oversized');
    const workflowContainer = document.querySelector('.workflow-branches');
    
    // Remove pending-recommendation class
    if (workflowContainer) {
        workflowContainer.classList.remove('pending-recommendation');
    }
    
    // Remove inactive class from both branches
    if (standardWorkflow) {
        standardWorkflow.classList.remove('inactive');
        standardWorkflow.classList.remove('selected');
    }
    
    if (hybridWorkflow) {
        hybridWorkflow.classList.remove('inactive');
        hybridWorkflow.classList.remove('selected');
    }
    
    // Add selected class to the recommended branch
    if (recommendationType === 'standard' && standardWorkflow) {
        standardWorkflow.classList.add('selected');
        if (hybridWorkflow) hybridWorkflow.classList.add('inactive');
        
        // Add recommendation badge if not already present
        if (!standardWorkflow.querySelector('.recommendation-badge')) {
            const badge = document.createElement('div');
            badge.className = 'recommendation-badge';
            badge.innerHTML = '<i class="fas fa-star"></i> Recommended';
            standardWorkflow.appendChild(badge);
        }
    } else if (recommendationType === 'hybrid' && hybridWorkflow) {
        hybridWorkflow.classList.add('selected');
        if (standardWorkflow) standardWorkflow.classList.add('inactive');
        
        // Add recommendation badge if not already present
        if (!hybridWorkflow.querySelector('.recommendation-badge')) {
            const badge = document.createElement('div');
            badge.className = 'recommendation-badge';
            badge.innerHTML = '<i class="fas fa-star"></i> Recommended';
            hybridWorkflow.appendChild(badge);
        }
    }
    
    // Store the recommendation in analysisState
    analysisState.recommendedWorkflow = recommendationType;
    
    // Store the recommendation in localStorage
    try {
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        workflowState.workflowMode = recommendationType;
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
    } catch (error) {
        console.error('[Analysis] Error saving workflow recommendation to localStorage:', error);
    }
}

/**
 * Reset workflow recommendation to initial state
 */
function resetWorkflowRecommendation() {
    // Get workflow branch elements
    const standardWorkflow = document.querySelector('.workflow-branch.standard');
    const hybridWorkflow = document.querySelector('.workflow-branch.oversized');
    const workflowContainer = document.querySelector('.workflow-branches');
    
    // Add pending-recommendation class
    if (workflowContainer) {
        workflowContainer.classList.add('pending-recommendation');
    }
    
    // Add inactive class to both branches
    if (standardWorkflow) {
        standardWorkflow.classList.add('inactive');
        standardWorkflow.classList.remove('selected');
        
        // Remove recommendation badge if present
        const badge = standardWorkflow.querySelector('.recommendation-badge');
        if (badge) badge.remove();
    }
    
    if (hybridWorkflow) {
        hybridWorkflow.classList.add('inactive');
        hybridWorkflow.classList.remove('selected');
        
        // Remove recommendation badge if present
        const badge = hybridWorkflow.querySelector('.recommendation-badge');
        if (badge) badge.remove();
    }
    
    // Reset the recommendation in analysisState
    analysisState.recommendedWorkflow = null;
}

/**
 * Update the current document being analyzed
 * @param {string} documentName - Name of the document currently being analyzed
 */
function updateCurrentDocument(documentName) {
    const currentDocElement = document.querySelector('.current-document');
    const currentDocValue = document.getElementById('current-document');
    
    if (currentDocElement && currentDocValue) {
        currentDocElement.style.display = 'block';
        currentDocValue.textContent = documentName;
    }
}

/**
 * Clear the document list
 */
function clearDocumentList() {
    if (analysisState.documentList) {
        analysisState.documentList.innerHTML = '<div class="empty-list-message">No documents analyzed yet</div>';
    }
}

/**
 * Update the document list with results
 * @param {Array} documents - Array of document objects with analysis results
 */
function updateDocumentList(documents) {
    console.log('[Analysis UI] Updating document list with', documents?.length || 0, 'documents');
    
    if (!analysisState.documentList) {
        console.warn('[Analysis UI] Document list element not found in state, attempting to get from DOM');
        analysisState.documentList = document.getElementById('document-list');
        
        if (!analysisState.documentList) {
            console.error('[Analysis UI] Could not find document list element in DOM');
            return;
        }
    }
    
    // Clear the list
    analysisState.documentList.innerHTML = '';
    console.log('[Analysis UI] Cleared document list');
    
    if (!documents || documents.length === 0) {
        console.warn('[Analysis UI] No documents provided to updateDocumentList');
        analysisState.documentList.innerHTML = '<div class="empty-list-message">No documents analyzed yet</div>';
        return;
    }
    
    // Add each document to the list
    console.log('[Analysis UI] Adding', documents.length, 'documents to list');
    
    documents.forEach(doc => {
        // Skip invalid documents
        if (!doc || !doc.name) {
            console.warn('[Analysis UI] Skipping invalid document:', doc);
            return;
        }
        
        const docItem = document.createElement('div');
        docItem.className = 'document-item';
        
        // Document name
        const nameDiv = document.createElement('div');
        nameDiv.className = 'doc-name';
        nameDiv.textContent = doc.name;
        docItem.appendChild(nameDiv);
        
        // Page count
        const pagesDiv = document.createElement('div');
        pagesDiv.className = 'doc-pages';
        pagesDiv.textContent = doc.pages || 0;
        docItem.appendChild(pagesDiv);
        
        // Oversized count - handle different property names
        const oversizedDiv = document.createElement('div');
        oversizedDiv.className = 'doc-oversized';
        
        const hasOversized = doc.hasOversized || false;
        const oversizedCount = doc.totalOversized || 
                               (doc.oversizedPages ? doc.oversizedPages.length : 0) || 0;
        
        oversizedDiv.textContent = hasOversized ? oversizedCount : '0';
        docItem.appendChild(oversizedDiv);
        
        // Status/badge
        const statusDiv = document.createElement('div');
        statusDiv.className = 'doc-status';
        
        const badgeDiv = document.createElement('div');
        badgeDiv.className = `document-badge ${hasOversized ? 'badge-oversized' : 'badge-standard'}`;
        badgeDiv.textContent = hasOversized ? 'Oversized' : 'Standard';
        
        statusDiv.appendChild(badgeDiv);
        docItem.appendChild(statusDiv);
        
        // Add to the list
        analysisState.documentList.appendChild(docItem);
    });
    
    console.log('[Analysis UI] Document list updated successfully');
}

// Export UI functions for use in other modules
window.updateAnalysisUI = updateAnalysisUI;
window.updateStatusBadge = updateStatusBadge;
window.updateProjectInfo = updateProjectInfo;
window.updateAnalysisProgress = updateAnalysisProgress;
window.showNotification = showNotification;
window.callGlobalNotification = callGlobalNotification;
window.updateWorkflowRecommendation = updateWorkflowRecommendation;
window.resetWorkflowRecommendation = resetWorkflowRecommendation;
window.updateCurrentDocument = updateCurrentDocument;
window.clearDocumentList = clearDocumentList;
window.updateDocumentList = updateDocumentList; 