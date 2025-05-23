// progress.js - Workflow Progress Bar Logic for multi-page navigation

(function() {
    // Helper functions for localStorage
    function saveWorkflowState(state) {
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
    }

    function loadWorkflowState() {
        const state = localStorage.getItem('microfilmWorkflowState');
        return state ? JSON.parse(state) : {};
    }
    
    // Map of URL paths to step numbers (0-based)
    const pathToStepMap = {
        'project': 0,        // step-1
        'document': 1,       // step-2
        'allocation': 2,     // step-3
        'index': 3,          // step-4
        'filmnumber': 4,     // step-5
        'references': 5,     // step-6
        'distribution': 6,   // step-7
        'export': 7          // step-8
    };
    
    // Create a custom event for step changes that other modules can listen to
    function dispatchStepChangeEvent(stepNumber, stepId) {
        document.dispatchEvent(new CustomEvent('workflow-step-changed', {
            detail: {
                stepNumber: stepNumber,   // 0-based index
                stepId: stepId,           // step-1, step-2, etc.
                stepName: Object.keys(pathToStepMap)[stepNumber] || 'unknown'
            }
        }));
    }
    
    // Expose a global progressComponent for other modules to use
    window.progressComponent = {
        // Internal state
        _currentStepNumber: -1,       // 0-based index (0 = step 1, 1 = step 2, etc.)
        _workflowMode: 'auto',
        
        /**
         * Get the current step number (0-based)
         * @returns {number} The current step number
         */
        getCurrentStepNumber: function() {
            return this._currentStepNumber;
        },
        
        /**
         * Get the current step ID (step-1, step-2, etc.)
         * @returns {string} The current step ID
         */
        getCurrentStepId: function() {
            return `step-${this._currentStepNumber + 1}`;
        },
        
        /**
         * Initialize the progress component
         * This should be called once at startup
         */
        initialize: function() {
            console.log('Progress component initializing...');
            
            // Check if the progress bar exists in the DOM
            const progressBar = document.querySelector('.workflow-progress');
            if (!progressBar) {
                console.log('Progress bar not found on this page');
                return false; // Exit early if not on a page with progress bar
            }
            
            // Initialize based on URL
            this.initializeFromUrl();
            
            // Initialize mode indicator based on localStorage
            const savedState = loadWorkflowState();
            if (savedState && savedState.workflowMode) {
                this.setWorkflowMode(savedState.workflowMode);
            }
            
            // Set up storage event listener for cross-tab synchronization
            window.addEventListener('storage', this._handleStorageChange.bind(this));
            
            console.log('Progress component initialized');
            return true;
        },
        
        /**
         * Handle localStorage changes (for cross-tab synchronization)
         * @private
         */
        _handleStorageChange: function(e) {
            if (e.key === 'microfilmWorkflowState') {
                console.log('Workflow state changed in another tab, updating progress bar');
                try {
                    const newState = JSON.parse(e.newValue || '{}');
                    
                    // If there's a current step in the new state, update the progress
                    if (newState.currentStep) {
                        const stepMatch = newState.currentStep.match(/step-(\d+)/);
                        if (stepMatch) {
                            const stepNumber = parseInt(stepMatch[1], 10) - 1;
                            this.setActiveStep(stepNumber, false); // Don't save state to avoid loops
                        }
                    }
                    
                    // Update mode indicator if changed
                    if (newState.workflowMode) {
                        this.setWorkflowMode(newState.workflowMode, false); // Don't save state
                    }
                } catch (err) {
                    console.error('Error parsing new workflow state:', err);
                }
            }
        },
        
        /**
         * Update the progress bar and step highlights.
         * This is the primary method for setting the active step.
         * @param {number} stepNumber - Zero-based index (0 = step 1, 1 = step 2, ...)
         * @param {boolean} saveState - Whether to save the state to localStorage
         */
        setActiveStep: function(stepNumber, saveState = true) {
            console.log(`Setting active step to ${stepNumber + 1}`);
            this._currentStepNumber = stepNumber;
            
            const steps = document.querySelectorAll('.progress-step:not(.mode-step)');
            const fill = document.querySelector('.progress-bar-fill');
            const totalSteps = steps.length;

            // Special case -1 for welcome page (before any steps)
            if (stepNumber === -1) {
                steps.forEach(step => {
                    step.classList.remove('active', 'completed');
                });
                if (fill) fill.style.width = '0%';
                
                // Save the state if needed
                if (saveState) {
                    const state = loadWorkflowState() || {};
                    state.currentStep = 'welcome';
                    saveWorkflowState(state);
                }
                
                return;
            }

            // Update step classes
            steps.forEach((step, idx) => {
                step.classList.remove('active', 'completed');
                if (idx < stepNumber) {
                    step.classList.add('completed');
                } else if (idx === stepNumber) {
                    step.classList.add('active');
                }
            });

            // Update progress bar fill
            if (fill && totalSteps > 1) {
                const percent = (stepNumber) / (totalSteps - 1) * 100;
                fill.style.width = percent + '%';
            }
            
            // Save state if requested
            if (saveState) {
                const state = loadWorkflowState() || {};
                state.currentStep = `step-${stepNumber + 1}`;
                saveWorkflowState(state);
                
                // Dispatch event for other modules
                dispatchStepChangeEvent(stepNumber, `step-${stepNumber + 1}`);
            }
            
            console.log(`Progress updated: Step ${stepNumber + 1} of ${totalSteps}`);
        },

        /**
         * Set workflow mode and update the mode indicator
         * @param {string} mode - The mode to set ('auto', 'semi', 'manual')
         * @param {boolean} saveState - Whether to save the state to localStorage
         */
        setWorkflowMode: function(mode, saveState = true) {
            this._workflowMode = mode;
            
            const modeStep = document.getElementById('mode-indicator');
            const modeIcon = document.querySelector('.mode-icon');
            const modeLabel = document.querySelector('.mode-label');
            
            if (!modeStep || !modeIcon || !modeLabel) {
                console.warn('Mode indicator elements not found in DOM');
                return;
            }
            
            // Remove existing mode classes
            modeStep.classList.remove('auto', 'semi', 'manual');
            
            // Set new mode class and content
            switch(mode) {
                case 'auto':
                    modeStep.classList.add('auto');
                    modeIcon.innerHTML = '✨';
                    modeLabel.textContent = 'Full Auto';
                    break;
                case 'semi':
                    modeStep.classList.add('semi');
                    modeIcon.innerHTML = '⚙️';
                    modeLabel.textContent = 'Semi Auto';
                    break;
                case 'manual':
                    modeStep.classList.add('manual');
                    modeIcon.innerHTML = '🔧';
                    modeLabel.textContent = 'Manual';
                    break;
                default:
                    // No mode selected or unknown mode
                    modeIcon.innerHTML = '🔄';
                    modeLabel.textContent = 'Mode';
            }
            
            // Save state if requested
            if (saveState) {
                const state = loadWorkflowState() || {};
                state.workflowMode = mode;
                saveWorkflowState(state);
                
                // Dispatch event for other modules
                document.dispatchEvent(new CustomEvent('workflow-mode-changed', {
                    detail: { mode: mode }
                }));
            }
            
            console.log(`Mode indicator updated to: ${mode}`);
        },
        
        /**
         * Initialize the progress based on the current URL
         */
        initializeFromUrl: function() {
            const currentPath = window.location.pathname;
            let stepNumber = -1; // Default to welcome
            
            // Get the current page from the URL path
            const pathSegments = window.location.pathname.split('/').filter(p => p);
            const currentPage = pathSegments[pathSegments.length - 1] || '';
            
            // Map the current page to a step number
            if (pathToStepMap.hasOwnProperty(currentPage)) {
                stepNumber = pathToStepMap[currentPage];
            } else if (currentPath === '/register/') {
                stepNumber = -1; // Welcome page
            }
            
            // Set the active step
            this.setActiveStep(stepNumber);
            console.log(`Initialized progress from URL: ${currentPath} → Step ${stepNumber + 1}`);
        }
    };

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize the progress component
        window.progressComponent.initialize();
    });
})();
