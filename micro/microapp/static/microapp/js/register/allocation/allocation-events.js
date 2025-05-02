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
                const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                
                // Update workflow state with current information
                workflowState.currentStep = 'step-2'; // Analysis is step 2
                workflowState.projectId = state.projectId;
                workflowState.workflowType = state.workflowType;
                
                // Save allocation results if available
                if (state.allocationResults) {
                    workflowState.allocationResults = state.allocationResults;
                    workflowState.allocation = {
                        completed: true,
                        timestamp: new Date().toISOString()
                    };
                }
                
                // Save updated workflow state
                localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
                
                // Get current URL parameters
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get('id') || workflowState.projectId;
                const flow = urlParams.get('flow') || workflowState.workflowType || 'standard';
                const mode = urlParams.get('mode') || 'auto';
                const step = '2'; // Step for analysis page
                
                // Navigate to analysis page with all parameters
                window.location.href = `/register/document?step=${step}&id=${projectId}&mode=${mode}&flow=${flow}`;
            });
        }
        
        const toIndexGenerationBtn = document.getElementById('to-step-6');
        if (toIndexGenerationBtn) {
            toIndexGenerationBtn.addEventListener('click', function() {
                // Save current state and allocation results before navigating
                const state = AllocationCore.getState();
                const workflowState = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
                
                // Validate that allocation is complete before proceeding
                if (!state.allocationResults) {
                    AllocationUI.showToast('Please complete the allocation process before proceeding', 'warning');
                    return;
                }
                
                // Update workflow state with current information
                workflowState.currentStep = 'step-4'; // Index generation is step 4
                workflowState.projectId = state.projectId;
                workflowState.workflowType = state.workflowType;
                
                // Save allocation results
                workflowState.allocationResults = state.allocationResults;
                workflowState.allocation = {
                    completed: true,
                    timestamp: new Date().toISOString()
                };
                
                // Save updated workflow state
                localStorage.setItem('microfilmWorkflowState', JSON.stringify(workflowState));
                
                // Get current URL parameters
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get('id') || workflowState.projectId;
                const flow = urlParams.get('flow') || workflowState.workflowType || 'standard';
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