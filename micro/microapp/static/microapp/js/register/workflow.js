// workflow.js - Handles workflow determination (Step 3)

document.addEventListener('DOMContentLoaded', function() {
    const selectStandardWorkflowBtn = document.getElementById('select-standard-workflow');
    const selectHybridWorkflowBtn = document.getElementById('select-hybrid-workflow');
    const toStep4Btn = document.getElementById('to-step-4');

    // --- Data Panel Update ---
    function updateWorkflowData(type, recommendationType) {
        const documentCount = parseInt(document.querySelector('.document-counter:nth-child(1) .counter-value')?.textContent || '0');
        const oversizedCount = parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value')?.textContent || '0');
        const workflowData = {
            workflow: {
                type: type,
                recommendationType: recommendationType,
                documentDistribution: {
                    standard: documentCount - oversizedCount,
                    oversized: oversizedCount
                }
            }
        };
        document.querySelector('#step-3 .data-output').textContent = JSON.stringify(workflowData, null, 2);
    }

    // Modified to save reference sheet data instead of trying to update UI that's not present
    function saveReferenceSheetData(status, reason, count, documentsRef) {
        // Instead of updating the UI, just save the data for the next page
        const referenceData = {
            referenceSheets: {
                status: status,
                reason: reason,
                sheetCount: count,
                referencedDocuments: documentsRef
            }
        };
        
        // Save this data to localStorage so it can be used by references.js
        saveStepData('references', referenceData);
    }

    // --- Workflow Selection ---
    selectStandardWorkflowBtn.addEventListener('click', function() {
        // Update workflow data
        updateWorkflowData('standard', 'standard');
        // Save reference data instead of updating UI directly
        saveReferenceSheetData('inactive', 'Standard workflow selected', 0, 0);

        // Update UI
        const standardBranch = document.querySelector('.workflow-branch.standard');
        const oversizedBranch = document.querySelector('.workflow-branch.oversized');
        standardBranch.classList.add('selected');
        standardBranch.classList.remove('inactive');
        oversizedBranch.classList.remove('selected');
        oversizedBranch.classList.add('inactive');

        // Button highlight
        selectStandardWorkflowBtn.classList.add('selected');
        selectHybridWorkflowBtn.classList.remove('selected');

        // Update status badge
        const statusBadge = document.querySelector('#step-3 .status-badge');
        statusBadge.className = 'status-badge completed';
        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Standard Workflow Selected';

        // Enable navigation to next step
        toStep4Btn.disabled = false;

        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Standard workflow selected!', 'success');
        }

        saveWorkflowSelection('standard', 0);
    });

    selectHybridWorkflowBtn.addEventListener('click', function() {
        // Update workflow data
        updateWorkflowData('hybrid', 'hybrid');
        const oversizedCount = parseInt(document.querySelector('.document-counter:nth-child(3) .counter-value')?.textContent || '0');
        // Save reference data instead of updating UI directly
        saveReferenceSheetData('pending', 'Requires reference sheet generation', oversizedCount, oversizedCount);

        // Update UI
        const standardBranch = document.querySelector('.workflow-branch.standard');
        const oversizedBranch = document.querySelector('.workflow-branch.oversized');
        oversizedBranch.classList.add('selected');
        oversizedBranch.classList.remove('inactive');
        standardBranch.classList.remove('selected');
        standardBranch.classList.add('inactive');

        // Button highlight
        selectHybridWorkflowBtn.classList.add('selected');
        selectStandardWorkflowBtn.classList.remove('selected');

        // Update status badge
        const statusBadge = document.querySelector('#step-3 .status-badge');
        statusBadge.className = 'status-badge completed';
        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Hybrid Workflow Selected';

        // Enable navigation to next step
        toStep4Btn.disabled = false;

        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Hybrid workflow selected!', 'success');
        }

        saveWorkflowSelection('hybrid', 18);
    });

    // --- Initialize workflow data panel on load ---
    updateWorkflowData('pending', 'standard');
    // Don't try to initialize reference sheet data
});

function saveWorkflowSelection(type, oversizedCount) {
    console.log('[Workflow] Saving workflow state:', { type, oversizedCount });
    saveStepData('workflow', {
        type, // 'standard' or 'hybrid'
        oversizedCount
    });
}
