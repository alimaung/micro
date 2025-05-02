/**
 * Document Analysis Workflow Module
 * 
 * Handles workflow recommendation functionality:
 * - Setting the recommended workflow based on analysis results
 * - Updating the UI to reflect recommendations
 * - Resetting workflow recommendations
 */

/**
 * Initialize the workflow recommendation UI
 * Sets up the initial state before analysis results are available
 */
function initWorkflowRecommendation() {
    // Get workflow branches container
    const workflowBranches = document.querySelector('.workflow-branches');
    
    // Ensure it has the pending-recommendation class
    if (workflowBranches && !workflowBranches.classList.contains('pending-recommendation')) {
        workflowBranches.classList.add('pending-recommendation');
    }
    
    // Ensure no workflow branch is selected initially
    if (analysisState.standardWorkflow) {
        analysisState.standardWorkflow.classList.remove('selected');
    }
    
    if (analysisState.hybridWorkflow) {
        analysisState.hybridWorkflow.classList.remove('selected');
        analysisState.hybridWorkflow.classList.add('inactive');
    }
    
    // Remove any existing recommendation badges
    const badges = document.querySelectorAll('.recommendation-badge');
    badges.forEach(badge => {
        if (badge && badge.parentNode) {
            badge.parentNode.removeChild(badge);
        }
    });
    
    // Reset the stored recommendation
    analysisState.recommendedWorkflow = null;
    
    // Reset in localStorage too
    try {
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        delete workflowState.recommendedWorkflow;
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
    } catch (error) {
        console.error('[Analysis] Error resetting workflow state:', error);
    }
}

/**
 * Set workflow recommendation based on analysis results
 * @param {string} recommendedType - The recommended workflow type ('standard' or 'hybrid')
 */
function setWorkflowRecommendation(recommendedType) {
    // Store the recommendation
    analysisState.recommendedWorkflow = recommendedType;
    
    // Remove the pending state
    const workflowBranches = document.querySelector('.workflow-branches');
    if (workflowBranches && workflowBranches.classList.contains('pending-recommendation')) {
        workflowBranches.classList.remove('pending-recommendation');
    }
    
    // Update UI based on recommendation
    if (recommendedType === 'hybrid') {
        // Hybrid workflow recommended (has oversized documents)
        analysisState.standardWorkflow.classList.remove('selected');
        analysisState.hybridWorkflow.classList.add('selected');
        analysisState.hybridWorkflow.classList.remove('inactive');
        
        // Remove standard badge if it exists
        if (analysisState.standardBadge && analysisState.standardBadge.parentNode) {
            analysisState.standardBadge.parentNode.removeChild(analysisState.standardBadge);
        }
        
        // Check if hybrid workflow already has a badge
        let hybridBadge = analysisState.hybridWorkflow.querySelector('.recommendation-badge');
        if (!hybridBadge) {
            hybridBadge = document.createElement('span');
            hybridBadge.className = 'recommendation-badge';
            hybridBadge.textContent = 'Recommended';
            analysisState.hybridWorkflow.querySelector('.branch-header').appendChild(hybridBadge);
        }
    } else {
        // Standard workflow recommended (no oversized documents)
        analysisState.standardWorkflow.classList.add('selected');
        analysisState.hybridWorkflow.classList.remove('selected');
        analysisState.hybridWorkflow.classList.add('inactive');
        
        // Make sure standard workflow has recommendation badge
        if (!analysisState.standardBadge || !analysisState.standardBadge.parentNode) {
            const newBadge = document.createElement('span');
            newBadge.className = 'recommendation-badge';
            newBadge.textContent = 'Recommended';
            analysisState.standardWorkflow.querySelector('.branch-header').appendChild(newBadge);
            analysisState.standardBadge = newBadge;
        }
        
        // Remove badge from hybrid workflow if it exists
        const hybridBadge = analysisState.hybridWorkflow.querySelector('.recommendation-badge');
        if (hybridBadge && hybridBadge.parentNode) {
            hybridBadge.parentNode.removeChild(hybridBadge);
        }
    }
    
    // Update workflow state in localStorage
    try {
        const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
        
        // Set the recommended workflow type
        workflowState.workflowMode = recommendedType === 'hybrid' ? 'hybrid' : 'standard';
        workflowState.recommendedWorkflow = recommendedType; // Store original recommendation
        
        console.log('[Analysis] Setting workflow mode to:', workflowState.workflowMode);
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
        
        // Update global URL parameters
        if (window.microfilmUrlParams) {
            window.microfilmUrlParams.mode = workflowState.workflowMode;
        }
    } catch (error) {
        console.error('[Analysis] Error updating workflow state:', error);
    }
}

/**
 * Reset workflow recommendation
 */
function resetWorkflowRecommendation() {
    // Reset recommendation
    analysisState.recommendedWorkflow = null;
    
    // Reset UI to pending state
    const workflowBranches = document.querySelector('.workflow-branches');
    if (workflowBranches && !workflowBranches.classList.contains('pending-recommendation')) {
        workflowBranches.classList.add('pending-recommendation');
    }
    
    // Reset UI
    analysisState.standardWorkflow.classList.remove('selected');
    analysisState.hybridWorkflow.classList.remove('selected');
    analysisState.hybridWorkflow.classList.add('inactive');
    
    // Remove all recommendation badges
    const badges = document.querySelectorAll('.recommendation-badge');
    badges.forEach(badge => {
        if (badge && badge.parentNode) {
            badge.parentNode.removeChild(badge);
        }
    });
    
    // Reset standardBadge reference
    analysisState.standardBadge = null;
}

// Export functions for use in other modules
window.initWorkflowRecommendation = initWorkflowRecommendation;
window.setWorkflowRecommendation = setWorkflowRecommendation;
window.resetWorkflowRecommendation = resetWorkflowRecommendation; 