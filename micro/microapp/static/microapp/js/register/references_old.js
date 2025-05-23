/**
 * References Management Module - Main Entry Point
 * 
 * This file is a backward compatibility wrapper that imports and initializes
 * the modular references management system.
 */

// Import the main References Manager
import { ReferencesManager } from './references/index.js';

// Create a global variable for backward compatibility
let referencesModule;

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the modern ReferencesManager
    const manager = new ReferencesManager();
    
    // Store for global access
    window.referencesManager = manager;
    
    // Backward compatibility with old code
    referencesModule = {
        init: (projectId) => {
            if (window.referencesManager) {
                // If already initialized, just refresh
                window.referencesManager.refresh();
            } else {
                // Create a new instance
                window.referencesManager = new ReferencesManager(projectId);
            }
        },
        refresh: () => {
            if (window.referencesManager) {
                window.referencesManager.refresh();
            }
        },
        getStatus: () => {
            return window.referencesManager ? window.referencesManager.getStatus() : { status: 'unknown' };
        }
    };
    
    // Make it globally accessible for backward compatibility
    window.referencesModule = referencesModule;
});

function refreshReferencesUI() {
    const workflowState = loadStepData('workflow');
    console.log('[References] Loaded workflow state:', workflowState);

    const generateReferencesBtn = document.getElementById('generate-references');
    const statusBadge = document.querySelector('#step-6 .status-badge');
    const lockedMsg = document.querySelector('.status-message.inactive');
    const animation = document.querySelector('.reference-animation');
    const toStep5Btn = document.getElementById('to-step-5');
    const progressBar = document.querySelector('#step-6 .progress-bar-fill');
    const progressPercentage = document.querySelector('#step-6 .progress-percentage');
    const progressStatus = document.getElementById('reference-status');

    // Reset progress bar and status
    if (progressBar) progressBar.style.width = '0%';
    if (progressPercentage) progressPercentage.textContent = '0%';
    if (progressStatus) progressStatus.textContent = '';

    if (workflowState && workflowState.type === 'hybrid' && workflowState.oversizedCount > 0) {
        // Hybrid workflow: show animation, enable button, hide locked message
        if (generateReferencesBtn) {
            generateReferencesBtn.disabled = false;
            generateReferencesBtn.onclick = handleGenerateReferences;
        }
        if (lockedMsg) lockedMsg.classList.add('hidden');
        if (animation) animation.classList.remove('hidden');
        if (statusBadge) {
            statusBadge.className = 'status-badge pending';
            statusBadge.innerHTML = '<i class="fas fa-clock"></i> Generation Required';
        }
        if (toStep5Btn) toStep5Btn.disabled = true;
    } else {
        // Standard workflow: hide animation, disable button, show locked message
        if (generateReferencesBtn) {
            generateReferencesBtn.disabled = true;
            generateReferencesBtn.onclick = null;
        }
        if (lockedMsg) lockedMsg.classList.remove('hidden');
        if (animation) animation.classList.add('hidden');
        if (statusBadge) {
            statusBadge.className = 'status-badge completed';
            statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Not Required';
        }
        if (toStep5Btn) toStep5Btn.disabled = false;
    }
}

function handleGenerateReferences() {
    const generateReferencesBtn = document.getElementById('generate-references');
    const statusBadge = document.querySelector('#step-6 .status-badge');
    const progressBar = document.querySelector('#step-6 .progress-bar-fill');
    const progressPercentage = document.querySelector('#step-6 .progress-percentage');
    const progressStatus = document.getElementById('reference-status');
    const toStep5Btn = document.getElementById('to-step-5');
    const workflowState = loadStepData('workflow');
    const oversizedCount = workflowState && workflowState.oversizedCount ? workflowState.oversizedCount : 0;

    if (generateReferencesBtn) generateReferencesBtn.disabled = true;
    if (statusBadge) {
        statusBadge.className = 'status-badge in-progress';
        statusBadge.innerHTML = '<i class="fas fa-sync fa-spin"></i> Generation In Progress';
    }
    if (progressStatus) progressStatus.textContent = 'Starting reference sheet generation...';

    let progress = 0;
    const interval = setInterval(() => {
        progress += 5;
        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressPercentage) progressPercentage.textContent = `${progress}%`;

        // Update status message based on progress
        if (progressStatus) {
            if (progress < 30) {
                progressStatus.textContent = 'Creating reference templates...';
            } else if (progress < 60) {
                progressStatus.textContent = 'Mapping document references...';
            } else if (progress < 90) {
                progressStatus.textContent = 'Generating cross-references...';
            } else {
                progressStatus.textContent = 'Finalizing reference sheets...';
            }
        }

        // Update data panel (optional, if you have a data panel)
        updateReferenceSheetData(
            'in-progress',
            'Generating reference sheets',
            Math.floor((progress / 100) * oversizedCount),
            Math.floor((progress / 100) * oversizedCount)
        );

        if (progress >= 100) {
            clearInterval(interval);
            if (progressBar) progressBar.style.width = '100%';
            if (progressPercentage) progressPercentage.textContent = '100%';
            if (progressStatus) progressStatus.textContent = 'Reference sheet generation complete!';
            if (statusBadge) {
                statusBadge.className = 'status-badge completed';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Generation Complete';
            }
            updateReferenceSheetData(
                'completed',
                'Reference sheets generated',
                oversizedCount,
                oversizedCount
            );
            if (typeof showNotification === 'function') {
                showNotification('Reference sheets generated successfully!', 'success');
            }
            if (toStep5Btn) toStep5Btn.disabled = false;
        }
    }, 200);
}

function initReferencesComponent() {
    console.log('References component initialized');
    
    const referenceForm = document.querySelector('#reference-form');
    const addReferenceBtn = document.querySelector('#add-reference');
    const referencesList = document.querySelector('#references-list');

    // Restore references from localStorage if available
    const savedReferences = loadStepData('references');
    if (savedReferences && Array.isArray(savedReferences)) {
        savedReferences.forEach(ref => addReferenceItem(ref));
    }

    // Add event listeners
    if (addReferenceBtn) {
        addReferenceBtn.addEventListener('click', () => addReferenceItem());
    }
    if (referenceForm) {
        referenceForm.addEventListener('submit', handleReferenceSubmit);
    }

    // Initialize delete buttons for existing references
    initDeleteButtons();

    function addReferenceItem(data = {}) {
        const referenceTemplate = `
            <div class="reference-item">
                <input type="text" class="reference-title" placeholder="Title" value="${data.title || ''}">
                <input type="text" class="reference-author" placeholder="Author" value="${data.author || ''}">
                <input type="text" class="reference-year" placeholder="Year" value="${data.year || ''}">
                <button type="button" class="delete-reference">Remove</button>
            </div>
        `;
        if (referencesList) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = referenceTemplate;
            const newRef = tempDiv.firstElementChild;
            referencesList.appendChild(newRef);

            // Add delete event listener
            const deleteBtn = newRef.querySelector('.delete-reference');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', handleDeleteReference);
            }

            // Save on change
            ['input', 'change'].forEach(evt =>
                newRef.querySelectorAll('input').forEach(input =>
                    input.addEventListener(evt, saveReferencesToStorage)
                )
            );
        }
        saveReferencesToStorage();
    }

    function handleReferenceSubmit(event) {
        event.preventDefault();
        console.log('References form submitted');
        saveReferencesToStorage();
        // Notify progress component
        if (window.progressComponent) {
            window.progressComponent.setActiveStep(5); // References is step 6 (index 5)
        }
    }

    function handleDeleteReference(event) {
        const referenceItem = event.target.closest('.reference-item');
        if (referenceItem && referencesList) {
            referencesList.removeChild(referenceItem);
            saveReferencesToStorage();
        }
    }

    function initDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.delete-reference');
        deleteButtons.forEach(button => {
            button.addEventListener('click', handleDeleteReference);
        });
    }

    function saveReferencesToStorage() {
        const references = getReferences();
        saveStepData('references', references);
    }

    function getReferences() {
        const references = [];
        const items = document.querySelectorAll('.reference-item');
        items.forEach(item => {
            const title = item.querySelector('.reference-title').value;
            const author = item.querySelector('.reference-author').value;
            const year = item.querySelector('.reference-year').value;
            references.push({ title, author, year });
        });
        return references;
    }

    // Expose public methods
    window.referencesComponent = {
        getReferences
    };
}

// --- Local Storage Step Data Helpers (assumes register.js provides these globally) ---
function saveStepData(stepKey, data) {
    const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
    state[stepKey] = data;
    localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
}
function loadStepData(stepKey) {
    const state = JSON.parse(localStorage.getItem('microfilmWorkflowState') || '{}');
    return state[stepKey] || null;
}

function updateReferenceSheetData(status, reason, count, documentsRef) {
    const referenceData = {
        referenceSheets: {
            status: status,
            reason: reason,
            sheetCount: count,
            referencedDocuments: documentsRef
        }
    };
    const dataOutput = document.querySelector('#step-6 .data-output');
    if (dataOutput) {
        dataOutput.textContent = JSON.stringify(referenceData, null, 2);
    }
}