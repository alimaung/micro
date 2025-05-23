// register.js - Main controller for register functionality with localStorage persistence

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('Register module initialized');
    
    // Make sure the Register nav link is active on all register subpages
    setActiveNavForRegisterPages();
    
    // Initialize navigation system - now with URL-based navigation
    initURLNavigation();

    // Back to Distribution (step 7)
    const backToStep7Btn = document.getElementById('back-to-step-7');
    if (backToStep7Btn) {
        backToStep7Btn.addEventListener('click', function() {
            // Navigate to distribution page instead of showing the step directly
            window.location.href = '/register/distribution/';
        });
    }

    // Finish Project (reset to step 1)
    const finishProjectBtn = document.getElementById('finish-project');
    if (finishProjectBtn) {
        finishProjectBtn.addEventListener('click', function() {
            // Ask for confirmation
            if (confirm('Are you sure you want to finish this project? You will start a new project next time.')) {
                // Clear both localStorage items
                localStorage.removeItem('microfilmWorkflowState');
                localStorage.removeItem('microfilmProjectState');
                localStorage.removeItem('microfilmFilmNumberResults');
                localStorage.removeItem('microfilmDistributionResults');
                localStorage.removeItem('microfilmIndexData');
                localStorage.removeItem('microfilmAnalysisData');
                localStorage.removeItem('microfilmAllocationData');
                localStorage.removeItem('microfilmReferenceSheets');
                
                // Go to welcome page
                window.location.href = '/register/';
                // Notification will be handled on the welcome page
            }
        });
    }
    
    // Listen for step changes from the progress component
    document.addEventListener('workflow-step-changed', function(e) {
        console.log('Step changed to:', e.detail.stepName, '(', e.detail.stepNumber + 1, ')');
    });
    
    // Listen for workflow mode changes
    document.addEventListener('workflow-mode-changed', function(e) {
        console.log('Workflow mode changed to:', e.detail.mode);
    });
});

/**
 * Set the active state for the Register navigation link on all register subpages
 */
function setActiveNavForRegisterPages() {
    // Check if we're on a register page or subpage
    const isRegisterPage = window.location.pathname.startsWith('/register/');
    
    if (isRegisterPage) {
        // Find the Register link in the navbar
        const registerNavLink = document.querySelector('.navbar-links a[href="/register/"]');
        
        if (registerNavLink) {
            // Add the active class to the Register link
            registerNavLink.classList.add('active');
        }
    }
}

function initURLNavigation() {
    // Get all next/prev buttons
    const nextButtons = document.querySelectorAll('.nav-button.next');
    const prevButtons = document.querySelectorAll('.nav-button.back');
    
    // Map step IDs to URLs
    const stepToURL = {
        'step-1': '/register/project/',
        'step-2': '/register/document/',
        'step-3': '/register/allocation/',
        'step-4': '/register/index/',
        'step-5': '/register/filmnumber/',
        'step-6': '/register/references/',
        'step-7': '/register/distribution/',
        'step-8': '/register/export/'
    };
    
    // Map step IDs to step numbers
    const stepIdToNumber = {
        'step-1': '1',
        'step-2': '2',
        'step-3': '3',
        'step-4': '4',
        'step-5': '5',
        'step-6': '6',
        'step-7': '7',
        'step-8': '8'
    };
    
    // Helper to get the next step URL based on the current step ID
    function getNextStepURL(currentId) {
        const stepMap = {
            'step-1': 'step-2',  // Project -> Analysis
            'step-2': 'step-3',  // Analysis -> Allocation
            'step-3': 'step-4',  // Allocation -> Index
            'step-4': 'step-5',  // Index -> Assignment
            'step-5': 'step-6',  // Assignment -> References
            'step-6': 'step-7',  // References -> Distribution
            'step-7': 'step-8',  // Distribution -> Export
        };
        
        const nextStepId = stepMap[currentId] || currentId;
        return stepToURL[nextStepId];
    }
    
    // Helper to get the previous step URL
    function getPrevStepURL(currentId) {
        const stepMap = {
            'step-2': 'step-1',  // Analysis -> Project
            'step-3': 'step-2',  // Allocation -> Analysis
            'step-4': 'step-3',  // Index -> Allocation
            'step-5': 'step-4',  // Assignment -> Index
            'step-6': 'step-5',  // References -> Assignment
            'step-7': 'step-6',  // Distribution -> References
            'step-8': 'step-7',  // Export -> Distribution
        };
        
        const prevStepId = stepMap[currentId] || currentId;
        return stepToURL[prevStepId];
    }
    
    // Helper to preserve URL parameters when navigating
    function addUrlParameters(baseUrl, stepId) {
        const urlParams = new URLSearchParams(window.location.search);
        const urlWithParams = new URL(baseUrl, window.location.origin);
        
        // Add mode parameter if it exists in URL or localStorage
        let mode = urlParams.get('mode');
        if (!mode) {
            const workflowState = loadWorkflowState();
            mode = workflowState.workflowMode || 'auto';
        }
        urlWithParams.searchParams.set('mode', mode);
        
        // Add ID parameter if it exists in URL or localStorage
        let id = urlParams.get('id');
        if (!id) {
            // Try to get from workflow state
            const workflowState = loadWorkflowState();
            if (workflowState.projectId) {
                id = workflowState.projectId;
            }
            
            // If not in workflow state, try project state
            if (!id) {
                const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
                id = projectState.projectId;
            }
        }
        
        // Only add ID parameter if we found one
        if (id) {
            urlWithParams.searchParams.set('id', id);
            console.log(`Adding project ID to URL: ${id}`);
        } else {
            console.warn('No project ID found in URL or localStorage');
        }
        
        // Add step parameter
        const stepNumber = stepIdToNumber[stepId];
        if (stepNumber) {
            urlWithParams.searchParams.set('step', stepNumber);
        }
        
        return urlWithParams.toString();
    }
    
    // Set up next button listeners
    nextButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Get the current step ID
            const stepElement = this.closest('.workflow-step');
            if (!stepElement) return;
            
            const currentStepId = stepElement.id;
            
            // Save progress to localStorage
            saveWorkflowState({
                ...loadWorkflowState(),
                currentStep: currentStepId
            });
            
            // Get the base URL for the next step
            const nextBaseURL = this.getAttribute('data-url') || getNextStepURL(currentStepId);
            
            // Get the next step ID
            const stepMap = {
                'step-1': 'step-2',
                'step-2': 'step-3',
                'step-3': 'step-4',
                'step-4': 'step-5',
                'step-5': 'step-6',
                'step-6': 'step-7',
                'step-7': 'step-8'
            };
            const nextStepId = stepMap[currentStepId] || currentStepId;
            
            // Navigate to the next URL with parameters
            if (nextBaseURL) {
                window.location.href = addUrlParameters(nextBaseURL, nextStepId);
            }
        });
    });
    
    // Set up previous button listeners
    prevButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Get the current step ID
            const stepElement = this.closest('.workflow-step');
            if (!stepElement) return;
            
            const currentStepId = stepElement.id;
            
            // Save progress to localStorage
            saveWorkflowState({
                ...loadWorkflowState(),
                currentStep: currentStepId
            });
            
            // Get the base URL for the previous step
            const prevBaseURL = this.getAttribute('data-url') || getPrevStepURL(currentStepId);
            
            // Get the previous step ID
            const stepMap = {
                'step-2': 'step-1',
                'step-3': 'step-2',
                'step-4': 'step-3',
                'step-5': 'step-4',
                'step-6': 'step-5',
                'step-7': 'step-6',
                'step-8': 'step-7'
            };
            const prevStepId = stepMap[currentStepId] || currentStepId;
            
            // Navigate to the previous URL with parameters
            if (prevBaseURL) {
                window.location.href = addUrlParameters(prevBaseURL, prevStepId);
            }
        });
    });
}

// --- Local Storage State Management ---

function saveWorkflowState(state) {
    localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
}

function loadWorkflowState() {
    const state = localStorage.getItem('microfilmWorkflowState');
    return state ? JSON.parse(state) : {};
}

// --- Hooks for saving step data ---
function saveStepData(stepKey, data) {
    const state = loadWorkflowState();
    state[stepKey] = data;
    saveWorkflowState(state);
}

function loadStepData(stepKey) {
    const state = loadWorkflowState();
    return state[stepKey] || null;
}
