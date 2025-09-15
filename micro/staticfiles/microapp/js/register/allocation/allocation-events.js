/**
 * Film Allocation Events Module
 * 
 * This module handles all event bindings and handlers for film allocation.
 */
const AllocationEvents = (function() {
    /**
     * Bind event listeners to DOM elements
     */
    function bindEvents() {
        const dom = AllocationUI.getDomElements();
        
        // Start allocation button
        if (dom.startAllocationBtn) {
            dom.startAllocationBtn.addEventListener('click', function() {
                const state = AllocationCore.getState();
                if (!state.isAllocating && state.analysisResults) {
                    AllocationCore.startAllocation();
                }
            });
        }
        
        // Reset allocation button
        if (dom.resetAllocationBtn) {
            dom.resetAllocationBtn.addEventListener('click', function() {
                AllocationCore.resetAllocation();
            });
        }
        
        // Copy allocation data button
        if (dom.copyAllocationDataBtn) {
            dom.copyAllocationDataBtn.addEventListener('click', function() {
                AllocationUI.copyAllocationData();
            });
        }
        
        // Export allocation data button
        if (dom.exportAllocationDataBtn) {
            dom.exportAllocationDataBtn.addEventListener('click', function() {
                AllocationUI.exportAllocationData();
            });
        }
        
        // Bind navigation events
        bindNavigationEvents();
    }
    
    /**
     * Bind events for navigation buttons
     */
    function bindNavigationEvents() {
        // Navigation buttons
        const backToAnalysisBtn = document.getElementById('back-to-analysis');
        if (backToAnalysisBtn) {
            backToAnalysisBtn.addEventListener('click', function() {
                // Save current state and allocation results before navigating
                const state = AllocationCore.getState();
                
                // Use the new saveState function to save all state information
                AllocationCore.saveState();
                
                // Get current URL parameters
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get('id') || state.projectId;
                const flow = urlParams.get('flow') || state.workflowType || 'standard';
                const mode = urlParams.get('mode') || 'auto';
                const step = '2'; // Step for analysis page
                
                // Log navigation information
                console.log('[Allocation] Navigating back to analysis:', {
                    projectId,
                    flow,
                    mode,
                    step
                });
                
                // Navigate to analysis page with all parameters
                window.location.href = `/register/document?step=${step}&id=${projectId}&mode=${mode}&flow=${flow}`;
            });
        }
        
        const toIndexGenerationBtn = document.getElementById('to-step-6');
        if (toIndexGenerationBtn) {
            toIndexGenerationBtn.addEventListener('click', function() {
                // Save current state and allocation results before navigating
                const state = AllocationCore.getState();
                
                // Validate that allocation is complete before proceeding
                if (!state.allocationResults) {
                    AllocationUI.showToast('Please complete the allocation process before proceeding', 'warning');
                    return;
                }
                
                // Use the new saveState function to save all state information
                AllocationCore.saveState();
                
                // Log all available state data
                console.log('[Allocation] Analysis Results:', state.analysisResults);
                console.log('[Allocation] Allocation Results:', state.allocationResults);
                
                // Log localStorage AFTER saving to verify content
                const savedWorkflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                console.log('[Allocation] Saved Workflow State:', savedWorkflowState);
                console.log('[Allocation] Saved Allocation Results:', savedWorkflowState.allocationResults);
                console.log('[Allocation] Saved Analysis Results:', savedWorkflowState.analysisResults);
                
                // Also log the dedicated allocation storage
                const dedicatedAllocationData = JSON.parse(localStorage.getItem('microfilmAllocationData') || '{}');
                console.log('[Allocation] Dedicated Allocation Storage:', dedicatedAllocationData);
                
                // Get current URL parameters
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get('id') || state.projectId;
                const flow = urlParams.get('flow') || state.workflowType || 'standard';
                const mode = urlParams.get('mode') || 'auto';
                const step = '4'; // Step for index generation page
                
                // Display loading state on button
                toIndexGenerationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                toIndexGenerationBtn.disabled = true;
                
                // Navigate to index generation page with all parameters
                window.location.href = `/register/index?step=${step}&id=${projectId}&mode=${mode}&flow=${flow}`;
            });
        }
    }
    
    // Return public API
    return {
        bindEvents
    };
})(); 