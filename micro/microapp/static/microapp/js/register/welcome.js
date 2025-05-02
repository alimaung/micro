// welcome.js - JavaScript for the register welcome page

document.addEventListener('DOMContentLoaded', function() {
    console.log('Welcome module initialized');
    
    // Set progress bar to show no progress (before any steps)
    if (window.progressComponent && typeof window.progressComponent.setActiveStep === 'function') {
        window.progressComponent.setActiveStep(-1); // -1 indicates welcome/pre-step state
    }
    
    // Check if there's a saved project in localStorage
    const savedState = loadWorkflowState();
    const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
    const resumeProjectBtn = document.querySelector('.resume-project');
    
    // Display project info if available
    const projectInfoContainer = document.querySelector('.project-info');
    if (projectInfoContainer && projectState && projectState.projectId) {
        let infoHTML = `<h4>Saved Project</h4>`;
        infoHTML += `<div class="info-item"><span>Project ID:</span> ${projectState.projectId}</div>`;
        
        if (projectState.projectInfo) {
            if (projectState.projectInfo.archiveId) {
                infoHTML += `<div class="info-item"><span>Archive ID:</span> ${projectState.projectInfo.archiveId}</div>`;
            }
            if (projectState.projectInfo.location) {
                infoHTML += `<div class="info-item"><span>Location:</span> ${projectState.projectInfo.location}</div>`;
            }
            if (projectState.projectInfo.documentType) {
                infoHTML += `<div class="info-item"><span>Document Type:</span> ${projectState.projectInfo.documentType}</div>`;
            }
        }
        
        // Show last modified time if available
        if (savedState && savedState.lastUpdated) {
            const lastUpdated = new Date(savedState.lastUpdated);
            infoHTML += `<div class="info-item"><span>Last Activity:</span> ${lastUpdated.toLocaleString()}</div>`;
        }
        
        projectInfoContainer.innerHTML = infoHTML;
        projectInfoContainer.style.display = 'block';
    }
    
    if (resumeProjectBtn) {
        if (savedState && savedState.currentStep) {
            // Enable the resume button if there's a saved project
            resumeProjectBtn.classList.remove('disabled');
            
            // Update button text if we know the project ID
            if (projectState && projectState.projectId) {
                resumeProjectBtn.textContent = `Resume Project #${projectState.projectId}`;
            }
            
            // Add event listener for the resume button
            resumeProjectBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Determine the URL based on the saved step
                const stepNumber = parseInt(savedState.currentStep.split('-')[1]);
                let targetUrl = '';
                
                switch(stepNumber) {
                    case 1: targetUrl = '/register/project/'; break;
                    case 2: targetUrl = '/register/document/'; break;
                    case 3: targetUrl = '/register/allocation/'; break;
                    case 4: targetUrl = '/register/index/'; break;
                    case 5: targetUrl = '/register/filmnumber/'; break;
                    case 6: targetUrl = '/register/references/'; break;
                    case 7: targetUrl = '/register/distribution/'; break;
                    case 8: targetUrl = '/register/export/'; break;
                    default: targetUrl = '/register/project/';
                }
                
                // Add URL parameters
                const url = new URL(targetUrl, window.location.origin);
                
                // Add project ID if available
                if (savedState.projectId) {
                    url.searchParams.set('id', savedState.projectId);
                } else if (projectState && projectState.projectId) {
                    url.searchParams.set('id', projectState.projectId);
                    
                    // Also update the workflow state with the project ID for future use
                    savedState.projectId = projectState.projectId;
                    saveWorkflowState(savedState);
                }
                
                // Add workflow mode if available
                if (savedState.workflowMode) {
                    url.searchParams.set('mode', savedState.workflowMode);
                } else {
                    url.searchParams.set('mode', 'auto');
                }
                
                // Add step parameter
                url.searchParams.set('step', stepNumber.toString());
                
                // Update the last updated timestamp
                savedState.lastUpdated = new Date().toISOString();
                saveWorkflowState(savedState);
                
                // Navigate to the appropriate step with parameters
                console.log('Resuming project with URL:', url.toString());
                window.location.href = url.toString();
            });
        } else {
            // Disable the resume button if there's no saved project
            resumeProjectBtn.classList.add('disabled');
            resumeProjectBtn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('No saved project found. Please start a new project.');
            });
        }
    }
    
    // Clear project button
    const clearProjectBtn = document.querySelector('.clear-project');
    if (clearProjectBtn) {
        if (savedState && savedState.currentStep) {
            clearProjectBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Are you sure you want to clear the saved project? This cannot be undone.')) {
                    localStorage.removeItem('microfilmWorkflowState');
                    localStorage.removeItem('microfilmProjectState');
                    location.reload(); // Reload the page to show changes
                }
            });
        } else {
            clearProjectBtn.classList.add('disabled');
            clearProjectBtn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('No saved project to clear.');
            });
        }
    }
});

// --- Local Storage State Management ---
function loadWorkflowState() {
    const state = localStorage.getItem('microfilmWorkflowState');
    return state ? JSON.parse(state) : {};
}

function saveWorkflowState(state) {
    localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
} 