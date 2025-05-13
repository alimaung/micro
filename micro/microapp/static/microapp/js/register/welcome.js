// welcome.js - JavaScript for the register welcome page

document.addEventListener('DOMContentLoaded', function() {
    console.log('Welcome module initialized');
    
    // Dark mode handling
    initDarkMode();
    
    // Set progress bar to show no progress (before any steps)
    if (window.progressComponent && typeof window.progressComponent.setActiveStep === 'function') {
        window.progressComponent.setActiveStep(-1); // -1 indicates welcome/pre-step state
    }
    
    // Check if there's a saved project in localStorage
    const savedState = loadWorkflowState();
    const projectState = JSON.parse(localStorage.getItem('microfilmProjectState') || '{}');
    
    // Resume project section handling
    const resumeSection = document.getElementById('resume-section');
    const resumeBtn = document.getElementById('resume-project-btn');
    
    if (resumeSection && savedState && savedState.currentStep) {
        resumeSection.style.display = 'block';
        
        // Add project details to the resume section if available
        if (projectState && projectState.projectInfo) {
            const projectInfoElem = document.createElement('p');
            projectInfoElem.classList.add('project-info');
            projectInfoElem.innerHTML = `Project: <strong>${projectState.projectInfo.archiveId || 'Unknown ID'}</strong>`;
            
            if (projectState.projectInfo.documentType) {
                projectInfoElem.innerHTML += ` | Type: <strong>${projectState.projectInfo.documentType}</strong>`;
            }
            
            // Insert after the existing paragraph
            const existingP = resumeSection.querySelector('p');
            if (existingP) {
                existingP.after(projectInfoElem);
            }
        }
        
        // Add the Clear Project button if it doesn't exist
        if (!document.querySelector('.clear-project-btn')) {
            const clearBtn = document.createElement('a');
            clearBtn.href = '#';
            clearBtn.classList.add('clear-project-btn');
            clearBtn.textContent = 'Start New Project';
            clearBtn.id = 'clear-project-btn';
            
            clearBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                if (confirm('This will clear your current project data. Are you sure?')) {
                    // Clear all localStorage items
                    localStorage.removeItem('microfilmWorkflowState');
                    localStorage.removeItem('microfilmProjectState');
                    localStorage.removeItem('microfilmFilmNumberResults');
                    localStorage.removeItem('microfilmDistributionResults');
                    localStorage.removeItem('microfilmIndexData');
                    localStorage.removeItem('microfilmAnalysisData');
                    localStorage.removeItem('microfilmAllocationData');
                    localStorage.removeItem('microfilmReferenceSheets');
                    
                    // Refresh the page
                    window.location.reload();
                }
            });
            
            // Add after the resume button
            if (resumeBtn) {
                resumeBtn.after(clearBtn);
            } else {
                resumeSection.appendChild(clearBtn);
            }
        }
        
        // Add event listener for the resume button
        if (resumeBtn) {
            resumeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Determine the URL based on the saved step
                const stepNumber = parseInt(savedState.currentStep.split('-')[1]);
                let targetUrl = '';
                
                switch(stepNumber) {
                    case 1: targetUrl = '/register/project/'; break;
                    case 2: targetUrl = '/register/document/'; break;
                    case 3: targetUrl = '/register/workflow/'; break;
                    case 4: targetUrl = '/register/references/'; break;
                    case 5: targetUrl = '/register/allocation/'; break;
                    case 6: targetUrl = '/register/index/'; break;
                    case 7: targetUrl = '/register/filmnumber/'; break;
                    case 8: targetUrl = '/register/distribution/'; break;
                    case 9: targetUrl = '/register/export/'; break;
                    default: targetUrl = '/register/project/';
                }
                
                // Add workflow mode if available
                if (savedState.workflowMode) {
                    targetUrl += `?mode=${savedState.workflowMode}`;
                }
                
                // Add project ID if available
                if (projectState && projectState.projectId) {
                    // Add either ? or & depending on whether we already have parameters
                    targetUrl += targetUrl.includes('?') ? '&' : '?';
                    targetUrl += `id=${projectState.projectId}`;
                }
                
                // Add the step number for clarity
                targetUrl += targetUrl.includes('?') ? '&' : '?';
                targetUrl += `step=${stepNumber}`;
                
                // Navigate to the appropriate step
                window.location.href = targetUrl;
            });
        }
    }
    
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
    
    // Set up hover effects for workflow cards
    setupCardHoverEffects();
    
    // Set up workflow mode buttons
    const autoBtn = document.getElementById('auto-workflow');
    const semiBtn = document.getElementById('semi-workflow');
    const manualBtn = document.getElementById('manual-workflow');
            
    // Function to save the selected workflow mode to localStorage
    function saveWorkflowMode(mode) {
        // Clear existing project data to start fresh
        localStorage.removeItem('microfilmWorkflowState');
        localStorage.removeItem('microfilmProjectState');
        
        // Create a new workflow state
        const state = { workflowMode: mode, lastModified: Date.now() };
        localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
        console.log(`Workflow mode saved: ${mode}`);
            }
            
    // Add click handlers for the workflow mode buttons
    if (autoBtn) {
        autoBtn.addEventListener('click', function(e) {
            saveWorkflowMode('auto');
        });
    }
    
    if (semiBtn) {
        semiBtn.addEventListener('click', function(e) {
            saveWorkflowMode('semi');
        });
    }
    
    if (manualBtn) {
        manualBtn.addEventListener('click', function(e) {
            saveWorkflowMode('manual');
        });
    }
});

// Set up hover effects for workflow cards
function setupCardHoverEffects() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    
    // Auto card hover effect
    const autoCard = document.querySelector('.auto-card');
    if (autoCard) {
        autoCard.addEventListener('mouseenter', function() {
            this.style.boxShadow = isDarkMode ? 
                '0 15px 30px rgba(37, 165, 91, 0.3)' : 
                '0 15px 30px rgba(46, 204, 113, 0.2)';
        });
        
        autoCard.addEventListener('mouseleave', function() {
            this.style.boxShadow = isDarkMode ? 
                '0 10px 20px rgba(0, 0, 0, 0.2)' : 
                '0 10px 20px rgba(0, 0, 0, 0.05)';
        });
    }
    
    // Semi card hover effect
    const semiCard = document.querySelector('.semi-card');
    if (semiCard) {
        semiCard.addEventListener('mouseenter', function() {
            this.style.boxShadow = isDarkMode ? 
                '0 15px 30px rgba(41, 128, 185, 0.3)' : 
                '0 15px 30px rgba(52, 152, 219, 0.2)';
        });
        
        semiCard.addEventListener('mouseleave', function() {
            this.style.boxShadow = isDarkMode ? 
                '0 10px 20px rgba(0, 0, 0, 0.2)' : 
                '0 10px 20px rgba(0, 0, 0, 0.05)';
        });
                }
                
    // Manual card hover effect
    const manualCard = document.querySelector('.manual-card');
    if (manualCard) {
        manualCard.addEventListener('mouseenter', function() {
            this.style.boxShadow = isDarkMode ? 
                '0 15px 30px rgba(127, 140, 141, 0.3)' : 
                '0 15px 30px rgba(149, 165, 166, 0.2)';
        });
        
        manualCard.addEventListener('mouseleave', function() {
            this.style.boxShadow = isDarkMode ? 
                '0 10px 20px rgba(0, 0, 0, 0.2)' : 
                '0 10px 20px rgba(0, 0, 0, 0.05)';
        });
    }
                }
                
// --- Dark Mode Handling ---
function initDarkMode() {
    // Check if user has a saved preference
    const savedDarkMode = localStorage.getItem('microfilmDarkMode');
    
    if (savedDarkMode === 'true') {
        // User has explicitly enabled dark mode
        document.body.classList.add('dark-mode');
        applyDarkModeAdjustments();
    } else if (savedDarkMode === 'false') {
        // User has explicitly disabled dark mode
        document.body.classList.remove('dark-mode');
        applyLightModeAdjustments();
        } else {
        // No saved preference, check system preference
        const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (prefersDarkMode) {
            document.body.classList.add('dark-mode');
            applyDarkModeAdjustments();
        }
    }
    
    // Listen for system preference changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            // Only apply if user hasn't set a manual preference
            if (!localStorage.getItem('microfilmDarkMode')) {
                if (event.matches) {
                    document.body.classList.add('dark-mode');
                    applyDarkModeAdjustments();
                    setupCardHoverEffects(); // Refresh hover effects
                } else {
                    document.body.classList.remove('dark-mode');
                    applyLightModeAdjustments();
                    setupCardHoverEffects(); // Refresh hover effects
                }
            }
            });
        }
    }
    
function applyDarkModeAdjustments() {
    // Force apply dark mode to all elements
    document.documentElement.style.setProperty('--bg-color', '#1a1a1a');
    document.documentElement.style.setProperty('--text-color', '#e0e0e0');
    document.documentElement.style.setProperty('--text-secondary', '#b0b0b0');
    document.documentElement.style.setProperty('--card-bg', '#2a2a2a');
    document.documentElement.style.setProperty('--card-shadow', 'rgba(0, 0, 0, 0.2)');
    document.documentElement.style.setProperty('--hero-gradient', 'linear-gradient(135deg, #1a5bb8 0%, #5546b8 100%)');
    document.documentElement.style.setProperty('--border-color', '#444444');
    document.documentElement.style.setProperty('--resume-bg', '#2a2a2a');
    document.documentElement.style.setProperty('--project-info-bg', '#2c3e50');
    
    // Adjust hero section for dark mode
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.3)';
    }
    
    // Adjust hero background opacity for dark mode
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        heroBackground.style.opacity = '0.05';
    }
    
    // Set base shadows for cards (colored shadows will be applied on hover)
    const cards = document.querySelectorAll('.workflow-card');
    cards.forEach(card => {
        card.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';
    });
    
    // Adjust step items
    const stepItems = document.querySelectorAll('.step-item');
    stepItems.forEach(item => {
        item.style.backgroundColor = '#2a2a2a';
        item.style.borderColor = '#444444';
    });
}

function applyLightModeAdjustments() {
    // Reset to light mode
    document.documentElement.style.setProperty('--bg-color', '#ffffff');
    document.documentElement.style.setProperty('--text-color', '#333333');
    document.documentElement.style.setProperty('--text-secondary', '#666666');
    document.documentElement.style.setProperty('--card-bg', '#ffffff');
    document.documentElement.style.setProperty('--card-shadow', 'rgba(0, 0, 0, 0.05)');
    document.documentElement.style.setProperty('--hero-gradient', 'linear-gradient(135deg, #1a73e8 0%, #6c5ce7 100%)');
    document.documentElement.style.setProperty('--border-color', '#e0e0e0');
    document.documentElement.style.setProperty('--resume-bg', '#f8f9fa');
    document.documentElement.style.setProperty('--project-info-bg', '#EBF4FF');
    
    // Adjust hero section for light mode
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
    }
    
    // Adjust hero background opacity for light mode
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        heroBackground.style.opacity = '0.1';
    }
    
    // Set base shadows for cards (colored shadows will be applied on hover)
    const cards = document.querySelectorAll('.workflow-card');
    cards.forEach(card => {
        card.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.05)';
    });
    
    // Reset step items
    const stepItems = document.querySelectorAll('.step-item');
    stepItems.forEach(item => {
        item.style.backgroundColor = '#ffffff';
        item.style.borderColor = '#e0e0e0';
            });
        }

// --- Local Storage State Management ---
function loadWorkflowState() {
    const state = localStorage.getItem('microfilmWorkflowState');
    return state ? JSON.parse(state) : {};
}

function saveWorkflowState(state) {
    localStorage.setItem('microfilmWorkflowState', JSON.stringify(state));
} 