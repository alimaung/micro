/* project.js */

// Project Setup (Step 1) logic for the registration workflow

document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const validateProjectBtn = document.getElementById('validate-project');
    const toStep2Btn = document.getElementById('to-step-2');
    // Only Step 1 navigation

    // --- Data Panel Update ---
    function updateProjectData() {
        const projectName = document.getElementById('project-name').value || '';
        const sourcePath = document.getElementById('project-folder').value || '';
        const outputPath = document.getElementById('output-folder').value || '';
        const filmType = document.getElementById('film-type').value;
        const filmStandard = document.getElementById('film-standard').value;
        const debugMode = document.getElementById('debug-mode').checked;
        const retainSources = document.getElementById('retain-sources').checked;
        const autoDetect = document.getElementById('auto-detect').checked;

        const projectData = {
            project: {
                name: projectName,
                sourcePath: sourcePath,
                outputPath: outputPath,
                filmType: filmType,
                filmStandard: filmStandard,
                options: {
                    debugMode: debugMode,
                    retainSources: retainSources,
                    autoDetectOversize: autoDetect
                }
            }
        };

        document.querySelector('.data-output').textContent = JSON.stringify(projectData, null, 2);
    }

    // --- Form Input Handling ---
    function checkProjectFormValidity() {
        const projectName = document.getElementById('project-name').value;
        const sourcePath = document.getElementById('project-folder').value;
        const outputPath = document.getElementById('output-folder').value;
        validateProjectBtn.disabled = !(projectName && sourcePath && outputPath);
    }

    // Add input event listeners to form fields
    document.getElementById('project-name').addEventListener('input', checkProjectFormValidity);
    document.getElementById('project-folder').addEventListener('input', checkProjectFormValidity);
    document.getElementById('output-folder').addEventListener('input', checkProjectFormValidity);

    // Mock browsing functionality
    document.querySelectorAll('.browse-button').forEach((button, index) => {
        button.addEventListener('click', function() {
            const mockPaths = [
                'C:/Users/admin/Documents/Microfilm_Project_Docs',
                'C:/Users/admin/Documents/Microfilm_Output'
            ];
            const inputElement = this.previousElementSibling;
            inputElement.value = mockPaths[index % 2];
            checkProjectFormValidity();
            updateProjectData();
        });
    });

    // Toggle options event listeners
    document.getElementById('debug-mode').addEventListener('change', updateProjectData);
    document.getElementById('retain-sources').addEventListener('change', updateProjectData);
    document.getElementById('auto-detect').addEventListener('change', updateProjectData);
    document.getElementById('film-type').addEventListener('change', updateProjectData);
    document.getElementById('film-standard').addEventListener('change', updateProjectData);

    // --- Step 1: Project Setup Stage ---
    validateProjectBtn.addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-check-circle"></i> Project Validated';
            toStep2Btn.disabled = false;
            // Update status badge
            document.querySelector('#step-1 .status-badge').className = 'status-badge completed';
            document.querySelector('#step-1 .status-badge').innerHTML = '<i class="fas fa-check-circle"></i> Configuration Valid';
            showNotification('Project configuration validated successfully!', 'success');
        }, 1500);
    });

    // --- Notification system (copied from register_old.js) ---
    function showNotification(message, type = 'info') {
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.padding = '12px 20px';
            notification.style.borderRadius = '8px';
            notification.style.color = '#fff';
            notification.style.fontWeight = '500';
            notification.style.zIndex = '9999';
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
            notification.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            notification.style.display = 'flex';
            notification.style.alignItems = 'center';
            notification.style.gap = '10px';
        }
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle"></i>';
                notification.style.backgroundColor = '#34a853';
                break;
            case 'error':
                icon = '<i class="fas fa-times-circle"></i>';
                notification.style.backgroundColor = '#ea4335';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle"></i>';
                notification.style.backgroundColor = '#fbbc04';
                break;
            default:
                icon = '<i class="fas fa-info-circle"></i>';
                notification.style.backgroundColor = '#1a73e8';
        }
        notification.innerHTML = icon + message;
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
    }

    // --- Initialize project data panel on load ---
    updateProjectData();
    checkProjectFormValidity();
});

